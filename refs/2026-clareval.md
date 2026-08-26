---
key: 2026-clareval
title: "ClarEval: A Benchmark for Evaluating Clarification Skills of Code Agents under Ambiguous Instructions"
authors: [Jialin Li, Yuan Wu, Yi Chang]
year: 2026
venue: arXiv preprint
peer_reviewed: false
arxiv: 2603.00187
citations: "3 (0 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2603.00187
kind: benchmark
read_depth: full
retrieved: 2026-07-31
pdf: refs/pdf/2026-clareval.pdf
task_shape: function-level
task_count: 2250
task_source: HumanEval (150) + LiveCodeBench (600) = 750 clear tasks × 3 ambiguity types
verifier: unit-tests
ambiguity_construction: removal-from-complete-spec
user_simulator: rule-based
metrics: [KQC, PIR, MPR, ATC, EAR]
contamination_posture: time-windowed
headroom: true
bears_on: [exp-02, exp-03, methodology-5d, metrics]
verdict: "the design to copy — ambiguity injection creates ~80pp of headroom where our trap set had none, and its rule-based user simulator is validated at 96.5% agreement against an LLM judge"
---

# ClarEval

`retrieved: 2026-07-31` · `read_depth: full` (body pp. 1–8 + appendices A–F, pp. 12–14;
pp. 10–11 are references) · [arXiv:2603.00187](https://arxiv.org/abs/2603.00187), v1 dated
27 Feb 2026

## What it does

Measures whether a code agent *asks* rather than guesses. Takes clear tasks, injects three
controlled ambiguity types, and scores the agent on how much of the withheld information it
recovers through dialogue and how efficiently. Calls the construct a "Collaborative Quotient."

**This is the design we should copy.** It is the same shape I sketched independently — author
the complete spec, delete from it, answer only what's asked — but already built, validated, and
with a metric suite.

## Design

**Ambiguity injection** (§3.1–3.2), formally `T̃ᵢ = F(Tᵢ, A)` for `A ∈ {A_G, A_P, A_T}`:

| Type | Construction |
|---|---|
| **Missing Goal** (`A_G`) | description = context ⊕ goal; keep only the context |
| **Missing Premises** (`A_P`) | `REMOVE(Dᵢ, P)` — delete textual references to critical constraints |
| **Ambiguous Terminology** (`A_T`) | `REPLACE(Dᵢ, t, t̃)` — swap a precise term for a vague one ("sort" → "organize") |

GPT-4o performs the transformation, then humans verify (§3.2, §3.4).

**Source data** (§3.1): 750 clear tasks — **150 HumanEval + 600 LiveCodeBench** — × 3 types =
**2,250 instances**. LiveCodeBench is included explicitly to make the benchmark
"contamination-aware."

**User simulator** (§3.3.2, Appendix C) — the transferable part. A deterministic, rule-based
**conditional lookup table** per task, `Sᵢ = {(I_trigger, R_content)}`, derived from
human-annotated ground truth: `I_trigger` is the intent asked about ("Input Format", "Edge
Case"), `R_content` the pre-defined answer restored from ground truth. Worked example from
Appendix C: `A_P` removed "the list must be sorted descending" → script holds
*if agent asks about order → reply "Sort it descending."* No model in the loop.

**Human verification** (§3.4): two-stage review by three senior engineers on ambiguity
validity, plausibility, script alignment. **Fleiss' κ = 0.82**; ~12% of generated samples
discarded or rewritten.

**Ecological validity check** (§3.4) — worth stealing: 50 ClarEval instances vs real
StackOverflow queries, two experts blind-rated "naturalness" 1–5. ClarEval **4.12 ± 0.6** vs
real **4.25 ± 0.8**, p > 0.05 — statistically indistinguishable. That is how you defend a
synthetic instrument.

Setup: 11 agents, temperature 0.1, 512-token output cap, unified system instruction
encouraging proactive clarification (Appendix A).

## Numbers worth keeping

**The headroom result (§5.1, Figure 3) — the one that matters for issue #4.** GPT-4o Pass@1:

| Condition | Pass@1 |
|---|---|
| Clarified (oracle-guided) upper bound | **89.02%** |
| Ambiguous baseline, overall | **8.94%** |
| by type: Ambiguous Terminology | 6.71% |
| by type: Missing Goal | 9.76% |
| by type: Missing Premises | 10.37% |

An ~80-percentage-point gap. Their phrasing: "Clarification is not merely an enhancement; it
is a prerequisite for correctness."

**Metric definitions** (§3.5, Appendix B):

- **KQC** = |C| / |K| — covered intents over expert-annotated required intents.
- **PIR** = |I| / |P| — missing premises identified in the *first* turn (zero-shot planning).
- **MPR** = |R| / |P| — premises actually resolved by the dialogue's end.
- **ATC** = (1/|R|) Σ Turn(pᵢ) — mean turn index of first resolution. Undefined when |R| = 0
  (NaN, excluded from averages) — a trap to remember if we implement it.
- **EAR** = (1/|P|) Σ_{p∈R} 1 / log₂(Turn(p)+1) — DCG-style. Turn 1 = 1.0, turn 2 ≈ 0.63,
  turn 3 = 0.5, unclarified = 0. Penalises both the "lazy agent" (low ATC, low MPR) and the
  "inefficient agent" (high MPR, high ATC).

Selected results (Table 2, Table 3): single-turn KQC best GPT5-Coder **0.867**
(Claude-Sonnet-4.5 0.852, Claude-Opus-4.1 0.847); multi-turn KQC best **Claude-Opus-4.1
0.754**; MPR best GPT5-Coder 0.951; ATC best GPT5-Coder **1.493**, worst Qwen2.5-Coder
**2.396**; EAR ranking led by GPT5-Coder 0.722 over Claude-Opus-4.1 0.605.

**Single-turn and multi-turn skill are nearly separate**: Pearson **r = 0.32** (p < 0.05).
Aider-GPT5 is 2nd on single-turn KQC (0.833) and 10th on multi-turn (0.376).

**Rule-based simulator robustness** (Appendix D) — the number that de-risks copying it:
200 sampled interaction turns, rule-based Hit/Miss labels vs a GPT-4o semantic judge →
**96.5% agreement**, **2.5% false negatives** (5/200, all highly metaphorical phrasings, e.g.
asking about "data hygiene" instead of "null values"). Their conclusion: the rule-based
approach is deterministic and cheap "without significantly penalizing the semantic flexibility
of SOTA models."

**Batching vs serial** (Appendix B.3): frontier models consolidate composite ambiguities into
one structured turn (low ATC); weaker ones fragment — ask about data type in turn 1, only
realising in turn 3 that sort order is also missing. ATC is therefore a proxy for
clarification *planning*, and fragmentation is a "cognitive tax" on the user.

## What it means for this repo

**1. It solves issue #4's headroom problem, and shows our instrument was the wrong kind.**
Our trap set gave the plain baseline 8/8 — no room to measure anything. Ambiguity injection
produces a ~10× spread (8.94% → 89.02%) on tasks *smaller* than tarpeek. Headroom comes from
withholding information, not from harder edge cases. This is the strongest argument for
rebuilding the instrument around ambiguity rather than escalating trap difficulty, and it is
evidence, not preference.

**2. It names what Run A did.** Appendix E's failure taxonomy calls it **Assumptive Generation
("Silent Failure")** — the agent ignores the ambiguity and generates on a high-probability
assumption. That is exactly our T4 finding: Run A pinned `tz=timezone.utc`, passed the trap,
and never mentioned timezones in its README. We observed the phenomenon; they have a name, a
taxonomy, and two sibling modes (**Generic Querying** — "anything else you need?" — and
**Hallucinated Constraints** — "I'll assume the data is sorted").

**3. Use its rule-based simulator, not an LLM one.** 96.5% agreement means the rigidity
objection is quantified and small, and it costs nothing to run, is fully replayable, and
cannot over-cooperate — see [`lost-in-simulation.md`](lost-in-simulation.md) for why that last
property matters.

**4. Metrics to adopt into our vocabulary**, recorded in
[`../docs/metrics.md`](../docs/metrics.md): KQC, MPR, ATC, EAR.
EAR in particular already solves a problem we would have hit — how to stop a framework looking
good by asking thirty questions.

**5. Caution for exp-02's P1.** Single- and multi-turn clarification correlate at r = 0.32.
A framework's *written* requirements quality (our P1) may say little about its *dialogue*
behaviour. Those are two instruments, not one.

## Limits

- Preprint, not peer-reviewed.
- **Function-level tasks** (HumanEval / LiveCodeBench), far below our task size, and the paper
  says so: it is a "unit test" for communicative intelligence in a controlled environment,
  deliberately free of repository context. Transfer to repo-scale work is unproven — that is
  what [`2026-ambig-swe.md`](2026-ambig-swe.md) is for.
- Ambiguity is injected by GPT-4o, so the instrument inherits one model's notion of vagueness,
  mitigated but not eliminated by human verification.
- Own stated limits (p. 9): no cross-cutting or composite ambiguities; and whether clarification
  skill predicts success in real development environments is untested.
- Evaluates models/agents, not workflow frameworks — the layer we care about is absent.
