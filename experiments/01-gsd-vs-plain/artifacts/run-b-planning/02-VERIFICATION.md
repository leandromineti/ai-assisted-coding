---
phase: 02-filtering-json-output-and-release-readiness
verified: 2026-07-28T21:46:50Z
status: human_needed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read README.md top to bottom as a brand-new user would (no prior look at gitwho.py source). Paste each usage example (the plain table run and the combined `--since --json` run) and confirm they execute exactly as printed. Compare the table and JSON worked examples against a fresh run's actual output. Confirm the exit-code table communicates what a non-zero exit means. Finally run `python3 gitwho.py --json .` against this repository and confirm the output matches the documented seven-key schema."
    expected: "A new user can operate gitwho end to end from the README alone, the pasted examples run unmodified and produce the shown output, and the JSON schema in the README matches a live run."
    why_human: "This is Task 3's own `<human-check>` verification item in 02-01-PLAN.md, deliberately deferred from a mid-execution checkpoint to end-of-phase per this project's `workflow.human_verify_mode`. It asks for overall readability/usability judgment — whether a new user could operate the tool without reading source — which is a subjective quality assessment automated grep/structural checks cannot make. (Automated checks in this report already confirmed the two worked examples are byte-identical to real captured tool output, all 9 required headings are present, and the JSON block parses — but that is necessary, not sufficient, for 'a new user can operate it'.)"
---

# Phase 2: Filtering, JSON Output, and Release Readiness Verification Report

**Phase Goal:** Users can filter by date, consume output as JSON, and trust the tool via tests + README.
**Verified:** 2026-07-28T21:46:50Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

All truths were verified by running the real CLI against a freshly built fixture repository (`scripts/make_fixture_repo.sh`) and the real `unittest` suite — not by trusting SUMMARY.md's narrative.

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `--since DATE` restricts the summary to commits inside git's own date window; COMMITS total equals `git rev-list --count --since=DATE HEAD` (CLI-02) | VERIFIED | `python3 gitwho.py --since=2024-01-04T00:00:00+0000 <fixture>` prints 3 rows summing to 4 commits; `git -C <fixture> rev-list --count --since=2024-01-04T00:00:00+0000 HEAD` independently returns `4` — exact match |
| 2 | A `--since` window containing no commits (including an unparseable date) prints an empty result and exits 0, never an error (CLI-02) | VERIFIED | `python3 gitwho.py --since=2099-01-01T00:00:00+0000 <fixture>` — table prints header+separator, 0 data rows, `echo $?` = 0; `--json` variant prints exactly `[]`, exit 0 |
| 3 | `--json` prints valid JSON: top-level array, one object per author, keys `name, email, commits, added, deleted, first_commit, last_commit` (CLI-03) | VERIFIED | `python3 gitwho.py --json <fixture>` piped through `python3 -m json.tool` parses cleanly; 3 objects, each with exactly those 7 keys in that order |
| 4 | The JSON array is ordered identically to the table — both renderers go through `sorted_stats` (CLI-03, CLI-04) | VERIFIED | `grep -c 'sorted_stats(' gitwho.py` = 3 (definition + one call in each renderer); live JSON and table runs against the same fixture show identical author order (Ann, Bob, ` Bad` full-history; Bob, ` Bad`, Ann windowed) |
| 5 | `--since` and `--json` compose; `--json` only switches the renderer, never which commits are selected (CLI-02, CLI-03) | VERIFIED | `python3 gitwho.py --json --since=2024-01-04T00:00:00+0000 <fixture>` returns exactly the windowed 3-author set with correct per-author figures (Bob 2/1/0, ` Bad` 1/0/0, Ann 1/5/5) |
| 6 | The table and JSON never disagree for the same invocation (CLI-03) | VERIFIED | Same authors/figures/order confirmed pairwise between table and JSON runs above; `tests/test_gitwho.py::TestJsonOutput.test_json_matches_table_row_for_row` (real subprocess-driven) passes |
| 7 | `python3 -m unittest discover -s tests -v` passes, exercising real git fixtures (binary, merge, non-ASCII author, empty repo, non-repo dir), git never mocked (QUAL-01) | VERIFIED | Ran the real command: `Ran 21 tests in 1.188s` / `OK`. AST scan of `tests/test_gitwho.py` imports found no module containing `mock` and no third-party test runner — `['json','re','shutil','subprocess','sys','tempfile','unittest','gitwho','pathlib']` only |
| 8 | README.md documents usage, every flag, all three exit codes, and the merge-commit policy in the module docstring's own words (QUAL-02) | VERIFIED | All 9 required `##` headings present; `grep -q` of the exact merge-commit sentence succeeds against both `README.md` and `gitwho.py`; every `--`-flag from `gitwho.py --help` (`--since`, `--json`, `--help`) appears in the README; exit-code table has exactly 3 rows with `has no commits` / `not a git repository`; `committer date` and `mailmap` both documented; first ` ```json ` block parses |
| 9 | Phase 1 behaviour unregressed: default no-flag table still prints the same three rows/figures | VERIFIED | `python3 gitwho.py <fixture>` (no flags) prints `Ann Adams 3 10 5 2024-01-01 2024-01-04` and `Bob Brown 3 1 0 2024-01-03 2024-01-06`, matching Phase 1's verified figures exactly |

