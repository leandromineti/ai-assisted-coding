import unittest
import tempfile
import os
from datetime import datetime
from logpeek.parser import LogFile, LogParseError


class TestLogFileParser(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def _create_test_file(self, content: str) -> str:
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_parse_valid_log(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        self.assertEqual(log.total_lines, 2)
        self.assertEqual(log.level_counts["INFO"], 1)
        self.assertEqual(log.level_counts["DEBUG"], 1)
        self.assertIsNotNone(log.first_timestamp)
        self.assertIsNotNone(log.last_timestamp)

    def test_parse_empty_file(self):
        filepath = self._create_test_file("")
        log = LogFile(filepath)
        log.parse()

        self.assertEqual(log.total_lines, 0)
        self.assertEqual(sum(log.level_counts.values()), 0)
        self.assertIsNone(log.first_timestamp)
        self.assertIsNone(log.last_timestamp)

    def test_parse_invalid_log(self):
        content = "this is not a valid log line\n"
        filepath = self._create_test_file(content)
        log = LogFile(filepath)

        with self.assertRaises(LogParseError):
            log.parse()

    def test_parse_mixed_valid_invalid(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "invalid line\n"
            "2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        self.assertEqual(log.total_lines, 3)
        self.assertEqual(log.level_counts["INFO"], 1)
        self.assertEqual(log.level_counts["DEBUG"], 1)

    def test_level_counts_all_levels(self):
        content = (
            "2026-05-31T23:58:00+00:00 DEBUG app: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO app: msg2\n"
            "2026-05-31T23:58:02+00:00 WARNING app: msg3\n"
            "2026-05-31T23:58:03+00:00 ERROR app: msg4\n"
            "2026-05-31T23:58:04+00:00 CRITICAL app: msg5\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        self.assertEqual(log.level_counts["DEBUG"], 1)
        self.assertEqual(log.level_counts["INFO"], 1)
        self.assertEqual(log.level_counts["WARNING"], 1)
        self.assertEqual(log.level_counts["ERROR"], 1)
        self.assertEqual(log.level_counts["CRITICAL"], 1)

    def test_top_loggers(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO app.a: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO app.b: msg2\n"
            "2026-05-31T23:58:02+00:00 INFO app.a: msg3\n"
            "2026-05-31T23:58:03+00:00 INFO app.c: msg4\n"
            "2026-05-31T23:58:04+00:00 INFO app.a: msg5\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        top = log.get_top_loggers(2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], "app.a")
        self.assertEqual(top[0][1], 3)
        self.assertEqual(top[1][0], "app.b")

    def test_filter_by_level(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO app.a: msg1\n"
            "2026-05-31T23:58:01+00:00 DEBUG app.b: msg2\n"
            "2026-05-31T23:58:02+00:00 INFO app.a: msg3\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        filtered = log.filter_by_level("INFO")
        self.assertEqual(filtered.total_lines, 2)
        self.assertEqual(filtered.level_counts["INFO"], 2)
        self.assertEqual(filtered.level_counts["DEBUG"], 0)

    def test_time_span(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO app: msg1\n"
            "2026-05-31T23:59:00+00:00 INFO app: msg2\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        self.assertEqual(
            log.first_timestamp,
            datetime.fromisoformat("2026-05-31T23:58:00+00:00")
        )
        self.assertEqual(
            log.last_timestamp,
            datetime.fromisoformat("2026-05-31T23:59:00+00:00")
        )

    def test_nonexistent_file(self):
        log = LogFile("/nonexistent/path/file.log")
        with self.assertRaises(LogParseError):
            log.parse()


if __name__ == "__main__":
    unittest.main()
