import io
import json
import os
import tarfile

import pytest

from tarpeek.cli import main


def make_tar(path, members=()):
    """Build a tar archive at `path` from a list of (name, kind, content, size, mtime).

    kind is one of "file", "dir", "symlink".
    """
    with tarfile.open(path, mode="w") as tar:
        for name, kind, content, mtime in members:
            info = tarfile.TarInfo(name=name)
            info.mtime = mtime
            if kind == "file":
                data = content.encode()
                info.type = tarfile.REGTYPE
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            elif kind == "dir":
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = content
                tar.addfile(info)
            else:
                raise ValueError(kind)


@pytest.fixture
def sample_tar(tmp_path):
    archive = tmp_path / "sample.tar"
    make_tar(
        archive,
        members=[
            ("big.bin", "file", "x" * 1000, 1_700_000_000),
            ("small.txt", "file", "hi", 1_700_000_100),
            ("some_dir", "dir", "", 1_700_000_200),
            ("link_to_big", "symlink", "big.bin", 1_700_000_300),
        ],
    )
    return archive


def test_table_output_lists_all_members(sample_tar, capsys):
    code = main([str(sample_tar)])
    out = capsys.readouterr().out
    assert code == 0
    assert "big.bin" in out
    assert "small.txt" in out
    assert "some_dir" in out
    assert "link_to_big" in out


def test_member_types_detected(sample_tar, capsys):
    code = main([str(sample_tar), "--json"])
    rows = json.loads(capsys.readouterr().out)
    by_name = {row["name"]: row for row in rows}
    assert code == 0
    assert by_name["big.bin"]["type"] == "file"
    assert by_name["some_dir"]["type"] == "dir"
    assert by_name["link_to_big"]["type"] == "symlink"


def test_sizes_are_correct(sample_tar, capsys):
    main([str(sample_tar), "--json"])
    rows = json.loads(capsys.readouterr().out)
    by_name = {row["name"]: row for row in rows}
    assert by_name["big.bin"]["size"] == 1000
    assert by_name["small.txt"]["size"] == 2
    assert by_name["some_dir"]["size"] == 0


def test_sorted_by_size_descending(sample_tar, capsys):
    main([str(sample_tar), "--json"])
    rows = json.loads(capsys.readouterr().out)
    sizes = [row["size"] for row in rows]
    assert sizes == sorted(sizes, reverse=True)


def test_min_size_filters_members(sample_tar, capsys):
    code = main([str(sample_tar), "--min-size", "500", "--json"])
    rows = json.loads(capsys.readouterr().out)
    assert code == 0
    names = {row["name"] for row in rows}
    assert names == {"big.bin"}


def test_min_size_negative_is_rejected(sample_tar, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([str(sample_tar), "--min-size", "-5"])
    assert exc_info.value.code != 0


def test_json_output_is_valid_json(sample_tar, capsys):
    main([str(sample_tar), "--json"])
    out = capsys.readouterr().out
    rows = json.loads(out)
    assert isinstance(rows, list)
    assert all({"name", "type", "size", "modified"} <= row.keys() for row in rows)


def test_modified_date_present(sample_tar, capsys):
    main([str(sample_tar), "--json"])
    rows = json.loads(capsys.readouterr().out)
    for row in rows:
        assert row["modified"]  # non-empty string


def test_min_size_that_excludes_everything(sample_tar, capsys):
    code = main([str(sample_tar), "--min-size", "999999"])
    out = capsys.readouterr()
    assert code == 0
    assert "No members match" in out.out


def test_min_size_that_excludes_everything_json_stays_valid(sample_tar, capsys):
    code = main([str(sample_tar), "--min-size", "999999", "--json"])
    rows = json.loads(capsys.readouterr().out)
    assert code == 0
    assert rows == []


def test_not_a_tar_archive_errors(tmp_path, capsys):
    bogus = tmp_path / "not_a_tar.txt"
    bogus.write_text("just some plain text, definitely not a tar file")
    code = main([str(bogus)])
    captured = capsys.readouterr()
    assert code != 0
    assert "not a valid tar archive" in captured.err


def test_missing_file_errors(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.tar"
    code = main([str(missing)])
    captured = capsys.readouterr()
    assert code != 0
    assert "not found" in captured.err


def test_empty_archive_errors(tmp_path, capsys):
    archive = tmp_path / "empty.tar"
    make_tar(archive, members=[])
    code = main([str(archive)])
    captured = capsys.readouterr()
    assert code != 0
    assert "empty archive" in captured.err


def test_never_writes_to_filesystem(sample_tar, tmp_path, capsys):
    work_dir = tmp_path / "workdir"
    work_dir.mkdir()
    before = set(os.listdir(work_dir))

    cwd = os.getcwd()
    os.chdir(work_dir)
    try:
        main([str(sample_tar), "--json"])
        main([str(sample_tar)])
    finally:
        os.chdir(cwd)

    after = set(os.listdir(work_dir))
    assert before == after


def test_compressed_archive_supported(tmp_path, capsys):
    archive = tmp_path / "sample.tar.gz"
    with tarfile.open(archive, mode="w:gz") as tar:
        info = tarfile.TarInfo(name="hello.txt")
        data = b"hello world"
        info.size = len(data)
        info.mtime = 1_700_000_000
        tar.addfile(info, io.BytesIO(data))

    code = main([str(archive), "--json"])
    rows = json.loads(capsys.readouterr().out)
    assert code == 0
    assert rows[0]["name"] == "hello.txt"
    assert rows[0]["size"] == len(b"hello world")
