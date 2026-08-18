import json
import os
import subprocess
import sys

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def run_cli(args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "logpeek.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_text_output_for_valid_file():
    result = run_cli([os.path.join(SAMPLES, "boot.log")])
    assert result.returncode == 0
    assert "Total lines:     6" in result.stdout
    assert "Time span:" in result.stdout
    assert "Top loggers:" in result.stdout


def test_json_output_is_valid_and_complete():
    result = run_cli(["--json", os.path.join(SAMPLES, "boot.log")])
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    entry = payload[0]
    assert entry["error"] is None
    assert entry["total_lines"] == 6
    assert entry["level_counts"] == {"INFO": 4, "DEBUG": 1, "WARNING": 1}
    assert entry["time_span"]["first"] == "2026-05-31T23:58:00+00:00"
    assert len(entry["top_loggers"]) == 2


def test_level_filter_flag():
    result = run_cli(["--level", "WARNING", os.path.join(SAMPLES, "boot.log")])
    assert result.returncode == 0
    assert "Level filter:    WARNING" in result.stdout
    assert "Matching lines:  1" in result.stdout


def test_empty_file_gives_clear_error_and_nonzero_exit():
    result = run_cli([os.path.join(SAMPLES, "empty.log")])
    assert result.returncode != 0
    assert "empty" in result.stderr.lower()


def test_non_log_file_gives_clear_error_and_nonzero_exit():
    result = run_cli([os.path.join(FIXTURES, "not_a_log.txt")])
    assert result.returncode != 0
    assert "error" in result.stderr.lower()


def test_missing_file_gives_clear_error_and_nonzero_exit():
    result = run_cli(["/no/such/file.log"])
    assert result.returncode != 0
    assert "no such file" in result.stderr.lower()


def test_multiple_files_mixed_success_and_failure():
    result = run_cli(
        [
            os.path.join(SAMPLES, "boot.log"),
            os.path.join(SAMPLES, "empty.log"),
        ]
    )
    # Good file still gets summarized even though the other one fails.
    assert "boot.log" in result.stdout
    assert "empty" in result.stderr.lower()
    assert result.returncode != 0


def test_json_output_for_multiple_files_reports_error_per_file():
    result = run_cli(
        [
            "--json",
            os.path.join(SAMPLES, "boot.log"),
            os.path.join(SAMPLES, "empty.log"),
        ]
    )
    payload = json.loads(result.stdout)
    assert len(payload) == 2
    ok, bad = payload
    assert ok["error"] is None
    assert bad["error"] is not None
    assert result.returncode != 0


def test_large_messy_file_does_not_crash():
    result = run_cli([os.path.join(SAMPLES, "app_main.log")])
    assert result.returncode == 0
    assert "Total lines:     40000" in result.stdout
    assert "Unparsed lines:" in result.stdout


def test_installed_console_script_runs_from_any_directory(tmp_path):
    result = subprocess.run(
        ["logpeek", os.path.join(SAMPLES, "boot.log")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Total lines:     6" in result.stdout
