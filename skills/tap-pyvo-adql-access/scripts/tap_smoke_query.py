#!/usr/bin/env python3
"""Small TAP/ADQL smoke query helper.

Examples:
  python tap_smoke_query.py --endpoint https://www.rave-survey.org/tap/ \
    --query 'SELECT TOP 1 * FROM ravedr6.dr6_x_gaiaedr3' --out /tmp/rave_probe
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny TAP query and cache preview/provenance.")
    parser.add_argument("--endpoint", required=True, help="TAP endpoint URL, e.g. https://www.rave-survey.org/tap/")
    parser.add_argument("--query", required=True, help="ADQL query; use TOP N, not LIMIT")
    parser.add_argument("--out", default="tap_probe", help="Output directory")
    args = parser.parse_args()

    import pyvo  # imported here so --help works without pyvo

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    service = pyvo.dal.TAPService(args.endpoint)
    result = service.run_sync(args.query)
    table = result.to_table()
    df = table.to_pandas()

    (out / "query.adql").write_text(args.query.rstrip() + "\n")
    df.head(20).to_csv(out / "preview.csv", index=False)
    try:
        df.to_parquet(out / "data.parquet", index=False)
        cache = "data.parquet"
    except Exception:
        df.to_csv(out / "data.csv", index=False)
        cache = "data.csv"

    provenance = {
        "access_method": "tap-adql-pyvo",
        "endpoint": args.endpoint,
        "created_utc": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "query_file": "query.adql",
        "cache": cache,
        "row_count": int(len(df)),
        "columns": list(df.columns),
    }
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
