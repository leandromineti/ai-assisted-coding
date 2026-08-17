import pytest
import tarfile
import tempfile
import json
import subprocess
import sys
from pathlib import Path
from tarpeek.cli import main


@pytest.fixture
def simple_tar(tmp_path):
    """Create a simple tar archive."""
    tar_path = tmp_path / "simple.tar"
    with tarfile.open(tar_path, "w") as tar:
        # Add a file
        tar.add(__file__, arcname="test_file.py")
    return tar_path


@pytest.fixture
def complex_tar(tmp_path):
    """Create a tar with multiple files of different sizes."""
    tar_path = tmp_path / "complex.tar"
    test_dir = tmp_path / "test_contents"
    test_dir.mkdir()
    (test_dir / "small.txt").write_text("a")
    (test_dir / "medium.txt").write_text("b" * 1000)
    (test_dir / "large.txt").write_text("c" * 10000)

    with tarfile.open(tar_path, "w") as tar:
        tar.add(test_dir, arcname="contents")

    return tar_path


@pytest.fixture
def empty_tar(tmp_path):
    """Create an empty tar archive."""
    tar_path = tmp_path / "empty.tar"
    with tarfile.open(tar_path, "w") as tar:
        pass
    return tar_path


class TestCliMain:
    def test_cli_prints_table(self, simple_tar, capsys):
        sys.argv = ["tarpeek", str(simple_tar)]
        main()
        captured = capsys.readouterr()
        assert "Name" in captured.out or "test_file.py" in captured.out

    def test_cli_with_json_flag(self, simple_tar, capsys):
        sys.argv = ["tarpeek", str(simple_tar), "--json"]
        main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_cli_with_min_size_filter(self, complex_tar, capsys):
        sys.argv = ["tarpeek", str(complex_tar), "--min-size", "500"]
        main()
        captured = capsys.readouterr()
        # Should only show files >= 500 bytes
        assert "medium.txt" in captured.out or "large.txt" in captured.out

    def test_cli_with_min_size_json(self, complex_tar, capsys):
        sys.argv = ["tarpeek", str(complex_tar), "--min-size", "500", "--json"]
        main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert all(m["size"] >= 500 for m in data)

    def test_cli_invalid_tar_exits_with_error(self, tmp_path, capsys):
        invalid_tar = tmp_path / "invalid.tar"
        invalid_tar.write_text("not a tar")
        sys.argv = ["tarpeek", str(invalid_tar)]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_cli_missing_file_exits_with_error(self, capsys):
        sys.argv = ["tarpeek", "/nonexistent/archive.tar"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_cli_empty_archive_exits_with_error(self, empty_tar, capsys):
        sys.argv = ["tarpeek", str(empty_tar)]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "empty" in captured.err.lower()

    def test_cli_min_size_no_results(self, simple_tar, capsys):
        sys.argv = ["tarpeek", str(simple_tar), "--min-size", "999999999"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "No members found" in captured.err

    def test_cli_size_sorting(self, complex_tar, capsys):
        sys.argv = ["tarpeek", str(complex_tar), "--json"]
        main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        sizes = [m["size"] for m in data]
        assert sizes == sorted(sizes, reverse=True)
