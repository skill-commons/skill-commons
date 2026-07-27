from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import jsonschema
import pytest

from skill_commons.io import canonical_json_bytes, dump_yaml, load_json_file, parse_skill

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_WITH_SKILL_VERSIONS = [
    "research-skill.schema.json",
    "research-skill-lock.schema.json",
]

VALID_SEMVER = [
    "0.0.0",
    "1.2.3",
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-0.3.7",
    "1.0.0-x.7.z.92",
    "1.0.0+20130313144700",
    "1.0.0-beta+exp.sha.5114f85",
]

INVALID_SEMVER = [
    "1.0",
    "01.0.0",
    "1.01.0",
    "1.0.01",
    "1.0.0-",
    "1.0.0-.",
    "1.0.0-alpha..1",
    "1.0.0-01",
    "1.0.0+",
    "1.0.0+build..1",
]


@pytest.mark.parametrize("schema_name", SCHEMAS_WITH_SKILL_VERSIONS)
def test_skill_version_contract_is_semver_2(schema_name: str) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema["$defs"]["semver"])

    assert all(validator.is_valid(version) for version in VALID_SEMVER)
    assert not any(validator.is_valid(version) for version in INVALID_SEMVER)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_canonical_json_rejects_non_finite_numbers(value: float) -> None:
    with pytest.raises(ValueError, match="finite JSON data model"):
        canonical_json_bytes({"value": value})


def test_canonical_json_rejects_integers_outside_the_i_json_safe_range() -> None:
    with pytest.raises(ValueError, match="finite JSON data model"):
        canonical_json_bytes({"value": 9_007_199_254_740_992})


def test_canonical_json_uses_rfc_8785_number_and_key_serialization() -> None:
    assert canonical_json_bytes({"z": 1.0, "a": 1e-7}) == b'{"a":1e-7,"z":1}'


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, date(2026, 7, 20)])
def test_yaml_output_rejects_values_outside_the_finite_json_data_model(value: object) -> None:
    with pytest.raises(ValueError, match="JSON"):
        dump_yaml({"value": value})


def test_parse_skill_preserves_crlf_body_bytes(tmp_path: Path) -> None:
    skill_dir = tmp_path / "crlf-skill"
    skill_dir.mkdir()
    source = (
        b"---\r\n"
        b"name: crlf-skill\r\n"
        b"description: Exercise byte-faithful parsing.\r\n"
        b"---\r\n"
        b"\r\n"
        b"# CRLF body\r\n"
    )
    (skill_dir / "SKILL.md").write_bytes(source)

    _, body, text = parse_skill(skill_dir)

    assert text.encode("utf-8") == source
    assert body.encode("utf-8") == b"\r\n# CRLF body\r\n"


@pytest.mark.parametrize(
    "payload, message",
    [
        ('{"value": NaN}', "non-finite"),
        ('{"value": 1, "value": 2}', "duplicate"),
    ],
)
def test_json_inputs_reject_nonstandard_constants_and_duplicate_keys(
    tmp_path: Path, payload: str, message: str
) -> None:
    path = tmp_path / "input.json"
    path.write_text(payload)
    with pytest.raises(ValueError, match=message):
        load_json_file(path)
