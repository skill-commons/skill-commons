---
name: rave-dr6-starhorse-access
description: Query RAVE DR6 via TAP and crossmatch with SHboost24 distances for nearby star analysis.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# RAVE DR6 + SHboost24 Access Pattern

## Portable setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install 'pyarrow==25.0.0' 'pandas==3.0.5'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
Network access to the public RAVE TAP and SHboost HTTPS services is required;
no credentials are used. The workflow submits read queries, downloads catalog
data, and writes a local crossmatch cache.

## When to Use
When you need RAVE DR6 star coordinates (ra, dec) paired with distances or Galactocentric positions for analysis of nearby stars.

## Data Sources

### 1. RAVE DR6 via TAP
- Endpoint: `https://www.rave-survey.org/tap/sync`
- Useful tables include `ravedr6.dr6_obsdata` (`ra_input`, `dec_input`,
  `rave_obs_id`), `ravedr6.dr6_cnn` (`source_id`, `rave_obs_id`), and
  `ravedr6.dr6_x_gaiaedr3` (the Gaia EDR3 crossmatch).
- A live `TOP 1` probe succeeded on all three tables on 2026-07-24. Discover
  the current table and column schema from the RAVE TAP service before building
  a larger query.
- The `dr6_obsdata` + `dr6_cnn` join remains a useful path when the workflow
  specifically needs input coordinates paired with CNN Gaia source IDs.
- Use the RAVE TAP endpoint for RAVE-specific tables. The Gaia@AIP TAP service
  is a separate catalog service, not a substitute for RAVE schema access.

### 2. SHboost24 via HTTP (no boto3/s3fs needed)
- Public parquet on S3: `https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet` (~190 MB)
- Download directly with `urllib.request` — no auth required
- Schema: `source_id`, `dist`, `xg`, `yg`, `zg`, `xgbdist_av_*`, `bprp0`, `mg0`, etc.
- SHboost24 has 1,701,553 stars with StarHorse distances and Galactocentric coordinates

## Procedure

### Step 1: Query RAVE DR6 (all ~426K crossmatched stars)

SQL:
```sql
SELECT o.ra_input, o.dec_input, c.source_id
FROM ravedr6.dr6_obsdata o
JOIN ravedr6.dr6_cnn c ON o.rave_obs_id = c.rave_obs_id
```

- Use `TOP 100000` (not `LIMIT m OFFSET n` — OFFSET causes 400 errors)
- Fetch in batches (~100K per batch, ~5 batches total)
- Format: `votable`
- Parse with regex: `<FIELD name="...">` for columns, `<TD>([^<]*)</TD>` for values
- Use the isolated CPython 3.12 environment from the portable setup.

### Step 2: Download SHboost24 parquet
```python
import urllib.request
url = "https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet"
urllib.request.urlopen(url).read()  # returns 190 MB
```

Read with `pyarrow.parquet` (no pandas needed for schema inspection):
```python
import pyarrow.parquet as pq
t = pq.read_table('/path/to/file.parquet', columns=['source_id', 'dist', 'xg', 'yg', 'zg'])
```

### Step 3: Crossmatch on source_id
```python
import pyarrow.parquet as pq, pickle

# SHboost lookup
t = pq.read_table('shboost_08july2024_pub.parquet', columns=['source_id', 'dist', 'xg', 'yg', 'zg'])
sh = t.to_pandas().reset_index()
sh_lookup = dict(zip(sh['source_id'], sh['dist']))

# RAVE data
with open('rave_dr6_gaia.pkl', 'rb') as f:
    rave = pickle.load(f)

# Match, deduplicate (keep first = nearest if sorted by dist)
matched = {}
for row in rave:
    sid = row['source_id']
    if sid in sh_lookup and sid not in matched:
        matched[sid] = {**row, 'dist': sh_lookup[sid]}

matched_list = sorted(matched.values(), key=lambda x: x['dist'])
top100 = matched_list[:100]
```

## Known Limitations
- Crossmatch rate is low (~658 / 426K RAVE stars) because SHboost24 is an independent survey
- SHboost24 `source_id` values are Gaia DR2/EDR3 format — RAVE DR6 CNN crossmatch provides these
- RAVE observes at |b| > 30°, mostly southern sky (dec < 0)

## Pitfalls
- Do NOT use `LIMIT/OFFSET` — use `TOP n` per batch
- Do not assume a fixed RAVE table/column layout. Inspect the live schema, then
  choose either the direct Gaia crossmatch table or the `dr6_obsdata` +
  `dr6_cnn` join appropriate to the requested columns.
- Do not use an environment missing the declared scientific dependencies; use
  the isolated setup above.
- SHboost parquet source_id may be the index — call `.reset_index()` on the DataFrame after `to_pandas()`

## Verification
- RAVE DR6 + CNN crossmatch: 426,574 stars fetched in ~5 batches
- SHboost24: 1,701,553 stars, dist range 0.008–546 kpc
- Crossmatch yield: ~658 unique stars (low rate by design)
- Top 100 closest stars span 0.032–0.24 kpc
