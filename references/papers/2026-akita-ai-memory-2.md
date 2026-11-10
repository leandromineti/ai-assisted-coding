---
key: 2026-akita-ai-memory-2
title: "AI-MEMORY 2.0 - o melhor sistema de memória para agentes e times"
authors: [Fabio Akita]
year: 2026
venue: "akitaonrails.com (author's blog)"
peer_reviewed: false   # the maker's own release essay for his own product; testimony, not a measured result
url: https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/
snapshot: https://web.archive.org/web/20261104222606/https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/   # PT page; the post is edited in place (see Limits). Save-page-now capture taken 2026-11-04, the day the text was read
kind: method
read_depth: full   # the PT page text (121 lines in the local cache) read end to end 2026-11-04; the author's own /en/ page used for every translation
retrieved: 2026-11-04
pdf: references/papers/pdf/2026-akita-ai-memory-2.pt.txt   # extracted page text, gitignored; the author's EN page is cached alongside as 2026-akita-ai-memory-2.en.txt
bears_on: [ai-memory, agentmemory, mempalace, basic-memory]
verdict: "vendor testimony about ai-memory 2.0 (v2.0.0 era) and its rivals — the from-essay source for the author's claims about MemPalace, agentmemory and basic-memory, and an owed confrontation for the ai-memory re-read (single writer, zero-LLM default path, local embeddings, LongMemEval-S hit@5)"
---

# AI-MEMORY 2.0 - o melhor sistema de memória para agentes e times (2026-09-02)

