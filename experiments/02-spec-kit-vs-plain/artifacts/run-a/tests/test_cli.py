import io
import json
import os
import tarfile

import pytest

from tarpeek import cli, core


def make_tar(path, members):
    """Build a tar file at `path`.

    `members` is a list of (name, kind, content_or_target) tuples where kind
    is one of 'file', 'dir', 'symlink'.
    """
    with tarfile.open(path, "w") as tf:
        for name, kind, extra in members:
            if kind == "file":
                data = extra.encode()
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
            elif kind == "dir":
                info = tarfile.TarInfo(name=name)
                info.type = tarfile.DIRTYPE
                tf.addfile(info)
            elif kind == "symlink":
                info = tarfile.TarInfo(name=name)
                info.type = tarfile.SYMTYPE
                info.linkname = extra
                tf.addfile(info)


@pytest.fixture
def sample_tar(tmp_path):
    path = tmp_path / "sample.tar"
    make_tar(
        str(path),
        [
            ("small.txt", "file", "hi"),
            ("big.txt", "file", "x" * 1000),
            ("a_dir", "dir", None),
            ("link_to_big", "symlink", "big.txt"),
        ],
    )
    return str(path)


@pytest.fixture
def empty_tar(tmp_path):
    path = tmp_path / "empty.tar"
    with tarfile.open(str(path), "w"):
        pass
    return str(path)


@pytest.fixture
def not_a_tar(tmp_path):
    path = tmp_path / "notatar.txt"
    path.write_text("just some plain text, not a tar archive")
    return str(path)


# --- core.read_members ---


def test_read_members_returns_expected_metadata(sample_tar):
    members = core.read_members(sample_tar)
    by_name = {m["name"]: m for m in members}

    assert by_name["small.txt"]["type"] == "file"
    assert by_name["small.txt"]["size"] == 2

    assert by_name["big.txt"]["type"] == "file"
    assert by_name["big.txt"]["size"] == 1000

    assert by_name["a_dir"]["type"] == "dir"
    assert by_name["a_dir"]["size"] == 0

    assert by_name["link_to_big"]["type"] == "symlink"


def test_read_members_missing_file_raises(tmp_path):
    missing = str(tmp_path / "does_not_exist.tar")
    with pytest.raises(FileNotFoundError):
        core.read_members(missing)


def test_read_members_not_a_tar_raises(not_a_tar):
    with pytest.raises(core.NotATarFileError):
        core.read_members(not_a_tar)


def test_read_members_empty_archive_raises(empty_tar):
    with pytest.raises(core.EmptyArchiveError):
        core.read_members(empty_tar)


# --- core.filter_and_sort ---


def test_filter_and_sort_sorts_by_size_descending(sample_tar):
    members = core.read_members(sample_tar)
    result = core.filter_and_sort(members)
    sizes = [m["size"] for m in result]
    assert sizes == sorted(sizes, reverse=True)


def test_filter_and_sort_min_size(sample_tar):
    members = core.read_members(sample_tar)
    result = core.filter_and_sort(members, min_size=500)
    assert all(m["size"] >= 500 for m in result)
    assert {m["name"] for m in result} == {"big.txt"}


# --- cli.main exit codes and output ---


def test_cli_success_table_output(sample_tar, capsys):
    exit_code = cli.main([sample_tar])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_OK
    assert "big.txt" in captured.out
    assert "NAME" in captured.out and "SIZE" in captured.out


def test_cli_json_output(sample_tar, capsys):
    exit_code = cli.main([sample_tar, "--json"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_OK

    data = json.loads(captured.out)
    names = [m["name"] for m in data]
    assert "big.txt" in names
    sizes = [m["size"] for m in data]
    assert sizes == sorted(sizes, reverse=True)


def test_cli_min_size_filters(sample_tar, capsys):
    exit_code = cli.main([sample_tar, "--min-size", "500", "--json"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_OK
    data = json.loads(captured.out)
    assert [m["name"] for m in data] == ["big.txt"]


def test_cli_missing_file_errors(tmp_path, capsys):
    missing = str(tmp_path / "nope.tar")
    exit_code = cli.main([missing])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_NOT_FOUND
    assert "error" in captured.err.lower()


def test_cli_not_a_tar_errors(not_a_tar, capsys):
    exit_code = cli.main([not_a_tar])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_NOT_TAR
    assert "error" in captured.err.lower()


def test_cli_empty_archive_errors(empty_tar, capsys):
    exit_code = cli.main([empty_tar])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_EMPTY
    assert "error" in captured.err.lower()


def test_cli_never_writes_to_filesystem(sample_tar, tmp_path, capsys):
    before = set(os.listdir(tmp_path))
    cli.main([sample_tar])
    cli.main([sample_tar, "--json"])
    after = set(os.listdir(tmp_path))
    assert before == after
