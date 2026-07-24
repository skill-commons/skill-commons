---
name: latex-paper-iteration
description: Iteratively improve LaTeX research papers — structural fixes, prose polishing, figure integration,
  compilation cycles. Also covers merging multiple papers into a unified manuscript.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# LaTeX Paper Iterative Improvement

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.
- Confirm that citations, data, numerical results, and conclusions are sourced rather
  than invented.


Use this skill when iteratively improving an existing LaTeX research paper, merging multiple papers, or generating scientific figures.

## When to Use
- Iteratively improving an existing LaTeX paper (prose, structure, figures, compilation)
- Merging multiple papers into one unified manuscript
- Adding/removing figures, tables, references across many iterations
- Running multiple compilation cycles (≥2 passes for bibliography)
- User says "iterate N times" or "improve X times"

## Approach

### Preferred: Single-File Rewrite for Major Changes
For substantial rewrites (10+ changes, new sections, structural overhaul), rewrite the
entire `main.tex` in one controlled file update rather than chaining fragile text
substitutions. Preserve a recoverable copy or use version control before a full rewrite.

### Monolithic main.tex vs Section Files
- **Default to monolithic** `main.tex` (all sections inlined) — it's simpler to iterate on and less prone to file corruption
- **Section files** (`sections/*.tex`) are an optional pattern for very long papers — but if you create them, make sure you actually `\\input{}` them from `main.tex`
- **Cleanup stale sections/** — after going monolithic, remove stale `sections/` directory

### Iteration Pattern
1. **Read** the complete current `main.tex`
2. **Plan** the improvements (structural, prose, figures, references)
3. **Apply** — use targeted edits for small changes or a full-file update for major changes
4. **Compile** — run `pdflatex` twice for proper bibliography resolution
5. **Verify** output page count and check for errors in the `.log` file

### Multi-Round Iteration (e.g., 7 figures + 25 text rounds)
When user requests many iterations:
1. **Figure iterations first** — generate/refresh matplotlib figures with `generate_*.py` scripts
2. **Text iterations second** — write comprehensive main.tex with all improvements applied
3. **Compile at the end** — no need to compile after every single iteration if applying all changes in one controlled update
4. **For iterative refinement** — use targeted changes between compilations

### Merging Multiple Papers
When merging multiple papers into one unified manuscript:
1. **Read all source papers** to understand content and structure
2. **Plan merged structure** — identify unique sections, overlapping content, logical flow
3. **Write monolithic main.tex** in one shot — include all merged content, new sections, cross-references
4. **Generate figures** — create new figures for merged paper (architecture diagrams, combined models)
5. **Compile and iterate** — 10+ rounds of refinement

## Figure Generation Workflow

### Scientific Figure Style Guide
When generating figures for academic papers, use these guidelines:
- **Professional color palettes** — use hex codes, avoid rainbow gradients. Good palettes:
  - Blues: `#2C5F8A`, `#4A90A4`, `#1E4D7A`
  - Greens: `#5BA06B`, `#4BA05A`, `#1B5E20`
  - Reds: `#C8374B`, `#D94F5C`
  - Oranges: `#D4872C`, `#E8913A`
  - Purples: `#7B68AE`, `#9B7DB8`
- **White background** (not dark) — `facecolor='white'`
- **Clear layer labels and groupings** — use `FancyBboxPatch` for rounded boxes, `FancyArrowPatch` for arrows
- **Consistent font sizes** — 7-11pt for labels, 13-15pt for titles
- **Proper legends** — include legend for color-coded elements
- **High DPI** — `dpi=200` minimum
- **Use `plt.close()`** after saving to free memory
- **Use `bbox_inches='tight'`** for clean borders
- **Use `plt.tight_layout()`** before saving

### Figure Generation Pattern
```python
# 1. Save a reviewed script as figures/generate_fig_name.py.
# 2. Execute it from the project directory:
#    python3 figures/generate_fig_name.py

# 3. Reference in LaTeX
# \includegraphics[width=0.9\\textwidth]{figures/fig_name.png}

# 4. Recompile from the project directory:
#    pdflatex -interaction=nonstopmode main.tex
```

### Figure Iteration
When user says "iterate images 7 times":
1. **Write improved matplotlib script** with better layout, colors, labels
2. **Execute and verify** — check for errors
3. **Repeat** — each iteration should visibly improve the figure (better layout, more labels, cleaner design)
4. **Recompile** paper after all figure iterations are done

### Common Figure Pitfalls
- **FancyArrowPatch**: Does not accept `style=` or `linestyle=` — these are `matplotlib.lines` parameters. Use `arrowstyle=` only.
- **SyntaxError with repeated kwargs**: `arrowstyle='->', arrowstyle='-|>'` — remove duplicates
- **Unicode in f-strings**: Use `f"\\u2022 {text}"` instead of literal bullet characters
- **matplotlib.use('Agg')**: Must be set BEFORE any other matplotlib imports for headless rendering

## LaTeX Compilation Rules
- **First pass**: generates `.aux`, `.toc`, bibliography entries
- **Second pass**: resolves cross-references, citation numbers, page numbers
- **Third pass** (only if needed): fixes TOC, cross-reference shifts
- Typical paper: 2 passes suffice
- Check `tail -5` for "Output written on main.pdf (N pages)"
- For large papers, check the .log file for warnings

## Common Pitfalls
- **Duplicate packages**: `hyperref` often duplicated via patches — always check full file before patching
- **Package conflicts**: `biblatex` vs traditional BibTeX — pick one and remove the other. Use `\\bibliographystyle{plainnat}` + `\\bibliography{references}`
- **Unused packages**: Remove unused `tcolorbox`, `mdframed`, `siunitx`, `csquotes`, `mdframed` if not referenced in body
- **Missing `\\usepackage{titlesec}`**: If using `\\titleformat`, must include `titlesec`
- **Concurrent edits**: Re-read a file before writing when another person or agent may
  have changed it, and preserve unrelated changes.
- **Partial reads**: Read the complete file before a full-file rewrite; reconstructing it
  from a partial view can corrupt content.
- **Section files not used**: If you create `sections/*.tex` but don't `\\input{}` them from `main.tex`, they're dead weight — clean them up

### Subprocess Encoding
When automating LaTeX compilation in Python, always handle encoding:
```python
import subprocess
result = subprocess.run(
    ['pdflatex', '-interaction=nonstopmode', 'main.tex'],
    capture_output=True, text=True, errors='replace', timeout=120
)
```

## File Structure Convention
```
<workspace>/<article-slug>/
├── main.tex              ← monolithic (all sections inlined)
├── references.bib        ← BibTeX references
├── main.pdf              ← compiled output
├── figures/
│   ├── generate_*.py     ← figure generation scripts
│   └── *.png             ← generated figures
├── main.aux, .log, .out, .toc, .bbl, .blg
└── sections/             ← OPTIONAL: only if \\input{}ed from main.tex
```

## Compilation Command
```bash
cd <workspace>/<article-slug> && pdflatex -interaction=nonstopmode main.tex 2>&1 | tail -10
```

Always compile at least twice for proper cross-references and bibliography.
