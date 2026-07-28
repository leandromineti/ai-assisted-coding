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

## Open questions

- GSD and spec-kit both add ceremony. What's the task-size threshold below which the
  ceremony costs more than it saves?
- Is the portability real? Does GSD-on-Cursor behave like GSD-on-Claude-Code, or does the
  underlying harness dominate the outcome?
- Claude Code ships plan mode natively. Where's the line between a harness's built-in
  process features and an installed framework — and is layer 4 being absorbed into layer 2?
- Neither is easy to A/B test, since you can't run the same task twice cleanly. What would
  a fair comparison even look like?
