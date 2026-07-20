from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skill_commons.io import dump_yaml, load_yaml, load_yaml_file, semantic_digest, sha256_file
from skill_commons.validation import report_failed, validate_skill

ROOT = Path(__file__).resolve().parents[1]


def test_positive_example_passes_all_profiles() -> None:
    report = validate_skill(
        ROOT / "examples" / "catalog-query-demo",
        ["agent-skills", "ori-compatibility", "commons-publication"],
    )
    assert not report_failed(report), report
    assert {name: value["status"] for name, value in report["profiles"].items()} == {
        "agent-skills": "pass",
        "ori-compatibility": "pass",
        "commons-publication": "warn",
    }
    finding_codes = {item["code"] for item in report["profiles"]["commons-publication"]["findings"]}
    assert "COMMONS_EXTERNAL_ATTESTATIONS_REQUIRED" in finding_codes


def test_duplicate_yaml_key_is_rejected() -> None:
    with pytest.raises(Exception, match="duplicate key"):
        load_yaml("name: one\nname: two\n")


def test_missing_manifest_only_blocks_publication() -> None:
    report = validate_skill(
        ROOT / "tests" / "fixtures" / "name-mismatch",
        ["ori-compatibility", "commons-publication"],
    )
    assert report["profiles"]["ori-compatibility"]["status"] == "warn"
    assert report["profiles"]["commons-publication"]["status"] == "blocked"


