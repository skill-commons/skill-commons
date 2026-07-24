#!/usr/bin/env python3
"""Publication-style CMD hexbin plot from a Parquet cache."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot CMD hexbin from Parquet cache.")
    parser.add_argument("--input", required=True, help="Input Parquet file")
    parser.add_argument("--x", default="bprp0", help="Colour column")
    parser.add_argument("--y", default="mg0", help="Magnitude column")
    parser.add_argument("--out", default="cmd.png", help="Output PNG")
    parser.add_argument(
        "--provenance",
        default="cmd_provenance.json",
        help="Output provenance JSON",
    )
    parser.add_argument("--title", default="Colour-Magnitude Diagram")
    parser.add_argument("--gridsize", type=int, default=320)
    args = parser.parse_args()

    df = pd.read_parquet(args.input, columns=[args.x, args.y])
    mask = np.isfinite(df[args.x]) & np.isfinite(df[args.y])
    plot = df.loc[mask, [args.x, args.y]]

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(7.2, 8.0), facecolor="white")
    hb = ax.hexbin(
        plot[args.x],
        plot[args.y],
        gridsize=args.gridsize,
        mincnt=1,
        bins="log",
        cmap="viridis",
        linewidths=0,
    )
    ax.invert_yaxis()
    ax.set_xlabel(args.x)
    ax.set_ylabel(args.y)
    ax.set_title(args.title)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("log10(count)")
    fig.tight_layout()
    out = Path(args.out)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)

    provenance = {
        "figure": str(out),
        "source_cache": args.input,
        "columns": [args.x, args.y],
        "rows_in": int(len(df)),
        "rows_plotted": int(len(plot)),
        "plot_type": "hexbin",
        "style": "white_background",
        "created_utc": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
    }
    Path(args.provenance).write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
