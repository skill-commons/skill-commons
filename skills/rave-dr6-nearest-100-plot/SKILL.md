---
name: rave-dr6-nearest-100-plot
description: 'Query the 100 nearest RAVE DR6 stars and generate two clear PNG plots: Galactic projection
  and RA/Dec scatter, with reproducible local parquet output.'
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# RAVE DR6 Nearest 100 Plot

## Portable setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'pyvo==1.9.1' 'pandas==3.0.5' 'pyarrow==25.0.0' \
  'numpy==2.5.1' 'matplotlib==3.11.1'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
Network access to the public RAVE TAP service is required; no credentials are
used. The workflow submits one bounded read query and writes a Parquet cache
and two figures.

## When to Use
Use this skill when the task is specifically to retrieve the nearest 100 RAVE DR6 stars and create straightforward scientific PNG plots rather than general TAP exploration.

## Procedure

### 1. Query the nearest 100 stars
Use `pyvo` and the public RAVE TAP service:
```python
import pyvo

service = pyvo.dal.TAPService('https://www.rave-survey.org/tap')
query = '''
SELECT TOP 100
    rave_obs_id, ra, dec, l, b, parallax, parallax_error,
    phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
'''
result = service.run_sync(query)
df = result.to_table().to_pandas()
```

### 2. Save a reproducible local table
```python
df.to_parquet('rave_dr6_nearest100.parquet', index=False)
```

### 3. Compute Galactic projection coordinates
```python
import numpy as np

l_rad = np.radians(df['l'].values)
b_rad = np.radians(df['b'].values)
df['xgal'] = np.cos(b_rad) * np.cos(l_rad)
df['ygal'] = np.cos(b_rad) * np.sin(l_rad)
```

### 4. Plot Galactic projection
```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 7), dpi=180)
scatter = ax.scatter(df['xgal'], df['ygal'], c=df['parallax'], cmap='plasma',
                     s=70, edgecolors='white', linewidths=0.5, alpha=0.9)
ax.scatter(0, 0, c='gold', s=250, marker='o', edgecolors='orange', linewidths=2, zorder=10)
ax.set_xlabel('xgal = cos(b) cos(l)')
ax.set_ylabel('ygal = cos(b) sin(l)')
ax.set_aspect('equal')
fig.colorbar(scatter, ax=ax, shrink=0.8).set_label('Parallax [mas]', rotation=270, labelpad=12)
fig.tight_layout()
fig.savefig('rave_dr6_nearest100_xgal_ygal.png', dpi=180)
```

### 5. Plot RA/Dec
```python
fig, ax = plt.subplots(figsize=(14, 5), dpi=180)
scatter = ax.scatter(df['ra'], df['dec'], c=df['parallax'], cmap='plasma',
                     s=100, edgecolors='white', linewidths=0.6, alpha=0.9)
ax.set_xlabel('RA [deg]')
ax.set_ylabel('Dec [deg]')
ax.set_title('RA vs Dec — 100 nearest RAVE DR6 stars')
fig.colorbar(scatter, ax=ax, shrink=0.8).set_label('Parallax [mas]', rotation=270, labelpad=14)
fig.tight_layout()
fig.savefig('rave_dr6_nearest100_ra_dec.png', dpi=180)
```

## Canonical Routing

This is a specialized example. For new work, use `rave-dr6` for live
table/column discovery and query construction, then apply
`astro-catalog-plotting-cache` for plotting, caching, and provenance
conventions.

## Pitfalls
- Use `run_sync()` with `pyvo`; avoid old async/query patterns that fail on this TAP service.
- Filter on `parallax > 0` before ordering by parallax.
- Keep the query lightweight with `TOP 100`.
- This skill is for clean scientific plots; if the user wants polished presentation graphics, switch to `rave-dr6-public-talk-visualizations`.

## Verification
- Query returns 100 rows.
- `rave_dr6_nearest100.parquet` is written.
- Both PNG outputs exist and open correctly.
- Galactic projection has the Sun at the origin and RA/Dec covers the sky footprint.
