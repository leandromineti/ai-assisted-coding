import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class LogEntry:
    def __init__(self, timestamp: datetime, level: str, logger: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


def parse_log_line(line: str) -> Optional[LogEntry]:
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s+(.+)$'
    match = re.match(pattern, line)
    if not match:
        return None

    timestamp_str, level, logger, message = match.groups()
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return LogEntry(timestamp, level, logger, message)
    except ValueError:
        return None


def parse_log_file(filepath: str) -> Tuple[List[LogEntry], int]:
    """Parse a log file and return list of valid entries and total line count."""
    entries = []
    total_lines = 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line:
                    total_lines += 1
                    continue
                total_lines += 1
                entry = parse_log_line(line)
                if entry:
                    entries.append(entry)
    except (IOError, OSError) as e:
        raise IOError(f"Cannot read file '{filepath}': {e}")

    return entries, total_lines


def get_level_counts(entries: List[LogEntry]) -> Dict[str, int]:
    """Count log entries by level."""
    counts = {}
    for entry in entries:
        counts[entry.level] = counts.get(entry.level, 0) + 1
    return counts


def get_time_span(entries: List[LogEntry]) -> Optional[Tuple[datetime, datetime]]:
    """Get the first and last timestamp from entries."""
    if not entries:
        return None
    return entries[0].timestamp, entries[-1].timestamp


def get_top_loggers(entries: List[LogEntry], top_n: int = 5) -> List[Tuple[str, int]]:
    """Get the top N most frequent logger names."""
    logger_counts = {}
    for entry in entries:
        logger_counts[entry.logger] = logger_counts.get(entry.logger, 0) + 1

    sorted_loggers = sorted(logger_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_loggers[:top_n]
