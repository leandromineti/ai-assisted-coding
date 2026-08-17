"""End-to-end CLI tests: exit codes, table output, --json, error paths, filesystem safety."""

import io
import json
import os
import sys
import tarfile

from tarpeek.cli import EXIT_ERROR, main


def _tarinfo(name, type_flag, size=0, mtime=0, linkname=None):
    info = tarfile.TarInfo(name=name)
    info.type = type_flag
    info.size = size
    info.mtime = mtime
    if linkname:
        info.linkname = linkname
    return info


def _write_tar(path, entries):
    """entries: list of (name, type_flag, size, mtime, content, linkname)"""
    with tarfile.open(path, "w") as tar:
        for name, type_flag, size, mtime, content, linkname in entries:
            info = _tarinfo(name, type_flag, size=size, mtime=mtime, linkname=linkname)
            if type_flag == tarfile.REGTYPE:
                tar.addfile(info, io.BytesIO(content))
            else:
                tar.addfile(info)


def _run(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["tarpeek"] + args)
    return main()


def _snapshot(root):
    entries = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            entries.add(os.path.relpath(os.path.join(dirpath, name), root))
    return entries


# --- T010: successful listing, size-descending order ---


def test_cli_lists_members_sorted_by_size_desc(tmp_path, monkeypatch, capsys):
    archive = str(tmp_path / "demo.tar")
    _write_tar(
        archive,
        [
            ("small.txt", tarfile.REGTYPE, 5, 0, b"hello", None),
            ("big.bin", tarfile.REGTYPE, 5000, 0, b"x" * 5000, None),
            ("subdir", tarfile.DIRTYPE, 0, 0, b"", None),
            ("link-to-small", tarfile.SYMTYPE, 0, 0, b"", "small.txt"),
        ],
    )
    exit_code = _run(monkeypatch, [archive])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.index("big.bin") < out.index("small.txt")
    assert "subdir" in out
    assert "link-to-small" in out


# --- T011: error paths ---


def test_cli_reports_missing_path(tmp_path, monkeypatch, capsys):
    exit_code = _run(monkeypatch, [str(tmp_path / "nope.tar")])
    err = capsys.readouterr().err
    assert exit_code == EXIT_ERROR
    assert err.strip() != ""


def test_cli_reports_non_tar_file(tmp_path, monkeypatch, capsys):
    plain = tmp_path / "notes.txt"
    plain.write_text("not a tar file")
    exit_code = _run(monkeypatch, [str(plain)])
    err = capsys.readouterr().err
    assert exit_code == EXIT_ERROR
    assert err.strip() != ""


def test_cli_reports_empty_archive(tmp_path, monkeypatch, capsys):
    archive = str(tmp_path / "empty.tar")
    _write_tar(archive, [])
    exit_code = _run(monkeypatch, [archive])
    err = capsys.readouterr().err
    assert exit_code == EXIT_ERROR
    assert err.strip() != ""


def test_cli_error_messages_are_distinct(tmp_path, monkeypatch, capsys):
    _run(monkeypatch, [str(tmp_path / "nope.tar")])
    missing_err = capsys.readouterr().err

    plain = tmp_path / "notes.txt"
    plain.write_text("not a tar file")
    _run(monkeypatch, [str(plain)])
    non_tar_err = capsys.readouterr().err

    archive = str(tmp_path / "empty.tar")
    _write_tar(archive, [])
    _run(monkeypatch, [archive])
    empty_err = capsys.readouterr().err

    assert len({missing_err, non_tar_err, empty_err}) == 3


# --- T012: filesystem-write guarantee ---


def test_cli_writes_no_files_on_success(tmp_path, monkeypatch, capsys):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    archive = str(tmp_path / "demo.tar")
    _write_tar(archive, [("a.txt", tarfile.REGTYPE, 5, 0, b"hello", None)])

    before = _snapshot(str(workdir))
    monkeypatch.chdir(workdir)
    _run(monkeypatch, [archive])
    capsys.readouterr()
    after = _snapshot(str(workdir))
    assert before == after


def test_cli_writes_no_files_on_error(tmp_path, monkeypatch, capsys):
    workdir = tmp_path / "workdir"
    workdir.mkdir()

    before = _snapshot(str(workdir))
    monkeypatch.chdir(workdir)
    _run(monkeypatch, [str(tmp_path / "nope.tar")])
    capsys.readouterr()
    after = _snapshot(str(workdir))
    assert before == after


# --- T019: --min-size ---


def _demo_archive(tmp_path):
    archive = str(tmp_path / "demo.tar")
    _write_tar(
        archive,
        [
            ("small.txt", tarfile.REGTYPE, 5, 0, b"hello", None),
            ("big.bin", tarfile.REGTYPE, 5000, 0, b"x" * 5000, None),
        ],
    )
    return archive


def test_cli_min_size_filters_out_smaller_members(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--min-size", "1000"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "big.bin" in out
    assert "small.txt" not in out


def test_cli_min_size_larger_than_every_member_is_success_with_empty_result(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--min-size", "999999999"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "small.txt" not in out
    assert "big.bin" not in out


def test_cli_min_size_rejects_negative_value_before_opening_archive(tmp_path, monkeypatch, capsys):
    exit_code = _run(monkeypatch, [str(tmp_path / "nope.tar"), "--min-size", "-5"])
    err = capsys.readouterr().err
    assert exit_code == EXIT_ERROR
    assert err.strip() != ""


def test_cli_min_size_rejects_non_numeric_value(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--min-size", "not-a-number"])
    err = capsys.readouterr().err
    assert exit_code == EXIT_ERROR
    assert err.strip() != ""


# --- T023: --json ---


def test_cli_json_outputs_valid_json_with_no_extra_text(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(out)
    assert isinstance(data, list)
    assert {m["name"] for m in data} == {"small.txt", "big.bin"}


def test_cli_json_same_sort_order_as_table(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(out)
    assert [m["name"] for m in data] == ["big.bin", "small.txt"]


def test_cli_json_empty_result_after_min_size_filter(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--min-size", "999999999", "--json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert json.loads(out) == []


def test_cli_json_combined_with_min_size_returns_only_filtered_members(tmp_path, monkeypatch, capsys):
    archive = _demo_archive(tmp_path)
    exit_code = _run(monkeypatch, [archive, "--min-size", "1000", "--json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(out)
    assert [m["name"] for m in data] == ["big.bin"]
