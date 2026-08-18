"""Aggregate parsed log entries into a per-file summary."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .parser import parse_line

TOP_LOGGER_COUNT = 5


class LogFileError(Exception):
    """Raised for a file that logpeek cannot or should not summarize."""


@dataclass
class Summary:
    path: str
    total_lines: int
    parsed_lines: int
    unparsed_lines: int
    level_filter: Optional[str]
    matched_lines: int
    level_counts: Dict[str, int] = field(default_factory=dict)
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    top_loggers: List[Tuple[str, int]] = field(default_factory=list)


def summarize_file(path: str, level_filter: Optional[str] = None) -> Summary:
    """Read and summarize a single log file.

    Raises LogFileError with a human-readable message for anything that
    isn't a usable log file (missing, empty, binary, or no parseable
    lines at all). Never opens the file for writing.
    """
    if not os.path.exists(path):
        raise LogFileError(f"{path}: no such file")
    if not os.path.isfile(path):
        raise LogFileError(f"{path}: not a regular file")
    if os.path.getsize(path) == 0:
        raise LogFileError(f"{path}: file is empty")

    # Individual bytes can be invalid UTF-8 (e.g. a stray Latin-1 byte inside
    # an otherwise well-formed message) without the file as a whole being
    # unreadable, so decoding errors are replaced rather than fatal. A file
    # that is genuinely not text/log data is instead caught below, once no
    # line manages to parse as a log entry.
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    total_lines = len(lines)
    entries = [e for e in (parse_line(line) for line in lines) if e is not None]
    unparsed_lines = total_lines - len(entries)

    if not entries:
        raise LogFileError(
            f"{path}: no recognizable log lines found (not a log file?)"
        )

    if level_filter:
        wanted = level_filter.upper()
        considered = [e for e in entries if e.level.upper() == wanted]
    else:
        considered = entries

    level_counts = dict(Counter(e.level for e in considered))
    top_loggers = Counter(e.logger for e in considered).most_common(TOP_LOGGER_COUNT)

    first_ts = min((e.timestamp for e in considered), default=None)
    last_ts = max((e.timestamp for e in considered), default=None)

    return Summary(
        path=path,
        total_lines=total_lines,
        parsed_lines=len(entries),
        unparsed_lines=unparsed_lines,
        level_filter=level_filter.upper() if level_filter else None,
        matched_lines=len(considered),
        level_counts=level_counts,
        first_timestamp=first_ts,
        last_timestamp=last_ts,
        top_loggers=top_loggers,
    )
