from datetime import datetime, timezone
from pathlib import Path

import pytest

from logpeek.parser import (
    LogFileError,
    parse_line,
    parse_timestamp,
    summarize_file,
)

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLES = Path(__file__).parent.parent / "samples"


def test_parse_timestamp_iso8601_with_offset():
    dt = parse_timestamp("2026-06-01T00:00:00+00:00")
    assert dt == datetime(2026, 6, 1, tzinfo=timezone.utc)


def test_parse_timestamp_iso8601_negative_offset_converts_to_utc():
    dt = parse_timestamp("2026-05-31T22:56:33-03:00")
    assert dt == datetime(2026, 6, 1, 1, 56, 33, tzinfo=timezone.utc)


def test_parse_timestamp_unix_epoch_seconds():
    dt = parse_timestamp("1767233000")
    assert dt == datetime.fromtimestamp(1767233000, tz=timezone.utc)


def test_parse_timestamp_epoch_zero_and_max_uint32():
    assert parse_timestamp("0") == datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert parse_timestamp("4294967295").year == 2106


def test_parse_timestamp_garbage_returns_none():
    assert parse_timestamp("2026-04-01T1") is None
    assert parse_timestamp("not-a-timestamp") is None


def test_parse_line_valid():
    entry = parse_line("2026-06-01T00:00:00+00:00 INFO api.gw: evt 0 code 3")
    assert entry is not None
    assert entry.level == "INFO"
    assert entry.logger == "api.gw"
    assert entry.message == "evt 0 code 3"


def test_parse_line_rejects_garbage():
    assert parse_line("{unterminated json dump") is None
    assert parse_line("### log rotated ###") is None
    assert parse_line("2026-04-01T1") is None
    assert parse_line("") is None


def test_summarize_file_empty_raises():
    with pytest.raises(LogFileError, match="empty"):
        summarize_file(FIXTURES / "empty.log")


def test_summarize_file_missing_raises():
    with pytest.raises(LogFileError, match="no such file"):
        summarize_file(FIXTURES / "does_not_exist.log")


def test_summarize_file_not_a_log_raises():
    with pytest.raises(LogFileError, match="not a recognized log format"):
        summarize_file(FIXTURES / "not_a_log.txt")


def test_summarize_boot_log():
    summary = summarize_file(SAMPLES / "boot.log")
    assert summary.total_lines == 6
    assert summary.parsed_lines == 6
    assert summary.unparsed_lines == 0
    assert summary.level_counts == {"DEBUG": 1, "INFO": 4, "WARNING": 1}
    assert summary.first_event == datetime(2026, 5, 31, 23, 58, 0, tzinfo=timezone.utc)
    assert summary.last_event == datetime(2026, 5, 31, 23, 58, 7, tzinfo=timezone.utc)
    assert summary.top_loggers == [("boot.init", 3), ("boot.svc", 3)]


def test_summarize_app_main_log_handles_mixed_garbage_and_formats():
    summary = summarize_file(SAMPLES / "app_main.log")
    assert summary.total_lines == 40000
    # 13 unterminated-json lines + 12 rotation markers + 12 truncated timestamps
    assert summary.unparsed_lines == 37
    assert summary.parsed_lines == 40000 - 37
    assert sum(summary.level_counts.values()) == summary.parsed_lines
    # relic.clock entries carry deliberately extreme epoch timestamps (1970 / 2106)
    assert summary.first_event == datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert summary.last_event.year == 2106
    assert len(summary.top_loggers) == 5
    assert summary.top_loggers[0][0] == "api.gw"


def test_summarize_file_level_filter_restricts_stats():
    summary = summarize_file(SAMPLES / "app_main.log", level_filter="error")
    assert summary.level_filter == "ERROR"
    assert set(summary.level_counts) == {"ERROR"}
    assert summary.total_lines == 40000  # unaffected by filtering
    assert summary.parsed_lines == 40000 - 37  # unaffected by filtering
    assert sum(count for _, count in summary.top_loggers) <= summary.level_counts["ERROR"]


def test_summarize_file_level_filter_no_matches_gives_empty_stats():
    summary = summarize_file(SAMPLES / "boot.log", level_filter="CRITICAL")
    assert summary.level_counts == {}
    assert summary.first_event is None
    assert summary.last_event is None
    assert summary.top_loggers == []
