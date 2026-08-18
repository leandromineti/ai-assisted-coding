import pytest
import tempfile
import json
import subprocess
import sys
from pathlib import Path
from logpeek.cli import is_log_file, format_summary, format_text_summary
from logpeek.parser import LogAnalyzer


class TestIsLogFile:
    def test_valid_log_file(self):
        assert is_log_file('/app/samples/boot.log') is True

    def test_empty_log_file(self):
        assert is_log_file('/app/samples/empty.log') is True

    def test_non_log_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a log file\n")
            f.write("Just some random text\n")
            f.flush()
            temp_path = f.name

        try:
            assert is_log_file(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_missing_file_treated_as_error(self):
        # is_log_file returns True for missing files (error handling is in parser)
        result = is_log_file('/nonexistent/file.log')
        assert result is True


class TestFormatSummary:
    def test_format_summary_boot_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        result = format_summary(analyzer, '/app/samples/boot.log')
        assert result['file'] == '/app/samples/boot.log'
        assert result['total_lines'] == 6
        assert 'levels' in result
        assert 'time_span' in result
        assert result['time_span']['start'] is not None
        assert result['time_span']['end'] is not None
        assert 'top_loggers' in result

    def test_format_summary_empty_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/empty.log')

        result = format_summary(analyzer, '/app/samples/empty.log')
        assert result['total_lines'] == 0
        assert result['levels'] == {}
        assert result['time_span']['start'] is None
        assert result['time_span']['end'] is None

    def test_format_summary_with_level_filter(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        result = format_summary(analyzer, '/app/samples/boot.log', level_filter='INFO')
        assert 'INFO' in result['levels']
        assert result['levels']['INFO'] == 4


class TestFormatTextSummary:
    def test_format_text_summary_boot_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        output = format_text_summary(analyzer, '/app/samples/boot.log')
        assert '/app/samples/boot.log' in output
        assert 'Total lines: 6' in output
        assert 'Levels:' in output
        assert 'Time span:' in output
        assert 'Top loggers:' in output

    def test_format_text_summary_empty_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/empty.log')

        output = format_text_summary(analyzer, '/app/samples/empty.log')
        assert 'Total lines: 0' in output
        assert 'Levels: (none)' in output
        assert 'Time span: (empty)' in output


class TestCLI:
    def test_cli_single_file(self):
        result = subprocess.run(
            [sys.executable, '-m', 'logpeek.cli', '/app/samples/boot.log'],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        assert 'File: /app/samples/boot.log' in result.stdout
        assert 'Total lines: 6' in result.stdout

    def test_cli_json_output(self):
        result = subprocess.run(
            [sys.executable, '-m', 'logpeek.cli', '--json', '/app/samples/boot.log'],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['file'] == '/app/samples/boot.log'
        assert data[0]['total_lines'] == 6

    def test_cli_level_filter(self):
        result = subprocess.run(
            [sys.executable, '-m', 'logpeek.cli', '--level', 'INFO', '/app/samples/boot.log'],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        assert 'Levels:' in result.stdout
        assert 'INFO: 4' in result.stdout

    def test_cli_multiple_files(self):
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'logpeek.cli',
                '/app/samples/boot.log',
                '/app/samples/empty.log',
            ],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        assert '/app/samples/boot.log' in result.stdout
        assert '/app/samples/empty.log' in result.stdout

    def test_cli_empty_file(self):
        result = subprocess.run(
            [sys.executable, '-m', 'logpeek.cli', '/app/samples/empty.log'],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        assert 'Total lines: 0' in result.stdout

    def test_cli_non_log_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a log file\n")
            f.write("Just some random text\n")
            f.flush()
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'logpeek.cli', temp_path],
                capture_output=True,
                text=True,
                cwd='/app',
            )
            assert result.returncode == 1
            assert 'does not appear to be a log file' in result.stderr
        finally:
            Path(temp_path).unlink()

    def test_cli_missing_file(self):
        result = subprocess.run(
            [sys.executable, '-m', 'logpeek.cli', '/nonexistent/file.log'],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 1
        assert 'Error' in result.stderr

    def test_cli_json_multiple_files(self):
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'logpeek.cli',
                '--json',
                '/app/samples/boot.log',
                '/app/samples/empty.log',
            ],
            capture_output=True,
            text=True,
            cwd='/app',
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 2
