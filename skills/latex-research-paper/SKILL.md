---
name: latex-research-paper
description: Draft, revise, merge, and verify LaTeX research papers or white papers, including bibliography management, scientific figures, and controlled compilation cycles.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# LaTeX Research Paper

## When to Use

Use this skill for the complete authoring lifecycle of a scholarly LaTeX document:

- draft a paper or technical white paper from verified source material;
- revise an existing manuscript for structure, clarity, or consistency;
- merge several papers or Markdown sections into one coherent document;
- add figures, tables, citations, and cross-references;
- compile and inspect a reviewable PDF.

Use `latex-journal-submission-package` after the manuscript is scientifically stable
and needs journal adaptation, portability fixes, or a submission archive.

## Non-Negotiable Research Rules

- Never invent authors, affiliations, citations, datasets, numerical results, or
  scientific conclusions.
- Use verified bibliographic metadata or an explicit `% TODO: verify citation`
  placeholder.
- Distinguish source claims from interpretation and label synthetic examples.
- Preserve recoverability with version control or a reviewed backup before a major
  rewrite.

## Choose the Authoring Mode

### New manuscript

Create a project under a user-approved workspace path:

```text
<article-slug>/
├── main.tex
├── references.bib
└── figures/
```

Derive the slug from the title using lowercase ASCII letters, numbers, and hyphens.
Draft only the sections supported by the available material. A conventional research
paper may include title, abstract, introduction, related work, methods, results,
discussion, conclusion, and references, but journal and disciplinary conventions take
precedence.

### Revision

1. Read the complete manuscript and bibliography.
2. Audit scientific support, structure, terminology, citations, figures, and build
   warnings.
3. Group edits into meaningful passes rather than treating an arbitrary iteration count
   as a reason for repeated cosmetic rewrites.
4. Use targeted edits for local changes. For a structural overhaul, rewrite the complete
   file in one controlled update.
5. Compile, inspect, and repeat only where the output reveals a real issue.

Useful passes include:

- scientific support and missing evidence;
- document structure and argument flow;
- terminology, notation, and prose consistency;
- citations and bibliography;
- figures, tables, captions, and cross-references;
- compilation and final proofing.

### Multi-source synthesis

1. Read every relevant source completely.
2. Map unique content, overlap, disagreements, and provenance.
3. Design one outline around the target argument rather than concatenating sections.
4. Deduplicate definitions, claims, citations, and figures.
5. Write transitions that make the merged document coherent.
6. Preserve source attribution and flag unresolved conflicts.

Use a monolithic `main.tex` by default. Split into `sections/*.tex` only for a long
document or genuine parallel authorship, and ensure every section is included with
`\input{}` or `\include{}`.

## Minimal Portable Preamble

Start with only the packages the document uses:

```latex
\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{microtype}
\usepackage{hyperref}
```

Pick one bibliography system. For traditional BibTeX:

```latex
\bibliographystyle{plainnat}
\bibliography{references}
```

Do not mix this with `biblatex` commands in the same build.

## Figures and Tables

- Generate data-backed figures from a standalone script where practical.
- Use a non-interactive backend such as `matplotlib.use("Agg")`.
- Prefer a white background, readable labels, explicit units, and at least 200 DPI for
  raster review outputs.
- Give every figure and table a caption and label, then reference it from the text.
- Keep generation scripts next to the figures so the result can be reproduced.
- Do not create a visual merely to satisfy a requested iteration count.

## Compilation

Inspect the available tools, then use `latexmk` when present:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Traditional BibTeX fallback:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Clean stale auxiliary files when they cause phantom references, but do not delete source
or user-authored outputs. Read the log and distinguish fatal errors from cosmetic
overfull/underfull-box warnings.

## Common Pitfalls

- Reconstructing a manuscript from a partial read.
- Leaving stale `sections/` files after moving to a monolithic document.
- Duplicating packages or loading incompatible bibliography systems.
- Treating placeholders as evidence.
- Referencing figure files that do not exist.
- Applying many fragile substitutions when a controlled rewrite is safer.
- Compiling only once and reporting unresolved citations as finished.

## Verification

- [ ] Every scientific claim, result, and citation is supported or clearly marked.
- [ ] The manuscript structure matches the requested document type.
- [ ] Bibliography commands and entries use one consistent system.
- [ ] Figures and tables exist, have labels/captions, and are referenced.
- [ ] The build completes without fatal errors.
- [ ] Citations and cross-references stabilize after the required passes.
- [ ] The PDF opens and key pages have been visually inspected.
