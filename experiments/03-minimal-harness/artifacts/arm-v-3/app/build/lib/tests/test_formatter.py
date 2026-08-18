import unittest
import json
import tempfile
import os
from datetime import datetime
from logpeek.parser import LogFile
from logpeek.formatter import Formatter


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def _create_test_file(self, content: str) -> str:
        filepath = os.path.join(self.temp_dir, "test.log")
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_format_text(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO app.a: msg1\n"
            "2026-05-31T23:58:01+00:00 DEBUG app.b: msg2\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        text = Formatter.format_text(log, filepath)
        self.assertIn(filepath, text)
        self.assertIn("Total lines: 2", text)
        self.assertIn("INFO (1)", text)
        self.assertIn("DEBUG (1)", text)
        self.assertIn("2026-05-31T23:58:00", text)

    def test_format_json_single_file(self):
        content = (
            "2026-05-31T23:58:00+00:00 INFO app.a: msg1\n"
            "2026-05-31T23:58:01+00:00 INFO app.a: msg2\n"
        )
        filepath = self._create_test_file(content)
        log = LogFile(filepath)
        log.parse()

        json_str = Formatter.format_json([(filepath, log)])
        data = json.loads(json_str)

        self.assertIn(filepath, data)
        self.assertEqual(data[filepath]["total_lines"], 2)
        self.assertEqual(data[filepath]["levels"]["INFO"], 2)
        self.assertIsNotNone(data[filepath]["time_span"])

    def test_format_json_empty_file(self):
        filepath = self._create_test_file("")
        log = LogFile(filepath)
        log.parse()

        json_str = Formatter.format_json([(filepath, log)])
        data = json.loads(json_str)

        self.assertEqual(data[filepath]["total_lines"], 0)
        self.assertIsNone(data[filepath]["time_span"])


if __name__ == "__main__":
    unittest.main()
