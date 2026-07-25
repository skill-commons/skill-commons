# Contributing to Skill Commons

All changes require an accountable human reviewer. Agent assistance is welcome, but the
human submitter remains responsible for correctness, provenance, safety, and the right to
submit every included file.

By contributing, you certify the Developer Certificate of Origin 1.1: the contribution
was created by you or supplied under terms permitting submission, and you understand the
project and its public history may retain it. Add `Signed-off-by: Name <email>` to commits
when the project begins accepting external contributions.

## Minimal contribution path

1. Fork the repository and create a focused branch.
2. Add or update one complete `skills/<name>/` directory.
3. Keep the portable `SKILL.md` useful without Commons-specific tooling.
4. Include a package license and identify source, authorship, derivation, and intended
   use.
5. Assign the active skill to exactly one primary group in `bundles/index.yaml`.
6. Explain why the workflow is not already covered by a broader canonical skill; merge
   reusable guidance into that skill when it is only a variant.
7. Run the relevant checks.
8. Open a pull request and complete its publication checklist.

```bash
uv sync --locked --all-groups
uv run skill-commons validate skills/<name> --profile agent-skills
uv run skill-commons validate skills/<name> --profile commons-publication
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run skill-commons catalog \
  --repository https://github.com/skill-commons/skill-commons \
  --check
```

Contributions must:

- identify copied, generated, derived, and third-party material;
- include applicable license and attribution evidence;
- disclose material AI assistance in the pull request description;
- contain no credentials, private prompts/transcripts, researcher data, or unapproved
  personal information;
- keep generated fixtures source-pinned and reproducible;
- preserve the separation between observed material and published Commons releases.

## Curation

The active tree favors one broad, maintained skill per capability. A fixed dataset
sample, one figure style, one research topic, or one journal troubleshooting case should
normally become an example or reference within a canonical skill, not a new package.

When consolidating a published package:

- merge only its reusable, accurate guidance;
- bump the surviving package version when its bytes change;
- record derivation and supersession in the surviving sidecar;
- remove the redundant active directory;
- add a coordinate-to-replacement entry under `consolidations` in
  `bundles/index.yaml`.

Git history preserves the removed source. Do not copy retired packages into another
active-looking tree merely to preserve them.

## Released packages

Released package bytes are immutable. Any content change requires a version bump and a
new review. Release tags use:

```text
skill/<name>/v<version>
```

Do not move, recreate, or reuse a release tag for different content.

## Review boundary

Automated checks can establish structural validity, deterministic bytes, and local
contract results. They cannot establish the contributor's right to publish, institutional
namespace control, scientific validity, or successful human redaction review. A curator
must assess those claims using the [curator checklist](docs/curator-checklist.md).
