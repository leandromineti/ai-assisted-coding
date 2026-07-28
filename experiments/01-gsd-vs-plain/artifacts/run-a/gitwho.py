#!/usr/bin/env python3
"""gitwho — summarize contributor activity for a git repository."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class Author:
    commits: int = 0
    added: int = 0
    deleted: int = 0
    first: str = ""
    last: str = ""
    _dates: list[str] = field(default_factory=list)


def run_git(repo: str, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git failed")
    return result.stdout


def collect(repo: str, since: str | None) -> dict[str, Author]:
    # %x00-separated header lines mark commit boundaries; numstat lines follow each.
    log_args = ["log", "--numstat", "--date=short", "--pretty=format:%x00%an\t%ad"]
    if since:
        log_args.append(f"--since={since}")
    out = run_git(repo, log_args)

    authors: dict[str, Author] = {}
    current: Author | None = None
    for line in out.splitlines():
        if line.startswith("\x00"):
            name, date = line[1:].split("\t")
            current = authors.setdefault(name, Author())
            current.commits += 1
            current._dates.append(date)
        elif line.strip() and current is not None:
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, _path = parts
                # binary files report "-"
                if added != "-":
                    current.added += int(added)
                if deleted != "-":
                    current.deleted += int(deleted)
    for author in authors.values():
        author.first = min(author._dates)
        author.last = max(author._dates)
    return authors


def render_table(authors: dict[str, Author]) -> str:
    rows = sorted(authors.items(), key=lambda kv: kv[1].commits, reverse=True)
    name_w = max(len("Author"), *(len(n) for n, _ in rows))
    header = (
        f"{'Author':<{name_w}}  {'Commits':>7}  {'Added':>7}  {'Deleted':>7}  "
        f"{'First':<10}  {'Last':<10}"
    )
    lines = [header, "-" * len(header)]
    for name, a in rows:
        lines.append(
            f"{name:<{name_w}}  {a.commits:>7}  {a.added:>7}  {a.deleted:>7}  "
            f"{a.first:<10}  {a.last:<10}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gitwho", description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="path to a git repository")
    parser.add_argument("--since", help="only count commits after this date (git syntax)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        run_git(args.repo, ["rev-parse", "--git-dir"])
    except RuntimeError:
        print(f"gitwho: not a git repository: {args.repo}", file=sys.stderr)
        return 2

    try:
        authors = collect(args.repo, args.since)
    except RuntimeError as err:
        print(f"gitwho: {err}", file=sys.stderr)
        return 1

    if not authors:
        print("gitwho: no commits found", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            name: {
                "commits": a.commits,
                "added": a.added,
                "deleted": a.deleted,
                "first": a.first,
                "last": a.last,
            }
            for name, a in sorted(
                authors.items(), key=lambda kv: kv[1].commits, reverse=True
            )
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_table(authors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
