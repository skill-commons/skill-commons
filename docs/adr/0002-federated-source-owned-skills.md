# ADR 0002 — Skills remain in source-owned repositories

**Status:** accepted
**Date:** 2026-07-28

## Context

Copying skills into one hub splits their history from the maintainer's repository,
obscures upstream changes, and makes the hub a second publication authority. It also
scales poorly: package registries normally index independently maintained packages
rather than absorbing every package's source.

Hermes already supports Git-backed skill taps and skill directories with their own
references and scripts. Skill Commons does not need a competing package format.

## Decision

Skill Commons is a federated metadata registry:

- every active record names one canonical Git repository and directory;
- skill content, support files, history, releases, and maintenance stay upstream;
- the registry stores the last reviewed commit and directory Git tree;
- scheduled checks report upstream directory changes for curator review;
- `categories` is an editorial discovery taxonomy, not a runtime installation format;
- generated README and JSON views are derived from registry metadata;
- Commons-maintained curated skills live in the separate
  `skill-commons/curated-research-skills` Hermes tap.

The registry YAML is an implementation detail of this hub, not a new skill packaging
standard.

## Consequences

- Contributors update one authoritative skill source.
- The hub can list third-party skills without republishing their bytes.
- Reference folders and scripts remain attached to their `SKILL.md`.
- Upstream changes are visible but are not accepted automatically.
- Users install from source with Hermes or another source-compatible client.
- The former copied-skill sidecars, schemas, packer, and validator are inert historical
  material under `warehouse/`.
