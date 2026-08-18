import re
from datetime import datetime
from typing import Optional, Tuple, Dict, List


class LogParser:
    LOG_PATTERN = re.compile(r'^(\S+)\s+(\w+)\s+([^:]+):\s*(.*)$')

    @staticmethod
    def parse_line(line: str) -> Optional[Tuple[str, str, str, str]]:
        match = LogParser.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        return match.groups()

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> datetime:
        return datetime.fromisoformat(timestamp_str)


class LogAnalyzer:
    def __init__(self):
        self.lines_total = 0
        self.levels = {}
        self.loggers = {}
        self.timestamps = []
        self.is_empty = True

    def process_file(self, filepath: str) -> None:
        try:
            with open(filepath, 'rb') as f:
                for line_bytes in f:
                    self.lines_total += 1
                    try:
                        line = line_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        line = line_bytes.decode('utf-8', errors='replace')

                    line = line.rstrip('\n\r')
                    if not line:
                        continue

                    parsed = LogParser.parse_line(line)
                    if parsed:
                        self.is_empty = False
                        timestamp_str, level, logger, message = parsed

                        self.levels[level] = self.levels.get(level, 0) + 1
                        self.loggers[logger] = self.loggers.get(logger, 0) + 1

                        try:
                            ts = LogParser.parse_timestamp(timestamp_str)
                            self.timestamps.append(ts)
                        except (ValueError, TypeError):
                            pass
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except IsADirectoryError:
            raise IsADirectoryError(f"Is a directory: {filepath}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {filepath}")

    def get_level_counts(self) -> Dict[str, int]:
        return self.levels

    def get_top_loggers(self, n: int = 5) -> List[Tuple[str, int]]:
        sorted_loggers = sorted(self.loggers.items(), key=lambda x: -x[1])
        return sorted_loggers[:n]

    def get_time_span(self) -> Tuple[Optional[str], Optional[str]]:
        if not self.timestamps:
            return None, None
        sorted_ts = sorted(self.timestamps)
        first = sorted_ts[0].isoformat()
        last = sorted_ts[-1].isoformat()
        return first, last

    def get_summary(self, level_filter: Optional[str] = None) -> Dict:
        level_counts = self.levels
        if level_filter:
            level_counts = {level_filter: level_counts.get(level_filter, 0)}

        first_ts, last_ts = self.get_time_span()

        return {
            'total_lines': self.lines_total,
            'levels': level_counts,
            'time_start': first_ts,
            'time_end': last_ts,
            'top_loggers': self.get_top_loggers(5),
        }
