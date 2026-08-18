---
name: everos
layer: 5
kind: memory
vendor: EverMind AI (EverMind-AI)
url: https://github.com/EverMind-AI/EverOS
license: Apache-2.0
open_source: true
stack: [Python]
version: v1.2.3-5-gd07cddc
commit: d07cddc
first_commit: 2026-06-05
stars: 12126
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README skim; source not read
harness_targets: "use-cases/claude-code-plugin/ exists in-repo (file listing at the pin) — a Claude Code plugin as a shipped use case; other harness targets not checked"
---

# everos

## What it is

"Ever OS" — a memory OS for agents from EverMind: durable memory writes plus
retrieval (keyword search first, per the quickstart: "one OpenRouter API key is
enough to start EverOS, write durable memories, and retrieve them"). Youngest
tool in the memory-kind set (first commit 2026-06-05) and the fastest to stars per
month after ai-memory (12.1k in ~10 weeks). Ships a Claude Code plugin among its
use cases. (README + file listing at the pin; source unread.)

## Notes for the kind comparison

Third instance of the "memory OS" branding (with MemOS and, loosely, mem0's
"memory layer") — the kind's vendors are converging on OS-metaphor positioning,
which usually signals scope ambition beyond a store: lifecycle, policies, and
retrieval as a managed whole. The in-repo Claude Code plugin makes it
harness-facing without the MCP-installer machinery ai-memory built.

## Stack & repo shape

Python-dominant (657 `.py`), only 88 commits — very high stars-to-commits ratio
(launch-marketing signal worth noting when reading its numbers); `.claude/rules/`
in-repo means the project itself is developed with agent rules files.

## My take

*(empty — not yet used; stub honesty)*
