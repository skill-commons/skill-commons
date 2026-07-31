# Skill Commons

Skill Commons is a federated discovery catalog for research skills. It records where each skill is maintained; it does not copy third-party skill content into this repository.

The canonical skill bytes, references, scripts, history, and updates remain in their source repositories. The first Commons-maintained source is the [`curated-research-skills`](https://github.com/skill-commons/curated-research-skills) Hermes tap.

## Use with Hermes

Subscribe to the Commons-maintained tap:

```bash
hermes skills tap add skill-commons/curated-research-skills
hermes skills search astronomy
```

Every table below also gives the explicit direct-install command. Hermes installs from the source repository's current default branch and records its resolved source and content hash locally.

## Skills

### General

Literature discovery, evidence synthesis, monitoring, and scientific calculation.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`arxiv`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/arxiv) | `2.0.0` | Search, read, cite, and monitor papers through arXiv. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/arxiv) | `hermes skills install skill-commons/curated-research-skills/skills/arxiv` |
| [`calculator`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/calculator) | `1.0.1` | Perform exact symbolic and numerical calculations. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/calculator) | `hermes skills install skill-commons/curated-research-skills/skills/calculator` |
| [`research-paper-evidence-workflow`](https://github.com/skill-commons/curated-research-skills/tree/8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e/skills/research-paper-evidence-workflow) | `1.0.0` | Map research-paper claims to supplied evidence, synthesize completed results, construct an evidence-backed outline, and audit a draft for traceability, numeric fidelity, scope, and overclaiming. Use when notes, tables, figures, result files, or a manuscript need a claim-evidence matrix, results narrative, outline, or evidence-focused review. Do not use to design or run experiments, retrieve citations, format or compile LaTeX, manage projects, submit or promote papers, or perform external writes. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e/skills/research-paper-evidence-workflow) | `hermes skills install skill-commons/curated-research-skills/skills/research-paper-evidence-workflow` |
| [`rss-feed-monitor`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/rss-feed-monitor) | `2.0.0` | Track public RSS or Atom feeds in an isolated local database, scan for new articles, and manage read state with explicit mutation safeguards. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/rss-feed-monitor) | `hermes skills install skill-commons/curated-research-skills/skills/rss-feed-monitor` |

### LaTeX

Research-manuscript authoring, revision, compilation, and submission packaging.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`latex-journal-submission-package`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/latex-journal-submission-package) | `2.0.0` | Build and verify portable LaTeX journal submissions. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/latex-journal-submission-package) | `hermes skills install skill-commons/curated-research-skills/skills/latex-journal-submission-package` |
| [`latex-research-paper`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/latex-research-paper) | `1.0.0` | Draft, revise, and verify LaTeX research manuscripts. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/latex-research-paper) | `hermes skills install skill-commons/curated-research-skills/skills/latex-research-paper` |

### Astronomy

Astronomy catalog access, survey-specific workflows, and scientific visualization.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`astro-catalog-plotting-cache`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/astro-catalog-plotting-cache) | `2.0.0` | Create cached, publication-ready astronomy catalog plots. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/astro-catalog-plotting-cache) | `hermes skills install skill-commons/curated-research-skills/skills/astro-catalog-plotting-cache` |
| [`gaia-dr3-tap-query`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/gaia-dr3-tap-query) | `3.0.0` | Query Gaia DR3 through AIP TAP and Daiquiri services. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/gaia-dr3-tap-query) | `hermes skills install skill-commons/curated-research-skills/skills/gaia-dr3-tap-query` |
| [`rave-dr6`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/rave-dr6) | `2.0.0` | Query, cache, and crossmatch public RAVE DR6 data. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/rave-dr6) | `hermes skills install skill-commons/curated-research-skills/skills/rave-dr6` |
| [`starhorse-access`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/starhorse-access) | `2.0.2` | Access StarHorse SHboost and SH21 catalog products. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/starhorse-access) | `hermes skills install skill-commons/curated-research-skills/skills/starhorse-access` |
| [`tap-pyvo-adql-access`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/tap-pyvo-adql-access) | `1.0.0` | Query astronomy TAP services with PyVO and ADQL. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/tap-pyvo-adql-access) | `hermes skills install skill-commons/curated-research-skills/skills/tap-pyvo-adql-access` |

