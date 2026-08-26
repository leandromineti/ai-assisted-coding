---
key: 2025-longmemeval
title: "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory"
authors: [Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang, Dong Yu]
year: 2025
venue: ICLR 2025
peer_reviewed: true
arxiv: 2410.10813
citations: "533 (133 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://github.com/xiaowu162/LongMemEval
kind: benchmark
read_depth: full   # main text (pp. 1–10, through Conclusion) read end to end; appendices A–E consulted via cross-references only
retrieved: 2026-08-18
pdf: references/papers/pdf/2025-longmemeval.pdf
bears_on: [mem0, ai-memory, memos, memory-kind, benchmarks]
verdict: "the strongest instrument of the three memory benchmarks cataloged — human-curated questions, judge validated at 97% human agreement, and a design-space taxonomy (indexing/retrieval/reading) that maps 1:1 onto what the memory-kind vendors actually build"
---

# LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory

`retrieved: 2026-08-18` · `read_depth: full` · [ICLR 2025 / repo](https://github.com/xiaowu162/LongMemEval)

## What it does

500 manually created questions over five memory abilities — information extraction,
multi-session reasoning, knowledge updates, temporal reasoning, abstention — embedded
in freely length-scalable simulated user–assistant chat histories (needle-in-haystack
over *sessions*, not documents). Two standard settings: LongMemEval_S (~115K
tokens/question) and LongMemEval_M (500 sessions, ~1.5M tokens) (§3). Then formulates
memory systems as a three-stage pipeline — indexing, retrieval, reading — with four
control points (value, key, query, reading strategy) and measures design choices along
each (§4–5).

## Design

- **Questions are human-expert-written** (LLM-seeded, manually filtered/rewritten),
  decomposed into evidence statements with annotated positions — so retrieval recall
  (Recall@k, NDCG@k) is measurable directly, not only end-task accuracy (§3.2–3.3).
- Evidence sessions are LLM-simulated *task-oriented* self-chat conveying facts
  indirectly, then manually screened; haystack filler comes from non-conflicting
  simulated chat plus ShareGPT/UltraChat (§3.2).
- **Scoring**: prompt-engineered gpt-4o-2024-08-06 judge, meta-evaluated at **>97%
  agreement with human experts** (§3.3) — the only one of the three cataloged memory
  benchmarks that validates its judge.
- Distinguishing coverage vs LoCoMo: assistant-side information recall, knowledge
  *updates*, and abstention; Table 1 positions all prior benchmarks.

## Numbers worth keeping

- Commercial memory systems, 97-question subset, ~10x shorter history than
  LongMemEval_S: ChatGPT (GPT-4o) **0.577** vs **0.918** offline reading — a 37%
  drop; Coze 0.330/64% drop (Figure 3a). "ChatGPT tended to overwrite crucial
  information as the chat continues."
- Long-context LLMs drop **30–60%** on LongMemEval_S vs oracle-context (Figure 3b);
  GPT-4o 0.870 → 0.606.
- Design findings (§5): round > session as value granularity; key expansion with
  extracted user facts **+9.4% recall@k, +5.4% accuracy**; time-aware indexing +
  query expansion **+6.8–11.3%** recall on temporal questions; Chain-of-Note + JSON
  reading up to **+10 pts** — even with *oracle* retrieval, reading strategy costs up
  to 10 points (Figure 6).

## What it means for this repo

Two distinct uses. **As an instrument**: this is the benchmark to prefer when grading
memory-kind vendor claims (mem0 cites it) — human-curated, judge-validated,
retrieval-recall observable. Same transfer caveat as LoCoMo: the domain is personal
chat-assistant memory (164 user attributes: lifestyle, belongings, life events); no
code, no tool traces. **As a design-space map**: its four control points line up with
what the arc's reads found built — ai-memory's fact-level pages and entity index are
key-expansion (CP2), its authority/decay tiers are value policy (CP1), memos' bounded
recall + `<memos_context>` injection is a reading strategy (CP4), and ai-memory's
`sessions/<id>.md` vs observation rows is exactly the session-vs-round granularity
question (CP1). ai-memory's own future-work names porting LongMemEval-S. The paper's
"even perfect recall loses 10 points to bad reading" is the sharpest available
argument that injection format — the thing the memory kind's harness shims control —
is measurable and material.

## Limits

- Chat histories are simulated (self-chat + ShareGPT filler); only the questions are
  human-authored. Realism rests on manual screening.
- Five abilities but 500 questions total — per-ability slices are small.
- Judge is a single OpenAI model (gpt-4o-2024-08-06); 97% agreement was measured at
  construction time, not per-evaluated-system.
- Commercial-system pilot (ChatGPT/Coze) used a 10x-shortened history and 97
  questions — directional, not a leaderboard.
