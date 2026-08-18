import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .parser import LogParser, LogSummary


def format_timestamp(dt) -> str:
    """Format datetime for human output."""
    return dt.isoformat() if dt else "N/A"


def summarize_file(file_path: str, level_filter: Optional[str] = None) -> dict:
    """Summarize a single log file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise IsADirectoryError(f"Not a file: {file_path}")

    try:
        parser = LogParser(level_filter=level_filter)
        entries, errors = parser.parse_file(file_path)
    except ValueError as e:
        raise ValueError(f"{file_path}: {e}")

    if path.stat().st_size == 0 and not entries:
        raise ValueError(f"{file_path}: Empty log file")

    if not entries and path.stat().st_size > 0:
        raise ValueError(f"{file_path}: No valid log entries found")

    summary = LogSummary(entries)

    time_span = summary.time_span()
    start_time, end_time = (format_timestamp(time_span[0]), format_timestamp(time_span[1])) if time_span else ("N/A", "N/A")

    result = {
        "file": file_path,
        "total_lines": summary.total_lines(),
        "level_counts": summary.level_counts(),
        "time_start": start_time,
        "time_end": end_time,
        "top_loggers": [{"name": name, "count": count} for name, count in summary.top_loggers()],
    }

    if errors:
        result["parse_errors"] = errors

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to log file(s)",
    )
    parser.add_argument(
        "--level",
        type=str,
        metavar="NAME",
        help="Filter logs by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    results = []
    exit_code = 0

    for file_path in args.files:
        try:
            result = summarize_file(file_path, level_filter=args.level)
            results.append(result)
        except (FileNotFoundError, IsADirectoryError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(f"File: {result['file']}")
            print(f"  Total lines: {result['total_lines']}")
            print(f"  Levels: {', '.join(f'{k}={v}' for k, v in result['level_counts'].items()) or 'none'}")
            print(f"  Time span: {result['time_start']} to {result['time_end']}")
            print(f"  Top loggers:")
            if result['top_loggers']:
                for logger in result['top_loggers']:
                    print(f"    {logger['name']}: {logger['count']}")
            else:
                print(f"    (none)")
            if 'parse_errors' in result:
                print(f"  Parse errors: {len(result['parse_errors'])}")
            print()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
