import unittest
from datetime import datetime
from logpeek.parser import LogParser, LogSummary, parse_timestamp


class TestParseTimestamp(unittest.TestCase):
    def test_iso8601_with_tz(self):
        ts = parse_timestamp("2026-06-10T09:00:00+00:00")
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)
        self.assertEqual(ts.month, 6)
        self.assertEqual(ts.day, 10)

    def test_iso8601_without_tz(self):
        ts = parse_timestamp("2026-06-10T09:00:00")
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)

    def test_unix_timestamp(self):
        ts = parse_timestamp("1735689600")
        self.assertIsNotNone(ts)
        self.assertIsInstance(ts, datetime)

    def test_invalid_timestamp(self):
        ts = parse_timestamp("not_a_timestamp")
        self.assertIsNone(ts)

    def test_empty_string(self):
        ts = parse_timestamp("")
        self.assertIsNone(ts)


class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.parser = LogParser()

    def test_parse_valid_line(self):
        line = "2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080"
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['level'], 'INFO')
        self.assertEqual(result['logger'], 'api.http')
        self.assertIn('listening', result['message'])

    def test_parse_unix_timestamp_line(self):
        line = "1735689600 INFO daemon.boot: first light"
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['level'], 'INFO')
        self.assertEqual(result['logger'], 'daemon.boot')

    def test_parse_debug_level(self):
        line = "2026-06-10T09:00:05+00:00 DEBUG api.http: route table built"
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['level'], 'DEBUG')

    def test_parse_warning_level(self):
        line = "2026-06-10T09:02:00-03:00 WARNING api.db: slow query 300ms"
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['level'], 'WARNING')

    def test_parse_critical_level(self):
        line = "2026-06-10T09:09:00+00:00 CRITICAL api.db: replica down"
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['level'], 'CRITICAL')

    def test_invalid_level_ignored(self):
        line = "2026-06-10T09:00:00+00:00 INVALID api.http: bad level"
        result = self.parser.parse_line(line)
        self.assertIsNone(result)

    def test_skip_mark_line(self):
        line = "-- MARK --"
        result = self.parser.parse_line(line)
        self.assertIsNone(result)

    def test_skip_reload_line(self):
        line = "[reload]"
        result = self.parser.parse_line(line)
        self.assertIsNone(result)

    def test_malformed_line_no_match(self):
        line = "2026-06-10T09:05:1"
        result = self.parser.parse_line(line)
        self.assertIsNone(result)

    def test_level_filter(self):
        parser = LogParser(level_filter="INFO")
        line_info = "2026-06-10T09:00:00+00:00 INFO api.http: msg"
        line_debug = "2026-06-10T09:00:00+00:00 DEBUG api.http: msg"

        self.assertIsNotNone(parser.parse_line(line_info))
        self.assertIsNone(parser.parse_line(line_debug))

    def test_invalid_level_filter(self):
        with self.assertRaises(ValueError):
            LogParser(level_filter="INVALID")

    def test_level_filter_case_insensitive(self):
        parser = LogParser(level_filter="info")
        line = "2026-06-10T09:00:00+00:00 INFO api.http: msg"
        self.assertIsNotNone(parser.parse_line(line))


class TestLogSummary(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {'timestamp': datetime(2026, 6, 10, 9, 0, 0), 'level': 'INFO', 'logger': 'api.http', 'message': 'msg1'},
            {'timestamp': datetime(2026, 6, 10, 9, 1, 0), 'level': 'DEBUG', 'logger': 'api.http', 'message': 'msg2'},
            {'timestamp': datetime(2026, 6, 10, 9, 2, 0), 'level': 'INFO', 'logger': 'api.auth', 'message': 'msg3'},
            {'timestamp': datetime(2026, 6, 10, 9, 3, 0), 'level': 'WARNING', 'logger': 'api.db', 'message': 'msg4'},
        ]
        self.summary = LogSummary(self.entries)

    def test_total_lines(self):
        self.assertEqual(self.summary.total_lines(), 4)

    def test_level_counts(self):
        counts = self.summary.level_counts()
        self.assertEqual(counts['DEBUG'], 1)
        self.assertEqual(counts['INFO'], 2)
        self.assertEqual(counts['WARNING'], 1)

    def test_time_span(self):
        start, end = self.summary.time_span()
        self.assertEqual(start, datetime(2026, 6, 10, 9, 0, 0))
        self.assertEqual(end, datetime(2026, 6, 10, 9, 3, 0))

    def test_top_loggers(self):
        top = self.summary.top_loggers(limit=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], 'api.http')
        self.assertEqual(top[0][1], 2)

    def test_top_loggers_limit(self):
        top = self.summary.top_loggers(limit=5)
        self.assertEqual(len(top), 3)

    def test_empty_entries(self):
        summary = LogSummary([])
        self.assertEqual(summary.total_lines(), 0)
        self.assertEqual(summary.level_counts(), {})
        self.assertIsNone(summary.time_span())
        self.assertEqual(summary.top_loggers(), [])


if __name__ == "__main__":
    unittest.main()
