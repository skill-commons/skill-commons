## What changed

<!-- Describe the registry, category, tooling, or documentation change. -->

## Registry review

<!-- Delete this section when the PR does not add or update a skill record. -->

- [ ] The registered repository is the maintainer's canonical public source.
- [ ] The complete skill, references, scripts, license, and history remain upstream.
- [ ] The registered commit and directory tree match the assessed source.
- [ ] The `SKILL.md` follows current Hermes conventions.
- [ ] Network access, credentials, external writes, and other material risks were reviewed.
- [ ] The skill is broad enough for independent discovery and is not a near-duplicate.
- [ ] The skill appears in exactly one category.
- [ ] Publication rights, attribution, licensing, and redaction were reviewed.
- [ ] The skill passes the ADR 0003 admission floor.
- [ ] Maturity, evidence facets, limitations, and the decision rationale are accurate for
      this exact tree and do not imply runtime authorization or scientific certification.

## Verification

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run pytest`
- [ ] `uv run skill-commons catalog --check`
- [ ] `uv run skill-commons check-upstreams` (for registry changes)

<!-- List any additional checks or explain unchecked items. -->
