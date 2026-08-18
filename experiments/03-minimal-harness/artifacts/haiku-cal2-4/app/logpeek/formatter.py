import json
from typing import List, Dict, Any
from logpeek.parser import LogSummary


class OutputFormatter:
    def format_text(self, filepath: str, summary: LogSummary) -> str:
        """Format summary as human-readable text."""
        lines = [f"File: {filepath}"]
        lines.append(f"Total lines: {summary.total_lines()}")

        level_counts = summary.get_level_counts()
        if level_counts:
            for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                count = level_counts.get(level, 0)
                if count > 0:
                    lines.append(f"  {level}: {count}")

        time_span = summary.get_time_span()
        if time_span:
            start, end = time_span
            lines.append(f"Time span: {start.isoformat()} to {end.isoformat()}")

        top_loggers = summary.get_top_loggers(5)
        if top_loggers:
            lines.append("Top 5 loggers:")
            for logger, count in top_loggers:
                lines.append(f"  {logger}: {count}")

        return '\n'.join(lines)

    def format_json(self, filepath: str, summary: LogSummary) -> str:
        """Format summary as JSON."""
        data = {
            'file': filepath,
            'total_lines': summary.total_lines(),
            'level_counts': summary.get_level_counts(),
        }

        time_span = summary.get_time_span()
        if time_span:
            start, end = time_span
            data['time_span'] = {
                'start': start.isoformat(),
                'end': end.isoformat(),
            }
        else:
            data['time_span'] = None

        top_loggers = summary.get_top_loggers(5)
        data['top_loggers'] = [{'name': name, 'count': count} for name, count in top_loggers]

        return json.dumps(data)
