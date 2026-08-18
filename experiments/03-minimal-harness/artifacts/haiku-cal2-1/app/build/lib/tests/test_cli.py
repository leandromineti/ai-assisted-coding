import tempfile
import subprocess
import json
from pathlib import Path
import sys


def run_logpeek(*args):
    """Run logpeek CLI and return exit code, stdout, stderr."""
    cmd = [sys.executable, "-m", "logpeek.cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_cli_basic(tmp_path):
    """Test basic CLI functionality."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-01T00:00:00+00:00 INFO app.main: msg1\n"
        "2026-06-01T00:00:01+00:00 ERROR app.db: msg2\n"
    )

    code, stdout, stderr = run_logpeek(str(log_file))
    assert code == 0
    assert "Total lines: 2" in stdout
    assert "INFO" in stdout
    assert "ERROR" in stdout


def test_cli_missing_file():
    """Test CLI with missing file."""
    code, stdout, stderr = run_logpeek("/nonexistent/file.log")
    assert code != 0
    assert "not found" in stderr.lower() or "error" in stderr.lower()


def test_cli_empty_file(tmp_path):
    """Test CLI with empty file."""
    log_file = tmp_path / "empty.log"
    log_file.write_text("")

    code, stdout, stderr = run_logpeek(str(log_file))
    assert code != 0
    assert "empty" in stderr.lower()


def test_cli_level_filter(tmp_path):
    """Test CLI with level filter."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-01T00:00:00+00:00 INFO app.main: msg1\n"
        "2026-06-01T00:00:01+00:00 ERROR app.db: msg2\n"
        "2026-06-01T00:00:02+00:00 INFO app.net: msg3\n"
    )

    code, stdout, stderr = run_logpeek(str(log_file), "--level", "INFO")
    assert code == 0
    assert "Total lines: 2" in stdout


def test_cli_json_output(tmp_path):
    """Test CLI with JSON output."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-01T00:00:00+00:00 INFO app.main: msg1\n"
        "2026-06-01T00:00:01+00:00 ERROR app.db: msg2\n"
    )

    code, stdout, stderr = run_logpeek(str(log_file), "--json")
    assert code == 0
    data = json.loads(stdout)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["total_lines"] == 2
    assert "INFO" in data[0]["levels"]


def test_cli_multiple_files(tmp_path):
    """Test CLI with multiple files."""
    log1 = tmp_path / "test1.log"
    log1.write_text("2026-06-01T00:00:00+00:00 INFO app.main: msg1\n")

    log2 = tmp_path / "test2.log"
    log2.write_text(
        "2026-06-01T00:00:00+00:00 ERROR app.db: msg2\n"
        "2026-06-01T00:00:01+00:00 ERROR app.db: msg3\n"
    )

    code, stdout, stderr = run_logpeek(str(log1), str(log2))
    assert code == 0
    assert "test1.log" in stdout
    assert "test2.log" in stdout


def test_cli_multiple_files_json(tmp_path):
    """Test CLI with multiple files and JSON output."""
    log1 = tmp_path / "test1.log"
    log1.write_text("2026-06-01T00:00:00+00:00 INFO app.main: msg1\n")

    log2 = tmp_path / "test2.log"
    log2.write_text("2026-06-01T00:00:00+00:00 ERROR app.db: msg2\n")

    code, stdout, stderr = run_logpeek(str(log1), str(log2), "--json")
    assert code == 0
    data = json.loads(stdout)
    assert len(data) == 2
