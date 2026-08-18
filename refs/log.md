# Ingest log

Append-only, newest last. One line per source ingested, prefixed `## [YYYY-MM-DD] ingest |`
so it greps. Conventions: [`README.md`](README.md).

## [2026-07-31] library created

Ten sources found in one afternoon while looking for prior art on simulating a human-in-the-loop
so that workflow frameworks could be compared fairly. Two of them bear on published conclusions
in this repo, which is what prompted building the library rather than filing a link dump.
Search paths that produced them, for reproducibility:

- "tau-bench simulated user pass^k reliability tool-agent benchmark"
- "benchmark clarifying questions ambiguous requirements code generation agent asks user"
- "evaluating spec-driven development frameworks agent scaffolding ablation spec-kit"

## [2026-07-31] ingest | Spec Kit Agents: Context-Grounded Agentic Workflows

`spec-kit-agents` · full read, 7pp. Closest prior art to exp-03: ablates discovery vs
validation hooks at n=128. Full read corrected two claims made from HTML extraction earlier the
same day — the blinded human preference favours the *un*augmented pipeline (Table 2), and the
agent under test was MiniMax-M2.5, not a Claude model (Table 7). Flags conclusion 6 for
re-examination.

## [2026-07-31] ingest | From Prompt to Process

`from-prompt-to-process` · full read, 15pp of 17. Six-dimension taxonomy over the same six
frameworks we study, docs-only and single-rater. Independently reaches conclusion 7's
depth-vs-portability tradeoff. Scores GSD 0 on validation, which our exp-01 run contradicts —
rule 8 earning its keep. Its research agenda names our attention-split instrument ("rate of
human review required") as a gap.

## [2026-07-31] ingest | ClarEval

`clareval` · full read, body + appendices A–F. The design to copy: ambiguity injection by
removal from complete specs, three types (missing goal / missing premises / ambiguous
terminology), a *rule-based* user simulator validated at 96.5% agreement against an LLM judge,
and a metric suite (KQC, PIR, MPR, ATC, EAR). Its headroom result — GPT-4o Pass@1 8.94%
ambiguous vs 89.02% clarified — is direct evidence that withholding information produces the
discrimination our trap set lacked. Also names Run A's T4 behaviour: "Assumptive Generation
(silent failure)".

## [2026-07-31] ingest | Ambig-SWE

`ambig-swe` · full read, body pp. 1–9. **ICLR 2026, peer-reviewed** — the best-credentialed
source in the batch. Repo-scale (SWE-Bench Verified, 500 issues) confirmation that withholding
information creates headroom (Claude Sonnet 4: 40.0 Hidden vs 68.0 Full). Two things it changes
for us: agents "almost never interact unless explicitly prompted", which confounds Run A's 0s
attention reading; and its causal-identification argument for why the complete spec must exist
before you delete from it.

## [2026-07-31] ingest | Lost in Simulation

`lost-in-simulation` · full read, body pp. 1–9. Real human user study (US/India/Kenya/Nigeria)
against τ-Bench retail. Swapping only the *user* LLM moves measured agent success by ~9pp
(Sonnet 3.7 67.0 vs Sonnet 4.5 75.9) — the apparatus becomes a free variable. Simulated users
ask ~2× as many questions as humans and are far more polite; failure attribution shifts from
user (62.2% human) to agent (48.9% simulated). Corrects an "information leakage" claim I made
earlier from an extraction summary — that claim is not in the paper.

## 2026-08-17 — instrument-saturation sweep for issue #4 (exp-02 trap redesign)

Four sources ingested (1 extract, 3 abstract) answering "how does the community fix a
saturated instrument": aider-polyglot-2024 (select items by baseline failure — kept
problems solved by ≤3/7 baselines; saturation symptoms match exp-02's verbatim),
swebench-verified-2024 (screen for *unfair* items too — 61.1% of SWE-bench's tests
rejected valid solutions; headroom and validity are separate screens),
evalplus-2023 (densify tests on existing tasks before authoring new ones — the cheap
first move), paperbench-2025 (partial credit done as weighted binary criteria, not
holistic judgment — dissolves the option-1-vs-2 dichotomy). Synthesis and
recommendation posted to issue #4; no protocol amendment yet — that happens at
decision time, per preregistration discipline.

## 2026-08-17 — the three unread clarification stubs promoted to extract (issue #6)

tau2-bench: dual-control τ successor; the apparatus finding transfers — constraining
the user simulator through environment affordances cut simulator error from 40–47%
(retail/airline) to 16% (telecom), the fix for the free-variable problem our τ-bench
note measured at ~9pp. No-user ablation isolates coordination cost (+18/+25pp).
humanevalcomm: 762 degraded HumanEval variants; >60% of code-LLM responses answer
broken specs with code rather than questions; pass@1 drops 35–52%. Caveat: the
question-answering proxy sees the original problem — the leaky-oracle shape.
clarifycodebench: 419 LiveCodeBench-v6 tasks, ten ambiguity categories, annotated key
questions with ground-truth answers + default-reply fallback (the clean oracle
template); best TKQR 0.30; reasoning effort buys code correctness but not ambiguity
detection — clarification dissociates from codegen capability, which is exp-02's P1/P2
dissociation stated as a field result.

## 2026-08-17 — three mainstream ingests for the benchmark survey (abstract depth)

swe-bench-2023: 2,294 GitHub-issue tasks, 12 Python repos; Claude 2 resolved 1.96% at
launch — biggest headroom in the field, and still needed Verified to remove the 68.3%
invalid items later. Headroom, validity, contamination: three independent properties.
terminal-bench-2026: our rig's closest relative — end-state pytest verification in
per-task Docker, canary GUIDs; v2.1's "verified refresh" (a dozen instruction-test
mismatches fixed) is the validity-arrives-late pattern's third instance.
livecodebench-2024: the canonical time-windowed contamination posture — release-dated
problems make contamination measurable (pre- vs post-cutoff gap), not just deterred.
agent-frameworks-eval: FULL READ 2026-08-17 (PDF refetched — the 07-31 cache died with
the 08-06 server rebuild). 7 frameworks × 3 tasks, one LLM, $875 of runs — and no
framework-less control anywhere: exp-03's question confirmed unoccupied. Single-agent
beat multi-agent on all three tasks; repair gaps traced to patch *tooling*, not
reasoning. Correction-rate metric borrowed into metrics.md with its zero≠good caveat.
Prose headlines contradict its own tables three ways (trajectories, vuln percentages);
tables are the citable layer — the read-the-PDF rule pays out again, this time inside
one paper.
swe-agent-2024: FULL READ 2026-08-17 (owner-directed ingest after it surfaced as the
ACI origin inside agent-frameworks-eval). The layer-2 premise, peer-reviewed with
numbers: interface alone is +64% relative over a bare shell, same model. Ablation
table folded into design-principles H3 (earliest measured two-chokepoint evidence);
linter guardrail (+3.0pp) folded into the cross-cutting gate vocabulary as the format
quadrant's priced instance. Sharpest single result: a badly shaped tool (iterative
search) scores BELOW no tool — a ✓ in a feature matrix can be negative.

