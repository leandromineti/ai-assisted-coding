import unittest
from datetime import datetime
from logpeek.analyzer import LogAnalysis
from logpeek.parser import LogLine


class TestLogAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysis = LogAnalysis("test.log")

    def test_empty_analysis(self):
        self.assertEqual(self.analysis.total_lines, 0)
        self.assertEqual(self.analysis.get_level_counts(), {})
        self.assertIsNone(self.analysis.get_time_span())

    def test_add_single_line(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        log_line = LogLine(ts, "INFO", "test.logger", "message")
        self.analysis.add_line(log_line)

        self.assertEqual(self.analysis.total_lines, 1)
        self.assertEqual(self.analysis.get_level_counts()["INFO"], 1)
        self.assertEqual(self.analysis.loggers["test.logger"], 1)

    def test_add_multiple_lines(self):
        ts1 = datetime(2026, 1, 1, 12, 0, 0)
        ts2 = datetime(2026, 1, 1, 12, 1, 0)
        ts3 = datetime(2026, 1, 1, 12, 2, 0)

        self.analysis.add_line(LogLine(ts1, "INFO", "logger1", "msg"))
        self.analysis.add_line(LogLine(ts2, "DEBUG", "logger2", "msg"))
        self.analysis.add_line(LogLine(ts3, "ERROR", "logger1", "msg"))

        self.assertEqual(self.analysis.total_lines, 3)
        self.assertEqual(self.analysis.get_level_counts()["INFO"], 1)
        self.assertEqual(self.analysis.get_level_counts()["DEBUG"], 1)
        self.assertEqual(self.analysis.get_level_counts()["ERROR"], 1)

    def test_logger_frequency(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        self.analysis.add_line(LogLine(ts, "INFO", "logger1", "msg"))
        self.analysis.add_line(LogLine(ts, "INFO", "logger1", "msg"))
        self.analysis.add_line(LogLine(ts, "INFO", "logger2", "msg"))
        self.analysis.add_line(LogLine(ts, "INFO", "logger2", "msg"))
        self.analysis.add_line(LogLine(ts, "INFO", "logger2", "msg"))

        top = self.analysis.get_top_loggers(2)
        self.assertEqual(top[0], ("logger2", 3))
        self.assertEqual(top[1], ("logger1", 2))

    def test_top_loggers_limited(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        for i in range(10):
            self.analysis.add_line(LogLine(ts, "INFO", f"logger{i}", "msg"))

        top = self.analysis.get_top_loggers(5)
        self.assertEqual(len(top), 5)

    def test_time_span_tracking(self):
        ts1 = datetime(2026, 1, 1, 10, 0, 0)
        ts2 = datetime(2026, 1, 1, 12, 0, 0)
        ts3 = datetime(2026, 1, 1, 11, 0, 0)

        self.analysis.add_line(LogLine(ts1, "INFO", "logger", "msg"))
        self.analysis.add_line(LogLine(ts2, "INFO", "logger", "msg"))
        self.analysis.add_line(LogLine(ts3, "INFO", "logger", "msg"))

        span = self.analysis.get_time_span()
        self.assertEqual(span[0], ts1)
        self.assertEqual(span[1], ts3)

    def test_line_without_timestamp(self):
        self.analysis.add_line(LogLine(None, "INFO", "logger", "msg"))
        self.assertEqual(self.analysis.total_lines, 1)
        self.assertIsNone(self.analysis.get_time_span())

    def test_to_dict(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        self.analysis.add_line(LogLine(ts, "INFO", "logger1", "msg"))
        self.analysis.add_line(LogLine(ts, "DEBUG", "logger2", "msg"))

        result = self.analysis.to_dict()
        self.assertEqual(result['file'], "test.log")
        self.assertEqual(result['total_lines'], 2)
        self.assertIn('levels', result)
        self.assertIn('top_loggers', result)
        self.assertIn('time_span', result)

    def test_to_dict_empty(self):
        result = self.analysis.to_dict()
        self.assertEqual(result['total_lines'], 0)
        self.assertNotIn('time_span', result)


if __name__ == '__main__':
    unittest.main()
