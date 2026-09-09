# Cluster CMD isochrone-fitting admission decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-09 (Europe/Berlin)

**Accountable maintainer and publication authority:** Tom Tong (`tomtong2015`), who
requested the reusable skill and explicitly authorized CRS review, PR and squash
merge followed by Skill Commons admission.

**Technical assessment:** Codex inspected the complete source, dependencies,
capabilities, scientific contracts and redaction. Separate agents investigated the
model and catalogue contracts, performed a bounded independent forward test, and
reviewed the exact installable source for this admission decision. This records
agent-assisted technical assessment under Tom Tong's publication authority; it does
not claim an additional independent human review or certification of stellar models.

## Decision and exact source

Admit `cluster-cmd-isochrone-fit` **1.0.0** at `curated` maturity, scoped to an
auditable geometric estimate of cluster CMD age from a supplied stellar-evolution
grid in matched Gaia passbands. The skill includes bounded public PARSEC and M67
retrieval adapters, an offline fitter, input contracts and sensitivity diagnostics.
Other clusters can supply the documented observation schema; M67 is a worked
example rather than a separate single-figure skill. CRS remains the continuing
source steward and Skill Commons the registry authority.

| Field | Value |
| --- | --- |
| Repository | `https://github.com/skill-commons/curated-research-skills` |
| Tracked default branch | `main` |
| Merged revision | `2e6762a0da8316e1995c872d49193cd770a42761` |
| Directory | `skills/cluster-cmd-isochrone-fit` |
| Git tree | `9da93a128e70ce0efdec34d6984abbd6d0ff0a3b` |

CRS PR 17 was squash-merged after its `validate` and dedicated CMD science checks
passed. The merged directory tree matches the assessed source and final Hermes
preparation packet. The complete eight-file tree contains `SKILL.md`, `LICENSE`,
`scripts/fetch_parsec.py`, `scripts/fetch_m67.py`, `scripts/fit_cmd.py`,
`references/parsec.md`, `references/m67.md` and `references/fitting.md`. No skill
bytes, model tables or catalogue data are copied into the registry.

The maturity decision rests on a supportable scientific scope, explicit limits,
complete-tree assessment, proportionate independent exercise, regression evidence
and continuing stewardship. It is not inferred automatically from source-repository
membership, numerical agreement with a literature age, or successful software tests.

## Evidence

- **Rights and attribution:** the original instructions and helpers are attributed
  to Tom Tong and Skill Commons contributors and include an MIT license. References
  distinguish this code license from catalogue and model-data terms, credit
  PARSEC/OBC, Gaia/DPAC, Hunt & Reffert and CDS/VizieR, and identify the corresponding
  literature. No explicit model redistribution license was found on the inspected
  CMD pages during development. Models are therefore fetched on demand and are not
  packaged or presented as MIT data. No third-party source code was copied.
- **Redaction and capabilities:** all eight installable files were inspected,
  including request construction, local output handling, parsers, scientific
  arithmetic, plots, setup commands and references. No embedded secrets, private
  observations, personal transcripts, machine-specific home paths or unfinished
  placeholders were found. Runtime fit reports record local input and helper paths;
  those user-workspace artifacts are outside the published skill and are not copied
  into this public decision. The fitter has no network implementation. The adapters
  use only named public services with no credentials: one fixed CDS TAP query and
  bounded sequential requests to official CMD with downloads from its constrained
  output URLs. CMD POSTs request temporary computational output; there is no account,
  catalogue or publication mutation.
- **Access and local side effects:** both adapters retain verified HTTPS, disable
  redirects and ambient proxies, and bound response sizes and network timeouts.
  PARSEC retrieval uses an argument-list invocation of system `curl`, with curl
  configuration disabled and no credential files. It limits each age/metallicity
  request to 600 curves, each bundle to 3,000 models and 256 MiB, and each model
  response to 32 MiB. The CDS query is capped at 5,000 rows and 3 MB and rejects a
  result reaching that row limit as possibly truncated. Fitting and catalogue
  conversion refuse existing output paths and writes inside the installed skill.
  PARSEC validates an existing bundle or stages a new one, refusing unexpected
  inventory and symlinks. There is no broad cleanup or shared-environment mutation.
