import unittest
import tempfile
import os
import json
import subprocess
import sys


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_temp_file(self, name: str, content: str) -> str:
        path = os.path.join(self.temp_dir, name)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def _run_logpeek(self, args):
        """Run logpeek CLI and return (exit_code, stdout, stderr)"""
        cmd = [sys.executable, '-m', 'logpeek.cli'] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    def test_single_file(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("test.log", content)

        exit_code, stdout, stderr = self._run_logpeek([filepath])

        self.assertEqual(exit_code, 0)
        self.assertIn("Total lines: 2", stdout)
        self.assertIn("INFO: 2", stdout)

    def test_nonexistent_file(self):
        exit_code, stdout, stderr = self._run_logpeek(["/nonexistent.log"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Error", stderr)

    def test_non_log_file(self):
        filepath = self._create_temp_file("notlog.txt", "just plain text\n")

        exit_code, stdout, stderr = self._run_logpeek([filepath])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Error", stderr)

    def test_empty_file(self):
        filepath = self._create_temp_file("empty.log", "")

        exit_code, stdout, stderr = self._run_logpeek([filepath])

        self.assertEqual(exit_code, 0)
        self.assertIn("Total lines: 0", stdout)

    def test_multiple_files(self):
        file1 = self._create_temp_file("test1.log",
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
        )
        file2 = self._create_temp_file("test2.log",
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg2\n"
        )

        exit_code, stdout, stderr = self._run_logpeek([file1, file2])

        self.assertEqual(exit_code, 0)
        self.assertIn(file1, stdout)
        self.assertIn(file2, stdout)

    def test_level_filter_info(self):
        content = (
            "2026-05-31T23:58:00+00:00 DEBUG boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
            "2026-05-31T23:58:02+00:00 DEBUG boot.init: msg3\n"
        )
        filepath = self._create_temp_file("filter.log", content)

        exit_code, stdout, stderr = self._run_logpeek([filepath, "--level", "INFO"])

        self.assertEqual(exit_code, 0)
        self.assertIn("INFO: 1", stdout)
        # DEBUG should not appear in level counts
        self.assertNotIn("DEBUG:", stdout)

    def test_level_filter_debug(self):
        content = (
            "2026-05-31T23:58:00+00:00 DEBUG boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("debug.log", content)

        exit_code, stdout, stderr = self._run_logpeek([filepath, "--level", "DEBUG"])

        self.assertEqual(exit_code, 0)
        self.assertIn("DEBUG: 1", stdout)

    def test_json_output_single_file(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("test.log", content)

        exit_code, stdout, stderr = self._run_logpeek([filepath, "--json"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['total_lines'], 2)
        self.assertEqual(data[0]['level_counts']['INFO'], 2)

    def test_json_output_multiple_files(self):
        file1 = self._create_temp_file("test1.log",
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
        )
        file2 = self._create_temp_file("test2.log",
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg2\n"
        )

        exit_code, stdout, stderr = self._run_logpeek([file1, file2, "--json"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_json_output_format(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO api.gw: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO api.auth: msg2\n"
            "2026-05-31T23:58:02+00:00 DEBUG api.gw: msg3\n"
        )
        filepath = self._create_temp_file("test.log", content)

        exit_code, stdout, stderr = self._run_logpeek([filepath, "--json"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout)[0]

        # Check structure
        self.assertIn('file', data)
        self.assertIn('total_lines', data)
        self.assertIn('level_counts', data)
        self.assertIn('time_span', data)
        self.assertIn('top_loggers', data)

        # Check time_span
        self.assertIn('start', data['time_span'])
        self.assertIn('end', data['time_span'])

        # Check top_loggers
        self.assertEqual(len(data['top_loggers']), 2)
        self.assertIn('name', data['top_loggers'][0])
        self.assertIn('count', data['top_loggers'][0])

    def test_multiple_files_one_error(self):
        valid_file = self._create_temp_file("valid.log",
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
        )

        exit_code, stdout, stderr = self._run_logpeek([valid_file, "/nonexistent.log"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Error", stderr)


if __name__ == '__main__':
    unittest.main()
