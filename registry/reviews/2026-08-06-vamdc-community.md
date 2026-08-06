# VAMDC community admission decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-08-06

**Accountable reviewer:** Tom Tong (`tomtong2015`)

## Decision

The `vamdc` skill is admitted at **`community`** review maturity. The decision is bound
to the complete `skill/` directory in the exact source identity below:

| Field | Value |
|---|---|
| Repository | `https://github.com/VAMDC/pyVAMDC` |
| Revision | `bfefc812782d055c5f54c6105a394d6d34e13815` |
| Path | `skill` |
| Git tree | `7db98d33cc99a8ae220f1585f69d49d15a04bf4c` |

Carlo Maria Zwölf confirmed that the VAMDC repository is the skill's canonical home.
The maintainers then merged the focused portability, attribution, and partial-result
disclosure changes in VAMDC/pyVAMDC pull request 11. The skill remains wholly upstream;
Skill Commons records only its exact source coordinates and this review decision.

`community` means the skill passed the Commons admission floor. It does not claim that
the complete tree, dependencies, scientific outputs, or every remote node completed the
independent procedure required for `reviewed` maturity.

## Evidence scope

- **Provenance and maintenance:** the upstream maintainer confirmed the canonical public
  source and merged the assessed contribution. The pinned revision is the merge commit
  on the repository's default branch, and the directory tree was recomputed from Git.
- **Rights:** the skill names the Observatoire de Paris authors and declares EUPL-1.2.
  These agree with the project metadata and the license bundled in the skill directory.
- **Packaging:** `skill/` contains `SKILL.md`, `LICENSE.txt`, and the referenced
  `references/parameter_guide.md`; it has no broken local dependency or copied Commons
  sidecar.
- **Capabilities and security:** the skill describes network queries to VAMDC nodes and
  the RADEX API, local result and diagnostic-log writes, local cache refresh or clearing,
  and potentially recursive line queries. No credential is required or embedded. The
  accepted-truncation path requires an explicit user choice and labels confirmed partial
  results.
- **Operability:** a clean `uv sync --extra dev` succeeded with CPython 3.11.15 at the
  pinned merge commit. All 21 collected tests passed, and the focused CLI test file
  passed Ruff. Repository-wide lint cleanliness is not claimed or required for this
  admission level.
- **Scientific validity:** supported workflows and count-before-download boundaries are
  documented. The review confirmed disclosure behavior for partial results but did not
  independently reproduce the scientific correctness of data returned by every VAMDC
  node.
- **Reproducibility:** the exact source and skill tree are pinned and the clean install
  was repeated. Project dependencies use version ranges rather than a committed,
  cross-platform resolution lock.

## Limitations

- Independent scientific validation across VAMDC nodes and returned datasets is not
  claimed.
- The recorded install evidence covers one current Python 3.11 environment and a
  range-based dependency resolution, not every supported Python version and platform.
- Availability, completeness, and node-reported truncation metadata depend on external
  VAMDC services. Users must still inspect result provenance and suitability for their
  scientific purpose.
- Review maturity does not authorize network access, local writes, cache deletion, or
  execution in a particular environment.

## References

- [Maintainer confirmation](https://github.com/VAMDC/pyVAMDC/issues/10#issuecomment-5197047268)
- [Merged upstream change](https://github.com/VAMDC/pyVAMDC/pull/11)
- [Pinned skill directory](https://github.com/VAMDC/pyVAMDC/tree/bfefc812782d055c5f54c6105a394d6d34e13815/skill)
- [Review-maturity policy](../../docs/adr/0003-review-maturity-and-evidence.md)
