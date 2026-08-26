---
key: 2026-claude-opus-5
vendor: Anthropic
title: "System Card: Claude Opus 5"
models_covered: [Claude Opus 5]
published: 2026-07-24
retrieved: 2026-08-26
url: https://www-cdn.anthropic.com/ceaf5c7ff2783855203fde8208ec311252dced5b/Claude%20Opus%205%20System%20Card.pdf
snapshot: https://web.archive.org/web/20260824142558/https://www-cdn.anthropic.com/ceaf5c7ff2783855203fde8208ec311252dced5b/Claude%20Opus%205%20System%20Card.pdf
pdf: references/cards/pdf/2026-claude-opus-5.pdf
bears_on: [claude-opus-5, knowledge_cutoff, category-1-first-party-surfaces]
---

# System Card: Claude Opus 5

198 pages, dated July 24 2026 — a **system card**, Anthropic's genre: capabilities, safety
evaluations, and release reasoning, with model specs as a small opening section. Contrast
the ~10-page DeepMind model cards, which are specs almost end to end.

## What it covers, and what it delegates

**Gemini 3.1 Pro's card and this one are pointers to opposite risks.** That card was thin
and delegated its sections to a parent; this one is self-contained for the model named in
its title — one model, no family inheritance to trace. The delegation question that decides
what a parent transfers does not arise here.

Only the specs section was read (2026-08-26); the evaluations, red-team results, and
release reasoning are unread and are the reason to come back to it.

## Quoted passages

§1.1 Model description:

> Claude Opus 5's knowledge cutoff date is May 2026.

**A second first-party surface agreeing with the first.** The models overview page carries
`reliableKnowledgeCutoff: 2026-05` and `trainingDataCutoff: 2026-05` for this model — the
two coincide, so the card's single figure raises no ambiguity about which one it means.
Where they diverge (Haiku 4.5: 2025-02 vs 2025-07) the card's phrasing would need care.

**Consumed by** [`tools/1-models/claude-opus-5.md`](../../tools/1-models/claude-opus-5.md)'s
`knowledge_cutoff`, as corroboration rather than as the origin — the value came from the
docs table and is unchanged.

## Open questions

- The URL is content-addressed (`/ceaf5c7f…/`), so a revision would land at a new path and
  this one would go stale silently rather than change under us — the inverse of the
  DeepMind failure mode. The snapshot guards replacement, not revision.
- 198 pages unread beyond §1.1. If category 1 ever wants evaluation evidence rather than
  specs, this is where it lives.
