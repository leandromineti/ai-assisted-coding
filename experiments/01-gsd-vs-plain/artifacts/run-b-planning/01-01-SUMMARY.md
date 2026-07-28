---
phase: 01-core-summary-command
plan: 01
subsystem: cli
tags: [git, subprocess, argparse, dataclasses, stdlib-only]

# Dependency graph
requires: []
provides:
  - "gitwho.py — single-file stdlib-only CLI: validate_repo, fetch_log, parse_log, aggregate, render_table, main"
  - "scripts/make_fixture_repo.sh — 7-commit deterministic fixture (binary, rename, merge, non-UTF-8 author), reusable by Phase 2's QUAL-01 pytest suite"
  - "Exit-code contract: 0 success, 1 empty repo, 2 not-a-repo"
  - "Control-byte git log format and AuthorStats aggregate shape Phase 2's --json renderer will consume unchanged"
affects: [02-since-json-tests-readme]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single subprocess choke point (_run_git) — every git invocation flows through one function"
    - "Pure pipeline around one impure I/O boundary: fetch_log (impure) -> parse_log -> aggregate -> render_table (all pure)"
    - "Control-byte (\\x1e/\\x1f) record format instead of blank-line splitting"
    - "Byte-mode subprocess capture + explicit errors=\"replace\" decode (never text=True)"
    - "Pre-flight validation as two sequential rev-parse checks branched by which one failed, not by exit code"

key-files:
  created:
    - gitwho.py
    - scripts/make_fixture_repo.sh
    - .gitignore
  modified: []

key-decisions:
  - "validate_repo shipped as a no-op stub in Task 1's tracer commit, then fully implemented in Task 3 — an intentional incremental build per the plan's task split, not a deviation"
  - ".mailmap does NOT affect gitwho's output: %an (used in LOG_FORMAT) is the raw author name, unaffected by mailmap; only %aN (capital N) applies mailmap rewriting. Empirically verified this session. Confirms gitwho's stated scope of reporting whatever git reports, with no identity merging"
  - "Added .gitignore for __pycache__/ (Rule 2 — missing project hygiene, not present in the greenfield repo)"

requirements-completed: [DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, CLI-01, CLI-04, CLI-05, CLI-06]

coverage:
  - id: D1
    description: "python3 gitwho.py [path], defaulting to the current directory, prints a per-author table (commits, added, deleted, first/last date) sorted by commit count descending, agreeing with git's own commit count"
    requirement: "DATA-01"
    verification:
      - kind: manual_procedural
        ref: "python3 gitwho.py . — header matches ^AUTHOR +COMMITS +ADDED +DELETED +FIRST +LAST$, COMMITS column sums to git rev-list --count HEAD, column is non-increasing"
        status: pass
      - kind: manual_procedural
        ref: "python3 gitwho.py (zero-argument invocation) — same table, exit 0, confirms CLI-01 default path"
        status: pass
    human_judgment: false
  - id: D2
    description: "Binary file changes, merge commits, renames, and non-UTF-8 author names are all handled without crashing, with exact expected figures (DATA-02, DATA-03, DATA-04, DATA-05)"
    requirement: "DATA-02"
    verification:
      - kind: integration
        ref: "scripts/make_fixture_repo.sh fixture (7 commits) piped through gitwho.py — exact match on Ann Adams 3/10/5, Bob Brown 3/1/0, non-UTF-8 author 1/0/0, all rows summing to 7 = git rev-list --count HEAD"
        status: pass
    human_judgment: false
  - id: D3
    description: "Not-a-repo (including nonexistent path) exits 2; empty repo exits 1; both print gitwho's own stderr message and empty stdout; happy path unbroken"
    requirement: "CLI-05"
    verification:
      - kind: manual_procedural
        ref: "python3 gitwho.py <not-a-repo-dir> exits 2; python3 gitwho.py <nonexistent-path> exits 2; python3 gitwho.py <empty-git-init> exits 1; neither stderr contains 'fatal:'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Table reads correctly against a large real repository (human spot-check called out in Task 3's <verify> human-check)"
    human_judgment: true
    rationale: "Task 3's verify block includes a human-check item to visually confirm column alignment, plausible dates, and no stack traces against a large real repo the human recognizes. Automated gates in this SUMMARY already spot-checked this repo (6 commits) and the 7-commit fixture; a human with a large repo to compare against has not yet reviewed the rendered output."

# Metrics
duration: 15min
completed: 2026-07-28
status: complete
---

# Phase 1 Plan 01: Core Summary Command Summary

**Single-file stdlib-only `gitwho.py` CLI: one `git log --numstat` call parsed via a control-byte record format into a sorted per-author table, plus a 7-commit fixture repo proving binary/merge/rename/non-UTF-8 correctness and a two-check pre-flight (not-a-repo exits 2, empty-repo exits 1).**

