---
name: astro-catalog-plotting-cache
description: Use when turning astronomy catalog data into reproducible cached products and publication-ready
  plots, especially CMDs, RA/Dec maps, Galactic projections, hexbin density plots, Datashader outputs,
  and provenance-backed figure deliverables.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Astro Catalog Plotting and Cache

## Portable setup

Use CPython 3.12 in an isolated environment. The following direct versions were
exercised for this publication:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'numpy==2.4.6' 'pandas==3.0.5' 'matplotlib==3.11.1' \
  'dask[dataframe]==2026.7.1' 'datashader==0.19.1' 'pyarrow==25.0.0'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
For a ready-to-run workflow, use the bundled `templates/cmd_hexbin.py`.
The core workflow is local: it reads a catalog cache and writes figure,
cache, and provenance files in the workspace.

## Overview

This is the canonical plotting layer for astronomy catalog outputs. Use it after data access has produced a dataframe, Parquet cache, or small preview table. It encodes the preferred publication-ready conventions: white backgrounds, hexbin/density for large samples, explicit NaN filtering, magnitude-axis inversion, and provenance files.

## When to Use

Use this skill when the user asks to:

- plot a color-magnitude diagram (CMD);
- visualize Gaia/RAVE/SHBoost/StarHorse catalog data;
- make RA/Dec or Galactic projections;
- handle dense scatter plots without overplotting;
- cache data before plotting;
- produce publication-ready PNGs from catalog tables.

## Core Rules

1. **Filter before plotting.** Drop NaNs and invalid numeric values in plotted columns.
2. **Use density, not scatter, for large stellar catalogs.** Prefer hexbin or Datashader.
3. **White background.** Publication-style figures should be readable in papers and slides.
4. **Invert magnitude axes.** Lower magnitude is brighter.
5. **Save provenance.** Figure without source/filter metadata is not reproducible.
6. **Read back outputs.** Verify the PNG and cache exist before reporting success.

## CMD Hexbin Template

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

xcol = "bprp0"
ycol = "mg0"
df = pd.read_parquet("data.parquet", columns=[xcol, ycol])
mask = np.isfinite(df[xcol]) & np.isfinite(df[ycol])
plot = df.loc[mask, [xcol, ycol]]

plt.style.use("default")
fig, ax = plt.subplots(figsize=(7.2, 8.0), facecolor="white")
hb = ax.hexbin(
    plot[xcol], plot[ycol],
    gridsize=320,
    mincnt=1,
    bins="log",
    cmap="viridis",
    linewidths=0,
)
ax.invert_yaxis()
ax.set_xlabel("BP - RP")
ax.set_ylabel(r"$M_G$")
ax.set_title("Colour-Magnitude Diagram")
cb = fig.colorbar(hb, ax=ax)
cb.set_label("log10(count)")
fig.tight_layout()
fig.savefig("cmd.png", dpi=300, bbox_inches="tight")
```

## RA/Dec Plot

For small samples:

```python
fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")
sc = ax.scatter(df["ra"], df["dec"], c=df.get("parallax"), s=8, cmap="plasma", alpha=0.8)
ax.set_xlabel("RA [deg]")
ax.set_ylabel("Dec [deg]")
fig.colorbar(sc, ax=ax, label="Parallax [mas]")
fig.tight_layout()
fig.savefig("radec.png", dpi=300, bbox_inches="tight")
```

For large samples use Datashader or hexbin in projected coordinates.

## Galactic XY Projection

```python
import numpy as np
l = np.deg2rad(df["l"].to_numpy())
b = np.deg2rad(df["b"].to_numpy())
x = np.cos(b) * np.cos(l)
y = np.cos(b) * np.sin(l)

fig, ax = plt.subplots(figsize=(7, 7), facecolor="white")

hb = ax.hexbin(x, y, gridsize=250, mincnt=1, bins="log", cmap="magma")
ax.scatter([0], [0], c="gold", edgecolors="orange", s=160, label="Sun")
ax.set_aspect("equal")
ax.set_xlabel("cos(b) cos(l)")
ax.set_ylabel("cos(b) sin(l)")
ax.legend(frameon=False)
fig.colorbar(hb, ax=ax, label="log10(count)")
fig.tight_layout()
fig.savefig("galactic_xy.png", dpi=300, bbox_inches="tight")
```

## Datashader for Very Large Data

Use Datashader when millions of points would make hexbin slow or memory-heavy. Keep the data pipeline Dask-backed as long as possible.

```python
import dask.dataframe as dd
import datashader as ds
import datashader.transfer_functions as tf

ddf = dd.read_parquet("data/*.parquet", columns=["bprp0", "mg0"])
ddf = ddf.dropna()
canvas = ds.Canvas(plot_width=1200, plot_height=1000,
                   x_range=(-1, 5), y_range=(15, -5))
agg = canvas.points(ddf, "bprp0", "mg0")
img = tf.shade(agg, cmap=["#f7fbff", "#6baed6", "#08306b"], how="log")
img.to_pil().save("cmd_datashader.png")
```

## Provenance

Write a sidecar file:

```yaml
figure: cmd.png
source_cache: data.parquet
columns: [bprp0, mg0]
filters:
  finite: [bprp0, mg0]
plot_type: hexbin
style: white_background
created_utc: "YYYY-MM-DDTHH:MM:SSZ"
```

## REANA Use

If REANA execution is requested, copy `templates/cmd_hexbin.py` into the
workflow repository and declare both the figure and provenance file as outputs.
Keep the orchestration configuration with that workflow; do not assume a sibling
repository or a fixed filesystem layout.

## Common Pitfalls

1. **Scatter for huge catalogs.** Dense scatter hides structure and is slow.
2. **NaNs in plotted columns.** Matplotlib may silently omit or distort results.
3. **Forgetting magnitude inversion.** CMDs should have brighter stars upward.
4. **Dark backgrounds for publication plots.** Use white unless the user requests talk visuals.
5. **Missing labels/units.** Axes need physical meaning.
6. **No cache readback.** Confirm files exist and can be loaded.
7. **Datashader API drift.** Check the installed Datashader version for exact methods.

## Verification Checklist

- [ ] Input cache exists and row count is known.
- [ ] NaNs/invalid values filtered.
- [ ] Density method chosen for large samples.
- [ ] Magnitude axis inverted where appropriate.
- [ ] PNG saved at publication-quality DPI.
- [ ] Provenance sidecar written.
- [ ] Output files read back or inspected.
