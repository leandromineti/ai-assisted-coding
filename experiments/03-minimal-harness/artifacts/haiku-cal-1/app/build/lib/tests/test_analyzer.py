"""Test log analyzer."""
import unittest
import tempfile
import os
from logpeek.analyzer import LogAnalyzer


class TestLogAnalyzer(unittest.TestCase):
    """Test log analysis."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_analyze_valid_log(self):
        """Analyze a valid log file."""
        filepath = os.path.join(self.tmpdir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080\n")
            f.write("2026-06-10T09:01:00+00:00 DEBUG api.http: route table built\n")
            f.write("2026-06-10T09:02:00+00:00 ERROR api.auth: bad password\n")

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        self.assertTrue(analyzer.is_valid_log_file())
        self.assertEqual(analyzer.total_lines, 3)
        self.assertEqual(analyzer.level_counts["INFO"], 1)
        self.assertEqual(analyzer.level_counts["DEBUG"], 1)
        self.assertEqual(analyzer.level_counts["ERROR"], 1)

    def test_analyze_empty_file(self):
        """Analyze an empty file."""
        filepath = os.path.join(self.tmpdir, "empty.log")
        with open(filepath, 'w') as f:
            pass

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        self.assertFalse(analyzer.is_valid_log_file())
        self.assertEqual(analyzer.total_lines, 0)

    def test_analyze_non_log_file(self):
        """Analyze a file with no valid log lines."""
        filepath = os.path.join(self.tmpdir, "notalog.log")
        with open(filepath, 'w') as f:
            f.write("This is just random text\n")
            f.write("-- MARK --\n")
            f.write("[reload]\n")

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        self.assertFalse(analyzer.is_valid_log_file())
        self.assertEqual(analyzer.total_lines, 3)

    def test_get_time_span(self):
        """Get time span from logs."""
        filepath = os.path.join(self.tmpdir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: start\n")
            f.write("2026-06-10T09:05:00+00:00 INFO api.http: middle\n")
            f.write("2026-06-10T09:10:00+00:00 INFO api.http: end\n")

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        first, last = analyzer.get_time_span()
        self.assertIsNotNone(first)
        self.assertIsNotNone(last)
        self.assertEqual(first.hour, 9)
        self.assertEqual(first.minute, 0)
        self.assertEqual(last.hour, 9)
        self.assertEqual(last.minute, 10)

    def test_get_time_span_empty(self):
        """Get time span from empty log."""
        filepath = os.path.join(self.tmpdir, "empty.log")
        with open(filepath, 'w') as f:
            pass

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        first, last = analyzer.get_time_span()
        self.assertIsNone(first)
        self.assertIsNone(last)

    def test_get_top_loggers(self):
        """Get top loggers by frequency."""
        filepath = os.path.join(self.tmpdir, "test.log")
        with open(filepath, 'w') as f:
            f.write("2026-06-10T09:00:00+00:00 INFO api.http: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 INFO api.http: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO api.http: msg3\n")
            f.write("2026-06-10T09:03:00+00:00 INFO api.db: msg4\n")
            f.write("2026-06-10T09:04:00+00:00 INFO api.auth: msg5\n")

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        top = analyzer.get_top_loggers(5)
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0][0], "api.http")
        self.assertEqual(top[0][1], 3)
        self.assertEqual(top[1][0], "api.db")
        self.assertEqual(top[1][1], 1)

    def test_mixed_timestamps(self):
        """Handle mixed ISO and Unix timestamps."""
        filepath = os.path.join(self.tmpdir, "mixed.log")
        with open(filepath, 'w') as f:
            f.write("2026-02-01T12:00:00+00:00 INFO ingest.a: begin\n")
            f.write("1738411260 DEBUG ingest.b: shard load\n")
            f.write("2026-02-01T12:02:00+05:30 INFO ingest.a: batch\n")

        analyzer = LogAnalyzer(filepath)
        analyzer.analyze()

        self.assertTrue(analyzer.is_valid_log_file())
        self.assertEqual(len(analyzer.timestamps), 3)

    def test_file_not_found(self):
        """Handle missing file."""
        analyzer = LogAnalyzer("/nonexistent/file.log")
        with self.assertRaises(ValueError) as context:
            analyzer.analyze()
        self.assertIn("Cannot read file", str(context.exception))


if __name__ == "__main__":
    unittest.main()
