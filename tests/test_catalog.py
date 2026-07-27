from __future__ import annotations

import copy
import shutil
from pathlib import Path

import pytest
import yaml

from skill_commons.catalog import (
    build_catalog,
    catalog_json_bytes,
    catalog_outputs,
    render_readme,
    write_catalog,
)

ROOT = Path(__file__).resolve().parents[1]


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    shutil.copytree(ROOT / "registry", repository / "registry")
    shutil.copytree(ROOT / "categories", repository / "categories")
    return repository


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def test_catalog_is_deterministic_and_records_federated_skills() -> None:
    first = build_catalog(ROOT)
    second = build_catalog(ROOT)

    assert first == second
    assert first["schema_version"] == "2.0"
    assert first["registry"] == "https://github.com/skill-commons/skill-commons"
    assert len(first["skills"]) == 11
    assert [category["name"] for category in first["categories"]] == [
        "General",
        "LaTeX",
        "Astronomy",
        "Data",
        "Visualization",
    ]
    records = {record["name"]: record for record in first["skills"]}
    starhorse = records["starhorse-access"]
    assert starhorse["category"] == {"id": "astronomy", "name": "Astronomy"}
    assert starhorse["source"]["revision"] == ("3530b84d27f5d29536cb44c6242ab91949963db0")
    assert starhorse["source"]["path"] == "skills/starhorse-access"
    assert starhorse["source"]["url"].endswith(
        "/tree/3530b84d27f5d29536cb44c6242ab91949963db0/skills/starhorse-access"
    )
    assert starhorse["hermes"]["identifier"] == (
        "skill-commons/curated-research-skills/skills/starhorse-access"
    )


def test_readme_contains_every_skill_description_source_and_install() -> None:
    catalog = build_catalog(ROOT)
    readme = render_readme(catalog)

    for record in catalog["skills"]:
        assert f"`{record['name']}`" in readme
        assert record["description"] in readme
        assert record["source"]["url"] in readme
        assert record["hermes"]["install"] in readme


def test_generated_outputs_can_be_written_and_checked(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    catalog = build_catalog(repository)

    assert write_catalog(repository, catalog, check=False)
    assert write_catalog(repository, catalog, check=True)
    assert set(catalog_outputs(catalog)) == {
        Path("README.md"),
        Path("catalog/index.json"),
    }

    (repository / "catalog" / "index.json").write_text("{}\n", encoding="utf-8")
    assert not write_catalog(repository, catalog, check=True)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("revision", "main", "exact lowercase 40-character Git SHA"),
        ("tree", "ABCDEF", "exact lowercase 40-character Git SHA"),
        ("path", "../skills/arxiv", "safe repository-relative directory"),
        ("path", "/skills/arxiv", "safe repository-relative directory"),
        ("path", "skills//arxiv", "safe repository-relative directory"),
        ("path", r"skills\arxiv", "safe repository-relative directory"),
        ("path", "skills/arxiv@{1}", "safe repository-relative directory"),
        ("path", "skills/arxiv/SKILL.md", "safe repository-relative directory"),
        ("repository", "git@github.com:example/skills.git", "canonical HTTPS GitHub"),
        (
            "repository",
            "https://github.com/example/skills?ref=main",
            "canonical HTTPS GitHub",
        ),
        ("branch", "../main", "safe Git branch"),
    ],
)
def test_catalog_rejects_invalid_source_identity(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    registry["skills"][0]["source"][field] = value
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match=message):
        build_catalog(repository)


def test_catalog_rejects_duplicate_name_and_source(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)

    duplicate_name = copy.deepcopy(registry["skills"][0])
    duplicate_name["source"]["path"] = "skills/different"
    registry["skills"].append(duplicate_name)
    _write_yaml(path, registry)
    with pytest.raises(ValueError, match="duplicate active skill name"):
        build_catalog(repository)

    registry = _yaml(ROOT / "registry" / "index.yaml")
    duplicate_source = copy.deepcopy(registry["skills"][0])
    duplicate_source["name"] = "different"
    registry["skills"].append(duplicate_source)
    _write_yaml(path, registry)
    with pytest.raises(ValueError, match="duplicate canonical source"):
        build_catalog(repository)


@pytest.mark.parametrize("name", ["1arxiv", "arxiv.skill", "skill", "readme"])
def test_catalog_rejects_non_hermes_skill_names(tmp_path: Path, name: str) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    registry["skills"][0]["name"] = name
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="Hermes-compatible skill name"):
        build_catalog(repository)


def test_catalog_requires_one_category_per_active_skill(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "categories" / "index.yaml"
    categories = _yaml(path)
    categories["categories"][0]["skills"].remove("arxiv")
    _write_yaml(path, categories)
    with pytest.raises(ValueError, match="missing from categories: arxiv"):
        build_catalog(repository)

    categories = _yaml(ROOT / "categories" / "index.yaml")
    categories["categories"][1]["skills"].append("arxiv")
    _write_yaml(path, categories)
    with pytest.raises(ValueError, match="multiple categories: arxiv"):
        build_catalog(repository)


def test_catalog_rejects_unknown_consolidation_replacement(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    registry["consolidations"][0]["replacement"] = "not-active"
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="unknown consolidation replacement"):
        build_catalog(repository)


def test_catalog_output_rejects_nonfinite_values() -> None:
    catalog = build_catalog(ROOT)
    catalog["skills"][0]["version"] = float("nan")

    with pytest.raises(ValueError, match="non-finite"):
        catalog_json_bytes(catalog)
