import unittest
import tempfile
import os
from logpeek.parser import LogEntry, LogSummary, parse_log_file, LogParseError


class TestLogEntry(unittest.TestCase):
    """Test LogEntry parsing."""

    def test_parse_valid_entry(self):
        """Test parsing a valid log line."""
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        entry = LogEntry.parse(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.timestamp, "2026-05-31T23:58:00+00:00")
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger_name, "boot.init")
        self.assertEqual(entry.message, "kernel handoff")

    def test_parse_with_different_levels(self):
        """Test parsing entries with different log levels."""
        lines = [
            "2026-05-31T23:58:00+00:00 DEBUG boot.svc: unit graph built",
            "2026-05-31T23:58:00+00:00 WARNING boot.svc: swap disabled",
            "2026-05-31T23:58:00+00:00 ERROR api.gw: evt 2 code 6",
            "2026-05-31T23:58:00+00:00 CRITICAL api.gw: evt 5 code 3",
        ]
        expected_levels = ["DEBUG", "WARNING", "ERROR", "CRITICAL"]

        for line, expected_level in zip(lines, expected_levels):
            entry = LogEntry.parse(line)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.level, expected_level)

    def test_parse_invalid_format(self):
        """Test that invalid lines return None."""
        invalid_lines = [
            "not a log line",
            "2026-05-31T23:58:00+00:00 INFO",  # missing logger and message
            "{unterminated json dump",  # malformed JSON
            "",  # empty line
        ]

        for line in invalid_lines:
            entry = LogEntry.parse(line)
            self.assertIsNone(entry)

    def test_parse_with_colon_in_message(self):
        """Test parsing when message contains colons."""
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: error: something failed"
        entry = LogEntry.parse(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.message, "error: something failed")


