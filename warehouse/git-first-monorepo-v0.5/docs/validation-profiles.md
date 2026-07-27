# Validation profiles

Schema validity is necessary but insufficient. The reference tooling reports three
independent profiles so a migration problem cannot be mistaken for a publication or
interoperability decision.

## Agent Skills

This profile has two layers:

1. normative checks derived from the published Agent Skills field and naming rules;
2. interoperability with the pinned `skills-ref` reference implementation.

The distinction matters because `skills-ref` 0.1.1 rejects some YAML constructs, such as
flow-style sequences, that a general YAML parser accepts. Portable output follows the
reference implementation's stricter serialization, while reports retain both verdicts.

## Ori compatibility

The first contract is `ori-frontmatter-v1`, matching the runtime behavior surveyed in
July 2026. It checks directory-based identity, `description`,
`prerequisites.python`, `platforms`, and the structured `metadata.hermes` activation and
configuration fields.

An `ori-sidecar-v1` contract will be added with the Ori owner before portable normalized
frontmatter becomes the default. Until then, conversion reports propose a normalized
frontmatter block but never apply it.

## Commons candidate readiness

The Phase 0 allowlist policy requires, at minimum:

- structural schema validity;
- a canonical pinned source revision and repository-relative path;
- namespace-control and publication-rights approval outside the author-controlled
  manifest;
- a non-empty SPDX `SKILL.md.license` semantically equivalent to
  `research-skill.yaml.package.license`, with non-conflicting, package-wide evidence;
- resolved authorship;
- complete dependency and capability declarations;
- safe referenced and packaged paths;
- a reviewed public diff and redaction result.

The current CLI proves the local structural subset. It always emits
`COMMONS_EXTERNAL_ATTESTATIONS_REQUIRED` as a warning because author-controlled files
cannot prove namespace control, publication rights, or a reviewed public diff/redaction
decision. These are verified by the separate curator-authorized catalog gate; a detached
catalog signature is still required after snapshot construction. The Phase 0 `catalog`
command only assembles structurally valid, evidence-digest-bound records supplied by that
trusted pipeline; it does not authenticate a caller's `verified` labels by itself.

## Exit codes

- `0`: selected profiles contain no failures or blockers;
- `1`: a deterministic report was produced, but a selected profile failed or is blocked;
- `2`: invocation, input parsing, or another operational error prevented a report.