## Performance

- **Duration:** 15 min
- **Started:** 2026-07-28T18:13Z (approx, first commit)
- **Completed:** 2026-07-28T21:15Z
- **Tasks:** 3
- **Files modified:** 3 (gitwho.py, scripts/make_fixture_repo.sh, .gitignore)

## Accomplishments

- `gitwho.py` implements the full pipeline: `_run_git` (single subprocess choke point) → `validate_repo` → `fetch_log` → `parse_log` → `aggregate` → `render_table`, wired into `main` with the documented 0/1/2 exit-code contract.
- `scripts/make_fixture_repo.sh` builds a deterministic 7-commit repository (binary file, feature-branch merge, rename, and a raw non-UTF-8-author commit object built via `git hash-object`) that Phase 2's QUAL-01 pytest suite will reuse.
- Every DATA-0x and CLI-0x requirement in this phase's frontmatter is proven against real git invocations — no requirement is asserted only by inspection.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "summarize this repo"** — `f4939f5` (feat) — tracer task; full happy-path pipeline, `validate_repo` stubbed intentionally per plan design
2. **Task 2: Prove the four correctness traps against a real fixture repository** — `c5e6ba0` (test)
3. **Task 3: Pre-flight validation slice** — `ff046a5` (feat)

**Plan metadata:** _(pending — this commit)_

## Files Created/Modified

- `gitwho.py` — the deliverable: single-file, stdlib-only, executable CLI (227 lines)
- `scripts/make_fixture_repo.sh` — deterministic fixture builder, 7 commits (85 lines)
- `.gitignore` — added `__pycache__/` and `*.pyc` (Rule 2 — project hygiene gap)

## Decisions Made

- `validate_repo` was shipped as a no-op stub in Task 1's tracer commit and fully implemented in Task 3, exactly as the plan specified ("Pre-flight validation and the error exit codes are Task 3's job; leave the single call site... clearly placed"). This is the plan's intended incremental build, not a deviation.
- **`.mailmap` observation (required by Task 2):** git's `%an` placeholder (used in `LOG_FORMAT`) is the *raw* author name and is **not** rewritten by a `.mailmap` file present in the repo. Only the capitalized `%aN` placeholder applies mailmap substitution. Verified empirically this session: copied the fixture repo, added a `.mailmap` mapping Bob Brown's identity to "Robert Brown", and confirmed `git log --format=%an` was unchanged while `git log --format=%aN` picked up the mapped name. Since gitwho's `LOG_FORMAT` uses `%an`, gitwho's output is unaffected by any `.mailmap` in the target repository — consistent with the project's stated out-of-scope decision on identity merging.
- No figure in Task 2's expected aggregate needed correction — all measured values (Ann Adams 3/10/5, Bob Brown 3/1/0, non-UTF-8 author 1/0/0, total 7 commits) matched exactly on first run.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added `.gitignore` for `__pycache__/`**
- **Found during:** Task 2 (after running `python3 -m py_compile` and the fixture script left a `__pycache__/` directory untracked in the working tree)
- **Issue:** Greenfield repo had no `.gitignore`; running the Python module leaves `__pycache__/*.pyc` as untracked cruft that would otherwise need per-run manual cleanup or risk accidental staging.
- **Fix:** Added `.gitignore` with `__pycache__/` and `*.pyc`.
- **Files modified:** `.gitignore`
- **Verification:** `git status --short` no longer lists `__pycache__/` as untracked after the ignore rule.
- **Committed in:** `c5e6ba0` (part of Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical / project hygiene)
**Impact on plan:** Purely additive hygiene fix; no scope creep, no change to `gitwho.py`'s behavior or contract.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. Stdlib-only, nothing to install.

## Next Phase Readiness

- The `AuthorStats` aggregate shape and `(name, email)` key are stable and ready for Phase 2's `--json` renderer to consume without reshaping.
- The control-byte `LOG_FORMAT` and the single-`git-log`-call pattern are locked; Phase 2's `--since` flag is a straightforward additional argv element to `fetch_log`.
- `scripts/make_fixture_repo.sh` is ready to be imported directly into Phase 2's QUAL-01 pytest suite as the fixture builder.
- Phase 2's README (QUAL-02) can document the exit-code contract (0/1/2) and the mailmap non-behavior directly from this SUMMARY.
- No blockers.

---
*Phase: 01-core-summary-command*
*Completed: 2026-07-28*

## Self-Check: PASSED

All created files verified present on disk (gitwho.py, scripts/make_fixture_repo.sh, .gitignore, this SUMMARY). All three task commit hashes (f4939f5, c5e6ba0, ff046a5) verified present in `git log --oneline --all`.
