import hashlib
import json
from pathlib import Path

import pytest

from logpeek.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLES = Path(__file__).parent.parent / "samples"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cli_never_modifies_input_files(capsys):
    paths = [SAMPLES / "app_main.log", SAMPLES / "boot.log", SAMPLES / "empty.log"]
    before = {p: sha256(p) for p in paths}

    main([str(p) for p in paths])

    after = {p: sha256(p) for p in paths}
    assert before == after


def test_cli_text_output_all_samples(capsys):
    exit_code = main(
        [str(SAMPLES / "app_main.log"), str(SAMPLES / "boot.log"), str(SAMPLES / "empty.log")]
    )
    out, err = capsys.readouterr()

    # empty.log fails -> non-zero overall exit code, error reported on stderr
    assert exit_code == 1
    assert "empty.log: file is empty" in err

    # the two valid files still get summarized on stdout
    assert "app_main.log" in out
    assert "boot.log" in out
    assert "Total lines: 40000" in out
    assert "Total lines: 6" in out


def test_cli_json_output_is_valid_and_complete(capsys):
    exit_code = main(["--json", str(SAMPLES / "boot.log")])
    out, _ = capsys.readouterr()

    assert exit_code == 0
    data = json.loads(out)
    assert len(data) == 1
    entry = data[0]
    assert entry["total_lines"] == 6
    assert entry["level_counts"] == {"DEBUG": 1, "INFO": 4, "WARNING": 1}
    assert entry["top_loggers"] == [
        {"logger": "boot.init", "count": 3},
        {"logger": "boot.svc", "count": 3},
    ]
    assert entry["first_event"] == "2026-05-31T23:58:00+00:00"
    assert entry["last_event"] == "2026-05-31T23:58:07+00:00"


def test_cli_json_output_reports_errors_inline(capsys):
    exit_code = main(["--json", str(SAMPLES / "empty.log")])
    out, _ = capsys.readouterr()

    assert exit_code == 1
    data = json.loads(out)
    assert len(data) == 1
    assert "error" in data[0]
    assert "empty" in data[0]["error"]


def test_cli_level_filter(capsys):
    exit_code = main(["--level", "WARNING", str(SAMPLES / "boot.log")])
    out, _ = capsys.readouterr()

    assert exit_code == 0
    assert "Filter: level=WARNING (1 matching entries)" in out
    assert "WARNING: 1" in out
    assert "DEBUG" not in out.split("Level counts:")[1]


def test_cli_not_a_log_file_reports_clear_error_and_nonzero_exit(capsys):
    exit_code = main([str(FIXTURES / "not_a_log.txt")])
    out, err = capsys.readouterr()

    assert exit_code == 1
    assert out == ""
    assert "not a recognized log format" in err


def test_cli_missing_file_reports_clear_error_and_nonzero_exit(capsys):
    exit_code = main([str(FIXTURES / "does_not_exist.log")])
    _, err = capsys.readouterr()

    assert exit_code == 1
    assert "no such file" in err


def test_cli_requires_at_least_one_path():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2
