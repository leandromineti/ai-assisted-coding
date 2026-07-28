# Architecture Research

**Domain:** Single-file Python CLI that shells out to `git` for repository analytics
**Researched:** 2026-07-28
**Confidence:** MEDIUM (cross-checked web sources + direct read of a real production
implementation's source code; no official "how to build git-parsing CLIs" spec exists —
this is a convention synthesized from working code, not documented doctrine)

## Standard Architecture

There is no framework or layered-services architecture for a tool this size. The
"architecture" that matters is a **pipeline of pure functions with exactly one impure
boundary** (the subprocess call to `git`). Every comparable tool that stayed maintainable
converges on this shape; every one that got hard to test skipped it.

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                              main(argv)                               │
│              argparse → orchestration → exit code                     │
├──────────────────────────────────────────────────────────────────────┤
│  IMPURE BOUNDARY                                                       │
│  ┌────────────────────┐   ┌────────────────────┐                      │
│  │  validate_repo()    │   │  fetch_log()        │                     │
│  │  rev-parse checks   │   │  git log --numstat  │                     │
│  └─────────┬───────────┘   └─────────┬───────────┘                     │
│            │ raises GitError          │ raw stdout (str)                │
├────────────┴───────────────────────────┴───────────────────────────────┤
│  PURE FUNCTIONS (fully unit-testable, no subprocess, no I/O)            │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────────────┐ │
│  │  parse_log()    │→ │  aggregate()    │→ │  render_table() /       │ │
│  │  text → records │   │  records → stats│   │  render_json()         │ │
│  └────────────────┘   └────────────────┘   └────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|-------------------------|
| `run_git(args, cwd)` | Single choke point for every subprocess call; raises a typed `GitError` (with stderr captured) on non-zero exit | `subprocess.run([...], capture_output=True, text=True, check=False)` — never `shell=True`, never a hand-built command string |
| `validate_repo(path)` | Distinguish "not a git repo" from "repo with zero commits" before doing real work | `git rev-parse --is-inside-work-tree` (fails = not a repo) then `git rev-parse --verify HEAD` (fails = no commits) |
| `fetch_log(path, since)` | Produce the one raw text blob that contains everything downstream needs — commit identity, author, timestamp, and per-file churn | one `git log --numstat` call with a custom `--format`, never `--stat` (human-oriented, not machine-stable) |
| `parse_log(raw_text)` | Turn the raw blob into a list/iterator of structured commit records | pure string/regex processing, zero I/O — this is the function most worth unit-testing directly |
| `aggregate(records)` | Fold commit records into per-author totals (commits, +lines, -lines, first/last date) | pure `dict`/`defaultdict` reduction, no git awareness at all |
| `render_table()` / `render_json()` | Turn the aggregate dict into the two required output formats | pure formatting functions — table via manual column alignment or stdlib only (no `tabulate` dependency, per stdlib-only constraint) |
| `main(argv)` | Wire the above together, map exceptions to exit codes | argparse setup + a thin `try/except` around the impure calls |

## Recommended Project Structure

Given the project's own constraint ("single-file CLI, one module plus tests plus
README"), the component boundaries above are **not separate files** — they are clearly
separated *functions/sections* inside one module. Splitting into a package would be
over-engineering for this scope; the pytest suite is what proves the boundaries are real.

```
gitwho/
├── gitwho.py              # single module, internally ordered as:
│                           #   1. exceptions (GitError, NotARepoError, EmptyRepoError)
│                           #   2. run_git() / validate_repo() / fetch_log()  [impure]
│                           #   3. parse_log()                                [pure]
│                           #   4. aggregate()                                [pure]
│                           #   5. render_table() / render_json()             [pure]
│                           #   6. build_arg_parser() / main()
├── tests/
│   ├── test_parse.py       # unit: literal numstat text blobs → parsed records
│   │                        #   (binary marker, no-renames delete+add pair, unicode
│   │                        #    author, merge commit with empty body, embedded blank
│   │                        #    lines in commit message)
│   ├── test_aggregate.py   # unit: records → stats (sort order, since-boundary dates,
│   │                        #   first/last commit computed from min/max timestamp)
│   ├── test_render.py      # unit: stats dict → table string / JSON string
│   └── test_cli.py         # integration: real repos built in tmp_path via subprocess
│                            #   git init/commit — not-a-repo dir, empty repo, normal
│                            #   repo, binary file, renamed file, merge commit
└── README.md
```

### Structure Rationale

- **One file, six internal sections:** matches the project's explicit size constraint
  while still giving `parse_log`/`aggregate`/`render_*` the property that matters most —
  they can be imported and called with plain strings/dicts in a test, with no `git`
  binary and no filesystem involved.
