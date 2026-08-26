---
key: 2026-gemini-3-pro
vendor: Google DeepMind
title: "Gemini 3 Pro - Model Card"
models_covered: [Gemini 3 Pro]
published: 2025-11
last_updated: 2026-05
retrieved: 2026-08-26
url: https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf
snapshot: https://web.archive.org/web/20260820223002/https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf
pdf: references/cards/pdf/2026-gemini-3-pro.pdf
bears_on: [gemini-3-1-pro, knowledge_cutoff, category-1-first-party-surfaces]
---

# Gemini 3 Pro — Model Card

10 pages. The **parent card** of the Gemini 3 family: several later models ship thin cards
that delegate whole sections here rather than restating them, which makes this the
document that actually answers questions about them.

## What it covers, and what it delegates

Speaks for **Gemini 3 Pro only**, and says so where it matters — its family list is a
pointer, not a claim of sameness:

> Gemini 3 Pro is not a modification or a fine-tune of a prior model. Each subsequent
> model in the Gemini 3 Pro family is based on Gemini 3 Pro (see each model card for
> individual model details). The Gemini 3 Pro family includes models such as: Gemini 3 Pro
> Image, Gemini 3 Flash, Gemini 3.1 Pro, Gemini 3.1 Flash Image, Gemini 3.1 Flash-Lite,
> Gemini 3.1 Flash Live, and Gemini 3.5 Flash.

Stamped `Model Release: November 2025, Last Updated: May 2026` — a revised-in-place
document, which is why the `snapshot` above rather than the live URL is what a quote here
can be re-checked against.

## Quoted passages

Known Limitations (p. 6):

> The knowledge cutoff date for Gemini 3 Pro was January 2025.

Model Data (p. 3) separates the two halves a cutoff describes unequally — *"The
pre-training dataset was a large-scale, diverse collection…"* and *"The post-training
dataset included different types of instruction tuning data, reinforcement learning data,
and human-preference data."* A knowledge cutoff describes the pre-training half, so a
later post-training refresh would not move it.

**Consumed by** [`tools/1-models/gemini-3-1-pro.md`](../../tools/1-models/gemini-3-1-pro.md)'s
`knowledge_cutoff`, by inheritance — see
[`2026-gemini-3-1-pro`](2026-gemini-3-1-pro.md), whose card delegates its *training
dataset* here.

## Open questions

- Does the January 2025 figure move when the card is next revised? The `Last Updated`
  stamp is the cheap tell; the snapshot above is the diff baseline.
- The card was not read end to end for anything beyond the fields above — architecture,
  benchmarks, and the safety evaluations are unread here.
