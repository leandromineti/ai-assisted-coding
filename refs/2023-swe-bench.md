---
key: 2023-swe-bench
title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
authors: [Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, et al.]
year: 2023
venue: "ICLR 2024"
peer_reviewed: true
arxiv: 2310.06770
citations: "3401 (535 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2310.06770
kind: benchmark
read_depth: abstract
retrieved: 2026-08-17
task_shape: repo-issue
task_count: 2294
task_source: "real GitHub issues + their fixing PRs across 12 popular Python repositories"
verifier: hidden-tests
ambiguity_construction: none
user_simulator: none
metrics: [resolve-rate]
contamination_posture: none   # public GitHub history — the contamination case study of the field
headroom: true   # at publication: best model (Claude 2) resolved 1.96%; the headroom has been consumed since — current rates not checked at this depth
bears_on: [conclusion-2, exp-02]
verdict: "the field's de-facto agentic benchmark and its cautionary tale in one — launched with enormous headroom (1.96% resolve) and later needed SWE-bench Verified to remove the 68.3% of items that were invalid, proving headroom and validity are independent failures"
---

# SWE-bench

`retrieved: 2026-08-17` · `read_depth: abstract` · [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)

## What it does

2,294 task instances from real GitHub issues and their fixing PRs across 12 Python
repositories; the model edits the codebase to resolve the issue, scored by resolve rate
against held-out tests.

## Numbers worth keeping

- At publication: "the best-performing model, Claude 2, is able to solve a mere 1.96% of
  the issues" — the largest launch headroom of any major coding benchmark.
- Later found (see [`swebench-verified-2024.md`](swebench-verified-2024.md)): 68.3% of
  sampled items were invalid — 38.3% underspecified, 61.1% with tests rejecting valid
  solutions.

## What it means for this repo

The two-sided lesson in one benchmark: massive headroom at launch did **not** mean the
instrument was sound (the Verified filtering came later and removed two-thirds of items),
and public task provenance made it the field's contamination case study. Conclusion 2's
confound also lives here — SWE-bench leaderboard entries are model+scaffold pairs.
Headroom, validity, and contamination are three independent properties; exp-02's
instrument must clear all three separately.

## Limits

Abstract depth; Python-only monoculture (the Aider-polyglot critique); resolve rates in
2026 not checked here — the headroom cell reflects publication time plus the known
saturation trajectory, not a current measurement.
