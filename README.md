# Skill Commons

This repository is the Git-native home of published Skill Commons skills, the Commons
package formats, and the small reference tools used to validate them. Skill Commons is
agent-neutral: Ori is one client, not the package format's owner.

Published skills use the open [Agent Skills](https://agentskills.io/) directory format.
Each installable skill has a root `SKILL.md`; no Claude plugin wrapper or OCI-aware reader
is required. Commons-specific research, dependency, capability, and provenance data live
in optional sidecars beside that portable entry point.

The format standardizes what an agent receives, not one universal installation command.
Point an Agent Skills-compatible client at the skill directory, or copy/symlink that
directory into the client's normal skills location. Clients that accept a Git URL plus a
subdirectory can use `skills/starhorse-access` directly.

Status: **v0.1.0-draft / Phase 0**. Schemas and command behavior may change before the
first stable release. Published package bytes and digests are nevertheless immutable.

## What is implemented

- A directly browsable and installable `skills/` tree. The first reviewed package is
  [`starhorse-access`](skills/starhorse-access/).
- Draft JSON Schemas for `research-skill.yaml`, `research-skill.lock`, and catalog
  snapshot payloads intended for detached signing.
- Three deliberately separate validation profiles:
  `agent-skills`, `ori-compatibility`, and `commons-publication`.
- A report-first converter for current Hermes/Ori frontmatter. It emits a sidecar and
  review report; it never rewrites `SKILL.md`.
- A deterministic, safe-path tar.gz packer.
- A deterministic static-catalog generator.
- An optional OCI export path that verifies immutable Git input, target locks,
  deterministic package and push digests, signed evidence, mirror reconstruction, and a
  detached signed catalog. OCI is preserved as an exercised distribution backend, not a
  prerequisite for contributing, browsing, or installing a skill.
- A source-pinned survey fixture for
  [`arm2arm/AstroAgentAssistant`](https://github.com/arm2arm/AstroAgentAssistant)
  commit `ef78afcf1412575dd23e8e88c01dbf50b8b02836`.

## Non-normative Phase 0 stretch sketches

The schemas for collections, external-catalog records, installation profiles, and
negative-state/tombstone records are **design sketches, not supported interchange
contracts**. They reserve the RFC's trust boundaries and principal concepts so prototypes
can exercise them, but their fields, identifiers, and signing envelopes may change before
promotion into the normative specification. In particular, no client should treat a
stretch-schema-valid document as signed, authorized, installable, or publication-ready.

Each stretch schema carries an explicit `NON-NORMATIVE PHASE 0 STRETCH SKETCH` comment.
Promotion requires exercised cross-object constraints, signing and delegation semantics,
and compatibility fixtures from at least one producer and consumer.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-groups
uv run pytest

uv run skill-commons validate examples/catalog-query-demo --profile all
uv run skill-commons validate skills/starhorse-access --profile agent-skills
uv run skill-commons validate skills/starhorse-access --profile commons-publication
uv run skill-commons convert /path/to/legacy-skill \
  --namespace aip \
  --source-url https://github.com/arm2arm/AstroAgentAssistant \
  --source-revision ef78afcf1412575dd23e8e88c01dbf50b8b02836 \
  --source-path astronomy/legacy-skill
uv run skill-commons pack examples/catalog-query-demo --output /tmp/catalog-query-demo.tar.gz

uv run skill-commons prepare-release \
  releases/aip/starhorse-access/2.0.2/publication.yaml \
  --source-repository /path/to/reana-env \
  --out /tmp/starhorse-prepared
```

`--source-path` names the package directory inside the pinned repository, not its
`SKILL.md`. `convert` writes the manifest to stdout unless `--output` or `--out` is
supplied; `--report` independently writes the report. It never modifies its input.
Reports include both the portable and Ori-bridge proposed
frontmatter diffs; `--projection` chooses which one an `--out` candidate receives.
Applying the portable projection upstream is intentionally deferred until a client reads
`research-skill.yaml` first.

## Validation profiles

| Profile | Question answered | Authority |
|---|---|---|
| `agent-skills` | Is `SKILL.md` portable under the public Agent Skills reference validator? | Agent Skills specification/reference library |
| `ori-compatibility` | Will today's Ori/Hermes runtime preserve identity, dependencies, activation, and configuration semantics? | Ori compatibility contract |
| `commons-publication` | Is the package locally ready to enter the curator-authorized publication gate? | Skill Commons candidate-readiness policy and schema |

A skill may pass one profile and fail another. Missing `license` frontmatter, for
example, is permitted by Agent Skills but blocks Commons publication until an SPDX
expression appears equivalently in portable frontmatter and the sidecar, with supporting
package-wide evidence.

## Repository layout

```text
skills/                     Published, Git-native Agent Skills packages
schemas/                    Core schemas plus clearly marked non-normative stretch sketches
src/skill_commons/          Reference CLI and library
tests/                      Contract and regression tests
examples/                   Converted Phase 0 reference packages
fixtures/surveys/           Source-pinned, generated corpus observations
docs/                       Threat model, migration and extension contracts
adapters/                   Phase 0 design sketches for external ecosystems
capability-taxonomy.yaml    Initial capability vocabulary
```

The architecture rationale remains in the Ori project's
[`ORI_SKILL_COMMONS_ARCHITECTURE.md`](https://gitlab-p4n.aip.de/physicsllm/c.1/drp-hermes/-/blob/main/docs/ORI_SKILL_COMMONS_ARCHITECTURE.md)
during the handoff. Normative format changes land here.

## Trust and publication boundary

Only reviewed directories merged under `skills/` are Git-native Commons publications.
Survey fixtures, converter output, and skills merely observed in other repositories are
not publications. Observed community and client-bundled skills retain their upstream
identity and do not become `aip/*` merely because a converter can parse them.

Local `commons-publication` validation always warns that namespace control, publication
rights, and reviewed redaction require external attestations. `pack` only creates
candidate bytes. The catalog builder is a deterministic structural assembler for trusted
pipeline inputs: it requires evidence digests for verified license, publisher-authority,
namespace-control, and redaction assessments, but does not authenticate those records.
For the Git-native collection, protected review and the exact Git commit identify the
published state. A detached signed catalog remains available for higher-assurance or OCI
distribution profiles; it is not required for ordinary Agent Skills installation.

The exercised optional GitLab OCI workflow and its mandatory registry invariants are
documented in [`docs/oci-publication.md`](docs/oci-publication.md). OCI manifest
timestamps are pinned, evidence tags are explicitly reconstructed in mirrors,
release/evidence retention tags are preserved, and live tag descriptors are checked
against the signed catalog. Publisher-isolation and backup/restore acceptance gates remain
explicitly open.

Client extensions are structured, namespaced sidecar data. They may add activation or
UI hints, but they may not weaken core capability, dependency, license, or provenance
declarations.

Canonical bytes, tree binding, archive normalization, and digest domains are defined in
[`docs/artifact-format.md`](docs/artifact-format.md).

## License

Code and specification text in this repository are licensed under Apache-2.0. Survey
fixtures contain factual observations and source coordinates, not copied skill bodies.
