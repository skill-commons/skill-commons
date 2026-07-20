from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from skill_commons.survey import survey_repository

ROOT = Path(__file__).resolve().parents[1]


def test_astroagentassistant_fixture_is_pinned_and_minimized() -> None:
    fixture = json.loads(
        (ROOT / "fixtures" / "surveys" / "astroagentassistant-ef78afc.json").read_text()
    )
    assert fixture["source_lock"] == {
        "repository": "https://github.com/arm2arm/AstroAgentAssistant",
        "revision": "ef78afcf1412575dd23e8e88c01dbf50b8b02836",
        "root_tree": "70828a8059843280d2867bab5ee7b60382a315a8",
        "license_blob": "e3402849838bc944fe2f1fcf4876328cb966fc52",
        "citation_blob": "8b980caf0e6f3c6001759bef722daef976228b61",
        "include": ["**/SKILL.md"],
        "parked_prefix": "outdated-skills/",
    }
    assert fixture["summary"]["active_skills"] == 114
    assert fixture["summary"]["parked_skills"] == 14
    assert fixture["summary"]["no_per_skill_license_declaration_active"] == 61
    assert fixture["summary"]["skills_ref_0_1_1_pass_active"] == 6
    assert len(fixture["observations"]) == 128
    forbidden = {"description", "author", "dependencies", "body"}
    assert all(not (forbidden & observation.keys()) for observation in fixture["observations"])


def test_survey_rejects_a_dirty_worktree(tmp_path: Path) -> None:
    repository = tmp_path / "source"
    skill = repository / "demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Synthetic survey fixture.\n---\n\n# Demo\n"
    )
    (repository / "LICENSE").write_text("Synthetic license fixture.\n")
    (repository / "CITATION.cff").write_text("cff-version: 1.2.0\n")
    subprocess.run(["git", "init", "-b", "main", repository], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            repository,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "add",
            ".",
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            repository,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    revision = subprocess.run(
        ["git", "-C", repository, "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (skill / "SKILL.md").write_text("changed\n")

    with pytest.raises(ValueError, match="dirty"):
        survey_repository(
            repository,
            source_url="https://example.invalid/survey-fixture",
            expected_revision=revision,
        )
