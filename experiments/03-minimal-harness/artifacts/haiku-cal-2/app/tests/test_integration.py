import unittest
import subprocess
import json
import sys
import os


class TestIntegration(unittest.TestCase):
    def test_web_api_log(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/web_api.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total lines:", result.stdout)
        self.assertIn("INFO", result.stdout)
        self.assertIn("Top loggers:", result.stdout)

    def test_legacy_daemon_log(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/legacy_daemon.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total lines:", result.stdout)

    def test_mixed_ingest_log(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/mixed_ingest.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total lines:", result.stdout)

    def test_empty_log_file(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/empty.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    def test_multiple_files(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/web_api.log", "samples/legacy_daemon.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("web_api.log", result.stdout)
        self.assertIn("legacy_daemon.log", result.stdout)

    def test_json_output(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "--json", "samples/web_api.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn('file', data[0])
        self.assertIn('total_lines', data[0])
        self.assertIn('levels', data[0])

    def test_level_filter(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "--level", "INFO", "samples/web_api.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("INFO", result.stdout)

    def test_nonexistent_file(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/nonexistent.log"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    def test_invalid_file(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "pyproject.toml"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    def test_mixed_valid_and_invalid_files(self):
        result = subprocess.run(
            [sys.executable, "-m", "logpeek.cli", "samples/web_api.log", "pyproject.toml"],
            cwd="/app",
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("web_api.log", result.stdout)
        self.assertIn("Error", result.stderr)


if __name__ == '__main__':
    unittest.main()
