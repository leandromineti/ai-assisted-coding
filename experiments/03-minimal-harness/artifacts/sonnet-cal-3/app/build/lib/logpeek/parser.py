"""Parsing and summarization of structured log files.

Expected log line shape::

    <timestamp> <LEVEL> <logger.name>: <message>

Timestamps may be either ISO 8601 (``2026-06-01T00:00:00+00:00``) or Unix
epoch seconds (``1767233000``). Lines that don't match this shape, or whose
timestamp can't be parsed, are counted as unparsed rather than raising an
error, so a handful of corrupt lines in an otherwise-valid file don't break
the summary.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG_LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+(?P<level>[A-Za-z]+)\s+(?P<logger>[\w.]+):\s*(?P<message>.*)$"
)

TOP_LOGGER_COUNT = 5


class LogFileError(Exception):
    """Raised when a file cannot be summarized (missing, empty, or unreadable as a log)."""


def parse_timestamp(token: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp or Unix epoch-seconds integer. Returns None on failure."""
    dt = None
    try:
        dt = datetime.fromisoformat(token)
    except ValueError:
        pass

    if dt is None:
        try:
            epoch_seconds = int(token)
        except ValueError:
            return None
        try:
            dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    logger: str
    message: str


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse a single log line, or return None if it doesn't look like a log entry."""
    match = LOG_LINE_RE.match(line)
    if not match:
        return None
    timestamp = parse_timestamp(match.group("ts"))
    if timestamp is None:
        return None
    return LogEntry(
        timestamp=timestamp,
        level=match.group("level").upper(),
        logger=match.group("logger"),
        message=match.group("message"),
    )


@dataclass
class FileSummary:
    path: str
    total_lines: int = 0
    parsed_lines: int = 0
    unparsed_lines: int = 0
    level_counts: dict = field(default_factory=dict)
    first_event: Optional[datetime] = None
    last_event: Optional[datetime] = None
    top_loggers: list = field(default_factory=list)  # list[tuple[str, int]]
    level_filter: Optional[str] = None


def summarize_file(path: "str | Path", level_filter: Optional[str] = None) -> FileSummary:
    """Read and summarize a single log file.

    Raises LogFileError if the file doesn't exist, can't be read, is empty,
    or contains no parsable log lines at all.
    """
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except IsADirectoryError:
        raise LogFileError(f"{path}: is a directory, not a file")
    except FileNotFoundError:
        raise LogFileError(f"{path}: no such file")
    except PermissionError:
        raise LogFileError(f"{path}: permission denied")

    if raw == "":
        raise LogFileError(f"{path}: file is empty")

    lines = raw.splitlines()

    level_counts: Counter = Counter()
    logger_counts: Counter = Counter()
    first_event = None
    last_event = None
    parsed_lines = 0
    unparsed_lines = 0
    normalized_filter = level_filter.upper() if level_filter else None

    for line in lines:
        entry = parse_line(line)
        if entry is None:
            unparsed_lines += 1
            continue
        parsed_lines += 1

        if normalized_filter is not None and entry.level != normalized_filter:
            continue

        level_counts[entry.level] += 1
        logger_counts[entry.logger] += 1
        if first_event is None or entry.timestamp < first_event:
            first_event = entry.timestamp
        if last_event is None or entry.timestamp > last_event:
            last_event = entry.timestamp

    if parsed_lines == 0:
        raise LogFileError(f"{path}: no parsable log lines found (not a recognized log format)")

    top_loggers = sorted(logger_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_LOGGER_COUNT]

    return FileSummary(
        path=str(path),
        total_lines=len(lines),
        parsed_lines=parsed_lines,
        unparsed_lines=unparsed_lines,
        level_counts=dict(sorted(level_counts.items())),
        first_event=first_event,
        last_event=last_event,
        top_loggers=top_loggers,
        level_filter=normalized_filter,
    )
