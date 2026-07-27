from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from skill_commons.io import load_yaml_file

ROOT = Path(__file__).resolve().parents[1]
VALID_SKILL = ROOT / "tests" / "fixtures" / "valid" / "catalog-query-demo"


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
    manifest = load_yaml_file(VALID_SKILL / "research-skill.yaml")
    manifest["package"]["source"]["path"] = "C:/escape"

    assert not jsonschema.Draft202012Validator(schema).is_valid(manifest)
