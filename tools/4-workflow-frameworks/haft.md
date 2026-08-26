---
name: haft
category: 4
vendor: Ivan Zakutnii (m0n0x41d)
url: https://github.com/m0n0x41d/haft
license: MIT   # LICENSE file is plain MIT; GitHub API reports NOASSERTION
open_source: true
stack: [Go, Rust, SQLite]
version: v9.1.0
commit: 8a5f038
first_commit: 2025-12-10
stars: 1383
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + full README; Go source and FPF spec unread
harness_targets: "Claude Code + Codex stable; experimental adapters: Grok, Pi, Hermes, Zed, Antigravity, Cursor, Gemini CLI, OpenCode (haft init flags @ 8a5f038)"
workflow_features:   # added 2026-08-18; stub — README-level claims only
  intent_pipeline: false         # governs decisions and evidence, not an implementation pipeline
  deterministic_engine: true     # Go runtime: ledger, migrations, MCP server
  format_gates: true             # typed records + parity enforcement
  state_store: database          # project SQLite ledger — the only non-repo-files store in the category
---

# haft

## What it is

A local decision-governance system for AI coding agents, implementing Levenchuk's First
Principles Framework (FPF): durable typed project records — what problem, which options
compared, what the human decided, what evidence supports it, and **what has gone
stale** (evidence decay), with parity enforcement across compared options. Small
reversible reasoning stays in conversation; results later work relies on become typed
records in a project SQLite ledger, served to agents over MCP (`haft serve`) with
per-harness skills and instruction sections installed by `haft init`. (README at the
pin; source unread.)

## Notes for the category-4 comparison

Not SDD — a third pole for the category's "where does failure live" question: not context
(GSD), not intent (spec-kit), but ungoverned decisions and stale evidence. The
mechanism resonance with this repo's own methodology is direct: evidence decay is the
`checked:`-dates discipline as a runtime mechanism; typed decision records are ADRs
with a database. The claude-task-master question from the ledger (encoded methodology
vs. memory extension over MCP) is the survey read's first job — the README's migration
machinery (startup-safe boundaries, verified snapshots, migration leases) shows the
center of gravity is a *governed datastore*, which cuts both ways.

## Stack & repo shape

Substantial Go codebase — go(2085) of 2299 tracked files, plus a Rust `embed-sidecar/`
(Cargo.toml) and TS test fixtures (`internal/codebase/testdata/typescript_parity/`).
`spec/enabling-system/ARCHITECTURE.md` in-repo. 1597 commits since 2025-12,
~100% single-author. By file count it is the *heaviest* runtime in category 4 — the
opposite pole from Conductor's 22 markdown files, in the same month's intake.

## My take

*(empty — not yet used; stub honesty)*
