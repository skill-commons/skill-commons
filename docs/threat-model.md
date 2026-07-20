# Phase 0 threat model

## Assets and trust boundaries

Skill packages contain instructions and may contain executable code. The protected assets
are researcher data, credentials, workspaces, institutional services, namespace identity,
catalog integrity, and the reproducibility record. Git source, package authors, imported
catalogs, generated metadata, and package contents remain untrusted until independently
validated.

## Principal threats

- Path traversal, absolute paths, unsafe symlinks, device files, archive bombs, or hidden
  install hooks in a package.
- Prompt instructions that exfiltrate data, request secrets, weaken client policy, or
  conceal external side effects.
- Dependency confusion, mutable VCS references, unpinned containers, compromised build
  workers, or lock files generated for the wrong architecture.
- Namespace takeover, false authorship, license laundering, or republication of imported
  work as an institutional original.
- Stale catalog snapshots that omit a newer advisory, yank, tombstone, or revocation.
- Client extensions that smuggle capabilities absent from the core declaration.
- Private prompt, transcript, data, token, hostname, workspace, or user material entering
  a harvested public candidate.
- Non-deterministic packing or evidence detached from the artifact digest it claims to
  describe.

## Phase 0 controls

- Allowlisted publication only; no unrestricted public upload or execution.
- Deterministic, bounded, cross-platform safe-path packing and exact digest identity;
  structured YAML input is also depth-limited before construction.
- Separate schema, interoperability, client-compatibility, and publication-policy checks.
- Reviewable conversion reports with field-level loss accounting and no source mutation.
- Package-wide license evidence and explicit provenance/namespace review.
- Core capability declarations that extensions cannot reduce or bypass.
- Metadata-only remote discovery followed by a trusted local policy and approval step.
- A catalog payload format with sequence, expiry, previous digest, and inseparable
  negative state, plus the requirement that a trusted external pipeline sign it before
  clients treat it as authoritative.
- No raw conversations, prompts, private test data, or secret values in provenance.

## Deferred controls

Isolated execution workers, incident response automation, federated mirrors, identity
delegation, transparency logs, evidence expiry policy, and stale-mirror drills enter the
Phase 1 implementation. Their schemas and trust seams are designed in Phase 0, but they
must not be described as operational before deployment and exercise.
