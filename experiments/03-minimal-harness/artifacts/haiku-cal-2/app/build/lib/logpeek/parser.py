import re
from datetime import datetime
from typing import Optional, Tuple


class LogLine:
    def __init__(self, timestamp: Optional[datetime], level: str, logger: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message


def parse_iso8601_timestamp(s: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def parse_unix_timestamp(s: str) -> Optional[datetime]:
    try:
        ts = int(s)
        if 0 <= ts <= 2**32 - 1:
            return datetime.fromtimestamp(ts)
    except (ValueError, TypeError, OSError):
        pass
    return None


def parse_line(line: str) -> Optional[LogLine]:
    line = line.rstrip('\n\r')
    if not line or line.startswith('--') or line.startswith('['):
        return None

    parts = line.split(None, 3)
    if len(parts) < 3:
        return None

    timestamp_str = parts[0]
    level_str = parts[1]
    logger_str = parts[2]

    timestamp = parse_iso8601_timestamp(timestamp_str) or parse_unix_timestamp(timestamp_str)

    level_str = level_str.upper()
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if level_str not in valid_levels:
        return None

    message = parts[3] if len(parts) > 3 else ""

    return LogLine(timestamp, level_str, logger_str, message)


def is_valid_log_file(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.rstrip('\n\r')
                if line and not line.startswith('--') and not line.startswith('['):
                    parts = line.split(None, 3)
                    if len(parts) >= 3:
                        timestamp_str = parts[0]
                        level_str = parts[1].upper()
                        if (parse_iso8601_timestamp(timestamp_str) or parse_unix_timestamp(timestamp_str)):
                            if level_str in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
                                return True
        return False
    except (IOError, OSError):
        return False
