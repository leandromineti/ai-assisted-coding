import sys
import argparse
from logpeek.processor import FileProcessor
from logpeek.formatter import OutputFormatter


def main():
    parser = argparse.ArgumentParser(
        description='Summarize structured log files',
        prog='logpeek',
    )
    parser.add_argument('files', nargs='+', help='Log file(s) to summarize')
    parser.add_argument('--level', help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    processor = FileProcessor()
    formatter = OutputFormatter()

    exit_code = 0
    outputs = []

    for filepath in args.files:
        try:
            summary = processor.process_file(filepath, level_filter=args.level)

            if args.json:
                output = formatter.format_json(filepath, summary)
            else:
                output = formatter.format_text(filepath, summary)

            outputs.append(output)

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            exit_code = 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            exit_code = 1

    if args.json:
        print('[')
        for i, output in enumerate(outputs):
            print(output, end='')
            if i < len(outputs) - 1:
                print(',')
            else:
                print()
        print(']')
    else:
        print('\n'.join(outputs))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
