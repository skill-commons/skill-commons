---
name: latex-research-paper
description: Generate complete, compilable LaTeX research papers in formal academic style with full section
  structure, BibTeX references, and figure support.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# LaTeX Research Paper Generator

## When to Use
Generate complete, compilable LaTeX research papers in formal academic style with full section structure, BibTeX references, and figure support.

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


## Trigger Conditions
Use when the user asks to:
- Write a research paper in LaTeX
- Generate an academic manuscript
- Create a full paper draft (not just a template)
- Produce a compilable `.tex` document with all sections

## Workflow

### 1. Title Slug Derivation
Convert the paper title into a directory name:
- Lowercase all characters
- Replace spaces with hyphens
- Remove all special characters (retain only `[a-z0-9-]`)

Create the project under a user-approved workspace path such as
`<workspace>/<titleslug>/`.

### 2. Directory & File Creation
Create the following structure:
```
<workspace>/<titleslug>/
├── main.tex
├── references.bib
└── figures/          (only if figures are needed)
```

### 3. LaTeX Document Structure (`main.tex`)

Use `\documentclass{article}` with these packages (minimum set):
```latex
\usepackage{amsmath, amssymb}          % Math
\usepackage{graphicx}                  % Figures
\usepackage{hyperref}                  % Links
\usepackage{booktabs}                  % Tables
\usepackage{microtype}                 % Typography
\usepackage{geometry}                  % Margins
\geometry{margin=1in}
```

**Mandatory sections** (do NOT skip unless explicitly told otherwise):
1. **Title** and **Author(s)** — use supplied information or a clearly marked placeholder
2. **Abstract** — summarize supported material; mark unavailable results as TODOs
3. **Introduction** — problem statement, motivation, contributions
4. **Related Work** — survey of relevant literature (use `\cite{}` placeholders)
5. **Methodology** — approach, methods, framework, or experiments
6. **Results** — report supplied or computed findings; never invent outcomes
7. **Discussion** — interpretation, limitations, implications
8. **Conclusion** — summary, future work
9. **References** — `\bibliographystyle{plain}` + `\bibliography{references}`

### 4. Writing Style
- Formal academic tone throughout
- No conversational language, first-person plural preferred over first-person singular
- Precise technical terminology
- Logical flow between sections (explicit transitions)
- Include equations where appropriate (use `equation` or `align` environments)
- Include tables/figures when they add value (use `table`/`figure` environments with `\caption` and `\label`)

### 5. Citations & Bibliography
- Use `\cite{key}` throughout the text
- Generate `references.bib` entries only from supplied or verified bibliographic metadata
- Use `plain` bibliography style
- If a needed reference is unavailable, use an explicit `% TODO: verify citation`
  placeholder rather than plausible-looking metadata

### 6. Figures & Tables
- Place images in `figures/` subdirectory
- Use placeholder paths: `\includegraphics{figures/plot1.png}`
- Add `\caption{}` and `\label{}` to every figure and table
- Reference figures/tables in text with `\ref{}`

### 7. Compilation Verification
After writing, compile to verify:
```bash
cd <workspace>/<titleslug>/
rm -f main.aux main.log main.out main.toc main.bbl main.blg  # clean stale files first
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
Fix any compilation errors. The document must compile cleanly.

**Practical compilation pitfalls:**
- **Missing images**: Always use `\usepackage[draft]{graphicx}` so missing image files fall back to draft boxes instead of fatal errors
- **`\\textquote{}` is NOT standard LaTeX**: It requires the `csquotes` package. Use standard LaTeX ``quotes'' or `\\textit{}` for inline quotes
- **At least 2 pdflatex passes + bibtex between them are required** for citations to resolve and cross-references to stabilize
- **Clean stale aux files** before compiling to avoid phantom "undefined reference" warnings from old runs

### 7.1 Quality Checklist
- [ ] Directory name correctly derived from title
- [ ] All 9 mandatory sections present
- [ ] Uses `draft` mode for graphicx (unless images are real files)
- [ ] No undefined control sequences (verify `\\textquote` isn't used — replace with ``quotes'' or standard alternatives)
- [ ] Compiles without errors (clean aux files → pdflatex → bibtex → pdflatex ×2)
- [ ] Formal academic tone throughout
- [ ] Citations in text match entries in `references.bib`
- [ ] No author names, citations, datasets, numerical results, or conclusions were invented
- [ ] Figures/tables have captions, labels, and are referenced in text
- [ ] Equations properly formatted with LaTeX math environments

### 7.2 Generating Diagrams for Papers

When the user asks for architecture diagrams or figures:

1. **Generate with Python/matplotlib** (not as placeholder text):
   - Write a standalone Python script in `figures/generate_<name>.py`
   - Use `matplotlib.use('Agg')` (headless)
   - Set `fig, ax = plt.subplots(..., facecolor=BG_COLOR)`
   - Use `FancyBboxPatch` for cards — **CRITICAL: use `facecolor='none'` NOT `facecolor='transparent'`** — matplotlib's `colors.to_rgba` throws a ValueError on `'transparent'`
   - Output to `figures/<name>.png` at 150 dpi
   - Run the script with `python3` (not `python` — may not exist)

2. **Integrate into the paper**:
   - Change `\usepackage[draft]{graphicx}` to `\usepackage{graphicx}` (remove draft mode)
   - Use `\includegraphics[width=0.95\textwidth]{figures/<name>.png}`
   - Compile again — the full chain: `rm -f main.{aux,log,out,toc,bbl,blg} && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

3. **BibTeX warnings**: `@misc` entries with URLs but no journal field are fine — BibTeX only warns (doesn't fail). Suppress by leaving journal out rather than adding fake data.
