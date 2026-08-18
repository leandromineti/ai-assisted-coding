import pytest
import tempfile
from pathlib import Path
from logpeek.parser import LogParser, LogEntry


class TestLogParser:
    def test_parse_valid_log_line(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff\n')
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is True
            assert len(parser.entries) == 1
            assert parser.entries[0].timestamp == '2026-05-31T23:58:00+00:00'
            assert parser.entries[0].level == 'INFO'
            assert parser.entries[0].logger == 'boot.init'
            assert parser.entries[0].message == 'kernel handoff'
        finally:
            Path(filepath).unlink()

    def test_parse_multiple_levels(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 DEBUG boot.init: debug msg\n')
            f.write('2026-05-31T23:58:01+00:00 INFO boot.init: info msg\n')
            f.write('2026-05-31T23:58:02+00:00 WARNING boot.svc: warning msg\n')
            f.write('2026-05-31T23:58:03+00:00 ERROR boot.svc: error msg\n')
            f.write('2026-05-31T23:58:04+00:00 CRITICAL boot.init: critical msg\n')
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is True
            assert len(parser.entries) == 5
            levels = [e.level for e in parser.entries]
            assert levels == ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        finally:
            Path(filepath).unlink()

    def test_parse_multiword_message(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 ERROR api.gw: failed to connect to upstream server\n')
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is True
            assert parser.entries[0].message == 'failed to connect to upstream server'
        finally:
            Path(filepath).unlink()

    def test_parse_malformed_line_skipped(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: valid line\n')
            f.write('{unterminated json dump\n')
            f.write('2026-05-31T23:58:01+00:00 INFO boot.init: another valid line\n')
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is True
            assert len(parser.entries) == 2
            assert parser.invalid_line_count == 1
        finally:
            Path(filepath).unlink()

    def test_parse_empty_file(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is False
            assert len(parser.entries) == 0
        finally:
            Path(filepath).unlink()

    def test_get_stats_basic(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f.write('2026-05-31T23:58:01+00:00 INFO boot.init: msg2\n')
            f.write('2026-05-31T23:58:02+00:00 ERROR boot.svc: msg3\n')
            f.flush()
            filepath = f.name

        try:
            parser.parse_file(filepath)
            stats = parser.get_stats()

            assert stats['total_lines'] == 3
            assert stats['level_counts']['INFO'] == 2
            assert stats['level_counts']['ERROR'] == 1
            assert stats['time_span']['start'] == '2026-05-31T23:58:00+00:00'
            assert stats['time_span']['end'] == '2026-05-31T23:58:02+00:00'
        finally:
            Path(filepath).unlink()

    def test_get_stats_with_level_filter(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('2026-05-31T23:58:00+00:00 INFO boot.init: msg1\n')
            f.write('2026-05-31T23:58:01+00:00 ERROR boot.init: msg2\n')
            f.write('2026-05-31T23:58:02+00:00 INFO boot.svc: msg3\n')
            f.flush()
            filepath = f.name

        try:
            parser.parse_file(filepath)
            stats = parser.get_stats(level_filter='INFO')

            assert stats['total_lines'] == 2
            assert stats['level_counts']['INFO'] == 2
            assert 'ERROR' not in stats['level_counts']
        finally:
            Path(filepath).unlink()

    def test_get_stats_top_loggers(self):
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for i in range(10):
                f.write(f'2026-05-31T23:58:0{i%6}+00:00 INFO api.gw: msg{i}\n')
            for i in range(5):
                f.write(f'2026-05-31T23:58:0{i%6}+00:00 INFO api.auth: msg{i}\n')
            for i in range(3):
                f.write(f'2026-05-31T23:58:0{i%6}+00:00 INFO api.http: msg{i}\n')
            f.flush()
            filepath = f.name

        try:
            parser.parse_file(filepath)
            stats = parser.get_stats()

            top_loggers = stats['top_loggers']
            assert len(top_loggers) == 3
            assert top_loggers[0] == ('api.gw', 10)
            assert top_loggers[1] == ('api.auth', 5)
            assert top_loggers[2] == ('api.http', 3)
        finally:
            Path(filepath).unlink()

    def test_encoding_replacement(self):
        """Test that non-UTF-8 sequences are handled gracefully."""
        parser = LogParser()
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.log', delete=False) as f:
            # Write a valid line, then a byte sequence that's invalid UTF-8
            f.write(b'2026-05-31T23:58:00+00:00 INFO boot.init: caf\xe9\n')
            f.flush()
            filepath = f.name

        try:
            assert parser.parse_file(filepath) is True
            assert len(parser.entries) == 1
            # The invalid byte should be replaced with a replacement character
            assert parser.entries[0].message is not None
        finally:
            Path(filepath).unlink()

    def test_nonexistent_file(self):
        parser = LogParser()
        with pytest.raises(RuntimeError):
            parser.parse_file('/nonexistent/path/file.log')
