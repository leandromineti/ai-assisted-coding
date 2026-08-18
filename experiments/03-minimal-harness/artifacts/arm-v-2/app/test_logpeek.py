import unittest
import json
import tempfile
from pathlib import Path
import sys
from io import StringIO

from logpeek.cli import parse_log_line, analyze_log_file, get_top_loggers, format_level_counts


class TestParseLogLine(unittest.TestCase):
    def test_valid_log_line(self):
        line = "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['timestamp'], "2026-05-31T23:58:00+00:00")
        self.assertEqual(result['level'], "INFO")
        self.assertEqual(result['logger'], "boot.init")
        self.assertEqual(result['message'], "kernel handoff")

    def test_various_log_levels(self):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            line = f"2026-05-31T23:58:00+00:00 {level} test.logger: message"
            result = parse_log_line(line)
            self.assertIsNotNone(result)
            self.assertEqual(result['level'], level)

    def test_invalid_log_line(self):
        invalid_lines = [
            "not a log line",
            "2026-05-31 INVALID",
            "",
            "{unterminated json dump",
        ]
        for line in invalid_lines:
            result = parse_log_line(line)
            self.assertIsNone(result, f"Expected None for: {line}")

    def test_multipart_logger_name(self):
        line = "2026-05-31T23:58:00+00:00 INFO api.gw.router: request processed"
        result = parse_log_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['logger'], "api.gw.router")


class TestAnalyzeLogFile(unittest.TestCase):
    def test_analyze_valid_log_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready\n")
            f.write("2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built\n")
            temp_path = f.name

        try:
            stats = analyze_log_file(Path(temp_path))
            self.assertEqual(stats['total_lines'], 3)
            self.assertEqual(stats['valid_lines'], 3)
            self.assertEqual(stats['invalid_lines'], 0)
            self.assertIn('INFO', stats['level_counts'])
            self.assertIn('DEBUG', stats['level_counts'])
            self.assertIsNone(stats['error'])
        finally:
            Path(temp_path).unlink()

    def test_analyze_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name

        try:
            stats = analyze_log_file(Path(temp_path))
            self.assertEqual(stats['total_lines'], 0)
            self.assertEqual(stats['valid_lines'], 0)
            self.assertIsNone(stats['error'])
        finally:
            Path(temp_path).unlink()

    def test_analyze_nonexistent_file(self):
        stats = analyze_log_file(Path("/nonexistent/file.log"))
        self.assertIsNotNone(stats['error'])
        self.assertIn("not found", stats['error'].lower())

    def test_analyze_mixed_valid_invalid_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("not a log line\n")
            f.write("2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready\n")
            temp_path = f.name

        try:
            stats = analyze_log_file(Path(temp_path))
            self.assertEqual(stats['total_lines'], 3)
            self.assertEqual(stats['valid_lines'], 2)
            self.assertEqual(stats['invalid_lines'], 1)
        finally:
            Path(temp_path).unlink()

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write("2026-05-31T23:58:01+00:00 DEBUG boot.init: msg2\n")
            f.write("2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n")
            temp_path = f.name

        try:
            stats = analyze_log_file(Path(temp_path), level_filter='INFO')
            self.assertEqual(stats['total_lines'], 3)
            self.assertEqual(stats['valid_lines'], 3)
            self.assertEqual(len(stats['level_counts']), 1)
            self.assertIn('INFO', stats['level_counts'])
            self.assertEqual(stats['level_counts']['INFO'], 2)
        finally:
            Path(temp_path).unlink()

    def test_time_span_extraction(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: start\n")
            f.write("2026-05-31T23:58:05+00:00 INFO boot.init: end\n")
            temp_path = f.name

        try:
            stats = analyze_log_file(Path(temp_path))
            self.assertEqual(stats['first_timestamp'], "2026-05-31T23:58:00+00:00")
            self.assertEqual(stats['last_timestamp'], "2026-05-31T23:58:05+00:00")
        finally:
            Path(temp_path).unlink()


class TestGetTopLoggers(unittest.TestCase):
    def test_top_loggers(self):
        stats = {
            'loggers': {
                'api.gw': 100,
                'api.http': 80,
                'api.db': 50,
                'api.auth': 30,
                'api.cache': 20,
                'api.queue': 10,
            }
        }
        top = get_top_loggers(stats, count=5)
        self.assertEqual(len(top), 5)
        self.assertEqual(top[0][0], 'api.gw')
        self.assertEqual(top[0][1], 100)
        self.assertEqual(top[4][0], 'api.cache')

    def test_fewer_loggers_than_count(self):
        stats = {'loggers': {'api.gw': 100, 'api.http': 80}}
        top = get_top_loggers(stats, count=5)
        self.assertEqual(len(top), 2)


class TestFormatLevelCounts(unittest.TestCase):
    def test_format_dict(self):
        level_counts = {'INFO': 10, 'DEBUG': 5}
        result = format_level_counts(level_counts)
        self.assertEqual(result, {'INFO': 10, 'DEBUG': 5})


if __name__ == '__main__':
    unittest.main()