- **Source integrity:** PARSEC manifests retain actual requests, intended grid,
  returned HTML, raw tables, retrieval times, model/filter/extinction identity,
  hashes and normalized data. Parsing rejects changed schemas, nonfinite values,
  missing or extra grid coordinates, noncontiguous curves, decreasing initial
  masses and an absent final terminator. Documented small service coordinate
  rounding is matched within an explicit tolerance while preserving original raw
  values. The catalogue adapter retains every returned member and exact source IDs,
  validates its fixed schema, propagates mean-flux errors and exports explicit
  quality-selection reasons. The fitter verifies declared CSV hashes, photometric
  compatibility, model order, selected measurements and malformed row widths.
- **Packaging and setup:** the final source passes CRS metadata, local-reference,
  category and generated-catalogue validation. Its native Hermes preparation packet
  accepts all eight files and the exact tree, using a client verified byte-identical
  to drp-hermes commit `fec12e5ca52136a65dbb3707ef43a90fdd62386f`. The generic Codex validator rejects
  the top-level `author` and `version` required by this Hermes-native repository;
  this schema mismatch is not described as a pass. Documented pip and uv recipes use
  fresh isolated CPython 3.12 environments and identical direct pins: NumPy 2.5.1,
  SciPy 1.18.0 and Matplotlib 3.11.1. Existing `.venv` paths, including symlinks, are
  refused. Direct-import and environment-guard regressions pass. These direct pins
  do not constitute a transitive lock.
- **Regression and CI:** the final local repository suite reports **512 passed,
  7 skipped**. Six skips require the separate CMD scientific runtime and one is the
  pre-existing opt-in NIFTy integration test. The pinned CPython 3.12 scientific and
  portable-environment suite reports **94 passed**, including all **38 CMD tests**.
  Repository and explicit helper Ruff lint/format checks and whitespace checks
  pass. Both CRS PR checks pass; the dedicated Linux scientific job also runs all
  38 CMD tests. Both workflows also pass on the merged `main` revision. Tests cover
  independent analytic weighted projection, invariance
  to curve sampling density, retained-phase gaps, two distinct synthetic age and
  distance recoveries, input identity/errors, grid incompleteness, source failures,
  malformed CSV, numerical replay and diagnostic output. These offline regressions
  do not imply live-service availability or universal scientific validity.
- **Scientific implementation:** the fitter searches real isochrones, uses exact
  nearest projections onto retained piecewise-linear CMD segments, and sums a
  declared Huber objective in color and magnitude. It keeps the observed fitting
  selection fixed across trial ages, respects removed model rows and phase gaps,
  and adds distance modulus only to already-extincted model magnitudes. Formal
  photometric errors and explicit metric floors remain distinct. It saves every
  trial score, per-star costs, residuals, selection reasons, model/input hashes,
  nuisance choices, bootstrap seed and runtime versions. Boundary, flat-profile,
  single-grid bootstrap and substantial Huber-tail diagnostics are explicit.
- **Real-data exercise:** the preserved broad PARSEC bundle contains 630 curves
  spanning log10(age/year) 9.00–10.00 in 0.05-dex steps, five initial metallicities
  and six extinction values. The observed source has 1,844 Hunt & Reffert Gaia DR3
  M67 members, of which 685 pass the independent adapter selection and 372 enter
  the declared baseline CMD window. The query excludes catalogue-derived ages and
  masses. An independently motivated distance modulus, extinction and near-solar
  composition are explicit conditional assumptions. The coordinator preserved the
  broad search, retrieved a real refined grid and completed twelve refined
  baseline/sensitivity runs. The baseline minimum is logAge 9.59, approximately
  **3.9 Gyr**; selected minima span **3.715–4.365 Gyr** without reaching an age
  boundary. This experimental range is not a confidence interval or an envelope
  of every systematic uncertainty.
- **Independent forward test:** a separate agent used only the skill, its
  references, supplied source bundles and a supplied pinned runtime in a separate
  workspace. It completed thirteen offline coarse-grid runs, inspected CMD and
  residual plots, and examined the per-star score contributions. Its conditional
  baseline was approximately 4 Gyr; it observed a substantial Huber-tail population
  and a boundary preference when freely profiling a limited distance range. It
  correctly withheld a new distance measurement, precise age error or posterior
  interpretation. It confirmed a corrected binary-line display without a numerical
  score change. This test did **not** independently install the runtime, retrieve
  online data, validate the refined grid or run the coordinator's twelve refined
  experiments. Subsequent final-source regression covers the added malformed-CSV
  guard; authorship and the bundled license do not alter successful fit arithmetic.
