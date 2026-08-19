# ADR-0013 — A third registry block: `memory_features` for layer-5 memory tools

`decided: 2026-08-19` · status: **accepted**

## Decision

The feature taxonomy gains a third block, **`memory_features`** — 11 keys assessed on
layer-5 reports with `kind: memory` (`applies_to: [5]`; the generator's row filter is
`layer == 5 and kind == "memory"`). The four comparison axes the reading arc already
used in prose (store wager, capture path, recall injection, scope) plus seven
discriminating bets (tiers, hybrid retrieval, decay, injection trust boundary,
deployment mode, harness installer, rule extraction). Rendered as a third matrix
section in `comparisons/features.md`.

Three scoping rules:

- **No `kind_link` on memory entries.** A `kind_link: memory` entry would make the
  cross-layer table's demand and supply the *same seven tools* — a self-referential
  row. Layer-5 supply participation already flows through the layer-2 `learning_loop`
  entry's existing `kind_link: memory`, which stays the single bleed row.
- **Descriptive enums are not grades.** Values like `files-git | vector | graph | rows`
  follow the layer-4 `state_store` precedent: they describe a mechanism choice, they do
  not rank enforcement (ADR-0011's ladder). Admission requires two verified instances
  of the *characteristic* (issue #2), not per enum variant — the stricter per-variant
  rule governs boolean→enum *promotions* (issue #13) and is unchanged.
- **Cells only where reports were read.** Four of seven memory-kind reports are above
  stub depth (ai-memory deep-dive; mem0/memos/cognee surveys); only they get blocks.
  Stubs render as dots.

This partially resolves ADR-0010's deferred block question in the **more-blocks**
direction: blocks multiply per assessed category rather than unifying into one
namespace. 0010 is referenced, not edited.

## Context

The memory-kind reading arc (issue #18, conclusion 13) ended with a four-wager,
four-posture comparison living in prose across five files and seven reports carrying
ad-hoc layer-2 keys — the registry had no `applies_to: [5]` entry at all. Each of the
11 admitted keys met the two-instance bar in the arc's existing reads before this
pass; the registry notes carry the per-key instances.

Considered and parked (meet the instance bar, below the interest bar): `mcp_surface`
(redundant with capture/recall vocabulary), `dedup`. Recorded as differentiators, not
keys — the **single-instance bets**, which are where the category's identity actually
lives: zero-LLM default path (ai-memory), git-versioned store (ai-memory),
native-memory displacement (mem0's PreToolUse block of Claude Code's own writes),
competitor import (mem0), skill crystallization (memos), provenance audit (ai-memory),
and — flagged loudest — **cross-harness continuity as a working mechanism has exactly
one source-verified instance** (ai-memory's thin baton) despite being the kind's
headline bet.

## Consequences

- `comparisons/features.md` gains a per-kind matrix (7 rows, 4 populated); the
  cross-layer table is unchanged by construction.
- The generator gains `MEMORY_FEATURE_KEYS` plus a `KNOWN_BLOCKS` guard — an
  unregistered block name previously produced a silent empty key list.
- Layer-5 rows STAY in the layer-2 matrix (their `learning_loop`/`skills` cells are
  verified data); the new block supplements, it does not re-home.
- Precedent set: per-kind blocks are the pattern for future kind assessments (hooks,
  skills) — each via its own ADR with the instance bar met first.
