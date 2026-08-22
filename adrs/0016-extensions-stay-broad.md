# ADR-0016 — Extensions stay broad: memory is a type, not the category

`decided: 2026-08-19` · `recorded: 2026-08-19` · status: **superseded by
[ADR-0020](0020-memory-category-extensions-renumbered.md) (2026-08-22)**

## Decision

Category 5 (Extensions) keeps its full seven-type scope. A proposed narrowing — reduce
the bucket to memory tools, move the non-memory reports into `notes/cross-cutting/` —
is rejected. Memory remains one `type:` among seven
(`mcp-server · skill · hook · subagent-def · rules-file · config-pack · memory`).

## The considered change and why it was plausible

At decision time, 7 of the bucket's 8 reports carry `type: memory` (ai-memory, mem0,
memos, cognee, everos, memmachine, memori); the eighth (ECC) carried no `type:` at all.
The generated supply table read `memory · 7 tracked` against `0 tracked` for every other
type. On the sample alone, "this is really the memory category" is a fair reading.

## Why it does not execute

1. **The concentration is a sampling artifact with a written cause.** All seven memory
   reports were seeded on one day (2026-08-18) by the deliberate, now-closed memory-type
   reading arc — issue #18 holds the seeding and the reading plan. The other types'
   `0 tracked` is not-checked, not checked-absent: `notes/candidates.md` has no category-5
   section of any type. A category boundary should not be redrawn to fit one arc's sample.
2. **Cross-cutting cannot receive tool reports.** Its own charter: "These are **not
   categories**… findings that span categories" — and the recorded entry test
   (`notes/cross-cutting/standards.md`): *can you install it? If yes, it's a category
   entry.* The one non-memory report, ECC, is installable (23 documented invocations,
   ~13 targets, deep-dived). There is no defensible cross-cutting home for it.
3. **The demand side names six of the seven types.** The feature registry's `kind_link`
   entries tie category-2 features to category-5 artifact types — `mcp` → `mcp-server`,
   `hooks`/`turn_end_gates`/`measured_gates` → `hook`, `skills` → `skill`,
   `subagents` → `subagent-def`, `rules_files` → `rules-file`, `learning_loop` →
   `memory`. Narrowing the supply side to memory would orphan five live demand links.
4. **The narrowing question already has a recorded decision point.** The standards
   scoreboard's ~2027-01 re-check is the dated trigger: if hooks stay harness-specific
   and skills stall at convention level, "category 5 is really 'MCP plus a pile of
   vendor features,' and the taxonomy should say so" — and ADR-0002 records the reverse
   trigger (re-promotion to a full category if formats standardize). Deciding now, on
   arc-biased evidence, would preempt both arms.
5. **The registry's trajectory points the other way.** ADR-0013 set the precedent that
   per-type feature blocks (memory first, hooks/skills when their instance bars are met)
   are how the bucket grows structure — types thicken inside category 5; they do not
   secede from it.

## Consequences

- ECC gains `type: config-pack` in frontmatter — the classification its deep-dive already
  made in prose ("a config pack at scale"), and the first use of that vocabulary value.
  Every report in the bucket now carries the `type:` key the index says they carry. Note
  the demand↔supply table is deliberately unaffected: `config-pack` has no `kind_link`
  (it bundles the other types), so this is consistency, not a supply-count change.
- The category index gains a dated coverage note naming the memory concentration as an
  arc artifact, pointing here.
- A balance arc issue (modeled on issue #18) opens for sighting non-memory candidates
  into `notes/candidates.md`, so the ~2027-01 re-check can judge the bucket on a sample
  that was allowed to be broad.

Reopen triggers: the ~2027-01 standards re-check (either arm), or the balance arc
closing with the non-memory types still empty — at which point the narrowing question
returns with a fair sample behind it.
