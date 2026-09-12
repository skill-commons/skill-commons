# Cluster CMD isochrone-fitting 1.0.1 review decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-12 (Europe/Berlin)

**Accountable maintainer and publication authority:** Tom Tong (`tomtong2015`),
who authorized completion of the citation correction, CRS squash merge and the
corresponding Skill Commons update. Codex performed the technical assessment under
that authority; this does not claim an additional independent human review.

## Decision and exact source

Update `cluster-cmd-isochrone-fit` to **1.0.1**, retaining `curated` maturity and the
existing evidence facets and scientific limits. This is a narrow correction to
literature attribution in the instructions and generated model provenance.

| Field | Value |
| --- | --- |
| Repository | `https://github.com/skill-commons/curated-research-skills` |
| Tracked default branch | `main` |
| Merged revision | `425cb21b31ee8c648e978ca345e2c19675f3a642` |
| Directory | `skills/cluster-cmd-isochrone-fit` |
| Git tree | `ebb2d3846d3bd3a66be2be50c62378badd2cd2c9` |

The merged skill tree matches the reviewed PR head. The full tree difference from
the [1.0.0 admission](2026-09-09-cluster-cmd-isochrone-fit.md) contains only the
version bump and two DOI replacements in `references/parsec.md` and
`scripts/fetch_parsec.py`. The other five installable files are identical. No data
or skill implementation is copied into this registry.

## Change and validation evidence

- Correct the OBC references to Marigo et al. (2008),
  `10.1051/0004-6361:20078467`, and Girardi et al. (2008), `10.1086/588526`.
  Crossref metadata was checked on 2026-09-12: the former Marigo DOI identified
  an unrelated Keppens paper; the former Girardi DOI returned HTTP 404. Both new
  identifiers identify the intended papers. Newly created model manifests carry
  the corrections into downstream fit provenance. Existing verified bundles are
  replayed without rewriting their historical metadata.
- The added offline regression creates a complete bundle through the downloader
  with synthetic transport responses, reads its emitted citations, checks the
  corrected documentation and verifies unchanged offline replay. It fails against
  the previous helper and passes with the corrected helper.
- An accompanying repository-only CI fix excludes access time from an existing
  path-preservation assertion. Symlink inspection may update that timestamp;
  identity, ownership, size, nanosecond modification/change timestamps, link
  destinations and content preservation remain checked. Runtime setup commands
  are unchanged.
- Local validation reports **513 passed, 7 skipped** in the default repository
  environment and **95 passed** in the pinned CPython 3.12 CMD science and portable
  environment suite, including all **39 CMD tests**. The default skips are the
  six science-runtime cases and the existing opt-in NIFTy integration test.
  Repository and explicit helper Ruff checks, native CRS metadata/catalogue
  validation and whitespace checks pass. The generic Codex skill validator still
  rejects the top-level `author` and `version` required by this Hermes-native
  repository; that schema mismatch is not described as a pass.
- Both GitHub checks passed on the reviewed PR head before the authorized squash
  merge. The patch changes neither fitting calculations nor source requests,
  parsers, passbands, extinction assumptions, dependencies, file permissions or
  service destinations. Existing attribution, MIT code licensing, provider data
  terms and bounded public-access behavior remain applicable. The changed source
  adds no secrets, private observations or machine-specific paths.
- Registry validation passes all **43 tests**, Ruff checks, deterministic catalogue
  checks, package build and whitespace checks. Live verification reports all **28
  sources current**, including the exact revision, tree and metadata above. The
  other 27 catalogue entries and consolidation records are unchanged. Both CRS
  workflows also passed on the merged `main` revision.

The original admission's geometric-estimator scope, conditional uncertainty
interpretation, rights assessment and operational limitations remain in force.
This patch does not establish a new age measurement, expand platform claims or
provide another independent scientific reproduction. Ori's reported end-to-end
M67 use motivated the correction; the registry assessment relies on the inspected
source changes and the reproducible checks above, without asserting a separate
audit of that run. The original admission remains an immutable record for 1.0.0.

## References

- [Merged CRS PR 18](https://github.com/skill-commons/curated-research-skills/pull/18)
- [CRS validation](https://github.com/skill-commons/curated-research-skills/actions/runs/34702193442/job/103575813095)
- [CMD science checks](https://github.com/skill-commons/curated-research-skills/actions/runs/34702193420/job/103575813206)
- [Exact assessed source](https://github.com/skill-commons/curated-research-skills/tree/425cb21b31ee8c648e978ca345e2c19675f3a642/skills/cluster-cmd-isochrone-fit)
- [Marigo et al. (2008)](https://doi.org/10.1051/0004-6361:20078467)
- [Girardi et al. (2008)](https://doi.org/10.1086/588526)
- [Review policy](../../docs/adr/0003-review-maturity-and-evidence.md)
