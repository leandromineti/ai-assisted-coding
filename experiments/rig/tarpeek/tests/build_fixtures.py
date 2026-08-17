#!/usr/bin/env python3
"""Build the scoring fixtures for experiment 02 and record their measured ground truth.

Deterministic by construction: fixed contents, fixed mtimes, no wall-clock anywhere.
After writing, every archive is re-read and its actual contents dumped to
expected.json — the scorer asserts against what the fixtures *measurably contain*,
never against what this script intended (methodology rule 5a).

Amendment 3 (2026-08-17) extensions — new members WITHIN the preregistered families,
no new families: traps2.tar (T1: PAX long-name member · T5: hardlink + char-device
members) and truncated.tar (T3: valid header, cut-off body). Original archives are
byte-identical to the amendment-1 instrument.

Usage:  python3 build_fixtures.py [--out DIR]     # default ./out
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
from pathlib import Path

# Raw non-UTF-8 member name (latin-1 "café_latin1.txt") — trap T1.
T1_NAME_BYTES = b"caf\xe9_latin1.txt"

EPOCH_MTIME = 0            # trap T2 (past)
FUTURE_MTIME = 4294967295  # trap T2 (2106)
NORMAL_MTIME = 1753660800  # 2026-07-28 00:00:00 UTC — fixed, not now()

# T1 (amendment 3): a member whose path exceeds ustar's 100-char name field —
# requires PAX/GNU handling and full-name rendering (169 chars total).
LONGNAME_MEMBER = (
    "deepdir/"
    + "/".join(f"level_{i:02d}_dir" for i in range(10))
    + "/very_long_named_file.txt"
)


def _add_file(tar: tarfile.TarFile, name: str, content: bytes, mtime: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(content)
    info.mtime = mtime
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, io.BytesIO(content))


def _add_symlink(tar: tarfile.TarFile, name: str, target: str, mtime: int) -> None:
    info = tarfile.TarInfo(name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    info.mtime = mtime
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info)


def _add_hardlink(tar: tarfile.TarFile, name: str, target: str, mtime: int) -> None:
    info = tarfile.TarInfo(name)
    info.type = tarfile.LNKTYPE
    info.linkname = target
    info.mtime = mtime
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info)


def _add_chardev(tar: tarfile.TarFile, name: str, mtime: int) -> None:
    info = tarfile.TarInfo(name)
    info.type = tarfile.CHRTYPE
    info.devmajor, info.devminor = 1, 3  # /dev/null's numbers — data only, never mknod'd
    info.mtime = mtime
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info)


def build(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    # normal.tar — functional checks: mixed sizes for the sort, a dir, min-size filter.
    with tarfile.open(out / "normal.tar", "w", format=tarfile.USTAR_FORMAT) as tar:
        d = tarfile.TarInfo("docs")
        d.type = tarfile.DIRTYPE
        d.mtime = NORMAL_MTIME
        d.uid = d.gid = 0
        tar.addfile(d)
        _add_file(tar, "docs/big.bin", b"B" * 5000, NORMAL_MTIME)
        _add_file(tar, "small.txt", b"s" * 12, NORMAL_MTIME)
        _add_file(tar, "medium.log", b"m" * 700, NORMAL_MTIME)

    # traps.tar — T1 (raw non-UTF-8 name), T2 (epoch + far-future mtimes),
    # T5 (relative-escape and absolute symlink targets). UNCHANGED from amendment 1.
    with tarfile.open(
        out / "traps.tar", "w", format=tarfile.USTAR_FORMAT,
        encoding="utf-8", errors="surrogateescape",
    ) as tar:
        t1_name = T1_NAME_BYTES.decode("utf-8", "surrogateescape")
        _add_file(tar, t1_name, b"latin1-named", NORMAL_MTIME)
        _add_file(tar, "epoch.txt", b"old", EPOCH_MTIME)
        _add_file(tar, "future.txt", b"new", FUTURE_MTIME)
        _add_symlink(tar, "escape_link", "../../outside/secret", NORMAL_MTIME)
        _add_symlink(tar, "abs_link", "/etc/passwd", NORMAL_MTIME)

    # traps2.tar — amendment 3, within-family members: T1 long name (PAX),
    # T5 hardlink and character-device members (metadata to list, never to create).
    with tarfile.open(out / "traps2.tar", "w", format=tarfile.PAX_FORMAT) as tar:
        _add_file(tar, "hl_orig.txt", b"hardlink target body", NORMAL_MTIME)
        _add_hardlink(tar, "hl_link.txt", "hl_orig.txt", NORMAL_MTIME)
        _add_chardev(tar, "devnode_member", NORMAL_MTIME)
        _add_file(tar, LONGNAME_MEMBER, b"deep", NORMAL_MTIME)

    # empty.tar — valid archive, zero members (T3, distinct from not-a-tar).
    with tarfile.open(out / "empty.tar", "w", format=tarfile.USTAR_FORMAT):
        pass

    # notatar.bin — T3: not a tar archive at all. Fixed bytes, no randomness.
    (out / "notatar.bin").write_bytes(b"PK\x03\x04 definitely not a tar " * 40)

    # truncated.tar — amendment 3, T3 family: a valid header whose data is cut off.
    # Built deterministically: write a one-member archive, keep only the first 700
    # bytes (512-byte header + 188 of 5000 data bytes).
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        _add_file(tar, "cutoff.bin", b"T" * 5000, NORMAL_MTIME)
    (out / "truncated.tar").write_bytes(buf.getvalue()[:700])


def measure(out: Path) -> dict:
    """Re-read every artifact and record what it actually contains."""
    result: dict = {"archives": {}, "notatar_size": (out / "notatar.bin").stat().st_size}
    for name in ("normal.tar", "traps.tar", "traps2.tar", "empty.tar"):
        members = []
        with tarfile.open(
            out / name, "r", encoding="utf-8", errors="surrogateescape"
        ) as tar:
            for m in tar.getmembers():
                members.append({
                    "name_bytes_hex": m.name.encode("utf-8", "surrogateescape").hex(),
                    "name_printable": m.name.encode("utf-8", "surrogateescape")
                                            .decode("utf-8", "replace"),
                    "type": ("dir" if m.isdir() else
                             "symlink" if m.issym() else
                             "hardlink" if m.islnk() else
                             "chardev" if m.ischr() else "file"),
                    "size": m.size,
                    "mtime": m.mtime,
                    "linkname": m.linkname or None,
                })
        result["archives"][name] = members
    # truncated.tar is deliberately unreadable as a whole — measure its identity, not
    # its members: exact size and sha256, plus proof the header names cutoff.bin.
    trunc = (out / "truncated.tar").read_bytes()
    result["truncated"] = {
        "size": len(trunc),
        "sha256": hashlib.sha256(trunc).hexdigest(),
        "header_names_cutoff": trunc[:100].rstrip(b"\x00").decode() == "cutoff.bin",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = parser.parse_args()

    build(args.out)
    measured = measure(args.out)
    expected_path = Path(__file__).parent / "expected.json"
    expected_path.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for v in measured["archives"].values())
    print(f"built 5 archives + notatar.bin in {args.out} — "
          f"{n} members measured into {expected_path.name}")


if __name__ == "__main__":
    main()
