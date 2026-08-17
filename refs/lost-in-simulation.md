---
key: lost-in-simulation
title: "Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations"
authors: [Preethi Seshadri, Samuel Cahyawijaya, Ayomide Odumakinde, Sameer Singh, Seraphina Goldfarb-Tarrant]
year: 2026
venue: arXiv preprint
peer_reviewed: false
arxiv: 2601.17087
citations: "25 (3 influential) — Semantic Scholar"
citations_at: 2026-08-17
url: https://arxiv.org/abs/2601.17087
kind: critique
read_depth: full
retrieved: 2026-07-31
pdf: refs/pdf/lost-in-simulation.pdf
bears_on: [exp-03, metrics, methodology-8]
verdict: "the reason to prefer a rule-based simulator: swapping only the user LLM moves measured agent success by 9pp, and simulated users are systematically miscalibrated against real humans"
---

# Lost in Simulation

`retrieved: 2026-07-31` · `read_depth: full` (body pp. 1–9 of 16; remainder references +
appendices) · [arXiv:2601.17087](https://arxiv.org/abs/2601.17087) v2, 28 Jan 2026

## What it does

Runs a **real human user study** against τ-Bench retail tasks — participants in the US, India,
Kenya and Nigeria, ~40 per age × dialect/country group — and compares agent performance with
real users against agent performance with LLM-simulated users. The agent is held fixed
(GPT-4o) so the only thing varying is who is on the other side.

Three questions: **robustness** (does the choice of user LLM change results?), **validity**
(do simulated results predict real ones?), **fairness** (does simulation proxy some
populations better than others?).

## Design

- τ-Bench retail (115 tasks); 18 tasks sampled to cover six difficulty levels, where difficulty
  is defined empirically by running the benchmark 5× with GPT-4o as both agent and user
  (success 0/5 … 5/5 → 0–100%). Three tasks per level.
- **ECE_Human–LLM** = Σᵢ wᵢ · |sᵢ^(Human) − sᵢ^(LLM)| — a calibration-error adaptation
  measuring the weighted absolute deviation between agent success with simulated vs real users
  across difficulty levels; 0 = perfectly calibrated, reported ×100. This is the metric to use
  if we ever validate our own oracle against humans.
- US participants stratified by dialect (Standard American English vs African American
  Vernacular English) and age (18–34, 35–54, 55+).

## Numbers worth keeping

**Robustness (Table 1) — the single most useful number for us.** τ-Bench retail success rate,
*same agent*, varying only the **user** model:

| User model | Agent success (%) |
|---|---|
| GPT-4o | 67.8 ± 1.2 |
| Sonnet 3.7 | 67.0 ± 3.3 |
| **Sonnet 4.5** | **75.9 ± 3.5** |
| Kimi-K2-Thinking | 71.3 ± 1.9 |

A **~9-percentage-point** swing in measured agent performance from swapping the simulated user
alone. An apparatus choice masquerading as a result.

**Validity (§4.2).** US participants: agent success **45.2%**, ECE **15.1**. Miscalibration is
not uniform — worst in the 0% and 60% difficulty bins (ECE 25.9 across the two). Direction
matters: simulated users **underestimate** agent success on the hardest tasks (real humans
30.8%) and **overestimate** it on moderately difficult ones (real humans 39.0%).

**Fairness (§4.3).** SAE 50.6% success / ECE 11.7 vs **AAVE 39.4% / ECE 20.3** — 11.2 points
worse performance and 8.6 points worse calibration (GEE β = 0.61, p < 0.001). The dialect gap
*widens with age*: ~12 points for 35–54, ~19 points for 55+ (β = 0.67, p = 0.01; β = 1.24,
p = 0.001). Cross-country differences (India 46.2, Kenya 43.5, Nigeria 43.7) are **not**
statistically significant (p > 0.49); simulation is best calibrated to SAE (13.0) and worst to
AAVE and India (both 18.9).

**Conversational artifacts (§4.4.1).** Simulated users ask questions in **18.8%** of their
turns vs **9.8%** for humans, and use politeness markers in **39.2%** vs **19.9%**. Nigerian
participants ask questions in only 4.3% of turns. Prompting simulated users to limit politeness
measurably shifts calibration (Appendix A.6).

**Error profiles (§4.4.2, Tables 4–5).** Agents make output errors far more often against
simulated users (**31.4%** vs 12.2–23.6% for humans) but omit or add actions *less*. Manually
annotated failure attribution (n = 45 per condition): with simulated users the **agent** is
blamed 48.9% of the time vs 24.5% with humans, while with humans the **user** is the primary
source of failure 62.2% vs 40.0%. Their reading: simulated users "exhibit more precise
instruction following or adapt more readily to agent responses," so simulation-based evaluation
**overemphasises agent execution errors** and hides the difficulty real users introduce.

## What it means for this repo

**1. It is the reason to prefer [ClarEval](clareval.md)'s rule-based simulator over an LLM
proxy.** The 9-point robustness swing means an LLM oracle makes the *apparatus* a free variable
in the result — precisely the failure methodology 8a was written for. A rule-based
trigger/response table has no such degree of freedom, and ClarEval validates it at 96.5%
agreement with an LLM judge. If we do use an LLM oracle, this paper's own recommendation
applies: run it under **multiple** user models and report the spread rather than picking one.

**2. It bounds what an oracle-based attention measurement can claim.** Simulated users are more
accommodating and more precise than real people, so any attention cost we measure against an
oracle is a **lower bound** on the real cost, and any framework benefit is an **upper bound** on
the real benefit. Report it as a bracket, not a measurement — and note the miscalibration is
non-monotonic (over-estimating on moderate tasks, under-estimating on hard ones), so it cannot
be corrected with a single scaling factor.

**3. Correction to what I said earlier in the session.** I reported that this paper documents
simulated users "leaking information unnecessarily." **I cannot find that claim in the paper**
— it came from an extraction summary, not the text. What it actually documents is heightened
**question-asking** and **politeness**, more precise instruction-following, and a shifted error
profile. The over-cooperation direction holds; the information-leakage specific does not, and
the note is the record.

**4. A fairness dimension our experiments ignore entirely.** Agent success varies 11 points by
dialect and up to 19 points by dialect within an age band. Our arms are driven by an
orchestrator writing in one register; whatever we measure about attention cost is measured for
that register only. Worth stating as a limitation rather than discovering later.

## Limits

- Preprint, not peer-reviewed.
- English only; age analysis is US-only; one domain (τ-Bench retail customer service); one
  fixed agent (GPT-4o), so calibration gaps across *agents* are unmeasured — the authors flag
  all four.
- Difficulty levels are defined by GPT-4o-vs-GPT-4o success rates, which is a model-relative
  notion of difficulty.
- It critiques simulation as a *stand-alone* paradigm; it does not claim simulation is useless,
  and its recommendations (multiple user models, validate against human data where possible,
  disclose limits) are the constructive path we should follow.
