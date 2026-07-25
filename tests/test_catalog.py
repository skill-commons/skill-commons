from __future__ import annotations

import copy
from pathlib import Path

import pytest

from skill_commons.catalog import (
    build_git_catalog,
    catalog_outputs,
    package_tree_digest,
    write_git_catalog,
)
from skill_commons.packer import SnapshotEntry

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/skill-commons/skill-commons"


def test_git_catalog_is_deterministic_and_records_published_skills() -> None:
    first = build_git_catalog(ROOT, REPOSITORY)
    second = build_git_catalog(ROOT, REPOSITORY + ".git")

    assert first == second
    assert first["repository"] == REPOSITORY
    assert first["schema_version"] == "1.1"
    assert len(first["skills"]) == len(
        [path for path in (ROOT / "skills").iterdir() if path.is_dir()]
    )
    assert len(first["skills"]) == 11
    assert [bundle["name"] for bundle in first["bundles"]] == [
        "General",
        "LaTeX",
        "Astronomy",
        "Data",
        "Visualization",
    ]
    records = {record["coordinate"]: record for record in first["skills"]}
    skill = records["aip/starhorse-access"]
    assert skill["coordinate"] == "aip/starhorse-access"
    assert skill["version"] == "2.0.2"
    assert skill["path"] == "skills/starhorse-access"
    assert skill["release_tag"] == "skill/starhorse-access/v2.0.2"
    assert skill["tree_digest"].startswith("sha256:")
    assert skill["bundle"] == {"id": "astronomy", "name": "Astronomy"}
    assert records["aip/tap-pyvo-adql-access"]["path"] == "skills/tap-pyvo-adql-access"
    assert records["aip/gaia-dr3-tap-query"]["path"] == "skills/gaia-dr3-tap-query"
    assert {item["coordinate"]: item["replacement"] for item in first["consolidations"]}[
        "aip/rave-dr6-nearest-100-plot"
    ] == "aip/rave-dr6"


def test_catalog_outputs_can_be_written_and_checked(tmp_path: Path) -> None:
    catalog = build_git_catalog(ROOT, REPOSITORY)
    output = tmp_path / "catalog"

    assert write_git_catalog(output, catalog, check=False)
    assert write_git_catalog(output, catalog, check=True)
    assert set(catalog_outputs(catalog)) == {"README.md", "index.json"}

    (output / "index.json").write_text("{}\n")
    assert not write_git_catalog(output, catalog, check=True)


def test_package_tree_digest_binds_paths_modes_and_bytes() -> None:
    base = [SnapshotEntry("SKILL.md", b"content\n", False)]
    changed_bytes = [SnapshotEntry("SKILL.md", b"different\n", False)]
    changed_mode = [SnapshotEntry("SKILL.md", b"content\n", True)]
    changed_path = [SnapshotEntry("OTHER.md", b"content\n", False)]

    assert package_tree_digest(base) != package_tree_digest(changed_bytes)
    assert package_tree_digest(base) != package_tree_digest(changed_mode)
    assert package_tree_digest(base) != package_tree_digest(changed_path)


def test_catalog_rejects_a_sidecar_name_that_differs_from_its_directory(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    skill = repository / "skills" / "starhorse-access"
    skill.parent.mkdir(parents=True)
    source = ROOT / "skills" / "starhorse-access"
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        destination = skill / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    bundles = repository / "bundles"
    bundles.mkdir()
    (bundles / "index.yaml").write_text(
        """schema_version: "1.0"
bundles:
- id: astronomy
  name: Astronomy
  description: Test bundle.
  skills: [aip/starhorse-access]
consolidations: []
"""
    )
    manifest = (skill / "research-skill.yaml").read_text()
    (skill / "research-skill.yaml").write_text(
        manifest.replace("name: starhorse-access", "name: wrong-name", 1)
    )

    with pytest.raises(ValueError, match="directory and package name differ"):
        build_git_catalog(repository, REPOSITORY)


def test_catalog_rejects_an_active_skill_in_multiple_bundles(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    skill = repository / "skills" / "starhorse-access"
    skill.parent.mkdir(parents=True)
    source = ROOT / "skills" / "starhorse-access"
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        destination = skill / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    bundles = repository / "bundles"
    bundles.mkdir()
    (bundles / "index.yaml").write_text(
        """schema_version: "1.0"
bundles:
- id: astronomy
  name: Astronomy
  description: First test bundle.
  skills: [aip/starhorse-access]
- id: duplicate
  name: Duplicate
  description: Second test bundle.
  skills: [aip/starhorse-access]
consolidations: []
"""
    )

    with pytest.raises(ValueError, match="multiple bundles"):
        build_git_catalog(repository, REPOSITORY)


def test_catalog_output_shape_is_json_safe() -> None:
    catalog = build_git_catalog(ROOT, REPOSITORY)
    altered = copy.deepcopy(catalog)
    altered["skills"][0]["research"]["keywords"].append(float("nan"))

    with pytest.raises(ValueError, match="finite"):
        catalog_outputs(altered)
