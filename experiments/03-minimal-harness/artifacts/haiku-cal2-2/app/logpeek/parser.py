"""Log file parsing and analysis."""

import re
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from collections import Counter


class LogEntry:
    """Represents a single log entry."""

    def __init__(
        self,
        timestamp: datetime,
        level: str,
        logger: str,
        message: str,
    ):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


def parse_log_line(line: str) -> Optional[LogEntry]:
    """
    Parse a structured log line.

    Format: TIMESTAMP LEVEL logger: message
    Example: 2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
    """
    # Match ISO timestamp, level, logger, and message
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s]*)\s+([A-Z]+)\s+([^:]+):\s*(.*)$'
    match = re.match(pattern, line.strip())

    if not match:
        return None

    timestamp_str, level, logger, message = match.groups()

    try:
        # Handle various ISO 8601 formats with and without timezone
        if '+' in timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        elif timestamp_str.endswith('Z'):
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.fromisoformat(timestamp_str)
    except ValueError:
        return None

    return LogEntry(timestamp, level, logger, message)


class LogAnalyzer:
    """Analyzes log files."""

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.errors: List[str] = []

    def parse_file(self, filepath: str) -> bool:
        """
        Parse a log file. Return True if successful, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(f"Failed to read {filepath}: {e}")
            return False

        if not lines:
            self.errors.append(f"{filepath}: empty file")
            return False

        for line_no, line in enumerate(lines, 1):
            line = line.rstrip('\n')
            if not line.strip():
                continue

            entry = parse_log_line(line)
            if entry is None:
                self.errors.append(
                    f"{filepath}:{line_no}: failed to parse log line"
                )
                return False

            self.entries.append(entry)

        if not self.entries:
            self.errors.append(f"{filepath}: no valid log entries found")
            return False

        return True

    def total_lines(self) -> int:
        """Return total number of parsed log entries."""
        return len(self.entries)

    def count_by_level(self) -> Dict[str, int]:
        """Return count of entries per log level."""
        counter = Counter(entry.level for entry in self.entries)
        return dict(counter)

    def time_span(self) -> Optional[Tuple[datetime, datetime]]:
        """Return (first_timestamp, last_timestamp) or None if no entries."""
        if not self.entries:
            return None
        return (self.entries[0].timestamp, self.entries[-1].timestamp)

    def top_loggers(self, count: int = 5) -> List[Tuple[str, int]]:
        """Return top N most frequent logger names."""
        counter = Counter(entry.logger for entry in self.entries)
        return counter.most_common(count)

    def filter_by_level(self, level: str) -> 'LogAnalyzer':
        """Return a new analyzer with entries filtered by level."""
        filtered = LogAnalyzer()
        filtered.entries = [e for e in self.entries if e.level == level]
        return filtered
