---
key: 2026-clarifycodebench
title: "ClarifyCodeBench: Evaluating LLMs on Clarifying Ambiguous Requirements for Code Generation"
authors: [unverified]
year: 2026
venue: arXiv preprint
peer_reviewed: false
arxiv: 2607.00711
citations: "1 (0 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2607.00711
kind: benchmark
read_depth: extract   # promoted from unread 2026-08-17 — WebFetch answered targeted questions against abstract + HTML full text
retrieved: 2026-08-17
pdf: references/papers/pdf/2026-clarifycodebench.pdf
task_shape: function-level
task_count: 419
task_source: "LiveCodeBench v6 problems, manually annotated: 199 with one ambiguity, 169 with two, 51 with three"
verifier: unit-tests
ambiguity_construction: annotated-key-questions   # ten ambiguity categories with ground-truth clarification answers
user_simulator: rule-based   # matched key question → ground-truth answer; unmatched → default reply (LLM-judge does the matching)
metrics: [TKQR, ORA, pass@1]
contamination_posture: time-windowed   # inherits LiveCodeBench v6's windowing
headroom: true   # best TKQR 0.30 (DeepSeek-V3.2); pass@1 ambiguous 39–41% vs full-spec 50–52%
bears_on: [exp-02, exp-03, metrics]
verdict: "the most instrument-careful of the clarification benchmarks — annotated key questions with ground-truth answers and a default-reply fallback avoid the oracle-knows-everything proxy, and its finding that reasoning effort buys code correctness but NOT ambiguity detection bears directly on where clarification value lives"
---

# ClarifyCodeBench

`retrieved: 2026-08-17` · `read_depth: extract` · [arXiv:2607.00711](https://arxiv.org/abs/2607.00711)

## What it does

Builds a clarification benchmark on LiveCodeBench v6: 419 tasks manually annotated with
ambiguities across **ten categories** (terminology, behavior, edge cases,
indices & ranges, ordering & atomicity, output format, comparison rules, units,
collection semantics, numerical precision), each carrying annotated key questions and
ground-truth answers.

## Design

- Ambiguity density is controlled: 199 tasks with one ambiguity, 169 with two, 51 with
  three.
- Loop: if the model's question matches an annotated key question (LLM-judge does the
  matching), it receives the **ground-truth answer**; otherwise a **default reply** —
  the oracle cannot leak beyond the annotation.
- Metrics: **TKQR** (turn-discounted key question rate — nDCG-shaped, rewards asking the
  right questions early: `TKQR = DCGn/IDCGn`) and **ORA** (optimal round adherence —
  Gaussian penalty on deviating from the ideal number of clarification rounds:
  `exp(−(n−K)²/2σ²)`, σ≈0.425K), plus pass@1 on unit tests.

## Numbers worth keeping

- Best TKQR **0.30** (DeepSeek-V3.2) with ORA 0.50 — even the best model asks less than
  a third of the key questions, discounted for lateness.
- pass@1: DeepSeek-V3.2 39.1% ambiguous vs 50.0% full-spec; GPT-5 reasoning 41.1% vs
  52.5%.
- Findings as stated: strong codegen ≠ effective clarification; **more reasoning buys
  code correctness but only marginal ambiguity-detection gains**; clarification degrades
  sharply as ambiguity density rises.

## What it means for this repo

Two transfers. (1) **Apparatus**: the matched-key-question + default-reply oracle is the
cleanest answer yet to the leaky-proxy problem (contrast HumanEvalComm's
sees-the-original GPT-3.5) — the right template for any exp-03 oracle. (2) **Finding**:
"reasoning effort improves code but not ambiguity detection" is evidence that
clarification is a distinct capability from capability-at-code — which is spec-kit's bet
stated as a measurable claim, and suggests exp-02's P1 (requirements) and P2 (code) can
genuinely dissociate, exactly as preregistered.

## Limits

Extract depth; authors unverified (preprint metadata not captured); LLM-judge does the
question-matching, so TKQR inherits judge reliability at the matching step; competitive-
programming tasks, not CLI-tool building.
