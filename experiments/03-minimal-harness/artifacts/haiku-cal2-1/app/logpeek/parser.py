import json
from datetime import datetime
from typing import NamedTuple, Optional
from collections import Counter, defaultdict


class LogEntry(NamedTuple):
    timestamp: datetime
    level: str
    logger: str
    message: str


class LogSummary(NamedTuple):
    file_path: str
    total_lines: int
    level_counts: dict[str, int]
    time_start: Optional[datetime]
    time_end: Optional[datetime]
    top_loggers: list[tuple[str, int]]


def parse_log_file(file_path: str, level_filter: Optional[str] = None) -> tuple[list[LogEntry], list[str]]:
    """
    Parse a log file and return entries and errors.

    Returns:
        (entries, errors) - entries matching level_filter (if provided), and list of error messages
    """
    entries = []
    errors = []
    line_num = 0

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    parts = line.split(maxsplit=2)
                    if len(parts) < 3:
                        errors.append(f"Line {line_num}: Invalid format (expected timestamp, level, logger)")
                        continue

                    timestamp_str = parts[0]
                    level = parts[1]
                    logger_and_msg = parts[2] if len(parts) > 2 else ""

                    if ':' not in logger_and_msg:
                        errors.append(f"Line {line_num}: Missing logger name")
                        continue

                    logger, message = logger_and_msg.split(':', 1)
                    logger = logger.strip()
                    message = message.strip()

                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        errors.append(f"Line {line_num}: Invalid timestamp format")
                        continue

                    entry = LogEntry(timestamp, level, logger, message)

                    if level_filter is None or level == level_filter:
                        entries.append(entry)

                except Exception as e:
                    errors.append(f"Line {line_num}: {str(e)}")
                    continue

    except UnicodeDecodeError as e:
        errors.append(f"File encoding error: {e}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    return entries, errors


def summarize_log_file(file_path: str, level_filter: Optional[str] = None) -> tuple[LogSummary, list[str]]:
    """
    Summarize a log file.

    Returns:
        (summary, errors) - LogSummary object and list of error messages
    """
    entries, errors = parse_log_file(file_path, level_filter)

    if not entries and errors:
        return None, errors

    level_counts: dict[str, int] = defaultdict(int)
    logger_counts: Counter[str] = Counter()

    for entry in entries:
        level_counts[entry.level] += 1
        logger_counts[entry.logger] += 1

    time_start = entries[0].timestamp if entries else None
    time_end = entries[-1].timestamp if entries else None

    top_loggers = logger_counts.most_common(5)

    summary = LogSummary(
        file_path=file_path,
        total_lines=len(entries),
        level_counts=dict(level_counts),
        time_start=time_start,
        time_end=time_end,
        top_loggers=top_loggers,
    )

    return summary, errors
