"""Command-line entry point for tarpeek."""

import argparse
import json
import sys
import tarfile
from datetime import datetime, timezone


class TarpeekError(Exception):
    """Raised for user-facing errors (bad path, bad archive, empty archive)."""


def member_type(member):
    if member.isdir():
        return "dir"
    if member.issym() or member.islnk():
        return "symlink"
    if member.isfile():
        return "file"
    return "other"


def format_mtime(mtime):
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def collect_members(archive_path, min_size=None):
    """Read member metadata from a tar archive without extracting anything.

    Returns (rows, total_member_count). Raises TarpeekError on any problem
    with the path or archive contents.
    """
    try:
        tar = tarfile.open(archive_path, mode="r")
    except FileNotFoundError:
        raise TarpeekError(f"file not found: {archive_path}")
    except IsADirectoryError:
        raise TarpeekError(f"'{archive_path}' is a directory, not a tar archive")
    except tarfile.ReadError as exc:
        raise TarpeekError(f"'{archive_path}' is not a valid tar archive ({exc})")
    except PermissionError as exc:
        raise TarpeekError(f"permission denied: {archive_path} ({exc})")

    try:
        members = tar.getmembers()
    finally:
        tar.close()

    rows = []
    for member in members:
        if min_size is not None and member.size < min_size:
            continue
        rows.append(
            {
                "name": member.name,
                "type": member_type(member),
                "size": member.size,
                "modified": format_mtime(member.mtime),
            }
        )

    rows.sort(key=lambda row: row["size"], reverse=True)
    return rows, len(members)


def render_table(rows):
    headers = ["NAME", "TYPE", "SIZE", "MODIFIED"]
    table_rows = [
        [row["name"], row["type"], str(row["size"]), row["modified"]] for row in rows
    ]

    widths = [len(header) for header in headers]
    for table_row in table_rows:
        for i, cell in enumerate(table_row):
            widths[i] = max(widths[i], len(cell))

    def format_row(cells):
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    lines = [format_row(headers)]
    lines.extend(format_row(row) for row in table_rows)
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", help="path to the tar archive")
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


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.min_size is not None and args.min_size < 0:
        parser.error("--min-size must not be negative")

    try:
        rows, total = collect_members(args.archive, args.min_size)
    except TarpeekError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return 1

    if total == 0:
        print(f"tarpeek: error: '{args.archive}' is an empty archive", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, indent=2))
    elif rows:
        print(render_table(rows))
    else:
        print("No members match the given filter.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
