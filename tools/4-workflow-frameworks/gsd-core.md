---
name: gsd-core
category: 4
vendor: Open GSD
url: https://github.com/open-gsd/gsd-core
license: MIT
open_source: true
stack: [Markdown, Node]
version: v1.11.0
commit: 182f60b4
# PIN MOVED d04592de → fee72d55 at the 2026-08-18 deep-dive re-read, and fee72d55 → 182f60b4
# (= tag v1.11.0) at the 2026-08-21 release re-read (rule 4b: a pin moves only with a
# re-read; both were). exp-01 artifacts keep their own pin (d04592de).
first_commit: 2025-12-14
stars: 8540
stars_at: 2026-08-21
read_at: 2026-08-21   # v1.11.0 release re-read; deep-dive 2026-08-18 @ fee72d55, survey 2026-07-28 @ d04592de, exp-01 late July
depth: deep-dive   # 2026-08-18: runtime traced in source by three parallel readers, load-bearing claims spot-verified at the pin. 2026-08-21: same method over the fee72d55→v1.11.0 window (release substance; per-claim confrontation; provenance re-measurement)
harness_targets: "18 install targets @ 182f60b4 (bin/install.js:838): claude, codex, copilot, cursor, windsurf, cline, opencode, antigravity, kimi, kimi-code, kilo, pi, trae, qwen, hermes, codebuddy, zcode, augment (+ vscode extension). List byte-identical fee72d55→v1.11.0; growth redirected to the out-of-tree EoS Registry (see 2026-08-21 assessment). Gemini CLI removed upstream 2026-06-18 (sunset)"
workflow_features:   # survey 2026-07-28 + exp-01; completed & re-verified at the 2026-08-18 deep-dive
  intent_pipeline: true          # structured task graphs from requirements
  deterministic_engine: true     # far beyond bookkeeping: 121k-line TS runtime (215 src/*.cts @ v1.11.0; 96.8k lines @ fee72d55) behind a one-arm dispatcher; Kahn's-algorithm wave computation; engineered locking
  format_gates: engine           # ADR-0011 graded: plan schema hard-errors in the runtime (v1.11.0: src/verify.cts:867-870 fields, :1093-1145 artifacts, :1189-1330 key_links — now compiled under a vendored RE2 engine that refuses rather than guesses); the category's only engine-graded format gate alongside OpenSpec's validator
  measured_gates: prose          # ADR-0011 graded: measurement enforced in code one level up (#1478-1480 live-measurement, provenance rules; v1.11.0: agents/gsd-plan-checker.md:718-733) but the VERDICT is an LLM invocation — <verify> bodies never machine-read
  process_gates: prose           # ADR-0011 graded: checkpoints honored by the orchestrator LLM; the codified boundary (agentVerdict may not block) is engine-enforced but is a meta-rule, not the gate itself
  context_isolation: true        # founding principle, now hook-ENFORCED: gsd-agent-isolation-guard blocks (exit 2) executor dispatch missing its isolation flag
  parallel_orchestration: true   # DAG waves computed in code + worktree machinery; dispatch itself is prose (model emits Agent() calls); Claude Workflow backend is default-off BETA
  state_store: repo-files        # .planning/ markdown (STATE.md regex-parsed, pid-liveness locking); no database
  retrospectives: true           # milestone RETROSPECTIVE.md automatic + planner consumes it; per-phase LEARNINGS.md opt-in twice over
---

# GSD — gsd-core

An *operating loop* for agentic engineering work; its stated enemy is context bloat and
scope drift. Three principles: explicit plans as **structured task graphs**, **clean
execution contexts** per unit of work, and **real verification** producing human-readable
evidence.

Installs into **18 harnesses** (`bin/install.js:838` @ v1.11.0; was `:647` @ fee72d55) via declarative per-runtime
descriptors in `capabilities/*/capability.json` — not hand-written adapters. *(Corrected
at deep-dive: July's six-harness list was wrong at read time — Gemini CLI had been
removed 2026-06-18 after Google sunset it, surviving only as a cross-AI reviewer lane;
and `pi/` was already in-tree, not a standalone CLI.)*

