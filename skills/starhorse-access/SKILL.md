---
name: starhorse-access
description: Access StarHorse data products including SHboost-2024 and the SH21 EDR3 catalog via gaia.aip.de
  TAP.
license: MIT
compatibility: Linux x86_64 with CPython 3.12; requires declared HTTPS access.
metadata:
  research-skill.manifest: research-skill.yaml
---

# StarHorse Access — SHboost-2024 & SH21 EDR3

## When to Use
Use this skill for ANY StarHorse-related data work. Two products:

1. **SHboost-2024** — XGBoost-approximated posteriors, public Parquet on S3
2. **SH21 EDR3** — Full Bayesian StarHorse posteriors for Gaia EDR3, via gaia.aip.de TAP

## Data Papers & Acknowledgment
Cite the source papers in any work using these products:
- **SH21 EDR3** — Anders, Khalatyan, Queiroz et al. 2022, *A&A* **658**, A91.
- **SHboost-2024** — Khalatyan, Anders, Chiappini et al. 2024, *A&A* **691**, A98.

These are access instructions only; the catalogs remain the authors' work under their
own terms. Follow the gaia.aip.de data-acknowledgment policy when publishing.

## Quick Decision
- **Nearby stars (< 20 pc), quick CMD** → SHboost-2024 (fast, local parquet)
- **Full catalog, CMDs, posteriors, flags** → SH21 EDR3 TAP (gaia.aip.de)
- **Rave DR6 crossmatch** → Use SH21 via TAP (SHboost has low crossmatch rate ~0.15%)

## Access Patterns

### SHboost-2024 (Parquet, public S3)
```bash
# Public HTTP — no auth needed
wget -O shboost.parquet "https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet"
```
~190 MB, 1,701,553 rows × 37 columns. Columns: `source_id`, `xgb_{av,logteff,logg,met,mass}` point estimates + `xgbdist_*_mean/std` posteriors, `dist`/`dist_lower`/`dist_upper`/`dist_flag`, `bprp0`, `mg0`, `xg/yg/zg/rg` + `v*g` velocities, string flags. **No `*50` percentile columns here (those are SH21 names); `xgb_logteff` is log10(Teff).** Full schema: `references/schema.md`.

### SH21 EDR3 (gaia.aip.de TAP, PostgreSQL)
```python
import requests, pyvo as vo, pandas as pd

def get_one_query(qstr, verbose=False):
    url = 'https://gaia.aip.de/tap'
    token = ""  # or "Token XXX" from gaia.aip.de account
    tap_session = requests.Session()
    tap_session.headers['Authorization'] = token
    tap_service = vo.dal.TAPService(url, session=tap_session)
    job = tap_service.submit_job(qstr, language='postgresql', runid='pybatch', queue="2h")
    job.run()
    job.raise_if_error()
    job.wait(phases=["COMPLETED", "ERROR", "ABORTED"], timeout=10.)
    if job.phase in ("ERROR", "ABORTED"):
        raise RuntimeError(f"Job {job.job.runid} failed: {job.phase}")
    return job.fetch_result().to_table().to_pandas()

# Example: CMD hexbin (200k stars, ~17s on gaia.aip.de)
df = get_one_query("select bprp0, mg0 from gaiaedr3_contrib.starhorse limit 200000")
```

### Alternative: ADQL via `run_sync()`
For moderate queries, ADQL is simpler:
```python
tap = vo.dal.TAPService("https://gaia.aip.de/tap")
result = tap.search("SELECT TOP 200000 source_id, bprp0, mg0, dist50, av50, fidelity FROM gaiaedr3_contrib.starhorse")
df = result.to_qtable().to_pandas()
```

## Full SH21 Schema (36 columns, verified 2026-06-30)

| # | Column | Description | # | Column | Description |
|---|--------|-------------|---|--------|-------------|
| 1 | source_id | Gaia EDR3 source ID | 2 | dist05 | 5th %ile distance (kpc) |
| 3 | dist16 | 16th %ile distance (kpc) | 4 | dist50 | median distance (kpc) |
| 5 | dist84 | 84th %ile distance (kpc) | 6 | dist95 | 95th %ile distance (kpc) |
| 7-11 | av05–av95 | A_V percentiles | 12-15 | teff16–teff84 | Teff percentiles (K) |
| 16-18 | logg16–logg84 | log g percentiles | 19-20 | met16–met84 | [M/H] percentiles |
| 21-23 | mass16–mass84 | Mass percentiles (M☉) | 24 | ag50 | median A_G |
| 25-26 | abp50, arp50 | median A_BP, A_RP | 27 | bprp0 | G_BP − G_RP colour |
| 28 | mg0 | Absolute G magnitude | 29-32 | xgal, ygal, zgal, rgal | Galactocentric coords (kpc) |
| 33 | fidelity | Quality score (0–1) | 34 | bp_rp_excess_corr | Excess factor correction |
| 35 | sh_photoflag | Photometry flag (VARCHAR) | 36 | sh_outflag | Output flag (VARCHAR) |

