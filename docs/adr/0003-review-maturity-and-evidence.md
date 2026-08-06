# ADR 0003: Review maturity and scoped evidence

**Status:** accepted

**Date:** 2026-08-06

## Context

Skill Commons must make useful community-maintained skills discoverable without claiming
that every registered skill has the same degree of testing, hardening, scientific review,
or long-term support. A single pass/fail publication gate would either exclude valuable
work or overstate what review established.

Earlier Commons designs proposed the sequence `unreviewed -> community -> reviewed ->
curated`. They also established the more important rule that identity, integrity,
licensing, security, functionality, scientific validity, reproducibility, maintenance,
capabilities, and risk are separate claims. The implemented federated registry already
pins an exact source commit and skill-directory tree, but it does not yet expose review
maturity or the evidence behind a curator decision.

## Decision

Every active registry entry records a review-maturity decision owned by Skill Commons and
bound to its exact repository, revision, path, and Git tree. The decision uses a named,
versioned policy and one of three maturity values:

- **`community`** passed the Commons admission floor in a maintainer-supported canonical
  source. It is suitable for discovery but has not completed the Commons independent
  technical-review procedure.
- **`reviewed`** is `community` plus an accountable Commons reviewer inspecting the
  complete exact tree, its dependencies and capabilities, scripts and references, and
  proportionate operational evidence such as setup, tests, or a bounded representative
  workflow.
- **`curated`** is `reviewed` plus deliberate editorial and safety curation to a
  supportable scope, an identified continuing steward, and repeatable regression or
  contract evidence appropriate to the skill's claims and risk.

`unreviewed` remains an intake or external-observation state and is not valid for an
active catalog entry. `status: active` remains a lifecycle/discovery field independent of
review maturity.

### Admission floor

Every active skill must have:

- a maintainer-confirmed canonical public source and an accountable right to publish;
- clear authorship, derivation, attribution, and licensing;
- an exact repository, commit, directory path, and Git tree;
- a complete installable directory with a valid, useful `SKILL.md` and no broken local
  references;
- clear tools, network use, named credentials, writes, side effects, and verification
  expectations;
- an explicit redaction review with no embedded secrets or private material; and
- no deceptive scientific claim or known critical unsafe default such as credential
  exfiltration, broad destructive cleanup, or unrestricted high-consequence control.

The registry, category, generated-view, and upstream-identity checks must also pass.

The following improve evidence but are not universal admission requirements: a committed
lockfile, repository-wide lint cleanliness, broad platform coverage, independent
scientific reproduction, comprehensive tests, and perfect network containment. Curators
record their actual state and known limitations instead of silently treating them as
either mandatory or proven.

### Evidence remains multidimensional

Review decisions record scoped findings for:

- identity and publication authority;
- source integrity and provenance;
- license and authorship;
- packaging and interoperability;
- installation and behavioral tests;
- security review;
- scientific validation;
- reproducibility;
- maintenance and freshness; and
- requested capabilities, side effects, risk, and known limitations.

These facets are descriptive evidence, not numeric scores or a second hidden tier system.
An unassessed facet must say so. Scientific validity is never inferred from installation
or software-test success.

### Registry-owned decisions

The active registry record carries the authoritative maturity, date, assessors, scoped
evidence, and known limitations beside the exact source identity. It also points to a
reviewed rationale under `registry/reviews/`. Review metadata is not a required upstream
sidecar and does not add Skill Commons-specific fields to a community maintainer's
`SKILL.md`.

Any change to the registered skill tree requires a new decision. Maturity never advances
automatically because a branch moved, a test passed, or a source belongs to a particular
organization. Promotion or demotion is an accountable catalog change under review.

The completed 2026-08 Commons curation program seeds the existing 22 CRS skills as
`curated` under one explicitly scoped decision. This records the work already performed;
it does not newly claim independent scientific reproduction for every skill.

### Client interpretation

Review maturity does not:

- grant installation or runtime permission;
- authorize network, filesystem, process, secret, or external-system access;
- guarantee security in every environment;
- assert universal scientific correctness;
- replace exact evidence, limitations, or local institutional policy; or
- imply that a `community` skill is unpopular, abandoned, or low quality.

Clients may use maturity and evidence as inputs to a local policy decision, but must not
turn `curated` into an automatic global trust badge.

## Consequences

Skill Commons can admit useful, maintainer-supported work at a clear and achievable floor
while making stronger review visible and promotable. Maintainers keep their normal source
format and are not required to adopt Commons infrastructure. Curators take on the cost of
assessment records and must keep their language scoped to the exact evidence.

The catalog schema becomes richer, and consumers must distinguish lifecycle status from
review maturity. Review records add some maintenance overhead, but they also preserve the
rationale needed to update, promote, demote, deprecate, or reproduce a skill responsibly.
