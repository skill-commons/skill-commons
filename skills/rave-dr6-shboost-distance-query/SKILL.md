---
name: rave-dr6-shboost-distance-query
description: Query and crossmatch RAVE DR6 stars with SHboost24 Gaia source IDs to obtain distances
  and Galactocentric coordinates, then select and plot nearby matches.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# RAVE DR6 + SHboost24 Distance Query Workflow

## Portable setup

Use CPython 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  'pandas==3.0.5' 'pyarrow==25.0.0' 'matplotlib==3.11.1'
```

Run Python examples with `.venv/bin/python`. Equivalent isolated environment
managers are fine; do not install these packages into the system interpreter.
Network access to the public RAVE TAP and SHboost HTTPS services is required;
no credentials are used. The workflow submits read queries, downloads catalog
data, and writes a crossmatch cache and figure in the workspace.

Query RAVE DR6 stars with SHboost24 distances via Gaia source_id crossmatch.

## Trigger
Need distances or Galactocentric coordinates for RAVE DR6 stars.

## Steps

### 1. Query RAVE DR6 TAP for ra, dec, source_id

Endpoint: `https://www.rave-survey.org/tap/sync`
Format: `votable`

```sql
SELECT o.ra_input, o.dec_input, c.source_id
FROM ravedr6.dr6_obsdata o
JOIN ravedr6.dr6_cnn c ON o.rave_obs_id = c.rave_obs_id
```

Fetch all rows in batches (no OFFSET with JOIN support — HTTP 400 error):
- Loop: `SELECT TOP 100000 ...` — run 5–6 times (~426K total, not 523K)
- Each batch: paginate by increasing `ra_input` threshold from last row's `ra_input`
- VOTable parsing: use `xml.etree.ElementTree` with dual namespace handling — first try `'.//v:TABLEDATA'` (IVO namespace), then fall back to `'.//TABLEDATA'` without prefix. Same for FIELD, TR, TD. Example:

**CRITICAL — use Python urllib, NOT shell curl:** some shell client wrappers have
returned truncated results (~241 rows instead of 426K). Use Python's
`urllib.request.urlopen()` instead; it correctly fetches all rows. Example:

```python
def parse_votable(xml_text):
    root = ET.fromstring(xml_text)
    ns = {'v': 'http://www.ivoa.net/xml/VOTable/v1.3'}
    table = root.find('.//v:TABLE', ns) or root.find('.//TABLE')
    fields = table.findall('.//v:FIELD', ns) or table.findall('.//FIELD')
    col_names = [f.get('name') for f in fields]
    tdata = table.find('.//v:TABLEDATA', ns) or table.find('.//TABLEDATA')
    trs = tdata.findall('.//v:TR', ns) or tdata.findall('.//TR')
    rows = []
    for tr in trs:
        tds = tr.findall('.//v:TD', ns) or tr.findall('.//TD')
        row = [td.text.strip() if td.text and td.text.strip() else None for td in tds]
        rows.append(row)
    return pd.DataFrame(rows, columns=col_names)
```

Expected crossmatch yield: ~2,500 stars out of 426K RAVE stars matched to SHboost24.

### 2. Download SHboost24 public parquet

```python
import pandas as pd
sh_url = "https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet"
sh = pd.read_parquet(sh_url)  # source_id is the INDEX, NOT a column
# Reset index to get source_id as a column:
sh = sh.reset_index()
# Columns: dist, xg, yg, zg, bprp0, mg0, and many xgb_* uncertainty columns
# dist range: ~0.008 to 546 kpc
# Top 100 closest RAVE-matched stars: 0.024 to 0.132 kpc (24–132 pc)
```

Important: `source_id` is the DataFrame index, not a regular column. If you only read columns explicitly, `source_id` will be missing — always call `.reset_index()` after loading if you need it.

### 3. Crossmatch on source_id

