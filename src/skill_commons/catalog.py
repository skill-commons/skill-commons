"""Generate human and machine catalogs from federated source records."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .io import json_safe, load_yaml_file

REGISTRY_SCHEMA_VERSION = "1.0"
CATEGORY_SCHEMA_VERSION = "1.0"
CATALOG_SCHEMA_VERSION = "2.0"
NAME_RE = re.compile(r"[a-z][a-z0-9_-]{0,63}")
RESERVED_NAMES = {"index", "readme", "skill", "unnamed-skill"}
CATEGORY_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
GIT_SHA_RE = re.compile(r"[0-9a-f]{40}")
BRANCH_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,254}")
SOURCE_PATH_RE = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")
GITHUB_REPOSITORY_RE = re.compile(
    r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9._-]{1,100})"
)


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    return value


def _list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{context} must be a list")
    return value


def _string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be a non-empty string")
    return value.strip()


def _name(value: Any, context: str) -> str:
    name = _string(value, context)
    if not NAME_RE.fullmatch(name) or name in RESERVED_NAMES:
        raise ValueError(f"{context} is not a Hermes-compatible skill name: {name!r}")
    return name


def _github_repository(value: Any, context: str) -> tuple[str, str, str]:
    repository = _string(value, context).rstrip("/").removesuffix(".git")
    match = GITHUB_REPOSITORY_RE.fullmatch(repository)
    if not match:
        raise ValueError(f"{context} must be a canonical HTTPS GitHub repository URL")
    return repository, match.group(1), match.group(2)


def _source_path(value: Any, context: str) -> str:
    path = _string(value, context)
    if (
        not SOURCE_PATH_RE.fullmatch(path)
        or any(part in {".", ".."} for part in path.split("/"))
        or path.rsplit("/", 1)[-1] == "SKILL.md"
    ):
        raise ValueError(f"{context} must identify a safe repository-relative directory")
    return path


def _branch(value: Any, context: str) -> str:
    branch = _string(value, context)
    if (
        not BRANCH_RE.fullmatch(branch)
        or ".." in branch
        or "//" in branch
        or branch.endswith(("/", ".", ".lock"))
    ):
        raise ValueError(f"{context} is not a safe Git branch name")
    return branch


def _sha(value: Any, context: str) -> str:
    sha = _string(value, context)
    if not GIT_SHA_RE.fullmatch(sha):
        raise ValueError(f"{context} must be an exact lowercase 40-character Git SHA")
    return sha


def _load_registry(repository_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source = _mapping(load_yaml_file(repository_root / "registry" / "index.yaml"), "registry")
    if source.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise ValueError(f"registry/index.yaml schema_version must be {REGISTRY_SCHEMA_VERSION!r}")
    registry_url, _, _ = _github_repository(source.get("registry"), "registry/registry")
    provenance = _string(source.get("provenance"), "registry/provenance")

    records: list[dict[str, Any]] = []
    names: set[str] = set()
    locations: set[tuple[str, str]] = set()
    for index, raw_record in enumerate(_list(source.get("skills"), "registry/skills")):
        record = _mapping(raw_record, f"registry/skills/{index}")
        name = _name(record.get("name"), f"registry/skills/{index}/name")
        if name in names:
            raise ValueError(f"duplicate active skill name: {name}")
        names.add(name)
        status = _string(record.get("status"), f"registry/skills/{index}/status")
        if status != "active":
            raise ValueError(f"registry skill {name!r} has unsupported status {status!r}")
        source_record = _mapping(record.get("source"), f"registry/skills/{index}/source")
        repository, owner, repository_name = _github_repository(
            source_record.get("repository"),
            f"registry/skills/{index}/source/repository",
        )
        path = _source_path(
            source_record.get("path"),
            f"registry/skills/{index}/source/path",
        )
        location = (repository, path)
        if location in locations:
            raise ValueError(f"duplicate canonical source: {repository}/{path}")
        locations.add(location)
        branch = _branch(
            source_record.get("branch"),
            f"registry/skills/{index}/source/branch",
        )
        revision = _sha(
            source_record.get("revision"),
            f"registry/skills/{index}/source/revision",
        )
        tree = _sha(
            source_record.get("tree"),
            f"registry/skills/{index}/source/tree",
        )
        identifier = f"{owner}/{repository_name}/{path}"
        encoded_path = quote(path, safe="/")
        records.append(
            {
                "name": name,
                "description": _string(
                    record.get("description"),
                    f"registry/skills/{index}/description",
                ),
                "version": _string(
                    record.get("version"),
                    f"registry/skills/{index}/version",
                ),
                "status": status,
                "source": {
                    "repository": repository,
                    "branch": branch,
                    "revision": revision,
                    "tree": tree,
                    "path": path,
                    "url": f"{repository}/tree/{revision}/{encoded_path}",
                },
                "hermes": {
                    "identifier": identifier,
                    "install": f"hermes skills install {identifier}",
                },
            }
        )

    consolidations: list[dict[str, str]] = []
    retired: set[str] = set()
    for index, raw_item in enumerate(
        _list(source.get("consolidations", []), "registry/consolidations")
    ):
        item = _mapping(raw_item, f"registry/consolidations/{index}")
        name = _name(item.get("name"), f"registry/consolidations/{index}/name")
        replacement = _name(
            item.get("replacement"),
            f"registry/consolidations/{index}/replacement",
        )
        if name in names:
            raise ValueError(f"consolidated skill is still active: {name}")
        if name in retired:
            raise ValueError(f"duplicate consolidated skill: {name}")
        if replacement not in names:
            raise ValueError(f"unknown consolidation replacement: {replacement}")
        retired.add(name)
        consolidations.append(
            {
                "name": name,
                "replacement": replacement,
                "reason": _string(
                    item.get("reason"),
                    f"registry/consolidations/{index}/reason",
                ),
            }
        )
    metadata = {
        "registry": registry_url,
        "provenance": provenance,
        "consolidations": consolidations,
    }
    return metadata, records


def _load_categories(
    repository_root: Path,
    active_names: set[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    source = _mapping(
        load_yaml_file(repository_root / "categories" / "index.yaml"),
        "categories",
    )
    if source.get("schema_version") != CATEGORY_SCHEMA_VERSION:
        raise ValueError(
            f"categories/index.yaml schema_version must be {CATEGORY_SCHEMA_VERSION!r}"
        )
    categories: list[dict[str, Any]] = []
    category_ids: set[str] = set()
    assigned: set[str] = set()
    by_skill: dict[str, dict[str, str]] = {}
    for index, raw_category in enumerate(_list(source.get("categories"), "categories/categories")):
        category = _mapping(raw_category, f"categories/categories/{index}")
        category_id = _string(
            category.get("id"),
            f"categories/categories/{index}/id",
        )
        if not CATEGORY_ID_RE.fullmatch(category_id):
            raise ValueError(f"category id is not a portable slug: {category_id!r}")
        if category_id in category_ids:
            raise ValueError(f"duplicate category id: {category_id}")
        category_ids.add(category_id)
        name = _string(category.get("name"), f"categories/categories/{index}/name")
        description = _string(
            category.get("description"),
            f"categories/categories/{index}/description",
        )
        skill_names = [
            _name(value, f"categories/categories/{index}/skills")
            for value in _list(
                category.get("skills"),
                f"categories/categories/{index}/skills",
            )
        ]
        if not skill_names:
            raise ValueError(f"category {category_id!r} must contain at least one skill")
        for skill_name in skill_names:
            if skill_name not in active_names:
                raise ValueError(
                    f"category {category_id!r} references unknown active skill: {skill_name}"
                )
            if skill_name in assigned:
                raise ValueError(f"active skill appears in multiple categories: {skill_name}")
            assigned.add(skill_name)
            by_skill[skill_name] = {"id": category_id, "name": name}
        categories.append(
            {
                "id": category_id,
                "name": name,
                "description": description,
                "skills": skill_names,
            }
        )
    missing = sorted(active_names - assigned)
    if missing:
        raise ValueError(f"active skills missing from categories: {', '.join(missing)}")
    return categories, by_skill


def build_catalog(repository_root: Path) -> dict[str, Any]:
    """Build a deterministic catalog from registry records and editorial categories."""

    repository_root = repository_root.resolve(strict=True)
    metadata, records = _load_registry(repository_root)
    categories, category_by_skill = _load_categories(
        repository_root,
        {record["name"] for record in records},
    )
    for record in records:
        record["category"] = category_by_skill[record["name"]]
    return json_safe(
        {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "registry": metadata["registry"],
            "provenance": metadata["provenance"],
            "categories": categories,
            "consolidations": metadata["consolidations"],
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
    ).encode()


def render_readme(catalog: dict[str, Any]) -> str:
    lines = [
        "# Skill Commons",
        "",
        "Skill Commons is a federated discovery catalog for research skills. It records "
        "where each skill is maintained; it does not copy third-party skill content into "
        "this repository.",
        "",
        "The canonical skill bytes, references, scripts, history, and updates remain in "
        "their source repositories. The first Commons-maintained source is the "
        "[`curated-research-skills`](https://github.com/skill-commons/"
        "curated-research-skills) Hermes tap.",
        "",
        "## Use with Hermes",
        "",
        "Subscribe to the Commons-maintained tap:",
        "",
        "```bash",
        "hermes skills tap add skill-commons/curated-research-skills",
        "hermes skills search astronomy",
        "```",
        "",
        "Every table below also gives the explicit direct-install command. Hermes installs "
        "from the source repository's current default branch and records its resolved "
        "source and content hash locally.",
        "",
        "## Skills",
    ]
    records = {record["name"]: record for record in catalog["skills"]}
    for category in catalog["categories"]:
        lines.extend(
            [
                "",
                f"### {category['name']}",
                "",
                category["description"],
                "",
                "| Skill | Version | Description | Source | Install |",
                "|---|---:|---|---|---|",
            ]
        )
        for skill_name in category["skills"]:
            record = records[skill_name]
            description = record["description"].replace("|", "\\|")
            lines.append(
                f"| [`{skill_name}`]({record['source']['url']}) "
                f"| `{record['version']}` | {description} "
                f"| [pinned source]({record['source']['url']}) "
                f"| `{record['hermes']['install']}` |"
            )
    if catalog["consolidations"]:
        lines.extend(
            [
                "",
                "<details>",
                "<summary>Consolidated former skill names</summary>",
                "",
                "| Former skill | Use instead | Reason |",
                "|---|---|---|",
            ]
        )
        for item in catalog["consolidations"]:
            reason = item["reason"].replace("|", "\\|")
            lines.append(f"| `{item['name']}` | `{item['replacement']}` | {reason} |")
        lines.extend(["", "</details>"])
    lines.extend(
        [
            "",
            "## How the registry works",
            "",
            "- [`registry/index.yaml`](registry/index.yaml) records each canonical "
            "repository, path, tracked branch, last reviewed commit, and Git tree.",
            "- [`categories/index.yaml`](categories/index.yaml) supplies the human "
            "taxonomy. Categories are not Hermes installation units.",
            "- [`catalog/index.json`](catalog/index.json) is the generated machine view.",
            "- `skill-commons check-upstreams` compares the recorded directory trees with "
            "the tracked branches and reports upstream changes without copying them.",
            "",
            "The YAML files above are implementation data for this catalog, not a new "
            "skill-package standard. Source repositories use the formats understood by "
            "their clients; the Commons-maintained tap follows current Hermes conventions.",
            "",
            "See [`CONTRIBUTING.md`](CONTRIBUTING.md) to register or update a source and "
            "[`docs/FEDERATED_REGISTRY.md`](docs/FEDERATED_REGISTRY.md) for the architecture.",
            "",
        ]
    )
    return "\n".join(lines)


def catalog_outputs(catalog: dict[str, Any]) -> dict[Path, bytes]:
    return {
        Path("README.md"): render_readme(catalog).encode(),
        Path("catalog/index.json"): catalog_json_bytes(catalog),
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


def write_catalog(repository_root: Path, catalog: dict[str, Any], *, check: bool) -> bool:
    """Write generated views or report whether committed views are current."""

    outputs = catalog_outputs(catalog)
    if check:
        return all(
            (repository_root / path).is_file() and (repository_root / path).read_bytes() == payload
            for path, payload in outputs.items()
        )
    for path, payload in outputs.items():
        _atomic_replace(repository_root / path, payload)
    return True
