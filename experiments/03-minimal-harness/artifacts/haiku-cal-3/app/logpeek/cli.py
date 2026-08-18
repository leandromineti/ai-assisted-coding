"""Command-line interface for logpeek."""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
from .parser import parse_log_file


def format_timespan(start, end) -> str:
    """Format time span as a readable string."""
    if start is None or end is None:
        return "N/A"
    return f"{start.isoformat()} to {end.isoformat()}"


def summarize_file(path: str, level_filter: str = None) -> Dict[str, Any]:
    """Summarize a single log file and return result dict."""
    summary, is_valid = parse_log_file(path, level_filter)

    result = {
        "file": path,
        "valid": is_valid,
        "total_lines": summary.total_lines,
    }

    if not is_valid:
        result["error"] = "Not a valid log file"
        return result

    if summary.total_lines == 0:
        result["error"] = "Empty file"
        return result

    result["level_counts"] = summary.get_level_counts()
    start, end = summary.get_time_span()
    result["time_span"] = format_timespan(start, end)
    result["top_loggers"] = summary.get_top_loggers(5)

    return result


def print_text_summary(result: Dict[str, Any]) -> None:
    """Print a human-readable summary."""
    print(f"\n{result['file']}:")
    print(f"  Total lines: {result['total_lines']}")

    if not result["valid"]:
        print(f"  Error: {result.get('error', 'Invalid log file')}")
        return

    if result["total_lines"] == 0:
        print(f"  Error: {result.get('error', 'Empty file')}")
        return

    level_counts = result.get("level_counts", {})
    if level_counts:
        print(f"  Level counts: {level_counts}")

    time_span = result.get("time_span", "N/A")
    print(f"  Time span: {time_span}")

    top_loggers = result.get("top_loggers", [])
    if top_loggers:
        print(f"  Top loggers: {', '.join(top_loggers)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Log file paths to analyze",
    )
    parser.add_argument(
        "--level",
        help="Filter by log level (e.g., INFO, DEBUG, ERROR)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    results = []
    has_error = False

    for file_path in args.files:
        result = summarize_file(file_path, args.level)
        results.append(result)

        if not result["valid"] or result["total_lines"] == 0:
            has_error = True

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        for result in results:
            print_text_summary(result)

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
