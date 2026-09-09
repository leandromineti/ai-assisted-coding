# ADR-0057 — the assessment cycle codified as a doc plus a project skill

`decided: 2026-09-09` · `status: accepted`

## Decision

The loop the repo runs in practice — assess a new tool with the methodology as it
stands → record → reassess the methodology to absorb what was learned (new enum
value · new feature key · new category) → close the arc in the documentation — is
named and written down in one hand-kept file, [`docs/assessment-cycle.md`](../docs/assessment-cycle.md),
and operationalized as a committed project skill,
[`.claude/skills/assess-tool/SKILL.md`](../.claude/skills/assess-tool/SKILL.md), a
guided runbook (owner decision: **not** an orchestrator — depth, pin, admission, and
minting decisions stay human-gated).

Two subsidiary decisions:

- **The skill is committed, not gitignored.** `.claude/skills/` is versioned,
  public-facing repo content — the executable face of the cycle doc, evolving with
  it through git history. Only runtime/local state under `.claude/` is ignored
  (`scheduled_tasks.lock`, `settings.local.json`).
- **The doc references, never copies.** Every stage links its governing text
  (methodology rules, taxonomy stress test, feature-registry admission bars,
  design-principles revision rule); if the cycle doc and an owner document disagree,
  the owner wins and the cycle doc is fixed.

## Why now

The cycle had run implicitly for six weeks, its fragments split across
`CLAUDE.md`'s three operations, the honesty columns, rule 6's promotion path, the
registry's admission rules, and session memories that no repo reader can see. The
2026-09-09 superpowers arc executed every stage end to end in one day
(candidate row → same-day deep-dive at pin b36e082 → report + registry cells →
conclusion 25 minted with its count re-derived and corrected → conclusion 7's fourth
shape → design-principles confronted per its own revision rule → follow-ups parked
as issue #48; commits `fa0d076` → `20ed0a3`), and the owner named the pattern and
asked for it to be materialized. That arc is the worked example the doc distills.

## What this does NOT change

No methodology rule is added or reworded; no admission bar moves (enum value: one
verified instance; key: two; category: stress test + ADR); no gate changes owner.
The doc and skill are a map of existing territory. A future change to any governed
stage happens in the governing document, with its own ADR where structural.
