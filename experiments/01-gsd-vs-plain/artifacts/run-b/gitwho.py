#!/usr/bin/env python3
"""gitwho - summarize contributor activity for a git repository.

Usage: gitwho [path] [--since DATE] [--json]

Prints a per-author table of commit counts, lines added, lines deleted, and
first/last commit dates for a git repository, sorted by commit count
descending.

Merge commits count as one commit for their author and contribute no line stats.

--since restricts the window using git's own date parsing. --json prints
the same per-author data as a JSON array.

Exit codes: 0 success, 1 empty repository, 2 not a git repository.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Iterator

RS = "\x1e"
US = "\x1f"
LOG_FORMAT = f"{RS}%H{US}%an{US}%ae{US}%at"


class GitError(Exception):
    """Raised when a git subprocess invocation fails unexpectedly."""


class NotARepoError(GitError):
    """Raised when the given path is not inside a git repository."""


class EmptyRepoError(GitError):
    """Raised when the given git repository has no commits."""


@dataclass(frozen=True)
class FileStat:
    added: int
    deleted: int
    path: str
    binary: bool


@dataclass(frozen=True)
class Commit:
    sha: str
    name: str
    email: str
    epoch: int
    files: tuple[FileStat, ...]


@dataclass
class AuthorStats:
    name: str
    email: str
    commits: int = 0
    added: int = 0
    deleted: int = 0
    first_epoch: int | None = None
    last_epoch: int | None = None


def _run_git(path: str, *args: str) -> subprocess.CompletedProcess:
    """The single subprocess choke point. Byte-mode capture, no shell."""
    return subprocess.run(
        ["git", "-C", path, *args],
        capture_output=True,
        env={**os.environ, "LC_ALL": "C"},
    )


def validate_repo(path: str) -> None:
    """Raise NotARepoError or EmptyRepoError.

    Two sequential, independently-branched checks. Both fail with the same
    git exit code (128), so the branch is on which check failed, never on
    the numeric code and never on matching stderr text.
    """
    result = _run_git(path, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0:
        raise NotARepoError(path)
    result = _run_git(path, "rev-parse", "--verify", "HEAD")
    if result.returncode != 0:
        raise EmptyRepoError(path)


def fetch_log(path: str, since: str | None = None) -> bytes:
    """Make the one and only `git log` call of the program."""
    args = ["log", "--no-renames", "--numstat", f"--format={LOG_FORMAT}"]
    if since is not None:
        args.append(f"--since={since}")
    result = _run_git(path, *args)
    if result.returncode != 0:
        raise GitError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def parse_log(raw: bytes) -> Iterator[Commit]:
    """Pure. Decode once with errors='replace', split into Commit records."""
    text = raw.decode("utf-8", errors="replace")
    for record in text.split(RS):
        if not record.strip():
            continue
        header, _, tail = record.partition("\n")
        sha, name, email, epoch_text = header.split(US)
        files = []
        for line in tail.splitlines():
            if not line.strip():
                continue
            added_field, deleted_field, filepath = line.split("\t", maxsplit=2)
            if added_field == "-":
                added, deleted, binary = 0, 0, True
            else:
                added, deleted, binary = int(added_field), int(deleted_field), False
            files.append(
                FileStat(added=added, deleted=deleted, path=filepath, binary=binary)
            )
        yield Commit(
            sha=sha,
            name=name,
            email=email,
            epoch=int(epoch_text),
            files=tuple(files),
        )


def aggregate(commits: Iterable[Commit]) -> dict[tuple[str, str], AuthorStats]:
    """Pure. Fold Commits into a dict keyed on (name, email)."""
    stats: dict[tuple[str, str], AuthorStats] = {}
    for commit in commits:
        key = (commit.name, commit.email)
        author = stats.setdefault(
            key, AuthorStats(name=commit.name, email=commit.email)
        )
        author.commits += 1
        for file_stat in commit.files:
            author.added += file_stat.added
            author.deleted += file_stat.deleted
        if author.first_epoch is None or commit.epoch < author.first_epoch:
            author.first_epoch = commit.epoch
        if author.last_epoch is None or commit.epoch > author.last_epoch:
            author.last_epoch = commit.epoch
    return stats


def format_epoch(epoch: int) -> str:
    """Pure. Returns YYYY-MM-DD in UTC."""
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%d")


def sorted_stats(stats: dict[tuple[str, str], AuthorStats]) -> list[AuthorStats]:
    """Pure. The single ordering rule both renderers share: commit count
    descending, name ascending as tiebreak."""
    return sorted(stats.values(), key=lambda s: (-s.commits, s.name))


def render_table(stats: dict[tuple[str, str], AuthorStats]) -> str:
    """Pure. Sorted table: AUTHOR COMMITS ADDED DELETED FIRST LAST."""
    rows = sorted_stats(stats)
    headers = ["AUTHOR", "COMMITS", "ADDED", "DELETED", "FIRST", "LAST"]
    # Column 0 (AUTHOR) and columns 4-5 (FIRST, LAST) are left-aligned;
    # columns 1-3 (COMMITS, ADDED, DELETED) are right-aligned.
    left_aligned = {0, 4, 5}

    data_rows = []
    for s in rows:
        data_rows.append(
            [
                s.name,
                str(s.commits),
                str(s.added),
                str(s.deleted),
                format_epoch(s.first_epoch) if s.first_epoch is not None else "",
                format_epoch(s.last_epoch) if s.last_epoch is not None else "",
            ]
        )

    widths = [len(h) for h in headers]
    for row in data_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def _fmt_row(cells: list[str]) -> str:
        parts = [
            cells[i].ljust(widths[i]) if i in left_aligned else cells[i].rjust(widths[i])
            for i in range(len(cells))
        ]
        return "  ".join(parts).rstrip()

    lines = [_fmt_row(headers), _fmt_row(["-" * w for w in widths])]
    for row in data_rows:
        lines.append(_fmt_row(row))
    return "\n".join(lines)


def render_json(stats: dict[tuple[str, str], AuthorStats]) -> str:
    """Pure. The JSON document: a top-level array, one object per author,
    ordered exactly like the table via sorted_stats. No trailing newline —
    main() prints one."""
    rows = [
        {
            "name": s.name,
            "email": s.email,
            "commits": s.commits,
            "added": s.added,
            "deleted": s.deleted,
            "first_commit": format_epoch(s.first_epoch) if s.first_epoch is not None else None,
            "last_commit": format_epoch(s.last_epoch) if s.last_epoch is not None else None,
        }
        for s in sorted_stats(stats)
    ]
    return json.dumps(rows, indent=2)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gitwho")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="path to a git repository (default: current directory)",
    )
    parser.add_argument(
        "--since",
        metavar="DATE",
        default=None,
        help=(
            "restrict the summary to commits since DATE, handed to git "
            "verbatim — accepts any date form git accepts (an ISO date, "
            "an ISO timestamp with an offset, or a relative expression "
            "like \"3 weeks ago\")"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of the table",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        validate_repo(args.path)
    except NotARepoError:
        print(f"gitwho: {args.path!r} is not a git repository", file=sys.stderr)
        return 2
    except EmptyRepoError:
        print(f"gitwho: {args.path!r} has no commits", file=sys.stderr)
        return 1
    try:
        raw = fetch_log(args.path, since=args.since)
    except GitError as exc:
        print(f"gitwho: {exc}", file=sys.stderr)
        return 1
    commits = parse_log(raw)
    stats = aggregate(commits)
    print(render_json(stats) if args.json else render_table(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
