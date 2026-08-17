import tarfile
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class TarMemberInfo:
    """Information about a tar archive member."""

    def __init__(self, name: str, member_type: str, size: int, mtime: datetime):
        self.name = name
        self.member_type = member_type
        self.size = size
        self.mtime = mtime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.member_type,
            "size": self.size,
            "mtime": self.mtime.isoformat(),
        }


class TarArchiveError(Exception):
    """Raised when there's an error reading the tar archive."""
    pass


def read_tar_members(
    archive_path: str, min_size: int = 0
) -> List[TarMemberInfo]:
    """
    Read members from a tar archive.

    Args:
        archive_path: Path to the tar archive
        min_size: Minimum size in bytes to include (0 includes all)

    Returns:
        List of TarMemberInfo objects sorted by size descending

    Raises:
        TarArchiveError: If the path is not a valid tar archive or cannot be read
    """
    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise TarArchiveError(f"File not found: {archive_path}")

    try:
        with tarfile.open(archive_path, "r:*") as tar:
            members = []
            for info in tar.getmembers():
                member_type = _get_member_type(info)
                mtime = datetime.fromtimestamp(info.mtime)

                if info.size >= min_size:
                    members.append(
                        TarMemberInfo(
                            name=info.name,
                            member_type=member_type,
                            size=info.size,
                            mtime=mtime,
                        )
                    )

            if not members:
                raise TarArchiveError(
                    f"Archive is empty or all members are below minimum size"
                )

            members.sort(key=lambda m: m.size, reverse=True)
            return members

    except tarfile.TarError as e:
        raise TarArchiveError(f"Failed to read tar archive: {e}")
    except (OSError, IOError) as e:
        raise TarArchiveError(f"Cannot read file: {e}")


def _get_member_type(info: tarfile.TarInfo) -> str:
    """Determine the type of a tar member (file/dir/symlink/etc)."""
    if info.isfile():
        return "file"
    elif info.isdir():
        return "dir"
    elif info.issym():
        return "symlink"
    elif info.islnk():
        return "hardlink"
    elif info.isblk():
        return "block"
    elif info.ischr():
        return "char"
    elif info.isfifo():
        return "fifo"
    elif info.isdev():
        return "dev"
    else:
        return "unknown"


def format_table(members: List[TarMemberInfo]) -> str:
    """Format members as a human-readable table."""
    if not members:
        return "No members to display"

    col_name = "Name"
    col_type = "Type"
    col_size = "Size"
    col_mtime = "Modified"

    name_width = max(len(col_name), max(len(m.name) for m in members))
    type_width = max(len(col_type), max(len(m.member_type) for m in members))
    size_width = max(len(col_size), max(len(str(m.size)) for m in members))
    mtime_width = len(col_mtime)

    lines = []

    header = (
        f"{col_name:<{name_width}}  "
        f"{col_type:<{type_width}}  "
        f"{col_size:>{size_width}}  "
        f"{col_mtime:<{mtime_width}}"
    )
    lines.append(header)
    lines.append(
        "-" * (name_width + type_width + size_width + mtime_width + 6)
    )

    for member in members:
        mtime_str = member.mtime.strftime("%Y-%m-%d %H:%M:%S")
        line = (
            f"{member.name:<{name_width}}  "
            f"{member.member_type:<{type_width}}  "
            f"{member.size:>{size_width}}  "
            f"{mtime_str:<{mtime_width}}"
        )
        lines.append(line)

    return "\n".join(lines)


def format_json(members: List[TarMemberInfo]) -> str:
    """Format members as JSON."""
    return json.dumps([m.to_dict() for m in members], indent=2)
