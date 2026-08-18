"""Tests for CLI functionality."""

import unittest
import tempfile
import os
import json
import subprocess
import sys


class TestCLI(unittest.TestCase):
    """Test CLI interface."""

    def setUp(self):
        """Create temporary log files for testing."""
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files."""
        for path in self.temp_files:
            if os.path.exists(path):
                os.unlink(path)

    def create_temp_log(self, content, suffix=".log"):
        """Create a temporary log file with content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as f:
            f.write(content)
            f.flush()
            self.temp_files.append(f.name)
            return f.name

    def run_logpeek(self, *args, expect_error=False):
        """Run logpeek CLI and return (stdout, stderr, returncode)."""
        cmd = [sys.executable, "-m", "logpeek.cli"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode

    def test_single_valid_log(self):
        """Test with a single valid log file."""
        log_path = self.create_temp_log(
            "2026-01-01T10:00:00+00:00 INFO app.main: started\n"
            "2026-01-01T10:01:00+00:00 DEBUG app.db: query\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path)
        self.assertEqual(code, 0)
        self.assertIn("Total lines: 2", stdout)
        self.assertIn("INFO", stdout)
        self.assertIn("DEBUG", stdout)

    def test_multiple_files(self):
        """Test with multiple files."""
        log1 = self.create_temp_log(
            "2026-01-01T10:00:00+00:00 INFO app.main: started\n"
        )
        log2 = self.create_temp_log(
            "2026-01-01T11:00:00+00:00 ERROR app.main: crashed\n"
        )
        stdout, stderr, code = self.run_logpeek(log1, log2)
        self.assertEqual(code, 0)
        self.assertIn(log1, stdout)
        self.assertIn(log2, stdout)

    def test_empty_file(self):
        """Test with an empty file."""
        log_path = self.create_temp_log("")
        stdout, stderr, code = self.run_logpeek(log_path)
        # Empty files are valid but have no entries
        self.assertEqual(code, 1)
        self.assertIn("Error: Empty file", stdout)

    def test_invalid_log_file(self):
        """Test with invalid log file."""
        log_path = self.create_temp_log("This is not a log file\n")
        stdout, stderr, code = self.run_logpeek(log_path)
        self.assertEqual(code, 1)
        self.assertIn("Not a valid log file", stdout)

    def test_json_output(self):
        """Test JSON output format."""
        log_path = self.create_temp_log(
            "2026-01-01T10:00:00+00:00 INFO app.main: started\n"
            "2026-01-01T10:01:00+00:00 DEBUG app.db: query\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path, "--json")
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn("file", data[0])
        self.assertIn("valid", data[0])
        self.assertIn("total_lines", data[0])
        self.assertIn("level_counts", data[0])

    def test_level_filter(self):
        """Test filtering by level."""
        log_path = self.create_temp_log(
            "2026-01-01T10:00:00+00:00 INFO app.main: started\n"
            "2026-01-01T10:01:00+00:00 DEBUG app.db: query\n"
            "2026-01-01T10:02:00+00:00 ERROR app.main: crash\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path, "--level", "INFO")
        self.assertEqual(code, 0)
        # Verify that only INFO level is shown
        self.assertIn("'INFO': 1", stdout)

    def test_nonexistent_file(self):
        """Test with nonexistent file."""
        stdout, stderr, code = self.run_logpeek("/nonexistent/file.log")
        self.assertEqual(code, 1)
        self.assertIn("Not a valid log file", stdout)

    def test_legacy_daemon_log(self):
        """Test parsing legacy daemon log format."""
        log_path = self.create_temp_log(
            "0 INFO daemon.boot: first light\n"
            "1735689600 INFO daemon.loop: tick\n"
            "1735693200 DEBUG daemon.loop: gc\n"
            "1735696800 WARNING daemon.net: retry\n"
            "1735700400 ERROR daemon.net: unreachable\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path)
        self.assertEqual(code, 0)
        self.assertIn("Total lines: 5", stdout)

    def test_mixed_timestamps_log(self):
        """Test parsing mixed timestamp formats."""
        log_path = self.create_temp_log(
            "2026-02-01T12:00:00+00:00 INFO ingest.a: begin\n"
            "1738411260 DEBUG ingest.b: shard load\n"
            "2026-02-01T12:02:00+05:30 INFO ingest.a: row batch 1\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path)
        self.assertEqual(code, 0)
        self.assertIn("Total lines: 3", stdout)

    def test_top_loggers(self):
        """Test that top loggers are displayed."""
        log_path = self.create_temp_log(
            "2026-01-01T10:00:00+00:00 INFO app.main: msg1\n"
            "2026-01-01T10:01:00+00:00 INFO app.main: msg2\n"
            "2026-01-01T10:02:00+00:00 INFO app.db: msg3\n"
            "2026-01-01T10:03:00+00:00 INFO app.auth: msg4\n"
        )
        stdout, stderr, code = self.run_logpeek(log_path)
        self.assertEqual(code, 0)
        self.assertIn("Top loggers:", stdout)
        self.assertIn("app.main", stdout)


if __name__ == "__main__":
    unittest.main()
