import hashlib
import os

import pytest

from logpeek.analyzer import LogFileError, summarize_file

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def test_boot_log_summary():
    summary = summarize_file(os.path.join(SAMPLES, "boot.log"))
    assert summary.total_lines == 6
    assert summary.parsed_lines == 6
    assert summary.unparsed_lines == 0
    assert summary.level_counts == {"INFO": 4, "DEBUG": 1, "WARNING": 1}
    assert summary.first_timestamp.isoformat() == "2026-05-31T23:58:00+00:00"
    assert summary.last_timestamp.isoformat() == "2026-05-31T23:58:07+00:00"
    top_names = [name for name, _ in summary.top_loggers]
    assert set(top_names) == {"boot.init", "boot.svc"}


def test_boot_log_never_modified():
    path = os.path.join(SAMPLES, "boot.log")
    before_hash = _sha256(path)
    before_mtime = os.path.getmtime(path)
    summarize_file(path)
    assert _sha256(path) == before_hash
    assert os.path.getmtime(path) == before_mtime


def test_empty_file_raises_clear_error():
    with pytest.raises(LogFileError, match="empty"):
        summarize_file(os.path.join(SAMPLES, "empty.log"))


def test_missing_file_raises_clear_error():
    with pytest.raises(LogFileError, match="no such file"):
        summarize_file("/no/such/path/does-not-exist.log")


def test_non_log_text_file_raises_clear_error():
    with pytest.raises(LogFileError, match="no recognizable log lines"):
        summarize_file(os.path.join(FIXTURES, "not_a_log.txt"))


def test_non_log_binary_file_raises_clear_error():
    with pytest.raises(LogFileError, match="no recognizable log lines"):
        summarize_file(os.path.join(FIXTURES, "not_a_log.bin"))


def test_app_main_log_handles_messy_lines_without_crashing():
    summary = summarize_file(os.path.join(SAMPLES, "app_main.log"))
    assert summary.total_lines == 40000
    # Some lines are corrupt (stray JSON, rotation markers, a truncated
    # timestamp) and must be skipped rather than raising.
    assert summary.unparsed_lines > 0
    assert summary.parsed_lines == summary.total_lines - summary.unparsed_lines
    assert summary.parsed_lines > 0
    # A stray non-UTF-8 byte inside one message must not blow up the read.
    assert sum(summary.level_counts.values()) == summary.parsed_lines
    top_names = [name for name, _ in summary.top_loggers]
    assert len(summary.top_loggers) == 5
    assert top_names == sorted(top_names, key=lambda n: -dict(summary.top_loggers)[n])


def test_app_main_log_never_modified():
    path = os.path.join(SAMPLES, "app_main.log")
    before_hash = _sha256(path)
    summarize_file(path)
    assert _sha256(path) == before_hash


def test_level_filter_restricts_stats():
    path = os.path.join(SAMPLES, "boot.log")
    summary = summarize_file(path, level_filter="warning")
    assert summary.level_filter == "WARNING"
    assert summary.matched_lines == 1
    assert summary.level_counts == {"WARNING": 1}
    assert summary.first_timestamp == summary.last_timestamp


def test_level_filter_with_no_matches_is_not_an_error():
    path = os.path.join(SAMPLES, "boot.log")
    summary = summarize_file(path, level_filter="TRACE")
    assert summary.matched_lines == 0
    assert summary.level_counts == {}
    assert summary.first_timestamp is None
    assert summary.top_loggers == []
