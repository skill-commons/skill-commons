# Gaia and RAVE spectrum update decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-05

**Accountable maintainer:** Tom Tong (`tomtong2015`)

**Technical assessment:** Codex, at the maintainer's request. This record does not claim
an additional independent human review or independent scientific reproduction.

## Decision and exact identity

Retain `curated` maturity for these two explicitly assessed trees in the canonical CRS
repository, after its spectrum additions and Ori author-guide compatibility corrections
landed on `main` at `607b1963d4ea0def94de8e259f5a7315f2e54aa5`:

| Skill | Version | Path | Git tree |
|---|---:|---|---|
| `gaia-dr3-tap-query` | `3.1.1` | `skills/gaia-dr3-tap-query` | `2fd8e4fdde6a8c599f9dd9487204c62e75b89460` |
| `rave-dr6` | `2.1.1` | `skills/rave-dr6` | `47b11565545857c2478f5137b0f0f4aefabd738b` |

This is a new, scoped decision for changed trees, not automatic advancement with CRS
`main`. The registry previously recorded Gaia 3.0.1 and RAVE 2.0.1; the intermediate
spectrum releases were merged upstream but were not yet registered. The continuing
steward remains Skill Commons. These are extensions of the catalog-access skills, not
separate skills for individual stars or demonstration plots.

## Evidence scope

- **Identity, provenance, rights:** the exact commit and directory hashes were resolved
  from merged CRS source and matched to the complete locally assessed directories. The
  existing authorship, MIT licenses, and canonical public source are retained. Source
  references identify archive documentation, data DOIs, scientific conventions, and Gaia
  attribution requirements; the software license does not grant additional data rights.
- **Packaging:** each complete directory contains five files, including its license,
  references, and in-tree executable helper. CRS validation and the current
  `hermes-commons prepare-submission` contract passed without selection warnings. Those
  packets were local validation artifacts, not duplicate skill submissions. Both
  descriptions fit within Hermes' short selection surface; no prerequisite block,
  external-clone wrapper, or Skill Commons metadata sidecar was introduced.
- **Environment and non-mutation:** both pip and uv setup recipes use a new isolated
  Python 3.12 workspace environment, stop on setup failure, and refuse existing paths
  including files, directories, symlinks, and dangling symlinks. Sixteen regression cases
  execute those refusal paths and verify preservation. Direct-import checks cover both
  helpers, including Gaia's newly explicit `requests==2.34.2` pin and RAVE's
  `astropy==8.0.1` pin. Pin-parity checks cover the pip/uv recipes. Instructions keep
  environments and outputs outside installed skill directories and do not modify the
  agent's shared environment.
- **Security and side effects:** the changed skill trees received a redaction and
  capability review; no embedded credentials, private datasets, prompts, or transcripts
  were found. The bounded public helpers make archive queries and local cache/plot writes,
  with no archive uploads. RAVE validates its official FITS path and limits downloads to
  10 MiB. Gaia validates source/product identity, arrays, units, and cache hashes, and
  stops with documented fallback guidance rather than creating authenticated SJS jobs.
  The existing Gaia REST fallback still has separate session/job side effects documented
  in its reference; those are not exercised by the sampled-spectrum helper.
- **Regression evidence:** CRS PR 12 passed its required `validate` CI. Local checks
  passed Ruff lint/format, generated inventory validation, and 171 tests; one unrelated
  opt-in NIFTy integration was skipped. Spectrum regressions cover invalid identifiers,
  product/array validation, wavelength and error handling, and bounded download behavior.
- **Fresh setup and live execution:** on macOS ARM64 with CPython 3.12.4, the exact Gaia uv
  recipe and RAVE pip recipe installed into separate clean workspaces and passed their
  dependency checks. Live Gaia retrieval for source `5722622022989721600` produced 2401
  RVS bins (2400 valid, preserving the missing final bin) and 343 valid sampled XP bins.
  Live RAVE retrieval for observation `20100313_0823m14_113` produced 984 bins. The raw
  products, CSV derivatives, provenance, and rendered PNGs were read back and checked.
  RAVE's CSV wavelengths and flux/error columns matched the FITS arrays and header;
  Gaia's artifact hashes matched provenance.
- **Cache reproducibility:** both Gaia products were replayed with the retrieval function
  replaced by a network-failure sentinel. They reused the cache successfully and retained
  the original retrieval timestamps. RAVE caches FITS but still fetches TAP metadata;
  this assessment does not claim a fully offline RAVE helper.
- **Scientific scope:** the skills distinguish normalized RAVE/RVS flux from physical XP
  flux density, fractional RAVE errors from Gaia absolute errors, and air from vacuum
  wavelengths. They preserve missing samples and warn against duplicate radial-velocity
  corrections. Successful retrieval and plotting establish software behavior, not the
  scientific correctness of every archive value, target-selection cut, or inference.
- **Registry validation:** regenerated catalog views, Ruff lint/format, and 39 registry
  tests passed. The live upstream check reported all 23 active entries as current,
  including exact metadata and source identity for these two newly registered trees.

## Limitations and client implications

- Direct pins are not transitive locks or artifact-hash locks. Index configuration,
  platform, interpreter patch version, and package availability remain client-controlled.
  Clean setup was exercised through one installer per skill, not every installer/platform
  combination. Compatibility with Ori's shared agent environment is not claimed.
- Live archive evidence covers one selected source/observation, not survey-wide quality,
  every FITS variation, continuous XP reconstruction, or authenticated SJS execution.
  Archive schema, availability, and array serialization can change.
- The RAVE FITS headers do not declare `SPECSYS`; the documented stellar-rest air-wavelength
  interpretation retains that caveat. Cross-survey overlays require explicit wavelength
  convention conversion, identity verification, and appropriate resolution treatment.
- No independent scientific reproduction is claimed. The existing Gaia catalog and REST
  workflows and RAVE crossmatches retain their earlier scope; this focused assessment did
  not rerun every possible catalog or authenticated workflow.
- Registry publication is not pod deployment. Clients must refresh their registry cache;
  an existing skill directory is not overwritten by `hermes-commons install`. Runtime
  installs and locally edited copies require an explicit, preservation-aware update.
  No vendored image content, image pin, or live user installation was changed here.

## References

- [RAVE spectrum addition, CRS PR 10](https://github.com/skill-commons/curated-research-skills/pull/10)
- [Gaia spectrum addition, CRS PR 11](https://github.com/skill-commons/curated-research-skills/pull/11)
- [Ori setup corrections, CRS PR 12](https://github.com/skill-commons/curated-research-skills/pull/12)
- [CRS PR 12 validation run](https://github.com/skill-commons/curated-research-skills/actions/runs/33970468961)
- [Exact merged CRS source](https://github.com/skill-commons/curated-research-skills/tree/607b1963d4ea0def94de8e259f5a7315f2e54aa5)
- [Previous Python-environment decision](2026-08-11-crs-python-environments.md)
- [Review-maturity policy](../../docs/adr/0003-review-maturity-and-evidence.md)
