"""Core logic for reading tar archive metadata without extracting anything."""

import os
import tarfile
from datetime import datetime, timezone


class NotATarFileError(Exception):
    """Raised when the given path is not a readable tar archive."""


class EmptyArchiveError(Exception):
    """Raised when the tar archive contains no members."""


def member_type(member):
    """Classify a tarfile.TarInfo member as 'file', 'dir', 'symlink', or 'other'."""
    if member.isdir():
        return "dir"
    if member.issym() or member.islnk():
        return "symlink"
    if member.isfile():
        return "file"
    return "other"


def read_members(path):
    """Return metadata dicts for every member of the tar archive at `path`.

    Only reads archive headers via tarfile - never extracts, so nothing is
    ever written to the filesystem.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")

    if not tarfile.is_tarfile(path):
        raise NotATarFileError(f"Not a valid tar archive: {path}")

    try:
        with tarfile.open(path, "r:*") as tf:
            members = tf.getmembers()
    except tarfile.TarError as exc:
        raise NotATarFileError(f"Not a valid tar archive: {path}") from exc

    if not members:
        raise EmptyArchiveError(f"Archive is empty: {path}")

    return [
        {
            "name": member.name,
            "type": member_type(member),
            "size": member.size,
            "modified": datetime.fromtimestamp(
                member.mtime, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }
        for member in members
    ]


def filter_and_sort(members, min_size=None):
    """Filter members by minimum size and sort the result by size descending."""
    if min_size is not None:
        members = [m for m in members if m["size"] >= min_size]
    return sorted(members, key=lambda m: m["size"], reverse=True)
