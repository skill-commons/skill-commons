# ADR 0001 — Public GitHub is the canonical forge

**Status:** accepted
**Date:** 2026-07-24

## Context

The initial AIP GitLab group is private, and the project owner cannot change its group
visibility. Community contribution and ordinary public Git access are immediate survival
requirements for Skill Commons.

Maintaining two writable repositories would create competing release authorities,
duplicated review, and ambiguous issue and pull-request locations.

## Decision

`https://github.com/skill-commons/skill-commons` is the canonical public repository for
source, contributions, issues, pull requests, protected release tags, and generated
catalogs.

The existing AIP GitLab `physicsllm/skill-commons/spec` project is a private, one-way
institutional backup. It does not accept independent package releases. Its four
OCI-carrier sibling projects are archived while their registry evidence remains
preserved.

## Consequences

- Public contributions use GitHub forks and pull requests.
- Canonical Git identity is the GitHub repository, exact commit or protected tag, and
  `skills/<name>` path.
- The full pre-migration Git history is preserved.
- Existing upstream provenance recorded inside migrated packages remains unchanged.
- A future forge move requires another recorded decision and one clearly designated
  authority.
