# Curator checklist

Use this checklist before merging a new or changed registry record.

## Source and ownership

- The URL is the canonical public repository selected by the skill maintainer.
- The repository history is retained upstream; no skill body or support file was copied
  into this registry.
- The registered path contains the complete skill, including every referenced file.
- The submitter or upstream maintainer has the right to publish the material.
- Authorship, derivation, licensing, and attribution are clear at the source.
- The assessed commit and directory Git tree exactly match the registry record.
- The tracked branch is the repository's default branch used by Hermes installation.

## Skill quality

- `SKILL.md` follows current Hermes conventions and has a useful description.
- The workflow is broad enough to justify independent discovery.
- A fixed sample, one figure style, topic query, or narrow troubleshooting case was
  merged into a broader skill instead of registered separately.
- Required tools, network access, credentials, external writes, and verification steps
  are clear.
- References and scripts named by the skill exist in its source directory.
- Private data, credentials, prompts, transcripts, and personal information received an
  explicit redaction review.

## Registry

- The active name and canonical `(repository, path)` are unique.
- The source repository, branch, revision, tree, and path are exact.
- The skill passes the ADR 0003 admission floor.
- Review maturity is an accountable human decision under the named policy, not a value
  inferred from repository membership or test results.
- The evidence facets and limitations describe what was actually assessed without
  treating software success as scientific validation.
- The review decision exists under `registry/reviews/` and remains bound to this exact
  source tree.
- The skill appears in exactly one category.
- A replacement exists for every new consolidation redirect.
- `skill-commons catalog --check` and the test suite pass.
- `skill-commons check-upstreams` verifies the pinned source and reports it as `current`.

Automated checks do not prove publication rights, scientific validity, or safe behavior.
Those remain human review decisions.
