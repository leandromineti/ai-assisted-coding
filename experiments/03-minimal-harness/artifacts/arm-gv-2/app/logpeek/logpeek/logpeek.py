import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})\s+([A-Z]+)\s+([^:]+):\s+(.*)$"
)


class LogAnalyzer:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.path = Path(filepath)
        self.total_lines = 0
        self.level_counts = Counter()
        self.loggers = Counter()
        self.first_timestamp = None
        self.last_timestamp = None
        self.error = None

    def analyze(self, level_filter: Optional[str] = None) -> bool:
        """Analyze log file. Returns True if successful, False if error."""
        if not self.path.exists():
            self.error = f"File not found: {self.filepath}"
            return False

        if not self.path.is_file():
            self.error = f"Not a file: {self.filepath}"
            return False

        try:
            with open(self.path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            self.error = f"Error reading file: {e}"
            return False

        if len(lines) == 0:
            # Empty file is valid
            return True

        valid_lines = 0
        for line in lines:
            line = line.rstrip("\n")
            match = LOG_PATTERN.match(line)
            if not match:
                # Skip invalid lines
                continue

            timestamp, level, logger, message = match.groups()
            valid_lines += 1
            self.total_lines += 1

            # Apply level filter if specified
            if level_filter and level != level_filter:
                continue

            self.level_counts[level] += 1
            self.loggers[logger] += 1

            if self.first_timestamp is None:
                self.first_timestamp = timestamp
            self.last_timestamp = timestamp

        # If no valid lines found, this is not a valid log file
        if valid_lines == 0 and len(lines) > 0:
            self.error = "File contains no valid log lines"
            return False

        return True

    def get_top_loggers(self, n: int = 5) -> list:
        """Get top N most frequent loggers."""
        return [name for name, count in self.loggers.most_common(n)]

    def to_dict(self) -> dict:
        """Convert analysis to dictionary for output."""
        result = {
            "file": self.filepath,
            "total_lines": self.total_lines,
            "levels": dict(self.level_counts),
        }

        if self.first_timestamp and self.last_timestamp:
            result["time_span"] = {
                "start": self.first_timestamp,
                "end": self.last_timestamp,
            }
        else:
            result["time_span"] = None

        result["top_loggers"] = self.get_top_loggers()

        return result


def format_output(analyzer: LogAnalyzer) -> str:
    """Format analyzer results as human-readable text."""
    lines = [f"File: {analyzer.filepath}"]
    lines.append(f"Total lines: {analyzer.total_lines}")

    # Level counts
    if analyzer.level_counts:
        levels_str = ", ".join(
            f"{level}: {count}" for level, count in sorted(analyzer.level_counts.items())
        )
        lines.append(f"Levels: {levels_str}")
    else:
        lines.append("Levels: (none)")

    # Time span
    if analyzer.first_timestamp and analyzer.last_timestamp:
        lines.append(f"Time span: {analyzer.first_timestamp} to {analyzer.last_timestamp}")
    else:
        lines.append("Time span: N/A")

    # Top loggers
    top_loggers = analyzer.get_top_loggers()
    if top_loggers:
        lines.append(f"Top loggers: {', '.join(top_loggers)}")
    else:
        lines.append("Top loggers: (none)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize structured log files"
    )
    parser.add_argument("files", nargs="+", help="Log file paths")
    parser.add_argument(
        "--level",
        type=str,
        default=None,
        help="Filter by log level (e.g., INFO, ERROR)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    results = []
    exit_code = 0

    for filepath in args.files:
        analyzer = LogAnalyzer(filepath)
        if not analyzer.analyze(args.level):
            print(f"Error: {analyzer.error}", file=sys.stderr)
            exit_code = 1
            continue

        results.append(analyzer)

    if exit_code != 0:
        sys.exit(exit_code)

    if args.json:
        output = json.dumps(
            [analyzer.to_dict() for analyzer in results],
            indent=2
        )
        print(output)
    else:
        output = "\n\n".join(format_output(analyzer) for analyzer in results)
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