class TestLogSummary(unittest.TestCase):
    """Test LogSummary aggregation."""

    def test_add_entry(self):
        """Test adding entries to summary."""
        summary = LogSummary()
        entry = LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot.init", "test")
        summary.add_entry(entry)

        self.assertEqual(len(summary.entries), 1)
        self.assertEqual(summary.level_counts["INFO"], 1)
        self.assertEqual(summary.logger_counts["boot.init"], 1)

    def test_level_counts(self):
        """Test level counting."""
        summary = LogSummary()
        entries = [
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot.init", "msg1"),
            LogEntry("2026-05-31T23:58:01+00:00", "INFO", "boot.svc", "msg2"),
            LogEntry("2026-05-31T23:58:02+00:00", "DEBUG", "boot.svc", "msg3"),
            LogEntry("2026-05-31T23:58:03+00:00", "WARNING", "boot.svc", "msg4"),
        ]

        for entry in entries:
            summary.add_entry(entry)

        self.assertEqual(summary.level_counts["INFO"], 2)
        self.assertEqual(summary.level_counts["DEBUG"], 1)
        self.assertEqual(summary.level_counts["WARNING"], 1)

    def test_logger_counts(self):
        """Test logger name counting."""
        summary = LogSummary()
        entries = [
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot.init", "msg1"),
            LogEntry("2026-05-31T23:58:01+00:00", "INFO", "boot.svc", "msg2"),
            LogEntry("2026-05-31T23:58:02+00:00", "INFO", "boot.svc", "msg3"),
        ]

        for entry in entries:
            summary.add_entry(entry)

        self.assertEqual(summary.logger_counts["boot.init"], 1)
        self.assertEqual(summary.logger_counts["boot.svc"], 2)

    def test_get_time_span_with_entries(self):
        """Test time span calculation with entries."""
        summary = LogSummary()
        summary.add_entry(LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot", "msg1"))
        summary.add_entry(LogEntry("2026-05-31T23:58:05+00:00", "INFO", "boot", "msg2"))

        first, last = summary.get_time_span()
        self.assertEqual(first, "2026-05-31T23:58:00+00:00")
        self.assertEqual(last, "2026-05-31T23:58:05+00:00")

    def test_get_time_span_empty(self):
        """Test time span with no entries."""
        summary = LogSummary()
        first, last = summary.get_time_span()
        self.assertIsNone(first)
        self.assertIsNone(last)

    def test_get_top_loggers(self):
        """Test getting top loggers."""
        summary = LogSummary()
        entries = [
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "a", "msg1"),
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "a", "msg2"),
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "b", "msg3"),
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "b", "msg4"),
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "c", "msg5"),
        ]

        for entry in entries:
            summary.add_entry(entry)

        top_5 = summary.get_top_loggers(5)
        self.assertEqual(len(top_5), 3)
        self.assertEqual(top_5[0][0], "a")
        self.assertEqual(top_5[0][1], 2)

    def test_filter_by_level(self):
        """Test filtering entries by log level."""
        summary = LogSummary()
        entries = [
            LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot", "msg1"),
            LogEntry("2026-05-31T23:58:01+00:00", "DEBUG", "boot", "msg2"),
            LogEntry("2026-05-31T23:58:02+00:00", "INFO", "boot", "msg3"),
        ]

        for entry in entries:
            summary.add_entry(entry)

        filtered = summary.filter_by_level("INFO")
        self.assertEqual(len(filtered.entries), 2)
        self.assertEqual(filtered.level_counts["INFO"], 2)
        self.assertNotIn("DEBUG", filtered.level_counts)

    def test_filter_by_level_case_insensitive(self):
        """Test that level filtering is case-insensitive."""
        summary = LogSummary()
        summary.add_entry(LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot", "msg1"))
        summary.add_entry(LogEntry("2026-05-31T23:58:01+00:00", "DEBUG", "boot", "msg2"))

        filtered = summary.filter_by_level("info")
        self.assertEqual(len(filtered.entries), 1)


class TestParseLogFile(unittest.TestCase):
    """Test log file parsing."""

    def test_parse_simple_log_file(self):
        """Test parsing a simple log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready\n")
            f.write("2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built\n")
            temp_path = f.name

        try:
            summary = parse_log_file(temp_path)
            self.assertEqual(len(summary.entries), 3)
            self.assertEqual(summary.level_counts["INFO"], 2)
            self.assertEqual(summary.level_counts["DEBUG"], 1)
        finally:
            os.unlink(temp_path)

    def test_parse_with_malformed_lines(self):
        """Test that malformed lines are skipped but valid ones are parsed."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: valid line 1\n")
            f.write("{unterminated json dump\n")  # malformed line
            f.write("2026-05-31T23:58:01+00:00 INFO boot.init: valid line 2\n")
            temp_path = f.name

        try:
            summary = parse_log_file(temp_path)
            self.assertEqual(len(summary.entries), 2)
        finally:
            os.unlink(temp_path)

    def test_parse_empty_file(self):
        """Test that empty files raise LogParseError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name

        try:
            with self.assertRaises(LogParseError) as cm:
                parse_log_file(temp_path)
            self.assertIn("No valid log entries", str(cm.exception))
        finally:
            os.unlink(temp_path)

    def test_parse_non_log_file(self):
        """Test that non-log files raise LogParseError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a log file\n")
            f.write("Just some random text\n")
            temp_path = f.name

        try:
            with self.assertRaises(LogParseError) as cm:
                parse_log_file(temp_path)
            self.assertIn("No valid log entries", str(cm.exception))
        finally:
            os.unlink(temp_path)

    def test_parse_with_level_filter(self):
        """Test parsing with level filter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write("2026-05-31T23:58:01+00:00 DEBUG boot.init: msg2\n")
            f.write("2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n")
            temp_path = f.name

        try:
            summary = parse_log_file(temp_path, filter_level="INFO")
            self.assertEqual(len(summary.entries), 2)
            self.assertEqual(summary.level_counts["INFO"], 2)
            self.assertNotIn("DEBUG", summary.level_counts)
        finally:
            os.unlink(temp_path)

    def test_parse_nonexistent_file(self):
        """Test that nonexistent files raise LogParseError."""
        with self.assertRaises(LogParseError) as cm:
            parse_log_file("/nonexistent/path/to/file.log")
        self.assertIn("Cannot read file", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
