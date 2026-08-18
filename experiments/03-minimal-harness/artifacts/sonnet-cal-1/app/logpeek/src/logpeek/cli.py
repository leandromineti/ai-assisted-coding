"""Command-line entry point for logpeek."""

from __future__ import annotations

import argparse
import json
import sys

from .parser import LEVELS, parse_lines
from .summary import Summary, summarize


class LogpeekError(Exception):
    """A per-file problem that should be reported without a traceback."""


def _read_summary(path: str, level_filter: str | None) -> Summary:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            result = parse_lines(fh)
    except FileNotFoundError:
        raise LogpeekError(f"no such file: {path}")
    except IsADirectoryError:
        raise LogpeekError(f"is a directory, not a file: {path}")
    except PermissionError:
        raise LogpeekError(f"permission denied: {path}")
    except OSError as exc:
        raise LogpeekError(f"could not read file: {exc}")

    if result.total_lines == 0:
        raise LogpeekError("empty file, nothing to summarize")

    if result.entries == []:
        raise LogpeekError(
            f"no valid log entries found ({result.unparseable_lines} of "
            f"{result.total_lines} lines unparseable) — is this a log file?"
        )

    return summarize(path, result, level_filter)


def _format_text(summary: Summary) -> str:
    lines = [f"== {summary.path} =="]
    lines.append(f"Total lines: {summary.total_lines}")
    lines.append(
        f"Parsed entries: {summary.parsed_lines} "
        f"(unparseable: {summary.unparseable_lines})"
    )
    lines.append("Level counts:")
    for level in LEVELS:
        lines.append(f"  {level}: {summary.level_counts[level]}")
    if summary.first_timestamp and summary.last_timestamp:
        lines.append(f"Time span: {summary.first_timestamp} -> {summary.last_timestamp}")
    else:
        lines.append("Time span: n/a (no matching entries)")
    lines.append("Top 5 loggers:")
    if summary.top_loggers:
        for entry in summary.top_loggers:
            lines.append(f"  {entry['logger']}: {entry['count']}")
    else:
        lines.append("  (none)")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logpeek",
        description="Summarize structured log files.",
    )
    parser.add_argument("files", nargs="+", help="path(s) to log file(s) to summarize")
    parser.add_argument(
        "--level",
        metavar="NAME",
        help="only include entries at this log level (e.g. ERROR)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of text",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    level_filter = None
    if args.level is not None:
        level_filter = args.level.upper()
        if level_filter not in LEVELS:
            parser.error(
                f"invalid --level {args.level!r}; choose from {', '.join(LEVELS)}"
            )

    summaries = []
    had_error = False
    for path in args.files:
        try:
            summaries.append(_read_summary(path, level_filter))
        except LogpeekError as exc:
            had_error = True
            print(f"logpeek: {path}: {exc}", file=sys.stderr)

    if args.json:
        print(json.dumps([s.to_dict() for s in summaries], indent=2))
    else:
        print("\n\n".join(_format_text(s) for s in summaries))

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
