---
name: cmd-plotting
description: Generate astronomy colour-magnitude diagrams in Python with reproducible plotting choices.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# CMD Plotting

## When to Use
Use this skill for colour-magnitude diagrams or related astronomy plots in Python.

## Setup

Create a workspace-local environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install \
  matplotlib==3.11.1 pandas==3.0.5 pyarrow==25.0.0
```

The published lock was exercised with CPython 3.12 on macOS ARM64. Start from
`templates/plot_cmd.py` when its Parquet input and column names fit the task.

## Procedure
1. Keep only required columns.
2. Use consistent axis labeling and explicit units when available.
3. Prefer density representations for large samples.
4. Save publication-ready PNG outputs by default.

## Pitfalls
- Avoid scatter plots for very large datasets when density plots are more appropriate.
- Avoid undocumented axis transformations.
- **For a known cluster, anchor member selection to literature values.** Set the parallax / proper-motion cuts from the cluster's published distance and mean proper motion — not from whatever maximizes the member count. A count-maximizing selection pulls in field stars, smears the main sequence, and makes the turn-off (and any age read-off) wrong.

## Verification
- Run the plotting script from a directory containing `input.parquet`.
- Confirm that `cmd.png` is non-empty and that its labels and axes match the
  stated convention.
