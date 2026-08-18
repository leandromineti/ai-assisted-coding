"""Command-line interface for logpeek."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .parser import FileSummary, LogFileError, summarize_file


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logpeek",
        description="Summarize one or more structured log files.",
    )
    parser.add_argument("paths", nargs="+", metavar="FILE", help="log file(s) to summarize")
    parser.add_argument(
        "--level",
        metavar="NAME",
        help="only include entries at this log level (e.g. ERROR)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable JSON instead of plain text",
    )
    return parser


def summary_to_dict(summary: FileSummary) -> dict:
    return {
        "path": summary.path,
        "total_lines": summary.total_lines,
        "parsed_lines": summary.parsed_lines,
        "unparsed_lines": summary.unparsed_lines,
        "level_filter": summary.level_filter,
        "level_counts": summary.level_counts,
        "first_event": summary.first_event.isoformat() if summary.first_event else None,
        "last_event": summary.last_event.isoformat() if summary.last_event else None,
        "top_loggers": [{"logger": name, "count": count} for name, count in summary.top_loggers],
    }


def format_summary_text(summary: FileSummary) -> str:
    lines = [f"==> {summary.path} <=="]
    lines.append(
        f"Total lines: {summary.total_lines} "
        f"({summary.parsed_lines} parsed, {summary.unparsed_lines} unparsed)"
    )

    if summary.level_filter:
        matched = sum(summary.level_counts.values())
        lines.append(f"Filter: level={summary.level_filter} ({matched} matching entries)")

    if summary.first_event and summary.last_event:
        lines.append(f"Time span: {summary.first_event.isoformat()} -> {summary.last_event.isoformat()}")
    else:
        lines.append("Time span: (no matching events)")

    lines.append("Level counts:")
    if summary.level_counts:
        for level, count in summary.level_counts.items():
            lines.append(f"  {level}: {count}")
    else:
        lines.append("  (none)")

    if summary.top_loggers:
        lines.append("Top loggers:")
        for name, count in summary.top_loggers:
            lines.append(f"  {name}: {count}")
    else:
        lines.append("Top loggers: (none)")

    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args(argv)

    results = []
    had_error = False

    for index, path in enumerate(args.paths):
        try:
            summary = summarize_file(path, level_filter=args.level)
        except LogFileError as exc:
            had_error = True
            if args.json:
                results.append({"path": str(path), "error": str(exc)})
            else:
                print(f"logpeek: {exc}", file=sys.stderr)
            continue

        if args.json:
            results.append(summary_to_dict(summary))
        else:
            if index:
                print()
            print(format_summary_text(summary))

    if args.json:
        print(json.dumps(results, indent=2))

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
