#!/usr/bin/env python3
"""The only writer of the reports' `stars:` / `stars_at:` pair. Hand-typing a star count into a
report is retired: a count is fetched from the GitHub API, written by line surgery, and carries
its own date and its own rate history. A hand-typed number drifts the day after it is typed; a
refresh that rewrites a frontmatter block is dangerous in a different way — the count is the
smallest part of what is at risk (comment trails, three comments that define what a count
means, pins, and failure modes that get written as data) — so this script is fail-closed
first and a counter second.

    python3 scripts/refresh-stars.py                    # dry-run: preview, summary, worklist; writes nothing
    python3 scripts/refresh-stars.py --apply            # the only write path
    python3 scripts/refresh-stars.py --only NAME        # repeatable; NAME is a report's file stem
    python3 scripts/refresh-stars.py --date YYYY-MM-DD  # run-date override; under --apply it must equal
                                                        # the API Date header's UTC date
    python3 scripts/refresh-stars.py --selftest         # run the embedded fixtures instead

Exit codes: 0 clean, 1 warnings (rename, archive, negative delta, stale qualifier, skipped
non-GitHub url, a comment with no policy entry — under --apply their files are still written),
2 API, data, guard or invocation failure (zero files written).

Population: `tools/[2-6]-*/*.md` whose first frontmatter block has a `stars:` key — 37 reports on
2026-11-04. `tools/candidates.md`, the template and the category READMEs are outside the glob or
carry no such key, and the hand-typed stars in the candidates ledger are its documented
exception. The baseline of record is the committed frontmatter value at run start: at the v4.0
milestone start (2026-11-04) that is each report's pre-refresh pair, and a body datapoint such as
dsh.md's intermediate figure is never silently preferred over it.

Trail grammar, written on the `stars_at:` line (three spaces before the hash):

    stars_at: {run date}   # gh api; {prior,} at {prior date} ({+/-rate}/day net)[; older entries, three at most][; prose]

The new entry records the value the file held before this run, dated by the old `stars_at`, with
the signed net rate between the two stored values; earlier entries and any prose follow byte for
byte. When the run date equals the stored date no zero-day entry is recorded. The `stars:` line
keeps every byte after its integer, so a comment on it survives.

The script never runs a generator, never reads an `upstream/` clone (the clone's state is not
GitHub's), never touches a body line or any frontmatter value other than the two it owns, reads
YAML with `yaml.safe_load` only and writes by line surgery — a structural guard re-reads the old
and the new block and refuses any write where another value differs.

Why the stargazers `history` endpoint is not used (D-04, D-05): the endpoint `repos/{slug}/
stargazers/history` was added by GitHub on 2026-09-04, and it is a survivors view — stars later
removed vanish from their original day, so it diverges from the net count (daytona net -560
versus history +422 at research time). It is deliberately unused. The measure is the net rate
between the two stored values, which is also what every earlier trail in the reports recorded.
Do not add it back.

`--selftest` is PERMANENT calibration (methodology rule 5d): it compares the bytes a run
produced against bytes written out by hand, never the exit status alone (rule 5e), and it spawns
no subprocess and touches no network.
"""
from __future__ import annotations

import argparse
import email.utils
import fnmatch
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POPULATION_GLOB = "tools/[2-6]-*/*.md"
CAP_PRIORS = 3
GH_TIMEOUT_S = 60
WORKLIST_PATHS = ("tools", "docs", "README.md", "articles", "adrs", "experiments")
IMMUTABLE_PREFIXES = ("adrs/", "experiments/")
SUPERLATIVE_RE = re.compile(r"(largest|biggest|fastest|most-starred|out-stars|smallest)", re.IGNORECASE)
SEGMENT = r"[A-Za-z0-9._-]+"
ARROW = "\u2192"
# Semantic-caveat policy (PITFALLS S2): what a count means for the four reports whose count is not
# a plain "stars of the thing this report is about". Printed as a CAVEAT line, never acted on.
POLICY = {
    "claude-code": "stars of the issues/distribution repo (access: closed-source) \u2014 community gravity, not source adoption",
    "modal": "client SDK repo only \u2014 not a measure of the product's reach",
    "daytona": "repository-now count beside a pre-closure freeze pin \u2014 two dates on one frontmatter block",
    "gsd-core": "counts the live repo only \u2014 the predecessor's stars stay stranded on the archive (see the report's provenance notes)",
}
# Warning kinds in their fixed per-report order.
KIND_ORDER = ["RENAMED", "ARCHIVED", "NEGATIVE", "STALE-QUALIFIER", "SKIPPED-NON-GITHUB", "NO-POLICY"]


class RefreshError(Exception):
    """Base of the four failures that map to exit 2 before any write."""

    def __init__(self, reason: str, rel: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.rel = rel


class DataError(RefreshError):
    """A report file the script cannot safely edit."""


class ApiError(RefreshError):
    """An API answer the script cannot trust."""


class GuardError(RefreshError):
    """A planned write that would change more than the two owned lines."""


class InvocationError(RefreshError):
    """A bad command line or an empty selection."""


@dataclass
class Report:
    rel: str
    path: Path
    lines: list  # [(content, eol)] decoded; eol is "", "\n" or "\r\n"
    end: int  # index of the closing '---' line of the first block
    stars_i: int
    stars: int
    stars_ws: str
    stars_tail: str
    at_i: int
    old_date: date
    at_ws: str
    at_sep: str | None  # whitespace before '#', None when there is no comment
    at_comment: str | None  # text after '#', None when there is no comment
    url: str | None
    slug: str | None

    @property
    def stem(self) -> str:
        return Path(self.rel).stem


@dataclass
class Fetched:
    slug: str
    count: int
    full_name: str
    archived: bool
    api_date: date


@dataclass
class Change:
    rel: str
    report: Report
    fetched: Fetched
    new_lines: list
    action: str  # 'prepend' or 'same-day'
    delta: int
    rate: str | None
    flags: list = field(default_factory=list)

    @property
    def old_bytes(self) -> bytes:
        return "".join(c + e for c, e in self.report.lines).encode("utf-8")

    @property
    def new_bytes(self) -> bytes:
        return "".join(c + e for c, e in self.new_lines).encode("utf-8")


STARS_RE = re.compile(r"^stars:([ \t]*)(\d+)(.*)$")
AT_RE = re.compile(r"^stars_at:([ \t]*)(\d{4}-\d{2}-\d{2})(?:([ \t]+)#(.*)|[ \t]*)$")
SLUG_RE = re.compile(rf"^({SEGMENT})/({SEGMENT})$")
URL_RE = re.compile(rf"^https://github\.com/({SEGMENT})/({SEGMENT})/?$")
RENAME_Q_RE = re.compile(rf"repo renamed {ARROW} ({SEGMENT}/{SEGMENT}) \(flagged (\d{{4}}-\d{{2}}-\d{{2}}), url: unchanged\)")
ARCHIVE_Q_RE = re.compile(r"repo archived \(flagged (\d{4}-\d{2}-\d{2})\)")
TAG_RE = re.compile(r"(?:gh api|repo-facts\.sh); ")
ENTRY_RE = re.compile(
    r"\d{1,3}(?:,\d{3})+ at \d{4}-\d{2}-\d{2}(?: \([+\-−]?\d+(?:\.\d+)?/day(?: net)?\))?(?=; |\Z)"
    r"|\d+ at \d{4}-\d{2}-\d{2}(?: \([+\-−]?\d+(?:\.\d+)?/day(?: net)?\))?(?=; |\Z)"
)


# --- discovery and parsing ---------------------------------------------------------------------

def split_lines(raw: bytes) -> list:
    """Decode strictly, split on LF only, keep each line's own EOL (CRLF stays CRLF)."""
    text = raw.decode("utf-8")
    out = []
    for part in re.findall(r"[^\n]*\n|[^\n]+", text):
        if part.endswith("\r\n"):
            out.append((part[:-2], "\r\n"))
        elif part.endswith("\n"):
            out.append((part[:-1], "\n"))
        else:
            out.append((part, ""))
    return out


def frontmatter_bounds(lines: list) -> int | None:
    """Index of the closing delimiter of the first frontmatter block, or None when there is none.
    The block exists only if line 0 is exactly '---'; never look past the closing line."""
    if not lines or lines[0][0] != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i][0] == "---":
            return i
    return None


