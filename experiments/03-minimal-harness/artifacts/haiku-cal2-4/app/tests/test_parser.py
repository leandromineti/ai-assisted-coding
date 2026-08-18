import unittest
from datetime import datetime
from logpeek.parser import LogParser, LogEntry, LogSummary


class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.parser = LogParser()

    def test_parse_valid_log_line(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'INFO')
        self.assertEqual(entry.logger, 'boot.init')
        self.assertEqual(entry.message, 'kernel handoff')
        self.assertEqual(entry.timestamp.year, 2026)
        self.assertEqual(entry.timestamp.month, 5)
        self.assertEqual(entry.timestamp.day, 31)

    def test_parse_debug_level(self):
        line = "2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'DEBUG')
        self.assertEqual(entry.logger, 'boot.svc')

    def test_parse_warning_level(self):
        line = "2026-05-31T23:58:05+00:00 WARNING boot.svc: swap disabled"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'WARNING')

    def test_parse_error_level(self):
        line = "2026-06-01T00:00:14+00:00 ERROR api.gw: evt 2 code 6"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'ERROR')
        self.assertEqual(entry.logger, 'api.gw')

    def test_parse_critical_level(self):
        line = "2026-06-01T00:00:00+00:00 CRITICAL system.core: fatal error"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'CRITICAL')

    def test_parse_logger_with_dots(self):
        line = "2026-06-01T00:00:07+00:00 INFO api.auth: evt 1 code 3"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.logger, 'api.auth')

    def test_parse_logger_with_dashes(self):
        line = "2026-06-01T00:00:00+00:00 INFO api-gateway: msg"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.logger, 'api-gateway')

    def test_parse_message_with_special_chars(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: [ERROR] unexpected but info level"
        entry = self.parser.parse(line)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, 'INFO')
        self.assertIn('[ERROR]', entry.message)

    def test_parse_no_timestamp(self):
        line = "INFO boot.init: no timestamp"
        entry = self.parser.parse(line)

        self.assertIsNone(entry)

    def test_parse_no_level(self):
        line = "2026-05-31T23:58:00+00:00 boot.init: no level"
        entry = self.parser.parse(line)

        self.assertIsNone(entry)

    def test_parse_invalid_timestamp(self):
        line = "2026-13-45T99:99:99+00:00 INFO boot.init: invalid timestamp"
        entry = self.parser.parse(line)

        self.assertIsNone(entry)

    def test_parse_empty_line(self):
        line = ""
        entry = self.parser.parse(line)

        self.assertIsNone(entry)

    def test_parse_whitespace_only(self):
        line = "   \t  "
        entry = self.parser.parse(line)

        self.assertIsNone(entry)


class TestLogSummary(unittest.TestCase):
    def setUp(self):
        self.summary = LogSummary()
        self.parser = LogParser()

    def test_add_entry(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: message"
        entry = self.parser.parse(line)
        self.summary.add_entry(entry)

        self.assertEqual(self.summary.total_lines(), 1)
        self.assertEqual(self.summary.levels['INFO'], 1)
        self.assertEqual(self.summary.loggers['boot.init'], 1)

    def test_total_lines_with_errors(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: message"
        entry = self.parser.parse(line)
        self.summary.add_entry(entry)
        self.summary.record_parse_error()
        self.summary.record_parse_error()

        self.assertEqual(self.summary.total_lines(), 3)

    def test_empty_summary(self):
        self.assertEqual(self.summary.total_lines(), 0)
        self.assertEqual(self.summary.get_level_counts(), {})
        self.assertIsNone(self.summary.get_time_span())

    def test_get_level_counts(self):
        lines = [
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1",
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2",
            "2026-05-31T23:58:02+00:00 DEBUG boot.svc: msg3",
            "2026-05-31T23:58:05+00:00 WARNING boot.svc: msg4",
        ]

        for line in lines:
            entry = self.parser.parse(line)
            if entry:
                self.summary.add_entry(entry)

        counts = self.summary.get_level_counts()
        self.assertEqual(counts['INFO'], 2)
        self.assertEqual(counts['DEBUG'], 1)
        self.assertEqual(counts['WARNING'], 1)

    def test_get_time_span(self):
        lines = [
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1",
            "2026-05-31T23:58:05+00:00 INFO boot.init: msg2",
            "2026-05-31T23:58:02+00:00 INFO boot.init: msg3",
        ]

        for line in lines:
            entry = self.parser.parse(line)
            if entry:
                self.summary.add_entry(entry)

        start, end = self.summary.get_time_span()
        self.assertEqual(start.second, 0)
        self.assertEqual(end.second, 5)

    def test_get_top_loggers(self):
        lines = [
            "2026-05-31T23:58:00+00:00 INFO api.gw: msg1",
            "2026-05-31T23:58:01+00:00 INFO api.auth: msg2",
            "2026-05-31T23:58:02+00:00 INFO api.gw: msg3",
            "2026-05-31T23:58:03+00:00 INFO api.gw: msg4",
            "2026-05-31T23:58:04+00:00 INFO api.http: msg5",
        ]

        for line in lines:
            entry = self.parser.parse(line)
            if entry:
                self.summary.add_entry(entry)

        top = self.summary.get_top_loggers(5)
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0], ('api.gw', 3))
        self.assertEqual(top[1][0] in ['api.auth', 'api.http'], True)

    def test_get_top_loggers_n(self):
        lines = [
            "2026-05-31T23:58:00+00:00 INFO logger1: msg",
            "2026-05-31T23:58:01+00:00 INFO logger2: msg",
            "2026-05-31T23:58:02+00:00 INFO logger3: msg",
            "2026-05-31T23:58:03+00:00 INFO logger4: msg",
            "2026-05-31T23:58:04+00:00 INFO logger5: msg",
            "2026-05-31T23:58:05+00:00 INFO logger6: msg",
        ]

        for line in lines:
            entry = self.parser.parse(line)
            if entry:
                self.summary.add_entry(entry)

        top = self.summary.get_top_loggers(3)
        self.assertEqual(len(top), 3)


if __name__ == '__main__':
    unittest.main()
