# ADR-0034 — `refs/` becomes `references/`, split into `papers/` and `cards/`

`decided: 2026-08-26` · status: **accepted**

## Decision

`refs/` is renamed **`references/`** and gains two halves:

- **`references/papers/`** — the existing library, unchanged: 22 notes, the paper template
  (renamed `_template-paper-note.md`), and the gitignored `pdf/` cache.
- **`references/cards/`** — a new kind of source: **vendor model cards**, one note each,
  with their own template, their own schema, and their own `pdf/`.

`README.md`, the generated `index.md`, and `log.md` stay at `references/` root. The index
now renders both halves — papers by kind, then a cards table.

**The card schema is deliberately not the paper schema.** `kind` and `read_depth` describe
literature. A card's honesty fields are:

| field | why |
|---|---|
| `models_covered` | a card often speaks for one model and delegates sections to a parent card; listing what THIS card covers is what stops a parent's figure being recorded on a child |
| `published` / `last_updated` | the card's own stamps — cards are revised **in place** ("may be updated from time-to-time", their wording) |
| `retrieved` | when this repo read it |
| **`snapshot`** | **required**. `--check` fails when it is missing, and refuses the live URL as its own evidence |

`--check` now reports `N papers + M cards`. Cards are exempt from the
`read_depth`/`unread`-may-not-be-cited machinery, which is about depth of reading
literature and has no card analogue.

## Why

The Gemini work created a second class of primary source. `gemini-3-1-pro.md`'s knowledge
cutoff now rests on two model cards, and quoting them inline left three problems: the
quotes were not citable, the cards were not dated as sources, and — the real one — **a
card is rewritten in place at a single URL**, so an inline quote against a live link is
not re-checkable. The 3 Pro card is stamped "Last Updated: May 2026"; whatever it says
tomorrow is what that URL will serve.

That is also why `snapshot` is required rather than encouraged, and why the PDFs stay
gitignored. For a paper the gitignore reason is "refetchable from arxiv/doi" — true, and
the PDF is disposable. For a card that reason is false, so the durable artifact is the
archive URL, not a local copy that a server rebuild deletes (as one did on 2026-08-06).
The note plus its snapshot is the record; the cached PDF is convenience.

Filing cards in `papers/` was rejected: it would have meant either bending `read_depth`
and `kind` to fit vendor documentation, or a library where half the entries leave the
honesty columns blank.

## The decoder

Anything dated **on or before 2026-08-26** cites source notes as `refs/<key>.md` — map to
**`references/papers/<key>.md`**. Bare `refs/` maps to `references/`; `refs/pdf/` to
`references/papers/pdf/`; `refs/_template-ref-note.md` to
`references/papers/_template-paper-note.md`. `refs/README.md`, `refs/index.md`, and
`refs/log.md` keep their names one level up. Chains with the ADR-0024–0030 decoders.

## Boundary

Same as 0024–0030: living docs, `adrs/README.md`, `scripts/`, `.gitignore`,
`exempt_paths`, and generated files are rewritten or regenerated; **ADR bodies and
preregistered experiment protocols keep their period paths**. Two `adrs/README.md` index
rows were restored to period naming by hand after the sweep rewrote them — ADR-0022's
("repo-voice prose in `refs/`") and ADR-0027's (`refs/index.md` as the generated-listing
example) — the same trap ADR-0030 recorded: a sweep must not rewrite text that quotes old
paths on purpose.

One generator subtlety worth recording, because it would have failed silently: the
dangling-link scan splits on a literal prefix, and the notes now live one level deeper. Had
it kept splitting on `references/`, every citation token would have read `papers/<key>` and
been discarded by the existing "contains a slash" guard — the check would have passed while
verifying nothing. It now scans `references/papers/` and `references/cards/` separately,
each against its own key set.

Verified by three negative tests, restored after each: a card note missing `snapshot` →
exit 1; a card whose `snapshot` is the live URL → exit 1 naming why a live URL is not
evidence; and (from the earlier ADR-0032/0033 pattern) the generator's own regeneration
after restore, clean.
