---
name: gsd-core
category: 4
vendor: Open GSD
url: https://github.com/open-gsd/gsd-core
license: MIT
open_source: true
stack: [Markdown, Node]
version: v1.9.1-148-gfee72d55
commit: fee72d55
# PIN MOVED d04592de → fee72d55 at the 2026-08-18 deep-dive re-read (rule 4b: a pin moves
# only with a re-read; this was one). exp-01 artifacts keep their own pin (d04592de).
first_commit: 2025-12-14
stars: 8420
stars_at: 2026-08-18
read_at: 2026-08-18   # deep-dive; survey read 2026-07-28 @ d04592de, drift-checked 2026-08-16, exp-01 run late July
depth: deep-dive   # 2026-08-18: runtime traced in source by three parallel readers (gsd-tools dispatcher + src/*.cts state/verify machinery; workflow architecture + isolation; drift + platform surface), load-bearing claims spot-verified in main session at the pin
harness_targets: "18 install targets @ fee72d55 (bin/install.js:647): claude, codex, copilot, cursor, windsurf, cline, opencode, antigravity, kimi, kimi-code, kilo, pi, trae, qwen, hermes, codebuddy, zcode, augment (+ vscode extension). Gemini CLI removed upstream 2026-06-18 (sunset) — July's list was wrong at read time"
workflow_features:   # survey 2026-07-28 + exp-01; completed & re-verified at the 2026-08-18 deep-dive
  intent_pipeline: true          # structured task graphs from requirements
  deterministic_engine: true     # far beyond bookkeeping: 96k-line TS runtime (src/*.cts) behind a one-arm dispatcher; Kahn's-algorithm wave computation; engineered locking
  format_gates: engine           # ADR-0011 graded: plan schema hard-errors in the runtime (src/verify.cts:846-900, 1063-1235); the layer's only engine-graded format gate alongside OpenSpec's validator
  measured_gates: prose          # ADR-0011 graded: measurement enforced in code one level up (#1478-1480 live-measurement, provenance rules) but the VERDICT is an LLM invocation — <verify> bodies never machine-read
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

Installs into **18 harnesses** (`bin/install.js:647`) via declarative per-runtime
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

It's also the set's live example of **layer-4 supply-chain risk**: this is a tool that
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
single most informative fact in the bootstrap pass — a layer-4 framework is mostly *prose*,
because the methodology is the product and the code is delivery machinery. Runtime is
CommonJS Node (`.cjs` plus 177 `.cts`).

`docs/ARCHITECTURE.md` exists, and is translated into ja-JP, ko-KR, and pt-BR — a
localization investment nothing else in the set makes.

4788 commits since **2025-12-14** — barely seven months old, the youngest project here by
first-commit date, at roughly 680 commits/month.

## Architecture — deep-dive 2026-08-18 (pin fee72d55; three-tract source read)

*Method: three parallel Opus readers (runtime internals · workflow architecture ·
drift + platform), all load-bearing claims spot-verified in the main session. Scale for
calibration: ~34.5k lines of workflow prose + 15.3k of agent prose, driven by a 96.8k-line
TypeScript runtime (173 `src/*.cts` files) with a 409k-line test suite (763 files).
Citation caveat: `gsd-core/bin/lib/*.cjs` are gitignored build artifacts — only 8 tracked
files exist there at the pin; a fresh clone cannot run until `npm run build:lib`. Cite
`src/*.cts`.*

### The shape: four layers, one of them real

`commands/gsd/*.md` (68) and `skills/gsd-*/SKILL.md` (71) are ~5-line-different shims —
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

### The enforcement ladder — the layer's sharpest answer to "who enforces?"

After spec-kit (15/19 gates prose), GSD's classification runs four rungs:

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
   This hook enforces the invariant at the tooling layer instead."*

The `<verify>` bodies exp-01 credited are **never machine-read** — the runtime checks
presence only (`verify.cts:744`, missing = warning at `:817`); executor and verifier
are LLM invocations. What makes expected values "measured" is enforced one level up:
the plan-checker's live-measurement dimensions (#1478-1480 — run the command, distrust
RESEARCH.md for numbers) and the researcher's provenance rule (VERIFIED requires
path+line+verbatim quote read *this session*; "registry existence alone does not
confer VERIFIED — a slopsquatted package also passes `npm view`").

### Context discipline: conversation is for humans, files are for agents

Every producer step spawns a fresh-context subagent (7 dispatch sites); the ONE step
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

The most distinctive artifact in the layer: **GSD ships negative empirical results
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

## Bleed

Reaches **down into layer 2** via `gsd-pi`, its own standalone CLI, and into **layer 5** via
`gsd-browser`. Documented in [`index.md`](index.md) — it's the clearest case in the repo of a
workflow framework growing into the runtime it was meant to sit on top of.

## Cost model

Free and open source (MIT). Inference cost is whatever your harness charges — though the
structured-task-graph approach implies more model calls per unit of work, which is a cost
question worth measuring.

## Surprises

1. **The markdown-to-code ratio.** 1398 `.md` vs 810 `.cjs` is close to a proof of the
   layer-4 definition: if the artifact is mostly prose, the thing being distributed
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
4. **Cross-layer frictions observed live:** a harness subagent guard (Write refusing
   "report files") collided with the framework's file-on-disk requirement — the agent
   self-healed via Bash heredoc; and a deterministic validator false-positived on an
   external-source citation. Layer-4-on-layer-2 bleed producing real failure modes.
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
   measured to be uninformative. No other tool in the layer publishes evidence against
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

- **What GSD has that nothing else in the layer has**: hard-blocking harness hooks
  (spec-kit: zero), the codified rule that only deterministic checks may block,
  filesystem isolation (worktrees) on top of context isolation, in-repo negative
  results steering the design, and a measured estimate-calibration loop. Its
  verification *substrate* (DAG waves, plan schema errors, artifact/key-link checks)
  is the most machine-enforced in the layer.
- **What the deep-dive deflates**: `<verify>` bodies are LLM-enforced (the hooks guard
  files and dispatch, not verification verdicts); default-config wave parallelism on
  Claude Code is partially blocked with the fix in BETA; the four-layer surface is one
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
  layer 5).

## Open questions

- How is 1398 markdown files' worth of methodology kept coherent? Is there a schema, or is
  it convention?
- Does the ceremony pay below some task size, and where's that threshold?
- 680 commits/month on a seven-month-old project — what's churning?
- Does `gsd-pi` behave identically to gsd-in-Claude-Code, or does the host harness dominate?
