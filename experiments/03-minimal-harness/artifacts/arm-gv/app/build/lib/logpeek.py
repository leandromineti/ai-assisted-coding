#!/usr/bin/env python3
"""
logpeek: CLI tool to summarize structured log files.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional, Dict, Any


LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2})\s+(\w+)\s+([\w.]+):'
)

VALID_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}


def parse_log_file(filepath: Path) -> tuple[int, Counter, Counter, list[str]]:
    """
    Parse a log file and return (total_lines, level_counts, logger_counts, timestamps).
    Malformed lines are skipped silently.

    Returns:
        (total_lines, level_counts, logger_counts, timestamps)
    """
    total_lines = 0
    level_counts = Counter()
    logger_counts = Counter()
    timestamps = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                total_lines += 1
                match = LOG_PATTERN.match(line.strip())
                if match:
                    timestamp, level, logger = match.groups()
                    level_counts[level] += 1
                    logger_counts[logger] += 1
                    timestamps.append(timestamp)
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return None

    return total_lines, level_counts, logger_counts, timestamps


def get_summary(filepath: Path, level_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Generate a summary of a log file.
    Returns None if the file is not a valid log file or cannot be read.
    """
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return None

    if not filepath.is_file():
        print(f"Error: Not a file: {filepath}", file=sys.stderr)
        return None

    result = parse_log_file(filepath)
    if result is None:
        return None

    total_lines, level_counts, logger_counts, timestamps = result

    if total_lines == 0:
        return {
            'file': str(filepath),
            'total_lines': 0,
            'level_counts': {},
            'time_span': None,
            'top_loggers': []
        }

    valid_log_lines = sum(level_counts.values())
    if valid_log_lines == 0:
        print(f"Error: {filepath} is not a valid log file (no valid log lines found)", file=sys.stderr)
        return None

    # Apply level filter if specified
    filtered_counts = level_counts.copy()
    if level_filter:
        if level_filter not in VALID_LEVELS:
            print(f"Error: Invalid log level '{level_filter}'. Valid levels are: {', '.join(sorted(VALID_LEVELS))}", file=sys.stderr)
            return None
        filtered_counts = Counter({level_filter: level_counts.get(level_filter, 0)})

    # Get time span
    time_span = None
    if timestamps:
        time_span = {
            'start': timestamps[0],
            'end': timestamps[-1]
        }

    # Get top 5 loggers
    top_loggers = [{'name': name, 'count': count} for name, count in logger_counts.most_common(5)]

    return {
        'file': str(filepath),
        'total_lines': total_lines,
        'level_counts': dict(filtered_counts),
        'time_span': time_span,
        'top_loggers': top_loggers
    }


def format_summary_text(summary: Dict[str, Any]) -> str:
    """Format summary as human-readable text."""
    lines = []
    lines.append(f"File: {summary['file']}")
    lines.append(f"Total lines: {summary['total_lines']}")

    level_counts = summary['level_counts']
    if level_counts:
        level_strs = [f"{level}: {count}" for level, count in sorted(level_counts.items())]
        lines.append(f"Log levels: {', '.join(level_strs)}")
    else:
        lines.append("Log levels: (none)")

    time_span = summary['time_span']
    if time_span:
        lines.append(f"Time span: {time_span['start']} to {time_span['end']}")
    else:
        lines.append("Time span: (none)")

    top_loggers = summary['top_loggers']
    if top_loggers:
        logger_strs = [f"{logger['name']} ({logger['count']})" for logger in top_loggers]
        lines.append(f"Top loggers: {', '.join(logger_strs)}")
    else:
        lines.append("Top loggers: (none)")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Summarize structured log files.')
    parser.add_argument('files', nargs='+', help='Log file paths')
    parser.add_argument('--level', type=str, help='Filter by log level (e.g., INFO, ERROR)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    summaries = []
    has_error = False

    for filepath_str in args.files:
        filepath = Path(filepath_str)
        summary = get_summary(filepath, args.level)
        if summary is None:
            has_error = True
            continue
        summaries.append(summary)

    if not summaries:
        if has_error:
            sys.exit(1)
        # No files provided or all failed
        sys.exit(1)

    if args.json:
        print(json.dumps(summaries, indent=2))
    else:
        for i, summary in enumerate(summaries):
            if i > 0:
                print()
            print(format_summary_text(summary))

    sys.exit(1 if has_error else 0)


if __name__ == '__main__':
    main()
