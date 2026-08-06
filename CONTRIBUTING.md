# Contributing to Skill Commons

Skill Commons is a registry, not a monorepo of copied skills. A skill remains in the
repository where its maintainer develops, reviews, licenses, and versions it. This
repository records the canonical location and builds human- and machine-readable
discovery views.

All changes require an accountable human reviewer. Agent assistance is welcome, but the
human submitter remains responsible for correctness, provenance, safety, and the right
to publish the registered source.

## Register a skill

1. Publish the complete skill in a public Git repository. Its directory must include a
   Hermes-compatible `SKILL.md`; references, scripts, and other support files stay beside
   it in that source repository.
2. Prefer a broad, reusable workflow over a fixed query, one plot, or a narrow
   troubleshooting recipe. If an active skill already covers the capability, improve
   that upstream instead.
3. Add one active record to [`registry/index.yaml`](registry/index.yaml), including:
   the repository's canonical HTTPS URL, tracked branch, exact assessed commit, exact
   skill-directory Git tree, repository-relative directory, and registry-owned review
   summary. Link the rationale under `registry/reviews/`.
4. Assign the skill to exactly one editorial category in
   [`categories/index.yaml`](categories/index.yaml).
5. Regenerate the catalog, run the checks below, and open a pull request.

Every active skill must pass the admission floor in
[`ADR 0003`](docs/adr/0003-review-maturity-and-evidence.md). Review maturity is assigned
under that named policy and records `community`, `reviewed`, or `curated`; it is not
inferred from the source organization and does not grant runtime permission. Lockfiles,
repository-wide lint, broad platform coverage, comprehensive tests, and independent
scientific reproduction improve evidence but are not universal admission requirements.

For a skill maintained by Skill Commons, contribute it to
[`skill-commons/curated-research-skills`](https://github.com/skill-commons/curated-research-skills)
first. Register its assessed source commit here only after the upstream change lands.

For an independently maintained skill, do not copy its files here. The upstream
maintainer keeps ownership and history; the registry entry points to that source.

## Record an exact source

Given an assessed upstream commit and skill path:

```bash
git -C /path/to/upstream rev-parse HEAD
git -C /path/to/upstream rev-parse HEAD:skills/example
```

Put the first value in `source.revision` and the second in `source.tree`. The commit
creates a stable review link. The tree lets the drift checker distinguish an unrelated
repository commit from an actual change to the skill directory.

## Update a registered source

When the tracked branch changes, run:

```bash
uv run skill-commons check-upstreams
```

- `current` means the pinned commit/tree and `SKILL.md` metadata were verified and the
  skill directory is unchanged.
- `changed` means a curator must review the new upstream skill tree before updating the
  recorded commit and tree.
- `missing` means the registered path no longer exists and the entry needs investigation.
- `branch-mismatch` means the recorded branch is not the repository's current default
  branch, so Hermes and the registry would follow different content.
- Any `invalid-*` or `metadata-mismatch` result means the pinned source record cannot be
  verified and must be corrected through review.

Never update a recorded commit or tree merely to silence the check.
The existing review decision remains bound to its exact tree; a changed tree requires a
new assessment and decision even when its maturity stays the same.

## Consolidate or retire a skill

The active catalog favors one strong skill per reusable capability. When one skill
supersedes another, remove the retired active record, update its category, and add a
`consolidations` entry pointing to the surviving skill. Do not copy retired content into
this repository as an archive; upstream history and this registry's Git history preserve
the record.

## Local checks

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run skill-commons catalog --check
uv run skill-commons check-upstreams
```

The last command accesses the registered public Git repositories. The other checks are
local and deterministic.

## Review boundary

Automated checks establish registry consistency, safe source coordinates, deterministic
generated views, and whether tracked directory trees changed. They cannot establish the
right to publish, scientific validity, adequate redaction, or trustworthy upstream
maintenance. A curator must assess those claims using the
[`curator checklist`](docs/curator-checklist.md).
