"""Command-line entry point for tarpeek."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class TarpeekError(Exception):
    """A user-facing error with a clear, actionable message."""


@dataclass
class MemberInfo:
    name: str
    type: str
    size: int
    mtime: str


def _member_type(member: tarfile.TarInfo) -> str:
    if member.isdir():
        return "dir"
    if member.issym() or member.islnk():
        return "symlink"
    if member.isfile():
        return "file"
    return "other"


def _format_mtime(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def read_members(path: Path) -> list[MemberInfo]:
    """Read member metadata from a tar archive without extracting anything."""
    if not path.exists():
        raise TarpeekError(f"path not found: {path}")
    if not path.is_file():
        raise TarpeekError(f"not a file: {path}")
    if not tarfile.is_tarfile(path):
        raise TarpeekError(f"not a valid tar archive: {path}")

    try:
        with tarfile.open(path, mode="r") as archive:
            members = archive.getmembers()
    except tarfile.TarError as exc:
        raise TarpeekError(f"not a valid tar archive: {path} ({exc})") from exc

    if not members:
        raise TarpeekError(f"archive is empty: {path}")

    return [
        MemberInfo(
            name=member.name,
            type=_member_type(member),
            size=member.size,
            mtime=_format_mtime(member.mtime),
        )
        for member in members
    ]


def filter_and_sort(
    members: list[MemberInfo], min_size: Optional[int]
) -> list[MemberInfo]:
    filtered = (
        [m for m in members if m.size >= min_size]
        if min_size is not None
        else list(members)
    )
    filtered.sort(key=lambda m: m.size, reverse=True)
    return filtered


def render_table(members: list[MemberInfo]) -> str:
    headers = ("NAME", "TYPE", "SIZE", "LAST MODIFIED")
    rows = [(m.name, m.type, str(m.size), m.mtime) for m in members]
    widths = [
        max(len(header), max(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]
    lines = ["  ".join(h.ljust(w) for h, w in zip(headers, widths))]
    lines.extend("  ".join(c.ljust(w) for c, w in zip(row, widths)) for row in rows)
    return "\n".join(lines)


def render_json(members: list[MemberInfo]) -> str:
    return json.dumps([asdict(m) for m in members], indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", type=Path, help="path to the tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        metavar="BYTES",
        help="only show members with size >= BYTES",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output as JSON instead of a table",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.min_size is not None and args.min_size < 0:
        print("tarpeek: error: --min-size must be >= 0", file=sys.stderr)
        return 1

    try:
        members = read_members(args.archive)
    except TarpeekError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return 1

    members = filter_and_sort(members, args.min_size)

    if args.json:
        print(render_json(members))
    elif members:
        print(render_table(members))
    else:
        print("No members match the given filter.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
