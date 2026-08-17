import io
import json
import tarfile

from tarpeek.cli import main


def _add_file(tar, name, content=b"", mtime=1_700_000_000):
    info = tarfile.TarInfo(name=name)
    info.size = len(content)
    info.mtime = mtime
    tar.addfile(info, fileobj=io.BytesIO(content))


def make_tar(path, builder):
    with tarfile.open(path, "w") as tar:
        builder(tar)
    return path


def test_table_output_sorted_by_size(tmp_path, capsys):
    archive = tmp_path / "sample.tar"
    make_tar(archive, lambda tar: (_add_file(tar, "small", b"a"), _add_file(tar, "big", b"a" * 100)))

    code = main([str(archive)])
    out = capsys.readouterr().out

    assert code == 0
    lines = out.strip().splitlines()
    assert "NAME" in lines[0]
    big_line = next(line for line in lines if line.startswith("big"))
    small_line = next(line for line in lines if line.startswith("small"))
    assert lines.index(big_line) < lines.index(small_line)


def test_json_output_is_valid_and_sorted(tmp_path, capsys):
    archive = tmp_path / "sample.tar"
    make_tar(archive, lambda tar: (_add_file(tar, "small", b"a"), _add_file(tar, "big", b"a" * 100)))

    code = main([str(archive), "--json"])
    out = capsys.readouterr().out

    assert code == 0
    data = json.loads(out)
    assert [m["name"] for m in data] == ["big", "small"]
    assert data[0]["size"] == 100
    assert data[0]["type"] == "file"


def test_min_size_flag_filters_output(tmp_path, capsys):
    archive = tmp_path / "sample.tar"
    make_tar(archive, lambda tar: (_add_file(tar, "small", b"a"), _add_file(tar, "big", b"a" * 100)))

    code = main([str(archive), "--min-size", "10", "--json"])
    out = capsys.readouterr().out

    assert code == 0
    data = json.loads(out)
    assert [m["name"] for m in data] == ["big"]


def test_missing_file_gives_clear_error_and_nonzero_exit(tmp_path, capsys):
    code = main([str(tmp_path / "missing.tar")])
    err = capsys.readouterr().err

    assert code != 0
    assert "missing.tar" in err


def test_non_tar_file_gives_clear_error_and_nonzero_exit(tmp_path, capsys):
    bogus = tmp_path / "bogus.tar"
    bogus.write_text("not a tar archive at all")

    code = main([str(bogus)])
    err = capsys.readouterr().err

    assert code != 0
    assert "not a valid tar archive" in err


def test_empty_archive_gives_clear_error_and_nonzero_exit(tmp_path, capsys):
    archive = tmp_path / "empty.tar"
    with tarfile.open(archive, "w"):
        pass

    code = main([str(archive)])
    err = capsys.readouterr().err

    assert code != 0
    assert "empty" in err.lower()


def test_never_writes_to_filesystem(tmp_path, capsys):
    import os

    archive = tmp_path / "sample.tar"
    make_tar(archive, lambda tar: _add_file(tar, "file.txt", b"contents"))

    before = set(os.listdir(tmp_path))
    main([str(archive), "--json"])
    capsys.readouterr()
    after = set(os.listdir(tmp_path))

    assert before == after
