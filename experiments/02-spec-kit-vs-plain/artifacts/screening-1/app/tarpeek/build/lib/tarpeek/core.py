"""Core logic for reading tar archive metadata without extracting anything."""

import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone

TYPE_FILE = "file"
TYPE_DIR = "dir"
TYPE_SYMLINK = "symlink"
TYPE_OTHER = "other"


class InvalidArchiveError(Exception):
    """Raised when the given path cannot be read as a tar archive."""


class ArchiveEmptyError(Exception):
    """Raised when a valid tar archive contains no members."""


@dataclass
class MemberInfo:
    name: str
    type: str
    size: int
    mtime: datetime

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "modified": self.mtime.strftime("%Y-%m-%d %H:%M:%S"),
        }


def _member_type(member):
    if member.issym():
        return TYPE_SYMLINK
    if member.isdir():
        return TYPE_DIR
    if member.isfile():
        return TYPE_FILE
    return TYPE_OTHER


def iter_members(path, min_size=0):
    """Return MemberInfo objects for a tar archive, sorted by size descending.

    Only reads member headers (tarfile.getmembers()); never extracts member
    contents and never writes anything to disk.

    Raises FileNotFoundError, IsADirectoryError, PermissionError,
    InvalidArchiveError, or ArchiveEmptyError as appropriate.
    """
    try:
        tf = tarfile.open(path, mode="r")
    except (tarfile.ReadError, tarfile.CompressionError, EOFError) as exc:
        raise InvalidArchiveError(f"'{path}' is not a valid tar archive") from exc

    try:
        members = tf.getmembers()
        if not members:
            raise ArchiveEmptyError(f"'{path}' is an empty archive")

        infos = [
            MemberInfo(
                name=member.name,
                type=_member_type(member),
                size=member.size,
                mtime=datetime.fromtimestamp(member.mtime, tz=timezone.utc),
            )
            for member in members
        ]
    finally:
        tf.close()

    infos = [info for info in infos if info.size >= min_size]
    infos.sort(key=lambda info: info.size, reverse=True)
    return infos
