---
key: 2025-tau2-bench
title: "τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment"
authors: [Victor Barres, Honghua Dong, Soham Ray, Xujie Si, Karthik Narasimhan]
year: 2025
venue: arXiv preprint
peer_reviewed: false
arxiv: 2506.07982
citations: "392 (53 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2506.07982
kind: benchmark
read_depth: extract   # promoted from unread 2026-08-17 — WebFetch answered targeted questions against abstract + HTML full text; PDF not read end to end
retrieved: 2026-08-17
pdf: references/papers/pdf/2025-tau2-bench.pdf
task_shape: dialogue
task_count: 279
task_source: "retail 115 + airline 50 (inherited from τ-bench) + telecom 114 eval set (from 2,285 programmatically generated)"
verifier: db-state   # "status assertions" over final world state via predefined assertion functions
ambiguity_construction: none
user_simulator: llm   # constrained by the environment's tools and observable state — the reliability fix over τ-bench
metrics: [pass^k]
headroom: true   # telecom pass^1: gpt-4.1 34%, o4-mini 42%, claude-3.7-sonnet 49%
bears_on: [metrics, exp-03]
verdict: "the dual-control successor to τ-bench — constraining the user simulator through the environment cut simulator error rates from 40–47% to 16%, which is the strongest fix yet for the τ-bench apparatus problem our tau-bench note records"
---

# τ²-Bench

`retrieved: 2026-08-17` · `read_depth: extract` · [arXiv:2506.07982](https://arxiv.org/abs/2506.07982)

## What it does

Extends τ-bench to **dual-control**: both agent and simulated user act on a shared
environment (the technical-support shape — "users need to actively participate in
modifying the state of the world"), with a new telecom domain whose tasks are generated
compositionally from atomic components.

## Design

- Domains: retail 115 + airline 50 (inherited) + **telecom 114** (eval set, drawn from
  2,285 programmatically generated tasks — compositional generator with controlled
  complexity).
- Verifier: **status assertions over final world state** ("e.g., checking if a service
  is connected") — same db/state-shape as τ-bench, not output matching.
- User simulator: LLM, but **constrained by the environment's tools and observable
  states** — behavior limited to affordances rather than free text.
- Metric: `pass^k` (fraction of k independent runs that all succeed); 4 runs per task at
  temperature 0.

## Numbers worth keeping

- Telecom pass^1: **gpt-4.1 34%, o4-mini 42%, claude-3.7-sonnet 49%** (vs gpt-4.1 74%
  retail / 56% airline) — substantial headroom at read date.
- **No-user ablation**: removing the user (agent controls all tools) *raises* gpt-4.1 by
  18 points and o4-mini by 25 — the dual-control coordination cost, isolated.
- **Simulator error rates**: telecom 16% total (6% critical) vs retail 40% (12%) and
  airline 47% (13%) — constraining the simulator through the environment is what fixed it.

## What it means for this repo

Two things. (1) The τ-bench note's core finding was that the user simulator is a free
variable that moves measured agent success by ~9pp; τ² quantifies the same apparatus
problem (40–47% simulator error in the old domains) *and demonstrates the fix* —
constrain the simulator by environment affordances rather than prompt. Directly relevant
to any exp-03 oracle design: an oracle that can only answer from a fixed fact set is the
text analog of an affordance-constrained simulator. (2) The no-user ablation is a clean
design pattern for isolating coordination cost — the same subtract-one-factor shape our
A/B arms use.

## Limits

Extract depth — full text queried, not read; the compositional generator's coverage
claims unverified; dialogue domains, not coding; pass^k needs multiple runs per task,
which an n=1 experiment budget must weigh.
