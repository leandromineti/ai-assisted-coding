"""Command-line interface for tarpeek."""

import argparse
import json
import sys

from .core import ArchiveEmptyError, InvalidArchiveError, iter_members

EXIT_OK = 0
EXIT_BAD_PATH = 1
EXIT_INVALID_ARCHIVE = 2
EXIT_EMPTY_ARCHIVE = 3


def format_table(infos):
    if not infos:
        return "No members found."

    headers = ["NAME", "TYPE", "SIZE", "MODIFIED"]
    rows = [
        [info.name, info.type, str(info.size), info.mtime.strftime("%Y-%m-%d %H:%M:%S")]
        for info in infos
    ]
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows)) for col in range(len(headers))
    ]

    def fmt_row(row):
        return "  ".join(cell.ljust(width) for cell, width in zip(row, widths))

    lines = [fmt_row(headers), "  ".join("-" * w for w in widths)]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


def format_json(infos):
    return json.dumps([info.to_dict() for info in infos], indent=2)


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
        help="only show members at least this many bytes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output machine-readable JSON instead of a table",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.min_size < 0:
        print("Error: --min-size must not be negative", file=sys.stderr)
        return EXIT_INVALID_ARCHIVE

    try:
        infos = iter_members(args.archive, min_size=args.min_size)
    except FileNotFoundError:
        print(f"Error: no such file: {args.archive}", file=sys.stderr)
        return EXIT_BAD_PATH
    except IsADirectoryError:
        print(f"Error: '{args.archive}' is a directory, not a tar archive", file=sys.stderr)
        return EXIT_BAD_PATH
    except PermissionError:
        print(f"Error: permission denied: {args.archive}", file=sys.stderr)
        return EXIT_BAD_PATH
    except InvalidArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_INVALID_ARCHIVE
    except ArchiveEmptyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_EMPTY_ARCHIVE

    print(format_json(infos) if args.json else format_table(infos))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