- **`tests/test_parse.py` as literal-text fixtures, not live git output:** the exact
  byte-for-byte numstat format is what breaks tools across git versions/locales: pinning
  it as inline string constants in tests documents the contract and catches format
  drift immediately, independent of whatever git version CI happens to have installed.
- **`tests/test_cli.py` as the only place that touches real git:** integration tests are
  slow and depend on the installed git version's exact behavior (rename heuristics,
  locale-dependent messages), so they are kept to a handful of end-to-end smoke cases,
  not exhaustive edge-case coverage.

## Architectural Patterns

### Pattern 1: Single subprocess call with a control-byte record format

**What:** One `git log --numstat` invocation returns everything (identity, author,
timestamp, per-file churn) instead of separate calls for commit counts, dates, and
diffstat. Use ASCII **Unit Separator (`\x1f`)** to delimit fields within a commit header
and **Record Separator (`\x1e`)** to delimit commits from each other — both are
non-printing control bytes that do not occur in any git-authored formatting and are
vanishingly unlikely to appear in real commit metadata (unlike printable delimiters such
as `|`, `,`, or even multi-character strings like `»¦«`, all of which a commit message
*could* legally contain).

**When to use:** Any time you need to reliably split a stream of git log output into
per-commit records without an external parsing library.

**Trade-offs:** Slightly less readable in a debugger than a plain-text format (control
bytes are invisible when printed) — mitigated by keeping the format string as a single
named constant with a comment showing the byte values. Strongly preferred over the
"prefix sentinel" trick below for a *new* implementation because it is byte-for-byte
unambiguous instead of merely "unlikely to collide."

**Example:**
```python
import subprocess

RS, US = "\x1e", "\x1f"          # ASCII record / unit separators
LOG_FORMAT = f"{RS}%H{US}%an{US}%ae{US}%at"

def fetch_log(repo: str, since: str | None) -> str:
    args = ["git", "-C", repo, "log", "--no-renames", "--numstat",
            f"--format={LOG_FORMAT}"]
    if since:
        args += [f"--since={since}"]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    return result.stdout

def parse_log(raw: str):
    for record in raw.split(RS):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        commit_hash, author, email, ts = header.split(US)
        for line in body.splitlines():
            if not line.strip():
                continue
            added, deleted, path = line.split("\t", 2)
            yield CommitFile(commit_hash, author, email, int(ts), added, deleted, path)
```

### Pattern 2: `--no-renames` to keep numstat lines to a fixed 3 fields

**What:** By default, git's rename detection is *off* for `git log --numstat` unless
`-M`/`--find-renames` is passed or the user's local `diff.renames` config enables it.
Because that config is not under this tool's control, **explicitly pass `--no-renames`**
rather than relying on the ambient default. This guarantees every numstat line is always
exactly `added\tdeleted\tpath` — a rename becomes a plain delete-old + add-new pair
instead of the `path/{old => new}` brace syntax that `-M`/`-C` would otherwise emit.

**When to use:** Any numstat parser that wants a fixed, predictable field count without
writing a brace-expansion parser for `old/{a => b}/rest`, `{a => b}`, and
`old => new` (all three forms occur depending on how much of the path changed).

**Trade-offs:** A pure rename now shows as N deletions + N additions instead of 0
changed lines, which slightly inflates churn for authors who rename files without
editing them. Given this project's scope explicitly excludes author-identity merging and
does not list rename-aware churn as a requirement, this is the right trade for
robustness. If rename-aware stats become a requirement later, add `-M` and the brace
parser as an isolated, separately tested addition — don't build it into the MVP parser.

### Pattern 3: Binary files are markers, not zeros

**What:** For a binary file, `--numstat` prints `-\t-\tpath` instead of numeric counts.
A parser that does `int(added)` unconditionally will crash on any repo containing a
binary file (images, lockfiles that got binary-diffed, etc. — a near-certainty in real
repos). Detect the `-` sentinel explicitly and treat it as "0 lines, but the file was
touched" rather than a parse error.

**When to use:** Always — every real repo of nontrivial age has at least one binary
commit somewhere in its history.

**Trade-offs:** None; this is a pure correctness fix with no cost. The only decision is
whether a binary-file line still counts toward "lines added/deleted" (recommendation: no
— report 0, since git itself reports no line count) versus toward "commits" (yes, the
commit still counts once per author regardless of what its files contain).

**Example:**
```python
def parse_numstat_line(line: str) -> tuple[int, int, str]:
    added, deleted, path = line.split("\t", 2)
    added = 0 if added == "-" else int(added)
    deleted = 0 if deleted == "-" else int(deleted)
    return added, deleted, path
```

