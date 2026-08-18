import tempfile
import pytest
from datetime import datetime
from pathlib import Path

from logpeek.parser import parse_log_file, summarize_log_file


@pytest.fixture
def sample_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write("2026-06-01T00:00:00+00:00 INFO app.main: test message 1\n")
        f.write("2026-06-01T00:00:01+00:00 ERROR app.db: test message 2\n")
        f.write("2026-06-01T00:00:02+00:00 INFO app.main: test message 3\n")
        f.write("2026-06-01T00:00:03+00:00 WARNING app.net: test message 4\n")
        path = f.name
    yield path
    Path(path).unlink()


@pytest.fixture
def malformed_log_file():
    """Create a log file with some malformed lines."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write("2026-06-01T00:00:00+00:00 INFO app.main: valid line\n")
        f.write("invalid line without proper format\n")
        f.write("2026-06-01T00:00:01+00:00 ERROR app.db: another valid line\n")
        path = f.name
    yield path
    Path(path).unlink()


def test_parse_valid_log(sample_log_file):
    entries, errors = parse_log_file(sample_log_file)
    assert len(entries) == 4
    assert entries[0].level == "INFO"
    assert entries[0].logger == "app.main"
    assert entries[1].level == "ERROR"
    assert entries[1].logger == "app.db"


def test_parse_with_level_filter(sample_log_file):
    entries, errors = parse_log_file(sample_log_file, level_filter="INFO")
    assert len(entries) == 2
    assert all(e.level == "INFO" for e in entries)


def test_parse_malformed_lines(malformed_log_file):
    entries, errors = parse_log_file(malformed_log_file)
    assert len(entries) == 2
    assert len(errors) > 0
    assert any("logger" in e.lower() or "format" in e.lower() or "invalid" in e.lower() for e in errors)


def test_summarize_log(sample_log_file):
    summary, errors = summarize_log_file(sample_log_file)
    assert summary.total_lines == 4
    assert summary.level_counts["INFO"] == 2
    assert summary.level_counts["ERROR"] == 1
    assert summary.level_counts["WARNING"] == 1
    assert summary.time_start == datetime.fromisoformat("2026-06-01T00:00:00+00:00")
    assert summary.time_end == datetime.fromisoformat("2026-06-01T00:00:03+00:00")


def test_summarize_with_level_filter(sample_log_file):
    summary, errors = summarize_log_file(sample_log_file, level_filter="INFO")
    assert summary.total_lines == 2
    assert summary.level_counts.get("INFO") == 2
    assert "ERROR" not in summary.level_counts


def test_top_loggers(sample_log_file):
    summary, errors = summarize_log_file(sample_log_file)
    assert len(summary.top_loggers) <= 5
    logger_names = [name for name, count in summary.top_loggers]
    assert "app.main" in logger_names
    assert summary.top_loggers[0][1] == 2  # app.main appears twice


def test_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        path = f.name
    try:
        summary, errors = summarize_log_file(path)
        assert summary is None or summary.total_lines == 0
    finally:
        Path(path).unlink()


def test_nonexistent_file():
    entries, errors = parse_log_file("/nonexistent/path/to/file.log")
    assert len(entries) == 0
    assert len(errors) > 0
