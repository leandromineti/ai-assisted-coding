import unittest
import tempfile
import os
from datetime import datetime
from logpeek.parser import LogParser, LogEntry, LogSummary, summarize_file


class TestLogParser(unittest.TestCase):
    def test_parse_iso_timestamp(self):
        line = "2026-06-10T09:00:00+00:00 INFO api.http: listening"
        entry = LogParser.parse_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "api.http:")
        self.assertIsNotNone(entry.timestamp)

    def test_parse_unix_timestamp(self):
        line = "1735689600 INFO daemon.boot: first light"
        entry = LogParser.parse_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.logger, "daemon.boot:")
        self.assertEqual(entry.timestamp, 1735689600.0)

    def test_parse_invalid_timestamp(self):
        line = "2026-06-10T09:05:1 DEBUG api.cache: bad timestamp"
        entry = LogParser.parse_line(line)
        self.assertIsNone(entry)

    def test_parse_non_log_line(self):
        self.assertIsNone(LogParser.parse_line("-- MARK --"))
        self.assertIsNone(LogParser.parse_line("[reload]"))
        self.assertIsNone(LogParser.parse_line("random text"))
        self.assertIsNone(LogParser.parse_line(""))

    def test_parse_all_log_levels(self):
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            line = f"1735689600 {level} test.logger: message"
            entry = LogParser.parse_line(line)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.level, level)

    def test_parse_iso_with_timezone(self):
        line = "2026-06-10T09:02:00-03:00 WARNING api.db: slow query"
        entry = LogParser.parse_line(line)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "WARNING")

    def test_iso_timestamp_conversion(self):
        line = "2026-06-10T09:00:00+00:00 INFO test.a: msg"
        entry = LogParser.parse_line(line)
        self.assertIsNotNone(entry)
        # Convert back and check date
        dt = datetime.fromtimestamp(entry.timestamp)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.day, 10)


class TestLogSummary(unittest.TestCase):
    def test_level_counting(self):
        summary = LogSummary()
        summary.add_entry(LogEntry('INFO', 'test.a', 1000))
        summary.add_entry(LogEntry('INFO', 'test.a', 2000))
        summary.add_entry(LogEntry('ERROR', 'test.b', 3000))

        self.assertEqual(summary.levels_count['INFO'], 2)
        self.assertEqual(summary.levels_count['ERROR'], 1)

    def test_logger_counting(self):
        summary = LogSummary()
        summary.add_entry(LogEntry('INFO', 'logger.a', 1000))
        summary.add_entry(LogEntry('INFO', 'logger.a', 2000))
        summary.add_entry(LogEntry('INFO', 'logger.b', 3000))
        summary.add_entry(LogEntry('INFO', 'logger.c', 4000))

        loggers = summary.get_top_loggers(2)
        self.assertEqual(len(loggers), 2)
        self.assertEqual(loggers[0][0], 'logger.a')
        self.assertEqual(loggers[0][1], 2)

    def test_time_span(self):
        summary = LogSummary()
        summary.add_entry(LogEntry('INFO', 'test', 1000.0))
        summary.add_entry(LogEntry('INFO', 'test', 5000.0))

        span = summary.get_time_span()
        self.assertIsNotNone(span)
        self.assertIn('1970-01-01', span[0])
        self.assertIn('1970-01-01', span[1])

    def test_no_timestamps(self):
        summary = LogSummary()
        summary.add_entry(LogEntry('INFO', 'test', None))
        summary.add_entry(LogEntry('INFO', 'test', None))

        span = summary.get_time_span()
        self.assertIsNone(span)


class TestSummarizeFile(unittest.TestCase):
    def test_summarize_valid_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api.db: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api.http: msg3\n")
            f.flush()
            fname = f.name

        try:
            summary, total_lines = summarize_file(fname)
            self.assertEqual(total_lines, 3)
            self.assertEqual(summary.levels_count['INFO'], 2)
            self.assertEqual(summary.levels_count['ERROR'], 1)
        finally:
            os.unlink(fname)

    def test_empty_file_raises_error(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.flush()
            fname = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                summarize_file(fname)
            self.assertIn("empty", str(ctx.exception).lower())
        finally:
            os.unlink(fname)

    def test_no_valid_entries_raises_error(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("-- MARK --\n")
            f.write("[reload]\n")
            f.write("random text\n")
            f.flush()
            fname = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                summarize_file(fname)
            self.assertIn("no valid log entries", str(ctx.exception).lower())
        finally:
            os.unlink(fname)

    def test_nonexistent_file_raises_error(self):
        with self.assertRaises(IOError):
            summarize_file("/nonexistent/path/file.log")

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api.db: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api.http: msg3\n")
            f.flush()
            fname = f.name

        try:
            summary, _ = summarize_file(fname, level_filter='INFO')
            self.assertEqual(summary.levels_count['INFO'], 2)
            self.assertNotIn('ERROR', summary.levels_count)
        finally:
            os.unlink(fname)

    def test_mixed_formats(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.write("1735689600 INFO test.b: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 ERROR test.a: msg3\n")
            f.flush()
            fname = f.name

        try:
            summary, _ = summarize_file(fname)
            self.assertEqual(summary.total_lines, 3)
            self.assertEqual(summary.levels_count['INFO'], 2)
        finally:
            os.unlink(fname)

    def test_file_with_invalid_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.write("-- MARK --\n")
            f.write("2026-06-10T09:02:00+00:00 ERROR test.a: msg3\n")
            f.write("[reload]\n")
            f.flush()
            fname = f.name

        try:
            summary, total_lines = summarize_file(fname)
            self.assertEqual(total_lines, 4)
            self.assertEqual(summary.levels_count['INFO'], 1)
            self.assertEqual(summary.levels_count['ERROR'], 1)
        finally:
            os.unlink(fname)


if __name__ == '__main__':
    unittest.main()
