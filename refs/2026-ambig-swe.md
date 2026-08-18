---
key: 2026-ambig-swe
title: "Ambig-SWE: Interactive Agents to Overcome Underspecificity in Software Engineering"
authors: [Sanidhya Vijayvargiya, Xuhui Zhou, Akhila Yerukola, Maarten Sap, Graham Neubig]
year: 2026
venue: ICLR 2026
peer_reviewed: true
arxiv: 2502.13069
citations: "27 (3 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2502.13069
kind: benchmark
read_depth: full
retrieved: 2026-07-31
pdf: refs/pdf/2026-ambig-swe.pdf
task_shape: repo-issue
task_count: 500
task_source: SWE-Bench Verified, underspecified variants via GPT-4o
verifier: hidden-tests
ambiguity_construction: removal-from-complete-spec
user_simulator: llm
metrics: [resolve-rate, detection-accuracy, FPR, FNR, cosine-information-gain, questions-per-task]
contamination_posture: none
headroom: true
bears_on: [exp-02, exp-03, conclusion-6, methodology-5d, metrics]
verdict: "peer-reviewed, repo-scale, and it identifies a confound in exp-02: agents almost never interact unless explicitly prompted, so 'plain asked nothing' is not evidence about plain"
---

# Ambig-SWE

`retrieved: 2026-07-31` · `read_depth: full` (body pp. 1–9 of 22; remainder is appendices and
references) · [arXiv:2502.13069](https://arxiv.org/abs/2502.13069) v3, 21 Feb 2026 ·
**Accepted at ICLR 2026**

The only peer-reviewed source in this batch, and the closest to our task scale. Weight it
accordingly.

## What it does

Takes SWE-Bench Verified's 500 fully-specified issues, generates *underspecified* variants,
and measures three separable capacities: (i) **detecting** that information is missing,
(ii) **acquiring** it by asking, (iii) **using** what comes back. Three settings isolate each.

## Design

**Three settings** (§2.3):

| Setting | Agent sees | Interaction |
|---|---|---|
| **Full** | the original detailed issue | disabled |
| **Hidden** | a summarised (underspecified) issue | disabled |
| **Interaction** | the summarised issue | enabled; the proxy holds the *full* issue |

**Underspecification is synthetic and that is deliberate** (§2.1). GPT-4o rewrites each issue
to preserve terminology but strip detail. They compared their variants against *naturally*
underspecified SWE-bench issues and found real ones retain more concrete technical detail
(snippets, error messages, file/line refs), reproduction info, external links, and
conversational fragments; theirs remove information more aggressively.

They then state the reason they don't just use naturally-vague issues, and it is the cleanest
justification I've seen for spec-first construction:

> naturally underspecified SWE-Bench examples "lack the paired ground truth (complete
> specifications) necessary for causal measurement of interaction impact. Without verified
> correct specifications, we cannot determine whether performance improvements result from
> resolving genuine underspecification versus other confounding factors."

**User proxy** (§2.2): GPT-4o holding the full issue, answering **only** from information
explicitly present in it — "preserving the original knowledge boundaries of the issue
reporter" — and replying *"I don't have that information"* when a queried detail is absent.
It also knows the file locations needing modification. Note this is an **LLM** proxy, unlike
ClarEval's rule-based script; see the tension section below.

Agent framework: **OpenHands**. Turn cap 30, raised to 100 for Claude Sonnet 4 and Qwen 3
Coder. Models: Claude Sonnet 4, Claude Sonnet 3.5, Claude Haiku 3.5, Llama 3.1 70B-Instruct,
Deepseek-v2, Qwen 3 Coder 480B.

## Numbers worth keeping

**Resolve rates, % (Figure 3)** — Hidden / Interaction / Full:

| Model | Hidden | Interaction | Full |
|---|---|---|---|
| Llama 3.1 70B | 3.20 | 4.80 | 8.80 |
| Deepseek-v2 | 5.60 | 7.20 | 12.20 |
| Claude Haiku 3.5 | 15.40 | 26.80 | 33.80 |
| Claude Sonnet 3.5 | 24.20 | 39.60 | 49.40 |
| Qwen 3 Coder | 45.60 | 53.80 | 64.60 |
| Claude Sonnet 4 | 40.00 | 61.40 | 68.00 |

Hidden→Interaction is significant for **every** model, and so is Interaction→Full — interaction
recovers a lot and still leaves a gap. The abstract's "up to 74%" improvement is Haiku 3.5's
relative gain (15.4→26.8). Recovery of Full-setting performance: Sonnet 3.5 and Haiku 3.5 up to
80%, Claude Sonnet 4 89%, Deepseek 59%, Llama 54% (§3.2).

**Interaction improves effectiveness but not efficiency** (§3.2): Qwen 3 Coder takes ~65 action
steps in both Hidden and Interaction; Claude Sonnet 4 *rises* from 65 to 75 steps when
interaction is enabled.

