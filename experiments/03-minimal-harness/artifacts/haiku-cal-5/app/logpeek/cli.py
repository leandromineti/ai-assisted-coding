#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from logpeek.parser import summarize_file


def format_text_output(filepath: str, summary, total_lines: int):
    """Format summary as human-readable text."""
    lines = []
    lines.append(f"File: {filepath}")
    lines.append(f"  Total lines: {total_lines}")

    # Log level counts
    levels_line = "  Levels: "
    level_parts = []
    for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        count = summary.levels_count.get(level, 0)
        if count > 0:
            level_parts.append(f"{level}={count}")
    lines.append(levels_line + ", ".join(level_parts))

    # Time span
    time_span = summary.get_time_span()
    if time_span:
        lines.append(f"  Time span: {time_span[0]} to {time_span[1]}")
    else:
        lines.append("  Time span: no valid timestamps")

    # Top loggers
    top_loggers = summary.get_top_loggers(5)
    if top_loggers:
        loggers_line = "  Top loggers: " + ", ".join(f"{name}({count})" for name, count in top_loggers)
    else:
        loggers_line = "  Top loggers: none"
    lines.append(loggers_line)

    return "\n".join(lines)


def format_json_output(filepath: str, summary, total_lines: int):
    """Format summary as JSON."""
    time_span = summary.get_time_span()
    top_loggers = summary.get_top_loggers(5)

    data = {
        "file": filepath,
        "total_lines": total_lines,
        "levels": dict(summary.levels_count),
        "time_span": {
            "first": time_span[0] if time_span else None,
            "last": time_span[1] if time_span else None,
        },
        "top_loggers": {name: count for name, count in top_loggers},
    }

    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize structured log files'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Log file path(s) to summarize'
    )
    parser.add_argument(
        '--level',
        type=str,
        help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    exit_code = 0
    results = []

    for filepath in args.files:
        try:
            summary, total_lines = summarize_file(filepath, level_filter=args.level)
            results.append((filepath, summary, total_lines, None))
        except (IOError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            exit_code = 1

    if not results:
        sys.exit(exit_code if exit_code != 0 else 1)

    if args.json:
        # For JSON output, collect all results into an array
        json_results = []
        for filepath, summary, total_lines, _ in results:
            data = {
                "file": filepath,
                "total_lines": total_lines,
                "levels": dict(summary.levels_count),
                "time_span": {
                    "first": summary.get_time_span()[0] if summary.get_time_span() else None,
                    "last": summary.get_time_span()[1] if summary.get_time_span() else None,
                },
                "top_loggers": {name: count for name, count in summary.get_top_loggers(5)},
            }
            json_results.append(data)

        if len(json_results) == 1:
            print(json.dumps(json_results[0], indent=2))
        else:
            print(json.dumps(json_results, indent=2))
    else:
        # Text output
        for filepath, summary, total_lines, _ in results:
            print(format_text_output(filepath, summary, total_lines))
            if filepath != args.files[-1]:
                print()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
