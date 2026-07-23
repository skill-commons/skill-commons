# Open Research Skill Commons — Git-first architecture

**Status:** v0.5.1 — adopted and published
**Date:** 2026-07-24
**Canonical repository:** `https://github.com/skill-commons/skill-commons`
**Scope:** The package, publication, discovery, trust, and evolution model for an open
collection of reusable research skills.

This document supersedes the OCI-first decisions in
[`ORI_SKILL_COMMONS_ARCHITECTURE.md` v0.4.1](https://gitlab-p4n.aip.de/physicsllm/c.1/drp-hermes/-/blob/main/docs/ORI_SKILL_COMMONS_ARCHITECTURE.md).
The earlier RFC remains valuable design history. Its research metadata, provenance,
validation, policy, evidence, preservation, and federation work is retained unless this
document changes it explicitly.

The change is one of sequencing and authority:

- **Git is the canonical publication and collaboration substrate now.**
- **The open Agent Skills directory format is the portable agent interface.**
- **OCI is preserved as an optional export and future federation profile, not a
  prerequisite for contributing, browsing, publishing, or installing a skill.**

---

## 1. Executive decision

The Commons succeeds only if researchers can see it, understand it, contribute to it,
and use it with agents they already have. Community adoption is therefore a first-order
architectural requirement, not a later user-interface concern.

The Phase 0 and Phase 1 product is a familiar Git collection:

```text
researcher or agent
        │
        ▼
  ordinary Git contribution
        │
        ▼
reviewed skill directory ───────► standard Agent Skills client
        │                              reads SKILL.md
        ├── research-skill.yaml
        ├── research-skill.lock
        └── tests / evidence
        │
        ├────────► generated Git catalog and release tag
        │
        └────────► optional OCI export, archive, or institutional mirror
```

The portable unit is a directory rooted at `SKILL.md`, as defined by the
[Agent Skills specification](https://agentskills.io/specification). A standard-compatible
agent can activate and follow that file without an Ori reader, Claude plugin manifest,
registry client, or Commons service. Commons-aware clients may additionally consume the
sidecar and lock for automated dependency, capability, provenance, and policy handling.

This architecture deliberately does **not** claim that every existing agent supports
Agent Skills or that every client uses the same installation command. The standard makes
the installed skill portable; Git makes its source and distribution accessible. Clients
still choose their own discovery paths, installation locations, and approval policies.

### 1.1 Why the authority changed

OCI remains technically sound for content-addressed artifacts, attestations, replication,
and registry federation. It is not the best adoption surface for the present project:

- researchers and maintainers already understand Git;
- a Git tree is directly browsable and reviewable;
- standard agents can consume `SKILL.md` without a new reader;
- contributors should not need ORAS, registry credentials, media types, or custom push
  tooling;
- maintaining Git and OCI as equal authorities would double concepts, CI paths, release
  work, and opportunities for drift;
- the immediate existential risk is an empty Commons, not insufficient registry scale.

The OCI vertical slice was not wasted work. It established deterministic packaging,
registry behavior, evidence binding, mirroring constraints, and future re-entry criteria.
Those results remain available when real use justifies the additional machinery.

### 1.2 Options considered

| Option | Decision | Reason |
|---|---|---|
| OCI-first | Reject for the current phase | High contributor and consumer friction; requires a specialized install path. |
| Git and OCI as co-equal authorities | Reject for the current phase | Split authority, duplicated releases, more CI and support burden. |
| Git façade backed by mandatory OCI | Reject | Users would still depend on the hidden complex path and its availability. |
| **Git canonical, OCI optional** | **Adopt** | Familiar contribution and native skill consumption now; preserves an upgrade path. |
| Delete all OCI work | Reject | Discards exercised packaging and federation knowledge with little benefit. |

---

## 2. Architectural invariants

These rules govern implementation and review.

1. **The corpus is the product.** Preserve skills, history, provenance, evidence,
   corrections, advisories, and curation decisions independently of any one service.
2. **The portable entry point is standard Agent Skills.** Every published skill has a
   spec-valid root `SKILL.md` whose `name` matches its parent directory.
3. **Git is canonical in the current architecture.** The authoritative bytes are the
   reviewed files at an exact repository commit and path.
4. **A plain agent can use the core skill.** The main workflow and human-readable setup
   must not require `research-skill.yaml`, an OCI registry, Ori, or vendor-specific
   marketplace metadata.
5. **Structured richness is additive.** The sidecar and lock add research and policy
   semantics without changing the meaning of `SKILL.md` or making it unreadable alone.
6. **Released versions are immutable.** Changes to released bytes require a new version.
   Never move or recreate a protected release tag with different content.
7. **One package has one canonical source.** Mirrors are one-way projections. Do not
   accept competing changes at two canonical forges.
8. **Publication is explicit and reviewed.** An agent may prepare a contribution but may
   not upload private learned material or publish on a person's behalf without approval.
9. **Trust remains multidimensional.** Identity, license, integrity, security, scientific
   validity, reproducibility, maintenance, and risk are separate claims.
10. **A skill requests capabilities; it does not authorize them.** Local client or
    institutional policy decides network, filesystem, process, secret, and installation
    permissions.
11. **Exact Git identity is recordable.** Install records and reproducibility reports
    retain the repository, commit, path, version, and tree digest when available.
12. **Negative state is first-class.** Deprecations, yanks, security advisories, and
    corrections are versioned in Git and included in generated catalogs and mirrors.
13. **Agent-specific adapters are optional views.** `.claude-plugin`, Codex UI metadata,
    MCP facades, and other adapters may be generated or maintained separately, but are
    never required fields of a Commons skill.
14. **No irreplaceable provider.** The complete public corpus and catalog must remain
    cloneable and exportable using ordinary Git and open file formats.

---

## 3. Canonical repository model

### 3.1 Layout

The canonical collection uses a shallow skills tree for simple browsing and broad client
compatibility:

```text
skill-commons/
├── skills/
│   └── starhorse-access/
│       ├── SKILL.md                    # required portable entry point
│       ├── LICENSE                     # required for Commons publication
│       ├── research-skill.yaml         # required for Commons publication
│       ├── research-skill.lock         # required when dependencies are declared
│       ├── scripts/                    # optional
│       ├── references/                 # optional
│       ├── assets/                     # optional
│       └── contracts/                  # optional validation contracts
├── schemas/                            # Commons schemas
├── catalog/                            # generated human and machine indexes
├── docs/                               # architecture, policy, and operator documentation
├── src/                                # reference validation, conversion, and catalog tooling
├── tests/                              # active contract and regression tests
└── warehouse/                          # inert Phase-0 and OCI design history
```

`skills/<name>/` is the complete installable unit. Copying only `SKILL.md` is not a
complete installation when it references bundled resources.

The Agent Skills `name` is globally unique within the canonical collection in Phase 1.
The governed Commons identity remains `<namespace>/<name>` in `research-skill.yaml`.
If two publishers propose the same portable name, curation must resolve the collision
explicitly; the system must not silently rename a published skill.

### 3.2 Package layers

Each package has three progressive layers.

#### Layer A — portable agent layer

`SKILL.md` follows the public Agent Skills specification:

```yaml
---
name: starhorse-access
description: Access StarHorse data products through public Parquet and AIP TAP services.
license: MIT
compatibility: Requires HTTPS access; Python examples require the documented packages.
metadata:
  research-skill.manifest: research-skill.yaml
---
```

Only `name` and `description` are required by Agent Skills. Commons publication also
requires a valid license assertion. `license`, `compatibility`, and flat string metadata
remain standard fields. The metadata pointer is a convenience, not a discovery
requirement; sidecar-aware clients also look for the conventional filename.

The body must include enough information for a capable generic agent to perform the main
workflow. When code needs non-standard dependencies, the body or a directly linked
reference must state:

- required tools, language, and tested versions;
- a safe environment setup approach;
- whether network access or credentials are needed;
- which actions have external side effects;
- how to verify the result.

A generic agent may infer and propose setup, but must not silently modify global
environments or install dependencies where local policy requires approval.

#### Layer B — Commons research and policy layer

`research-skill.yaml` carries structured fields that do not belong in portable
frontmatter:

- namespace, version, and source/provenance origin;
- accountable authorship, ORCID, and creation mode;
- disciplines, methods, software, data sources, intended uses, assumptions, and known
  failure modes;
- typed relations to tasks and other skills;
- supported operating systems, architectures, clients, and runtimes;
- dependency intent;
- requested filesystem, network, process, secret, and external-side-effect capabilities;
- validation contracts and provenance;
- license evidence and client-extension envelopes.

An agent that ignores this file can still follow `SKILL.md`. A Commons-aware client can
offer safer automation, richer discovery, exact policy decisions, and better
reproducibility.

#### Layer C — reproducible resolution and evidence layer

`research-skill.lock` records tested, target-specific dependency resolutions and artifact
hashes. Contracts, validation receipts, SBOMs, provenance attestations, reviews, and
scientific reproduction records may accompany the package or live in a separately
reviewed evidence tree.

The lock is generated, not hand-authored. A lock for one platform is evidence for that
platform only. It does not prove support for another architecture or operating system.

### 3.3 Version identity

A release has both a human coordinate and exact Git identity:

```text
coordinate:  aip/starhorse-access:2.0.2
git identity: <repository>@<commit>:skills/starhorse-access
tree digest:  sha256:<canonical tree digest>
tag:          skill/starhorse-access/v2.0.2
```

An exact protected tag plus path is the preferred release selector. An exact commit plus
path remains authoritative when no release tag exists. `main` shows the current reviewed
state but is not an immutable version selector.

Release rules:

1. `package.version` changes whenever released package bytes change.
2. The version, `SKILL.md`, sidecar, lock, license, and bundled resources are reviewed as
   one directory.
3. CI validates the directory before merge and again before tagging.
4. Release tags are protected and never force-moved.
5. Historical versions remain available through Git commits and tags; they need not be
   duplicated as version directories on `main`.
6. Generated archives or OCI artifacts must reproduce the tagged Git directory and must
   record the source commit and path.

The source recorded inside a migrated package and the Commons publication locator have
different roles. For StarHorse 2.0.2, `research-skill.yaml` correctly records the
`reana-env` tree from which the package was curated; the Commons release is the reviewed
directory in this repository. Future upstream changes enter the Commons through an
explicit reviewed import. A mirror must not become a second writable release authority.

---

## 4. Contribution and publication workflow

### 4.1 Contributor path

The normal workflow is deliberately ordinary:

1. Fork or branch the canonical Git repository.
2. Add or edit one complete `skills/<name>/` directory.
3. Run the local validators and relevant contracts.
4. Open a pull request with the source, authorship, license, and intended-use assertions.
5. CI produces a review report; it does not silently rewrite the contribution.
6. An accountable maintainer resolves findings and approves publication.
7. Merge to protected `main`.
8. When declaring a release, create the protected per-skill version tag and update the
   generated catalog.

The contribution guide should make the minimal successful path shorter than the full
research metadata guide. A first-time contributor may start with `SKILL.md` and a license;
tooling or a curator can scaffold the sidecar as a reviewable diff. A complete sidecar is
required before the package receives a curated Commons release, while advanced evidence
can be added progressively unless policy makes it a release blocker.

### 4.2 Required publication checks

Phase 1 CI should enforce:

- Agent Skills reference validation;
- directory/name agreement and globally unique portable names;
- accepted license expression plus package-wide license evidence;
- `SKILL.md`/sidecar identity and license consistency;
- schema-valid sidecar and lock;
- no unsafe paths, symlinks, secret-bearing files, oversized files, or embedded VCS state;
- declared dependencies and capabilities consistent with bundled scripts and tests;
- source, namespace, authorship, and redaction review status;
- contract tests appropriate to the skill's declared risk;
- version bump when a previously released package changes;
- no reuse or movement of a protected release tag.

CI findings distinguish errors, warnings, and evidence that only a human or trusted
external process can establish. A local validator must not pretend to prove namespace
control, publication rights, scientific validity, or reviewed redaction.

### 4.3 Importing external skills

Observation is not republication. For a skill from another repository:

- record its canonical source and license;
- preserve authorship and derivation;
- obtain or establish publication rights before copying it into `skills/`;
- prefer an external-catalog record when the Commons does not own or curate the package;
- never assign an institutional namespace merely because a converter can parse it;
- use reviewable conversion diffs rather than silent normalization.

---

## 5. Discovery and installation

### 5.1 Human discovery

The Git forge is the first user interface:

- directory browsing shows the complete skill;
- rendered Markdown shows instructions and references;
- commit history and blame show evolution;
- issues and pull requests support discussion and contribution;
- tags show released versions;
- ordinary clone and archive operations provide export.

The generated `catalog/` adds a human index and machine-readable index without becoming
a second source of truth. It is reconstructed from reviewed package directories. Release
tags and advisory records can be added to the generation inputs as those workflows
mature.

### 5.2 Agent discovery

The portable discovery record is `SKILL.md` metadata. Compatible clients load `name` and
`description`, activate the full file when relevant, and load referenced resources only
as needed.

Installation mechanisms may include:

- clone the repository and point the client at `skills/<name>`;
- copy or symlink the complete directory into the client's normal skills location;
- give a supporting client the Git URL, commit/tag, and subdirectory;
- install a generated collection or agent-specific adapter;
- let Ori perform a policy-checked Git installation.

The Commons must document concrete recipes for supported clients, but none of those
recipes changes the canonical package. A `.claude-plugin` marketplace, Codex metadata,
or MCP interface is an optional adapter and may be added later if it improves discovery.

### 5.3 Install record

A capable installer records at least:

```yaml
coordinate: aip/starhorse-access
version: 2.0.2
source:
  repository: https://github.com/skill-commons/skill-commons
  commit: <exact commit>
  path: skills/starhorse-access
tree_digest: sha256:...
policy:
  decision: allow-with-conditions
  decided_at: ...
```

The installer inventories files and requested capabilities before mutation, avoids
overwriting locally changed skills, and records local divergence. Standard clients that
do not support this richer record may still install the directory normally.

---

## 6. Catalog, trust, and governance

### 6.1 Generated catalog

The first catalog is static and Git-versioned, not a mandatory database service.
Implemented outputs are:

- `catalog/index.json` — machine-readable coordinates, versions, paths, package tree
  digests, descriptions, research facets, status, and source information;
- `catalog/README.md` — generated human index;

Planned additions are:

- `catalog/advisories/` — signed or reviewed negative-state records;
- optional detached signatures over tagged catalog snapshots.

The committed index must not attempt to contain the commit hash that contains the index;
that would be self-referential. The checkout commit is supplied by Git, while a tagged
release snapshot or CI artifact may map protected tags to resolved commits. The catalog
is a derived view. A mismatch is resolved in favor of the tagged package directory and
reviewed governance records, followed by catalog regeneration.

Search can begin with forge search and static facets. PostgreSQL, vector search, a web
portal, REST, or MCP becomes justified only after corpus size and user behavior demand it.

### 6.2 Git-native trust foundation

Phase 1 uses controls familiar to maintainers:

- protected `main` and protected release tags;
- required pull-request review and CODEOWNERS ownership;
- CI validation and preserved reports;
- exact commit and tree-digest pinning;
- signed commits or tags where operationally supportable;
- explicit namespace, authorship, license, and redaction assertions;
- versioned advisories, deprecations, yanks, and corrections;
- one-way mirrors and regular backup/restore tests.

This is less elaborate than the full OCI evidence model but materially stronger than an
unreviewed repository of prompts. The architecture can add transparency logs or signed
catalog snapshots without changing the skill format.

### 6.3 Scientific trust

Software integrity is not scientific validity. The Commons separately records:

- who authored, curated, reviewed, or reproduced a skill;
- what input data, software, and assumptions were used;
- which contracts passed on which target and date;
- known failure modes and excluded uses;
- citations and credit;
- reproduction attempts, failures, corrections, and superseding releases.

Bad or outdated releases remain addressable for reproducibility but can be deprecated,
yanked from default discovery, or accompanied by advisories. Their history is not erased.

---

## 7. Ori and other clients

Ori is the first rich client, not a prerequisite for the Commons.

Ori should implement the package in this order:

1. Discover and read standard `SKILL.md` exactly as other Agent Skills clients do.
2. If present and supported, read `research-skill.yaml` for dependencies, capabilities,
   research metadata, policy, and client extensions.
3. Validate the sidecar and lock before relying on them.
4. Show a pre-install inventory and policy result.
5. Install from an exact Git commit/tag and path.
6. Provision dependencies in an isolated environment according to local policy.
7. Record the source identity and local divergence.

Unknown optional extensions are preserved and ignored. Unknown required extensions block
a compatibility claim. An extension cannot grant undeclared capabilities or weaken core
policy.

Other clients can stop after step 1 and remain useful. Adapters should improve ergonomics
without forking package content or creating a competing identity.

---

## 8. OCI status and re-entry criteria

### 8.1 Current status

OCI is a **parked, optional export profile**.

The existing StarHorse 2.0.2 vertical slice, publication scripts, probe records, signed
catalog, evidence, and mirror verification remain preserved under
`warehouse/oci-phase0/`. They are inert engineering evidence and may support
institutional or archival use. The small deterministic packer remains active because it
is useful independently of OCI publication.

For new releases:

- contributors are not required to understand or use OCI;
- ordinary installation does not depend on a registry;
- OCI export must start from a tagged canonical Git directory;
- the export must not synthesize different skill content under the same version;
- OCI failures must not block ordinary Git contribution or installation unless an
  explicitly selected institutional profile requires OCI;
- Git and OCI must never both claim to be independent authorities.

### 8.2 Re-entry gate

Reconsider first-class OCI distribution only when at least one demonstrated need exists:

- several institutions operate independent synchronized mirrors;
- packages contain artifacts for which Git is operationally unsuitable;
- consumers require digest-addressed deployment and portable attestations;
- release volume or bandwidth makes Git distribution inadequate;
- institutional policy requires registry-native SBOM, signature, or provenance flows;
- non-Ori consumers request the OCI interface;
- a funded operational team can maintain registry, signing, backup, incident response,
  and compatibility testing without reducing community support.

The decision requires evidence from real users and a migration plan. Technical elegance
alone is not a trigger.

---

## 9. Hosting and federation

The public GitHub repository
[`skill-commons/skill-commons`](https://github.com/skill-commons/skill-commons) is the
singular canonical forge. Issues, pull requests, protected branches, and release tags
live there.

The private AIP GitLab project `physicsllm/skill-commons/spec` is a one-way institutional
backup. It does not accept independent package releases. The prior OCI carrier projects
are archived, preserving their registry evidence without presenting empty sibling
projects as active parts of the hub.

Institutional identity, ORCID, and namespace control remain curator-reviewed claims; the
choice of forge does not establish them automatically. Backup and restore checks must
preserve full history, protected release tags, and negative state.

This hosting decision is recorded in
[`ADR 0001`](adr/0001-public-github-canonical.md).

Long-term federation can index multiple canonical repositories through external-catalog
records and signed snapshots. It does not require copying every skill into one repository
or making OCI mandatory.

---

## 10. Delivery plan

### Phase 0G — Git pivot and first real package

Status: **implemented on 2026-07-23**.

- Adopt Agent Skills as the required portable format.
- Make Git the current authority.
- Materialize the complete `starhorse-access` 2.0.2 package under
  `skills/starhorse-access/`.
- Preserve exact reviewed bytes and the deterministic package digest.
- Validate the Agent Skills profile in CI.
- Retain the OCI vertical slice as historical and optional evidence.

### Phase 1A — contribution-ready collection

Status: **in progress; public hosting, contributor guidance, catalog generation, and the
initial protected tag convention were implemented on 2026-07-24**.

- Add contributor and curator documentation with minimal templates. **Done.**
- Define and enforce the per-skill protected tag convention. **Done for the initial
  repository.**
- Generate a static human and machine catalog from Git. **Done.**
- Add version-bump and released-byte immutability checks.
- Add advisory/deprecation/yank records and negative-state generation.
- Add portable prerequisite/setup linting for skills with dependencies.
- Decide public visibility and the canonical community contribution forge. **Done; see
  ADR 0001.**
- Migrate a small, rights-cleared set of additional AIP skills.

### Phase 1B — native client paths

- Teach Ori to install exact Git paths and read the sidecar before legacy frontmatter.
- Add pre-install inventory, policy output, isolated dependency provisioning, and local
  divergence protection.
- Document tested installation recipes for major Agent Skills clients.
- Add optional adapters only where they measurably reduce user friction.

### Phase 2 — evidence and community growth

- Add review, reproduction, correction, citation, and contributor-credit workflows.
- Add external-catalog records rather than republishing third-party skills.
- Improve static search and add a service only when usage justifies one.
- Exercise backups, one-way mirrors, and restoration.
- Evaluate DOI/RO-Crate preservation for significant scholarly releases.

### Phase 3 — evidence-driven federation

- Revisit signed snapshots, multi-institution governance, registry exports, and OCI only
  against the re-entry gate in §8.2.
- Preserve Git and Agent Skills as the contributor-facing and portable base even if richer
  distribution layers are added.

---

## 11. Acceptance criteria for the Git-first architecture

The architecture is working when:

1. A new contributor can understand the repository and propose a skill using ordinary
   Git and Markdown.
2. A standards-compatible agent can use a published skill directory without Ori or OCI.
3. A complete install can be pinned to an exact commit/tag and reproduced.
4. CI catches invalid frontmatter, inconsistent identity/license, unsafe files, and
   unreviewed release mutations.
5. A generic agent can find human-readable prerequisites and verification instructions.
6. Ori can add policy and dependency automation from the sidecar without changing the
   portable `SKILL.md` contract.
7. A deprecated or dangerous release remains reproducible but is excluded from default
   discovery with visible negative state.
8. Public corpus history can be cloned and restored without the Commons service, an OCI
   registry, or a particular vendor.
9. At least several rights-cleared skills and external contributors demonstrate that the
   workflow can grow beyond the founding team.

---

## 12. Decision record and compatibility note

This v0.5 architecture changes these v0.4.1 decisions:

| v0.4.1 | v0.5.1 |
|---|---|
| Git is authoring only; OCI is canonical distribution. | Git is canonical publication and distribution for the current phase. |
| Installed identity is primarily an OCI digest. | Installed identity is repository + exact commit/tag + path, optionally with a tree digest. |
| Registry and signed catalog are required release authorities. | Protected Git review/tag is the base authority; signed catalogs are optional higher-assurance profiles. |
| Agent consumption expects a Commons/Ori artifact reader. | Standard `SKILL.md` is directly consumable; the sidecar reader adds richer behavior. |
| Git + OCI + custom catalog is the immediate recommended stack. | Git + generated static catalog is immediate; OCI and services are demand-driven additions. |

The following v0.4.1 decisions remain:

- the corpus and specification outlive the platform;
- Agent Skills plus `research-skill.yaml` is the package model;
- structured research metadata, provenance, credit, relations, capabilities, locks,
  contracts, advisories, and negative state matter;
- trust dimensions remain separate;
- explicit publication, accountable human review, local policy, one canonical source,
  one-way mirrors, and replaceable infrastructure remain mandatory;
- OCI probe findings remain mandatory for any future OCI export that claims the exercised
  publication profile.

This architecture should be amended by decision record when evidence changes it. It
should not drift through undocumented implementation shortcuts.
