# The assessment cycle

`created: 2026-09-09` · decision record: [ADR-0057](../adrs/0057-assessment-cycle-codified.md)

The loop this repo actually runs, named. [`methodology.md`](methodology.md) holds the
*rules* (each one a scar); [`tool-taxonomy.md`](tool-taxonomy.md) holds the *vocabulary*;
[`feature-taxonomy.md`](feature-taxonomy.md) holds the *instrument*. This file holds the
**cycle** those three live inside: assess a new tool with the methodology as it stands,
record the results, then reassess the methodology to absorb what the assessment taught —
as a new enum value, a new feature key, or (rarely) a new category — and close the arc
in the documentation. One turn of the cycle makes the next assessment sharper; that is
the repo's actual product loop, and every conclusion in
[`conclusions.md`](conclusions.md) came out of a turn of it.

**This file references, never copies** (rule 3's spirit applied to process): each stage
below names what it consumes, what it produces, its gate, and *where the governing text
lives*. The definitions stay with their owners. The
[`/assess-tool` skill](../.claude/skills/assess-tool/SKILL.md) is this file's executable
table of contents for a working session.

---

## The six stages

### 1. Sight

*Consumes:* a tool encountered anywhere. *Produces:* a dated row in
[`tools/candidates.md`](../tools/candidates.md).

The row is the claim: sighted and assessed, not ingested — stars hand-typed with a date
(the ledger's documented exception), an honest "why not (yet)", and **pre-read
predictions written into the row**, because stage 3's report must score them. A
candidate that never ripens costs one row; the backlog is the ledger plus GitHub
issues, never a TODO file.

*Gate:* none — sighting is free. *Governing text:* the ledger's own header
(ADR-0009/0031).

### 2. Assess — with the instrument as it stands

*Consumes:* a candidate row and a depth decision. *Produces:* a pinned clone, evidence.

- **Depth is chosen, then honored** — `stub` (mechanical facts, source unread) ·
  `survey` (used or skimmed) · `deep-dive` (the category's component decomposition
  actually traced, the report declaring which components). The honesty column's rules
  apply: downgrade freely, never upgrade without the work; closed subjects cap at
  `survey`. A candidate may go straight to deep-dive with stub facts collected en
  route (the bmad-method precedent, repeated at superpowers).
- **Ingest mechanics** live in [`CLAUDE.md`](../CLAUDE.md) § The three operations:
  clone into `upstream/`, `scripts/repo-facts.sh` for every mechanical fact, pin
  recorded with its date. Decide the pin deliberately (currency vs. coherence with a
  measured experiment; a released-branch subject pins the last release).
- **The registry is applied as-is.** Keys are set only when verified — omitted means
  not checked, `false` means checked and absent, and both are claims (rule 1b: an
  absence names the surface searched). Vocabulary is **not improvised mid-read**:
  a characteristic the registry cannot express is *collected* as a candidate for
  stage 4, not written into cells.
- **Run evidence** (rule 8): cross-check docs against source against a run. A run
  probe may be omitted **with the reason written into the `depth:` comment** — silent
  omission is not part of the pattern. When the subject ships its own acceptance
  test, that is the pre-designed live probe.

*Gate:* **owner spend sign-off before anything that costs** — API calls, live
harness sessions, experiment arms. Sign-offs arrive as short informal lines and are
quoted verbatim where the evidence lands. *Governing text:* `CLAUDE.md` § The three
operations and § The honesty columns; [`methodology.md`](methodology.md) rules 1, 1a,
1b, 4, 8.

### 3. Record

*Consumes:* the evidence. *Produces:* the report, regenerated indexes, a green battery.

The report carries dated cells citing evidence at the pin, counts that carry their
measure, and a **scored-predictions section** confronting the candidates row's own
forecasts. Promotion removes the candidates row (anything still load-bearing moves
into the report first); the category README's seed inventory gains a dated entry; the
generators re-run (`build-tool-index.py` — never hand-edit `comparisons/`); the
**six-command lint battery** (`CLAUDE.md` § Lint) runs green, and a deny-list finding
in fresh prose is fixed in the prose, never by loosening the lint.

*Gate:* the battery. *Governing text:* `CLAUDE.md` § Lint;
[`tools/_template-tool-report.md`](../tools/_template-tool-report.md).

### 4. Reassess — does what was learned fit the methodology?

*Consumes:* the read's collected candidate vocabulary and boundary strains.
*Produces:* registry changes with ADRs, or written non-admissions.

Three admission paths, in increasing weight, each with its existing owner:

- **A new enum value on an existing key** — one verified instance suffices (the rule
  binds keys, not values), backed by a dated ADR.
  Owner: [`feature-taxonomy.md`](feature-taxonomy.md) § the registry contract;
  precedent ADR-0052–0056.
- **A new feature key** — two verified instances (issue #2's rule), admitted in
  `feature-taxonomy.yaml` and nowhere else; the new-field checklist (generator,
  matrix, build-db) applies.
- **A new category, or a boundary change** — triggered by the stress test ("if a new
  case has no defensible home, the taxonomy needs revision — not the case"), settled
  by owner-gated discussion argued from the record, and recorded in an ADR always.
  Owner: [`tool-taxonomy.md`](tool-taxonomy.md) § Stress test;
  [`adrs/README.md`](../adrs/README.md) for what an ADR is.
- **Drift vocabulary** surfaced by the read grows the deny-list by
  `tool-taxonomy.md`'s own procedure (decide it is drift first; never loosen).

**Non-admissions are findings too**: a candidate key that fails the two-instance bar,
or fails on the merits, is written down with its trigger for re-check — argued from
the record, not dropped.

*Gate:* the owner, explicitly, for every taxonomy change; ADRs only on explicit go.
*Governing text:* as linked per path.

### 5. Promote

*Consumes:* the report's findings. *Produces:* conclusions and confronted principles.

- **Rule 6's path**, walked, not skipped: run log → report/category note (dated) →
  [`conclusions.md`](conclusions.md). A finding that changed no note is an anecdote.
- **Before minting or amending a conclusion**: re-derive any advertised count from
  the reports' own frontmatter and text — never from a summary, including your own
  (two same-day corrections, 2026-08-27 and 2026-09-09, exist because this step was
  almost skipped). Decide amend-vs-mint: a conclusion that already accretes instances
  ("shapes") takes the new one as a dated amendment; only a genuinely uncovered claim
  gets a new number. Non-adopters and counterexamples go *inside* the conclusion,
  explained. Headlines mirror verbatim into `README.md`'s index.
- **[`design-principles.md`](design-principles.md) is confronted** per its own
  revision rule: confirm, contradict, or note silence for every relevant principle,
  dated — a deep-dive that skips this owes the constitution a debt.
- **Standing bets** tracked in issues get dated data points when the read moves them.

*Gate:* the owner's, for minting new conclusion numbers. *Governing text:*
`methodology.md` rule 6; `design-principles.md` header; `conclusions.md` header.

### 6. Close the arc

*Consumes:* everything above. *Produces:* a clean, shipped, re-entrant state.

- **Documentation checkpoint**: sweep for cross-references the new findings made
  stale (counts, "N deep-dives", section titles cited elsewhere — a rename requires
  a repo-wide link sweep).
- **Park the follow-ups**: 1–3 strongest next moves proposed; the rest become GitHub
  issues, including **re-read triggers** (a release tag for high-velocity subjects,
  a date for scored predictions).
- Commit straight to `main`, push. Dates verified against `date -u` before stamping.

*Gate:* none new — the battery already ran. *Governing text:* `CLAUDE.md`
§ Conventions.

---

## What this file is not

- **Not a tenth methodology rule.** The rules are scars, each earned by a specific
  failure; this file is the loop those rules live inside, and it adds no new
  obligation — every gate cited above already existed where its owner defines it.
- **Not the owner of any definition.** If this file and a governing document ever
  disagree, the governing document wins and this file gets fixed.
- **Not automation.** The [`/assess-tool` skill](../.claude/skills/assess-tool/SKILL.md)
  that walks a session through these stages is a guided runbook — the judgment calls
  (depth, pin, admission, minting) stay human-gated on purpose.
