"""Reproducible preparation and catalog finalization for curated releases."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import tomllib
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema
from packaging.utils import canonicalize_name

from . import __version__
from .catalog import _catalog_schema, build_catalog_snapshot
from .io import dump_yaml, load_json_file, load_yaml_file, parse_skill_text, semantic_digest
from .packer import SnapshotEntry, pack_snapshot, snapshot_tree
from .validation import report_failed, validate_skill

ATTESTATION_TYPES = (
    "https://aip.de/skill-commons/validation/v1",
    "https://aip.de/skill-commons/contract-test/v1",
    "https://aip.de/skill-commons/preinstall-inventory/v1",
    "https://aip.de/skill-commons/policy-result/v1",
    "https://aip.de/skill-commons/static-scan/v1",
    "https://aip.de/skill-commons/provenance/v1",
    "https://aip.de/skill-commons/spdx/v1",
)


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"refusing to overwrite existing output: {path}")
    path.write_bytes(data)


def _safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"unsafe release path: {value!r}")
    return path


def _run_git(repository: Path, *arguments: str, text: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=text,
    )
    return result.stdout


def _source_entries(recipe: dict[str, Any], repository: Path) -> list[SnapshotEntry]:
    source = recipe["source"]
    revision = source["revision"]
    source_path = _safe_relative(source["path"]).as_posix()
    resolved = str(_run_git(repository, "rev-parse", f"{revision}^{{commit}}", text=True)).strip()
    if resolved != revision:
        raise ValueError(f"source revision mismatch: expected {revision}, resolved {resolved}")
    tree_oid = str(
        _run_git(repository, "rev-parse", f"{revision}:{source_path}", text=True)
    ).strip()
    if tree_oid != source["tree_oid"]:
        raise ValueError(f"source tree OID mismatch: expected {source['tree_oid']}, got {tree_oid}")

    listing = bytes(
        _run_git(repository, "ls-tree", "-r", "-z", "--full-tree", revision, source_path)
    )
    observed: dict[str, tuple[str, bool]] = {}
    prefix = source_path + "/"
    for record in listing.rstrip(b"\0").split(b"\0") if listing else []:
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split(" ")
        full_path = raw_path.decode("utf-8")
        if kind != "blob" or not full_path.startswith(prefix):
            raise ValueError(f"unsupported source tree entry: {full_path}")
        relative = full_path[len(prefix) :]
        _safe_relative(relative)
        observed[relative] = (oid, mode == "100755")

    expected = {item["path"]: item for item in source["files"]}
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        unexpected = sorted(set(observed) - set(expected))
        raise ValueError(f"source file set mismatch; missing={missing}, unexpected={unexpected}")

    entries: list[SnapshotEntry] = []
    for relative in sorted(expected, key=lambda value: value.encode("utf-8")):
        item = expected[relative]
        oid, executable = observed[relative]
        if oid != item["blob_oid"]:
            raise ValueError(
                f"source blob OID mismatch for {relative}: expected {item['blob_oid']}, got {oid}"
            )
        data = bytes(_run_git(repository, "show", f"{revision}:{source_path}/{relative}"))
        digest = _sha256_bytes(data)
        if digest != item["digest"]:
            raise ValueError(
                f"source byte digest mismatch for {relative}: "
                f"expected {item['digest']}, got {digest}"
            )
        entries.append(SnapshotEntry(relative=relative, data=data, executable=executable))

    tree_digest = semantic_digest(
        [
            {
                "path": entry.relative,
                "digest": _sha256_bytes(entry.data),
                "executable": entry.executable,
            }
            for entry in entries
        ]
    )
    if tree_digest != source["tree_digest"]:
        raise ValueError(
            f"source tree digest mismatch: expected {source['tree_digest']}, got {tree_digest}"
        )
    return entries


def _build_lock(
    recipe: dict[str, Any], manifest: dict[str, Any], recipe_dir: Path
) -> dict[str, Any]:
    lock_input = recipe["dependency_lock"]
    path = recipe_dir / _safe_relative(lock_input["input"])
    data = path.read_bytes()
    if _sha256_bytes(data) != lock_input["digest"]:
        raise ValueError("pylock input digest mismatch")
    parsed = tomllib.loads(data.decode("utf-8"))
    direct = {canonicalize_name(name) for name in lock_input["direct"]}
    packages: list[dict[str, Any]] = []
    for package in parsed["packages"]:
        name = canonicalize_name(package["name"])
        wheels = package.get("wheels", [])
        if len(wheels) != 1:
            raise ValueError(f"pylock must retain exactly one selected wheel for {name}")
        wheel = wheels[0]
        packages.append(
            {
                "name": name,
                "version": str(package["version"]),
                "direct": name in direct,
                "source": {"kind": "index", "url": f"https://pypi.org/simple/{name}/"},
                "artifact": {"url": wheel["url"], "sha256": wheel["hashes"]["sha256"]},
            }
        )
    if {item["name"] for item in packages if item["direct"]} != direct:
        raise ValueError("direct dependency set is not fully represented in pylock")
    target = lock_input["target"]
    return {
        "schema_version": "0.1.0-draft",
        "package": {"coordinate": recipe["coordinate"], "version": recipe["version"]},
        "manifest_digest": semantic_digest(manifest),
        "resolutions": [
            {
                "id": target["id"],
                "target": {
                    "operating_system": target["operating_system"],
                    "architecture": target["architecture"],
                    "python_implementation": target["python_implementation"],
                    "python_version": target["python_version"],
                },
                "resolver": lock_input["resolver"],
                "requirements_digest": semantic_digest(manifest["dependencies"]),
                "python": sorted(packages, key=lambda item: item["name"]),
                "system": [],
                "containers": [],
            }
        ],
    }


def _run_static_contract(package_dir: Path) -> dict[str, Any]:
    contract = load_json_file(package_dir / "contracts/static-content.json")
    expected = load_json_file(package_dir / "contracts/static-content.expected.json")
    checks: list[dict[str, Any]] = []
    for relative, rules in contract["files"].items():
        _safe_relative(relative)
        text = (package_dir / relative).read_text(encoding="utf-8")
        for value in rules.get("required_strings", []):
            checks.append(
                {
                    "kind": "required-string",
                    "path": relative,
                    "value_digest": _sha256_bytes(value.encode("utf-8")),
                    "status": "pass" if value in text else "fail",
                }
            )
    package_text = "\n".join(
        entry.data.decode("utf-8") for entry in snapshot_tree(package_dir) if _is_utf8(entry.data)
    )
    for pattern in contract.get("forbidden_patterns", []):
        matches = bool(re.search(pattern, package_text))
        checks.append(
            {
                "kind": "forbidden-pattern",
                "pattern_digest": _sha256_bytes(pattern.encode("utf-8")),
                "status": "fail" if matches else "pass",
            }
        )
    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    if status != expected["status"]:
        raise ValueError(f"static contract expected {expected['status']}, observed {status}")
    return {
        "schema_version": "0.1.0-draft",
        "contract_id": "static-content-v1",
        "status": status,
        "checks": checks,
    }


def _is_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _inventory(
    recipe: dict[str, Any],
    manifest: dict[str, Any],
    lock: dict[str, Any],
    entries: list[SnapshotEntry],
) -> dict[str, Any]:
    skill = next(entry for entry in entries if entry.relative == "SKILL.md")
    metadata_tokens = (len(dump_yaml(recipe["portable_frontmatter"]).encode("utf-8")) + 3) // 4
    instruction_tokens = (len(skill.data) + 3) // 4
    return {
        "schema_version": "0.1.0-draft",
        "coordinate": recipe["coordinate"],
        "version": recipe["version"],
        "files": [
            {
                "path": entry.relative,
                "digest": _sha256_bytes(entry.data),
                "size": len(entry.data),
                "executable": entry.executable,
            }
            for entry in entries
        ],
        "dependencies": {
            "declared": manifest["dependencies"],
            "resolution": lock["resolutions"][0],
        },
        "capabilities": manifest["capabilities"],
        "context_budget": {
            "metadata_tokens": metadata_tokens,
            "instruction_tokens": instruction_tokens,
            "estimator": "utf8-byte-ceiling-divide-by-four",
            "version": "1",
            "encoding": "utf-8",
        },
        "install_mutations": {
            "package_files": len(entries),
            "python_packages": len(lock["resolutions"][0]["python"]),
            "system_packages": 0,
            "containers": 0,
        },
    }


def _policy_result(recipe: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0-draft",
        "coordinate": recipe["coordinate"],
        "version": recipe["version"],
        "decision": "allow-with-conditions",
        "conditions": [
            "restrict-network-egress-to-declared-hosts",
            "gaia-token-is-user-supplied-optional-and-must-never-enter-package-or-logs",
            "require-user-approval-before-submitting-long-running-tap-jobs",
            "preserve-rel-version-and-sha256-evidence-tags-and-live-check-them",
            "acceptance-gate-4-publisher-isolation-remains-open",
            "acceptance-gate-5-backup-restore-remains-open",
        ],
        "open_gates": [4, 5],
        "gate_status": recipe["acceptance_gates"],
        "authority": "local-install-policy; signed-catalog-required-for-release-authority",
    }


def _sbom(
    recipe: dict[str, Any], lock: dict[str, Any], entries: list[SnapshotEntry], artifact_digest: str
) -> dict[str, Any]:
    document_id = artifact_digest.removeprefix("sha256:")
    file_records = []
    relationships = []
    for index, entry in enumerate(entries, start=1):
        spdx_id = f"SPDXRef-File-{index}"
        file_records.append(
            {
                "SPDXID": spdx_id,
                "fileName": f"./{entry.relative}",
                "checksums": [
                    {"algorithm": "SHA256", "checksumValue": _sha256_bytes(entry.data)[7:]}
                ],
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-Package",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": spdx_id,
            }
        )
    dependency_records = []
    for index, package in enumerate(lock["resolutions"][0]["python"], start=1):
        spdx_id = f"SPDXRef-Python-{index}"
        dependency_records.append(
            {
                "SPDXID": spdx_id,
                "name": package["name"],
                "versionInfo": package["version"],
                "downloadLocation": package["artifact"]["url"],
                "checksums": [
                    {"algorithm": "SHA256", "checksumValue": package["artifact"]["sha256"]}
                ],
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-Package",
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": spdx_id,
            }
        )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{recipe['coordinate']}@{recipe['version']}",
        "documentNamespace": f"https://skill-commons.aip.de/spdx/{document_id}",
        "creationInfo": {
            "created": recipe["created"],
            "creators": [f"Tool: skill-commons-{__version__}"],
        },
        "packages": [
            {
                "SPDXID": "SPDXRef-Package",
                "name": recipe["coordinate"],
                "versionInfo": recipe["version"],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": True,
                "licenseConcluded": "MIT",
                "licenseDeclared": "MIT",
                "checksums": [{"algorithm": "SHA256", "checksumValue": artifact_digest[7:]}],
            },
            *dependency_records,
        ],
        "files": file_records,
        "relationships": relationships,
    }


def prepare_release(recipe_path: Path, source_repository: Path, output: Path) -> dict[str, Any]:
    """Materialize immutable Git input, validate it, and emit deterministic release inputs."""

    recipe_path = recipe_path.resolve(strict=True)
    recipe = load_yaml_file(recipe_path)
    if recipe.get("schema_version") != "0.1.0-draft":
        raise ValueError("unsupported publication recipe schema")
    if output.exists():
        raise ValueError(f"refusing to overwrite existing release output: {output}")
    output.mkdir(parents=True)
    package_dir = output / "package" / recipe["manifest"]["package"]["name"]
    package_dir.mkdir(parents=True)
    recipe_dir = recipe_path.parent

    source_entries = _source_entries(recipe, source_repository.resolve(strict=True))
    for entry in source_entries:
        data = entry.data
        if entry.relative == "SKILL.md":
            _, body, _ = parse_skill_text(data.decode("utf-8"))
            data = ("---\n" + dump_yaml(recipe["portable_frontmatter"]) + "---\n" + body).encode(
                "utf-8"
            )
        _write(package_dir / entry.relative, data)

    for overlay in recipe["overlays"]:
        source = recipe_dir / _safe_relative(overlay["source"])
        destination = package_dir / _safe_relative(overlay["path"])
        data = source.read_bytes()
        if _sha256_bytes(data) != overlay["digest"]:
            raise ValueError(f"overlay digest mismatch: {overlay['source']}")
        _write(destination, data)

    manifest = recipe["manifest"]
    _write(package_dir / "research-skill.yaml", dump_yaml(manifest).encode("utf-8"))
    lock = _build_lock(recipe, manifest, recipe_dir)
    _write(package_dir / "research-skill.lock", dump_yaml(lock).encode("utf-8"))

    contract_report = _run_static_contract(package_dir)
    validation = validate_skill(package_dir, ["agent-skills", "commons-publication"])
    if report_failed(validation):
        raise ValueError("materialized package failed publication validation")

    entries = snapshot_tree(package_dir)
    artifact = output / f"{recipe['manifest']['package']['name']}-{recipe['version']}.tar.gz"
    repeated = output / f".{artifact.name}.repeat"
    artifact_digest = pack_snapshot(entries, artifact)
    repeated_digest = pack_snapshot(entries, repeated)
    if artifact_digest != repeated_digest or artifact.read_bytes() != repeated.read_bytes():
        raise ValueError("deterministic pack check failed")
    repeated.unlink()

    inventory = _inventory(recipe, manifest, lock, entries)
    policy = _policy_result(recipe)
    static_scan = {
        "schema_version": "0.1.0-draft",
        "status": contract_report["status"],
        "scope": (
            "package paths and conservative credential-pattern scan; "
            "not dependency vulnerability analysis"
        ),
        "files_scanned": len(entries),
        "findings": [],
    }
    provenance = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": artifact.name, "digest": {"sha256": artifact_digest[7:]}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://aip.de/skill-commons/deterministic-pack/v1",
                "externalParameters": {
                    "coordinate": recipe["coordinate"],
                    "version": recipe["version"],
                    "created": recipe["created"],
                },
                "resolvedDependencies": [
                    {
                        "uri": recipe["source"]["repository"],
                        "digest": {
                            "gitCommit": recipe["source"]["revision"],
                            "sha256": recipe["source"]["tree_digest"][7:],
                        },
                    }
                ],
            },
            "runDetails": {
                "builder": {"id": "https://gitlab-p4n.aip.de/physicsllm/skill-commons/spec"},
                "metadata": {"invocationId": artifact_digest},
            },
        },
    }
    evidence = output / "evidence"
    evidence.mkdir()
    records = {
        "validation.json": validation,
        "contract-report.json": contract_report,
        "inventory.json": inventory,
        "policy-result.json": policy,
        "static-scan.json": static_scan,
        "provenance.intoto.json": provenance,
        "sbom.spdx.json": _sbom(recipe, lock, entries, artifact_digest),
    }
    evidence_digests: dict[str, str] = {}
    for name, record in records.items():
        payload = _json_bytes(record)
        _write(evidence / name, payload)
        evidence_digests[name] = _sha256_bytes(payload)

    receipt = {
        "schema_version": "0.1.0-draft",
        "coordinate": recipe["coordinate"],
        "version": recipe["version"],
        "source": recipe["source"],
        "manifest_digest": semantic_digest(manifest),
        "lock_digest": _sha256_bytes((package_dir / "research-skill.lock").read_bytes()),
        "artifact": {
            "path": artifact.name,
            "digest": artifact_digest,
            "size": artifact.stat().st_size,
        },
        "deterministic_pack": {"runs": 2, "status": "pass", "digest": artifact_digest},
        "validation_status": {
            name: value["status"] for name, value in validation["profiles"].items()
        },
        "evidence": evidence_digests,
        "open_gates": [4, 5],
    }
    _write(output / "prepare-receipt.json", _json_bytes(receipt))
    return receipt


def finalize_catalog(
    recipe_path: Path,
    prepared: Path,
    repository: str,
    oci_digest: str,
    signature_digest: str,
    attestation_digest: str,
    output: Path,
) -> dict[str, Any]:
    """Bind live OCI and evidence descriptors into an authoritative catalog candidate."""

    recipe = load_yaml_file(recipe_path.resolve(strict=True))
    receipt = load_json_file(prepared / "prepare-receipt.json")
    inventory = load_json_file(prepared / "evidence/inventory.json")
    assertion_digest = recipe["rights_assertion"]["digest"]
    if repository != recipe["registry"]["primary"]:
        raise ValueError("catalog repository differs from publication recipe primary")
    for value in (oci_digest, signature_digest, attestation_digest):
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
            raise ValueError(f"invalid OCI descriptor digest: {value}")
    release = {
        "coordinate": recipe["coordinate"],
        "version": recipe["version"],
        "artifact": {
            "repository": repository,
            "digest": oci_digest,
            "media_type": recipe["registry"]["layer_media_type"],
            "size": receipt["artifact"]["size"],
        },
        "manifest_digest": receipt["manifest_digest"],
        "source": recipe["manifest"]["package"]["source"],
        "release_state": "active",
        "description": recipe["portable_frontmatter"]["description"],
        "license": recipe["manifest"]["package"]["license"],
        "compatibility": recipe["manifest"]["compatibility"],
        "capability_summary": recipe["manifest"]["capabilities"],
        "context_budget": inventory["context_budget"],
        "assessments": {
            "license": "verified",
            "publisher_authority": "verified",
            "namespace_control": "verified",
            "redaction": "verified",
            "source_relation": "derived",
        },
        "assessment_evidence": {
            "license": assertion_digest,
            "publisher_authority": assertion_digest,
            "namespace_control": assertion_digest,
            "redaction": assertion_digest,
        },
        "validation_profiles": receipt["validation_status"],
        "evidence": sorted([signature_digest, attestation_digest]),
    }
    catalog = recipe["catalog"]
    snapshot = build_catalog_snapshot(
        [release],
        sequence=catalog["sequence"],
        generated_at=catalog["generated_at"],
        expires_at=catalog["expires_at"],
        previous_snapshot_digest=None,
        negative_sequence=catalog["negative_sequence"],
        negative_records=[],
    )
    output.mkdir(parents=True, exist_ok=True)
    _write(output / "release-record.json", _json_bytes(release))
    _write(output / "catalog.json", _json_bytes(snapshot))
    status = {
        "schema_version": "0.1.0-draft",
        "release": f"{recipe['coordinate']}@{recipe['version']}",
        "subject": {"repository": repository, "digest": oci_digest},
        "evidence_tags": {
            f"sha256-{oci_digest[7:]}.sig": signature_digest,
            f"sha256-{oci_digest[7:]}.att": attestation_digest,
        },
        "catalog_digest": _sha256_bytes((output / "catalog.json").read_bytes()),
        "gate_status": recipe["acceptance_gates"],
        "open_gates": [4, 5],
    }
    _write(output / "publication-status.json", _json_bytes(status))
    return status


def _run_checked(*arguments: str) -> str:
    result = subprocess.run(arguments, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def verify_published_release(
    catalog_path: Path,
    catalog_signature: Path,
    public_key: Path,
    prepare_receipt_path: Path,
    coordinate: str,
    version: str,
    mirror: str | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify signed catalog authority and all referenced live registry state."""

    catalog_path = catalog_path.resolve(strict=True)
    catalog_signature = catalog_signature.resolve(strict=True)
    public_key = public_key.resolve(strict=True)
    prepare_receipt = load_json_file(prepare_receipt_path.resolve(strict=True))
    catalog = load_json_file(catalog_path)
    _run_checked(
        "cosign",
        "verify-blob",
        "--key",
        str(public_key),
        "--insecure-ignore-tlog=true",
        "--signature",
        str(catalog_signature),
        str(catalog_path),
    )
    jsonschema.Draft202012Validator(
        _catalog_schema(), format_checker=jsonschema.FormatChecker()
    ).validate(catalog)
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        raise ValueError("catalog verification time must include a timezone")
    generated = datetime.fromisoformat(catalog["generated_at"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(catalog["expires_at"].replace("Z", "+00:00"))
    if generated > current:
        raise ValueError("catalog generated_at is in the future")
    if current >= expires:
        raise ValueError("catalog has expired")
    if catalog["sequence"] == 1 and catalog["previous_snapshot_digest"] is not None:
        raise ValueError("catalog sequence 1 must not name a previous snapshot")
    expected_input_digest = semantic_digest(
        {
            "releases": catalog["releases"],
            "negative_state": catalog["negative_state"]["records"],
        }
    )
    if catalog["input_digest"] != expected_input_digest:
        raise ValueError("catalog input_digest does not bind its release and negative state")
    matches = [
        item
        for item in catalog["releases"]
        if item["coordinate"] == coordinate and item["version"] == version
    ]
    if len(matches) != 1:
        raise ValueError(f"catalog must contain exactly one {coordinate}@{version} release")
    release = matches[0]
    repository = release["artifact"]["repository"]
    subject_digest = release["artifact"]["digest"]
    release_tag = f"rel-{version}"
    if _run_checked("oras", "resolve", f"{repository}:{release_tag}") != subject_digest:
        raise ValueError("persistent release tag does not resolve to the catalog subject")
    prefix = f"sha256-{subject_digest[7:]}"
    evidence_tags = {suffix: f"{prefix}.{suffix}" for suffix in ("sig", "att")}
    live_evidence = {
        suffix: _run_checked("oras", "resolve", f"{repository}:{tag}")
        for suffix, tag in evidence_tags.items()
    }
    if set(live_evidence.values()) != set(release["evidence"]):
        raise ValueError("live evidence descriptors differ from the signed catalog")
    subject = f"{repository}@{subject_digest}"
    _run_checked(
        "cosign", "verify", "--key", str(public_key), "--insecure-ignore-tlog=true", subject
    )
    for predicate_type in ATTESTATION_TYPES:
        _run_checked(
            "cosign",
            "verify-attestation",
            "--key",
            str(public_key),
            "--insecure-ignore-tlog=true",
            "--type",
            predicate_type,
            subject,
        )

    artifact_name = prepare_receipt["artifact"]["path"]
    artifact_digest = prepare_receipt["artifact"]["digest"]
    with tempfile.TemporaryDirectory(prefix="skill-commons-verify-") as temporary:
        _run_checked("oras", "pull", subject, "-o", temporary)
        pulled_digest = _sha256_bytes((Path(temporary) / artifact_name).read_bytes())
    if pulled_digest != artifact_digest:
        raise ValueError("pulled package bytes differ from the preparation receipt")

    mirror_result: dict[str, Any] | None = None
    if mirror is not None:
        if _run_checked("oras", "resolve", f"{mirror}:{release_tag}") != subject_digest:
            raise ValueError("mirror release tag does not resolve to the catalog subject")
        for suffix, tag in evidence_tags.items():
            descriptor = _run_checked("oras", "resolve", f"{mirror}:{tag}")
            if descriptor != live_evidence[suffix]:
                raise ValueError(f"mirror {suffix} evidence descriptor differs from primary")
        mirror_subject = f"{mirror}@{subject_digest}"
        _run_checked(
            "cosign",
            "verify",
            "--key",
            str(public_key),
            "--insecure-ignore-tlog=true",
            mirror_subject,
        )
        for predicate_type in ATTESTATION_TYPES:
            _run_checked(
                "cosign",
                "verify-attestation",
                "--key",
                str(public_key),
                "--insecure-ignore-tlog=true",
                "--type",
                predicate_type,
                mirror_subject,
            )
        mirror_result = {"repository": mirror, "status": "pass"}

    return {
        "schema_version": "0.1.0-draft",
        "coordinate": coordinate,
        "version": version,
        "catalog": {
            "digest": _sha256_bytes(catalog_path.read_bytes()),
            "signature": "pass",
            "schema": "pass",
            "freshness": "pass",
            "input_digest": "pass",
            "sequence": catalog["sequence"],
            "expires_at": catalog["expires_at"],
        },
        "subject": {"repository": repository, "digest": subject_digest},
        "release_tag": {"name": release_tag, "status": "pass"},
        "evidence": {"descriptors": live_evidence, "attestation_types": len(ATTESTATION_TYPES)},
        "package_digest": artifact_digest,
        "mirror": mirror_result,
        "status": "pass",
    }
