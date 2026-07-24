---
name: datashader-019-pipeline
description: 'Generate density plots (CMD, hexbin, 2D histograms) using datashader 0.19.0 with Dask for
  lazy data loading and matplotlib for final rendering. Handles the 0.19.0 API: no Canvas.hexbin(), no
  tf.to_rgba(), tf.shade() returns Image.to_pil().'
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---


## When to Use
Generate density plots (CMD, hexbin, 2D histograms) using datashader 0.19.0 with Dask for lazy data loading and matplotlib for final rendering. Handles the 0.19.0 API: no Canvas.hexbin(), no tf.to_rgba(), tf.shade() returns Image.to_pil().

## Overview

Pipeline for creating high-density 2D scatter plots (e.g., stellar CMDs) from
large datasets using datashader 0.19.0 + Dask + matplotlib. Handles 500k–50M
points efficiently with hexbin-like density rendering and log-scaled colour maps.

## Prerequisites

- Python 3.12+ with `dask[dataframe]`, `datashader>=0.19`, `s3fs`, `pandas`, `matplotlib`
- Access to the dataset (S3 or local)

## Step‑by‑Step Procedure

1. **Create an isolated environment and install the tested dependencies:**
   ```bash
   python3.12 -m venv .venv
   .venv/bin/python -m pip install \
     "dask[dataframe]==2026.7.1" datashader==0.19.0 s3fs==2026.6.0 \
     pandas==3.0.5 matplotlib==3.11.1 pyarrow==25.0.0 numpy==2.4.6
   ```
   Keep the environment in the workspace; do not install these packages into a
   system Python. The published lock was exercised with CPython 3.12 on macOS ARM64.

2. **Load data with Dask (lazy, column-selective):**
   ```python
   import dask.dataframe as dd
   ddf = dd.read_parquet("s3://bucket/path/part.*.parquet",
                         storage_options={"anon": True, "client_kwargs": {"endpoint_url": S3_ENDPOINT}},
                         columns=["bprp0", "mg0"])  # only fetch needed columns
   sample = ddf.sample(frac=frac, random_state=42).persist()
   df = sample.compute()
   ```
   → Caches locally as Parquet for fast repeat runs.

3. **Render with datashader 0.19.0:**
   ```python
   import datashader as ds
   import datashader.transfer_functions as tf
   import numpy as np
   from matplotlib import colormaps

   canvas = ds.Canvas(x_range=(xmin, xmax), y_range=(ymin, ymax),
                      plot_width=1024, plot_height=1024)

   # 2D histogram via points (hexbin was removed in 0.19.0)
   agg = canvas.points(df, x='bprp0', y='mg0', agg=ds.count())
   # Returns xarray DataArray with dims ('y', 'x')

   # Shade with matplotlib colormap (pass colormap object, NOT string)
   cmap = colormaps.get_cmap('viridis')  # or custom ListedColormap
   shaded = tf.shade(agg, cmap=cmap, how='log')
   # Returns datashader.transfer_functions.Image object

   # Convert Image to RGB numpy array — fastest: direct uint32 bit extraction
   rgb = shaded.data            # uint32 array, ARGB layout (byte2=R, byte1=G, byte0=B)
   r = ((rgb >> 16) & 0xFF).astype(np.uint8)
   g = ((rgb >> 8) & 0xFF).astype(np.uint8)
   b = (rgb & 0xFF).astype(np.uint8)
   rgb = np.stack([r, g, b], axis=-1)  # shape (H, W, 3), uint8, correct orientation
   # No flip needed — uint32 extraction preserves datashader's coordinate order
   ```

4. **Display/save with matplotlib:**
   ```python
   fig, ax = plt.subplots(figsize=(14, 14), dpi=150, facecolor='#0a0a1a')
   ax.set_facecolor('#0a0a1a')
   ax.imshow(rgb, extent=(xmin, xmax, ymin, ymax), aspect='equal', origin='upper')
   ax.set_title('...')
   ax.set_xlabel('...')
   ax.set_ylabel('...')
   ax.invert_yaxis()  # CMD convention
   plt.savefig(path, dpi=300, facecolor='#0a0a1a')
   ```

## Key API Changes from Older datashader

| Old (pre-0.19)        | New (0.19.0)                    |
|-----------------------|---------------------------------|
| `canvas.hexbin(df, x, y, agg)` | `canvas.points(df, x, y, agg=ds.count())` |
| `tf.shade(agg, cmap='viridis', how='log')` | Pass `cmap=colormaps.get_cmap('viridis')` (object, not string) |
| `tf.to_rgba(shaded)`  | `tf.shade().to_pil()` → `np.array(pil_img)` |
| `tf.uint32_to_uint8(img)` | Not needed; `to_pil()` handles conversion |
| `dcolors.interpolate_color(a, b, n)` | Not available; use `matplotlib.colors.LinearSegmentedColormap.from_list()` |

## Important Details

- **uint32 RGB extraction (preferred):** `tf.shade().data` is a uint32 numpy array in ARGB layout.
  Extract RGB with bit-shifting: `r=((rgb>>16)&0xFF)`, `g=((rgb>>8)&0xFF)`, `b=(rgb&0xFF)`. No flip needed.
- **Alternative `to_pil()`:** `tf.shade().to_pil()` works but is slower. If used, convert with `np.array(pil_img)` and flip with `rgb[::-1,:,:]`.
- **Log scaling:** Use `how='log'` in `tf.shade()` to make low-density regions visible.
- **Column-selective Dask read:** Always specify `columns=[]` in `dd.read_parquet()` to avoid loading full rows.
- **Caching:** Write sampled data to local Parquet; check `len(df) >= TARGET_ROWS` before re-fetching.

## Canonical Routing

Use `astro-catalog-plotting-cache` for the general plotting and cache workflow.
Use this skill when the Datashader 0.19 API details and the large-density rendering
pipeline are specifically relevant.

## Pitfalls

- **String colormap names fail:** `tf.shade(agg, cmap='viridis', ...)` raises `ValueError: Unknown color`. Pass a `matplotlib.colors.Colormap` object.
- **No more hexbin on Canvas:** `canvas.hexbin()` was removed. Use `canvas.points()` with `agg=ds.count()` for a 2D histogram.
- **Image object has no `.view()`:** `tf.uint32_to_uint8()` was removed. Use `.to_pil()`.
- **`dcolors.interpolate_color()` removed:** Use `matplotlib.colors.LinearSegmentedColormap.from_list()` instead.

## Verification

After rendering you should have:
- A PNG file with a dark background showing a dense star-field CMD
- Clear density gradient from blue (low) → purple → orange → yellow → white (high)
- Inverted Y-axis (higher magnitude = lower on plot)
- Log-scaled colour bar