### Data

Reproducible access to large research datasets and object storage.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`data-aip-de-s3`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/data-aip-de-s3) | `2.0.0` | Access and cache research data from S3-compatible stores. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/data-aip-de-s3) | `hermes skills install skill-commons/curated-research-skills/skills/data-aip-de-s3` |
| [`drphub-products`](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/drphub-products) | `1.0.0` | Inspect Digital Research Product Hub health, API capabilities, product summaries, maturity, and lineage through a bounded read-only REST client. Use when a user needs to diagnose a DRP Hub endpoint, search or inspect products, verify immutable Git and image identities, or review maturity and clone relationships without creating, changing, publishing, sharing, reviewing, or deleting remote data. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/drphub-products) | `hermes skills install skill-commons/curated-research-skills/skills/drphub-products` |

### Visualization

General-purpose publication and report graphics.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`large-tabular-visualization`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/large-tabular-visualization) | `2.0.0` | Build interpretable interactive or static visualizations from tabular data that is too dense or too large for ordinary point plotting. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/large-tabular-visualization) | `hermes skills install skill-commons/curated-research-skills/skills/large-tabular-visualization` |
| [`seaborn-paper-plots`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/seaborn-paper-plots) | `1.0.1` | Create reproducible publication plots with Seaborn. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/seaborn-paper-plots) | `hermes skills install skill-commons/curated-research-skills/skills/seaborn-paper-plots` |

### Scientific Computing