**Score:** 9/9 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `gitwho.py` | `--since` pass-through, `render_json`, shared `sorted_stats`; exports `sorted_stats, render_json, fetch_log, render_table, build_arg_parser, main`; contains `--since=`; ≥250 lines | VERIFIED | 274 lines. All named symbols present (`def fetch_log(path, since=None)`, `def sorted_stats`, `def render_json`, `def build_arg_parser`, `def main`, `def render_table`). Single `subprocess.run` call site (count=1). No `shell=True`/`text=True` in non-comment lines |
| `tests/test_gitwho.py` | Stdlib unittest suite driving real CLI against real fixtures; ≥150 lines | VERIFIED | 295 lines. 21 tests across `TestTableOutput`, `TestSinceFilter`, `TestJsonOutput`, `TestErrorContract`; `make_fixture_repo.sh` referenced; no mocking imports (AST-verified); actually ran and passed |
| `README.md` | Usage/flags/JSON schema/exit codes/counting policy/test instructions; contains merge-commit sentence; ≥80 lines | VERIFIED | 194 lines. All required content present and cross-checked against source (see truth #8) |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `main` | `fetch_log` | `since=args.since` keyword forward | WIRED | `gitwho.py:263` — `raw = fetch_log(args.path, since=args.since)` |
| `fetch_log` | `git log` | `--since=` appended as one argv element | WIRED | `gitwho.py:100` — `args.append(f"--since={since}")`, only when `since is not None`; spread into the single `_run_git` call |
| `sorted_stats` | `render_table` / `render_json` | both renderers call the shared ordering helper | WIRED | `sorted_stats(` appears 3 times in non-comment lines: 1 definition, 1 call each in `render_table` and `render_json` |
| `render_json` | `json.dumps` | JSON built only via stdlib serializer | WIRED | `gitwho.py:221` — `return json.dumps(rows, indent=2)`; no string concatenation building JSON anywhere in the file |
| `tests/test_gitwho.py` | `scripts/make_fixture_repo.sh` | suite builds its fixture with the real Phase 1 builder | WIRED | `grep -q 'make_fixture_repo.sh' tests/test_gitwho.py` succeeds; confirmed the suite's `setUpModule` invokes it via `subprocess.run` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| `--since` window agrees with `git rev-list --count` | `python3 gitwho.py --since=2024-01-04T00:00:00+0000 <fixture>` vs `git -C <fixture> rev-list --count --since=... HEAD` | Both report 4 | PASS |
| `--json` full output is valid, correctly ordered, correctly keyed | `python3 gitwho.py --json <fixture> \| python3 -m json.tool` | 3 objects, exact figures, matches Measured fixture table verbatim | PASS |
| Empty `--since` window is `[]` / 0 exit, both renderers | `python3 gitwho.py [--json] --since=2099-01-01T00:00:00+0000 <fixture>` | `[]` and header-only table, `$?`=0 in both | PASS |
| Phase 1 no-flag table unregressed | `python3 gitwho.py <fixture>` | Matches Phase 1 verified rows exactly | PASS |
| Real test suite (not a claim, an execution) | `python3 -m unittest discover -s tests -v` | `Ran 21 tests in 1.188s` / `OK` | PASS |
| No mocked git in test suite (structural) | AST scan of `tests/test_gitwho.py` imports | `['json','re','shutil','subprocess','sys','tempfile','unittest','gitwho','pathlib']`, no `mock`/pytest/nose | PASS |
| Security regressions absent | `grep -v '^\s*#' gitwho.py \| grep -E 'shell=True\|text=True'` | No match; `subprocess.run` count = 1 | PASS |
| Git commits referenced in SUMMARY exist | `git cat-file -e 671a6f5 f6473d3 c831392 74b2fb8` | All 4 present in repo history | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| CLI-02 | 02-01 | `--since DATE` restricts window via git's own date parsing | SATISFIED | Truths #1, #2, #5; `TestSinceFilter` (4 tests, all pass) |
| CLI-03 | 02-01 | `--json` emits the same data machine-readably | SATISFIED | Truths #3, #4, #5, #6; `TestJsonOutput` (5 tests, all pass) |
| QUAL-01 | 02-01 | Tests cover real git path via fixtures, no mocked git | SATISFIED | Truth #7; 21/21 tests pass, AST-verified no mocking |
| QUAL-02 | 02-01 | README documents usage/flags/exit codes/merge policy | SATISFIED | Truth #8; all structural gates pass |

REQUIREMENTS.md's Phase 2 traceability table lists exactly these 4 IDs (CLI-02, CLI-03, QUAL-01, QUAL-02), and the PLAN frontmatter's `requirements:` field declares exactly the same 4. No orphaned requirements.

### Anti-Patterns Found

None. Scanned `gitwho.py`, `tests/test_gitwho.py`, and `README.md` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and stub/empty-return language — zero real matches. Two README lines contain the word "placeholder" but both refer to git's `%an`/`%aN` *format placeholders* (a documentation term describing git's own log-format syntax), not to incomplete gitwho code — confirmed false positive by reading context.