def _valid_segment(seg: str) -> bool:
    return bool(re.fullmatch(SEGMENT, seg)) and seg not in (".", "..") and not seg.startswith("-")


def parse_slug(url) -> str | None:
    """owner/repo from https://github.com/owner/repo[/]; anything else is None."""
    if not isinstance(url, str):
        return None
    m = URL_RE.match(url.strip())
    if not m or not (_valid_segment(m.group(1)) and _valid_segment(m.group(2))):
        return None
    return f"{m.group(1)}/{m.group(2)}"


def parse_report(rel: str, path: Path, raw: bytes) -> Report | None:
    """A Report for a file in the population, None for a file with no stars: key in block one."""
    try:
        lines = split_lines(raw)
    except UnicodeDecodeError as exc:
        raise DataError(f"not valid UTF-8 ({exc.reason})", rel)
    end = frontmatter_bounds(lines)
    if end is None:
        return None
    stars_idx = [i for i in range(1, end) if lines[i][0].startswith("stars:")]
    at_idx = [i for i in range(1, end) if lines[i][0].startswith("stars_at:")]
    if not stars_idx:
        return None
    if len(stars_idx) > 1 or len(at_idx) > 1:
        raise DataError("stars: or stars_at: appears more than once in the first block", rel)
    if not at_idx:
        raise DataError("stars: without stars_at: (the pair is written together)", rel)
    sm = STARS_RE.match(lines[stars_idx[0]][0])
    tail = sm.group(3) if sm else ""
    if not sm or not (tail.strip() == "" or re.match(r"[ \t]+#", tail)):
        raise DataError(f"stars: value is not a plain integer: {lines[stars_idx[0]][0]!r}", rel)
    am = AT_RE.match(lines[at_idx[0]][0])
    if not am:
        raise DataError(f"stars_at: line has an unsupported shape: {lines[at_idx[0]][0]!r}", rel)
    try:
        old_date = date.fromisoformat(am.group(2))
    except ValueError:
        raise DataError(f"stars_at: is not a real date: {am.group(2)!r}", rel)
    block = "".join(c + e for c, e in lines[1:end])
    try:
        meta = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        raise DataError(f"first frontmatter block is not valid YAML: {exc}", rel)
    if not isinstance(meta, dict):
        raise DataError("first frontmatter block is not a mapping", rel)
    if type(meta.get("stars")) is not int or meta["stars"] != int(sm.group(2)):
        raise DataError("stars: does not parse as the plain integer it looks like", rel)
    if meta.get("stars_at") != old_date or type(meta.get("stars_at")) is not date:
        raise DataError("stars_at: does not parse as a plain date", rel)
    comment = am.group(4)
    if comment is not None and comment.strip() == "":
        comment = None  # an empty comment after '#' is no comment
    url = meta.get("url") if isinstance(meta.get("url"), str) else None
    return Report(
        rel=rel, path=path, lines=lines, end=end,
        stars_i=stars_idx[0], stars=int(sm.group(2)), stars_ws=sm.group(1), stars_tail=tail,
        at_i=at_idx[0], old_date=old_date, at_ws=am.group(1),
        at_sep=am.group(3) if comment is not None else None, at_comment=comment,
        url=url, slug=parse_slug(url),
    )


def _in_population(rel: str) -> bool:
    return rel.count("/") == 2 and fnmatch.fnmatchcase(rel, POPULATION_GLOB)


def discover(root: Path, list_files) -> list:
    reports = []
    for rel in sorted(list_files(root)):
        if not _in_population(rel):
            continue
        path = root / rel
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise DataError(f"cannot read: {exc.strerror}", rel)
        rep = parse_report(rel, path, raw)
        if rep is not None:
            reports.append(rep)
    return reports


