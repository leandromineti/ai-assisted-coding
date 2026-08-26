# `references/` — the citation library

`created: 2026-07-31`

One note per source we've read and found relevant, so that what the literature already knows
compounds instead of living in a chat transcript. **Two halves since 2026-08-26**
([ADR-0034](../adrs/0034-references-papers-and-cards.md)): `papers/` — literature, the
original library — and `cards/` — vendor model cards, which are primary sources this repo
quotes but are not literature and do not fit the paper schema. Adapted from
[Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
immutable sources, a generated wiki over them, and a schema document
([`../CLAUDE.md`](../CLAUDE.md)) that tells an agent how to maintain both.

## Why it exists

On 2026-07-31 a single afternoon's search turned up two papers that bear directly on this
repo's published conclusions — one of them a 128-run ablation pointing somewhere our own n=1
experiment does not. That knowledge had nowhere to live. Without a library, the next session
either rediscovers it or, worse, keeps citing conclusions the literature has already refined.

Methodology [rule 1](../docs/methodology.md) (verify against primary sources, date every claim)
and [rule 4](../docs/methodology.md) (traceable or it's an opinion) apply to papers exactly as
they apply to source code. This is where that happens.

## Layout

| Path | What | Hand-kept? |
|---|---|---|
| `papers/_template-paper-note.md` | the paper-note template + frontmatter schema | yes |
| `papers/<citekey>.md` | one note per source read; filename stem **is** the citekey, shaped `<year>-<name>` (year first, per owner convention 2026-08-18; year = the frontmatter `year:` field) | yes |
| `cards/_template-card-note.md` | the card-note template + its **different** schema | yes |
| `cards/<citekey>.md` | one note per vendor model card read | yes |
| `index.md` | catalog of every source — papers by kind, then cards | **generated** |
| `log.md` | append-only ingest log | append-only |
| `papers/pdf/`, `cards/pdf/` | local copies of the sources | gitignored |
| [`../comparisons/benchmarks.md`](../comparisons/benchmarks.md) | characteristics of `kind: benchmark` sources | **generated** |
| [`../docs/metrics.md`](../docs/metrics.md) | metric vocabulary, each citing a ref | yes |

`index.md` and `benchmarks.md` come from `python3 scripts/build-refs-index.py`. Do not edit
them; edit a note's frontmatter and re-run. Hand-kept indexes drift, and you find out when
they're already wrong (methodology rule 3).

**PDFs are never committed.** They belong to their publishers and would bloat this history —
same treatment as `upstream/` clones. Each note carries `arxiv` or `doi`, so any copy is
refetchable:

```sh
curl -sL -o references/papers/pdf/<key>.pdf https://arxiv.org/pdf/<arxiv-id>
```

## Cards are not papers

A card note carries a different schema on purpose. `read_depth` and `kind` describe
literature; a vendor card's honesty fields are **which models it speaks for**, when the
vendor published and last revised it, when we read it, and **what snapshot backs the
quotes**:

| field | why it exists |
|---|---|
| `models_covered` | a card often covers one model and delegates sections to a parent card. Listing what THIS card speaks for is what stops a parent's figure being recorded on a child — the mistake behind the Grok 4.5 retraction (2026-08-17) and a near-miss on Gemini 3.1 Pro (2026-08-26) |
| `last_updated` | the card's own stamp. Cards are revised **in place** — "may be updated from time-to-time" is their own wording — so this is the tell that a quote may have moved |
| `snapshot` | **required**; `--check` fails without an archive URL, and refuses the live URL as its own evidence. A paper at a DOI is immutable and its PDF is disposable; a card is one mutable URL, so the snapshot *is* the record |

The distinction that decides what a delegation transfers, learned the hard way and worth
restating at every card read: delegating a **section** that happens to contain a
model-scoped figure transfers nothing; delegating **the fact's own subject** transfers the
fact.

## `read_depth` is the point

The field that makes this library trustworthy rather than decorative:

| value | means |
|---|---|
| `full` | read end to end |
| `extract` | a tool answered questions against it; nobody read the whole thing |
| `abstract` | abstract only |
| `unread` | recorded as a lead — **nothing in this repo may cite it** |

`scripts/build-refs-index.py --check` **fails** if an `unread` source is cited anywhere
outside `references/`. That is the whole guard: an abstract skim must not quietly harden into a
citation, which is exactly how a search-result summary becomes a "finding." Downgrade
`read_depth` freely; never upgrade it without doing the reading.

It mirrors `depth: stub | survey | deep-dive` on tool reports, for the same reason.

## The three operations

**Ingest** — read a source, then: write `references/<key>.md` from the template; fetch the PDF into
`pdf/`; set `bears_on` and `verdict` honestly; update any note or conclusion the source
actually touches (a source that changed nothing is an anecdote — methodology rule 6); append
one line to `log.md`; re-run the generator.

**Query** — search the notes before searching the web. If the answer required synthesis
across several notes, that synthesis is itself worth a note or a line in
[`../docs/README.md`](../docs/README.md).

**Lint** — `python3 scripts/build-refs-index.py --check`. Catches missing frontmatter, keys
that don't match filenames, unread-but-cited sources, dangling `references/<key>.md` links, and
notes with no `bears_on`. Run it before committing.

## Two deliberate deviations from the gist

- **Relative markdown links, not `[[wikilinks]]`.** The rest of the repo uses relative links
  and they render on GitHub, where wikilinks don't.
- **The index is generated, not maintained by the model.** The gist has the agent rewrite
  `index.md` on every ingest; methodology rule 3 forbids hand-kept summaries, so the catalog
  is derived from frontmatter instead. Ingest touches the *note*; the index falls out.
