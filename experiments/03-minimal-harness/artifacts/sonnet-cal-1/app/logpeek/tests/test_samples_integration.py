"""Exercise every file in the provided samples/ directory end to end."""

import os

import pytest

from logpeek.cli import main

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "samples")


def _sample(name):
    return os.path.join(SAMPLES_DIR, name)


pytestmark = pytest.mark.skipif(
    not os.path.isdir(SAMPLES_DIR), reason="samples/ directory not present"
)


def test_boot_log_summarizes_cleanly(capsys):
    rc = main([_sample("boot.log")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Total lines: 6" in out


def test_empty_log_is_a_clear_error(capsys):
    rc = main([_sample("empty.log")])
    err = capsys.readouterr().err
    assert rc != 0
    assert "empty" in err.lower()


def test_app_main_log_handles_embedded_garbage_and_odd_timestamps(capsys):
    rc = main([_sample("app_main.log")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Total lines: 40000" in out
    # The file has ~39 embedded garbage/sentinel lines mixed in with
    # otherwise valid entries; none of them should crash the tool, and the
    # reported time span should stay within a sane calendar range rather
    # than being dragged to 1970 or 2106 by sentinel epoch values.
    assert "unparseable: 39" in out
    for stray_year in ("1970-", "2106-"):
        assert stray_year not in out


def test_app_main_log_never_modified():
    path = _sample("app_main.log")
    before = os.stat(path).st_mtime_ns
    main([path])
    main([path, "--json"])
    assert os.stat(path).st_mtime_ns == before


def test_all_samples_together_report_per_file_and_nonzero_exit(capsys):
    rc = main([_sample("boot.log"), _sample("empty.log"), _sample("app_main.log")])
    captured = capsys.readouterr()
    assert rc != 0  # empty.log fails
    assert "boot.log" in captured.out
    assert "app_main.log" in captured.out
    assert "empty.log" in captured.err
