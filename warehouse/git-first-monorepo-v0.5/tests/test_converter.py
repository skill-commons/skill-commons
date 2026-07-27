from __future__ import annotations

from pathlib import Path

from skill_commons.converter import (
    build_manifest,
    conversion_report,
    emit_candidate,
    projected_skill,
)
from skill_commons.io import parse_skill, parse_skill_text

ROOT = Path(__file__).resolve().parents[1]
REVISION = "ef78afcf1412575dd23e8e88c01dbf50b8b02836"
SOURCE = "https://github.com/example/synthetic-skills"


def convert_fixture(name: str):
    skill = ROOT / "tests" / "fixtures" / name
    manifest, findings, dispositions = build_manifest(
        skill,
        namespace="example",
        source_url=SOURCE,
        source_revision=REVISION,
        source_path=f"fixtures/{name}",
        population_claim="synthetic-test",
    )
    return skill, manifest, findings, dispositions


def test_conversion_is_loss_accounted_and_does_not_mutate_source() -> None:
    skill, manifest, findings, dispositions = convert_fixture("legacy-observation")
    before = (skill / "SKILL.md").read_bytes()
    proposed = projected_skill(skill, manifest, "portable")
    _, original_body, _ = parse_skill(skill)
    proposed_dir_body = proposed.split("---\n", 2)[2]

    assert manifest["package"]["version"] == "1.0.0"
    assert manifest["package"]["license"] == "NOASSERTION"
    assert manifest["dependencies"]["python"] == ["requests>=2"]
    assert manifest["extensions"]["de.aip.ori"]["data"]["activation"] == {
        "requires_toolsets": ["web"]
    }
    assert proposed_dir_body == original_body
    assert (skill / "SKILL.md").read_bytes() == before
    assert any(item.code == "CONVERT_FIELD_UNMAPPED" for item in findings)
    source_fields = {item["source"] for item in dispositions}
    assert {
        "name",
        "description",
        "version",
        "body",
        "metadata.hermes.requires_toolsets",
    } <= source_fields


def test_conflicting_dependency_conventions_are_not_unioned() -> None:
    _, manifest, findings, _ = convert_fixture("dependency-conflict")
    assert manifest["dependencies"]["python"] == ["requests>=2"]
    assert any(item.code == "CONVERT_DEPENDENCY_CONFLICT" for item in findings)


def test_name_mismatch_becomes_alias_proposal() -> None:
    _, manifest, findings, _ = convert_fixture("name-mismatch")
    assert manifest["package"]["name"] == "name-mismatch"
    assert manifest["package"]["aliases"] == ["old-name"]
    assert any(item.code == "CONVERT_NAME_ALIAS_PROPOSED" for item in findings)


def test_report_is_deterministic() -> None:
    skill, manifest, findings, dispositions = convert_fixture("legacy-observation")
    projected = projected_skill(skill, manifest, "ori-bridge")
    first = conversion_report(skill, manifest, findings, dispositions, "ori-bridge", projected)
    second = conversion_report(skill, manifest, findings, dispositions, "ori-bridge", projected)
    assert first == second
    assert set(first["proposed_projections"]) == {"portable", "ori-bridge"}


def test_malformed_known_fields_are_quarantined_without_leaf_loss(tmp_path: Path) -> None:
    skill = tmp_path / "malformed-fields"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        """---
name: malformed-fields
description: Exercise complete loss accounting.
version: 1.2.3
prerequisites:
  python: {unexpected: shape}
  commands: 7
  mpi: openmpi
platforms: {linux: true}
tags: [valid, 3]
category: [research]
related_skills: 7
metadata:
  hermes:
    requires_tools: {unexpected: shape}
    config: {unexpected: shape}
    tags: 3
    category: [research]
    related_skills: {unexpected: shape}
---

# Malformed fields
"""
    )

    manifest, findings, dispositions = build_manifest(
        skill,
        namespace="example",
        source_url=SOURCE,
        source_revision=REVISION,
        source_path="fixtures/malformed-fields",
        population_claim="synthetic-test",
    )

    unmapped = manifest["extensions"]["de.aip.ori"]["data"]["unmapped"]
    assert {
        "prerequisites.python.unexpected",
        "prerequisites.commands",
        "prerequisites.mpi",
        "platforms.linux",
        "tags",
        "category",
        "related_skills",
        "metadata.hermes.requires_tools.unexpected",
        "metadata.hermes.config.unexpected",
        "metadata.hermes.tags",
        "metadata.hermes.category",
        "metadata.hermes.related_skills.unexpected",
    } <= set(unmapped)
    assert any(item.code == "CONVERT_FIELD_UNMAPPED" for item in findings)
    assert all(
        item["disposition"]
        in {
            "copied",
            "normalized",
            "preserved",
            "proposed",
            "conflict",
            "unmapped",
        }
        for item in dispositions
    )


