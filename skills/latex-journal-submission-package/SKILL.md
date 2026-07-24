---
name: latex-journal-submission-package
description: Convert a working LaTeX manuscript into a journal-style submission package with separate
  BibTeX, build helper, manifest, and zip archive; useful when TeX is unavailable locally.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# LaTeX Journal Submission Package

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.


Use this when a user has a working LaTeX manuscript and wants a cleaner, submission-style package (for example MNRAS), especially if the environment cannot compile TeX yet.

## When to use
- The manuscript exists as a single `.tex` file with inline bibliography.
- The user wants a journal-adapted version or a submission-ready directory layout.
- The machine may not have `pdflatex`, `latexmk`, or the journal class installed.
- You still want to deliver a useful package: `main.tex`, `references.bib`, `compile.sh`, README, notes, zip.

## Goal
Produce:
- a journal-formatted manuscript source (or adapted variant)
- separate `references.bib`
- helper build script
- README with compile instructions
- notes/manifest for provenance
- zip archive for transfer

## Workflow

### 1) Inspect the live environment first
Always verify, do not assume:
- OS and architecture
- presence of `pdflatex`, `latexmk`, `kpsewhich`, `tectonic`
- package manager availability

Example checks:
```bash
. /etc/os-release && echo "$PRETTY_NAME"
uname -sr
uname -m
command -v apt
command -v pdflatex
command -v latexmk
command -v kpsewhich
command -v tectonic
```

If TeX tools are missing, say so explicitly and continue packaging anyway.

### 2) If targeting MNRAS, adapt the preamble and front matter
A journal's requirements can change. Check the current author instructions before
finalizing class options, front matter, and package contents.

A practical starting point:
```latex
\documentclass[fleqn,usenatbib,useAMS]{mnras}
```
Typical useful packages:
```latex
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
```
Add publisher-requested font packages only after confirming they are installed.
Avoid `longtable` in the normal MNRAS two-column layout; prefer `table` or `table*`.
Add MNRAS-style title, author, date, `\pubyear`, `\label{firstpage}`, `\pagerange`, `\maketitle`, abstract, and `keywords` environment.

### 3) Convert inline bibliography into BibTeX
If the source uses `thebibliography`, extract each `\bibitem{key}` into BibTeX.

Recommended approach:
- Parse the inline bibliography programmatically.
- For arXiv entries, query the arXiv API by ID to recover accurate author lists, title, year, and primary category.
- Replace the inline bibliography in `main.tex` with:
```latex
\bibliographystyle{mnras}
\bibliography{references}
```

### 4) Important arXiv metadata pitfall
The arXiv API returns IDs like `2603.26953v1`, not bare `2603.26953`.
When matching IDs, strip the version suffix with a regex like:
```python
re.sub(r'v\d+$', '', arxiv_id)
```
If bulk metadata lookup behaves inconsistently, fall back to one-ID-per-request. This worked reliably.

### 5) Build the submission directory layout
Recommended layout:
```text
submission_package/
  main.tex
  references.bib
  compile.sh
  README.txt
  figures/
    README.txt
  notes/
    package_notes.txt
    manifest.json
```

### 6) Include a compile helper
Use:
```bash
#!/usr/bin/env bash
set -euo pipefail
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf main.tex
else
  pdflatex main.tex
  bibtex main
  pdflatex main.tex
  pdflatex main.tex
fi
```
Make it executable.

### 7) Include explicit README guidance
Document:
- what files are included
- that the package was structurally prepared even if TeX is missing
- what must be updated before submission (authors, affiliations, acknowledgements, figures)
- how to compile locally

### 8) Zip the package
After generating all files, create a zip archive for easy delivery.

## Ubuntu package requirements for actual compilation
If the user asks what is needed to compile MNRAS on Ubuntu, check live first, then recommend:
```bash
sudo apt update && sudo apt install -y \
  latexmk \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-publishers
```
Run installation only after the user approves system changes.
Why:
- `pdflatex` comes from TeX Live base stack
- `latexmk` is the easiest build driver
- `mnras.cls` is typically in `texlive-publishers`

Nice-to-have but optional:
```bash
biber texlive-science
```

## Verification checklist
Before finishing:
- check brace balance and key environment balance in the generated `.tex`
- verify `main.tex` references `references.bib`
- inspect the first part of `references.bib`
- search for bad placeholders like `Unknown`
- confirm zip archive exists

## What to tell the user
If TeX is missing, clearly state:
- the package is ready structurally
- PDF generation is blocked only by missing TeX tooling
- exact Ubuntu packages required to compile

## Reusable lessons learned
- Packaging is still useful even without compilation.
- Separating bibliography and adding a build helper significantly improves handoff quality.
- arXiv metadata recovery is worth doing because naive BibTeX extraction often leaves poor author/title fields.
- For journal adaptation requests, deliver both the adapted `.tex` and a full package directory/zip, not just one file.
