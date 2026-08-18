import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
from io import StringIO
from logpeek.cli import process_file, format_output_json, format_output_text
from logpeek.analyzer import LogAnalysis


class TestProcessFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            process_file("/nonexistent/file.log")

    def test_directory_instead_of_file(self):
        with self.assertRaises(IsADirectoryError):
            process_file(self.temp_dir)

    def test_invalid_log_file(self):
        filepath = os.path.join(self.temp_dir, "invalid.txt")
        with open(filepath, 'w') as f:
            f.write("This is not a log file\n")
            f.write("Just some random text\n")

        with self.assertRaises(ValueError):
            process_file(filepath)

    def test_empty_log_file(self):
        filepath = os.path.join(self.temp_dir, "empty.log")
        with open(filepath, 'w') as f:
            pass

        with self.assertRaises(ValueError):
            process_file(filepath)

    def test_valid_iso8601_log(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: test\n")

        analysis = process_file(filepath)
        self.assertEqual(analysis.total_lines, 1)

    def test_valid_unix_timestamp_log(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("1735689600 INFO daemon.boot: test\n")

        analysis = process_file(filepath)
        self.assertEqual(analysis.total_lines, 1)

    def test_level_filter(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api: msg3\n")

        analysis = process_file(filepath, level_filter="INFO")
        self.assertEqual(analysis.total_lines, 2)
        self.assertEqual(analysis.get_level_counts()["INFO"], 2)

    def test_level_filter_case_insensitive(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api: msg2\n")

        analysis = process_file(filepath, level_filter="error")
        self.assertEqual(analysis.total_lines, 1)

    def test_handles_invalid_lines(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api: valid\n")
            f.write("-- MARK --\n")
            f.write("[reload]\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api: valid\n")

        analysis = process_file(filepath)
        self.assertEqual(analysis.total_lines, 2)

    def test_handles_corrupted_lines(self):
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api: valid\n")
            f.write("2026-06-10T09:05:1 broken timestamp\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR api: valid\n")

        analysis = process_file(filepath)
        self.assertEqual(analysis.total_lines, 2)


class TestFormatting(unittest.TestCase):
    def test_format_text_output(self):
        analysis = LogAnalysis("test.log")
        from logpeek.parser import LogLine
        from datetime import datetime

        ts1 = datetime(2026, 1, 1, 10, 0, 0)
        ts2 = datetime(2026, 1, 1, 12, 0, 0)
        analysis.add_line(LogLine(ts1, "INFO", "logger1", "msg"))
        analysis.add_line(LogLine(ts2, "ERROR", "logger2", "msg"))

        output = format_output_text([analysis])
        self.assertIn("File: test.log", output)
        self.assertIn("Total lines: 2", output)
        self.assertIn("INFO", output)
        self.assertIn("ERROR", output)
        self.assertIn("Top loggers:", output)

    def test_format_json_output(self):
        analysis = LogAnalysis("test.log")
        from logpeek.parser import LogLine
        from datetime import datetime

        ts = datetime(2026, 1, 1, 10, 0, 0)
        analysis.add_line(LogLine(ts, "INFO", "logger1", "msg"))

        output = format_output_json([analysis])
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['file'], "test.log")
        self.assertEqual(data[0]['total_lines'], 1)

    def test_format_multiple_files(self):
        analysis1 = LogAnalysis("test1.log")
        analysis2 = LogAnalysis("test2.log")
        from logpeek.parser import LogLine
        from datetime import datetime

        ts = datetime(2026, 1, 1, 10, 0, 0)
        analysis1.add_line(LogLine(ts, "INFO", "logger", "msg"))
        analysis2.add_line(LogLine(ts, "ERROR", "logger", "msg"))

        output = format_output_json([analysis1, analysis2])
        data = json.loads(output)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['file'], "test1.log")
        self.assertEqual(data[1]['file'], "test2.log")


if __name__ == '__main__':
    unittest.main()
