# Client extension contract

`research-skill.yaml` reserves `extensions` for structured, globally namespaced client
data. A profile key uses reverse-DNS form and contains:

```yaml
extensions:
  de.aip.ori:
    schema: urn:skill-commons:extension:de.aip.ori:1
    required: false
    data:
      activation:
        requires_toolsets: [web]
```

Rules:

- The schema identifier is immutable and versioned. Validators resolve only locally
  pinned, allowlisted extension schemas; they never fetch arbitrary schemas from a
  package-provided URL.
- Unknown optional extensions are preserved and may be ignored. An unknown required
  extension prevents a client from claiming compatibility or installing the package.
- An extension cannot add undeclared processes, hosts, secrets, writes, side effects,
  dependencies, or paid services. Core declarations are authoritative.
- Sidecar discovery is convention-based: clients look for `research-skill.yaml` in the
  package root. A `SKILL.md.metadata` pointer is optional and never required.

The initial `de.aip.ori` schema preserves current activation, configuration and discovery
semantics. Ori owns the runtime implementation; Skill Commons owns the envelope and the
cross-file conformance contract.
