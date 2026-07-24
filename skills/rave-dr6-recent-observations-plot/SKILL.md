---
name: rave-dr6-recent-observations-plot
description: Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and generate a
  simple RA‑Dec scatter plot. Use an isolated Python environment and optionally use Astropy to derive
  Galactic coordinates.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Plot the newest 100 RAVE DR6 observations

## Portable setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'pyvo==1.9.1' 'pandas==3.0.5' 'matplotlib==3.11.1' \
  'seaborn==0.13.2' 'astropy==8.0.1' 'numpy==2.5.1'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
Network access to the public RAVE TAP service is required; no credentials are
used. The workflow submits one bounded read query and writes one or two PNG
figures.

## When to Use
Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and
generate a simple RA‑Dec scatter plot. Optionally use Astropy to derive Galactic
coordinates.

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Canonical Routing

This is a specialized example. For new work, use `rave-dr6` for live
table/column discovery and query construction, then apply
`astro-catalog-plotting-cache` for plotting, caching, and provenance
conventions.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.

This skill demonstrates how to query the RAVE DR6 TAP service for the latest 100 observations, then produce a scatter plot of RA vs Dec (and optionally Galactic X/Y).

# Prerequisites

Complete the isolated setup above before running the workflow.

# Steps
1. **Create a Python script** (`rave_recent_plot.py`) with the following content:
```python
import warnings, numpy as np, pandas as pd, matplotlib
warnings.filterwarnings('ignore')
matplotlib.use('Agg')
import matplotlib.pyplot as plt, seaborn as sns, pyvo

# Connect to the RAVE TAP service
service = pyvo.dal.TAPService('https://www.rave-survey.org/tap/')

# Query the newest 100 observations (ordered by obsdate descending)
query = '''
SELECT TOP 100 ra_input, dec_input, obsdate
FROM ravedr6.dr6_obsdata
ORDER BY obsdate DESC
'''
result = service.run_sync(query)
# Convert to pandas DataFrame
df = result.to_table().to_pandas()

# Plot RA vs Dec
plt.figure(figsize=(8,6))
sns = sns.scatterplot(data=df, x='ra_input', y='dec_input', hue='obsdate', palette='viridis', edgecolor='white', s=80)
plt.title('Newest 100 RAVE DR6 Observations (RA vs Dec)')
plt.xlabel('RA (deg)')
plt.ylabel('Dec (deg)')
plt.legend(title='Obsdate', loc='best')
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('rave_newest_ra_dec.png', dpi=180)
print('Saved plot to rave_newest_ra_dec.png')
```
2. **Run the script**:
```bash
python3 rave_recent_plot.py
```
   The PNG file `rave_newest_ra_dec.png` will be created in the current directory.

3. *(Optional)* **Plot Galactic X/Y** if you need a galactic projection:
   - Add the following after step 1 (requires `astropy`):
```python
from astropy.coordinates import SkyCoord
import astropy.units as u
# Convert RA/Dec to Galactic coordinates
coords = SkyCoord(ra=df['ra_input'].values*u.deg, dec=df['dec_input'].values*u.deg, frame='icrs')
gal = coords.galactic
l = gal.l.rad
b = gal.b.rad
# Compute planar projection
x = np.cos(b) * np.cos(l)
y = np.cos(b) * np.sin(l)
# Plot
plt.figure(figsize=(8,8))
sns = sns.scatterplot(x=x, y=y, hue=df['obsdate'], palette='plasma', edgecolor='white', s=80)
plt.scatter(0,0,c='gold',s=300,marker='o',edgecolor='orange',linewidth=2,zorder=10)
plt.title('Newest 100 RAVE DR6 Observations (Galactic X/Y)')
plt.xlabel('x = cos(b) cos(l)')
plt.ylabel('y = cos(b) sin(l)')
plt.axis('equal')
plt.legend(title='Obsdate', loc='best')
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('rave_newest_xy_gal.png', dpi=180)
print('Saved galactic plot to rave_newest_xy_gal.png')
```

# Pitfalls & Tips
- The `dr6_obsdata` table does **not** contain galactic longitude/latitude; you must compute them from RA/Dec (shown in the optional block).
- All 100 rows currently share the same `obsdate = 20130404`, so the hue will appear uniform. If you query a broader date range, colour coding becomes useful.
- If `pyvo` is missing, recreate the isolated environment using the setup above;
  never bypass system-package protections.
- Use `service.run_sync()` (synchronous) – avoid `submit_job()` which leads to errors on this TAP endpoint.
- Ensure the script runs in a directory where you have write permission for the PNG output.

# Verification
After running, open `rave_newest_ra_dec.png`. It should display a scatter of points across the RA‑Dec ranges (~146°‑225° RA, –42° to –47° Dec) corresponding to the latest RAVE observations.
