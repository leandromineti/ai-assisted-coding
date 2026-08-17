"""Tests for table and JSON rendering."""

import json

from tarpeek.archive import ArchiveMember
from tarpeek.output import render_json, render_table

_MEMBERS = [
    ArchiveMember(name="big.log", type="file", size=4096, last_modified="2026-08-10T09:15:00Z"),
    ArchiveMember(name="docs", type="dir", size=0, last_modified="2026-07-15T12:00:00Z"),
]


# --- T009: table renderer ---


def test_render_table_includes_all_columns_and_values():
    table = render_table(_MEMBERS)
    for expected in ("big.log", "file", "4096", "2026-08-10T09:15:00Z", "docs", "dir", "2026-07-15T12:00:00Z"):
        assert expected in table


def test_render_table_readable_for_empty_list():
    table = render_table([])
    assert isinstance(table, str)


# --- T022: render_json ---


def test_render_json_parses_as_top_level_array_with_expected_keys():
    data = json.loads(render_json(_MEMBERS))
    assert isinstance(data, list)
    assert len(data) == 2
    for obj in data:
        assert set(obj.keys()) == {"name", "type", "size", "last_modified"}


def test_render_json_value_types_are_correct():
    data = json.loads(render_json(_MEMBERS))
    obj = data[0]
    assert isinstance(obj["name"], str)
    assert isinstance(obj["type"], str)
    assert isinstance(obj["size"], int)
    assert isinstance(obj["last_modified"], str)


def test_render_json_empty_list_renders_empty_array():
    assert json.loads(render_json([])) == []
