# Phase 1: Core Summary Command - Research

**Researched:** 2026-07-28
**Domain:** Git subprocess parsing / CLI pre-flight validation (Python stdlib)
**Confidence:** HIGH

## Summary

Phase 1 is the correctness-critical core of gitwho: one `git log --numstat` invocation,
parsed into per-author commit/line/date stats, rendered as a sorted table, with two
pre-flight checks (not-a-repo, empty-repo) gating the pipeline. Project-level research
(`.planning/research/{SUMMARY,ARCHITECTURE,PITFALLS}.md`) already establishes the
overall architecture (pure-function pipeline around one impure subprocess boundary),
the control-byte record format, and the five critical pitfalls this phase must defend
against. This document does not repeat that — it verifies the exact mechanics
empirically against the git binary actually installed on this machine (git 2.53.0) and
resolves the implementation-level questions the planner needs answered: the exact
pre-flight algorithm for distinguishing not-a-repo from empty-repo, the exact exit
codes involved, the exact parsing algorithm for merge/binary/rename/non-UTF-8 cases, and
what each plan task should verify.

The single most important finding from this session's empirical testing: **both
pre-flight checks fail with the same git exit code (128)**. `git rev-parse
--is-inside-work-tree` and `git rev-parse --verify HEAD` are not distinguishable by exit
code value alone — the pipeline must run them as two sequential, independent checks and
branch on *which command failed*, not on the numeric exit code. This confirms and
sharpens PITFALLS.md's Pitfall 6 (which flagged the risk but didn't pin the exact codes).
This session also empirically reproduced the non-UTF-8 author name crash from PITFALLS.md
Pitfall 4 by constructing a raw commit object with an invalid-UTF-8 byte in the author
field (via `git hash-object -t commit`) and confirmed `subprocess.run(..., text=True)`
raises `UnicodeDecodeError`, while `text=False` + explicit
`.decode("utf-8", errors="replace")` recovers cleanly.