*(2026-08-18: the "already installed on this machine" note from July no longer holds —
no gsd-* artifacts exist under `~/.claude` on this host, almost certainly lost in the
2026-08-06 server rebuild. Owner's daily use is on other devices.)*

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

207 commits / 1045 files since the read, and this is the **weakest verdict in the sweep**
— not because the report is wrong, but because it cites almost nothing checkable. Its only
file references are `docs/ARCHITECTURE.md` and an index link, so rule 4b's "does the drift
touch what the report claims?" has almost no surface to test against. Recorded as the
honest state rather than dressed up.

What could be checked:

- **`gsd-pi` is not in this repo's tree at either end** — and that is *correct*, not a
  finding. It is a separately distributed CLI, which is what "standalone" in the bleed
  section means. Verified before writing, because "the escape-hatch CLI has vanished" would
  have been a conclusion-7-sized claim built on a bad grep.
- **Version moved `1.8.0` → `1.9.1`** (`.claude-plugin/plugin.json`), a minor bump.
- **Multi-harness support is still being actively worked**, judging by archived changesets
  in the drift (`codex-install-skill-surface`, `codex-install-bundled-hooks-blocker`,
  `codex-adapter-text-mode-fallback`) — consistent with the `harness_targets` claim, though
  not a verification of it.

**The methodological finding is the useful one: a survey that cites no source files cannot
be drift-checked.** Rule 4b's cheap test runs off the report's own citations, so a report
with none forces the expensive option (a re-read) or no answer at all. That is an argument
for citing files even at `survey` depth — a citation is what makes a claim *re-checkable*
later, not just traceable now. gsd-core and spec-kit are already queued for re-reads on
issue #9; this one genuinely needs it, where spec-kit's turned out not to.

## Provenance — a fork born from a vanished maintainer

`checked: 2026-07-28`

`open-gsd/gsd-core` is a **community fork** of the original
[`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) ("Get Shit Done"
by TÂCHES, created 2025-12-14). Per the fork announcement
([discussion #109](https://github.com/open-gsd/gsd-core/discussions/109)) and the GitHub
API (both checked 2026-07-28):

- The original maintainer went silent **2026-04-01**; their social accounts were deleted
  or unreachable, and the associated `$GSD` crypto token was publicly linked to a
  rug-pull. The announcement is explicit that whether this was the maintainer's action,
  a co-founder exit, or an account takeover is **unconfirmed**.
- trek-e completed the fork **2026-05-22** (matches the new repo's `created_at`),
  migrating 394 branches, 229 tags, 84 labels, 77 open issues, and 17 PRs. The original
  repo is now archived (last push 2026-05-31).
- Renames along the way: npm package `get-shit-done-cc` → `get-shit-done-redux` →
  `gsd-core`; the brand quietly became "**Git. Ship. Done**"; token and
  `@gsd_foundation` references were stripped. MIT license unchanged.

Two consequences for this repo's index columns: `first_commit: 2025-12-14` **is** the
product's true start (the history migrated intact), but `stars: 7,336` measures only the
fork era — the original carries **64,799 stars**, stranded on the archive. GSD's actual
reach is closer to the old number; the two can't be added (overlapping audiences).

It's also the set's live example of **category-4 supply-chain risk**: this is a tool that
injects prose and hooks into your harness, whose upstream went dark in ambiguous
circumstances — the fork itself states it cannot verify upstream security and forked
precisely for that reason. "Who maintains the methodology you install" is a real
question, not a hypothetical.

## The distinguishing bet

That agents fail from **context mismanagement**, not insufficient intelligence — so the
leverage is in giving each unit of work a clean, right-sized context and verifying the
result with evidence. Compare spec-kit, which shares the diagnosis but locates the failure
in under-specified intent.

## Main features

Observed in a full run (new-project → plan → execute → verify ×2 phases; see
[`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md)):

- **A refinement funnel, not a pipeline.** Research → requirements → phase-research →
  plan → check → execute → verify, where each stage catches what the previous left
  vague. Observed concretely: pitfalls research became four checkable requirements; the
  phase researcher caught an underspecified exit code in those requirements; the checker
  caught an untested claim in the plan; the executor closed it.
- **Empirical research agents** — the standout feature. GSD's researchers and planner
  *measured* git behavior (fixture repos, `git hash-object` crafted commits, timezone
  probes) instead of trusting training data. Nearly all observed quality delta traces
  to this.
- **Plans as runnable contracts**: tasks carry `<read_first>`, `<acceptance_criteria>`,
  and `<verify>` gates with *measured* expected values. *(Deep-dive correction
  2026-08-18: the survey's "the planner dry-runs its own gates" was a misattribution of
  observed behavior — no dry-run exists in plan-phase at either pin. What exp-01
  observed is the plan-checker's live-measurement rule: Dimension #1480 "attempt live
  measurement first… Run it. Use the result as ground truth"
  (`agents/gsd-plan-checker.md:682-699`), plus the measurement-provenance rules in
  `agents/gsd-phase-researcher.md:28-35`.)*
