#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from logpeek.parser import summarize_log_file


def format_time_span(summary) -> str:
    """Format the time span from summary."""
    if summary.time_start is None or summary.time_end is None:
        return "N/A (no entries)"
    if summary.time_start == summary.time_end:
        return summary.time_start.isoformat()
    return f"{summary.time_start.isoformat()} to {summary.time_end.isoformat()}"


def format_summary_text(summary, errors: list[str]) -> None:
    """Print summary in human-readable format."""
    print(f"\nFile: {summary.file_path}")
    print(f"Total lines: {summary.total_lines}")

    level_str = ", ".join(f"{level}: {count}" for level, count in sorted(summary.level_counts.items()))
    print(f"Levels: {level_str}")

    print(f"Time span: {format_time_span(summary)}")

    if summary.top_loggers:
        print("Top 5 loggers:")
        for logger, count in summary.top_loggers:
            print(f"  {logger}: {count}")

    if errors:
        print(f"Warnings/Errors ({len(errors)}):")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


def format_summary_json(summary, errors: list[str]) -> dict:
    """Convert summary to JSON-serializable dict."""
    return {
        "file": summary.file_path,
        "total_lines": summary.total_lines,
        "levels": summary.level_counts,
        "time_span": {
            "start": summary.time_start.isoformat() if summary.time_start else None,
            "end": summary.time_end.isoformat() if summary.time_end else None,
        },
        "top_loggers": [{"name": name, "count": count} for name, count in summary.top_loggers],
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek",
    )
    parser.add_argument("files", nargs="+", help="Log files to summarize")
    parser.add_argument("--level", help="Filter by log level (e.g., ERROR, INFO)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = []
    exit_code = 0

    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            exit_code = 1
            continue

        if not path.is_file():
            print(f"Error: Not a file: {file_path}", file=sys.stderr)
            exit_code = 1
            continue

        if path.stat().st_size == 0:
            print(f"Error: Empty file: {file_path}", file=sys.stderr)
            exit_code = 1
            continue

        summary, errors = summarize_log_file(file_path, args.level)

        if summary is None:
            print(f"Error: Unable to parse log file: {file_path}", file=sys.stderr)
            if errors:
                for error in errors[:5]:
                    print(f"  {error}", file=sys.stderr)
            exit_code = 1
            continue

        if args.json:
            results.append(format_summary_json(summary, errors))
        else:
            format_summary_text(summary, errors)

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
