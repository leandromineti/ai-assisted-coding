---
key: 2026-akita-agent-memory
title: "Memória de Agentes IA: Karpathy LLM Wiki e agentmemory na Prática"
authors: [Fabio Akita]
year: 2026
venue: "akitaonrails.com (author's blog)"
peer_reviewed: false   # a single practitioner's blog post; testimony, not a measured result
url: https://akitaonrails.com/2026/05/18/memoria-agentes-karpathy-llm-wiki-agentmemory/
snapshot: https://web.archive.org/web/20261104222431/https://akitaonrails.com/2026/05/18/memoria-agentes-karpathy-llm-wiki-agentmemory/   # PT page; the post is edited in place (see Limits). Save-page-now capture taken 2026-11-04, the day the text was read
kind: critique
read_depth: full   # the PT page text (297 lines in the local cache) read end to end 2026-11-04; the author's own /en/ page used for every translation
retrieved: 2026-11-04
pdf: references/papers/pdf/2026-akita-agent-memory.pt.txt   # extracted page text, gitignored; the author's EN page is cached alongside as 2026-akita-agent-memory.en.txt
bears_on: [agentmemory, ai-memory, conclusion-14]
verdict: "refines conclusion 14 as testimony — the author's own 2026-05-23 retraction of agentmemory (three named defects, no mechanism given) is the from-essay source for the agentmemory ledger row and an owed confrontation for the ai-memory re-read"
---

# Memória de Agentes IA: Karpathy LLM Wiki e agentmemory na Prática (2026-05-18, with a 2026-05-23 retraction)

`retrieved: 2026-11-04` · `read_depth: full` · [PT live](https://akitaonrails.com/2026/05/18/memoria-agentes-karpathy-llm-wiki-agentmemory/) · [PT archived](https://web.archive.org/web/20261104222431/https://akitaonrails.com/2026/05/18/memoria-agentes-karpathy-llm-wiki-agentmemory/) · [EN live (the author's own translation)](https://www.akitaonrails.com/en/2026/05/18/ai-agent-memory-karpathy-llm-wiki-agentmemory/) · [EN archived](https://web.archive.org/web/20261104222542/https://akitaonrails.com/en/2026/05/18/ai-agent-memory-karpathy-llm-wiki-agentmemory/)

Text caches (gitignored, not links): `references/papers/pdf/2026-akita-agent-memory.pt.txt`, `references/papers/pdf/2026-akita-agent-memory.en.txt`.

Quote convention: every `> ` line is one contiguous verbatim span of the Portuguese original; the
`> EN: ` line under it is the author's own English page, never our translation. A passage the
English page lacks is marked "no author translation". Locators are the PT section headings.

## What it does

A practitioner's survey of how Codex CLI, opencode and Claude Code compact their context (read
from each one's source, Claude Code's via a circulating leak), why compaction loses long-term
memory, Karpathy's "LLM Wiki" pattern, and a one-week trial of agentmemory, an open-source MCP
memory server. A 2026-05-23 update at the top then retracts the recommendation: after a week of
personal use the author walks agentmemory back and names the ai-memory project he started as a
replacement.

## Design

Locators are the PT section headings. The post reports what the author ran and read; it reports
no benchmark and no controlled comparison.

- **agentmemory: implementação prática do padrão** — what the tool is, as the author describes it:

> Storage em SQLite + index vetorial em memória, zero dependência externa.

> EN: Storage on SQLite + in-memory vector index, zero external dependencies.

> Expõe 51 tools de memória (memory_smart_search, memory_save, memory_sessions, memory_consolidate, etc.).

> EN: Exposes 51 memory tools (memory_smart_search, memory_save, memory_sessions, memory_consolidate, etc.).

> Plugins de hooks pra Claude Code (12 hooks) e Codex (6 hooks)

> EN: Hook plugins for Claude Code (12 hooks) and Codex (6 hooks)

