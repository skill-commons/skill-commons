---
name: mnras-latex-compile-portability-fixes
description: Fix common MNRAS LaTeX portability issues on Ubuntu/Debian TeX Live installs, compile successfully,
  and package submission artifacts.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# MNRAS LaTeX compile portability fixes

## When to Use
Fix common MNRAS LaTeX portability issues on Ubuntu/Debian TeX Live installs, compile successfully, and package submission artifacts.

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.


Use this when an MNRAS manuscript fails to compile on a typical Ubuntu/Debian TeX Live environment, especially after adapting a generic article into MNRAS.

## When this skill applies
- The user has an `.tex` manuscript intended for MNRAS.
- The document compiles poorly or fails due to missing font packages.
- The paper was converted from a generic article class into `mnras`.
- The user wants a submission-style package (`main.tex`, `references.bib`, helper files) and a compiled PDF.

## Key lessons learned

### 1. Avoid `newtxtext,newtxmath` for portability unless you know the environment has them
A common failure on Ubuntu/Debian is:
- `! LaTeX Error: File 'newtxtext.sty' not found.`

If the goal is successful compilation rather than exact Times-like typography, remove:
```latex
\usepackage{ae,aecompl}
\usepackage{newtxtext,newtxmath}
```
Keep a simpler preamble such as:
```latex
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath}
```
This trades typographic fidelity for portability and is often the right short-term fix.

### 2. `longtable` is not safe inside normal MNRAS two-column mode
If compilation fails with:
- `Package longtable Error: longtable not in 1-column mode.`

Replace `longtable` with a regular table layout suitable for MNRAS, usually:
```latex
\begin{table*}
\centering
\caption{...}
\label{...}
\small
\begin{tabularx}{\textwidth}{...}
...
\end{tabularx}
\end{table*}
```
For wide summary tables in two-column papers, `table*` + `tabularx` is a safer default than `longtable`.

### 3. Separate inline bibliography into a BibTeX file for cleaner packaging
If the working draft contains:
```latex
\begin{thebibliography}{99}
...
\end{thebibliography}
```
convert it into:
```latex
\bibliographystyle{mnras}
\bibliography{references}
```
and create `references.bib`.

This makes the paper easier to compile, easier to maintain, and closer to a real submission package.

### 4. After BibTeX conversion, expect multiple latexmk passes
Use:
```bash
latexmk -pdf -interaction=nonstopmode main.tex
```
`latexmk` may need multiple BibTeX + pdflatex rounds before citations settle. Do not stop after the first pass if the PDF already exists but references are unresolved.

### 5. Treat warnings differently from fatal errors
Typical non-fatal warnings:
- underfull/overfull hboxes
- font substitution warnings
- duplicate table destination warnings from float movement

Typical fatal blockers that need edits:
- missing `.sty` files
- `longtable not in 1-column mode`
- unresolved bibliography due to missing `.bbl` generation

A PDF can be acceptable for review even with the first category of warnings.

## Recommended workflow

### A. Verify tools
Check availability:
```bash
command -v pdflatex
command -v latexmk
command -v bibtex
```

### B. Patch for portability
If `newtxtext.sty` is missing, remove:
```latex
\usepackage{ae,aecompl}
\usepackage{newtxtext,newtxmath}
```
from both the working draft and the packaged `main.tex` if both exist.

### C. Replace problematic wide tables
If using `longtable` in MNRAS two-column mode, replace it with `table*` + `tabularx`.

### D. Build
Run:
```bash
cd /path/to/submission/package
latexmk -pdf -interaction=nonstopmode main.tex
```

### E. Verify success
Success indicators:
- `Output written on main.pdf`
- `Latexmk: All targets (main.pdf) are up-to-date`

## Submission package layout
A practical reusable package layout is:
```text
mnras_submission_package/
├── main.tex
├── references.bib
├── compile.sh
├── README.txt
├── figures/
│   └── README.txt
└── notes/
    ├── package_notes.txt
    └── manifest.json
```

## Pitfalls
- Don’t assume MNRAS can use `longtable` in the default two-column layout.
- Don’t assume Ubuntu/Debian TeX Live has `newtxtext/newtxmath` installed even if `mnras.cls` exists.
- Don’t stop after the first pdflatex pass when BibTeX is now required.
- Don’t treat all warnings as fatal; focus first on blockers that prevent a stable PDF.

## Good outcome criteria
- The document compiles to PDF successfully.
- Citations resolve via BibTeX.
- The user receives a reviewable PDF even if cosmetic warnings remain.
- The source is packaged in a clean submission-like directory for further editing.
