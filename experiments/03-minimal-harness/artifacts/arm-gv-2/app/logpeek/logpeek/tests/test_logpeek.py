import json
import tempfile
from pathlib import Path

import pytest

from logpeek.logpeek import LogAnalyzer, format_output


class TestLogAnalyzer:
    def test_valid_log_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n")
            f.write("2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            assert analyzer.total_lines == 2
            assert analyzer.level_counts["INFO"] == 1
            assert analyzer.level_counts["DEBUG"] == 1
            assert analyzer.first_timestamp == "2026-05-31T23:58:00+00:00"
            assert analyzer.last_timestamp == "2026-05-31T23:58:01+00:00"

            Path(f.name).unlink()

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            assert analyzer.total_lines == 0
            assert analyzer.first_timestamp is None
            assert analyzer.last_timestamp is None

            Path(f.name).unlink()

    def test_non_log_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("This is not a log file\n")
            f.write("Just random text\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert not analyzer.analyze()
            assert analyzer.error == "File contains no valid log lines"

            Path(f.name).unlink()

    def test_missing_file(self):
        analyzer = LogAnalyzer("/nonexistent/path/file.log")
        assert not analyzer.analyze()
        assert "File not found" in analyzer.error

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write("2026-05-31T23:58:01+00:00 ERROR boot.init: msg2\n")
            f.write("2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze(level_filter="INFO")
            assert analyzer.total_lines == 3  # Total lines still counts all
            assert analyzer.level_counts["INFO"] == 2  # But level_counts only has filtered
            assert analyzer.level_counts.get("ERROR", 0) == 0

            Path(f.name).unlink()

    def test_top_loggers(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO api.gw: msg1\n")
            f.write("2026-05-31T23:58:01+00:00 INFO api.gw: msg2\n")
            f.write("2026-05-31T23:58:02+00:00 INFO api.gw: msg3\n")
            f.write("2026-05-31T23:58:03+00:00 INFO api.auth: msg4\n")
            f.write("2026-05-31T23:58:04+00:00 INFO api.db: msg5\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            top = analyzer.get_top_loggers(5)
            assert top[0] == "api.gw"
            assert top[1] == "api.auth"
            assert top[2] == "api.db"

            Path(f.name).unlink()

    def test_to_dict(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            data = analyzer.to_dict()
            assert data["file"] == f.name
            assert data["total_lines"] == 1
            assert data["levels"]["INFO"] == 1
            assert data["time_span"]["start"] == "2026-05-31T23:58:00+00:00"
            assert data["time_span"]["end"] == "2026-05-31T23:58:00+00:00"
            assert "top_loggers" in data

            Path(f.name).unlink()

    def test_format_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            output = format_output(analyzer)
            assert "File:" in output
            assert "Total lines: 1" in output
            assert "INFO: 1" in output
            assert "Time span:" in output

            Path(f.name).unlink()

    def test_mixed_valid_and_invalid_lines(self):
        """Test file with both valid and invalid lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write("invalid line\n")
            f.write("2026-05-31T23:58:01+00:00 ERROR boot.init: msg2\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            assert analyzer.total_lines == 2
            assert analyzer.level_counts["INFO"] == 1
            assert analyzer.level_counts["ERROR"] == 1

            Path(f.name).unlink()

    def test_encoding_with_errors(self):
        """Test file with non-UTF-8 bytes."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".log", delete=False) as f:
            f.write(b"2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n")
            f.write(b"2026-05-31T23:58:01+00:00 ERROR boot.init: msg2\n")
            f.write(b"\xe9invalid\n")  # Non-UTF-8 byte
            f.write(b"2026-05-31T23:58:02+00:00 INFO boot.init: msg3\n")
            f.flush()

            analyzer = LogAnalyzer(f.name)
            assert analyzer.analyze()
            assert analyzer.total_lines == 3

            Path(f.name).unlink()
