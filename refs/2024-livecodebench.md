---
key: 2024-livecodebench
title: "LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code"
authors: [Naman Jain, King Han, Alex Gu, et al.]
year: 2024
venue: "ICLR 2025"
peer_reviewed: true
arxiv: 2403.07974
citations: "1994 (309 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2403.07974
kind: benchmark
read_depth: abstract
retrieved: 2026-08-17
task_shape: function-level
task_count: 400   # at publication (May 2023–May 2024 window); grows continuously by design
task_source: "competitive-programming problems continuously collected from LeetCode, AtCoder, CodeForces, each stamped with its release date"
verifier: unit-tests
ambiguity_construction: none
user_simulator: none
metrics: [pass@1]
contamination_posture: time-windowed   # THE canonical instance of the posture — evaluate only on problems published after a model's cutoff
headroom: true   # competitive-programming difficulty tail; current rates not checked at this depth
bears_on: [exp-02, metrics]
verdict: "the canonical time-windowed contamination defence — problems carry release dates so any model can be scored only on post-cutoff items; also evaluates self-repair/execution/test-prediction, not just generation"
---

# LiveCodeBench

`retrieved: 2026-08-17` · `read_depth: abstract` · [arXiv:2403.07974](https://arxiv.org/abs/2403.07974)

## What it does

Continuously collects competition problems from LeetCode, AtCoder, and CodeForces, each
stamped with its release date, so evaluation can be restricted to problems published
*after* a model's training cutoff — contamination controlled by construction rather than
by hope. ~400 problems in the May-2023–May-2024 window at publication; also scores
self-repair, code execution, and test-output prediction, not just generation.

## What it means for this repo

The contamination column's `time-windowed` value is this design. It is the strongest of
the three postures the matrix names (none < canary < time-windowed) because it makes
contamination *measurable* — score a model on pre- vs post-cutoff windows and the gap is
the contamination estimate. The paper reports empirical contamination/overfitting
findings on that basis (specifics not captured at abstract depth). For the repo's own
instrument the transferable idea is smaller: exp-02's fixtures are generated
deterministic archives, not public problems, so its contamination surface is the
*orchestrator's* knowledge, not the training corpus — a different threat model the
survey should distinguish. ClarifyCodeBench builds on LiveCodeBench v6 and inherits the
posture.

## Limits

Abstract depth; the specific contamination evidence (per-model pre/post-cutoff gaps) not
captured — do not cite numbers from this note; competitive-programming shape, far from
agentic CLI work.
