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
5. Run the relevant checks.
6. Open a pull request and complete its publication checklist.

```bash
uv sync --locked --all-groups
uv run skill-commons validate skills/<name> --profile agent-skills
uv run skill-commons validate skills/<name> --profile commons-publication
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Contributions must:

- identify copied, generated, derived, and third-party material;
- include applicable license and attribution evidence;
- disclose material AI assistance in the pull request description;
- contain no credentials, private prompts/transcripts, researcher data, or unapproved
  personal information;
- keep generated fixtures source-pinned and reproducible;
- preserve the separation between observed material and published Commons releases.

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
