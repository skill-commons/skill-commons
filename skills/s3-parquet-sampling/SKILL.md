---
name: s3-parquet-sampling
description: Sample or reduce massive Parquet datasets on S3 using local Parquet caching, Dask-first processing
  for large inputs, and hvPlot/Datashader for scalable scientific visualization.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# S3 Parquet Sampling and Plotting

## When to Use
Use this skill when working with a large Parquet dataset on S3 where loading the full dataset eagerly is impractical. Sample or reduce it, cache the working result locally as Parquet, and generate scalable plots.

## Setup

Create a workspace-local environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  "dask[dataframe]==2026.7.1" hvplot==0.12.2 datashader==0.19.1 \
  pyarrow==25.0.0 pandas==3.0.5 s3fs==2026.6.0
```

The published lock was exercised with CPython 3.12 on macOS ARM64. Configure
anonymous access or credentials through `storage_options`; never hardcode secrets.

## Procedure

### 1. Start with Dask for large datasets
```python
import dask.dataframe as dd

columns = ['x', 'y']
ddf = dd.read_parquet('s3://bucket/path/to/data/', columns=columns)
```

If the dataset is huge, Dask is the default choice. Aim to keep the effective working footprint around **32GB RAM** by pruning columns, filtering early, and avoiding eager `.compute()` until necessary.

### 2. Reduce before caching
Examples:
```python
# Example filter / reduction before materializing locally
reduced = ddf.dropna(subset=['x', 'y'])
reduced = reduced.sample(frac=0.01)
```

### 3. Cache locally as Parquet
```python
cache_path = './cache/sample_cache.parquet'
reduced.to_parquet(cache_path, write_index=False)
```

If you need a pandas DataFrame afterward, load it from the local cache rather than the original S3 path.

### 4. Reload from cache
```python
import pandas as pd

df = pd.read_parquet(cache_path)
```

### 5. Plot with hvPlot first
For medium-sized cached data:
```python
import hvplot.pandas  # noqa
plot = df.hvplot.scatter(x='x', y='y', alpha=0.3, responsive=True)
```

### 6. For large data, prefer Dask + hvPlot + Datashader
```python
import hvplot.dask  # noqa
plot = reduced.hvplot.scatter(
    x='x', y='y', rasterize=True, cnorm='eq_hist', responsive=True
)
```

Use `rasterize=True` or `datashade=True` for dense large datasets where plotting raw points becomes slow or unreadable.

## S3 access notes
- Read only required columns.
- Prefer filters that reduce row groups early when available.
- Use a local Parquet cache for all repeated downstream work.

## Pitfalls
- Do NOT load the full remote dataset eagerly with pandas when the dataset is large.
- Do NOT keep recomputing from S3 if the reduced sample can be cached locally.
- Do NOT save unnecessary columns in the local cache.
- Do NOT default to static matplotlib-only plotting when hvPlot or Datashader would better represent dense data.

## Verification
- Local Parquet cache exists and has non-zero size.
- Large-input processing used Dask rather than eager full reads.
- Plotting path is explicit and scalable (`hvplot`, `rasterize=True`, or `datashade=True` as appropriate).
- The final dataset size reflects a reduced/sample subset rather than the full original dataset.
