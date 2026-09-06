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
    assert len(first["skills"]) == 26
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
    assert starhorse["source"]["path"] == "skills/starhorse-access"
    assert starhorse["hermes"]["identifier"] == (
        "skill-commons/curated-research-skills/skills/starhorse-access"
    )
    assert starhorse["review"]["maturity"] == "curated"
    assert starhorse["review"]["policy"] == "skill-commons-review-v1"
    assert starhorse["review"]["evidence"]["scientific_validity"] == ("scope-documented")
    vamdc = records["vamdc"]
    assert vamdc["category"] == {"id": "astronomy", "name": "Astronomy"}
    assert vamdc["review"]["maturity"] == "community"
    assert vamdc["review"]["evidence"]["maintenance"] == "maintainer-confirmed"
    assert vamdc["source"]["revision"] == ("bfefc812782d055c5f54c6105a394d6d34e13815")
    assert vamdc["source"]["tree"] == ("7db98d33cc99a8ae220f1585f69d49d15a04bf4c")
    assert vamdc["source"]["path"] == "skill"


def test_catalog_records_crs_python_environment_update() -> None:
    catalog = build_catalog(ROOT)
    revision = "74a11aaad374108c60162e879390ee3604efddd1"
    repository = "https://github.com/skill-commons/curated-research-skills"
    decision = "registry/reviews/2026-08-11-crs-python-environments.md"
    expected = {
        "astro-catalog-plotting-cache": (
            "2.0.1",
            "astronomy",
            "5cf29a2fb99eb5a37bc634adfd10fd8473b0e5dd",
        ),
        "calculator": (
            "1.0.2",
            "general",
            "6cca9161ab486fc1d156b29bdfc77381bf5be001",
        ),
        "data-aip-de-s3": (
            "2.0.1",
            "data",
            "781fd0f4671557bffab222bb5a1ea2213ec43117",
        ),
        "seaborn-paper-plots": (
            "1.0.2",
            "visualization",
            "17f845f49c24513c22c47e0caba5f8359852cdf7",
        ),
        "starhorse-access": (
            "2.0.3",
            "astronomy",
            "7a01d8773322cd90be85dcd4dfd66d76cdc93e58",
        ),
        "tap-pyvo-adql-access": (
            "1.0.1",
            "astronomy",
            "16605f835e35c0186e99f762daee5daedeff0df3",
        ),
    }
    records = {
        record["name"]: record
        for record in catalog["skills"]
        if record["source"]["repository"] == repository and record["source"]["revision"] == revision
    }

    assert {
        name: (record["version"], record["category"]["id"], record["source"]["tree"])
        for name, record in records.items()
    } == expected
    for name, record in records.items():
        assert record["source"]["path"] == f"skills/{name}"
        assert record["source"]["url"].endswith(f"/tree/{revision}/skills/{name}")
        assert record["review"]["assessed_at"] == "2026-08-11"
        assert record["review"]["decision"] == decision
        assert any(
            "transitive dependencies are not locked" in limitation
            for limitation in record["review"]["limitations"]
        )


def test_catalog_records_gaia_rave_spectrum_update() -> None:
    catalog = build_catalog(ROOT)
    revision = "607b1963d4ea0def94de8e259f5a7315f2e54aa5"
    repository = "https://github.com/skill-commons/curated-research-skills"
    decision = "registry/reviews/2026-09-05-gaia-rave-spectra.md"
    expected = {
        "gaia-dr3-tap-query": (
            "3.1.1",
            "2fd8e4fdde6a8c599f9dd9487204c62e75b89460",
            "Query Gaia DR3 catalogs and spectra at AIP.",
        ),
        "rave-dr6": (
            "2.1.1",
            "47b11565545857c2478f5137b0f0f4aefabd738b",
            "Query and plot public RAVE DR6 spectra and catalogs.",
        ),
    }
    records = {
        record["name"]: record
        for record in catalog["skills"]
        if record["source"]["repository"] == repository and record["source"]["revision"] == revision
    }

    assert {
        name: (record["version"], record["source"]["tree"], record["description"])
        for name, record in records.items()
    } == expected
    for name, record in records.items():
        assert record["source"]["branch"] == "main"
        assert record["source"]["path"] == f"skills/{name}"
        assert record["source"]["url"].endswith(f"/tree/{revision}/skills/{name}")
        assert record["category"] == {"id": "astronomy", "name": "Astronomy"}
        assert record["review"]["maturity"] == "curated"
        assert record["review"]["assessed_at"] == "2026-09-05"
        assert record["review"]["decision"] == decision
        assert record["review"]["evidence"]["scientific_validity"] == "scope-documented"
        assert any(
            "transitive dependencies are not locked" in limitation
            for limitation in record["review"]["limitations"]
        )
        assert any(
            "Live spectrum checks cover one demonstration" in limitation
            for limitation in record["review"]["limitations"]
        )


