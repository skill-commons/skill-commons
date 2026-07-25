---
name: gaia-dr3-tap-query
description: Query Gaia DR3 at gaia.aip.de through TAP/PyVO, with schema discovery, representative sampling, local caching, and a Daiquiri REST fallback for exceptional async jobs.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Gaia DR3 @AIP — TAP / pyvo (default)

## When to Use
Use this for Gaia DR3 catalog access at AIP. Start with one bounded `run_sync()` call
against `https://gaia.aip.de/tap/`. For full-table aggregation, exceptional long-running
jobs, or TAP outages, read [`references/daiquiri-rest.md`](references/daiquiri-rest.md)
and use the same skill's REST fallback.

> Dependencies (`pyvo`, `pandas`, `pyarrow`, `matplotlib`, `seaborn`) are
> not bundled with the skill. Create an isolated Python 3.12 environment and install the
> tested versions below. The complete tested resolution is recorded in
> `research-skill.lock`.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  "astropy==8.0.1" "matplotlib==3.11.1" "numpy==2.5.1" \
  "pandas==3.0.5" "pyarrow==25.0.0" "pyvo==1.9.1" \
  "scipy==1.18.0" "seaborn==0.13.2"
```

Run the examples with `.venv/bin/python`. They send queries to `gaia.aip.de` and write
Parquet or image files beneath the current workspace. Begin with the five-row
verification query before increasing result sizes.

## Procedure

### 1. Connect
```python
import pyvo, warnings
warnings.filterwarnings("ignore")
service = pyvo.dal.TAPService("https://gaia.aip.de/tap/")
```

### 2a. Uniform random subsample — the RIGHT way to get N representative stars, FAST
`random_index` is a precomputed shuffle column; filtering on it returns a uniform
sample without sorting the 1.8-billion-row table. ~200k stars come back in ~1 s.
```python
q = """SELECT ra, dec, phot_g_mean_mag, parallax, bp_rp
       FROM gaiadr3.gaia_source
       WHERE random_index < 200000"""
df = service.run_sync(q, maxrec=300000).to_table().to_pandas()
```

### 2b. Nearest stars / targeted selection
```python
q = """SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
       FROM gaiadr3.gaia_source
       WHERE parallax > 10
       ORDER BY parallax DESC"""        # a parallax floor bounds the sort -> fast
df = service.run_sync(q).to_table().to_pandas()
```

### 3. Cache to a workspace topic folder
```python
import os
out = "gaia-dr3-allsky"                 # descriptive topic folder under the workspace
os.makedirs(out, exist_ok=True)
df.to_parquet(f"{out}/gaia_sample.parquet", index=False)
```

### 4. Discover tables / columns (optional)
```python
print([t.name for t in service.tables if "gaiadr3" in t.name][:10])
```

## Quick-Look Plot Recipes

Use these only to inspect a query result. For reusable CMDs, sky maps, density rendering,
cache provenance, or presentation figures, use `astro-catalog-plotting-cache`.

### RA/Dec sky scatter
```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 5))
sc = plt.scatter(df["ra"], df["dec"], c=df.get("parallax"), cmap="plasma", s=4)
plt.xlabel("RA [deg]"); plt.ylabel("Dec [deg]"); plt.colorbar(sc, label="parallax [mas]")
plt.title("Gaia DR3 sample"); plt.savefig(f"{out}/gaia_ra_dec.png", dpi=150, bbox_inches="tight")
```

### All-sky density (Galactic, Mollweide) — for large samples
```python
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from matplotlib.colors import LogNorm
g = SkyCoord(ra=df.ra.values*u.deg, dec=df.dec.values*u.deg).galactic
l = -g.l.wrap_at(180*u.deg).radian; b = g.b.radian          # l increases left (convention)
H, xe, ye = np.histogram2d(l, b, bins=[np.linspace(-np.pi, np.pi, 361),
                                       np.linspace(-np.pi/2, np.pi/2, 181)])
fig = plt.figure(figsize=(13, 7)); ax = fig.add_subplot(111, projection="mollweide")
pcm = ax.pcolormesh(*np.meshgrid(xe, ye), H.T, cmap="magma",
                    norm=LogNorm(vmin=1, vmax=H.max()), shading="auto")
ax.grid(True, alpha=0.2); fig.colorbar(pcm, ax=ax, orientation="horizontal", shrink=0.6, label="stars/bin")
fig.savefig(f"{out}/allsky_density.png", dpi=130, bbox_inches="tight")
```

## Pitfalls
- Use `TOP N` or `WHERE random_index < N` — **not `LIMIT`** (unsupported by this service).
- **Never `ORDER BY random()`** over the full table — it forces a full scan + sort (minutes → stuck).
- For nearest-stars queries add a parallax floor (`WHERE parallax > 10`) so the sort is bounded.
- Samples above the sync row cap: pass `maxrec=`; for >1M rows use `service.submit_job(q)` (async).
- Save all outputs under the workspace (a topic folder); do not rely on
  client-specific home directories or temporary storage.
- **Keep queries in the foreground.** Run the query in a single foreground script — never launch it as a background process (terminal `background=true` / `notify_on_complete`). A detached query job keeps running after you stop and spawns stray completion nudges. A `run_sync` of a few hundred k rows returns in ~1 s; for a genuinely large scan use `service.submit_job(q)` and poll it *within* the foreground script. If you think you need millions of rows, subsample instead (`WHERE random_index < N`).
- **Anchor selections to literature values.** When isolating a known object's members (e.g. an open cluster), set your parallax / proper-motion / distance cuts from its published values — not from whatever maximizes the star count.
- **This service also speaks PostgreSQL (not only ADQL).** gaia.aip.de is a Daiquiri service: `service.submit_job(qstr, language='postgresql')` runs native PostgreSQL — the recipe many published notebooks for AIP-hosted tables use (e.g. StarHorse's `get_one_query`; see the `starhorse-access` skill). If a notebook/paper gives you a PostgreSQL query for an AIP table, run it VERBATIM with `language='postgresql'` — do NOT rewrite it into ADQL. Both languages work; rewriting is where errors creep in.
- Use the Daiquiri REST fallback only when TAP is unsuitable. It creates a server-side
  job and local cookie state and therefore requires bounded polling and cleanup.

## Verification
- `service.run_sync("SELECT TOP 5 ra, dec FROM gaiadr3.gaia_source")` returns 5 rows.
- A `random_index < N` query returns ~N real rows in ~1 s.
- Output Parquet / PNG land in the workspace topic folder.
