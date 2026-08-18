import unittest
import json
from logpeek.parser import LogEntry, LogSummary
from logpeek.formatter import OutputFormatter


class TestOutputFormatter(unittest.TestCase):
    """Test output formatting."""

    def setUp(self):
        """Create a sample summary for testing."""
        self.summary = LogSummary()
        self.summary.add_entry(LogEntry("2026-05-31T23:58:00+00:00", "INFO", "boot.init", "msg1"))
        self.summary.add_entry(LogEntry("2026-05-31T23:58:01+00:00", "INFO", "boot.svc", "msg2"))
        self.summary.add_entry(LogEntry("2026-05-31T23:58:02+00:00", "DEBUG", "boot.svc", "msg3"))
        self.summary.add_entry(LogEntry("2026-05-31T23:58:03+00:00", "WARNING", "boot.init", "msg4"))
        self.summary.add_entry(LogEntry("2026-05-31T23:58:04+00:00", "ERROR", "api.gw", "msg5"))

    def test_text_format_contains_total_lines(self):
        """Test that text output contains total line count."""
        output = OutputFormatter.text_format("test.log", self.summary)
        self.assertIn("Total lines: 5", output)

    def test_text_format_contains_level_counts(self):
        """Test that text output contains level counts."""
        output = OutputFormatter.text_format("test.log", self.summary)
        self.assertIn("Level counts:", output)
        self.assertIn("DEBUG: 1", output)
        self.assertIn("INFO: 2", output)
        self.assertIn("WARNING: 1", output)
        self.assertIn("ERROR: 1", output)

    def test_text_format_contains_time_span(self):
        """Test that text output contains time span."""
        output = OutputFormatter.text_format("test.log", self.summary)
        self.assertIn("Time span:", output)
        self.assertIn("2026-05-31T23:58:00+00:00", output)
        self.assertIn("2026-05-31T23:58:04+00:00", output)

    def test_text_format_contains_top_loggers(self):
        """Test that text output contains top loggers."""
        output = OutputFormatter.text_format("test.log", self.summary)
        self.assertIn("Top 5 loggers:", output)
        self.assertIn("boot.init: 2", output)
        self.assertIn("boot.svc: 2", output)
        self.assertIn("api.gw: 1", output)

    def test_text_format_contains_filename(self):
        """Test that text output contains the filename."""
        output = OutputFormatter.text_format("test.log", self.summary)
        self.assertIn("test.log", output)

    def test_json_format_structure(self):
        """Test that JSON output has the correct structure."""
        output = OutputFormatter.json_format("test.log", self.summary)
        data = json.loads(output)

        self.assertEqual(data["file"], "test.log")
        self.assertEqual(data["total_lines"], 5)
        self.assertIn("level_counts", data)
        self.assertIn("time_span", data)
        self.assertIn("top_loggers", data)

    def test_json_format_level_counts(self):
        """Test JSON level counts."""
        output = OutputFormatter.json_format("test.log", self.summary)
        data = json.loads(output)

        self.assertEqual(data["level_counts"]["DEBUG"], 1)
        self.assertEqual(data["level_counts"]["INFO"], 2)
        self.assertEqual(data["level_counts"]["WARNING"], 1)
        self.assertEqual(data["level_counts"]["ERROR"], 1)

    def test_json_format_time_span(self):
        """Test JSON time span."""
        output = OutputFormatter.json_format("test.log", self.summary)
        data = json.loads(output)

        self.assertEqual(data["time_span"]["first"], "2026-05-31T23:58:00+00:00")
        self.assertEqual(data["time_span"]["last"], "2026-05-31T23:58:04+00:00")

    def test_json_format_top_loggers(self):
        """Test JSON top loggers."""
        output = OutputFormatter.json_format("test.log", self.summary)
        data = json.loads(output)

        loggers = data["top_loggers"]
        self.assertEqual(len(loggers), 3)
        self.assertEqual(loggers[0]["name"], "boot.init")
        self.assertEqual(loggers[0]["count"], 2)

    def test_json_format_empty_summary(self):
        """Test JSON output with empty summary."""
        empty_summary = LogSummary()
        output = OutputFormatter.json_format("empty.log", empty_summary)
        data = json.loads(output)

        self.assertEqual(data["file"], "empty.log")
        self.assertEqual(data["total_lines"], 0)
        self.assertIsNone(data["time_span"]["first"])
        self.assertIsNone(data["time_span"]["last"])
        self.assertEqual(data["top_loggers"], [])


if __name__ == "__main__":
    unittest.main()
