---
name: gaia-dr3-daiquiri-rest
description: FALLBACK Gaia access (prefer gaia-dr3-tap-query). Query Gaia DR3 at gaia.aip.de via its Daiquiri
  REST API for full-table COUNTs and very large async scans — CSRF handling, async jobs, queue names,
  JSON result fetching. Access 1.8 billion sources with ~153 columns.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Gaia DR3 @AIP — Daiquiri REST API

## Portable setup

Use `curl` 8.7 or newer, standard POSIX shell utilities, and the CPython 3.12
standard library. The examples do not require third-party Python packages or an
API key. Keep the cookie jar in a fresh temporary directory and remove it when
the query finishes.
Network access to `gaia.aip.de` is required. The workflow creates a temporary
server-side query job and local session cookie, but does not modify catalog
data.

## When to Use
This is the **fallback** path. For normal Gaia queries and plotting, use
`gaia-dr3-tap-query` (TAP/pyvo — one `run_sync` call). Use this Daiquiri REST API
only for what TAP can't do: full-table `COUNT(*)`, very large async scans (the `2h`
queue), or when the TAP endpoint is unavailable.

Two notes that prevent past failures:
- Fetch results via the JSON `/query/api/jobs/{id}/rows/` endpoint. There is **no CSV
  download endpoint** — do not attempt one (it returns `Not found`).
- For a uniform subsample use `WHERE random_index < N`; **never `ORDER BY random()`**
  over the full 1.8B-row table (it scans and sorts everything).

## Prerequisites
- `curl` and Python 3 stdlib only — no API keys, no installation needed.

## Procedure

### 1. Get CSRF token and session cookie
```bash
COOKIE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/gaia-daiquiri.XXXXXX")
COOKIE_JAR="$COOKIE_DIR/cookies.txt"
trap 'unlink "$COOKIE_JAR" 2>/dev/null || true; rmdir "$COOKIE_DIR" 2>/dev/null || true' EXIT

curl -s -c "$COOKIE_JAR" "https://gaia.aip.de/query//sql/" > /dev/null
CSRF=$(grep csrftoken "$COOKIE_JAR" | awk '{print $7}')
test -n "$CSRF" || { echo "CSRF token not found" >&2; exit 1; }
```

### 2. Submit an async query job
```bash
curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -X POST \
    -H "Referer: https://gaia.aip.de/query//sql/" \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $CSRF" \
    -H "X-Requested-With: XMLHttpRequest" \
    -d '{"query": "SELECT COUNT(*) FROM gaiadr3.gaia_source", "query_language": "postgresql", "queue": "5m"}' \
    "https://gaia.aip.de/query/api/jobs/"
```
Returns: `{"id": "<uuid>", "phase": "QUEUED", ...}`

### 3. Poll for completion
```bash
JOB_ID="<uuid_from_step2>"
for i in $(seq 1 20); do
    sleep 5
    PHASE=$(curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
        -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
        -H "X-CSRFToken: $CSRF" \
        -H "X-Requested-With: XMLHttpRequest" \
        "https://gaia.aip.de/query/api/jobs/$JOB_ID/" | \
        python3 -c "import sys,json; print(json.load(sys.stdin).get('phase'))")
    echo "[$((i*5))s] Phase: $PHASE"
    [ "$PHASE" = "COMPLETED" ] && break
    [ "$PHASE" = "ERROR" ] && break
done
```

### 4. Fetch results
```bash
curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
    -H "X-CSRFToken: $CSRF" \
    -H "X-Requested-With: XMLHttpRequest" \
    "https://gaia.aip.de/query/api/jobs/$JOB_ID/rows/?limit=10&offset=0"
```

### 5. Get table metadata (column list)
```bash
curl -s "https://gaia.aip.de/metadata/gaiadr3/gaia_source/"
```

## Queue Names

| UI label | Queue param | Timeout |
|---|---|---|
| "30 Seconds" | omit (default) | 30s — times out on large queries |
| "5 Minutes" | `"5m"` | 5 min |
| "2 Hours" | `"2h"` | 2 hours |

Always use `"5m"` or `"2h"` for COUNT or large scans.

## Query Language

Always use `"postgresql"` — not `adql`, even though the web UI defaults to ADQL.

## Key Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/query/api/jobs/` | Submit async query job |
| GET | `/query/api/jobs/{id}/` | Poll job status (phase) |
| GET | `/query/api/jobs/{id}/rows/` | Fetch JSON results |
| GET | `/metadata/gaiadr3/gaia_source/` | Full column list with types/units |

## Known Limitations

- **`/query/tap/sync/` and `/query/tap/async/`** return HTML — do NOT use for programmatic queries.
- **`/query/sync/`** returns 405 Method Not Allowed.
- Default 30s queue times out on COUNT over `gaiadr3.gaia_source` (~1.8B rows) — always use `"5m"`.
- CSRF token must be extracted from the cookie jar (`csrftoken` cookie) and sent via `X-CSRFToken` header.
- Required headers: `X-Requested-With: XMLHttpRequest`, `Referer: https://gaia.aip.de/query//sql/`.

## Database Stats

- **Table**: `gaiadr3.gaia_source`
- **Row count**: ~1,811,709,771 sources (as of 2026)
- **Columns**: 153 (solution_id, designation, source_id, ra, dec, parallax, parallax_error, pm, pmra, pmdec, phot_g_mean_mag, phot_rp_mean_mag, phot_bp_mean_mag, bp_rp, radial_velocity, l, b, ecl_lon, ecl_lat, and many more)
- **Distance estimation**: distance_gspphot, or `1000/parallax` for simple estimates

## Pitfalls
- **Run this in the foreground with bounded polling** (as in step 3). Do not
  detach the query or fan out concurrent chunk jobs. Submit one async job, poll
  it within the foreground process, and cap the number of polls.
- Do NOT use TAP endpoints — they return HTML, not JSON.
- Do NOT omit the queue parameter for large scans — the default 30s timeout will truncate results.
- CSRF token expires — always refresh it by re-requesting the base URL before submitting a new job.
- Do NOT assume the UI queue names match the API — use `"5m"`, `"2h"`.

## Verification
- CSRF extraction returns a non-empty token.
- Job submission returns a valid UUID.
- Polling eventually reaches `COMPLETED` (not `ERROR`).
- `/metadata/` endpoint returns a JSON list of 153 columns.
