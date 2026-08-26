---
key: 2026-gemini-3-1-pro
vendor: Google DeepMind
title: "Gemini 3.1 Pro Model Card"
models_covered: [Gemini 3.1 Pro]
published: 2026-02
last_updated: 2026-02
retrieved: 2026-08-26
url: https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf
snapshot: https://web.archive.org/web/20260821204825/https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf
pdf: references/cards/pdf/2026-gemini-3-1-pro.pdf
bears_on: [gemini-3-1-pro, knowledge_cutoff, category-1-first-party-surfaces]
---

# Gemini 3.1 Pro — Model Card

9 pages, and **thin by design**: a specimen of the delegating card. It contains no
occurrence of "knowledge" or "cutoff" anywhere, yet it is how the cutoff question for
Gemini 3.1 Pro gets answered — through what it delegates.

## What it covers, and what it delegates

Speaks for **Gemini 3.1 Pro**. At least six sections are one line each, pointing at
[`2026-gemini-3-pro`](2026-gemini-3-pro.md): Known Limitations, Acceptable Usage,
Evaluation Approach, Safety Policies, Training Data Processing, Hardware, Software.

**The distinction that decides what transfers** — recorded because this repo got it wrong
first and corrected it the same day (2026-08-26):

- Delegating a **section** that happens to contain a model-scoped figure transfers
  nothing. The parent's cutoff sentence names *Gemini 3 Pro*; Known Limitations pointing
  there does not make it 3.1 Pro's. This is the shape that produced the Grok 4.5 retraction
  of 2026-08-17, where a figure documented for 4.6 was recorded on 4.5.
- Delegating **the fact's own subject** transfers the fact. A knowledge cutoff is a
  property of the training dataset, and this card sends the training dataset itself to the
  parent.

## Quoted passages

Model Data:

> Training Dataset: Gemini 3.1 Pro is based on Gemini 3 Pro. For more information about
> the training dataset for Gemini 3.1 Pro, see the Gemini 3 Pro model card.

The same "is based on Gemini 3 Pro" formula repeats for Training Data Processing,
Hardware, and Software — it is the card's inheritance idiom, not a stray line.

Known Limitations, for contrast (delegation of a section, not of a subject):

> Known Limitations: For more information about the known limitations for Gemini 3.1 Pro,
> see the Gemini 3 Pro model card.

**Consumed by** [`tools/1-models/gemini-3-1-pro.md`](../../tools/1-models/gemini-3-1-pro.md):
`knowledge_cutoff: January 2025`, inherited through the training-dataset delegation above
plus the parent card's figure.

## Open questions

- No first-party page yet names Gemini 3.1 Pro and a cutoff in one sentence. The card's
  landing page (`deepmind.google/models/model-cards/gemini-3-1-pro/`) and whatever Google
  publishes at GA are the candidates — the model is still Preview at six months.
- `published` and `last_updated` are both February 2026: this card has not been revised
  since release, unlike its parent.
