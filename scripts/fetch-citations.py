#!/usr/bin/env python3
"""Fetch citation counts for references/ notes from Semantic Scholar — never hand-type them.

    python3 scripts/fetch-citations.py            # print current counts (dry run)
    python3 scripts/fetch-citations.py --write    # update citations/citations_at in frontmatter

Reads every references/*.md with an `arxiv:` frontmatter key, batch-queries the Semantic
Scholar Graph API, and (with --write) rewrites two frontmatter keys in place:

    citations: "N (M influential) — Semantic Scholar"
    citations_at: YYYY-MM-DD

Sources without an arXiv id (blog posts, vendor pages) are skipped — a citation count
for a non-paper is noise, and the index renders their cell as ·.

The number is CONTEXT, not a quality weight: it is age-confounded (this repo reads
2026 preprints that cannot have accumulated citations), and validity-independent (the
library's most-cited member, SWE-bench, later had 68.3% of its items removed as
invalid). The index carries this caveat; keep it there.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references" / "papers"
API = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=citationCount,influentialCitationCount"


def notes_with_arxiv() -> list[tuple[Path, str]]:
    out = []
    for path in sorted(REFS.glob("*.md")):
        if path.name.startswith("_") or path.name in ("index.md", "README.md", "log.md"):
            continue
        m = re.search(r"^arxiv:\s*([0-9.]+)", path.read_text(), re.M)
        if m:
            out.append((path, m.group(1)))
    return out


def fetch(arxiv_ids: list[str]) -> list[dict | None]:
    req = urllib.request.Request(
        API,
        data=json.dumps({"ids": [f"ARXIV:{a}" for a in arxiv_ids]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    # Unauthenticated Semantic Scholar shares a rate pool; 429s are routine, not errors.
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            wait = 30 * (attempt + 1)
            print(f"429 rate-limited; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def main() -> int:
    write = "--write" in sys.argv
    today = datetime.date.today().isoformat()
    targets = notes_with_arxiv()
    papers = fetch([a for _, a in targets])
    changed = 0
    for (path, arxiv), p in zip(targets, papers):
        if p is None:
            print(f"{path.stem:26s} arXiv:{arxiv} NOT FOUND on Semantic Scholar", file=sys.stderr)
            continue
        value = f"{p['citationCount']} ({p['influentialCitationCount']} influential) — Semantic Scholar"
        print(f"{path.stem:26s} {value}")
        if not write:
            continue
        text = path.read_text()
        new_lines = [f'citations: "{value}"', f"citations_at: {today}"]
        if re.search(r"^citations:", text, re.M):
            text = re.sub(r'^citations:.*$', new_lines[0], text, count=1, flags=re.M)
            text = re.sub(r"^citations_at:.*$", new_lines[1], text, count=1, flags=re.M)
        else:
            # insert after the arxiv: line, keeping frontmatter grouping sensible
            text = re.sub(
                r"(^arxiv:.*$)", r"\1\n" + "\n".join(new_lines), text, count=1, flags=re.M
            )
        path.write_text(text)
        changed += 1
    if write:
        print(f"\nwrote {changed} notes — re-run build-refs-index.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