> Retrieval híbrida: BM25 + vetor + knowledge graph, fundidos com Reciprocal Rank Fusion (RRF, k=60), com diversificação por sessão.

> EN: Hybrid retrieval: BM25 + vector + knowledge graph, fused via Reciprocal Rank Fusion (RRF, k=60), with per-session diversification.

> Working (raw observations) → Episodic (resumos de sessão) → Semantic (fatos e padrões extraídos) → Procedural (workflows e padrões de decisão).

> EN: Working (raw observations) → Episodic (session summaries) → Semantic (extracted facts and patterns) → Procedural (workflows and decision patterns).

- **Os trade-offs que ficam** — the author's own caveats, written before the retraction. The first
  two bear on a concurrency/liveness question and a zero-LLM question:

> O daemon roda como processo permanente.

> EN: The daemon runs as a permanent process.

> senão os hooks do plugin perdem eventos

> EN: or the plugin hooks miss events

> Sem chave de provider configurada, o agentmemory roda em “no-op mode” — ainda indexa observações e busca, mas não comprime nem consolida.

> EN: Without a provider key configured, agentmemory runs in “no-op mode” — still indexes observations and searches, but doesn’t compress or consolidate.

> a porta 49134 do iii engine bindeia em 0.0.0.0 por default (passa pelo firewall, vale conferir)

> EN: the iii engine’s port 49134 binds to 0.0.0.0 by default (passes through your firewall, worth checking)

> o import-jsonl não respeita o flag --dry-run apesar de o help global dizer que sim

> EN: import-jsonl doesn’t honor the --dry-run flag despite the global help saying it does

- **Vantagem prática: handoff sem fricção** — the cross-agent continuity claim (relevant to
  conclusion 14, which finds continuity real and pull-shaped):

> Os dois agentes lêem do mesmo lugar.

> EN: Both agents read from the same place.

The compaction sections (Codex CLI, opencode, Claude Code) and the Karpathy LLM Wiki section are
background to the above and carry no claim a ledger row or report needs; they were read, not
mined.

### 2026-05-23 update (retraction)

The update sits at the top of the PT page, above the original first paragraph. It names three
defects in one parenthetical and gives no mechanism, measurement or source reference for any of
them. Each defect below is the shortest verbatim span that states it, so the agentmemory ledger
row can quote the essay and not a paraphrase.

- **Framing:**

> depois de uma semana rodando o agentmemory em produção pessoal, voltei atrás

> EN: after a week running agentmemory in personal production, I’m walking it back

> A arquitetura escolhida acumula uma classe de bug que não fecha sem reescrever metade do sistema

> EN: The architecture it picked accumulates a class of bug that doesn’t close without rewriting half the system

- **Defect 1, BM25 reindex at every restart:**

> BM25 reindex a cada restart

> EN: BM25 reindex on every restart

- **Defect 2, the ~5 s data-loss window** (the essay writes "5s", not "~5 s"):

> janela de 5s de perda de dados

> EN: 5-second data-loss window

- **Defect 3, the wrong hook on ~47% of Claude Code tool calls:**

> hook errado em ~47% das tool calls do Claude Code

> EN: wrong hook key on ~47% of Claude Code tool calls

The English page carries this update (marker "Update (May 23, 2026)", checked 2026-11-04), and
its wording differs slightly from the PT ("wrong hook key" for "hook errado"). The parenthetical
ends "etc", so the list is not claimed to be complete. The update also names the replacement:

> Comecei um substituto em Rust chamado ai-memory que resolve esses problemas.

> EN: I started a Rust replacement called ai-memory that fixes those.

The author is therefore both the retraction's source and the maker of the named replacement.

## Numbers worth keeping

Copied, never rounded; locators are PT section headings.