**Primary recommendation:** Implement the pipeline exactly as ARCHITECTURE.md specifies
(control-byte format, `--no-renames`, header-count-based commit counting, binary `-`
sentinel guard, bytes-mode subprocess capture with explicit UTF-8 replace-decode), and
implement the not-a-repo/empty-repo distinction as two sequential `rev-parse` calls
branched by *which one* failed, mapping to exit code 2 (not-a-repo) and exit code 1
(empty-repo) respectively.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-01 | Collect per-author commits, lines added, lines deleted, first/last commit date from one `git log --numstat` invocation | Verified control-byte format + `%at` epoch approach against real repo (see Code Examples, Pattern 1) |
| DATA-02 | Binary-file numstat markers (`-\t-`) handled without crashing, excluded from line counts | Verified `-`/`-` marker empirically on a real binary commit (see Common Pitfalls #1) |
| DATA-03 | Rename detection pinned via `--no-renames` | Verified empirically: with `--no-renames`, a `git mv` produces a plain delete+add pair, not brace syntax (see Common Pitfalls #3) |
| DATA-04 | Merge commits count toward commits, contribute no line stats (git default), policy documented | Verified empirically: merge commit header appears in the stream with zero numstat lines following (see Common Pitfalls #2) |
| DATA-05 | Non-UTF-8 author names do not crash the tool (decode with replacement) | Empirically reproduced the crash and the fix this session (see Common Pitfalls #4) — this is the strongest-verified finding in this document |
| CLI-01 | Repo path is a positional argument, defaults to current directory | Standard `argparse` pattern (see Code Examples) |
| CLI-04 | Output sorted by commit count descending | Trivial `sorted(..., key=lambda kv: -kv[1].commits)` at render time, no special research needed |
| CLI-05 | Not-a-repo produces clear error, exit code 2, via pre-flight `rev-parse` (not stderr string-matching) | Verified exact exit code (128 from git) and exact stderr text empirically; mapped to gitwho's own exit code 2 (see Common Pitfalls #5) |
| CLI-06 | Empty repo produces clear error, non-zero exit | Verified exact exit code (128 from git, via `rev-parse --verify HEAD`) and exact stderr text empirically; recommend gitwho exit code 1 to keep it distinct from CLI-05's 2 (see Open Questions #1) |
</phase_requirements>

## Architectural Responsibility Map

gitwho is a single local process with no client/server split, so the standard
browser/API/DB tier model doesn't apply. The equivalent tiers for a shell-out CLI are:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Repo validation (not-a-repo, empty-repo) | Impure I/O boundary (`validate_repo`) | CLI orchestration (`main`, exit-code mapping) | Must run before any parsing; owns the only two `rev-parse` calls in the program |
| Git log retrieval | Impure I/O boundary (`fetch_log`) | — | Single subprocess call, single choke point per ARCHITECTURE.md |
| Record parsing (binary/merge/rename/encoding handling) | Pure parsing (`parse_log`) | — | Zero I/O; the function most worth exhaustive unit testing per project research |
| Per-author aggregation + sort | Pure aggregation (`aggregate`) | CLI orchestration (sort direction) | Fold of records into stats dict; sort-by-commits-desc (CLI-04) is a one-line detail here, not a separate component |
| Table rendering | Pure rendering (`render_table`) | — | Consumes only the aggregate dict; JSON rendering is Phase 2, not built here but the dict shape should already support it without rework |
| Exit-code mapping | CLI orchestration (`main`) | — | Only `main()` knows the mapping from exception type to process exit code |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `subprocess` | stdlib (3.14.4 installed on this machine) | Shell out to `git log`, `git rev-parse` | Project's own architectural decision (PROJECT.md); no viable stdlib alternative for spawning a process |
| `argparse` | stdlib | CLI positional path argument, future flag surface | Only stdlib-native CLI parser; already decided at project level (SUMMARY.md) |
| `dataclasses` | stdlib | Typed per-author stats record (`AuthorStats`), typed per-file commit record (`CommitFile`) | Zero-dependency typed records, matches project's stdlib-only constraint |
| `collections.defaultdict` | stdlib | Single-pass aggregation fold | Standard idiom for `aggregate()`, no dependency needed |

**Version verification:** [VERIFIED: local environment probe] `git --version` on this
machine reports `git version 2.53.0`; `python3 --version` reports `Python 3.14.4`. All
flags this phase relies on (`--numstat`, `--no-renames`, `--format`, `%H %an %ae %at`,
`rev-parse --is-inside-work-tree`, `rev-parse --verify HEAD`) have been stable in git
since well before 2.x releases widely deployed today — no version-gating concern.
[CITED: project SUMMARY.md] notes Python 3.11+ as the recommended floor (3.9 EOL, 3.10
nearing EOL) — not independently re-verified this session, carried forward from
project-level research.

No packages beyond the standard library are needed for this phase.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual `rev-parse` pre-flight checks | Catching the `git log` failure and string-matching stderr | Explicitly rejected by DATA/CLI-05's own wording ("not stderr string-matching") and by PITFALLS.md Pitfall 6 — locale/git-version text drift makes string-matching unreliable |
| Control-byte (`\x1e`/`\x1f`) record format | git-fame's "prefix sentinel" regex split (`aN...aE...ct...`) | Control bytes are byte-for-byte unambiguous; a prefix sentinel is a plain ASCII substring a pathological commit message could theoretically contain. ARCHITECTURE.md already made this call — confirmed correct in this session's empirical testing (see Code Examples) |

**Installation:** None — stdlib only, nothing to install.

## Package Legitimacy Audit

**Not applicable.** This phase uses only Python standard library modules
(`subprocess`, `argparse`, `dataclasses`, `collections`, `sys`, `datetime`). No
third-party packages are installed or proposed. The Package Legitimacy Gate is
skipped because there is nothing to audit.

## Architecture Patterns

### System Architecture Diagram

```
argv (repo path, defaults to cwd)
   │
   ▼
┌─────────────────────────────┐
│ validate_repo(path)         │  git -C <path> rev-parse --is-inside-work-tree
│   check 1: is a repo?       │──fails (exit 128)──▶ NotARepoError ──▶ stderr msg, exit 2
│   check 2: has commits?     │  git -C <path> rev-parse --verify HEAD
│                             │──fails (exit 128)──▶ EmptyRepoError ──▶ stderr msg, exit 1
└──────────────┬──────────────┘
               │ both pass
               ▼
┌─────────────────────────────┐
│ fetch_log(path)              │  git -C <path> log --no-renames --numstat
│  (impure, one subprocess)    │      --format="\x1e%H\x1f%an\x1f%ae\x1f%at"
└──────────────┬──────────────┘  capture_output=True, text=False (bytes)
               │ raw bytes
               ▼
┌─────────────────────────────┐
│ parse_log(raw_bytes)         │  decode utf-8, errors="replace"
│  (pure)                      │  split on \x1e → per-commit records
│                               │  split header on \x1f → hash/author/email/epoch
│                               │  each numstat line: guard "-" before int()
└──────────────┬──────────────┘
               │ Iterator[CommitFile]
               ▼
┌─────────────────────────────┐
│ aggregate(records)            │  fold into dict[author_key, AuthorStats]
│  (pure)                       │  commits += 1 per HEADER seen (not per numstat line)
│                               │  lines: skip binary "-" entries, add otherwise
│                               │  first/last: running min/max of epoch int
└──────────────┬──────────────┘
               │ dict[author_key, AuthorStats]
               ▼
┌─────────────────────────────┐
│ render_table(stats)           │  sort by .commits desc (CLI-04)
│  (pure)                       │  format epoch → display date at render time only
└──────────────┬──────────────┘
               │
               ▼
           stdout, exit 0
```

### Recommended Project Structure

```
gitwho/
├── gitwho.py              # single module (per project's stated size constraint):
│                            #   1. exceptions: GitError, NotARepoError, EmptyRepoError
│                            #   2. run_git() / validate_repo() / fetch_log()   [impure]
│                            #   3. parse_log()                                 [pure]
│                            #   4. aggregate()                                 [pure]
│                            #   5. render_table()                              [pure]
│                            #   6. build_arg_parser() / main()
└── (tests/ deferred to Phase 2 per QUAL-01 traceability — see Open Questions #4
     for whether Phase 1 should include lightweight ad-hoc verification anyway)
```

### Pattern 1: Two independent `rev-parse` pre-flight checks, branched by which one failed

**What:** Both `git rev-parse --is-inside-work-tree` (not-a-repo case) and
`git rev-parse --verify HEAD` (empty-repo case) exit with the **same** git exit code
(128, empirically confirmed below). They cannot be distinguished by exit code value.
They must be run as two sequential, independently-caught calls; the pipeline branches on
*which call raised*, not on the numeric code that call returned.

**When to use:** Every invocation, before any parsing happens. This is a hard
sequencing requirement, not an optimization — the second check only runs if the first
one succeeded (a path that fails `is-inside-work-tree` should never even attempt
`verify HEAD`).

**Empirical verification (this session, git 2.53.0):**
```
$ git -C /path/to/not-a-repo rev-parse --is-inside-work-tree
fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
exit=128

$ git -C /path/to/empty-repo rev-parse --is-inside-work-tree
true
exit=0

$ git -C /path/to/empty-repo rev-parse --verify HEAD
fatal: Needed a single revision
exit=128
```
[VERIFIED: local git 2.53.0, empirically reproduced this session]

**Example:**
```python
import subprocess

class GitError(Exception): pass
class NotARepoError(GitError): pass
class EmptyRepoError(GitError): pass

def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)

def validate_repo(path: str) -> None:
    r = _run(["git", "-C", path, "rev-parse", "--is-inside-work-tree"])
    if r.returncode != 0:
        raise NotARepoError(f"{path!r} is not a git repository")
    r = _run(["git", "-C", path, "rev-parse", "--verify", "HEAD"])
    if r.returncode != 0:
        raise EmptyRepoError(f"{path!r} has no commits")

# main() maps exception type -> exit code, not the git subprocess's own exit code:
#   NotARepoError -> sys.exit(2)   (CLI-05, explicit requirement)
#   EmptyRepoError -> sys.exit(1)  (CLI-06, "non-zero"; 1 keeps it distinct from 2)
```

**Trade-off / edge case worth flagging:** if the given path does not exist at all (not
just "not a repo"), `git -C <nonexistent-path> ...` fails *before* even reaching repo
detection, with a different stderr message ("cannot change to '<path>': No such file or
directory") but the **same exit code 128**. [VERIFIED: local git 2.53.0, empirically
reproduced this session] Functionally this still lands correctly in the `NotARepoError`
/ exit-2 branch since the check is exit-code-based, not message-based — a nonexistent
path is arguably a valid instance of "not a git repository." No special-case handling is
required to satisfy CLI-05 as written, but the planner may want a task to verify this
specific sub-case (nonexistent path, not just an existing non-repo directory) since it's
easy to accidentally test only the "existing empty directory" variant.

### Pattern 2: Control-byte record format (from project ARCHITECTURE.md, re-verified here)

**What:** One `git log --no-renames --numstat --format="\x1e%H\x1f%an\x1f%ae\x1f%at"`
call. `\x1e` (Record Separator) delimits commits, `\x1f` (Unit Separator) delimits
header fields. Commit message/body is deliberately **not** included in the format
string for this phase — DATA-01 only requires commits/lines/dates, not messages — which
sidesteps ARCHITECTURE.md's Anti-Pattern 3 (blank-line-in-message-body splitting risk)
entirely rather than needing to defend against it.

**When to use:** The one and only `git log` invocation this phase needs.

**Empirical verification (this session, git 2.53.0, real repo with a binary commit, a
rename, a non-ASCII author, and a merge commit):**
```
$ git log --no-renames --numstat --format=$'\x1e%H\x1f%an\x1f%ae\x1f%at'
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990      ← merge commit header
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990      ← next header immediately
                                                                (no numstat lines for
                                                                 the merge — confirms
                                                                 DATA-04)
1<TAB>0<TAB>main.txt
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990
1<TAB>0<TAB>feature.txt
[RS]<hash>[US]José Müller[US]jose@example.com[US]1785271990  ← non-ASCII author,
                                                                 correctly UTF-8 in
                                                                 this case (see
                                                                 Pitfall #4 for the
                                                                 genuinely-invalid case)
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990
0<TAB>1<TAB>a.txt          ← --no-renames: delete...
1<TAB>0<TAB>renamed.txt    ← ...+ add pair, NOT "a.txt => renamed.txt" (confirms DATA-03)
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990
-<TAB>-<TAB>image.png      ← binary marker (confirms DATA-02)
[RS]<hash>[US]Alice[US]alice@example.com[US]1785271990
1<TAB>0<TAB>a.txt
```
[VERIFIED: local git 2.53.0, empirically reproduced this session against a purpose-built
fixture repo]

**Example:**
```python
RS, US = "\x1e", "\x1f"
LOG_FORMAT = f"{RS}%H{US}%an{US}%ae{US}%at"

def fetch_log(path: str) -> bytes:
    r = subprocess.run(
        ["git", "-C", path, "log", "--no-renames", "--numstat",
         f"--format={LOG_FORMAT}"],
        capture_output=True, text=False,   # bytes — see Pitfall #4
    )
    if r.returncode != 0:
        raise GitError(r.stderr.decode("utf-8", errors="replace").strip())
    return r.stdout

def parse_log(raw: bytes):
    text = raw.decode("utf-8", errors="replace")
    for record in text.split(RS):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        commit_hash, author, email, ts = header.split(US)
        commits_seen_marker = True  # count this header regardless of body content
        for line in body.splitlines():
            if not line.strip():
                continue
            added, deleted, filepath = line.split("\t", 2)
            yield commit_hash, author, email, int(ts), added, deleted, filepath
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Distinguishing "not a repo" from "empty repo" | Regex/substring matching on `git log`'s stderr | Two dedicated `rev-parse` pre-flight calls, branched by which raised | Locale- and git-version-dependent stderr text is explicitly disallowed by CLI-05's own wording; exit-code-based branching (Pattern 1) is the standard, stable approach |
| Splitting per-commit records | Blank-line (`\n\n`) splitting on raw `git log` output | Control-byte (`\x1e`) record separator emitted by the `--format` string itself | A commit message body containing a blank line silently fragments records under naive splitting (ARCHITECTURE.md Anti-Pattern 3) — moot here since the format string excludes the message body entirely, but still the correct general pattern |
| Date parsing/formatting | Regex on git's human-readable date output | `%at` (Unix epoch int) in the format string; format to display string only at render time using Python's own `datetime` | Epoch integers are locale-independent and trivially compared for min/max; git's default date text is locale/config-dependent |
| Rename-aware numstat parsing | A brace-expansion parser for `old/{a => b}/rest` syntax | `--no-renames` on every invocation | This phase has no rename-aware feature requirement (DATA-03 explicitly wants the format pinned, not rename tracking); skips real parsing complexity for zero requirement benefit |

**Key insight:** Every "problem" in this phase that looks like it needs custom parsing
logic (repo-state detection, record splitting, date handling, rename handling) has a
dedicated git flag or command that neutralizes the complexity at the source, rather than
needing to be handled after the fact in Python. The pattern across this whole phase is:
push the hard cases onto git's own deterministic flags (`--no-renames`, `%at`,
`rev-parse --verify`) instead of writing more robust Python parsing code.

## Common Pitfalls

### Pitfall 1: Binary files break naive `int()` parsing

**What goes wrong:** `--numstat` emits `-\t-\tpath` for binary files; `int("-")` raises
`ValueError`.
**Why it happens:** Test repos rarely include binaries; real repos almost always do.
**How to avoid:** Guard explicitly: `added = 0 if added_field == "-" else int(added_field)`
(same for deleted). Still count the commit toward commits; report 0 toward lines.
**Warning signs:** Works on the tool's own repo, crashes on the first real target repo.
**Verification this session:** [VERIFIED: local git 2.53.0] Reproduced against a
fixture repo — `git log --no-renames --numstat` on a commit adding a raw binary file
produced the literal line `-\t-\timage.png`.

### Pitfall 2: Merge commits produce a header with zero numstat lines, not zero-value lines

**What goes wrong:** A parser that assumes every commit header is followed by at least
one numstat line (even a `0\t0\tpath` one) will either crash or silently drop merge
commits from the commit count if counting is done by "numstat lines seen" rather than
"headers seen."
**Why it happens:** `git log`'s default diff-merges behavior for a full-history walk
shows no diff at all for merge commits — the intuitive assumption (`git show
<merge-sha>` shows a combined diff) doesn't transfer to `git log`.
**How to avoid:** Count commits during `parse_log` by counting `\x1e`-delimited header
records seen, never by counting numstat lines. A merge commit still contributes exactly
1 to its author's commit count and 0 to their line counts.
**Verification this session:** [VERIFIED: local git 2.53.0] Built a fixture repo with a
real `--no-ff` merge; confirmed the merge commit's header appears in the stream
immediately followed by the next commit's header — zero numstat lines in between.

### Pitfall 3: Rename detection reshapes the numstat line, and is not under this tool's control by default

**What goes wrong:** Without `--no-renames`, a renamed file can appear as
`3\t1\tarch/{old => new}/path` if the user's ambient `diff.renames` git config enables
rename detection — a 3-field-assuming parser mis-parses the path.
**How to avoid:** Pass `--no-renames` explicitly on every invocation.
**Verification this session:** [VERIFIED: local git 2.53.0] With `--no-renames` passed,
a `git mv a.txt renamed.txt` commit produced two clean lines — `0\t1\ta.txt` (delete)
and `1\t0\trenamed.txt` (add) — never the brace syntax, confirming the flag neutralizes
the ambient-config risk regardless of local `diff.renames` setting.

### Pitfall 4: Non-UTF-8 author names crash `text=True` subprocess capture

**What goes wrong:** `subprocess.run(..., text=True)` decodes stdout using the
platform's default encoding (UTF-8 here) in strict mode; a genuinely non-UTF-8 byte in
an author name raises `UnicodeDecodeError` and crashes the whole run on one bad commit
out of possibly thousands.
**Why it happens:** Git commit objects don't enforce UTF-8 encoding on the author
field — old commits, non-UTF-8 locale tooling, or deliberately crafted objects can
contain arbitrary bytes.
**How to avoid:** Capture as bytes (`text=False`, no `encoding=` argument) and decode
explicitly with `.decode("utf-8", errors="replace")`.
**Verification this session:** [VERIFIED: local git 2.53.0, reproduced via
`git hash-object -t commit`] A normal `git commit --author` with a Latin-1 byte in the
name did **not** reproduce the crash — git's own commit machinery appears to normalize
typed input to valid UTF-8 in this git version/environment when the name is supplied as
a shell/env string. To force a *genuinely* invalid byte into a real commit object, this
session bypassed the normal commit path and constructed a raw commit object directly
with `git hash-object -t commit -w`, embedding raw byte `0xE9` (invalid UTF-8
continuation byte) in the `author` line. Confirmed:
```python
>>> raw_bytes.decode("utf-8")
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 46: invalid continuation byte
>>> subprocess.run([...], capture_output=True, text=True)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 ...   # confirmed crash in text=True mode
>>> raw_bytes.decode("utf-8", errors="replace")
'...Andr�...'   # confirmed graceful recovery
```
This is the strongest empirical result in this document: the exact failure mode DATA-05
protects against was reproduced and the fix was verified end-to-end on this machine's
actual git binary, not inferred from documentation. **Implication for testing:** a
fixture test for DATA-05 that only uses `git commit --author="Name <email>"` with an
accented name may not actually exercise the crash path, since git's normal commit path
tends to normalize typed author strings to valid UTF-8. A real DATA-05 regression test
should construct the fixture the same way this session did — a raw commit object via
`git hash-object -t commit -w` with a deliberately invalid UTF-8 byte — or accept that
the test is verifying the defensive code path exists rather than proving a specific
input reliably triggers it.

### Pitfall 5: Not-a-repo and empty-repo both fail with git exit code 128 — must branch on which check failed, not the code

**What goes wrong:** Treating "the pre-flight check failed" as one undifferentiated
case, or worse, trying to use the git exit code itself to distinguish the two states.
**Why it happens:** It's natural to assume different failure *kinds* get different exit
codes; git's own convention doesn't work that way for these two `rev-parse` invocations.
**How to avoid:** Run `rev-parse --is-inside-work-tree` first; if it fails, raise
`NotARepoError` (regardless of the numeric code, which will be 128). Only if it
succeeds, run `rev-parse --verify HEAD`; if *that* fails, raise `EmptyRepoError`
(again, regardless of the numeric code, also 128). The distinguishing signal is program
control flow (which check ran and failed), not the subprocess exit code value.
**Verification this session:** [VERIFIED: local git 2.53.0] Both failure cases
independently confirmed to exit 128; see Pattern 1 above for full transcripts.

## Code Examples

### Full pre-flight + fetch, wired together

```python
import subprocess
import sys

RS, US = "\x1e", "\x1f"
LOG_FORMAT = f"{RS}%H{US}%an{US}%ae{US}%at"

class GitError(Exception): pass
class NotARepoError(GitError): pass
class EmptyRepoError(GitError): pass

def validate_repo(path: str) -> None:
    r = subprocess.run(
        ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise NotARepoError(path)
    r = subprocess.run(
        ["git", "-C", path, "rev-parse", "--verify", "HEAD"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise EmptyRepoError(path)

def fetch_log(path: str) -> bytes:
    r = subprocess.run(
        ["git", "-C", path, "log", "--no-renames", "--numstat",
         f"--format={LOG_FORMAT}"],
        capture_output=True, text=False,
    )
    if r.returncode != 0:
        raise GitError(r.stderr.decode("utf-8", errors="replace").strip())
    return r.stdout

def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="gitwho")
    parser.add_argument("path", nargs="?", default=".",
                         help="path to a git repository (default: current directory)")
    args = parser.parse_args(argv)
    try:
        validate_repo(args.path)
    except NotARepoError:
        print(f"error: {args.path!r} is not a git repository", file=sys.stderr)
        return 2
    except EmptyRepoError:
        print(f"error: {args.path!r} has no commits", file=sys.stderr)
        return 1
    raw = fetch_log(args.path)
    # ... parse_log -> aggregate -> render_table ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```
[VERIFIED: local git 2.53.0 / Python 3.14.4, exit-code branches manually re-derived from
this session's empirical `rev-parse` transcripts above]

### Binary-safe numstat line parsing

```python
def parse_numstat_line(line: str) -> tuple[int, int, str]:
    added, deleted, filepath = line.split("\t", 2)
    added = 0 if added == "-" else int(added)
    deleted = 0 if deleted == "-" else int(deleted)
    return added, deleted, filepath
```
[VERIFIED: pattern confirmed against real binary-file numstat output this session]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `git log --stat` (human-readable) for scripting | `git log --numstat` (machine-parseable) | Always — `--stat` was never intended for scripting | `--stat` truncates paths and varies column width per invocation; `--numstat` is the documented scripting-safe sibling |
| stderr string-matching for repo-state errors | Dedicated `rev-parse` pre-flight checks | Established convention, not a recent change | Explicitly required by this project's own CLI-05 wording |

No dated deprecations apply to this phase — the git flags and Python stdlib APIs used
here have been stable for well over a decade.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Empty-repo (CLI-06) should exit with code **1**, distinct from CLI-05's explicit code 2 | Phase Requirements, Pattern 1 | REQUIREMENTS.md only specifies "non-zero" for CLI-06; if the user/planner wants a different convention (e.g. both non-repo and empty-repo cases sharing a code, or empty-repo using a different specific code), this needs confirming before locking the exit-code contract, since exit codes are explicitly called out in PROJECT.md as "part of the contract" |
| A2 | Author identity key for aggregation should be `(name, email)`, not name alone | Architecture Patterns, Don't Hand-Roll | REQUIREMENTS.md doesn't specify the grouping key explicitly. Grouping by name alone risks conflating two different people who share a display name; grouping by `(name, email)` matches "no identity merging" scope and matches git-fame's precedent (per project ARCHITECTURE.md). If wrong, two commits from the same real person under different emails would appear as two separate table rows — which is explicitly the *documented* v1 behavior per Out of Scope ("`.mailmap` merging... beyond scope for v1"), so this is low risk, but the exact display format (name only vs. `name <email>`) still needs a planning-time decision |
| A3 | Git's own commit-creation path appears to normalize author-name input to valid UTF-8 when supplied via `git commit --author`/env vars, in this git version/environment | Common Pitfalls #4 | If wrong on a different git version/environment, the empirical crash reproduction technique (raw `hash-object -t commit`) may not be needed as a fixture-construction technique on all target environments — but it is still the more reliable technique to guarantee a DATA-05 test actually exercises the crash path, so no material risk to the recommendation itself |
| A4 | Shallow-clone detection is out of scope for Phase 1 (and possibly all of v1) | Open Questions #2 | Project-level PITFALLS.md flags shallow-clone silent-truncation as a real risk, but it appears in neither REQUIREMENTS.md's v1 list nor the Out of Scope table — it was simply never assigned. If the user actually wants this covered, a requirement is missing, not just a phase decision |

## Open Questions

1. **Exact exit code for CLI-06 (empty repo)?**
   - What we know: CLI-05 pins not-a-repo to exit code 2 explicitly. CLI-06 only says
     "non-zero exit" for empty repo.
   - What's unclear: whether the project wants a second explicit, documented code (this
     research recommends 1) or is indifferent as long as it's non-zero and distinct from
     0.
   - Recommendation: lock exit code 1 for empty-repo in the plan; document both codes in
     the module docstring/README (README itself is Phase 2 scope, but the contract
     should be decided now since PROJECT.md calls exit codes "part of the contract").

2. **Is shallow-clone detection in scope for Phase 1, a later phase, or not at all?**
   - What we know: PITFALLS.md (project-level research) flags shallow clones as a
     silent-wrong-data risk with no error raised, common in CI (`actions/checkout`
     default `fetch-depth: 1`).
   - What's unclear: it is not listed in REQUIREMENTS.md's v1 requirements or its Out of
     Scope table — it simply isn't mentioned at the requirements level at all.
   - Recommendation: treat as out of scope for Phase 1 as currently planned (not
     blocking), but flag to the user/planner as a possible requirements gap — this can
     be resolved with a one-line `rev-parse --is-shallow-repository` check added
     cheaply in Phase 1's `validate_repo` if the user wants it, since it fits naturally
     alongside the two checks already being built there.

3. **Display format for author identity in the table: name only, or `name <email>`?**
   - What we know: DATA-01 says "per-author"; the aggregation key should be
     `(name, email)` per Assumption A2.
   - What's unclear: REQUIREMENTS.md's example success criteria only says "per author"
     without specifying the displayed column format.
   - Recommendation: display name only in the table (simpler, matches `git shortlog`'s
     convention per project FEATURES research), but note this in the plan so the
     planner makes it an explicit task decision rather than an implicit one.

4. **Should Phase 1 include any ad-hoc/smoke verification, given QUAL-01 (the real
   fixture test suite) is scoped to Phase 2?**
   - What we know: `nyquist_validation` is disabled in this project's config, so this
     research document does not include a formal Validation Architecture section, and
     the roadmap explicitly defers the full pytest fixture suite to Phase 2.
   - What's unclear: whether Phase 1's plan should still include lightweight
     inline checks (e.g. a `__main__` smoke script or a couple of ad-hoc assertions)
     given how correctness-critical this phase is, or defer *all* verification to
     Phase 2 as roadmapped.
   - Recommendation: the planner should still specify concrete manual/automated
     verification steps per task (e.g., "run against the fixture repo built in this
     research session's probe scripts and confirm binary/merge/rename/non-UTF-8 cases
     don't crash") even without a formal pytest suite yet, since QUAL-01's full suite
     coming in Phase 2 is a documentation/regression-proofing pass, not the first time
     these cases get exercised.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `git` CLI | Entire pipeline (subprocess boundary) | Yes | 2.53.0 [VERIFIED: local `git --version`] | None needed — no fallback path exists per PROJECT.md's design ("shells out to git by design") |
| Python 3 | Runtime | Yes | 3.14.4 [VERIFIED: local `python3 --version`] | None needed |

No missing dependencies. No fallback logic required for this phase.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Local single-user CLI, no auth surface |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | Operates with the invoking user's own filesystem/git permissions; no privilege boundary crossed |
| V5 Input Validation | Yes | Always pass `subprocess.run([...])` as a list, never `shell=True`, never f-string command interpolation — the repo path and (in Phase 2) `--since` value are user-supplied strings that must never reach a shell. Already the plan in ARCHITECTURE.md's Anti-Pattern 2 |
| V6 Cryptography | No | No cryptographic operations |
| V7 Error Handling / Logging | Yes | Never print git's raw stderr directly as the tool's own error message (PITFALLS.md UX Pitfall) — catch the two specific pre-flight failure modes and print gitwho's own plain-language message; reserve raw stderr surfacing for a genuinely unexpected/unhandled `GitError` only |
| V12 Files and Resources | Yes | The repo path argument is passed to `git -C <path>` — no path traversal risk beyond what the invoking user already has access to via their own shell, since this is a local CLI with no privilege elevation and no network exposure. No additional sanitization needed beyond the list-form subprocess call already required by V5 |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Shell/argument injection via unsanitized repo path or future `--since` value | Tampering | Never use `shell=True`; always pass argv as a `list[str]` to `subprocess.run` (verified pattern in Code Examples above) |
| Denial of service via unhandled `UnicodeDecodeError` on malformed author bytes | Denial of Service | Capture subprocess output as bytes (`text=False`), decode explicitly with `errors="replace"` — empirically verified this session (Pitfall #4) to be both the exact failure mode and the exact fix |
| Information disclosure via raw git stderr passthrough (e.g. leaking full filesystem paths or internal git diagnostics not meant for the tool's own users) | Information Disclosure | Low severity for a local CLI (the user already has filesystem access), but still worth wrapping per V7 above rather than printing git's raw fatal messages verbatim |

## Sources

### Primary (HIGH confidence)
- Local `git 2.53.0` binary — empirically executed this session for every claim tagged
  `[VERIFIED: local git 2.53.0]` above (pre-flight exit codes, control-byte format
  output, binary marker, rename behavior, merge-commit numstat suppression, non-UTF-8
  crash reproduction and fix).
- Local `python3 3.14.4` — empirically executed for subprocess decode-mode behavior.

### Secondary (MEDIUM confidence, carried forward from project-level research)
- `.planning/research/ARCHITECTURE.md` — pipeline shape, control-byte pattern rationale,
  git-fame precedent read directly via `gh api`.
- `.planning/research/PITFALLS.md` — full pitfall catalog, cross-referenced against
  official git-scm.com docs.
- `.planning/research/SUMMARY.md` — stack/version recommendations, phase-to-pitfall
  mapping.

### Tertiary (LOW confidence)
- None used this session — all phase-specific claims were empirically verified rather
  than sourced from web search, since the local environment has the exact git binary
  the tool will run against.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, versions confirmed via local probe, no ambiguity.
- Architecture: HIGH — the pipeline shape was inherited from project-level research
  (MEDIUM there) but every phase-specific mechanic (pre-flight exit codes, control-byte
  format, binary/merge/rename behavior, non-UTF-8 crash) was independently empirically
  reproduced this session against the actual git binary in this environment, raising
  confidence to HIGH for this phase's specific claims.
- Pitfalls: HIGH — five of five phase-relevant pitfalls (binary, merge, rename,
  non-UTF-8, not-a-repo/empty-repo conflation) were reproduced empirically, not just
  cited from documentation.

**Research date:** 2026-07-28
**Valid until:** Stable — git's `--numstat`/`rev-parse` behavior and Python's
`subprocess` API are not fast-moving; treat this as valid for the life of the project
unless the target git version changes materially (e.g. below git 2.x, which is not a
realistic deployment target).
