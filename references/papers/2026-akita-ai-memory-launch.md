---
key: 2026-akita-ai-memory-launch
title: "Criei um Sistema de Memória pra Agentes de Código: ai-memory"
authors: [Fabio Akita]
year: 2026
venue: "akitaonrails.com (author's blog)"
peer_reviewed: false   # a single practitioner's blog post, written by the maker of the product it launches; testimony, not a measured result
url: https://akitaonrails.com/2026/05/23/criei-sistema-memoria-agentes-codigo-ai-memory/
snapshot: https://web.archive.org/web/20261104231813/https://akitaonrails.com/2026/05/23/criei-sistema-memoria-agentes-codigo-ai-memory/   # PT page; save-page-now capture taken 2026-11-04, the day the text was read
kind: critique   # half retraction rationale (why agentmemory failed), half launch of ai-memory; ingested for the first half
read_depth: full   # the PT page text (256 lines in the local cache) read end to end 2026-11-04; the author's own /en/ page used for every translation
retrieved: 2026-11-04
pdf: references/papers/pdf/2026-akita-ai-memory-launch.pt.txt   # extracted page text, gitignored; the author's EN page is cached alongside as 2026-akita-ai-memory-launch.en.txt
bears_on: [agentmemory, ai-memory, conclusion-14]
verdict: "vendor testimony — the 'relato completo' the 2026-05-18 essay's retraction points to: gives a mechanism and an agentmemory issue number for each of the three retraction defects (#309, #204, #539), but no agentmemory version and no measurement method; supersedes the agentmemory ledger row's 'without a mechanism' absence and re-scopes its predictions 1 and 2"
---

# Criei um Sistema de Memória pra Agentes de Código: ai-memory (2026-05-23)

