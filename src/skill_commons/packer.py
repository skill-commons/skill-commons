"""Deterministic, race-resistant package snapshot and archive builder."""

from __future__ import annotations

import gzip
import hashlib
import io
import os
import stat
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

DEFAULT_MAX_FILE_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_ENTRIES = 10_000
DENIED_NAMES = {".git", ".netrc", ".npmrc", ".pypirc", ".secrets", "credentials"}


@dataclass(frozen=True)
class SnapshotEntry:
    """One immutable input captured before any output is written."""

    relative: str
    data: bytes
    executable: bool


def _denied(relative: Path) -> bool:
    return any(
        part in DENIED_NAMES or part == ".env" or part.startswith(".env.")
        for part in relative.parts
    )


def _validate_archive_path(relative: Path | PurePosixPath) -> None:
    value = relative.as_posix()
    if "\\" in value:
        raise ValueError(f"backslashes are not allowed in package paths: {relative}")
    if PureWindowsPath(value).drive or ":" in value:
        raise ValueError(
            f"Windows drive or alternate-stream syntax is not allowed in package paths: {relative}"
        )
    try:
        tarfile.TarInfo(value).tobuf(format=tarfile.USTAR_FORMAT, encoding="utf-8", errors="strict")
    except (UnicodeError, ValueError) as exc:
        raise ValueError(f"package path is not representable in USTAR: {relative}") from exc


def _read_regular_file(
    directory_fd: int, name: str, relative: Path, max_file_bytes: int
) -> tuple[bytes, bool]:
    before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        kind = "symlink" if stat.S_ISLNK(before.st_mode) else "non-regular package entry"
        raise ValueError(f"{kind}: {relative}")
    if before.st_size > max_file_bytes:
        raise ValueError(f"package file exceeds size limit: {relative}")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    descriptor = os.open(name, flags, dir_fd=directory_fd)
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError(f"package entry changed while being opened: {relative}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            data = handle.read(max_file_bytes + 1)
        after_open = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    if len(data) > max_file_bytes:
        raise ValueError(f"package file exceeds size limit: {relative}")
    after_path = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    observed_before = (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
    observed_after_open = (
        after_open.st_dev,
        after_open.st_ino,
        after_open.st_size,
        after_open.st_mtime_ns,
    )
    observed_after_path = (
        after_path.st_dev,
        after_path.st_ino,
        after_path.st_size,
        after_path.st_mtime_ns,
    )
    if observed_before != observed_after_open or observed_before != observed_after_path:
        raise ValueError(f"package entry changed while being read: {relative}")
    if len(data) != opened.st_size:
        raise ValueError(f"package entry size changed while being read: {relative}")
    return data, bool(opened.st_mode & 0o111)


def snapshot_tree(
    root: Path,
    *,
    require_manifest: bool = True,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_entries: int = DEFAULT_MAX_ENTRIES,
) -> list[SnapshotEntry]:
    """Capture a checked tree once so later packaging never reopens source files."""

    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"package root is not a directory: {root}")
    entries: list[SnapshotEntry] = []
    entry_count = 0
    total = 0
    if not hasattr(os, "fwalk"):
        raise ValueError("secure descriptor-relative package traversal is unavailable")
    for directory, directories, files, directory_fd in os.fwalk(
        root, topdown=True, follow_symlinks=False
    ):
        relative_directory = Path(directory).relative_to(root)
        directories.sort(key=lambda value: value.encode("utf-8"))
        files.sort(key=lambda value: value.encode("utf-8"))
        for name in directories:
            entry_count += 1
            if entry_count > max_entries:
                raise ValueError("package exceeds entry-count limit")
            relative = relative_directory / name
            _validate_archive_path(relative)
            if _denied(relative):
                raise ValueError(f"secret-bearing or VCS-control path is not allowed: {relative}")
            mode = os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink: {relative}")
            if not stat.S_ISDIR(mode):
                raise ValueError(f"non-directory traversal entry: {relative}")
        for name in files:
            entry_count += 1
            if entry_count > max_entries:
                raise ValueError("package exceeds entry-count limit")
            relative = relative_directory / name
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe package path: {relative}")
            _validate_archive_path(relative)
            if _denied(relative):
                raise ValueError(f"secret-bearing or VCS-control path is not allowed: {relative}")
            data, executable = _read_regular_file(directory_fd, name, relative, max_file_bytes)
            total += len(data)
            if total > max_total_bytes:
                raise ValueError("package exceeds total size limit")
            entries.append(SnapshotEntry(relative.as_posix(), data, executable))

    entries.sort(key=lambda entry: entry.relative.encode("utf-8"))

    names = {entry.relative for entry in entries}
    if require_manifest and "SKILL.md" not in names:
        raise ValueError("package has no root SKILL.md")
    if require_manifest and "research-skill.yaml" not in names:
        raise ValueError("package has no root research-skill.yaml")
    return entries


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"refusing to overwrite existing output: {path}")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise ValueError(f"refusing to overwrite existing output: {path}") from exc
    finally:
        Path(temporary).unlink(missing_ok=True)


def pack_snapshot(entries: list[SnapshotEntry], output: Path) -> str:
    """Pack one immutable snapshot without reopening the source tree."""

    if len(entries) > DEFAULT_MAX_ENTRIES:
        raise ValueError("package snapshot exceeds entry-count limit")
    total = 0
    for entry in entries:
        if not isinstance(entry.relative, str):
            raise ValueError("package snapshot path must be a string")
        relative = PurePosixPath(entry.relative)
        if (
            not entry.relative
            or entry.relative == "."
            or relative.is_absolute()
            or ".." in relative.parts
            or relative.as_posix() != entry.relative
        ):
            raise ValueError(f"unsafe package snapshot path: {entry.relative!r}")
        _validate_archive_path(relative)
        if _denied(relative):
            raise ValueError(f"secret-bearing or VCS-control path is not allowed: {entry.relative}")
        if not isinstance(entry.data, bytes):
            raise ValueError(f"package snapshot data must be bytes: {entry.relative}")
        if len(entry.data) > DEFAULT_MAX_FILE_BYTES:
            raise ValueError(f"package file exceeds size limit: {entry.relative}")
        total += len(entry.data)
        if total > DEFAULT_MAX_TOTAL_BYTES:
            raise ValueError("package exceeds total size limit")
        if not isinstance(entry.executable, bool):
            raise ValueError(f"package executable flag must be boolean: {entry.relative}")
    names = [entry.relative for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("package snapshot contains duplicate paths")
    if "SKILL.md" not in names or "research-skill.yaml" not in names:
        raise ValueError("package snapshot lacks SKILL.md or research-skill.yaml")
    output = output.resolve()
    buffer = io.BytesIO()
    with (
        gzip.GzipFile(filename="", mode="wb", fileobj=buffer, compresslevel=9, mtime=0) as zipped,
        tarfile.open(fileobj=zipped, mode="w", format=tarfile.USTAR_FORMAT) as archive,
    ):
        for entry in sorted(entries, key=lambda item: item.relative.encode("utf-8")):
            info = tarfile.TarInfo(entry.relative)
            info.size = len(entry.data)
            info.mode = 0o755 if entry.executable else 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            archive.addfile(info, io.BytesIO(entry.data))
    payload = buffer.getvalue()
    _atomic_write(output, payload)
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def pack_directory(root: Path, output: Path) -> str:
    root = root.resolve(strict=True)
    output = output.resolve()
    if output.is_relative_to(root):
        raise ValueError("archive output must be outside the package root")
    entries = snapshot_tree(root)
    return pack_snapshot(entries, output)
