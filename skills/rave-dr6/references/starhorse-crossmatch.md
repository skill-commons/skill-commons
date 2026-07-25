# RAVE DR6 to StarHorse/SHboost crossmatch

Use this path when RAVE stars need posterior distances or Galactocentric coordinates not
provided by the selected RAVE table. Read `starhorse-access` for the current product and
schema before downloading it.

## 1. Verify identifier semantics

Inspect both schemas and confirm that the `source_id` fields refer to compatible Gaia
releases. Do not join a DR2 identifier to an EDR3 identifier merely because both are
64-bit integers.

A commonly useful RAVE path is:

```sql
SELECT TOP 100000
    o.rave_obs_id, o.ra_input, o.dec_input, c.source_id
FROM ravedr6.dr6_obsdata AS o
JOIN ravedr6.dr6_cnn AS c
  ON o.rave_obs_id = c.rave_obs_id
ORDER BY o.ra_input, o.rave_obs_id
```

Probe it with `TOP 1` first. Use the live service schema to verify column names.

## 2. Paginate by a stable key

Do not depend on `OFFSET` for a large TAP join. If one bounded result is insufficient,
use keyset pagination with a deterministic ordering and both parts of the final key:

```sql
WHERE (
  o.ra_input > :last_ra
  OR (o.ra_input = :last_ra AND o.rave_obs_id > :last_id)
)
ORDER BY o.ra_input, o.rave_obs_id
```

Persist each completed page before requesting the next. Stop if the returned last key
does not advance. Check for duplicate observation IDs across pages.

## 3. Read only needed distance columns

For a Parquet product, project the join key and required science columns:

```python
import pandas as pd

starhorse = pd.read_parquet(
    "shboost_product.parquet",
    columns=["dist", "xg", "yg", "zg"],
).reset_index()
```

Some SHboost Parquet files encode `source_id` as the index rather than an ordinary
column. Inspect the schema and call `reset_index()` only when appropriate. Download a
large single file to a stable local cache before repeated analysis.

## 4. Join and audit

```python
rave["source_id"] = rave["source_id"].astype("int64")
starhorse["source_id"] = starhorse["source_id"].astype("int64")
matched = rave.merge(
    starhorse[["source_id", "dist", "xg", "yg", "zg"]],
    on="source_id",
    how="inner",
    validate="many_to_one",
)
```

Before deduplication, report:

- RAVE observation rows and unique source IDs;
- StarHorse rows and unique source IDs;
- matched rows and unique source IDs;
- duplicated keys and unmatched fraction;
- units and coordinate-frame definitions.

Use `validate="many_to_one"` only after confirming the distance product has one row per
source. Otherwise investigate rather than silently dropping duplicates.

## 5. Coordinates

Do not hard-code the Sun's Galactocentric coordinates without citing the product
definition. If plotting Sun-centered offsets, record the adopted solar position and use:

```python
x_offset = matched["xg"] - solar_x
y_offset = matched["yg"] - solar_y
```

Hand the cached, audited match to `astro-catalog-plotting-cache` for visualization.
