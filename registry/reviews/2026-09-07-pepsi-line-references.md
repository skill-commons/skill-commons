# PEPSI line-identification update decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-07 (Europe/Berlin)

**Accountable maintainer and publication authority:** Tom Tong (`tomtong2015`), who
co-authored the upstream PR with Claude, requested Codex's corrections, squash-merged
CRS PR 15, and requested this registry PR and administrator squash merge.

**Technical assessment:** Codex inspected the final source changes, scientific
references, packaging and validation evidence. No new independent human technical
review or independent reproduction of stellar physics is claimed.

## Decision and exact source

Retain `pepsi-spectra` at `curated` maturity for **1.0.1**, scoped to the public PEPSI
Paper II `cont_v2` normalized stellar atlas. CRS and Skill Commons remain the source
steward and registry authority.

- Repository: `https://github.com/skill-commons/curated-research-skills`
- Tracked default branch: `main`
- Merged revision: `02a9fea5f86d520f33416f62bc6254349d309cc0`
- Directory: `skills/pepsi-spectra`
- Git tree: `cdaccd2dfceb315e7491fe4bc2c87368d1089447`

The tree was recomputed from the landed PR 15 commit and matches the tested Hermes
submission packet. It contains five files: `SKILL.md`, `LICENSE`, `references/atlas.md`,
`references/lines.md`, and `scripts/pepsi_spectrum_demo.py`. The registry copies no
skill contents or spectra.

This decision builds on the [1.0.0 admission](2026-09-06-pepsi-spectra.md), preserving
its scoped rights, security, setup and runtime evidence. Git comparison confirms the
helper, atlas reference and license are unchanged. The only skill changes are the
entrypoint's version/identification guidance and the new line reference. Retained
maturity reflects that bounded review and continuing stewardship, not an automatic
promotion or an assertion that every generated interpretation is correct.

## New evidence and behavior

- **Scientific correction:** line identifications require the sourced table or a line
  list actually queried during the session; other features remain unidentified.
  References distinguish Mg I b1/b2/b4 from Fe I b3 and identify the excited lower Mg
  term. NIST supplies the Mg wavelengths/levels, including 5167.322 Å. Moore's historical
  Fe I value is explicitly for identification, not a modern precision-velocity reference.
  Sodium wavelengths and explicitly labelled Ca II K/H wavelengths have citations.
- **Measurement interpretation:** a reference must be compared with a measured or
  fitted core, not an arbitrary grid point. Local sampling and gaps are inspected;
  justified sub-pixel fitting is permitted. Formal fitting precision is distinguished
  from absolute accuracy, with noise, blends, calibration and reference uncertainty
  requiring consideration. Unassessed uncertainties do not support physical-shift claims.
- **Provenance and rights:** the new reference cites public scientific sources and
  provides a verification date. It retains the existing MIT code/instruction license,
  authorship and archive attribution. Review found no embedded credentials, private
  material, machine-specific paths or unfinished templates. No external source code,
  archive data or complete third-party documents were added.
- **Capabilities and dependencies:** retrieval/rendering code, network destinations,
  output behavior and direct dependency pins are byte-identical to 1.0.0. The new
  instructions permit line-list consultation but do not supply credentials, authorize
  remote writes, or claim a new general line-fitting implementation.
- **Packaging and tests:** the current Hermes submission client accepted all five
  files without warnings, with the exact tree above. Native CRS inventory checks,
  Ruff lint/format and whitespace validation passed. The full merged-base suite passed
  471 tests, with one unrelated opt-in NIFTy integration skipped. Required CRS PR 15
  `validate` CI passed on the corrected head before the maintainer merged it. Generic
  Codex validation rejects the existing Hermes-required `author` and `version` fields;
  the native CRS/Hermes validator is the applicable packaging contract.
- **Registry validation:** all 42 registry tests, Ruff lint/format, generated-catalog
  checks, package build and whitespace checks passed. Live upstream verification
  reported all 27 records current. Only the PEPSI record changed; other source pins,
  categories and consolidation entries are preserved.

## Retained evidence and limitations

The previous admission's live 18 Sco/Arcturus retrieval, raw-data readback and blocked
network replay remain evidence for the unchanged helper. They were not rerun for this
documentation update. `operability: tested` and `reproducibility: tested` retain that
explicit historical scope; they do not mean automated narrative identification was
scientifically reproduced in this update.

Mask polarity remains undocumented, only the observed uniform raw `0x01` state is
supported, and no mask-based good-pixel claim is made. Fresh setup/live execution was
sampled on macOS ARM64 CPython 3.12.4, not a platform matrix or all stars. Direct pins
are not transitive locks. A dataset-specific redistribution license and independent
scientific reproduction are not claimed. The skill's MIT license does not cover spectra.

The table's printed digits do not establish laboratory uncertainty, and historical
compilations must not silently become modern velocity zero points. Instructional
guardrails reduce a known narrative failure; they do not guarantee agent compliance,
unblended features, abundance precision or reliable physical shifts.

This registration grants no runtime permission and changes no live Ori installation,
vendored skill or production image. Consumers use their normal registry refresh/update
workflow and preserve any locally modified skill.

## References

- [Merged CRS PR 15](https://github.com/skill-commons/curated-research-skills/pull/15)
- [Successful corrected-head CI](https://github.com/skill-commons/curated-research-skills/actions/runs/34105514800)
- [Exact assessed source](https://github.com/skill-commons/curated-research-skills/tree/02a9fea5f86d520f33416f62bc6254349d309cc0/skills/pepsi-spectra)
- [NIST Mg I](https://physics.nist.gov/PhysRefData/Handbook/Tables/magnesiumtable3_a.htm)
- [Moore, NBS Technical Note 36](https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote36.pdf)
- [Line-centroid methodology](https://arxiv.org/abs/1809.10295)
- [Review policy](../../docs/adr/0003-review-maturity-and-evidence.md)
