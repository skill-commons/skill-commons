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
    assert first["schema_version"] == "3.0"
    assert first["registry"] == "https://github.com/skill-commons/skill-commons"
    assert len(first["skills"]) == 23
    assert [category["name"] for category in first["categories"]] == [
        "General",
        "LaTeX",
        "Astronomy",
        "Data",
        "Visualization",
        "Scientific Computing",
        "Software Development",
    ]
    records = {record["name"]: record for record in first["skills"]}
    starhorse = records["starhorse-access"]
    assert starhorse["category"] == {"id": "astronomy", "name": "Astronomy"}
    assert starhorse["source"]["revision"] == ("38abb15a603dbc7a36efc83fcb82abe719c13ee8")
    assert starhorse["source"]["path"] == "skills/starhorse-access"
    assert starhorse["source"]["url"].endswith(
        "/tree/38abb15a603dbc7a36efc83fcb82abe719c13ee8/skills/starhorse-access"
    )
    assert starhorse["hermes"]["identifier"] == (
        "skill-commons/curated-research-skills/skills/starhorse-access"
    )
    assert starhorse["review"]["maturity"] == "curated"
    assert starhorse["review"]["policy"] == "skill-commons-review-v1"
    assert starhorse["review"]["decision"] == ("registry/reviews/2026-08-06-crs-seed.md")
    assert starhorse["review"]["evidence"]["scientific_validity"] == ("scope-documented")
    vamdc = records["vamdc"]
    assert vamdc["category"] == {"id": "astronomy", "name": "Astronomy"}
    assert vamdc["review"]["maturity"] == "community"
    assert vamdc["review"]["evidence"]["maintenance"] == "maintainer-confirmed"
    assert vamdc["source"]["revision"] == ("bfefc812782d055c5f54c6105a394d6d34e13815")
    assert vamdc["source"]["tree"] == ("7db98d33cc99a8ae220f1585f69d49d15a04bf4c")
    assert vamdc["source"]["path"] == "skill"
    expected_wave1 = {
        "large-tabular-visualization": (
            "visualization",
            "9907635e20d07c982a8761bff3882b06f2b902fd",
        ),
        "rss-feed-monitor": (
            "general",
            "cb59f3968c6bad42e21e076b3696d5395bb21087",
        ),
        "dt4acc-host-smoke-test": (
            "scientific-computing",
            "125e2df89f58adc92bd6e5cf0f79d34a3561a60a",
        ),
        "python-library-docs-first": (
            "software-development",
            "50d2b3d6d03c6ca8855bab0e2b563f1bbf5f3849",
        ),
    }
    for name, (category_id, tree) in expected_wave1.items():
        assert records[name]["category"]["id"] == category_id
        assert records[name]["source"]["tree"] == tree

    expected_wave2 = {
        "research-paper-evidence-workflow": (
            "general",
            "e22a48e40523c6d2770d9258a5599da7d3d75e81",
        ),
        "reana-workflow-authoring": (
            "scientific-computing",
            "11c0977e59f7a2af9cda76d8f41aefcefe05ac3d",
        ),
    }
    for name, (category_id, tree) in expected_wave2.items():
        assert records[name]["category"]["id"] == category_id
        assert records[name]["source"]["revision"] == ("8a2b3fa36e89b51517d9efccf2bbcea6ab6c1e4e")
        assert records[name]["source"]["tree"] == tree

    expected_wave3 = {
        "drphub-products": (
            "data",
            "cf1f55bbc120383e1313a6f9bbcf24a69dbfc3bb",
        ),
        "dt4acc-operations": (
            "scientific-computing",
            "d1c9da7dbf3a344786604d06677d69ca97378f98",
        ),
        "reana-operator": (
            "scientific-computing",
            "53e58285d6b0b689c9e571d8108e762f467d03b9",
        ),
    }
    for name, (category_id, tree) in expected_wave3.items():
        assert records[name]["category"]["id"] == category_id
        assert records[name]["source"]["revision"] == ("d5f096ee426dbbbea885bfb5199e8b7070960a1a")
        assert records[name]["source"]["tree"] == tree

    expected_wave4 = {
        "jubik-bootstrap": "be5008c4d907fc09f7979b6df53a5130ca867821",
        "nifty-re-variational-inference": "eb2bd3b810e3060aa197d99794785021d4196670",
    }
    for name, tree in expected_wave4.items():
        assert records[name]["category"]["id"] == "scientific-computing"
        assert records[name]["source"]["revision"] == ("4f63c019b3d05fe72501c706fbe69d105f9fb643")
        assert records[name]["source"]["tree"] == tree


def test_readme_contains_every_skill_description_source_and_install() -> None:
    catalog = build_catalog(ROOT)
    readme = render_readme(catalog)

    for record in catalog["skills"]:
        assert f"`{record['name']}`" in readme
        assert record["description"] in readme
        assert record["source"]["url"] in readme
        assert record["hermes"]["install"] in readme
        assert record["review"]["maturity"] in readme
        assert record["review"]["decision"] in readme


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


def test_catalog_rejects_unreviewed_active_skill(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    registry["skills"][0]["review"]["maturity"] = "unreviewed"
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="community, curated, reviewed"):
        build_catalog(repository)


def test_catalog_rejects_incomplete_or_unknown_review_evidence(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    evidence = registry["skills"][0]["review"]["evidence"]
    del evidence["rights"]
    evidence["popularity"] = "high"
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="evidence must contain exactly"):
        build_catalog(repository)


def test_catalog_rejects_unquoted_review_date(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    text = path.read_text(encoding="utf-8").replace(
        'assessed_at: "2026-07-28"',
        "assessed_at: 2026-07-28",
        1,
    )
    path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="assessed_at must be a non-empty string"):
        build_catalog(repository)


@pytest.mark.parametrize(
    "decision",
    [
        "../reviews/decision.md",
        "registry/reviews/nested/decision.md",
        "registry/reviews/missing.md",
        r"registry\reviews\decision.md",
    ],
)
def test_catalog_rejects_unsafe_or_missing_review_decision(
    tmp_path: Path,
    decision: str,
) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    registry["skills"][0]["review"]["decision"] = decision
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="decision must"):
        build_catalog(repository)


def test_catalog_requires_limitations_for_unassessed_evidence(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = repository / "registry" / "index.yaml"
    registry = _yaml(path)
    review = registry["skills"][0]["review"]
    review["evidence"]["scientific_validity"] = "not-assessed"
    review["limitations"] = []
    _write_yaml(path, registry)

    with pytest.raises(ValueError, match="must explain unassessed or stale evidence"):
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
