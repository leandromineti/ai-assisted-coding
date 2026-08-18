#!/usr/bin/env python3
import argparse
import sys
from logpeek.parser import parse_log_file, LogParseError
from logpeek.formatter import OutputFormatter


def main():
    """Main entry point for the logpeek CLI."""
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Log file(s) to summarize",
    )
    parser.add_argument(
        "--level",
        metavar="NAME",
        help="Filter by log level (case-insensitive)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    formatter = OutputFormatter()
    has_error = False
    outputs = []

    for filepath in args.files:
        try:
            summary = parse_log_file(filepath, filter_level=args.level)

            if args.json:
                outputs.append(formatter.json_format(filepath, summary))
            else:
                outputs.append(formatter.text_format(filepath, summary))

        except LogParseError as e:
            print(f"Error: {e}", file=sys.stderr)
            has_error = True
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            has_error = True

    # Print all outputs
    if args.json:
        # For JSON, output an array if multiple files
        if len(outputs) == 1:
            print(outputs[0])
        else:
            print("[")
            for i, output in enumerate(outputs):
                print(output, end="")
                if i < len(outputs) - 1:
                    print(",")
                else:
                    print()
            print("]")
    else:
        # For text, just concatenate with blank lines
        print("\n".join(outputs))

    # Exit with non-zero code if any file had an error
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
