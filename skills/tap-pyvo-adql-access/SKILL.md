---
name: tap-pyvo-adql-access
description: Use when querying astronomy TAP services with ADQL through pyvo or curl, including service
  probes, metadata discovery, TOP-based queries, VOTable/FITS conversion, pandas/Parquet caching, and
  robust network fallbacks.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# TAP / pyvo / ADQL Access

## Overview

This is the canonical pattern for IVOA TAP catalog access. It covers pyvo, ADQL syntax, small service probes, metadata inspection, conversion to pandas, and Parquet caching. Use catalog-specific skills only after this generic pattern is clear.

## Portable setup

Use Python 3.12 in an isolated environment. The tested dependency set is recorded in
`research-skill.lock`.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  "astropy==8.0.1" "pandas==3.0.5" "pyarrow==25.0.0" \
  "pyvo==1.9.1" "PyYAML==6.0.3"
```

Run the examples with `.venv/bin/python`. Network requests go to the TAP endpoint chosen
by the user, and the caching examples write query results into the current workspace.
Inspect the endpoint and query before execution; begin with a tiny `TOP 1` probe.

## When to Use

Use this skill when the user asks to:

- query an astronomy catalog via TAP;
- write or debug ADQL;
- use `pyvo.dal.TAPService`;
- fetch VOTable/FITS/CSV results;
- discover schemas/tables/columns from a TAP service;
- cache TAP query results for plotting or REANA.

Use `gaia-aip-data-access` for Gaia@AIP details and `rave-dr6-data-access` for RAVE-specific table names and survey caveats.

## Procedure

### 1. Probe service availability

Start with the smallest possible query:

```python
import pyvo
service = pyvo.dal.TAPService("https://example.org/tap/")
result = service.run_sync("SELECT TOP 1 * FROM schema.table")
print(result.to_table()[:1])
```

If table names are unknown, query TAP metadata first rather than guessing.

### 2. Write ADQL, not generic SQL

Use:

```sql
SELECT TOP 100 col1, col2
FROM schema.table
WHERE condition
```

Avoid:

```sql
SELECT col1, col2 FROM schema.table LIMIT 100
```

Many TAP services reject `LIMIT`; `TOP N` is the safe default.

### 3. Convert and cache

```python
from pathlib import Path
import pandas as pd

out = Path("outputs/my-query")
out.mkdir(parents=True, exist_ok=True)

result = service.run_sync(query)
df = result.to_table().to_pandas()
df.to_parquet(out / "data.parquet", index=False)
df.head(20).to_csv(out / "preview.csv", index=False)
(out / "query.adql").write_text(query)
```

### 4. Record provenance

```python
import datetime, yaml, platform
provenance = {
    "access_method": "tap-adql-pyvo",
    "endpoint": service.baseurl,
    "created_utc": datetime.datetime.utcnow().isoformat() + "Z",
    "query_file": "query.adql",
    "row_count": int(len(df)),
    "columns": list(df.columns),
    "python": platform.python_version(),
}
(out / "provenance.yaml").write_text(yaml.safe_dump(provenance, sort_keys=False))
```

### 5. Use curl fallback when pyvo is unavailable

```bash
curl -s -X POST 'https://example.org/tap/sync' \
  -d 'REQUEST=doQuery' \
  -d 'LANG=ADQL' \
  --data-urlencode 'QUERY=SELECT TOP 10 * FROM schema.table' \
  -d 'FORMAT=votable' \
  -o result.xml
```

Some services may ignore `FORMAT=csv`; VOTable is the safest portable default.

Parse with Astropy:

```python
from astropy.io.votable import parse_single_table
df = parse_single_table("result.xml").to_table().to_pandas()
```

## Metadata Discovery

Common TAP metadata tables:

```sql
SELECT TOP 100 schema_name, table_name, description
FROM TAP_SCHEMA.tables
```

```sql
SELECT TOP 100 table_name, column_name, datatype, unit, description
FROM TAP_SCHEMA.columns
WHERE table_name = 'schema.table'
```

Use service-specific metadata pages when available; they are often faster and more complete.

## Optional REANA use

If a separately installed `reana-operator` skill is available, package the TAP query as
`analysis.py` and run:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/tap-task \
  --task "TAP query and plot" \
  --script analysis.py \
  --output data.parquet \
  --output preview.csv \
  --environment-profile astro-ml \
  --package pyvo \
  --run --timestamp
```

`pyvo` may not be present in every modeled REANA environment, so add `--package pyvo`
unless you have verified it is included. This optional path is not required for the
portable TAP workflow.

## Common Pitfalls

1. **Using `LIMIT`.** Prefer `TOP N` in ADQL.
2. **Querying the wrong schema.** Use `TAP_SCHEMA.tables` before constructing joins.
3. **Large synchronous queries.** Start with `TOP 1`/`TOP 100`; use async if available for larger jobs.
4. **Assuming pyvo errors are query errors.** Separate network/TLS/service downtime from ADQL parsing failures.
5. **Skipping column projection.** Selecting `*` from billion-row catalogs is slow and expensive.
6. **Losing query provenance.** Save the exact ADQL text with outputs.

## Verification Checklist

- [ ] `TOP 1` probe succeeds or failure is classified.
- [ ] Query uses ADQL syntax.
- [ ] Selected columns are explicit for non-trivial queries.
- [ ] Result converted to pandas/table successfully.
- [ ] Query text, preview, cache, and provenance are written.
- [ ] If REANA was requested and is available, the packaged scientific task runs there.
