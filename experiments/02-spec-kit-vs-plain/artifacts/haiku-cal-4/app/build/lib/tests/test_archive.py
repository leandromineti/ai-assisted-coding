import pytest
import tarfile
import tempfile
import os
import json
from datetime import datetime
from tarpeek.archive import TarArchive, TarMember


@pytest.fixture
def simple_tar(tmp_path):
    """Create a simple tar archive with a few members."""
    tar_path = tmp_path / "simple.tar"
    with tarfile.open(tar_path, "w") as tar:
        # Add a file
        tar.add(__file__, arcname="test_file.py")
    return tar_path


@pytest.fixture
def complex_tar(tmp_path):
    """Create a tar archive with files, dirs, and symlinks."""
    tar_path = tmp_path / "complex.tar"

    # Create some temporary files/dirs to archive
    test_dir = tmp_path / "test_contents"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("hello")
    (test_dir / "file2.txt").write_text("world" * 100)
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("nested")

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


class TestTarArchive:
    def test_read_simple_tar(self, simple_tar):
        archive = TarArchive(str(simple_tar))
        assert len(archive.members) > 0
        assert all(hasattr(m, "name") for m in archive.members)
        assert all(hasattr(m, "type") for m in archive.members)
        assert all(hasattr(m, "size") for m in archive.members)
        assert all(hasattr(m, "mtime") for m in archive.members)

    def test_member_types(self, complex_tar):
        archive = TarArchive(str(complex_tar))
        types = {m.type for m in archive.members}
        # Should have at least files and dirs
        assert "file" in types or "dir" in types

    def test_filter_by_min_size(self, complex_tar):
        archive = TarArchive(str(complex_tar))
        min_100 = archive.filter_by_min_size(100)
        assert all(m.size >= 100 for m in min_100)

    def test_filter_empty_result(self, complex_tar):
        archive = TarArchive(str(complex_tar))
        # Filter for a very large size unlikely to be in the archive
        very_large = archive.filter_by_min_size(999999999)
        assert len(very_large) == 0

    def test_sort_by_size_descending(self, complex_tar):
        archive = TarArchive(str(complex_tar))
        sorted_members = archive.sort_by_size()
        sizes = [m.size for m in sorted_members]
        assert sizes == sorted(sizes, reverse=True)

    def test_to_json(self, simple_tar):
        archive = TarArchive(str(simple_tar))
        members = archive.sort_by_size()
        json_str = archive.to_json(members)
        data = json.loads(json_str)
        assert isinstance(data, list)
        assert len(data) == len(members)
        for item in data:
            assert "name" in item
            assert "type" in item
            assert "size" in item
            assert "mtime" in item

    def test_tar_member_to_dict(self):
        member = TarMember("test.txt", "file", 1024, 1609459200)
        d = member.to_dict()
        assert d["name"] == "test.txt"
        assert d["type"] == "file"
        assert d["size"] == 1024
        assert "mtime" in d
        # Verify mtime is ISO format
        datetime.fromisoformat(d["mtime"])

    def test_invalid_tar_raises_value_error(self, tmp_path):
        invalid_tar = tmp_path / "invalid.tar"
        invalid_tar.write_text("not a tar file")
        with pytest.raises(ValueError, match="Not a valid tar archive"):
            TarArchive(str(invalid_tar))

    def test_missing_file_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Archive not found"):
            TarArchive("/nonexistent/path/to/archive.tar")

    def test_empty_archive(self, empty_tar):
        archive = TarArchive(str(empty_tar))
        assert len(archive.members) == 0


class TestTarMember:
    def test_member_init(self):
        member = TarMember("test.txt", "file", 512, 1234567890)
        assert member.name == "test.txt"
        assert member.type == "file"
        assert member.size == 512
        assert member.mtime == 1234567890

    def test_member_types(self):
        file_member = TarMember("file.txt", "file", 100, 0)
        assert file_member.type == "file"

        dir_member = TarMember("mydir/", "dir", 0, 0)
        assert dir_member.type == "dir"

        symlink_member = TarMember("link", "symlink", 0, 0)
        assert symlink_member.type == "symlink"
