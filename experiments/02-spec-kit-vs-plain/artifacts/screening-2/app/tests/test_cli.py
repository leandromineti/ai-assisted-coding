import io
import json
import tarfile
from pathlib import Path

import pytest

from tarpeek.cli import (
    EXIT_EMPTY_ARCHIVE,
    EXIT_INVALID_ARCHIVE,
    EXIT_NOT_FOUND,
    EXIT_OK,
    main,
)


def _add_file(tar: tarfile.TarFile, name: str, size: int, mtime: int) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = size
    info.mtime = mtime
    info.type = tarfile.REGTYPE
    tar.addfile(info, fileobj=io.BytesIO(b"\0" * size))


def _add_dir(tar: tarfile.TarFile, name: str, mtime: int) -> None:
    info = tarfile.TarInfo(name=name)
    info.type = tarfile.DIRTYPE
    info.mtime = mtime
    tar.addfile(info)


def _add_symlink(tar: tarfile.TarFile, name: str, target: str, mtime: int) -> None:
    info = tarfile.TarInfo(name=name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    info.mtime = mtime
    tar.addfile(info)


@pytest.fixture
def sample_archive(tmp_path: Path) -> Path:
    archive_path = tmp_path / "sample.tar"
    with tarfile.open(archive_path, "w") as tar:
        _add_dir(tar, "docs", mtime=1_600_000_000)
        _add_file(tar, "small.txt", size=10, mtime=1_600_000_100)
        _add_file(tar, "big.bin", size=5000, mtime=1_600_000_200)
        _add_symlink(tar, "link", target="small.txt", mtime=1_600_000_300)
    return archive_path


@pytest.fixture
def empty_archive(tmp_path: Path) -> Path:
    archive_path = tmp_path / "empty.tar"
    with tarfile.open(archive_path, "w"):
        pass
    return archive_path


@pytest.fixture
def not_a_tar(tmp_path: Path) -> Path:
    path = tmp_path / "not_a_tar.txt"
    path.write_text("just some text, not a tar archive")
    return path


def test_table_output_sorted_by_size_desc(sample_archive, capsys):
    exit_code = main([str(sample_archive)])
    out = capsys.readouterr().out
    assert exit_code == EXIT_OK

    lines = out.strip().splitlines()
    header_idx = 0
    data_lines = lines[header_idx + 2 :]  # skip header + separator
    names_in_order = [line.split()[0] for line in data_lines]
    assert names_in_order == ["big.bin", "small.txt", "docs", "link"]


def test_json_output_structure(sample_archive, capsys):
    exit_code = main([str(sample_archive), "--json"])
    out = capsys.readouterr().out
    assert exit_code == EXIT_OK

    data = json.loads(out)
    assert [m["name"] for m in data] == ["big.bin", "small.txt", "docs", "link"]

    by_name = {m["name"]: m for m in data}
    assert by_name["docs"]["type"] == "dir"
    assert by_name["small.txt"]["type"] == "file"
    assert by_name["link"]["type"] == "symlink"
    assert by_name["big.bin"]["size"] == 5000
    assert by_name["docs"]["modified"] == "2020-09-13 12:26:40"


def test_min_size_filters_members(sample_archive, capsys):
    exit_code = main([str(sample_archive), "--min-size", "100", "--json"])
    out = capsys.readouterr().out
    assert exit_code == EXIT_OK

    data = json.loads(out)
    assert [m["name"] for m in data] == ["big.bin"]


def test_min_size_that_matches_nothing_is_not_an_error(sample_archive, capsys):
    exit_code = main([str(sample_archive), "--min-size", "999999"])
    out = capsys.readouterr().out
    assert exit_code == EXIT_OK
    assert "No members match" in out


def test_nonexistent_path_errors(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.tar"
    exit_code = main([str(missing)])
    err = capsys.readouterr().err
    assert exit_code == EXIT_NOT_FOUND
    assert "no such file" in err


def test_not_a_tar_archive_errors(not_a_tar, capsys):
    exit_code = main([str(not_a_tar)])
    err = capsys.readouterr().err
    assert exit_code == EXIT_INVALID_ARCHIVE
    assert "not a valid tar archive" in err


def test_empty_archive_errors(empty_archive, capsys):
    exit_code = main([str(empty_archive)])
    err = capsys.readouterr().err
    assert exit_code == EXIT_EMPTY_ARCHIVE
    assert "archive is empty" in err


def test_never_writes_to_filesystem(sample_archive, tmp_path, capsys):
    before = sorted(p.name for p in tmp_path.iterdir())
    main([str(sample_archive), "--json"])
    capsys.readouterr()
    after = sorted(p.name for p in tmp_path.iterdir())
    assert before == after


def test_directory_path_errors(tmp_path, capsys):
    exit_code = main([str(tmp_path)])
    err = capsys.readouterr().err
    assert exit_code == EXIT_NOT_FOUND
    assert "not a file" in err
