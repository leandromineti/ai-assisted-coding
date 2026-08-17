import tarfile
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class TarMember:
    """Represents a single member in a tar archive."""

    def __init__(self, name: str, type_str: str, size: int, mtime: int):
        self.name = name
        self.type = type_str
        self.size = size
        self.mtime = mtime

    def to_dict(self) -> Dict[str, Any]:
        mtime_str = datetime.fromtimestamp(self.mtime, tz=timezone.utc).isoformat()
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "mtime": mtime_str,
        }

    def __repr__(self) -> str:
        return f"TarMember({self.name}, {self.type}, {self.size}, {self.mtime})"


class TarArchive:
    """Reads and summarizes tar archive contents without extraction."""

    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.members: List[TarMember] = []
        self._read()

    def _read(self) -> None:
        """Read tar archive and populate members list."""
        try:
            with tarfile.open(self.archive_path, "r:*") as tar:
                for tarinfo in tar.getmembers():
                    type_str = self._get_type(tarinfo)
                    member = TarMember(
                        name=tarinfo.name,
                        type_str=type_str,
                        size=tarinfo.size,
                        mtime=tarinfo.mtime,
                    )
                    self.members.append(member)
        except tarfile.ReadError as e:
            raise ValueError(f"Not a valid tar archive: {self.archive_path}") from e
        except FileNotFoundError:
            raise FileNotFoundError(f"Archive not found: {self.archive_path}")

    @staticmethod
    def _get_type(tarinfo) -> str:
        """Determine member type: file, dir, or symlink."""
        if tarinfo.issym():
            return "symlink"
        elif tarinfo.isdir():
            return "dir"
        else:
            return "file"

    def filter_by_min_size(self, min_size: int) -> List[TarMember]:
        """Return members with size >= min_size."""
        return [m for m in self.members if m.size >= min_size]

    def sort_by_size(self, members: Optional[List[TarMember]] = None) -> List[TarMember]:
        """Sort members by size descending."""
        target = members if members is not None else self.members
        return sorted(target, key=lambda m: m.size, reverse=True)

    def to_json(self, members: List[TarMember]) -> str:
        """Convert members list to JSON."""
        data = [m.to_dict() for m in members]
        return json.dumps(data, indent=2)
