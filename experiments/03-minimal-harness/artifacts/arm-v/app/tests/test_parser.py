import unittest
from logpeek.parser import LogParser
from pathlib import Path
import tempfile


class TestLogParser(unittest.TestCase):

    def test_parse_boot_log(self):
        """Test parsing boot.log"""
        parser = LogParser()
        parser.parse_file("samples/boot.log")

        self.assertEqual(parser.total_lines, 6)
        self.assertEqual(parser.levels["INFO"], 4)
        self.assertEqual(parser.levels["DEBUG"], 1)
        self.assertEqual(parser.levels["WARNING"], 1)
        self.assertEqual(len(parser.timestamps), 6)
        self.assertIn("boot.init", parser.loggers)
        self.assertIn("boot.svc", parser.loggers)

    def test_parse_app_main_log(self):
        """Test parsing app_main.log"""
        parser = LogParser()
        parser.parse_file("samples/app_main.log")

        self.assertEqual(parser.total_lines, 40000)
        self.assertGreater(len(parser.levels), 0)
        self.assertGreater(len(parser.loggers), 0)
        self.assertEqual(len(parser.timestamps), 40000 - len(parser.parse_errors))

    def test_time_span(self):
        """Test time span extraction"""
        parser = LogParser()
        parser.parse_file("samples/boot.log")
        summary = parser.get_summary()

        self.assertIsNotNone(summary["time_span"])
        self.assertEqual(summary["time_span"]["start"], "2026-05-31T23:58:00+00:00")
        self.assertEqual(summary["time_span"]["end"], "2026-05-31T23:58:07+00:00")

    def test_top_loggers(self):
        """Test top loggers extraction"""
        parser = LogParser()
        parser.parse_file("samples/boot.log")
        summary = parser.get_summary()

        top_loggers = summary["top_loggers"]
        self.assertEqual(len(top_loggers), 2)
        self.assertIn("boot.init", top_loggers)
        self.assertIn("boot.svc", top_loggers)

    def test_filter_by_level(self):
        """Test level filtering"""
        parser = LogParser()
        parser.parse_file("samples/boot.log")
        parser.filter_by_level("INFO")
        summary = parser.get_summary()

        self.assertEqual(summary["total_lines"], 4)
        self.assertEqual(summary["levels"]["INFO"], 4)
        self.assertNotIn("DEBUG", summary["levels"])
        self.assertNotIn("WARNING", summary["levels"])

    def test_file_not_found(self):
        """Test file not found error"""
        parser = LogParser()
        with self.assertRaises(FileNotFoundError):
            parser.parse_file("nonexistent.log")

    def test_empty_file(self):
        """Test empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name

        try:
            parser = LogParser()
            parser.parse_file(temp_path)
            self.assertEqual(parser.total_lines, 0)
            summary = parser.get_summary()
            self.assertEqual(summary["total_lines"], 0)
            self.assertIsNone(summary["time_span"])
        finally:
            Path(temp_path).unlink()

    def test_malformed_log_lines(self):
        """Test handling of malformed log lines"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("this is not a valid log line\n")
            f.write("2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready\n")
            temp_path = f.name

        try:
            parser = LogParser()
            parser.parse_file(temp_path)
            self.assertEqual(parser.total_lines, 3)
            self.assertEqual(len(parser.parse_errors), 1)
            self.assertIn("Line 2", parser.parse_errors[0])
            self.assertIn("does not match log format", parser.parse_errors[0])
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    unittest.main()