## Data Flow

### Request Flow

```
CLI args (repo path, --since, --json)
    ↓
validate_repo(path)  ──fails──→  NotARepoError / EmptyRepoError → stderr + exit 1/2
    ↓ ok
fetch_log(path, since)  ──git nonzero exit──→  GitError (bad --since syntax etc.) → stderr + exit 1
    ↓ raw text
parse_log(raw text) → Iterator[CommitFile]
    ↓
aggregate(commits) → dict[author_key, AuthorStats]
    ↓
sort by commits desc
    ↓
render_table() or render_json()  (chosen by --json flag)
    ↓
stdout, exit 0
```

### Key Data Flows

1. **Chronology falls out of traversal order, not a second query.** `git log` streams
   commits newest-first by default. Rather than issuing a second call for "first commit"
   and "last commit" per author, track running `min(timestamp)`/`max(timestamp)` per
   author while folding the single stream — first/last date is a byproduct of
   `aggregate()`, not a separate git invocation. Use `%at` (author-time, Unix epoch) in
   the format string, not a pre-formatted date string: integers are trivially compared
   for min/max and converted to a display format once, at render time — never during
   aggregation.
2. **Commit counting must not depend on the numstat body being non-empty.** git still
   emits the `--format` header line for a commit even when its diff body is empty (e.g.
   a merge commit, which by default shows no diff/numstat at all unless `-m` or
   `--first-parent` is passed). Count commits by counting header records seen during
   `parse_log`, not by counting numstat lines — otherwise merge-only authors silently
   vanish from the commit-count column while still (correctly) contributing zero lines.
   This is the single most-cited gotcha in an existing production tool's source (see
   `git-fame`, below) — it defends against this by cross-checking with a *second*
   command (`git shortlog -s -e`) because its own use of pathspec filters can drop
   commits from the numstat stream. This tool has no pathspec filtering, so the
   single-command header-count approach is sufficient and simpler — but the failure
   mode is worth designing against deliberately, not discovering via a bug report.

## Real-World Precedent

Read directly (via `gh api repos/casperdcl/git-fame/contents/...`, not a secondhand
description) — `git-fame` (casperdcl/git-fame, PyPI `git-fame`), a maintained Python CLI
solving the near-identical problem (per-author git contribution stats):

- Single command: `git log --format="aN%aN aE%aE ct%ct" --numstat`.
- Splits the whole output blob with a regex anchored on the format's literal prefix
  characters (`RE_AUTHS_LOG = re.compile(r"^aN(.+?) aE(.*?) ct(\d+)\n\n", flags=re.M)`)
  — i.e. a "prefix sentinel" trick rather than a control-byte record separator.
  **This repo's finding:** control bytes (Pattern 1 above) are strictly safer for a new
  implementation, since a sentinel like `aN` is a plain ASCII substring that a
  sufficiently adversarial commit could in principle collide with; git-fame accepts that
  theoretical risk in exchange for output that's readable in a debugger.
- Strips binary-file numstat lines with `RE_STAT_BINARY = re.compile(r"^\s*?-\s*-.*?\n", flags=re.M)`
  before further parsing — confirms binary detection via the `-`/`-` marker is the
  standard approach, not a defensive edge case this repo invented.
- Rewrites rename syntax with `RE_RENAME = re.compile(r"\{.+? => (.+?)\}")` — confirms
  that if rename detection (`-M`/`-C`) is enabled, the brace-parsing burden is real and
  non-trivial; reinforces the recommendation to use `--no-renames` for the MVP instead.
- Does **not** trust numstat-derived commit counts; separately shells out to
  `git shortlog -s -e` and merges by `"Name <email>"` key — because its own `--incl`/
  `--excl` pathspec filtering can make `git log <pathspec> --numstat` silently omit
  commits that touched no matching file. This tool has no pathspec filtering, so a
  single `git log --numstat` call is sufficient — the two-command split-and-merge
  pattern is a lesson to keep in reserve, not something to build now.

Confidence on these specific claims: **MEDIUM** — verified by reading the actual source
file content, not by search-result summary, but not cross-checked against a second
independent implementation's source for the same claims.

## Anti-Patterns

### Anti-Pattern 1: Parsing `git log --stat` or default `git log -p` output

**What people do:** Reach for the human-readable `--stat` summary (` 3 files changed,
12 insertions(+), 4 deletions(-)`) or full patch output because it's what's visible in
a terminal.

**Why it's wrong:** `--stat` output is formatted for terminal width (truncates long
paths, right-aligns numbers, varies its column widths per invocation) and is explicitly
documented as not intended for scripting. `--numstat` exists specifically as the
machine-parseable sibling of `--stat` — same data, tab-separated, no truncation, no
width-dependent formatting.

