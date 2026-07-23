"""Deterministic Git-native catalog generation from published skill directories."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .io import json_safe, load_yaml_file, parse_skill, semantic_digest, sha256_bytes
from .packer import SnapshotEntry, snapshot_tree

CATALOG_SCHEMA_VERSION = "1.0"


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


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
    return json_safe(
        {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "repository": repository,
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
        "Git and the package directories remain authoritative.",
        "",
        "| Skill | Version | Description | Status |",
        "|---|---:|---|---|",
    ]
    for record in catalog["skills"]:
        description = record["description"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| [`{record['coordinate']}`](../{record['path']}/) "
            f"| `{record['version']}` | {description} | {record['status']} |"
        )
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
