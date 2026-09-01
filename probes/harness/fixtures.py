#!/usr/bin/env python3
"""probes/harness/fixtures.py — the one test payload MODAL-01 needs: a pinned,
deterministic 1x1 RGB PNG for the image-input content-block probes.

    python3 probes/harness/fixtures.py --selftest

TINY_PNG_BASE64 is a module-level string LITERAL, not a value computed at import
time: zlib's compressed output can differ across zlib/Python versions, and a
payload that varies would change every image cell's probe_id (runner.py's
probe_id() hashes the canonical request body) between machines that ran this
module at different times. The constant below is the pasted, one-time result of
running make_tiny_png() in this session (Python 3.12.3) — make_tiny_png() stays in
this module purely as readable, re-derivable provenance and is never called on the
firing path.
"""
from __future__ import annotations

import argparse
import base64
import struct
import sys
import zlib

# 69 raw bytes / 92 base64 characters — a syntactically valid 1x1 RGB PNG
# (signature + IHDR + IDAT + IEND, each chunk CRC32-correct). Produced once via
# make_tiny_png() below and pasted here as a pinned literal.
TINY_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


def make_tiny_png(width: int = 1, height: int = 1, color: tuple[int, int, int] = (255, 0, 0)) -> bytes:
    """Documentation of how TINY_PNG_BASE64 was produced — NOT called on the
    firing path. Builds a minimal, well-formed PNG from stdlib zlib+struct alone
    (no Pillow, no external image library — RESEARCH.md § Don't Hand-Roll): the
    8-byte signature, an IHDR chunk declaring 8-bit RGB with no alpha, a single
    zlib-compressed scanline as one IDAT chunk, and an empty IEND chunk — each
    chunk followed by its own CRC32 of (tag + data)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB, no alpha
    raw = b"".join(b"\x00" + bytes(color) * width for _ in range(height))
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _iter_png_chunks(data: bytes):
    """Yield (tag, chunk_data, stored_crc32) for every chunk following the 8-byte
    PNG signature. Pure structural walk — used only by selftest() to validate the
    pinned constant by parsing, never by re-compressing and comparing."""
    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        chunk_data = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        yield tag, chunk_data, stored_crc
        pos += 12 + length


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems). Validates
    TINY_PNG_BASE64 by decoding it and walking its chunk structure — never by
    calling make_tiny_png() and comparing, which would make this test depend on
    zlib's exact compressed output for this Python build rather than on the
    pinned constant's own structural validity."""
    problems = 0
    cases = 0

    # --- exact base64 length ---
    cases += 1
    if len(TINY_PNG_BASE64) != 92:
        problems += 1
        print(
            f"FAIL fixtures: TINY_PNG_BASE64 must be exactly 92 characters, got {len(TINY_PNG_BASE64)}",
            file=sys.stderr,
        )

    # --- decodes as valid base64 ---
    cases += 1
    try:
        decoded = base64.b64decode(TINY_PNG_BASE64, validate=True)
    except Exception as e:  # noqa: BLE001 — any decode failure is a selftest finding
        problems += 1
        decoded = b""
        print(f"FAIL fixtures: TINY_PNG_BASE64 does not decode as base64: {e}", file=sys.stderr)

    # --- exact 69-byte length ---
    cases += 1
    if len(decoded) != 69:
        problems += 1
        print(f"FAIL fixtures: decoded payload must be 69 bytes, got {len(decoded)}", file=sys.stderr)

    # --- 8-byte PNG signature ---
    cases += 1
    if decoded[:8] != b"\x89PNG\r\n\x1a\n":
        problems += 1
        print("FAIL fixtures: decoded payload is missing the PNG signature", file=sys.stderr)

    # --- every chunk's stored CRC32 matches a recomputed one ---
    ihdr_found = False
    for tag, chunk_data, stored_crc in _iter_png_chunks(decoded):
        cases += 1
        recomputed = zlib.crc32(tag + chunk_data)
        if recomputed != stored_crc:
            problems += 1
            print(
                f"FAIL fixtures: chunk {tag!r} CRC mismatch: stored={stored_crc}, recomputed={recomputed}",
                file=sys.stderr,
            )
        if tag == b"IHDR":
            ihdr_found = True
            cases += 1
            width, height = struct.unpack(">II", chunk_data[:8])
            if (width, height) != (1, 1):
                problems += 1
                print(
                    f"FAIL fixtures: IHDR declares ({width}, {height}), expected (1, 1)",
                    file=sys.stderr,
                )

    # --- an IHDR chunk was actually present to check ---
    cases += 1
    if not ihdr_found:
        problems += 1
        print("FAIL fixtures: no IHDR chunk found while walking the chunk structure", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(prog="fixtures.py", usage="fixtures.py --selftest")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    print("usage: fixtures.py --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
