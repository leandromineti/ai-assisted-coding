import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from .parser import parse_line, is_valid_log_file
from .analyzer import LogAnalysis


def process_file(filepath: str, level_filter: Optional[str] = None) -> LogAnalysis:
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.is_dir():
        raise IsADirectoryError(f"Is a directory: {filepath}")

    if not is_valid_log_file(filepath):
        raise ValueError(f"Not a valid log file: {filepath}")

    analysis = LogAnalysis(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                log_line = parse_line(line)
                if log_line:
                    if level_filter is None or log_line.level == level_filter.upper():
                        analysis.add_line(log_line)
    except IOError as e:
        raise IOError(f"Error reading file: {filepath}: {e}")

    return analysis


def format_output_text(analyses: list) -> str:
    output = []
    for analysis in analyses:
        output.append(f"File: {analysis.filepath}")
        output.append(f"  Total lines: {analysis.total_lines}")

        levels = analysis.get_level_counts()
        if levels:
            for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                if level in levels:
                    output.append(f"    {level}: {levels[level]}")

        time_span = analysis.get_time_span()
        if time_span:
            output.append(f"  Time span: {time_span[0].isoformat()} to {time_span[1].isoformat()}")

        top_loggers = analysis.get_top_loggers(5)
        if top_loggers:
            output.append(f"  Top loggers:")
            for name, count in top_loggers:
                output.append(f"    {name}: {count}")

        output.append("")

    return "\n".join(output)


def format_output_json(analyses: list) -> str:
    return json.dumps([a.to_dict() for a in analyses], indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize structured log files'
    )
    parser.add_argument(
        'files',
        nargs='+',
        metavar='FILE',
        help='Log file path(s) to summarize'
    )
    parser.add_argument(
        '--level',
        metavar='NAME',
        help='Filter logs by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    analyses = []
    has_error = False

    for filepath in args.files:
        try:
            analysis = process_file(filepath, args.level)
            analyses.append(analysis)
        except (FileNotFoundError, IsADirectoryError, ValueError, IOError) as e:
            print(f"Error: {e}", file=sys.stderr)
            has_error = True

    if has_error and not analyses:
        sys.exit(1)

    if analyses:
        if args.json:
            print(format_output_json(analyses))
        else:
            print(format_output_text(analyses), end='')

    if has_error:
        sys.exit(1)


if __name__ == '__main__':
    main()
