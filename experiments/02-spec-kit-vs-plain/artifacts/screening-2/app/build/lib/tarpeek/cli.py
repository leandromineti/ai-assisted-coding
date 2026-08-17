"""Command-line tool that summarizes a tar archive's contents without extracting it."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_INVALID_ARCHIVE = 2
EXIT_EMPTY_ARCHIVE = 3


class TarpeekError(Exception):
    """Base error for tarpeek, carrying the process exit code to use."""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class MemberInfo:
    name: str
    type: str
    size: int
    modified: str


def member_type(member: tarfile.TarInfo) -> str:
    if member.isdir():
        return "dir"
    if member.issym():
        return "symlink"
    if member.isfile():
        return "file"
    return "other"


def format_mtime(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def read_members(archive_path: Path) -> list[MemberInfo]:
    """Read member metadata from a tar archive without extracting anything."""
    try:
        with tarfile.open(archive_path, mode="r:*") as tar:
            members = tar.getmembers()
    except tarfile.ReadError as exc:
        raise TarpeekError(
            f"not a valid tar archive: {archive_path}", EXIT_INVALID_ARCHIVE
        ) from exc
    except tarfile.CompressionError as exc:
        raise TarpeekError(
            f"unsupported compression in {archive_path}: {exc}", EXIT_INVALID_ARCHIVE
        ) from exc

    return [
        MemberInfo(
            name=member.name,
            type=member_type(member),
            size=member.size,
            modified=format_mtime(member.mtime),
        )
        for member in members
    ]


def filter_and_sort(
    members: Sequence[MemberInfo], min_size: Optional[int]
) -> list[MemberInfo]:
    filtered = (
        [m for m in members if m.size >= min_size] if min_size is not None else list(members)
    )
    return sorted(filtered, key=lambda m: m.size, reverse=True)


def render_table(members: Sequence[MemberInfo]) -> str:
    if not members:
        return "No members match the given filters."

    headers = ("NAME", "TYPE", "SIZE", "MODIFIED")
    rows = [(m.name, m.type, str(m.size), m.modified) for m in members]
    widths = [
        max(len(header), *(len(row[i]) for row in rows)) for i, header in enumerate(headers)
    ]

    def fmt_row(row: Sequence[str]) -> str:
        return "  ".join(cell.ljust(width) for cell, width in zip(row, widths))

    lines = [fmt_row(headers), fmt_row(["-" * w for w in widths])]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


def render_json(members: Sequence[MemberInfo]) -> str:
    return json.dumps([asdict(m) for m in members], indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", type=Path, help="Path to the tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        metavar="BYTES",
        help="Only show members whose size is at least BYTES",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as JSON instead of a table",
    )
    return parser


def run(archive: Path, min_size: Optional[int], as_json: bool) -> str:
    """Produce the rendered output for an archive. Raises TarpeekError on failure."""
    if not archive.exists():
        raise TarpeekError(f"no such file: {archive}", EXIT_NOT_FOUND)
    if not archive.is_file():
        raise TarpeekError(f"not a file: {archive}", EXIT_NOT_FOUND)

    members = read_members(archive)
    if not members:
        raise TarpeekError(f"archive is empty: {archive}", EXIT_EMPTY_ARCHIVE)

    result = filter_and_sort(members, min_size)
    return render_json(result) if as_json else render_table(result)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        output = run(args.archive, args.min_size, args.as_json)
    except TarpeekError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return exc.exit_code

    print(output)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
