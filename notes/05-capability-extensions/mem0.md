---
name: mem0
layer: 5
kind: memory
vendor: Mem0 (mem0ai, YC S24)
url: https://github.com/mem0ai/mem0
license: Apache-2.0
open_source: true
stack: [TypeScript, Python]
version: ts-v3.1.6-20-g001c2352
commit: 001c2352
first_commit: 2023-06-20
stars: 63535
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README skim; source not read
features:
  skills: true   # ships itself partly as a SKILL.md skill (skills/mem0/ in-repo, plus integrations/mem0-plugin/); presence verified by file listing, behavior not read
---

# mem0

## What it is

"The memory layer for personalized AI": an SDK (Python/TypeScript) and managed
platform that LLM-extracts memories from conversation history, stores them per
user/agent/session, and retrieves them into later context. General-purpose — built
for assistants and agent apps, not specifically for coding harnesses — but it
reaches them through integrations, and the repo carries a `skills/mem0/` SKILL.md
package plus an integrations plugin. Publishes its own benchmark results (LoCoMo
92.5, LongMemEval 94.4 for the April-2026 algorithm rewrite, per README). (README at
the pin; source unread.)

## The distinguishing bet

Memory is an **inference problem with a benchmark**, not a filing problem: an
LLM-scored extraction/consolidation algorithm behind an API, sold on recall metrics
and token efficiency — the opposite wager from ai-memory's grep-able markdown wiki.
Also the platform bet: memory as a managed service (YC company) vs a local file
artifact.

## Why it's in this repo

- The **memory kind's** SDK/API-facing seed (bucket index, kind added 2026-08-18) —
  the shape comparison against ai-memory is the kind's first real question: does
  coding-agent memory want a retrieval service or a readable wiki?
- Self-benchmarking makes it refs-relevant — instruments cataloged
  ([2024-locomo](../../refs/2024-locomo.md), [2025-longmemeval](../../refs/2025-longmemeval.md))
  and the vendor paper now read at full depth
  ([2025-mem0](../../refs/2025-mem0.md), arXiv 2504.19413, 2026-08-18). The grading
  resolved in two steps: the README's "LoCoMo 92.5" is an LLM-judge-style number from
  a later (2026) eval — it exceeds even the *paper's* best overall J (68.44), not just
  the LoCoMo paper's F1 scale — and the paper's own Table 2 shows the no-memory
  **full-context baseline beating both mem0 variants on quality (J 72.90)**. The
  honest, source-grounded claim is an efficiency frontier: near-competitive J at ~8%
  of full-context's p95 latency and a fraction of the tokens, measured on
  LoCoMo-minus-adversarial (10 conversations, abstention never tested). Both
  instruments measure social/chat-assistant memory — zero coding content — so even
  the reconciled numbers wouldn't ground coding-harness claims.
- Bucket-membership edge case worth watching: an SDK you *build into an app* is not
  obviously "installed into a harness" — its claim to this bucket runs through the
  skill/plugin integrations, not the SDK itself.

## Stack & repo shape

TS + Python monorepo (433 `.ts`, 370 `.py`, 245 `.mdx` — docs-heavy), npm + PyPI
packages, `examples/` demos, `integrations/mem0-plugin/`, in-repo `skills/mem0/`
with an architecture reference. 2,595 commits since 2023-06; company-backed.

## My take

*(empty — not yet used; stub honesty)*
