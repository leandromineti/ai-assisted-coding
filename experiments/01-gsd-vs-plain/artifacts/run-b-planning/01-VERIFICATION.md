---
phase: 01-core-summary-command
verified: 2026-07-28T22:00:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 1: Core Summary Command Verification Report

**Phase Goal:** Running gitwho against a real git repository produces a correct, sorted per-author summary table, with clear pre-flight errors for invalid inputs.
**Verified:** 2026-07-28T22:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

All truths were verified by actually running `gitwho.py` against real git repositories (this repo plus a freshly built fixture repo), not by reading SUMMARY.md claims.

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `python3 gitwho.py` with no arguments inside a git repo prints a per-author table (commits/added/deleted/first/last), sorted by commit count descending (DATA-01, CLI-01, CLI-04) | VERIFIED | Ran `python3 gitwho.py .` — header exactly matches `^AUTHOR +COMMITS +ADDED +DELETED +FIRST +LAST$`; 1 data row (`Leandro Brioschi Mineti`) rendered with all 5 numeric/date columns populated |
| 2 | Sum of COMMITS column equals `git rev-list --count HEAD` (DATA-01, DATA-04) | VERIFIED | This repo: table shows 10, `git rev-list --count HEAD` = 10, match. Fixture repo: table sums to 7, `git rev-list --count HEAD` on fixture = 7, match |
| 3 | Binary-file change summarized without crashing; contributes 0 to both line counts (DATA-02) | VERIFIED | Fixture commit 3 (`img.png`, raw NUL bytes) → Bob Brown row shows `1 added, 0 deleted` total across all 3 of his commits (binary commit + merge + feature-branch add), i.e. binary contributed exactly 0 |
| 4 | Merge commit adds exactly 1 to commit count and 0 to line counts (DATA-04) | VERIFIED | Fixture merge commit (Bob Brown, 2024-01-06) — Bob's final row is 3 commits / 1 added / 0 deleted; the merge itself contributed the 3rd commit and 0 lines (his only added line came from the pre-merge feature commit) |
| 5 | Renamed file counted as delete+add, never brace-expansion, regardless of ambient rename config (DATA-03) | VERIFIED | Fixture rename (`a.txt`→`renamed.txt`) reflected as `+5/-5` matching exact expected figures. Additionally re-ran the fixture with `git config diff.renames true` set on the target repo (an ambient-config attack the plan explicitly calls out) — output was byte-identical, proving `--no-renames` neutralizes the ambient setting |
| 6 | Author with non-UTF-8 byte in commit object appears as a row and process exits 0 (DATA-05) | VERIFIED | Fixture commit 7 built via raw `git hash-object -t commit` with byte `0xE9` in the author field — row renders as `Andr<0xEF BF BD> Bad` (U+FFFD replacement char) with 1/0/0/2024-01-07/2024-01-07, and `echo $?` after the run confirmed exit code 0 |
| 7 | Directory that is not a git repo: gitwho's own stderr, empty stdout, exit 2 (CLI-05) | VERIFIED | Ran against a fresh empty (non-git) temp dir: exit=2, stdout empty, stderr = `gitwho: '<path>' is not a git repository` (no `fatal:` leak). Also verified the nonexistent-path sub-case separately: exit=2 |
| 8 | Git repo with no commits: gitwho's own stderr, empty stdout, exit 1 (CLI-06) | VERIFIED | Ran against `git init`-only repo: exit=1, stdout empty, stderr = `gitwho: '<path>' has no commits` (no `fatal:` leak) |

**Score:** 8/8 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `gitwho.py` | Whole pipeline; exports `GitError`, `NotARepoError`, `EmptyRepoError`, `FileStat`, `Commit`, `AuthorStats`, `validate_repo`, `fetch_log`, `parse_log`, `aggregate`, `render_table`, `build_arg_parser`, `main`; contains `--no-renames`; ≥120 lines | VERIFIED | 227 lines. All 13 named symbols confirmed present via grep. Compiles (`py_compile`), executable bit set, shebang correct. `--no-renames` present |
| `scripts/make_fixture_repo.sh` | Deterministic 7-commit fixture proving DATA-02..05; ≥40 lines | VERIFIED | 85 lines, executable, `set -euo pipefail`. Ran twice against fresh temp dirs — deterministic 7-commit repo produced each time, exact expected figures reproduced |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `main` | `validate_repo` | called as first statement after arg parsing; exception→exit-code mapping | WIRED | `validate_repo(args.path)` called at line 208 inside `try`/`except NotARepoError`→2 / `except EmptyRepoError`→1 |
| `fetch_log` | `git log` | single subprocess call with `--no-renames`, `--numstat`, control-byte `--format` | WIRED | Line 93-95: one `_run_git` call carrying all three; `subprocess.run` appears exactly once in the whole file (the single choke point in `_run_git`) |
| `parse_log` | `aggregate` | one `Commit` yielded per header record; `aggregate` increments `commits` once per `Commit`, not per file | WIRED | `parse_log` yields one `Commit` per `RS`-delimited record regardless of file count (line 121-127); `aggregate` does `author.commits += 1` once per commit (line 138), outside the per-file loop (line 139-141) — confirmed against the fixture's zero-file merge commit |
| `aggregate` | `render_table` | sort by `(-commits, name)` | WIRED | Line 156: `sorted(stats.values(), key=lambda s: (-s.commits, s.name))` — confirmed Ann Adams/Bob Brown tie on 3 commits resolved alphabetically as expected |

