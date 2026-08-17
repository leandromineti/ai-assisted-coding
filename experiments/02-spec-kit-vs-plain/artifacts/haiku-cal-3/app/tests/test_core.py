import pytest
import tarfile
import tempfile
import json
from pathlib import Path
from datetime import datetime

from tarpeek.core import ArchiveReader, TarPeekError


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def simple_archive(temp_dir):
    archive_path = temp_dir / "test.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        import io
        content = b"Hello, World!"
        tarinfo = tarfile.TarInfo(name="file.txt")
        tarinfo.size = len(content)
        tar.addfile(tarinfo, io.BytesIO(content))

        content2 = b"Another file"
        tarinfo2 = tarfile.TarInfo(name="subdir/file2.txt")
        tarinfo2.size = len(content2)
        tar.addfile(tarinfo2, io.BytesIO(content2))
    return archive_path


@pytest.fixture
def archive_with_dir(temp_dir):
    archive_path = temp_dir / "test_dir.tar"
    with tarfile.open(archive_path, "w") as tar:
        tarinfo = tarfile.TarInfo(name="mydir")
        tarinfo.type = tarfile.DIRTYPE
        tar.addfile(tarinfo)

        import io
        content = b"File in dir"
        tarinfo2 = tarfile.TarInfo(name="mydir/file.txt")
        tarinfo2.size = len(content)
        tar.addfile(tarinfo2, io.BytesIO(content))
    return archive_path


@pytest.fixture
def archive_with_symlink(temp_dir):
    archive_path = temp_dir / "test_symlink.tar"
    with tarfile.open(archive_path, "w") as tar:
        tarinfo = tarfile.TarInfo(name="link.txt")
        tarinfo.type = tarfile.SYMTYPE
        tarinfo.linkname = "target.txt"
        tar.addfile(tarinfo)
    return archive_path


@pytest.fixture
def empty_archive(temp_dir):
    archive_path = temp_dir / "empty.tar"
    with tarfile.open(archive_path, "w") as tar:
        pass
    return archive_path


class TestArchiveReader:
    def test_read_simple_archive(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members()
        assert len(members) == 2
        assert members[0].name in ["file.txt", "subdir/file2.txt"]
        assert members[0].type == "file"

    def test_member_types(self, archive_with_dir, archive_with_symlink):
        reader_dir = ArchiveReader(str(archive_with_dir))
        members = reader_dir.read_members()
        assert any(m.type == "dir" for m in members)
        assert any(m.type == "file" for m in members)

        reader_symlink = ArchiveReader(str(archive_with_symlink))
        members = reader_symlink.read_members()
        assert any(m.type == "symlink" for m in members)

    def test_size_sorting(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members()
        sorted_members = reader.sort_by_size(members)
        sizes = [m.size for m in sorted_members]
        assert sizes == sorted(sizes, reverse=True)

    def test_min_size_filter(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        with pytest.raises(TarPeekError, match="No members match filter"):
            reader.read_members(min_size=50)

    def test_min_size_filter_partial(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members(min_size=10)
        assert len(members) == 2

    def test_invalid_path(self):
        with pytest.raises(TarPeekError, match="Archive not found"):
            ArchiveReader("/nonexistent/archive.tar")

    def test_invalid_tar_file(self, temp_dir):
        not_tar = temp_dir / "notatar.tar"
        not_tar.write_text("This is not a tar file")
        with pytest.raises(TarPeekError, match="Invalid tar archive"):
            reader = ArchiveReader(str(not_tar))
            reader.read_members()

    def test_empty_archive(self, empty_archive):
        reader = ArchiveReader(str(empty_archive))
        with pytest.raises(TarPeekError, match="Archive is empty"):
            reader.read_members()

    def test_member_modified_timestamp(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members()
        for member in members:
            datetime.fromisoformat(member.modified)

    def test_no_writes_to_filesystem(self, simple_archive, temp_dir):
        original_files = set(temp_dir.iterdir())
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members()
        current_files = set(temp_dir.iterdir())
        assert original_files == current_files

    def test_member_to_dict(self, simple_archive):
        reader = ArchiveReader(str(simple_archive))
        members = reader.read_members()
        member_dict = members[0].to_dict()
        assert set(member_dict.keys()) == {"name", "type", "size", "modified"}
        assert isinstance(member_dict["name"], str)
        assert isinstance(member_dict["type"], str)
        assert isinstance(member_dict["size"], int)
        assert isinstance(member_dict["modified"], str)
