# Published release record

This directory records the exercised Phase 0B publication of
`aip/starhorse-access@2.0.2`.

- OCI subject:
  `gitlab-p4n.aip.de:5005/physicsllm/skill-commons/aip/starhorse-access@sha256:fe3722fdc6a3892d4084907a65dbb3bafdd3421f12373e43884fd5690e477275`
- Deterministic package bytes:
  `sha256:a375de9ccbc9abf40b9bda1efd7e8b4a55704fd3f64c0e4a8f81aa26a86913b9`
- Mirror:
  `gitlab-p4n.aip.de:5005/physicsllm/skill-commons/mirror-aip/starhorse-access`
- Persistent tag in both repositories: `rel-2.0.2`

`catalog.json` is the authoritative catalog payload only when its detached
`catalog.sig` verifies with `catalog.pub` and the live evidence-tag descriptors still
match `publication-status.json`. The public key is a dedicated **Phase 0B pilot key**,
not a production or federated trust root. The encrypted private key and its passphrase
are not in this repository; they are restricted to the publisher account on the DGX.

The evidence directory contains the seven predicates attached to the subject: candidate
validation, static contract result, pre-install inventory, local policy result, static
scan, in-toto/SLSA-shaped provenance, and SPDX SBOM. `publish-transcript.txt` is the
redacted successful run. It records two identical pushes, primary verification, explicit
evidence-tag reconstruction in the mirror, mirror verification, and catalog signing.
`consumer-verification.json` is a subsequent independent run of `verify-release` against
the signed catalog and live primary/mirror state.

Acceptance gates 4 (publisher isolation) and 5 (backup/restore) remain open. Gate 2 is
conditional on retaining `rel-*`/`sha256-*` tags and checking live evidence descriptors;
the release does not claim otherwise.
