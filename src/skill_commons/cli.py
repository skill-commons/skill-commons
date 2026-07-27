"""Command-line entry point for the federated Skill Commons catalog."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

from . import __version__
from .catalog import build_catalog, write_catalog
from .upstreams import check_upstreams


def _command_catalog(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    catalog = build_catalog(root)
    current = write_catalog(root, catalog, check=args.check)
    if args.check and not current:
        print("generated README.md or catalog/index.json is stale", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "skills": len(catalog["skills"]),
                "status": "current" if args.check else "written",
            },
            sort_keys=True,
        )
    )
    return 0


def _command_check_upstreams(args: argparse.Namespace) -> int:
    results = check_upstreams(build_catalog(args.root.resolve()))
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for result in results:
            suffix = ""
            if result["observed_revision"] != result["current_revision"]:
                suffix = f" (branch now {result['current_revision'][:12]})"
            print(f"{result['name']}: {result['status']}{suffix}")
            for issue in result["issues"]:
                print(f"  - {issue}")
    return 1 if any(result["status"] != "current" for result in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-commons")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser(
        "catalog",
        help="generate README.md and catalog/index.json from registry metadata",
    )
    catalog.add_argument("--root", type=Path, default=Path.cwd())
    catalog.add_argument("--check", action="store_true")
    catalog.set_defaults(func=_command_catalog)

    upstreams = subparsers.add_parser(
        "check-upstreams",
        help="report source-directory changes on tracked Git branches",
    )
    upstreams.add_argument("--root", type=Path, default=Path.cwd())
    upstreams.add_argument("--format", choices=["text", "json"], default="text")
    upstreams.set_defaults(func=_command_check_upstreams)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
        yaml.YAMLError,
    ) as exc:
        print(f"skill-commons: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
