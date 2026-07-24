---
name: s3-parquet-sampling-plot-cached
description: Efficiently sample a subset of a massive Parquet dataset stored on an S3‑compatible bucket,
  cache the sampled rows locally as a Parquet file for fast reuse, and produce high‑resolution PNG plots
  suitable for analysis and publication.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Overview

## When to Use
Efficiently sample a subset of a massive Parquet dataset stored on an S3‑compatible bucket, cache the sampled rows locally as a Parquet file for fast reuse, and produce high‑resolution PNG plots suitable for analysis and publication.

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Canonical Routing

Use `data-aip-de-s3` for AIP object-store access choices,
`s3-parquet-sampling` for the general reduction workflow, and
`astro-catalog-plotting-cache` for reusable plotting and cache conventions.
Keep this skill as the SHboost-specific worked specialization.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.

This skill demonstrates how to efficiently sample a subset of a massive Parquet dataset stored on an S3‑compatible bucket, cache the sampled rows locally as a Parquet file for fast reuse, and produce high‑resolution PNG and vector PDF plots suitable for publications. It was built while working with the **shboost2024** dataset (≈ 218 M rows) and can be adapted to any similarly structured S3 Parquet collection.

# Steps
1. **Create an isolated workspace environment:**
   ```bash
   python3.12 -m venv .venv
   ```
2. **Install the complete tested dependency set**:
   ```bash
   .venv/bin/python -m pip install \
     "dask[dataframe]==2026.7.1" s3fs==2026.6.0 matplotlib==3.11.1 \
     seaborn==0.13.2 pandas==3.0.5 pyarrow==25.0.0 datashader==0.19.1 \
     colorcet==3.2.1 pillow==12.3.0
   ```
   The published lock was exercised with CPython 3.12 on macOS ARM64. Do not
   modify a system Python implicitly.
3. **Configure S3 connection** – set endpoint, enable anonymous access if the bucket is public:
   ```python
   S3_ENDPOINT = "https://s3.data.aip.de:9000"
   STORAGE_OPTS = {
       "use_ssl": True,
       "anon": True,
       "client_kwargs": {"endpoint_url": S3_ENDPOINT},
   }
   ```
4. **Read the dataset lazily with Dask**:
   ```python
   import dask.dataframe as dd
   df = dd.read_parquet(
       "s3://shboost2024/shboost_08july2024_pub.parq/*.parquet",
       storage_options=STORAGE_OPTS,
   )
   ```
5. **Determine sampling fraction** for the desired number of rows (e.g., 100 k):
   ```python
   TARGET_ROWS = 100_000
   total_rows = df.shape[0].compute()
   frac = min(TARGET_ROWS / total_rows, 1.0)
   print(f"Dataset size: {total_rows:,} rows – sampling {frac:.6%} → ~{TARGET_ROWS:,} rows")
   ```
6. **Sample and persist** the data, then materialise into a pandas DataFrame:
   ```python
   sample = df.sample(frac=frac, random_state=42).persist()
   pdf = sample.compute()
   print(f"Sampled rows: {len(pdf):,}")
   ```
7. **Cache locally as Parquet** for future runs:
   ```python
   CACHE_PATH = "shboost_cache.parquet"
   pdf.to_parquet(CACHE_PATH, index=False)
   print("Cache saved to", CACHE_PATH)
   ```
   On subsequent executions, simply `pd.read_parquet(CACHE_PATH)` if the file exists and `--force-refresh` is not supplied.
8. **Plot the CMD (or any two columns)** – when following this user's preferred ShBoost workflow, keep the original axes (`x=bprp0`, `y=mg0`), invert only the plotted y-axis, use a number-density hexbin view with a 512×512 grid, and write PNG output only. This approach handles large datasets efficiently while matching the established plotting convention.

```python
import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image
from colorcet import fire
from PIL import Image, ImageOps, ImageDraw, ImageFont

# Render from the local cached derivative.
dask_df = dd.read_parquet(CACHE_PATH, columns=["bprp0", "mg0"])

# Determine data extents (tiny compute pass)
x_min, x_max = dask_df['bprp0'].min().compute(), dask_df['bprp0'].max().compute()
y_min, y_max = dask_df['mg0'].min().compute(), dask_df['mg0'].max().compute()
# Canvas with normal y orientation; we'll flip later
cvs = ds.Canvas(plot_width=512, plot_height=512, x_range=(x_min, x_max), y_range=(y_min, y_max))
agg = cvs.points(dask_df, 'bprp0', 'mg0', ds.count())
# Shade with a bright colormap on a dark background, using log scaling for density
img = tf.shade(agg, cmap=fire, how='log', min_alpha=1)
img = tf.set_background(img, 'black')
# Export image (adds .png automatically)
export_image(img, filename='shboost_cmd')
# Flip vertically to get inverted y‑axis (astronomy style)
png_file = 'shboost_cmd.png'
pil_img = Image.open(png_file)
flipped = ImageOps.flip(pil_img)
# Optional: draw title on top
draw = ImageDraw.Draw(flipped)
title = f"ShBoost 2024 Colour‑Magnitude Diagram ({dd.read_parquet(CACHE_PATH).shape[0].compute():,} stars)"
font = ImageFont.load_default()
bbox = draw.textbbox((0, 0), title, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.rectangle([(0, 0), (w + 10, h + 10)], fill='black')
draw.text((5, 5), title, fill='white', font=font)
flipped.save(png_file)
print(f"✅ Saved PNG -> {png_file}")
```
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns
   sns.set_style("whitegrid")
   plt.rcParams.update({
       "font.size": 12,
       "axes.titlesize": 14,
       "axes.labelsize": 13,
       "figure.figsize": (8, 6),
       "savefig.dpi": 300,
       "savefig.bbox": "tight",
   })
   plt.figure()
   sns.scatterplot(
       data=pdf,
       x="mg0",    # horizontal axis
       y="bprp0", # vertical axis
       s=8,
       alpha=0.6,
       linewidth=0,
       edgecolor=None,
       color="#1b9e77",
   )
   plt.title("ShBoost 2024 Colour‑Magnitude Diagram (≈100 k stars)")
   plt.xlabel("mg0")
   plt.ylabel("bprp0")
   plt.tight_layout()
   plt.gca().invert_yaxis()
   plt.savefig("shboost_cmd.png", dpi=300)
   plt.close()
   ```
9. **Command‑line interface** (optional) to toggle cache refresh:
   ```python
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("--force-refresh", action="store_true",
                       help="Re‑sample from S3 and overwrite the cache.")
   args = parser.parse_args()
   # Pass args.force_refresh to the loading function.
   ```

# Pitfalls & Tips
- **Package installation**: on some systems `pip install dask[dataframe]` may be blocked by external‑managed‑environment policies. Use a virtual env or `--break-system-packages` only as a last resort.
- **Memory usage**: sampling ~100 k rows from a 218 M‑row dataset usually fits comfortably in RAM, but avoid larger fractions without checking available memory.
- **Axis inversion**: simply swap the `x=` and `y=` arguments in `sns.scatterplot` and adjust the `plt.xlabel` / `plt.ylabel` calls.
- **Cache invalidation**: if the underlying S3 data changes, run with `--force-refresh` to rebuild the parquet cache.
- **Performance**: Dask’s `sample` is lazy; persisting forces computation and keeps the sample in memory, which is faster than recomputing for each plot.

# Example Usage
```bash
# First run (creates cache and plots)
python shboost_plot_cached.py

# Subsequent run (fast, uses cache)
python shboost_plot_cached.py

# Force a fresh download from S3
python shboost_plot_cached.py --force-refresh
```
