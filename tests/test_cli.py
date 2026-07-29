from __future__ import annotations

import json
import shutil
from pathlib import Path

from skill_commons.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    shutil.copytree(ROOT / "registry", repository / "registry")
    shutil.copytree(ROOT / "categories", repository / "categories")
    return repository


def test_catalog_command_writes_and_checks_generated_views(tmp_path: Path, capsys) -> None:
    repository = _repository(tmp_path)

    assert main(["catalog", "--root", str(repository)]) == 0
    written = json.loads(capsys.readouterr().out)
    assert written == {"skills": 15, "status": "written"}
    assert (repository / "README.md").is_file()
    assert (repository / "catalog" / "index.json").is_file()

    assert main(["catalog", "--root", str(repository), "--check"]) == 0
    current = json.loads(capsys.readouterr().out)
    assert current == {"skills": 15, "status": "current"}


def test_catalog_check_reports_stale_outputs(tmp_path: Path, capsys) -> None:
    repository = _repository(tmp_path)

    assert main(["catalog", "--root", str(repository), "--check"]) == 1
    assert "stale" in capsys.readouterr().err
