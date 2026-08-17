"""tarpeek: summarize the contents of a tar archive without extracting it."""

import argparse
import json
import os
import sys
import tarfile
from datetime import datetime, timezone


class TarpeekError(Exception):
    """Base error for tarpeek. Carries the process exit code to use."""

    exit_code = 1


class ArchiveNotFoundError(TarpeekError):
    exit_code = 1


class InvalidArchiveError(TarpeekError):
    exit_code = 2


class EmptyArchiveError(TarpeekError):
    exit_code = 3


def member_type(member):
    """Classify a TarInfo member as 'dir', 'symlink', 'file', or 'other'."""
    if member.issym() or member.islnk():
        return "symlink"
    if member.isdir():
        return "dir"
    if member.isfile():
        return "file"
    return "other"


def collect_members(path):
    """Read member metadata from the tar archive at `path` without extracting anything.

    Raises ArchiveNotFoundError, InvalidArchiveError, or EmptyArchiveError.
    """
    if not os.path.exists(path):
        raise ArchiveNotFoundError(f"file not found: {path}")
    if os.path.isdir(path):
        raise InvalidArchiveError(f"not a valid tar archive (is a directory): {path}")

    try:
        with tarfile.open(path, mode="r") as tf:
            members = tf.getmembers()
    except (tarfile.TarError, OSError) as exc:
        raise InvalidArchiveError(f"not a valid tar archive: {path} ({exc})") from exc

    if not members:
        raise EmptyArchiveError(f"archive is empty: {path}")

    rows = [
        {
            "name": m.name,
            "type": member_type(m),
            "size": m.size,
            "mtime": datetime.fromtimestamp(m.mtime, tz=timezone.utc),
        }
        for m in members
    ]
    return rows


def filter_and_sort(rows, min_size=0):
    filtered = [r for r in rows if r["size"] >= min_size]
    return sorted(filtered, key=lambda r: r["size"], reverse=True)


def format_table(rows):
    if not rows:
        return "No members match the given filters."

    headers = ("NAME", "TYPE", "SIZE", "LAST MODIFIED")
    str_rows = [
        (r["name"], r["type"], str(r["size"]), r["mtime"].strftime("%Y-%m-%d %H:%M:%S"))
        for r in rows
    ]
    widths = [
        max(len(headers[i]), max(len(row[i]) for row in str_rows))
        for i in range(len(headers))
    ]

    def fmt_row(cols):
        return "  ".join(col.ljust(widths[i]) for i, col in enumerate(cols))

    lines = [fmt_row(headers), fmt_row(["-" * w for w in widths])]
    lines.extend(fmt_row(row) for row in str_rows)
    return "\n".join(lines)


def format_json(rows):
    payload = [
        {
            "name": r["name"],
            "type": r["type"],
            "size": r["size"],
            "mtime": r["mtime"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        for r in rows
    ]
    return json.dumps(payload, indent=2)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", help="path to the tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        metavar="BYTES",
        help="only show members at least this many bytes in size",
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

    if args.min_size < 0:
        print("tarpeek: error: --min-size must not be negative", file=sys.stderr)
        return 2

    try:
        rows = collect_members(args.archive)
    except TarpeekError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return exc.exit_code

    rows = filter_and_sort(rows, min_size=args.min_size)

    if args.json:
        print(format_json(rows))
    else:
        print(format_table(rows))

    return 0


if __name__ == "__main__":
    sys.exit(main())
