# Skill Commons Git-first handoff memo

> **Historical handoff:** This memo captured the 2026-07-23 transition. Current
> architecture and repository status live in
> [`SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md`](../../docs/SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md)
> and the root README.

**Audience:** Claude Fable and the next Codex session  
**Date:** 2026-07-23  
**Repository:** `git@gitlab-p4n.aip.de:physicsllm/skill-commons/spec.git`  
**Branch:** `main`

Read this memo first, then read
[`SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md`](../../docs/SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md).
That architecture is the current decision. The older Ori v0.4.1 architecture is design
history and remains authoritative only where the new document does not supersede it.

---

## 1. Decision in one paragraph

The project has pivoted from OCI-first to **Git-first**. Colleagues, including Arman, want
a visible and familiar Git collection, and community contribution is the project's main
survival constraint. Published skills therefore live completely in Git as standard
Agent Skills directories rooted at `SKILL.md`. Ori is a richer client, not a prerequisite.
OCI is retained as optional, parked export technology and as preserved engineering
evidence; do not make contributors or ordinary clients depend on it.

Do not describe the current architecture as an active Git+OCI hybrid. That implies two
release authorities and two mandatory workflows. The precise description is:

> Git is canonical. Agent Skills is the portable interface. OCI is an optional export
> profile that may become first-class only after demonstrated demand.

---

## 2. Current repository state

The Git-first pivot was implemented in commit `a5d593c`:

```text
a5d593c Materialize StarHorse as a Git-native Agent Skill
```

The complete first package is:

```text
skills/starhorse-access/
├── SKILL.md
├── LICENSE
├── research-skill.yaml
├── research-skill.lock
├── references/schema.md
└── contracts/
    ├── static-content.json
    └── static-content.expected.json
```

Important identity data:

| Item | Value |
|---|---|
| Commons coordinate | `aip/starhorse-access` |
| Version | `2.0.2` |
| Canonical materialized path | `skills/starhorse-access` |
| Materialization commit | `a5d593c` |
| Deterministic package digest | `sha256:a375de9ccbc9abf40b9bda1efd7e8b4a55704fd3f64c0e4a8f81aa26a86913b9` |
| Reviewed upstream | `p4nreana/reana-env` commit `5f1d331b106cc96b47f0633cddc94b05325b8b49` |
| Upstream path | `skills/starhorse-access` |
| Upstream tree digest | `sha256:6c412460f445423ce1d27cbf9dc5d9d67d62b47a6deb77176b793ab7da7de440` |

The materialized directory is byte-for-byte identical to the reviewed package produced
by the earlier release pipeline. Repacking it produces the same digest above. Do **not**
edit the 2.0.2 package in place and continue calling it 2.0.2. Any content change requires
a version bump and a new reviewed release.

`research-skill.yaml` records `reana-env` as the provenance/source origin. That is
intentional and is not a contradiction: the reviewed Commons publication lives here,
while the sidecar preserves where the migrated content came from. Import future upstream
changes through an explicit reviewed merge request.

The OCI vertical-slice records remain under:

```text
releases/aip/starhorse-access/2.0.2/
```

They are historical evidence and an optional export profile, not the source from which a
normal user must reconstruct the skill.

---

## 3. Validation status at handoff

Verified locally after materialization:

- Agent Skills profile: **pass**
  (`agent-skills-specification+skills-ref@0.1.1`)
- Commons publication profile: **warn**, with only
  `COMMONS_EXTERNAL_ATTESTATIONS_REQUIRED`
- deterministic package digest: **matches** the published 2.0.2 digest
- test suite: **84 passed**
- Ruff lint and format checks: **pass**
- Git diff whitespace check: **pass**

The Commons warning is expected. A local validator cannot independently establish
namespace control, publication rights, or human-reviewed redaction. Those assertions were
approved by Tom and are recorded in the release material and the Hermes handoff documents.
Do not convert that warning into a fake local pass.

The current `ori-compatibility` profile does **not** pass for the portable package. The
current Ori/Hermes runtime still expects legacy frontmatter for dependency and platform
behavior and does not yet enforce the sidecar equivalents. This is an Ori implementation
gap, not an Agent Skills failure. Claude owns the Ori side of the project and should make
the runtime read the sidecar before legacy fields.

Useful local checks:

```bash
uv sync --all-groups
uv run skill-commons validate skills/starhorse-access --profile agent-skills
uv run skill-commons validate skills/starhorse-access --profile commons-publication
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

---

## 4. What Claude should do on the Ori side

Claude owns Ori; Codex owns the Commons. The coordination contract after this pivot is:

1. Ori discovers and reads the standard root `SKILL.md`.
2. Ori looks for `research-skill.yaml` beside it.
3. If supported, Ori validates and uses the sidecar for dependencies, capabilities,
   compatibility, research metadata, and the `de.aip.ori` extension.
4. Ori validates `research-skill.lock` before automated provisioning.
5. Ori installs from an exact Git repository, commit/tag, and subdirectory.
6. Ori shows the pre-install inventory and policy decision.
7. Ori avoids overwriting locally changed copies and records divergence.
8. Ori does not require the OCI registry or signed OCI catalog for the normal Git path.

The ideal end state is progressive enhancement:

```text
generic Agent Skills client ──► SKILL.md ──► useful core workflow
                                      │
