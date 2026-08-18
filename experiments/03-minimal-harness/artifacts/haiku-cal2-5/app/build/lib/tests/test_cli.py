import unittest
import tempfile
import os
import json
import sys
from io import StringIO
from logpeek.cli import analyze_file, format_text_output, is_valid_log_file


class TestAnalyzeFile(unittest.TestCase):
    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for path in self.temp_files:
            if os.path.exists(path):
                os.unlink(path)

    def create_temp_log(self, content):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            self.temp_files.append(f.name)
            return f.name

    def test_analyze_valid_file(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "2026-05-31T23:58:01+00:00 ERROR api.gw: error occurred\n"
        )
        path = self.create_temp_log(content)
        result = analyze_file(path)

        self.assertEqual(result["file"], path)
        self.assertEqual(result["total_lines"], 2)
        self.assertEqual(result["valid_entries"], 2)
        self.assertIn("INFO", result["level_counts"])
        self.assertIn("ERROR", result["level_counts"])
        self.assertIn("time_span", result)
        self.assertIn("top_loggers", result)

    def test_analyze_file_with_invalid_lines(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "invalid line\n"
            "2026-05-31T23:58:01+00:00 ERROR api.gw: error\n"
        )
        path = self.create_temp_log(content)
        result = analyze_file(path)

        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["valid_entries"], 2)

    def test_analyze_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            analyze_file("/nonexistent/file.log")

    def test_analyze_empty_file(self):
        path = self.create_temp_log("")
        with self.assertRaises(ValueError) as ctx:
            analyze_file(path)
        self.assertIn("Empty file", str(ctx.exception))

    def test_analyze_file_no_valid_entries(self):
        content = (
            "invalid line 1\n"
            "invalid line 2\n"
        )
        path = self.create_temp_log(content)
        with self.assertRaises(ValueError) as ctx:
            analyze_file(path)
        self.assertIn("No valid log entries", str(ctx.exception))

    def test_analyze_with_level_filter(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "2026-05-31T23:58:01+00:00 ERROR api.gw: error occurred\n"
            "2026-05-31T23:58:02+00:00 INFO boot.svc: service started\n"
        )
        path = self.create_temp_log(content)
        result = analyze_file(path, level_filter="INFO")

        self.assertEqual(result["valid_entries"], 2)
        self.assertEqual(result["level_counts"]["INFO"], 2)
        self.assertNotIn("ERROR", result["level_counts"])

    def test_analyze_with_nonmatching_level_filter(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "2026-05-31T23:58:01+00:00 INFO api.gw: success\n"
        )
        path = self.create_temp_log(content)
        with self.assertRaises(ValueError) as ctx:
            analyze_file(path, level_filter="ERROR")
        self.assertIn("No entries with level", str(ctx.exception))


class TestFormatTextOutput(unittest.TestCase):
    def test_format_single_file(self):
        analyses = [
            {
                "file": "test.log",
                "total_lines": 10,
                "valid_entries": 8,
                "level_counts": {"INFO": 5, "ERROR": 3},
                "time_span": {
                    "first": "2026-01-01T10:00:00+00:00",
                    "last": "2026-01-01T10:05:00+00:00",
                },
                "top_loggers": [
                    {"name": "app.api", "count": 5},
                    {"name": "app.db", "count": 3},
                ],
            }
        ]
        output = format_text_output(analyses)
        self.assertIn("test.log", output)
        self.assertIn("10", output)
        self.assertIn("INFO", output)
        self.assertIn("app.api", output)

    def test_format_multiple_files(self):
        analyses = [
            {
                "file": "test1.log",
                "total_lines": 10,
                "valid_entries": 8,
                "level_counts": {"INFO": 5, "ERROR": 3},
                "time_span": {
                    "first": "2026-01-01T10:00:00+00:00",
                    "last": "2026-01-01T10:05:00+00:00",
                },
                "top_loggers": [],
            },
            {
                "file": "test2.log",
                "total_lines": 20,
                "valid_entries": 18,
                "level_counts": {"INFO": 15, "ERROR": 3},
                "time_span": {
                    "first": "2026-01-01T11:00:00+00:00",
                    "last": "2026-01-01T11:10:00+00:00",
                },
                "top_loggers": [],
            },
        ]
        output = format_text_output(analyses)
        self.assertIn("test1.log", output)
        self.assertIn("test2.log", output)


class TestIsValidLogFile(unittest.TestCase):
    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for path in self.temp_files:
            if os.path.exists(path):
                os.unlink(path)

    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"content")
            self.temp_files.append(f.name)

        self.assertTrue(is_valid_log_file(f.name))

    def test_nonexistent_file(self):
        self.assertFalse(is_valid_log_file("/nonexistent/file.log"))


if __name__ == "__main__":
    unittest.main()