Simulation, validation, and reproducible scientific software workflows.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`dt4acc-host-smoke-test`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/dt4acc-host-smoke-test) | `2.0.0` | Run a bounded, simulation-only host smoke test for local dt4acc, dt4acc-lib, and lat2db checkouts without facility services or containers. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/dt4acc-host-smoke-test) | `hermes skills install skill-commons/curated-research-skills/skills/dt4acc-host-smoke-test` |
| [`dt4acc-operations`](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/dt4acc-operations) | `1.0.0` | Preflight, plan, start, inspect, and stop a local dt4acc simulation packaged as an already-built, digest-pinned Apptainer SIF. Use when an operator needs a bounded simulation IOC lifecycle with exact source/build provenance, a clean child environment, no host or facility network, content-bound start/stop confirmation, and exact owned-process cleanup. This first CRS version never builds or pulls images, connects to facility services, accesses live PVs, imports MongoDB data, or performs PV writes. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/dt4acc-operations) | `hermes skills install skill-commons/curated-research-skills/skills/dt4acc-operations` |
| [`jubik-bootstrap`](https://github.com/skill-commons/curated-research-skills/tree/4f63c019b3d05fe72501c706fbe69d105f9fb643/skills/jubik-bootstrap) | `1.0.0` | Preflight, plan, create, and diagnose a pinned J-UBIK core environment with an isolated lock-backed, wheel-only workflow and a genuine synthetic SkyModel smoke test. Use when a researcher is blocked on J-UBIK installation, JAX/NIFTy compatibility, environment configuration, artifact provenance, or core readiness. This skill proves only the CPU core; it never claims JWST, Chandra, or eROSITA adapter readiness, downloads calibration or observation data, invokes instrument software, or runs research inference. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/4f63c019b3d05fe72501c706fbe69d105f9fb643/skills/jubik-bootstrap) | `hermes skills install skill-commons/curated-research-skills/skills/jubik-bootstrap` |
| [`nifty-re-variational-inference`](https://github.com/skill-commons/curated-research-skills/tree/4f63c019b3d05fe72501c706fbe69d105f9fb643/skills/nifty-re-variational-inference) | `1.0.0` | Build, run, and validate bounded Bayesian variational-inference workflows with the JAX-based NIFTy.re API. Use when a researcher needs to formulate priors, a response and likelihood, prove a NIFTy.re installation against an analytic posterior, run a small CPU pilot, inspect optimizer and sampling evidence, or prepare a reproducible inference handoff. Do not use this skill to bootstrap J-UBIK, configure telescope instruments, certify an arbitrary scientific model from one successful run, or launch unbounded production inference. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/4f63c019b3d05fe72501c706fbe69d105f9fb643/skills/nifty-re-variational-inference) | `hermes skills install skill-commons/curated-research-skills/skills/nifty-re-variational-inference` |
| [`reana-operator`](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/reana-operator) | `1.0.0` | Inspect an authenticated REANA service through a fixed read-only command allowlist, including connectivity, cluster information, workflow inventory, status, redacted logs, workspace files, and disk usage. Use when a user wants to diagnose or review remote REANA state after a local workflow has been authored. This first CRS version never uploads, creates, starts, stops, deletes, downloads, shares, or otherwise mutates a workflow. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/d5f096ee426dbbbea885bfb5199e8b7070960a1a/skills/reana-operator) | `hermes skills install skill-commons/curated-research-skills/skills/reana-operator` |
| [`reana-workflow-authoring`](https://github.com/skill-commons/curated-research-skills/tree/8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e/skills/reana-workflow-authoring) | `1.0.0` | Scaffold, edit, and conservatively validate provider-neutral local REANA Serial workflow projects, including reana.yaml structure, declared inputs and outputs, runtime-image reproducibility, path containment, symlinks, and accidental secrets. Use when a user asks to create or review a local REANA workflow definition before operational handoff. This skill never authenticates, contacts a REANA server or registry, uploads, submits, starts, monitors, downloads, or mutates a remote workflow. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e/skills/reana-workflow-authoring) | `hermes skills install skill-commons/curated-research-skills/skills/reana-workflow-authoring` |

### Software Development

Documentation-grounded software development and library workflows.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`python-library-docs-first`](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/python-library-docs-first) | `2.0.0` | Verify version-sensitive third-party Python APIs against authoritative documentation before writing, reviewing, fixing, or explaining code. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/python-library-docs-first) | `hermes skills install skill-commons/curated-research-skills/skills/python-library-docs-first` |

<details>
<summary>Consolidated former skill names</summary>

