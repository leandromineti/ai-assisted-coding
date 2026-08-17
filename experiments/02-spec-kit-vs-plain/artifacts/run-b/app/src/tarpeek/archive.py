"""Tar archive reading, member classification, filtering, and sorting."""

import os
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone


class TarpeekError(Exception):
    """Base class for all tarpeek user-facing errors."""


class PathNotFoundError(TarpeekError):
    """Raised when the given path does not exist."""


class PathPermissionError(TarpeekError):
    """Raised when the given path exists but is not readable."""


class NotATarFileError(TarpeekError):
    """Raised when the given path exists and is readable but is not a valid tar archive."""


class EmptyArchiveError(TarpeekError):
    """Raised when the archive is valid but contains zero members."""


class InvalidMinSizeError(TarpeekError):
    """Raised when --min-size is non-numeric or negative."""


@dataclass
class ArchiveMember:
    """A single entry recorded inside a tar archive."""

    name: str
    type: str
    size: int
    last_modified: str


def validate_path(path: str) -> None:
    """Raise PathNotFoundError or PathPermissionError before any tarfile access is attempted."""
    if not os.path.exists(path):
        raise PathNotFoundError(f"path not found: {path}")
    if not os.access(path, os.R_OK):
        raise PathPermissionError(f"permission denied: {path}")


def _member_from_tarinfo(info: tarfile.TarInfo) -> ArchiveMember:
    if info.isdir():
        member_type = "dir"
    elif info.issym():
        member_type = "symlink"
    elif info.isfile():
        member_type = "file"
    else:
        member_type = "other"

    last_modified = datetime.fromtimestamp(info.mtime, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return ArchiveMember(name=info.name, type=member_type, size=info.size, last_modified=last_modified)


def read_archive(path: str) -> list[ArchiveMember]:
    """Read all member headers from the tar archive at path, without extracting any content."""
    validate_path(path)
    try:
        with tarfile.open(path, "r:*") as tar:
            members = [_member_from_tarinfo(info) for info in tar.getmembers()]
    except tarfile.ReadError as exc:
        raise NotATarFileError(f"not a valid tar archive: {path}") from exc

    if not members:
        raise EmptyArchiveError(f"archive is empty: {path}")

    return members


def sort_members(members: list[ArchiveMember]) -> list[ArchiveMember]:
    """Sort members by size descending, ties broken by name ascending."""
    return sorted(members, key=lambda m: (-m.size, m.name))


def filter_by_min_size(members: list[ArchiveMember], min_size: int) -> list[ArchiveMember]:
    """Keep only members with size >= min_size. May legitimately return an empty list."""
    return [m for m in members if m.size >= min_size]
