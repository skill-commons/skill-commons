---
name: mnras-latex-portable
description: Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package
  failures and fixing common two-column table issues.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# MNRAS LaTeX Portable Build

## When to Use
Use this skill when preparing a manuscript for MNRAS (Monthly Notices of the Royal Astronomical Society) journal submission. Covers: portable build on Ubuntu, fixing two-column table issues, avoiding missing font packages, and packaging submission artifacts.

## Procedure

### 1. Install TeX Live dependencies
First inspect the available tools. Install system packages only with the user's approval
and appropriate privileges:
```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-base texlive-latex-extra \
  texlive-fonts-extra texlive-fonts-recommended texlive-publishers
```

### 2. Compile the manuscript
```bash
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
```

### 3. Fix two-column table overflow
MNRAS uses `mnras.cls` with `twocolumn` layout. Tables wider than the column width fail with:
```
! LaTeX Error: Float too large for this column.
```
Fix by using `table*` or `\resizebox{\linewidth}{!}{...}`:
```latex
\begin{table*}
  \resizebox{\linewidth}{!}{
    \begin{tabular}{lcc}
      \hline
      Column A & Column B & Column C \\
      ...
    \end{tabular}
  }
\end{table*}
```

### 4. Fix missing font packages
Common missing fonts on minimal Ubuntu installs:
```bash
# With approval, install Type-1 fonts
sudo apt-get install -y cm-super texlive-fonts-extra

# If still missing, add to preamble:
\usepackage[T1]{fontenc}
\usepackage{lmodern}
```

### 5. Package submission artifacts
```bash
# Create zip of manuscript + figures
zip -r mnras_submission.zip manuscript.tex references.bib figures/ tables/ appendices/

# Create separate BibTeX file
cp references.bib mnras_refs.bib
```

## MNRAS Starting Points

Treat these as build defaults, not a substitute for the current MNRAS author
instructions. Verify the journal's current class, option, length, and packaging rules
before submission.

| Item | Requirement |
|---|---|
| Class | `\documentclass[lineno,referee]{mnras}` |
| Bibliography | `\bibliographystyle{mnras}` with `usenatbib` |
| Abstract | Check the current journal word limit |
| Keywords | `\keywords{}` after abstract |
| Figure captions | Below figures |
| Table captions | Above tables |
| Layout | MNRAS normally uses a two-column layout |

## Pitfalls
- Do NOT assume `pdflatex` is available — check with `which pdflatex` first.
- Do NOT use `\begin{sidewaystable}` without `rotating` package — add `\usepackage{rotating}`.
- Do NOT use `booktabs` without installing `texlive-latex-extra`.
- Use `table` for one-column tables and `table*` for full-width tables; resize only when
  readability is preserved.

## Verification
- `pdflatex` runs without errors (or only non-critical warnings).
- Output PDF opens correctly in a viewer.
- Bibliography compiles with correct citation labels.
- Submission zip contains all required files.
