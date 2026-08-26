---
key: 2025-agent-frameworks-eval
title: "A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks"
authors: [Zhuowen Yin, Cuifeng Gao, Chunsong Fan, Wenzhang Yang, Yinxing Xue, Lijun Zhang]
year: 2025
venue: arXiv preprint (ACM template, "publication date November 2025", no venue named — v1 2025-11-02)
peer_reviewed: false
arxiv: 2511.00872
citations: "6 (0 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2511.00872
kind: empirical-study
read_depth: full
retrieved: 2026-08-17   # PDF refetched this date — the 2026-07-31 cache was lost in the 2026-08-06 server rebuild
pdf: references/papers/pdf/2025-agent-frameworks-eval.pdf
bears_on: [conclusion-6, conclusion-8, conclusion-11, exp-03, metrics]
verdict: "does NOT preempt exp-03 — no framework-less control anywhere in its 7×3 grid, which is exactly our question; corroborates the ceremony-is-cost decomposition at framework scale (single-agent beats multi-agent on all three tasks, 'specialized tools > more agents'); its correction-rate metric is worth borrowing WITH its own caveat (zero corrections = no self-monitoring, not efficiency); several internal inconsistencies between abstract, tables, and answer boxes — cite tables, not prose"
---

# A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks

`retrieved: 2026-08-17` · `read_depth: full` · [arXiv:2511.00872](https://arxiv.org/abs/2511.00872)

## What it does

Runs seven general-purpose agent frameworks (AgentOrchestra, OWL, SE-Agent×3
iterations, Trae, GPTswarm, OpenHands, SWE-Agent) across three code-centric tasks —
software development (SRDD, 1,200 prompts), vulnerability detection (LLM-SmartAudit,
115 smart contracts), program repair (SWE-bench Lite, 300 issues) — on one backend LLM
(DeepSeek-V3.1), measuring effectiveness (RQ1), efficiency (RQ2: trajectory steps,
correction attempts/rate), and overhead (RQ3: dollars, tokens, stage-attributed token
breakdown). Claims to be the first systematic framework-vs-framework comparison on SE
tasks (§6).

## Design

- **Inclusion rule** (§3.2): general-purpose (must run all three tasks) + open-source.
  Excludes task-specific agents — and, silently, every commercial harness.
- **One backend LLM** for all frameworks: DeepSeek-V3.1, step limit 100, default
  toolsets, benchmark-native prompts (ChatDev's for SRDD, LLM-SmartAudit's,
  SWE-Agent's adapted for repair) (§3.4). Model-isolated in our conclusion-2 sense —
  they fixed the model and varied the *harness/framework*, the complementary cut to
  our rig's fixed-harness-varied-model calibration.
- **No plain baseline.** Nowhere in the 7×3 grid is there a framework-less
  single-prompt control. Every number is framework-vs-framework.
- **Metrics** (§3.4, Table 3): dev quality = ChatDev's embedding-scored
  Completeness × Executability × Consistency; vuln = TP/(TP+FP); repair = official
  SWE-bench Lite harness. Efficiency = avg trajectory steps + correction attempts +
  correction rate. Overhead = USD + input/output tokens + per-stage breakdown
  (execution/editing/thinking/management; per-sub-agent for multi-agent systems).
- SE-Agent's three "iterations" are reported as three columns throughout —
  effectively 9 subject-columns.

## Numbers worth keeping

- Dev (Table 4): OpenHands best quality **0.47** (executability 1.00 across
  categories); AgentOrchestra best completeness 0.86 but quality 0.36; SE-Agent
  Iter-3 quality collapses to 0.15 (executability 0.26).
- Vuln (Table 5): totals 44–76% by count; Gas Limitation ~0% for every framework;
  RP/UD/RE near-100% for every framework — the discriminating items are family-level,
  not framework-level. (See Limits for the percentage inconsistencies.)
- Repair (Table 6): SE-Agent Iter-3 **161/300 (54%)** best; SWE-Agent 159 (53%);
  OpenHands 146 (49%); **AgentOrchestra 10 (3%), GPTswarm 15 (5%), OWL 31 (10%)** —
  the three failures are diff-format failures: no patch tooling, so patches don't
  apply (§4.1, §5.1). Tooling artifact, not reasoning.
- Efficiency (Tables 7–9): AgentOrchestra correction rate 41–45% across tasks
  (highest); GPTswarm fixed 3-cycle CodeReact → 2.9 steps on repair; OpenHands 25.2
  correction attempts on repair (36% of its steps).
- Overhead (Tables 10–11): whole study **$875.05**; AgentOrchestra $370.19 (42% of
  it); GPTswarm $16.29 total. OpenHands consumed **1.26B input tokens** on dev alone
  but cache pricing ($0.07/M cached vs $0.56/M) kept it to $39.98. Stage breakdown:
  multi-agent spend concentrates in planning agents (AgentOrchestra planning 66–67%
  of tokens on every task); single-agent spend concentrates in execution+editing.
- SE-Agent vertical iteration: repair 47.33% → 53.00% → 53.67% across iterations
  (§5.1) — trajectory summarization as training-free improvement.

## What it means for this repo

- **Exp-03 is not preempted — its gap is our argument.** The study's own framing
  ("first systematic comparison") plus the absent plain control means the
  framework-vs-plain question that exp-02 answered and exp-03 extends is untouched in
  the literature this paper surveys (§6 confirms: prior empirical work is
  task-specific or architecture-focused). Cite this when positioning exp-03.
- **Conclusion 6/11 corroborated at framework scale:** single-agent beats multi-agent
  on *all three tasks* (§5.1, contradicting Gao et al.'s multi-agent-for-complex-tasks
  finding, which they cite); their mechanism story — coordination overhead, context
  overflow, inter-agent hallucination propagation, "specialized tools yield superior
  results compared to adding dedicated agents" — is our ceremony-vs-mechanism
  decomposition wearing architecture vocabulary. The repair-failure mechanism
  (AgentOrchestra/OWL/GPTswarm losing 90+ points to missing patch tooling) is their
  version of our T3a-by-design finding: outcome gaps trace to tooling and decisions,
  not intelligence.
- **Conclusion 8 echo:** the winning configurations are the harness-shaped ones
  (SWE-Agent's ACI, OpenHands' event stream + tool library) — capability living in
  the tool interface, not the orchestration graph.
- **Metric to borrow, with its caveat (→ metrics.md):** correction rate — but the
  paper's sharpest methodological point is that **zero corrections signals missing
  self-monitoring, not efficiency** (GPTswarm/OWL at ~0 corrections *and* ~0 repair
  rate, §4.2). Any future use here must read it jointly with effectiveness.
- **Their stage-attributed token breakdown** validates exp-02's per-step cost ledger
  as the right instrument shape — ours is finer (per pipeline step with artifacts;
  theirs is regex-classified action categories).

## Limits

- **Internal inconsistencies, found by this read:** the abstract says AgentOrchestra
  has the longest trajectories, the RQ2 answer box says SE-Agent (Iter-3), and
  Table 7 says OpenHands (81.28 steps on dev) — three different answers to the same
  question. Vuln headline "GPTswarm 77%" doesn't match its own Table 5 (80/115 =
  70%, printed as "78%"; SWE-Agent's 87/115 = 76% is the table's actual maximum).
  Several table percentages don't match their counts. A truncated sentence in §4.1
  ("fully repaired (100This indicates…"). Trust tables over prose, and totals over
  percentages — and treat every headline claim as needing a table check.
- v1 preprint, ACM template with placeholder DOI, no named venue; not peer-reviewed.
- Vuln task is smart contracts only (Solidity) — narrow proxy for "vulnerability
  detection"; SRDD prompts are ChatGPT-3.5-generated task descriptions (synthetic).
- One backend LLM (DeepSeek-V3.1) — framework rankings may not transfer across
  models (they acknowledge, §5.2).
- Dev "quality" is ChatDev's embedding-based script — executability is binary-ish
  but completeness/consistency are similarity scores, adjacent to the
  structural-completeness trap conclusion 4 warns about.
- Benchmark-native prompts differ per task and were "adapted" for frameworks not
  built for them — a per-framework prompt confound the paper does not quantify.
