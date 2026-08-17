#!/usr/bin/env python3
"""Build the CANDIDATE screening fixtures for the exp-02 escalation (Aider move).

Escalation per amendment 3 item 5 (owner sign-off 2026-08-17): a candidate pool of
NEW trap families, screened by 5 fresh unaided baseline runs. Candidates that fail in
>= 2 of 5 runs AND pass the fairness screen (reference implementation) enter the
instrument; the rest are discarded. Until that decision, these fixtures live here,
separate from build_fixtures.py, so the accepted instrument stays byte-identical.

Only one candidate family needs an archive fixture: N3 (duplicate member names —
legal in tar, last-wins on extract). N1 (hostile paths) builds its inputs at check
time from tmp dirs; N2/N4 reuse the accepted fixtures.

Deterministic by construction, measured after writing (methodology rule 5a), same as
the main builder.

Usage:  python3 build_candidate_fixtures.py [--out DIR]     # default ./out
"""
from __future__ import annotations

import argparse
import io
import json
import tarfile
from pathlib import Path

from build_fixtures import NORMAL_MTIME

# N3: the same member name twice — first 100 bytes, then 200 bytes one minute later.
# Distinct sizes and mtimes so the two occurrences are tellable apart in any listing.
DUP_NAME = "dup.txt"
DUP_FIRST_SIZE, DUP_SECOND_SIZE = 100, 200
DUP_SECOND_MTIME = NORMAL_MTIME + 60


def _add_file(tar: tarfile.TarFile, name: str, content: bytes, mtime: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(content)
    info.mtime = mtime
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, io.BytesIO(content))


def build(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out / "dup.tar", "w", format=tarfile.USTAR_FORMAT) as tar:
        _add_file(tar, DUP_NAME, b"1" * DUP_FIRST_SIZE, NORMAL_MTIME)
        _add_file(tar, "bystander.txt", b"b" * 50, NORMAL_MTIME)
        _add_file(tar, DUP_NAME, b"2" * DUP_SECOND_SIZE, DUP_SECOND_MTIME)


def measure(out: Path) -> dict:
    """Re-read the archive and record what it actually contains (rule 5a)."""
    members = []
    with tarfile.open(out / "dup.tar", "r") as tar:
        for m in tar.getmembers():
            members.append({"name": m.name, "size": m.size, "mtime": m.mtime})
    return {"archives": {"dup.tar": members}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = parser.parse_args()

    build(args.out)
    measured = measure(args.out)
    expected_path = Path(__file__).parent / "candidate_expected.json"
    expected_path.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
    n = len(measured["archives"]["dup.tar"])
    print(f"built dup.tar in {args.out} — {n} members measured into "
          f"{expected_path.name}")


if __name__ == "__main__":
    main()