### Behavioral Spot-Checks

All three tasks' full `<verify><automated>` gate strings from the PLAN were re-run verbatim (not just individually grepped) against the real codebase and real repositories — this is stronger than a spot-check, it is full reproduction of the plan's own proof obligations.

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Task 1 gate string (compile, security greps, self-run against this repo, sort/sum checks) | Full Task 1 `<verify>` command | All sub-checks passed; table sum (10) matched `git rev-list --count HEAD` | PASS |
| Task 2 gate string (fixture build, 7 commits, exact 3-row match) | Full Task 2 `<verify>` command | All sub-checks passed; exact figures reproduced (Ann 3/10/5, Bob 3/1/0, non-UTF-8 author 1/0/0, sum 7) | PASS |
| Task 3 gate string (pre-flight checks, exit codes, no `fatal:` leak, happy path unbroken) | Full Task 3 `<verify>` command | All sub-checks passed; not-a-repo=2, nonexistent-path=2, empty-repo=1, happy path still 0 | PASS |
| Ambient `diff.renames=true` does not change output (DATA-03 stronger claim) | `git config diff.renames true` on fixture copy, re-run gitwho | Output byte-identical to the `--no-renames`-pinned run | PASS |
| `.mailmap` observation from SUMMARY | `git log --format=%an` vs `%aN` on a copy with `.mailmap` mapping Bob Brown→Robert Brown | `%an` unaffected (Bob Brown), `%aN` rewritten (Robert Brown) — confirms SUMMARY's claim that gitwho (which uses `%an`) is mailmap-independent | PASS |
| Only stdlib imports (AST-level check) | `ast.parse` + walk import nodes | `{argparse, dataclasses, datetime, os, subprocess, sys, typing}` — all stdlib | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| DATA-01 | 01-01 | Per-author commits/added/deleted/first/last from one `git log --numstat` call | SATISFIED | Table columns present and correct; single `fetch_log` call site |
| DATA-02 | 01-01 | Binary `-`/`-` markers handled, excluded from line counts | SATISFIED | Fixture binary commit contributes 0/0 |
| DATA-03 | 01-01 | Rename pinned via `--no-renames`, immune to ambient config | SATISFIED | `--no-renames` present; ambient `diff.renames=true` test confirmed no behavior change |
| DATA-04 | 01-01 | Merge commits count as 1 commit, 0 lines; policy documented | SATISFIED | Fixture merge commit contributes 1/0; docstring contains "contribute no line stats" |
| DATA-05 | 01-01 | Non-UTF-8 author names don't crash | SATISFIED | Raw 0xE9 byte fixture author renders as replacement-char row, exit 0 |
| CLI-01 | 01-01 | Repo path positional, defaults to cwd | SATISFIED | `nargs="?", default="."` in `build_arg_parser`; zero-arg invocation confirmed working |
| CLI-04 | 01-01 | Sorted by commit count descending | SATISFIED | `sorted(..., key=lambda s: (-s.commits, s.name))`; fixture output shows Ann/Bob (3 each, alpha tiebreak) above the 1-commit row |
| CLI-05 | 01-01 | Not-a-repo: clear error, exit 2, pre-flight not stderr-matching | SATISFIED | `validate_repo` branches purely on `returncode`, never on stderr text; exit 2 confirmed for both existing-non-repo-dir and nonexistent-path |
| CLI-06 | 01-01 | Empty repo: clear error, non-zero exit | SATISFIED | Exit 1 confirmed, distinct from CLI-05's 2 |

No orphaned requirements: REQUIREMENTS.md's Phase 1 traceability table lists exactly these 9 IDs, and the PLAN frontmatter's `requirements:` field declares exactly the same 9. All are checked off `[x]` in REQUIREMENTS.md and all are independently confirmed above, not merely trusted from the checkbox.

### Anti-Patterns Found

None. Scanned `gitwho.py` and `scripts/make_fixture_repo.sh` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`, placeholder language, and empty-return stubs — zero matches in both files.

### Human Verification Required

None required to certify the phase goal. (Note: Task 3's `<verify>` block includes an optional `human-check` item — "run against a large real repo you know and eyeball it" — which SUMMARY.md correctly flags as not yet performed by a human with an independently-known large repo. This is a nice-to-have sanity check beyond the phase's automatable success criteria, not a gap: every ROADMAP success criterion and every plan-declared must-have was independently reproduced above via real command execution against this repo and the fixture repo, which already exercises every correctness trap and error path the phase goal requires.)

### Gaps Summary

None. Every observable truth, artifact, and key link was independently verified by executing real commands against real git repositories (this project's own repo and a freshly built fixture repo), not by trusting SUMMARY.md's narrative. All figures matched exactly. An additional stress test beyond the plan's own gates (ambient `diff.renames=true`) was run and also passed, and the SUMMARY's `.mailmap` claim was independently reproduced and confirmed correct.

One process-level observation (not a phase-goal gap): `.planning/ROADMAP.md`'s Phase 1 checkbox and progress table (`0/1 plans complete`, unchecked `[ ]`) have not been updated to reflect completion, even though `.planning/STATE.md` correctly shows `completed_phases: 1` and 100% progress. This is bookkeeping only and does not affect whether the phase goal is achieved in the codebase.

---

_Verified: 2026-07-28T22:00:00Z_
_Verifier: Claude (gsd-verifier)_
