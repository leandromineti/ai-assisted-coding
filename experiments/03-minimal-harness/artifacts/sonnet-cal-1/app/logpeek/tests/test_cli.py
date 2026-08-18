import json
import os

import pytest

from logpeek.cli import main

GOOD_LOG = """\
2026-06-01T00:00:00+00:00 INFO api.gw: evt 0
2026-06-01T00:00:07+00:00 ERROR api.auth: evt 1
2026-06-01T00:00:14+00:00 INFO api.gw: evt 2
"""


@pytest.fixture
def good_log(tmp_path):
    path = tmp_path / "good.log"
    path.write_text(GOOD_LOG)
    return path


def test_summarizes_valid_log_and_exits_zero(good_log, capsys):
    rc = main([str(good_log)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Total lines: 3" in out
    assert "INFO: 2" in out
    assert "ERROR: 1" in out


def test_json_output_is_valid_and_matches_text(good_log, capsys):
    rc = main([str(good_log), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["total_lines"] == 3
    assert data[0]["level_counts"]["INFO"] == 2
    assert data[0]["top_loggers"][0]["logger"] == "api.gw"


def test_empty_file_errors_with_nonzero_exit(tmp_path, capsys):
    path = tmp_path / "empty.log"
    path.write_text("")
    rc = main([str(path)])
    err = capsys.readouterr().err
    assert rc != 0
    assert "empty" in err.lower()


def test_non_log_file_errors_with_nonzero_exit(tmp_path, capsys):
    path = tmp_path / "notalog.txt"
    path.write_text("hello\nworld\nthis is not a log\n")
    rc = main([str(path)])
    err = capsys.readouterr().err
    assert rc != 0
    assert str(path) in err


def test_missing_file_errors_with_nonzero_exit(tmp_path, capsys):
    path = tmp_path / "nope.log"
    rc = main([str(path)])
    err = capsys.readouterr().err
    assert rc != 0
    assert "no such file" in err.lower()


def test_level_filter_narrows_output(good_log, capsys):
    rc = main([str(good_log), "--level", "error"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Parsed entries: 1" in out


def test_invalid_level_exits_nonzero(good_log, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([str(good_log), "--level", "BOGUS"])
    assert exc_info.value.code != 0


def test_multiple_files_one_bad_one_good_reports_both(tmp_path, good_log, capsys):
    empty_path = tmp_path / "empty.log"
    empty_path.write_text("")
    rc = main([str(empty_path), str(good_log)])
    captured = capsys.readouterr()
    assert rc != 0
    assert "empty" in captured.err.lower()
    assert "Total lines: 3" in captured.out


def test_input_file_is_never_modified(good_log):
    before_mtime = os.stat(good_log).st_mtime_ns
    before_content = good_log.read_bytes()
    main([str(good_log)])
    main([str(good_log), "--json"])
    main([str(good_log), "--level", "info"])
    assert os.stat(good_log).st_mtime_ns == before_mtime
    assert good_log.read_bytes() == before_content
