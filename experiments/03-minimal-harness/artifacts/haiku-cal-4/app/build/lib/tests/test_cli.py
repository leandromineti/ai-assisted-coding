import unittest
import json
import tempfile
from pathlib import Path
from logpeek.cli import summarize_file


class TestSummarizeFile(unittest.TestCase):
    def test_summarize_valid_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 DEBUG api.http: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 ERROR api.auth: msg3\n")
            temp_path = f.name

        try:
            result = summarize_file(temp_path)
            self.assertEqual(result['total_lines'], 3)
            self.assertIn('INFO', result['level_counts'])
            self.assertIn('DEBUG', result['level_counts'])
            self.assertIn('ERROR', result['level_counts'])
            self.assertEqual(len(result['top_loggers']), 2)
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            summarize_file("/nonexistent/file.log")

    def test_empty_file_error(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                summarize_file(temp_path)
            self.assertIn("Empty log file", str(ctx.exception))
        finally:
            Path(temp_path).unlink()

    def test_no_valid_entries_error(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("this is not a valid log line\n")
            f.write("another invalid line\n")
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                summarize_file(temp_path)
            self.assertIn("No valid log entries found", str(ctx.exception))
        finally:
            Path(temp_path).unlink()

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 DEBUG api.http: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api.auth: msg3\n")
            temp_path = f.name

        try:
            result = summarize_file(temp_path, level_filter="INFO")
            self.assertEqual(result['total_lines'], 2)
            self.assertEqual(result['level_counts'].get('INFO'), 2)
            self.assertNotIn('DEBUG', result['level_counts'])
        finally:
            Path(temp_path).unlink()

    def test_top_loggers_ordering(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 INFO api.http: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api.auth: msg3\n")
            f.write("2026-06-10T09:03:00+00:00 INFO api.db: msg4\n")
            f.write("2026-06-10T09:04:00+00:00 INFO api.db: msg5\n")
            f.write("2026-06-10T09:05:00+00:00 INFO api.db: msg6\n")
            temp_path = f.name

        try:
            result = summarize_file(temp_path)
            loggers = result['top_loggers']
            self.assertEqual(loggers[0]['name'], 'api.db')
            self.assertEqual(loggers[0]['count'], 3)
            self.assertEqual(loggers[1]['name'], 'api.http')
            self.assertEqual(loggers[1]['count'], 2)
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    unittest.main()
