#!/usr/bin/env python3
"""Tests for logpeek CLI."""

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


class TestLogpeekCLI(unittest.TestCase):
    """Test logpeek CLI against sample files."""

    def setUp(self):
        """Set up test fixtures."""
        self.samples_dir = Path(__file__).parent / 'samples'

    def run_logpeek(self, *args):
        """Run logpeek CLI and return (stdout, stderr, returncode)."""
        cmd = ['python', '-m', 'logpeek'] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode

    def test_boot_log(self):
        """Test parsing boot.log."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'))
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        self.assertIn('Total lines: 6', stdout)
        self.assertIn('INFO', stdout)
        self.assertIn('DEBUG', stdout)
        self.assertIn('WARNING', stdout)
        self.assertIn('boot.init', stdout)
        self.assertIn('boot.svc', stdout)

    def test_app_main_log(self):
        """Test parsing app_main.log."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'app_main.log'))
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        self.assertIn('Total lines: 40000', stdout)
        self.assertIn('INFO', stdout)
        self.assertIn('api.gw', stdout)

    def test_empty_log(self):
        """Test parsing empty.log."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'empty.log'))
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        self.assertIn('Total lines: 0', stdout)

    def test_multiple_files(self):
        """Test parsing multiple files."""
        boot = str(self.samples_dir / 'boot.log')
        empty = str(self.samples_dir / 'empty.log')
        stdout, stderr, code = self.run_logpeek(boot, empty)
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        self.assertIn('boot.log', stdout)
        self.assertIn('empty.log', stdout)
        self.assertIn('Total lines: 6', stdout)
        self.assertIn('Total lines: 0', stdout)

    def test_json_output(self):
        """Test JSON output format."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'), '--json')
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['total_lines'], 6)
        self.assertIn('level_counts', data[0])
        self.assertIn('time_span', data[0])
        self.assertIn('top_loggers', data[0])

    def test_level_filter_info(self):
        """Test --level filter for INFO."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'), '--level', 'INFO')
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        self.assertIn('INFO', stdout)
        # Only INFO should be in level_counts
        self.assertNotIn('DEBUG', stdout.split('Log levels:')[1].split('\n')[0])

    def test_level_filter_json(self):
        """Test --level filter with JSON output."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'), '--level', 'ERROR', '--json')
        self.assertEqual(code, 0, f"Expected exit code 0, got {code}\nstderr: {stderr}")
        data = json.loads(stdout)
        self.assertIn('ERROR', data[0]['level_counts'])

    def test_invalid_level(self):
        """Test invalid level filter."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'), '--level', 'INVALID')
        self.assertNotEqual(code, 0, f"Expected non-zero exit code for invalid level")
        self.assertIn('Invalid log level', stderr)

    def test_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        stdout, stderr, code = self.run_logpeek('/nonexistent/file.log')
        self.assertNotEqual(code, 0, f"Expected non-zero exit code for nonexistent file")
        self.assertIn('Error', stderr)

    def test_non_log_file(self):
        """Test error handling for non-log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a log file\nJust some text\n")
            f.flush()
            temp_path = f.name

        try:
            stdout, stderr, code = self.run_logpeek(temp_path)
            self.assertNotEqual(code, 0, f"Expected non-zero exit code for non-log file")
            self.assertIn('not a valid log file', stderr)
        finally:
            Path(temp_path).unlink()

    def test_top_loggers_count(self):
        """Test that top loggers are limited to top 5."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'app_main.log'))
        self.assertEqual(code, 0)
        # boot.log should have fewer than 5 loggers
        boot_stdout, _, _ = self.run_logpeek(str(self.samples_dir / 'boot.log'))
        logger_line = boot_stdout.split('Top loggers:')[1].split('\n')[0]
        # boot.log has 2 loggers, app_main has 4
        self.assertIn('boot.init', boot_stdout)

    def test_time_span_format(self):
        """Test that time span is properly formatted."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'))
        self.assertEqual(code, 0)
        self.assertIn('Time span:', stdout)
        self.assertIn('2026-05-31', stdout)

    def test_json_time_span(self):
        """Test time span in JSON output."""
        stdout, stderr, code = self.run_logpeek(str(self.samples_dir / 'boot.log'), '--json')
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertIsNotNone(data[0]['time_span'])
        self.assertIn('start', data[0]['time_span'])
        self.assertIn('end', data[0]['time_span'])


class TestLogpeekModule(unittest.TestCase):
    """Test logpeek module functions directly."""

    def setUp(self):
        """Set up test fixtures."""
        self.samples_dir = Path(__file__).parent / 'samples'

    def test_parse_boot_log(self):
        """Test parsing boot.log directly."""
        from logpeek import parse_log_file

        total, levels, loggers, timestamps = parse_log_file(self.samples_dir / 'boot.log')
        self.assertEqual(total, 6)
        self.assertEqual(sum(levels.values()), 6)
        self.assertIn('INFO', levels)
        self.assertGreater(levels['INFO'], 0)

    def test_empty_file(self):
        """Test parsing empty file."""
        from logpeek import parse_log_file

        total, levels, loggers, timestamps = parse_log_file(self.samples_dir / 'empty.log')
        self.assertEqual(total, 0)
        self.assertEqual(len(levels), 0)

    def test_malformed_lines_ignored(self):
        """Test that malformed lines are ignored."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-01-01T00:00:00+00:00 INFO app: valid line\n')
            f.write('This is malformed\n')
            f.write('2026-01-01T00:00:01+00:00 ERROR app: another valid line\n')
            f.flush()
            temp_path = f.name

        try:
            from logpeek import parse_log_file
            total, levels, loggers, timestamps = parse_log_file(Path(temp_path))
            self.assertEqual(total, 3)
            self.assertEqual(sum(levels.values()), 2)
        finally:
            Path(temp_path).unlink()


if __name__ == '__main__':
    unittest.main()
