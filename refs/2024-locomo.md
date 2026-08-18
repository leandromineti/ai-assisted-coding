---
key: 2024-locomo
title: "Evaluating Very Long-Term Conversational Memory of LLM Agents"
authors: [Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, Yuwei Fang]
year: 2024
venue: ACL 2024
peer_reviewed: true
arxiv: 2402.17753
citations: "743 (149 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://snap-research.github.io/locomo/
kind: benchmark
read_depth: full   # main text (pp. 1–9, through Limitations & Broader Impacts) read end to end; appendices A–C consulted via cross-references only
retrieved: 2026-08-18
pdf: refs/pdf/2024-locomo.pdf
bears_on: [mem0, memos, memory-kind, benchmarks]
verdict: "catalogs the instrument mem0's headline numbers ride on — persona-driven *social* conversation memory, zero coding content; a vendor score here says nothing about coding-agent memory"
---

# Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo)

`retrieved: 2026-08-18` · `read_depth: full` · [ACL 2024 / project page](https://snap-research.github.io/locomo/)

## What it does

Builds LoCoMo, 50 very-long-term open-domain dialogues (~300 turns, ~9K tokens avg,
up to 35 sessions) between two LLM-simulated personas grounded in temporal event
graphs, then human-verified; and an evaluation framework with three tasks — QA over
five reasoning categories, event summarization, and multimodal dialog generation —
to measure whether models comprehend months-long conversational history (§3–4).

## Design

- **Generation, not collection**: two gpt-3.5-turbo agents with personas + causally
  linked event graphs (up to 25 events over 6–12 months), a reflect-&-respond memory
  module, and image sharing/reaction; human annotators then edited ~15% of turns and
  removed/substituted ~19% of images (§3.4). The dataset is machine-written by
  2023-era models — fluent but synthetic dynamics.
- **QA task** (§4.1): five categories — single-hop, multi-hop, temporal, open-domain,
  adversarial (unanswerable-by-design) — scored by F1 partial match against answers
  deliberately phrased with in-conversation wording.
- **Event summarization** (§4.2): summaries scored with FactScore-style atomic-fact
  precision/recall against the generating event graph — factuality, not lexical
  overlap.
- **Baselines** (§5): base LLMs (Mistral-7B, Llama-2-70B-chat, gpt-3.5/4-turbo),
  long-context gpt-3.5-turbo-16k, and RAG over three retrieval granularities —
  whole dialogs, *observations* (assertions extracted per speaker), session
  summaries — with DRAGON as retriever.

## Numbers worth keeping

- Human QA overall F1 **87.9** vs best model **32.4** (gpt-4-turbo, 4K ctx); best
  long-context **37.8** (gpt-3.5-turbo-16k) (Table 2).
- Adversarial category collapses under long context: **2.1** F1 at 16K vs 70.2 for
  gpt-4-turbo at 4K — long context amplifies hallucinated answerability (Table 2, §6.1).
- Temporal reasoning is the hardest category throughout (humans 92.6; models ~10–26).
- RAG sweet spot: observations at top-5 → **41.4** overall F1, beating both whole-dialog
  and summary granularities; summaries retrieve well (R@k 90+) but answer worse —
  "loss of information during the conversion of dialogs to summaries" (Table 3, §6.1).

## What it means for this repo

The memory kind's most-cited instrument (mem0's published results ride on it — see
`notes/05-capability-extensions/mem0.md`). Three things the catalog must remember
when a vendor number arrives: (1) the domain is **social persona chat** — no code, no
tools, no repo state; transfer to coding-agent memory is asserted, never measured;
(2) the observation-granularity RAG finding independently corroborates what ai-memory
and memos build (fact/trace-level stores over session summaries — same shape LongMemEval
later measures as round > session); (3) scores are F1 against 2023-era synthetic
conversations — a 2026 system scoring high here is not news, and saturation by
frontier models is plausible (checked: the paper itself predates them; treat any
vendor's "SOTA on LoCoMo" as unsaturation-unverified). Rule 5d instinct applies:
before believing a comparison on this instrument, ask whether it still discriminates.

## Limits

- Dataset is LLM-generated (gpt-3.5-turbo) with human patching; the authors flag it
  "may not fully reflect the nuances of real-world online conversations" (§8).
- **The public release is smaller than the paper's 50 conversations**: downstream
  evaluations describe the released LoCoMo as **10** conversations (~26K tokens, ~200
  questions each) — see [2025-mem0](2025-mem0.md) §3.1, which also drops the
  adversarial category. Numbers "on LoCoMo" from different reports may not share
  either the item set or the categories.
- 50 conversations; QA set ~7.5K questions but correlated within conversations.
- F1-on-short-phrases scoring; the authors themselves flag verbose-LLM evaluation
  trouble (§8) — no LLM judge, unlike LongMemEval/BEAM.
- English-only; closed-source generation pipeline (text-davinci-003 / gpt-3.5-turbo).