def test_dotted_legacy_keys_cannot_overwrite_nested_loss_accounting(tmp_path: Path) -> None:
    skill = tmp_path / "dotted-key-collision"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        """---
name: dotted-key-collision
description: Exercise collision-free legacy field accounting.
tags:
  a: NESTED-VALUE
tags.a: TOP-LEVEL-VALUE
---

# Dotted key collision
"""
    )

    manifest, _, _ = build_manifest(
        skill,
        namespace="example",
        source_url=SOURCE,
        source_revision=REVISION,
        source_path="fixtures/dotted-key-collision",
        population_claim="synthetic-test",
    )
    unmapped = manifest["extensions"]["de.aip.ori"]["data"]["unmapped"]

    assert "tags.a" in unmapped
    assert {"NESTED-VALUE", "TOP-LEVEL-VALUE"} <= set(unmapped.values())


def test_candidate_emission_preserves_body_bytes_and_executable_mode(tmp_path: Path) -> None:
    skill = tmp_path / "crlf-candidate"
    skill.mkdir()
    body = b"\r\n# CRLF body\r\n\r\nKeep these bytes.\r\n"
    (skill / "SKILL.md").write_bytes(
        b"---\r\n"
        b"name: crlf-candidate\r\n"
        b"description: Exercise byte-faithful candidate emission.\r\n"
        b"version: 1.0.0\r\n"
        b"---\r\n" + body
    )
    script = skill / "run.sh"
    script.write_bytes(b"#!/bin/sh\nexit 0\n")
    script.chmod(0o751)
    manifest, findings, dispositions = build_manifest(
        skill,
        namespace="example",
        source_url=SOURCE,
        source_revision=REVISION,
        source_path="fixtures/crlf-candidate",
        population_claim="synthetic-test",
    )
    projected = projected_skill(skill, manifest, "portable")
    report = conversion_report(skill, manifest, findings, dispositions, "portable", projected)

    output = tmp_path / "candidate-output"
    emit_candidate(skill, output, manifest, report, projected)

    assert (output / "package" / "SKILL.md").read_bytes().endswith(body)
    assert (output / "package" / "run.sh").stat().st_mode & 0o111
    assert (output / "evidence" / "source-to-portable.patch").is_file()
    assert (output / "evidence" / "source-to-ori-bridge.patch").is_file()


def test_report_first_conversion_quarantines_yaml_dates_and_malformed_core_fields(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "legacy-edge-case"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        """---
name: {unexpected: shape}
description: [unexpected, shape]
version: broken
author: [Unknown, Authors]
license: {signal: MIT}
date: 2026-07-20
threshold: .nan
large_integer: 9007199254740992
1: numeric-key-value
$legacy-yaml-key:literal: reserved-prefix-value
---

# Legacy edge case
"""
    )
    manifest, findings, dispositions = build_manifest(
        skill,
        namespace="example",
        source_url=SOURCE,
        source_revision=REVISION,
        source_path="fixtures/legacy-edge-case",
        population_claim="synthetic-test",
    )

    portable = projected_skill(skill, manifest, "portable")
    bridge = projected_skill(skill, manifest, "ori-bridge")
    report = conversion_report(skill, manifest, findings, dispositions, "portable", portable)
    unmapped = manifest["extensions"]["de.aip.ori"]["data"]["unmapped"]

    assert "TODO: supply a reviewed skill description." in portable
    assert parse_skill_text(bridge)[0]["description"] == (
        "TODO: supply a reviewed skill description."
    )
    assert unmapped["date"] == {
        "$legacy_yaml_type": "date",
        "value": "2026-07-20",
    }
    assert unmapped["threshold"] == {
        "$legacy_yaml_type": "non-finite-float",
        "value": "nan",
    }
    assert unmapped["large_integer"] == {
        "$legacy_yaml_type": "unsafe-integer",
        "value": "9007199254740992",
    }
    assert "numeric-key-value" in unmapped.values()
    assert "reserved-prefix-value" in unmapped.values()
    assert {
        "name.unexpected",
        "description",
        "version",
        "author",
        "license.signal",
    } <= set(unmapped)
    assert report["candidate"]["projection"] == "portable"
    assert report["profiles"]["agent-skills"]["status"] == "fail"
    assert any(item.code == "CONVERT_DESCRIPTION_INVALID" for item in findings)
