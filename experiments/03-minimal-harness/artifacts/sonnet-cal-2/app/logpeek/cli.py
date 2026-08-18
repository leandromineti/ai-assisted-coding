"""Command-line interface for logpeek."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .analyzer import LogFileError, Summary, summarize_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logpeek",
        description="Summarize structured log files: line counts, level "
        "breakdown, time span, and top logger names.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="log file(s) to summarize")
    parser.add_argument(
        "--level",
        metavar="NAME",
        help="only consider entries at this log level (e.g. ERROR)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    return parser


def _summary_to_dict(summary: Summary) -> dict:
    return {
        "file": summary.path,
        "error": None,
        "total_lines": summary.total_lines,
        "parsed_lines": summary.parsed_lines,
        "unparsed_lines": summary.unparsed_lines,
        "level_filter": summary.level_filter,
        "matched_lines": summary.matched_lines,
        "level_counts": summary.level_counts,
        "time_span": {
            "first": summary.first_timestamp.isoformat()
            if summary.first_timestamp
            else None,
            "last": summary.last_timestamp.isoformat()
            if summary.last_timestamp
            else None,
        },
        "top_loggers": [
            {"logger": name, "count": count} for name, count in summary.top_loggers
        ],
    }


def _print_text(summary: Summary) -> None:
    print(f"==> {summary.path} <==")
    print(f"Total lines:     {summary.total_lines}")
    print(f"Parsed entries:  {summary.parsed_lines}")
    if summary.unparsed_lines:
        print(f"Unparsed lines:  {summary.unparsed_lines} (skipped)")
    if summary.level_filter:
        print(f"Level filter:    {summary.level_filter}")
        print(f"Matching lines:  {summary.matched_lines}")

    if summary.matched_lines == 0:
        print("No matching entries.")
        print()
        return

    first = summary.first_timestamp.isoformat() if summary.first_timestamp else "?"
    last = summary.last_timestamp.isoformat() if summary.last_timestamp else "?"
    print(f"Time span:       {first} to {last}")

    print("Level counts:")
    for level, count in sorted(summary.level_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {level:<10} {count}")

    print("Top loggers:")
    for name, count in summary.top_loggers:
        print(f"  {name:<20} {count}")
    print()


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    results = []
    had_error = False

    for path in args.files:
        try:
            summary = summarize_file(path, level_filter=args.level)
        except LogFileError as exc:
            had_error = True
            if args.json:
                results.append({"file": path, "error": str(exc)})
            else:
                print(f"Error: {exc}", file=sys.stderr)
            continue

        if args.json:
            results.append(_summary_to_dict(summary))
        else:
            _print_text(summary)

    if args.json:
        print(json.dumps(results, indent=2))

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
