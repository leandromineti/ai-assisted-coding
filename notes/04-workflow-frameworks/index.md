# Layer 4 — Workflow frameworks

`checked: 2026-07-28`

An encoded **methodology** riding on top of a harness. Runtime is to framework as harness
is to this. See [`../../taxonomy.md`](../../taxonomy.md).

The layer test is **harness portability by design**: the methodology is defined once and
targets many harnesses.

## Seed inventory

### GSD — <https://opengsd.net> · [report](gsd-core.md)

Bills itself as an *operating loop* for agentic engineering work — its stated enemy is
context bloat and scope drift.

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

30+ agent integrations (`specify integration list`). Install: `uv tool install specify-cli`
— needs Python 3.11+, git, and `uv`.

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
| **Empirical grounding** | Agents instructed to *measure* the domain (fixture repos, probes) rather than trust training data | Carried most of the quality margin: the invalid-UTF-8 crash class, timezone traps, exit-code collision were all found by measurement |
| **Verification gates** | Machine-checkable acceptance criteria with *measured* expected values; verifiers that re-derive rather than trust | Carried the rest: the checker caught an untested claim; verifiers exceeded brief and honestly abstained on subjective checks |
| **Context discipline** | Fresh right-sized context per unit of work; artifacts as the interface between stages | Plausibly load-bearing (each stage caught the previous stage's vagueness — the refinement funnel) but not isolated by this experiment |
| **Process gates** | Approval points, threat models, mode ceremonies | Near-zero observed value on this task (STRIDE for a read-only CLI; three no-op default-on hooks) |
| **Bookkeeping** | State files, checkboxes, traceability tables | Mixed: traceability caught requirement gaps; checkbox upkeep was dropped by the framework itself in both phases |

Frameworks should get profiled against these columns as they're studied — spec-kit's
mechanism mix is presumably intent-capture-heavy, and that difference is the real
comparison, not "GSD vs spec-kit."

## Open questions

- ~~GSD and spec-kit both add ceremony. What's the task-size threshold below which the
  ceremony costs more than it saves?~~ **Partially answered 2026-07-28** (experiment 01,
  n=1): the threshold splits by what "saves" means — the test task was below it for
  build speed (~78 min vs ~1 min) and arguably above it for ship quality (a real
  crash-class margin). The sharper successor question: **which mechanisms buy the
  margin?** (table above — empirical grounding + gates, on this evidence).
- Is the portability real? Does GSD-on-Cursor behave like GSD-on-Claude-Code, or does the
  underlying harness dominate the outcome?
- Claude Code ships plan mode natively. Where's the line between a harness's built-in
  process features and an installed framework — and is layer 4 being absorbed into layer 2?
- ~~Neither is easy to A/B test, since you can't run the same task twice cleanly. What
  would a fair comparison even look like?~~ **Working answer 2026-07-28:** preregister
  the protocol and falsification criteria, run the contaminated arm second with fresh
  subagent contexts, log during (not after), and state n honestly. Experiment 01 is the
  template; its limitations section is part of the answer.
