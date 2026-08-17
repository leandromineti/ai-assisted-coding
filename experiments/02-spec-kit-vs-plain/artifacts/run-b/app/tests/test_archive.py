"""Tests for member classification, mtime conversion, sorting, and empty-archive detection."""

import io
import tarfile
from datetime import datetime, timezone

import pytest

from tarpeek.archive import (
    ArchiveMember,
    EmptyArchiveError,
    _member_from_tarinfo,
    filter_by_min_size,
    read_archive,
    sort_members,
)


def _tarinfo(name, type_flag, size=0, mtime=0, linkname=None):
    info = tarfile.TarInfo(name=name)
    info.type = type_flag
    info.size = size
    info.mtime = mtime
    if linkname:
        info.linkname = linkname
    return info


def _write_tar(path, entries):
    """entries: list of (name, type_flag, size, mtime, content)"""
    with tarfile.open(path, "w") as tar:
        for name, type_flag, size, mtime, content in entries:
            info = _tarinfo(name, type_flag, size=size, mtime=mtime)
            if type_flag == tarfile.REGTYPE:
                tar.addfile(info, io.BytesIO(content))
            else:
                tar.addfile(info)


# --- T007: type classification + mtime conversion ---


def test_member_from_tarinfo_classifies_file():
    member = _member_from_tarinfo(_tarinfo("a.txt", tarfile.REGTYPE, size=10))
    assert member.name == "a.txt"
    assert member.type == "file"
    assert member.size == 10


def test_member_from_tarinfo_classifies_dir():
    member = _member_from_tarinfo(_tarinfo("adir", tarfile.DIRTYPE))
    assert member.type == "dir"


def test_member_from_tarinfo_classifies_symlink():
    member = _member_from_tarinfo(_tarinfo("link", tarfile.SYMTYPE, linkname="a.txt"))
    assert member.type == "symlink"


def test_member_from_tarinfo_classifies_other_as_fallback():
    member = _member_from_tarinfo(_tarinfo("dev0", tarfile.CHRTYPE))
    assert member.type == "other"


def test_member_from_tarinfo_converts_mtime_to_utc_iso8601():
    epoch = int(datetime(2026, 8, 10, 9, 15, 0, tzinfo=timezone.utc).timestamp())
    member = _member_from_tarinfo(_tarinfo("f", tarfile.REGTYPE, mtime=epoch))
    assert member.last_modified == "2026-08-10T09:15:00Z"


# --- T008: sort order + empty-archive detection ---


def test_sort_members_by_size_desc_then_name_asc():
    members = [
        ArchiveMember(name="b", type="file", size=10, last_modified="x"),
        ArchiveMember(name="a", type="file", size=10, last_modified="x"),
        ArchiveMember(name="c", type="file", size=20, last_modified="x"),
    ]
    result = sort_members(members)
    assert [m.name for m in result] == ["c", "a", "b"]


def test_read_archive_raises_on_empty_archive(tmp_path):
    path = str(tmp_path / "empty.tar")
    _write_tar(path, [])
    with pytest.raises(EmptyArchiveError):
        read_archive(path)


def test_read_archive_returns_members_for_non_empty_archive(tmp_path):
    path = str(tmp_path / "demo.tar")
    _write_tar(path, [("a.txt", tarfile.REGTYPE, 5, 0, b"hello")])
    members = read_archive(path)
    assert len(members) == 1
    assert members[0].name == "a.txt"


# --- T018: filter_by_min_size ---


def _members(*sizes):
    return [ArchiveMember(name=f"m{i}", type="file", size=s, last_modified="x") for i, s in enumerate(sizes)]


def test_filter_by_min_size_excludes_members_below_threshold():
    members = _members(1, 5, 10)
    result = filter_by_min_size(members, 5)
    assert sorted(m.size for m in result) == [5, 10]


def test_filter_by_min_size_includes_members_at_threshold():
    members = _members(5)
    result = filter_by_min_size(members, 5)
    assert len(result) == 1


def test_filter_by_min_size_returns_empty_list_without_raising():
    members = _members(1, 2, 3)
    result = filter_by_min_size(members, 1000)
    assert result == []
