from __future__ import annotations

import copy

import jsonschema
import pytest

from skill_commons.catalog import build_catalog_snapshot


def release_record():
    return {
        "coordinate": "example/catalog-query-demo",
        "version": "1.0.0",
        "artifact": {
            "repository": "registry.example.invalid/skills/catalog-query-demo",
            "digest": "sha256:" + "1" * 64,
            "media_type": "application/vnd.skill-commons.package.v1+tar+gzip",
            "size": 1234,
        },
        "manifest_digest": "sha256:" + "2" * 64,
        "source": {
            "repository": "https://example.invalid/skill-commons/spec",
            "revision": "3" * 40,
            "path": "examples/catalog-query-demo",
        },
        "release_state": "active",
        "description": "Synthetic catalog fixture.",
        "license": "MIT",
        "compatibility": {},
        "capability_summary": {},
        "context_budget": {
            "metadata_tokens": 20,
            "instruction_tokens": 80,
            "estimator": "fixture",
            "version": "1",
            "encoding": "approximate-whitespace",
        },
        "assessments": {
            "license": "verified",
            "publisher_authority": "verified",
            "namespace_control": "verified",
            "redaction": "verified",
            "source_relation": "native",
        },
        "assessment_evidence": {
            "license": "sha256:" + "5" * 64,
            "publisher_authority": "sha256:" + "6" * 64,
            "namespace_control": "sha256:" + "7" * 64,
            "redaction": "sha256:" + "8" * 64,
        },
        "validation_profiles": {"commons-publication": "pass"},
        "evidence": ["sha256:" + "4" * 64],
    }


def test_catalog_snapshot_is_deterministic() -> None:
    kwargs = {
        "sequence": 1,
        "generated_at": "2026-07-20T00:00:00Z",
        "expires_at": "2026-07-27T00:00:00Z",
        "previous_snapshot_digest": None,
        "negative_sequence": 0,
        "negative_records": [],
    }
    assert build_catalog_snapshot([release_record()], **kwargs) == build_catalog_snapshot(
        [release_record()], **kwargs
    )


def catalog_kwargs() -> dict:
    return {
        "sequence": 1,
        "generated_at": "2026-07-20T00:00:00Z",
        "expires_at": "2026-07-27T00:00:00Z",
        "previous_snapshot_digest": None,
        "negative_sequence": 0,
        "negative_records": [],
    }


def test_catalog_rejects_duplicate_release_and_negative_identities() -> None:
    release = release_record()
    with pytest.raises(ValueError, match="duplicate catalog identity"):
        build_catalog_snapshot([release, copy.deepcopy(release)], **catalog_kwargs())

    negative = {
        "kind": "yank",
        "coordinate": "example/catalog-query-demo",
        "version": "1.0.0",
        "record_digest": "sha256:" + "5" * 64,
    }
    kwargs = catalog_kwargs()
    kwargs["negative_records"] = [negative, copy.deepcopy(negative)]
    with pytest.raises(ValueError, match="duplicate catalog identity"):
        build_catalog_snapshot([], **kwargs)


def test_catalog_rejects_invalid_chain_and_time_window() -> None:
    kwargs = catalog_kwargs()
    kwargs["expires_at"] = kwargs["generated_at"]
    with pytest.raises(ValueError, match="later"):
        build_catalog_snapshot([], **kwargs)

    kwargs = catalog_kwargs()
    kwargs["sequence"] = 2
    with pytest.raises(ValueError, match="previous_snapshot_digest"):
        build_catalog_snapshot([], **kwargs)


def test_catalog_assembler_rejects_unverified_publisher_input() -> None:
    release = release_record()
    release["assessments"]["publisher_authority"] = "asserted"
    with pytest.raises(jsonschema.ValidationError):
        build_catalog_snapshot([release], **catalog_kwargs())


@pytest.mark.parametrize("license_value", ["", "NOASSERTION", "not-an-spdx-license"])
def test_catalog_rejects_unpublishable_license_conclusions(license_value: str) -> None:
    release = release_record()
    release["license"] = license_value
    with pytest.raises((ValueError, jsonschema.ValidationError)):
        build_catalog_snapshot([release], **catalog_kwargs())


def test_catalog_rejects_malformed_nested_record_without_traceback() -> None:
    release = release_record()
    release["assessments"] = []
    with pytest.raises(jsonschema.ValidationError):
        build_catalog_snapshot([release], **catalog_kwargs())
