import os
import tarfile
import time

import pytest

from tarpeek.core import ArchiveEmptyError, InvalidArchiveError, iter_members


def _add_file(tar, name, content=b"", mtime=None):
    data = content
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mtime = mtime if mtime is not None else int(time.time())
    tar.addfile(info, fileobj=__import__("io").BytesIO(data))


def _add_dir(tar, name, mtime=None):
    info = tarfile.TarInfo(name=name)
    info.type = tarfile.DIRTYPE
    info.mtime = mtime if mtime is not None else int(time.time())
    tar.addfile(info)


def _add_symlink(tar, name, target, mtime=None):
    info = tarfile.TarInfo(name=name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    info.mtime = mtime if mtime is not None else int(time.time())
    tar.addfile(info)


def make_tar(path, builder):
    with tarfile.open(path, "w") as tar:
        builder(tar)
    return path


def test_iter_members_reports_name_type_size_mtime(tmp_path):
    archive = tmp_path / "sample.tar"

    def build(tar):
        _add_file(tar, "small.txt", b"hi", mtime=1_700_000_000)
        _add_dir(tar, "adir", mtime=1_700_000_000)
        _add_symlink(tar, "alink", "small.txt", mtime=1_700_000_000)

    make_tar(archive, build)

    infos = iter_members(str(archive))
    by_name = {info.name: info for info in infos}

    assert by_name["small.txt"].type == "file"
    assert by_name["small.txt"].size == 2
    assert by_name["adir"].type == "dir"
    assert by_name["alink"].type == "symlink"
    assert by_name["small.txt"].mtime.year == 2023


def test_iter_members_sorted_by_size_descending(tmp_path):
    archive = tmp_path / "sizes.tar"

    def build(tar):
        _add_file(tar, "tiny", b"a")
        _add_file(tar, "big", b"a" * 1000)
        _add_file(tar, "medium", b"a" * 50)

    make_tar(archive, build)

    infos = iter_members(str(archive))
    assert [info.name for info in infos] == ["big", "medium", "tiny"]


def test_min_size_filters_members(tmp_path):
    archive = tmp_path / "sizes.tar"

    def build(tar):
        _add_file(tar, "tiny", b"a")
        _add_file(tar, "big", b"a" * 1000)

    make_tar(archive, build)

    infos = iter_members(str(archive), min_size=100)
    assert [info.name for info in infos] == ["big"]


def test_nonexistent_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        iter_members(str(tmp_path / "does-not-exist.tar"))


def test_non_tar_file_raises_invalid_archive_error(tmp_path):
    not_a_tar = tmp_path / "notatar.txt"
    not_a_tar.write_text("just some plain text, definitely not a tar file")

    with pytest.raises(InvalidArchiveError):
        iter_members(str(not_a_tar))


def test_empty_archive_raises_archive_empty_error(tmp_path):
    archive = tmp_path / "empty.tar"
    with tarfile.open(archive, "w"):
        pass  # no members added

    with pytest.raises(ArchiveEmptyError):
        iter_members(str(archive))


def test_directory_path_raises_is_a_directory_error(tmp_path):
    with pytest.raises(IsADirectoryError):
        iter_members(str(tmp_path))


def test_never_writes_to_filesystem(tmp_path):
    archive = tmp_path / "sample.tar"

    def build(tar):
        _add_file(tar, "file.txt", b"contents")

    make_tar(archive, build)

    before = set(os.listdir(tmp_path))
    iter_members(str(archive))
    after = set(os.listdir(tmp_path))

    assert before == after
