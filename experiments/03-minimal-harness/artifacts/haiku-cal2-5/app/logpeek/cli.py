import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from .parser import parse_log_file, get_level_counts, get_time_span, get_top_loggers


def is_valid_log_file(filepath: str) -> bool:
    """Check if file exists and is readable."""
    try:
        with open(filepath, 'r') as f:
            f.read(1)
        return True
    except (IOError, OSError):
        return False


def analyze_file(filepath: str, level_filter: str = None) -> Dict[str, Any]:
    """Analyze a single log file."""
    if not is_valid_log_file(filepath):
        raise FileNotFoundError(f"Cannot read file: {filepath}")

    try:
        entries, total_lines = parse_log_file(filepath)
    except IOError as e:
        raise IOError(str(e))

    if total_lines == 0:
        raise ValueError(f"Empty file: {filepath}")

    if not entries:
        raise ValueError(f"No valid log entries found in: {filepath}")

    filtered_entries = entries
    if level_filter:
        filtered_entries = [e for e in entries if e.level == level_filter]
        if not filtered_entries:
            raise ValueError(f"No entries with level '{level_filter}' in: {filepath}")

    level_counts = get_level_counts(filtered_entries)
    time_span = get_time_span(filtered_entries)
    top_loggers = get_top_loggers(filtered_entries, top_n=5)

    result = {
        "file": filepath,
        "total_lines": total_lines,
        "valid_entries": len(filtered_entries),
        "level_counts": level_counts,
    }

    if time_span:
        result["time_span"] = {
            "first": time_span[0].isoformat(),
            "last": time_span[1].isoformat(),
        }

    result["top_loggers"] = [{"name": name, "count": count} for name, count in top_loggers]

    return result


def format_text_output(analyses: List[Dict[str, Any]]) -> str:
    """Format analysis results as human-readable text."""
    lines = []
    for analysis in analyses:
        lines.append(f"File: {analysis['file']}")
        lines.append(f"  Total lines: {analysis['total_lines']}")
        lines.append(f"  Valid entries: {analysis['valid_entries']}")

        level_counts = analysis["level_counts"]
        if level_counts:
            counts_str = ", ".join([f"{level}: {count}" for level, count in sorted(level_counts.items())])
            lines.append(f"  Level counts: {counts_str}")

        if "time_span" in analysis and analysis["time_span"]:
            span = analysis["time_span"]
            lines.append(f"  Time span: {span['first']} to {span['last']}")

        if analysis["top_loggers"]:
            lines.append("  Top loggers:")
            for logger_info in analysis["top_loggers"]:
                lines.append(f"    {logger_info['name']}: {logger_info['count']}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files",
        prog="logpeek"
    )
    parser.add_argument("files", nargs="+", help="Log file(s) to analyze")
    parser.add_argument("--level", metavar="NAME", help="Filter by log level")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    analyses = []
    errors = []

    for filepath in args.files:
        try:
            analysis = analyze_file(filepath, args.level)
            analyses.append(analysis)
        except (FileNotFoundError, ValueError, IOError) as e:
            errors.append(str(e))

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not analyses:
        print("Error: No valid files to analyze", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(analyses, indent=2))
    else:
        print(format_text_output(analyses), end="")


if __name__ == "__main__":
    main()
