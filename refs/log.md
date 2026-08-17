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
