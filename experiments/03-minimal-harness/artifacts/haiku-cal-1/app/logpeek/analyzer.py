"""Analyze log files."""
from typing import Dict, List, Tuple, Optional
from collections import Counter
from datetime import datetime
from logpeek.parser import parse_log_line


class LogAnalyzer:
    """Analyze a single log file."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines = []
        self.total_lines = 0
        self.level_counts: Dict[str, int] = {}
        self.loggers: List[str] = []
        self.timestamps: List[datetime] = []
        self.parse_errors = 0

    def analyze(self) -> None:
        """Parse and analyze the log file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                self.lines = f.readlines()
        except (IOError, OSError) as e:
            raise ValueError(f"Cannot read file: {e}")

        self.total_lines = len(self.lines)

        if self.total_lines == 0:
            return

        for line in self.lines:
            parsed = parse_log_line(line)
            if parsed is None:
                self.parse_errors += 1
                continue

            timestamp, level, logger, message = parsed
            self.timestamps.append(timestamp)
            self.level_counts[level] = self.level_counts.get(level, 0) + 1
            self.loggers.append(logger)

    def get_time_span(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Return (first_timestamp, last_timestamp) or (None, None) if no valid logs."""
        if not self.timestamps:
            return None, None
        normalized = [ts.replace(tzinfo=None) if ts.tzinfo else ts for ts in self.timestamps]
        return min(normalized), max(normalized)

    def get_top_loggers(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the n most frequent logger names."""
        if not self.loggers:
            return []
        counter = Counter(self.loggers)
        return counter.most_common(n)

    def is_valid_log_file(self) -> bool:
        """Check if the file contains at least one valid log line."""
        return len(self.timestamps) > 0
