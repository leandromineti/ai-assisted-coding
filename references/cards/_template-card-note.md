---
key: <citekey, shaped <year>-<slug> — MUST equal this file's name without .md>
vendor: <who publishes the card>
title: "<the card's own title, quoted>"
# models_covered is the field that stops the family-inheritance mistake: a card often
# covers ONE model and delegates sections to a parent card. List exactly what THIS card
# speaks for, in the vendor's own naming.
models_covered: [<Model Name>]
published: <YYYY-MM or YYYY-MM-DD, as the card states it>
last_updated: <the card's own "Last Updated" stamp — a card is revised in place>
retrieved: <YYYY-MM-DD this copy was fetched and read>
url: <the live card URL — mutable; not evidence on its own>
# snapshot is REQUIRED (--check fails without an archive URL). The live URL serves
# whatever version is current, so a quote below is only re-checkable against a snapshot.
snapshot: <https://web.archive.org/web/<timestamp>/<url>>
pdf: <references/cards/pdf/<key>.pdf if cached locally — gitignored, convenience only>
# bears_on: what in THIS repo the card touches — report slugs, feature keys, conclusions.
bears_on: [<slug>]
---

# <Card title>

## What it covers, and what it delegates

<Which sections speak for the models above, and which point at another card. This is the
load-bearing part: a card that delegates a SECTION containing a model-scoped figure
transfers nothing; a card that delegates the FACT'S OWN SUBJECT transfers the fact.>

## Quoted passages

> <verbatim, with the section it came from>

<Why this repo depends on it, and which report or field consumes it.>

## Open questions

<What the card does not answer, and where that answer might live.>