**Detection under three prompt levels (Table 2)** — Neutral / Moderate / Strong encouragement,
accuracy (FPR ↓, FNR ↓):

| Model | Neutral | Moderate | Strong |
|---|---|---|---|
| Claude Sonnet 4 | 0.74 (.08/.44) | 0.74 (.10/.42) | **0.89 (.03/.18)** |
| Claude Sonnet 3.5 | 0.60 | **0.84** | 0.76 |
| Claude Haiku 3.5 | 0.54 | 0.57 | 0.63 |
| Deepseek-v2 | **0.69** | 0.57 | 0.51 |
| Llama 3.1 70B | 0.48 (FPR .46) | 0.47 (FPR .95) | 0.52 (FPR .93) |
| Qwen 3 Coder | 0.50 | 0.50 | 0.50 — **FNR 1.00 throughout** |

> "Without explicit prompting, models almost never interact, even for severely underspecified
> inputs." Only the two Sonnets reach notable accuracy at distinguishing specified from
> underspecified (89% and 84%). Qwen 3 Coder never interacts under any prompt. Deepseek gets
> *worse* with stronger encouragement; Llama interacts arbitrarily (FPR .93–.95).

**Question quality (§5)**: information gain by cosine distance (`text-embedding-3-small`)
between the summarised task and post-interaction knowledge, plus a GPT-4o 1–5 judge.
Claude Sonnet 4 matches Qwen 3 Coder's information gain (0.171 vs 0.179) with **50% fewer
questions** (4.03 vs 6.02) via an **exploration-first** strategy — explore the codebase, then
ask only what cannot be discovered. Llama asks too few and too vaguely (2.61 avg, *"Are there
any existing workarounds?"*). Deepseek asks implementation questions that exceed what a user
could know; Claude targets behaviour and failure modes, "better matching realistic user
knowledge." Qwen's resolve rate *worsens* when given file locations — it re-explores anyway,
wasting turns (Table 1, §3.3).

## What it means for this repo

**1. It identifies a confound in exp-02, and this is the most important thing in the note.**
Run A asked **zero** questions, which I recorded as 0s attention-required and treated as the
plain arm's baseline behaviour. This paper shows that agents "almost never interact" unless
*explicitly prompted to*, and that detection accuracy swings from 0.74 to 0.89 on Claude
Sonnet 4 purely by changing how hard the prompt encourages asking. So Run A's silence is
mostly evidence about **our prompt**, not about the plain arm's judgment — and comparing it to
a framework arm whose pipeline explicitly instructs clarification is comparing a prompted
condition to an unprompted one.

Fix, borrowed from Table 2: make **encouragement level an explicit controlled variable**
(neutral / moderate / strong) held identical across arms, and report it. That is a
methodology-8a-shaped problem — a property we assumed was measured when it was actually
configured.

**2. Repo-scale headroom, with numbers.** Hidden vs Full is 40.00 vs 68.00 for Claude Sonnet 4
— a 28-point gap on real repository issues, not toy functions. Combined with
[`clareval.md`](clareval.md)'s ~80-point gap on function-level tasks, withholding information
reliably produces headroom at *both* scales. Our trap set produced none.

**3. The causal-identification argument justifies spec-first construction.** Their reason for
not using naturally-vague issues — no paired ground truth, so no causal attribution — is the
argument for authoring the complete spec and deleting from it. It also warns against a
tempting shortcut: harvesting real vague issues would be cheaper and would not support the
claim we want to make.

**4. Exploration-first is a finding about frameworks, not just models.** Claude Sonnet 4 gets
equal information from half as many questions by exploring before asking. A workflow framework
that front-loads a clarify phase *before* the agent has looked at the codebase may therefore
score worse on attention cost than one that lets it explore first — a concrete, testable
prediction for exp-02's spec-kit arm, whose `/clarify` runs early by design.

**5. Interaction buys effectiveness, not efficiency.** Step counts don't fall and sometimes
rise. If we price attention *and* wall-clock, expect them to move in opposite directions.

## Limits

- Underspecification is synthetic and admittedly more aggressive than real issues; the paper
  documents the distributional difference rather than hiding it.
- The user proxy is **GPT-4o**, so it inherits the LLM-simulated-user risks quantified in
  [`lost-in-simulation.md`](lost-in-simulation.md) — over-cooperation and information leakage.
  Their conservative design ("only information explicitly present", *"I don't have that
  information"*) mitigates but does not eliminate this, and they do not validate the proxy
  against a rule-based baseline the way ClarEval does (96.5% agreement).
- **No contamination defence**: SWE-Bench Verified is heavily represented in training data,
  which compresses differences between arms — the failure mode that produced our own ceiling.
- Claude Sonnet 4's Hidden setting was run on a 100/500 subset for cost, not the full set.
- Models are one generation behind current (Sonnet 4 / 3.5 era); the "models rarely ask"
  finding may weaken on newer models, and is worth re-testing rather than assumed.
- Evaluates models, not workflow frameworks.
