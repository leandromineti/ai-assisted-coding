import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Tuple


class LogEntry:
    def __init__(self, timestamp: datetime, level: str, logger: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


class LogParser:
    ISO8601_PATTERN = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})'
    LEVEL_PATTERN = r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b'

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse a single log line. Returns None if parsing fails."""
        timestamp_match = re.search(self.ISO8601_PATTERN, line)
        if not timestamp_match:
            return None

        level_match = re.search(self.LEVEL_PATTERN, line)
        if not level_match:
            return None

        try:
            timestamp_str = timestamp_match.group(1)
            timestamp = datetime.fromisoformat(timestamp_str)
            level = level_match.group(1)

            # Extract logger name: look for pattern after level (e.g. "INFO boot.init:")
            level_pos = level_match.end()
            rest = line[level_pos:].lstrip()
            logger_match = re.match(r'([a-zA-Z0-9._-]+):', rest)
            logger = logger_match.group(1) if logger_match else "unknown"

            # Extract message: everything after the logger name
            if logger_match:
                message = rest[logger_match.end():].strip()
            else:
                message = rest

            return LogEntry(timestamp, level, logger, message)
        except (ValueError, AttributeError):
            return None


class LogSummary:
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.parse_errors = 0
        self.levels = Counter()
        self.loggers = Counter()

    def add_entry(self, entry: LogEntry):
        self.entries.append(entry)
        self.levels[entry.level] += 1
        self.loggers[entry.logger] += 1

    def record_parse_error(self):
        self.parse_errors += 1

    def total_lines(self) -> int:
        return len(self.entries) + self.parse_errors

    def get_level_counts(self) -> Dict[str, int]:
        return dict(self.levels)

    def get_time_span(self) -> Optional[Tuple[datetime, datetime]]:
        if not self.entries:
            return None
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp)
        return (sorted_entries[0].timestamp, sorted_entries[-1].timestamp)

    def get_top_loggers(self, n: int = 5) -> List[Tuple[str, int]]:
        return self.loggers.most_common(n)
