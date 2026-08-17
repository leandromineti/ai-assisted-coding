import json
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from io import BytesIO

import pytest

from tarpeek.cli import summarize_archive, format_table, get_member_type


@pytest.fixture
def sample_tar(tmp_path):
    """Create a sample tar archive for testing."""
    archive_path = tmp_path / "sample.tar"

    with tarfile.open(archive_path, "w") as tar:
        # Add a file
        info = tarfile.TarInfo(name="file.txt")
        info.size = 100
        info.mtime = 1692374400  # 2023-08-18
        tar.addfile(info, BytesIO(b"x" * 100))

        # Add a directory
        info = tarfile.TarInfo(name="mydir/")
        info.type = tarfile.DIRTYPE
        info.mtime = 1692374400
        tar.addfile(info)

        # Add a larger file
        info = tarfile.TarInfo(name="bigfile.bin")
        info.size = 5000
        info.mtime = 1692288000  # 2023-08-17
        tar.addfile(info, BytesIO(b"y" * 5000))

        # Add a symlink
        info = tarfile.TarInfo(name="link")
        info.type = tarfile.SYMTYPE
        info.linkname = "file.txt"
        info.mtime = 1692374400
        tar.addfile(info)

    return archive_path


@pytest.fixture
def empty_tar(tmp_path):
    """Create an empty tar archive."""
    archive_path = tmp_path / "empty.tar"
    with tarfile.open(archive_path, "w") as tar:
        pass
    return archive_path


@pytest.fixture
def not_tar(tmp_path):
    """Create a non-tar file."""
    archive_path = tmp_path / "not_tar.txt"
    archive_path.write_text("This is not a tar archive")
    return archive_path


def test_summarize_archive(sample_tar):
    """Test basic archive summarization."""
    members = summarize_archive(sample_tar)

    assert len(members) == 4
    assert all("name" in m and "type" in m and "size" in m and "modified" in m for m in members)


def test_summarize_archive_sorted_by_size(sample_tar):
    """Test that results are sorted by size descending."""
    members = summarize_archive(sample_tar)

    sizes = [m["size"] for m in members]
    assert sizes == sorted(sizes, reverse=True)

    # bigfile.bin (5000) should be first
    assert members[0]["name"] == "bigfile.bin"
    assert members[0]["size"] == 5000


def test_summarize_archive_member_types(sample_tar):
    """Test member type detection."""
    members = summarize_archive(sample_tar)
    members_by_name = {m["name"]: m for m in members}

    assert members_by_name["file.txt"]["type"] == "file"
    # Directory may be stored as "mydir/" or "mydir" depending on tar implementation
    assert any(m["type"] == "dir" for m in members)
    assert members_by_name["bigfile.bin"]["type"] == "file"
    assert members_by_name["link"]["type"] == "symlink"


def test_min_size_filter(sample_tar):
    """Test --min-size filtering."""
    members = summarize_archive(sample_tar, min_size=1000)

    # Only bigfile.bin (5000) and file.txt (100) won't qualify; only bigfile qualifies
    assert len(members) == 1
    assert members[0]["name"] == "bigfile.bin"


def test_empty_archive(empty_tar):
    """Test that empty archive raises ValueError."""
    with pytest.raises(ValueError, match="Archive is empty"):
        summarize_archive(empty_tar)


def test_not_tar_archive(not_tar):
    """Test that non-tar file raises ValueError."""
    with pytest.raises(ValueError, match="Not a valid tar archive"):
        summarize_archive(not_tar)


def test_nonexistent_file(tmp_path):
    """Test that nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        summarize_archive(tmp_path / "nonexistent.tar")


def test_format_table(sample_tar, capsys):
    """Test table formatting."""
    members = summarize_archive(sample_tar)
    format_table(members)

    captured = capsys.readouterr()
    output = captured.out

    assert "Name" in output
    assert "Type" in output
    assert "Size" in output
    assert "Modified" in output
    assert "bigfile.bin" in output
    assert "file.txt" in output
    assert "mydir" in output  # May be stored as mydir or mydir/
    assert "link" in output


def test_format_table_empty(capsys):
    """Test table formatting with no members."""
    format_table([])

    captured = capsys.readouterr()
    assert "No members match the filter" in captured.out


def test_modified_timestamp_format(sample_tar):
    """Test that modified timestamp is in ISO format."""
    members = summarize_archive(sample_tar)

    for member in members:
        # Should parse as valid ISO format
        datetime.fromisoformat(member["modified"])


def test_get_member_type():
    """Test member type detection function."""
    # Create mock members
    file_member = tarfile.TarInfo("file.txt")
    file_member.type = tarfile.REGTYPE
    assert get_member_type(file_member) == "file"

    dir_member = tarfile.TarInfo("dir/")
    dir_member.type = tarfile.DIRTYPE
    assert get_member_type(dir_member) == "dir"

    sym_member = tarfile.TarInfo("link")
    sym_member.type = tarfile.SYMTYPE
    assert get_member_type(sym_member) == "symlink"
