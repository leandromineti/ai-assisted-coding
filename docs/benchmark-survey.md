# Benchmarks as instruments — a survey

`checked: 2026-08-18`

This is the narrative half of the repo's benchmark review; the catalog half is the
generated matrix ([`../../comparisons/benchmarks.md`](../comparisons/benchmarks.md)),
which stays the evidence base for every row-level fact here. Scope: benchmarks as
**instruments for this repo's questions** — can they isolate the variables the taxonomy
names, can they discriminate, can they be trusted — not a leaderboard guide. Every
benchmark named below has a refs note at `abstract` depth or better; per-claim locators
live in those notes.

The survey's thesis, up front: **a benchmark is a measurement instrument, and the field
systematically ships instruments with at most one of the three properties an instrument
needs — headroom, validity, and contamination control — then retrofits the others after
scores mislead someone.** This repo's own exp-02 walked the same path, which is why the
lessons below are load-bearing rather than decorative.

## 1. The confound nobody isolates

The repo's headline benchmark finding (README conclusion 2) is that **no public
benchmark isolates model from harness** — every leaderboard entry is a model+scaffold
pair. [SWE-bench](../references/papers/2023-swe-bench.md) resolve rates are scaffold-dependent;
[Terminal-Bench](../references/papers/2026-terminal-bench.md) leaderboard rows name harnesses
(codex's report cites "leads Terminal-Bench 2.1" — with its own caveat that the
benchmark can't separate the harness from the vendor's model); and the one benchmark
this repo found that *tried* to fix the harness turned out to inherit that harness's
per-model prompt dispatch (conclusion 2's origin, and the repo's first upstream
contribution).

The taxonomy's maker-span section upgrades this from measurement nuisance to structural
fact: for spanned vendors the model and harness are **co-designed**, so the confound is
not an artifact of lazy benchmark design — it is a property of the thing being measured.
Any instrument claiming to compare fundamentals must pin two of the triad
(model/harness/environment) to vary the third; a leaderboard that pins none is measuring
bundles, which is fine only as long as it says so.

## 2. The saturation lifecycle

Coding benchmarks follow one lifecycle, documented across a decade of instances:

1. **Launch with headroom** — [SWE-bench](../references/papers/2023-swe-bench.md) opened with the
   best model resolving 1.96%.
