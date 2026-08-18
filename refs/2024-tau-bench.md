---
key: 2024-tau-bench
title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
authors: [Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan]
year: 2024
venue: ICLR 2025
peer_reviewed: true
arxiv: 2406.12045
citations: "979 (133 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2406.12045
kind: benchmark
read_depth: extract
retrieved: 2026-07-31
pdf: refs/pdf/2024-tau-bench.pdf
task_shape: dialogue
task_count: 165
task_source: hand-authored (τ-retail 115 + τ-airline 50)
verifier: db-state
ambiguity_construction: none
user_simulator: llm
metrics: [pass^k, pass@k]
contamination_posture: none
headroom: true
bears_on: [metrics, exp-03, methodology-5d]
verdict: "source of pass^k — the reliability metric we need, since >60% average success collapses to <25% when the same task must be solved 8 times"
---

# τ-bench

`retrieved: 2026-07-31` · `read_depth: **extract**` — I read **pp. 5–8 directly** (metric
definition, benchmark construction, experiments, main results, failure analysis). Abstract and
headline results also confirmed from the paper page; **pp. 1–4 and the appendices are unread**,
so treat anything about its framing or related work as unverified here. ·
[arXiv:2406.12045](https://arxiv.org/abs/2406.12045) · ICLR 2025

## What it does

Evaluates an agent conversing with an LLM-simulated user while calling domain API tools under a
written domain policy. Success is decided by comparing the **final database state** against an
annotated target, plus substring checks that required information was conveyed — deliberately
avoiding LLM-judge subjectivity. Two domains: τ-retail (115 tasks) and τ-airline (50 tasks).

## Numbers worth keeping

**`pass^k` — the metric to adopt** (§3, p. 5). With `n` trials per task of which `c` succeed:

```
pass^k  = E_task[ C(c,k) / C(n,k) ]          # all k trials succeed
pass@k  = 1 − E_task[ C(n−c,k) / C(n,k) ]    # at least one succeeds
pass^1 = pass@1 = E[r] = E[c/n]
```

The user prompt and database transitions are fixed across trials; only LM sampling of user and
agent messages varies. So `pass^k` isolates **reliability under conversational variation with
the same underlying semantics** — which is exactly the property a workflow framework claims to
improve.

**The reliability collapse** (§5.1, Figure 4): gpt-4o function-calling has >60% average task
success on τ-retail, and **pass^8 drops below 25%**. Their words: it matters "not just to build
agents with high average success (pass^1), but with more robustness and consistency (pass^k
trend)."

pass^1 by model, function calling (Table 2, retail / airline / avg): gpt-4o **61.2 / 35.2 /
48.2** · gpt-4-turbo 57.7 / 32.4 / 45.1 · claude-3-opus 44.2 / 34.7 / 39.5 · claude-3-sonnet
26.3 / 27.6 / 27.0 · gemini-1.5-pro 21.7 / 14.0 / 17.9 · claude-3-haiku 19.0 / 14.4 / 16.7 ·
llama-3-70B 14.8 / 14.4 / 14.6.

**Policy documents are barely used** (Table 3): removing the domain policy from the system
prompt costs gpt-4o only 4.4% on τ-retail (61.2 → 56.8) but 22.4% on τ-airline (33.2 → 10.8),
where rules are more complex. In the simple domain, success "mostly stem[s] from using tools in
an intuitive and common sense way" rather than from following the written policy.

**Cost** (§5.1): gpt-4o agent $0.38/task + gpt-4 user simulation $0.23/task; one trial across
τ-retail ≈ $200. Input prompt is 95.9% of agent cost.

**Failure taxonomy** (Figure 5, 36 failed gpt-4o trajectories): wrong argument 33.3%, wrong
info 22.2%, wrong decision 25.0%, partially resolved 19.4%. Wrong-argument + wrong-info together
are 55% of failures.

## What it means for this repo

**1. `pass^k` is the reliability instrument we're missing.** Every measurement in exp-01 and
exp-02 is n=1 per arm, so a framework whose value is *consistency* rather than peak quality is
invisible to us by construction. At Run A's measured $0.374, k=5 costs under $2 — the objection
to replication was never cost, it was an assumption we never priced. This is the concrete
metric behind issue #4's replication option.

**2. It shows the ceiling problem is not unique to us.** A benchmark can look healthy on
average success and still be uninformative about reliability. Reporting a single score *is* the
methodological error, independent of instrument headroom.

**3. Its policy-ablation result is a caution for conclusion 6.** In the simple domain, the
agent succeeded without reading the rules. Our tarpeek task is a *simple* domain by the same
standard — so a framework's specification and gate artifacts may be similarly bypassable there,
and a null result on a small task would not generalise to a complex one.

**4. Its verifier design is worth copying** — final-state comparison against annotated ground
truth, not an LLM judge. That is what the rig's hidden pytest verifier already does, and it is
reassuring that a peer-reviewed benchmark reached the same choice for the same stated reason.

## Limits

- **My read is partial** (pp. 5–8); the note's claims are confined to those pages.
- 2024 paper; models are gpt-4o / claude-3 era. Absolute numbers are stale; the metric and the
  pass^1-vs-pass^k gap are the durable contributions.
- Tasks are hand-authored customer-service dialogues, not software engineering — the *metric*
  transfers, the domain does not.
- LLM-simulated user, subject to [`lost-in-simulation.md`](lost-in-simulation.md)'s critique,
  which used this very benchmark as its testbed and found ~9pp of measured performance riding on
  the choice of user model.
- No contamination defence; hand-authored 2024 tasks may now be in training data.
