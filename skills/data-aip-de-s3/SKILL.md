---
name: data-aip-de-s3
description: Access AIP and other S3-compatible research data with explicit authentication, column and row reduction, Dask-backed Parquet reads, and cache-first handling of large or non-columnar files.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# data.aip.de S3 Access

## When to Use

Use this skill for public or credentialed research objects on `data.aip.de` or another
S3-compatible endpoint. It covers endpoint discovery, safe read configuration, large
Parquet reduction, local caching, and cache-first treatment of formats such as HDF5.

A file format, sample size, or downstream plot is not a separate access skill. Use
`astro-catalog-plotting-cache` for astronomy plots and `seaborn-paper-plots` for general
figures after a reusable local table exists.

For the known public SHboost layout, read
[`references/bucket-layout.md`](references/bucket-layout.md).

## Portable Setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'dask[dataframe]==2026.7.1' 'hvplot==0.12.2' \
  'datashader==0.19.1' 'pyarrow==25.0.0' \
  'pandas==3.0.5' 's3fs==2026.6.0'
```

Do not install into the system interpreter. Credentials must come from the user's normal
provider configuration or environment—not from a committed script or skill.

## 1. Define the Access Contract

Record before reading:

- endpoint URL, bucket, prefix/object key, and expected format;
- whether access is anonymous or credentialed;
- object size or Parquet partition layout;
- required columns, filters, and scientifically justified sampling;
- cache directory, available storage, and memory limit;
- whether remote objects are immutable or can change.

Probe metadata or one small object first. Never infer anonymous access from a public
hostname.

## 2. Configure S3 Explicitly

```python
endpoint = "https://s3.data.aip.de:9000"
storage_options = {
    "anon": True,
    "client_kwargs": {"endpoint_url": endpoint},
}
```

Use `anon=False` or omit it for provider-managed credentials as appropriate. Do not log
secret values. This workflow is read-only; do not upload, overwrite, or delete remote
objects unless a separate user request explicitly authorizes it.

## 3. Read Parquet with Early Reduction

Use pandas only when metadata and object size show the projected result is comfortably
small. Otherwise start with Dask:

```python
import dask.dataframe as dd

columns = ["source_id", "x", "y"]
ddf = dd.read_parquet(
    "s3://bucket/catalog/*.parquet",
    columns=columns,
    storage_options=storage_options,
)
reduced = ddf.dropna(subset=["x", "y"])
```

Apply partition filters, row predicates, and column projection before `.compute()`.
Avoid calculating a full row count solely to choose an approximate random fraction; use
Parquet metadata, a bounded partition sample, or a scientifically defined predicate when
possible.

If sampling is appropriate:

```python
sample = reduced.sample(frac=0.01, random_state=42)
sample.to_parquet("cache/catalog-sample", write_index=False)
```

State that an unweighted sample is not automatically a population estimate.

## 4. Cache for Reuse

Cache the smallest stable derivative that preserves the scientific task:

```text
cache/catalog-sample/
cache/query-or-filter.txt
cache/provenance.yaml
```

Record endpoint, object path, source version or object metadata, selected columns,
filters, sampling method and seed, row count, software versions, and creation time.
Read the derivative back before reporting success.

Cache invalidation must be deliberate. Refresh when source identity, schema, filters, or
scientific intent changes—not merely because a local file is old.

## 5. Handle HDF5 and Other Monolithic Files Cache-First

S3 object storage does not make an HDF5 file cloud-columnar. Unless the format and server
support a verified efficient range-read workflow:

1. verify object size and local free space;
2. download one complete object to a stable workspace cache;
3. verify size and available checksum/object metadata;
4. inspect it locally with the appropriate format-specific tool;
5. extract only needed datasets;
6. convert reused tabular derivatives to Parquet.

Do not repeatedly reopen a large remote HDF5 object for interactive analysis. Declare
and install a format-specific library such as `h5py` in the downstream environment only
when the task actually needs it.

## 6. Plot Only After Access Is Stable

For a quick diagnostic on a cached medium-sized dataframe, hvPlot is acceptable. Use
Dask + hvPlot/Datashader for a dense large result. Domain plotting, labels, projections,
and figure provenance belong in the appropriate visualization skill rather than this
access layer.

## Pitfalls

- Eager pandas reads of an unknown multi-GB dataset.
- Loading all columns before discovering which are needed.
- Recomputing the same remote scan instead of caching a derivative.
- Hard-coded credentials or accidental remote write configuration.
- Sampling without recording method, fraction, seed, and limitations.
- Treating remote HDF5 like a partitioned Parquet dataset.
- Reusing a stale cache after the source schema or selection changed.
- Plotting directly from the remote source before validating and caching the data.

## Verification

- [ ] Endpoint, bucket/key, authentication mode, and format are recorded.
- [ ] The smallest probe succeeds without exposing credentials.
- [ ] Large Parquet access uses projection and early reduction.
- [ ] A local derivative and provenance record exist and can be read back.
- [ ] Source identity and cache invalidation criteria are explicit.
- [ ] Remote objects were not modified.
- [ ] Downstream plotting uses the reviewed local derivative.
