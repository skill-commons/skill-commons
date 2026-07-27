"""Independent Agent Skills, Ori, and Commons validation profiles."""

from __future__ import annotations

import importlib.metadata
import json
import re
import tempfile
from collections.abc import Iterable
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from license_expression import get_spdx_licensing
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version
from skills_ref import ValidationError as ReferenceValidationError
from skills_ref import validate as reference_validate

from . import __version__
from .io import load_yaml, parse_skill_text, semantic_digest, sha256_bytes
from .model import Finding, ProfileResult
from .packer import SnapshotEntry, snapshot_tree

AGENT_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ORI_HERMES_LISTS = {
    "requires_toolsets",
    "requires_tools",
    "fallback_for_toolsets",
    "fallback_for_tools",
}
KNOWN_EXTENSION_SCHEMAS = {
    "de.aip.ori": "urn:skill-commons:extension:de.aip.ori:1",
}
SCHEMA_ROOT = Path(__file__).resolve().parent / "schemas"
if not SCHEMA_ROOT.exists():
    SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"


def _finding(
    code: str,
    profile: str,
    severity: str,
    message: str,
    pointer: str = "",
) -> Finding:
    return Finding(code=code, profile=profile, severity=severity, message=message, pointer=pointer)


def _as_string_list(value: Any) -> list[str] | None:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return None


def _normative_agent_findings(skill_dir: Path, fm: dict[str, Any]) -> list[Finding]:
    profile = "agent-skills"
    findings: list[Finding] = []
    unexpected = sorted(set(fm) - AGENT_KEYS, key=lambda value: repr(value))
    if unexpected:
        findings.append(
            _finding(
                "AGENT_UNEXPECTED_FIELDS",
                profile,
                "error",
                "Unsupported frontmatter fields: " + ", ".join(repr(value) for value in unexpected),
                "/frontmatter",
            )
        )
    name = fm.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64 or not NAME_RE.fullmatch(name):
        findings.append(
            _finding(
                "AGENT_INVALID_NAME",
                profile,
                "error",
                "name violates the Agent Skills naming rule",
                "/frontmatter/name",
            )
        )
    elif name != skill_dir.name:
        findings.append(
            _finding(
                "AGENT_NAME_DIRECTORY_MISMATCH",
                profile,
                "error",
                "name must match the parent directory",
                "/frontmatter/name",
            )
        )
    description = fm.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        findings.append(
            _finding(
                "AGENT_INVALID_DESCRIPTION",
                profile,
                "error",
                "description must contain 1-1024 characters",
                "/frontmatter/description",
            )
        )
    metadata = fm.get("metadata")
    if metadata is not None and (
        not isinstance(metadata, dict)
        or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()
        )
    ):
        findings.append(
            _finding(
                "AGENT_METADATA_NOT_STRING_MAP",
                profile,
                "error",
                "metadata must map strings to strings",
                "/frontmatter/metadata",
            )
        )
    compatibility = fm.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
    ):
        findings.append(
            _finding(
                "AGENT_INVALID_COMPATIBILITY",
                profile,
                "error",
                "compatibility must contain 1-500 characters",
                "/frontmatter/compatibility",
            )
        )
    license_value = fm.get("license")
    if license_value is not None and (
        not isinstance(license_value, str) or not license_value.strip()
    ):
        findings.append(
            _finding(
                "AGENT_INVALID_LICENSE",
                profile,
                "error",
                "license must be a non-empty string when present",
                "/frontmatter/license",
            )
        )
    allowed = fm.get("allowed-tools")
    if allowed is not None and not isinstance(allowed, str):
        findings.append(
            _finding(
                "AGENT_INVALID_ALLOWED_TOOLS",
                profile,
                "error",
                "allowed-tools must be a string",
                "/frontmatter/allowed-tools",
            )
        )
    return findings


def validate_agent_skills(
    skill_dir: Path, fm: dict[str, Any], skill_bytes: bytes | None = None
) -> ProfileResult:
    result = ProfileResult(
        name="agent-skills", contract="agent-skills-specification+skills-ref@0.1.1"
    )
    result.findings.extend(_normative_agent_findings(skill_dir, fm))
    reference_errors: list[str] = []
    try:
        if skill_bytes is None:
            reference_errors = list(reference_validate(skill_dir))
        else:
            with tempfile.TemporaryDirectory(prefix="skill-commons-agent-validation-") as temporary:
                reference_dir = Path(temporary) / skill_dir.name
                reference_dir.mkdir()
                (reference_dir / "SKILL.md").write_bytes(skill_bytes)
                reference_errors = list(reference_validate(reference_dir))
    except ReferenceValidationError as exc:
        reference_errors = list(exc.errors or [str(exc)])
    except Exception as exc:  # pragma: no cover - defensive boundary around external tool
        reference_errors = [str(exc)]
    for error in reference_errors:
        result.findings.append(
            _finding(
                "AGENT_REFERENCE_REJECTED",
                "agent-skills",
                "error",
                str(error),
                "/SKILL.md",
            )
        )
    result.details = {
        "normative_status": "fail"
        if any(
            item.code != "AGENT_REFERENCE_REJECTED" and item.severity == "error"
            for item in result.findings
        )
        else "pass",
        "reference_status": "fail" if reference_errors else "pass",
        "reference_version": importlib.metadata.version("skills-ref"),
    }
    return result