### Human Verification Required

### 1. README end-to-end readability and example fidelity (harvested from 02-01-PLAN.md, Task 3 `<human-check>`)

**Test:** Read `README.md` top to bottom as a brand-new user would. Paste and run each usage example. Compare the worked table and JSON examples against a fresh live run. Confirm the exit-code table is clear. Finally run `python3 gitwho.py --json .` against this repository and check the output matches the documented schema.

**Expected:** A new user can operate gitwho end to end from the README alone with no need to open `gitwho.py`; pasted examples run unmodified and match the shown output.

**Why human:** This is Task 3's own plan-authored human-check item, deferred to end-of-phase per this project's verification workflow rather than run mid-execution. It is a subjective usability/readability judgment. Automated checks in this report already confirm the mechanical facts underneath it — the two worked examples in the README are byte-identical to real output captured in this verification run against a fresh fixture, all 9 required headings exist, and the JSON block parses — but "could a new user operate this without reading source" is not something grep can certify.

### Gaps Summary

No gaps. Every observable truth, artifact, and key link required by the phase goal and by REQUIREMENTS.md was independently reproduced by executing real commands against a freshly built fixture repository and by running the actual `unittest` suite (21/21 passing, no mocked git, AST-verified). The `--since` window figures, the JSON schema and ordering, the empty-window zero-exit behaviour, and the Phase 1 regression check all matched the plan's "Measured fixture expectations" exactly on independent re-execution — nothing needed correction.

The single item routed to human verification is not a functional gap: it is a plan-authored subjective-quality checkpoint (README readability from a new user's perspective) that this project's workflow deliberately defers to end-of-phase rather than skips. All structural/mechanical facts underneath that checkpoint are already confirmed above.

**Process note (not a phase-goal gap):** `.planning/ROADMAP.md`'s Phase 2 checkbox (`[ ]`) and its progress-table status (`In Progress`, no completion date) have not been updated to reflect the phase's actual completion, even though the Plans row shows `1/1` and `.planning/STATE.md` shows `completed_phases: 2`. This is the same bookkeeping gap already flagged in Phase 1's verification and does not affect whether the phase goal is achieved in the codebase.

---

_Verified: 2026-07-28T21:46:50Z_
_Verifier: Claude (gsd-verifier)_
