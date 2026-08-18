from collections import Counter
from typing import Optional, Dict, List
from datetime import datetime
from .parser import LogLine


class LogAnalysis:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.total_lines = 0
        self.levels = Counter()
        self.loggers = Counter()
        self.first_timestamp: Optional[datetime] = None
        self.last_timestamp: Optional[datetime] = None

    def add_line(self, log_line: LogLine) -> None:
        self.total_lines += 1
        self.levels[log_line.level] += 1
        self.loggers[log_line.logger] += 1

        if log_line.timestamp:
            if self.first_timestamp is None:
                self.first_timestamp = log_line.timestamp
            self.last_timestamp = log_line.timestamp

    def get_top_loggers(self, n: int = 5) -> List[tuple]:
        return self.loggers.most_common(n)

    def get_level_counts(self) -> Dict[str, int]:
        return dict(self.levels)

    def get_time_span(self) -> Optional[tuple]:
        if self.first_timestamp and self.last_timestamp:
            return (self.first_timestamp, self.last_timestamp)
        return None

    def to_dict(self) -> dict:
        time_span = self.get_time_span()
        result = {
            'file': self.filepath,
            'total_lines': self.total_lines,
            'levels': self.get_level_counts(),
            'top_loggers': [{'name': name, 'count': count} for name, count in self.get_top_loggers()],
        }
        if time_span:
            result['time_span'] = {
                'first': time_span[0].isoformat(),
                'last': time_span[1].isoformat(),
            }
        return result
