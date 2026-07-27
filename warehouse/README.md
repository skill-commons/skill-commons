# Warehouse

This directory preserves good design and implementation work that is not part of the
current federated registry surface.

Warehouse material is historical or experimental. It is excluded from the supported
Python package, generated catalog, and default CI checks, and it is not a source of
active skill bytes or current standards.

## Contents

- [`git-first-monorepo-v0.5/`](git-first-monorepo-v0.5/) — the former Commons-specific
  sidecar schemas, validator, converter, packer, architecture documents, and tests.
- [`oci-phase0/`](oci-phase0/) — deterministic packaging, signed catalog, registry,
  attestation, and mirror evidence from the optional OCI vertical slice.
- [`phase0/`](phase0/) — adapter sketches, surveys, placeholders, and non-normative
  schema experiments.
- [`handoffs/`](handoffs/) — dated coordination notes superseded by current repository
  documentation.

The last commit where the copied 11-skill monorepo and v0.5 machinery occupied their
original active paths is `1671891c805c8d2644f0fe86a0c84579ba17a3a0`. The 11 curated
skill directories now live in their complete, maintained form in
[`skill-commons/curated-research-skills`](https://github.com/skill-commons/curated-research-skills).

Material should leave the warehouse only after demonstrated demand and an explicit
architecture decision.