- **Numerical and replay controls:** separate real-PARSEC planted-age controls
  recovered logAge 9.2 and 9.7 with the planted distance modulus. Adding equal-mass
  binaries and arbitrary outliers shifted one fit by one coarse age step,
  demonstrating residual contamination bias. The preserved broad and refined
  acquisition bundles passed complete inventory/hash checks, raw reparsing and
  byte-identical normalized-CSV regeneration in offline mode. Fitting replay
  reproduces numerical results under the tested inputs and runtime; creation times
  and local paths are intentionally provenance, not byte-stable report content.


- **Registry validation:** all 43 registry tests pass, along with Ruff lint/format,
  deterministic catalogue checks, package build and whitespace checks. Live upstream
  verification reports all 28 registered records as current, including this exact
  merged CRS revision, directory tree and metadata. All 27 preceding source records
  and all consolidation entries are unchanged. The registry adds discovery and
  review metadata only.

## Scientific and operational limits

This is a geometric cluster-locus estimator. It does not implement a normalized
population likelihood, IMF/completeness weighting, binary population, field-star
mixture, full measurement covariance or Bayesian posterior. Conditional star
bootstrap quantiles do not include stellar-physics, atmosphere, calibration,
membership, selection, nuisance or shared-catalogue systematic uncertainty.
Neither robust-score differences nor the sensitivity range supply formal
confidence levels. Numerical success alone does not establish an age-sensitive
turnoff population or a scientifically resolved fit.

The live Gaia EDR3 request succeeded with **OBC**, not the advertised YBC options.
The source and documentation name this choice explicitly. OBC uses constant solar
extinction coefficients with Cardelli+O'Donnell R_V=3.1, an approximation for broad
Gaia bands and varying stellar spectra. The model includes extinction already; the
illustrative G2V coefficients in the service HTML are not substituted for returned
magnitudes. The fit remains conditional on nonrotating PARSEC 1.2S, its composition,
helium and phase conventions, and the chosen nuisance values. No second evolutionary
library or population-based uncertainty calibration was validated.

M67 contains unresolved binaries and blue stragglers, and substantial residual
model/sample mismatch remains. Gaia NSS zero and acceptable RUWE do not establish
singleness; HDBSCAN proximity is not a calibrated membership probability. An
equal-mass binary line is only a diagnostic. The worked cuts and nuisance constraints
are specific to this example and must not be transferred blindly to another cluster
or tuned to match a literature age. The former empirical-age demo artifacts were
not located; the new workflow replaces that method without claiming to have edited
or rerun the original notebook.

Live scientific execution is evidenced on macOS ARM64 CPython 3.12; Linux CI covers
offline regression. No broad platform, live Linux transport, browser-rendered HTML,
cross-platform byte-identical rendering or independent end-to-end refined-age
reproduction is claimed. CMD temporary links expire and fresh upstream responses
may change; preserve the raw reviewed bundles. Network environments requiring a
proxy need a separately assessed access recipe. Runtime provenance hashes detect
changes within the preserved artifacts, not independently authenticated acquisition
times or provider correctness.

Admission is not runtime permission or pod deployment. This publication changes no
live Ori installation, vendored skill content or production image. Consumers refresh
the registry and install through their normal runtime workflow.

## References

- [Merged CRS PR 17](https://github.com/skill-commons/curated-research-skills/pull/17)
- [Successful CRS validation](https://github.com/skill-commons/curated-research-skills/actions/runs/34352958298/job/102470465949)
- [Successful CMD scientific CI](https://github.com/skill-commons/curated-research-skills/actions/runs/34352958437/job/102470466395)
- [Exact assessed skill](https://github.com/skill-commons/curated-research-skills/tree/2e6762a0da8316e1995c872d49193cd770a42761/skills/cluster-cmd-isochrone-fit)
- [Official CMD service](https://stev.oapd.inaf.it/cgi-bin/cmd_3.9)
- [Hunt & Reffert catalogue](https://doi.org/10.26093/cds/vizier.36860042)
- [Review policy](../../docs/adr/0003-review-maturity-and-evidence.md)
