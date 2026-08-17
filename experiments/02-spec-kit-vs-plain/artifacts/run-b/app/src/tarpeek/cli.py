"""argparse setup, main() entry point, and error-to-exit-code mapping."""

import argparse
import sys

from tarpeek.archive import (
    InvalidMinSizeError,
    TarpeekError,
    filter_by_min_size,
    read_archive,
    sort_members,
)
from tarpeek.output import render_json, render_table

EXIT_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarpeek",
        description="Inspect a tar archive's contents without extracting it.",
    )
    parser.add_argument("path", metavar="PATH", help="path to the tar archive to summarize")
    parser.add_argument(
        "--min-size",
        dest="min_size",
        default=None,
        help="only show members with size >= BYTES (non-negative integer)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="emit JSON instead of a human-readable table",
    )
    return parser


def _parse_min_size(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise InvalidMinSizeError(f"invalid --min-size value: {raw}") from None
    if value < 0:
        raise InvalidMinSizeError(f"invalid --min-size value: {raw}")
    return value


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        min_size = _parse_min_size(args.min_size) if args.min_size is not None else None

        members = read_archive(args.path)
        if min_size is not None:
            members = filter_by_min_size(members, min_size)
        members = sort_members(members)
        print(render_json(members) if args.json_output else render_table(members))
        return 0
    except TarpeekError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
