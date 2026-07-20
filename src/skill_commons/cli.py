"""Command-line entry point for the Phase 0 reference tools."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from . import __version__
from .catalog import build_catalog_snapshot
from .converter import (
    build_manifest,
    conversion_report,
    emit_candidate,
    projected_skill,
)
from .io import dump_yaml, json_safe, load_json_file
from .packer import pack_snapshot, snapshot_tree
from .survey import survey_repository
from .validation import report_failed, validate_skill

PROFILE_ALIASES = {
    "agent-skills": ["agent-skills"],
    "ori": ["ori-compatibility"],
    "ori-compatibility": ["ori-compatibility"],
    "publication": ["commons-publication"],
    "commons-publication": ["commons-publication"],
    "all": ["agent-skills", "ori-compatibility", "commons-publication"],
}


def _atomic_create(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise ValueError(f"refusing to overwrite existing output: {path}") from exc
    finally:
        Path(temporary).unlink(missing_ok=True)


def _write_json(path: Path, value: Any) -> None:
    payload = (
        json.dumps(
            json_safe(value),
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    _atomic_create(path, payload)


def _inside(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _preflight_conversion_outputs(args: argparse.Namespace, skill_dir: Path) -> None:
    file_outputs = [path.resolve() for path in (args.output, args.report) if path is not None]
    if len(file_outputs) != len(set(file_outputs)):
        raise ValueError("manifest output and report must be different paths")
    for path in file_outputs:
        if _inside(path, skill_dir):
            raise ValueError("conversion outputs must not be inside the source skill")
        if path.exists():
            raise ValueError(f"refusing to overwrite existing output: {path}")
    if args.out is None:
        return
    output_dir = args.out.resolve()
    if _inside(output_dir, skill_dir) or _inside(skill_dir, output_dir):
        raise ValueError("candidate output directory must not overlap the source skill")
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ValueError("candidate output directory must be empty")
    if args.report is not None and _inside(args.report.resolve(), output_dir):
        raise ValueError("external report path must not be inside the candidate output")


def _profiles(values: list[str]) -> list[str]:
    selected: list[str] = []
    for value in values:
        for part in value.split(","):
            key = part.strip()
            if key not in PROFILE_ALIASES:
                raise ValueError(f"unknown profile: {key}")
            selected.extend(PROFILE_ALIASES[key])
    return list(dict.fromkeys(selected))


def _print_validation_text(report: dict[str, Any]) -> None:
    for name, profile in report["profiles"].items():
        print(f"{name}: {profile['status']} ({profile['contract']})")
        for finding in profile["findings"]:
            pointer = f" {finding['pointer']}" if finding.get("pointer") else ""
            print(f"  [{finding['severity']}] {finding['code']}{pointer}: {finding['message']}")


def _command_validate(args: argparse.Namespace) -> int:
    selected = _profiles(args.profile or ["all"])
    report = validate_skill(args.skill_dir, selected)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_validation_text(report)
    return 1 if report_failed(report) else 0


def _command_convert(args: argparse.Namespace) -> int:
    skill_dir = args.skill_dir.resolve()
    _preflight_conversion_outputs(args, skill_dir)
    source_snapshot = snapshot_tree(skill_dir, require_manifest=False)
    manifest, findings, dispositions = build_manifest(
        skill_dir,
        namespace=args.namespace,
        source_url=args.source_url,
        source_revision=args.source_revision,
        source_path=args.source_path,
        population_claim=args.population_claim,
        source_snapshot=source_snapshot,
    )
    projected = projected_skill(
        skill_dir, manifest, args.projection, source_snapshot=source_snapshot
    )
    report = conversion_report(
        skill_dir,
        manifest,
        findings,
        dispositions,
        args.projection,
        projected,
        source_snapshot=source_snapshot,
    )
    if args.out:
        emit_candidate(
            skill_dir,
            args.out,
            manifest,
            report,
            projected,
            source_snapshot=source_snapshot,
        )
    elif args.output:
        _atomic_create(args.output, dump_yaml(manifest).encode("utf-8"))
    else:
        print(dump_yaml(manifest), end="")
    if args.report:
        report_copy = dict(report)
        _write_json(args.report, report_copy)
    blocked = any(
        item["severity"] in {"error", "blocker"} for item in report["conversion_findings"]
    )
    blocked = blocked or report["profiles"]["commons-publication"]["status"] in {
        "fail",
        "blocked",
    }
    return 1 if blocked else 0


def _command_pack(args: argparse.Namespace) -> int:
    skill_dir = args.skill_dir.resolve(strict=True)
    output = args.output.resolve()
    if output.is_relative_to(skill_dir):
        raise ValueError("archive output must be outside the package root")
    snapshot = snapshot_tree(skill_dir)
    if not args.allow_draft:
        report = validate_skill(
            skill_dir, ["agent-skills", "commons-publication"], snapshot=snapshot
        )
        if report_failed(report):
            _print_validation_text(report)
            print(
                "refusing to pack a candidate-readiness-blocked package; "
                "use --allow-draft for testing",
                file=sys.stderr,
            )
            return 1
    digest = pack_snapshot(snapshot, output)
    print(json.dumps({"artifact": str(args.output), "digest": digest}, sort_keys=True))
    return 0


def _command_audit(args: argparse.Namespace) -> int:
    report = survey_repository(
        args.repository,
        source_url=args.source_url,
        expected_revision=args.expected_revision,
    )
    _write_json(args.output, report)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "active": report["summary"]["active_skills"],
                "parked": report["summary"]["parked_skills"],
            },
            sort_keys=True,
        )
    )
    return 0


def _command_catalog(args: argparse.Namespace) -> int:
    releases = [load_json_file(path) for path in args.release]
    negatives = [load_json_file(path) for path in args.negative_record]
    snapshot = build_catalog_snapshot(
        releases,
        sequence=args.sequence,
        generated_at=args.generated_at,
        expires_at=args.expires_at,
        previous_snapshot_digest=args.previous_snapshot_digest,
        negative_sequence=args.negative_sequence,
        negative_records=negatives,
    )
    _write_json(args.output, snapshot)
    print(json.dumps({"output": str(args.output), "releases": len(releases)}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-commons")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="run independent validation profiles")
    validate.add_argument("skill_dir", type=Path)
    validate.add_argument("--profile", action="append")
    validate.add_argument("--format", choices=["text", "json"], default="text")
    validate.set_defaults(func=_command_validate)

    convert = subparsers.add_parser("convert", help="emit a sidecar and conversion evidence")
    convert.add_argument("skill_dir", type=Path)
    convert.add_argument("--namespace", required=True)
    convert.add_argument("--source-url", required=True)
    convert.add_argument("--source-revision", required=True)
    convert.add_argument(
        "--source-path",
        required=True,
        help="repository-relative path to the source package directory",
    )
    convert.add_argument("--population-claim", default="github-community-tree")
    convert.add_argument("--projection", choices=["portable", "ori-bridge"], default="ori-bridge")
    output_group = convert.add_mutually_exclusive_group()
    output_group.add_argument("--output", type=Path, help="write research-skill.yaml only")
    output_group.add_argument(
        "--out", type=Path, help="write candidate package and evidence to an empty directory"
    )
    convert.add_argument("--report", type=Path, help="write the complete conversion report")
    convert.set_defaults(func=_command_convert)

    pack = subparsers.add_parser(
        "pack", help="build deterministic candidate bytes (does not publish)"
    )
    pack.add_argument("skill_dir", type=Path)
    pack.add_argument("--output", required=True, type=Path)
    pack.add_argument("--allow-draft", action="store_true")
    pack.set_defaults(func=_command_pack)

    audit = subparsers.add_parser("audit", help="generate a source-pinned structural survey")
    audit.add_argument("repository", type=Path)
    audit.add_argument("--source-url", required=True)
    audit.add_argument("--expected-revision", required=True)
    audit.add_argument("--output", required=True, type=Path)
    audit.set_defaults(func=_command_audit)

    catalog = subparsers.add_parser("catalog", help="assemble a static positive catalog snapshot")
    catalog.add_argument("--release", action="append", type=Path, default=[])
    catalog.add_argument("--negative-record", action="append", type=Path, default=[])
    catalog.add_argument("--sequence", required=True, type=int)
    catalog.add_argument("--negative-sequence", required=True, type=int)
    catalog.add_argument("--generated-at", required=True)
    catalog.add_argument("--expires-at", required=True)
    catalog.add_argument("--previous-snapshot-digest")
    catalog.add_argument("--output", required=True, type=Path)
    catalog.set_defaults(func=_command_catalog)
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
        jsonschema.ValidationError,
        subprocess.CalledProcessError,
        yaml.YAMLError,
    ) as exc:
        print(f"skill-commons: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
