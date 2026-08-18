---
key: 2024-humanevalcomm
title: "HumanEvalComm: Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agents"
authors: [Jie JW Wu, Fatemeh H Fard]
year: 2024
venue: ACM TOSEM 34(7)
peer_reviewed: true
arxiv: 2406.00215
citations: "34 (1 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2406.00215
kind: benchmark
read_depth: extract   # promoted from unread 2026-08-17 — WebFetch answered targeted questions against the HTML full text
retrieved: 2026-08-17
pdf: refs/pdf/2024-humanevalcomm.pdf
task_shape: function-level
task_count: 762
task_source: "HumanEval's 164 problems, degraded into variants: 1a ambiguity 164 · 1c inconsistency 164 · 1p incompleteness 164 · 2ac 162 · 2ap 74 · 2cp 34"
verifier: unit-tests
ambiguity_construction: degradation-of-complete-spec   # three defect types applied singly and in pairs
user_simulator: llm   # GPT-3.5 evaluator answers clarifying questions, seeing modified + ORIGINAL problem
metrics: [communication-rate, good-question-rate, pass@1, test-pass-rate]
contamination_posture: none   # HumanEval-derived — maximally public base set
headroom: true   # >60% of code-LLM responses still emit code instead of asking; pass@1 drops 35–52%
bears_on: [exp-02, exp-03, metrics]
verdict: "the degradation-construction benchmark — its headline (>60% of responses answer degraded specs with code, not questions) is the field-scale version of what exp-02's P1 rubric probes, but its clarification answers come from a GPT-3.5 proxy that has seen the original problem, an apparatus choice τ-bench taught us to distrust"
---

# HumanEvalComm

`retrieved: 2026-08-17` · `read_depth: extract` · [arXiv:2406.00215](https://arxiv.org/abs/2406.00215)

## What it does

Degrades HumanEval's 164 problems along three defect axes — ambiguity, inconsistency,
incompleteness, singly and pairwise — into **762 variants**, then measures whether models
*ask* before coding, and what asking buys.

## Design

- Construction: each variant applies one defect type (1a/1c/1p, 164 each) or a pair
  (2ac 162, 2ap 74, 2cp 34 — pairs kept only where the combination produces a genuinely
  different description).
- Loop: model answers a degraded problem; if it asks questions, a **GPT-3.5 evaluator**
  answers them — with access to the modified *and original* problem — and rates question
  quality (3=Good/2=Fair/1=Bad).
- Metrics: **Communication Rate** (% responses with no code — i.e., the model asked
  instead), **Good Question Rate**, then pass@1 / test-pass-rate on the final code
  against unit tests.

## Numbers worth keeping

- ">60% of responses … still generate code rather than ask questions" on degraded
  problems (code LLMs).
- pass@1 drops **35–52%** and test-pass-rate **17–35%** on degraded vs original problems.
- Their agent (Okanagan) lifts Communication Rate +58pp absolute and Good Question Rate
  +38pp, buying pass@1 +8pp and test-pass-rate +7pp.

## What it means for this repo

The don't-ask default is quantified at scale: models overwhelmingly answer broken specs
with code. That is the behavior exp-02's P1 rubric (R4: ambiguities surfaced) probes per
arm, and spec-kit's `/clarify` is a layer-4 mechanism aimed at exactly this — so
HumanEvalComm gives the field-scale prior for what an unaided arm should do (not ask).
Apparatus caveat that transfers directly: the question-answering proxy *sees the original
problem* — the same oracle-knows-the-answer shape whose sensitivity τ-bench measured at
~9pp. Any exp-03 oracle should be constrained the τ²-bench way instead.

## Limits

Extract depth; function-level tasks far below exp-02's task size; LLM-judged question
quality (GPT-3.5, dated) — the Good Question Rate inherits judge reliability issues;
contamination maximal (HumanEval base).
