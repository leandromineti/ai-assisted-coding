---
key: 2026-gpt-6-astra
vendor: OpenAI
title: "GPT-6 Astra System Card"
models_covered: [GPT-6 Astra]
published: 2026-09-03
last_updated: 2026-09-03
retrieved: 2026-09-04
url: https://deploymentsafety.openai.com/gpt-6-astra
snapshot: https://web.archive.org/web/20260904224247/https://deploymentsafety.openai.com/gpt-6-astra
bears_on: [gpt-6-astra, category-1-first-party-surfaces]
---

# GPT-6 Astra System Card

Read 2026-09-04 at question depth (targeted sections + a full-text search for
specific terms), not end to end. **The card lives on a new first-party surface**:
`deploymentsafety.openai.com` ("OpenAI Deployment Safety Hub"), a hosted page with
an in-page PDF at `/gpt-6-astra/gpt-6-astra.pdf` — a rewritten-in-place page, not
the content-addressed CDN pattern of Anthropic cards, so the snapshot above is the
record. "Published September 3, 2026"; no separate last-updated stamp.

## What it covers, and what it delegates

Titled for and about **GPT-6 Astra**, comparing throughout against GPT-5.6 Sol — but
it carries **no explicit scope sentence** ("this card covers…"), and **GPT-6 Astra
Pro is never mentioned in it**. `models_covered` above records the title's subject,
not a stated scope. No delegation idiom found (unlike DeepMind's chained Flash
cards).

## Quoted passages

Production misalignment monitoring can end API tasks — the wire-behavior fact that
made this card worth reading before any probe touches the model:

> When the system detects a potentially high-severity issue, it can automatically
> pause or end the affected conversation. … Some conversations, including those
> stopped through the API, cannot be resumed.

And the monitoring has an interface boundary:

> We do not apply this monitoring system to Astra in the Chat Completions API,
> because that interface does not allow the model to reason and use tools at the
> same time.

Why reasoning cannot be disabled (a vendor documenting *why* a knob is withheld):

> Note we do not currently have plans to make reasoning=None available.

A self-published negative result:

> GPT-6 Astra's monitorability has decreased relative to GPT-5.6 Sol.

**Checked absence (rule 1b):** the card states **no knowledge cutoff**. "cutoff"
occurs exactly once in the full text and dates nothing: an internal
*"ExploitBench - Internal Port (June–August 2026)"* dataset is described as
containing *"only recent new vulnerabilities disclosed after Astra's knowledge
cutoff"*. Section 2 (Model Data and Training) gives filtering and RL process, no
date. The Apr 30, 2026 cutoff is a docs-page-only fact.

**Consumed by** [`tools/1-models/gpt-6-astra.md`](../../tools/1-models/gpt-6-astra.md):
the misalignment-monitoring stop behavior (§ body), the always-on reasoning
rationale, and the cutoff's checked absence.

## Open questions

- Does the PDF twin (`/gpt-6-astra/gpt-6-astra.pdf`) match the page, and which gets
  revised first?
- The "Daybreak" program (launch post: relaxes the Critical-threshold cyber
  safeguards for vetted users) — does the card describe its criteria? Not searched
  for; the card was read at question depth only.
- Astra Pro: no card, no API page, no pricing — where will its record live?
