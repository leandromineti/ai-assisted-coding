import unittest
import tempfile
import os
import json
import subprocess
import sys
from pathlib import Path


class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).parent.parent
        # Ensure the package is installed for CLI testing
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-e', str(cls.project_root)],
            capture_output=True,
            check=False
        )

    def run_logpeek(self, *args):
        """Run logpeek command and return (returncode, stdout, stderr)"""
        result = subprocess.run(
            ['logpeek'] + list(args),
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def test_single_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR test.b: msg2\n")
            f.flush()
            fname = f.name

        try:
            code, stdout, stderr = self.run_logpeek(fname)
            self.assertEqual(code, 0)
            self.assertIn("File:", stdout)
            self.assertIn("Total lines: 2", stdout)
            self.assertIn("INFO=1", stdout)
            self.assertIn("ERROR=1", stdout)
        finally:
            os.unlink(fname)

    def test_multiple_files(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1:
            f1.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f1.flush()
            fname1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
            f2.write("2026-06-10T09:00:00+00:00 ERROR test.b: msg2\n")
            f2.flush()
            fname2 = f2.name

        try:
            code, stdout, stderr = self.run_logpeek(fname1, fname2)
            self.assertEqual(code, 0)
            self.assertIn("File: " + fname1, stdout)
            self.assertIn("File: " + fname2, stdout)
        finally:
            os.unlink(fname1)
            os.unlink(fname2)

    def test_empty_file_error(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.flush()
            fname = f.name

        try:
            code, stdout, stderr = self.run_logpeek(fname)
            self.assertNotEqual(code, 0)
            self.assertIn("Error:", stderr)
        finally:
            os.unlink(fname)

    def test_invalid_file_error(self):
        code, stdout, stderr = self.run_logpeek("/nonexistent/file.log")
        self.assertNotEqual(code, 0)
        self.assertIn("Error:", stderr)

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR test.b: msg2\n")
            f.write("2026-06-10T09:02:00+00:00 INFO test.c: msg3\n")
            f.flush()
            fname = f.name

        try:
            code, stdout, stderr = self.run_logpeek('--level', 'INFO', fname)
            self.assertEqual(code, 0)
            self.assertIn("INFO=2", stdout)
            self.assertNotIn("ERROR", stdout)
        finally:
            os.unlink(fname)

    def test_json_output(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.write("2026-06-10T09:01:00+00:00 ERROR test.b: msg2\n")
            f.flush()
            fname = f.name

        try:
            code, stdout, stderr = self.run_logpeek('--json', fname)
            self.assertEqual(code, 0)
            data = json.loads(stdout)
            self.assertIn('file', data)
            self.assertIn('total_lines', data)
            self.assertEqual(data['total_lines'], 2)
            self.assertIn('INFO', data['levels'])
        finally:
            os.unlink(fname)

    def test_json_multiple_files(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1:
            f1.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f1.flush()
            fname1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
            f2.write("2026-06-10T09:00:00+00:00 ERROR test.b: msg2\n")
            f2.flush()
            fname2 = f2.name

        try:
            code, stdout, stderr = self.run_logpeek('--json', fname1, fname2)
            self.assertEqual(code, 0)
            data = json.loads(stdout)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
        finally:
            os.unlink(fname1)
            os.unlink(fname2)

    def test_partial_failure(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-06-10T09:00:00+00:00 INFO test.a: msg1\n")
            f.flush()
            fname = f.name

        try:
            code, stdout, stderr = self.run_logpeek(fname, "/nonexistent/file.log")
            self.assertNotEqual(code, 0)
            self.assertIn("Error:", stderr)
            # One file succeeds, but exit code is still non-zero due to the other
        finally:
            os.unlink(fname)


if __name__ == '__main__':
    unittest.main()
