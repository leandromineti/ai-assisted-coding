import unittest
from datetime import datetime
from logpeek.parser import parse_line, parse_iso8601_timestamp, parse_unix_timestamp, LogLine


class TestTimestampParsing(unittest.TestCase):
    def test_iso8601_with_timezone(self):
        ts = parse_iso8601_timestamp("2026-06-10T09:00:00+00:00")
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)
        self.assertEqual(ts.month, 6)
        self.assertEqual(ts.day, 10)

    def test_iso8601_different_timezone(self):
        ts = parse_iso8601_timestamp("2026-06-10T09:02:00-03:00")
        self.assertIsNotNone(ts)

    def test_unix_timestamp_valid(self):
        ts = parse_unix_timestamp("1735689600")
        self.assertIsNotNone(ts)

    def test_unix_timestamp_zero(self):
        ts = parse_unix_timestamp("0")
        self.assertIsNotNone(ts)

    def test_unix_timestamp_max_32bit(self):
        ts = parse_unix_timestamp("4294967295")
        self.assertIsNotNone(ts)

    def test_unix_timestamp_beyond_32bit(self):
        ts = parse_unix_timestamp("4294967296")
        self.assertIsNone(ts)

    def test_invalid_timestamp(self):
        ts = parse_iso8601_timestamp("not-a-timestamp")
        self.assertIsNone(ts)
        ts = parse_unix_timestamp("not-a-timestamp")
        self.assertIsNone(ts)


class TestLineParsing(unittest.TestCase):
    def test_iso8601_format(self):
        line = "2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.level, "INFO")
        self.assertEqual(parsed.logger, "api.http:")
        self.assertEqual(parsed.message, "listening on :8080")

    def test_unix_timestamp_format(self):
        line = "1735689600 INFO daemon.boot: first light"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.level, "INFO")
        self.assertEqual(parsed.logger, "daemon.boot:")
        self.assertEqual(parsed.message, "first light")

    def test_case_insensitive_level(self):
        line = "2026-06-10T09:00:00+00:00 debug api.http: test"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.level, "DEBUG")

    def test_all_log_levels(self):
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            line = f"2026-06-10T09:00:00+00:00 {level} logger: message"
            parsed = parse_line(line)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.level, level)

    def test_empty_line(self):
        parsed = parse_line("")
        self.assertIsNone(parsed)

    def test_comment_line(self):
        parsed = parse_line("-- MARK --")
        self.assertIsNone(parsed)

    def test_bracket_line(self):
        parsed = parse_line("[reload]")
        self.assertIsNone(parsed)

    def test_malformed_line_too_few_parts(self):
        line = "2026-06-10T09:00:00+00:00 INFO"
        parsed = parse_line(line)
        self.assertIsNone(parsed)

    def test_invalid_log_level(self):
        line = "2026-06-10T09:00:00+00:00 UNKNOWN logger: message"
        parsed = parse_line(line)
        self.assertIsNone(parsed)

    def test_invalid_timestamp_parsed_with_none_ts(self):
        line = "bad-timestamp INFO logger: message"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertIsNone(parsed.timestamp)

    def test_no_message(self):
        line = "2026-06-10T09:00:00+00:00 INFO logger:"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.message, "")

    def test_message_with_spaces(self):
        line = "2026-06-10T09:00:00+00:00 INFO logger: this is a longer message"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.message, "this is a longer message")

    def test_incomplete_timestamp_parsed_with_none_ts(self):
        line = "2026-06-10T09:05:1 INFO logger: incomplete"
        parsed = parse_line(line)
        self.assertIsNotNone(parsed)
        self.assertIsNone(parsed.timestamp)


if __name__ == '__main__':
    unittest.main()
