# ADR-0051 — `memory_import` joins the memory_features block

`decided: 2026-09-04` · status: **accepted**

## Decision

`memory_import` becomes the fourteenth key in the category-5 assessed block
(`memory_features:`), `group: integration`, `value_type: presence`:

> ships a path that ingests memory born outside the tool's own capture pipeline —
> rival tools' stores, repo rule files, or transcript/conversation exports — rather
> than only accumulating what its own hooks/adapters observed.

Explicitly out of scope: re-ingesting the tool's *own* exported bundles (that is
portability of its own store, already told by `memory_store`), and ordinary
document/RAG ingestion (loading docs as *content* is not importing *memory*).

## The two-instance trigger

"Competitor import (mem0)" sat on the category README's single-instance watch-list
from 2026-08-19. The second instance arrived at the ai-memory v2.0.2 release re-read
(2026-09-04):

1. **mem0** (deep-dive 2026-08-19): a manual import skill plus `auto_import.py`,
   which ships `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.windsurfrules` (cwd + git
   root) to the platform on every session start — rival rule stores ingested as
   memories.
2. **ai-memory** (v2.0.2 re-read 2026-09-04): `companions/ai-memory-importer`, a
   deliberately workspace-isolated crate that replays external corpora — OMC flat
   markdown wikis (a rival memory tool's store) and a generic conversation-export
   JSON envelope (ChatGPT/Claude-Desktop-style) — through the public hook pipeline
   as `agent=external-import` sessions. Present at the old pin too, unnoticed by the
   deep-dive; the re-read's substance tract surfaced it.

Merits check (the ADR-0049/aider discipline — the second instance must be the same
fact, not a rhyme): both ingest memory that predates the tool's own capture, and both
exist to lower the cost of *arriving* — the in-direction mirror of mem0's displacement
gate on the out-direction. Mechanisms differ (upload-to-platform vs replay-through-
hooks); the fact classified is the presence of the path, and mechanism lives in the
cell comment, the block's standing convention.

Why it discriminates *here*: the category's central question is what an independent
memory layer buys against native harness loops — the verified answer is portability
(cross-harness continuity, conclusion 14). `memory_import` is the same wager pointed
at the past: continuity with memory you already have. A key that tells the switching-
cost story in both directions belongs in the block that exists to test it.

## Argued and not admitted (with triggers)

- **Default egress**: ai-memory 2.0's background model fetch (asset in) and memos'
  publish-time telemetry (usage out) are different facts; no merge. Trigger: a second
  instance of either fact *on its own terms*.
- **Deliberate deletion**: ai-memory's tombstoned `purge-session` is one instance;
  `decay` is lifecycle, purge is operator-initiated forgetting. Trigger: a second
  tool shipping non-resurrectable purge.
- **Temporal recall** (`as_of`) and **typed relation edges**: single instances; the
  store-wager key already carries the graph-vs-files axis.

## Consequences

- Registry entry added to `docs/feature-taxonomy.yaml` (integration group, blurb
  extended); cells set on `mem0` (true) and `ai-memory` (true); all other category-5
  reports leave the key omitted = not checked, per the block's standing semantics.
- The category README's watch-list retires "competitor import (mem0)" and its
  assessed-block section moves to 14 keys, dated.
- No decoder needed: no existing prose used a prior name for this fact.
