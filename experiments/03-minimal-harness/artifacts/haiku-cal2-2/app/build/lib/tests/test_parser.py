"""Tests for log parser."""

import unittest
from datetime import datetime
import tempfile
import os

from logpeek.parser import parse_log_line, LogEntry, LogAnalyzer


class TestParseLogLine(unittest.TestCase):
    """Test log line parsing."""

    def test_parse_standard_log_line(self):
        """Test parsing a standard log line."""
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        entry = parse_log_line(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "boot.init")
        self.assertEqual(entry.message, "kernel handoff")
        self.assertEqual(
            entry.timestamp,
            datetime.fromisoformat("2026-05-31T23:58:00+00:00"),
        )

    def test_parse_with_various_levels(self):
        """Test parsing lines with different log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            line = f"2026-06-01T00:00:00+00:00 {level} test.logger: message"
            entry = parse_log_line(line)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.level, level)

    def test_parse_with_multipart_logger_name(self):
        """Test parsing with dotted logger names."""
        line = "2026-06-01T00:00:00+00:00 INFO api.gw.handler: evt 0"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.logger, "api.gw.handler")

    def test_parse_with_message_containing_spaces(self):
        """Test parsing messages with multiple spaces and special chars."""
        line = "2026-06-01T00:00:00+00:00 INFO logger: complex message with spaces"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.message, "complex message with spaces")

    def test_parse_malformed_line_returns_none(self):
        """Test that malformed lines return None."""
        malformed_lines = [
            "not a log line",
            "2026-06-01T00:00:00+00:00 INVALID",
            "{unterminated json dump",
            "",
        ]
        for line in malformed_lines:
            entry = parse_log_line(line)
            self.assertIsNone(entry)


class TestLogAnalyzer(unittest.TestCase):
    """Test log analysis."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = LogAnalyzer()

    def test_parse_valid_file(self):
        """Test parsing a valid log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-01T00:00:00+00:00 INFO test.logger: msg1\n")
            f.write("2026-06-01T00:00:01+00:00 DEBUG test.logger: msg2\n")
            temp_path = f.name

        try:
            success = self.analyzer.parse_file(temp_path)
            self.assertTrue(success)
            self.assertEqual(self.analyzer.total_lines(), 2)
        finally:
            os.unlink(temp_path)

    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name

        try:
            success = self.analyzer.parse_file(temp_path)
            self.assertFalse(success)
            self.assertIn("empty file", self.analyzer.errors[0])
        finally:
            os.unlink(temp_path)

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file."""
        success = self.analyzer.parse_file("/nonexistent/path.log")
        self.assertFalse(success)
        self.assertTrue(any("Failed to read" in e for e in self.analyzer.errors))

    def test_parse_file_with_invalid_line(self):
        """Test parsing a file with invalid log lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-01T00:00:00+00:00 INFO test.logger: valid\n")
            f.write("invalid log line\n")
            temp_path = f.name

        try:
            success = self.analyzer.parse_file(temp_path)
            self.assertFalse(success)
            self.assertTrue(
                any("failed to parse" in e for e in self.analyzer.errors)
            )
        finally:
            os.unlink(temp_path)

    def test_count_by_level(self):
        """Test counting entries by log level."""
        entries_data = [
            ("2026-06-01T00:00:00+00:00", "INFO", "test", "msg1"),
            ("2026-06-01T00:00:01+00:00", "INFO", "test", "msg2"),
            ("2026-06-01T00:00:02+00:00", "ERROR", "test", "msg3"),
            ("2026-06-01T00:00:03+00:00", "DEBUG", "test", "msg4"),
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for ts, level, logger, msg in entries_data:
                f.write(f"{ts} {level} {logger}: {msg}\n")
            temp_path = f.name

        try:
            self.analyzer.parse_file(temp_path)
            counts = self.analyzer.count_by_level()
            self.assertEqual(counts.get("INFO"), 2)
            self.assertEqual(counts.get("ERROR"), 1)
            self.assertEqual(counts.get("DEBUG"), 1)
        finally:
            os.unlink(temp_path)

    def test_time_span(self):
        """Test time span calculation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-01T00:00:00+00:00 INFO test: msg1\n")
            f.write("2026-06-01T00:00:10+00:00 INFO test: msg2\n")
            f.write("2026-06-01T00:00:20+00:00 INFO test: msg3\n")
            temp_path = f.name

        try:
            self.analyzer.parse_file(temp_path)
            start, end = self.analyzer.time_span()
            self.assertEqual(start.isoformat(), "2026-06-01T00:00:00+00:00")
            self.assertEqual(end.isoformat(), "2026-06-01T00:00:20+00:00")
        finally:
            os.unlink(temp_path)

    def test_top_loggers(self):
        """Test top loggers calculation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for i in range(5):
                f.write(f"2026-06-01T00:00:{i:02d}+00:00 INFO logger.a: msg\n")
            for i in range(3):
                f.write(f"2026-06-01T00:01:{i:02d}+00:00 INFO logger.b: msg\n")
            f.write("2026-06-01T00:02:00+00:00 INFO logger.c: msg\n")
            temp_path = f.name

        try:
            self.analyzer.parse_file(temp_path)
            top = self.analyzer.top_loggers(2)
            self.assertEqual(len(top), 2)
            self.assertEqual(top[0][0], "logger.a")
            self.assertEqual(top[0][1], 5)
            self.assertEqual(top[1][0], "logger.b")
            self.assertEqual(top[1][1], 3)
        finally:
            os.unlink(temp_path)

    def test_filter_by_level(self):
        """Test filtering by log level."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-01T00:00:00+00:00 INFO test: msg1\n")
            f.write("2026-06-01T00:00:01+00:00 ERROR test: msg2\n")
            f.write("2026-06-01T00:00:02+00:00 INFO test: msg3\n")
            temp_path = f.name

        try:
            self.analyzer.parse_file(temp_path)
            filtered = self.analyzer.filter_by_level("INFO")
            self.assertEqual(filtered.total_lines(), 2)
            self.assertEqual(filtered.entries[0].message, "msg1")
            self.assertEqual(filtered.entries[1].message, "msg3")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
