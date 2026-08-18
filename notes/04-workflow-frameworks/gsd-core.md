---
name: gsd-core
layer: 4
vendor: Open GSD
url: https://github.com/open-gsd/gsd-core
license: MIT
open_source: true
stack: [Markdown, Node]
version: v1.8.0-102-gd04592de
commit: d04592de
first_commit: 2025-12-14
stars: 7336
stars_at: 2026-07-28
read_at: 2026-07-28   # drift-checked 2026-08-16 (rule 4b) — see the drift-check section; pin deliberately not moved
depth: survey   # full flow run end-to-end (experiments/01-gsd-vs-plain) + core workflow prose read; gsd-tools.cjs internals unread
harness_targets: [Claude Code, Codex, Gemini CLI, Cursor, Windsurf, Copilot]
workflow_features:   # added 2026-08-18 from the survey read + exp-01 run
  intent_pipeline: true          # structured task graphs from requirements
  deterministic_engine: true     # gsd-tools.cjs bookkeeping (existence verified; internals unread)
  measured_gates: true           # <verify> gates with measured expected values
  process_gates: true            # mode ceremonies, approval points (exp-01: near-zero observed value)
  context_isolation: true        # clean execution contexts per unit — the founding principle
  state_store: repo-files        # planning artifacts committed to the repo
---

# GSD — gsd-core

An *operating loop* for agentic engineering work; its stated enemy is context bloat and
scope drift. Three principles: explicit plans as **structured task graphs**, **clean
execution contexts** per unit of work, and **real verification** producing human-readable
evidence.

Installs into Claude Code, Codex, Gemini CLI, Cursor, Windsurf, and Copilot. Ships
alongside `gsd-pi` (standalone CLI), `gsd-browser` (deterministic Chrome control), and
announced-but-unshipped `gsd-workbench` and `gsd-cloud`.

**Already installed on this machine**, so source claims can be cross-checked against
observed behavior — the only tool in the set where that's possible.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

207 commits / 1045 files since the read, and this is the **weakest verdict in the sweep**
— not because the report is wrong, but because it cites almost nothing checkable. Its only
file references are `docs/ARCHITECTURE.md` and an index link, so rule 4b's "does the drift
touch what the report claims?" has almost no surface to test against. Recorded as the
honest state rather than dressed up.

What could be checked:

- **`gsd-pi` is not in this repo's tree at either end** — and that is *correct*, not a
  finding. It is a separately distributed CLI, which is what "standalone" in the bleed
  section means. Verified before writing, because "the escape-hatch CLI has vanished" would
  have been a conclusion-7-sized claim built on a bad grep.
- **Version moved `1.8.0` → `1.9.1`** (`.claude-plugin/plugin.json`), a minor bump.
- **Multi-harness support is still being actively worked**, judging by archived changesets
  in the drift (`codex-install-skill-surface`, `codex-install-bundled-hooks-blocker`,
  `codex-adapter-text-mode-fallback`) — consistent with the `harness_targets` claim, though
  not a verification of it.

**The methodological finding is the useful one: a survey that cites no source files cannot
be drift-checked.** Rule 4b's cheap test runs off the report's own citations, so a report
with none forces the expensive option (a re-read) or no answer at all. That is an argument
for citing files even at `survey` depth — a citation is what makes a claim *re-checkable*
later, not just traceable now. gsd-core and spec-kit are already queued for re-reads on
issue #9; this one genuinely needs it, where spec-kit's turned out not to.

## Provenance — a fork born from a vanished maintainer

`checked: 2026-07-28`

`open-gsd/gsd-core` is a **community fork** of the original
[`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) ("Get Shit Done"
by TÂCHES, created 2025-12-14). Per the fork announcement
([discussion #109](https://github.com/open-gsd/gsd-core/discussions/109)) and the GitHub
API (both checked 2026-07-28):

- The original maintainer went silent **2026-04-01**; their social accounts were deleted
  or unreachable, and the associated `$GSD` crypto token was publicly linked to a
  rug-pull. The announcement is explicit that whether this was the maintainer's action,
  a co-founder exit, or an account takeover is **unconfirmed**.
- trek-e completed the fork **2026-05-22** (matches the new repo's `created_at`),
  migrating 394 branches, 229 tags, 84 labels, 77 open issues, and 17 PRs. The original
  repo is now archived (last push 2026-05-31).
- Renames along the way: npm package `get-shit-done-cc` → `get-shit-done-redux` →
  `gsd-core`; the brand quietly became "**Git. Ship. Done**"; token and
  `@gsd_foundation` references were stripped. MIT license unchanged.

Two consequences for this repo's index columns: `first_commit: 2025-12-14` **is** the
product's true start (the history migrated intact), but `stars: 7,336` measures only the
fork era — the original carries **64,799 stars**, stranded on the archive. GSD's actual
reach is closer to the old number; the two can't be added (overlapping audiences).

It's also the set's live example of **layer-4 supply-chain risk**: this is a tool that
injects prose and hooks into your harness, whose upstream went dark in ambiguous
circumstances — the fork itself states it cannot verify upstream security and forked
precisely for that reason. "Who maintains the methodology you install" is a real
question, not a hypothetical.

## The distinguishing bet

That agents fail from **context mismanagement**, not insufficient intelligence — so the
leverage is in giving each unit of work a clean, right-sized context and verifying the
result with evidence. Compare spec-kit, which shares the diagnosis but locates the failure
in under-specified intent.

## Main features

Observed in a full run (new-project → plan → execute → verify ×2 phases; see
[`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md)):