def validate_ori(
    skill_dir: Path, fm: dict[str, Any], manifest: dict[str, Any] | None
) -> ProfileResult:
    result = ProfileResult(name="ori-compatibility", contract="ori-frontmatter-v1")
    name = fm.get("name")
    if not isinstance(name, str) or not name:
        result.findings.append(
            _finding(
                "ORI_NAME_FALLBACK",
                result.name,
                "warning",
                "Ori will fall back to the directory name",
                "/frontmatter/name",
            )
        )
    elif name != skill_dir.name:
        result.findings.append(
            _finding(
                "ORI_DIRECTORY_IDENTITY_WINS",
                result.name,
                "warning",
                f"Ori identity is directory {skill_dir.name!r}, not frontmatter name {name!r}",
                "/frontmatter/name",
            )
        )
    if not isinstance(fm.get("description"), str) or not fm.get("description"):
        result.findings.append(
            _finding(
                "ORI_DESCRIPTION_MISSING",
                result.name,
                "error",
                "Ori requires description for the startup catalog",
                "/frontmatter/description",
            )
        )

    prerequisites = fm.get("prerequisites")
    prereq_python: list[str] | None = []
    if prerequisites is not None:
        if not isinstance(prerequisites, dict):
            result.findings.append(
                _finding(
                    "ORI_PREREQUISITES_TYPE",
                    result.name,
                    "error",
                    "prerequisites must be a mapping",
                    "/frontmatter/prerequisites",
                )
            )
            prereq_python = None
        elif "python" in prerequisites:
            prereq_python = _as_string_list(prerequisites.get("python"))
            if prereq_python is None:
                result.findings.append(
                    _finding(
                        "ORI_PYTHON_REQUIREMENTS_TYPE",
                        result.name,
                        "error",
                        "prerequisites.python must be a string or list of strings",
                        "/frontmatter/prerequisites/python",
                    )
                )

    dependencies = fm.get("dependencies")
    dep_python = _as_string_list(dependencies) if dependencies is not None else []
    if dependencies is not None and dep_python is None:
        result.findings.append(
            _finding(
                "ORI_INERT_DEPENDENCIES_TYPE",
                result.name,
                "warning",
                "legacy dependencies is inert and has an unsupported shape",
                "/frontmatter/dependencies",
            )
        )
    elif dep_python and not prereq_python:
        result.findings.append(
            _finding(
                "ORI_INERT_DEPENDENCIES_ONLY",
                result.name,
                "warning",
                "dependencies is ignored by Ori; propose prerequisites.python bridge",
                "/frontmatter/dependencies",
            )
        )
    elif dep_python and prereq_python and dep_python != prereq_python:
        result.findings.append(
            _finding(
                "ORI_DEPENDENCY_CONFLICT",
                result.name,
                "error",
                "dependencies and prerequisites.python disagree",
                "/frontmatter",
            )
        )

    metadata = fm.get("metadata")
    hermes = metadata.get("hermes") if isinstance(metadata, dict) else None
    if hermes is not None:
        if not isinstance(hermes, dict):
            result.findings.append(
                _finding(
                    "ORI_HERMES_METADATA_TYPE",
                    result.name,
                    "error",
                    "metadata.hermes must be a mapping",
                    "/frontmatter/metadata/hermes",
                )
            )
        else:
            for key in sorted(ORI_HERMES_LISTS):
                if key in hermes and _as_string_list(hermes[key]) is None:
                    result.findings.append(
                        _finding(
                            "ORI_ACTIVATION_TYPE",
                            result.name,
                            "error",
                            f"metadata.hermes.{key} must be a list of strings",
                            f"/frontmatter/metadata/hermes/{key}",
                        )
                    )
            config = hermes.get("config")
            if config is not None and (
                not isinstance(config, list)
                or not all(
                    isinstance(item, dict) and isinstance(item.get("key"), str) for item in config
                )
            ):
                result.findings.append(
                    _finding(
                        "ORI_CONFIG_TYPE",
                        result.name,
                        "error",
                        "metadata.hermes.config must be a list of mappings with key",
                        "/frontmatter/metadata/hermes/config",
                    )
                )

    platforms = fm.get("platforms")
    if platforms is not None and _as_string_list(platforms) is None:
        result.findings.append(
            _finding(
                "ORI_PLATFORMS_TYPE",
                result.name,
                "error",
                "platforms must be a list of strings",
                "/frontmatter/platforms",
            )
        )

    if manifest is not None and not isinstance(manifest, dict):
        result.findings.append(
            _finding(
                "ORI_SIDECAR_TYPE",
                result.name,
                "error",
                "research-skill.yaml must be a mapping",
                "/research-skill.yaml",
            )
        )
        return result
    if manifest is not None:
        package = manifest.get("package")
        if not isinstance(package, dict) or package.get("name") != skill_dir.name:
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_IDENTITY_MISMATCH",
                    result.name,
                    "error",
                    "sidecar package name disagrees with Ori's directory identity",
                    "/package/name",
                )
            )
        sidecar_dependencies = manifest.get("dependencies")
        if not isinstance(sidecar_dependencies, dict):
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_DEPENDENCIES_TYPE",
                    result.name,
                    "error",
                    "sidecar dependencies must be a mapping",
                    "/dependencies",
                )
            )
        elif prereq_python is not None:
            sidecar_python = sidecar_dependencies.get("python", [])
            expected = prereq_python or dep_python or []
            if expected != sidecar_python:
                result.findings.append(
                    _finding(
                        "ORI_SIDECAR_DEPENDENCY_MISMATCH",
                        result.name,
                        "error",
                        "legacy and sidecar Python dependencies disagree",
                        "/dependencies/python",
                    )
                )
        if isinstance(sidecar_dependencies, dict):
            for dependency_kind in ("system", "containers"):
                if sidecar_dependencies.get(dependency_kind):
                    result.findings.append(
                        _finding(
                            "ORI_SIDECAR_DEPENDENCY_UNSUPPORTED",
                            result.name,
                            "error",
                            (
                                "current Ori does not provision sidecar "
                                f"{dependency_kind} dependencies"
                            ),
                            f"/dependencies/{dependency_kind}",
                        )
                    )
        compatibility = manifest.get("compatibility")
        if not isinstance(compatibility, dict):
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_COMPATIBILITY_TYPE",
                    result.name,
                    "error",
                    "sidecar compatibility must be a mapping",
                    "/compatibility",
                )
            )
            compatibility = {}
        clients = compatibility.get("clients", [])
        if not isinstance(clients, list) or not all(isinstance(client, str) for client in clients):
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_CLIENTS_TYPE",
                    result.name,
                    "error",
                    "sidecar compatibility.clients must be a list of strings",
                    "/compatibility/clients",
                )
            )
            clients = []
        elif clients and "ori" not in clients:
            result.findings.append(
                _finding(
                    "ORI_CLIENT_EXCLUDED",
                    result.name,
                    "error",
                    "compatibility.clients explicitly excludes Ori",
                    "/compatibility/clients",
                )
            )
        if compatibility.get("architectures"):
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_ARCHITECTURE_UNSUPPORTED",
                    result.name,
                    "error",
                    "current Ori does not enforce sidecar architecture constraints",
                    "/compatibility/architectures",
                )
            )
        if compatibility.get("python") is not None:
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_PYTHON_UNSUPPORTED",
                    result.name,
                    "error",
                    "current Ori does not enforce sidecar Python compatibility constraints",
                    "/compatibility/python",
                )
            )
        platform_values = _as_string_list(platforms) if platforms is not None else []
        if platform_values is not None:
            sidecar_platforms = compatibility.get("operating_systems", [])
            if list(dict.fromkeys(platform_values)) != sidecar_platforms:
                result.findings.append(
                    _finding(
                        "ORI_SIDECAR_PLATFORM_MISMATCH",
                        result.name,
                        "error",
                        "legacy platforms and sidecar operating systems disagree",
                        "/compatibility/operating_systems",
                    )
                )

        extensions = manifest.get("extensions", {})
        if not isinstance(extensions, dict):
            result.findings.append(
                _finding(
                    "ORI_SIDECAR_EXTENSIONS_TYPE",
                    result.name,
                    "error",
                    "sidecar extensions must be a mapping",
                    "/extensions",
                )
            )
            extensions = {}
        for extension_name, extension in extensions.items():
            if (
                extension_name not in KNOWN_EXTENSION_SCHEMAS
                and isinstance(extension, dict)
                and extension.get("required") is True
            ):
                result.findings.append(
                    _finding(
                        "ORI_REQUIRED_EXTENSION_UNKNOWN",
                        result.name,
                        "error",
                        f"Ori cannot satisfy required extension {extension_name!r}",
                        f"/extensions/{extension_name}",
                    )
                )
        ori_extension = extensions.get("de.aip.ori")
        if ori_extension is not None and not isinstance(ori_extension, dict):
            result.findings.append(
                _finding(
                    "ORI_EXTENSION_TYPE",
                    result.name,
                    "error",
                    "de.aip.ori extension must be a mapping",
                    "/extensions/de.aip.ori",
                )
            )
        elif ori_extension:
            if ori_extension.get("schema") != KNOWN_EXTENSION_SCHEMAS["de.aip.ori"]:
                result.findings.append(
                    _finding(
                        "ORI_EXTENSION_SCHEMA_MISMATCH",
                        result.name,
                        "error",
                        "de.aip.ori does not use the pinned extension schema identifier",
                        "/extensions/de.aip.ori/schema",
                    )
                )
            clients = compatibility.get("clients", [])
            if not isinstance(clients, list) or "ori" not in clients:
                result.findings.append(
                    _finding(
                        "ORI_EXTENSION_CLIENT_MISSING",
                        result.name,
                        "error",
                        "a de.aip.ori extension requires ori in compatibility.clients",
                        "/compatibility/clients",
                    )
                )
            extension_data = ori_extension.get("data")
            if not isinstance(extension_data, dict):
                result.findings.append(
                    _finding(
                        "ORI_EXTENSION_DATA_TYPE",
                        result.name,
                        "error",
                        "de.aip.ori extension data must be a mapping",
                        "/extensions/de.aip.ori/data",
                    )
                )
                extension_data = {}
            legacy_activation = {
                key: list(dict.fromkeys(value))
                for key in ORI_HERMES_LISTS
                if isinstance(hermes, dict)
                and (value := _as_string_list(hermes.get(key))) is not None
                and key in hermes
            }
            if extension_data.get("activation", {}) != legacy_activation:
                result.findings.append(
                    _finding(
                        "ORI_SIDECAR_ACTIVATION_MISMATCH",
                        result.name,
                        "error",
                        "legacy and sidecar activation declarations disagree",
                        "/extensions/de.aip.ori/data/activation",
                    )
                )
            legacy_config = hermes.get("config") if isinstance(hermes, dict) else None
            sidecar_config = extension_data.get("config")
            if (legacy_config is not None or sidecar_config is not None) and (
                sidecar_config != legacy_config
            ):
                result.findings.append(
                    _finding(
                        "ORI_SIDECAR_CONFIG_MISMATCH",
                        result.name,
                        "error",
                        "legacy and sidecar configuration declarations disagree",
                        "/extensions/de.aip.ori/data/config",
                    )
                )
    return result


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))


