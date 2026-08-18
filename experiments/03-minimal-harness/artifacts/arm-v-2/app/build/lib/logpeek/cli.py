#!/usr/bin/env python3
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional, Dict, List, Tuple


def parse_log_line(line: str) -> Optional[Dict]:
    """Parse a structured log line into components."""
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s*(.*)$'
    match = re.match(pattern, line)
    if not match:
        return None
    timestamp_str, level, logger_name, message = match.groups()
    return {
        'timestamp': timestamp_str,
        'level': level,
        'logger': logger_name,
        'message': message
    }


def analyze_log_file(file_path: Path, level_filter: Optional[str] = None) -> Dict:
    """Analyze a log file and return statistics."""
    stats = {
        'file': str(file_path),
        'total_lines': 0,
        'valid_lines': 0,
        'invalid_lines': 0,
        'level_counts': defaultdict(int),
        'loggers': defaultdict(int),
        'first_timestamp': None,
        'last_timestamp': None,
        'error': None
    }

    if not file_path.exists():
        stats['error'] = f"File not found: {file_path}"
        return stats

    if not file_path.is_file():
        stats['error'] = f"Not a file: {file_path}"
        return stats

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        stats['error'] = f"Error reading file: {e}"
        return stats

    stats['total_lines'] = len(lines)

    if stats['total_lines'] == 0:
        return stats

    parsed_entries = []
    for line in lines:
        line = line.rstrip('\n\r')
        if not line.strip():
            continue

        parsed = parse_log_line(line)
        if parsed:
            stats['valid_lines'] += 1
            if level_filter is None or parsed['level'] == level_filter:
                parsed_entries.append(parsed)
                stats['level_counts'][parsed['level']] += 1
                stats['loggers'][parsed['logger']] += 1

                if stats['first_timestamp'] is None:
                    stats['first_timestamp'] = parsed['timestamp']
                stats['last_timestamp'] = parsed['timestamp']
        else:
            stats['invalid_lines'] += 1

    if level_filter is not None and len(parsed_entries) > 0:
        stats['level_counts'] = {level_filter: len(parsed_entries)}

    return stats


def get_top_loggers(stats: Dict, count: int = 5) -> List[Tuple[str, int]]:
    """Get the top N logger names by frequency."""
    loggers = stats.get('loggers', {})
    if isinstance(loggers, defaultdict):
        loggers = dict(loggers)
    return sorted(loggers.items(), key=lambda x: x[1], reverse=True)[:count]


def format_level_counts(level_counts: Dict) -> Dict:
    """Convert level_counts to a regular dict for JSON serialization."""
    if isinstance(level_counts, defaultdict):
        return dict(level_counts)
    return level_counts


def print_text_report(files_stats: List[Dict]) -> None:
    """Print human-readable report."""
    for stats in files_stats:
        print(f"\n{stats['file']}:")

        if stats['error']:
            print(f"  Error: {stats['error']}")
            continue

        print(f"  Total lines: {stats['total_lines']}")

        if stats['total_lines'] == 0:
            continue

        level_counts = format_level_counts(stats['level_counts'])
        if level_counts:
            print(f"  Levels: {', '.join(f'{level} ({count})' for level, count in sorted(level_counts.items()))}")

        if stats['first_timestamp'] and stats['last_timestamp']:
            print(f"  Time span: {stats['first_timestamp']} to {stats['last_timestamp']}")

        top_loggers = get_top_loggers(stats)
        if top_loggers:
            logger_str = ', '.join(f'{name} ({count})' for name, count in top_loggers)
            print(f"  Top loggers: {logger_str}")


def print_json_report(files_stats: List[Dict]) -> None:
    """Print machine-readable JSON report."""
    output = []
    for stats in files_stats:
        entry = {
            'file': stats['file'],
            'total_lines': stats['total_lines']
        }

        if stats['error']:
            entry['error'] = stats['error']
        else:
            if stats['total_lines'] > 0:
                entry['levels'] = format_level_counts(stats['level_counts'])
                entry['time_span'] = None
                if stats['first_timestamp'] and stats['last_timestamp']:
                    entry['time_span'] = {
                        'start': stats['first_timestamp'],
                        'end': stats['last_timestamp']
                    }
                entry['top_loggers'] = get_top_loggers(stats)

        output.append(entry)

    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Summarize structured log files')
    parser.add_argument('files', nargs='+', help='Log file paths')
    parser.add_argument('--level', type=str, help='Filter by log level')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    files_stats = []
    has_error = False

    for file_arg in args.files:
        file_path = Path(file_arg)
        stats = analyze_log_file(file_path, args.level)
        files_stats.append(stats)

    if args.json:
        print_json_report(files_stats)
    else:
        print_text_report(files_stats)

    for stats in files_stats:
        if stats['error']:
            print(f"Error: {stats['error']}", file=sys.stderr)
            has_error = True

    sys.exit(1 if has_error else 0)


if __name__ == '__main__':
    main()
