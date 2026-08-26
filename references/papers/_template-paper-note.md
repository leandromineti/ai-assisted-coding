---
key: <citekey, shaped <year>-<name> (year = the year: field below) — MUST equal this file's name without .md; --check enforces it>
title: "<full title, quoted>"
authors: [<First Last>, <First Last>]   # first few is fine; add "et al." as a final entry
year: <YYYY>
venue: <"arXiv preprint" | "ICLR 2025" | "ACM TOSEM" | ...>
peer_reviewed: <true | false>   # a 2026 preprint is a lead, not a settled result
arxiv: <NNNN.NNNNN — omit if not on arXiv>
doi: <10.xxxx/yyyy — omit if none>
# citations: NEVER hand-typed — run `python3 scripts/fetch-citations.py --write`
# (Semantic Scholar, needs arxiv:). Context only: age-confounded, validity-independent.
citations: "<N (M influential) — Semantic Scholar>"
citations_at: <YYYY-MM-DD>
url: <canonical landing page, not the PDF>
kind: <benchmark | empirical-study | method | critique | survey>
# read_depth is the honesty field, and the one --check polices. Downgrade it freely;
# never upgrade it without actually doing the reading.
#   full     — read end to end
#   extract  — a tool answered questions against it; nobody read the whole thing
#   abstract — abstract only
#   unread   — recorded as a lead. NOTHING in this repo may cite it. --check fails if it does.
read_depth: <full | extract | abstract | unread>
retrieved: <YYYY-MM-DD the copy behind this note was fetched>
pdf: <references/papers/pdf/<key>.pdf if cached locally — gitignored, refetchable from arxiv/doi>
# bears_on: what in THIS repo the source touches. Free-form slugs, but prefer ones that
# grep: conclusion-N, exp-NN, methodology-Nx, taxonomy, a tool name. Empty = --check warns.
bears_on: [<conclusion-6>, <exp-03>]
# verdict: one line on what it does to OUR claims — supports / refines / contradicts /
# supersedes / unrelated-but-useful. This is the field the index shows; make it earn its row.
verdict: "<refines conclusion 6 — validation > grounding at n=128>"
---

# <Title>

`retrieved: <YYYY-MM-DD>` · `read_depth: <...>` · [<venue link>](<url>)

## What it does

<Two or three sentences. What question it asks and how it answers it — enough that a future
session knows whether to open the PDF.>

## Design

<Only what we might borrow or must not copy: task construction, verifier, user simulator,
metrics, sample sizes. Cite sections or pages — methodology rule 4 applies to papers exactly
as to source code: a claim without a locator is an opinion.>

## Numbers worth keeping

<Quantitative results we might cite later, each with its locator. Do NOT round or reformat
values from memory; copy them.>

## What it means for this repo

<The part that earns the note. Which conclusion, experiment, or methodology rule it
supports, refines, or threatens — and what we would have to change if it's right. If it
contradicts something we've published in `docs/conclusions.md`, say so plainly here and
open an issue; do not quietly leave both standing.>

## Limits

<Sample size, contamination posture, single-rater scoring, LLM-judge dependence, whether it
ran anything at all. The reasons NOT to lean on it.>
