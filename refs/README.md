# `refs/` — the citation library

`created: 2026-07-31`

One note per source we've read and found relevant, so that what the literature already knows
compounds instead of living in a chat transcript. Adapted from
[Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
immutable sources, a generated wiki over them, and a schema document
([`../CLAUDE.md`](../CLAUDE.md)) that tells an agent how to maintain both.

## Why it exists

On 2026-07-31 a single afternoon's search turned up two papers that bear directly on this
repo's published conclusions — one of them a 128-run ablation pointing somewhere our own n=1
experiment does not. That knowledge had nowhere to live. Without a library, the next session
either rediscovers it or, worse, keeps citing conclusions the literature has already refined.

Methodology [rule 1](../methodology.md) (verify against primary sources, date every claim)
and [rule 4](../methodology.md) (traceable or it's an opinion) apply to papers exactly as
they apply to source code. This is where that happens.

## Layout

| Path | What | Hand-kept? |
|---|---|---|
| `_template-ref-note.md` | the note template + frontmatter schema | yes |
| `<citekey>.md` | one note per source; filename stem **is** the citekey, shaped `<year>-<name>` (year first, per owner convention 2026-08-18; year = the frontmatter `year:` field) | yes |
| `index.md` | catalog of every source, grouped by kind | **generated** |
| `log.md` | append-only ingest log | append-only |
| `pdf/` | local copies of the sources | gitignored |
| [`../comparisons/benchmarks.md`](../comparisons/benchmarks.md) | characteristics of `kind: benchmark` sources | **generated** |
| [`../notes/cross-cutting/metrics.md`](../notes/cross-cutting/metrics.md) | metric vocabulary, each citing a ref | yes |

`index.md` and `benchmarks.md` come from `python3 scripts/build-refs-index.py`. Do not edit
them; edit a note's frontmatter and re-run. Hand-kept indexes drift, and you find out when
they're already wrong (methodology rule 3).

**PDFs are never committed.** They belong to their publishers and would bloat this history —
same treatment as `upstream/` clones. Each note carries `arxiv` or `doi`, so any copy is
refetchable:

```sh
curl -sL -o refs/pdf/<key>.pdf https://arxiv.org/pdf/<arxiv-id>
```

## `read_depth` is the point

The field that makes this library trustworthy rather than decorative:

| value | means |
|---|---|
| `full` | read end to end |
| `extract` | a tool answered questions against it; nobody read the whole thing |
| `abstract` | abstract only |
| `unread` | recorded as a lead — **nothing in this repo may cite it** |

`scripts/build-refs-index.py --check` **fails** if an `unread` source is cited anywhere
outside `refs/`. That is the whole guard: an abstract skim must not quietly harden into a
citation, which is exactly how a search-result summary becomes a "finding." Downgrade
`read_depth` freely; never upgrade it without doing the reading.

It mirrors `depth: stub | survey | deep-dive` on tool reports, for the same reason.

## The three operations

**Ingest** — read a source, then: write `refs/<key>.md` from the template; fetch the PDF into
`pdf/`; set `bears_on` and `verdict` honestly; update any note or conclusion the source
actually touches (a source that changed nothing is an anecdote — methodology rule 6); append
one line to `log.md`; re-run the generator.

**Query** — search the notes before searching the web. If the answer required synthesis
across several notes, that synthesis is itself worth a note or a line in
[`../notes/cross-cutting/index.md`](../notes/cross-cutting/index.md).

**Lint** — `python3 scripts/build-refs-index.py --check`. Catches missing frontmatter, keys
that don't match filenames, unread-but-cited sources, dangling `refs/<key>.md` links, and
notes with no `bears_on`. Run it before committing.

## Two deliberate deviations from the gist

- **Relative markdown links, not `[[wikilinks]]`.** The rest of the repo uses relative links
  and they render on GitHub, where wikilinks don't.
- **The index is generated, not maintained by the model.** The gist has the agent rewrite
  `index.md` on every ingest; methodology rule 3 forbids hand-kept summaries, so the catalog
  is derived from frontmatter instead. Ingest touches the *note*; the index falls out.
