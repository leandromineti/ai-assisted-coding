import pytest
import json
import tarfile
import tempfile
from pathlib import Path
from io import StringIO
import sys

from tarpeek.cli import main, format_size


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_archive(temp_dir):
    archive_path = temp_dir / "sample.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        import io
        for i in range(3):
            content = f"File {i} content".encode()
            tarinfo = tarfile.TarInfo(name=f"file{i}.txt")
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
    return archive_path


class TestFormatSize:
    def test_bytes(self):
        assert format_size(512) == "512B"

    def test_kilobytes(self):
        result = format_size(1024)
        assert "KB" in result and ("1" in result or "1.0" in result)

    def test_megabytes(self):
        result = format_size(1024 * 1024)
        assert "MB" in result and ("1" in result or "1.0" in result)

    def test_gigabytes(self):
        result = format_size(1024 * 1024 * 1024)
        assert "GB" in result and ("1" in result or "1.0" in result)


class TestCLI:
    def test_main_with_valid_archive(self, sample_archive, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['tarpeek', str(sample_archive)])
        result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert "file0.txt" in captured.out or "file1.txt" in captured.out
        assert "Type" in captured.out or "type" in captured.out

    def test_main_with_nonexistent_archive(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['tarpeek', '/nonexistent/archive.tar'])
        result = main()
        captured = capsys.readouterr()
        assert result == 1
        assert "Error" in captured.err or "not found" in captured.err

    def test_main_with_invalid_tar(self, temp_dir, monkeypatch, capsys):
        bad_archive = temp_dir / "notatar.tar"
        bad_archive.write_text("Not a tar file")
        monkeypatch.setattr(sys, 'argv', ['tarpeek', str(bad_archive)])
        result = main()
        captured = capsys.readouterr()
        assert result == 1
        assert "Error" in captured.err

    def test_main_with_json_output(self, sample_archive, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['tarpeek', '--json', str(sample_archive)])
        result = main()
        captured = capsys.readouterr()
        assert result == 0
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(set(item.keys()) == {"name", "type", "size", "modified"} for item in data)

    def test_main_with_min_size(self, sample_archive, monkeypatch, capsys):
        monkeypatch.setattr(
            sys, 'argv',
            ['tarpeek', '--min-size', '1000', str(sample_archive)]
        )
        result = main()
        captured = capsys.readouterr()
        assert result == 1
        assert "Error" in captured.err

    def test_main_empty_archive(self, temp_dir, monkeypatch, capsys):
        empty_archive = temp_dir / "empty.tar"
        with tarfile.open(empty_archive, "w") as tar:
            pass
        monkeypatch.setattr(sys, 'argv', ['tarpeek', str(empty_archive)])
        result = main()
        captured = capsys.readouterr()
        assert result == 1
        assert "empty" in captured.err.lower()

    def test_main_sorted_by_size_descending(self, sample_archive, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['tarpeek', '--json', str(sample_archive)])
        result = main()
        captured = capsys.readouterr()
        assert result == 0
        data = json.loads(captured.out)
        sizes = [item["size"] for item in data]
        assert sizes == sorted(sizes, reverse=True)
