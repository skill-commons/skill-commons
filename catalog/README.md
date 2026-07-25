# Skill catalog

This index is generated from the complete, reviewed directories under [`skills/`](../skills/).
The functional bundles are curated in [`bundles/index.yaml`](../bundles/index.yaml). Git and the package directories remain authoritative.

## General

Broad research utilities that are useful across disciplines.

| Skill | Version | Description |
|---|---:|---|
| [`aip/arxiv`](../skills/arxiv/) | `2.0.0` | Search, read, cite, and monitor academic papers through arXiv and related public metadata services, including reusable topic alerts and verified BibTeX generation. |
| [`aip/calculator`](../skills/calculator/) | `1.0.1` | Exact symbolic + numeric math with sympy/mpmath — derive formulas, evaluate constants, propagate errors, convert units. Use for ANY multi-step arithmetic or algebra instead of mental math. |

## LaTeX

Authoring, revising, compiling, and packaging scholarly LaTeX manuscripts.

| Skill | Version | Description |
|---|---:|---|
| [`aip/latex-research-paper`](../skills/latex-research-paper/) | `1.0.0` | Draft, revise, merge, and verify LaTeX research papers or white papers, including bibliography management, scientific figures, and controlled compilation cycles. |
| [`aip/latex-journal-submission-package`](../skills/latex-journal-submission-package/) | `2.0.0` | Adapt a stable LaTeX manuscript to a journal, fix portable build problems, verify the result, and assemble a clean submission archive; includes MNRAS guidance. |

## Astronomy

Astronomy catalog access, survey-specific workflows, and scientific visualization.

| Skill | Version | Description |
|---|---:|---|
| [`aip/tap-pyvo-adql-access`](../skills/tap-pyvo-adql-access/) | `1.0.0` | Use when querying astronomy TAP services with ADQL through pyvo or curl, including service probes, metadata discovery, TOP-based queries, VOTable/FITS conversion, pandas/Parquet caching, and robust network fallbacks. |
| [`aip/gaia-dr3-tap-query`](../skills/gaia-dr3-tap-query/) | `3.0.0` | Query Gaia DR3 at gaia.aip.de through TAP/PyVO, with schema discovery, representative sampling, local caching, and a Daiquiri REST fallback for exceptional async jobs. |
| [`aip/rave-dr6`](../skills/rave-dr6/) | `2.0.0` | Discover and query RAVE DR6 tables through its public TAP service, cache bounded results, and crossmatch RAVE sources with Gaia or StarHorse distance products. |
| [`aip/starhorse-access`](../skills/starhorse-access/) | `2.0.2` | Access StarHorse data products including SHboost-2024 and the SH21 EDR3 catalog via gaia.aip.de TAP. |
| [`aip/astro-catalog-plotting-cache`](../skills/astro-catalog-plotting-cache/) | `2.0.0` | Use when turning astronomy catalog data into reproducible cached products and publication-ready plots, especially CMDs, RA/Dec maps, Galactic projections, hexbin density plots, Datashader outputs, and provenance-backed figure deliverables. |

## Data

Reproducible access to large research datasets and object storage.

| Skill | Version | Description |
|---|---:|---|
| [`aip/data-aip-de-s3`](../skills/data-aip-de-s3/) | `2.0.0` | Access AIP and other S3-compatible research data with explicit authentication, column and row reduction, Dask-backed Parquet reads, and cache-first handling of large or non-columnar files. |

## Visualization

General-purpose publication and report graphics outside domain-specific workflows.

| Skill | Version | Description |
|---|---:|---|
| [`aip/seaborn-paper-plots`](../skills/seaborn-paper-plots/) | `1.0.1` | Create clean seaborn/matplotlib plots suitable for papers, notes, and reproducible reports. |

## Consolidated skills

These former package coordinates are preserved as redirects in the catalog and in Git history; they are no longer independent skills.

| Former skill | Use instead | Reason |
|---|---|---|
| `aip/cold-streams-monitoring` | `aip/arxiv` | A topic-specific arXiv query and scheduler wrapper is now covered by generic monitoring. |
| `aip/iterative-paper-improvement` | `aip/latex-research-paper` | Its revision rounds duplicate the canonical manuscript authoring and revision workflow. |
| `aip/latex-paper-iteration` | `aip/latex-research-paper` | Drafting, revision, merging, figures, and compile loops now live in one authoring skill. |
| `aip/multi-section-latex-whitepaper` | `aip/latex-research-paper` | Multi-source synthesis is a mode of the canonical manuscript workflow. |
| `aip/mnras-latex-compile-portability-fixes` | `aip/latex-journal-submission-package` | MNRAS portability fixes are journal-specific packaging guidance, not a separate task. |
| `aip/mnras-latex-portable` | `aip/latex-journal-submission-package` | MNRAS build and package guidance is consolidated into the journal submission skill. |
| `aip/mnras-latex-portable-build-and-package` | `aip/latex-journal-submission-package` | This package duplicated the canonical journal build and submission workflow. |
| `aip/cmd-plotting` | `aip/astro-catalog-plotting-cache` | A CMD is one plot type already covered by the broader astronomy plotting skill. |
| `aip/datashader-019-pipeline` | `aip/astro-catalog-plotting-cache` | Datashader is an implementation path within the broader large-catalog plotting workflow. |
| `aip/gaia-dr3-daiquiri-rest` | `aip/gaia-dr3-tap-query` | Daiquiri REST is retained as a fallback mode of the canonical Gaia access skill. |
| `aip/gaia-dr3-plot-with-dust` | `aip/astro-catalog-plotting-cache` | One Gaia sample and dust-overlay figure is too narrow to be an independent skill. |
| `aip/rave-dr6-nearest-100-plot` | `aip/rave-dr6` | A fixed nearest-100 query is an example, not a distinct RAVE capability. |
| `aip/rave-dr6-public-talk-visualizations` | `aip/astro-catalog-plotting-cache` | Presentation styling is a plotting choice independent of the RAVE data source. |
| `aip/rave-dr6-recent-observations-plot` | `aip/rave-dr6` | A fixed newest-100 query and plot is covered by general RAVE querying and plotting. |
| `aip/rave-dr6-shboost-distance-query` | `aip/rave-dr6` | The reusable RAVE-StarHorse crossmatch is now a reference inside the canonical RAVE skill. |
| `aip/rave-dr6-starhorse-access` | `aip/rave-dr6` | This was a second version of the same RAVE-StarHorse crossmatch workflow. |
| `aip/hdf5-on-s3-cached` | `aip/data-aip-de-s3` | Cache-first HDF5 handling is one format path within general object-store access. |
| `aip/s3-parquet-sampling` | `aip/data-aip-de-s3` | Parquet projection, reduction, and caching are core object-store access operations. |
| `aip/s3-parquet-sampling-plot-cached` | `aip/data-aip-de-s3` | Its S3 access is covered here; astronomy plotting belongs to the plotting skill. |

Machine-readable metadata: [`index.json`](index.json).
