import re
from datetime import datetime
from typing import Optional, Tuple
from collections import Counter


class LogEntry:
    def __init__(self, level: str, logger: str, timestamp: Optional[float] = None):
        self.level = level
        self.logger = logger
        self.timestamp = timestamp


class LogParser:
    # ISO 8601 timestamp pattern: 2026-06-10T09:00:00+00:00 or similar
    ISO_PATTERN = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}'

    # Unix timestamp pattern: just digits
    UNIX_PATTERN = r'^\d+$'

    # Log level keywords
    LOG_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}

    @staticmethod
    def parse_line(line: str) -> Optional[LogEntry]:
        """Parse a single log line. Returns LogEntry or None if unparseable."""
        line = line.strip()
        if not line or line.startswith('--') or line.startswith('['):
            return None

        parts = line.split()
        if len(parts) < 3:
            return None

        timestamp_str = parts[0]
        level_str = parts[1]
        logger_str = parts[2] if len(parts) > 2 else None

        if level_str not in LogParser.LOG_LEVELS or not logger_str:
            return None

        timestamp = None

        # Try ISO timestamp
        if re.match(LogParser.ISO_PATTERN, timestamp_str):
            try:
                dt = datetime.fromisoformat(timestamp_str)
                timestamp = dt.timestamp()
            except (ValueError, OSError):
                return None
        # Try Unix timestamp
        elif re.match(LogParser.UNIX_PATTERN, timestamp_str):
            try:
                ts = int(timestamp_str)
                # Validate it's a reasonable timestamp (post-1970, before year 2300)
                if 0 <= ts <= 10413792000:
                    timestamp = float(ts)
                else:
                    return None
            except ValueError:
                return None
        else:
            return None

        return LogEntry(level=level_str, logger=logger_str, timestamp=timestamp)


class LogSummary:
    def __init__(self):
        self.total_lines = 0
        self.levels_count = Counter()
        self.loggers_count = Counter()
        self.timestamps = []

    def add_entry(self, entry: LogEntry):
        self.levels_count[entry.level] += 1
        self.loggers_count[entry.logger] += 1
        if entry.timestamp is not None:
            self.timestamps.append(entry.timestamp)

    def get_time_span(self) -> Optional[Tuple[str, str]]:
        """Return (first_time, last_time) as ISO strings, or None if no valid timestamps."""
        if not self.timestamps:
            return None

        sorted_ts = sorted(self.timestamps)
        first = datetime.fromtimestamp(sorted_ts[0]).isoformat()
        last = datetime.fromtimestamp(sorted_ts[-1]).isoformat()
        return (first, last)

    def get_top_loggers(self, n: int = 5) -> list:
        """Return list of (logger, count) tuples for top n loggers."""
        return self.loggers_count.most_common(n)


def summarize_file(filepath: str, level_filter: Optional[str] = None) -> Tuple[LogSummary, int]:
    """
    Parse a log file and return (LogSummary, line_count).

    Raises:
        IOError: If file cannot be read.
        ValueError: If file has no valid log lines.
    """
    summary = LogSummary()
    total_lines = 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                total_lines += 1
                entry = LogParser.parse_line(line)
                if entry is None:
                    continue

                if level_filter and entry.level != level_filter:
                    continue

                summary.add_entry(entry)
    except IOError as e:
        raise IOError(f"Cannot read file '{filepath}': {e}")

    summary.total_lines = total_lines

    if total_lines == 0:
        raise ValueError(f"File '{filepath}' is empty")

    if summary.levels_count.total() == 0:
        raise ValueError(f"File '{filepath}' contains no valid log entries")

    return summary, total_lines
