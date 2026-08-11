# CRS Python-environment update decision

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-08-11

**Accountable reviewer:** Tom Tong (`tomtong2015`)

## Decision

The nine Skill Commons-maintained skills below remain at `curated` review maturity for
their exact trees in CRS merge commit
`74a11aaad374108c60162e879390ee3604efddd1`:

| Skill | Version | Git tree |
|---|---:|---|
| `astro-catalog-plotting-cache` | `2.0.1` | `5cf29a2fb99eb5a37bc634adfd10fd8473b0e5dd` |
| `calculator` | `1.0.2` | `6cca9161ab486fc1d156b29bdfc77381bf5be001` |
| `data-aip-de-s3` | `2.0.1` | `781fd0f4671557bffab222bb5a1ea2213ec43117` |
| `gaia-dr3-tap-query` | `3.0.1` | `41f7ba8c0479e421f32d48fd7c8ad0b0dd2c09af` |
| `large-tabular-visualization` | `2.0.1` | `3c282a30589a4d5570c8c30f9cdcf247e4f8a2cb` |
| `rave-dr6` | `2.0.1` | `0ea4a9465df0e67e66a97d3b762a623ec158e654` |
| `seaborn-paper-plots` | `1.0.2` | `17f845f49c24513c22c47e0caba5f8359852cdf7` |
| `starhorse-access` | `2.0.3` | `7a01d8773322cd90be85dcd4dfd66d76cdc93e58` |
| `tap-pyvo-adql-access` | `1.0.1` | `16605f835e35c0186e99f762daee5daedeff0df3` |

This is a new decision for changed directory trees, not an automatic carry-forward from
the earlier CRS seed. The changes preserve the curated workflows and add clearer,
consistent pip and uv isolated-environment guidance. CRS remains the canonical source
and continuing steward, and the repository now has repeatable checks that prevent the
documented pip and uv direct requirements from drifting apart.

## Evidence scope

- **Identity and provenance:** the registry revision and all nine directory trees were
  resolved from the merged CRS `main` commit. Names, descriptions, authorship, licenses,
  and CRS provenance remain unchanged.
- **Packaging and interoperability:** eight skills retain their existing pip baseline
  and add matching uv instructions; `large-tabular-visualization` adds both pip and uv
  setup instructions. Static contract tests enforce direct-pin parity. The skills
  disclose that uv can download a managed interpreter, show how to disable that behavior,
  and require a new workspace environment instead of replacing an existing one. The
  focused forward-execution evidence below applies only to the large-tabular uv path.
- **Security:** no credential handling, remote-service authorization, or research-data
  scope changed. An explicit redaction review of the changed trees found no embedded
  secrets, private data, prompts, transcripts, or personal information. Environment
  creation and package installation remain explicit network and filesystem actions. The
  new large-tabular smoke uses synthetic data in a private temporary directory,
  suppresses bytecode writes to the installed skill tree, reads back its output, and
  leaves no persistent smoke output.
- **Operability:** CRS pull request 6 passed the always-on repository CI with 141 tests
  passing and one unrelated opt-in scientific integration skipped. Static regression
  tests cover every simple pip setup, require a corresponding uv path, compare direct
  pins, and require the documented safety and reproducibility caveats.
- **Focused rendering evidence:** the large-tabular direct pins installed into a clean
  CPython 3.12.4 environment with uv 0.10.12; `uv pip check` passed for 50 packages. The
  bounded smoke combined two Dask Parquet partitions, reached Datashader through
  `rasterize=True`, recovered the exact synthetic count aggregate, and verified that an
  inline Bokeh document contained serialized raster data without an external script
  dependency.
- **Scientific validity:** the changes establish environment setup and software behavior
  only. They do not validate a research dataset, aggregation choice, visualization,
  catalog query, numerical result, or scientific conclusion.
- **Maintenance:** the nine patch-version skill updates were reviewed and merged in CRS
  before this metadata update. Future changes to any registered directory tree require
  another assessment.

## Limitations

- The simple environment recipes pin direct requirements but do not provide complete
  transitive locks, artifact hashes, a fixed package index, or a universal wheel-only
  policy. Pip and uv can resolve different transitive artifacts across time, platforms,
  configuration, and index state.
- The commands target POSIX-style environments. Python patch/vendor, uv version, operating
  system, architecture, trusted index/proxy configuration, and wheel availability remain
  client-controlled unless an individual skill states a narrower tested boundary.
- The focused large-tabular installation and rendering run was performed on macOS ARM64.
  The linked Ori report also records Linux x86_64 resolution evidence, but this decision
  does not claim complete cross-platform forward testing for all nine environments.
- Package installation can execute a build backend when a compatible wheel is not
  available. Clients must retain their normal source, index, network, and execution
  policy rather than treating `curated` as permission.
- Independent scientific reproduction is not claimed for any of the nine skills.

## References

- [CRS pull request 6](https://github.com/skill-commons/curated-research-skills/pull/6)
- [CRS issue 5 and Ori environment report](https://github.com/skill-commons/curated-research-skills/issues/5)
- [Merged CRS source](https://github.com/skill-commons/curated-research-skills/tree/74a11aaad374108c60162e879390ee3604efddd1)
- [CRS validation run](https://github.com/skill-commons/curated-research-skills/actions/runs/31513817484)
- [Previous CRS seed decision](2026-08-06-crs-seed.md)
- [Review-maturity policy](../../docs/adr/0003-review-maturity-and-evidence.md)