def test_catalog_records_coseecat_exact_source_and_scoped_review() -> None:
    records = {record["name"]: record for record in build_catalog(ROOT)["skills"]}
    record = records["coseecat"]
    assert record["version"] == "1.0.0"
    assert record["description"] == "Query solar electron events and plots from CoSEE-Cat."
    assert record["category"] == {"id": "astronomy", "name": "Astronomy"}
    source = record["source"]
    assert source["repository"] == "https://github.com/skill-commons/curated-research-skills"
    assert source["branch"] == "main"
    assert source["revision"] == "684f4e5301123cc614082373dea304c1fdf43937"
    assert source["tree"] == "3236a546c437d66022b3dc7597e3940b2cd3c123"
    assert source["path"] == "skills/coseecat"
    assert record["review"]["maturity"] == "curated"
    assert record["review"]["decision"] == "registry/reviews/2026-09-06-coseecat.md"
    assert record["review"]["evidence"]["scientific_validity"] == "scope-documented"
    assert record["review"]["evidence"]["reproducibility"] == "tested"
    assert record["review"]["limitations"]


def test_catalog_records_pepsi_spectra_source_and_scoped_review() -> None:
    records = {record["name"]: record for record in build_catalog(ROOT)["skills"]}
    pepsi = records["pepsi-spectra"]
    revision = "5e368912f83725338ee6835076beb8304824baeb"
    assert pepsi["version"] == "1.0.0"
    assert pepsi["description"] == "Retrieve and plot public PEPSI stellar spectra."
    assert pepsi["category"] == {"id": "astronomy", "name": "Astronomy"}
    assert pepsi["source"]["repository"] == (
        "https://github.com/skill-commons/curated-research-skills"
    )
    assert pepsi["source"]["branch"] == "main"
    assert pepsi["source"]["revision"] == revision
    assert pepsi["source"]["path"] == "skills/pepsi-spectra"
    assert pepsi["source"]["tree"] == "2d524aaac026be4f9d8c28dfa59ce65a372fd881"
    assert pepsi["source"]["url"].endswith(f"/tree/{revision}/skills/pepsi-spectra")
    review = pepsi["review"]
    assert review["maturity"] == "curated"
    assert review["assessed_at"] == "2026-09-06"
    assert review["decision"] == "registry/reviews/2026-09-06-pepsi-spectra.md"
    assert review["evidence"]["scientific_validity"] == "scope-documented"
    assert any("Mask polarity is undocumented" in item for item in review["limitations"])
    assert any("transitive dependencies are not locked" in item for item in review["limitations"])


