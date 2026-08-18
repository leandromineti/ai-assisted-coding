"""Parse structured log lines."""
from datetime import datetime, timezone
from typing import Optional, Tuple


def parse_iso_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp with timezone."""
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            pass
    return None


def parse_unix_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse Unix timestamp (seconds since epoch) as UTC."""
    try:
        ts = int(ts_str)
        return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
    except (ValueError, OSError, OverflowError):
        return None


def parse_log_line(line: str) -> Optional[Tuple[datetime, str, str, str]]:
    """
    Parse a log line and return (timestamp, level, logger, message).
    Returns None if the line is not a valid log line.
    """
    line = line.rstrip('\n')
    if not line or line.startswith('--') or line.startswith('['):
        return None

    parts = line.split(None, 2)
    if len(parts) < 3:
        return None

    ts_str = parts[0]
    level = parts[1]
    logger_and_msg = parts[2]

    if ':' not in logger_and_msg:
        return None

    logger, message = logger_and_msg.split(':', 1)
    logger = logger.strip()
    message = message.strip()

    timestamp = parse_iso_timestamp(ts_str)
    if timestamp is None:
        timestamp = parse_unix_timestamp(ts_str)

    if timestamp is None:
        return None

    return timestamp, level, logger, message