- **A refinement funnel, not a pipeline.** Research → requirements → phase-research →
  plan → check → execute → verify, where each stage catches what the previous left
  vague. Observed concretely: pitfalls research became four checkable requirements; the
  phase researcher caught an underspecified exit code in those requirements; the checker
  caught an untested claim in the plan; the executor closed it.
- **Empirical research agents** — the standout feature. GSD's researchers and planner
  *measured* git behavior (fixture repos, `git hash-object` crafted commits, timezone
  probes) instead of trusting training data. Nearly all observed quality delta traces
  to this.
- **Plans as runnable contracts**: tasks carry `<read_first>`, `<acceptance_criteria>`,
  and `<verify>` gates with *measured* expected values; the planner dry-runs its own
  gates before committing.
- **Honest verification**: verifiers re-derive claims against real runs, exceed their
  brief (ambient-config attack re-runs), and *abstain* on subjective checks
  (`human_needed`) rather than auto-passing.
- **Deterministic bookkeeping** via `gsd-tools.cjs` (init queries, commits, state) —
  real code where prompt ceremony was expected.
- **Self-healing prose**: workflows encode defenses against known LLM failure modes
  (e.g. the #222 false-refusal recovery for the synthesizer).

## Stack & repo shape

**Majority markdown: 1398 `.md` against 810 `.cjs`** across 2636 tracked files. This is the
single most informative fact in the bootstrap pass — a layer-4 framework is mostly *prose*,
because the methodology is the product and the code is delivery machinery. Runtime is
CommonJS Node (`.cjs` plus 177 `.cts`).

`docs/ARCHITECTURE.md` exists, and is translated into ja-JP, ko-KR, and pt-BR — a
localization investment nothing else in the set makes.

4788 commits since **2025-12-14** — barely seven months old, the youngest project here by
first-commit date, at roughly 680 commits/month.

## Architecture

_TODO — source unread. `docs/ARCHITECTURE.md` is the way in. The interesting question for a
prose-dominant tool is how the markdown is structured, versioned, and targeted at multiple
harnesses._

## Bleed

Reaches **down into layer 2** via `gsd-pi`, its own standalone CLI, and into **layer 5** via
`gsd-browser`. Documented in [`index.md`](index.md) — it's the clearest case in the repo of a
workflow framework growing into the runtime it was meant to sit on top of.

## Cost model

Free and open source (MIT). Inference cost is whatever your harness charges — though the
structured-task-graph approach implies more model calls per unit of work, which is a cost
question worth measuring.

## Surprises

1. **The markdown-to-code ratio.** 1398 `.md` vs 810 `.cjs` is close to a proof of the
   layer-4 definition: if the artifact is mostly prose, the thing being distributed
   really is a methodology rather than a program. Recorded before reading a line of
   source.
2. **The value concentrates in two places** (from the experiment): empirical research
   agents and measured verification gates. The surrounding process ceremony — STRIDE
   threat model for a read-only local CLI, three enterprise-shaped hooks seeded on by
   default for a 200-line project, ROADMAP checkboxes the framework itself forgot to
   tick in both phases — produced almost none of the observed quality delta.
3. **Ceremony cost is front-loaded and enormous on small tasks:** first product code at
   minute 40; ~1.47M subagent tokens and ~3,750 planning-doc lines for 763 product LOC.
   Yet the result genuinely was more robust — a real crash-class difference plus four
   latent-defect classes over the unstructured baseline (see the experiment's results).
4. **Cross-layer frictions observed live:** a harness subagent guard (Write refusing
   "report files") collided with the framework's file-on-disk requirement — the agent
   self-healed via Bash heredoc; and a deterministic validator false-positived on an
   external-source citation. Layer-4-on-layer-2 bleed producing real failure modes.
5. **Research caches are cwd-keyed and can leak.** A researcher's digest cache
   (`.planning/research/.cache/*.json`) materialized in the *orchestrating* repo's root
   rather than the target project, because the orchestrator's shell cwd differed from
   the project directory. Nearly got committed; caught only by reviewing the staged
   file list. Wart class: framework state keyed on ambient cwd instead of an explicit
   project root. When orchestrating GSD against another directory, anchor every path
   absolutely and audit `git status` before committing the host repo.

## Open questions

- How is 1398 markdown files' worth of methodology kept coherent? Is there a schema, or is
  it convention?
- Does the ceremony pay below some task size, and where's that threshold?
- 680 commits/month on a seven-month-old project — what's churning?
- Does `gsd-pi` behave identically to gsd-in-Claude-Code, or does the host harness dominate?
