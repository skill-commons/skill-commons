---
name: mnras-latex-portable-build-and-package
description: Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package
  failures and fixing common two-column table issues.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Portable MNRAS LaTeX build and packaging

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.


Use this when a user wants an MNRAS-style paper prepared, compiled, or packaged on a Linux/Ubuntu machine, especially when the environment may have only a minimal TeX installation.

## When to use
- Converting a generic LaTeX article into MNRAS format
- Preparing a submission-style package (`main.tex`, `.bib`, helper script)
- Fixing compilation failures on Ubuntu due to missing TeX packages
- Debugging MNRAS-specific layout issues in two-column mode

## Key lessons learned

### 1. Avoid `newtxtext,newtxmath` for portability unless you know they are installed
A common failure on Ubuntu/minimal TeX installs is:
- `! LaTeX Error: File 'newtxtext.sty' not found.`

For portability, prefer removing:
```latex
\usepackage{ae,aecompl}
\usepackage{newtxtext,newtxmath}
```
and keep a simpler preamble such as:
```latex
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
```

This may produce font-substitution warnings, but it compiles much more reliably.

### 2. `longtable` is not valid in MNRAS two-column mode
A typical hard error is:
- `Package longtable Error: longtable not in 1-column mode.`

If the manuscript is in standard MNRAS two-column layout, replace `longtable` with a floating table, usually:
```latex
\begin{table*}
\centering
\caption{...}
\label{tab:...}
\small
\begin{tabularx}{\textwidth}{...}
...
\end{tabularx}
\end{table*}
```

This is the correct fix for wide summary tables in MNRAS.

### 3. Prepare a clean package layout
For submission-style packaging, structure the directory as:
```text
mnras_submission_package/
  main.tex
  references.bib
  compile.sh
  README.txt
  figures/
    README.txt
  notes/
    manifest.json
    package_notes.txt
```

Use:
- `main.tex` for the manuscript
- `references.bib` instead of inline `thebibliography` where possible
- `compile.sh` with `latexmk -pdf main.tex` fallback to manual pdflatex/bibtex sequence

### 4. Replace inline bibliography with BibTeX
If starting from a document using `thebibliography`, convert it to:
```latex
\bibliographystyle{mnras}
\bibliography{references}
```
Then place entries in `references.bib`.

For arXiv-heavy drafts, retrieve metadata from arXiv or another authoritative source.
Do not guess authors, identifiers, dates, or titles. A verified entry can use this shape:
```bibtex
@misc{verified_key,
  author = {...},
  title = {...},
  year = {...},
  eprint = {...},
  archivePrefix = {arXiv},
  primaryClass = {...},
  url = {https://arxiv.org/abs/...}
}
```

### 5. Recommended Ubuntu packages
If asked what is required to compile on Ubuntu, recommend:
```bash
sudo apt update && sudo apt install -y latexmk texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-publishers biber texlive-science
```

Run installation only after the user approves system changes. This package set was
reported sufficient on Ubuntu 24.04; re-check it against the current environment.

### 6. Build command
Preferred:
```bash
cd /path/to/mnras_submission_package && latexmk -pdf main.tex
```
Fallback:
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## Practical workflow
1. Convert manuscript to MNRAS class:
   ```latex
   \documentclass[fleqn,usenatbib,useAMS]{mnras}
   ```
2. Use a portable preamble without `newtxtext,newtxmath` unless known installed.
3. Replace `longtable` with `table*` + `tabularx` in two-column MNRAS.
4. Convert inline bibliography to BibTeX.
5. Build with `latexmk -pdf main.tex`.
6. If compilation fails, inspect for:
   - missing style files
   - `longtable` errors in two-column mode
   - unresolved bibliography due to missing `.bbl`
7. Re-run `latexmk` until citations and references stabilize.

## Expected remaining warnings
Warnings that may remain but are usually non-fatal:
- font size substitutions
- underfull/overfull boxes
- duplicate destination warnings for tables

These do not necessarily block PDF generation.

## Deliverables
When done, provide:
- path to `main.tex`
- path to `references.bib`
- path to the generated `main.pdf`
- optional zip package path
