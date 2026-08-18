"""Tests for CLI."""

import unittest
import tempfile
import os
import json
import subprocess
from pathlib import Path


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_log_file(self, filename, content):
        """Helper to create a log file."""
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def run_logpeek(self, args):
        """Run logpeek CLI with given arguments."""
        cmd = ["python", "-m", "logpeek.cli"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr

    def test_analyze_valid_file(self):
        """Test analyzing a valid log file."""
        log_path = self.create_log_file(
            "test.log",
            "2026-06-01T00:00:00+00:00 INFO test.logger: msg1\n"
            "2026-06-01T00:00:01+00:00 ERROR test.logger: msg2\n",
        )

        returncode, stdout, stderr = self.run_logpeek([log_path])
        self.assertEqual(returncode, 0)
        self.assertIn("Total lines: 2", stdout)
        self.assertIn("test.logger", stdout)

    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        log1 = self.create_log_file(
            "test1.log",
            "2026-06-01T00:00:00+00:00 INFO test: msg\n",
        )
        log2 = self.create_log_file(
            "test2.log",
            "2026-06-01T00:00:00+00:00 INFO test: msg\n",
        )

        returncode, stdout, stderr = self.run_logpeek([log1, log2])
        self.assertEqual(returncode, 0)
        self.assertIn(log1, stdout)
        self.assertIn(log2, stdout)

    def test_empty_file_error(self):
        """Test that empty file produces error."""
        log_path = self.create_log_file("empty.log", "")

        returncode, stdout, stderr = self.run_logpeek([log_path])
        self.assertEqual(returncode, 1)
        self.assertIn("empty file", stderr)

    def test_invalid_file_error(self):
        """Test that invalid file produces error."""
        log_path = self.create_log_file(
            "invalid.log",
            "not a log line\n",
        )

        returncode, stdout, stderr = self.run_logpeek([log_path])
        self.assertEqual(returncode, 1)
        self.assertIn("failed to parse", stderr)

    def test_nonexistent_file_error(self):
        """Test that nonexistent file produces error."""
        returncode, stdout, stderr = self.run_logpeek(["/nonexistent.log"])
        self.assertEqual(returncode, 1)
        self.assertIn("Failed to read", stderr)

    def test_level_filter(self):
        """Test filtering by log level."""
        log_path = self.create_log_file(
            "test.log",
            "2026-06-01T00:00:00+00:00 INFO test: msg1\n"
            "2026-06-01T00:00:01+00:00 ERROR test: msg2\n"
            "2026-06-01T00:00:02+00:00 INFO test: msg3\n",
        )

        returncode, stdout, stderr = self.run_logpeek([log_path, "--level", "INFO"])
        self.assertEqual(returncode, 0)
        self.assertIn("Total lines: 2", stdout)

    def test_json_output(self):
        """Test JSON output."""
        log_path = self.create_log_file(
            "test.log",
            "2026-06-01T00:00:00+00:00 INFO test: msg1\n"
            "2026-06-01T00:00:01+00:00 ERROR test: msg2\n",
        )

        returncode, stdout, stderr = self.run_logpeek([log_path, "--json"])
        self.assertEqual(returncode, 0)

        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["total_lines"], 2)
        self.assertIn("INFO", data[0]["levels"])
        self.assertIn("ERROR", data[0]["levels"])

    def test_json_with_errors(self):
        """Test JSON output with errors."""
        log_path = self.create_log_file("empty.log", "")

        returncode, stdout, stderr = self.run_logpeek([log_path, "--json"])
        self.assertEqual(returncode, 1)

        data = json.loads(stdout)
        self.assertEqual(len(data), 1)
        self.assertIn("error", data[0])


if __name__ == "__main__":
    unittest.main()