| Former skill | Use instead | Reason |
|---|---|---|
| `cold-streams-monitoring` | `arxiv` | A topic-specific arXiv query and scheduler wrapper is covered by generic monitoring. |
| `iterative-paper-improvement` | `latex-research-paper` | Its revision rounds duplicate the canonical manuscript workflow. |
| `latex-paper-iteration` | `latex-research-paper` | Drafting, revision, merging, figures, and compile loops belong in one authoring skill. |
| `multi-section-latex-whitepaper` | `latex-research-paper` | Multi-source synthesis is a mode of the canonical manuscript workflow. |
| `mnras-latex-compile-portability-fixes` | `latex-journal-submission-package` | MNRAS portability fixes are packaging guidance, not a separate task. |
| `mnras-latex-portable` | `latex-journal-submission-package` | MNRAS build guidance is consolidated into the journal submission skill. |
| `mnras-latex-portable-build-and-package` | `latex-journal-submission-package` | This duplicated the canonical journal build and submission workflow. |
| `cmd-plotting` | `astro-catalog-plotting-cache` | A color-magnitude diagram is one plot type in the broader astronomy plotting skill. |
| `datashader-019-pipeline` | `astro-catalog-plotting-cache` | Datashader is one implementation path in the broader catalog plotting workflow. |
| `gaia-dr3-daiquiri-rest` | `gaia-dr3-tap-query` | Daiquiri REST is retained as a fallback in the canonical Gaia access skill. |
| `gaia-dr3-plot-with-dust` | `astro-catalog-plotting-cache` | One Gaia sample and dust-overlay figure is too narrow to be an independent skill. |
| `rave-dr6-nearest-100-plot` | `rave-dr6` | A fixed nearest-100 query is an example, not a distinct RAVE capability. |
| `rave-dr6-public-talk-visualizations` | `astro-catalog-plotting-cache` | Presentation styling is a plotting choice independent of the RAVE data source. |
| `rave-dr6-recent-observations-plot` | `rave-dr6` | A fixed newest-100 query and plot is covered by general RAVE querying and plotting. |
| `rave-dr6-shboost-distance-query` | `rave-dr6` | The reusable RAVE-StarHorse crossmatch is part of the canonical RAVE skill. |
| `rave-dr6-starhorse-access` | `rave-dr6` | This was a second version of the same RAVE-StarHorse crossmatch workflow. |
| `hdf5-on-s3-cached` | `data-aip-de-s3` | Cache-first HDF5 handling is one path within general object-store access. |
| `s3-parquet-sampling` | `data-aip-de-s3` | Parquet projection, reduction, and caching are core object-store operations. |
| `s3-parquet-sampling-plot-cached` | `data-aip-de-s3` | S3 access belongs here; astronomy plotting belongs in the plotting skill. |
| `dask-hvplot-datashader-scientific-plots` | `large-tabular-visualization` | The implementation-specific plotting workflow is now maintained as a general large-table visualization skill. |
| `blogwatcher` | `rss-feed-monitor` | RSS and Atom monitoring is maintained under a tool-independent task name. |
| `dtwin-host-smoke-test` | `dt4acc-host-smoke-test` | The canonical name identifies the dt4acc stack and its simulation-only scope. |
| `python-mcp-docs-first` | `python-library-docs-first` | Python documentation research no longer requires a specific MCP provider. |
| `dask-mcp-docs-first` | `python-library-docs-first` | Dask documentation research is one use of the provider-neutral Python workflow. |
| `pandas-datashader-mcp-docs-first` | `python-library-docs-first` | pandas and Datashader documentation research is one use of the provider-neutral Python workflow. |
| `research-paper-writing` | `research-paper-evidence-workflow` | Evidence mapping, completed-result synthesis, outlining, and claim review are maintained as a focused read-only workflow; operational project management and submission actions remain excluded. |
| `reana-aip` | `reana-workflow-authoring` | Reusable local REANA authoring guidance is maintained without AIP-only endpoints, credentials, or remote operations. |
| `reana-cmd-plot-workflow-external-script` | `reana-workflow-authoring` | An external-script plotting workflow is an example covered by the general Serial authoring workflow. |
| `reana-dev-workflow-setup` | `reana-workflow-authoring` | Local workflow setup and validation belong in the canonical REANA authoring skill. |
| `reana-run-script-with-workspace` | `reana-workflow-authoring` | Running a script against declared workspace inputs is a Serial authoring pattern, not a separate skill. |
| `reana-serial-python` | `reana-workflow-authoring` | A Python Serial workflow is covered by the provider-neutral canonical authoring workflow. |
| `reana-serial-python-analysis-template` | `reana-workflow-authoring` | The analysis template is consolidated into the general local scaffolding workflow. |
| `reana-workflow-best-practices` | `reana-workflow-authoring` | REANA authoring best practices are maintained directly in the canonical workflow. |

</details>

## How the registry works

- [`registry/index.yaml`](registry/index.yaml) records each canonical repository, path, tracked branch, last reviewed commit, and Git tree.
- [`categories/index.yaml`](categories/index.yaml) supplies the human taxonomy. Categories are not Hermes installation units.
- [`catalog/index.json`](catalog/index.json) is the generated machine view.
- `skill-commons check-upstreams` compares the recorded directory trees with the tracked branches and reports upstream changes without copying them.

The YAML files above are implementation data for this catalog, not a new skill-package standard. Source repositories use the formats understood by their clients; the Commons-maintained tap follows current Hermes conventions.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) to register or update a source and [`docs/FEDERATED_REGISTRY.md`](docs/FEDERATED_REGISTRY.md) for the architecture.
