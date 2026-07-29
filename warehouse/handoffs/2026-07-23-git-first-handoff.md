# Skill Commons Git-first handoff memo

## Current handoff update — 2026-07-30

Read this section first. The remainder of this file is the preserved 2026-07-23
historical handoff and no longer describes the active repository layout.

### Current architecture and repository state

Skill Commons is now a federated, metadata-only registry:

- [`skill-commons/curated-research-skills`](https://github.com/skill-commons/curated-research-skills)
  (CRS) is the canonical Hermes tap for skills curated and maintained by Skill Commons.
- [`skill-commons/skill-commons`](https://github.com/skill-commons/skill-commons) is the
  central discovery registry. It records immutable reviewed source commits and
  skill-directory Git trees; it does not copy skill contents.
- `arm2arm/AstroAgentAssistant` (AAA) is a historical source for the AIP workflows being
  consolidated. Do not open routine curation PRs there: curate the reusable result into
  CRS and preserve exact provenance.
- Categories are browsing metadata, not Hermes bundles or installation units.
- The older schemas, packer, OCI work, and copied-skill implementation remain inert under
  `warehouse/`.

Merged state:

| Repository | Reviewed main commit | State |
|---|---|---|
| CRS | `8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e` | Waves 1 and 2 merged; 17 active skills |
| Central registry | `4210f88` | Both waves registered; 17 upstream records current |
| AAA candidate audit | `ef78afcf1412575dd23e8e88c01dbf50b8b02836` | Original 28-candidate decision baseline |
| AAA sources used by merged waves | `16b4fa2cfd3c5b6b674a750efc7b39a183b416cb` | Pinned in CRS provenance |

AAA has changed after the audit baseline. Treat later commits as new input requiring
review; never advance provenance merely because AAA `main` moved.

### Completed conditional-candidate waves

Wave 1 produced four canonical CRS skills:

- `large-tabular-visualization`
- `rss-feed-monitor`
- `dt4acc-host-smoke-test`
- `python-library-docs-first`

Wave 2 produced two canonical CRS skills:

- `research-paper-evidence-workflow`
- `reana-workflow-authoring`

These names are also active in the central registry. Their predecessor names are
consolidation redirects, not separate skills waiting to be ported.

### Remaining standalone skills awaiting modification

The original 28 conditional candidates now reduce to **three possible standalone
skills**. All three remain blocked. Do not copy their current AAA directories into CRS.

| Proposed CRS skill | AAA inputs to review | Required modification before a CRS port |
|---|---|---|
| `reana-operator` | `reana-workflows/reana-client-config`, `reana-workflows/reana-client-failover`, `reana-workflows/reana-operator` | Separate remote operation from the completed local-only `reana-workflow-authoring`; begin read-only; use secure credential discovery; redact logs; replace unrestricted command forwarding with an allowlist; remove or tightly isolate the read/write Docker fallback; pin the client image; show server, inventory, image, resources, workflow name, and outputs before any upload or run; require explicit confirmation for every external write or computation start; add mocked and forward tests. |
| `drphub-products` | `astronomy/drphub-cards` | Build and test a small client against an explicit API contract; make reads the default; store JWT/service credentials outside plaintext project files; redact owner UUIDs, ORCIDs, private metadata, and audit data; reject mutable `HEAD` and tag-only runtime identities; repair ETag/idempotency handling; provide dry-run previews; require confirmation for create, patch, delete, clone, publish, review, share, or batch mutation. |
| `dt4acc-operations` | `science/dt4acc-container-troubleshooting`, `science/dtwin-epics-runbook`, `science/dtwin-setup` | Default to simulation and fail closed on unknown networks; clearly distinguish simulated PVs from live facility control; add facility/network allowlists and a separate live-system opt-in; pin repositories, images, system packages, and Python dependencies; scope privileged container/fakeroot steps; replace broad `fuser`/`pkill -9` cleanup; snapshot and restore any mutable state; fix and execute-test the Apptainer path; add safe rollback and end-to-end simulation tests. |

Recommended order is `reana-operator` read-only functionality first,
`drphub-products` read-only functionality second, and `dt4acc-operations` last. Mutating
features may remain out of the first CRS versions even when the read-only cores are ready.

### Remaining merge-only curation

The following are **not** new standalone skills:

| AAA inputs | Destination | Required action |
|---|---|---|
| `astronomy/rave-dr6-3d-animation`, `astronomy/rave-dr6-3d-public-animation` | Existing CRS `astro-catalog-plotting-cache` | Salvage only the generic, data-source-independent Matplotlib animation pattern after tests. Do not copy either data recipe: one requests CSV and parses it as VOTable; the other mixes Gaia data into a purported RAVE workflow. |

This is an optional enrichment PR to CRS. It should not increase the active skill count.

### Explicitly excluded from the port queue

Do not turn these into CRS skills unless a future curator reopens the decision with new
evidence:

- `astronomy/astro-data-access-umbrella` — category/router concept, not a skill.
- `research/2026-agentic-astronomy-literature` — warehouse-only snapshot.
- `reana-workflows/reana-cmd-plot-workflow` — restricted source; a
  credential-looking literal was found during review. Never reproduce it. Confirm
  revocation independently before using any related credential.
- `reana-workflows/reana-shboost24` — restricted, AIP-specific operational example.
- `science/dtwin-burnin-tests` — unsafe for curation until repeated PV writes have robust
  targeting, snapshot, restore, rollback, and simulation-only tests.

The seven REANA authoring examples already consolidated into
`reana-workflow-authoring`, the three MCP-docs variants consolidated into
`python-library-docs-first`, and the other Wave 1 predecessors are also not pending
ports.

### Required workflow for the next Codex session

1. Pull both public repositories and verify their current `main` commits.
2. Work on source content in CRS, not in the central registry and not by copying an AAA
   directory unchanged.
3. Curate one canonical capability at a time. Preserve the AAA commit and input paths in
   `PROVENANCE.md`.
4. Remove provider assumptions from the core workflow. Put an AIP adapter in a reference
   only when it is safe, necessary, and clearly labeled.
5. Never copy credential literals, private endpoints presented as public defaults,
   mutable runtime defaults, destructive cleanup commands, or unrestricted external-write
   recipes.
6. Keep read-only and local-only behavior as the default. Treat credentials, facility
   access, submissions, remote compute, uploads, mutations, and process control as
   separately gated capabilities.
7. Validate the complete skill directory, run repository tests, add focused safety
   regression tests, and forward-test the skill without live credentials or production
   systems.
8. Open a CRS pull request and obtain human review. Do not update the central registry
   before the CRS PR is merged.
9. After merge, add or update the central registry record using the immutable CRS merge
   commit and exact skill-directory Git tree; regenerate README/catalog and run the live
   upstream checker.

The next session should not interpret “blocked” as “copy now and document the risk.”
Modification and executable safeguards are prerequisites for publication.

---

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
