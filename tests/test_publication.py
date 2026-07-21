from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from skill_commons.io import load_yaml_file
from skill_commons.publication import (
    _build_lock,
    _safe_relative,
    finalize_catalog,
    verify_published_release,
)

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "releases/aip/starhorse-access/2.0.2/publication.yaml"


@pytest.mark.parametrize("value", ["../escape", "/absolute", "C:/drive", "a\\b", ""])
def test_publication_rejects_unsafe_relative_paths(value: str) -> None:
    with pytest.raises(ValueError, match="unsafe release path"):
        _safe_relative(value)


def test_starhorse_lock_binds_manifest_and_selected_wheels() -> None:
    recipe = load_yaml_file(RECIPE)
    lock = _build_lock(recipe, recipe["manifest"], RECIPE.parent)
    resolution = lock["resolutions"][0]

    assert resolution["target"] == {
        "operating_system": "linux",
        "architecture": "amd64",
        "python_implementation": "cpython",
        "python_version": "3.12",
    }
    assert {item["name"] for item in resolution["python"] if item["direct"]} == {
        "fsspec",
        "pandas",
        "pyarrow",
        "pyvo",
        "requests",
    }
    assert all(len(item["artifact"]["sha256"]) == 64 for item in resolution["python"])


def test_finalize_catalog_binds_live_evidence_descriptors(tmp_path: Path) -> None:
    recipe = load_yaml_file(RECIPE)
    prepared = tmp_path / "prepared"
    (prepared / "evidence").mkdir(parents=True)
    (prepared / "prepare-receipt.json").write_text(
        json.dumps(
            {
                "artifact": {"size": 12345},
                "manifest_digest": "sha256:" + "1" * 64,
                "validation_status": {
                    "agent-skills": "pass",
                    "commons-publication": "warn",
                },
            }
        )
    )
    (prepared / "evidence/inventory.json").write_text(
        json.dumps(
            {
                "context_budget": {
                    "metadata_tokens": 12,
                    "instruction_tokens": 345,
                    "estimator": "fixture",
                    "version": "1",
                    "encoding": "utf-8",
                }
            }
        )
    )
    output = tmp_path / "final"
    subject = "sha256:" + "2" * 64
    signature = "sha256:" + "3" * 64
    attestation = "sha256:" + "4" * 64

    status = finalize_catalog(
        RECIPE,
        prepared,
        recipe["registry"]["primary"],
        subject,
        signature,
        attestation,
        output,
    )

    catalog = json.loads((output / "catalog.json").read_text())
    release = catalog["releases"][0]
    assert release["artifact"]["digest"] == subject
    assert release["evidence"] == [signature, attestation]
    assert status["open_gates"] == [4, 5]
    assert status["evidence_tags"] == {
        f"sha256-{'2' * 64}.sig": signature,
        f"sha256-{'2' * 64}.att": attestation,
    }


def test_verify_release_checks_catalog_live_evidence_package_and_mirror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    published = RECIPE.parent / "published"
    catalog = json.loads((published / "catalog.json").read_text())
    release = catalog["releases"][0]
    subject_digest = release["artifact"]["digest"]
    repository = release["artifact"]["repository"]
    prefix = f"sha256-{subject_digest[7:]}"
    status = json.loads((published / "publication-status.json").read_text())
    evidence = status["evidence_tags"]
    package = b"verified fixture package bytes"
    receipt = tmp_path / "prepare-receipt.json"
    receipt.write_text(
        json.dumps(
            {
                "artifact": {
                    "path": "starhorse-access-2.0.2.tar.gz",
                    "digest": "sha256:" + hashlib.sha256(package).hexdigest(),
                }
            }
        )
    )
    mirror = "registry.example.invalid/mirror/starhorse-access"
    calls: list[tuple[str, ...]] = []

    def fake_run(*arguments: str) -> str:
        calls.append(arguments)
        if arguments[:2] == ("oras", "resolve"):
            reference = arguments[2]
            if reference.endswith(":rel-2.0.2"):
                return subject_digest
            if reference.endswith(f":{prefix}.sig"):
                return evidence[f"{prefix}.sig"]
            if reference.endswith(f":{prefix}.att"):
                return evidence[f"{prefix}.att"]
        if arguments[:2] == ("oras", "pull"):
            output = Path(arguments[arguments.index("-o") + 1])
            (output / "starhorse-access-2.0.2.tar.gz").write_bytes(package)
        return ""

    monkeypatch.setattr("skill_commons.publication._run_checked", fake_run)
    report = verify_published_release(
        published / "catalog.json",
        published / "catalog.sig",
        published / "catalog.pub",
        receipt,
        "aip/starhorse-access",
        "2.0.2",
        mirror,
    )

    assert report["status"] == "pass"
    assert report["subject"] == {"repository": repository, "digest": subject_digest}
    assert report["mirror"] == {"repository": mirror, "status": "pass"}
    assert sum(call[:2] == ("cosign", "verify-attestation") for call in calls) == 14


def test_verify_release_rejects_future_catalog_before_registry_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    published = RECIPE.parent / "published"
    monkeypatch.setattr("skill_commons.publication._run_checked", lambda *arguments: "")

    with pytest.raises(ValueError, match="future"):
        verify_published_release(
            published / "catalog.json",
            published / "catalog.sig",
            published / "catalog.pub",
            published / "prepare-receipt.json",
            "aip/starhorse-access",
            "2.0.2",
            None,
            now=datetime(2026, 7, 21, 21, 0, tzinfo=UTC),
        )
