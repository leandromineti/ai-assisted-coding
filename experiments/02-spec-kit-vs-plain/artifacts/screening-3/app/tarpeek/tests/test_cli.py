import io
import json
import os
import tarfile

import pytest

from tarpeek.cli import main


def make_tar(path, entries):
    """entries: list of (name, kind, content_or_target) where kind in
    'file', 'dir', 'symlink'."""
    with tarfile.open(path, mode="w") as tf:
        for name, kind, payload in entries:
            info = tarfile.TarInfo(name=name)
            info.mtime = 1_700_000_000
            if kind == "file":
                data = payload.encode()
                info.size = len(data)
                info.type = tarfile.REGTYPE
                tf.addfile(info, io.BytesIO(data))
            elif kind == "dir":
                info.type = tarfile.DIRTYPE
                tf.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = payload
                tf.addfile(info)
            else:
                raise ValueError(kind)


@pytest.fixture
def sample_tar(tmp_path):
    path = tmp_path / "sample.tar"
    make_tar(
        path,
        [
            ("small.txt", "file", "hi"),
            ("big.txt", "file", "x" * 1000),
            ("mydir", "dir", None),
            ("link.txt", "symlink", "big.txt"),
        ],
    )
    return str(path)


def snapshot_fs(root):
    """Return a set of all paths under root, recursively, for before/after comparisons."""
    found = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            found.add(os.path.relpath(os.path.join(dirpath, name), root))
    return found


def test_table_output_sorted_by_size_desc(sample_tar, capsys):
    code = main([sample_tar])
    assert code == 0
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if l and not l.startswith("-") and "NAME" not in l]
    names_in_order = [l.split()[0] for l in lines]
    assert names_in_order.index("big.txt") < names_in_order.index("small.txt")


def test_json_output_structure(sample_tar, capsys):
    code = main([sample_tar, "--json"])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 4
    sizes = [d["size"] for d in data]
    assert sizes == sorted(sizes, reverse=True)
    types = {d["type"] for d in data}
    assert types == {"file", "dir", "symlink"}
    for entry in data:
        assert set(entry.keys()) == {"name", "type", "size", "mtime"}


def test_min_size_filter(sample_tar, capsys):
    code = main([sample_tar, "--min-size", "500", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["name"] == "big.txt"


def test_min_size_filters_everything_is_not_an_error(sample_tar, capsys):
    code = main([sample_tar, "--min-size", "999999", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data == []


def test_negative_min_size_rejected(sample_tar, capsys):
    code = main([sample_tar, "--min-size", "-5"])
    assert code != 0
    err = capsys.readouterr().err
    assert "min-size" in err


def test_missing_file(tmp_path, capsys):
    missing = str(tmp_path / "does-not-exist.tar")
    code = main([missing])
    assert code != 0
    err = capsys.readouterr().err
    assert "not found" in err.lower()


def test_not_a_tar_archive(tmp_path, capsys):
    bogus = tmp_path / "notatar.tar"
    bogus.write_text("this is definitely not a tar file, just plain text padding")
    code = main([str(bogus)])
    assert code != 0
    err = capsys.readouterr().err
    assert "not a valid tar archive" in err.lower()


def test_empty_archive(tmp_path, capsys):
    empty = tmp_path / "empty.tar"
    with tarfile.open(empty, mode="w"):
        pass
    code = main([str(empty)])
    assert code != 0
    err = capsys.readouterr().err
    assert "empty" in err.lower()


def test_directory_given_instead_of_file(tmp_path, capsys):
    code = main([str(tmp_path)])
    assert code != 0
    err = capsys.readouterr().err
    assert "directory" in err.lower() or "not a valid tar archive" in err.lower()


def test_never_writes_to_filesystem(sample_tar, tmp_path):
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    before = snapshot_fs(str(tmp_path))
    cwd = os.getcwd()
    os.chdir(workdir)
    try:
        main([sample_tar, "--json"])
        main([sample_tar])
    finally:
        os.chdir(cwd)
    after = snapshot_fs(str(tmp_path))
    assert before == after


def test_different_exit_codes_for_different_failures(tmp_path):
    missing_code = main([str(tmp_path / "nope.tar")])

    bogus = tmp_path / "bogus.tar"
    bogus.write_text("not a tar file at all")
    invalid_code = main([str(bogus)])

    empty = tmp_path / "empty2.tar"
    with tarfile.open(empty, mode="w"):
        pass
    empty_code = main([str(empty)])

    assert missing_code != 0
    assert invalid_code != 0
    assert empty_code != 0
    assert len({missing_code, invalid_code, empty_code}) == 3
