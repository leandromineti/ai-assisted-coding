#!/usr/bin/env python3
import sys
import argparse
from .parser import LogFile, LogParseError
from .formatter import Formatter


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Log file paths to summarize"
    )
    parser.add_argument(
        "--level",
        type=str,
        help="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Validate level if provided
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if args.level and args.level.upper() not in valid_levels:
        print(
            f"Error: invalid log level '{args.level}'. "
            f"Must be one of: {', '.join(sorted(valid_levels))}",
            file=sys.stderr
        )
        sys.exit(1)

    log_files = []
    has_errors = False

    for filepath in args.files:
        try:
            log_file = LogFile(filepath)
            log_file.parse()

            if args.level:
                log_file = log_file.filter_by_level(args.level.upper())

            log_files.append((filepath, log_file))
        except LogParseError as e:
            print(f"Error: {filepath}: {e}", file=sys.stderr)
            has_errors = True
        except FileNotFoundError:
            print(f"Error: {filepath}: file not found", file=sys.stderr)
            has_errors = True
        except Exception as e:
            print(f"Error: {filepath}: {e}", file=sys.stderr)
            has_errors = True

    if has_errors and not log_files:
        sys.exit(1)

    if args.json:
        print(Formatter.format_json(log_files))
    else:
        for filepath, log_file in log_files:
            print(Formatter.format_text(log_file, filepath), end="")
        print()  # Final newline

    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