## 2026-08-18 — memory-benchmark instrument catalog (issue #18 close-out)

Three full reads, all `kind: benchmark`, cataloging the instruments the memory-kind
vendors self-report on before any vendor number is repeated (benchmark-survey
discipline):

- **[2024-locomo](2024-locomo.md)** — the instrument mem0's headline numbers ride on.
  Persona-driven social-chat memory, 50 LLM-generated conversations, F1 scoring.
  Saturation by 2026 models plausible; discriminance unverified.
- **[2025-longmemeval](2025-longmemeval.md)** — the strongest of the three: human-curated
  questions, judge meta-evaluated at 97% human agreement, retrieval recall observable.
  Its indexing/retrieval/reading control points map 1:1 onto what ai-memory and memos
  ship — folded into both tool reports' framing.
- **[2026-beam](2026-beam.md)** — behind cognee's 0.79/0.67 claims; fully synthetic up to
  10M tokens, nugget-scored LLM judge; the paper's own best configs average ~0.36 at
  100K, so the vendor number needs config reconciliation before belief.

Cross-cutting finding recorded in all three notes: every instrument measures personal
chat-assistant memory — **no coding-agent memory benchmark exists** (no tool traces, no
repo state, no code entities). The kind's vendors benchmark on conversation and sell to
coding harnesses.

Same day: library renamed to year-first citekeys (`<year>-<name>.md`), all 21 notes +
pdf/ copies + repo-wide links; `key:` fields updated in place. Convention noted in
README.md. Generated index/benchmarks rebuilt.
