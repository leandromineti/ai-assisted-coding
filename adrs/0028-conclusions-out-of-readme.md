# ADR-0028 — The Conclusions move to `docs/conclusions.md`; README keeps the headlines

`decided: 2026-08-26` · status: **accepted**

## Decision

The numbered Conclusions leave `README.md` for **`docs/conclusions.md`**, text unchanged.
`README.md` keeps a **headline index** — one line per conclusion (number, claim, date) —
above a link to the full file. The numbers stay the citation keys they already were:
prose across the repo says "conclusion N", never a path.

`docs/` was chartered two decisions earlier as everything that is not a tool report, a
source note, or an experiment (ADR-0025/0026), so this needs no new directory. In
`docs/README.md` the conclusions sit in their own section between the constitution and
the cross-category notes: they are not a note *about* the survey, they are what it
concluded.

## Why

Owner request (2026-08-26): the Conclusions were lines 99–417 of a 421-line README —
**76% of the front page** — and the README had become unreadable as an introduction to
the repo.

The counter-argument, stated for the record because it is the same argument that drove
ADR-0026 and 0027 hours earlier: `README.md` is the one surface GitHub guarantees a
visitor sees, and this repo's actual output belongs there. The headline index is what
answers it — the front page still shows all fourteen claims and their dates, in less
than a screen, and the evidence links are one click away. What moved is the 300 lines of
supporting citation, not the findings.

An alternative — rename `articles/` to `results/` and file the conclusions there — was
considered the same day and rejected: "results" is already load-bearing vocabulary for
what an experiment appends below its preregistered protocol (methodology rule 5, and
`taxonomy.yaml`'s append-only exempt paths), and `articles/` is a drafting bench with a
publish-outward workflow, not a results directory. Same failure mode as the rejected
`constitution/` in ADR-0026: a directory name that misdescribes its contents on day one.

## The decoder

Anything dated **on or before 2026-08-26** cites the conclusions as living in
`README.md` — as `README.md#conclusions`, "README conclusions 11–12", or "`README.md`
Conclusions". All map to `docs/conclusions.md`. **Conclusion numbers are unchanged**, so
"conclusion 7" means what it always meant; only the container moved. Chains with the
ADR-0024–0027 decoders.

## Boundary

Same as 0024–0027: living docs, `scripts/`, and citing prose are rewritten; **ADR bodies
and preregistered experiment protocols keep their period paths** and read under the
decoder above (`adrs/0004` and `adrs/0007` both say "README conclusions" and stay as
written).

Two mechanical notes for the next person who moves a claims file:

- The move was **verbatim** — conclusions are dated claims, so their text was carried
  across untouched, with only the outbound links re-expressed for the new depth
  (`tools/…` → `../tools/…`, `docs/x` → `x`), exactly as ADR-0026 treated the
  constitution. Per-conclusion heading anchors were considered and rejected for the same
  reason: they would have meant rewriting fourteen dated claims' formatting to gain
  anchors nothing currently cites (all four existing citations pointed at the section,
  not the item).
- Extracting the headline index by regex mis-parsed conclusion 9, whose date
  parenthetical contains a markdown link — the inner `)` closed the match early and
  truncated the line. Hand-repaired. A bold-and-parenthetical opener is not safely
  machine-extractable; check every line of a generated index against its source.
