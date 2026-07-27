# Phase 0 migration contract

Conversion is an evidence-producing staging operation, not an in-place fixer.

For every legacy frontmatter field, the conversion report records one disposition:
`copied`, `normalized`, `preserved`, `proposed`, `conflict`, or `unmapped`. Unknown input
must never disappear.

Key rules:

- The directory basename is the candidate package name. A disagreeing `name` becomes an
  alias proposal and publication blocker rather than a silent rename.
- `--source-path` is mandatory and identifies the repository-relative package root. The
  converter binds the full safe source-tree snapshot in provenance; it does not infer an
  ambiguous `<name>/SKILL.md` path or hash only one file.
- Missing versions may be represented as the explicit assumption `0.1.0`, but remain a
  publication blocker.
- Free-form author strings are retained literally as one contributor; they are not split
  heuristically and do not prove publication rights.
- A missing per-skill license declaration remains `NOASSERTION`. Repository licenses are
  evidence observations, not automatic relicensing decisions. A reviewed publication
  candidate must place a non-empty SPDX expression in `SKILL.md.license` that is
  semantically equivalent to `research-skill.yaml.package.license`.
- `prerequisites.python` is copied verbatim. The inert legacy `dependencies` convention
  is never silently unioned with it: an equivalent value is normalized, a different value
  is a conflict, and dependencies-only input receives a proposed Ori bridge.
- `related_skills` remains a relation candidate. It is not upgraded automatically to the
  stronger `compatible_with` relation.
- Ori activation and config fields move into `extensions.de.aip.ori`.
- The Markdown body remains byte-for-byte unchanged in any proposed projection.
- Every report contains portable and Ori-bridge diffs. Selecting one candidate projection
  never hides the alternative or rewrites the source.

The report labels its validation subject explicitly: profiles run against the source
directory plus the proposed in-memory manifest. After review and candidate emission, run
`skill-commons validate <candidate>/package --profile all` before packing; the converter
does not mislabel a hybrid pre-emission check as a released-package verdict.

The Phase 0 converter has no `--fix` or `--in-place` mode. Applying the portable
projection waits for Ori's sidecar-first reader and human review.