def _validate_dependency_lock(
    manifest: dict[str, Any], result: ProfileResult, entries: dict[str, SnapshotEntry]
) -> None:
    lock_entry = entries.get("research-skill.lock")
    dependencies_declared = any(
        manifest["dependencies"][kind] for kind in ("python", "system", "containers")
    )
    if dependencies_declared and lock_entry is None:
        result.findings.append(
            _finding(
                "COMMONS_LOCK_MISSING",
                result.name,
                "blocker",
                "declared dependencies require research-skill.lock",
                "/research-skill.lock",
            )
        )
        return
    if lock_entry is None:
        return
    try:
        lock = load_yaml(lock_entry.data.decode("utf-8"))
        jsonschema.Draft202012Validator(
            _load_schema("research-skill-lock.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        ).validate(lock)
    except (OSError, TypeError, ValueError, jsonschema.ValidationError, yaml.YAMLError) as exc:
        result.findings.append(
            _finding(
                "COMMONS_LOCK_INVALID",
                result.name,
                "blocker",
                str(exc),
                "/research-skill.lock",
            )
        )
        return
    package = manifest["package"]
    if lock["package"] != {
        "coordinate": f"{package['namespace']}/{package['name']}",
        "version": package["version"],
    }:
        result.findings.append(
            _finding(
                "COMMONS_LOCK_IDENTITY_MISMATCH",
                result.name,
                "blocker",
                "lock coordinate/version disagrees with the manifest",
                "/research-skill.lock/package",
            )
        )
    if lock["manifest_digest"] != semantic_digest(manifest):
        result.findings.append(
            _finding(
                "COMMONS_LOCK_MANIFEST_MISMATCH",
                result.name,
                "blocker",
                "lock manifest_digest does not bind the current manifest",
                "/research-skill.lock/manifest_digest",
            )
        )
    if dependencies_declared and not lock["resolutions"]:
        result.findings.append(
            _finding(
                "COMMONS_LOCK_RESOLUTION_MISSING",
                result.name,
                "blocker",
                "declared dependencies require at least one target resolution",
                "/research-skill.lock/resolutions",
            )
        )
    requirements_digest = semantic_digest(manifest["dependencies"])
    operating_systems = manifest["compatibility"]["operating_systems"]
    architectures = manifest["compatibility"]["architectures"]
    python_compatibility = manifest["compatibility"]["python"]
    python_specifier = None
    if python_compatibility is not None:
        try:
            python_specifier = SpecifierSet(python_compatibility)
        except InvalidSpecifier:
            result.findings.append(
                _finding(
                    "COMMONS_PYTHON_COMPATIBILITY_INVALID",
                    result.name,
                    "blocker",
                    f"invalid Python compatibility specifier: {python_compatibility!r}",
                    "/compatibility/python",
                )
            )
    required_python: dict[str, list[Requirement]] = {}
    for index, requirement in enumerate(manifest["dependencies"]["python"]):
        try:
            parsed_requirement = Requirement(requirement)
        except InvalidRequirement:
            result.findings.append(
                _finding(
                    "COMMONS_DEPENDENCY_REQUIREMENT_INVALID",
                    result.name,
                    "blocker",
                    f"invalid Python requirement: {requirement!r}",
                    f"/dependencies/python/{index}",
                )
            )
            continue
        if parsed_requirement.marker is not None:
            result.findings.append(
                _finding(
                    "COMMONS_DEPENDENCY_MARKER_UNSUPPORTED",
                    result.name,
                    "blocker",
                    "Phase 0 lock validation does not yet evaluate target-specific markers",
                    f"/dependencies/python/{index}",
                )
            )
            continue
        name = canonicalize_name(parsed_requirement.name)
        required_python.setdefault(name, []).append(parsed_requirement)
    resolution_ids: set[str] = set()
    for index, resolution in enumerate(lock["resolutions"]):
        if resolution["id"] in resolution_ids:
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_RESOLUTION_DUPLICATE",
                    result.name,
                    "blocker",
                    f"duplicate resolution id: {resolution['id']}",
                    f"/research-skill.lock/resolutions/{index}/id",
                )
            )
        resolution_ids.add(resolution["id"])
        if resolution["requirements_digest"] != requirements_digest:
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_REQUIREMENTS_MISMATCH",
                    result.name,
                    "blocker",
                    "resolution requirements_digest does not bind manifest dependencies",
                    f"/research-skill.lock/resolutions/{index}/requirements_digest",
                )
            )
        target = resolution["target"]
        if operating_systems and target["operating_system"] not in operating_systems:
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_TARGET_MISMATCH",
                    result.name,
                    "blocker",
                    "lock target operating system is outside manifest compatibility",
                    f"/research-skill.lock/resolutions/{index}/target/operating_system",
                )
            )
        if architectures and target["architecture"] not in architectures:
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_TARGET_MISMATCH",
                    result.name,
                    "blocker",
                    "lock target architecture is outside manifest compatibility",
                    f"/research-skill.lock/resolutions/{index}/target/architecture",
                )
            )
        try:
            target_python = Version(target["python_version"])
        except InvalidVersion:
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_PYTHON_TARGET_INVALID",
                    result.name,
                    "blocker",
                    "lock target python_version is not a valid PEP 440 version",
                    f"/research-skill.lock/resolutions/{index}/target/python_version",
                )
            )
        else:
            if python_specifier is not None and not python_specifier.contains(
                target_python, prereleases=True
            ):
                result.findings.append(
                    _finding(
                        "COMMONS_LOCK_PYTHON_TARGET_MISMATCH",
                        result.name,
                        "blocker",
                        (
                            f"lock target Python {target_python} does not satisfy "
                            f"compatibility.python {python_compatibility!r}"
                        ),
                        f"/research-skill.lock/resolutions/{index}/target/python_version",
                    )
                )
        locked_versions: dict[int, Version | None] = {}
        locked_names: dict[str, list[int]] = {}
        locked_direct_records: dict[str, list[tuple[int, dict[str, Any], Version | None]]] = {}
        for package_index, item in enumerate(resolution["python"]):
            normalized_name = canonicalize_name(item["name"])
            locked_names.setdefault(normalized_name, []).append(package_index)
            try:
                locked_versions[package_index] = Version(item["version"])
            except InvalidVersion:
                locked_versions[package_index] = None
                result.findings.append(
                    _finding(
                        "COMMONS_LOCK_VERSION_INVALID",
                        result.name,
                        "blocker",
                        f"locked version for {normalized_name!r} is not valid PEP 440",
                        (
                            f"/research-skill.lock/resolutions/{index}/python/"
                            f"{package_index}/version"
                        ),
                    )
                )
            if item["direct"]:
                locked_direct_records.setdefault(normalized_name, []).append(
                    (package_index, item, locked_versions[package_index])
                )
        for name, package_indices in locked_names.items():
            if len(package_indices) > 1:
                result.findings.append(
                    _finding(
                        "COMMONS_LOCK_PACKAGE_DUPLICATE",
                        result.name,
                        "blocker",
                        f"multiple lock records resolve normalized package {name!r}",
                        f"/research-skill.lock/resolutions/{index}/python",
                    )
                )
        locked_direct = set(locked_direct_records)
        required_names = set(required_python)
        if locked_direct != required_names:
            missing = sorted(required_names - locked_direct)
            unexpected = sorted(locked_direct - required_names)
            result.findings.append(
                _finding(
                    "COMMONS_LOCK_DIRECT_DEPENDENCY_MISMATCH",
                    result.name,
                    "blocker",
                    "direct Python lock coverage differs"
                    + (f"; missing: {', '.join(missing)}" if missing else "")
                    + (f"; unexpected: {', '.join(unexpected)}" if unexpected else ""),
                    f"/research-skill.lock/resolutions/{index}/python",
                )
            )
        for name, requirements in required_python.items():
            records = locked_direct_records.get(name, [])
            if len(records) > 1:
                result.findings.append(
                    _finding(
                        "COMMONS_LOCK_DIRECT_DEPENDENCY_DUPLICATE",
                        result.name,
                        "blocker",
                        f"multiple direct lock records resolve {name!r}",
                        f"/research-skill.lock/resolutions/{index}/python",
                    )
                )
            if len(records) != 1:
                continue
            package_index, locked, locked_version = records[0]
            if locked_version is None:
                continue
            for requirement in requirements:
                if requirement.url is not None:
                    locked_urls = {locked["source"]["url"], locked["artifact"]["url"]}
                    if requirement.url not in locked_urls:
                        result.findings.append(
                            _finding(
                                "COMMONS_LOCK_DIRECT_URL_MISMATCH",
                                result.name,
                                "blocker",
                                f"locked source for {name!r} does not match its direct URL",
                                (
                                    f"/research-skill.lock/resolutions/{index}/python/"
                                    f"{package_index}/source/url"
                                ),
                            )
                        )
                elif requirement.specifier and not requirement.specifier.contains(
                    locked_version, prereleases=True
                ):
                    result.findings.append(
                        _finding(
                            "COMMONS_LOCK_VERSION_CONSTRAINT_MISMATCH",
                            result.name,
                            "blocker",
                            (
                                f"locked {name}=={locked_version} does not satisfy "
                                f"{requirement.specifier}"
                            ),
                            (
                                f"/research-skill.lock/resolutions/{index}/python/"
                                f"{package_index}/version"
                            ),
                        )
                    )
        for dependency_kind in ("system", "containers"):
            if manifest["dependencies"][dependency_kind] and not resolution[dependency_kind]:
                result.findings.append(
                    _finding(
                        "COMMONS_LOCK_CATEGORY_UNRESOLVED",
                        result.name,
                        "blocker",
                        f"declared {dependency_kind} dependencies have no locked entries",
                        f"/research-skill.lock/resolutions/{index}/{dependency_kind}",
                    )
                )


