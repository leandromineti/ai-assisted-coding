---
phase: 02-filtering-json-output-and-release-readiness
plan: 01
subsystem: cli
tags: [git, json, argparse, unittest, stdlib-only, readme]

# Dependency graph
requires:
  - phase: 01-core-summary-command
    provides: "gitwho.py's pure pipeline (fetch_log/parse_log/aggregate/render_table), the AuthorStats aggregate shape, and scripts/make_fixture_repo.sh"
provides:
  - "--since DATE pass-through into the single git log call (CLI-02)"
  - "--json renderer emitting a top-level array with the fixed 7-key schema (CLI-03)"
  - "sorted_stats — the single shared ordering helper both renderers call (P2-08 anti-drift)"
  - "tests/test_gitwho.py — 21-test stdlib unittest suite against real git fixtures, no mocked git (QUAL-01)"
  - "README.md — usage, flags, JSON schema, exit codes, counting policy, identity policy, test instructions (QUAL-02)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single ordering helper (sorted_stats) shared by both renderers so table and JSON output can never drift out of sync"
    - "json.dumps(..., indent=2) with default ensure_ascii=True — non-ASCII author bytes escape to \\uXXXX rather than risk an encoding failure on any stdout"
    - "--since is a pure pass-through: gitwho never parses or validates the date, it appends one argv element and lets git's own approxidate parser decide"
    - "Test suite drives the real CLI as a child process (subprocess, not in-process main() calls) so the published exit-code contract is what's actually tested"

key-files:
  created:
    - tests/test_gitwho.py
    - README.md
  modified:
    - gitwho.py

key-decisions:
  - "Unwrapped the module docstring's merge-commit sentence onto a single line (Rule 1 - bug). Phase 1 had wrapped it across two lines; Task 3's verification requires the exact sentence to match verbatim via a single-line grep against both gitwho.py and README.md, which the wrapped form could never satisfy."
  - "Added a direct pure-function test (test_sorted_stats_pure_function_matches_cli_order) that imports gitwho and calls sorted_stats/aggregate/parse_log in-process, per the plan's instruction that the module be 'importable for the few direct pure-function assertions' — all other tests drive the CLI as a real subprocess."

requirements-completed: [CLI-02, CLI-03, QUAL-01, QUAL-02]

coverage:
  - id: D1
    description: "--since DATE restricts the summary to commits inside git's own date window; the COMMITS total agrees with git rev-list --count --since=DATE HEAD"
    requirement: "CLI-02"
    verification:
      - kind: integration
        ref: "tests/test_gitwho.py#TestSinceFilter.test_since_agrees_with_git_rev_list_count"
        status: pass
      - kind: integration
        ref: "tests/test_gitwho.py#TestSinceFilter.test_since_future_date_yields_empty_table_and_exit_zero"
        status: pass
    human_judgment: false
  - id: D2
    description: "--json prints the same per-author data as the table, as a valid JSON array with the fixed 7-key schema, ordered identically to the table via the shared sorted_stats helper"
    requirement: "CLI-03"
    verification:
      - kind: integration
        ref: "tests/test_gitwho.py#TestJsonOutput.test_json_key_order_and_types"
        status: pass
      - kind: integration
        ref: "tests/test_gitwho.py#TestJsonOutput.test_json_matches_table_row_for_row"
        status: pass
      - kind: integration
        ref: "tests/test_gitwho.py#TestJsonOutput.test_json_empty_window_is_empty_array"
        status: pass
    human_judgment: false
  - id: D3
    description: "python3 -m unittest discover -s tests -v passes from the repository root, exercising real git fixture repositories (binary file, merge commit, non-ASCII author, empty repo, non-repo directory) with no mocked git anywhere"
    requirement: "QUAL-01"
    verification:
      - kind: unit
        ref: "python3 -m unittest discover -s tests -v — 21 tests, OK, ~1.2s"
        status: pass
      - kind: other
        ref: "AST scan of tests/test_gitwho.py imports — no module containing 'mock', no third-party test runner"
        status: pass
    human_judgment: false
  - id: D4
    description: "README.md documents usage, every argparse flag, all three exit codes, and the merge-commit line-stats policy in the same words as the module docstring"
    requirement: "QUAL-02"
    verification:
      - kind: other
        ref: "grep -q of the exact merge-commit sentence against both README.md and gitwho.py; grep of every long --help flag against README.md"
        status: pass
      - kind: other
        ref: "README.md's json fenced code block parses under python3 -m json.tool"
        status: pass
    human_judgment: true
    rationale: "Task 3's <verify> includes a human-check item — read README top to bottom as a new user would and confirm the examples run as printed. The automated gates above confirm structural correctness (headings, exact strings, valid JSON) but not overall readability/usability."
  - id: D5
    description: "Phase 1 behaviour is unregressed: the default no-flag table against the fixture still prints the same three rows with the same figures"
    verification:
      - kind: integration
        ref: "tests/test_gitwho.py#TestTableOutput (all 6 methods) plus the plan's own <verification> step 3 fixture check"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-28
status: complete
---

# Phase 2 Plan 01: Filtering, JSON Output, and Release Readiness Summary

