---
name: iterative-paper-improvement
description: Structured multi-round improvement workflow for LaTeX academic papers — each round targets
  specific improvements (structure, prose, figures, compilation). Also covers merging multiple papers
  and multi-phase iterations (X figure rounds + Y text rounds).
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Iterative Paper Improvement Workflow

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.
- Never invent citations, datasets, quantitative results, or scientific conclusions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.


## Overview

When the user asks to iterate/improve a LaTeX paper, run a structured multi-round improvement cycle with compilation verification after each round.

## When to Use

- User says "improve", "iterate", "revise", or "make better" a paper
- User requests "more scientific", "more understandable", or "better style" for figures
- Merging multiple papers into a unified manuscript
- User says "iterate N times on images, M times on text"

## Process Selection

### Option A: Standard 10-Round Cycle (existing papers)
Use for iterative improvement of a single paper. See rounds 1-10 below.

### Option B: Merged Paper
Use when combining multiple papers into one. Process:
1. **Read all source papers** — read each `main.tex` completely
2. **Plan merged structure** — identify unique sections, overlapping content, logical flow
3. **Write monolithic main.tex** — use one controlled update with all merged content,
   new sections, and cross-references
4. **Generate new figures** — architecture diagrams, combined models, etc.
5. **Compile and iterate** — 10+ rounds of refinement

### Option C: Multi-Phase Iteration (X figure rounds + Y text rounds)
Use when user says "iterate 7 times on images, 25 times on text". Process:
1. **Figure iterations FIRST** — write/rewrite matplotlib scripts, execute, iterate until satisfied
2. **Text iterations SECOND** — write comprehensive main.tex with ALL improvements applied in one shot (not 25 separate patch+compile cycles)
3. **Compile at the end** — no need to compile after every single iteration when applying all text changes at once
4. **Deliver** — PDF with all improvements

## The 10-Round Improvement Cycle

Each round targets specific improvements:

### Round 1: Structural fixes
- Remove duplicate packages (`\usepackage{hyperref}` twice)
- Remove unused packages (tcolorbox, mdframed, siunitx, csquotes, mdframed)
- Switch biblatex → traditional BibTeX for broader compatibility
- Add missing figures (maturity model, repo structure)
- Fix `\bibliography{}` references

### Round 2: Academic prose
- Improve introduction flow and transitions
- Strengthen thesis statements
- Formalize language ("we aim" → "the framework aims")
- Enhance motivation paragraphs

### Round 3: Related work
- Better contextualize literature positioning
- Strengthen the reproducibility crisis narrative
- Clarify how the framework advances the state of the art

### Round 4: Practical sections
- Add concrete examples and verification steps
- Expand step-by-step guides
- Add metadata field descriptions

### Round 5: Method/technical sections
- Improve technical precision (Snakemake, REANA descriptions)
- Better explain tool integration
- Add code examples where helpful

### Round 6: Governance and quality
- Tighten quality checklist descriptions
- Improve role definitions
- Expand contribution workflow

### Round 7: Language tightening
- Remove redundant phrases
- Eliminate wordiness
- Ensure consistent tone throughout

### Round 8: Captions and formatting
- Improve table and figure captions (more descriptive)
- Ensure consistent citation formatting
- Check cross-references

### Round 9: Future outlook
- Expand roadmap details
- Improve community growth section
- Enhance EOSC/FDO integration descriptions

### Round 10: Final polish
- Consistency checks (em-dashes, terminology)
- Strengthen conclusion
- Final impact statement

## Key Pitfalls

- **Concurrent edits**: Re-read a file before writing when another person or agent may
  have changed it, and preserve unrelated changes.
- **FancyArrowPatch**: Does not accept `style=` — use `arrowstyle=` only. No `linestyle=` param.
- **Duplicate packages**: Check for duplicate `\usepackage` entries
- **biblatex vs BibTeX**: If references.bib is standard BibTeX, use `\bibliographystyle{plainnat}` not biblatex
- **Unicode strings in f-strings**: Use `"\u2022"` instead of literal bullet character
- **Repeated keyword args**: `arrowstyle='->', arrowstyle='-|>'` — remove duplicates
- **Partial reads**: Read the complete file before a full-file rewrite; reconstructing it
  from a partial view can corrupt content.
- **Section files not used**: If you create sections/*.tex but don't \input{} them from main.tex, they're dead weight — clean them up

## Figure Generation Rule

**Whenever the paper references a diagram/figure:**
1. Generate a Python script using matplotlib
2. Use scientific style: professional colors (hex palette), clear labels, legends, white background
3. Save to `figures/` directory with descriptive name
4. Recompile and verify

### Scientific Figure Style Guide
- Professional color palettes (avoid rainbow gradients)
- Clear layer labels and groupings
- Consistent font sizes (9-11pt for labels)
- White background (not dark) — `facecolor='white'`
- Proper legends
- High DPI (200+)
- Use FancyBboxPatch for rounded boxes
- Use FancyArrowPatch for directional arrows
- Use sans-serif fonts for modern look
- Use `plt.tight_layout()` before saving
- Use `plt.savefig(..., bbox_inches='tight')` for clean borders

## Process

### Step 1: Read and audit
Read full `main.tex` to understand current state, identify issues.

### Step 2: Choose process
- Single paper improve → 10-round cycle
- Multiple papers → merged paper process
- X/Y iterations → figure iterations first, comprehensive text rewrite second, compile at end

### Step 3: Plan rounds
Determine which rounds are most relevant. Skip rounds that have no impact.

### Step 4: Apply changes
Use targeted edits for small changes. For major rewrites, use one controlled update of
`main.tex` after preserving a recoverable copy or version-control state.
**For text iteration counts > 10**: Write main.tex comprehensively in one shot rather than patching 10+ times.

### Step 5: Compile after each round
Always run `pdflatex` and check output for errors. Compile at least twice for bibliography.

### Step 6: Deliver PDF
Return the PDF through the user's requested delivery mechanism and report its path.

## File Locations
- Paper: `<workspace>/<article-slug>/main.tex`
- Figures: `<workspace>/<article-slug>/figures/`
- BibTeX: `<workspace>/<article-slug>/references.bib`
- Section files: `<workspace>/<article-slug>/sections/` (optional)

## Compilation
```bash
cd <workspace>/<article-slug>
pdflatex -interaction=nonstopmode main.tex 2>&1 | tail -10
```

Always compile at least twice for proper cross-references and bibliography.
