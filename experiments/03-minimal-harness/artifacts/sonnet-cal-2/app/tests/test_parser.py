from datetime import datetime, timezone

from logpeek.parser import parse_line


def test_parses_iso8601_line():
    entry = parse_line("2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff")
    assert entry is not None
    assert entry.timestamp == datetime(2026, 5, 31, 23, 58, tzinfo=timezone.utc)
    assert entry.level == "INFO"
    assert entry.logger == "boot.init"
    assert entry.message == "kernel handoff"


def test_parses_epoch_line():
    entry = parse_line("1767233000 INFO relay.legacy: batch item 1654")
    assert entry is not None
    assert entry.timestamp == datetime.fromtimestamp(1767233000, tz=timezone.utc)
    assert entry.logger == "relay.legacy"


def test_parses_epoch_zero_boundary():
    entry = parse_line("0 WARNING relic.clock: epoch zero import")
    assert entry is not None
    assert entry.timestamp == datetime(1970, 1, 1, tzinfo=timezone.utc)


def test_parses_large_epoch_boundary():
    entry = parse_line("4294967295 ERROR relic.clock: horizon import")
    assert entry is not None
    assert entry.timestamp == datetime.fromtimestamp(4294967295, tz=timezone.utc)


def test_rejects_json_garbage():
    assert parse_line("{unterminated json dump") is None


def test_rejects_rotation_marker():
    assert parse_line("### log rotated ###") is None


def test_rejects_truncated_timestamp_only_line():
    assert parse_line("2026-04-01T1") is None


def test_rejects_blank_line():
    assert parse_line("") is None
    assert parse_line("\n") is None


def test_message_may_contain_colons():
    entry = parse_line("2026-05-31T23:58:00+00:00 INFO svc.x: ratio 3:1 achieved")
    assert entry is not None
    assert entry.message == "ratio 3:1 achieved"
