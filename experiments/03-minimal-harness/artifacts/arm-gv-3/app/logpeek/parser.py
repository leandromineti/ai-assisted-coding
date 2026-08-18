import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from collections import defaultdict


class LogEntry:
    def __init__(self, timestamp: str, level: str, logger: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


class LogParser:
    """Parser for structured log files with ISO 8601 timestamps."""

    LEVEL_PATTERN = r'DEBUG|INFO|WARNING|ERROR|CRITICAL'
    LINE_PATTERN = rf'^(\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}[^\s]+)\s+({LEVEL_PATTERN})\s+(.+?):\s+(.*)$'

    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        self.entries: List[LogEntry] = []
        self.valid_line_count = 0
        self.invalid_line_count = 0

    def parse_file(self, filepath: str) -> bool:
        """
        Parse a log file. Returns True if at least one valid log line was found.
        Raises an exception if the file cannot be read.
        """
        self.entries = []
        self.valid_line_count = 0
        self.invalid_line_count = 0

        try:
            with open(filepath, 'r', encoding=self.encoding, errors='replace') as f:
                for line in f:
                    line = line.rstrip('\n')
                    if not line:
                        continue

                    match = re.match(self.LINE_PATTERN, line)
                    if match:
                        timestamp, level, logger, message = match.groups()
                        self.entries.append(LogEntry(timestamp, level, logger, message))
                        self.valid_line_count += 1
                    else:
                        self.invalid_line_count += 1
        except Exception as e:
            raise RuntimeError(f"Failed to read {filepath}: {e}")

        return self.valid_line_count > 0

    def get_stats(self, level_filter: Optional[str] = None) -> Dict:
        """Get statistics from parsed logs. If level_filter is set, only count entries with that level."""
        entries = self.entries
        if level_filter:
            entries = [e for e in entries if e.level == level_filter]

        total_lines = len(entries)
        level_counts = defaultdict(int)
        logger_counts = defaultdict(int)

        for entry in entries:
            level_counts[entry.level] += 1
            logger_counts[entry.logger] += 1

        # Get time span
        time_span = None
        if entries:
            try:
                first_ts = datetime.fromisoformat(entries[0].timestamp.replace('Z', '+00:00'))
                last_ts = datetime.fromisoformat(entries[-1].timestamp.replace('Z', '+00:00'))
                time_span = {
                    'start': entries[0].timestamp,
                    'end': entries[-1].timestamp,
                    'duration_seconds': (last_ts - first_ts).total_seconds()
                }
            except ValueError:
                time_span = {
                    'start': entries[0].timestamp,
                    'end': entries[-1].timestamp,
                    'duration_seconds': None
                }

        # Get top 5 loggers
        top_loggers = sorted(logger_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_lines': total_lines,
            'level_counts': dict(level_counts),
            'time_span': time_span,
            'top_loggers': top_loggers
        }