**`--since`/`--json` wired through gitwho.py's existing pipeline behind one new shared `sorted_stats` ordering helper, a 21-test stdlib `unittest` suite proving it all against real git fixtures with zero mocked git calls, and a README documenting the full CLI contract.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-28T21:20:00Z (approx)
- **Completed:** 2026-07-28T21:43:27Z
- **Tasks:** 3
- **Files modified:** 3 (gitwho.py, tests/test_gitwho.py, README.md)

## Accomplishments

- `gitwho.py` gained `--since DATE` (a pure pass-through appended as one argv element to the single `git log` call) and `--json` (a new pure `render_json` renderer built only via `json.dumps`), both routed through a new `sorted_stats` helper that is now the single place either renderer decides row order — the anti-drift link required by P2-08.
- `tests/test_gitwho.py`: 21 stdlib `unittest` tests across `TestTableOutput`, `TestSinceFilter`, `TestJsonOutput`, and `TestErrorContract`, all driving `gitwho.py` as a real child process against fixtures built by the real `scripts/make_fixture_repo.sh` — no mocking library imported anywhere (AST-verified), full suite runs in ~1.2s.
- `README.md`: usage, the full flag table, the `--since`/git-date-parsing caveats, the JSON schema, the exit-code table, the commit-counting policy (quoting the module docstring verbatim), the `.mailmap` non-behavior, and the test-running instructions — every example captured from a real run of the fixture repository.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "narrow the window and hand it to a script"** — `671a6f5` (feat) — tracer task; `--since`/`--json` wired through every layer, verified end-to-end before expansion
2. **Task 2: The QUAL-01 proof** — `f6473d3` (test)
3. **Task 3: README** — `c831392` (docs; also carries the Rule 1 docstring fix)

**Plan metadata:** _(pending — this commit)_

## Files Created/Modified

- `gitwho.py` (modified) — `+import json`, `fetch_log(path, since=None)`, `sorted_stats(stats)`, `render_json(stats)`, `--since`/`--json` argparse flags, `main` renderer dispatch, docstring update (274 lines)
- `tests/test_gitwho.py` (created) — 4 test classes, 21 tests, module-scoped fixtures built once via `scripts/make_fixture_repo.sh` (295 lines)
- `README.md` (created) — 9 required headings, worked examples captured from a real fixture run (194 lines)

## Decisions Made

- **Docstring line-wrap fix (Rule 1):** Phase 1's module docstring wrapped the merge-commit sentence across two source lines ("...commit for their author and\ncontribute no line stats."). Task 3's plan-level verification step 5 requires `grep -q 'Merge commits count as one commit for their author and contribute no line stats'` to succeed against **both** `gitwho.py` and `README.md` — a single-line grep that the wrapped form could never satisfy, even though the shorter substring `'contribute no line stats'` (Phase 1's own gate) still matched. Fixed by putting the full sentence on one line in the docstring; no behavioral change, verified no regression via the full Phase 1 acceptance-criteria re-run and the new test suite.
- No figure in the plan's "Measured fixture expectations" tables needed correction. Every commit count, added/deleted figure, and date in both the full-history and `--since=2024-01-04T00:00:00+0000` windows matched exactly on first run, including the tie-break ordering (` Bad` author sorting before `Ann Adams` on name).
- Final JSON key set as shipped, in fixed order: `name`, `email`, `commits`, `added`, `deleted`, `first_commit`, `last_commit` — exactly as P2-02 specified.
- Test suite: 21 tests (comfortably above the required 18), full run in ~1.2s (well under the 60s budget).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Unwrapped the merge-commit sentence in gitwho.py's docstring onto one line**
- **Found during:** Task 3 (README verification gate)
- **Issue:** The module docstring inherited from Phase 1 wrapped "Merge commits count as one commit for their author and contribute no line stats." across two source lines. Task 3's plan-level `<verification>` step 5 requires the exact sentence, on one line, to `grep` successfully against both `gitwho.py` and `README.md` — a real correctness requirement (README and source must state the policy identically), not a style preference.
- **Fix:** Reformatted the docstring so the sentence occupies a single line, adding a blank line before/after for readability. No other text changed.
- **Files modified:** `gitwho.py`
- **Verification:** `grep -q 'Merge commits count as one commit for their author and contribute no line stats' gitwho.py` now succeeds; full Task 1 acceptance criteria and the 21-test suite re-run clean after the change (no behavioral regression).
- **Committed in:** `c831392` (part of Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix, discovered by the plan's own verification gate)
**Impact on plan:** Docstring formatting only; no change to any function's behavior or the CLI contract. No scope creep.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. Stdlib-only, nothing to install.

## Next Phase Readiness

- `gitwho` is v1-shippable: the CLI surface (`path`, `--since`, `--json`), the exit-code contract (0/1/2), and the JSON schema (7 keys, fixed order) are all locked, tested, and documented.
- The `sorted_stats` helper is the durable anti-drift guarantee for any future third rendering mode (e.g. CSV, explicitly out of scope for v1 per REQUIREMENTS.md).
- `CLI-07` (`--until DATE`) remains a deferred v2 requirement; not touched here.
- No blockers.

---
*Phase: 02-filtering-json-output-and-release-readiness*
*Completed: 2026-07-28*

## Self-Check: PASSED

All created/modified files verified present on disk (gitwho.py, tests/test_gitwho.py, README.md, this SUMMARY). All three task commit hashes (671a6f5, f6473d3, c831392) verified present in `git log --oneline --all`. Full plan-level `<verification>` block (7 steps) re-run clean after the Task 3 docstring fix.
