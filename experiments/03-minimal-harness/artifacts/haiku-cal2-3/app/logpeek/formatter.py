import json
from typing import Dict, List, Tuple, Optional
from logpeek.parser import LogSummary


class OutputFormatter:
    """Formats log summaries for output."""

    @staticmethod
    def text_format(filepath: str, summary: LogSummary) -> str:
        """Format summary as human-readable text."""
        lines = []
        lines.append(f"\n{filepath}")
        lines.append("=" * 60)

        total_lines = len(summary.entries)
        lines.append(f"Total lines: {total_lines}")

        # Level counts
        lines.append("Level counts:")
        for level in sorted(summary.level_counts.keys()):
            count = summary.level_counts[level]
            lines.append(f"  {level}: {count}")

        # Time span
        first_ts, last_ts = summary.get_time_span()
        if first_ts and last_ts:
            lines.append(f"Time span: {first_ts} to {last_ts}")

        # Top loggers
        top_loggers = summary.get_top_loggers(5)
        if top_loggers:
            lines.append("Top 5 loggers:")
            for logger_name, count in top_loggers:
                lines.append(f"  {logger_name}: {count}")

        return "\n".join(lines)

    @staticmethod
    def json_format(filepath: str, summary: LogSummary) -> str:
        """Format summary as JSON."""
        first_ts, last_ts = summary.get_time_span()
        top_loggers = summary.get_top_loggers(5)

        data = {
            "file": filepath,
            "total_lines": len(summary.entries),
            "level_counts": summary.level_counts,
            "time_span": {
                "first": first_ts,
                "last": last_ts,
            },
            "top_loggers": [
                {"name": name, "count": count}
                for name, count in top_loggers
            ],
        }

        return json.dumps(data)
