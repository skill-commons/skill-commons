"""Deterministic static catalog assembly from trusted, evidence-bound release records."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
from license_expression import get_spdx_licensing

from . import __version__
from .io import semantic_digest


def _catalog_schema() -> dict[str, Any]:
    schema_root = Path(__file__).resolve().parent / "schemas"
    if not schema_root.exists():
        schema_root = Path(__file__).resolve().parents[2] / "schemas"
    return json.loads((schema_root / "catalog-snapshot.schema.json").read_text(encoding="utf-8"))


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an RFC 3339 timestamp") from exc
    if timestamp.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return timestamp


def _reject_duplicate_keys(records: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    observed: set[tuple[Any, ...]] = set()
    for record in records:
        key = tuple(record[field] for field in fields)
        if key in observed:
            label = "@".join(str(part) for part in key)
            raise ValueError(f"duplicate catalog identity: {label}")
        observed.add(key)


def build_catalog_snapshot(
    release_records: list[dict[str, Any]],
    *,
    sequence: int,
    generated_at: str,
    expires_at: str,
    previous_snapshot_digest: str | None,
    negative_sequence: int,
    negative_records: list[dict[str, Any]],
) -> dict[str, Any]:
    schema = _catalog_schema()
    structural_snapshot = {
        "schema_version": "0.1.0-draft",
        "sequence": sequence,
        "generated_at": generated_at,
        "expires_at": expires_at,
        "previous_snapshot_digest": previous_snapshot_digest,
        "generator": {"name": "skill-commons", "version": __version__},
        "input_digest": "sha256:" + "0" * 64,
        "releases": release_records,
        "negative_state": {"sequence": negative_sequence, "records": negative_records},
    }
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    validator.validate(structural_snapshot)
    generated = _parse_timestamp(generated_at, "generated_at")
    expires = _parse_timestamp(expires_at, "expires_at")
    if generated >= expires:
        raise ValueError("expires_at must be later than generated_at")
    if sequence == 1 and previous_snapshot_digest is not None:
        raise ValueError("sequence 1 must not name a previous snapshot")
    if sequence > 1 and previous_snapshot_digest is None:
        raise ValueError("sequence greater than 1 requires previous_snapshot_digest")
    _reject_duplicate_keys(release_records, ("coordinate", "version"))
    _reject_duplicate_keys(negative_records, ("coordinate", "version", "kind"))
    for record in release_records:
        assessments = record.get("assessments", {})
        if assessments.get("license") != "verified":
            raise ValueError("catalog release requires a verified license assessment")
        if assessments.get("publisher_authority") != "verified":
            raise ValueError("catalog release requires verified publisher authority")
        license_info = get_spdx_licensing().validate(record["license"], strict=True)
        if record["license"] == "NOASSERTION" or license_info.errors:
            message = "; ".join(license_info.errors) or "NOASSERTION is not publishable"
            raise ValueError(
                f"catalog release license is not a verified SPDX expression: {message}"
            )
        if record.get("release_state") not in {"active", "deprecated"}:
            raise ValueError("positive catalog releases must be active or deprecated")
        publication_status = record.get("validation_profiles", {}).get("commons-publication")
        if publication_status not in {"pass", "warn"}:
            raise ValueError("catalog release did not pass candidate-readiness validation")
    releases = sorted(release_records, key=lambda item: (item["coordinate"], item["version"]))
    negatives = sorted(
        negative_records,
        key=lambda item: (item["coordinate"], item["version"], item["kind"]),
    )
    snapshot = {
        "schema_version": "0.1.0-draft",
        "sequence": sequence,
        "generated_at": generated_at,
        "expires_at": expires_at,
        "previous_snapshot_digest": previous_snapshot_digest,
        "generator": {"name": "skill-commons", "version": __version__},
        "input_digest": semantic_digest({"releases": releases, "negative_state": negatives}),
        "releases": releases,
        "negative_state": {"sequence": negative_sequence, "records": negatives},
    }
    validator.validate(snapshot)
    return snapshot
