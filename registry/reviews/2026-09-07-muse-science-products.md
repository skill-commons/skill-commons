# MUSE science-products admission decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-07 (Europe/Berlin)

**Accountable maintainer and publication authority:** Tom Tong (`tomtong2015`), who
requested the skill and the complete CRS-then-Skill-Commons PR/squash-merge workflow.

**Technical assessment:** Codex inspected the complete source, dependencies,
capabilities, scientific references and redaction; separate agents implemented and
tested the helper, checked product contracts, and performed an independent forward
test. This does not claim an additional independent human review or independent
validation of the original instrument processing.

## Decision and exact source

Admit `muse-science-products` **1.0.0** at `curated` maturity, scoped to public AIP
MUSE science-product discovery, interpretation, plotting and caching. CRS and Skill
Commons are the continuing source steward and registry authority. The two bounded
demonstration workflows cover Orion physical maps and Antennae maps/catalogue
summaries; the reference explains how to assess further products without creating
a separate skill for each figure.

| Field | Value |
|---|---|
| Repository | `https://github.com/skill-commons/curated-research-skills` |
| Tracked default branch | `main` |
| Merged revision | `c8942427e748dedfc6ee158363d9c7766086c04b` |
| Directory | `skills/muse-science-products` |
| Git tree | `99b689dc4fe41320134f2957c9bacac95a43bd49` |

CRS PR 16 was squash-merged after its required `validate` check passed. The exact
directory tree was recomputed from the merged commit and matches the tested Hermes
submission packet. The complete tree contains `SKILL.md`, `LICENSE`,
`references/products.md`, and `scripts/muse_products.py`. No skill bytes or archive
products are copied into the registry.

The maturity decision reflects deliberate scientific and operational scope,
complete-tree review, independent technical exercise, repeatable regressions and
continuing stewardship. It does not follow automatically from repository membership
or successful tests.

## Evidence

- **Rights and attribution:** original instructions and helper are MIT-licensed and
  attributed to Tiantian Tong and Skill Commons contributors. The release's DataCite
  record declares CC0 for data; the skill distinguishes that from its own code license
  and cites the release DOI and Weilbacher et al. (2015, 2018). FITS sources are fetched
  on demand, not packaged as assets. No third-party source code was copied.
- **Redaction and capabilities:** the full installable tree was inspected, including
  request construction, parsing, HTML generation, setup commands and references. No
  embedded secrets, private material, machine-specific home paths or unfinished
  placeholders were found. The helper performs only public HTTPS GETs to seven fixed
  AIP source objects, plus local writes to a dedicated output bundle. It requires no
  credentials or remote mutation.
- **Source integrity and access:** each source is pinned by size and SHA256 and checked
  before FITS parsing. The helper validates table schema/row counts, image dimensions,
  BUNIT and celestial WCS. Reads have connect/read timeouts and product-specific byte
  bounds (all below 32 MiB); redirects and ambient proxy/netrc credentials are disabled.
  All sources must pass validation before output files are written. Output paths reject
  symlinks, installed-skill locations and unrelated contents. Modified/incomplete caches
  fail before replay writes or network refresh; there is no broad cleanup.
- **Packaging:** CRS validation and the current Hermes `prepare-submission` contract
  accepted the four files, astronomy category, metadata and selection lead with no
  warnings, using the client from drp-hermes commit
  `8ec000bfa43108f9d7898d0cb62f5eb6a199e5e6`. Generic Codex validation rejects the Hermes-required top-level `author`
  and `version`; the authoritative CRS/Hermes contract accepts and requires them.
- **Portable setup:** fresh isolated macOS ARM64 CPython 3.12.4 environments succeeded,
  including the independent tester following the documented setup. Dependency checks
  passed. Pip and uv recipes have identical direct pins: Astropy 8.0.1, NumPy 2.5.1,
  Matplotlib 3.11.1 and requests 2.34.2. Existing `.venv` path refusal and direct-import
  coverage are regression-tested; no shared Ori environment was modified.
- **Regression and CI:** 471 CRS tests passed with one unrelated opt-in NIFTy integration
  skipped, including 76 MUSE cases. Coverage exercises credential-free bounded reads,
  exact source identity, all-source validation before writes, cache corruption/missing
  artifacts with no mutation, network-free replay, finite JSON, escaped HTML, and
  row/column preservation with explicit S/N exclusions. Repository and explicit helper
  Ruff lint/format checks passed. Required CRS PR 16 CI passed. Deterministic tests use
  stub transports and lightweight scalar dependencies; live scientific execution is
  separate evidence, not implied by those unit tests.
