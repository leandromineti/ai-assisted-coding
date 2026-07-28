# Run log — appended during the runs, not reconstructed

## Run A — plain

- 17:33 preregistration committed (`907feb7`). Run A starts.
- 17:34 Run A complete. **~1 minute wall-clock.**
  - Model invocations: **1 orchestrator turn, 0 subagents** (three file writes + one
    test/smoke command batch).
  - Artifacts: 3 files, 224 lines — `gitwho.py` 122, `test_gitwho.py` 82, `README.md` 20.
    Product:process ratio — all product, zero process files.
  - Tests: 5/5 pass; they build **real throwaway git repos** (no mocked git — the
    llm-coding-benchmark trap avoided by construction). Smoke: real repo table correct,
    non-repo dir exits 2.
  - Handled unprompted: binary-file `-` in numstat, author-name column widths.
  - Not handled (noticed later, honest gap): author disambiguation by email (same name
    different email counts as one; `.mailmap` ignored).

## Run B — GSD

- 17:35 fresh repo initialized at scratchpad/toy-gsd (git, personal identity).
- 17:35 `/gsd-new-project` invoked. **Protocol deviation, as preregistered:** run
  executed in GSD's own auto-mode shape — the preregistered task text serves as the idea
  document; config = GSD's recommended defaults; no interactive questioning. Logged
  config: `mode=yolo, granularity=coarse, parallelization=true, commit_docs=true,
  model_profile=balanced, research=true, plan_check=true, verifier=true,
  drift_guard=true`.
- 17:36 config.json written + committed (GSD commit 1: `3e086dd`). Note: GSD's tooling
  (`gsd-tools.cjs config-new-project`, `query commit`) is deterministic CLI code, not
  model calls — the framework runs real code for bookkeeping.
- 17:36 PROJECT.md synthesized from the task text + committed (GSD commit 2: `1b1521d`).
  Notable: the template *forced* an Out of Scope section — the `.mailmap`/identity gap
  that run A only noticed after the fact got written down **before any code existed**.
  First concrete "structure helped" data point.
- 17:37 research step: **4 parallel `gsd-project-researcher` subagents spawned**
  (STACK / FEATURES / ARCHITECTURE / PITFALLS), model sonnet per config and the standing
  subagent rule. This is the single biggest ceremony line-item so far: four model
  contexts for a ~150-line CLI. Waiting.
- 17:40 FEATURES researcher done: **54k tokens, 13 tool uses, 2.6 min** (web-searched
  git shortlog / git-fame / git-quick-stats / onefetch). Verdict: scope already covers
  all table stakes; first/last-commit-date column is the one novel feature; suggests
  `--until` for v1.x. Assigned its own confidence levels honestly (MEDIUM, one LOW).
- 17:41 STACK researcher done: **54k tokens, 15 tool uses, 3.3 min.** Verified the
  `git log --pretty` + `--numstat` mechanism against git-scm.com rather than training
  data; recommends `%x1f` unit separators + `%aI` ISO dates (run A used `%x00` + short
  dates — the researcher's format is more robust). Anti-recommendations list
  (GitPython, click, rich) matches run A's implicit choices. Surfaced a real ambiguity
  run A never considered: does "stdlib only" cover dev/test tooling (pytest vs unittest)?
- 17:43 PITFALLS researcher done: **69k tokens, 19 tool uses, 4.9 min.** The heavyweight
  of the four, and the one that found real defects in run A's implementation: **run A
  never decided a merge-commit policy** (git's default numstat emits no diff for merges —
  silent), **doesn't pin `--no-renames`** (ambient `diff.renames` config changes the
  column format), **doesn't force locale/encoding**, and would silently accept a shallow
  clone's truncated history. None of these is covered by run A's tests. This is the
  strongest pro-structure evidence so far — and it came from the researcher run A's
  workflow simply doesn't have.
- 17:44 ARCHITECTURE researcher done: **72k tokens, 22 tool uses, 5.3 min.** Read
  git-fame's production source via `gh api` (primary evidence, not summaries); confirmed
  the merge-commit undercount trap and recommends `\x1f`/`\x1e` control-byte delimiters
  over run A's `\x00`+tab. Prescribes the pure-parser architecture (one impure `run_git`
  boundary feeding pure `parse → aggregate → render`) — run A's shape is close but its
  parser isn't pure (collect() shells out internally, so unit tests can't feed it
  literal numstat text).
