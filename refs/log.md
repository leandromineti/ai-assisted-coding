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
