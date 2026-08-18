---
name: ai-memory
layer: 5
kind: memory
vendor: Fabio Akita (akitaonrails)
url: https://github.com/akitaonrails/ai-memory
license: MIT
open_source: true
stack: [Rust]
version: v1.28.1-16-gacd9c0b
commit: acd9c0b
first_commit: 2026-05-21
stars: 2596
stars_at: 2026-08-18
read_at: 2026-08-19
depth: stub   # facts from repo-facts.sh + README support matrix; source not read
harness_targets: "README support matrix at acd9c0b lists ~24 targets — Supported with MCP + lifecycle hooks: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Devin CLI, Command Code, Kimi Code, Kiro CLI, OpenClaw, Antigravity CLI, Grok Build CLI, Zero, Pi, OMP; MCP-only: Claude Desktop, VS Code Copilot, Zed, Swival; community: Hermes. Counted from README, not verified per-target"
features:
  learning_loop: true   # README-level, not source-traced: lifecycle hooks capture sanitized observations -> session-end consolidation into a markdown wiki -> bounded handoff injected at next session start; on once installed
---

# ai-memory

## What it is

Long-term, cross-harness memory for coding agents, installed as an MCP server plus
per-harness lifecycle hooks. Sessions are captured through the harness's own hook
events, consolidated at session end into a plain-markdown wiki in a git repo (no
vector database), and the next session — in the *same or a different* harness —
receives a bounded handoff. Its pitch is continuity across harness switches: "quit
Claude Code mid-task, start Codex in the same directory, continue without
re-explaining." (README at the pin; source unread.)

## The distinguishing bet

Two visible from the README, both disputable by rivals: (1) **memory belongs to the
project, not the harness** — cross-harness continuity as the point, against every
harness's own native session persistence; (2) **plain markdown in git beats a vector
store** — grep-able, Obsidian-openable, rsync-backed, "no vector database to babysit."
mem0 wagers the opposite of (2).

## Why it's in this repo

- The **memory kind's** harness-facing seed (bucket index, kind added 2026-08-19).
- Candidate **second harness-independent autonomous learning loop** after ECC —
  issue #13's promotion trigger for the `learning_loop` column; needs a source read
  before it counts.
- A live test of conclusion 8's absorption story: harnesses ship native memory, yet
  this grew 2.6k stars in 3 months by sitting *outside* all of them, on exactly the
  distribution waist (MCP + hooks) the bucket's membership test names.
- Distribution-mechanism density: its support matrix is itself a survey of ~20
  harnesses' hook schemas and their quirks (which harnesses discard SessionStart
  stdout, which lack a true session-end event) — likely the richest single document
  on hook-surface fragmentation we've seen; relevant to the standards scoreboard.

## Stack & repo shape

Rust workspace (213 `.rs`, crates: core, cli, consolidate, importer companion), heavy
scripting for per-harness installers (84 `.sh`, 77 `.ps1`), SQL present (49 files —
worth checking what's stored relationally vs in the wiki), `docs/ARCHITECTURE.md`
exists. 1,276 commits in ~3 months by a known solo author (Fabio Akita).

## My take

*(empty — not yet used; stub honesty)*
