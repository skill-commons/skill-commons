---
name: latex-journal-submission-package
description: Adapt a stable LaTeX manuscript to a journal, fix portable build problems, verify the result, and assemble a clean submission archive; includes MNRAS guidance.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# LaTeX Journal Submission Package

## When to Use

Use this skill after a manuscript is scientifically stable and needs:

- adaptation to a journal class or author instructions;
- portable compilation on a clean environment;
- bibliography and asset normalization;
- a complete, reviewable submission directory and archive;
- diagnosis of journal-specific layout or TeX package failures.

Use `latex-research-paper` for drafting, merging, and substantive manuscript revision.
This skill does not submit a manuscript or claim journal compliance on the user's behalf.

## Workflow

### 1. Read current instructions and inspect the manuscript

Journal rules change. Check the current authoritative author instructions before choosing
class options, word limits, bibliography style, figure formats, or archive contents.
Then inventory:

- the main TeX entry point and included section files;
- bibliography system and database;
- figures, tables, appendices, custom classes, styles, and fonts;
- generated files that should not enter the submission;
- available build tools (`latexmk`, `pdflatex`, `bibtex`, `biber`, `kpsewhich`).

Do not install system packages without the user's approval.

### 2. Work in a clean package directory

```text
submission-package/
├── main.tex
├── references.bib
├── figures/
├── compile.sh
├── README.txt
└── notes/
    ├── manifest.json
    └── package-notes.txt
```

Copy only files required by the manuscript. Rewrite absolute paths and verify every
`\input`, `\include`, `\includegraphics`, bibliography, class, and style reference.

### 3. Normalize the bibliography

Pick the system required by the journal. If converting an inline `thebibliography`,
create real BibTeX entries from verified metadata rather than parsing prose into guessed
fields. arXiv IDs returned by APIs may include version suffixes such as `v2`; normalize
them only when matching records, and preserve the cited version when scientifically
relevant.

### 4. Add a portable build helper

```bash
#!/usr/bin/env bash
set -euo pipefail
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
else
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
fi
```

Adapt the fallback for `biber` or another engine when the document requires it.

### 5. Compile and classify failures

Fix fatal problems first:

- missing class, style, font, or figure files;
- bibliography tools or databases not found;
- undefined control sequences;
- journal layout incompatibilities;
- unresolved file paths.

Treat overfull/underfull boxes and font substitutions as review items rather than
automatically fatal errors. Re-run until citations and cross-references stabilize.
If TeX is unavailable, still deliver the structurally checked package and report that
PDF verification remains outstanding.

### 6. Verify and archive

- compile from the clean package directory, not the development tree;
- inspect the PDF visually;
- search logs for unresolved citations and references;
- compare the archive file list with the manifest;
- scan for credentials, private notes, local paths, and unrelated data;
- create the zip only after the directory is complete.

## MNRAS Portability Reference

Treat these as known failure patterns, not a substitute for current MNRAS instructions.

Start from the journal's current class guidance. A commonly used research layout is:

```latex
\documentclass[fleqn,usenatbib,useAMS]{mnras}
```

On minimal TeX Live installations:

- `newtxtext`/`newtxmath` may be missing; remove optional font packages or install the
  journal-supported dependency set with approval;
- `longtable` does not work in normal two-column mode; use `table` for one column or
  `table*` with `tabularx` for a readable full-width table;
- do not resize tables until text becomes illegible;
- use `\bibliographystyle{mnras}` with the journal's expected citation system.

Before suggesting Ubuntu packages, inspect the environment. A typical approved install
may include `latexmk`, `texlive-latex-base`, `texlive-latex-extra`,
`texlive-fonts-recommended`, and `texlive-publishers`; package names and sufficiency can
change.

## Verification Checklist

- [ ] Current journal instructions were checked and recorded.
- [ ] All included source, bibliography, figure, class, and style files are present.
- [ ] The package compiles from its own clean directory, or the missing tool blocker is
      explicit.
- [ ] Citations and cross-references resolve.
- [ ] Fatal errors are absent and remaining warnings were reviewed.
- [ ] The PDF was visually inspected.
- [ ] README and manifest describe contents, build command, and outstanding placeholders.
- [ ] The archive contains no secrets, private notes, absolute paths, or unrelated files.
