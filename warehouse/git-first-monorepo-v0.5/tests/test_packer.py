from __future__ import annotations

import os
import shutil
import tarfile
from pathlib import Path

import pytest

from skill_commons.packer import SnapshotEntry, pack_directory, pack_snapshot, snapshot_tree

ROOT = Path(__file__).resolve().parents[1]
VALID_SKILL = ROOT / "tests" / "fixtures" / "valid" / "catalog-query-demo"


def test_packer_is_deterministic_across_mtimes_and_directories(tmp_path: Path) -> None:
    source = VALID_SKILL
    one = tmp_path / "one"
    two = tmp_path / "two"
    shutil.copytree(source, one)
    shutil.copytree(source, two)
    for path in two.rglob("*"):
        if path.is_file():
            os.utime(path, (1_234_567_890, 1_234_567_890))
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    assert pack_directory(one, first) == pack_directory(two, second)
    assert first.read_bytes() == second.read_bytes()


def test_packer_rejects_symlinks(tmp_path: Path) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    (package / "escape").symlink_to("/etc/passwd")
    with pytest.raises(ValueError, match="symlink"):
        pack_directory(package, tmp_path / "bad.tar.gz")


def test_packer_rejects_secret_bearing_paths_instead_of_silently_dropping_them(
    tmp_path: Path,
) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    (package / ".env").write_text("EXAMPLE=not-a-real-secret\n")
    with pytest.raises(ValueError, match="secret-bearing"):
        pack_directory(package, tmp_path / "bad.tar.gz")


def test_packer_preserves_only_the_executable_class(tmp_path: Path) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    script = package / "run.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    script.chmod(0o751)
    output = tmp_path / "package.tar.gz"

    pack_directory(package, output)

    with tarfile.open(output, "r:gz") as archive:
        assert archive.getmember("run.sh").mode == 0o755
        assert archive.getmember("SKILL.md").mode == 0o644


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO creation is POSIX-only")
def test_packer_rejects_non_regular_entries_without_opening_them(tmp_path: Path) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    os.mkfifo(package / "input.pipe")

    with pytest.raises(ValueError, match="non-regular"):
        pack_directory(package, tmp_path / "bad.tar.gz")


def test_packer_rejects_oversize_files_before_writing_output(tmp_path: Path) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    (package / "large.bin").write_bytes(b"12345")
    output = tmp_path / "bad.tar.gz"

    with pytest.raises(ValueError, match="size limit"):
        snapshot_tree(package, max_file_bytes=4)
    assert not output.exists()


def test_snapshot_rejects_entry_count_bombs(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_text("---\nname: package\ndescription: test\n---\n")
    (package / "research-skill.yaml").write_text("schema_version: 0.1.0-draft\n")
    (package / "empty").touch()

    from skill_commons.packer import snapshot_tree

    with pytest.raises(ValueError, match="entry-count limit"):
        snapshot_tree(package, max_entries=2)


def test_packer_refuses_to_overwrite_an_existing_artifact(tmp_path: Path) -> None:
    output = tmp_path / "existing.tar.gz"
    output.write_bytes(b"keep me")
    with pytest.raises(ValueError, match="overwrite"):
        pack_directory(VALID_SKILL, output)
    assert output.read_bytes() == b"keep me"


@pytest.mark.parametrize(
    "name, message",
    [
        ("..\\escape", "backslashes"),
        ("C:/escape.txt", "Windows"),
        ("a" * 101, "USTAR"),
    ],
)
def test_packer_rejects_cross_platform_traversal_and_unencodable_names(
    tmp_path: Path, name: str, message: str
) -> None:
    package = tmp_path / "package"
    shutil.copytree(VALID_SKILL, package)
    unsafe = package / name
    unsafe.parent.mkdir(parents=True, exist_ok=True)
    unsafe.write_text("unsafe archive name\n")

    with pytest.raises(ValueError, match=message):
        pack_directory(package, tmp_path / "bad.tar.gz")


@pytest.mark.parametrize(
    "name",
    ["../escape", "/absolute", "C:/escape.txt", "safe.txt:stream", "./normalized"],
)
def test_pack_snapshot_cannot_bypass_path_validation(tmp_path: Path, name: str) -> None:
    entries = snapshot_tree(VALID_SKILL)
    entries.append(SnapshotEntry(name, b"unsafe\n", False))

    with pytest.raises(ValueError, match="package|Windows"):
        pack_snapshot(entries, tmp_path / "bad.tar.gz")
