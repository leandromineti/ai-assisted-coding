"""Command-line interface for logpeek."""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

from .parser import LogAnalyzer


def format_timespan(time_span):
    """Format time span as a readable string."""
    if not time_span:
        return "N/A"
    start, end = time_span
    return f"{start.isoformat()} to {end.isoformat()}"


def analyze_file(filepath: str, level_filter: str = None) -> Dict[str, Any]:
    """Analyze a single file and return results as a dict."""
    analyzer = LogAnalyzer()
    success = analyzer.parse_file(filepath)

    if not success:
        return {
            "file": filepath,
            "error": analyzer.errors[0] if analyzer.errors else "Unknown error",
        }

    # Apply level filter if specified
    if level_filter:
        analyzer = analyzer.filter_by_level(level_filter)
        if not analyzer.entries:
            return {
                "file": filepath,
                "error": f"No entries with level {level_filter}",
            }

    time_span = analyzer.time_span()

    return {
        "file": filepath,
        "total_lines": analyzer.total_lines(),
        "levels": analyzer.count_by_level(),
        "time_span": {
            "start": time_span[0].isoformat() if time_span else None,
            "end": time_span[1].isoformat() if time_span else None,
        } if time_span else None,
        "top_loggers": [
            {"name": name, "count": count}
            for name, count in analyzer.top_loggers(5)
        ],
    }


def print_text_report(result: Dict[str, Any]):
    """Print a human-readable report for a file."""
    if "error" in result:
        print(f"Error: {result['file']}: {result['error']}", file=sys.stderr)
        return False

    print(f"File: {result['file']}")
    print(f"  Total lines: {result['total_lines']}")
    print(f"  Levels: {result['levels']}")

    if result["time_span"]:
        print(
            f"  Time span: {result['time_span']['start']} to "
            f"{result['time_span']['end']}"
        )
    else:
        print(f"  Time span: N/A")

    print("  Top loggers:")
    for logger in result["top_loggers"]:
        print(f"    {logger['name']}: {logger['count']}")
    print()
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize structured log files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Log file(s) to analyze",
    )
    parser.add_argument(
        "--level",
        dest="level",
        help="Filter by log level",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    results = []
    has_errors = False

    for filepath in args.files:
        result = analyze_file(filepath, args.level)
        results.append(result)

        if "error" in result:
            has_errors = True

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if not print_text_report(result):
                has_errors = True

    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
