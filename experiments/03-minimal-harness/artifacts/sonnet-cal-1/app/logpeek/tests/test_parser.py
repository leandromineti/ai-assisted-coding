from logpeek.parser import parse_lines


def test_parses_well_formed_iso_lines():
    lines = [
        "2026-06-01T00:00:00+00:00 INFO api.gw: evt 0\n",
        "2026-06-01T00:00:07+00:00 ERROR api.auth: evt 1\n",
    ]
    result = parse_lines(lines)
    assert result.total_lines == 2
    assert result.unparseable_lines == 0
    assert len(result.entries) == 2
    assert result.entries[0].level == "INFO"
    assert result.entries[0].logger == "api.gw"
    assert result.entries[0].message == "evt 0"
    assert result.entries[1].level == "ERROR"


def test_counts_garbage_lines_as_unparseable_without_crashing():
    lines = [
        "2026-06-01T00:00:00+00:00 INFO api.gw: evt 0\n",
        "{unterminated json dump\n",
        "### log rotated ###\n",
        "2026-04-01T1\n",  # truncated timestamp
        "2026-06-01T00:00:07+00:00 ERROR api.auth: evt 1\n",
    ]
    result = parse_lines(lines)
    assert result.total_lines == 5
    assert result.unparseable_lines == 3
    assert len(result.entries) == 2


def test_blank_lines_count_as_total_but_are_unparseable():
    lines = ["2026-06-01T00:00:00+00:00 INFO api.gw: evt 0\n", "\n", "\n"]
    result = parse_lines(lines)
    assert result.total_lines == 3
    assert result.unparseable_lines == 2
    assert len(result.entries) == 1


def test_unix_epoch_timestamp_in_plausible_range_is_accepted():
    lines = ["1767233000 INFO relay.legacy: batch item 1\n"]
    result = parse_lines(lines)
    assert result.unparseable_lines == 0
    assert result.entries[0].timestamp.year == 2026


def test_epoch_sentinel_values_outside_plausible_range_are_rejected():
    # 0 (1970) and 2**32-1 (2106) are boundary/sentinel values that would
    # otherwise blow the reported time span out to a meaningless range.
    lines = [
        "0 WARNING relic.clock: epoch zero import\n",
        "4294967295 ERROR relic.clock: horizon import\n",
    ]
    result = parse_lines(lines)
    assert result.total_lines == 2
    assert result.unparseable_lines == 2
    assert result.entries == []


def test_logger_name_is_stripped_of_surrounding_whitespace():
    lines = ["2026-06-01T00:00:00+00:00 INFO   api.gw  : evt 0\n"]
    result = parse_lines(lines)
    assert result.entries[0].logger == "api.gw"
