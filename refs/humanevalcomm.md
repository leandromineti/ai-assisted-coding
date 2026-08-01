---
key: humanevalcomm
title: "HumanEvalComm: Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agents"
authors: [Jie JW Wu, Fatemeh H Fard]
year: 2024
venue: ACM TOSEM 34(7)
peer_reviewed: true
arxiv: 2406.00215
url: https://arxiv.org/abs/2406.00215
kind: benchmark
read_depth: unread
retrieved: 2026-07-31
pdf: refs/pdf/humanevalcomm.pdf
bears_on: [exp-02, metrics]
verdict: "UNREAD — queued lead, must not be cited until read"
---

# HumanEvalComm: Benchmarking the Communication Competence of Code Generation for LLMs and LLM Agents

`retrieved: 2026-07-31` · `read_depth: **unread**` · [arXiv:2406.00215](https://arxiv.org/abs/2406.00215)

> **Nothing below is verified.** The PDF is cached at `refs/pdf/humanevalcomm.pdf` and has **not** been
> read. The lines under "Why it's queued" come from the abstract and search-result summaries
> only, which is exactly the provenance this library exists to keep separate from evidence.
> `scripts/build-refs-index.py --check` fails if this key is cited anywhere outside `refs/`.
> To promote it: read the PDF, rewrite this note from
> [`_template-ref-note.md`](_template-ref-note.md), and set an honest `read_depth`.

## Why it's queued

The earliest of the clarification benchmarks and the only **peer-reviewed** one in that group
(ACM TOSEM). Injects inconsistency, ambiguity and incompleteness into problem descriptions and
scores Communication Rate and Good Question Rate; also introduces an agent (Okanagan). Cited by
[`clareval.md`](clareval.md) as the work that pioneered ambiguity injection for clarification
testing, which is the lineage of the design we intend to copy — so it should be read to see
what ClarEval changed and why.