- **Research phase totals: 4 subagents, ~250k tokens, 69 tool uses, ~5.5 min wall
  (parallel).** Run A's entire build was 1 turn and ~1 minute. The research alone is
  roughly two orders of magnitude more token-spend than run A's whole run.
- 17:46 synthesizer spawned (sonnet). Framework observation worth keeping: the workflow
  ships a documented **self-heal for a known LLM false-refusal** (their issue #222 — the
  synthesizer sometimes returns SUMMARY.md inline while fabricating a claim that file
  writes are blocked; the orchestrator is instructed to detect the template markers and
  persist the file itself). GSD encodes defenses against its own agents' failure modes —
  the methodology-as-prose contains production bug fixes, the layer-4 analogue of
  opencode's content-filter comment.
- 17:47 synthesizer done: **78k tokens, 9 tool uses, 3 min.** SUMMARY.md written and
  committed (GSD commit 3: `3d76459`). Two cross-layer frictions observed, both
  self-healed:
  1. **Harness guard vs framework requirement:** the subagent's Write tool refused
     SUMMARY.md as a "report file" (a layer-2/3 policy: subagents should return text,
     not write reports). But GSD *requires* the file on disk for the roadmapper. The
     agent worked around it via Bash heredoc and flagged it honestly. A layer-4
     methodology colliding with a layer-2 permission surface — the taxonomy's
     cross-layer bleed, observed live.
  2. **Deterministic validator false positive:** `gsd-tools verify-summary` returned
     `passed: false` because it parsed the ARCHITECTURE researcher's citation of
     git-fame's source (`gitfame/_gitfame.py`, an external repo it read via gh api) as
     a local file that should exist. The file-existence heuristic can't tell citations
     from deliverables. Proceeded on the workflow's own substantive-check rule (file
     exists, 144 lines, no truncation sentinel).
- 17:47 REQUIREMENTS.md written by orchestrator (auto mode) + committed (GSD commit 4:
  `1779b9b`). 13 v1 requirements — and this is where research became *checkable*:
  DATA-02 (binary markers), DATA-03 (`--no-renames` pin), DATA-04 (merge policy),
  DATA-05 (encoding) all derive from the pitfalls research. **Run A satisfies none of
  those four.** QUAL-01 mandates fixture-repo tests, no mocked git.
- 17:48 roadmapper spawned (sonnet).
- 17:49 roadmapper done: **55k tokens, 12 tool uses, 2 min.** 2 phases, 13/13
  requirements mapped, traceability table filled. Good judgment observed: research
  suggested 3 phases; the roadmapper collapsed to 2 because the pipeline-only phase had
  "no independent user-observable surface" — it pushed back on its own input rather than
  rubber-stamping. Roadmap + STATE committed (GSD commit 5: `40a6deb`).
- **new-project flow complete at 17:49: ~14 min wall, 6 subagents (~438k subagent
  tokens), 5 planning commits, 8 planning documents, zero lines of product code.**
  Now `/gsd-plan-phase 1`.
- 17:51 plan-phase init: planner gets **opus** (config `balanced` profile: opus for
  planning, sonnet elsewhere) — matches the standing subagent rule with no clamping
  needed. Hook discovery: config-new-project seeded `ai_integration`, `ui`, and
  `pattern_mapper` hooks **true by default**; all three are void here (no AI component,
  no frontend, empty repo — nothing to pattern-match) and skip on their own
  applicability conditions. Ceremony observation: the default config carries
  enterprise-shaped hooks even for a 200-line CLI; a user who didn't inspect them would
  pay three no-op skill/agent dispatches.
- 17:52 phase researcher spawned (sonnet), explicitly instructed to build on the
  project research rather than repeat it. No CONTEXT.md exists (discuss-phase not run —
  it's optional and was skipped as part of the auto chain).
- 17:58 phase researcher done: **107k tokens, 17 tool uses, 6 min — the most valuable
  subagent of the run so far.** Qualitatively different from the project researchers: it
  **empirically reproduced** every DATA requirement against local git 2.53 — built a
  fixture repo (binary file, --no-ff merge, rename), hand-crafted a commit object with
  genuinely invalid UTF-8 via `git hash-object` to reproduce the DATA-05 crash and its
  fix, and discovered that **both pre-flight failures return exit 128** (must branch on
  which check failed, not the code — sharpens the project-level pitfall). Also caught
  CLI-06's exit code as underspecified in requirements ("non-zero" — recommends 1 vs
  not-a-repo's 2) and noted a genuine requirements gap (shallow-clone detection was in
  project research but never became a requirement). Research → requirements → phase
  research is behaving like a *refinement funnel*, each stage catching what the
  previous one left vague.
