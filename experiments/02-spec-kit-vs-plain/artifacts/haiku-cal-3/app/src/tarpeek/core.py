import tarfile
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TarMember:
    name: str
    type: str
    size: int
    modified: str

    def to_dict(self) -> Dict:
        return asdict(self)


class TarPeekError(Exception):
    pass


class ArchiveReader:
    def __init__(self, archive_path: str):
        self.archive_path = Path(archive_path)
        self._validate_path()

    def _validate_path(self) -> None:
        if not self.archive_path.exists():
            raise TarPeekError(f"Archive not found: {self.archive_path}")

    def read_members(self, min_size: int = 0) -> List[TarMember]:
        try:
            with tarfile.open(self.archive_path, 'r:*') as tar:
                members = []
                for member in tar.getmembers():
                    if member.size < min_size:
                        continue

                    member_type = self._get_member_type(member)
                    modified = datetime.fromtimestamp(member.mtime).isoformat()

                    tar_member = TarMember(
                        name=member.name,
                        type=member_type,
                        size=member.size,
                        modified=modified,
                    )
                    members.append(tar_member)

                if not members:
                    if not tar.getmembers():
                        raise TarPeekError("Archive is empty")
                    raise TarPeekError(
                        f"No members match filter (min-size: {min_size})"
                    )

                return members

        except tarfile.ReadError as e:
            raise TarPeekError(f"Invalid tar archive: {e}")
        except (OSError, IOError) as e:
            raise TarPeekError(f"Error reading archive: {e}")

    @staticmethod
    def _get_member_type(member: tarfile.TarInfo) -> str:
        if member.issym():
            return "symlink"
        elif member.islnk():
            return "hardlink"
        elif member.isdir():
            return "dir"
        elif member.isfile():
            return "file"
        else:
            return "other"

    @staticmethod
    def sort_by_size(members: List[TarMember]) -> List[TarMember]:
        return sorted(members, key=lambda m: m.size, reverse=True)