def validate_publication(
    skill_dir: Path,
    fm: dict[str, Any],
    manifest: dict[str, Any] | None,
    snapshot: list[SnapshotEntry] | None = None,
) -> ProfileResult:
    result = ProfileResult(name="commons-publication", contract="aip-phase0-candidate-readiness-v1")
    if manifest is None:
        result.findings.append(
            _finding(
                "COMMONS_MANIFEST_MISSING",
                result.name,
                "blocker",
                "research-skill.yaml is required",
                "/research-skill.yaml",
            )
        )
        return result

    validator = jsonschema.Draft202012Validator(
        _load_schema("research-skill.schema.json"), format_checker=jsonschema.FormatChecker()
    )
    for error in sorted(
        validator.iter_errors(manifest),
        key=lambda item: tuple(repr(part) for part in item.absolute_path),
    ):
        pointer = "/" + "/".join(str(item) for item in error.absolute_path)
        result.findings.append(
            _finding("COMMONS_SCHEMA_INVALID", result.name, "blocker", error.message, pointer)
        )
    if any(item.code == "COMMONS_SCHEMA_INVALID" for item in result.findings):
        return result

    result.findings.append(
        _finding(
            "COMMONS_EXTERNAL_ATTESTATIONS_REQUIRED",
            result.name,
            "warning",
            (
                "local validation cannot establish namespace control, publication rights, "
                "or reviewed redaction; the curator-authorized catalog gate must verify them"
            ),
            "/catalog/assessments",
        )
    )

    package_entries = snapshot or snapshot_tree(skill_dir, require_manifest=False)
    entry_map = {entry.relative: entry for entry in package_entries}

    package = manifest["package"]
    if package["name"] != skill_dir.name:
        result.findings.append(
            _finding(
                "COMMONS_NAME_DIRECTORY_MISMATCH",
                result.name,
                "blocker",
                "package.name must match the package directory",
                "/package/name",
            )
        )
    if fm.get("name") != skill_dir.name:
        result.findings.append(
            _finding(
                "COMMONS_PORTABLE_NAME_MISMATCH",
                result.name,
                "blocker",
                "portable SKILL.md name must match the package directory",
                "/SKILL.md/name",
            )
        )
    licensing = get_spdx_licensing()
    package_license_info = None
    if package["license"] == "NOASSERTION":
        result.findings.append(
            _finding(
                "COMMONS_LICENSE_UNRESOLVED",
                result.name,
                "blocker",
                "a publication candidate requires an SPDX license conclusion",
                "/package/license",
            )
        )
    else:
        package_license_info = licensing.validate(package["license"], strict=True)
        if package_license_info.errors:
            result.findings.append(
                _finding(
                    "COMMONS_LICENSE_NOT_SPDX",
                    result.name,
                    "blocker",
                    "; ".join(package_license_info.errors),
                    "/package/license",
                )
            )
    portable_license = fm.get("license")
    portable_license_info = None
    if not isinstance(portable_license, str) or not portable_license.strip():
        result.findings.append(
            _finding(
                "COMMONS_PORTABLE_LICENSE_MISSING",
                result.name,
                "blocker",
                "publication requires a non-empty SPDX license in portable SKILL.md",
                "/SKILL.md/license",
            )
        )
    else:
        portable_license_info = licensing.validate(portable_license, strict=True)
        if portable_license_info.errors:
            result.findings.append(
                _finding(
                    "COMMONS_PORTABLE_LICENSE_NOT_SPDX",
                    result.name,
                    "blocker",
                    "; ".join(portable_license_info.errors),
                    "/SKILL.md/license",
                )
            )
        elif package_license_info is not None and not package_license_info.errors:
            package_expression = licensing.parse(package["license"], validate=True, strict=True)
            portable_expression = licensing.parse(portable_license, validate=True, strict=True)
            if not licensing.is_equivalent(package_expression, portable_expression):
                result.findings.append(
                    _finding(
                        "COMMONS_PORTABLE_LICENSE_MISMATCH",
                        result.name,
                        "blocker",
                        "portable SKILL.md license is not equivalent to package.license",
                        "/SKILL.md/license",
                    )
                )
    evidence = manifest["license_evidence"]
    if not evidence:
        result.findings.append(
            _finding(
                "COMMONS_LICENSE_EVIDENCE_MISSING",
                result.name,
                "blocker",
                "license evidence is required",
                "/license_evidence",
            )
        )
    valid_evidence_expressions: list[str] = []
    for index, item in enumerate(evidence):
        pointer = f"/license_evidence/{index}"
        evidence_info = get_spdx_licensing().validate(item["expression"], strict=True)
        if evidence_info.errors:
            result.findings.append(
                _finding(
                    "COMMONS_LICENSE_EVIDENCE_NOT_SPDX",
                    result.name,
                    "blocker",
                    "; ".join(evidence_info.errors),
                    pointer + "/expression",
                )
            )
        else:
            valid_evidence_expressions.append(item["expression"])
        if "path" in item:
            evidence_entry = entry_map.get(item["path"])
            if evidence_entry is None:
                result.findings.append(
                    _finding(
                        "COMMONS_LICENSE_EVIDENCE_PATH_INVALID",
                        result.name,
                        "blocker",
                        "license evidence path is missing or escapes the package",
                        pointer + "/path",
                    )
                )
            elif "digest" in item and sha256_bytes(evidence_entry.data) != item["digest"]:
                result.findings.append(
                    _finding(
                        "COMMONS_LICENSE_EVIDENCE_DIGEST_MISMATCH",
                        result.name,
                        "blocker",
                        "license evidence digest does not match the packaged file",
                        pointer + "/digest",
                    )
                )
    if (
        package["license"] != "NOASSERTION"
        and package_license_info is not None
        and not package_license_info.errors
        and valid_evidence_expressions
    ):
        package_expression = get_spdx_licensing().parse(
            package["license"], validate=True, strict=True
        )
        evidence_expression = get_spdx_licensing().parse(
            " AND ".join(f"({value})" for value in valid_evidence_expressions),
            validate=True,
            strict=True,
        )
        if not get_spdx_licensing().is_equivalent(package_expression, evidence_expression):
            result.findings.append(
                _finding(
                    "COMMONS_LICENSE_EVIDENCE_CONFLICT",
                    result.name,
                    "blocker",
                    "combined license evidence is not equivalent to package.license",
                    "/license_evidence",
                )
            )
    package_paths = {entry.relative for entry in package_entries}
    if "research-skill.yaml" not in package_paths:
        package_paths.add("research-skill.yaml")
    uncovered_paths = sorted(
        path
        for path in package_paths
        if not any(
            fnmatchcase(path, pattern)
            for item in evidence
            for pattern in item.get("applies_to", [])
        )
    )
    if uncovered_paths:
        result.findings.append(
            _finding(
                "COMMONS_LICENSE_COVERAGE_PARTIAL",
                result.name,
                "blocker",
                "license evidence does not cover: " + ", ".join(uncovered_paths),
                "/license_evidence",
            )
        )
    authorship = manifest["authorship"]
    if authorship["status"] != "verified" or not authorship["contributors"]:
        result.findings.append(
            _finding(
                "COMMONS_AUTHORSHIP_UNRESOLVED",
                result.name,
                "blocker",
                "candidate readiness requires verified authorship",
                "/authorship",
            )
        )
    if manifest["dependencies"]["completeness"] != "complete":
        result.findings.append(
            _finding(
                "COMMONS_DEPENDENCIES_INCOMPLETE",
                result.name,
                "blocker",
                "dependency declaration is not complete",
                "/dependencies/completeness",
            )
        )
    if manifest["capabilities"]["completeness"] != "complete":
        result.findings.append(
            _finding(
                "COMMONS_CAPABILITIES_INCOMPLETE",
                result.name,
                "blocker",
                "capability declaration is not complete",
                "/capabilities/completeness",
            )
        )
    provenance = manifest["provenance"]
    if provenance["origin"] in {"migrated", "derived", "mirror"} and not provenance["upstreams"]:
        result.findings.append(
            _finding(
                "COMMONS_UPSTREAM_MISSING",
                result.name,
                "blocker",
                "migrated, derived, and mirrored packages require an immutable upstream",
                "/provenance/upstreams",
            )
        )
    if provenance["origin"] == "migrated" and provenance["upstreams"]:
        source = package["source"]
        matching_sources = [
            upstream
            for upstream in provenance["upstreams"]
            if upstream["relation"] == "source"
            and all(upstream[key] == source[key] for key in ("repository", "revision", "path"))
        ]
        if len(matching_sources) != 1:
            result.findings.append(
                _finding(
                    "COMMONS_SOURCE_UPSTREAM_MISMATCH",
                    result.name,
                    "blocker",
                    "migrated provenance requires one source upstream matching package.source",
                    "/provenance/upstreams",
                )
            )
    expected_relation = {
        "derived": "derived-from",
        "mirror": "mirrored-from",
    }.get(provenance["origin"])
    if expected_relation is not None and not any(
        upstream["relation"] == expected_relation for upstream in provenance["upstreams"]
    ):
        result.findings.append(
            _finding(
                "COMMONS_UPSTREAM_RELATION_MISMATCH",
                result.name,
                "blocker",
                f"{provenance['origin']} provenance requires a {expected_relation} upstream",
                "/provenance/upstreams",
            )
        )
    for index, upstream in enumerate(provenance["upstreams"]):
        if not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", upstream["revision"]):
            result.findings.append(
                _finding(
                    "COMMONS_UPSTREAM_REVISION_NOT_FULL",
                    result.name,
                    "blocker",
                    "publication requires every upstream to use a full immutable revision",
                    f"/provenance/upstreams/{index}/revision",
                )
            )
    revision = package["source"]["revision"]
    if not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", revision):
        result.findings.append(
            _finding(
                "COMMONS_SOURCE_REVISION_NOT_FULL",
                result.name,
                "blocker",
                "publication requires a full source revision",
                "/package/source/revision",
            )
        )

    for index, contract in enumerate(manifest["validation"]["contracts"]):
        for field in ("input", "expected"):
            if contract[field] not in entry_map:
                result.findings.append(
                    _finding(
                        "COMMONS_CONTRACT_PATH_INVALID",
                        result.name,
                        "blocker",
                        f"contract {field} path is missing or escapes the package",
                        f"/validation/contracts/{index}/{field}",
                    )
                )

    _validate_dependency_lock(manifest, result, entry_map)

    for extension_name, extension in manifest.get("extensions", {}).items():
        expected_schema = KNOWN_EXTENSION_SCHEMAS.get(extension_name)
        if expected_schema is None and extension["required"]:
            result.findings.append(
                _finding(
                    "COMMONS_REQUIRED_EXTENSION_UNKNOWN",
                    result.name,
                    "blocker",
                    f"required extension {extension_name!r} is not locally allowlisted",
                    f"/extensions/{extension_name}",
                )
            )
        elif expected_schema is not None and extension["schema"] != expected_schema:
            result.findings.append(
                _finding(
                    "COMMONS_EXTENSION_SCHEMA_MISMATCH",
                    result.name,
                    "blocker",
                    f"extension {extension_name!r} does not use its pinned schema identifier",
                    f"/extensions/{extension_name}/schema",
                )
            )

    ori_extension = manifest.get("extensions", {}).get("de.aip.ori")
    if ori_extension:
        extension_schema = _load_schema("extensions/de.aip.ori-v1.schema.json")
        for error in sorted(
            jsonschema.Draft202012Validator(extension_schema).iter_errors(ori_extension["data"]),
            key=lambda item: tuple(repr(part) for part in item.absolute_path),
        ):
            pointer = "/extensions/de.aip.ori/data/" + "/".join(
                str(item) for item in error.absolute_path
            )
            result.findings.append(
                _finding(
                    "COMMONS_ORI_EXTENSION_INVALID", result.name, "blocker", error.message, pointer
                )
            )
        if ori_extension["data"].get("unmapped"):
            result.findings.append(
                _finding(
                    "COMMONS_UNMAPPED_LEGACY_FIELDS",
                    result.name,
                    "blocker",
                    "unmapped legacy fields require a disposition",
                    "/extensions/de.aip.ori/data/unmapped",
                )
            )
    return result


