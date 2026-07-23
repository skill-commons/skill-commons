# Claude marketplace adapter sketch

Phase 0 specifies export as a projection of an already reviewed Commons collection.
Export never changes member package digests and never makes Claude's marketplace metadata
authoritative for Commons identity.

The adapter should:

- generate host-specific marketplace metadata from collection and release records;
- retain Commons coordinates, exact digests, source, license and attribution in a
  round-trip record;
- emit portable `SKILL.md` plus package resources only when the release license and target
  capability model permit it;
- report every unsupported or lossy field rather than hiding it;
- keep structured Commons and Ori metadata in `research-skill.yaml`, not nested
  `SKILL.md.metadata`;
- treat installation as a local trusted-client action, not remote instruction execution.

Import is metadata-first. An observed marketplace entry becomes an external-catalog record
until provenance, license, namespace and artifact equivalence are independently verified.
