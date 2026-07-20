from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from skill_commons.io import load_yaml_file

ROOT = Path(__file__).resolve().parents[1]
STRETCH_SCHEMAS = [
    "collection.schema.json",
    "external-catalog-record.schema.json",
    "installation-profile.schema.json",
    "tombstone.schema.json",
]
DIGEST = "sha256:" + "a" * 64


def test_all_json_schemas_are_valid_draft_2020_12() -> None:
    schemas = sorted((ROOT / "schemas").rglob("*.schema.json"))
    assert schemas
    for path in schemas:
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_core_manifest_rejects_windows_drive_qualified_package_paths() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "research-skill.schema.json").read_text(encoding="utf-8")
    )
    manifest = load_yaml_file(ROOT / "examples" / "catalog-query-demo" / "research-skill.yaml")
    manifest["package"]["source"]["path"] = "C:/escape"

    assert not jsonschema.Draft202012Validator(schema).is_valid(manifest)


def _validate_stretch(name: str, instance: dict[str, object]) -> None:
    schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        instance
    )


def test_stretch_schemas_are_explicitly_non_normative() -> None:
    for name in STRETCH_SCHEMAS:
        schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        assert schema["$comment"].startswith("NON-NORMATIVE PHASE 0 STRETCH SKETCH")


def test_collection_sketch_carries_rfc_collection_concepts() -> None:
    _validate_stretch(
        "collection.schema.json",
        {
            "schema_version": "0.1.0-draft",
            "namespace": "aip",
            "name": "stellar-catalogue-analysis",
            "version": "1.0.0",
            "description": "Pinned astronomy skill collection.",
            "owner": "urn:aai:group:aip",
            "curators": ["urn:aai:user:curator"],
            "purpose": "Reproducible stellar catalogue analysis.",
            "license_policy": "Only packages with verified public redistribution rights.",
            "review_rationale": "Reviewed for the AIP pilot.",
            "members": [
                {
                    "coordinate": "aip/starhorse-access",
                    "version": "2.1.0",
                    "digest": DIGEST,
                    "requirement": "required",
                    "order": 0,
                }
            ],
            "compatibility": {
                "clients": ["ori"],
                "operating_systems": ["linux"],
                "architectures": ["amd64"],
            },
            "known_conflicts": [],
            "environment_hints": ["one-environment-per-skill"],
            "orchestration_hints": [],
            "intended_scopes": ["workspace", "research-group"],
            "export_targets": ["ori"],
        },
    )


def test_installation_profile_uses_rfc_scope_and_risk_vocabularies() -> None:
    _validate_stretch(
        "installation-profile.schema.json",
        {
            "schema_version": "0.1.0-draft",
            "name": "aip-fleet-seed",
            "version": "1.0.0",
            "owner": "urn:aai:group:aip",
            "scope": "fleet-baked",
            "collections": [],
            "releases": [
                {
                    "coordinate": "aip/starhorse-access",
                    "version": "2.1.0",
                    "digest": DIGEST,
                }
            ],
            "policy": {
                "maximum_risk": "R2",
                "network": "declared-only",
                "named_secrets": "deny",
                "external_side_effects": "deny",
                "paid_services": "deny",
                "approval": "institutional-policy",
            },
            "update_behavior": {
                "mode": "review-required",
                "on_local_divergence": "refuse-overwrite",
            },
            "target_environment": {
                "client": "ori",
                "operating_system": "linux",
                "architecture": "amd64",
                "python": ">=3.11",
                "resolution_digest": None,
            },
        },
    )


def test_external_record_requires_scan_state_and_only_verified_mapping() -> None:
    _validate_stretch(
        "external-catalog-record.schema.json",
        {
            "schema_version": "0.1.0-draft",
            "ecosystem": "claude-marketplace",
            "native_id": "example/skill",
            "source": "https://example.invalid/skill",
            "source_revision": None,
            "native_name": "skill",
            "native_version": None,
            "native_artifact_digest": None,
            "license_signal": None,
            "attribution": "Observed from the named external catalog.",
            "last_seen_at": "2026-07-20T12:00:00Z",
            "scan": {
                "status": "not-scanned",
                "scanner": None,
                "scanned_at": None,
                "evidence_digest": None,
            },
            "mapping": {
                "coordinate": "aip/starhorse-access",
                "version": "2.1.0",
                "digest": DIGEST,
                "verification": "verified",
                "evidence_digest": DIGEST,
            },
        },
    )


def test_tombstone_can_target_an_identity_and_carries_appeal_state() -> None:
    _validate_stretch(
        "tombstone.schema.json",
        {
            "schema_version": "0.1.0-draft",
            "sequence": 1,
            "kind": "tombstone",
            "effect": "block-install",
            "severity": "high",
            "target": {"coordinate": "aip/withdrawn-skill"},
            "reason": {
                "code": "legal-withdrawal",
                "summary": "Publication authority was withdrawn.",
            },
            "issued_at": "2026-07-20T12:00:00Z",
            "expires_at": None,
            "authority": {
                "issuer": "urn:aai:group:aip-curators",
                "policy": "aip-phase0-allowlist-v1",
                "decision_digest": DIGEST,
            },
            "replacement": None,
            "advisory_links": [],
            "appeal": {"state": "open", "url": None, "updated_at": None},
            "evidence": [DIGEST],
        },
    )
