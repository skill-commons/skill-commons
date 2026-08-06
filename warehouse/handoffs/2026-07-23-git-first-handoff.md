# Skill Commons Git-first handoff memo

## Current handoff update — 2026-08-06

Read this section first. The remainder of this file is the preserved 2026-07-23
historical handoff and no longer describes the active repository layout.

### Current architecture and repository state

Skill Commons is now a federated, metadata-only registry:

- [`skill-commons/curated-research-skills`](https://github.com/skill-commons/curated-research-skills)
  (CRS) is the canonical Hermes tap for skills curated and maintained by Skill Commons.
- [`skill-commons/skill-commons`](https://github.com/skill-commons/skill-commons) is the
  central discovery registry. It records immutable reviewed source commits and
  skill-directory Git trees; it does not copy skill contents.
- Independently maintained repositories can remain canonical. The first completed
  example is [`VAMDC/pyVAMDC`](https://github.com/VAMDC/pyVAMDC); the registry points
  directly to its exact `skill/` tree rather than copying it into CRS.
- Every active record now includes `community`, `reviewed`, or `curated` review maturity,
  scoped evidence, and explicit limitations under `skill-commons-review-v1`.
- `arm2arm/AstroAgentAssistant` (AAA) is historical input. The reviewed AAA curation
  program is complete; do not treat later AAA changes as an automatic port queue.
- Categories are browsing metadata, not Hermes bundles or installation units.
- The older schemas, packer, OCI work, and copied-skill implementation remain inert under
  `warehouse/`.

Merged state:

| Repository | Reviewed revision | State |
|---|---|---|
| CRS | `4f63c019b3d05fe72501c706fbe69d105f9fb643` | All curation waves merged; 22 active skills |
| Central registry | `cb355bbbd820265645062ddbd6fd52bc83e0e2cf` | 23 active records; review maturity and evidence implemented; `vamdc` registered; 33 consolidation redirects |
| pyVAMDC registered source | commit `bfefc812782d055c5f54c6105a394d6d34e13815`; tree `7db98d33cc99a8ae220f1585f69d49d15a04bf4c` | First independently maintained `community` entry |
| AAA candidate audit | `ef78afcf1412575dd23e8e88c01dbf50b8b02836` | Original 28-candidate decision baseline |
| AAA sources used by the main waves | `16b4fa2cfd3c5b6b674a750efc7b39a183b416cb` | Pinned in CRS provenance |
| Later AAA J-UBIK/NIFTy input | `fade33165867df7012a71703fa43bb62766e6c06` | Reviewed separately and pinned in CRS provenance |
| Ori architecture handoff | `e016e1273fb02a906f1c660fe86e611a12eba3b1` in [`drp-hermes!1`](https://gitlab-p4n.aip.de/physicsllm/c.1/drp-hermes/-/merge_requests/1) | Claude-facing review maturity, first external intake, and Ori integration guidance updated; MR open and ready to merge at handoff time |

AAA has changed after the audit baseline. Treat later commits as new input requiring
review; never advance provenance merely because AAA `main` moved.

### Review maturity and admission policy

Central registry pull request
[`skill-commons/skill-commons#10`](https://github.com/skill-commons/skill-commons/pull/10)
implemented the active review model:

- `community` passed the admission floor in a maintainer-supported canonical source;
- `reviewed` adds accountable complete-tree technical review and proportionate
  operational evidence;
- `curated` adds deliberate editorial/safety curation, a continuing steward, and
  repeatable regression or contract evidence.

`unreviewed` remains intake state and is not active in the catalog. Maturity is bound to
one exact repository/revision/path/tree and is not a universal trust score, scientific
certificate, or runtime authorization. Keep provenance, rights, security, operability,
scientific validity, reproducibility, maintenance, capabilities, and limitations as
separate evidence. Any skill-tree change requires a new decision; the same tree can be
promoted later if stronger independent evidence is added.

The hard admission floor remains: maintainer-confirmed canonical publication authority;
clear authorship, derivation, attribution, and licensing; exact Git identity; a complete
installable directory; disclosed tools, network, credentials, writes, side effects, and
verification; redaction with no secrets/private material; and no known critical unsafe
default or deceptive scientific claim. Lockfiles, whole-repository lint, broad platform
coverage, comprehensive tests, independent scientific reproduction, and perfect network
containment improve evidence but are not universal gates.

The existing 22 CRS entries were explicitly seeded as `curated` based on the completed
curation program. That decision does not newly claim independent scientific reproduction
for every skill.

### Community announcement and external-skill intake

Tom announced Skill Commons to the IVOA `ai-interop` mailing list on 2026-08-04 while
the community discussion about MCP and agent skills was active. The announcement:

- led with Skill Commons as a community-led registry that works with the AI agents the
  community chooses;
- linked to [`skill-commons/skill-commons`](https://github.com/skill-commons/skill-commons);
- introduced Ori as AIP's research assistant and noted briefly that it uses a locally
  hosted open-source LLM;
- used Ori research screenshots as supporting examples, not as the main subject; and
- stated that an attempt was already under way to intake the ESO skills.

Use Tom's full affiliation in external communication: **the Leibniz Institute for
Astrophysics Potsdam (AIP)**. His public identity reference is
[`aip.de/en/members/tiantian-tong`](https://www.aip.de/en/members/tiantian-tong/).

Two maintainer-first onboarding invitations were initiated; one is complete and one
remains open:

| Candidate source | Review baseline | Public contact | Current state |
|---|---|---|---|
| [`szampier/skills`](https://github.com/szampier/skills) | `dbedc67de5eea2cc12d36fc259fa9d51d9aa0e82` | [Issue #1](https://github.com/szampier/skills/issues/1) | Awaiting Stefano's response |
| [`VAMDC/pyVAMDC`](https://github.com/VAMDC/pyVAMDC) | merge commit `bfefc812782d055c5f54c6105a394d6d34e13815`; `skill/` tree `7db98d33cc99a8ae220f1585f69d49d15a04bf4c` | [Issue #10](https://github.com/VAMDC/pyVAMDC/issues/10) | **Completed:** upstream merged; exact source registered at `community`; central registry CI passed and merged |

For `szampier/skills`, the proposed first demo intake is limited to `eso-tap-obs` and
`eso-tap-cat`. They appear well suited as independently maintained Astronomy skills, but
Tom is not a contributor to that repository. Do not copy, fork, or register them before
the maintainer responds. A 2026-08-06 re-audit found repository-level MIT licensing, clear
Git authorship, complete self-contained directories, read-only ESO/SIMBAD network use,
and successful bounded live checks. Do not require duplicate per-skill version/author/
license fields, a lockfile, or an upstream test suite merely for `community` admission.
If Stefano agrees, offer only proportionate polish: correct the erroneous radius
conversion (`0.1° = 6 arcmin`, not `0.016667°`), prefer bounded/failure-aware `curl` with
safe URL encoding, and clarify `MAXREC=200` truncation. Leave `astroquery-eso` and
`edps-workflow` for later, separate review. Do not imply official ESO endorsement unless
ESO explicitly provides it.

For `VAMDC/pyVAMDC`, Carlo Maria Zwölf confirmed the repository as the canonical home and
the maintainers addressed the original installation, EUPL, metadata, timeout/cache,
testing, and provenance findings. The focused follow-up
[`VAMDC/pyVAMDC#11`](https://github.com/VAMDC/pyVAMDC/pull/11) made `skill/`
self-contained and agent-neutral, aligned authorship, and required an explicit user
choice plus `PARTIAL RESULT` disclosure for accepted truncation. Normal successful CLI
behavior was unchanged. The exact merged checkout installed cleanly on Python 3.11; all
21 tests and the focused Ruff check passed. Central registry pull request
[`skill-commons/skill-commons#11`](https://github.com/skill-commons/skill-commons/pull/11)
then registered the immutable commit/path/tree at `community`, with limitations for
cross-node scientific validation, range-based dependency resolution, and remote-node
availability/truncation metadata. Registry CI passed after one GitHub-hosted runner
acquisition retry; the first attempt executed zero steps and was not a code failure.

The intended onboarding sequence for either external source is: receive maintainer
interest and confirm the canonical repository; agree on scope; make and test changes
upstream; obtain the upstream merge; then register the exact merged commit, path, and Git
tree in the central metadata catalog. Do not copy the skills into CRS merely to accelerate
the demonstration. If no reply arrives promptly, community outreach may continue, but
silence is not permission to register or modify their work.

### Completed curation waves

Wave 1 produced four canonical CRS skills:

- `large-tabular-visualization`
- `rss-feed-monitor`
- `dt4acc-host-smoke-test`
- `python-library-docs-first`

Wave 2 produced two canonical CRS skills:

- `research-paper-evidence-workflow`
- `reana-workflow-authoring`

Wave 3 rewrote the three previously blocked operational candidates into deliberately
bounded first versions:

- `reana-operator` — authenticated remote inspection through a fixed read-only allowlist;
- `drphub-products` — bounded read-only product discovery and inspection;
- `dt4acc-operations` — digest-pinned, network-isolated local simulation lifecycle only.

The final scientific wave added:

- `nifty-re-variational-inference` — a bounded CPU NIFTy.re workflow verified against an
  analytic posterior;
- `jubik-bootstrap` — isolated, lock-backed, wheel-only J-UBIK core initialization with a
  genuine synthetic `SkyModel` smoke test.

Both final skills passed a clean pinned Linux scientific-integration run before merge.
All eleven curated-wave names are active in the central registry. Their predecessors are
provenance inputs or consolidation redirects, not pending ports.

### AAA curation is complete

“Complete” means every reviewed candidate received an explicit disposition. It does not
mean every AAA directory was copied:

- reusable standalone capabilities were curated and registered;
- narrow and duplicate recipes were consolidated into maintained canonical skills;
- restricted, unsafe, snapshot, and router-only material was excluded;
- the two RAVE animation candidates were reviewed and dropped because they did not add a
  reliable, data-source-independent enrichment worth maintaining.

There is no remaining AAA port or merge-only queue. Later AAA changes are new input and
need a fresh curator decision, exact source commit, provenance, safety review, tests, and
human approval.

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
- `astronomy/rave-dr6-3d-animation` and
  `astronomy/rave-dr6-3d-public-animation` — reviewed and deliberately dropped; do not
  reopen as merge-only enrichment without new, correct, generic evidence.

The seven REANA authoring examples already consolidated into
`reana-workflow-authoring`, the three MCP-docs variants consolidated into
`python-library-docs-first`, and the other Wave 1 predecessors are also not pending
ports.

### Required context for the next Codex session

1. Pull CRS and the central registry; verify the reviewed heads above or record any newer
   human-approved merges before acting.
2. Read the implemented Commons/Ori architecture in
   [`NEW_SKILL_COMMONS_ARCHITECTURE.md`](https://gitlab-p4n.aip.de/physicsllm/c.1/drp-hermes/-/blob/main/docs/NEW_SKILL_COMMONS_ARCHITECTURE.md).
   At handoff time the 2026-08-06 update is in
   [`drp-hermes!1`](https://gitlab-p4n.aip.de/physicsllm/c.1/drp-hermes/-/merge_requests/1);
   verify whether it merged before relying on `main`.
3. Do not scout AAA for more ports unless Tom explicitly opens a new audit. The completed
   disposition is the default decision.
4. The next high-value work is Ori integration: consume the CRS tap, add registry-aware
   discovery across CRS and independent repositories, retain and verify source
   commit/path/tree, surface maturity/evidence/limitations without turning them into
   permission, preserve complete skill directories, protect local divergence, and map
   named secret requirements to trusted per-user environment injection.
5. Keep OCI, mandatory Commons sidecars, a custom registry service, and automatic AAA sync
   parked. The active interfaces are Git, Hermes, `SKILL.md`, `skills.sh.json`, and the
   metadata-only catalog.
6. If a genuinely new skill or update is requested, change the canonical source first,
   test and merge it, then register the exact merged commit and directory tree. Never
   advance a registry record merely because its upstream branch moved.
7. For `szampier/skills`, wait for Stefano's explicit response. If positive, use the
   reduced, proportionate scope above and target `community`; silence is not permission.

The complete achievement summary, security boundary, and Claude/Ori implementation order
now live in the drp-hermes document above. This handoff should remain short and operational;
the historical 2026-07-23 material below is preserved only for archaeology.

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
