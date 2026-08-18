import subprocess
import tempfile
import json
from pathlib import Path


def run_logpeek(*args, **kwargs):
    """Run logpeek command and return result."""
    cmd = ['python', '-m', 'logpeek.cli'] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd='/app'
    )
    return result


class TestCLI:
    def test_single_file_basic(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f.write('2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n')
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek(filepath)
            assert result.returncode == 0
            assert 'Total lines: 2' in result.stdout
            assert 'INFO: 2' in result.stdout
        finally:
            Path(filepath).unlink()

    def test_multiple_files(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1:
            f1.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f1.flush()
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
            f2.write('2026-05-31T23:58:01+00:00 ERROR api.gw: msg2\n')
            f2.flush()
            file2 = f2.name

        try:
            result = run_logpeek(file1, file2)
            assert result.returncode == 0
            assert 'Total lines: 1' in result.stdout
            assert file1 in result.stdout
            assert file2 in result.stdout
        finally:
            Path(file1).unlink()
            Path(file2).unlink()

    def test_level_filter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f.write('2026-05-31T23:58:01+00:00 ERROR boot.init: msg2\n')
            f.write('2026-05-31T23:58:02+00:00 INFO boot.svc: msg3\n')
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek('--level', 'ERROR', filepath)
            assert result.returncode == 0
            assert 'Total lines: 1' in result.stdout
            assert 'ERROR: 1' in result.stdout
        finally:
            Path(filepath).unlink()

    def test_json_output(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f.write('2026-05-31T23:58:01+00:00 ERROR api.gw: msg2\n')
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek('--json', filepath)
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['total_lines'] == 2
            assert data[0]['level_counts']['INFO'] == 1
            assert data[0]['level_counts']['ERROR'] == 1
        finally:
            Path(filepath).unlink()

    def test_empty_file_error(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek(filepath)
            assert result.returncode == 1
            assert 'No valid log lines found' in result.stderr
        finally:
            Path(filepath).unlink()

    def test_nonexistent_file_error(self):
        result = run_logpeek('/nonexistent/file.log')
        assert result.returncode == 1
        assert 'File not found' in result.stderr

    def test_mixed_valid_invalid_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: valid\n')
            f.write('{malformed json\n')
            f.write('2026-05-31T23:58:01+00:00 ERROR boot.init: also valid\n')
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek(filepath)
            assert result.returncode == 0
            assert 'Total lines: 2' in result.stdout
        finally:
            Path(filepath).unlink()

    def test_top_loggers_output(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for i in range(10):
                f.write(f'2026-05-31T23:58:0{i%6}+00:00 INFO api.gw: msg\n')
            for i in range(5):
                f.write(f'2026-05-31T23:58:0{i%6}+00:00 INFO api.auth: msg\n')
            f.flush()
            filepath = f.name

        try:
            result = run_logpeek(filepath)
            assert result.returncode == 0
            assert 'Top loggers:' in result.stdout
            assert 'api.gw (10)' in result.stdout
            assert 'api.auth (5)' in result.stdout
        finally:
            Path(filepath).unlink()
