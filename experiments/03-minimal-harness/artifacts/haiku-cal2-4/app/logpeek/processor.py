import sys
from pathlib import Path
from typing import Optional
from logpeek.parser import LogParser, LogSummary


class FileProcessor:
    def __init__(self):
        self.parser = LogParser()

    def process_file(self, filepath: str, level_filter: Optional[str] = None) -> LogSummary:
        """
        Process a single log file and return a summary.
        Raises FileNotFoundError if file doesn't exist.
        Raises ValueError if file is not a valid log file (contains no parseable lines).
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if not path.is_file():
            raise ValueError(f"Not a file: {filepath}")

        summary = LogSummary()
        valid_entries = 0

        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.rstrip('\n\r')

                    if not line.strip():
                        # Empty line doesn't count as parse error when filtering
                        if level_filter is None:
                            summary.parse_errors += 1
                        continue

                    entry = self.parser.parse(line)
                    if entry:
                        if level_filter is None or entry.level == level_filter:
                            summary.add_entry(entry)
                        valid_entries += 1
                    else:
                        if level_filter is None:
                            summary.record_parse_error()

        except (IOError, OSError) as e:
            raise ValueError(f"Error reading file {filepath}: {e}")

        # Check if this is actually a log file
        if valid_entries == 0 and summary.total_lines() > 0:
            raise ValueError(f"File does not contain valid log entries: {filepath}")

        return summary