All float columns are float32. Convert to float64 before chained pandas boolean masks.

## Flag Columns (VARCHAR — always use string literals!)

**sh_outflag** — 4-character code:
- `0000` (86%) — full quality, converged, good photometry
- `0001`, `0010` — minor issues
- `0011`–`1111` — various flagged combinations
- `2000`, `2001` — LMC; `1000`, `1001` — SMC

**sh_photoflag** — photometry used: `GBPRPgrizy/JHKsW1W2`, `GBPRP/grizJHKs`, `GBPRP/grizJHKs`, `GBPRP`, `G`, etc.

⚠️ Compare with `'0000'` (string), NOT `0` (integer).

## Key Columns for CMD Work
- `bprp0` — G_BP − G_RP colour (mag)
- `mg0` — Absolute G magnitude (mag, inverted axis for CMD)
- `av50` — median A_V for dereddening
- `fidelity` — quality score 0–1; use `>= 0.95` for flag-cleaned sample

## Plotting: CMD Hexbin (reproduces paper Figure 5)
```python
fig, ax = plt.subplots(figsize=(7, 7))
hb = ax.hexbin(df['bprp0'], df['mg0'], gridsize=80, cmap='jet',
               norm=mpl.colors.LogNorm(), mincnt=1, edgecolors='none')
ax.invert_yaxis()
ax.set_xlabel(r'$G_{BP} - G_{RP}$')
ax.set_ylabel(r'$M_G$')
```

## Pitfalls
- **Pandas float32 boolean chaining**: `(df['col'] > 0) & (df['col2'] < 1)` — wrap EVERY comparison in parentheses for float32 columns.
- **ADQL vs PostgreSQL**: `get_one_query()` uses `language='postgresql'`. ADQL via `run_sync()` is simpler for routine queries.
- **`run_sync()` returns pyvo TAPResults, NOT DataFrame**. Use `.to_qtable().to_pandas()` or `pd.DataFrame({c: data[c] for c in data.colnames})`. Column names are in `.colnames`, NOT `.fieldnames`.
- **Run in foreground**. PostgreSQL TAP jobs on gaia.aip.de typically complete in ~17 s for 200 k rows (verified 2026-06-30), but use `timeout=300` to be safe. If you launch via `terminal(background=true)`, the job keeps running after the session ends and creates stray completion nudges. Run the query script in foreground.
- **Data quality: ~98.6 % valid rows**. A `LIMIT 200000` query returns ~197 k rows with non-null bprp0/mg0. The ~1.4 % nulls are stars lacking BPRP or MG photometry. Always check `.notna()` before plotting.
- **`submit_job` returns immediately; `job.run()` starts execution**. You must call both.
- **Timeout on `job.wait()` is per-wait**. If the first 10 s wait times out (job still processing), call `job.wait()` again in a loop or set a longer timeout.
- **No `LIMIT` syntax issue**. PostgreSQL dialect supports `LIMIT` natively. ADQL requires `TOP N` or `WHERE random_index < N`.
- **ADQL async endpoint may return 404**. If you see `/async/phase` 404 errors, switch to ADQL via `tap_service.search()` instead.
- **sh_photoflag and sh_outflag are VARCHAR**. Always compare with string literals.
- **All float columns are float32**. Convert to float64 before chained boolean masks.
- **`fidelity` is 0–1 continuous**. Use for quality cuts.

## Verification
- Data source and access path explicitly recorded.
- Key columns and caveats documented.
- SH21 schema verified 2026-06-30 against live gaia.aip.de TAP query.
- Full schemas re-validated 2026-07-20 against TAP_SCHEMA + the SHboost Parquet
  footer → `references/schema.md` (SHboost column list corrected: `xgb_*` naming,
  no `*50` columns).
- Data-paper citations + accountable curator/ORCID added 2026-07-21 (Skill Commons
  first-package publication prep).