**Do this instead:** Always `--numstat`, never `--stat`, for anything that gets parsed
by code.

### Anti-Pattern 2: Building the git command as a shell string

**What people do:** `subprocess.run(f"git log --since={since}", shell=True)` — often
because `--since` needs to accept an arbitrary user-supplied string.

**Why it's wrong:** `shell=True` with any interpolated value (repo path, `--since` date
string) is a command-injection vector, and it's unnecessary — git accepts every argument
as a separate `argv` entry.

**Do this instead:** Always pass a `list[str]` to `subprocess.run`/`check_output`,
never `shell=True`, never an f-string command line. This is not a git-specific
concern but is worth stating explicitly since this project's core loop is "take a
user-supplied string, hand it to a subprocess."

### Anti-Pattern 3: Splitting commit records on blank lines

**What people do:** Assume each commit's `--format` output is separated from the next by
a blank line (`\n\n`) and `split("\n\n")` on the raw output, because that's what the
*default* `git log` pretty-format does.

**Why it's wrong:** A commit message body can itself contain blank lines (any
multi-paragraph commit message does), so a naive blank-line split silently fragments a
single commit into multiple bogus "records." This is exactly the kind of bug that only
shows up on someone else's repo, in production, months later.

**Do this instead:** Use an explicit, unambiguous record separator emitted only once
per commit by the `--format` string itself (Pattern 1's `\x1e`), never rely on
incidental whitespace structure in the message body.

### Anti-Pattern 4: Locale- or timezone-dependent date parsing

**What people do:** Parse git's default human-readable date format (`Mon Jan 12
10:00:00 2026 -0500`) with a hand-rolled string parser, or worse, let it vary with the
invoking user's `git config` (`date.format`) or system locale.

**Why it's wrong:** The default date format is locale-and-config-dependent and not
guaranteed stable across machines running the same tool, which directly conflicts with
this project's stated correctness bar ("agrees with what git reports" — it must agree
*consistently*, not just on the author's machine).

**Do this instead:** Request `%at` (Unix epoch integer) in the format string for all
internal computation (sorting, min/max), and format to a display string
(`--json` output, table `--since`-friendly ISO date) only at render time, using Python's
own `datetime`/`time` formatting — never git's ambient date rendering.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| `git` CLI binary | Single subprocess boundary function (`run_git`), one blocking call per invocation, no daemon/long-lived process | No Python git library (e.g. GitPython, pygit2) per the project's stdlib-only constraint — and unnecessary, since `git log --numstat` is a stable, well-documented text protocol that doesn't need an object-model wrapper for this use case |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| impure I/O layer ↔ `parse_log()` | plain `str` (raw stdout) in, generator of typed records out | this is the seam that makes the parser testable without git installed — feed it literal text constants in tests |
| `parse_log()` ↔ `aggregate()` | iterable of per-file commit records in, `dict[author, AuthorStats]` out | `aggregate()` has zero knowledge of git's output format — it only knows about the already-parsed record shape, so a future format change (e.g. adding email-based author merging) only touches `parse_log()` |
| `aggregate()` ↔ `render_*()` | plain dict/dataclass in, `str` out | rendering has no knowledge of git or parsing at all — `render_json` can be tested with a hand-built dict literal, no fixtures needed |

## Sources

- [casperdcl/git-fame — `gitfame/_gitfame.py`](https://github.com/casperdcl/git-fame/blob/main/gitfame/_gitfame.py) — read directly via `gh api`; primary source for the "prefix-sentinel regex split", binary-line stripping regex, rename-brace regex, and the commit-count-via-shortlog cross-check pattern. Confidence: MEDIUM (direct source read, single implementation, not cross-verified against a second tool's source).
- [git-scm.com — git-log documentation](https://git-scm.com/docs/git-log) — official reference for `--numstat`, `-z`, `--no-renames`, `--first-parent`, `--since` date syntax. Confidence: MEDIUM (web-search-surfaced summary of official docs, not a full direct read of the current doc revision).
- Web search synthesis (multiple queries, cross-checked) on: binary-file `-`/`-` numstat markers, merge-commit numstat suppression by default, `-z` NUL-termination semantics for path fields, and pytest patterns for git-backed CLIs (`tmp_path` fixture repos vs. literal-text unit fixtures). Confidence: MEDIUM (`websearch`, verified/cross-checked across ≥2 independent result sets per claim).

---
*Architecture research for: single-file Python CLI parsing `git log --numstat`*
*Researched: 2026-07-28*
