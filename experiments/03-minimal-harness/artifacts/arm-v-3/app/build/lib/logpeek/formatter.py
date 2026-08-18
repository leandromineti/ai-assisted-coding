import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .parser import LogFile


class Formatter:
    @staticmethod
    def format_text(log_file: LogFile, filepath: str) -> str:
        """Format a log file summary as human-readable text."""
        lines = [f"\n{filepath}:"]

        lines.append(f"  Total lines: {log_file.total_lines}")

        levels_line = "  Levels: "
        level_parts = []
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            count = log_file.level_counts[level]
            if count > 0:
                level_parts.append(f"{level} ({count})")
        if level_parts:
            lines.append(levels_line + ", ".join(level_parts))
        else:
            lines.append(levels_line + "(none)")

        if log_file.first_timestamp and log_file.last_timestamp:
            time_span = (
                f"{log_file.first_timestamp.isoformat()} to "
                f"{log_file.last_timestamp.isoformat()}"
            )
            lines.append(f"  Time span: {time_span}")
        else:
            lines.append("  Time span: (no log entries)")

        top_loggers = log_file.get_top_loggers(5)
        if top_loggers:
            lines.append("  Top 5 loggers:")
            for logger_name, count in top_loggers:
                lines.append(f"    {logger_name}: {count}")
        else:
            lines.append("  Top 5 loggers: (none)")

        return "\n".join(lines)

    @staticmethod
    def format_json(log_files: List[Tuple[str, LogFile]]) -> str:
        """Format log file summaries as JSON."""
        result = {}

        for filepath, log_file in log_files:
            top_loggers = log_file.get_top_loggers(5)
            result[filepath] = {
                "total_lines": log_file.total_lines,
                "levels": {
                    level: log_file.level_counts[level]
                    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                "time_span": (
                    {
                        "first": log_file.first_timestamp.isoformat(),
                        "last": log_file.last_timestamp.isoformat(),
                    }
                    if log_file.first_timestamp and log_file.last_timestamp
                    else None
                ),
                "top_loggers": (
                    {logger_name: count for logger_name, count in top_loggers}
                    if top_loggers
                    else {}
                ),
            }

        return json.dumps(result, indent=2)
