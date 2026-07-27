"""Report-first conversion of legacy Hermes/Ori skill frontmatter."""

from __future__ import annotations

import base64
import copy
import difflib
import json
import math
import re
import shutil
import tempfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from . import __version__
from .io import (
    I_JSON_SAFE_INTEGER,
    dump_yaml,
    json_safe,
    parse_skill_text,
    semantic_digest,
    sha256_bytes,
)
from .model import Finding
from .packer import SnapshotEntry, snapshot_tree
from .validation import validate_agent_skills, validate_ori, validate_publication

SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
KNOWN_TOP_LEVEL = {
    "name",
    "description",
    "version",
    "author",
    "license",
    "prerequisites",
    "dependencies",
    "platforms",
    "metadata",
    "tags",
    "category",
    "related_skills",
}
KNOWN_HERMES = {
    "requires_toolsets",
    "requires_tools",
    "fallback_for_toolsets",
    "fallback_for_tools",
    "config",
    "tags",
    "category",
    "related_skills",
}
LEGACY_KEY_PREFIX = "$legacy-yaml-key:"


def _string_list(value: Any) -> list[str] | None:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return None


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _source_package_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or "\\" in value
        or ":" in value
        or path.as_posix() != value
    ):
        raise ValueError("source path must be a safe repository-relative package directory")
    if path.name == "SKILL.md":
        raise ValueError("source path names the package directory, not its SKILL.md file")
    return path.as_posix()


def _snapshot_digest(entries: list[SnapshotEntry]) -> str:
    return semantic_digest(
        [
            {
                "path": entry.relative,
                "digest": sha256_bytes(entry.data),
                "executable": entry.executable,
            }
            for entry in entries
        ]
    )


def _parse_snapshot(
    entries: list[SnapshotEntry],
) -> tuple[dict[str, Any], str, str, bytes]:
    skill_entry = next((entry for entry in entries if entry.relative == "SKILL.md"), None)
    if skill_entry is None:
        raise ValueError("source package has no root SKILL.md")
    fm, body, text = parse_skill_text(skill_entry.data.decode("utf-8"))
    return fm, body, text, skill_entry.data


