import json
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from collections import Counter


class LogParser:
    """Parse structured log files and extract summary information."""

    LOG_PATTERN = re.compile(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s]*)\s+(\w+)\s+([^:]+):\s*(.*)$'
    )

    def __init__(self):
        self.lines = []
        self.timestamps = []
        self.levels = Counter()
        self.loggers = Counter()
        self.parse_errors = []
        self.total_lines = 0

    def parse_file(self, filepath: str) -> None:
        """Parse a log file and populate summary data."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n')
                    if not line:
                        continue

                    self.total_lines += 1
                    self.lines.append(line)
                    match = self.LOG_PATTERN.match(line)

                    if match:
                        timestamp_str, level, logger, message = match.groups()
                        self.levels[level] += 1
                        self.loggers[logger] += 1
                        try:
                            ts = datetime.fromisoformat(timestamp_str)
                            self.timestamps.append(ts)
                        except ValueError:
                            self.parse_errors.append(
                                f"Line {line_num}: invalid timestamp format"
                            )
                    else:
                        self.parse_errors.append(
                            f"Line {line_num}: does not match log format"
                        )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except Exception as e:
            raise RuntimeError(f"Error reading file: {e}")

    def get_summary(self) -> Dict:
        """Return a summary of the parsed log file."""
        summary = {
            "total_lines": len(self.lines),
            "levels": dict(self.levels),
            "top_loggers": dict(self.loggers.most_common(5)),
        }

        if self.timestamps:
            summary["time_span"] = {
                "start": self.timestamps[0].isoformat(),
                "end": self.timestamps[-1].isoformat(),
            }
        else:
            summary["time_span"] = None

        return summary

    def filter_by_level(self, level: str) -> None:
        """Filter lines to only those matching the given level."""
        filtered_lines = []
        filtered_timestamps = []
        filtered_levels = Counter()
        filtered_loggers = Counter()
        new_errors = []

        for i, line in enumerate(self.lines, 1):
            match = self.LOG_PATTERN.match(line)
            if match:
                timestamp_str, log_level, logger, message = match.groups()
                if log_level == level:
                    filtered_lines.append(line)
                    filtered_loggers[logger] += 1
                    filtered_levels[log_level] += 1
                    if self.timestamps and i - 1 < len(self.timestamps):
                        filtered_timestamps.append(self.timestamps[i - 1])

        self.lines = filtered_lines
        self.levels = filtered_levels
        self.loggers = filtered_loggers
        self.timestamps = filtered_timestamps