def git_list_files(root: Path) -> list:
    """Git-tracked files under the worklist scope (the default lister; the selftest injects its own)."""
    try:
        proc = subprocess.run(["git", "ls-files", "-z", "--", *WORKLIST_PATHS], cwd=root,
                              capture_output=True, check=False, timeout=GH_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InvocationError(f"git ls-files failed: {type(exc).__name__}")
    if proc.returncode != 0:
        raise InvocationError("git ls-files failed: " + proc.stderr.decode("utf-8", "replace").strip()[:120])
    return sorted(p for p in proc.stdout.decode("utf-8").split("\0") if p)


# --- fetch (fail closed) -----------------------------------------------------------------------

def parse_gh_include(raw) -> tuple:
    """Parse `gh api -i` output: (status, lower-cased header map, JSON body). The observed shape
    (gh 2.103.3, 2026-11-04): status line ending LF, headers ending CRLF, a CRLF CRLF blank
    line, then the JSON body — LF-only or CRLF separators are both accepted."""
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    sep = re.search(r"\r?\n\r?\n", text)
    if not sep:
        raise ApiError("malformed gh -i output (no header/body separator)")
    head, body_text = text[: sep.start()], text[sep.end():]
    lines = head.splitlines()
    sm = re.match(r"HTTP/\S+\s+(\d{3})", lines[0]) if lines else None
    if not sm:
        raise ApiError("malformed gh -i output (no status line)")
    headers = {}
    for ln in lines[1:]:
        key, _, val = ln.partition(":")
        headers[key.strip().lower()] = val.strip()
    try:
        body = json.loads(body_text)
    except ValueError:
        raise ApiError("gh -i body is not JSON")
    return int(sm.group(1)), headers, body


def gh_fetch(slug: str) -> tuple:
    """One call per repo. argv list only; the slug already passed parse_slug. On failure only the
    first stderr line is surfaced and nothing from stdout (headers) is ever printed."""
    argv = ["gh", "api", "-i", "--hostname", "github.com", f"repos/{slug}"]
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=GH_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired:
        raise ApiError(f"{slug}: gh api timed out after {GH_TIMEOUT_S}s")
    except FileNotFoundError:
        raise ApiError("gh is not installed or not on PATH")
    if proc.returncode != 0:
        first = (proc.stderr.decode("utf-8", "replace").strip().splitlines() or ["no stderr"])[0]
        raise ApiError(f"{slug}: {first[:200]}")
    return parse_gh_include(proc.stdout)


def validate_repo(slug: str, status, headers: dict, body) -> Fetched:
    if status != 200:
        raise ApiError(f"{slug}: HTTP {status}")
    try:
        stamp = email.utils.parsedate_to_datetime(headers.get("date", ""))
    except (TypeError, ValueError):
        raise ApiError(f"{slug}: no parseable Date header")
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    api_date = stamp.astimezone(timezone.utc).date()
    if not isinstance(body, dict):
        raise ApiError(f"{slug}: response body is not an object")
    count = body.get("stargazers_count")
    if type(count) is not int or count <= 0:
        raise ApiError(f"{slug}: stargazers_count is not a positive integer: {count!r}")
    full_name = body.get("full_name")
    sm = SLUG_RE.match(full_name) if isinstance(full_name, str) else None
    if not sm or not (_valid_segment(sm.group(1)) and _valid_segment(sm.group(2))):
        raise ApiError(f"{slug}: full_name missing or malformed: {full_name!r}")
    archived = body.get("archived")
    if type(archived) is not bool:
        raise ApiError(f"{slug}: archived is missing or not a boolean: {archived!r}")
    return Fetched(slug=slug, count=count, full_name=full_name, archived=archived, api_date=api_date)


# --- rendering ---------------------------------------------------------------------------------

def format_rate(delta: int, days: int) -> str:
    """Net rate, one exact contract: Decimal(|delta|)/Decimal(days), ROUND_HALF_UP, one decimal
    below 100/day and an integer at or above (decided on the one-decimal value); the sign is the
    delta's ('-' below zero, '+' otherwise, so +0.0)."""
    if days < 1:
        raise DataError(f"rate interval must be at least one day, got {days}")
    magnitude = Decimal(abs(delta)) / Decimal(days)
    one = magnitude.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    text = str(magnitude.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if one >= 100 else str(one)
    return ("-" if delta < 0 else "+") + text


def parse_trail(body: str) -> tuple:
    """Split a comment body into (entries, rest). An entry is '{count} at {date}' with an
    optional ' ({rate}/day[ net])'; a 'gh api; ' or 'repo-facts.sh; ' tag is consumed only when an
    entry follows. Entries keep their exact bytes; rest is everything after the last entry's '; '
    separator, verbatim (it may contain semicolons of its own)."""
    tag = TAG_RE.match(body)
    pos = tag.end() if tag else 0
    entries: list = []
    while True:
        em = ENTRY_RE.match(body, pos)
        if not em:
            break
        entries.append(em.group(0))
        pos = em.end()
        if body.startswith("; ", pos):
            pos += 2
        else:
            break
    if not entries:
        return [], body
    return entries, body[pos:]


def render_stars_line(report: Report, new_count: int) -> str:
    """Replace only the integer; every byte after it (a trailing comment) survives."""
    return f"stars:{report.stars_ws}{new_count}{report.stars_tail}"


def render_stars_at_line(report: Report, new_count: int, today: date, qualifiers: list) -> str:
    old = report.lines[report.at_i][0]
    body = report.at_comment.lstrip() if report.at_comment is not None else ""
    if today == report.old_date:
        if not qualifiers:
            return old  # same day: keep the date and the trail; no zero-day entry is ever recorded
        new_body = body
    else:
        days = (today - report.old_date).days
        if days < 0:
            raise DataError(f"stars_at {report.old_date} is in the future (run date {today})", report.rel)
        entries, rest = parse_trail(body)
        entry = f"{report.stars:,} at {report.old_date} ({format_rate(new_count - report.stars, days)}/day net)"
        entries = ([entry] + entries)[:CAP_PRIORS]
        new_body = "gh api; " + "; ".join(entries) + (f"; {rest}" if rest else "")
    for q in qualifiers:
        new_body = f"{new_body}; {q}" if new_body else q
    sep = report.at_sep if report.at_sep is not None else "   "
    return f"stars_at:{report.at_ws}{today}{sep}# {new_body}"


def structural_guard(report: Report, new_lines: list, fetched: Fetched, today: date) -> None:
    """Refuse any write that changes more than the two owned lines. Raises GuardError."""
    rel = report.rel
    if len(new_lines) != len(report.lines):
        raise GuardError("line count changed", rel)
    for i, (old, new) in enumerate(zip(report.lines, new_lines)):
        if i not in (report.stars_i, report.at_i) and old != new:
            raise GuardError(f"line {i + 1} changed outside the two owned lines", rel)
        if old[1] != new[1]:
            raise GuardError(f"line {i + 1} EOL bytes changed", rel)
    try:
        old_meta = yaml.safe_load("".join(c + e for c, e in report.lines[1:report.end]))
        new_meta = yaml.safe_load("".join(c + e for c, e in new_lines[1:report.end]))
    except yaml.YAMLError as exc:
        raise GuardError(f"new block is not valid YAML: {exc}", rel)
    if set(old_meta) != set(new_meta):
        raise GuardError("frontmatter key set changed", rel)
    for key in old_meta:
        if key not in ("stars", "stars_at") and old_meta[key] != new_meta[key]:
            raise GuardError(f"frontmatter value changed: {key}", rel)
    if type(new_meta["stars"]) is not int or new_meta["stars"] != fetched.count:
        raise GuardError("new stars is not the fetched count", rel)
    want_at = today if today != report.old_date else report.old_date
    if new_meta["stars_at"] != want_at:
        raise GuardError("new stars_at is not the run date", rel)


# --- the run -----------------------------------------------------------------------------------

def find_qualifiers(text: str) -> tuple:
    """The script's own qualifiers anywhere in a comment: (rename matches, archived matches)."""
    return list(RENAME_Q_RE.finditer(text)), list(ARCHIVE_Q_RE.finditer(text))


def analyze(report: Report, fetched: Fetched, today: date) -> tuple:
    """(new qualifiers to append, warnings [(kind, line)]) for one report (D-01..D-03, D-04)."""
    rel = report.rel
    comment = report.at_comment or ""
    renames, archives = find_qualifiers(comment)
    new_q: list = []
    warns: list = []
    if fetched.full_name.lower() != report.slug.lower():
        warns.append(("RENAMED", f"WARNING: RENAMED {rel} {report.slug} {ARROW} {fetched.full_name} (url: not rewritten)"))
        if fetched.full_name.lower() not in {m.group(1).lower() for m in renames}:
            new_q.append(f"repo renamed {ARROW} {fetched.full_name} (flagged {today}, url: unchanged)")
    if fetched.archived:
        warns.append(("ARCHIVED", f"WARNING: ARCHIVED {rel} {report.slug}"))
        if not archives:
            new_q.append(f"repo archived (flagged {today})")
    delta = fetched.count - report.stars
    if delta < 0:
        if today == report.old_date:
            detail = "(same-day, no rate)"
        else:
            detail = f"({format_rate(delta, (today - report.old_date).days)}/day net)"
        warns.append(("NEGATIVE", f"WARNING: NEGATIVE {rel} {_signed(delta)} {detail}"))
    for m in renames:
        if m.group(1).lower() == report.slug.lower():
            warns.append(("STALE-QUALIFIER", f"WARNING: STALE-QUALIFIER {rel} {m.group(0)}"))
    if archives and not fetched.archived:
        for m in archives:
            warns.append(("STALE-QUALIFIER", f"WARNING: STALE-QUALIFIER {rel} {m.group(0)}"))
    if report.stem not in POLICY:
        rest = parse_trail(comment.lstrip())[1] if comment.strip() else ""
        rest = ARCHIVE_Q_RE.sub("", RENAME_Q_RE.sub("", rest)).strip(" ;\t")
        stars_comment = report.stars_tail.strip().lstrip("#").strip() if "#" in report.stars_tail else ""
        if rest or stars_comment:
            warns.append(("NO-POLICY", f"WARNING: NO-POLICY {rel} non-trail comment prose without a POLICY entry"))
    return new_q, warns


def plan_change(report: Report, fetched: Fetched, today: date, qualifiers: list) -> Change:
    new_lines = list(report.lines)
    stars_eol = report.lines[report.stars_i][1]
    at_eol = report.lines[report.at_i][1]
    new_lines[report.stars_i] = (render_stars_line(report, fetched.count), stars_eol)
    new_lines[report.at_i] = (render_stars_at_line(report, fetched.count, today, qualifiers), at_eol)
    structural_guard(report, new_lines, fetched, today)
    same_day = today == report.old_date
    delta = fetched.count - report.stars
    rate = None if same_day else format_rate(delta, (today - report.old_date).days)
    return Change(rel=report.rel, report=report, fetched=fetched, new_lines=new_lines,
                  action="same-day" if same_day else "prepend", delta=delta, rate=rate)


def _k_forms(value: int) -> list:
    """k renderings of a count: one decimal half-up from 1,000, integer half-up from 10,000."""
    forms = []
    if value >= 1000:
        forms.append(f"{(Decimal(value) / 1000).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}k")
    if value >= 10000:
        forms.append(f"{(Decimal(value) / 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP)}k")
    return forms


def _in_worklist_scope(rel: str) -> bool:
    return rel == "README.md" or any(rel.startswith(f"{p}/") for p in WORKLIST_PATHS if p != "README.md")


def build_worklist(root: Path, reports: list, list_files) -> list:
    """Checklist lines for every place a pre-refresh star figure or a superlative appears in prose
    (D-07). Whole-number-token matching; each report's own stars:/stars_at: lines are excluded; the
    script edits none of it. One '- [ ] path:line — reasons' line per hit, sorted by path then line."""
    forms: dict = {}
    own: set = set()
    for rep in reports:
        own.add((rep.rel, rep.stars_i + 1))
        own.add((rep.rel, rep.at_i + 1))
        for form in [str(rep.stars), f"{rep.stars:,}", *_k_forms(rep.stars)]:
            forms.setdefault(form.lower(), []).append(rep)
    combined = None
    if forms:
        alt = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
        combined = re.compile(rf"(?<![\w.,])(?:{alt})(?!\w|[.,]\d)", re.IGNORECASE)
    hits = []
    for rel in sorted(list_files(root)):
        if not _in_worklist_scope(rel):
            continue
        try:
            text = (root / rel).read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(text.split("\n"), 1):  # LF numbering, as grep and git count lines
            line = line.rstrip("\r")
            if (rel, n) in own:
                continue
            reasons: list = []
            if combined is not None:
                for m in combined.finditer(line):
                    for rep in forms[m.group(0).lower()]:
                        reason = f'"{m.group(0)}" ({rep.stem} stars {rep.stars:,} at {rep.old_date})'
                        if reason not in reasons:
                            reasons.append(reason)
            for m in SUPERLATIVE_RE.finditer(line):
                reason = f'superlative "{m.group(0)}"'
                if reason not in reasons:
                    reasons.append(reason)
            if reasons:
                tail = " \u2014 immutable (do not edit)" if rel.startswith(IMMUTABLE_PREFIXES) else ""
                hits.append((rel, n, f"- [ ] {rel}:{n} \u2014 {'; '.join(reasons)}{tail}"))
    return [h[2] for h in sorted(hits, key=lambda h: (h[0], h[1]))]


def _signed(n: int) -> str:
    return f"{'-' if n < 0 else '+'}{abs(n):,}"


def run(root: Path, *, apply: bool, only, date_override, fetch, list_files, out, err, today=None) -> int:
    try:
        return _run(root, apply=apply, only=list(only), date_override=date_override, fetch=fetch,
                    list_files=list_files, out=out, err=err, today=today)
    except RefreshError as exc:
        print(f"ERROR: {exc.rel}: {exc.reason}" if exc.rel else f"ERROR: {exc.reason}", file=err)
        return 2


def _run(root, *, apply, only, date_override, fetch, list_files, out, err, today) -> int:
    # Phase A: discover and select
    reports = discover(root, list_files)
    if only:
        known = {r.stem for r in reports}
        unknown = sorted(set(only) - known)
        if unknown:
            raise InvocationError(f"--only names no report: {', '.join(unknown)}")
        reports = [r for r in reports if r.stem in set(only)]
    if not reports:
        raise InvocationError("no stars-bearing reports found")
    run_date = date_override or today or datetime.now(timezone.utc).date()
    warnings: list = []  # (rel, order, line)

    # Phase B: fetch and validate every report before anything is rendered
    fetched: dict = {}
    for rep in reports:
        if rep.slug is None:
            warnings.append((rep.rel, 4, f"WARNING: SKIPPED-NON-GITHUB {rep.rel} {rep.url}"))
            continue
        try:
            status, headers, body = fetch(rep.slug)
            got = validate_repo(rep.slug, status, headers, body)
        except ApiError as exc:
            exc.rel = exc.rel or rep.rel
            raise
        if apply and got.api_date != run_date:
            raise ApiError(f"Date header {got.api_date} differs from run date {run_date}", rep.rel)
        fetched[rep.rel] = got

    # Phase C: render and guard every change
    changes = []
    for rep in reports:
        if rep.rel not in fetched:
            continue
        quals, found = analyze(rep, fetched[rep.rel], run_date)
        ch = plan_change(rep, fetched[rep.rel], run_date, quals)
        ch.flags = [k for k in KIND_ORDER if any(kind == k for kind, _ in found)]
        for kind, line in found:
            warnings.append((rep.rel, KIND_ORDER.index(kind), line))
        changes.append(ch)

    # Phase D: report
    if date_override and not apply:
        print(f"date override {date_override}: preview only \u2014 --apply stamps the API Date", file=out)
    for ch in changes:
        if ch.new_bytes == ch.old_bytes:
            continue
        print(f"{ch.rel} [{ch.action}]", file=out)
        for i, (old, new) in enumerate(zip(ch.report.lines, ch.new_lines)):
            if old != new:
                print(f"  -{old[0]}", file=out)
                print(f"  +{new[0]}", file=out)
    print("## Summary", file=out)
    print("| report | slug | stars | delta | rate | action | flags |", file=out)
    print("|---|---|---|---|---|---|---|", file=out)
    by_rel = {ch.rel: ch for ch in changes}
    for rep in reports:
        ch = by_rel.get(rep.rel)
        if ch is None:
            print(f"| {rep.rel} | {rep.url or '—'} | — | — | — | skip | SKIPPED-NON-GITHUB |", file=out)
            continue
        rate = f"{ch.rate}/day net" if ch.rate else "—"
        flags = ", ".join(ch.flags) or "—"
        print(f"| {rep.rel} | {ch.fetched.slug} | {rep.stars:,} → {ch.fetched.count:,} | "
              f"{_signed(ch.delta)} | {rate} | {ch.action} | {flags} |", file=out)
    for rep in reports:
        if rep.stem in POLICY:
            print(f"CAVEAT {rep.rel}: {POLICY[rep.stem]}", file=out)
    print("## Prose worklist (pre-refresh values; no prose edited)", file=out)
    print("Forms searched: each pre-refresh stars value as raw, comma and k forms, plus "
          "largest|biggest|fastest|most-starred|out-stars|smallest; scope: git-tracked files under "
          "tools/ docs/ README.md articles/ adrs/ experiments/ (adrs/ and experiments/ are immutable).", file=out)
    for line in build_worklist(root, reports, list_files):
        print(line, file=out)
    for _, _, line in sorted(warnings, key=lambda w: (w[0], w[1])):
        print(line, file=err)

    # Phase E: write (apply only) — all temp files exist before the first replace
    written = 0
    if apply:
        todo = [ch for ch in changes if ch.new_bytes != ch.old_bytes]
        temps: list = []
        try:
            for ch in todo:
                target = ch.report.path
                tmp = tempfile.NamedTemporaryFile(dir=target.parent, prefix=".refresh-stars-",
                                                  suffix=".tmp", delete=False)
                temps.append((Path(tmp.name), target))
                with tmp:
                    tmp.write(ch.new_bytes)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                shutil.copymode(target, tmp.name)
        except OSError as exc:
            for tmp_path, _ in temps:
                tmp_path.unlink(missing_ok=True)
            print(f"ERROR: could not stage the writes ({exc.strerror}); nothing was replaced", file=err)
            return 2
        replaced: list = []
        try:
            for tmp_path, target in temps:
                tmp_path.replace(target)
                replaced.append(target)
        except OSError as exc:
            for tmp_path, _ in temps:
                tmp_path.unlink(missing_ok=True)
            print(f"ERROR: replace failed ({exc.strerror}); already replaced: "
                  f"{', '.join(str(p) for p in replaced) or 'none'} — restore them with git", file=err)
            return 2
        written = len(replaced)
    total = f"{written} written" if apply else "0 written (dry-run)"
    print(f"{len(reports)} reports, {total}, {len(warnings)} warning(s)", file=out)
    return 1 if warnings else 0


# ---------------------------------------------------------------------------------------------
# selftest — fixtures are written by hand from the grammar above; the expected bytes are never
# produced by the renderer under test.

TODAY = date(2026, 11, 4)
_DATE_HDR = "Wed, 04 Nov 2026 12:00:00 GMT"


def _doc(
    stars: str,
    stars_at: str | None,
    *,
    url: str = "https://github.com/acme/tool",
    eol: str = "\n",
    final_newline: bool = True,
    body_extra: tuple = (),
) -> bytes:
    head = ["---", "tool: tool", f"url: {url}", "commit: 0123abc4", "depth: survey", stars]
    if stars_at is not None:
        head.append(stars_at)
    head += ["read_at: 2026-08-16", "---"]
    body = ["# Tool", "", "| field | value |", "|---|---|", "| stars | 100 |", "", "stars: 100",
            "stars_at: 2026-08-16", *body_extra]
    text = eol.join(head + body) + (eol if final_newline else "")
    return text.encode("utf-8")


def _ok(count, full_name, *, archived=False, date_hdr=_DATE_HDR):
    return (200, {"date": date_hdr},
            {"stargazers_count": count, "full_name": full_name, "archived": archived})


A = "tools/2-harnesses/aider.md"
M = "tools/3-execution-environments/modal.md"
D = "tools/3-execution-environments/daytona.md"
CC = "tools/2-harnesses/claude-code.md"
GC = "tools/2-harnesses/gemini-cli.md"
CE = "tools/2-harnesses/cecli.md"
XA, XB, XC = "tools/2-harnesses/xa.md", "tools/2-harnesses/xb.md", "tools/2-harnesses/xc.md"


def _fx(id, files, api, *, expect=None, exit=0, warns=(), apply=True, only=(), today=TODAY,
        date_override=None, out_has=(), out_last=None, out_first=None, out_count=(), err_has=(),
        worklist=None):
    return {"id": id, "files": files, "api": api, "expect": expect if expect is not None else {},
            "exit": exit, "warns": list(warns), "apply": apply, "only": list(only), "today": today,
            "date_override": date_override, "out_has": list(out_has), "out_last": out_last,
            "out_first": out_first, "out_count": list(out_count), "err_has": list(err_has),
            "worklist": worklist}


def _trio(b_doc, b_api):
    """Three reports where only b is bad; a and c are fine and must stay untouched too."""
    good = _doc("stars: 100", "stars_at: 2026-08-16", url="https://github.com/acme/xa")
    files = {
        XA: good,
        XB: b_doc,
        XC: _doc("stars: 100", "stars_at: 2026-08-16", url="https://github.com/acme/xc"),
    }
    api = {"acme/xa": _ok(260, "acme/xa"), "acme/xb": b_api, "acme/xc": _ok(260, "acme/xc")}
    return files, api


_EM = "—"
_ARROW = "→"

FIXTURES: list = []


def _build_fixtures() -> list:
    fx = []
    # --- the real trail shapes (bytes copied from the live files, 2026-11-04) -------------
    fx.append(_fx(
        "shape-no-comment",
        {A: _doc("stars: 48519", "stars_at: 2026-08-27", url="https://github.com/Aider-AI/aider")},
        {"Aider-AI/aider": _ok(48657, "Aider-AI/aider")},
        expect={A: _doc("stars: 48657", "stars_at: 2026-11-04   # gh api; 48,519 at 2026-08-27 (+2.0/day net)",
                        url="https://github.com/Aider-AI/aider")}))
    fx.append(_fx(
        "shape-modal-stars-comment",
        {M: _doc(f"stars: 502   # the client repo only {_EM} not a measure of the product's reach",
                 "stars_at: 2026-08-16", url="https://github.com/modal-labs/modal-client")},
        {"modal-labs/modal-client": _ok(662, "modal-labs/modal-client")},
        expect={M: _doc(f"stars: 662   # the client repo only {_EM} not a measure of the product's reach",
                        "stars_at: 2026-11-04   # gh api; 502 at 2026-08-16 (+2.0/day net)",
                        url="https://github.com/modal-labs/modal-client")}))
    daytona_prose = (f"TODAY, post-closure {_EM} describes the repository now, not at the freeze pin. "
                     "`commit:` above describes the freeze pin; `stars`/`stars_at` describe the repository "
                     f"today. Two different dates on one block; that is the whole shape {_EM} of this report.")
    fx.append(_fx(
        "shape-daytona-prose",
        {D: _doc("stars: 71943", f"stars_at: 2026-08-21   # {daytona_prose}",
                 url="https://github.com/daytonaio/daytona")},
        {"daytonaio/daytona": _ok(72168, "daytonaio/daytona", archived=False)},
        expect={D: _doc("stars: 72168",
                        f"stars_at: 2026-11-04   # gh api; 71,943 at 2026-08-21 (+3.0/day net); {daytona_prose}",
                        url="https://github.com/daytonaio/daytona")}))
    cc_prose = f"of the issues/distribution repo {_EM} measures community gravity, not source adoption"
    fx.append(_fx(
        "shape-claude-code-qualifier",
        {CC: _doc("stars: 147932", f"stars_at: 2026-09-24   # {cc_prose}",
                  url="https://github.com/anthropics/claude-code")},
        {"anthropics/claude-code": _ok(148014, "anthropics/claude-code")},
        expect={CC: _doc("stars: 148014",
                         f"stars_at: 2026-11-04   # gh api; 147,932 at 2026-09-24 (+2.0/day net); {cc_prose}",
                         url="https://github.com/anthropics/claude-code")}))
    fx.append(_fx(
        "shape-gemini-decimal-chain",
        {GC: _doc("stars: 107148", "stars_at: 2026-09-24   # gh api; 106,681 at 2026-08-25 (+15.6/day)",
                  url="https://github.com/google-gemini/gemini-cli")},
        {"google-gemini/gemini-cli": _ok(107230, "google-gemini/gemini-cli")},
        expect={GC: _doc("stars: 107230",
                         "stars_at: 2026-11-04   # gh api; 107,148 at 2026-09-24 (+2.0/day net); "
                         "106,681 at 2026-08-25 (+15.6/day)",
                         url="https://github.com/google-gemini/gemini-cli")}))
    fx.append(_fx(
        "shape-cecli-repo-facts",
        {CE: _doc("stars: 408", "stars_at: 2026-09-24   # repo-facts.sh; 405 at 2026-09-09",
                  url="https://github.com/cecli-dev/cecli")},
        {"cecli-dev/cecli": _ok(490, "cecli-dev/cecli")},
        expect={CE: _doc("stars: 490",
                         "stars_at: 2026-11-04   # gh api; 408 at 2026-09-24 (+2.0/day net); 405 at 2026-09-09",
                         url="https://github.com/cecli-dev/cecli")}))
    # --- same-day handling --------------------------------------------------------------------
    same = _doc("stars: 100", "stars_at: 2026-11-04   # gh api; 90 at 2026-10-01 (+0.3/day)")
    fx.append(_fx("same-day-noop", {A: same}, {"acme/tool": _ok(100, "acme/tool")},
                  expect={A: same}, out_has=["same-day"]))
    fx.append(_fx(
        "same-day-count-change", {A: same}, {"acme/tool": _ok(130, "acme/tool")},
        expect={A: _doc("stars: 130", "stars_at: 2026-11-04   # gh api; 90 at 2026-10-01 (+0.3/day)")}))
    # --- encoding ---------------------------------------------------------------------------
    fx.append(_fx(
        "crlf-no-trailing-newline",
        {D: _doc("stars: 100", f"stars_at: 2026-08-16   # gh api; 90 at 2026-07-28 (+1.2/day); kept {_EM} {_ARROW} intact",
                 eol="\r\n", final_newline=False)},
        {"acme/tool": _ok(260, "acme/tool")},
        expect={D: _doc("stars: 260",
                        "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net); 90 at 2026-07-28 "
                        f"(+1.2/day); kept {_EM} {_ARROW} intact",
                        eol="\r\n", final_newline=False)}))
    # --- skip / body --------------------------------------------------------------------------
    gl = _doc("stars: 100", "stars_at: 2026-08-16", url="https://gitlab.com/acme/tool")
    fx.append(_fx("non-github-url", {A: gl}, {}, expect={A: gl}, exit=1, warns=["SKIPPED-NON-GITHUB"]))
    body_doc = _doc("stars: 100", "stars_at: 2026-08-16",
                    body_extra=("---", "stars: 100", "stars_at: 2026-08-16", "| stars | 100 |"))
    fx.append(_fx(
        "body-stars-row-untouched", {A: body_doc}, {"acme/tool": _ok(260, "acme/tool")},
        expect={A: body_doc.replace(
            b"stars: 100\nstars_at: 2026-08-16\nread_at", b"stars: 260\nstars_at: 2026-11-04   "
            b"# gh api; 100 at 2026-08-16 (+2.0/day net)\nread_at", 1)}))
    # --- boundaries -------------------------------------------------------------------------
    fx.append(_fx(
        "cap-three-priors",
        {A: _doc("stars: 100", "stars_at: 2026-08-16   # gh api; 90 at 2026-08-01 (+1.0/day); "
                               "80 at 2026-07-01 (+0.5/day); 70 at 2026-06-01 (+0.4/day)")},
        {"acme/tool": _ok(260, "acme/tool")},
        expect={A: _doc("stars: 260", "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net); "
                                      "90 at 2026-08-01 (+1.0/day); 80 at 2026-07-01 (+0.5/day)")}))
    fx.append(_fx(
        "one-day-interval",
        {A: _doc("stars: 100", "stars_at: 2026-11-03")}, {"acme/tool": _ok(105, "acme/tool")},
        expect={A: _doc("stars: 105", "stars_at: 2026-11-04   # gh api; 100 at 2026-11-03 (+5.0/day net)")}))
    # --- fail closed: three reports, one bad, nothing may change -------------------------------
    ok_b = _doc("stars: 100", "stars_at: 2026-08-16", url="https://github.com/acme/xb")
    for fid, b_doc, b_api in [
        ("fail-closed-http-404", ok_b, (404, {"date": _DATE_HDR}, {"message": "Not Found"})),
        ("fail-closed-bad-count", ok_b, _ok(0, "acme/xb")),
        ("fail-closed-bool-count", ok_b, _ok(True, "acme/xb")),
        ("fail-closed-missing-full-name", ok_b,
         (200, {"date": _DATE_HDR}, {"stargazers_count": 260, "archived": False})),
        ("fail-closed-date-mismatch", ok_b,
         _ok(260, "acme/xb", date_hdr="Thu, 05 Nov 2026 00:00:01 GMT")),
        ("fail-closed-future-stars-at",
         _doc("stars: 100", "stars_at: 2027-01-01", url="https://github.com/acme/xb"), _ok(260, "acme/xb")),
        ("fail-closed-malformed-stars",
         _doc("stars: UNKNOWN", "stars_at: 2026-08-16", url="https://github.com/acme/xb"), _ok(260, "acme/xb")),
        ("fail-closed-missing-stars-at",
         _doc("stars: 100", None, url="https://github.com/acme/xb"), _ok(260, "acme/xb")),
    ]:
        files, api = _trio(b_doc, b_api)
        fx.append(_fx(fid, files, api, exit=2))
    # --- dry run ------------------------------------------------------------------------------
    dry = _doc("stars: 100", "stars_at: 2026-08-16")
    fx.append(_fx("dry-run-writes-nothing", {A: dry}, {"acme/tool": _ok(260, "acme/tool")},
                  expect={A: dry}, apply=False,
                  out_has=["  -stars: 100", "  +stars: 260", "  +stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net)"],
                  out_last="1 reports, 0 written (dry-run), 0 warning(s)"))
    # --- identity and status flags (D-01..D-03) and negative deltas --------------------------
    PS = "tools/4-workflow-frameworks/pilot-shell.md"
    ps_url = "https://github.com/maxritter/pilot-shell"
    q_rename = f"repo renamed {_ARROW} maxritter/qualitylayer (flagged 2026-11-04, url: unchanged)"
    fx.append(_fx(
        "negative-delta",
        {A: _doc("stars: 71943", "stars_at: 2026-08-21")}, {"acme/tool": _ok(71383, "acme/tool")},
        expect={A: _doc("stars: 71383", "stars_at: 2026-11-04   # gh api; 71,943 at 2026-08-21 (-7.5/day net)")},
        exit=1, warns=["NEGATIVE"], err_has=[f"WARNING: NEGATIVE {A} -560 (-7.5/day net)"]))
    fx.append(_fx(
        "rename-first-run",
        {PS: _doc("stars: 2019", "stars_at: 2026-08-18", url=ps_url)},
        {"maxritter/pilot-shell": _ok(2175, "maxritter/qualitylayer")},
        expect={PS: _doc("stars: 2175", f"stars_at: 2026-11-04   # gh api; 2,019 at 2026-08-18 (+2.0/day net); {q_rename}",
                         url=ps_url)},
        exit=1, warns=["RENAMED"],
        err_has=[f"WARNING: RENAMED {PS} maxritter/pilot-shell {_ARROW} maxritter/qualitylayer (url: not rewritten)"]))
    after_rename = _doc("stars: 2175", f"stars_at: 2026-11-04   # gh api; 2,019 at 2026-08-18 (+2.0/day net); {q_rename}",
                        url=ps_url)
    fx.append(_fx(
        "rename-rerun",
        {PS: after_rename},
        {"maxritter/pilot-shell": _ok(2187, "maxritter/qualitylayer", date_hdr="Tue, 10 Nov 2026 12:00:00 GMT")},
        today=date(2026, 11, 10),
        expect={PS: _doc("stars: 2187", "stars_at: 2026-11-10   # gh api; 2,175 at 2026-11-04 (+2.0/day net); "
                                        f"2,019 at 2026-08-18 (+2.0/day net); {q_rename}", url=ps_url)},
        exit=1, warns=["RENAMED"]))
    fx.append(_fx(
        "rename-rerun-same-day",
        {PS: after_rename}, {"maxritter/pilot-shell": _ok(2175, "maxritter/qualitylayer")},
        expect={PS: after_rename}, exit=1, warns=["RENAMED"]))
    fx.append(_fx(
        "archived",
        {A: _doc("stars: 100", "stars_at: 2026-08-16")}, {"acme/tool": _ok(260, "acme/tool", archived=True)},
        expect={A: _doc("stars: 260", "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net); "
                                      "repo archived (flagged 2026-11-04)")},
        exit=1, warns=["ARCHIVED"], err_has=[f"WARNING: ARCHIVED {A} acme/tool"]))
    fx.append(_fx(
        "rename-and-archived",
        {PS: _doc("stars: 2019", "stars_at: 2026-08-18", url=ps_url)},
        {"maxritter/pilot-shell": _ok(2175, "maxritter/qualitylayer", archived=True)},
        expect={PS: _doc("stars: 2175", f"stars_at: 2026-11-04   # gh api; 2,019 at 2026-08-18 (+2.0/day net); "
                                        f"{q_rename}; repo archived (flagged 2026-11-04)", url=ps_url)},
        exit=1, warns=["RENAMED", "ARCHIVED"]))
    fixed_url = "https://github.com/maxritter/qualitylayer"
    fx.append(_fx(
        "stale-qualifier",
        {PS: _doc("stars: 2175", f"stars_at: 2026-11-04   # gh api; 2,019 at 2026-08-18 (+2.0/day net); {q_rename}",
                  url=fixed_url)},
        {"maxritter/qualitylayer": _ok(2187, "maxritter/qualitylayer", date_hdr="Tue, 10 Nov 2026 12:00:00 GMT")},
        today=date(2026, 11, 10),
        expect={PS: _doc("stars: 2187", "stars_at: 2026-11-10   # gh api; 2,175 at 2026-11-04 (+2.0/day net); "
                                        f"2,019 at 2026-08-18 (+2.0/day net); {q_rename}", url=fixed_url)},
        exit=1, warns=["STALE-QUALIFIER"], err_has=[f"WARNING: STALE-QUALIFIER {PS} {q_rename}"]))
    fx.append(_fx(
        "stale-archived-qualifier",
        {A: _doc("stars: 100", "stars_at: 2026-08-16   # gh api; 90 at 2026-07-01 (+1.0/day); "
                               "repo archived (flagged 2026-10-01)")},
        {"acme/tool": _ok(260, "acme/tool", archived=False)},
        expect={A: _doc("stars: 260", "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net); "
                                      "90 at 2026-07-01 (+1.0/day); repo archived (flagged 2026-10-01)")},
        exit=1, warns=["STALE-QUALIFIER"]))
    E2B = "tools/3-execution-environments/e2b.md"
    fx.append(_fx(
        "case-only-slug",
        {E2B: _doc("stars: 100", "stars_at: 2026-08-16", url="https://github.com/e2b-dev/E2B")},
        {"e2b-dev/E2B": _ok(260, "e2b-dev/e2b")},
        expect={E2B: _doc("stars: 260", "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net)",
                          url="https://github.com/e2b-dev/E2B")}))
    FOO = "tools/5-memory/foo.md"
    fx.append(_fx(
        "no-policy-comment",
        {FOO: _doc("stars: 100", "stars_at: 2026-08-16   # something odd about this count",
                   url="https://github.com/acme/foo")},
        {"acme/foo": _ok(260, "acme/foo")},
        expect={FOO: _doc("stars: 260", "stars_at: 2026-11-04   # gh api; 100 at 2026-08-16 (+2.0/day net); "
                                        "something odd about this count", url="https://github.com/acme/foo")},
        exit=1, warns=["NO-POLICY"]))
    cc_doc = _doc("stars: 147932", f"stars_at: 2026-09-24   # {cc_prose}", url="https://github.com/anthropics/claude-code")
    fx.append(_fx(
        "policy-caveat-printed",
        {CC: cc_doc}, {"anthropics/claude-code": _ok(148014, "anthropics/claude-code")},
        expect={CC: _doc("stars: 148014", f"stars_at: 2026-11-04   # gh api; 147,932 at 2026-09-24 (+2.0/day net); {cc_prose}",
                         url="https://github.com/anthropics/claude-code")},
        out_count=[(f"CAVEAT {CC}: stars of the issues/distribution repo (access: closed-source) "
                    f"{_EM} community gravity, not source adoption", 1), ("CAVEAT ", 1)]))
    # --- invocation guards --------------------------------------------------------------------
    plain = _doc("stars: 100", "stars_at: 2026-08-16")
    fx.append(_fx("only-unknown-name", {A: plain}, {"acme/tool": _ok(260, "acme/tool")},
                  only=["no-such-report"], exit=2))
    fx.append(_fx("date-override-apply-mismatch", {A: plain}, {"acme/tool": _ok(260, "acme/tool")},
                  date_override=date(2026, 11, 5), exit=2))
    fx.append(_fx(
        "date-override-dry-run", {A: plain}, {"acme/tool": _ok(260, "acme/tool")},
        apply=False, date_override=date(2026, 11, 5), expect={A: plain},
        out_first=f"date override 2026-11-05: preview only {_EM} --apply stamps the API Date",
        out_has=["  +stars_at: 2026-11-05   # gh api; 100 at 2026-08-16 (+2.0/day net)"]))
    # --- prose worklist (D-07) --------------------------------------------------------------
    CG = "tools/5-memory/cognee.md"
    stamp = "(cognee stars 30,103 at 2026-08-18)"
    imm = " \u2014 immutable (do not edit)"
    fx.append(_fx(
        "worklist",
        {
            CG: _doc("stars: 30103", "stars_at: 2026-08-18", url="https://github.com/acme/cognee"),
            "README.md": "Roughly 30k stars.\n".encode(),
            "docs/n.md": "# Notes\ncognee has 30.1k stars today\nit is the fastest growing\nid 1930103 is no count\n".encode(),
            "adrs/0001-x.md": "# ADR\nAt 30,103 stars we chose.\n".encode(),
            "experiments/01-x/log.md": "Largest in class\n".encode(),
        },
        {"acme/cognee": _ok(30259, "acme/cognee")},
        expect={CG: _doc("stars: 30259", "stars_at: 2026-11-04   # gh api; 30,103 at 2026-08-18 (+2.0/day net)",
                         url="https://github.com/acme/cognee")},
        worklist=[
            f'- [ ] README.md:1 \u2014 "30k" {stamp}',
            f'- [ ] adrs/0001-x.md:2 \u2014 "30,103" {stamp}{imm}',
            f'- [ ] docs/n.md:2 \u2014 "30.1k" {stamp}',
            '- [ ] docs/n.md:3 \u2014 superlative "fastest"',
            f'- [ ] experiments/01-x/log.md:1 \u2014 superlative "Largest"{imm}',
        ]))
    return fx


def _byte_diff(actual: bytes, expected: bytes) -> str | None:
    """None when equal, else a description of the first differing line."""
    if actual == expected:
        return None
    a, e = actual.split(b"\n"), expected.split(b"\n")
    for i in range(max(len(a), len(e))):
        ai = a[i] if i < len(a) else b"<missing>"
        ei = e[i] if i < len(e) else b"<missing>"
        if ai != ei:
            return f"line {i + 1}: got {ai[:140]!r} want {ei[:140]!r}"
    return "bytes differ"


def _walk_files(root: Path) -> list:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def _run_fixture(fx: dict) -> tuple:
    """Run one file fixture in a fresh tree; return (problems, produced files)."""
    tmp = Path(tempfile.mkdtemp(prefix="refresh-stars-selftest-"))
    problems: list = []
    produced: dict = {}
    try:
        for rel, data in fx["files"].items():
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        api = fx["api"]

        def fetch(slug):
            r = api[slug]
            if isinstance(r, Exception):
                raise r
            return r

        out, err = io.StringIO(), io.StringIO()
        try:
            rc = run(tmp, apply=fx["apply"], only=fx["only"], date_override=fx["date_override"],
                     fetch=fetch, list_files=_walk_files, out=out, err=err, today=fx["today"])
        except Exception as exc:  # a crash is a finding, not an abort of the selftest
            problems.append(f"crashed: {type(exc).__name__}: {exc}")
            return problems, produced
        if rc != fx["exit"]:
            problems.append(f"exit {rc}, want {fx['exit']} (stderr: {err.getvalue().strip()[:200]!r})")
        kinds = re.findall(r"^WARNING: (\S+)", err.getvalue(), re.M)
        if kinds != fx["warns"]:
            problems.append(f"warnings {kinds}, want {fx['warns']}")
        for s in fx["out_has"]:
            if s not in out.getvalue():
                problems.append(f"stdout lacks {s!r}")
        for s in fx["err_has"]:
            if s not in err.getvalue():
                problems.append(f"stderr lacks {s!r}")
        for s, n in fx["out_count"]:
            if out.getvalue().count(s) != n:
                problems.append(f"stdout has {out.getvalue().count(s)} of {s!r}, want {n}")
        out_lines = out.getvalue().rstrip("\n").split("\n")
        if fx["out_last"] is not None and out_lines[-1:] != [fx["out_last"]]:
            problems.append(f"last stdout line {out_lines[-1:]!r}, want {fx['out_last']!r}")
        if fx["worklist"] is not None:
            got_wl = [ln for ln in out_lines if ln.startswith("- [ ] ")]
            if got_wl != fx["worklist"]:
                problems.append(f"worklist {got_wl!r}, want {fx['worklist']!r}")
            if "## Prose worklist (pre-refresh values; no prose edited)" not in out_lines:
                problems.append("worklist heading missing")
            if not out_lines[-1].startswith("1 reports, "):
                problems.append("trailing summary line is not last")
        if fx["out_first"] is not None and out_lines[:1] != [fx["out_first"]]:
            problems.append(f"first stdout line {out_lines[:1]!r}, want {fx['out_first']!r}")
        after = _walk_files(tmp)
        if after != sorted(fx["files"]):
            problems.append(f"file set changed: {after}")
        for rel, data in fx["files"].items():
            produced[rel] = (tmp / rel).read_bytes() if (tmp / rel).exists() else b"<missing>"
            want = fx["expect"].get(rel, data)
            diff = _byte_diff(produced[rel], want)
            if diff:
                problems.append(f"{rel}: {diff}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return problems, produced


def _case_gh_include_parse() -> list:
    problems = []
    body = '{"stargazers_count": 5, "full_name": "a/b", "archived": false}'
    ok = ("HTTP/2.0 200 OK\nDate: Wed, 04 Nov 2026 18:56:47 GMT\r\nContent-Type: application/json\r\n"
          "\r\n" + body)
    nf = "HTTP/2.0 404 Not Found\nDate: Wed, 04 Nov 2026 18:56:47 GMT\r\n\r\n" + '{"message": "Not Found"}'
    try:
        st, hd, bd = parse_gh_include(ok.encode())
        if st != 200 or hd.get("date") != "Wed, 04 Nov 2026 18:56:47 GMT" or bd.get("stargazers_count") != 5:
            problems.append(f"200 shape parsed to {st!r} {hd!r} {bd!r}")
        st, hd, bd = parse_gh_include(nf.encode())
        if st != 404:
            problems.append(f"404 shape status {st!r}")
    except Exception as exc:
        problems.append(f"crashed: {type(exc).__name__}: {exc}")
    return problems


def _case_rate_format() -> list:
    problems = []
    cases = [((1555, 100), "+15.6"), ((9994, 100), "+99.9"), ((9995, 100), "+100"), ((1005, 10), "+101"),
             ((-560, 75), "-7.5"), ((0, 80), "+0.0"), ((5, 1), "+5.0"), ((160, 80), "+2.0")]
    for (delta, days), want in cases:
        try:
            got = format_rate(delta, days)
        except Exception as exc:
            got = f"crashed: {type(exc).__name__}: {exc}"
        if got != want:
            problems.append(f"format_rate({delta}, {days}) = {got!r}, want {want!r}")
    return problems


_SUBPROCESS_CALLS: list = []


def _case_cli_flag_conflict() -> list:
    import contextlib
    problems = []
    for argv in (["--selftest", "--apply"], ["--selftest", "--only", "x"], ["--selftest", "--date", "2026-11-04"]):
        sink = io.StringIO()
        with contextlib.redirect_stderr(sink):
            rc = main(argv)
        if rc != 2:
            problems.append(f"main({argv}) returned {rc}, want 2")
    return problems


def _case_no_subprocess() -> list:
    return [f"subprocess.run was called {len(_SUBPROCESS_CALLS)} time(s): {_SUBPROCESS_CALLS[:2]!r}"] \
        if _SUBPROCESS_CALLS else []


def _case_harness_discriminates(modal_fixture: dict) -> list:
    """The comparator must report a mismatch against a deliberately wrong expectation."""
    _, produced = _run_fixture(modal_fixture)
    got = produced.get(M, b"")
    problems = []
    if not got or _byte_diff(got, modal_fixture["expect"][M]) is not None:
        problems.append("the modal fixture itself did not match its expected bytes")
    wrong = modal_fixture["expect"][M].replace(b"stars: 662", b"stars: 663", 1)
    if _byte_diff(got, wrong) is None:
        problems.append("comparator accepted a deliberately wrong expected byte string")
    return problems


def selftest() -> tuple:
    """Run every fixture; return (cases_run, problems). Patches subprocess.run for the whole run."""
    fixtures = _build_fixtures()
    cases = problems = 0
    real_run = subprocess.run

    def _recorder(*a, **k):
        _SUBPROCESS_CALLS.append(a[0] if a else k.get("args"))
        raise RuntimeError("selftest: subprocess is forbidden")

    _SUBPROCESS_CALLS.clear()
    subprocess.run = _recorder
    try:
        for fx in fixtures:
            cases += 1
            found, _ = _run_fixture(fx)
            for msg in found:
                print(f"ERROR: fixture '{fx['id']}' {msg}", file=sys.stderr)
            problems += bool(found)
        groups = [("gh-include-parse", _case_gh_include_parse), ("rate-format", _case_rate_format),
                  ("cli-flag-conflict", _case_cli_flag_conflict)]
        for gid, fn in groups:
            cases += 1
            found = fn()
            for msg in found:
                print(f"ERROR: fixture '{gid}' {msg}", file=sys.stderr)
            problems += bool(found)
        modal = next(f for f in fixtures if f["id"] == "shape-modal-stars-comment")
        cases += 1
        found = _case_harness_discriminates(modal)
        for msg in found:
            print(f"ERROR: fixture 'harness-discriminates' {msg}", file=sys.stderr)
        problems += bool(found)
        cases += 1
        found = _case_no_subprocess()
        for msg in found:
            print(f"ERROR: fixture 'no-subprocess' {msg}", file=sys.stderr)
        problems += bool(found)
    finally:
        subprocess.run = real_run
    return cases, problems


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="refresh-stars.py",
        usage="refresh-stars.py [--apply] [--only NAME]... [--date YYYY-MM-DD] | --selftest",
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", action="append", metavar="NAME", default=[])
    parser.add_argument("--date", metavar="YYYY-MM-DD", default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.date is not None:
        try:
            args.date = date.fromisoformat(args.date)
        except ValueError:
            print("usage: --date must be an ISO date (YYYY-MM-DD)", file=sys.stderr)
            return 2
    if args.selftest:
        if args.apply or args.only or args.date is not None:
            print("usage: --selftest takes no other flag", file=sys.stderr)
            return 2
        cases, problems = selftest()
        print(f"{cases} fixtures run, {problems} problem(s)")
        return 1 if problems else 0
    return run(ROOT, apply=args.apply, only=args.only, date_override=args.date,
               fetch=gh_fetch, list_files=git_list_files, out=sys.stdout, err=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