def _legacy_json(value: Any) -> Any:
    """Preserve common YAML-native scalars explicitly in the JSON extension quarantine."""

    if isinstance(value, datetime):
        return {"$legacy_yaml_type": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"$legacy_yaml_type": "date", "value": value.isoformat()}
    if isinstance(value, bytes):
        return {
            "$legacy_yaml_type": "binary",
            "base64": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > I_JSON_SAFE_INTEGER:
        return {"$legacy_yaml_type": "unsafe-integer", "value": str(value)}
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            spelling = "nan"
        elif value > 0:
            spelling = "+infinity"
        else:
            spelling = "-infinity"
        return {"$legacy_yaml_type": "non-finite-float", "value": spelling}
    if isinstance(value, dict):
        if all(isinstance(key, str) for key in value):
            return {key: _legacy_json(item) for key, item in value.items()}
        return {
            "$legacy_yaml_type": "mapping",
            "entries": [
                {"key": _legacy_json(key), "value": _legacy_json(item)}
                for key, item in value.items()
            ],
        }
    if isinstance(value, list):
        return [_legacy_json(item) for item in value]
    if isinstance(value, tuple):
        return {
            "$legacy_yaml_type": "tuple",
            "items": [_legacy_json(item) for item in value],
        }
    if isinstance(value, set):
        return {
            "$legacy_yaml_type": "set",
            "items": [_legacy_json(item) for item in sorted(value, key=repr)],
        }
    return json_safe(value)


def _legacy_key_segment(key: Any) -> str:
    """Encode non-string or reserved-prefix YAML keys as collision-free JSON names."""

    if isinstance(key, str) and key and "." not in key and not key.startswith(LEGACY_KEY_PREFIX):
        return key
    encoded = json.dumps(
        _legacy_json(key),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    token = base64.urlsafe_b64encode(encoded).decode("ascii").rstrip("=")
    return LEGACY_KEY_PREFIX + token


def _legacy_source_path(prefix: str, key: Any) -> str:
    segment = _legacy_key_segment(key)
    return f"{prefix}.{segment}" if prefix else segment


def _sorted_legacy_keys(values: Any) -> list[Any]:
    return sorted(values, key=lambda value: _legacy_key_segment(value).encode("utf-8"))


def _leaf_fields(value: Any, prefix: str) -> list[tuple[str, Any]]:
    if isinstance(value, dict) and value:
        fields: list[tuple[str, Any]] = []
        for key in _sorted_legacy_keys(value):
            fields.extend(_leaf_fields(value[key], _legacy_source_path(prefix, key)))
        return fields
    return [(prefix, value)]


def _ensure_loss_accounting(
    fm: dict[str, Any],
    extension: dict[str, Any] | None,
    findings: list[Finding],
    dispositions: list[dict[str, str]],
) -> dict[str, Any] | None:
    existing_unmapped = (
        set(extension.get("data", {}).get("unmapped", {})) if extension is not None else set()
    )
    covered = {
        item["source"]
        for item in dispositions
        if item["disposition"] in {"copied", "normalized", "preserved", "proposed"}
        or item["source"] in existing_unmapped
    }
    missing = [
        (path, value)
        for path, value in _leaf_fields(fm, "")
        if not any(path == source or path.startswith(source + ".") for source in covered)
    ]
    if not missing:
        return extension
    if extension is None:
        extension = {
            "schema": "urn:skill-commons:extension:de.aip.ori:1",
            "required": False,
            "data": {},
        }
    unmapped = extension["data"].setdefault("unmapped", {})
    for path, value in missing:
        unmapped[path] = _legacy_json(value)
        findings.append(
            Finding(
                code="CONVERT_FIELD_UNMAPPED",
                profile="conversion",
                severity="blocker",
                message=f"legacy field {path!r} has no approved mapping",
                pointer="/extensions/de.aip.ori/data/unmapped",
                disposition="unmapped",
                source_field=path,
            )
        )
        dispositions.append(
            {
                "source": path,
                "target": "extensions.de.aip.ori.data.unmapped",
                "disposition": "unmapped",
            }
        )
    return extension


def _version(value: Any, findings: list[Finding], dispositions: list[dict[str, str]]) -> str:
    if value is None:
        findings.append(
            Finding(
                code="CONVERT_VERSION_ASSUMED",
                profile="conversion",
                severity="blocker",
                message="missing version represented as assumed 0.1.0",
                pointer="/package/version",
                disposition="proposed",
                source_field="version",
            )
        )
        dispositions.append(
            {"source": "version", "target": "package.version", "disposition": "proposed"}
        )
        return "0.1.0"
    text = str(value)
    if SEMVER_RE.fullmatch(text):
        dispositions.append(
            {"source": "version", "target": "package.version", "disposition": "copied"}
        )
        return text
    if re.fullmatch(r"[0-9]+\.[0-9]+", text):
        normalized = text + ".0"
        findings.append(
            Finding(
                code="CONVERT_VERSION_NORMALIZED",
                profile="conversion",
                severity="blocker",
                message=f"non-SemVer version {text!r} proposed as {normalized!r}",
                pointer="/package/version",
                disposition="proposed",
                source_field="version",
            )
        )
        dispositions.append(
            {"source": "version", "target": "package.version", "disposition": "proposed"}
        )
        return normalized
    findings.append(
        Finding(
            code="CONVERT_VERSION_INVALID",
            profile="conversion",
            severity="blocker",
            message=f"version {text!r} is not SemVer; placeholder 0.1.0 proposed",
            pointer="/package/version",
            disposition="conflict",
            source_field="version",
        )
    )
    dispositions.append(
        {"source": "version", "target": "package.version", "disposition": "conflict"}
    )
    return "0.1.0"


def _dependencies(
    fm: dict[str, Any], findings: list[Finding], dispositions: list[dict[str, str]]
) -> list[str]:
    prerequisites = fm.get("prerequisites")
    prereq_python: list[str] | None = []
    if prerequisites is not None and not isinstance(prerequisites, dict):
        findings.append(
            Finding(
                code="CONVERT_PREREQUISITES_TYPE",
                profile="conversion",
                severity="blocker",
                message="prerequisites has an unsupported type",
                pointer="/dependencies/python",
                disposition="unmapped",
                source_field="prerequisites",
            )
        )
    elif isinstance(prerequisites, dict) and not prerequisites:
        dispositions.append(
            {
                "source": "prerequisites",
                "target": "dependencies.python",
                "disposition": "normalized",
            }
        )
    elif isinstance(prerequisites, dict) and "python" in prerequisites:
        prereq_python = _string_list(prerequisites["python"])
        if prereq_python is None:
            findings.append(
                Finding(
                    code="CONVERT_PREREQUISITES_TYPE",
                    profile="conversion",
                    severity="blocker",
                    message="prerequisites.python has an unsupported type",
                    pointer="/dependencies/python",
                    disposition="unmapped",
                    source_field="prerequisites.python",
                )
            )
            prereq_python = []
        else:
            dispositions.append(
                {
                    "source": "prerequisites.python",
                    "target": "dependencies.python",
                    "disposition": "copied",
                }
            )
    dependency_python = _string_list(fm.get("dependencies")) if "dependencies" in fm else []
    if "dependencies" in fm and dependency_python is None:
        findings.append(
            Finding(
                code="CONVERT_DEPENDENCIES_TYPE",
                profile="conversion",
                severity="blocker",
                message="legacy dependencies has an unsupported shape",
                pointer="/dependencies/python",
                disposition="unmapped",
                source_field="dependencies",
            )
        )
        dependency_python = []
    elif "dependencies" in fm and not dependency_python:
        dispositions.append(
            {
                "source": "dependencies",
                "target": "dependencies.python",
                "disposition": "copied",
            }
        )
    elif dependency_python and not prereq_python:
        findings.append(
            Finding(
                code="CONVERT_INERT_DEPENDENCIES_BRIDGE",
                profile="conversion",
                severity="warning",
                message=(
                    "dependencies is inert in current Ori; bridge projection proposes "
                    "prerequisites.python"
                ),
                pointer="/dependencies/python",
                disposition="proposed",
                source_field="dependencies",
            )
        )
        dispositions.append(
            {
                "source": "dependencies",
                "target": "dependencies.python",
                "disposition": "normalized",
            }
        )
    elif dependency_python and prereq_python and dependency_python != prereq_python:
        findings.append(
            Finding(
                code="CONVERT_DEPENDENCY_CONFLICT",
                profile="conversion",
                severity="blocker",
                message=(
                    "dependencies and prerequisites.python disagree; prerequisites.python retained"
                ),
                pointer="/dependencies/python",
                disposition="conflict",
                source_field="dependencies",
            )
        )
        dispositions.append(
            {
                "source": "dependencies",
                "target": "dependencies.python",
                "disposition": "conflict",
            }
        )
    return _unique(prereq_python or dependency_python or [])


def _ori_extension(
    fm: dict[str, Any], findings: list[Finding], dispositions: list[dict[str, str]]
) -> dict[str, Any] | None:
    metadata = fm.get("metadata")
    hermes = metadata.get("hermes") if isinstance(metadata, dict) else None
    data: dict[str, Any] = {}
    unmapped: dict[str, Any] = {}
    if isinstance(hermes, dict):
        activation: dict[str, list[str]] = {}
        for key in sorted(
            {
                "requires_toolsets",
                "requires_tools",
                "fallback_for_toolsets",
                "fallback_for_tools",
            }
        ):
            if key not in hermes:
                continue
            value = _string_list(hermes[key])
            if value is None:
                findings.append(
                    Finding(
                        code="CONVERT_ORI_ACTIVATION_TYPE",
                        profile="conversion",
                        severity="blocker",
                        message=f"metadata.hermes.{key} has an unsupported type",
                        pointer=f"/extensions/de.aip.ori/data/activation/{key}",
                        disposition="unmapped",
                        source_field=f"metadata.hermes.{key}",
                    )
                )
                continue
            activation[key] = _unique(value)
            dispositions.append(
                {
                    "source": f"metadata.hermes.{key}",
                    "target": f"extensions.de.aip.ori.data.activation.{key}",
                    "disposition": "normalized",
                }
            )
        if activation:
            data["activation"] = activation
        if "config" in hermes:
            config = hermes["config"]
            if isinstance(config, list) and all(
                isinstance(item, dict) and isinstance(item.get("key"), str) for item in config
            ):
                try:
                    data["config"] = json_safe(config)
                except ValueError:
                    findings.append(
                        Finding(
                            code="CONVERT_ORI_CONFIG_NON_JSON",
                            profile="conversion",
                            severity="blocker",
                            message="metadata.hermes.config contains a non-JSON YAML value",
                            pointer="/extensions/de.aip.ori/data/unmapped",
                            disposition="unmapped",
                            source_field="metadata.hermes.config",
                        )
                    )
                else:
                    dispositions.append(
                        {
                            "source": "metadata.hermes.config",
                            "target": "extensions.de.aip.ori.data.config",
                            "disposition": "copied",
                        }
                    )
            else:
                findings.append(
                    Finding(
                        code="CONVERT_ORI_CONFIG_TYPE",
                        profile="conversion",
                        severity="blocker",
                        message="metadata.hermes.config has an unsupported shape",
                        pointer="/extensions/de.aip.ori/data/config",
                        disposition="unmapped",
                        source_field="metadata.hermes.config",
                    )
                )
        discovery: dict[str, Any] = {}
        if "tags" in hermes:
            tags = _string_list(hermes["tags"])
            if tags is not None:
                discovery["tags"] = _unique(tags)
                dispositions.append(
                    {
                        "source": "metadata.hermes.tags",
                        "target": "extensions.de.aip.ori.data.discovery.tags",
                        "disposition": "normalized",
                    }
                )
        if isinstance(hermes.get("category"), str):
            discovery["legacy_category"] = hermes["category"]
            dispositions.append(
                {
                    "source": "metadata.hermes.category",
                    "target": "extensions.de.aip.ori.data.discovery.legacy_category",
                    "disposition": "copied",
                }
            )
        if "related_skills" in hermes:
            related = _string_list(hermes["related_skills"])
            if related is not None:
                discovery["related_skill_candidates"] = _unique(related)
                dispositions.append(
                    {
                        "source": "metadata.hermes.related_skills",
                        "target": ("extensions.de.aip.ori.data.discovery.related_skill_candidates"),
                        "disposition": "normalized",
                    }
                )
        top_category = fm.get("category")
        if isinstance(top_category, str) and "legacy_category" not in discovery:
            discovery["legacy_category"] = top_category
            dispositions.append(
                {
                    "source": "category",
                    "target": "extensions.de.aip.ori.data.discovery.legacy_category",
                    "disposition": "copied",
                }
            )
        elif top_category == discovery.get("legacy_category"):
            dispositions.append(
                {
                    "source": "category",
                    "target": "extensions.de.aip.ori.data.discovery.legacy_category",
                    "disposition": "normalized",
                }
            )
        if discovery:
            data["discovery"] = discovery
        for key in _sorted_legacy_keys(set(hermes) - KNOWN_HERMES):
            source = _legacy_source_path("metadata.hermes", key)
            unmapped[source] = _legacy_json(hermes[key])
            findings.append(
                Finding(
                    code="CONVERT_FIELD_UNMAPPED",
                    profile="conversion",
                    severity="blocker",
                    message=f"legacy field {source!r} has no approved mapping",
                    pointer="/extensions/de.aip.ori/data/unmapped",
                    disposition="unmapped",
                    source_field=source,
                )
            )
            dispositions.append(
                {
                    "source": source,
                    "target": "extensions.de.aip.ori.data.unmapped",
                    "disposition": "unmapped",
                }
            )
        if not hermes:
            dispositions.append(
                {
                    "source": "metadata.hermes",
                    "target": "extensions.de.aip.ori.data",
                    "disposition": "preserved",
                }
            )
    elif hermes is not None:
        unmapped["metadata.hermes"] = _legacy_json(hermes)
        findings.append(
            Finding(
                code="CONVERT_ORI_METADATA_TYPE",
                profile="conversion",
                severity="blocker",
                message="metadata.hermes has an unsupported type",
                pointer="/extensions/de.aip.ori/data/unmapped",
                disposition="unmapped",
                source_field="metadata.hermes",
            )
        )
        dispositions.append(
            {
                "source": "metadata.hermes",
                "target": "extensions.de.aip.ori.data.unmapped",
                "disposition": "unmapped",
            }
        )

    if (
        "category" in fm
        and not any(item["source"] == "category" for item in dispositions)
        and isinstance(fm["category"], str)
    ):
        data.setdefault("discovery", {})["legacy_category"] = fm["category"]
        dispositions.append(
            {
                "source": "category",
                "target": "extensions.de.aip.ori.data.discovery.legacy_category",
                "disposition": "copied",
            }
        )

    if isinstance(metadata, dict):
        for key in _sorted_legacy_keys(set(metadata) - {"hermes"}):
            source = _legacy_source_path("metadata", key)
            unmapped[source] = _legacy_json(metadata[key])
            findings.append(
                Finding(
                    code="CONVERT_FIELD_UNMAPPED",
                    profile="conversion",
                    severity="blocker",
                    message=f"legacy field {source!r} has no approved mapping",
                    pointer="/extensions/de.aip.ori/data/unmapped",
                    disposition="unmapped",
                    source_field=source,
                )
            )
            dispositions.append(
                {
                    "source": source,
                    "target": "extensions.de.aip.ori.data.unmapped",
                    "disposition": "unmapped",
                }
            )
    elif metadata is not None:
        unmapped["metadata"] = _legacy_json(metadata)
        dispositions.append(
            {
                "source": "metadata",
                "target": "extensions.de.aip.ori.data.unmapped",
                "disposition": "unmapped",
            }
        )

    for key in _sorted_legacy_keys(set(fm) - KNOWN_TOP_LEVEL):
        source = _legacy_source_path("", key)
        unmapped[source] = _legacy_json(fm[key])
        findings.append(
            Finding(
                code="CONVERT_FIELD_UNMAPPED",
                profile="conversion",
                severity="blocker",
                message=f"legacy field {source!r} has no approved mapping",
                pointer="/extensions/de.aip.ori/data/unmapped",
                disposition="unmapped",
                source_field=source,
            )
        )
        dispositions.append(
            {
                "source": source,
                "target": "extensions.de.aip.ori.data.unmapped",
                "disposition": "unmapped",
            }
        )
    if unmapped:
        data["unmapped"] = unmapped
    if not data:
        return None
    return {
        "schema": "urn:skill-commons:extension:de.aip.ori:1",
        "required": False,
        "data": data,
    }


def build_manifest(
    skill_dir: Path,
    *,
    namespace: str,
    source_url: str,
    source_revision: str,
    source_path: str,
    population_claim: str = "github-community-tree",
    source_snapshot: list[SnapshotEntry] | None = None,
) -> tuple[dict[str, Any], list[Finding], list[dict[str, str]]]:
    source_entries = source_snapshot or snapshot_tree(skill_dir, require_manifest=False)
    fm, _, _, skill_bytes = _parse_snapshot(source_entries)
    resolved_source_path = _source_package_path(source_path)
    source_tree_digest = _snapshot_digest(source_entries)
    findings: list[Finding] = []
    dispositions: list[dict[str, str]] = []
    directory_name = skill_dir.name
    legacy_name = fm.get("name")
    aliases: list[str] = []
    if isinstance(legacy_name, str) and legacy_name != directory_name:
        aliases.append(legacy_name)
        findings.append(
            Finding(
                code="CONVERT_NAME_ALIAS_PROPOSED",
                profile="conversion",
                severity="blocker",
                message=(
                    f"directory identity {directory_name!r} wins; {legacy_name!r} "
                    "retained as an alias proposal"
                ),
                pointer="/package/name",
                disposition="proposed",
                source_field="name",
            )
        )
        dispositions.append(
            {"source": "name", "target": "package.aliases", "disposition": "proposed"}
        )
    elif isinstance(legacy_name, str):
        dispositions.append({"source": "name", "target": "package.name", "disposition": "copied"})
    else:
        findings.append(
            Finding(
                code="CONVERT_NAME_INVALID",
                profile="conversion",
                severity="blocker",
                message="missing or non-string name replaced by directory identity",
                pointer="/package/name",
                disposition="proposed",
                source_field="name",
            )
        )

    version = _version(fm.get("version"), findings, dispositions)
    license_value = fm.get("license")
    package_license = (
        license_value if isinstance(license_value, str) and license_value else "NOASSERTION"
    )
    license_evidence: list[dict[str, Any]] = []
    if package_license == "NOASSERTION":
        findings.append(
            Finding(
                code="CONVERT_NO_PER_SKILL_LICENSE_DECLARATION",
                profile="conversion",
                severity="blocker",
                message=(
                    "no per-skill license declaration; repository-level evidence requires "
                    "human scope review"
                ),
                pointer="/package/license",
                disposition="unmapped",
                source_field="license",
            )
        )
        if "license" not in fm:
            dispositions.append(
                {"source": "license", "target": "package.license", "disposition": "proposed"}
            )
    else:
        license_evidence.append(
            {
                "kind": "upstream-declaration",
                "expression": package_license,
                "url": source_url,
                "revision": source_revision,
                "digest": sha256_bytes(skill_bytes),
                "applies_to": ["SKILL.md"],
            }
        )
        dispositions.append(
            {"source": "license", "target": "package.license", "disposition": "copied"}
        )

    author = fm.get("author")
    contributors = []
    if isinstance(author, str) and author:
        contributors = [{"name": author, "role": "author"}]
        dispositions.append(
            {
                "source": "author",
                "target": "authorship.contributors[0].name",
                "disposition": "copied",
            }
        )
    else:
        findings.append(
            Finding(
                code="CONVERT_AUTHORSHIP_UNRESOLVED",
                profile="conversion",
                severity="blocker",
                message="no author string observed; authorship requires human review",
                pointer="/authorship",
                disposition="unmapped",
                source_field="author",
            )
        )

    python_deps = _dependencies(fm, findings, dispositions)
    prerequisites = fm.get("prerequisites")
    commands = []
    if isinstance(prerequisites, dict) and "commands" in prerequisites:
        command_values = _string_list(prerequisites.get("commands"))
        if command_values is None:
            findings.append(
                Finding(
                    code="CONVERT_COMMANDS_TYPE",
                    profile="conversion",
                    severity="blocker",
                    message="prerequisites.commands has an unsupported shape",
                    pointer="/capabilities/processes",
                    disposition="unmapped",
                    source_field="prerequisites.commands",
                )
            )
        else:
            commands = _unique(command_values)
            dispositions.append(
                {
                    "source": "prerequisites.commands",
                    "target": "capabilities.processes",
                    "disposition": "normalized",
                }
            )
    if isinstance(prerequisites, dict):
        for key in _sorted_legacy_keys(set(prerequisites) - {"python", "commands"}):
            source = _legacy_source_path("prerequisites", key)
            findings.append(
                Finding(
                    code="CONVERT_PREREQUISITE_UNMAPPED",
                    profile="conversion",
                    severity="blocker",
                    message=f"{source} has no approved mapping",
                    pointer="/extensions/de.aip.ori/data/unmapped",
                    disposition="unmapped",
                    source_field=source,
                )
            )

    metadata = fm.get("metadata")
    hermes = metadata.get("hermes") if isinstance(metadata, dict) else None
    hermes_tags = _string_list(hermes.get("tags")) if isinstance(hermes, dict) else None
    top_tags = _string_list(fm.get("tags")) if "tags" in fm else None
    tags = hermes_tags if hermes_tags is not None else top_tags or []
    if hermes_tags is not None:
        dispositions.append(
            {
                "source": "metadata.hermes.tags",
                "target": "research.keywords",
                "disposition": "normalized",
            }
        )
    if top_tags is not None and (hermes_tags is None or top_tags == hermes_tags):
        dispositions.append(
            {"source": "tags", "target": "research.keywords", "disposition": "normalized"}
        )
    hermes_related = (
        _string_list(hermes.get("related_skills")) if isinstance(hermes, dict) else None
    )
    top_related = _string_list(fm.get("related_skills")) if "related_skills" in fm else None
    related = hermes_related if hermes_related is not None else top_related or []
    if hermes_related is not None:
        dispositions.append(
            {
                "source": "metadata.hermes.related_skills",
                "target": "relations.related_to",
                "disposition": "proposed",
            }
        )
    if top_related is not None and (hermes_related is None or top_related == hermes_related):
        dispositions.append(
            {
                "source": "related_skills",
                "target": "relations.related_to",
                "disposition": "proposed",
            }
        )
    if related:
        findings.append(
            Finding(
                code="CONVERT_RELATION_REVIEW_REQUIRED",
                profile="conversion",
                severity="warning",
                message=(
                    "related_skills preserved as related_to candidates; stronger relation "
                    "requires review"
                ),
                pointer="/relations/related_to",
                disposition="proposed",
                source_field=(
                    "metadata.hermes.related_skills"
                    if hermes_related is not None
                    else "related_skills"
                ),
            )
        )

    platforms_value = _string_list(fm.get("platforms")) if "platforms" in fm else []
    platforms = platforms_value or []
    if platforms_value is not None and "platforms" in fm:
        dispositions.append(
            {
                "source": "platforms",
                "target": "compatibility.operating_systems",
                "disposition": "proposed",
            }
        )
    description = fm.get("description")
    if isinstance(description, str) and description:
        dispositions.append(
            {"source": "description", "target": "SKILL.md.description", "disposition": "copied"}
        )
    else:
        findings.append(
            Finding(
                code="CONVERT_DESCRIPTION_INVALID",
                profile="conversion",
                severity="blocker",
                message="missing or invalid description replaced by an explicit review placeholder",
                pointer="/SKILL.md/description",
                disposition="proposed",
                source_field="description",
            )
        )
    dispositions.append({"source": "body", "target": "SKILL.md.body", "disposition": "copied"})
    extension = _ori_extension(fm, findings, dispositions)
    extension = _ensure_loss_accounting(fm, extension, findings, dispositions)
    manifest: dict[str, Any] = {
        "schema_version": "0.1.0-draft",
        "package": {
            "namespace": namespace,
            "name": directory_name,
            **({"aliases": aliases} if aliases else {}),
            "version": version,
            "license": package_license,
            "source": {
                "repository": source_url,
                "revision": source_revision,
                "path": resolved_source_path,
            },
        },
        "authorship": {
            "status": "asserted" if contributors else "unresolved",
            "contributors": contributors,
            "creation_mode": "unknown",
        },
        "research": {
            "disciplines": [],
            "methods": [],
            "software": [],
            "data_sources": [],
            "intended_uses": [],
            "excluded_uses": [],
            "assumptions": [],
            "known_failure_modes": [],
            "keywords": _unique(tags),
        },
        "relations": {
            "implements_tasks": [],
            "derived_from": [],
            "supersedes": [],
            "compatible_with": [],
            "related_to": _unique(related),
        },
        "compatibility": {
            "clients": ["ori"],
            "operating_systems": _unique(platforms),
            "architectures": [],
            "python": None,
        },
        "dependencies": {
            "completeness": "unknown",
            "python": python_deps,
            "system": [],
            "containers": [],
        },
        "capabilities": {
            "completeness": "unknown",
            "filesystem": [],
            "network": [],
            "processes": commands,
            "named_secrets": [],
            "external_side_effects": [],
            "paid_services": [],
        },
        "validation": {
            "contracts": [],
            "network_required": None,
            "maximum_runtime_seconds": None,
            "stochastic": None,
        },
        "license_evidence": license_evidence,
        "provenance": {
            "origin": "migrated",
            "source_state": "active",
            "population_claims": [
                {
                    "issuer": source_url,
                    "scheme": "source-tree-population",
                    "value": population_claim,
                    "evidence": f"{source_revision}:{resolved_source_path}",
                }
            ],
            "upstreams": [
                {
                    "repository": source_url,
                    "revision": source_revision,
                    "path": resolved_source_path,
                    "digest": source_tree_digest,
                    "relation": "source",
                }
            ],
        },
    }
    if extension:
        manifest["extensions"] = {"de.aip.ori": extension}
    return (
        manifest,
        findings,
        sorted(dispositions, key=lambda item: (item["source"], item["target"])),
    )


def projected_skill(
    skill_dir: Path,
    manifest: dict[str, Any],
    projection: str,
    source_snapshot: list[SnapshotEntry] | None = None,
) -> str:
    entries = source_snapshot or snapshot_tree(skill_dir, require_manifest=False)
    fm, body, _, _ = _parse_snapshot(entries)
    description = fm.get("description")
    if not isinstance(description, str) or not description:
        description = "TODO: supply a reviewed skill description."
    if projection == "portable":
        projected: dict[str, Any] = {
            "name": manifest["package"]["name"],
            "description": description,
        }
        if manifest["package"]["license"] != "NOASSERTION":
            projected["license"] = manifest["package"]["license"]
        projected["metadata"] = {"research-skill.manifest": "research-skill.yaml"}
    elif projection == "ori-bridge":
        projected = copy.deepcopy(fm)
        projected["name"] = manifest["package"]["name"]
        projected["description"] = description
        dependencies = _string_list(fm.get("dependencies")) if "dependencies" in fm else []
        prerequisites = projected.get("prerequisites")
        if dependencies and not (
            isinstance(prerequisites, dict) and _string_list(prerequisites.get("python"))
        ):
            if not isinstance(prerequisites, dict):
                prerequisites = {}
                projected["prerequisites"] = prerequisites
            prerequisites["python"] = dependencies
    else:
        raise ValueError(f"unknown projection: {projection}")
    projected_yaml = (
        dump_yaml(projected)
        if projection == "portable"
        else yaml.safe_dump(
            projected,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=100,
        )
    )
    return "---\n" + projected_yaml + "---\n" + body


def conversion_report(
    skill_dir: Path,
    manifest: dict[str, Any],
    findings: list[Finding],
    dispositions: list[dict[str, str]],
    projection: str,
    projected_text: str,
    source_snapshot: list[SnapshotEntry] | None = None,
) -> dict[str, Any]:
    entries = source_snapshot or snapshot_tree(skill_dir, require_manifest=False)
    fm, _, source_text, skill_bytes = _parse_snapshot(entries)
    profiles = [
        validate_agent_skills(skill_dir, fm, skill_bytes),
        validate_ori(skill_dir, fm, manifest),
        validate_publication(skill_dir, fm, manifest, entries),
    ]
    projection_texts = {
        "portable": projected_skill(skill_dir, manifest, "portable", entries),
        "ori-bridge": projected_skill(skill_dir, manifest, "ori-bridge", entries),
    }
    if projection_texts[projection] != projected_text:
        raise ValueError("selected projection text does not match the deterministic projection")
    projection_reports: dict[str, dict[str, Any]] = {}
    for name, text in projection_texts.items():
        patch = "".join(
            difflib.unified_diff(
                source_text.splitlines(keepends=True),
                text.splitlines(keepends=True),
                fromfile="source/SKILL.md",
                tofile=f"candidate-{name}/SKILL.md",
            )
        )
        projection_reports[name] = {
            "skill_md_digest": sha256_bytes(text.encode("utf-8")),
            "source_to_candidate_patch": patch,
        }
    return {
        "report_schema_version": "0.1.0-draft",
        "tool": {"name": "skill-commons", "version": __version__},
        "source": {
            "directory": skill_dir.name,
            "skill_md_digest": sha256_bytes(skill_bytes),
        },
        "candidate": {
            "projection": projection,
            "manifest_digest": semantic_digest(manifest),
            "skill_md_digest": projection_reports[projection]["skill_md_digest"],
            "source_to_candidate_patch": projection_reports[projection][
                "source_to_candidate_patch"
            ],
        },
        "proposed_projections": projection_reports,
        "profile_subject": {
            "skill_directory": "source",
            "manifest": "proposed-in-memory",
            "note": "Revalidate the emitted candidate directory before packing.",
        },
        "profiles": {item.name: item.to_dict() for item in profiles},
        "conversion_findings": [
            item.to_dict()
            for item in sorted(findings, key=lambda item: (item.code, item.source_field or ""))
        ],
        "field_dispositions": dispositions,
    }


def emit_candidate(
    skill_dir: Path,
    out_dir: Path,
    manifest: dict[str, Any],
    report: dict[str, Any],
    projected_text: str,
    source_snapshot: list[SnapshotEntry] | None = None,
) -> None:
    source_resolved = skill_dir.resolve()
    output_resolved = out_dir.resolve()
    if (
        output_resolved == source_resolved
        or output_resolved.is_relative_to(source_resolved)
        or source_resolved.is_relative_to(output_resolved)
    ):
        raise ValueError("output directory must not overlap the source skill")
    if output_resolved.exists() and any(output_resolved.iterdir()):
        raise ValueError("output directory must be empty")
    entries = source_snapshot or snapshot_tree(source_resolved, require_manifest=False)
    observed_digest = _snapshot_digest(entries)
    expected_digest = manifest["provenance"]["upstreams"][0]["digest"]
    if observed_digest != expected_digest:
        raise ValueError("source package changed after manifest construction")

    output_resolved.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_resolved.name}.", dir=output_resolved.parent))
    try:
        package_dir = staging / "package"
        evidence_dir = staging / "evidence"
        package_dir.mkdir()
        evidence_dir.mkdir()
        source_modes: dict[str, int] = {}
        for entry in entries:
            destination = package_dir / entry.relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(entry.data)
            mode = 0o755 if entry.executable else 0o644
            destination.chmod(mode)
            source_modes[entry.relative] = mode
        skill_path = package_dir / "SKILL.md"
        skill_path.write_bytes(projected_text.encode("utf-8"))
        skill_path.chmod(source_modes.get("SKILL.md", 0o644))
        manifest_path = package_dir / "research-skill.yaml"
        manifest_path.write_bytes(dump_yaml(manifest).encode("utf-8"))
        manifest_path.chmod(0o644)

        report_without_patch = copy.deepcopy(report)
        selected_patch = report["candidate"]["source_to_candidate_patch"]
        selected_patch_name = f"source-to-{report['candidate']['projection']}.patch"
        (evidence_dir / selected_patch_name).write_bytes(selected_patch.encode("utf-8"))
        report_without_patch["candidate"]["source_to_candidate_patch"] = (
            f"evidence/{selected_patch_name}"
        )
        for name, projection_report in report["proposed_projections"].items():
            patch_name = f"source-to-{name}.patch"
            (evidence_dir / patch_name).write_bytes(
                projection_report["source_to_candidate_patch"].encode("utf-8")
            )
            report_without_patch["proposed_projections"][name]["source_to_candidate_patch"] = (
                f"evidence/{patch_name}"
            )
        report_payload = (
            json.dumps(
                report_without_patch,
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        (evidence_dir / "conversion-report.json").write_bytes(report_payload)
        if output_resolved.exists():
            output_resolved.rmdir()
        staging.replace(output_resolved)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