def test_catalog_records_crs_hermes_selection_lead_update() -> None:
    catalog = build_catalog(ROOT)
    revision = "dccccb8a1bb3926de04e00e630d0a455cc9579a9"
    repository = "https://github.com/skill-commons/curated-research-skills"
    decision = "registry/reviews/2026-08-11-crs-hermes-selection-leads.md"
    expected = {
        "drphub-products": (
            "1.0.1",
            "data",
            "dbb4356b6ab299ab177f3d4f66c0a41fcd78629d",
            "Inspect Digital Research Product Hub products and health.",
        ),
        "dt4acc-host-smoke-test": (
            "2.0.1",
            "scientific-computing",
            "5efbf09fd153539add371201fd8e2de251103bf5",
            "Smoke-test local dt4acc checkouts without any containers.",
        ),
        "dt4acc-operations": (
            "1.0.1",
            "scientific-computing",
            "2b4377cf1b9c75be692ae7b3631117b16bbac8f4",
            "Operate local dt4acc simulations from digest-pinned SIFs.",
        ),
        "jubik-bootstrap": (
            "1.0.1",
            "scientific-computing",
            "816e1e48f21a7b9adf0c2f2a3f04b676cd03a6ef",
            "Bootstrap a pinned J-UBIK CPU core and verify readiness.",
        ),
        "large-tabular-visualization": (
            "2.0.2",
            "visualization",
            "90bad822b9cd3b05748cf51e1e9b0bbd5e8773a1",
            "Visualize large tabular data with hvPlot and Datashader.",
        ),
        "nifty-re-variational-inference": (
            "1.0.1",
            "scientific-computing",
            "44e43748e039251818b60f3a8706eb767f2f1c87",
            "Run bounded Bayesian variational inference with NIFTy.re.",
        ),
        "python-library-docs-first": (
            "2.0.1",
            "software-development",
            "77bb31cb83e9d3ec0ed531aecaa4db8da8e5fe9a",
            "Verify Python APIs against version-matched documentation.",
        ),
        "reana-operator": (
            "1.0.1",
            "scientific-computing",
            "10247fefc562cbebe5f3169a1d3e837af315e1e8",
            "Inspect remote REANA workflows using read-only commands.",
        ),
        "reana-workflow-authoring": (
            "1.0.1",
            "scientific-computing",
            "777eca16d210c1f222de4b85374330d95e24f18f",
            "Author and validate local REANA Serial workflow projects.",
        ),
        "research-paper-evidence-workflow": (
            "1.0.1",
            "general",
            "101363fc87305fc256d7d0df8599262190cd05b9",
            "Map research-paper claims to evidence; audit draft scope.",
        ),
        "rss-feed-monitor": (
            "2.0.1",
            "general",
            "8140059b198afe0666c7315fb3c4539b541f97a4",
            "Monitor RSS and Atom feeds in an isolated local database.",
        ),
    }
    records = {
        record["name"]: record
        for record in catalog["skills"]
        if record["source"]["repository"] == repository and record["source"]["revision"] == revision
    }

    assert {
        name: (
            record["version"],
            record["category"]["id"],
            record["source"]["tree"],
            record["description"].split(". ", 1)[0] + ".",
        )
        for name, record in records.items()
    } == expected
    for name, record in records.items():
        selection_lead = expected[name][3]
        assert len(selection_lead) <= 57
        assert record["description"].startswith(selection_lead)
        assert record["source"]["path"] == f"skills/{name}"
        assert record["source"]["url"].endswith(f"/tree/{revision}/skills/{name}")
        assert record["review"]["maturity"] == "curated"
        assert record["review"]["assessed_at"] == "2026-08-11"
        assert record["review"]["decision"] == decision
        assert any(
            "advisory lead check does not guarantee model selection" in limitation
            for limitation in record["review"]["limitations"]
        )


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


def test_catalog_records_drphub_cards_exact_source_and_admission_scope() -> None:
    records = {record["name"]: record for record in build_catalog(ROOT)["skills"]}
    record = records["drphub-cards"]
    assert record["version"] == "2.1.3"
    assert record["category"] == {"id": "data", "name": "Data"}
    assert record["source"]["revision"] == "b6d62b41f4ba9bc7a2355f1f38ec0a3071a7fac5"
    assert record["source"]["tree"] == "9ed2b00b8ffcd23815bd9b1028f42f5c659cbce3"
    assert record["source"]["path"] == "skills/drphub-cards"
    assert record["review"]["maturity"] == "community"
    assert record["review"]["decision"] == "registry/reviews/2026-09-06-drphub-cards.md"
    assert record["review"]["limitations"]
    assert records["drphub-products"]["source"]["tree"] == (
        "dbb4356b6ab299ab177f3d4f66c0a41fcd78629d"
    )
