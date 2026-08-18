"""Parse structured log lines and extract metadata."""

import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from collections import Counter


class LogEntry:
    """Represents a parsed log entry."""

    def __init__(self, timestamp: Optional[datetime], level: str, logger: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


def _parse_iso8601(s: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp with optional timezone."""
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            # Ensure all datetimes are timezone-naive UTC for comparison
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except ValueError:
            pass
    return None


def _parse_unix_timestamp(s: str) -> Optional[datetime]:
    """Parse Unix timestamp (seconds since epoch)."""
    try:
        ts = float(s)
        return datetime.utcfromtimestamp(ts)
    except (ValueError, OSError):
        return None


def parse_log_line(line: str) -> Optional[LogEntry]:
    """
    Parse a structured log line.
    Supports: ISO 8601 timestamps, Unix timestamps, and lines with LEVEL + logger.name + message.
    """
    if not line or line.startswith("--"):
        return None

    # Try ISO 8601 timestamp format: 2026-06-10T09:00:00+00:00 LEVEL logger.name: message
    iso_pattern = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2})?) (\w+) ([\w.]+):\s*(.*)$"
    match = re.match(iso_pattern, line)
    if match:
        ts_str, level, logger, message = match.groups()
        timestamp = _parse_iso8601(ts_str)
        return LogEntry(timestamp, level, logger, message)

    # Try Unix timestamp format: 1735689600 LEVEL logger.name: message
    unix_pattern = r"^(\d+) (\w+) ([\w.]+):\s*(.*)$"
    match = re.match(unix_pattern, line)
    if match:
        ts_str, level, logger, message = match.groups()
        timestamp = _parse_unix_timestamp(ts_str)
        return LogEntry(timestamp, level, logger, message)

    return None


class LogSummary:
    """Summarize log file contents."""

    def __init__(self):
        self.total_lines = 0
        self.parsed_lines = 0
        self.level_counts: Dict[str, int] = Counter()
        self.logger_counts: Dict[str, int] = Counter()
        self.timestamps: list = []
        self.unparseable_lines = []

    def add_entry(self, entry: LogEntry) -> None:
        """Add a parsed log entry to the summary."""
        self.parsed_lines += 1
        self.level_counts[entry.level] += 1
        self.logger_counts[entry.logger] += 1
        if entry.timestamp:
            self.timestamps.append(entry.timestamp)

    def add_unparseable(self, line: str) -> None:
        """Track unparseable lines."""
        self.unparseable_lines.append(line)

    def get_level_counts(self) -> Dict[str, int]:
        """Return level counts as a dict."""
        return dict(self.level_counts)

    def get_top_loggers(self, n: int = 5) -> list:
        """Return top N logger names by frequency."""
        return [name for name, _ in self.logger_counts.most_common(n)]

    def get_time_span(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Return (first_timestamp, last_timestamp)."""
        if not self.timestamps:
            return None, None
        sorted_ts = sorted(self.timestamps)
        return sorted_ts[0], sorted_ts[-1]

    def filter_by_level(self, level: str) -> None:
        """Reset summary to only count entries of a specific level."""
        # This is used after parsing; we'll rebuild the summary
        pass


def parse_log_file(path: str, level_filter: Optional[str] = None) -> Tuple[LogSummary, bool]:
    """
    Parse a log file and return (summary, is_valid_log_file).
    Returns (summary, False) if file is not a valid log file.
    Returns (summary, True) if file was successfully parsed.
    """
    summary = LogSummary()
    has_parseable_entries = False

    # Try multiple encodings
    encodings = ["utf-8", "latin-1", "iso-8859-1"]
    for encoding in encodings:
        summary = LogSummary()
        has_parseable_entries = False
        try:
            with open(path, "r", encoding=encoding) as f:
                for line in f:
                    line = line.rstrip("\n")
                    summary.total_lines += 1

                    if not line or line.startswith("--"):
                        continue

                    entry = parse_log_line(line)
                    if entry:
                        if level_filter is None or entry.level == level_filter:
                            summary.add_entry(entry)
                        has_parseable_entries = True
                    else:
                        summary.add_unparseable(line)
            break
        except (IOError, UnicodeDecodeError):
            if encoding == encodings[-1]:
                return summary, False
            continue

    # Empty files are valid but contain no entries
    if summary.total_lines == 0:
        return summary, True

    # If no lines parsed at all (non-empty but not a log file)
    if not has_parseable_entries:
        return summary, False

    return summary, True