Ori / Commons-aware client ───────────┴──► sidecar + lock + policy automation
```

Do not reintroduce nested `metadata.hermes` into portable frontmatter. Preserve client
runtime semantics under the versioned `de.aip.ori` extension in `research-skill.yaml`.

---

## 5. What the next Codex session should do

Work in this order unless Tom changes priorities.

### Priority 1 — make Git publication complete

- Review and merge the new Git-first architecture and this memo.
- Define the protected release-tag convention. The architecture proposes
  `skill/<name>/v<version>` but no tag has been created yet.
- Add CI that refuses a changed released package without a version bump.
- Generate a minimal human and machine catalog from `skills/` and exact Git identities.
- Add Git-native deprecation/yank/advisory records.

### Priority 2 — make generic usage honest

The Agent Skills format standardizes the package, not one universal installation command
or dependency installer. Add documentation for clone/copy/symlink/Git-subdirectory use.

For the next StarHorse release, ensure `SKILL.md` or a directly linked reference states
portable environment setup explicitly: required Python packages, safe isolated setup,
network/credential needs, side effects, and verification. The machine-readable sidecar
and lock remain richer, but a generic agent must not need to understand them to perform
the workflow.

Do not modify 2.0.2 merely to add this text. Prepare a new version.

### Priority 3 — exercise the contribution path

- Add a minimal contributor template and curator checklist.
- Migrate one additional rights-cleared AIP skill through an ordinary merge request.
- Measure how much manual metadata and review work is required.
- Prefer small, real exercises over more speculative schemas.

### Priority 4 — decide the community front door

The current AIP GitLab project is canonical. Determine with Tom and Arman whether it will
be publicly readable and accept outside contributions. If a GitHub mirror is added for
reach, keep it one-way and label one canonical issue/MR location. Do not create two
writable authorities.

---

## 6. Decisions that should not be casually reopened

- No required `.claude-plugin` wrapper.
- No required vendor-specific package metadata.
- `SKILL.md` follows the open Agent Skills specification.
- `research-skill.yaml` remains the agent-neutral structured sidecar.
- Git is canonical for the present phase.
- The complete installable directory lives in Git.
- OCI is optional and parked, not deleted and not co-equal.
- Ori is a client, not the owner of the package format.
- One canonical source per package; mirrors are one-way.
- Publication remains explicit and human-accountable.
- Trust, security, scientific validation, and maintenance remain separate evidence axes.

Reopen one of these only with new evidence from contributors, users, operations, or
institutional requirements, and record the change in an ADR or architecture revision.

---

## 7. Open decisions and known gaps

1. **Public hosting:** AIP GitLab visibility and external contribution policy are not yet
   settled.
2. **Release tags:** the per-skill convention is proposed, not implemented.
3. **Static catalog:** the existing signed catalog is OCI-shaped; a simple Git-native
   generated index is still needed.
4. **Negative state:** advisories, yanks, and deprecations need a Git-native layout and
   generation rule.
5. **Portable setup guidance:** StarHorse 2.0.2 is standard-valid but a future release
   should state dependency setup more explicitly for generic agents.
6. **Ori sidecar-first reader:** current runtime compatibility is incomplete.
7. **Platform coverage:** the StarHorse lock is Linux amd64 CPython 3.12 evidence only.
   Do not infer arm64 support from the existence of the DGX Spark; generate and test a
   native lock before advertising it.
8. **OCI gates 4 and 5:** publisher isolation and backup/restore remain open for the OCI
   profile. They do not block Git-native publication but must remain visible if OCI is
   used again.
9. **Architecture cross-links:** the older Ori RFC should eventually receive a short
   supersession notice pointing here, without deleting its history.

---

## 8. Source map

Read these when deeper context is needed:

| Topic | Location |
|---|---|
| Current architecture | `docs/SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md` |
| Current session handoff | `docs/GIT_FIRST_HANDOFF_MEMO.md` |
| Repository overview | `README.md` |
| Materialized skill | `skills/starhorse-access/` |
| Sidecar extension contract | `docs/extensions.md` |
| Validation profiles | `docs/validation-profiles.md` |
| Threat model | `docs/threat-model.md` |
| Canonical bytes/digests | `docs/artifact-format.md` |
| Historical optional OCI path | `docs/oci-publication.md` |
| Historical StarHorse release evidence | `releases/aip/starhorse-access/2.0.2/` |
| Old architecture v0.4.1 | `drp-hermes/docs/ORI_SKILL_COMMONS_ARCHITECTURE.md` |
| Claude's original frontmatter/runtime survey | `drp-hermes/docs/skill-commons/FRONTMATTER_REALITY.md` |
| Claude's delivery index | `drp-hermes/docs/skill-commons/FABLE_COMMONS_RESPONSE.md` |

---

## 9. Handoff discipline

Before changing package or architecture behavior:

1. Pull `main` and inspect the exact current commit.
2. Read this memo and the Git-first architecture.
3. Preserve existing user changes and unrelated work.
4. Validate a package with the correct profiles; do not call a warning a pass or an Ori
   compatibility failure an Agent Skills failure.
5. Keep released versions immutable.
6. Update this memo when repository state, ownership, blockers, or priorities materially
   change.
7. Tell the other owner through a committed Markdown note when a Commons/Ori interface
   changes.

The project is no longer blocked on designing a sophisticated registry. The next proof is
social and operational: can researchers understand the Git collection, install a skill
with their existing agent, and contribute the next useful package?
