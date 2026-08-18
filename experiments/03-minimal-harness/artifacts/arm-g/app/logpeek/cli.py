import argparse
import json
import sys
from pathlib import Path
from .parser import LogAnalyzer


def format_summary(analyzer: LogAnalyzer, filepath: str, level_filter=None):
    summary = analyzer.get_summary(level_filter)
    first_ts, last_ts = summary['time_start'], summary['time_end']

    output = {
        'file': filepath,
        'total_lines': summary['total_lines'],
        'levels': summary['levels'],
        'time_span': {
            'start': first_ts,
            'end': last_ts,
        },
        'top_loggers': [
            {'name': name, 'count': count} for name, count in summary['top_loggers']
        ],
    }
    return output


def format_text_summary(analyzer: LogAnalyzer, filepath: str, level_filter=None):
    summary = analyzer.get_summary(level_filter)
    first_ts, last_ts = summary['time_start'], summary['time_end']
    top_loggers = summary['top_loggers']

    lines = [f"File: {filepath}"]
    lines.append(f"Total lines: {summary['total_lines']}")

    if summary['levels']:
        level_parts = [f"{level}: {count}" for level, count in summary['levels'].items()]
        lines.append(f"Levels: {', '.join(level_parts)}")
    else:
        lines.append("Levels: (none)")

    if first_ts and last_ts:
        lines.append(f"Time span: {first_ts} to {last_ts}")
    else:
        lines.append("Time span: (empty)")

    if top_loggers:
        logger_parts = [f"{name} ({count})" for name, count in top_loggers]
        lines.append(f"Top loggers: {', '.join(logger_parts)}")
    else:
        lines.append("Top loggers: (none)")

    return '\n'.join(lines)


def is_log_file(filepath: str) -> bool:
    """Check if file appears to be a log file by sampling content."""
    try:
        with open(filepath, 'rb') as f:
            for _ in range(min(10, 100)):  # Sample first 10 lines
                line_bytes = f.readline()
                if not line_bytes:
                    break
                try:
                    line = line_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    line = line_bytes.decode('utf-8', errors='replace')

                line = line.rstrip('\n\r')
                if not line:
                    continue

                # Check if line matches log pattern
                from .parser import LogParser
                if LogParser.parse_line(line):
                    return True

        # If we got here and the file is empty, treat it as a valid log file
        path = Path(filepath)
        if path.stat().st_size == 0:
            return True

        return False
    except (IsADirectoryError, PermissionError, FileNotFoundError):
        return True  # Let parser handle these errors


def main():
    parser = argparse.ArgumentParser(
        description='Summarize structured log files',
        prog='logpeek',
    )
    parser.add_argument('files', nargs='+', help='Log file(s) to analyze')
    parser.add_argument('--level', dest='level_filter', help='Filter by log level')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    results = []
    has_error = False

    for filepath in args.files:
        try:
            if not is_log_file(filepath):
                print(
                    f"Error: {filepath} does not appear to be a log file",
                    file=sys.stderr,
                )
                has_error = True
                continue

            analyzer = LogAnalyzer()
            analyzer.process_file(filepath)

            if args.json:
                result = format_summary(analyzer, filepath, args.level_filter)
                results.append(result)
            else:
                output = format_text_summary(analyzer, filepath, args.level_filter)
                print(output)
                print()

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            has_error = True
        except IsADirectoryError as e:
            print(f"Error: {e}", file=sys.stderr)
            has_error = True
        except PermissionError as e:
            print(f"Error: {e}", file=sys.stderr)
            has_error = True
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            has_error = True

    if args.json:
        print(json.dumps(results, indent=2))

    if has_error:
        sys.exit(1)


if __name__ == '__main__':
    main()
