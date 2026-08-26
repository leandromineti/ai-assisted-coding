#!/usr/bin/env python3
"""Build a queryable SQLite export of the corpus — generated, never authoritative.

    python3 scripts/build-db.py                    # (re)build comparisons/repo.db
    python3 scripts/build-db.py --query "SQL"      # build if stale, then run one query

The frontmatter stays the source of truth (ADR-0035). This file is a VIEW over it, the
same standing as anything in comparisons/: gitignored, rebuilt from scratch in about a
second, and safe to delete. Nothing may cite it, and no fact may live only here — if a
query wants a column that does not exist, the fix is a registry key and a reading, not a
column in this script.

Three tables plus one derived:

  reports   one row per tool report — the spine every category shares, plus the
            category-specific transcription fields, plus each nested feature block kept
            whole as a JSON column (queryable with json_extract)
  features  the same blocks unpivoted to (report, block, key, value) — because most
            questions are "who has X" and that is a WHERE, not a JSON path
  papers    one row per references/papers/ note
  cards     one row per references/cards/ note
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "comparisons" / "repo.db"

# Derived, never listed: a sixth block added to the registry tomorrow becomes a column
# here without touching this script. Hardcoding it was this script's one unguarded copy of
# the schema — the other consumers at least exit on an unknown block (ADR-0036).
REGISTRY = yaml.safe_load((ROOT / "docs" / "feature-taxonomy.yaml").read_text())
BLOCKS = tuple(dict.fromkeys(e["block"] for e in REGISTRY["features"]))
# Scalar frontmatter carried as real columns. Everything else lands in `extra` as JSON,
# so a field added to a report tomorrow is queryable today without touching this script.
SCALARS = (
    "name", "category", "depth", "maker", "license", "access", "url", "type",
    "stars", "first_commit", "version", "commit", "checked",
    "model_id", "release_mode", "released", "context_window", "max_output",
    "knowledge_cutoff", "execution", "environment_relation",
)
LISTS = ("environments", "harness_targets", "surfaces", "stack", "bears_on")


def read_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


def notes(directory: Path) -> list[tuple[Path, dict]]:
    out = []
    if not directory.is_dir():
        return out
    for path in sorted(directory.rglob("*.md")):
        if path.name.startswith("_") or path.name in ("README.md", "index.md", "log.md"):
            continue
        fm = read_frontmatter(path)
        if fm:
            out.append((path, fm))
    return out


def build() -> sqlite3.Connection:
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    cols = ", ".join(f'"{c}" TEXT' if c not in ("category", "stars", "context_window", "max_output")
                     else f'"{c}" INTEGER' for c in SCALARS)
    con.executescript(f"""
        CREATE TABLE reports ({cols}, path TEXT,
            {", ".join(f'"{b}" TEXT' for b in BLOCKS)},
            {", ".join(f'"{l}" TEXT' for l in LISTS)},
            pricing TEXT, extra TEXT);
        CREATE TABLE features (report TEXT, block TEXT, key TEXT, value TEXT);
        CREATE TABLE papers (key TEXT, title TEXT, year INTEGER, venue TEXT, kind TEXT,
            read_depth TEXT, retrieved TEXT, arxiv TEXT, doi TEXT, url TEXT,
            citations TEXT, bears_on TEXT, path TEXT);
        CREATE TABLE cards (key TEXT, vendor TEXT, title TEXT, models_covered TEXT,
            published TEXT, last_updated TEXT, retrieved TEXT, url TEXT, snapshot TEXT,
            path TEXT);
        CREATE TABLE meta (built_at TEXT, note TEXT);
    """)

    for path, fm in notes(ROOT / "tools"):
        if "category" not in fm:
            continue
        known = set(SCALARS) | set(LISTS) | set(BLOCKS) | {"pricing"}
        row = [fm.get(c) for c in SCALARS]
        row.append(path.relative_to(ROOT).as_posix())
        row += [json.dumps(fm.get(b)) if fm.get(b) is not None else None for b in BLOCKS]
        row += [json.dumps(fm.get(l)) if fm.get(l) is not None else None for l in LISTS]
        row.append(json.dumps(fm.get("pricing")) if fm.get("pricing") is not None else None)
        row.append(json.dumps({k: v for k, v in fm.items() if k not in known} , default=str))
        # YAML parses bare dates into date objects; sqlite3 3.12 deprecated adapting them
        # silently, and a date column that arrives as a string sorts identically anyway.
        def cell(v):
            if isinstance(v, (list, dict)):
                # default=str: YAML turns a full date (2026-02-16) into a date object,
                # and one can now sit inside a structured value like knowledge_cutoff.
                return json.dumps(v, default=str)
            return v if v is None or isinstance(v, (int, float, str)) else str(v)
        con.execute(
            f"INSERT INTO reports VALUES ({','.join('?' * len(row))})",
            [cell(v) for v in row],
        )
        for block in BLOCKS:
            for key, value in (fm.get(block) or {}).items():
                con.execute(
                    "INSERT INTO features VALUES (?,?,?,?)",
                    (fm.get("name"), block, key,
                     json.dumps(value) if isinstance(value, (list, dict)) else str(value)),
                )

    for path, fm in notes(ROOT / "references" / "papers"):
        con.execute(
            "INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (fm.get("key"), fm.get("title"), fm.get("year"), fm.get("venue"), fm.get("kind"),
             fm.get("read_depth"), str(fm.get("retrieved") or ""), str(fm.get("arxiv") or ""),
             fm.get("doi"), fm.get("url"), fm.get("citations"),
             json.dumps(fm.get("bears_on")), path.relative_to(ROOT).as_posix()),
        )

    for path, fm in notes(ROOT / "references" / "cards"):
        con.execute(
            "INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?)",
            (fm.get("key"), fm.get("vendor"), fm.get("title"),
             json.dumps(fm.get("models_covered")), str(fm.get("published") or ""),
             str(fm.get("last_updated") or ""), str(fm.get("retrieved") or ""),
             fm.get("url"), fm.get("snapshot"), path.relative_to(ROOT).as_posix()),
        )

    con.execute(
        "INSERT INTO meta VALUES (?,?)",
        (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "generated by scripts/build-db.py — a view over frontmatter, never authoritative"),
    )
    con.commit()
    return con


def main() -> int:
    con = build()
    counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ("reports", "features", "papers", "cards")}
    print(f"wrote {DB.relative_to(ROOT)} — " +
          " · ".join(f"{v} {k}" for k, v in counts.items()))

    if "--query" in sys.argv:
        sql = sys.argv[sys.argv.index("--query") + 1]
        cur = con.execute(sql)
        headers = [d[0] for d in cur.description]
        rows = cur.fetchall()
        widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h))
                  for i, h in enumerate(headers)]
        print()
        print(" | ".join(str(h).ljust(w) for h, w in zip(headers, widths)))
        print("-+-".join("-" * w for w in widths))
        for r in rows:
            print(" | ".join(str(c).ljust(w) for c, w in zip(r, widths)))
        print(f"\n{len(rows)} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
