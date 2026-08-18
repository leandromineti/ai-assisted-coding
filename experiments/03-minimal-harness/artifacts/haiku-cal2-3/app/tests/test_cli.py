import unittest
import tempfile
import os
import sys
from io import StringIO
from logpeek.cli import main


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary test files."""
        for temp_path in self.temp_files:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def create_temp_log(self, content):
        """Create a temporary log file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(content)
            temp_path = f.name
        self.temp_files.append(temp_path)
        return temp_path

    def test_single_file_text_output(self):
        """Test text output for a single file."""
        log_content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready\n"
            "2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built\n"
        )
        log_path = self.create_temp_log(log_content)

        sys.argv = ["logpeek", log_path]
        stdout = StringIO()
        sys.stdout = stdout

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        finally:
            sys.stdout = sys.__stdout__

        output = stdout.getvalue()
        self.assertIn("Total lines: 3", output)
        self.assertIn("INFO: 2", output)
        self.assertIn("DEBUG: 1", output)

    def test_json_output(self):
        """Test JSON output format."""
        log_content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg\n"
            "2026-05-31T23:58:01+00:00 DEBUG boot.svc: msg\n"
        )
        log_path = self.create_temp_log(log_content)

        sys.argv = ["logpeek", "--json", log_path]
        stdout = StringIO()
        sys.stdout = stdout

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        finally:
            sys.stdout = sys.__stdout__

        output = stdout.getvalue()
        self.assertIn('"file":', output)
        self.assertIn('"total_lines": 2', output)
        self.assertIn('"level_counts":', output)

    def test_level_filter(self):
        """Test --level filter."""
        log_content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 DEBUG boot.svc: msg2\n"
            "2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n"
        )
        log_path = self.create_temp_log(log_content)

        sys.argv = ["logpeek", "--level", "INFO", log_path]
        stdout = StringIO()
        sys.stdout = stdout

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        finally:
            sys.stdout = sys.__stdout__

        output = stdout.getvalue()
        self.assertIn("Total lines: 2", output)
        self.assertIn("INFO: 2", output)
        # Should not have DEBUG
        self.assertNotIn("DEBUG", output)

    def test_multiple_files(self):
        """Test processing multiple files."""
        log_content = "2026-05-31T23:58:00+00:00 INFO boot.init: msg\n"
        log_path1 = self.create_temp_log(log_content)
        log_path2 = self.create_temp_log(log_content)

        sys.argv = ["logpeek", log_path1, log_path2]
        stdout = StringIO()
        sys.stdout = stdout

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        finally:
            sys.stdout = sys.__stdout__

        output = stdout.getvalue()
        # Both files should be in output
        self.assertIn(log_path1, output)
        self.assertIn(log_path2, output)

    def test_empty_file_error(self):
        """Test that empty files produce an error."""
        log_path = self.create_temp_log("")

        sys.argv = ["logpeek", log_path]
        stderr = StringIO()
        sys.stderr = stderr

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 1)
        finally:
            sys.stderr = sys.__stderr__

        output = stderr.getvalue()
        self.assertIn("Error:", output)
        self.assertIn("No valid log entries", output)

    def test_non_log_file_error(self):
        """Test that non-log files produce an error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a log file\n")
            temp_path = f.name
        self.temp_files.append(temp_path)

        sys.argv = ["logpeek", temp_path]
        stderr = StringIO()
        sys.stderr = stderr

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 1)
        finally:
            sys.stderr = sys.__stderr__

        output = stderr.getvalue()
        self.assertIn("Error:", output)

    def test_nonexistent_file_error(self):
        """Test that nonexistent files produce an error."""
        sys.argv = ["logpeek", "/nonexistent/path/to/file.log"]
        stderr = StringIO()
        sys.stderr = stderr

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 1)
        finally:
            sys.stderr = sys.__stderr__

        output = stderr.getvalue()
        self.assertIn("Error:", output)

    def test_mixed_valid_and_invalid_files(self):
        """Test processing mix of valid and invalid files."""
        log_content = "2026-05-31T23:58:00+00:00 INFO boot.init: msg\n"
        valid_log = self.create_temp_log(log_content)

        sys.argv = ["logpeek", valid_log, "/nonexistent/file.log"]
        stdout = StringIO()
        stderr = StringIO()
        sys.stdout = stdout
        sys.stderr = stderr

        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 1)  # Should fail due to missing file
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        error_output = stderr.getvalue()
        self.assertIn("Error:", error_output)


if __name__ == "__main__":
    unittest.main()