```python
rave["source_id"] = rave["source_id"].astype(int)
merged = rave.merge(sh[["source_id","dist","xg","yg","zg"]], on="source_id", how="inner")
merged = merged.drop_duplicates("source_id").sort_values("dist")
closest100 = merged.head(100)
```

### 4. Plot X_G vs Y_G with Sun Reference

Sun's Galactocentric position in SHboost24 frame: X_G = −8.178 kpc, Y_G = 0.0 kpc, Z_G = +0.020 kpc.

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path("rave-shboost")
out.mkdir(parents=True, exist_ok=True)
df = pd.read_parquet(out / "closest100.parquet")

SUN_X = -8.178  # kpc
SUN_Y = 0.0     # kpc

# Offset so Sun is at origin
xg_off = df["xg"].values - SUN_X
yg_off = df["yg"].values - SUN_Y
dist_pc = df["dist"].values * 1000

xmin, xmax = xg_off.min(), xg_off.max()
ymin, ymax = yg_off.min(), yg_off.max()
pad = max(xmax - xmin, ymax - ymin) * 0.12 + 0.01

fig, ax = plt.subplots(figsize=(9, 8))
sc = ax.scatter(xg_off, yg_off, c=dist_pc, cmap="plasma_r",
                s=70, alpha=0.85, edgecolors="white", linewidths=0.5, zorder=3)
cbar = plt.colorbar(sc, ax=ax, pad=0.02)
cbar.set_label("Distance (pc)", fontsize=12)

# Sun at origin
ax.plot(0, 0, "P", color="gold", markersize=22, markeredgewidth=2.2, zorder=10)
ax.plot(0, 0, "+", color="darkorange", markersize=26, markeredgewidth=2.5, zorder=11)
ax.annotate("Sun", xy=(0, 0), xytext=(0.008, 0.012),
            color="darkorange", fontsize=12, fontweight="bold", zorder=12)

ax.set_xlim(xmin - pad, xmax + pad)
ax.set_ylim(ymin - pad, ymax + pad)
ax.set_xlabel("X$_G$ − X$_{⊙}$  (kpc, Sun at 0)", fontsize=13)
ax.set_ylabel("Y$_G$ − Y$_{⊙}$  (kpc, Sun at 0)", fontsize=13)
ax.set_title("RAVE DR6 — 100 Nearest Stars (SHboost24 distances)\n"
             "Galactocentric X$_G$ vs Y$_G$, Sun Reference Frame", fontsize=12, pad=10)
ax.grid(True, linestyle="--", alpha=0.35)
ax.set_aspect("equal", adjustable="datalim")

textstr = (f"N = {len(df)} stars\nDist: {dist_pc.min():.0f}–{dist_pc.max():.0f} pc\nSun at ({SUN_X}, {SUN_Y}) kpc")
ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
        fontsize=9, verticalalignment="top", horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.75))

plt.tight_layout()
plt.savefig(out / "rave_100nearest_xgal_ygal.png", dpi=180, bbox_inches="tight")
```

## Notes
- RAVE DR6 has no parallax column — cannot compute distances natively
- SHboost24 source_id is Gaia DR2 format (int64); in the parquet it is the DataFrame index (NOT a column)
- RAVE DR6 `source_id` from `dr6_cnn` is also Gaia DR2
- No credentials needed for either RAVE TAP or SHboost parquet
- Use stdlib `xml.etree.ElementTree` for VOTable parsing; the isolated setup
  includes PyArrow for Parquet access over HTTPS.
- Some shell `curl` wrappers returned truncated RAVE TAP data (~241 rows). Use
  Python `urllib.request.urlopen()` instead; it was verified to fetch all
  426,574 rows across five batches.
- RAVE DR6 CNN crossmatch size: 522,981 stars; SHboost24: 1,701,553 stars; crossmatch yield: ~2,564 unique matches
- The Sun in SHboost24 coordinates is at (X_G, Y_G, Z_G) = (−8.178, 0.0, +0.020) kpc; plotting with the Sun at the origin uses X_off = X_G − (−8.178) so the Sun sits at (0, 0)
