---
key: agent-frameworks-eval
title: "A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks"
authors: [unverified]
year: 2025
venue: arXiv preprint
peer_reviewed: false
arxiv: 2511.00872
url: https://arxiv.org/abs/2511.00872
kind: empirical-study
read_depth: abstract   # promoted from unread 2026-08-17 — abstract fetched and questioned; the 29pp PDF remains unread
retrieved: 2026-07-31
pdf: refs/pdf/agent-frameworks-eval.pdf
bears_on: [conclusion-6, conclusion-8, exp-03]
verdict: "abstract-level: compares 7 general-purpose agent frameworks (AgentOrchestra, OpenHands, GPTswarm, ...) on dev/vuln-detection/repair via success+efficiency+token-overhead — adjacent to exp-03 but frameworks-vs-frameworks, not framework-vs-plain; the full read stays queued for exp-03 positioning"
---

# A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks

`retrieved: 2026-08-17` · `read_depth: abstract` · [arXiv:2511.00872](https://arxiv.org/abs/2511.00872)

> **Abstract-level only** (promoted 2026-08-17). The 29pp PDF is cached and unread; the
> facts below the abstract line are leads. Abstract facts: 7 general-purpose frameworks
> (incl. AgentOrchestra, OpenHands, GPTswarm) on software development, vulnerability
> detection, and program repair; measured on task success, execution efficiency, and
> token overhead. Findings as stated: overall performance "moderate"; AgentOrchestra has
> the longest trajectories and most corrections (coordination overhead); OpenHands
> strongest reflective reasoning; software development the highest monetary cost;
> GPTswarm most cost-efficient. Framework-vs-framework, not framework-vs-plain — so it
> does NOT preempt exp-03's question, but its efficiency/overhead instrumentation is
> worth reading in full before exp-03's design.
> The lines under "Why it's queued" come from the abstract and search-result summaries
> only, which is exactly the provenance this library exists to keep separate from evidence.
> `scripts/build-refs-index.py --check` fails if this key is cited anywhere outside `refs/`.
> To promote it: read the PDF, rewrite this note from
> [`_template-ref-note.md`](_template-ref-note.md), and set an honest `read_depth`.

## Why it's queued

Empirically compares agent *frameworks* (not models) on code-centric SE tasks — potentially the
closest prior art to this repo's whole premise after
[`spec-kit-agents.md`](spec-kit-agents.md). 29 pages. Read it early: if it already measures what
exp-03 plans to measure, exp-03 needs repositioning, and if it doesn't, its gaps are our
argument. Author list not verified.
