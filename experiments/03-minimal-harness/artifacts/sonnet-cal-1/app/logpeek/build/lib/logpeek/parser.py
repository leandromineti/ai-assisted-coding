"""Parsing of structured log lines.

Expected line format::

    TIMESTAMP LEVEL LOGGER.NAME: message text

TIMESTAMP may be an ISO-8601 timestamp (optionally with a UTC offset) or a
Unix epoch (seconds, integer). Lines that don't match this shape are treated
as unparseable and reported separately rather than raised as errors, since
real-world log files routinely contain the odd rotated-log banner, truncated
line, or embedded blob.

Bare integer timestamps are only accepted within a plausible calendar range
(years 2000-2099). This rejects sentinel/boundary values such as 0 (epoch
start) or 4294967295 (the 32-bit unsigned rollover, year 2106) that would
otherwise silently blow out the reported time span to a meaningless range.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

_LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+(?P<level>" + "|".join(LEVELS) + r")\s+(?P<logger>[^:]+):\s*(?P<message>.*)$"
)

_MIN_EPOCH = 946684800  # 2000-01-01T00:00:00+00:00
_MAX_EPOCH = 4102444800  # 2100-01-01T00:00:00+00:00


def _parse_timestamp(raw: str) -> datetime | None:
    if raw.isdigit():
        value = int(raw)
        if not (_MIN_EPOCH <= value < _MAX_EPOCH):
            return None
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    logger: str
    message: str


@dataclass
class ParseResult:
    entries: list[LogEntry] = field(default_factory=list)
    total_lines: int = 0
    unparseable_lines: int = 0


def parse_lines(lines) -> ParseResult:
    """Parse an iterable of raw text lines into a ParseResult."""
    result = ParseResult()
    for raw_line in lines:
        line = raw_line.rstrip("\n").rstrip("\r")
        result.total_lines += 1
        match = _LINE_RE.match(line)
        entry = None
        if match:
            ts = _parse_timestamp(match.group("ts"))
            if ts is not None:
                entry = LogEntry(
                    timestamp=ts,
                    level=match.group("level"),
                    logger=match.group("logger").strip(),
                    message=match.group("message"),
                )
        if entry is None:
            result.unparseable_lines += 1
        else:
            result.entries.append(entry)
    return result
