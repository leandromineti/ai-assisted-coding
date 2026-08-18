---
name: cognee
layer: 5
kind: memory
vendor: Topoteretes (topoteretes)
url: https://github.com/topoteretes/cognee
license: Apache-2.0
open_source: true
stack: [Python, TypeScript]
version: v1.5.0-2-gb948f88d4
commit: b948f88d4
first_commit: 2023-08-16
stars: 30103
stars_at: 2026-08-18
read_at: 2026-08-19
depth: stub   # facts from repo-facts.sh + README skim; source not read
---

# cognee

## What it is

Self-described "open-source AI memory platform for agents": Python-first pipelines
that ingest documents/conversations into a combined knowledge-graph + vector store
and serve retrieval to agents. Ships an MCP server (`cognee-mcp/` in-repo), a
frontend, and a starter kit; an `evals/` tree suggests self-benchmarking
(HotpotQA-derived). Oldest tool in the memory-kind set (first commit 2023-08-16,
predating the coding-agent wave) and the second-largest by stars (30.1k). (README +
file listing at the pin; source unread.)

## Notes for the kind comparison

SDK/platform-facing like mem0, but with the **knowledge-graph** wager: memory as
structured entity/relation extraction rather than flat memory items. MCP server
gives it a direct harness-facing path — its bucket membership doesn't need a skill
shim. Pipeline vocabulary ("cognify") and DB-agnostic backends.

## Stack & repo shape

Python-dominant (2,168 `.py`) monorepo with TS frontend; 9,781 commits — by far the
most-committed repo in the kind. `cognee-mcp/` has its own pyproject + package.json.

## My take

*(empty — not yet used; stub honesty)*
