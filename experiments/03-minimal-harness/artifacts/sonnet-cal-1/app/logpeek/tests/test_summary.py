from logpeek.parser import parse_lines
from logpeek.summary import summarize

LINES = [
    "2026-06-01T00:00:00+00:00 INFO api.gw: evt 0\n",
    "2026-06-01T00:00:07+00:00 ERROR api.auth: evt 1\n",
    "2026-06-01T00:00:14+00:00 INFO api.gw: evt 2\n",
    "2026-06-01T00:00:21+00:00 INFO api.db: evt 3\n",
    "2026-06-01T00:00:28+00:00 ERROR api.gw: evt 4\n",
]


def test_summarize_counts_levels_and_time_span():
    result = parse_lines(LINES)
    summary = summarize("test.log", result)
    assert summary.total_lines == 5
    assert summary.parsed_lines == 5
    assert summary.level_counts == {
        "DEBUG": 0,
        "INFO": 3,
        "WARNING": 0,
        "ERROR": 2,
        "CRITICAL": 0,
    }
    assert summary.first_timestamp == "2026-06-01T00:00:00+00:00"
    assert summary.last_timestamp == "2026-06-01T00:00:28+00:00"


def test_summarize_top_loggers_ranked_by_frequency():
    result = parse_lines(LINES)
    summary = summarize("test.log", result)
    top = [entry["logger"] for entry in summary.top_loggers]
    assert top[0] == "api.gw"
    assert set(top) == {"api.gw", "api.auth", "api.db"}


def test_summarize_with_level_filter_narrows_everything():
    result = parse_lines(LINES)
    summary = summarize("test.log", result, level_filter="ERROR")
    assert summary.parsed_lines == 2
    assert summary.level_counts["ERROR"] == 2
    assert summary.level_counts["INFO"] == 0
    assert {e["logger"] for e in summary.top_loggers} == {"api.auth", "api.gw"}


def test_summarize_empty_entries_has_no_time_span():
    result = parse_lines([])
    summary = summarize("test.log", result)
    assert summary.first_timestamp is None
    assert summary.last_timestamp is None
    assert summary.top_loggers == []
