# ADR-0043 — § Vendor span becomes § Maker span; negative claims get a rule (1b)

`decided: 2026-08-26` · status: **accepted**

## Decision

Two changes, one cause.

1. **`docs/tool-taxonomy.md` § *Vendor span* is renamed § *Maker span***, and "vendor span"
   becomes "maker span" wherever the repo names the concept. This **supersedes the
   section-name clause of [ADR-0042](0042-vendor-becomes-maker.md)**, which renamed the
   frontmatter field `vendor:` → `maker:` but deliberately kept the narrower word for this
   section. The rest of ADR-0042 stands.
2. **Methodology gains rule 1b — "a negative claim needs a surface that could have shown
   the thing."** A sibling to 1a: 1a governs how to grade what you *find* about a closed
   subject, 1b how to claim you found *nothing*.

## Why the section renames

ADR-0042's reasoning was that every row in the table is a company, so *vendor* was the
precise word and *vendor span* was "the subset of maker span with a business behind it".
That distinction was real but it was not doing any work: the section has exactly one table,
every entry in it is a maker, and no passage anywhere needed the narrower set. What the
split actually produced was a field called `maker:` feeding a section called *Vendor span* —
two words for one relation, which is the collision ADR-0042 spent its length avoiding, just
moved one level up. One word, applied consistently, is worth more than a distinction with
no consumer. Owner decision, 2026-08-26.

## Why rule 1b

The same section was **wrong three times in one day**, each time by the same method.

| claim | basis | reality |
|---|---|---|
| six of eight makers ship a harness | no report in `tools/` | Moonshot's `kimi-code` had shipped 2026-05-22 |
| seven of eight; Z.ai "a strategy, not a gap" | a **GitHub org search** | ZCode exists — closed, proprietary, never on GitHub |
| eight of eight | the makers' own sites | holds |

Both bad claims inferred absence from a surface that **structurally cannot represent the
thing**: `tools/` holds only what someone has already ingested, a repository host holds only
what is open source. This is precisely the blind spot
[ADR-0041](0041-vendors-matrix-removed.md) had deleted an entire generated matrix over an
hour earlier — the tracked-only floor understating span exactly where span is greatest — and
this section reproduced it in prose within the hour, then again fifteen minutes later.

The repo's anti-goal section says a rule joins the methodology only when its absence caused
a real mistake. Three same-day scars, all recorded, is the strongest case any rule in that
file has had.

Rule 1b's operative content: before asserting an absence about a maker's product line,
search **the maker's own site**; where an absence survives, record where you looked and
when, so the next reader sees the shape of the hole rather than inheriting the conclusion.

## Consequences

- The 8/8 finding is promoted to **conclusion 16** — it clears rule 6 (every row links to a
  note: two candidate rows, `claude-code.md`, § Maker span). Its falsifier is inverted on
  the way in: the model→harness direction is saturated and can no longer surprise, so the
  live claim is its converse — a *harness* maker with no model training or branding one.
- § Maker span keeps the three wrong versions as a worked example rather than overwriting
  them. The failure repeated *after* the lesson was written, twice, which is the part worth
  preserving; a clean final number would hide exactly what rule 1b exists to teach.
- ADR-0042's index status becomes "section-name clause superseded by 0043", following the
  ADR-0037 precedent for a partially-superseded record. Its field rename, its rejection of
  `provider`, and its `references/cards/` carve-out are untouched.
- Two stale references surfaced while sweeping and are fixed: `README.md` still listed
  `vendors` among the generated matrices (removed in ADR-0041) and still called the
  distinction "bleed/vendor-span".
