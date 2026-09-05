# PEPSI stellar-atlas admission decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-06 (Europe/Berlin)

**Accountable maintainer:** Tom Tong (`tomtong2015`)

**Technical assessment:** Codex, with separate agent-assisted contract, code, and
regression-test passes, at the maintainer's request. This is not a claim of an additional
independent human review or independent scientific reproduction.

## Decision and exact identity

Admit `pepsi-spectra` **1.0.0** at `curated` maturity, scoped to the public PEPSI Paper II
`cont_v2` normalized stellar atlas. The canonical source and continuing steward are CRS
and Skill Commons. The exact assessed identity is:

- Repository: `https://github.com/skill-commons/curated-research-skills`
- Default branch: `main`
- Merged commit: `5e368912f83725338ee6835076beb8304824baeb`
- Path: `skills/pepsi-spectra`
- Directory tree: `2d524aaac026be4f9d8c28dfa59ce65a372fd881`

The complete four-file directory contains `SKILL.md`, `LICENSE`, `references/atlas.md`,
and `scripts/pepsi_spectrum_demo.py`. The tree hash matched the current Hermes staging
contract before merge and was resolved again from the landed CRS commit. The registry
does not vendor those files or any archive spectrum.

This maturity decision rests on deliberate scope and safety curation, a continuing
steward, inspected complete source, bounded operational evidence, and repeatable
regressions. It is not inferred from repository membership. A selected star or zoom is
an example of the reusable atlas workflow, not a separate skill.

## Evidence

- **Authorship, rights, provenance:** original skill code/instructions carry the existing
  CRS MIT license and contributor attribution. Archive and primary-paper references
  explain the product source and scientific conventions. No archive FITS bytes or other
  research dataset are distributed in the skill. No dataset-specific open license was
  identified, and the skill explicitly avoids extending its software license to the data.
- **Discovery and packaging:** the description fits Hermes' short selection surface;
  all support files are referenced by path. CRS category/grouping and generated-inventory
  validation passed. The current `hermes-commons prepare-submission` contract staged all
  four files without selection warnings. There is no prerequisite block, external code
  clone, unfilled template, or Commons sidecar inside the skill.
- **Dependency contract:** the skill pins Astropy 8.0.1, NumPy 2.5.1, and Matplotlib 3.11.1
  in a fresh isolated Python 3.12 workspace environment. Both pip and uv recipes have
  matching direct pins and refuse pre-existing directories, files, and symlinks. Tests
  verify non-mutation and direct-import coverage. The documented uv recipe installed
  successfully into a clean macOS ARM64/CPython 3.12.4 environment and passed its package
  compatibility check. Shared Ori environments and installed skill directories were not
  modified. Backup/reconstruction requirements are disclosed.
- **Security/capabilities:** source inspection and redaction review found no embedded
  credentials, private material, or executable instructions copied from remote responses.
  The helper performs bounded public HTTPS reads from exact Paper II catalog/product
  paths, refuses redirects, limits each index to 256 KiB and a product to 32 MiB, and
  writes a dedicated workspace evidence bundle. It validates catalog rows, identity,
  FITS schema, and cache hashes before use. It performs no archive upload, publication,
  instrument control, raw-data reduction, or private-data access.
- **Independent technical findings:** a separate pass checked official CSV indexes,
  link-building JavaScript, release documentation, the paper, and two actual FITS
  products. It confirmed the nonstandard mask bytes and undocumented polarity. A
  code-review pass found duplicate CSV headers could overwrite metadata silently; this
  was corrected with a failing-then-passing regression before publication.
- **Regression/CI:** CRS PR 13 passed the required `validate` check. The complete suite
  passed 298 tests, with one unrelated opt-in NIFTy integration skipped. PEPSI-specific
  coverage includes URLs/redirects, response bounds, malformed/duplicate catalog fields,
  exact selection, numeric validity, variance, unknown mask states, gap preservation,
  offline cache identity/corruption, and dependency-free help. The helper also passed an
  explicit Ruff lint/format check in addition to repository checks.
- **18 Sco execution/readback:** live discovery and retrieval produced 433,381 native
  rows, including 2,906 samples in 5160–5190 Angstrom. All exported wavelengths,
  intensities, variances, sigma values, raw mask bytes, and numeric-validity flags matched
  the raw FITS-derived values. The PNG was inspected and provenance hashes verified.
  Original FITS SHA256 was
  `2a1a90f2f70fbf56f36b9001106cb4ca81f9e7837dedbe37f34a5e917f255260`.
- **Cache reproducibility:** a replay with socket connection and DNS operations blocked
  succeeded, preserving the original retrieval timestamp, raw/catalog/cache modification
  times, and identical FITS/CSV/PNG hashes. This is the scope of `reproducibility: tested`,
  not a claim of a complete transitive dependency lock or cross-platform bit identity.
- **Second target:** Arcturus (`α Boo`) retrieved 435,550 rows; its Ca II region was
  rendered and inspected. All CSV native-grid values and derived uncertainties were
  checked against FITS, and cached replay was exercised.
- **Registry validation:** all 40 registry tests passed, as did Ruff lint/format and
  generated-catalog checks. Live upstream checks resolved all 24 entries as current,
  including this skill's exact merged commit and directory tree.

## Scientific boundaries and limitations

The skill preserves the distinction between `Var` and sigma, normalized intensity and
absolute flux, air and vacuum wavelengths, and native sampling and resolving power.
It does not shift already corrected stellar-rest-frame wavelengths again. Combined
header dates remain strings, not a single physical observation epoch. The release's
Adler32-labelled `CHECKSUM` is not represented as a standard FITS checksum proof.

Most importantly, inspected `Mask` columns store numeric byte `0x01` despite FITS
logical declarations. Astropy's ordinary Boolean view is not a reliable interpretation.
The helper uses Astropy 8 raw-logical-byte access, retains the observed uniform state,
and makes **no mask-based exclusion or good-pixel claim**. This limitation appears on
the plot and in provenance. Unknown or mixed bytes stop the helper; a documented
producer mapping would be needed to extend that behavior.

Further limitations:

- The release contains 48 catalog entries, but live scientific execution was sampled
  on 18 Sco and Arcturus, not every star or future product variation.
- The direct pins are not transitive/artifact locks. Fresh setup was tested with uv on
  one macOS/Python configuration; a complete pip/platform matrix is not claimed.
- Gap splitting at ten times the median native spacing is a display heuristic, not
  an instrument quality flag. Full original samples remain available.
- Pixel variance omits some continuum, telluric, calibration, and other systematic
  effects. Retrieval and plotting do not establish abundance precision, validate every
  archive value, or constitute independent scientific reproduction.
- Other PEPSI releases, unrefined products, raw-data reduction, instrument operations,
  and private data are outside this release's helper scope.
- Registry admission is not runtime permission or pod deployment. No image pin, vendored
  skill, or live Ori installation was changed. Clients must refresh the registry before
  installation and preserve any existing local copy when considering an update.

## References

- [CRS PR 13](https://github.com/skill-commons/curated-research-skills/pull/13)
- [Required CRS CI run](https://github.com/skill-commons/curated-research-skills/actions/runs/33997191234)
- [Exact assessed source](https://github.com/skill-commons/curated-research-skills/tree/5e368912f83725338ee6835076beb8304824baeb/skills/pepsi-spectra)
- [Official Paper II release](https://pepsi.aip.de/?page_id=552)
- [Strassmeier, Ilyin & Weber 2018](https://doi.org/10.1051/0004-6361/201731633)
- [Review-maturity policy](../../docs/adr/0003-review-maturity-and-evidence.md)
