import re
from collections import Counter
from datetime import datetime
from typing import Optional, List, Dict, Tuple


class LogParseError(Exception):
    """Raised when a log file cannot be parsed."""
    pass


class LogEntry:
    """Represents a single log entry."""

    def __init__(self, timestamp: str, level: str, logger_name: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger_name = logger_name
        self.message = message

    @staticmethod
    def parse(line: str) -> Optional["LogEntry"]:
        """Parse a log line. Returns None if the line doesn't match the expected format."""
        # Expected format: ISO_TIMESTAMP LEVEL logger_name: message
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s+(.*)$'
        match = re.match(pattern, line.rstrip('\n'))
        if match:
            timestamp, level, logger_name, message = match.groups()
            return LogEntry(timestamp, level, logger_name, message)
        return None


class LogSummary:
    """Summarizes a structured log file."""

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.level_counts: Dict[str, int] = {}
        self.logger_counts: Counter = Counter()

    def add_entry(self, entry: LogEntry) -> None:
        """Add a parsed log entry."""
        self.entries.append(entry)
        self.level_counts[entry.level] = self.level_counts.get(entry.level, 0) + 1
        self.logger_counts[entry.logger_name] += 1

    def get_time_span(self) -> Tuple[Optional[str], Optional[str]]:
        """Return (first_timestamp, last_timestamp) or (None, None) if no entries."""
        if not self.entries:
            return None, None
        return self.entries[0].timestamp, self.entries[-1].timestamp

    def get_top_loggers(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the n most frequent logger names."""
        return self.logger_counts.most_common(n)

    def filter_by_level(self, level: str) -> "LogSummary":
        """Return a new LogSummary with only entries matching the given level."""
        filtered = LogSummary()
        for entry in self.entries:
            if entry.level.upper() == level.upper():
                filtered.add_entry(entry)
        return filtered


def parse_log_file(filepath: str, filter_level: Optional[str] = None) -> LogSummary:
    """
    Parse a log file and return a LogSummary.
    Raises LogParseError if the file cannot be parsed or is not a valid log file.
    """
    summary = LogSummary()
    has_valid_lines = False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n')
                if not line.strip():
                    continue

                entry = LogEntry.parse(line)
                if entry is None:
                    # If we've seen valid entries and now see an invalid one, it's still a log file
                    # (e.g., malformed lines in the middle). Only raise if no valid entries found yet.
                    continue

                has_valid_lines = True
                summary.add_entry(entry)

        if not has_valid_lines:
            raise LogParseError(f"No valid log entries found in {filepath}")

    except IOError as e:
        raise LogParseError(f"Cannot read file {filepath}: {e}")

    if filter_level:
        summary = summary.filter_by_level(filter_level)

    return summary
