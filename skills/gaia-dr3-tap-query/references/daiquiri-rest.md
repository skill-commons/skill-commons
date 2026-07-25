# Gaia@AIP Daiquiri REST fallback

Use this fallback only for a full-table aggregation, an exceptional long-running scan,
or a TAP outage. Ordinary Gaia work belongs in the TAP/PyVO workflow in `SKILL.md`.

The web query service uses a session cookie, CSRF token, asynchronous job, and paginated
JSON results. Its API details can change; probe the endpoints before a costly query.

## 1. Create isolated session state

```bash
SESSION_DIR=$(mktemp -d "${TMPDIR:-/tmp}/gaia-daiquiri.XXXXXX")
COOKIE_JAR="$SESSION_DIR/cookies.txt"
trap 'unlink "$COOKIE_JAR" 2>/dev/null || true; rmdir "$SESSION_DIR" 2>/dev/null || true' EXIT

curl -sS -c "$COOKIE_JAR" "https://gaia.aip.de/query//sql/" >/dev/null
CSRF=$(awk '$6 == "csrftoken" {print $7}' "$COOKIE_JAR")
test -n "$CSRF" || { echo "CSRF token not found" >&2; exit 1; }
```

Keep the cookie jar private and delete it when finished.

## 2. Submit one bounded job

```bash
curl -sS -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST \
  -H "Referer: https://gaia.aip.de/query//sql/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"query":"SELECT COUNT(*) FROM gaiadr3.gaia_source","query_language":"postgresql","queue":"5m"}' \
  "https://gaia.aip.de/query/api/jobs/"
```

Record the returned job UUID. Supported queue identifiers have included `5m` and `2h`;
verify them against the live service instead of relying on UI labels.

## 3. Poll with a hard bound

```bash
JOB_ID="<returned-uuid>"
for attempt in $(seq 1 20); do
  response=$(curl -sS -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
    -H "X-CSRFToken: $CSRF" \
    -H "X-Requested-With: XMLHttpRequest" \
    "https://gaia.aip.de/query/api/jobs/$JOB_ID/")
  phase=$(printf '%s' "$response" |
    python3 -c 'import json,sys; print(json.load(sys.stdin).get("phase",""))')
  printf '%s\n' "$phase"
  case "$phase" in
    COMPLETED) break ;;
    ERROR|ABORTED) exit 1 ;;
  esac
  sleep 5
done
test "$phase" = "COMPLETED" || { echo "job did not complete in polling window" >&2; exit 1; }
```

Do not detach the poller or fan out concurrent full-table jobs.

## 4. Fetch JSON rows

```bash
curl -sS -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://gaia.aip.de/query/api/jobs/$JOB_ID/rows/?limit=1000&offset=0"
```

Fetch additional pages deliberately. Do not guess a CSV endpoint; the verified result
path is the JSON `rows/` resource. Column metadata is available from:

```bash
curl -sS "https://gaia.aip.de/metadata/gaiadr3/gaia_source/"
```

## Pitfalls

- Refresh the base page before a new session; stale CSRF tokens fail.
- Use PostgreSQL for this REST query API unless the live service documents otherwise.
- The default short queue is unsuitable for expensive aggregation.
- A completed job can still return more rows than should be held eagerly; paginate and
  cache deliberately.
- Prefer `random_index` sampling over a full-table random sort.
