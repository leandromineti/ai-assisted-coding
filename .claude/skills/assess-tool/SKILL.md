---
name: assess-tool
description: Guided runbook for one turn of this repo's assessment cycle — sighting, ingesting, and reporting a new tool, then reassessing the methodology and closing the arc. Use when asked to assess, ingest, survey, or deep-dive a tool, or to promote a candidate from the ledger.
---

# /assess-tool — one turn of the assessment cycle

This skill is the executable table of contents for
[`docs/assessment-cycle.md`](../../../docs/assessment-cycle.md) — read the stage
there before executing it here. This file owns sequencing and stop points only;
every definition lives with its owner. If they disagree, the docs win.

**Standing rules for the whole run:** verify the working date with `date -u` before
stamping anything; every count carries its measure; absences name the surface
searched; commits go straight to `main` after a green battery.

## Phase 0 — orient

- [ ] Identify the tool, its likely category (`docs/tool-taxonomy.md`), and whether a
      candidates row already exists (`tools/candidates.md`).
- [ ] Decide target depth (stub / survey / deep-dive) per `CLAUDE.md` § The honesty
      columns. Deep-dive requires tracing the category's declared components.

## Phase 1 — sight (skip if promoting an existing row)

- [ ] Write the dated candidates row: hand-typed stars with date, "why not (yet)",
      and pre-read predictions the report will score.
- **Done-check:** row reads honestly without the tool's marketing voice.

## Phase 2 — assess

- [ ] Add to `upstream/repos.txt`, run `scripts/sync-upstream.sh`, then
      `scripts/repo-facts.sh <name>` — never hand-type mechanical facts.
- [ ] Decide and record the pin deliberately (check the branch model:
      `git rev-list --left-right --count origin/main...origin/dev`-style before
      trusting freshness).
- [ ] **Deep-dive dispatch shape:** ~3 parallel reader subagents, one per category
      component, briefs carrying: exact clone path + pin, READ-ONLY, file:line
      citations mandatory, counts with measures, absences with searched surfaces,
      quote load-bearing text verbatim, surprises section, and the repo's sharpest
      current question for that component. Spot-verify load-bearing claims in the
      main session before writing anything.
- [ ] Run evidence (rule 8): run probe, or omit-with-reason in the `depth:` comment.
- **STOP — owner gate:** anything that spends (API calls, live sessions, experiment
  arms) waits for an explicit sign-off line; quote it verbatim where the evidence
  lands.

## Phase 3 — record

- [ ] Report from `tools/_template-tool-report.md` (category 1 uses the model
      template); registry keys only where verified; scored-predictions section
      confronting the candidates row.
- [ ] Promotion bookkeeping: remove the candidates row, add the category README seed
      entry, re-run `python3 scripts/build-tool-index.py`.
- [ ] Six-command battery (`CLAUDE.md` § Lint) — fix deny-list findings in the
      prose, never in the lint.
- **Done-check:** battery green; every citation spot-checked; commit + push.

## Phase 4 — reassess the methodology

- [ ] Walk the read's collected candidate vocabulary through the three admission
      paths (enum value: 1 instance + ADR · key: 2 instances, registry-only ·
      category/boundary: stress test + discussion + ADR) —
      `docs/assessment-cycle.md` § 4 links each owner.
- [ ] Write non-admissions down with their re-check trigger.
- **STOP — owner gate:** every taxonomy change is argued from the record and decided
  by the owner; ADRs only on explicit go.

## Phase 5 — promote

- [ ] Rule 6's path: report → category note → `docs/conclusions.md`. Re-derive every
      advertised count from frontmatter/text before writing it. Amend an accreting
      thread vs. mint a new number; mirror headlines into `README.md`.
- [ ] Confront `docs/design-principles.md` per its revision rule — confirm /
      contradict / note silence, dated, for every relevant principle. This is owed,
      not optional.
- [ ] Drop dated data points on any standing issue-tracked bets the read moved.
- **STOP — owner gate:** minting a new conclusion number.

## Phase 6 — close the arc

- [ ] Stale-reference sweep (counts, titles cited elsewhere, "N deep-dives" phrasing).
- [ ] Park follow-ups + re-read triggers (next release tag; dated predictions) as
      GitHub issues; propose the 1–3 strongest next moves.
- [ ] Final commit + push; update session memories with *craft* learned (process
      changes belong in `docs/assessment-cycle.md`, not memory).
