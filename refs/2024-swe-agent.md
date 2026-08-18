---
key: 2024-swe-agent
title: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
authors: [John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press]
year: 2024
venue: NeurIPS 2024
peer_reviewed: true
arxiv: 2405.15793
citations: "1638 (161 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2405.15793
kind: empirical-study
read_depth: full   # main body + appendices A–B end to end; C (prompt listings) and D (case studies) surveyed at structure level
retrieved: 2026-08-17
pdf: refs/pdf/2024-swe-agent.pdf
bears_on: [conclusion-8, exp-03, taxonomy, metrics, design-principles]
verdict: "the academic origin of this repo's layer-2 premise — the interface between agent and computer is a measurable capability layer, worth +64% relative over a bare shell with the SAME model; its ablation table is the earliest measured H3 evidence we hold (visibility shaping and execution gating each buy points), and its iterative-search result proves interfaces can SUBTRACT (worse than no tool at all); peer-reviewed, 2,294-instance scale"
---

# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

`retrieved: 2026-08-17` · `read_depth: full` · [NeurIPS 2024, arXiv:2405.15793](https://arxiv.org/abs/2405.15793)

## What it does

Introduces the **agent-computer interface (ACI)** as a design object: LM agents are "a
new category of end user" and the interface layer between agent and computer —
commands, feedback format, context management — is where capability can be added
*without touching model weights*. Builds SWE-agent (search/nav commands, windowed
file viewer, line-range editor with integrated linter, history collapsing) and shows
GPT-4 Turbo going from 1.31% (RAG) / 11.0% (bare shell, Lite) to 12.47% full /
18.0% Lite on SWE-bench. Four stated ACI design principles: simple actions with
concise docs; compact/efficient actions; informative-but-concise feedback; guardrails
for error recovery (§2).

## Design

- Fixed LM, designed interface — the complement of our rig's fixed-harness,
  varied-model cut, and the same isolation logic (§2: "we assume a fixed LM and focus
  on designing the ACI").
- Interface improvement loop: manual trajectory inspection + grid search over ACI
  configs on a dev split (n=37) — measured interface engineering, not vibes (§4, B.1).
- The whole ACI is **configuration**: one YAML (prompt templates, command files with
  docstring frontmatter, history processor, parser) instantiates the agent (A.3).
  The framework *is* data.
- Guardrail: linter runs inside `edit`; invalid edits are discarded and re-prompted —
  a deterministic format gate at the harness layer (§3).
- Budget $4/instance; auto-submit of partial edits on cost exhaustion (§4).
- Failure taxonomy by LLM judge (GPT-4o), validated against author hand-labels on
  n=15 (87% agreement) — small validation set, noted (B.4).

## Numbers worth keeping

- Headline (Table 1): SWE-agent w/ GPT-4 Turbo **12.47%** full SWE-bench / **18.0%**
  Lite vs Shell-only 11.0% Lite (**+64% relative from the interface alone, same
  model**) vs RAG 1.31/2.67%. Claude 3 Opus: 10.46/13.0%. Avg cost $1.59–2.59 per
  resolved instance.
- Ablations (Table 3, Lite, GPT-4 Turbo — each vs 18.0 baseline):
  - edit w/o linting 15.0 (↓3.0); no edit command 10.3 (↓7.7)
  - **iterative search 12.0 (↓6.0) — WORSE than no search tool at all (15.7, ↓2.3)**
  - viewer window: 30 lines 14.3 (↓3.7), full file 12.7 (↓5.3) — non-monotone in
    context given
  - full history 15.0 (↓3.0) vs last-5-observations collapse; no demo 16.3 (↓1.7)
  - Sweep (B.1): 200-line window underperforms 100 at every setting — more visible
    context hurts twice.
- Behavior (§5.2, B.3): trajectories open with reproduction (`create`) or
  localization (`find_file`/`search_dir`); turns 5+ are edit→execute loops. 51.7% of
  all trajectories contain ≥1 failed (lint-rejected) edit; recovery odds start at
  90.5% and fall to **57.2% after a single failed edit** (Fig. 20) — error cascades
  are the mechanism, guardrails the countermeasure.
- **Succeed quickly, fail slowly** (§5.2, B.9): resolved runs median $1.21 / 12
  steps vs unresolved mean $2.52 / 21 steps; 14.3% of submit-terminated runs resolve
  vs 3.1% of cost-exhausted ones — "increasing the maximum budget or token limit are
  unlikely to substantially increase performance."
- Variance (B.5): 6 runs on Lite span 17.33–18.67% (σ≈0.49) — stable mean — while
  pass@6 hits 32.67% vs pass@1 17.94% — unstable instances. Mean-stability with
  per-instance churn, the same shape as our screening noise band.
- Contamination control (B.2): resolve rate uncorrelated with issue creation year.
- Localization: agent file-localization F1 59.05% vs BM25 45.47% (B.9). Failure
  modes: 52% incorrect/overly-specific implementations, 23.4% cascading edit
  failures (Fig. 8).

## What it means for this repo

- **Layer-2's premise, peer-reviewed and measured.** "The interface is a capability
  layer independent of the model" is this paper's thesis with numbers attached —
  +7pp over a bare shell holding the model fixed. When the taxonomy needs an
  academic citation for why harnesses are a *layer* and not plumbing, this is it.
  It also strengthens conclusion 8's reading of agent-frameworks-eval (the winning
  frameworks there are the ACI-shaped ones; this is where that design came from).
- **H3's earliest measured evidence** (folded into design-principles): the ablation
  table prices both chokepoints separately — visibility shaping (window size,
  history collapse, search result format) and execution gating (the linter
  guardrail) each buy 3–6pp. And the *enforcement* is mechanical, not prose: the
  linter discards the edit; it does not ask the model to reconsider.
- **Interfaces can subtract:** iterative search (a faithful copy of a *human* UI
  pattern) scores below having no search tool. Tool existence is not tool value —
  relevant to issue #3 (does PTC earn a column) and to reading any harness's
  feature matrix: a ✓ can be negative.
- **A format gate with measured value** (folded into the cross-cutting gate
  vocabulary): exp-01 credited *measured* gates and found format/prose gates cheap;
  SWE-agent shows a deterministic format gate (linting) buying +3.0pp at layer 2 —
  the gate-vocabulary axes (deterministic?, domain-contact?) now have a priced
  instance in the no-domain-contact quadrant.
- **The failure-cascade result rhymes with exp-02's:** Haiku's blanket `rc=1` never
  cascades but never discriminates; SWE-agent's linter exists precisely because
  recovery odds halve after one failed edit. Error-*containment* design is a
  capability axis in both directions.
- **Budget insensitivity** ("succeed quickly, fail slowly") supports H6's
  designed-termination framing and our wall-clock planning: paying for more turns
  mostly buys longer failures.

## Limits

- 2024 models (GPT-4 Turbo, Claude 3 Opus) — absolute numbers are two model
  generations stale; the *deltas* between interface variants are the durable part,
  and even those could compress as models get better at raw shells.
- Ablations are n=300 (Lite), single run per cell — the 6-run variance study
  (σ≈0.49) suggests cell differences under ~1pp are noise; the headline ablation
  gaps (3–7.7pp) clear that bar.
- Failure taxonomy validated on only 15 hand-labeled instances (87% agreement).
- ACI tuned on SWE-bench dev with GPT-4 then reused for Claude — portability shown
  once, to one other model, both same-era.
- SWE-bench validity issues (68.3% invalid items, per swebench-verified-2024) apply
  to the full-set numbers here; Lite is curated but predates Verified.
