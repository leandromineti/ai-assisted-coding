"""Command-line interface for tarpeek."""

import argparse
import json
import sys

from .core import EmptyArchiveError, NotATarFileError, filter_and_sort, read_members

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_NOT_TAR = 2
EXIT_EMPTY = 3


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Summarize the contents of a tar archive without extracting it.",
    )
    parser.add_argument("archive", help="Path to the tar archive")
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        metavar="BYTES",
        help="Only show members with size >= BYTES",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON instead of a table"
    )
    return parser


def format_table(members):
    if not members:
        return "No members match the given filters."

    headers = ("NAME", "TYPE", "SIZE", "MODIFIED")
    rows = [(m["name"], m["type"], str(m["size"]), m["modified"]) for m in members]
    widths = [max(len(headers[i]), max(len(row[i]) for row in rows)) for i in range(4)]
    aligns = (str.ljust, str.ljust, str.rjust, str.ljust)

    def fmt_row(row):
        return "  ".join(aligns[i](cell, widths[i]) for i, cell in enumerate(row))

    lines = [fmt_row(headers), "  ".join("-" * w for w in widths)]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        members = read_members(args.archive)
    except FileNotFoundError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except NotATarFileError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return EXIT_NOT_TAR
    except EmptyArchiveError as exc:
        print(f"tarpeek: error: {exc}", file=sys.stderr)
        return EXIT_EMPTY

    members = filter_and_sort(members, args.min_size)

    if args.json:
        print(json.dumps(members, indent=2))
    else:
        print(format_table(members))

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
