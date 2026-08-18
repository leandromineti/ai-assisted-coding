import re
from datetime import datetime, timezone
from collections import Counter
from typing import Optional, Tuple, Dict, List

LOG_PATTERN = re.compile(
    r'^(?P<timestamp>\S+)\s+(?P<level>\w+)\s+(?P<logger>\S+):\s*(?P<message>.*)$'
)

VALID_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO 8601 or Unix timestamp to datetime (always UTC, timezone-naive)."""
    ts_str = ts_str.strip()

    if not ts_str:
        return None

    try:
        ts_int = int(ts_str)
        return datetime.utcfromtimestamp(ts_int)
    except (ValueError, OSError, OverflowError):
        pass

    iso_formats = [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
    ]

    for fmt in iso_formats:
        try:
            dt = datetime.strptime(ts_str, fmt)
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    return None


class LogParser:
    def __init__(self, level_filter: Optional[str] = None):
        self.level_filter = level_filter
        if level_filter and level_filter.upper() not in VALID_LEVELS:
            raise ValueError(f"Invalid log level: {level_filter}")

    def parse_line(self, line: str) -> Optional[Dict]:
        """Parse a single log line. Returns None if invalid."""
        line = line.rstrip('\n')
        if not line or line.startswith('[') or line.startswith('--'):
            return None

        match = LOG_PATTERN.match(line)
        if not match:
            return None

        level = match.group('level').upper()
        if level not in VALID_LEVELS:
            return None

        ts = parse_timestamp(match.group('timestamp'))
        if ts is None:
            return None

        if self.level_filter and level != self.level_filter.upper():
            return None

        return {
            'timestamp': ts,
            'level': level,
            'logger': match.group('logger'),
            'message': match.group('message'),
        }

    def parse_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """Parse entire file. Returns (valid_entries, errors)."""
        entries = []
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line_no, line in enumerate(f, 1):
                    parsed = self.parse_line(line)
                    if parsed is not None:
                        entries.append(parsed)
                    elif line.strip():
                        errors.append(f"Line {line_no}: Could not parse")
        except (IOError, OSError) as e:
            raise ValueError(f"Cannot read file: {e}")

        return entries, errors


class LogSummary:
    def __init__(self, entries: List[Dict]):
        self.entries = entries

    def total_lines(self) -> int:
        return len(self.entries)

    def level_counts(self) -> Dict[str, int]:
        if not self.entries:
            return {}
        counts = Counter(e['level'] for e in self.entries)
        return dict(sorted(counts.items()))

    def time_span(self) -> Optional[Tuple[datetime, datetime]]:
        if not self.entries:
            return None
        timestamps = [e['timestamp'] for e in self.entries]
        return (min(timestamps), max(timestamps))

    def top_loggers(self, limit: int = 5) -> List[Tuple[str, int]]:
        if not self.entries:
            return []
        counter = Counter(e['logger'] for e in self.entries)
        return counter.most_common(limit)
