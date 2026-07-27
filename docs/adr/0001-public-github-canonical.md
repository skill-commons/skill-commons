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

The `skill-commons` GitHub organization is the canonical public forge. The
`https://github.com/skill-commons/skill-commons` repository is canonical for registry
metadata, categories, contributions, issues, pull requests, and generated catalogs.
Skill content is canonical in the source repository named by each registry record, as
refined by [ADR 0002](0002-federated-source-owned-skills.md).

The existing AIP GitLab `physicsllm/skill-commons/spec` project is a private, one-way
institutional backup. It does not accept independent package releases. Its four
OCI-carrier sibling projects are archived while their registry evidence remains
preserved.

## Consequences

- Public contributions use GitHub forks and pull requests.
- Canonical skill identity is its registered source repository, exact commit, and
  repository-relative directory.
- The full pre-migration Git history is preserved.
- Commons-maintained skills may use a separate repository in the public organization.
- A future forge move requires another recorded decision and one clearly designated
  authority.
