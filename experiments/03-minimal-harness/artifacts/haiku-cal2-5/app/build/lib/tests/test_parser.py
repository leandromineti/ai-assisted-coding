import unittest
import tempfile
import os
from datetime import datetime
from logpeek.parser import (
    parse_log_line,
    parse_log_file,
    LogEntry,
    get_level_counts,
    get_time_span,
    get_top_loggers,
)


class TestParseLogLine(unittest.TestCase):
    def test_valid_log_line(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "boot.init")
        self.assertEqual(entry.message, "kernel handoff")

    def test_log_line_with_colon_in_message(self):
        line = "2026-05-31T23:58:00+00:00 ERROR api.gw: error: connection timeout: retrying"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "ERROR")
        self.assertEqual(entry.logger, "api.gw")
        self.assertEqual(entry.message, "error: connection timeout: retrying")

    def test_various_log_levels(self):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            line = f"2026-05-31T23:58:00+00:00 {level} test.logger: test message"
            entry = parse_log_line(line)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.level, level)

    def test_invalid_log_line_no_match(self):
        line = "invalid log line"
        entry = parse_log_line(line)
        self.assertIsNone(entry)

    def test_invalid_timestamp(self):
        line = "2026-13-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        entry = parse_log_line(line)
        self.assertIsNone(entry)

    def test_empty_line(self):
        entry = parse_log_line("")
        self.assertIsNone(entry)

    def test_timestamp_parsing(self):
        line = "2026-06-01T14:30:45+05:30 INFO app.test: message"
        entry = parse_log_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.timestamp.year, 2026)
        self.assertEqual(entry.timestamp.month, 6)
        self.assertEqual(entry.timestamp.day, 1)


class TestParseLogFile(unittest.TestCase):
    def test_parse_valid_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("2026-05-31T23:58:01+00:00 ERROR api.gw: error occurred\n")
            temp_path = f.name

        try:
            entries, total_lines = parse_log_file(temp_path)
            self.assertEqual(len(entries), 2)
            self.assertEqual(total_lines, 2)
            self.assertEqual(entries[0].level, "INFO")
            self.assertEqual(entries[1].level, "ERROR")
        finally:
            os.unlink(temp_path)

    def test_parse_file_with_invalid_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("invalid line\n")
            f.write("2026-05-31T23:58:01+00:00 ERROR api.gw: error\n")
            temp_path = f.name

        try:
            entries, total_lines = parse_log_file(temp_path)
            self.assertEqual(len(entries), 2)
            self.assertEqual(total_lines, 3)
        finally:
            os.unlink(temp_path)

    def test_parse_file_with_empty_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("\n")
            f.write("2026-05-31T23:58:01+00:00 ERROR api.gw: error\n")
            temp_path = f.name

        try:
            entries, total_lines = parse_log_file(temp_path)
            self.assertEqual(len(entries), 2)
            self.assertEqual(total_lines, 3)
        finally:
            os.unlink(temp_path)

    def test_parse_nonexistent_file(self):
        with self.assertRaises(IOError):
            parse_log_file("/nonexistent/path/file.log")

    def test_parse_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name

        try:
            entries, total_lines = parse_log_file(temp_path)
            self.assertEqual(len(entries), 0)
            self.assertEqual(total_lines, 0)
        finally:
            os.unlink(temp_path)


class TestGetLevelCounts(unittest.TestCase):
    def test_level_counts(self):
        entries = [
            LogEntry(datetime.now(), "INFO", "app.a", "msg"),
            LogEntry(datetime.now(), "INFO", "app.b", "msg"),
            LogEntry(datetime.now(), "ERROR", "app.c", "msg"),
            LogEntry(datetime.now(), "WARNING", "app.d", "msg"),
        ]
        counts = get_level_counts(entries)
        self.assertEqual(counts["INFO"], 2)
        self.assertEqual(counts["ERROR"], 1)
        self.assertEqual(counts["WARNING"], 1)

    def test_level_counts_empty(self):
        counts = get_level_counts([])
        self.assertEqual(counts, {})


class TestGetTimeSpan(unittest.TestCase):
    def test_time_span(self):
        dt1 = datetime.fromisoformat("2026-01-01T10:00:00+00:00")
        dt2 = datetime.fromisoformat("2026-01-01T12:00:00+00:00")
        entries = [
            LogEntry(dt1, "INFO", "app", "msg"),
            LogEntry(dt2, "ERROR", "app", "msg"),
        ]
        span = get_time_span(entries)
        self.assertEqual(span[0], dt1)
        self.assertEqual(span[1], dt2)

    def test_time_span_single_entry(self):
        dt = datetime.fromisoformat("2026-01-01T10:00:00+00:00")
        entries = [LogEntry(dt, "INFO", "app", "msg")]
        span = get_time_span(entries)
        self.assertEqual(span[0], dt)
        self.assertEqual(span[1], dt)

    def test_time_span_empty(self):
        span = get_time_span([])
        self.assertIsNone(span)


class TestGetTopLoggers(unittest.TestCase):
    def test_top_loggers(self):
        entries = [
            LogEntry(datetime.now(), "INFO", "api.gw", "msg"),
            LogEntry(datetime.now(), "INFO", "api.gw", "msg"),
            LogEntry(datetime.now(), "INFO", "api.http", "msg"),
            LogEntry(datetime.now(), "INFO", "api.db", "msg"),
            LogEntry(datetime.now(), "INFO", "api.db", "msg"),
            LogEntry(datetime.now(), "INFO", "api.db", "msg"),
        ]
        top = get_top_loggers(entries, top_n=5)
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0][0], "api.db")
        self.assertEqual(top[0][1], 3)
        self.assertEqual(top[1][0], "api.gw")
        self.assertEqual(top[1][1], 2)

    def test_top_loggers_limit(self):
        entries = [
            LogEntry(datetime.now(), "INFO", "logger" + str(i), "msg")
            for i in range(10)
        ]
        top = get_top_loggers(entries, top_n=5)
        self.assertEqual(len(top), 5)

    def test_top_loggers_empty(self):
        top = get_top_loggers([], top_n=5)
        self.assertEqual(len(top), 0)


if __name__ == "__main__":
    unittest.main()
