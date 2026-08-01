---
key: tau2-bench
title: "τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment"
authors: [Victor Barres, Honghua Dong, Soham Ray, Xujie Si, Karthik Narasimhan]
year: 2025
venue: arXiv preprint
peer_reviewed: false
arxiv: 2506.07982
url: https://arxiv.org/abs/2506.07982
kind: benchmark
read_depth: unread
retrieved: 2026-07-31
pdf: refs/pdf/tau2-bench.pdf
bears_on: [metrics, exp-03]
verdict: "UNREAD — queued lead, must not be cited until read"
---

# τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment

`retrieved: 2026-07-31` · `read_depth: **unread**` · [arXiv:2506.07982](https://arxiv.org/abs/2506.07982)

> **Nothing below is verified.** The PDF is cached at `refs/pdf/tau2-bench.pdf` and has **not** been
> read. The lines under "Why it's queued" come from the abstract and search-result summaries
> only, which is exactly the provenance this library exists to keep separate from evidence.
> `scripts/build-refs-index.py --check` fails if this key is cited anywhere outside `refs/`.
> To promote it: read the PDF, rewrite this note from
> [`_template-ref-note.md`](_template-ref-note.md), and set an honest `read_depth`.

## Why it's queued

Successor to [`tau-bench.md`](tau-bench.md) in which *both* the agent and the user can act on
the environment — a "dual-control" setting. Relevant because our arms operate in an environment
the human also touches, which single-control benchmarks do not model. Read it before designing
any oracle that is allowed to change state rather than only answer questions.
