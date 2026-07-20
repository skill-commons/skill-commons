"""Source-pinned, metadata-minimizing corpus survey."""

from __future__ import annotations

import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from . import __version__
from .io import parse_skill_text, sha256_bytes
from .validation import validate_agent_skills


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _git_object(root: Path, revision: str, path: str) -> str:
    return _git(root, "rev-parse", f"{revision}:{path}")


def _git_bytes(root: Path, revision: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), "show", f"{revision}:{path}"],
        check=True,
        capture_output=True,
    )
    return completed.stdout


def survey_repository(
    root: Path,
    *,
    source_url: str,
    expected_revision: str,
) -> dict[str, Any]:
    root = root.resolve()
    revision = _git(root, "rev-parse", "HEAD")
    if revision != expected_revision:
        raise ValueError(f"expected revision {expected_revision}, found {revision}")
    dirty = _git(root, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise ValueError("survey source worktree or index is dirty")
    tracked_paths = _git(root, "ls-tree", "-r", "--name-only", revision).splitlines()
    relative_paths = sorted(path for path in tracked_paths if path.endswith("/SKILL.md"))
    observations: list[dict[str, Any]] = []
    key_frequency: Counter[str] = Counter()
    reference_passes: list[str] = []
    active = 0
    parked = 0
    no_per_skill_license = 0
    for relative in relative_paths:
        expected_blob = _git_object(root, revision, relative)
        skill_bytes = _git_bytes(root, revision, relative)
        state = "parked" if relative.startswith("outdated-skills/") else "active"
        if state == "active":
            active += 1
        else:
            parked += 1
        source_skill_dir = Path(relative).parent
        fm, body, _ = parse_skill_text(skill_bytes.decode("utf-8"))
        for key in fm:
            key_frequency[str(key)] += 1
        license_value = fm.get("license")
        if license_value is None and state == "active":
            no_per_skill_license += 1
        with tempfile.TemporaryDirectory(prefix="skill-commons-survey-") as temporary:
            skill_dir = Path(temporary) / source_skill_dir.name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_bytes(skill_bytes)
            profile = validate_agent_skills(skill_dir, fm)
        reference_status = profile.details["reference_status"]
        if state == "active" and reference_status == "pass":
            reference_passes.append(source_skill_dir.as_posix())
        observations.append(
            {
                "path": relative,
                "source_state": state,
                "skill_md_git_blob": expected_blob,
                "skill_tree_git_oid": _git_object(root, revision, source_skill_dir.as_posix()),
                "skill_md_sha256": sha256_bytes(skill_bytes),
                "frontmatter_keys": sorted(str(key) for key in fm),
                "frontmatter_types": {
                    str(key): type(value).__name__
                    for key, value in sorted(fm.items(), key=lambda item: repr(item[0]))
                },
                "description_length": len(fm.get("description", ""))
                if isinstance(fm.get("description"), str)
                else None,
                "body_lines": body.count("\n") + 1,
                "name_matches_directory": fm.get("name") == source_skill_dir.name,
                "per_skill_license_signal": (
                    "none"
                    if license_value is None
                    else "MIT"
                    if license_value == "MIT"
                    else "declared-other"
                ),
                "agent_skills_normative_status": profile.details["normative_status"],
                "skills_ref_0_1_1_status": reference_status,
                "diagnostic_codes": sorted({finding.code for finding in profile.findings}),
            }
        )
    return {
        "fixture_schema_version": "0.1.0-draft",
        "generator": {"name": "skill-commons", "version": __version__},
        "source_lock": {
            "repository": source_url,
            "revision": revision,
            "root_tree": _git(root, "rev-parse", f"{revision}^{{tree}}"),
            "license_blob": _git_object(root, revision, "LICENSE"),
            "citation_blob": _git_object(root, revision, "CITATION.cff"),
            "include": ["**/SKILL.md"],
            "parked_prefix": "outdated-skills/",
        },
        "summary": {
            "active_skills": active,
            "parked_skills": parked,
            "no_per_skill_license_declaration_active": no_per_skill_license,
            "skills_ref_0_1_1_pass_active": len(reference_passes),
            "skills_ref_0_1_1_passing_paths": sorted(reference_passes),
            "frontmatter_key_frequency_all": dict(sorted(key_frequency.items())),
        },
        "observations": observations,
        "rights_notice": (
            "Factual structural observations only. This fixture does not copy skill bodies, "
            "assert publication rights, or conclude that a root license covers imported material."
        ),
    }
