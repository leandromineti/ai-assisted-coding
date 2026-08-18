import re
from datetime import datetime
from collections import Counter
from typing import Optional, Tuple, Dict, List

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+"
    r"(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+"
    r"([^:]+):\s+"
)


class LogParseError(Exception):
    """Raised when a file cannot be parsed as a log file."""
    pass


class LogFile:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.total_lines = 0
        self.level_counts: Dict[str, int] = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        }
        self.first_timestamp: Optional[datetime] = None
        self.last_timestamp: Optional[datetime] = None
        self.logger_names: List[str] = []
        self._parsed = False

    def parse(self) -> None:
        """Parse the log file."""
        if self._parsed:
            return

        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            raise LogParseError(f"Cannot read file: {e}")

        lines = content.strip().split("\n") if content.strip() else []
        self.total_lines = len(lines)

        if self.total_lines == 0:
            self._parsed = True
            return

        loggers = []
        found_valid_line = False

        for line in lines:
            if not line.strip():
                continue

            match = LOG_PATTERN.match(line)
            if not match:
                continue

            found_valid_line = True
            timestamp_str, level, logger_name = match.groups()

            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                continue

            if level in self.level_counts:
                self.level_counts[level] += 1

            loggers.append(logger_name)

            if self.first_timestamp is None:
                self.first_timestamp = timestamp
            self.last_timestamp = timestamp

        if not found_valid_line and self.total_lines > 0:
            raise LogParseError("File does not contain valid log entries")

        self.logger_names = loggers
        self._parsed = True

    def get_top_loggers(self, count: int = 5) -> List[Tuple[str, int]]:
        """Return the top N most frequent logger names."""
        if not self._parsed:
            self.parse()

        counter = Counter(self.logger_names)
        return counter.most_common(count)

    def filter_by_level(self, level: str) -> "LogFile":
        """Create a filtered copy with only entries of a specific level."""
        if not self._parsed:
            self.parse()

        filtered = LogFile(self.filepath)

        # Re-parse to collect only entries of the specified level
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            filtered._parsed = True
            return filtered

        lines = content.strip().split("\n") if content.strip() else []
        loggers = []

        for line in lines:
            if not line.strip():
                continue

            match = LOG_PATTERN.match(line)
            if not match:
                continue

            timestamp_str, entry_level, logger_name = match.groups()

            if entry_level != level:
                continue

            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                continue

            filtered.total_lines += 1
            filtered.level_counts[level] += 1
            loggers.append(logger_name)

            if filtered.first_timestamp is None:
                filtered.first_timestamp = timestamp
            filtered.last_timestamp = timestamp

        filtered.logger_names = loggers
        filtered._parsed = True
        return filtered
