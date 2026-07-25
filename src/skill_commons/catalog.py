"""Deterministic Git-native catalog generation from published skill directories."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .io import json_safe, load_yaml_file, parse_skill, semantic_digest, sha256_bytes
from .packer import SnapshotEntry, snapshot_tree

CATALOG_SCHEMA_VERSION = "1.1"
BUNDLE_SCHEMA_VERSION = "1.0"
BUNDLE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _load_curation(
    repository_root: Path,
    active_coordinates: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, dict[str, str]]]:
    path = repository_root / "bundles" / "index.yaml"
    if not path.is_file():
        raise ValueError(f"bundle index does not exist: {path}")
    source = _require_mapping(load_yaml_file(path), "bundles/index.yaml")
    if source.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        raise ValueError(f"bundles/index.yaml schema_version must be {BUNDLE_SCHEMA_VERSION!r}")

    bundles: list[dict[str, Any]] = []
    bundle_ids: set[str] = set()
    assigned: set[str] = set()
    bundle_by_coordinate: dict[str, dict[str, str]] = {}
    for index, raw_bundle in enumerate(_require_list(source.get("bundles"), "bundles")):
        bundle = _require_mapping(raw_bundle, f"bundles/{index}")
        bundle_id = _require_string(bundle.get("id"), f"bundles/{index}/id")
        if not BUNDLE_ID_RE.fullmatch(bundle_id):
            raise ValueError(f"bundle id is not a portable slug: {bundle_id!r}")
        if bundle_id in bundle_ids:
            raise ValueError(f"duplicate bundle id: {bundle_id}")
        bundle_ids.add(bundle_id)
        name = _require_string(bundle.get("name"), f"bundles/{index}/name")
        description = _require_string(
            bundle.get("description"),
            f"bundles/{index}/description",
        )
        coordinates = [
            _require_string(value, f"bundles/{index}/skills")
            for value in _require_list(bundle.get("skills"), f"bundles/{index}/skills")
        ]
        if not coordinates:
            raise ValueError(f"bundle {bundle_id!r} must contain at least one skill")
        for coordinate in coordinates:
            if coordinate not in active_coordinates:
                raise ValueError(
                    f"bundle {bundle_id!r} references unknown active skill: {coordinate}"
                )
            if coordinate in assigned:
                raise ValueError(f"active skill appears in multiple bundles: {coordinate}")
            assigned.add(coordinate)
            bundle_by_coordinate[coordinate] = {"id": bundle_id, "name": name}
        bundles.append(
            {
                "id": bundle_id,
                "name": name,
                "description": description,
                "skills": coordinates,
            }
        )

    missing = sorted(active_coordinates - assigned)
    if missing:
        raise ValueError(f"active skills missing from bundles: {', '.join(missing)}")

    consolidations: list[dict[str, str]] = []
    retired_coordinates: set[str] = set()
    for index, raw_consolidation in enumerate(
        _require_list(source.get("consolidations", []), "consolidations")
    ):
        consolidation = _require_mapping(raw_consolidation, f"consolidations/{index}")
        coordinate = _require_string(
            consolidation.get("coordinate"),
            f"consolidations/{index}/coordinate",
        )
        replacement = _require_string(
            consolidation.get("replacement"),
            f"consolidations/{index}/replacement",
        )
        reason = _require_string(
            consolidation.get("reason"),
            f"consolidations/{index}/reason",
        )
        if coordinate in active_coordinates:
            raise ValueError(f"consolidated skill is still active: {coordinate}")
        if coordinate in retired_coordinates:
            raise ValueError(f"duplicate consolidated skill: {coordinate}")
        if replacement not in active_coordinates:
            raise ValueError(f"consolidation replacement is not an active skill: {replacement}")
        retired_coordinates.add(coordinate)
        consolidations.append(
            {
                "coordinate": coordinate,
                "replacement": replacement,
                "reason": reason,
            }
        )

    return bundles, consolidations, bundle_by_coordinate


def package_tree_digest(entries: list[SnapshotEntry]) -> str:
    """Digest canonical paths, file bytes, and executable bits without an archive."""

    records = [
        {
            "path": entry.relative,
            "mode": "755" if entry.executable else "644",
            "digest": sha256_bytes(entry.data),
        }
        for entry in entries
    ]
    return semantic_digest(records)


def _skill_record(skill_dir: Path, repository_root: Path) -> dict[str, Any]:
    entries = snapshot_tree(skill_dir)
    frontmatter, _, _ = parse_skill(skill_dir)
    manifest = _require_mapping(
        load_yaml_file(skill_dir / "research-skill.yaml"),
        f"{skill_dir.name}/research-skill.yaml",
    )
    package = _require_mapping(manifest.get("package"), f"{skill_dir.name}/package")
    research = _require_mapping(manifest.get("research", {}), f"{skill_dir.name}/research")
    compatibility = _require_mapping(
        manifest.get("compatibility", {}),
        f"{skill_dir.name}/compatibility",
    )
    source = _require_mapping(package.get("source"), f"{skill_dir.name}/package/source")

    name = _require_string(package.get("name"), f"{skill_dir.name}/package/name")
    if name != skill_dir.name:
        raise ValueError(f"skill directory and package name differ: {skill_dir.name} != {name}")
    namespace = _require_string(package.get("namespace"), f"{name}/package/namespace")
    version = _require_string(package.get("version"), f"{name}/package/version")
    license_expression = _require_string(package.get("license"), f"{name}/package/license")
    if frontmatter.get("name") != name:
        raise ValueError(f"{name}/SKILL.md name differs from the sidecar")
    if frontmatter.get("license") != license_expression:
        raise ValueError(f"{name}/SKILL.md license differs from the sidecar")

    return {
        "coordinate": f"{namespace}/{name}",
        "name": name,
        "version": version,
        "description": _require_string(frontmatter.get("description"), f"{name}/description"),
        "license": license_expression,
        "path": skill_dir.relative_to(repository_root).as_posix(),
        "release_tag": f"skill/{name}/v{version}",
        "status": "active",
        "tree_digest": package_tree_digest(entries),
        "upstream": {
            "repository": _require_string(source.get("repository"), f"{name}/source/repository"),
            "revision": _require_string(source.get("revision"), f"{name}/source/revision"),
            "path": _require_string(source.get("path"), f"{name}/source/path"),
        },
        "research": {
            "disciplines": research.get("disciplines", []),
            "methods": research.get("methods", []),
            "keywords": research.get("keywords", []),
        },
        "compatibility": {
            "operating_systems": compatibility.get("operating_systems", []),
            "architectures": compatibility.get("architectures", []),
            "python": compatibility.get("python"),
        },
    }


def build_git_catalog(repository_root: Path, repository: str) -> dict[str, Any]:
    """Build a deterministic catalog from the complete directories under ``skills/``."""

    repository_root = repository_root.resolve(strict=True)
    skills_root = repository_root / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"skills directory does not exist: {skills_root}")
    repository = repository.removesuffix(".git").rstrip("/")
    if not repository.startswith("https://"):
        raise ValueError("catalog repository must be an HTTPS URL")

    skill_dirs = sorted(
        (path for path in skills_root.iterdir() if path.is_dir()),
        key=lambda path: path.name.encode("utf-8"),
    )
    records = [_skill_record(path, repository_root) for path in skill_dirs]
    coordinates = [record["coordinate"] for record in records]
    if len(coordinates) != len(set(coordinates)):
        raise ValueError("catalog contains duplicate Commons coordinates")
    bundles, consolidations, bundle_by_coordinate = _load_curation(
        repository_root,
        set(coordinates),
    )
    for record in records:
        record["bundle"] = bundle_by_coordinate[record["coordinate"]]
    return json_safe(
        {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "repository": repository,
            "bundles": bundles,
            "consolidations": consolidations,
            "skills": records,
        }
    )


def catalog_json_bytes(catalog: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            json_safe(catalog),
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def render_catalog_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# Skill catalog",
        "",
        "This index is generated from the complete, reviewed directories under "
        "[`skills/`](../skills/).",
        "The functional bundles are curated in [`bundles/index.yaml`](../bundles/index.yaml). "
        "Git and the package directories remain authoritative.",
    ]
    records = {record["coordinate"]: record for record in catalog["skills"]}
    for bundle in catalog["bundles"]:
        lines.extend(
            [
                "",
                f"## {bundle['name']}",
                "",
                bundle["description"],
                "",
                "| Skill | Version | Description |",
                "|---|---:|---|",
            ]
        )
        for coordinate in bundle["skills"]:
            record = records[coordinate]
            description = record["description"].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| [`{record['coordinate']}`](../{record['path']}/) "
                f"| `{record['version']}` | {description} |"
            )
    if catalog["consolidations"]:
        lines.extend(
            [
                "",
                "## Consolidated skills",
                "",
                "These former package coordinates are preserved as redirects in the catalog and "
                "in Git history; they are no longer independent skills.",
                "",
                "| Former skill | Use instead | Reason |",
                "|---|---|---|",
            ]
        )
        for item in catalog["consolidations"]:
            reason = item["reason"].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{item['coordinate']}` | `{item['replacement']}` | {reason} |")
    lines.extend(
        [
            "",
            "Machine-readable metadata: [`index.json`](index.json).",
            "",
        ]
    )
    return "\n".join(lines)


def catalog_outputs(catalog: dict[str, Any]) -> dict[str, bytes]:
    return {
        "index.json": catalog_json_bytes(catalog),
        "README.md": render_catalog_markdown(catalog).encode("utf-8"),
    }


def _atomic_replace(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_git_catalog(output_dir: Path, catalog: dict[str, Any], *, check: bool) -> bool:
    """Write the generated catalog, or return whether committed outputs are current."""

    outputs = catalog_outputs(catalog)
    if check:
        return all(
            (output_dir / name).is_file() and (output_dir / name).read_bytes() == payload
            for name, payload in outputs.items()
        )
    for name, payload in outputs.items():
        _atomic_replace(output_dir / name, payload)
    return True