- **Honest verification**: verifiers re-derive claims against real runs, exceed their
  brief (ambient-config attack re-runs), and *abstain* on subjective checks
  (`human_needed`) rather than auto-passing.
- **Deterministic bookkeeping** via `gsd-tools.cjs` (init queries, commits, state) —
  real code where prompt ceremony was expected.
- **Self-healing prose**: workflows encode defenses against known LLM failure modes
  (e.g. the #222 false-refusal recovery for the synthesizer).

## Stack & repo shape

**Majority markdown: 1398 `.md` against 810 `.cjs`** across 2636 tracked files. This is the
single most informative fact in the bootstrap pass — a category-4 framework is mostly *prose*,
because the methodology is the product and the code is delivery machinery. Runtime is
CommonJS Node (`.cjs` plus 177 `.cts`).

`docs/ARCHITECTURE.md` exists, and is translated into ja-JP, ko-KR, and pt-BR — a
localization investment nothing else in the set makes.

4788 commits since **2025-12-14** — barely seven months old, the youngest project here by
first-commit date, at roughly 680 commits/month. *(2026-08-21: that 4788 was a clone-state
artifact — the same commit recounts as 4995 once all refs are fetched; 5364 at v1.11.0.
Ratio at v1.11.0: 1442 `.md` vs 1006 `.cjs` — still majority prose, but the code half is
growing faster; see the release assessment.)*

## Architecture — deep-dive 2026-08-18 (pin fee72d55; three-tract source read)

*Method: three parallel Opus readers (runtime internals · workflow architecture ·
drift + platform), all load-bearing claims spot-verified in the main session. Scale for
calibration: ~34.5k lines of workflow prose + 15.3k of agent prose, driven by a 96.8k-line
TypeScript runtime (173 `src/*.cts` files) with a 409k-line test suite (763 files).
Citation caveat: `gsd-core/bin/lib/*.cjs` are gitignored build artifacts — only 8 tracked
files exist there at the pin; a fresh clone cannot run until `npm run build:lib`. Cite
`src/*.cts`.*

### The shape: four categories, one of them real

`commands/gsd/*.md` (68 *(2026-08-21: miscounted — 71 at this same pin)*) and
`skills/gsd-*/SKILL.md` (71) are ~5-line-different shims —
one surface counted twice. Both point into `gsd-core/workflows/*.md` (the actual
methodology, 110 files), which lazy-loads `references/` (103 files) and per-workflow
`steps/` fragments under a section manifest. Agents (34) auto-load via `subagent_type`.
The runtime is a one-arm dispatcher (`gsd-tools.cjs:3824`: a `switch` with only
`default`, every case migrated out per ADR-2346) routing ~107 host commands into
compiled `src/*.cts` modules.

### The loop, and what carries state

The generated loop-host contract (`loop-host-contract.cjs`, built from HTML markers in
the workflow files) defines: **discuss → plan → execute → verify → ship**, where each
step's only inter-step channel is a named file — CONTEXT.md → PLAN.md → SUMMARY.md →
UAT.md. Routing (`next.md`) keys on **file presence on disk**, not a state machine, with
a recovery route scanning all phases for `plans > summaries` ("catches the session that
died mid-execution with STATE.md advanced past the phase that has unfinished work").
State is markdown: STATE.md regex-parsed by a pure text-transform module
(`src/state-document.cts` — which reimplements ECMAScript case-canonicalization so
field matching can't fold the Kelvin sign), guarded by genuinely engineered locking
(pid-liveness with EPERM-as-alive, deadman ceilings against pid reuse, atomic
rename-steal, Docker/NFS errno retry sets).

### The enforcement ladder — the category's sharpest answer to "who enforces?"

After spec-kit (15/19 gates prose), GSD's classification runs four grades:

1. **Code that hard-errors**: plan schema (8 required frontmatter fields), checkpoint/
   `autonomous` consistency, dependency **cycles** (`src/verify.cts:846-900`,
   `src/phase.cts:737-744`); `must_haves.artifacts`/`key_links` checked against the
   filesystem (`verify.cts:1063-1235`).
2. **Deterministic gate verdicts that don't block**: the 10 registered capability gates
   (6 marked blocking, 4 advisory) each compute a real verdict from disk/git state —
   then emit `{block: true}` JSON **with exit 0**; the halt is prose ("honor
   `blocking`", `references/loop-hook-dispatch.md:45-56`).
3. **A codified boundary**: LLM-verdict gates are *structurally forbidden* from
   blocking — `capability-validator` rejects `agentVerdict` + `blocking: true` at
   registry-validation time ("non-deterministic checks may not halt the loop";
   ADR-894: "non-deterministic blocking gates flap"). The line spec-kit never drew.
4. **Harness-native hooks that actually block**: 26 hooks speaking 12+ dialects
   (Claude, Codex, Cursor, Windsurf, Cline, Kimi TOML…); three exit-2 hard-blockers —
   write-guard (catastrophic `.planning/` shrink), worktree-path-guard, and
   **agent-isolation-guard**, whose header is the thesis: *"A prose backstop cannot
   fix a prose defect — it is the same class of artifact the model may equally skip.
   This hook enforces the invariant at the tooling `layer` instead."*
   *(2026-08-21: "three" was a curated subset presented as a total — a lexical exit-2
   grep matches 8 hook files at this same pin, including workflow-guard's force-`git
   add` block and the two Windsurf pre-hooks. The trio above remains the right list
   for the `.planning`/worktree/isolation invariants specifically.)*

The `<verify>` bodies exp-01 credited are **never machine-read** — the runtime checks
presence only (`verify.cts:744`, missing = warning at `:817`); executor and verifier
are LLM invocations. What makes expected values "measured" is enforced one level up:
the plan-checker's live-measurement dimensions (#1478-1480 — run the command, distrust
RESEARCH.md for numbers) and the researcher's provenance rule (VERIFIED requires
path+line+verbatim quote read *this session*; "registry existence alone does not
confer VERIFIED — a slopsquatted package also passes `npm view`").

### Context discipline: conversation is for humans, files are for agents

Every producer step spawns a fresh-context subagent (7 dispatch sites *(2026-08-21:
the "7" reproduces under no measure tried — counts range 5–39 depending on definition;
the zero-for-discuss half is solid and stable at both pins)*); the ONE step
with zero `Agent()` calls is `discuss-phase` — exactly where the human is. Handoffs are
paths-not-content ("executors read files themselves with their fresh context window"),
completion is detected by **filesystem spot-checks, not the return channel** ("never
block indefinitely waiting for a signal"), and executors are forbidden to touch shared
state — enforced by the `IS_WORKTREE` primitive, not prose. Isolation is three-valued
(`harness-worktree` / `orchestrator-worktree` / `none`), fail-closed ("FATAL: runtime
declares no executor-isolation primitive — executors would run unisolated"), persisted
as an *unconditional side effect* of resolving it, and enforced by the hard-blocking
hook. This is the precise inverse of spec-kit's one-conversation design — and GSD
additionally isolates the **filesystem**, which spec-kit has no analogue for.

### Parallelism: the plan is code, the dispatch is a model obeying a table

Wave assignment is real — Kahn's algorithm over `depends_on`, longest-path levels,
cycles hard-error, the declared `wave:` loses to the computed one, halt propagation
through a single shared DAG engine. But no scheduler process exists: the orchestrator
LLM emits `Agent()` calls following prose ("one at a time with `run_in_background:
true`" — to avoid `.git/config.lock` races). On Claude Code in default config, true
wave parallelism is partially blocked (#853 nesting limitation); the fix — a generated
Workflow-tool backend (`capabilities/claude-orchestration`) — is default-off BETA with
a documented history of being structurally unable to activate (wrong loop point; an SDK
version gate that failed on every run while the capability reported `active: true`).

### Learning loops, and honesty as a design input

Five encoded loops: per-phase LEARNINGS.md (opt-in twice over), automatic milestone
RETROSPECTIVE.md with model-mix cost observations, planner consumption of both
("patterns to avoid", weak-prior global learnings), a measured estimate-calibration
loop (`confidence` derived from sample count — "Do not rate your own certainty. Self-
rated confidence was measured in this project and found weak"), and the repo's own
machine-canon CONTEXT.md (409 single-line predicates; "if you can't compress a
session's lesson into a predicate, the lesson isn't sharp enough yet").

The most distinctive artifact in the category: **GSD ships negative empirical results
about itself.** `references/honest-verifier.md`: the verifier "does not know that it
does not know" — ~100% confident false-pass on blind-spot checks (~0.93 confidence);
"are you sure?" barely moves it (so there deliberately is no such prompt; exogenous
tag routing cuts false-passes to 17%); stated limits ("n=27 — direction-finding, not
powered"); a documented standing cost (budget tier degrades the mechanism).
`edge-probe.md`: ~0.93 confidence while catching 0/12 omitted-edge defects — "worse
than a coin flip"; "the fix is not a better verifier… the fix is spec completeness."

### Drift since exp-01 (d04592de → fee72d55: 207 commits, 10 days)

A hardening window, not a feature window: 120 `fix` vs 3 `feat`; 65% of insertions are
tests. Themes: the **fragment model** (workflows decomposed into per-runtime-composed
`steps/` fragments — forced by Codex's 32,768-byte instruction-file cap, the thinnest
harness reshaping the framework's core architecture); fail-closed guard hardening
("make a guard's failure distinguishable from its benign result"); and the two new
hard-blocking hooks. Verifier substance relocated (size cap), not revised;
`verification-patterns.md` and `honest-verifier.md` untouched. One semantic fix worth
knowing: deleting a verification artifact previously *raised* the completeness score
(#3016). **Dated nuance for exp-01's mechanism table**: the spec-phase edge/prohibition
probes were unreachable dead prose 2026-06-12 → 2026-07-31 (four "Jump to Step 6"
instructions routed around them; two dedicated contract tests sliced the file *below*
the dead jump and were structurally blind to it) — exp-01's empirical-grounding credit
came from researcher/planner instructions, which were live, but any claim citing the
spec-phase probes needs the date qualifier.

### Provenance health (2026-08-18)

Consolidating hard, not fragmenting — but bus factor ≈ 1: top author 60% of all
history, **74% of the drift window**; distinct monthly authors collapsed 77 → ~16-18
while volume held; no external-fork PRs in the window; 16 releases in 61 days. One
sharp hazard for THIS repo's citation discipline: the fork inherited its predecessor's
issue numbers, mass-rewrote 174 URLs onto its own tracker, and its live counter
(#3122) is ~18 days from colliding with inherited archive references (#3828 ceiling) —
**cite commit hashes, not issue numbers, for anything pre-fork (before 2026-05-22)**.

## Release assessment — v1.11.0 (2026-08-21; pin fee72d55 → 182f60b4)

*Method: same three-tract pattern as the deep-dive, scaled to the release window —
release substance, per-claim confrontation of every citation above against the v1.11.0
tree, provenance re-measurement — with load-bearing findings spot-verified in the main
session. Window: fee72d55 (2026-08-06) → 182f60b4 (= tag v1.11.0, 2026-08-19), 369
commits / 1191 files; `main` is 1 commit past the tag, so this assesses current HEAD
too. The v1.10.0 tag (68a04ccf, 2026-08-08) sits inside the window via a `next`-branch
release flow, but only its 31-commit tail is new here — 92% of the window is v1.11.0,
and v1.10.0's headline substance (write-guard, isolation guard, fragment model,
verification ledger) was already in fee72d55 and is already covered above.*

### Character: a hardening release that hunts its own dead prose

fix:feat = 168:15 (11:1); 63.7% of all changed lines are `tests/`; the instruction surface
(workflows + references + agents + capabilities) took **1.4%** of insertions and
`gsd-core/workflows/` is net −73 lines. The largest new-code category after tests is
**meta-enforcement**: 22 new `scripts/lint-*.cjs` drift guards plus 8 new eslint rules,
including `lint-unreachable-guard-drift.cjs` — a guard against dead guards — several
promoted directly from the repo's CONTEXT.md defect-predicate registry (bcf7b048).
A framework spending its release on keeping its own prose and code from diverging is
the closest thing to a category-4 tool adopting this repo's rule 3.

### The headline: the "green-but-inert" epidemic, confirmed and systemic

Deep-dive surprise #3 (dead prose no compiler can see) turns out to be a *class*, not
an incident. Four independent instances found and fixed in this one window:

- **46 spawn blocks across 24 workflows never delivered their required-reading
  instruction** — spawners emitted `<files_to_read>` while agents gate on
  `<required_reading>`; "you MUST Read every listed file" never fired (71180983; now
  pinned by a build-time vocabulary lint).
- **Four `execute-plan` steps silently never ran** — dispatch prompts listed companion
  files as raw `@`-includes, which Claude Code does not expand inside an `Agent()`
  prompt string (5452f1a7; now build-time embedded, size pinned by test).
- **The 40,931-byte `verify-phase.md` workflow shipped to every runtime and was loaded
  by nothing.** Deleted; its live gates moved to `references/verifier-phase-gates.md`,
  eagerly loaded via the verifier's `<required_reading>` (d30c99bc).
- **The verifier's abstention rule pointed at a definition that resolved nowhere** —
  "explicit evidence" was defined only in `honest-verifier.md`, behind a `references/`
  cite dead from every install location, so the term fell back to exactly the
  symbol-presence notion the abstention protocol exists to refuse (285cd41b; definition
  now inline in the agent). Part of a systemic sweep: 43 dead `references/` cites
  across 19 shipped files, now gated at build time.

`honest-verifier.md`, `edge-probe.md`, and `verification-patterns.md` are byte-identical
across the window (verified: zero diff) — but the first should be read as *bypassed*,
not stable: the fix moved its load-bearing definition into the agent rather than repair
the file's role. Same pattern in bulk elsewhere: three shell guards that could never
fire, ESLint silently skipping 56 source files (all of `hooks/`) while exiting 0, all
ten `.githooks/pre-commit` guards inert, 25 test suites running (and passing) twice.
The window's recurring failure mode is *green-but-inert*, not *wrong* — and it is the
strongest evidence yet gathered here on the reliability floor of prose-graded enforcement.

### Movements on the enforcement ladder: everything moved up, nothing moved down

- **Completion became a disk-strict predicate** (e201cde7; `src/verification.cts:740-769`,
  five consumers): phase-complete = `verification.status === 'passed'` on disk,
  unconditionally — "A ROADMAP checkbox has no machine authority and is never
  consulted." Retires the tolerance where missing/stale verdicts counted as
  non-failing, so a project that never runs the verifier now reports incomplete, and
  deleting a VERIFICATION.md *lowers* completion (the #3016 fix, generalized).
  Completion is now falsifiable-by-artifact rather than assertable-by-checkbox.
- **Untrusted plan regexes moved to a vendored RE2 engine** (`src/pattern.cts:127`,
  6,480-line vendored `re2js` — a supply-chain posture choice over an npm dep).
  `key_links[].pattern` is plan frontmatter, i.e. untrusted input the verifier
  compiles: previously `(a+)+$` hung verify-phase and a malformed pattern was
  neutralized into a match-almost-anything literal yielding false `verified: true`.
  Now linear-time by construction, and unsupported patterns are *refused*
  (`pattern_neutralized`, link left unverified) — a gate learning to refuse rather
  than guess. Cost: backreferences/look-around silently degrade to unverified.
- **A new bottom step on the enforcement ladder, below the agent altogether**: an
  opt-in `.git/hooks/pre-commit` guard for `commit_docs`
  (`src/commands.cts:2491-2660`) — the first GSD gate binding inside git itself,
  stopping a raw `git commit` no agent ever touched. Off by default,
  wired by no install path (verified) — it raises GSD's ceiling, not its default
  posture. It exists because the prose grade demonstrably leaked (workflow steps were
  staging `.planning/` with raw `git add`).
- **The hardest stop in the autonomous loop is still prose, now honestly so**:
  auto-mode was synthesizing "approved" for unmet `blocking-human` preconditions and
  the blocker loop retried forever; both fixed (8fc88f66) — but the gate spans two
  markdown artifacts and nothing in `src/` enforces it. The sharpest illustration yet
  of where GSD's enforcement ladder tops out.

No gate was demoted from code to prose. One deliberate non-promotion, stated with
limits in-tree: the verifier's new coincidental-reliance classification is advisory,
endogenous, "measurably weaker than the exogenous backstop tag", precision unmeasured.

### Claim confrontation: the architecture section survives the pin move

Everything load-bearing above holds at 182f60b4, with citations refreshed: one-arm
dispatcher (`gsd-tools.cjs:4343-4345`, still zero non-default cases); plan-schema
hard-errors (`src/verify.cts:867-870`, `src/phase.cts:898-903`); presence-only
`<verify>` (`verify.cts:761`, warning at `:834`); live-measurement dimensions
#1478-1480 (`agents/gsd-plan-checker.md:718-733`, text unchanged); provenance rules
(`agents/gsd-phase-researcher.md:28-37`); 10 capability gates, 6 blocking / 4
advisory, exit-0 verdicts with the halt in prose; the agentVerdict-may-not-block
boundary (`capability-validator.cjs:2803-2806`); 18 install targets byte-identical
(`bin/install.js:838`); isolation three-valued and fail-closed; claude-orchestration
**still default-off BETA**, its manifest still stating the plan-checker and verifier
"remain inline until separately wired". One footnote earned: `verify.cts` does
lexically *parse* `<verify>` bodies into text for a warn-only cross-task ban scan —
"never machine-read" is precisely "never machine-executed".

### Provenance: the bus factor sharpens, and the collision prediction lands

- **First external-fork PRs**: 0xdhx landed 54 commits (15.4% of the window) via two
  fork merges (e705652b, 8f437cfb) — test-environment hermeticity plus verifier
  fixes — and seven more non-maintainer identities squash-landed 11 commits. The
  deep-dive's "no external-fork PRs" is now dated to its window.
- **But concentration effectively rose**: 202 of the top author's 210 window commits
  carry `Co-authored-by: sim <sim@local>` — a no-GitHub-identity, maintainer-side
  address (paired agent or automation). Top author + sim = **80.1%** of the window.
  Read bus factor as one effective owner at 80%, not two at 60/20. 12% of window
  commits carry explicit Claude co-author trailers (a floor; trailer discipline is
  inconsistent).
- **Release regime matured**: zero rc tags since v1.7.0-rc.6 (07-12), zero patch
  releases since v1.9.1 (07-31); minors every 7–11 days. Release frequency roughly
  halved while release size grew — the June patch-storm era is over.
- **The issue-counter collision happened on schedule.** The deep-dive predicted ~18
  days to ceiling #3828; measured counter rate was ~39-41/day and the counter entered
  the inherited band (floor **#3668**, measured ceiling actually **#3857**) on
  ~2026-08-19 — the forecast was accurate at its stated ceiling but understated the
  hazard by quoting the band's ceiling rather than its floor. Full traversal
  completes ~08-24/25, after which every `#NNNN` below 3857 in-tree is permanently
  ambiguous between live and pre-fork. **The pre-fork cite-by-hash rule is no longer
  precautionary; it is mandatory.**

### Platform: the surface froze on purpose

The 18-runtime list is byte-identical across the window; the one new host (Reasonix)
was explicitly *refused* an in-tree runtime ("build the extension for it" —
`.out-of-scope/eos-registry-not-in-tree-runtime.md`) and landed as the third entry in
the out-of-tree **EoS Registry** (Embeddable Orchestration System — a non-endorsing
catalog for hosts embedding GSD via the Host-Integration Interface). Growth redirected,
not stalled. The fragment model is unchanged (48 `steps/` fragments, +1; the 32,768-byte
Codex anchor intact in all three places). The Node floor moved 22→24 in `package.json`
`engines` — but nothing in the install path enforces it, no `engine-strict` exists, and
the same release shipped a `RegExp.escape` fallback because the build itself broke on
the Node 22 lane: **the declared floor and the buildable floor now differ**, and the
in-tree claim that a seam test prevents exactly this divergence is stale.

### Warts worth remembering

A 134 MB STATE.md: frontmatter escaping doubled backslashes on every read-modify-write
(2ⁿ−1 growth; OOM after 26 writes) — GSD's state file is a hand-parsed YAML/markdown
hybrid, and this window carries ~20 separate frontmatter-preservation fixes around it.
Repo hygiene: a zero-byte `pwned_cmdsub` (a shell-injection fix's own proof-of-execution
artifact) and two `.pr-body-*.md` files sit at the repo root at v1.11.0 — none ship
(`package.json` `files` allowlist), but all three landed via security/hardening PRs.

### For the daily user (delta to the 2026-08-18 verdict)

Nothing here argues for a switch; most of it argues the opposite. The release closes
the gap between believed and actual enforcement — the direction this report said
mattered — and the deflations stand unchanged: `<verify>` verdicts are still LLM-run,
wave parallelism on Claude Code is still BETA-gated, and the bus factor is effectively
one person at 80% with an agent co-author. The new watch-items are the Node-floor
ambiguity (declared 24, builds on 22) and the now-live issue-number ambiguity for
anything below #3857.

## Bleed

Reaches **down into category 2** via `gsd-pi`, its own standalone CLI, and into **category 6** via
`gsd-browser`. Documented in [`README.md`](README.md) — it's the clearest case in the repo of a
workflow framework growing into the runtime it was meant to sit on top of.

## Cost model

Free and open source (MIT). Inference cost is whatever your harness charges — though the
structured-task-graph approach implies more model calls per unit of work, which is a cost
question worth measuring.

## Surprises

1. **The markdown-to-code ratio.** 1398 `.md` vs 810 `.cjs` is close to a proof of the
   category-4 definition: if the artifact is mostly prose, the thing being distributed
   really is a methodology rather than a program. Recorded before reading a line of
   source.
2. **The value concentrates in two places** (from the experiment): empirical research
   agents and measured verification gates. The surrounding process ceremony — STRIDE
   threat model for a read-only local CLI, three enterprise-shaped hooks seeded on by
   default for a 200-line project, ROADMAP checkboxes the framework itself forgot to
   tick in both phases — produced almost none of the observed quality delta.
3. **Ceremony cost is front-loaded and enormous on small tasks:** first product code at
   minute 40; ~1.47M subagent tokens and ~3,750 planning-doc lines for 763 product LOC.
   Yet the result genuinely was more robust — a real crash-class difference plus four
   latent-defect classes over the unstructured baseline (see the experiment's results).
4. **Cross-category frictions observed live:** a harness subagent guard (Write refusing
   "report files") collided with the framework's file-on-disk requirement — the agent
   self-healed via Bash heredoc; and a deterministic validator false-positived on an
   external-source citation. Category-4-on-category-2 bleed producing real failure modes.
5. **Research caches are cwd-keyed and can leak.** A researcher's digest cache
   (`.planning/research/.cache/*.json`) materialized in the *orchestrating* repo's root
   rather than the target project, because the orchestrator's shell cwd differed from
   the project directory. Nearly got committed; caught only by reviewing the staged
   file list. Wart class: framework state keyed on ambient cwd instead of an explicit
   project root. When orchestrating GSD against another directory, anchor every path
   absolutely and audit `git status` before committing the host repo.

## Deep-dive surprises (2026-08-18)

1. **GSD has concluded prose cannot enforce its own founding principle — and says so.**
   The migration pattern repeats: isolation → hard-blocking hook ("a prose backstop
   cannot fix a prose defect"); the isolation decision persisted as an unconditional
   side effect of querying it; measurement rules hardened from exhortation into
   checkable form. A workflow framework explicitly demoting its own medium.
2. **It ships negative empirical results about its own verifier** and designs against
   them — including refusing to add an "are you sure?" prompt because confidence was
   measured to be uninformative. No other tool in the category publishes evidence against
   itself.
3. **Prompt-as-control-flow has no compiler, demonstrated.** The empirical-grounding
   probes were unreachable dead prose for seven weeks — four "Jump to Step 6"
   instructions routed around them, and the two dedicated contract tests sliced the
   file below the dead jumps, structurally blind. Dead code no linter could see.
4. **The thinnest harness reshapes the whole framework.** Codex's 32,768-byte
   instruction-file cap produced the fragment model: a 29-term predicate grammar, a
   section-manifest build step, ~2k lines of new runtime — portability's ceiling made
   visible in the architecture.
5. **The generated-artifact discipline failed exactly the way ours predicts.** Nine
   compiled `bin/lib` artifacts were tracked in git and silently diverged from their
   sources (#2653) before being untracked — methodology rule 3's drift failure mode,
   observed in the wild at scale.
6. **Citation hazard**: the fork inherited its predecessor's issue numbers and is ~18
   days from live-number collision with them — pre-fork `#NNNN` references must be
   cited by commit hash.

## For the daily user weighing alternatives (2026-08-18)

What today's deep-dives say to someone running GSD daily and eyeing the field:

- **What GSD has that nothing else in the category has**: hard-blocking harness hooks
  (spec-kit: zero), the codified rule that only deterministic checks may block,
  filesystem isolation (worktrees) on top of context isolation, in-repo negative
  results steering the design, and a measured estimate-calibration loop. Its
  verification *substrate* (DAG waves, plan schema errors, artifact/key-link checks)
  is the most machine-enforced in the category.
- **What the deep-dive deflates**: `<verify>` bodies are LLM-enforced (the hooks guard
  files and dispatch, not verification verdicts); default-config wave parallelism on
  Claude Code is partially blocked with the fix in BETA; the four-category surface is one
  methodology counted several times; bus factor ≈ 1.
- **Against spec-kit**: opposite architecture on every axis that matters — files vs
  conversation, enforcement ladder vs prose gates, engine driving the methodology vs
  engine disconnected from it. A switch buys intent-capture ceremony (exp-02: wins
  requirements rubrics, discovers nothing) and gives up context isolation and every
  hard gate. On today's evidence that trade is backwards for a GSD user.
- **Against OpenSpec**: the lean pole — delta specs, format gates, no fan-out, no
  measured gates. Complementary shape, smaller bet, weaker verification.
- **Open alternatives worth watching, not switching to yet**: BMAD *(deep-dived
  2026-08-18 — right-sizing answered: real but prose-judged fork, all framework gates
  prose; the enforcement lives in the separate bmad-loop orchestrator. Still not a
  switch: the opposite bet from GSD's hook-enforced direction — [report](bmad-method.md))*,
  spec-kitty (worktree factory, multi-maintainer), haft (decision governance, likely
  category 6).

## Open questions

- How is 1398 markdown files' worth of methodology kept coherent? Is there a schema, or is
  it convention?
- Does the ceremony pay below some task size, and where's that threshold?
- 680 commits/month on a seven-month-old project — what's churning?
- Does `gsd-pi` behave identically to gsd-in-Claude-Code, or does the host harness dominate?