def validate_skill(
    skill_dir: Path,
    profiles: Iterable[str],
    snapshot: list[SnapshotEntry] | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    entries = snapshot or snapshot_tree(skill_dir, require_manifest=False)
    entry_map = {entry.relative: entry for entry in entries}
    skill_entry = entry_map.get("SKILL.md")
    if skill_entry is None:
        raise ValueError("package has no root SKILL.md")
    fm, _, _ = parse_skill_text(skill_entry.data.decode("utf-8"))
    manifest_entry = entry_map.get("research-skill.yaml")
    manifest = (
        load_yaml(manifest_entry.data.decode("utf-8")) if manifest_entry is not None else None
    )
    selected = list(profiles)
    results: list[ProfileResult] = []
    if "agent-skills" in selected:
        results.append(validate_agent_skills(skill_dir, fm, skill_entry.data))
    if "ori-compatibility" in selected:
        results.append(validate_ori(skill_dir, fm, manifest))
    if "commons-publication" in selected:
        results.append(validate_publication(skill_dir, fm, manifest, entries))
    try:
        manifest_digest = semantic_digest(manifest) if manifest is not None else None
    except ValueError:
        manifest_digest = None
    report = {
        "report_schema_version": "0.1.0-draft",
        "tool": {"name": "skill-commons", "version": __version__},
        "input": {
            "directory": skill_dir.name,
            "skill_md_digest": sha256_bytes(skill_entry.data),
            "manifest_digest": manifest_digest,
        },
        "profiles": {item.name: item.to_dict() for item in results},
    }
    return report


def report_failed(report: dict[str, Any]) -> bool:
    return any(item["status"] in {"fail", "blocked"} for item in report["profiles"].values())
