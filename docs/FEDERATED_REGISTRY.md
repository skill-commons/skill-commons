# Federated registry

Skill Commons separates discovery from ownership. The hub answers “which maintained
skill should I use, and where is it?” The source repository answers “what are the skill
bytes, references, scripts, license, and history?”

## Active data

- [`registry/index.yaml`](../registry/index.yaml) lists canonical source coordinates and
  consolidation redirects together with review-maturity summaries.
- [`registry/reviews/`](../registry/reviews/) preserves the human rationale and evidence
  scope behind those summaries.
- [`categories/index.yaml`](../categories/index.yaml) assigns each active skill to one
  editorial category.
- [`catalog/index.json`](../catalog/index.json) and the root README are generated views.

The registry stores both an assessed commit and an assessed directory tree. The drift
checker fetches the commit, verifies that the recorded path is a directory with exactly
that tree, and compares the name, description, and version with its `SKILL.md`. The tree
is content-sensitive only to the registered directory, so unrelated upstream commits do
not create false skill updates.

## Hermes relationship

Skill Commons adopts Hermes' existing Git/tap model for Commons-maintained skills. The
canonical tap is:

```text
skill-commons/curated-research-skills
```

A direct skill coordinate has the form:

```text
owner/repository/skills/name
```

The catalog exposes that coordinate and a direct `hermes skills install` command. Hermes
resolves the repository's default branch when installing and keeps its own local
source/content tracking. Skill Commons verifies that its tracked branch is that default;
the registered commit is the curator's last assessed source state.

## Review maturity

Active records use `community`, `reviewed`, or `curated` review maturity under the named
Skill Commons policy. The value summarizes review process, not universal trust,
scientific correctness, or permission to install or execute the skill. Evidence facets
and known limitations remain visible beside the value. `unreviewed` material can be
considered during intake but is not an active catalog entry.

The source repository does not need Commons-specific metadata. Skill Commons owns the
review summary and decision record, and every decision remains bound to the exact source
tree. See [`ADR 0003`](adr/0003-review-maturity-and-evidence.md).

Categories are for browsing. They do not define a new Hermes plugin, manifest, or
installation unit. The upstream tap's `skills.sh.json` remains the Hermes-facing index
for that repository.

## Change flow

1. A maintainer changes the skill in its canonical source repository.
2. The drift check detects a different directory tree on the tracked branch.
3. A curator assesses the new skill, its references, risks, license, provenance, and
   applicable evidence facets.
4. A pull request updates the registered commit, tree, version, review decision, and
   description as needed.
5. The README and machine catalog are regenerated.

No source change is copied or silently accepted by the registry.

## Commons-maintained source

The Commons-maintained curated collection is hosted at
[`skill-commons/curated-research-skills`](https://github.com/skill-commons/curated-research-skills).
Its flat `skills/<name>/SKILL.md` layout and root `skills.sh.json` follow current Hermes
tap conventions. Future maintainers may register their own repositories instead of
moving content there.
