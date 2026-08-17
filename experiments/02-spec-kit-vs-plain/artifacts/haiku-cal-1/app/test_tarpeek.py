import json
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
import pytest


@pytest.fixture
def temp_archive():
    """Create a temporary tar archive with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test files and directories
        (tmpdir / "file1.txt").write_text("a" * 100)
        (tmpdir / "file2.txt").write_text("b" * 200)
        (tmpdir / "subdir").mkdir()
        (tmpdir / "subdir" / "file3.txt").write_text("c" * 50)

        archive_path = tmpdir / "test.tar.gz"

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(tmpdir / "file1.txt", arcname="file1.txt")
            tar.add(tmpdir / "file2.txt", arcname="file2.txt")
            tar.add(tmpdir / "subdir", arcname="subdir")
            tar.add(tmpdir / "subdir" / "file3.txt", arcname="subdir/file3.txt")

        yield str(archive_path)


@pytest.fixture
def empty_archive():
    """Create an empty tar archive."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        archive_path = tmpdir / "empty.tar.gz"

        with tarfile.open(archive_path, "w:gz") as tar:
            pass

        yield str(archive_path)


def test_read_archive_basic(temp_archive):
    """Test reading a valid tar archive."""
    result = subprocess.run(
        ["tarpeek", temp_archive],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "file1.txt" in result.stdout
    assert "file2.txt" in result.stdout
    assert "subdir" in result.stdout
    assert "file3.txt" in result.stdout


def test_read_archive_with_types(temp_archive):
    """Test that file types are correctly identified."""
    result = subprocess.run(
        ["tarpeek", temp_archive],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    assert "file" in output
    assert "dir" in output


def test_read_archive_sorted_by_size(temp_archive):
    """Test that members are sorted by size descending."""
    result = subprocess.run(
        ["tarpeek", temp_archive],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    lines = result.stdout.split("\n")

    file_lines = [l for l in lines if l and not l.startswith("-")]
    data_lines = file_lines[2:]

    sizes = []
    for line in data_lines:
        if line.strip():
            parts = line.split()
            if parts[1] == "file":
                size = int(parts[2])
                sizes.append(size)

    assert sizes == sorted(sizes, reverse=True)


def test_json_output(temp_archive):
    """Test JSON output format."""
    result = subprocess.run(
        ["tarpeek", temp_archive, "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0

    for item in data:
        assert "name" in item
        assert "type" in item
        assert "size" in item
        assert "mtime" in item


def test_min_size_filter(temp_archive):
    """Test --min-size filtering."""
    result = subprocess.run(
        ["tarpeek", temp_archive, "--min-size", "100"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    assert "file2.txt" in output
    assert "file1.txt" in output
    assert "file3.txt" not in output


def test_empty_archive_error(empty_archive):
    """Test handling of empty archives."""
    result = subprocess.run(
        ["tarpeek", empty_archive],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "empty" in result.stderr.lower()


def test_nonexistent_file():
    """Test handling of nonexistent file."""
    result = subprocess.run(
        ["tarpeek", "/nonexistent/path/to/archive.tar"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr.lower()


def test_invalid_tar_file():
    """Test handling of invalid tar file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        invalid_tar = tmpdir / "invalid.tar"
        invalid_tar.write_text("This is not a tar archive!")

        result = subprocess.run(
            ["tarpeek", str(invalid_tar)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "failed to read" in result.stderr.lower()


def test_min_size_all_filtered(temp_archive):
    """Test when all members are filtered by min-size."""
    result = subprocess.run(
        ["tarpeek", temp_archive, "--min-size", "10000"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "below minimum size" in result.stderr.lower()


def test_symlink_detection():
    """Test that symlinks are correctly identified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        (tmpdir / "file.txt").write_text("content")

        archive_path = tmpdir / "with_symlink.tar"

        with tarfile.open(archive_path, "w") as tar:
            tar.add(tmpdir / "file.txt", arcname="file.txt")

            symlink_info = tarfile.TarInfo(name="link.txt")
            symlink_info.type = tarfile.SYMTYPE
            symlink_info.linkname = "file.txt"
            tar.addfile(symlink_info)

        result = subprocess.run(
            ["tarpeek", str(archive_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "symlink" in result.stdout


def test_output_includes_mtime(temp_archive):
    """Test that modified time is included in output."""
    result = subprocess.run(
        ["tarpeek", temp_archive],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    assert "Modified" in output
    assert "-" in output
    assert ":" in output