- **Scientific contracts:** all seven source FITS files and both release papers were
  inspected. Orion temperature/density units absent from BUNIT are documented from the
  paper, with published median smoothing retained. Signed barycentric velocities are
  retained; exact-zero Orion velocity masking is labelled as presumed footprint fill,
  not a released quality flag. Antennae velocity binning targets Hα S/N about 30 and is
  not described as a hard per-pixel threshold. The Gaussian-fit map retains native
  per-spaxel units and is not internally extinction-corrected.
- **Table arithmetic:** independent checks compared all 31,512 original values
  (606 rows × 52 columns) with the exported CSV. All source rows remain, with field and
  source-row identity plus explicit inclusion/reasons. The stated observed Balmer-line
  S/N selection retains 549/551 central and 52/55 southern regions. Selected median
  corrected Hα luminosities are approximately 4.4812e37 and 3.8782e36 erg/s. Independent
  source inspection reconciled the missing 1e-20 scale in bare-cgs flux TUNIT against
  both published luminosity columns at 22 Mpc for every row. The helper uses published
  `LHa_cor` directly, does not double-apply that factor, and does not invent complete
  extinction-corrected luminosity uncertainties.
- **Independent forward test:** a separate agent followed the skill in a fresh
  workspace and checked the original FITS directly, without reusing the helper's
  analysis routines. All five maps matched raw counts, statistics and celestial WCS;
  all catalogue values and per-row selection reasons agreed. Final helper SHA256 was
  `bac9634638cc14860b764370ba96593509f6416e21c85ce40be8f545ff067196`.
  Both PNGs were visually inspected. Static HTML inspection verified a single embedded
  PNG and no remote active assets; browser-rendered HTML QA was unavailable because
  local-file navigation was denied, and no workaround was attempted.
- **Replay:** the final independent pass used a self-tested CPython audit hook blocking
  DNS and IPv4/IPv6 socket creation, including direct `_socket` entrypoints. Both
  `--offline` workflows made zero network attempts and retained byte-identical contents
  across all eight Orion and ten Antennae bundle files, including retrieval timestamps,
  HTML and provenance. The author's separate replay pass also passed. The helper records
  its source hash and direct-package metadata identity; changed runtime identities
  require fresh output bundles. This proves local replay of these snapshots, not
  cryptographically authenticated acquisition timestamps or universal reproducibility.
- **Registry verification:** all 42 registry tests, Ruff lint/format, deterministic
  catalogue checks, package build and whitespace checks passed. Live upstream
  verification reported all 27 records as current, including this exact landed MUSE
  revision and tree. Existing source records and consolidation entries are unchanged.

## Scientific and operational limits

The workflow visualizes published derived products. It does not reduce raw MUSE data,
extract spectral cubes, refit lines, independently derive temperatures/densities or
infer ages, star-formation rates or escaping ionizing radiation. Map medians summarize
correlated pixels and published smoothing; stars, mosaic artifacts and extreme failed
fits can remain. Robust display limits are separated from validity exclusions.

The Antennae ECDF compares selected catalogue samples, not completeness-matched
populations or a corrected luminosity function. No significance or causal conclusion
is attached. Table indexing origins were not established for image overlays. Corrected
flux errors do not establish full luminosity uncertainties. The alternative narrow-band
Hα map has an unresolved order-of-magnitude normalization discrepancy; the default uses
the Gaussian-fit map instead and documents why no empirical rescaling is applied.

Live execution covers one OS/Python configuration and these seven pinned products.
Additional products require explicit contract inspection. Direct package pins are not
a transitive lock, and cross-platform byte-identical rendering is not claimed. Networks
requiring an ambient proxy need a separately reviewed access recipe. HTML was statically
checked and figures visually checked; a browser-rendered HTML inspection is not claimed.

Admission is not runtime permission or pod deployment. The publication changes no live
Ori installation, vendored skill content or production image. Consumers refresh the
registry and install through the normal runtime workflow.

## References

- [Merged CRS PR 16](https://github.com/skill-commons/curated-research-skills/pull/16)
- [Successful CRS CI](https://github.com/skill-commons/curated-research-skills/actions/runs/34077004303)
- [Exact assessed skill](https://github.com/skill-commons/curated-research-skills/tree/c8942427e748dedfc6ee158363d9c7766086c04b/skills/muse-science-products)
- [AIP MUSE Science Data](https://data.aip.de/projects/musescience.html)
- [Release rights metadata](https://api.datacite.org/dois/10.17876/data/2023_3)
- [Orion paper](https://doi.org/10.1051/0004-6361/201526529)
- [Antennae paper](https://doi.org/10.1051/0004-6361/201731669)
- [Review policy](../../docs/adr/0003-review-maturity-and-evidence.md)
