# Warehouse

This directory preserves useful work that is not part of the current Git-first product
surface.

Warehouse material is:

- historical or experimental;
- excluded from the supported Python package, active schemas, generated catalog, and
  default CI checks;
- not a source of published skill bytes or current release authority;
- retained so future work can reuse exercised designs and evidence.

The last commit where all Phase-0 material occupied its original runnable paths is
`ac56d5a`. Use that commit when reproducing the old integrated toolchain.

## Contents

- [`oci-phase0/`](oci-phase0/) — deterministic packaging, signed catalog, registry,
  attestation, and mirror evidence from the optional OCI vertical slice.
- [`phase0/`](phase0/) — adapter sketches, surveys, placeholders, and non-normative
  schema experiments.
- [`handoffs/`](handoffs/) — dated coordination notes superseded by current repository
  documentation.

Material should leave the warehouse only after demonstrated user or operational demand
and an explicit architecture decision.
