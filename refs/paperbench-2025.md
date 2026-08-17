---
key: paperbench-2025
title: "PaperBench: Evaluating AI's Ability to Replicate AI Research"
authors: [OpenAI, et al.]
year: 2025
venue: "OpenAI (frontier-evals)"
peer_reviewed: false
url: https://github.com/openai/frontier-evals/tree/main/project/paperbench
kind: benchmark
read_depth: abstract
retrieved: 2026-08-17
bears_on: [exp-02, issue-4]
verdict: "shows what issue #4's option 2 looks like done well — partial credit via a hierarchical tree of ~8,000 individually gradable binary criteria with weights, not a holistic quality score; dissolves the option-1-vs-option-2 dichotomy"
---

# PaperBench

`retrieved: 2026-08-17` · `read_depth: abstract` · [github.com/openai/frontier-evals](https://github.com/openai/frontier-evals/tree/main/project/paperbench)

## What it does

Evaluates agents on replicating 20 ICML-2024 papers from scratch. Each paper carries a
manually-built **hierarchical rubric tree** decomposing replication into >8,000
individually gradable leaf criteria with point weights; a model-based judge grades each
leaf, and the score is the weighted fraction of criteria met. (HealthBench applies the
same shape at larger scale: ~48,562 physician-written weighted criteria.)

## What it means for this repo

Reframes issue #4's option 2. The issue's stated cost — "reintroduces judgment the
machine checks removed" — assumes *holistic* grading; the community's partial-credit form
is **analytic**: many small binary criteria, each independently checkable, weighted and
summed. That is structurally the same object as a large trap set — which means options 1
and 2 are not alternatives but the same design at different granularities. For exp-02:
a trap set of N machine-checked binary items scored as a weighted sum *is* option 2
without a judge, and keeps the objectivity the machine checks bought. The judge only
enters where a criterion can't be machine-checked — which exp-02 can simply exclude.

## Limits

read_depth abstract; rubric construction cost is enormous at PaperBench scale (hand-built
per paper) and only the *shape* transfers to an n=1 experiment; model-judge leaves depend
on judge reliability, which conclusion 6's own re-examination (issue #8) already flags as
a weak point — another reason to keep exp-02's leaves machine-checked.
