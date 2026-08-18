import pytest
import tempfile
from pathlib import Path
from logpeek.parser import LogParser, LogAnalyzer


class TestLogParser:
    def test_parse_valid_line(self):
        line = "2026-06-01T00:00:00+00:00 INFO api.gw: evt 0 code 3"
        result = LogParser.parse_line(line)
        assert result is not None
        timestamp, level, logger, message = result
        assert timestamp == "2026-06-01T00:00:00+00:00"
        assert level == "INFO"
        assert logger == "api.gw"
        assert message == "evt 0 code 3"

    def test_parse_line_with_whitespace(self):
        line = "  2026-06-01T00:00:00+00:00 DEBUG boot.svc: unit graph built  "
        result = LogParser.parse_line(line)
        assert result is not None
        timestamp, level, logger, message = result
        assert level == "DEBUG"
        assert logger == "boot.svc"

    def test_parse_critical_level(self):
        line = "2026-06-01T00:00:35+00:00 CRITICAL api.gw: evt 5 code 3"
        result = LogParser.parse_line(line)
        assert result is not None
        _, level, _, _ = result
        assert level == "CRITICAL"

    def test_parse_warning_level(self):
        line = "2026-06-04T05:46:33+00:00 WARNING api.http: evt 39999 code 9"
        result = LogParser.parse_line(line)
        assert result is not None
        _, level, _, _ = result
        assert level == "WARNING"

    def test_parse_invalid_line(self):
        line = "{unterminated json dump"
        result = LogParser.parse_line(line)
        assert result is None

    def test_parse_marker_line(self):
        line = "### log rotated ###"
        result = LogParser.parse_line(line)
        assert result is None

    def test_parse_truncated_timestamp(self):
        line = "2026-04-01T1"
        result = LogParser.parse_line(line)
        assert result is None

    def test_parse_timestamp_valid(self):
        ts = LogParser.parse_timestamp("2026-06-01T00:00:00+00:00")
        assert ts.year == 2026
        assert ts.month == 6
        assert ts.day == 1
        assert ts.hour == 0

    def test_parse_timestamp_invalid(self):
        with pytest.raises(ValueError):
            LogParser.parse_timestamp("not a timestamp")


class TestLogAnalyzer:
    def test_analyze_boot_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        assert analyzer.lines_total == 6
        assert analyzer.levels['INFO'] == 4
        assert analyzer.levels['DEBUG'] == 1
        assert analyzer.levels['WARNING'] == 1
        assert len(analyzer.loggers) > 0

    def test_analyze_empty_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/empty.log')

        assert analyzer.lines_total == 0
        assert len(analyzer.levels) == 0
        assert len(analyzer.loggers) == 0
        assert analyzer.is_empty is True

    def test_get_time_span_boot_log(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        first, last = analyzer.get_time_span()
        assert first is not None
        assert last is not None
        assert first <= last

    def test_get_time_span_empty(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/empty.log')

        first, last = analyzer.get_time_span()
        assert first is None
        assert last is None

    def test_get_top_loggers_boot(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        top = analyzer.get_top_loggers(5)
        assert len(top) > 0
        assert top[0][1] >= top[1][1] if len(top) > 1 else True

    def test_get_top_loggers_empty(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/empty.log')

        top = analyzer.get_top_loggers(5)
        assert len(top) == 0

    def test_level_filter(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/boot.log')

        summary = analyzer.get_summary(level_filter='INFO')
        assert 'INFO' in summary['levels']
        assert summary['levels']['INFO'] == 4

    def test_file_not_found(self):
        analyzer = LogAnalyzer()
        with pytest.raises(FileNotFoundError):
            analyzer.process_file('/nonexistent/path/file.log')

    def test_process_file_with_malformed_lines(self):
        # app_main.log contains intentional malformed lines
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/app_main.log')

        # Should process without error and count valid lines
        assert analyzer.lines_total > 0
        assert len(analyzer.levels) > 0

    def test_app_main_top_5_loggers(self):
        analyzer = LogAnalyzer()
        analyzer.process_file('/app/samples/app_main.log')

        top = analyzer.get_top_loggers(5)
        assert len(top) >= 1
        # First should be api.gw based on measurements
        assert top[0][0] == 'api.gw'