- 18:00 planner spawned (**opus** per balanced profile). Deviations logged: no
  SPEC.md/CONTEXT.md exist (optional stages not in the auto chain), so the planner
  derives must_haves from the phase's success criteria directly; tracer-first default
  active; told to lock the exit-code decision (1 for empty repo).
- 18:11 planner done: **141k tokens, 30 tool uses, 10.6 min — the single most expensive
  agent of the run.** 1 plan, 3 tasks, tracer-first. What justifies the cost: it *ran*
  its own verification gates before committing — the fixture-repo recipe executes and
  every expected figure in the plan is a **measured** value (Ann Adams 3/10/5…), not an
  estimate; and two real parser traps were found by dry-running: git emits a **blank
  line between the record header and the first numstat line**, and bare `mktemp -d`
  under a TMPDIR inside a git repo would corrupt the not-a-repo gate. Six decisions
  locked and numbered (P-01..P-06). Ceremony flag: a **STRIDE threat model at ASVS L1**
  for a read-only local CLI — three entries have real gates, but threat-modeling a
  150-line stdlib script is the ceremony-floor question in miniature. GSD commit 6:
  `ff3f8b2`.
- 18:12 plan-checker spawned (sonnet). Also noteworthy: the planner's handoff says
  "run `/clear` for a fresh context window before executing" — GSD assumes context
  hygiene between stages, which the experiment's single-session design violates
  (logged as a limitation; subagent stages are isolated anyway).
- 18:13 plan-checker done: **75k tokens, 4 tool uses, ~1 min. 0 blockers, 2 warnings.**
  Warning 2 is a real catch: the plan's `must_haves` claims zero-argument invocation
  works, but every automated gate passes an explicit path — the exact invocation form
  in the truth statement is untested. (Warning 1 is bookkeeping: research Open
  Questions not marked RESOLVED.) 13 verification dimensions checked, most auto-skipped
  as N/A for this project shape. YOLO + 0 blockers → proceed without a planner
  iteration; warnings carried to execution notes.
