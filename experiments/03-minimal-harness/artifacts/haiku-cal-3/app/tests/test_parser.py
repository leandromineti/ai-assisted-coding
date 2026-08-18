"""Tests for log parser."""

import unittest
from datetime import datetime
from logpeek.parser import parse_log_line, LogEntry, parse_log_file, LogSummary
import tempfile
import os


class TestParseLogLine(unittest.TestCase):
    """Test individual log line parsing."""

    def test_parse_iso8601_with_utc_timezone(self):
        """Parse ISO 8601 timestamp with UTC timezone."""
        line = "2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "api.http")
        self.assertEqual(entry.message, "listening on :8080")
        self.assertIsNotNone(entry.timestamp)

    def test_parse_iso8601_with_offset_timezone(self):
        """Parse ISO 8601 timestamp with offset timezone."""
        line = "2026-06-10T09:02:00-03:00 WARNING api.db: slow query 300ms"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "WARNING")
        self.assertEqual(entry.logger, "api.db")
        self.assertEqual(entry.message, "slow query 300ms")

    def test_parse_unix_timestamp(self):
        """Parse Unix timestamp."""
        line = "1735689600 INFO daemon.boot: first light"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "daemon.boot")
        self.assertEqual(entry.message, "first light")
        self.assertIsNotNone(entry.timestamp)

    def test_parse_multiword_message(self):
        """Parse message with multiple words."""
        line = "1735693200 DEBUG daemon.loop: garbage collection running"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.message, "garbage collection running")

    def test_parse_logger_with_multiple_dots(self):
        """Parse logger name with multiple dots."""
        line = "2026-02-01T12:00:00+00:00 INFO ingest.a: begin"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.logger, "ingest.a")

    def test_reject_marker_line(self):
        """Reject marker lines starting with --."""
        line = "-- MARK --"
        entry = parse_log_line(line)
        self.assertIsNone(entry)

    def test_reject_empty_line(self):
        """Reject empty lines."""
        entry = parse_log_line("")
        self.assertIsNone(entry)

    def test_reject_invalid_format(self):
        """Reject lines that don't match any known format."""
        line = "this is not a log line"
        entry = parse_log_line(line)
        self.assertIsNone(entry)

    def test_parse_error_level(self):
        """Parse ERROR level."""
        line = "1735700400 ERROR daemon.net: unreachable"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "ERROR")

    def test_parse_debug_level(self):
        """Parse DEBUG level."""
        line = "1738411260 DEBUG ingest.b: shard load"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "DEBUG")


class TestLogSummary(unittest.TestCase):
    """Test LogSummary aggregation."""

    def test_add_entry(self):
        """Test adding entries to summary."""
        summary = LogSummary()
        entry1 = LogEntry(datetime(2026, 1, 1, 10, 0), "INFO", "app.main", "started")
        entry2 = LogEntry(datetime(2026, 1, 1, 11, 0), "ERROR", "app.error", "crash")

        summary.add_entry(entry1)
        summary.add_entry(entry2)

        self.assertEqual(summary.parsed_lines, 2)
        self.assertEqual(summary.level_counts["INFO"], 1)
        self.assertEqual(summary.level_counts["ERROR"], 1)

    def test_level_counts(self):
        """Test level count aggregation."""
        summary = LogSummary()
        summary.add_entry(LogEntry(None, "INFO", "a", "msg"))
        summary.add_entry(LogEntry(None, "INFO", "b", "msg"))
        summary.add_entry(LogEntry(None, "ERROR", "c", "msg"))

        counts = summary.get_level_counts()
        self.assertEqual(counts["INFO"], 2)
        self.assertEqual(counts["ERROR"], 1)

    def test_top_loggers(self):
        """Test getting top loggers by frequency."""
        summary = LogSummary()
        summary.add_entry(LogEntry(None, "INFO", "app.main", "msg"))
        summary.add_entry(LogEntry(None, "INFO", "app.main", "msg"))
        summary.add_entry(LogEntry(None, "INFO", "app.auth", "msg"))
        summary.add_entry(LogEntry(None, "INFO", "app.db", "msg"))

        top = summary.get_top_loggers(2)
        self.assertEqual(top[0], "app.main")
        self.assertEqual(top[1], "app.auth")

    def test_time_span(self):
        """Test time span calculation."""
        summary = LogSummary()
        start = datetime(2026, 1, 1, 10, 0)
        end = datetime(2026, 1, 1, 12, 0)
        summary.add_entry(LogEntry(start, "INFO", "a", "msg"))
        summary.add_entry(LogEntry(end, "INFO", "a", "msg"))

        first, last = summary.get_time_span()
        self.assertEqual(first, start)
        self.assertEqual(last, end)

    def test_time_span_no_timestamps(self):
        """Test time span with no timestamps."""
        summary = LogSummary()
        summary.add_entry(LogEntry(None, "INFO", "a", "msg"))

        first, last = summary.get_time_span()
        self.assertIsNone(first)
        self.assertIsNone(last)


