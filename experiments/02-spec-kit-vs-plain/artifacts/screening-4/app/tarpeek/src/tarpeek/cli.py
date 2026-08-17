"""tarpeek: summarize the contents of a tar archive without extracting it."""

import argparse
import json
import sys
import tarfile
from datetime import datetime, timezone


class TarPeekError(Exception):
    """Raised for user-facing errors (bad path, bad archive, empty archive)."""


def _member_type(member):
    if member.isdir():
        return "dir"
    if member.issym() or member.islnk():
        return "symlink"
    if member.isfile():
        return "file"
    return "other"


def _format_mtime(epoch_seconds):
    return (
        datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def inspect_archive(path, min_size=None):
    """Return a list of member dicts (name, type, size, mtime), sorted by size desc.

    Reads only tar metadata (member headers) - never extracts file contents
    and never writes anything to disk. Raises TarPeekError for a missing
    path, a non-tar file, or an archive with no members.
    """
    try:
        tar = tarfile.open(path, mode="r")
    except FileNotFoundError:
        raise TarPeekError(f"No such file: {path}")
    except IsADirectoryError:
        raise TarPeekError(f"Not a file: {path}")
    except PermissionError:
        raise TarPeekError(f"Permission denied: {path}")
    except tarfile.TarError:
        raise TarPeekError(f"Not a valid tar archive: {path}")

    try:
        members = tar.getmembers()
    finally:
        tar.close()

    if not members:
        raise TarPeekError(f"Archive is empty: {path}")

    rows = [
        {
            "name": member.name,
            "type": _member_type(member),
            "size": member.size,
            "mtime": _format_mtime(member.mtime),
        }
        for member in members
        if min_size is None or member.size >= min_size
    ]
    rows.sort(key=lambda row: row["size"], reverse=True)
    return rows


def _print_table(rows, stream):
    headers = ("NAME", "TYPE", "SIZE", "MODIFIED")
    widths = [len(h) for h in headers]
    for row in rows:
        widths[0] = max(widths[0], len(row["name"]))
        widths[1] = max(widths[1], len(row["type"]))
        widths[2] = max(widths[2], len(str(row["size"])))
        widths[3] = max(widths[3], len(row["mtime"]))

    fmt = f"{{:<{widths[0]}}}  {{:<{widths[1]}}}  {{:>{widths[2]}}}  {{:<{widths[3]}}}"
    print(fmt.format(*headers), file=stream)
    for row in rows:
        print(
            fmt.format(row["name"], row["type"], row["size"], row["mtime"]),
            file=stream,
        )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", help="Path to the tar archive to inspect")
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
        help="Print machine-readable JSON instead of a table",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.min_size is not None and args.min_size < 0:
        print("tarpeek: error: --min-size must not be negative", file=sys.stderr)
        return 2

    try:
        rows = inspect_archive(args.archive, min_size=args.min_size)
    except TarPeekError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        _print_table(rows, sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
