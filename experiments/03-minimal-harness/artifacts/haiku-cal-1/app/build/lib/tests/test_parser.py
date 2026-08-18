"""Test log parser."""
import unittest
from datetime import datetime
from logpeek.parser import parse_iso_timestamp, parse_unix_timestamp, parse_log_line


class TestParseTimestamp(unittest.TestCase):
    """Test timestamp parsing."""

    def test_parse_iso_timestamp_basic(self):
        """Parse basic ISO 8601 timestamp."""
        ts = parse_iso_timestamp("2026-06-10T09:00:00+00:00")
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)
        self.assertEqual(ts.month, 6)
        self.assertEqual(ts.day, 10)
        self.assertEqual(ts.hour, 9)
        self.assertEqual(ts.minute, 0)
        self.assertEqual(ts.second, 0)

    def test_parse_iso_timestamp_negative_offset(self):
        """Parse ISO timestamp with negative offset."""
        ts = parse_iso_timestamp("2026-06-10T09:02:00-03:00")
        self.assertIsNotNone(ts)

    def test_parse_iso_timestamp_invalid(self):
        """Invalid ISO timestamp returns None."""
        ts = parse_iso_timestamp("not-a-timestamp")
        self.assertIsNone(ts)

    def test_parse_unix_timestamp(self):
        """Parse Unix timestamp."""
        ts = parse_unix_timestamp("1735689600")
        self.assertIsNotNone(ts)

    def test_parse_unix_timestamp_invalid(self):
        """Invalid Unix timestamp returns None."""
        ts = parse_unix_timestamp("not-a-number")
        self.assertIsNone(ts)

    def test_parse_unix_timestamp_overflow(self):
        """Overflow Unix timestamp returns None."""
        ts = parse_unix_timestamp("999999999999999")
        self.assertIsNone(ts)


class TestParseLogLine(unittest.TestCase):
    """Test log line parsing."""

    def test_parse_iso_log_line(self):
        """Parse a standard ISO log line."""
        line = "2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        ts, level, logger, message = result
        self.assertEqual(level, "INFO")
        self.assertEqual(logger, "api.http")
        self.assertEqual(message, "listening on :8080")

    def test_parse_unix_log_line(self):
        """Parse a Unix timestamp log line."""
        line = "1735689600 INFO daemon.boot: first light"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        ts, level, logger, message = result
        self.assertEqual(level, "INFO")
        self.assertEqual(logger, "daemon.boot")
        self.assertEqual(message, "first light")

    def test_parse_log_line_with_extra_spaces(self):
        """Parse log line with extra spaces in message."""
        line = "2026-06-10T09:00:00+00:00 DEBUG api.cache: hit ratio 0.93"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        ts, level, logger, message = result
        self.assertEqual(message, "hit ratio 0.93")

    def test_parse_mark_line(self):
        """Mark lines are skipped."""
        line = "-- MARK --"
        result = parse_log_line(line)
        self.assertIsNone(result)

    def test_parse_reload_line(self):
        """Reload lines are skipped."""
        line = "[reload]"
        result = parse_log_line(line)
        self.assertIsNone(result)

    def test_parse_malformed_timestamp(self):
        """Malformed timestamp returns None."""
        line = "2026-06-10T09:05:1 DEBUG api.cache: hit ratio"
        result = parse_log_line(line)
        self.assertIsNone(result)

    def test_parse_empty_line(self):
        """Empty line returns None."""
        result = parse_log_line("")
        self.assertIsNone(result)

    def test_parse_line_without_colon(self):
        """Line without colon in logger:message returns None."""
        line = "2026-06-10T09:00:00+00:00 INFO some text"
        result = parse_log_line(line)
        self.assertIsNone(result)

    def test_parse_critical_level(self):
        """Parse CRITICAL log level."""
        line = "2026-06-10T09:12:00+00:00 CRITICAL api.db: replica down"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        ts, level, logger, message = result
        self.assertEqual(level, "CRITICAL")

    def test_parse_warning_level(self):
        """Parse WARNING log level."""
        line = "2026-06-10T09:02:00-03:00 WARNING api.db: slow query 300ms"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        ts, level, logger, message = result
        self.assertEqual(level, "WARNING")


if __name__ == "__main__":
    unittest.main()
