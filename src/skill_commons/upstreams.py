"""Verify pinned Git provenance and report changes on upstream default branches."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .io import load_yaml

FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)",
    re.DOTALL,
)
GIT_TIMEOUT_SECONDS = 60


def _git(*args: str, cwd: Path) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GCM_INTERACTIVE": "never",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
        env=environment,
    )
    return completed.stdout.strip()


def _default_branch(checkout: Path) -> str:
    output = _git("ls-remote", "--symref", "origin", "HEAD", cwd=checkout)
    prefix = "ref: refs/heads/"
    suffix = "\tHEAD"
    for line in output.splitlines():
        if line.startswith(prefix) and line.endswith(suffix):
            branch = line[len(prefix) : -len(suffix)]
            if branch:
                return branch
    raise ValueError("upstream repository does not advertise a default branch")


def _object_state(checkout: Path, revision: str, path: str) -> dict[str, Any]:
    expression = f"{revision}:{path}"
    try:
        object_type = _git("cat-file", "-t", expression, cwd=checkout)
    except subprocess.CalledProcessError:
        return {"type": None, "tree": None}
    object_id = _git("rev-parse", "--verify", expression, cwd=checkout)
    return {"type": object_type, "tree": object_id}


def _skill_metadata(checkout: Path, revision: str, path: str) -> dict[str, Any] | None:
    try:
        document = _git("show", f"{revision}:{path}/SKILL.md", cwd=checkout)
    except subprocess.CalledProcessError:
        return None
    match = FRONTMATTER_RE.match(document)
    if match is None:
        return None
    metadata = load_yaml(match.group(1))
    if not isinstance(metadata, dict):
        return None
    return metadata


def _fetch_git_state(
    repository: str,
    branch: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="skill-commons-upstream-") as temporary:
        checkout = Path(temporary)
        _git("init", "--quiet", cwd=checkout)
        _git("remote", "add", "origin", repository, cwd=checkout)
        default_branch = _default_branch(checkout)
        _git(
            "-c",
            "protocol.version=2",
            "fetch",
            "--quiet",
            "--no-tags",
            "--depth=1",
            "--filter=blob:none",
            "origin",
            f"refs/heads/{default_branch}:refs/remotes/origin/default",
            cwd=checkout,
        )
        current_revision = _git(
            "rev-parse",
            "--verify",
            "refs/remotes/origin/default^{commit}",
            cwd=checkout,
        )
        current = {
            record["source"]["path"]: _object_state(
                checkout,
                current_revision,
                record["source"]["path"],
            )
            for record in records
        }

        observed: dict[tuple[str, str], dict[str, Any]] = {}
        by_revision: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            by_revision.setdefault(record["source"]["revision"], []).append(record)
        for revision, revision_records in by_revision.items():
            try:
                _git(
                    "-c",
                    "protocol.version=2",
                    "fetch",
                    "--quiet",
                    "--no-tags",
                    "--depth=1",
                    "--filter=blob:none",
                    "origin",
                    revision,
                    cwd=checkout,
                )
                fetched_revision = _git(
                    "rev-parse",
                    "--verify",
                    "FETCH_HEAD^{commit}",
                    cwd=checkout,
                )
            except subprocess.CalledProcessError:
                fetched_revision = None
            for record in revision_records:
                path = record["source"]["path"]
                key = (revision, path)
                if fetched_revision != revision:
                    observed[key] = {
                        "revision_found": False,
                        "type": None,
                        "tree": None,
                        "metadata": None,
                    }
                    continue
                state = _object_state(checkout, revision, path)
                observed[key] = {
                    "revision_found": True,
                    **state,
                    "metadata": (
                        _skill_metadata(checkout, revision, path)
                        if state["type"] == "tree"
                        else None
                    ),
                }
        return {
            "requested_branch": branch,
            "default_branch": default_branch,
            "current_revision": current_revision,
            "current": current,
            "observed": observed,
        }


def _metadata_issues(record: dict[str, Any], metadata: Any) -> list[str]:
    if not isinstance(metadata, dict):
        return ["pinned source has no readable SKILL.md frontmatter"]
    issues: list[str] = []
    for field in ("name", "description", "version"):
        if metadata.get(field) != record[field]:
            issues.append(
                f"registry {field} does not match pinned SKILL.md "
                f"({record[field]!r} != {metadata.get(field)!r})"
            )
    return issues


def check_upstreams(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Verify reviewed source identity and compare it with each default branch."""

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in catalog["skills"]:
        source = record["source"]
        grouped.setdefault((source["repository"], source["branch"]), []).append(record)

    results: list[dict[str, Any]] = []
    for (repository, branch), records in sorted(grouped.items()):
        state = _fetch_git_state(repository, branch, records)
        for record in records:
            source = record["source"]
            observed = state["observed"][(source["revision"], source["path"])]
            current = state["current"][source["path"]]
            issues: list[str] = []
            if not observed["revision_found"]:
                status = "invalid-revision"
                issues.append("recorded revision could not be fetched")
            elif observed["type"] != "tree":
                status = "invalid-source"
                issues.append("recorded path is not a directory at the recorded revision")
            elif observed["tree"] != source["tree"]:
                status = "invalid-provenance"
                issues.append("recorded tree does not match the recorded revision and path")
            else:
                issues.extend(_metadata_issues(record, observed["metadata"]))
                if issues:
                    status = "metadata-mismatch"
                elif branch != state["default_branch"]:
                    status = "branch-mismatch"
                    issues.append(
                        f"tracked branch {branch!r} is not the upstream default "
                        f"{state['default_branch']!r}"
                    )
                elif current["type"] is None:
                    status = "missing"
                    issues.append("registered path is absent from the current default branch")
                elif current["type"] != "tree":
                    status = "invalid-source"
                    issues.append("registered path is no longer a directory")
                elif current["tree"] != source["tree"]:
                    status = "changed"
                    issues.append("upstream skill directory changed since review")
                else:
                    status = "current"
            results.append(
                {
                    "name": record["name"],
                    "status": status,
                    "issues": issues,
                    "repository": repository,
                    "branch": branch,
                    "default_branch": state["default_branch"],
                    "observed_revision": source["revision"],
                    "current_revision": state["current_revision"],
                    "observed_tree": source["tree"],
                    "verified_observed_tree": observed["tree"],
                    "current_tree": current["tree"],
                }
            )
    return results
