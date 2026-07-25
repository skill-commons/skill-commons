---
name: rave-dr6
description: Discover and query RAVE DR6 tables through its public TAP service, cache bounded results, and crossmatch RAVE sources with Gaia or StarHorse distance products.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# RAVE DR6

## When to Use

Use this skill for RAVE DR6 table discovery, stellar-parameter queries, observation
metadata, Gaia crossmatches, and RAVE-to-StarHorse distance joins. A fixed sample size,
ordering, or plot style is a query/visualization choice—not a separate skill.

Use `tap-pyvo-adql-access` for generic TAP mechanics and
`astro-catalog-plotting-cache` after the query has produced a local table.

## Portable Setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'pyvo==1.9.1' 'pandas==3.0.5' 'pyarrow==25.0.0' \
  'matplotlib==3.11.1' 'seaborn==0.13.2' 'numpy==2.5.1'
```

Run examples with `.venv/bin/python`. The public service requires network access but no
credentials. Start with metadata and a tiny query before requesting a larger result.

## Query Workflow

### 1. Connect and inspect the live schema

```python
from pyvo.dal import TAPService

tap = TAPService("https://www.rave-survey.org/tap/")
for table in tap.tables:
    print(table.name)
```

Inspect columns before constructing joins:

```python
table = tap.tables["ravedr6.dr6_x_gaiaedr3"]
for column in table.columns:
    print(column.name, column.datatype, column.unit)
```

Do not assume that an example table, column, or row count remains unchanged.

### 2. Run a bounded synchronous query

```python
query = """
SELECT TOP 100
    rave_obs_id, source_id, ra, dec, l, b,
    parallax, parallax_error, phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = tap.run_sync(query)
df = result.to_table().to_pandas()
```

The RAVE service has been reliable with `run_sync()`. Do not assume its asynchronous
endpoint behaves like another TAP provider. Use `TOP N`, explicit columns, and selective
`WHERE` clauses.

### 3. Cache the exact result and query

```python
from pathlib import Path

out = Path("outputs/rave-dr6")
out.mkdir(parents=True, exist_ok=True)
df.to_parquet(out / "subset.parquet", index=False)
(out / "query.adql").write_text(query)
```

Record the endpoint, query, retrieval time, row count, and column units with the cache.

## Useful Tables

Discover these from the live service before relying on them:

| Table | Typical role |
|---|---|
| `ravedr6.dr6_sparv` | Master parameters, classifications, and diagnostics |
| `ravedr6.dr6_obsdata` | Observation identifiers, input coordinates, and dates |
| `ravedr6.dr6_cnn` | CNN products and a Gaia source identifier |
| `ravedr6.dr6_x_gaiaedr3` | Gaia EDR3 crossmatch with astrometry and photometry |
| `ravedr6.dr6_x_gaiadr2` | Gaia DR2 crossmatch |
| `ravedr6.dr6_orbits` | Orbital parameters |
| `ravedr6.dr6_seismic` | Seismic products |

## Distance Choices

- A positive parallax supports a simple exploratory ordering, but
  `1000 / parallax_mas` is not a precision distance estimator.
- Use a documented posterior distance product when the scientific task needs distances
  or Galactocentric coordinates.
- For an external StarHorse/SHboost product, follow
  [`references/starhorse-crossmatch.md`](references/starhorse-crossmatch.md). Validate
  source-ID release semantics before joining.

## Plotting

Pass the local Parquet result to `astro-catalog-plotting-cache`. That skill covers
RA/Dec maps, Galactic projections, CMDs, density rendering, publication style, talk
style, and figure provenance. Choose sample size and style from the scientific question,
not from a hard-coded “nearest 100” recipe.

## Pitfalls

- Use ADQL `TOP N`, not SQL `LIMIT`.
- Inspect the schema instead of guessing joins or Gaia release semantics.
- Do not launch an unbounded query against the full survey.
- Keep synchronous requests in a bounded foreground process.
- Filter missing or non-physical parallaxes before exploratory distance calculations.
- Anchor cluster or stream selections to literature values rather than maximizing the
  number of selected stars.
- Deduplicate by the scientifically appropriate identifier after a crossmatch; one
  source can have multiple observations.

## Verification

- [ ] A `TOP 1` query succeeds and the expected columns exist.
- [ ] The scientific query has explicit columns and a bounded result.
- [ ] The exact query and result cache are saved.
- [ ] Units and Gaia/source-ID release semantics were checked.
- [ ] Crossmatch duplicates and unmatched rows were measured.
- [ ] Any plot is produced from the cache with recorded provenance.
