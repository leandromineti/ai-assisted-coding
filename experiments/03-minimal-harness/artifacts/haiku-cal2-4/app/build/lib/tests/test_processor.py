import unittest
import tempfile
import os
from pathlib import Path
from logpeek.processor import FileProcessor


class TestFileProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = FileProcessor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_temp_file(self, name: str, content: str) -> str:
        path = os.path.join(self.temp_dir, name)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def test_process_valid_log_file(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("test.log", content)

        summary = self.processor.process_file(filepath)

        self.assertEqual(summary.total_lines(), 2)
        self.assertEqual(summary.levels['INFO'], 2)

    def test_process_empty_file(self):
        filepath = self._create_temp_file("empty.log", "")

        summary = self.processor.process_file(filepath)

        self.assertEqual(summary.total_lines(), 0)
        self.assertEqual(summary.get_time_span(), None)

    def test_process_file_with_empty_lines(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("sparse.log", content)

        summary = self.processor.process_file(filepath)

        # 2 valid entries + 1 empty line = 3 total lines
        self.assertEqual(summary.total_lines(), 3)
        self.assertEqual(summary.levels['INFO'], 2)

    def test_process_file_with_invalid_lines(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "not a valid log line\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
        )
        filepath = self._create_temp_file("mixed.log", content)

        summary = self.processor.process_file(filepath)

        self.assertEqual(summary.total_lines(), 3)
        self.assertEqual(summary.levels['INFO'], 2)
        self.assertEqual(summary.parse_errors, 1)

    def test_process_non_log_file(self):
        content = "this is not a log file\nat all\n"
        filepath = self._create_temp_file("notlog.txt", content)

        with self.assertRaises(ValueError) as cm:
            self.processor.process_file(filepath)

        self.assertIn("does not contain valid log entries", str(cm.exception))

    def test_process_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            self.processor.process_file("/nonexistent/path/file.log")

    def test_process_directory_as_file(self):
        with self.assertRaises(ValueError) as cm:
            self.processor.process_file(self.temp_dir)

        self.assertIn("Not a file", str(cm.exception))

    def test_process_with_level_filter(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 DEBUG boot.init: msg2\n"
            "2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n"
        )
        filepath = self._create_temp_file("filter.log", content)

        summary = self.processor.process_file(filepath, level_filter='INFO')

        # When filtering by level, total_lines only counts filtered entries
        self.assertEqual(summary.total_lines(), 2)
        self.assertEqual(summary.levels['INFO'], 2)
        self.assertNotIn('DEBUG', summary.levels)

    def test_process_with_utf8_errors(self):
        # Create a file with some invalid UTF-8
        filepath = os.path.join(self.temp_dir, "invalid_utf8.log")
        with open(filepath, 'wb') as f:
            f.write(b"2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write(b"\xff\xfe invalid bytes\n")
            f.write(b"2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n")

        summary = self.processor.process_file(filepath)

        # Should handle gracefully with errors='replace'
        self.assertEqual(summary.levels['INFO'], 2)

    def test_process_multiple_levels(self):
        content = (
            "2026-05-31T23:58:00+00:00 DEBUG boot.init: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n"
            "2026-05-31T23:58:02+00:00 WARNING boot.init: msg3\n"
            "2026-05-31T23:58:03+00:00 ERROR boot.init: msg4\n"
            "2026-05-31T23:58:04+00:00 CRITICAL boot.init: msg5\n"
        )
        filepath = self._create_temp_file("levels.log", content)

        summary = self.processor.process_file(filepath)

        self.assertEqual(summary.total_lines(), 5)
        self.assertEqual(summary.levels['DEBUG'], 1)
        self.assertEqual(summary.levels['INFO'], 1)
        self.assertEqual(summary.levels['WARNING'], 1)
        self.assertEqual(summary.levels['ERROR'], 1)
        self.assertEqual(summary.levels['CRITICAL'], 1)

    def test_file_never_modified(self):
        content = "2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n"
        filepath = self._create_temp_file("readonly.log", content)

        # Get original mtime
        original_mtime = os.path.getmtime(filepath)

        # Process the file
        self.processor.process_file(filepath)

        # Verify mtime hasn't changed
        new_mtime = os.path.getmtime(filepath)
        self.assertEqual(original_mtime, new_mtime)


if __name__ == '__main__':
    unittest.main()
