# CRS Hermes selection-lead update decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-08-11

**Accountable reviewer:** Tom Tong (`tomtong2015`)

## Decision

The eleven Skill Commons-maintained skills below remain at `curated` review maturity for
their exact trees in CRS merge commit
`dccccb8a1bb3926de04e00e630d0a455cc9579a9`:

| Skill | Version | Git tree |
|---|---:|---|
| `drphub-products` | `1.0.1` | `dbb4356b6ab299ab177f3d4f66c0a41fcd78629d` |
| `dt4acc-host-smoke-test` | `2.0.1` | `5efbf09fd153539add371201fd8e2de251103bf5` |
| `dt4acc-operations` | `1.0.1` | `2b4377cf1b9c75be692ae7b3631117b16bbac8f4` |
| `jubik-bootstrap` | `1.0.1` | `816e1e48f21a7b9adf0c2f2a3f04b676cd03a6ef` |
| `large-tabular-visualization` | `2.0.2` | `90bad822b9cd3b05748cf51e1e9b0bbd5e8773a1` |
| `nifty-re-variational-inference` | `1.0.1` | `44e43748e039251818b60f3a8706eb767f2f1c87` |
| `python-library-docs-first` | `2.0.1` | `77bb31cb83e9d3ec0ed531aecaa4db8da8e5fe9a` |
| `reana-operator` | `1.0.1` | `10247fefc562cbebe5f3169a1d3e837af315e1e8` |
| `reana-workflow-authoring` | `1.0.1` | `777eca16d210c1f222de4b85374330d95e24f18f` |
| `research-paper-evidence-workflow` | `1.0.1` | `101363fc87305fc256d7d0df8599262190cd05b9` |
| `rss-feed-monitor` | `2.0.1` | `8140059b198afe0666c7315fb3c4539b541f97a4` |

This is a new decision for changed directory trees, not an automatic carry-forward from
an earlier assessment. Between CRS commits
`74a11aaad374108c60162e879390ee3604efddd1` and
`dccccb8a1bb3926de04e00e630d0a455cc9579a9`, each listed skill directory changes only
the `description` and patch `version` fields in `SKILL.md` frontmatter. The workflow
bodies, scripts, references, assets, dependency declarations, and locks are unchanged.

The revised descriptions make the capability and object distinguishable inside Hermes'
current 57-character selection surface while retaining or restating the detailed trigger,
workflow, and safety-boundary prose that becomes available after selection. Existing
evidence facets remain applicable to the unchanged operational content, and `curated`
maturity is explicitly reaffirmed for these new exact trees.

## Evidence scope

- **Identity and provenance:** the registry revision and all eleven directory trees were
  resolved from the merged CRS `main` commit. Names, paths, categories, authorship,
  licenses, and provenance remain unchanged.
- **Selection metadata:** every affected description now opens with a complete,
  distinguishing sentence no longer than 57 characters. The leads separate related
  capabilities such as local REANA authoring from remote read-only inspection, dt4acc
  host smoke testing from pinned-SIF operation, and J-UBIK bootstrap from NIFTy.re
  inference.
- **Automation:** the CRS validator mirrors Hermes' 60-character output—57 source
  characters plus an ellipsis—and emits a non-blocking GitHub warning when an overflowing
  description lacks a complete opening sentence in that surface. Regression tests cover
  truncation and advisory-warning behavior, and the generated README documents the
  convention.
- **Security and redaction:** the exact changed skill trees were reviewed. Their only new
  material is public selection metadata; no embedded secrets, private data, prompts,
  transcripts, personal information, credential behavior, external authorization, or
  side-effect scope was added.
- **Operability:** CRS pull request 8 passed the always-on CI with 143 tests passing and
  one existing opt-in NIFTy.re integration skipped. The separately pinned CPU scientific
  integration for J-UBIK and NIFTy.re also passed. These runs establish regression
  consistency, not a new operational or scientific claim.
- **Scientific validity:** no dataset, numerical result, model, inference, visualization,
  or scientific conclusion changed or received new validation.
- **Maintenance:** the eleven patch-version metadata updates were reviewed and merged in
  CRS before this registry update. Future changes to any registered directory tree
  require another assessment.

## Limitations

- The 57-character selection surface reflects the current cited Hermes behavior. Hermes
  or another client can expose a different budget, normalization, metadata set, or
  selection mechanism.
- The advisory audit checks whether an opening sentence fits structurally; it does not
  prove semantic distinctness, correct model selection, or appropriate use for every
  prompt.
- Skill selection by a language model is not deterministic. Improved metadata cannot
  replace reading the full skill, applying its boundaries, or enforcing local policy.
- No executable, dependency, lock, platform, network, security, or scientific behavior
  was changed or independently revalidated by this metadata-only assessment. Earlier
  decision-specific evidence and limitations remain relevant to those scopes.
- Independent scientific reproduction is not claimed for any of the eleven skills.

## References

- [CRS pull request 8](https://github.com/skill-commons/curated-research-skills/pull/8)
- [CRS issue 7](https://github.com/skill-commons/curated-research-skills/issues/7)
- [Merged CRS source](https://github.com/skill-commons/curated-research-skills/tree/dccccb8a1bb3926de04e00e630d0a455cc9579a9)
- [CRS validation run](https://github.com/skill-commons/curated-research-skills/actions/runs/31533149832)
- [CRS pinned scientific integration](https://github.com/skill-commons/curated-research-skills/actions/runs/31533149856)
- [Previous CRS seed decision](2026-08-06-crs-seed.md)
- [Previous CRS Python-environment decision](2026-08-11-crs-python-environments.md)
- [Review-maturity policy](../../docs/adr/0003-review-maturity-and-evidence.md)
