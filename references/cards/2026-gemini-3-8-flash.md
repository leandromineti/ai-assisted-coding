---
key: 2026-gemini-3-8-flash
vendor: Google DeepMind
title: "Gemini 3.8 Flash"
models_covered: [Gemini 3.8 Flash]
published: 2026-09-02
last_updated: 2026-09-02
retrieved: 2026-09-04
url: https://deepmind.google/models/model-cards/gemini-3-8-flash/
snapshot: https://web.archive.org/web/20260904224020/https://deepmind.google/models/model-cards/gemini-3-8-flash/
bears_on: [gemini-3-8-flash, knowledge_cutoff, category-1-first-party-surfaces]
---

# Gemini 3.8 Flash — Model Card

A landing-page card (no PDF found on the index), carrying **two publication stamps
that disagree in granularity** — "Published 2 September 2026" and "Published:
September, 2026" — and no separate last-updated field; `last_updated` above copies
the day-level stamp. Unlike the [3.1 Pro card](2026-gemini-3-1-pro.md), which
answers the cutoff question only through delegation, **this card states its cutoff
itself**, so the delegation analysis below matters for other facts, not that one.

## What it covers, and what it delegates

Speaks for **Gemini 3.8 Flash** only. The restricted sibling **Gemini 3.8 Flash
Cyber** (Fairwind Program access) is not covered and has no card of its own on the
index (checked 2026-09-04).

Ten sections are delegated to the **Gemini 3.7 Flash** card ("see the Gemini 3.7
Flash model card"; the Frontier Safety Assessment section says "read the"):
Architecture, Training Dataset, Training Data Processing, Hardware, Software, Known
Limitations, Acceptable Usage, Evaluation Approach, Safety Policies, Frontier
Safety Assessment.

The chain continues downward — the 3.7 card delegates its training dataset to 3.6
("Gemini 3.7 Flash is based on Gemini 3.6 Flash…"), and 3.6 to 3.5. The chain
bottom (the 3.5 Flash card) is unread; any training-data claim that has to walk the
whole chain is not yet sourced.

## Quoted passages

The cutoff, stated on this card directly (Intended Usage and Limitations):

> The knowledge cutoff date for Gemini 3.8 Flash is March 2026 – users can expect
> updated information for some domains while in others they may experience the
> model's knowledge is limited to January 2025

Two-date structure: a headline cutoff plus an in-sentence floor clause. And the
**identical sentence appears verbatim on the 3.7 and 3.6 Flash cards** (published
August and July 2026, read 2026-09-04) — a copy-forward consistent with the
"based on" chain, so the March 2026 figure is first-party and quotable for 3.8 but
is not evidence of fresh training for 3.8 specifically.

I/O spec, consistent with the API docs' exact figures (1,048,576 / 65,536):

> …with a token context window of up to 1M

> …with a 64K token output

**Consumed by** [`tools/1-models/gemini-3-8-flash.md`](../../tools/1-models/gemini-3-8-flash.md):
`knowledge_cutoff: 2026-03` — the API docs surface (models index, per-model page,
pricing page) carries no cutoff row at all, so this card is the fact's only
first-party home, the same split the category-1 index records for Google
(§ First-party surfaces worth knowing).

## Open questions

- Does a PDF version of this card exist (the 3.1 Pro card was PDF-only, this one
  page-only) — and does the page get revised in place at the next model rev?
- The "limited to January 2025" floor clause: is it a statement about this model's
  data mix or inherited prose from the chain? Only the 3.5-card bottom (unread)
  could tell.
