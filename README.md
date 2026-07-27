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

Literature discovery, monitoring, and scientific calculation.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`arxiv`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/arxiv) | `2.0.0` | Search, read, cite, and monitor papers through arXiv. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/arxiv) | `hermes skills install skill-commons/curated-research-skills/skills/arxiv` |
| [`calculator`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/calculator) | `1.0.1` | Perform exact symbolic and numerical calculations. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/calculator) | `hermes skills install skill-commons/curated-research-skills/skills/calculator` |

### LaTeX

Research-manuscript authoring, revision, compilation, and submission packaging.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`latex-journal-submission-package`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/latex-journal-submission-package) | `2.0.0` | Build and verify portable LaTeX journal submissions. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/latex-journal-submission-package) | `hermes skills install skill-commons/curated-research-skills/skills/latex-journal-submission-package` |
| [`latex-research-paper`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/latex-research-paper) | `1.0.0` | Draft, revise, and verify LaTeX research manuscripts. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/latex-research-paper) | `hermes skills install skill-commons/curated-research-skills/skills/latex-research-paper` |

### Astronomy

Astronomy catalog access, survey-specific workflows, and scientific visualization.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`astro-catalog-plotting-cache`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/astro-catalog-plotting-cache) | `2.0.0` | Create cached, publication-ready astronomy catalog plots. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/astro-catalog-plotting-cache) | `hermes skills install skill-commons/curated-research-skills/skills/astro-catalog-plotting-cache` |
| [`gaia-dr3-tap-query`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/gaia-dr3-tap-query) | `3.0.0` | Query Gaia DR3 through AIP TAP and Daiquiri services. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/gaia-dr3-tap-query) | `hermes skills install skill-commons/curated-research-skills/skills/gaia-dr3-tap-query` |
| [`rave-dr6`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/rave-dr6) | `2.0.0` | Query, cache, and crossmatch public RAVE DR6 data. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/rave-dr6) | `hermes skills install skill-commons/curated-research-skills/skills/rave-dr6` |
| [`starhorse-access`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/starhorse-access) | `2.0.2` | Access StarHorse SHboost and SH21 catalog products. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/starhorse-access) | `hermes skills install skill-commons/curated-research-skills/skills/starhorse-access` |
| [`tap-pyvo-adql-access`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/tap-pyvo-adql-access) | `1.0.0` | Query astronomy TAP services with PyVO and ADQL. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/tap-pyvo-adql-access) | `hermes skills install skill-commons/curated-research-skills/skills/tap-pyvo-adql-access` |

### Data

Reproducible access to large research datasets and object storage.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`data-aip-de-s3`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/data-aip-de-s3) | `2.0.0` | Access and cache research data from S3-compatible stores. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/data-aip-de-s3) | `hermes skills install skill-commons/curated-research-skills/skills/data-aip-de-s3` |

### Visualization

General-purpose publication and report graphics.

| Skill | Version | Description | Source | Install |
|---|---:|---|---|---|
| [`seaborn-paper-plots`](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/seaborn-paper-plots) | `1.0.1` | Create reproducible publication plots with Seaborn. | [pinned source](https://github.com/skill-commons/curated-research-skills/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/seaborn-paper-plots) | `hermes skills install skill-commons/curated-research-skills/skills/seaborn-paper-plots` |

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

</details>

## How the registry works

- [`registry/index.yaml`](registry/index.yaml) records each canonical repository, path, tracked branch, last reviewed commit, and Git tree.
- [`categories/index.yaml`](categories/index.yaml) supplies the human taxonomy. Categories are not Hermes installation units.
- [`catalog/index.json`](catalog/index.json) is the generated machine view.
- `skill-commons check-upstreams` compares the recorded directory trees with the tracked branches and reports upstream changes without copying them.

The YAML files above are implementation data for this catalog, not a new skill-package standard. Source repositories use the formats understood by their clients; the Commons-maintained tap follows current Hermes conventions.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) to register or update a source and [`docs/FEDERATED_REGISTRY.md`](docs/FEDERATED_REGISTRY.md) for the architecture.
