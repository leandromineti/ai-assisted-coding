"""Parsing of individual log lines.

Expected line shape::

    <timestamp> <LEVEL> <logger.name>: <message>

``<timestamp>`` may be an ISO-8601 timestamp with a UTC offset
(``2026-06-01T00:00:00+00:00``) or an integer Unix epoch in seconds
(``1767233000``). Lines that don't match this shape, or whose timestamp
can't be parsed, are reported as unparsed rather than raising.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

_LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+(?P<level>[A-Z][A-Z0-9_]*)\s+(?P<logger>[\w.-]+):\s?(?P<message>.*)$"
)


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    logger: str
    message: str


def _parse_timestamp(token: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(token)
    except ValueError:
        pass

    if re.fullmatch(r"-?\d+", token):
        try:
            return datetime.fromtimestamp(int(token), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    return None


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse a single log line, returning None if it isn't recognized."""
    match = _LINE_RE.match(line.strip("\n"))
    if not match:
        return None

    timestamp = _parse_timestamp(match.group("ts"))
    if timestamp is None:
        return None

    return LogEntry(
        timestamp=timestamp,
        level=match.group("level"),
        logger=match.group("logger"),
        message=match.group("message"),
    )
