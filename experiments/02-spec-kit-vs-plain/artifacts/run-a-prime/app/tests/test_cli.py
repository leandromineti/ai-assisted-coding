import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest

from tarpeek.cli import main


def make_tar(tar_path: Path, src_dir: Path) -> None:
    with tarfile.open(tar_path, mode="w") as archive:
        for item in sorted(src_dir.rglob("*")):
            archive.add(item, arcname=item.relative_to(src_dir), recursive=False)


@pytest.fixture
def sample_tar(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "small.txt").write_bytes(b"hi")
    (src / "big.bin").write_bytes(b"x" * 1000)
    (src / "subdir").mkdir()
    (src / "subdir" / "nested.txt").write_bytes(b"nested contents")
    os.symlink("small.txt", src / "link_to_small")

    tar_path = tmp_path / "sample.tar"
    make_tar(tar_path, src)
    return tar_path


@pytest.fixture
def empty_tar(tmp_path: Path) -> Path:
    tar_path = tmp_path / "empty.tar"
    with tarfile.open(tar_path, mode="w"):
        pass
    return tar_path


def run_main(args, capsys):
    exit_code = main(args)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_table_output_sorted_by_size_descending(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar)], capsys)
    assert exit_code == 0
    assert err == ""

    lines = out.strip().splitlines()
    header = lines[0]
    assert "NAME" in header and "TYPE" in header and "SIZE" in header
    assert "LAST MODIFIED" in header

    rows = lines[1:]
    assert len(rows) == 5  # small.txt, big.bin, subdir, subdir/nested.txt, link_to_small

    size_column = header.split().index("SIZE")
    sizes = [int(row.split()[size_column]) for row in rows]
    assert sizes == sorted(sizes, reverse=True)


def test_table_includes_all_member_types(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar)], capsys)
    assert exit_code == 0
    assert "file" in out
    assert "dir" in out
    assert "symlink" in out
    assert "big.bin" in out
    assert "small.txt" in out
    assert "subdir" in out
    assert "link_to_small" in out


def test_json_output_is_sorted_by_size_descending(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar), "--json"], capsys)
    assert exit_code == 0
    data = json.loads(out)
    sizes = [entry["size"] for entry in data]
    assert sizes == sorted(sizes, reverse=True)

    names = {entry["name"] for entry in data}
    assert "big.bin" in names
    assert "small.txt" in names

    for entry in data:
        assert set(entry.keys()) == {"name", "type", "size", "mtime"}


def test_min_size_filters_members(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar), "--json", "--min-size", "500"], capsys)
    assert exit_code == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["name"] == "big.bin"


def test_min_size_with_no_matches_prints_message(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar), "--min-size", "999999"], capsys)
    assert exit_code == 0
    assert "No members match" in out


def test_negative_min_size_is_rejected(sample_tar, capsys):
    exit_code, out, err = run_main([str(sample_tar), "--min-size", "-1"], capsys)
    assert exit_code != 0
    assert "min-size" in err


def test_missing_file_errors_with_nonzero_exit(tmp_path, capsys):
    missing = tmp_path / "does-not-exist.tar"
    exit_code, out, err = run_main([str(missing)], capsys)
    assert exit_code != 0
    assert "not found" in err


def test_non_tar_file_errors_with_nonzero_exit(tmp_path, capsys):
    not_a_tar = tmp_path / "notes.txt"
    not_a_tar.write_text("just some plain text, not a tar archive")
    exit_code, out, err = run_main([str(not_a_tar)], capsys)
    assert exit_code != 0
    assert "not a valid tar archive" in err


def test_empty_archive_errors_with_nonzero_exit(empty_tar, capsys):
    exit_code, out, err = run_main([str(empty_tar)], capsys)
    assert exit_code != 0
    assert "empty" in err


def test_never_writes_to_filesystem(sample_tar, tmp_path, capsys, monkeypatch):
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)

    before = set(workdir.rglob("*"))
    exit_code, out, err = run_main([str(sample_tar)], capsys)
    after = set(workdir.rglob("*"))

    assert exit_code == 0
    assert before == after


def test_installed_console_script_runs_from_any_directory(sample_tar, tmp_path):
    tarpeek_bin = shutil.which("tarpeek")
    if tarpeek_bin is None:
        pytest.skip("tarpeek is not installed on PATH")

    other_dir = tmp_path / "elsewhere"
    other_dir.mkdir()

    result = subprocess.run(
        [tarpeek_bin, str(sample_tar), "--json"],
        cwd=other_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 5
    assert not any(other_dir.iterdir())