`retrieved: 2026-11-04` · `read_depth: full` · [PT live](https://akitaonrails.com/2026/05/23/criei-sistema-memoria-agentes-codigo-ai-memory/) · [EN live (the author's own translation)](https://akitaonrails.com/en/2026/05/23/i-built-memory-system-for-coding-agents-ai-memory/) · [PT archived](https://web.archive.org/web/20261104231813/https://akitaonrails.com/2026/05/23/criei-sistema-memoria-agentes-codigo-ai-memory/) · [EN archived](https://web.archive.org/web/20261104231835/https://akitaonrails.com/en/2026/05/23/i-built-memory-system-for-coding-agents-ai-memory/)

Text caches (gitignored, not links): `references/papers/pdf/2026-akita-ai-memory-launch.pt.txt`, `references/papers/pdf/2026-akita-ai-memory-launch.en.txt`.

Quote convention: every `> ` line is one contiguous verbatim span of the Portuguese original; the
`> EN: ` line under it is the author's own English page, never our translation. Locators are the
PT section headings.

## What it does

The post the 2026-05-23 update of the author's
[2026-05-18 essay](2026-akita-agent-memory.md) points to for "o relato completo" (the full
account). It does two things: it explains, defect by defect, why the author walked back his
recommendation of agentmemory after a week of personal use, and it launches ai-memory, the Rust
replacement he started (at the `v0.2-complete` tag, by his account), with its design, install
path, commands and a consolidation-model comparison. It reports no benchmark of agentmemory and
no controlled comparison between the two tools.

## Design

### Por que o agentmemory não rolou — the defect account

The framing:

> Depois de uma semana rodando ele em produção pessoal, voltei atrás.

> EN: After a week running it in personal production, I’m walking it back.

The section lists five defects, each with a one-line mechanism and an agentmemory issue number.
The 05-18 update's parenthetical named three of them and ended "etc"; this list adds two
(#456 two config-read paths, #303 cwd-relative state store). The three the agentmemory ledger
row predicts on:

- **Defect 1, BM25 reindex at every restart (#309).** Mechanism given: the index is persisted to
  a file through the iii-engine KV, the save times out on large stores, the file is left nearly
  empty, and each restart rebuilds.

> Reindexação do BM25 a cada restart. O índice persiste num arquivo (mem:index:bm25.bin) através de um KV remoto chamado iii-engine.

> EN: BM25 reindex on every restart. The index persists to a file (mem:index:bm25.bin) through a remote KV called iii-engine.

> Com poucas observações isso voa, mas passa de 10K observações e o state::set começa a dar timeout, o arquivo fica em ~96 bytes vazio, e cada restart paga ~5 minutos reconstruindo do zero (issue #309, aberta).

> EN: With few observations it flies, but pass 10K observations and state::set starts timing out, the file stays at ~96 empty bytes, and every restart pays ~5 minutes rebuilding from scratch (issue #309, still open).

  So the defect, on this account, is not that no persisted index is loaded. A persisted index
  exists; its save fails silently past a size threshold, and the rebuild follows from that.

- **Defect 2, the 5 s data-loss window (#204).** Mechanism given: a 5 s debounce in front of
  persistence, and a 30 s `state::set` timeout that kills the Node process.

> Janela de perda de dados de 5 segundos. Toda persistência passa por um debounce de 5s do IndexPersistence.

> EN: 5-second data-loss window. All persistence flows through a 5s debounce on IndexPersistence.

> Quando o timeout de 30s do state::set estoura, o processo Node morre levando junto tudo que tava em memória (#204).

> EN: When the 30s state::set timeout blows up, the Node process dies taking everything that was in memory with it (#204).

  What is lost, on the post's account: "tudo que tava em memória" (the author's English:
  "everything that was in memory"), behind a debounce the post names `IndexPersistence` and says
  "Toda persistência" (his English: "All persistence") flows through. The post does not separate observation records from index
  state. ai-memory's own digest of agentmemory (`docs/issues-agentmemory.md` at ai-memory
  `v3.3.3`, line 27) is narrower: "losing every in-memory BM25/vector update since the last
  debounce flush", that is, index updates. The trigger in both is a process death caused by the
  `state::set` timeout, not an arbitrary kill.

- **Defect 3, the wrong hook on ~47% of Claude Code tool calls (#539).** Mechanism given: a
  payload field mismatch, not a wrong hook registration.

> Hook errado em ~47% das tool calls do Claude Code. O hook leu data.tool_output, mas o Claude Code manda tool_response.

> EN: Wrong hook key on ~47% of Claude Code tool calls. The hook reads data.tool_output, but Claude Code sends tool_response.

> Seis semanas com observações sumindo silenciosamente (#539).

> EN: Six weeks of observations silently vanishing (#539).

  The post states the consequence as observations vanishing. The digest (line 37) states it as
  "`mem::compress` silently failed on ~47% of Claude Code tool calls" and records "(#539, fixed
  PR #561)"; the post does not say whether it was fixed. Neither gives a denominator for the
  ~47%.

The section's closing points to the author's research write-up, and the link under "aqui"
(checked in the fetched PT HTML, 2026-11-04) is
`https://github.com/akitaonrails/ai-memory/blob/main/docs/issues-agentmemory.md`, the digest
itself at `main`:

> Tem mais. Documentei aqui no meu repo de pesquisa.

> EN: There’s more. I wrote it all up here in my research repo.

> A forma do problema é estrutural, não falta de esforço do mantenedor.

> EN: The shape of the problem is structural, not a lack of effort from the maintainer.

The five defect lines also link one agentmemory GitHub issue each (#309, #204, #456, #539, #303,
read from the fetched PT HTML's `href`s). Those issues were not opened for this note (see Limits).

### A pesquisa antes do código / ai-memory's design

The author says the research behind ai-memory read rivals' source and issues:

> Em vez de só sair codando, pesquisamos o código-fonte e issues dos projetos relevantes pra entender o que cada um acertou e errou.

> EN: Instead of just diving into code, we dug through the source and issues of the relevant projects to understand what each one got right and wrong.

ai-memory's answer to defects 1 and 2, as claimed for the `v0.2-complete` era:

> Índice persistente em SQLite + FTS5. Nativo. Sem reindex a cada restart.

> EN: Persistent index in SQLite + FTS5. Native. No reindex on every restart.

> Writer único em thread dedicada via mpsc. Sem janela de perda de 5s, sem timeout de 30s estourando.

> EN: Single writer in a dedicated thread via mpsc. No 5s loss window, no 30s timeout blowing up.

The cross-agent handoff, as claimed (section *Exemplo de handoff entre agentes*):

> No SessionStart do Codex, o servidor viu o handoff pending, recuperou e injetou no contexto inicial.

> EN: At Codex’s SessionStart, the server saw the pending handoff, fetched it, and injected it into the initial context.

> O ai-memory tá nas tags v0.2-complete no GitHub.

> EN: ai-memory is at the v0.2-complete tag on GitHub.

The install, command, web-UI and Docker sections are product documentation and carry no claim a
ledger row or report needs; they were read, not mined. The consolidation-model table (section
*Qual LLM usar pra consolidação*) reports an A/B of 6 providers over 5 synthetic fixtures; the
post gives the summary only and points to `docs/llm-provider-comparison.md` for the full tables.

## Numbers worth keeping

Copied, never rounded; locators are PT section headings. All are the author's statements; the
post shows no method, run or output behind any of them.

- Defect 1 (#309): "10K observações" as the threshold, "~96 bytes" left in the index file,
  "~5 minutos" per restart rebuild; issue marked "aberta" on 2026-05-23.
- Defect 2 (#204): a "5s" debounce, a "30s" `state::set` timeout.
- Defect 3 (#539): "~47%" of Claude Code tool calls, "Seis semanas" of loss.
- agentmemory at the time: "15.7K estrelas"; the architecture as "4 portas, 3 processos".
- **No agentmemory version is named anywhere in the post** (searched: the PT cache end to end,
  2026-11-04). The defects are dated only by the post (2026-05-23) and by the issue numbers.

## What it means for this repo

- **Supersedes an absence.** The [2026-05-18 note](2026-akita-agent-memory.md) and the
  agentmemory row in [`tools/candidates.md`](../../tools/candidates.md) said the retraction gave
  no mechanism; they had searched the 05-18 page only. This post gives one per defect. The row
  carries a dated pre-read amendment (2026-11-04, review CR-01/CR-02/WR-01) that re-scopes its
  predictions 1 and 2 on these mechanisms and re-tags their provenance.
- **Two figures need the mechanism, not the number.** Defect 1's mechanism (a persisted index
  whose save silently fails) means a source read that finds "load the persisted index, rebuild
  if missing" has not yet decided anything; the save path decides it. Defect 2's loss is stated
  as "everything in memory" here and as index updates in the digest, so what is lost has to be
  scored per kind of data.
- **Owed confrontations, named and not applied.** The ai-memory re-read owes a check of the two
  design claims quoted above (SQLite + FTS5 index with no restart reindex; a single mpsc writer
  with no loss window) at its pin. The handoff claim is the mechanism conclusion 14 measured
  for ai-memory: the post describes a pending handoff injected at SessionStart; exp-04 measured
  the automatic floor at 0/10 for mid-session facts at its own pin. The post is testimony about
  the `v0.2-complete` era and changes neither the conclusion nor the report.

## Limits

- **Testimony grade** (methodology rule 1a): one practitioner's week of personal use plus his
  reading of a rival's issues. Every mechanism is stated, none is shown in code or output here.
- **The author ships the replacement.** The defect account is written by the maker of ai-memory
  in the post that launches it. A real defect list and a competitor's pitch are not separable
  from the page alone.
- **Not peer-reviewed.** `peer_reviewed: false`.
- **Surfaces not read** (pre-read discipline for the agentmemory and MemPalace deep dives,
  phase 15 decision D-07): the agentmemory GitHub issues the post links (#309, #204, #456,
  #539, #303); ai-memory's `research-agentmemory.md` and the other `research-*.md` files the
  post names; `docs/llm-provider-comparison.md`. The digest the post links at `main` was read
  at the `v3.3.3` tag instead, which is the copy the ledger row cites.
- **Snapshot route.** The page's `datePublished` and `dateModified` both read
  `2026-05-23T16:30:00-03:00` on 2026-11-04 (PT and EN). The author's other posts are known to
  be edited in place with an unchanged `dateModified`
  ([2026-05-18 note](2026-akita-agent-memory.md), Limits), so the record is a save-page-now
  capture, run on 2026-11-04, the day the text was read, for both the PT and the EN page.
  Measure: each capture was fetched raw (`id_`), decompressed and reduced to its text (scripts
  and styles dropped, inline tags joined without a separator, NFC, whitespace collapsed, `*_`` `
  stripped on both sides). Every quoted line in this note was then checked as a substring of
  that text: PT 14/14 and EN 14/14. The page title matched in both.
- **Measures.** Fetched 2026-11-04 with `curl --compressed -L`, both HTTP 200, HTML `<title>`s
  "Criei um Sistema de Memória pra Agentes de Código: ai-memory – AkitaOnRails.com" and
  "I Built a Memory System for Coding Agents: ai-memory – AkitaOnRails.com". Article body only
  (the `<article>` element; scripts, styles, nav, header, footer and asides dropped), NFC.
  Cache sizes: PT 22108 characters / 22732 UTF-8 bytes, 256 lines; EN 21733 characters / 21958
  UTF-8 bytes, 256 lines. Quote check: every `> ` line in this note is a substring of the PT
  cache and every `> EN: ` line a substring of the EN cache, compared after NFC and
  whitespace-run collapsing on both sides: PT 14/14, EN 14/14 (2026-11-04). Without that
  normalisation, as exact substrings of the raw caches: 28/28.
