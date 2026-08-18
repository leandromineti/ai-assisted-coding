# ADR-0009 — Candidates ledger: one pre-report rung, cross-layer

`decided: 2026-08-18` · status: **accepted**

## Decision

A single hand-kept, cross-layer ledger at [`notes/candidates.md`](../notes/candidates.md),
sectioned by layer. **Candidate** becomes the named first rung of the engagement
ladder — candidate → stub → survey → deep-dive — but **not** a `depth:` frontmatter
value: a candidate by definition has no clone, no pinned commit, and no report, so the
generated pipeline (`build-tool-index.py`, `comparisons/`) is untouched and `stub`
remains the floor for reports. The ledger owns everything before a report exists; the
generator owns everything after.

Conventions set by the ledger header: stars hand-typed **with a date** (a narrow,
documented exception to "never hand-type stars", which governs reports where
`repo-facts.sh` exists); append-mostly; promotion annotates the row with a dated
pointer to the new report rather than deleting it; refusal reasoning stays.

## Context

The layer-4 index had grown a "Considered, not added (2026-07-28)" table; no other
layer had one. On 2026-08-18 a single session logged four layer-4 candidates
(Conductor, pilot-shell, spec-kitty, haft) and surfaced a layer-2 sighting (qwen-code)
with nowhere to put it. The choice was per-layer tables in each index versus one
ledger; per-layer tables multiply a hand-kept pattern and invite divergent formats,
and the existing table had already outgrown its "considered, not added" framing — its
recent rows read as a field census of where a layer is growing, not a refusal list.

The rule-3 tension is accepted and documented in the ledger header: rows are primary
dated observations (miniature decision records), not derived summaries of content
living elsewhere — the same exception class as the ADR index table.

## Consequences

- The layer-4 table relocated verbatim (dated annotations where reality moved on:
  hermes-agent has since been ingested at deep-dive). Old anchor
  `notes/04-workflow-frameworks/index.md#considered-not-added-2026-07-28` is gone;
  decoder: those rows now live in `notes/candidates.md` under "Layer 4".
- Layer indexes carry a one-line pointer to the ledger instead of local tables.
- Sighting a tool in any layer now has a standard cheap move: one dated ledger row,
  no report obligation.