class TestParseLogFile(unittest.TestCase):
    """Test full file parsing."""

    def test_parse_valid_log_file(self):
        """Parse a valid log file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("2026-01-01T10:00:00+00:00 INFO app.main: started\n")
            f.write("2026-01-01T10:01:00+00:00 DEBUG app.db: query\n")
            f.write("2026-01-01T10:02:00+00:00 ERROR app.main: crash\n")
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path)
            self.assertTrue(is_valid)
            self.assertEqual(summary.total_lines, 3)
            self.assertEqual(summary.parsed_lines, 3)
            self.assertEqual(summary.level_counts["INFO"], 1)
            self.assertEqual(summary.level_counts["DEBUG"], 1)
            self.assertEqual(summary.level_counts["ERROR"], 1)
        finally:
            os.unlink(path)

    def test_parse_empty_file(self):
        """Parse an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path)
            self.assertTrue(is_valid)
            self.assertEqual(summary.total_lines, 0)
        finally:
            os.unlink(path)

    def test_parse_invalid_log_file(self):
        """Reject non-log files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("This is not a log file\n")
            f.write("Just some random text\n")
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path)
            self.assertFalse(is_valid)
        finally:
            os.unlink(path)

    def test_parse_with_level_filter(self):
        """Parse with level filter."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("2026-01-01T10:00:00+00:00 INFO app.main: started\n")
            f.write("2026-01-01T10:01:00+00:00 DEBUG app.db: query\n")
            f.write("2026-01-01T10:02:00+00:00 ERROR app.main: crash\n")
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path, level_filter="INFO")
            self.assertTrue(is_valid)
            self.assertEqual(summary.parsed_lines, 1)
            self.assertEqual(summary.level_counts.get("INFO"), 1)
            self.assertEqual(summary.level_counts.get("DEBUG"), None)
        finally:
            os.unlink(path)

    def test_parse_mixed_timestamps(self):
        """Parse file with mixed timestamp formats."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("2026-02-01T12:00:00+00:00 INFO ingest.a: begin\n")
            f.write("1738411260 DEBUG ingest.b: shard load\n")
            f.write("2026-02-01T12:02:00+05:30 INFO ingest.a: row batch 1\n")
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path)
            self.assertTrue(is_valid)
            self.assertEqual(summary.parsed_lines, 3)
        finally:
            os.unlink(path)

    def test_parse_with_markers(self):
        """Parse file with marker lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("2026-01-01T10:00:00+00:00 INFO app.main: started\n")
            f.write("-- MARK --\n")
            f.write("2026-01-01T10:01:00+00:00 DEBUG app.db: query\n")
            f.flush()
            path = f.name

        try:
            summary, is_valid = parse_log_file(path)
            self.assertTrue(is_valid)
            self.assertEqual(summary.total_lines, 3)
            self.assertEqual(summary.parsed_lines, 2)
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        """Handle nonexistent file gracefully."""
        summary, is_valid = parse_log_file("/nonexistent/file.log")
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
