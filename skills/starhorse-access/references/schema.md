# StarHorse product schemas (validated against the live services)

Validated 2026-07-20: SH21 via an anonymous ADQL query of `TAP_SCHEMA.columns` on
`https://gaia.aip.de/tap` (36 columns); SHboost-2024 via the Parquet footer of the
public S3 object (37 columns, 1,701,553 rows). Re-validation commands at the bottom.

## SH21 EDR3 — `gaiaedr3_contrib.starhorse` (gaia.aip.de TAP)

36 columns. All value columns are `float` (float32 — convert to float64 before chained
pandas boolean masks); the two `sh_*flag` columns are `char(80)` — compare with string
literals. Percentiles are posterior percentiles (05/16/50/84/95 = 5th…95th).

| Column(s) | Type | Unit | Description (TAP_SCHEMA) |
|---|---|---|---|
| `source_id` | long | — | Gaia EDR3 unique source identifier |
| `dist05 dist16 dist50 dist84 dist95` | float | kpc | StarHorse distance percentiles |
| `av05 av16 av50 av84 av95` | float | mag | line-of-sight extinction A_V at λ = 5420 Å, percentiles |
| `teff16 teff50 teff84` | float | K | effective temperature percentiles |
| `logg16 logg50 logg84` | float | log(g) | surface gravity percentiles |
| `met16 met50 met84` | float | dex | metallicity [M/H] percentiles |
| `mass16 mass50 mass84` | float | solMass | stellar mass percentiles |
| `ag50` | float | mag | extinction in G band A_G, median (from AV50 + teff50) |
| `abp50 arp50` | float | mag | extinction in G_BP / G_RP bands, median (from AV50 + teff50) |
| `bprp0` | float | mag | dereddened colour (G_BP − G_RP)₀ |
| `mg0` | float | mag | absolute G magnitude (recalibrated G, dist50, AG50) |
| `xgal ygal zgal` | float | kpc | Galactocentric Cartesian coords (R₀ = 8.2 kpc) |
| `rgal` | float | kpc | Galactocentric planar distance |
| `fidelity` | float | — | Gaia EDR3 **astrometric fidelity flag** (Rybizki et al. 2021); 0–1, `>= 0.95` for clean samples |
| `bp_rp_excess_corr` | float | — | BP/RP flux excess factor, corrected per Riello et al. 2021 |
| `sh_photoflag` | char(80) | — | photometry input flag (e.g. `GBPRPgrizy/JHKsW1W2`) |
| `sh_outflag` | char(80) | — | output flag, 4-char code (`'0000'` = 86%, full quality) |

Note vs. older notes: `met16` exists (the percentile triple is complete), and
`fidelity` is specifically the Rybizki et al. (2021) astrometric fidelity, not a
generic quality score.

## SHboost-2024 — public Parquet on S3

`https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet`
(~190 MB, single part). **1,701,553 rows × 37 columns.** No auth needed.

⚠️ Column naming differs from SH21 — there are **no** `*50`-style percentile columns
here. XGBoost point estimates are `xgb_*`; sampled-posterior mean/std are
`xgbdist_*_mean` / `xgbdist_*_std`. Temperature is **log10(Teff)** (`xgb_logteff`),
not Teff.

| Column(s) | Type | Meaning |
|---|---|---|
| `source_id` | int64 | Gaia source identifier |
| `xgb_av`, `xgbdist_av_mean`, `xgbdist_av_std` | float | A_V: point estimate; posterior mean/std |
| `xgb_logteff`, `xgbdist_logteff_mean`, `xgbdist_logteff_std` | float | log10(Teff): point estimate; mean/std |
| `xgb_logg`, `xgbdist_logg_mean`, `xgbdist_logg_std` | float | log g: point estimate; mean/std |
| `xgb_met`, `xgbdist_met_mean`, `xgbdist_met_std` | float | metallicity: point estimate; mean/std |
| `xgb_mass`, `xgbdist_mass_mean`, `xgbdist_mass_std` | float | mass: point estimate; mean/std |
| `dist`, `dist_lower`, `dist_upper` | float | distance with lower/upper bounds |
| `dist_flag` | int32 | distance-quality flag |
| `bprp0`, `mg0` | float | dereddened colour / absolute G magnitude (mag) |
| `xg yg zg rg` | float | Galactocentric position |
| `vxg vyg vzg vrg vphig` | float | Galactocentric velocity components |
| `xgb_inputflag` | string | input-photometry flag |
| `xgb_{av,logteff,logg,met,mass}_outputflag` | string | per-parameter output flags |

Physical units are not embedded in the Parquet footer; position/velocity/distance
units follow the SHBoost paper conventions (confirm citation before external release).

## Access caveats

- **TAP:** anonymous synchronous ADQL works (verified for schema + data queries); an
  account token (`Authorization: Token …`) unlocks the longer async queues (e.g.
  `queue="2h"` with `language='postgresql'`). See SKILL.md for both patterns.
- **S3:** plain public HTTPS GET, no credentials; the dataset is one Parquet part file.
- Nulls: ~1.4 % of SH21 rows lack `bprp0`/`mg0` — filter `.notna()` before plotting.

## Re-validation

```bash
# SH21 columns (anonymous):
curl -s "https://gaia.aip.de/tap/sync" \
  --data-urlencode "REQUEST=doQuery" --data-urlencode "LANG=ADQL" \
  --data-urlencode "QUERY=SELECT column_name, datatype, unit, description FROM TAP_SCHEMA.columns WHERE table_name='gaiaedr3_contrib.starhorse' ORDER BY column_index"
```

```python
# SHboost footer (needs pyarrow + fsspec):
import pyarrow.parquet as pq, fsspec
with fsspec.open("https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet", "rb") as f:
    pf = pq.ParquetFile(f); print(pf.metadata.num_rows, pf.schema_arrow)
```
