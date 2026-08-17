import io
import json
import os
import tarfile
import time

import pytest

from tarpeek.cli import inspect_archive, main, TarPeekError


def _add_file(tar, name, content=b"", mtime=None):
    info = tarfile.TarInfo(name=name)
    info.size = len(content)
    info.mtime = mtime if mtime is not None else int(time.time())
    info.type = tarfile.REGTYPE
    tar.addfile(info, io.BytesIO(content))


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


@pytest.fixture
def sample_archive(tmp_path):
    path = tmp_path / "sample.tar"
    with tarfile.open(path, mode="w") as tar:
        _add_dir(tar, "docs")
        _add_file(tar, "docs/big.txt", b"x" * 1000)
        _add_file(tar, "docs/small.txt", b"y" * 10)
        _add_symlink(tar, "link_to_big", "docs/big.txt")
    return path


@pytest.fixture
def empty_archive(tmp_path):
    path = tmp_path / "empty.tar"
    with tarfile.open(path, mode="w"):
        pass
    return path


def _listing(directory):
    return {
        os.path.relpath(os.path.join(root, name), directory)
        for root, dirs, files in os.walk(directory)
        for name in dirs + files
    }


class TestInspectArchive:
    def test_sorted_by_size_descending(self, sample_archive):
        rows = inspect_archive(str(sample_archive))
        sizes = [row["size"] for row in rows]
        assert sizes == sorted(sizes, reverse=True)

    def test_types_detected(self, sample_archive):
        rows = {row["name"]: row for row in inspect_archive(str(sample_archive))}
        assert rows["docs"]["type"] == "dir"
        assert rows["docs/big.txt"]["type"] == "file"
        assert rows["link_to_big"]["type"] == "symlink"

    def test_min_size_filters(self, sample_archive):
        rows = inspect_archive(str(sample_archive), min_size=100)
        names = {row["name"] for row in rows}
        assert names == {"docs/big.txt"}

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(TarPeekError):
            inspect_archive(str(tmp_path / "does-not-exist.tar"))

    def test_not_a_tar_archive_raises(self, tmp_path):
        bogus = tmp_path / "not-a-tar.txt"
        bogus.write_text("just some plain text, not a tar archive")
        with pytest.raises(TarPeekError):
            inspect_archive(str(bogus))

    def test_empty_archive_raises(self, empty_archive):
        with pytest.raises(TarPeekError):
            inspect_archive(str(empty_archive))


class TestMainCli:
    def test_table_output(self, sample_archive, capsys):
        exit_code = main([str(sample_archive)])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "NAME" in captured.out
        assert "docs/big.txt" in captured.out
        lines = [l for l in captured.out.splitlines()[1:] if l.strip()]
        assert lines[0].startswith("docs/big.txt")

    def test_json_output(self, sample_archive, capsys):
        exit_code = main([str(sample_archive), "--json"])
        captured = capsys.readouterr()
        assert exit_code == 0
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert data[0]["name"] == "docs/big.txt"
        assert {"name", "type", "size", "mtime"} <= data[0].keys()

    def test_min_size_flag(self, sample_archive, capsys):
        exit_code = main([str(sample_archive), "--min-size", "100", "--json"])
        captured = capsys.readouterr()
        assert exit_code == 0
        data = json.loads(captured.out)
        assert [row["name"] for row in data] == ["docs/big.txt"]

    def test_negative_min_size_rejected(self, sample_archive, capsys):
        exit_code = main([str(sample_archive), "--min-size", "-5"])
        captured = capsys.readouterr()
        assert exit_code == 2
        assert "error" in captured.err.lower()

    def test_not_a_tar_archive_error(self, tmp_path, capsys):
        bogus = tmp_path / "not-a-tar.txt"
        bogus.write_text("just some plain text, not a tar archive")
        exit_code = main([str(bogus)])
        captured = capsys.readouterr()
        assert exit_code != 0
        assert "not a valid tar archive" in captured.err.lower()

    def test_missing_file_error(self, tmp_path, capsys):
        exit_code = main([str(tmp_path / "nope.tar")])
        captured = capsys.readouterr()
        assert exit_code != 0
        assert "no such file" in captured.err.lower()

    def test_empty_archive_error(self, empty_archive, capsys):
        exit_code = main([str(empty_archive)])
        captured = capsys.readouterr()
        assert exit_code != 0
        assert "empty" in captured.err.lower()

    def test_never_writes_to_filesystem(self, sample_archive, empty_archive, tmp_path, capsys):
        before = _listing(tmp_path)
        main([str(sample_archive)])
        main([str(sample_archive), "--json"])
        main([str(sample_archive), "--min-size", "50"])
        main([str(empty_archive)])
        main([str(tmp_path / "nope.tar")])
        capsys.readouterr()
        after = _listing(tmp_path)
        assert before == after
