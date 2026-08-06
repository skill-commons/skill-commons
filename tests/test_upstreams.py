from __future__ import annotations

import copy
import json
from pathlib import Path

from skill_commons.catalog import build_catalog
from skill_commons.cli import main
from skill_commons.upstreams import check_upstreams

ROOT = Path(__file__).resolve().parents[1]


def _state(
    records: list[dict],
    *,
    default_branch: str = "main",
    current_revision: str = "f" * 40,
) -> dict:
    return {
        "requested_branch": "main",
        "default_branch": default_branch,
        "current_revision": current_revision,
        "current": {
            record["source"]["path"]: {
                "type": "tree",
                "tree": record["source"]["tree"],
            }
            for record in records
        },
        "observed": {
            (record["source"]["revision"], record["source"]["path"]): {
                "revision_found": True,
                "type": "tree",
                "tree": record["source"]["tree"],
                "metadata": {
                    "name": record["name"],
                    "description": record["description"],
                    "version": record["version"],
                },
            }
            for record in records
        },
    }


def test_upstream_checker_distinguishes_current_changed_and_missing(monkeypatch) -> None:
    catalog = build_catalog(ROOT)
    records = catalog["skills"]
    repository = "https://github.com/skill-commons/curated-research-skills"
    repository_records = [
        record for record in records if record["source"]["repository"] == repository
    ]
    state = _state(repository_records)
    state["current"][repository_records[1]["source"]["path"]]["tree"] = "0" * 40
    state["current"][repository_records[2]["source"]["path"]] = {"type": None, "tree": None}

    def fake_fetch(repository: str, branch: str, fetched_records: list[dict]):
        assert branch == "main"
        if repository == "https://github.com/skill-commons/curated-research-skills":
            assert fetched_records == repository_records
            return state
        return _state(fetched_records)

    monkeypatch.setattr("skill_commons.upstreams._fetch_git_state", fake_fetch)
    results = check_upstreams(catalog)
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses[repository_records[0]["name"]] == "current"
    assert statuses[repository_records[1]["name"]] == "changed"
    assert statuses[repository_records[2]["name"]] == "missing"


def test_upstream_checker_rejects_false_provenance_and_wrong_default(monkeypatch) -> None:
    catalog = build_catalog(ROOT)
    records = catalog["skills"]
    state = _state(records, default_branch="trunk")
    first_key = (records[0]["source"]["revision"], records[0]["source"]["path"])
    second_key = (records[1]["source"]["revision"], records[1]["source"]["path"])
    third_key = (records[2]["source"]["revision"], records[2]["source"]["path"])
    fourth_key = (records[3]["source"]["revision"], records[3]["source"]["path"])
    state["observed"][first_key]["revision_found"] = False
    state["observed"][second_key]["tree"] = "0" * 40
    state["observed"][third_key]["type"] = "blob"
    state["observed"][fourth_key]["metadata"]["description"] = "Wrong description"

    monkeypatch.setattr(
        "skill_commons.upstreams._fetch_git_state",
        lambda _repository, _branch, _records: state,
    )
    statuses = {result["name"]: result["status"] for result in check_upstreams(catalog)}

    assert statuses[records[0]["name"]] == "invalid-revision"
    assert statuses[records[1]["name"]] == "invalid-provenance"
    assert statuses[records[2]["name"]] == "invalid-source"
    assert statuses[records[3]["name"]] == "metadata-mismatch"
    assert statuses[records[4]["name"]] == "branch-mismatch"


def test_upstream_checker_detects_registry_metadata_mismatch(monkeypatch) -> None:
    catalog = build_catalog(ROOT)
    state = _state(catalog["skills"])
    record = catalog["skills"][0]
    key = (record["source"]["revision"], record["source"]["path"])
    state["observed"][key]["metadata"] = copy.deepcopy(state["observed"][key]["metadata"])
    state["observed"][key]["metadata"]["version"] = "999.0.0"

    monkeypatch.setattr(
        "skill_commons.upstreams._fetch_git_state",
        lambda _repository, _branch, _records: state,
    )
    result = next(result for result in check_upstreams(catalog) if result["name"] == record["name"])

    assert result["status"] == "metadata-mismatch"
    assert "registry version does not match" in result["issues"][0]


def test_upstream_cli_succeeds_when_skill_trees_are_unchanged(
    monkeypatch,
    capsys,
) -> None:
    catalog = build_catalog(ROOT)
    state = _state(catalog["skills"])
    monkeypatch.setattr(
        "skill_commons.upstreams._fetch_git_state",
        lambda _repository, _branch, _records: state,
    )

    assert main(["check-upstreams", "--root", str(ROOT), "--format", "json"]) == 0
    results = json.loads(capsys.readouterr().out)
    assert {result["status"] for result in results} == {"current"}
