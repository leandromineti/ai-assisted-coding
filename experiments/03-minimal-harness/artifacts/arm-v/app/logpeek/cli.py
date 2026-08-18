import sys
import json
import argparse
from pathlib import Path
from .parser import LogParser


def format_human_readable(filepath: str, summary: dict, parse_errors: list) -> str:
    """Format summary for human-readable output."""
    lines = [f"File: {filepath}"]
    lines.append(f"Total lines: {summary['total_lines']}")

    if summary['levels']:
        level_strs = [f"{level}: {count}" for level, count in sorted(summary['levels'].items())]
        lines.append(f"Levels: {', '.join(level_strs)}")
    else:
        lines.append("Levels: (none)")

    if summary['time_span']:
        lines.append(
            f"Time span: {summary['time_span']['start']} to {summary['time_span']['end']}"
        )
    else:
        lines.append("Time span: (no valid timestamps)")

    if summary['top_loggers']:
        logger_strs = [f"{logger}: {count}" for logger, count in summary['top_loggers'].items()]
        lines.append(f"Top loggers: {', '.join(logger_strs)}")
    else:
        lines.append("Top loggers: (none)")

    if parse_errors:
        lines.append(f"Parse errors: {len(parse_errors)} lines with issues")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Log file(s) to summarize"
    )
    parser.add_argument(
        "--level",
        type=str,
        help="Filter to specific log level"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    results = []
    has_fatal_error = False

    for filepath in args.files:
        try:
            log_parser = LogParser()
            log_parser.parse_file(filepath)

            if log_parser.total_lines == 0:
                print(f"Error: {filepath} is empty", file=sys.stderr)
                continue

            if args.level:
                log_parser.filter_by_level(args.level)

            summary = log_parser.get_summary()
            result = {
                "file": filepath,
                "summary": summary,
                "parse_errors": log_parser.parse_errors
            }
            results.append(result)

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            has_fatal_error = True
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            has_fatal_error = True

    if not results:
        if has_fatal_error:
            sys.exit(1)
        sys.exit(1)

    if args.json:
        output = {
            "files": [r["summary"] for r in results]
        }
        if any(r["parse_errors"] for r in results):
            output["parse_errors"] = {
                r["file"]: r["parse_errors"] for r in results if r["parse_errors"]
            }
        print(json.dumps(output, indent=2))
    else:
        for i, result in enumerate(results):
            if i > 0:
                print()
            print(format_human_readable(
                result["file"],
                result["summary"],
                result["parse_errors"]
            ))

    sys.exit(1 if has_fatal_error else 0)


if __name__ == "__main__":
    main()