- agentmemory's tool surface — "Expõe 51 tools de memória", "12 hooks" for Claude Code, "6 hooks"
  for Codex, RRF "k=60", ports 3111 (REST) and 3113 (viewer), 4 consolidation tiers (section
  *agentmemory: implementação prática do padrão*). These are the author's description of the
  tool as of 2026-05-18, not a source reading.
- The retraction's figures: "5s" window and "~47%" of Claude Code tool calls (update at the top);
  both are the author's, unmeasured in the post.
- Claude Code's compaction constants, as the author read them in the leaked source (section
  *Claude Code: três níveis de compaction + summary detalhado*). The code lines are English in
  both pages:

> export const AUTOCOMPACT_BUFFER_TOKENS = 13_000

> EN: export const AUTOCOMPACT_BUFFER_TOKENS = 13_000

> 1,279 sessions had 50+ consecutive failures (up to 3,272), wasting ~250K API calls/day globally

> EN: 1,279 sessions had 50+ consecutive failures (up to 3,272), wasting ~250K API calls/day globally

  The second is the author's quotation of an internal code comment in a leaked source; this repo
  has not seen that source, so it is hearsay twice over.

## What it means for this repo

- **From-essay source.** This note is where the agentmemory ledger row (phase 15, plan 15-03)
  quotes the three 2026-05-23 defects from, and where its from-essay predictions get their tag.
  The essay gives symptoms only; whether the shipped `v0.9.31` still has them, and whether the
  ~47% fraction is even reproducible by reading source, is exactly what the row's predictions
  leave to the later deep dive.
- **Owed confrontations, named and not applied (D-19).** The ai-memory re-read owes a check of
  the essay's claim that ai-memory "resolve esses problemas": a rival's retraction note is a
  maker's marketing claim about the replacement, to be confronted with source at the re-read
  pin. The agentmemory deep dive owes a source check of each of the three defects at its pin.
- **Conclusion 14** (cross-harness continuity is real and pull-shaped): the "handoff sem
  fricção" section is the author's practitioner claim of the same phenomenon from a
  daemon-plus-MCP design. It supports the direction of the conclusion as testimony and adds no
  measurement. No conclusion, report or README is edited by this note.

## Limits

- **Testimony grade** (methodology rule 1a): one practitioner's account of one week of personal
  use. No benchmark, no controlled arm, no run output reproduced in the post.
- **The author ships a rival memory tool.** The retraction is made by the maker of the named
  replacement (ai-memory); the update promotes it. A real defect list and a competitor's pitch
  are not separable from the page alone.
- **Not peer-reviewed.** `peer_reviewed: false`.
- **Edited in place, with an unchanged `dateModified`.** The page's `datePublished` and
  `dateModified` both read `2026-05-18T15:00:00-03:00` on 2026-11-04, although the 2026-05-23
  update sits at the top of the page. A reader going by page metadata would take the post as
  unchanged since 05-18 and miss the retraction. That is the reason the record is a Wayback
  snapshot: the capture linked above (2026-11-04) carries the title and the 05-23 update.
- **Snapshot route.** Save-page-now, run on 2026-11-04, the day the text was read, for both
  the PT and the EN page. Measure: each capture was fetched raw (`id_`), decompressed and reduced
  to its text (scripts and styles dropped, inline tags joined without a separator, NFC, whitespace
  collapsed, `*_`` ` stripped on both sides). Every quoted line in this note was then checked as a
  substring of that text: PT 19/19 and EN 19/19. The page title matched in both.
- **Measures.** Cache sizes: PT 24765 characters / 25384 UTF-8 bytes; EN 24055 characters /
  24287 UTF-8 bytes (the extractor keeps article-body text only; page navigation is dropped).
  Quote equality means a substring match after NFC and whitespace-run collapsing.
- **Source claims are the author's.** The compaction material (thresholds, prompts, the circuit
  breaker) is stated by the author from source this repo has not read, Claude Code's from a
  leak. Nothing here is source-traced by us (methodology rule 8: docs-view, and weaker).