`retrieved: 2026-11-04` · `read_depth: full` · [PT live](https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/) · [PT archived](https://web.archive.org/web/20261104222606/https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/) · [EN live (the author's own translation)](https://www.akitaonrails.com/en/2026/09/02/ai-memory-2-0-best-memory-system-for-agents-and-teams/) · [EN archived](https://web.archive.org/web/20261104222630/https://akitaonrails.com/en/2026/09/02/ai-memory-2-0-best-memory-system-for-agents-and-teams/)

Text caches (gitignored, not links): `references/papers/pdf/2026-akita-ai-memory-2.pt.txt`, `references/papers/pdf/2026-akita-ai-memory-2.en.txt`.

Quote convention: every `> ` line is one contiguous verbatim span of the Portuguese original; the
`> EN: ` line under it is the author's own English page, never our translation. Locators are the
PT section headings.

## What it does

The release essay for ai-memory 2.0, written by the project's maker. It states why the version
became 2.0 (a semantic-versioning reset), the headline changes (an open on-disk format, local
embeddings on by default, several agents and several people on one project) and a positioning
section against competing memory tools by name. It is a pitch, labelled as one ("o pitch
completo"), not a measurement.

## Design

What the author says the 2.0 design is. Each claim is dated to the version it describes
(ai-memory 2.0.x as of 2026-09-02); the repo's ai-memory report is pinned at v2.0.2, and the
re-read targets v3.3.3.

- **Embeddings locais, ligados por padrão** — an in-process embeddings model, and one benchmark
  figure:

> No benchmark LongMemEval-S, o hit@5 sobe de 0.617 só com full-text para 0.779 com os embeddings locais.

> EN: On the LongMemEval-S benchmark, hit@5 goes from 0.617 with full-text only to 0.779 with the local embeddings.

> Na primeira execução ele baixa o modelo (uns 87 MB, com checksum fixo) em background

> EN: On the first run it downloads the model (about 87 MB, with a fixed checksum) in the background

> Foi justamente essa camada nativa que gerou um tipo de crash recorrente em outros projetos de memória.

> EN: That native layer is exactly what caused a recurring kind of crash in other memory projects.

- **Vários agentes ao mesmo tempo, no mesmo projeto** — the concurrency model, as claimed:

> Todas as escritas passam por um único writer, com fila e backpressure, então uma rajada não corrompe nada.

> EN: Every write goes through a single writer, with a queue and backpressure, so a burst doesn’t corrupt anything.

> Quando duas janelas gravam na mesma página, a segunda não apaga a primeira.

> EN: When two windows write to the same page, the second doesn’t erase the first.

- **Onde o ai-memory fica frente à concorrência** — the zero-LLM and single-binary claims:

> E o caminho padrão roda com zero chamada de LLM.

> EN: And the default path runs with zero LLM calls.

> Ele é um binário só. Sem sidecar, sem três bancos pra sincronizar.

> EN: It’s a single binary. No sidecar, no three databases to sync.

- **Um time inteiro no mesmo projeto** — the multi-user posture (attribution, no per-page
  permission):

> E não existe permissão por página, de propósito.

> EN: And there’s no per-page permission, on purpose.

> qualquer pessoa autenticada pode escrever, e o histórico é que guarda quem foi

> EN: anyone authenticated can write, and the history is what keeps track of who did

### The rival comparison, quoted for the ledger rows

Section *Onde o ai-memory fica frente à concorrência*. The author says the research behind it is
"documentada no repositório" (his own repo). The three rivals this milestone's ledger rows
cover are named below; each is the maker's characterisation of a competitor, to be confronted
with the competitor's source, not accepted:

> Tem o agentmemory, que é um MCP server em TypeScript preso a um sidecar nativo e a uma superfície gigante de dezenas de ferramentas.

> EN: There’s agentmemory, a TypeScript MCP server tied to a native sidecar and a giant surface of dozens of tools.

*Corrected 2026-11-10 (fold-in): read at `v0.9.31`, the sidecar is the iii engine, a separately downloaded prebuilt binary whose licence file declares Apache-2.0 AND Elastic-2.0 (agentmemory report, Engine dependency; iii's source was not read, so the licence is TESTIMONY), and the surface is 54 tools in the registry and 7 on the no-server shim. The maker's characterisation above is kept as read on its date.*

> Tem o basic-memory, em Python, Markdown no disco, mas com captura manual: você tem que pedir pra ele lembrar.

> EN: There’s basic-memory, in Python, Markdown on disk, but with manual capture: you have to ask it to remember.

> Tem o MemPalace, que viralizou com quase 50 mil estrelas em duas semanas por causa de um número de benchmark que, auditado, se mostrou inflado, além de sofrer de corrupção quando duas escritas acontecem juntas.

> EN: There’s MemPalace, which went viral with almost 50,000 stars in two weeks over a benchmark number that, once audited, turned out to be inflated, on top of suffering corruption when two writes happen together.

> E tem os grafos temporais como Zep, os “memory OS” como Letta (o antigo MemGPT) e os extratores de fato como o Mem0.

> EN: And there are the temporal graphs like Zep, the “memory OS” like Letta (the old MemGPT), and the fact extractors like Mem0.

graphiti is not named in the essay (it names Zep, the maker of that library, as the example of
"temporal graphs"); the line is recorded here for that reason and for nothing stronger. The
design-level claim about all of them:

> Foi exatamente esse desenho que evitou a corrupção de escrita concorrente que derrubou os outros.

> EN: That design is exactly what avoided the concurrent-write corruption that took the others down.

> Nenhum concorrente entrega esse conjunto.

> EN: No competitor delivers this set.

## Numbers worth keeping

Copied, never rounded; all are the author's, stated on 2026-09-02.

- LongMemEval-S hit@5: 0.617 (full-text only) to 0.779 (local embeddings), quoted in *Design*
  above. The essay gives no variant, split, harness or run count beside it.
- Project scale, section *A 2.0 é de todo mundo*:

> Os números até a 2.0: mais de 1.500 commits, 371 pull requests mergeados e 181 issues fechadas.

> EN: The numbers up to 2.0: more than 1,500 commits, 371 merged pull requests, and 181 closed issues.

> Hoje são cerca de setenta.

> EN: Today it’s around seventy.

  The second is the count of people with a merged PR; the essay gives no measure behind "cerca
  de setenta", and this repo's own contributor counts for ai-memory (a `git shortlog`
  distinct-author measure in the report) are a different instrument.
- MemPalace: "quase 50 mil estrelas em duas semanas" (quoted above), a star-velocity figure
  with no date and no source in the essay.

## What it means for this repo

- **Owed confrontation for the ai-memory re-read (named, not applied; D-19).** The claims worth
  confronting with source at the re-read pin: the single writer with a queue and backpressure,
  the zero-LLM default path, the in-process local embeddings, version-on-conflict writes, and
  the LongMemEval-S hit@5 figure. They describe 2.0.x; the report pins v2.0.2 and the re-read
  targets v3.3.3.
- **From-essay source for rival characterisations.** Wherever the essay describes MemPalace,
  agentmemory and basic-memory, the ledger rows quoting it tag the claim *from-essay*. All of
  those are the maker of a competing product characterising competitors. In particular the
  MemPalace claims (an audited, inflated benchmark number; corruption on two simultaneous
  writes) are exactly the concurrency-per-write-path questions the later MemPalace deep dive
  has to decide from source.

  *Corrected 2026-11-10 (fold-in): decided from source at MemPalace `v3.11.0`: every write path the prediction names reaches the same cross-process lock (prediction 1 TRUE, with bounds), and the benchmark clause is partly the vendor's own record (`docs/HISTORY.md`), per the [MemPalace report](../../tools/5-memory/mempalace.md) (Scored pre-read predictions; Benchmark claims). The ledger rows that quoted this essay's characterisations of MemPalace and agentmemory were removed when those reports landed, so the "owed" wording above describes a discharged obligation.*
- No conclusion, report or README is edited by this note.

## Limits

- **The vendor's own account of its own product.** It is testimony about ai-memory 2.0, not
  source (methodology rule 1a, testimony grade). The essay is explicitly a pitch.
- **Version-bound.** Every claim is dated to the version it describes (ai-memory 2.0.x on
  2026-09-02). The repo's ai-memory report is pinned at v2.0.2 and the re-read targets v3.3.3,
  so a claim that holds for 2.0 says nothing about 3.3.3 until confronted.
- **Not peer-reviewed.** `peer_reviewed: false`.
- **Rival characterisations come from an interested party.** Nothing in the essay is sourced to
  the competitors' code; the author's repo research is not reproduced in the post.
- **Edited in place.** The page's `datePublished` and `dateModified` both read
  `2026-09-02T11:00:00-03:00` on 2026-11-04. The snapshot is the record: save-page-now, run on
  2026-11-04, the day the text was read, for both the PT and the EN page. Measure: each capture was
  fetched raw (`id_`), decompressed and reduced to its text (scripts and styles dropped, inline tags
  joined without a separator, NFC, whitespace collapsed, `*_`` ` stripped on both sides). Every
  quoted line in this note was then checked as a substring of that text: PT 17/17 and EN 17/17.
  The page title matched in both.
- **Measures.** Cache sizes: PT 12902 characters / 13269 UTF-8 bytes; EN 12856 characters /
  13003 UTF-8 bytes (article-body text only). Quote equality means a substring match after NFC
  and whitespace-run collapsing.
