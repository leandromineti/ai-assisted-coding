"""Command-line interface for logpeek."""
import sys
import argparse
import json
from typing import List, Dict, Any
from logpeek.analyzer import LogAnalyzer


def format_timestamp(ts) -> str:
    """Format datetime as ISO string (UTC if naive)."""
    if ts is None:
        return ""
    if ts.tzinfo is None:
        return ts.isoformat() + "Z"
    return ts.isoformat()


def analyze_files(filepaths: List[str], level_filter: str = None, as_json: bool = False) -> int:
    """
    Analyze log files and print summary.
    Returns 0 on success, non-zero on error.
    """
    results = []
    has_errors = False

    for filepath in filepaths:
        try:
            analyzer = LogAnalyzer(filepath)
            analyzer.analyze()

            if not analyzer.is_valid_log_file():
                if analyzer.total_lines == 0:
                    print(f"error: {filepath}: empty file", file=sys.stderr)
                else:
                    print(f"error: {filepath}: not a log file", file=sys.stderr)
                has_errors = True
                continue

            first_ts, last_ts = analyzer.get_time_span()

            level_counts = analyzer.level_counts
            if level_filter:
                level_counts = {k: v for k, v in level_counts.items() if k == level_filter}

            top_loggers = analyzer.get_top_loggers(5)

            result = {
                "file": filepath,
                "total_lines": analyzer.total_lines,
                "level_counts": level_counts,
                "time_span": {
                    "first": format_timestamp(first_ts),
                    "last": format_timestamp(last_ts),
                },
                "top_loggers": [{"name": name, "count": count} for name, count in top_loggers],
            }
            results.append(result)

        except ValueError as e:
            print(f"error: {filepath}: {e}", file=sys.stderr)
            has_errors = True
            continue

    if as_json:
        output = {
            "files": results,
            "errors": has_errors,
        }
        print(json.dumps(output, indent=2))
    else:
        for result in results:
            print(f"\n{result['file']}")
            print(f"  total lines: {result['total_lines']}")
            print(f"  level counts: {', '.join(f'{k}={v}' for k, v in sorted(result['level_counts'].items()))}")
            time_first = result['time_span']['first']
            time_last = result['time_span']['last']
            print(f"  time span: {time_first} to {time_last}")
            if result['top_loggers']:
                loggers_str = ", ".join(f"{item['name']}({item['count']})" for item in result['top_loggers'])
                print(f"  top loggers: {loggers_str}")

    return 1 if has_errors else 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="log file paths",
    )
    parser.add_argument(
        "--level",
        type=str,
        default=None,
        help="filter by log level (NAME)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output as JSON",
    )

    args = parser.parse_args()

    exit_code = analyze_files(args.files, level_filter=args.level, as_json=args.json)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
