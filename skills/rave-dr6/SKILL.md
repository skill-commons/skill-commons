---
name: rave-dr6
description: Query the RAVE DR6 catalog at https://www.rave-survey.org/tap/ using pyvo (TAPService.run_sync).
  Access stellar parameters, Gaia cross-matches, distances, and Galactic coordinates (l, b). Includes
  galactic and equirectangular projection plotting recipes.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# RAVE DR6 TAP Query

## Portable setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'pyvo==1.9.1' 'pandas==3.0.5' 'pyarrow==25.0.0' \
  'matplotlib==3.11.1' 'seaborn==0.13.2' 'numpy==2.5.1'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
Network access to the public RAVE TAP service is required; no credentials are
used. The workflow submits read queries and writes local Parquet and figure
files.

## When to Use
Use this skill when querying the RAVE (RAdial Velocity Experiment) 6th Data Release for stellar parameters, distances (parallax), or Galactic coordinates. Ideal for: generic TAP exploration, finding the nearest 100 stars, plotting RA/Dec sky distributions, galactic plane projections, or cross-matching with Gaia.

## Skill taxonomy
Use the public RAVE skills with this split:
- `rave-dr6` — canonical query + table/column discovery skill
- `rave-dr6-nearest-100-plot` — focused workflow for the nearest-100 PNG plots
- `rave-dr6-public-talk-visualizations` — polished public-talk-ready visual outputs

Start with `rave-dr6` for general querying and branch to the more specialized skill when the task is specifically plotting or presentation oriented.

## Procedure

### 1. Connect to the TAP service
```python
import pyvo, pandas as pd, warnings
warnings.filterwarnings('ignore')
tap = pyvo.dal.TAPService("https://www.rave-survey.org/tap/")
```

### 2. List available tables
```python
for t in tap.tables:
    print(t.name)
```

### 3. Inspect columns of a table
```python
t = tap.tables['ravedr6.dr6_x_gaiaedr3']
for c in t.columns:
    print(c.name)
```

### 4. Run a synchronous query
Use `run_sync()` — **not** `query()` or `submit_job()` (those use async and return 400 errors).

```python
query = """
SELECT TOP 100
    rave_obs_id, ra, dec, l, b, parallax, parallax_error,
    phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
"""
result = tap.run_sync(query)
df = result.to_table().to_pandas()
```

### 5. Save locally as Parquet
```python
df.to_parquet('rave_dr6_subset.parquet', index=False)
```

### 6. Galactic projection (xgal vs ygal)
Project onto the Galactic plane with the Sun at origin:

```python
import numpy as np
l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
df['xgal'] = np.cos(b_rad) * np.cos(l_rad)
df['ygal'] = np.cos(b_rad) * np.sin(l_rad)
```

```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, seaborn as sns
sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(8, 7))
ax.scatter(df['xgal'], df['ygal'], c=df['parallax'], cmap='plasma',
           s=70, edgecolors='white', linewidths=0.5, alpha=0.9)
ax.scatter(0, 0, c='gold', s=300, marker='o', edgecolors='orange', linewidths=2, zorder=10)
ax.annotate('Sun', xy=(0, 0), xytext=(0.07, 0.07), fontsize=12, color='darkorange',
            fontweight='bold', arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.5))
ax.set_xlabel('xgal = cos(b) cos(l)')
ax.set_ylabel('ygal = cos(b) sin(l)')
ax.set_aspect('equal')
ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1)
fig.colorbar(ax.collections[0], ax=ax, shrink=0.8).set_label('Parallax [mas]', rotation=270, labelpad=12)
fig.tight_layout()
fig.savefig('rave_dr6_xgal_ygal.png', dpi=180)
```

### 7. Plot RA vs Dec (equirectangular)
```python
fig, ax = plt.subplots(figsize=(14, 5))
scatter = ax.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma',
                     s=100, edgecolors='white', linewidths=0.6, alpha=0.9)
ax.set_xlabel('RA [deg]', fontsize=13)
ax.set_ylabel('Dec [deg]', fontsize=13)
ax.set_title('RA vs Dec — RAVE DR6 Stars', fontsize=14, fontweight='bold')
fig.colorbar(scatter, ax=ax, shrink=0.8).set_label('Parallax [mas]', rotation=270, labelpad=14)
fig.tight_layout()
fig.savefig('rave_dr6_ra_dec.png', dpi=180)
```

## Key Tables

| Table | Description |
|---|---|
| `ravedr6.dr6_sparv` | Master file + classification + obs diagnostics |
| `ravedr6.dr6_x_gaiaedr3` | Gaia EDR3 cross-match — has ra, dec, parallax, phot_g_mean_mag, bp_rp, l, b |
| `ravedr6.dr6_x_gaiadr2` | Gaia DR2 cross-match |
| `ravedr6.dr6_orbits` | Orbital parameters |
| `ravedr6.dr6_seismic` | Seismic data |
| `ravedr6.dr6_madera` | Asteroseismic parameters |

## Pitfalls
- **`run_sync()` is the only correct method** — `query()` does not exist on TAPService, `submit_job()` uses async and fails with 400.
- **Filter `parallax > 0`** — negative parallax entries correspond to stars with poorly constrained distances.
- **Use `TOP N` or `WHERE` clauses** to limit results — the TAP service times out on very large queries.
- **Distance estimation**: parallax in mas → distance in pc ≈ 1000/parallax.
- **For nearest stars**: `parallax > 0 ORDER BY parallax DESC`.
- **Keep the query in the foreground.** Run it in one foreground process rather
  than detaching it. RAVE TAP is sync-only (`run_sync`); bound the result with
  `TOP N` or a `WHERE` clause.
- **Anchor selections to literature values.** When isolating a known object's members (e.g. an open cluster or stellar stream), set your parallax / proper-motion / distance cuts from its published values — not from whatever maximizes the star count.

## Verification
- Query returns 100 rows for the TOP 100 example.
- Parquet file is saved with non-zero size.
- RA covers 0–360°, Dec covers southern sky (RAVE observes from Siding Spring, Australia).
- Galactic projection places the Sun at origin and shows asymmetric stellar distribution.