def test_declared_dependencies_require_a_manifest_bound_lock(tmp_path: Path) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["dependencies"]["python"] = ["requests==2.32.4"]
    manifest_path.write_text(dump_yaml(manifest))

    missing_report = validate_skill(skill, ["commons-publication"])
    missing_codes = {
        item["code"] for item in missing_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_MISSING" in missing_codes

    lock = {
        "schema_version": "0.1.0-draft",
        "package": {
            "coordinate": "example/catalog-query-demo",
            "version": "1.0.0",
        },
        "manifest_digest": semantic_digest(manifest),
        "resolutions": [
            {
                "id": "linux-amd64-py312",
                "target": {
                    "operating_system": "linux",
                    "architecture": "amd64",
                    "python_implementation": "cpython",
                    "python_version": "3.12.12",
                },
                "resolver": {"name": "uv", "version": "0.9.30"},
                "requirements_digest": semantic_digest(manifest["dependencies"]),
                "python": [
                    {
                        "name": "requests",
                        "version": "2.32.4",
                        "direct": True,
                        "source": {
                            "kind": "index",
                            "url": "https://pypi.org/simple",
                        },
                        "artifact": {
                            "url": "https://example.invalid/requests.whl",
                            "sha256": "2" * 64,
                        },
                    }
                ],
                "system": [],
                "containers": [],
            }
        ],
    }
    (skill / "research-skill.lock").write_text(dump_yaml(lock))

    locked_report = validate_skill(skill, ["commons-publication"])
    locked_codes = {
        item["code"] for item in locked_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_MISSING" not in locked_codes
    assert "COMMONS_LOCK_INVALID" not in locked_codes
    assert "COMMONS_LOCK_MANIFEST_MISMATCH" not in locked_codes

    lock["resolutions"][0]["python"][0]["version"] = "1.0.0"
    (skill / "research-skill.lock").write_text(dump_yaml(lock))
    version_report = validate_skill(skill, ["commons-publication"])
    version_codes = {
        item["code"] for item in version_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_VERSION_CONSTRAINT_MISMATCH" in version_codes
    lock["resolutions"][0]["python"][0]["version"] = "2.32.4"

    manifest["compatibility"]["python"] = ">=3.13"
    manifest_path.write_text(dump_yaml(manifest))
    lock["manifest_digest"] = semantic_digest(manifest)
    (skill / "research-skill.lock").write_text(dump_yaml(lock))
    target_report = validate_skill(skill, ["commons-publication"])
    target_codes = {
        item["code"] for item in target_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_PYTHON_TARGET_MISMATCH" in target_codes
    manifest["compatibility"]["python"] = None
    manifest_path.write_text(dump_yaml(manifest))
    lock["manifest_digest"] = semantic_digest(manifest)

    lock["resolutions"][0]["target"]["python_version"] = "not-pep440"
    lock["resolutions"][0]["python"].append(
        {
            "name": "transitive-package",
            "version": "also-not-pep440",
            "direct": False,
            "source": {"kind": "index", "url": "https://pypi.org/simple"},
            "artifact": {
                "url": "https://example.invalid/transitive.whl",
                "sha256": "4" * 64,
            },
        }
    )
    (skill / "research-skill.lock").write_text(dump_yaml(lock))
    invalid_versions_report = validate_skill(skill, ["commons-publication"])
    invalid_version_codes = {
        item["code"]
        for item in invalid_versions_report["profiles"]["commons-publication"]["findings"]
    }
    assert {
        "COMMONS_LOCK_PYTHON_TARGET_INVALID",
        "COMMONS_LOCK_VERSION_INVALID",
    } <= invalid_version_codes
    lock["resolutions"][0]["target"]["python_version"] = "3.12.12"
    lock["resolutions"][0]["python"].pop()

    lock["resolutions"][0]["python"] = []
    (skill / "research-skill.lock").write_text(dump_yaml(lock))
    uncovered_report = validate_skill(skill, ["commons-publication"])
    uncovered_codes = {
        item["code"] for item in uncovered_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_DIRECT_DEPENDENCY_MISMATCH" in uncovered_codes

    manifest["dependencies"]["system"] = ["curl>=8"]
    manifest["dependencies"]["containers"] = ["example.invalid/tool@sha256:" + "3" * 64]
    manifest_path.write_text(dump_yaml(manifest))
    lock["manifest_digest"] = semantic_digest(manifest)
    lock["resolutions"][0]["requirements_digest"] = semantic_digest(manifest["dependencies"])
    lock["resolutions"][0]["python"] = [
        {
            "name": "requests",
            "version": "2.32.4",
            "direct": True,
            "source": {"kind": "index", "url": "https://pypi.org/simple"},
            "artifact": {
                "url": "https://example.invalid/requests.whl",
                "sha256": "2" * 64,
            },
        }
    ]
    (skill / "research-skill.lock").write_text(dump_yaml(lock))
    category_report = validate_skill(skill, ["commons-publication"])
    category_codes = {
        item["code"] for item in category_report["profiles"]["commons-publication"]["findings"]
    }
    assert "COMMONS_LOCK_CATEGORY_UNRESOLVED" in category_codes


def test_mixed_license_evidence_can_support_an_aggregate_expression(tmp_path: Path) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    data_license = skill / "DATA_LICENSE"
    data_license.write_text("Synthetic CC-BY-4.0 evidence fixture.\n")
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["package"]["license"] = "MIT AND CC-BY-4.0"
    manifest["license_evidence"] = [
        {
            "kind": "package-file",
            "expression": "MIT",
            "path": "LICENSE",
            "digest": sha256_file(skill / "LICENSE"),
            "applies_to": ["SKILL.md", "LICENSE", "research-skill.yaml"],
        },
        {
            "kind": "package-file",
            "expression": "CC-BY-4.0",
            "path": "DATA_LICENSE",
            "digest": sha256_file(data_license),
            "applies_to": ["DATA_LICENSE"],
        },
    ]
    manifest_path.write_text(dump_yaml(manifest))

    report = validate_skill(skill, ["commons-publication"])
    codes = {item["code"] for item in report["profiles"]["commons-publication"]["findings"]}

    assert "COMMONS_LICENSE_EVIDENCE_CONFLICT" not in codes
    assert "COMMONS_LICENSE_COVERAGE_PARTIAL" not in codes


def test_license_evidence_must_equal_not_merely_overlap_the_package_expression(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["license_evidence"][0]["expression"] = "MIT OR GPL-3.0-only"
    manifest_path.write_text(dump_yaml(manifest))

    report = validate_skill(skill, ["commons-publication"])
    codes = {item["code"] for item in report["profiles"]["commons-publication"]["findings"]}

    assert "COMMONS_LICENSE_EVIDENCE_CONFLICT" in codes


@pytest.mark.parametrize("portable_license", [None, "GPL-3.0-only"])
def test_publication_requires_equivalent_portable_and_manifest_licenses(
    tmp_path: Path, portable_license: str | None
) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    skill_path = skill / "SKILL.md"
    text = skill_path.read_text()
    if portable_license is None:
        text = text.replace("license: MIT\n", "")
    else:
        text = text.replace("license: MIT", f"license: {portable_license}")
    skill_path.write_text(text)

    report = validate_skill(skill, ["commons-publication"])
    codes = {item["code"] for item in report["profiles"]["commons-publication"]["findings"]}

    expected = (
        "COMMONS_PORTABLE_LICENSE_MISSING"
        if portable_license is None
        else "COMMONS_PORTABLE_LICENSE_MISMATCH"
    )
    assert expected in codes
    assert report["profiles"]["commons-publication"]["status"] == "blocked"


def test_untrusted_nested_sidecar_shapes_become_findings_not_tracebacks(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["dependencies"] = []
    manifest_path.write_text(dump_yaml(manifest))

    report = validate_skill(skill, ["ori-compatibility", "commons-publication"])

    assert report["profiles"]["ori-compatibility"]["status"] == "fail"
    assert report["profiles"]["commons-publication"]["status"] == "blocked"


def test_noncanonical_sidecar_values_become_schema_findings_not_tracebacks(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest_text = manifest_path.read_text().replace("version: 1.0.0", "version: 2026-07-20")
    manifest_path.write_text(manifest_text)

    report = validate_skill(skill, ["ori-compatibility", "commons-publication"])
    publication = report["profiles"]["commons-publication"]

    assert publication["status"] == "blocked"
    assert any(item["code"] == "COMMONS_SCHEMA_INVALID" for item in publication["findings"])
    assert report["input"]["manifest_digest"] is None


def test_agent_profile_rejects_non_string_license(tmp_path: Path) -> None:
    skill = tmp_path / "bad-license"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        """---
name: bad-license
description: Exercise optional license typing.
license: {kind: MIT}
---

# Bad license
"""
    )

    report = validate_skill(skill, ["agent-skills"])
    codes = {item["code"] for item in report["profiles"]["agent-skills"]["findings"]}

    assert report["profiles"]["agent-skills"]["status"] == "fail"
    assert "AGENT_INVALID_LICENSE" in codes


def test_ori_rejects_sidecar_only_semantics_and_unknown_required_extension(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["compatibility"]["operating_systems"] = ["linux"]
    manifest["compatibility"]["architectures"] = ["arm64"]
    manifest["compatibility"]["python"] = ">=3.12"
    manifest["compatibility"]["clients"] = "claude-only"
    manifest["dependencies"]["system"] = ["curl>=8"]
    manifest["extensions"] = {
        "de.aip.ori": {
            "schema": "urn:skill-commons:extension:de.aip.ori:1",
            "required": False,
            "data": {"config": [{"key": "EXAMPLE"}]},
        },
        "org.example.required": {
            "schema": "urn:example:required:1",
            "required": True,
            "data": {},
        },
    }
    manifest_path.write_text(dump_yaml(manifest))

    report = validate_skill(skill, ["ori-compatibility"])
    codes = {item["code"] for item in report["profiles"]["ori-compatibility"]["findings"]}

    assert {
        "ORI_SIDECAR_PLATFORM_MISMATCH",
        "ORI_SIDECAR_CONFIG_MISMATCH",
        "ORI_REQUIRED_EXTENSION_UNKNOWN",
        "ORI_SIDECAR_ARCHITECTURE_UNSUPPORTED",
        "ORI_SIDECAR_PYTHON_UNSUPPORTED",
        "ORI_SIDECAR_DEPENDENCY_UNSUPPORTED",
        "ORI_SIDECAR_CLIENTS_TYPE",
    } <= codes


def test_migrated_provenance_source_must_match_package_source(tmp_path: Path) -> None:
    skill = tmp_path / "catalog-query-demo"
    shutil.copytree(ROOT / "examples" / "catalog-query-demo", skill)
    manifest_path = skill / "research-skill.yaml"
    manifest = load_yaml_file(manifest_path)
    manifest["provenance"]["origin"] = "migrated"
    manifest["provenance"]["upstreams"] = [
        {
            "repository": "https://attacker.invalid/unrelated",
            "revision": "a" * 40,
            "path": "elsewhere",
            "digest": "sha256:" + "0" * 64,
            "relation": "source",
        }
    ]
    manifest_path.write_text(dump_yaml(manifest))

    report = validate_skill(skill, ["commons-publication"])
    codes = {item["code"] for item in report["profiles"]["commons-publication"]["findings"]}

    assert "COMMONS_SOURCE_UPSTREAM_MISMATCH" in codes