- 18:15 executor spawned (sonnet), **main-tree mode** — single-plan wave, so worktree
  isolation would be pure bootstrap tax with nothing to isolate against (logged as a
  judgment call; GSD's own per-plan worktree gate exists for related reasons). The
  checker's zero-arg-invocation warning passed to the executor as an explicit
  verification addition. This is the first moment in the GSD run where product code
  gets written — **40 minutes in.**
- 18:21 executor done: **141k tokens, 52 tool uses, ~6 min.** 3/3 tasks, 4 atomic
  commits (tracer → fixture proof → error slice → metadata). Product: `gitwho.py` 227
  lines + `scripts/make_fixture_repo.sh` 85 lines. All plan gates passed **including
  the checker's zero-arg addition** — the warning found upstream got closed downstream,
  the loop working end-to-end. Bonus empirical find: `.mailmap` does NOT affect output
  because the format uses `%an` (raw) not `%aN` (mailmap-applied) — the exact open
  question the FEATURES researcher had flagged, now answered by the executor. One
  deviation (added `.gitignore`, Rule 2 hygiene), one tooling wart (`state.advance-plan`
  choked on a "TBD" placeholder in STATE.md; manually corrected).
- 18:24 verifier done: **105k tokens, 24 tool uses, 2.6 min. PASSED 8/8 must-haves** —
  against real execution, not summary claims. It exceeded its brief in the right way:
  re-ran the fixture with `git config diff.renames true` set (the ambient-config attack)
  and proved output byte-identical, and independently reproduced the `.mailmap`/%an
  finding. One bookkeeping nit (ROADMAP checkbox not ticked). **Phase 1 complete.**
- 18:25 Phase 2 begins (CLI-02 `--since`, CLI-03 `--json`, QUAL-01 tests, QUAL-02
  README). **Documented deviation:** phase-2 research skipped via the workflow's own
  `--skip-research` flag — it would be the *third* research pass over the same tiny
  domain, and both prior layers explicitly marked phase 2 "standard patterns, no
  research flags." Full plan → check → execute → verify ceremony retained.
- 18:39 phase-2 planner done: **166k tokens, 25 tool uses, 13.3 min — most expensive
  agent of the entire run** (research skipped, so it ran its own probes). Five measured
  git behaviors, four of which changed the plan: bare `--since` dates are
  **timezone-dependent** (4 commits under Asia/Tokyo vs 3 under UTC — mandated `+0000`
  offsets in all test literals); `--since` filters committer date while columns show
  author date; unparseable `--since` exits 0 with empty output (approxidate → "now" —
  can only be documented, not fixed, given CLI-02); `unittest discover -t .`
  importability trap. Also structural anti-drift design (one `sorted_stats` feeding
  both renderers + a pairwise JSON-vs-table test) and an **AST-based anti-mock gate**
  it verified can't be tripped by comments — it removed its own earlier grep-based
  gate for exactly that false-positive risk. Honest self-assessment: the ≥18-test and
  ≥80-line floors are judgment calls an executor could satisfy thinly. GSD commit:
  `0efada8`.
- 18:41 phase-2 checker done: **70k tokens, 4 tool uses, ~1 min. PASSED, 0 issues** —
  13 dimensions. Subtle competence note: it recognized the plan's `; test "$?" = "0"`
  idiom as deliberate exit-code capture, not error-swallowing — the checker carries a
  vocabulary of anti-pattern *exceptions*, not just anti-patterns.
- 18:42 phase-2 executor spawned (sonnet, main-tree).
- 18:50 phase-2 executor done: **176k tokens, 71 tool uses, ~8 min.** 3/3 tasks, 4
  commits. Product: `--since`/`--json` + `sorted_stats` anti-drift helper in gitwho.py,
  **21-test** stdlib unittest suite (real fixtures, no mocked git), README with JSON
  schema + exit codes + the merge/timezone/committer-date caveats. Every measured
  planning figure matched on first run. One Rule-1 deviation: phase 1's docstring had
  wrapped the merge-policy sentence, breaking the verbatim README↔docstring gate —
  unwrapped, regression-clean, documented.
- 18:51 phase-2 verifier spawned (sonnet) — final GSD stage.
- 18:54 phase-2 verifier done: **102k tokens, 16 tool uses, 2.7 min. 9/9 must-haves,
  status `human_needed`** — one deliberately deferred human-check (README readability,
  a subjective judgment it abstained on rather than auto-passing; the honest-verifier
  principle observed live). Confirmed README examples are byte-identical to real runs.
  Same ROADMAP-checkbox bookkeeping nit as phase 1 — the framework's own bookkeeping is
  its most consistently dropped ball.
- **GSD run complete ~18:54. Totals: ~78 min wall, 13 subagents, ~1.47M subagent
  tokens, 15 commits, 763 product LOC + ~3,750 planning-doc lines.**
- 18:48–18:55 head-to-head (compare.sh + invalid-UTF-8 probe): preregistered checks
  **tie 6/6** (7th check was a comparison-script bug — both tools right, Alice=3).
  Decisive delta on the deep case: **run A crashes (unhandled UnicodeDecodeError) on
  the invalid-UTF-8 author fixture; run B renders correctly.** Full results appended
  to README.md.

## Post-hoc cost measurement (2026-07-28, ~19:0x, pre-session-close)

Prompted by the direct question "are we counting token usage?" — the honest answer was
"only from notification metadata." Measured properly from the session transcript + 16
agent transcripts (`usage` fields):

| measured | run A | run B orchestrator | run B subagents |
|---|---|---|---|
| output | 16.8k | 186k | 346k |
| cache write | 26k | 2.54M | 5.34M |
| cache read | 8.5M | 91.9M | 49.7M |

Two corrections to the earlier accounting: the notification metric ("1.47M") is an
opaque ~4× blend of actual output; and the orchestrator — not the subagents — dominated
cost (~2/3 of estimated spend via 92M cache reads from one long-lived context).
Methodology rule 5c added with this as its scar.
