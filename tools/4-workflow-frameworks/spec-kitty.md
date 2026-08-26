---
name: spec-kitty
category: 4
maker: Spec Kitty, Inc. (Priivacy-ai)
url: https://github.com/Priivacy-ai/spec-kitty
license: MIT
access: open-source
stack: [Python]
version: v3.2.6rc1-371-g30cffb08b
commit: 30cffb08b
first_commit: 2025-08-21   # predates the GitHub repo (2025-10-09) — imported spec-kit history
stars: 1520
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README + tree inspection; source unread
harness_targets: [Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf, OpenCode]
workflow_features:   # added 2026-08-18; stub — README + tree-level claims
  intent_pipeline: true          # spec → plan → tasks → next → review → accept → merge
  deterministic_engine: true     # Python runtime: lifecycle lanes, worktree management, dashboard
  process_gates: true            # review/accept/merge gates with audit trail (README)
  parallel_orchestration: true   # isolated git worktrees under .worktrees/ (README)
  state_store: repo-files        # kitty-specs/ — verified in the tree (dogfood artifacts checked in)
  retrospectives: true           # per-mission retrospective, default-on (README)
---

# spec-kitty

## What it is

A spec-kit derivative grown into a "governed software factory": spec → plan → tasks →
next → review → accept → merge, with work packages moving through kanban lifecycle
lanes, parallel agents in isolated git worktrees under `.worktrees/`, review/accept/
merge gates with an audit trail, per-mission retrospectives, and a `dispatch`
governance command that opens typed Op records. Repo-native state under `kitty-specs/`;
optional local kanban dashboard. Explicitly positioned as "bright software factory,
not a black box" — humans hold intent/architecture/acceptance, agents implement in
traceable worktrees. (README at the pin; source unread.)

## Notes for the category-4 comparison

The lineage is verifiable in the mechanical facts alone: `first_commit` 2025-08-21
predates the repo's own GitHub creation (2025-10-09) — spec-kit's history was imported,
and `src/specify_cli/` still carries spec-kit's CLI name. What it adds to the parent is
orchestration: worktree isolation (category-3 bleed), lifecycle lanes, merge governance.
Dogfooding is visible in the tree — `kitty-specs/` mission artifacts and `kitty-ops/`
are checked into the repo itself (8.6k markdown files of the 17k tracked). Genuinely
multi-maintainer (two leads ~8k commits) and incorporated ("Spec Kitty, Inc.", 2026
LICENSE) — the only category-4 subject that is both.

## Stack & repo shape

Python CLI (`spec-kitty-cli` on PyPI): src/ split into `charter`, `doctrine`,
`glossary`, `kernel`, `mission_runtime`, `runtime`, `specify_cli`. md(8605) py(4217)
json(2021) yaml(1018) — the markdown mass is dogfood artifacts, not framework prose.
8743 commits (imported history included), 17162 tracked files.

## My take

*(empty — not yet used; stub honesty)*
