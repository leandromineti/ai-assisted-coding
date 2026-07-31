# Layer 4 — Workflow frameworks

`checked: 2026-07-28`

An encoded **methodology** riding on top of a harness. Runtime is to framework as harness
is to this. See [`../../taxonomy.md`](../../taxonomy.md).

The layer test is **harness portability by design**: the methodology is defined once and
targets many harnesses.

## Seed inventory

### GSD — <https://opengsd.net> · [report](gsd-core.md)

Bills itself as an *operating loop* for agentic engineering work — its stated enemy is
context bloat and scope drift. Note the provenance: `gsd-core` is a 2026-05-22 community
fork of the original `gsd-build/get-shit-done` (64.8k stars, now archived), whose
maintainer vanished amid a crypto-token rug-pull association — see the
[report's provenance section](gsd-core.md#provenance--a-fork-born-from-a-vanished-maintainer).

Three principles: explicit plans as **structured task graphs**, **clean execution
contexts** per unit of work, and **real verification** producing human-readable evidence.

Ships as several pieces, which is itself instructive:

| Piece | What | Layer |
|-------|------|-------|
| `gsd-core` | The framework proper; installs into Claude Code, Codex, Gemini CLI, Cursor, Windsurf, Copilot. | 4 |
| `gsd-pi` | Standalone CLI for autonomous workflows. | **2 — bleed** |
| `gsd-browser` | Deterministic Chrome control with recording and assertions. | **3 — bleed** |
| `gsd-workbench` | Desktop workspace. Announced, not shipped at check date. | 2 |
| `gsd-cloud` | Hosted cross-device state. Announced, not shipped at check date. | — |

*Already installed on this machine* — the `gsd-*` skills are live in this Claude Code
install, which makes it the cheapest layer-4 subject to study first-hand.

### spec-kit — <https://github.com/github/spec-kit> · [report](spec-kit.md)

GitHub's toolkit for **Spec-Driven Development**: specifications come first and are treated
as executable artifacts that *generate* the implementation, rather than documentation that
merely guides it. Intent before mechanism — the "what" before the "how".

Workflow commands:

`/speckit.constitution` (project principles) → `/speckit.specify` (requirements) →
`/speckit.plan` (technical strategy) → `/speckit.tasks` (task list) → `/speckit.implement`
(execute). Optional: `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`.

40+ agent integrations (44 config dirs @ 655a3cb; `specify integration list`).
Install: `uv tool install specify-cli` — needs Python 3.11+, git, and `uv`.

### OpenSpec — <https://github.com/Fission-AI/OpenSpec> · [report](openspec.md)

*(Added 2026-07-28 from the candidate sweep.)* The lean pole of spec-driven development:
**delta specs** — spec only the change (proposal → delta spec → design → tasks), archive
completed changes into a living source-of-truth. Same bet as spec-kit, opposite ceremony
budget. 63k stars, MIT, visibly dogfooded (its own history lives in `openspec/changes/`).

### ECC (everything-claude-code) — **moved to layer 3** (2026-07-30)

*(Added 2026-07-28 as a deliberate boundary case; resolved at deep-dive.)* The source
read answered the question this entry was created to ask: **no process spine** — the
README's own guidance is "start with the workflow you need, not the full catalog,"
workflow content is opt-in catalog items, and the multi-* orchestration commands
require an external runtime (`ccg-workflow`). A config pack at scale with a real
learning runtime, not an encoded methodology. Report now at
[`../03-capability-extensions/ecc.md`](../03-capability-extensions/ecc.md). What it
contributed to *this* layer's questions: verification gates can arrive as installable
Stop hooks (a layer-3 delivery vehicle for the mechanism exp-01 credited to layer 4),
and its `ecc2` Rust control plane repeats the conclusion-7 escape-hatch pattern from
outside layer 4 proper.

## Considered, not added (2026-07-28)

From the same web + GitHub-API sweep (stars as of 2026-07-28), recorded so the reasoning
isn't re-derived later:

| Candidate | Stars | Why not (yet) |
|---|---|---|
| BMAD-METHOD (`bmad-code-org`) | 51k | Famous, active — but its predicted profile (role-playing agent teams, process-gates-heavy) is the mechanism column exp-01 measured near zero. First in line if layer-4 scope expands; would make a good ceremony-pole test subject |
| hermes-agent (`NousResearch`) | 222k | A layer-2 harness, not a framework (spec-kit installs *into* it). Queued on the layer-2 backlog: [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) |
| claude-task-master (`eyaltoledano`) | 28k | Quiet since 2026-04; MCP-server-shaped (layer-3 bleed dominant) |
| SuperClaude_Framework | 24k | Single-harness (Claude Code only) — fails the layer-4 portability test; useful as the boundary counterexample |
| wshobson/agents | 38k | Multi-harness plugin *marketplace* — layer-3 distribution, no methodology |
| agent-os (`buildermethods`) | 5k | Too small, quieting since 2026-05 |
| microsoft/amplifier | 3k | Too small; watchlist |
| Kiro (AWS), Tessl | — | Closed products — observation-only if ever added; no clone possible |

## The shared bet

Both wager that **agents fail from insufficient structure, not insufficient intelligence** —
that the fix for a drifting agent is a better-specified process, not a better model. GSD
locates the failure in context management; spec-kit locates it in under-specified intent.
Same diagnosis, different organ.

That bet is falsifiable, and testing it is one of the more valuable things this repo could
do: as models improve, does imposed structure keep paying, or does it become overhead?
First test run: [`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md).

## Mechanisms — the unit of value

*(Added 2026-07-28 after experiment 01. "GSD is a layer-4 tool" proved true and nearly
useless as an analytical claim: the value variance was inside the tool. The tool is the
unit of **distribution**; the mechanism is the unit of **value**. Compare frameworks
mechanism-by-mechanism, not brand-by-brand.)*

| Mechanism class | What it is | Exp-01 evidence (n=1) |
|---|---|---|
| **Intent capture** | Structured extraction and pinning of the "what" before execution: ID'd requirements, rationed clarification, artifacts that test the English itself | Not exercised by exp-01 (added 2026-07-28 from the spec-kit source read — GSD is thin here) |
| **Empirical grounding** | Agents instructed to *measure* the domain (fixture repos, probes) rather than trust training data | Carried most of the quality margin: the invalid-UTF-8 crash class, timezone traps, exit-code collision were all found by measurement |
| **Verification gates** | Machine-checkable acceptance criteria with *measured* expected values; verifiers that re-derive rather than trust | Carried the rest: the checker caught an untested claim; verifiers exceeded brief and honestly abstained on subjective checks |
| **Context discipline** | Fresh right-sized context per unit of work; artifacts as the interface between stages | Plausibly load-bearing (each stage caught the previous stage's vagueness — the refinement funnel) but not isolated by this experiment |
| **Process gates** | Approval points, threat models, mode ceremonies | Near-zero observed value on this task (STRIDE for a read-only CLI; three no-op default-on hooks) |
| **Bookkeeping** | State files, checkboxes, traceability tables | Mixed: traceability caught requirement gaps; checkbox upkeep was dropped by the framework itself in both phases |

### Profiles so far

*(GSD: run + source read, exp-01. spec-kit: source read only, 2026-07-28 — see
[spec-kit.md](spec-kit.md) for evidence.)*

| Mechanism class | GSD | spec-kit |
|---|---|---|
| Intent capture | Thin | **Center of mass**: FR-/SC- IDs, prioritized independently-testable stories, rationed clarification (max 3 markers / 5 questions), "unit tests for requirements" checklists |
| Empirical grounding | **Heavy** (fixture measurement, probes) | Nearly absent — Phase-0 "research" is best-practices lookup from training data |
| Verification gates | **Heavy**, measured expected values | Document-vs-document only; the one hard gate is user-overridable |
| Context discipline | **Core mechanism** (fresh subagent contexts) | Weakest column; the one isolation attempt (fork for analyze) was reverted after compounding-context freezes (#3185) |
| Process gates | Moderate (hooks, STRIDE, modes) | Moderate (hook ceremonies, constitution governance wrapper with no consumer) |
| Bookkeeping | Moderate, self-dropped under load | Strong grammar-enforced (task ID/[P]/[US] format, ≥80% traceability floor) |

The two frameworks are near-complements: GSD spends structure on the execution side,
spec-kit on the intake side; each is thin exactly where the other is thick. "GSD vs
spec-kit" as brands was the wrong comparison — this table is the real one.

## Open questions

- ~~GSD and spec-kit both add ceremony. What's the task-size threshold below which the
  ceremony costs more than it saves?~~ **Partially answered 2026-07-28** (experiment 01,
  n=1): the threshold splits by what "saves" means — the test task was below it for
  build speed (~78 min vs ~1 min) and arguably above it for ship quality (a real
  crash-class margin). The sharper successor question: **which mechanisms buy the
  margin?** (table above — empirical grounding + gates, on this evidence).
- Is the portability real? Does GSD-on-Cursor behave like GSD-on-Claude-Code, or does the
  underlying harness dominate the outcome? **Mechanism half answered 2026-07-28** for
  spec-kit (source-read): portability is a compile step over placeholder-token markdown,
  cheap because every harness converged on "slash command = prompt file in a directory" —
  and bounded by it: the methodology can't use any capability beyond prose-following, so
  forks, code-level hooks, and context isolation are structurally unavailable. Behavioral
  equivalence across harnesses remains untested.
- Claude Code ships plan mode natively. Where's the line between a harness's built-in
  process features and an installed framework — and is layer 4 being absorbed into layer 2?
- ~~Neither is easy to A/B test, since you can't run the same task twice cleanly. What
  would a fair comparison even look like?~~ **Working answer 2026-07-28:** preregister
  the protocol and falsification criteria, run the contaminated arm second with fresh
  subagent contexts, log during (not after), and state n honestly. Experiment 01 is the
  template; its limitations section is part of the answer.
