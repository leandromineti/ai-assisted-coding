"""Turn a ParseResult into the summary statistics logpeek reports."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .parser import LEVELS, ParseResult


@dataclass
class Summary:
    path: str
    total_lines: int
    parsed_lines: int
    unparseable_lines: int
    level_counts: dict
    first_timestamp: str | None
    last_timestamp: str | None
    top_loggers: list

    def to_dict(self) -> dict:
        return {
            "file": self.path,
            "total_lines": self.total_lines,
            "parsed_lines": self.parsed_lines,
            "unparseable_lines": self.unparseable_lines,
            "level_counts": self.level_counts,
            "time_span": {
                "first": self.first_timestamp,
                "last": self.last_timestamp,
            },
            "top_loggers": self.top_loggers,
        }


def summarize(path: str, result: ParseResult, level_filter: str | None = None) -> Summary:
    entries = result.entries
    if level_filter is not None:
        entries = [e for e in entries if e.level == level_filter]

    level_counts = {level: 0 for level in LEVELS}
    for entry in entries:
        level_counts[entry.level] += 1

    if entries:
        ordered = sorted(entries, key=lambda e: e.timestamp)
        first_ts = ordered[0].timestamp.isoformat()
        last_ts = ordered[-1].timestamp.isoformat()
    else:
        first_ts = None
        last_ts = None

    logger_counts = Counter(e.logger for e in entries)
    top_loggers = [
        {"logger": name, "count": count}
        for name, count in logger_counts.most_common(5)
    ]

    return Summary(
        path=path,
        total_lines=result.total_lines,
        parsed_lines=len(entries),
        unparseable_lines=result.unparseable_lines,
        level_counts=level_counts,
        first_timestamp=first_ts,
        last_timestamp=last_ts,
        top_loggers=top_loggers,
    )
