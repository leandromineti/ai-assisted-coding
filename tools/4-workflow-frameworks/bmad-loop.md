---
name: bmad-loop
category: 4
maker: BMad Code, LLC
url: https://github.com/bmad-code-org/bmad-loop
license: MIT
access: open-source
stack: [Python]
version: v0.10.0-135-g75e0348
commit: 75e0348
first_commit: 2026-06-10
stars: 93
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # README + module.yaml read in full; three targeted source probes (verify-command execution path, epic-boundary gate, retro consumers) answering the bmad-method deep-dive's open question 1; the 42-file engine otherwise unread
harness_targets: "drives claude (default), codex, gemini, copilot, antigravity via profiles + a generic tmux adapter, opencode per README badge (README.md, Requirements) — DRIVE targets, not install targets; the skills module installs through bmad-method's 47-code installer"
workflow_features:   # stub 2026-08-18 — only probed keys set; graded per ADR-0011
  deterministic_engine: true     # the README's whole pitch ("No LLM in the control loop") verified in shape: engine.py 6220 lines, verify.py 3123, 42 modules, resumable state machine on disk; story selection/retries/gates are code
  format_gates: engine           # orchestrator checks artifacts on disk post-session: spec frontmatter status, baseline-commit validity, non-empty diff, sprint-status sync (README; frontmatter.py:363 set_frontmatter_status + devcontract machinery sighted — full gate path not traced at stub depth)
  measured_gates: engine         # VERIFIED CALL PATH: policy `[verify] commands` (policy.py:855,1165) executed by run_verify_commands (verify.py:2661); engine.py:2037-2040 blocks the flow on the outcome before any commit — the first engine-graded measured gate in this repo's category-4 ecosystem, and it lives in the companion orchestrator, not the framework
  process_gates: engine          # gates.pause_at_epic_boundary (gates.py:128-129: policy modes per-epic / per-story-spec-approval); engine.py:6210-6215 pauses the run for a human at the boundary — code-enforced, not prose
  context_isolation: true        # by construction: dev and review are separate disposable sessions the orchestrator spawns; "review never inherits the implementer's context" (README) — adapters not traced at stub depth
  retrospectives: false          # the sharp negative: parses retro action items from sprint-status (sprintstatus.py:67-71) but "does not yet drive them as work (see roadmap: retro-item automation)"; at an epic boundary the engine only SUGGESTS "run /bmad-retrospective when convenient" (engine.py:6202-6207); the retro document's `verdict:` frontmatter has no consumer here either
  state_store: repo-files        # sprint-status.yaml as "the workflow ledger" via "a single idempotent, never-regress writer" (README) + resumable run state on disk
---

# bmad-loop

The BMAD ecosystem's companion orchestrator — "a deterministic ralph-loop orchestrator
for the BMAD-METHOD implementation phase" (README). Plain Python drives pick-story →
implement → adversarially review → verify → commit; LLMs run only inside disposable
sessions the orchestrator spawns via a tmux adapter and watches through **harness hooks**
(`Stop`/`SessionStart`/`SessionEnd`/`PreCompact` writing structured event files — "no
pane-scraping"). Young and small (public 2026-06-19, 93 stars, early open beta,
pre-1.0 breaking changes disclaimed) but built fast and seriously: 1,417 commits in ~10
weeks, 167 Python files, a TUI dashboard, pluggable OS/multiplexer seams, and tests.

## Why this stub exists

The [bmad-method deep-dive](bmad-method.md) (same day) found a framework that ships
deterministic tooling and denies it authority — zero hooks, every gate prose, every
script failure routed around. Its open question 1 asked whether bmad-loop is where the
enforcement actually lives. **Answer: yes — inverted wholesale.** The orchestrator's
stated theses are the exact negation of the framework's: "No LLM in the control loop.
Story selection, retry budgets, gates, and completion checks are code, not prompts" and
"Trust nothing, verify everything" (README). Concretely, at this pin:

- **Measured gates, engine-graded** — the first in the ecosystem this repo tracks: the
  user's own test/lint commands live in policy (`[verify] commands`, `policy.py:1165`),
  are executed by the orchestrator (`run_verify_commands`, `verify.py:2661`), and the
  outcome blocks the loop before any commit (`engine.py:2037-2040`). No LLM judges the
  verdict.
- **Process gates, engine-graded**: policy gate modes `per-epic` /
  `per-story-spec-approval` (`gates.py:128-129`) make the engine pause the run and wait
  for a human (`engine.py:6210-6215`), with desktop notification + an `ATTENTION` file.
- **Artifact verification in code**: post-session checks of spec frontmatter status,
  baseline-commit validity (including a carefully specified reachable-descendant proof),
  non-empty diff, and sprint-status sync (README; `verify.py` is 3,123 lines).
- **Context isolation by construction**: dev and review are separate fresh sessions —
  the anchoring-bias rationale BMAD states in prose, here enforced by the spawner.
- **Optional worktree isolation** (`[scm] isolation = "worktree"`): per-story
  worktree/branch with local merge-back — the machinery the framework itself lacks.

**One loop still does not close.** The retro-verdict consumer the framework designed for
does not exist here either: retro action items are parsed (`sprintstatus.py:67-71`) but
explicitly not driven as work ("see roadmap: retro-item automation"), and the epic
boundary merely suggests running `/bmad-retrospective` (`engine.py:6202-6207`).
Learn → Plan remains unshipped across the whole BMAD ecosystem at these pins.

## Placement note

Category 4 as a module of the BMAD methodology (it requires a BMAD v6 project and drives
`bmad-build-auto` + the bmad-loop skill pair), but it is conclusion 7's escape-hatch
pattern productized — a standalone runtime that reaches **down into category 2** harder
than gsd-pi does: it drives *other* harnesses (claude/codex/gemini/copilot/antigravity)
from outside their chat loops rather than being one. The split distribution is itself
the finding: BMAD keeps the framework maximally prose-governed and sells the
enforcement separately.

## What a survey read should check first

- The dev contract (`devcontract.py`) and `result.json` skill protocol — how much of the
  "automation mode" contract leaks back into the framework's skills.
- Whether the review stage's adversarial verdict is machine-parsed or LLM-summarized
  (`resolve.py`, `documents.py` — `validate --json` suggests structured verdicts).
- The hook interpreter seam (`signals.py`, `process_host.py`) — what exactly the
  harness hooks write and what happens on hosts without hook support.
- Whether worktree isolation defaults on by now (pre-1.0 churn is disclaimed).
