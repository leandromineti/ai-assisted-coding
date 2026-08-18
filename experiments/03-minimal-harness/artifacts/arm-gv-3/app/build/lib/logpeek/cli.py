#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from .parser import LogParser


def format_output(filepath: str, stats: dict, json_format: bool = False) -> str:
    """Format statistics for output."""
    if json_format:
        return json.dumps({
            'file': filepath,
            **stats
        }, indent=2)

    lines = [f"File: {filepath}"]
    lines.append(f"Total lines: {stats['total_lines']}")

    level_counts = stats['level_counts']
    if level_counts:
        level_str = ", ".join(f"{level}: {count}" for level, count in sorted(level_counts.items()))
        lines.append(f"By level: {level_str}")
    else:
        lines.append("By level: (none)")

    if stats['time_span']:
        lines.append(f"Time span: {stats['time_span']['start']} to {stats['time_span']['end']}")
    else:
        lines.append("Time span: (none)")

    if stats['top_loggers']:
        loggers = ", ".join(f"{logger} ({count})" for logger, count in stats['top_loggers'])
        lines.append(f"Top loggers: {loggers}")
    else:
        lines.append("Top loggers: (none)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize structured log files'
    )
    parser.add_argument('files', nargs='+', help='Log files to analyze')
    parser.add_argument('--level', type=str, help='Filter by log level (e.g., ERROR, INFO)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.json:
        results = []

    exit_code = 0

    for filepath in args.files:
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"Error: File not found: {filepath}", file=sys.stderr)
                exit_code = 1
                continue

            if not path.is_file():
                print(f"Error: Not a file: {filepath}", file=sys.stderr)
                exit_code = 1
                continue

            log_parser = LogParser()
            has_valid_logs = log_parser.parse_file(filepath)

            if not has_valid_logs:
                print(f"Error: No valid log lines found in {filepath}", file=sys.stderr)
                exit_code = 1
                continue

            stats = log_parser.get_stats(level_filter=args.level)

            if args.json:
                results.append({
                    'file': filepath,
                    **stats
                })
            else:
                output = format_output(filepath, stats, json_format=False)
                print(output)
                print()

        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