2. **Scores climb; the ceiling arrives.** HumanEval reached the high-90s and stopped
   informing (recorded via [EvalPlus](../references/papers/2023-evalplus.md), whose premise is
   that "passing" HumanEval had stopped meaning correct).
   [Aider's original benchmark](../references/papers/2024-aider-polyglot.md) showed the diagnostic
   symptoms this repo now knows firsthand: top score ~84%, new champions winning by 1–2
   items, models two generations old clearing half the set.
3. **The instrument gets rebuilt or retired.** Three rebuild strategies exist:
   - **Densify the verifier** ([EvalPlus](../references/papers/2023-evalplus.md)): keep the tasks,
     multiply the tests (~80×) until previously-passing solutions fail. Cheapest;
     buys time, not immunity — the densified sets approached saturation within two
     model generations.
   - **Select items by baseline failure** ([Aider
     polyglot](../references/papers/2024-aider-polyglot.md)): run K baselines over a large
     candidate pool, keep only items most baselines fail (Aider: solved by ≤3 of 7,
     from 697 candidates to 225). Headroom by construction — the scale recalibrated
     from an 84% ceiling to a 62% top score.
   - **Retire and replace.** Nobody keeps reporting a saturated number as informative.

The psychometrics framing (standard item-response theory, no citation needed) makes the
failure precise: an item has a difficulty *and* a discrimination, and an item every
baseline passes has **zero discrimination regardless of its difficulty-by-design** — it
contributes nothing to separating the systems under test. exp-02's trap set is this
repo's live instance: proven fails-closed twice and still saturated on first contact
(methodology rule 5d is the scar), with the redesign now preregistered in
[amendment 3's territory](../experiments/02-spec-kit-vs-plain/README.md).

## 3. Validity is a separate property from difficulty

The lifecycle above is about headroom. A different failure arrives independently:
**items that no correct solution can pass.**
[SWE-bench Verified](../references/papers/2024-swebench-verified.md) is the canonical audit —
93 annotators found 38.3% of sampled items underspecified and **61.1% with tests that
could reject valid solutions**; 68.3% of the benchmark was discarded. The pattern
repeats at smaller scale: [Terminal-Bench](../references/papers/2026-terminal-bench.md) 2.1 is a
"verified refresh" of 2.0 that fixed instruction–test mismatches across roughly a dozen
tasks. Validity screening arrives *late*, after scores misled — three instances now,
counting exp-02's own vacuous-pass catch (a do-nothing stub was trivially
"timezone-invariant"; the fails-closed proof caught it, 2026-07-28).

**Contamination is the third independent property.** The matrix names three postures,
in increasing strength: `none` (public tasks, hope), `canary`
([Terminal-Bench](../references/papers/2026-terminal-bench.md)'s searchable GUID convention —
detection, not prevention; this repo's own rig verifier carries one), and
`time-windowed` ([LiveCodeBench](../references/papers/2024-livecodebench.md): problems stamped
with release dates, so contamination becomes *measurable* as a pre-/post-cutoff score
gap). Contamination and saturation compound: a contaminated task saturates faster
because both arms partly recall the answer — which is why the matrix's two scar columns
are exactly `headroom` and `contamination`.

The synthesis this repo now applies (exp-02 amendment 3): an instrument is acceptable
only with a **three-point proof** — a do-nothing stub fails everything (fails-closed), a
hardened reference passes everything (validity/fairness), and the calibration baseline
fails enough items to measure with (headroom). No community benchmark ran all three
before launch; that is the field's actual lesson, learned here the same way.

## 4. Scoring shapes

Binary pass/fail is the floor, and three refinements matter:

- **Reliability exponents**: [τ-bench](../references/papers/2024-tau-bench.md)'s `pass^k` (all of k
  runs succeed) prices flakiness that pass@1 hides — carried forward by
  [τ²-bench](../references/papers/2025-tau2-bench.md) (4 runs per task).
- **Analytic partial credit**: [PaperBench](../references/papers/2025-paperbench.md) decomposes
  each task into thousands of individually gradable weighted binary criteria. This is
  the honest form of "graded rubric" — many small checks summed, not one holistic
  judgment — and it dissolves the false choice between machine-checked binary scoring
  and partial credit (exp-02's option-1-vs-option-2 debate ended exactly there).
- **Judge dependence is a cost, not a detail**: PaperBench's leaves are LLM-judged;
  [HumanEvalComm](../references/papers/2024-humanevalcomm.md)'s Good Question Rate is GPT-3.5-rated;
  and this repo's issue #8 exists because a published n=128 result's LLM-judge headline
  is mildly contradicted by its own blinded human sample. Where a leaf *can* be
  machine-checked, it should be; judges belong at the margin.

**The apparatus is part of the instrument.** [τ-bench](../references/papers/2024-tau-bench.md)'s user
simulator moves measured agent success by ~9pp when only the simulator's LLM changes;
[τ²-bench](../references/papers/2025-tau2-bench.md) measured simulator error at 40–47% in its inherited
domains and cut it to 16% by constraining the simulator to environment affordances.
[HumanEvalComm](../references/papers/2024-humanevalcomm.md)'s question-answering proxy *sees the
original problem* — a leaky oracle; [ClarifyCodeBench](../references/papers/2026-clarifycodebench.md)'s
matched-key-question + default-reply oracle is the clean template. A benchmark's
simulated human deserves the same fails-closed scrutiny as its verifier.

## 5. The ambiguity corner (what exp-03 has to work with)

The clarification benchmarks are this repo's deepest-read cluster, because exp-03's
question (does a framework's clarify machinery buy anything?) lives there:

| Benchmark | Construction | The result that matters here |
|---|---|---|
| [HumanEvalComm](../references/papers/2024-humanevalcomm.md) | 762 degraded HumanEval variants (3 defect types, singly/pairwise) | >60% of responses answer broken specs with code, not questions; pass@1 drops 35–52% |
| [ClarEval](../references/papers/2026-clareval.md) | 750 clear tasks × 3 ambiguity types | (read at full depth — see note) |
| [Ambig-SWE](../references/papers/2026-ambig-swe.md) | SWE-bench Verified issues, underspecified variants | (read at full depth — see note) |
| [ClarifyCodeBench](../references/papers/2026-clarifycodebench.md) | 419 LiveCodeBench-v6 tasks, 10 ambiguity categories, annotated key questions | best model asks <⅓ of key questions (TKQR 0.30); **reasoning effort buys code correctness but not ambiguity detection** |
| [τ²-bench](../references/papers/2025-tau2-bench.md) | dual-control dialogue | removing the user *raises* scores 18–25pp — coordination cost isolated |

Two field-scale priors fall out for exp-02/03: the **don't-ask default is real and
large** (unaided models code through broken specs), and **clarification dissociates from
code capability** (ClarifyCodeBench's reasoning-effort finding) — which is spec-kit's
bet restated as a measurable claim, and exactly the P1/P2 dissociation exp-02
preregistered. *(Closed 2026-08-18: exp-03 ran and the arc it belonged to closed with it —
the don't-ask default held (zero clarifying questions in 20 runs, fixed oracle never
exercised), and the discoverable-ambiguity variant of withholding proved tier-fragile:
plain Sonnet resolved it unprompted. Category-4 code-outcome A/Bs stop per issue #17;
this section stays as the map of the instruments' literature.)* The adjacent framework-comparison literature
([agent-frameworks-eval](../references/papers/2025-agent-frameworks-eval.md), **full read
2026-08-17**) compares frameworks *to each other* on success/efficiency/token-overhead
— 7 frameworks × 3 tasks, one backend LLM, and **no framework-less control anywhere in
the grid** — so the framework-vs-*plain* question this repo's experiments ask remains
unoccupied, now confirmed at full depth rather than assumed from the abstract. The
full read also surfaced two things the abstract hides: single-agent beats multi-agent
on all three of its tasks (coordination overhead + patch-tooling gaps, corroborating
the ceremony-is-cost decomposition at framework scale), and its correction-rate
metric is usable here only jointly with effectiveness — zero corrections in its data
signals missing self-monitoring, not efficiency (GPTswarm/OWL: ~0 corrections *and*
3–10% repair rates). Its prose headlines contradict its own tables in places; cite
tables only.

## 6. The memory corner (what category 5 — Memory — reports against)

*(Added 2026-08-18, closing the memory-type reading arc's instrument question — three
full reads the same day.)* The instruments the memory vendors self-report on:

| Benchmark | Construction | The result that matters here |
|---|---|---|
| [LoCoMo](../references/papers/2024-locomo.md) | 50 LLM-generated persona dialogues (~9K tokens, ≤35 sessions), human-patched; F1 scoring | human 87.9 vs best model 32.4; long context *collapses* adversarial answerability (2.1 F1); observation-granularity RAG beats sessions and summaries |
| [LongMemEval](../references/papers/2025-longmemeval.md) | 500 human-curated questions in scalable simulated histories (115K / 1.5M tokens); judge meta-evaluated at 97% human agreement | commercial memory systems drop 37–64% vs offline reading; even with *oracle* retrieval, reading strategy costs up to 10 points |
| [BEAM](../references/papers/2026-beam.md) | 100 fully synthetic conversations, 100K–10M tokens; nugget-scored LLM judge | best configs average ~0.36 at 100K — huge headroom; weakest ability everywhere is contradiction resolution |

Three take-aways, each recorded in the refs notes:

1. **No coding-agent memory benchmark exists.** All three measure personal
   chat-assistant memory — no tool traces, no repo state, no code entities. The type's
   vendors benchmark on conversation and sell to coding harnesses; every transfer claim
   is unmeasured.
2. **Vendor numbers exceed the instruments' own scales.** mem0's "LoCoMo 92.5" is above
   the paper's measured *human* baseline (87.9); cognee's BEAM 0.79 is ~2× the paper's
   best configurations. Neither is comparable to the published metric without config
   reconciliation — flagged in both tool notes. *(mem0's side resolved 2026-08-18 by
   reading the vendor paper, [2025-mem0](../references/papers/2025-mem0.md): the metric is
   LLM-judge on LoCoMo-minus-adversarial, the paper's own best J is 68.44 — still far
   below the README's 92.5 — and the paper's no-memory full-context baseline scores
   J 72.90, beating the memory system on quality. The measured claim is efficiency,
   not accuracy. Deepened at the 2026-08-19 deep-dive: the 92.5 is one of TWO
   number-sets coexisting at the same pin (README 92.5/94.4 vs migration docs
   91.6/93.4, same baseline, unreconciled), the eval harness was extracted to a
   sibling repo two months pre-pin, and the numbers are explicitly disclaimed as
   platform-only — unreproducible from the OSS tree at any pin. It also documents that released LoCoMo = 10 conversations, not the
   paper's 50 — "on LoCoMo" scores may not even share an item set.)*
3. **The instruments converge on the mechanisms the vendors ship.** LongMemEval's
   indexing/retrieval/reading control points and BEAM's episodic/working/scratchpad
   decomposition map onto ai-memory's tiers-and-slots and memos' trace categories almost
   term for term — academia and vendors building the same three memories under
   different names (rule-4 trace in each ref note's "what it means" section).

## 7. What this repo takes

1. **The three-point instrument proof** (§3) — now the preregistered acceptance
   criterion for exp-02's rebuilt trap set, and the default for any future instrument
   here.
2. **Select-by-baseline-failure** as the escalation when densification fails — with
   thresholds preregistered before need (amendment 3).
3. **Analytic binary scoring** — many small machine-checked criteria, judges only where
   machine checks can't reach (and then flagged, per issue #8's caution).
4. **Contamination posture as a declared field**, not an afterthought — the rig's canary
   line, the fixtures' determinism, and the recognition that exp-02's contamination
   surface is the *orchestrator's knowledge*, a threat model none of the public postures
   addresses (the mitigation is preregistration plus fresh-context arms, declared in the
   protocol).
5. **Apparatus scrutiny** — any simulated human (exp-03's oracle) gets the
   affordance-constrained design (τ², ClarifyCodeBench), never the sees-the-answer proxy.
6. **Known-groups validation** (added 2026-08-17, after running it): before trusting an
   instrument's discrimination claims, run a group it *should* separate and check that it
   does. Executed for exp-02's settled 21-check instrument with 5 `claude-haiku-4-5`
   baselines against the 5 Sonnet 5 screening baselines: complete separation (Haiku
   completed runs all 17/21; Sonnet 18–20/21; plus one Haiku completion failure from an
   undeclared runtime dependency). Two lessons with reach beyond this task:
   **saturated-within-tier is not saturated-across-tiers** — the same instrument that
   couldn't rank Sonnet baselines cleanly ranks tiers; and **trap items are not monotone
   in capability** — Haiku *beat* Sonnet on the truncated-archive item because its coarse
   blanket error handling never lets a traceback escape, while failing everything that
   requires distinguishing failures. Family-level failure patterns (Haiku: the whole
   ambient-config family, every completed run), not single items, are what separate
   tiers. Full tables: `experiments/02-spec-kit-vs-plain/log.md` § Model-tier
   calibration verdict.

The measurement vocabulary these map onto lives in [`metrics.md`](metrics.md); the
per-benchmark facts live in the [matrix](../comparisons/benchmarks.md) and its refs
notes, each with its own honesty grade.
