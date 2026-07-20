from __future__ import annotations

import json
from pathlib import Path

from skill_commons.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_profile_does_not_implicitly_add_all(capsys) -> None:
    exit_code = main(
        [
            "validate",
            str(ROOT / "examples" / "catalog-query-demo"),
            "--profile",
            "agent-skills",
            "--format",
            "json",
        ]
    )
    report = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert list(report["profiles"]) == ["agent-skills"]


def test_default_profile_selects_all(capsys) -> None:
    exit_code = main(
        [
            "validate",
            str(ROOT / "examples" / "catalog-query-demo"),
            "--format",
            "json",
        ]
    )
    report = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert set(report["profiles"]) == {
        "agent-skills",
        "ori-compatibility",
        "commons-publication",
    }


def _convert_args(skill: Path) -> list[str]:
    return [
        "convert",
        str(skill),
        "--namespace",
        "example",
        "--source-url",
        "https://github.com/example/synthetic-skills",
        "--source-revision",
        "ef78afcf1412575dd23e8e88c01dbf50b8b02836",
        "--source-path",
        f"fixtures/{skill.name}",
    ]


def test_convert_refuses_any_output_inside_source(capsys) -> None:
    source = ROOT / "tests" / "fixtures" / "name-mismatch"
    before = (source / "SKILL.md").read_bytes()

    exit_code = main(_convert_args(source) + ["--output", str(source / "SKILL.md")])

    assert exit_code == 2
    assert "inside the source" in capsys.readouterr().err
    assert (source / "SKILL.md").read_bytes() == before


def test_convert_refuses_colliding_or_existing_outputs(tmp_path: Path, capsys) -> None:
    source = ROOT / "tests" / "fixtures" / "name-mismatch"
    existing = tmp_path / "existing.yaml"
    existing.write_text("keep me\n")
    same = tmp_path / "same.json"

    existing_exit = main(_convert_args(source) + ["--output", str(existing)])
    same_exit = main(_convert_args(source) + ["--output", str(same), "--report", str(same)])

    assert existing_exit == 2
    assert same_exit == 2
    assert existing.read_text() == "keep me\n"
    assert not same.exists()
    errors = capsys.readouterr().err
    assert "overwrite" in errors
    assert "different paths" in errors


def test_convert_refuses_report_inside_candidate_output(tmp_path: Path, capsys) -> None:
    source = ROOT / "tests" / "fixtures" / "name-mismatch"
    candidate = tmp_path / "candidate"

    exit_code = main(
        _convert_args(source)
        + ["--out", str(candidate), "--report", str(candidate / "report.json")]
    )

    assert exit_code == 2
    assert "inside the candidate" in capsys.readouterr().err
    assert not candidate.exists()


def test_deep_yaml_is_rejected_with_an_operational_diagnostic(tmp_path: Path, capsys) -> None:
    skill = tmp_path / "deep-yaml"
    skill.mkdir()
    nested = "[" * 150 + "0" + "]" * 150
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: deep-yaml\n"
        "description: Exercise the structured-input depth budget.\n"
        f"unknown: {nested}\n"
        "---\n"
    )

    exit_code = main(["validate", str(skill), "--profile", "agent-skills"])

    assert exit_code == 2
    assert "nesting exceeds" in capsys.readouterr().err
