---
name: superpowers
category: 4
maker: Prime Radiant
url: https://github.com/obra/superpowers
license: MIT
access: open-source
stack: [Markdown, Shell, Node]
version: v6.3.0
commit: b36e082
first_commit: 2025-10-09
stars: 283395
stars_at: 2026-09-09
read_at: 2026-09-09   # candidate 2026-09-09 (one day) → stub facts + deep-dive same sitting, the bmad-method same-day precedent
depth: deep-dive   # 2026-09-09: all four category-4 functions traced in source by three parallel readers (F1 intent refinement, F2 work decomposition, F3 gap research — absent, surface declared, F4 verification) plus the delivery substrate; load-bearing claims spot-verified at the pin in the main session; all four runtime executables run-probed same day
harness_targets: "three measures @ b36e082, stated because they differ: 9 harnesses with a dedicated manifest or code adapter in-tree (Claude Code, Cursor, Codex, Devin, Hermes, Kimi, OpenCode, Pi, Gemini); 11 with any dedicated source artifact (+ Antigravity's tool-map reference, + Copilot CLI's env-var branch in hooks/session-start:52-55); 14 install sections in README.md lines 49-260 (Factory Droid, Grok Build CLI, and the official Claude marketplace ride .claude-plugin/ with zero dedicated files)"
workflow_features:   # deep-dive 2026-09-09 @ b36e082
  intent_pipeline: true          # three-path router (spike/bounded/architectural, brainstorming/SKILL.md:22-52) → sectioned design → committed spec → writing-plans; the full pipeline engages only on the architectural branch, which the agent itself selects
  deterministic_engine: false    # checked and absent: no orchestrator, scheduler, or state machine anywhere (surface: all 12 non-md files under skills/, hooks/, scripts/); the harness is the only runtime — "The bootstrap is the entire integration" (docs/porting-to-a-new-harness.md:52-55)
  format_gates: script           # ADR-0011 graded: exactly one machine-checked artifact constraint — task-brief's awk heading grammar, exit 3 on a missing task (scripts/task-brief:28-39, run-probed); every other format rule (plan header, No Placeholders, ledger grammar, reviewer verdict format) is prose
  measured_gates: false          # checked and absent: no gate compares against a measured expected value; worktree baseline suite counts are reported but never persisted or diffed (using-git-worktrees/SKILL.md:126-136); the only script with a verdict (find-polluter.sh) compares filesystem state, not a baseline
  process_gates: prose           # ADR-0011 graded: dense and unusually explicit — a HARD-GATE block (brainstorming/SKILL.md:14-20), four Iron Laws ("Skip any step = lying, not verifying"), SDD's never-skip-review rule (SKILL.md:311-313) — all exhortation; the one shipped hook enforces nothing (see Architecture)
  context_isolation: true        # founding SDD principle, prose-only: fresh subagent per task, "They should never inherit your session's context" (subagent-driven-development/SKILL.md:10), file handoffs so artifacts "never enter the controller's context" — instructed, not hook-enforced (contrast gsd-core)
  parallel_orchestration: true   # dispatching-parallel-agents (same-response dispatch = parallel, SKILL.md:66-77) + using-git-worktrees; scoped to independent fixes — SDD itself forbids parallel implementers ("Never dispatch multiple implementation subagents in parallel", SKILL.md:282)
  state_store: repo-files        # committed docs/superpowers/{specs,plans}/ + gitignored .superpowers/ scratch (sdd per-plan ledger workspace, brainstorm session dirs); ephemeral by design — workspace deleted after final review, "git history is the durable record"; no cross-session memory
  retrospectives: false          # checked and absent: zero hits for retrospectiv|post-?mortem|lessons learned|learnings across all 51 files under skills/; writing-skills' "RED-GREEN-REFACTOR for Skills" is a human maintainer discipline, and its measurement half (drill evals) lives out of tree in superpowers-evals
---

# superpowers

Jesse Vincent's "complete software development methodology for your coding agents":
14 skills (`find skills -name SKILL.md | wc -l` @ b36e082) covering
brainstorm → plan → subagent-driven execution → TDD → review → merge, plus one
SessionStart hook that injects a 3,333-byte bootstrap telling the model it must use
them. The category's largest tool by an order of magnitude (283.4k stars in eleven
months; the next largest tracked category-4 repo is 38k) and its purest test of the
**methodology-as-prose** position: where GSD grew a 121k-line TypeScript runtime and
OpenSpec a validator, superpowers ships **zero workflow engine on purpose** — 127
lines of bash that check argument validity, and everything else compliance-by-persuasion.

## The distinguishing bet

**The runtime contract with the model is 3,333 bytes of injected text, and every gate
is behavioral, not mechanical.** The single shipped hook (`hooks/hooks.json:3-13`,
SessionStart, matcher `startup|clear|compact`) reads
`skills/using-superpowers/SKILL.md` and emits it as `additionalContext`
(`hooks/session-start:11,31`) — *"If you think there is even a 1% chance a skill might
apply … you ABSOLUTELY MUST invoke the skill"* (`using-superpowers/SKILL.md:11-13`).
From there, discovery is delegated entirely to the host harness's skill machinery,
and compliance is engineered with the tools of persuasion: Iron Laws, 12-row
rationalization tables that pre-name the excuse the agent is about to make
(`using-superpowers/SKILL.md:37-50`), and adversarial pressure-test scenarios shipped
*inside the skill directories* (`systematic-debugging/test-pressure-1.md`: a
$15,000/minute outage with a manager shouting "FIX IT NOW", built to make the
shortcut rational). Verification authority rests on an **adversarial reader with a
different context** — a reviewer subagent told *"Treat the implementer's report as
unverified claims about the code"* (`task-reviewer-prompt.md:64-71`) — never on a
script. The repo knows the position it has taken: PreToolUse path *enforcement* is
"Phase 4" of an unshipped design (`docs/superpowers/specs/2026-04-06-worktree-rototill-design.md:31,341`),
and the porting guide states the architecture plainly: *"The bootstrap is the entire
integration. Without it, the skill files are inert"* (`docs/porting-to-a-new-harness.md:52-55`).
The cost of the bet is stated in Tract findings below: every gate degrades to zero
under a non-compliant model, and nothing detects the degradation.

## Main features

- **Three-path router** (v6.3.0's headline change): brainstorming classifies every
  request as **spike** (answer, no artifacts), **bounded** (design in chat, no spec
  file, no plan), or **architectural** (full pipeline: questions → 2–3 approaches →
  sectioned design approved per section → committed spec → plan) before its first
  question, says the classification out loud so the human can override, and ratchets
  one-way — *"When in doubt between two paths, take the heavier one"*
  (`brainstorming/SKILL.md:22-52`).
- **Plan grammar for a hostile audience**: plans are written for *"an enthusiastic
  junior engineer with poor taste"* — every task carries exact file paths, an
  Interfaces block (consumes/produces with exact signatures), and five TDD steps
  each with `Run:`/`Expected:` pairs; six placeholder patterns are banned by name
  (`writing-plans/SKILL.md:84-138`). Tasks are sized by *review economics* ("split
  only where a reviewer could meaningfully reject one task while approving its
  neighbor", `:38-42`); the README's "2-5 minutes" figure belongs to steps, not tasks.
- **Subagent-driven development (SDD)**: fresh implementer per task; one reviewer
  dispatch returning **two verdicts** (spec compliance + code quality,
  `task-reviewer-prompt.md:3-5`); a five-round fix loop that *resumes* the original
  implementer for rounds 1–3 and escalates to a fresh implementer on a more capable
  model for 4–5; a circuit breaker at round 5 with controller adjudication —
  *"Adjudicating earlier to end a loop is pre-judging with a different name"*
  (`SKILL.md:354-429`). Inter-task human checkpoints are explicitly **abolished**:
  *"Do not pause to check in with your human partner between tasks"* (`SKILL.md:17-31`) —
  rulings recorded in a ledger instead.
- **Compaction-surviving ledger**: the one genuine structural (non-prose) defense —
  `scripts/sdd-workspace` scopes the progress ledger per-plan under
  `.superpowers/sdd/<plan-basename>/` because *"a stale ledger misread as current
  progress makes controllers skip whole task sequences"* (script header :7-9,
  observed-in-the-wild failure per RELEASE-NOTES.md:48). Built for context recovery,
  not correctness.
- **TDD with the delete rule**: *"Write code before the test? Delete it. Start
  over"* with four no-exceptions clauses (`test-driven-development/SKILL.md:33-45`);
  the implementer's report must contain RED and GREEN evidence
  (`implementer-prompt.md:134-136`) — which the reviewer is told to read but *not*
  re-run (`task-reviewer-prompt.md:75-82`).
- **Systematic debugging**: four prose-gated phases with the library's one counted
  rule — three failed fixes forces an architecture question and a human escalation
  (`systematic-debugging/SKILL.md:191-196`).

## Stack & repo shape

Shell + Markdown: `md(94) sh(41) json(14) js(10) txt(9) py(6)` (repo-facts extension
count @ b36e082); 195 tracked files, 681 commits. The 14 skills hold 51 files
(`find skills -type f | wc -l`); total harness adapter code is **364 lines**
(104 py + 139 js + 121 ts) plus ~7 KB of JSON manifests. `tests/` holds 60 files
(`git ls-files tests | wc -l`) — overwhelmingly *plugin infrastructure* (manifests,
hooks, version-sync, the brainstorm server), not skill behavior; the skill-behavior
eval harness (drill: real tmux sessions judged by an LLM verifier) lives out of tree
in `prime-radiant-inc/superpowers-evals`, gitignored as `evals/` (`.gitignore:10-13`).

**Provenance:** a single-author project with one substantial collaborator — Jesse
Vincent 523 + `jesse` 13 = 536/681 commits (78.7%), top two humans 91.3%
(`git shortlog -sn`). 93 commits carry a `Co-Authored-By` trailer (commit-count
measure, `git log --grep`); trailer *lines* naming Claude number 124 (line-count
measure — squashed release commits fold many sub-commit trailers into one message).
The project dogfoods its own disclosure rule: every PR must name the model, harness,
and plugins that produced it (`CLAUDE.md:34`), and its contributor doc opens with
"This repo has a 94% PR rejection rate" (`CLAUDE.md:7`, TESTIMONY — their own figure).
**Release model:** `main` is the released branch (34 tags in ~10 months, one every
~9 days), all work lands on `dev` — 129 commits ahead of `main` at the pin
(`git rev-list --left-right --count origin/main...origin/dev` = `0 129`), so
"pushed yesterday" on GitHub means dev activity, and a pin of `main` is a pin of the
last release. **No CI, ever**: `.github/workflows/` does not exist and never has
(`git log --all -- .github/workflows` is empty); the 60 tests run only when someone
runs them, and `.pre-commit-config.yaml`'s three hooks are all scoped
`^evals/.*\.py$` — a gitignored, absent directory — so the repo's only automated
gate never fires on a clean clone.

## Architecture — deep-dive 2026-09-09 (pin b36e082; three-tract source read + same-day run probe)

*Method: three parallel Opus readers (F1+F2 intent/decomposition · F4+F3
verification/loop · substrate/portability/provenance), load-bearing claims
spot-verified in the main session at the pin; the four runtime executables run-probed
same day (below). All four category-4 functions traced; F3 traced to a graded
absence.*

### F1 — intent refinement: a real pipeline, on one branch of three

The architectural path is the strongest F1 in the category's prose tier: classify →
clarifying questions one at a time → 2–3 approaches with trade-offs → sectioned
design approved *per section* → spec committed to
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` → self-review → human review →
`writing-plans`, all under the HARD-GATE (`brainstorming/SKILL.md:94-104,221-231`).
But v6.3.0's router means the full machinery engages **only when the agent itself
classifies the work as architectural** — bounded work produces a chat paragraph and
no spec, and spikes produce only an answer. The framework's F1 artifact discipline is
therefore self-selected per task. One quality gate quietly degraded: both
`spec-document-reviewer-prompt.md` and `plan-document-reviewer-prompt.md` ship as
subagent dispatch templates but are referenced by **no skill** at this pin (grep over
skills/, only RELEASE-NOTES mentions remain) — both SKILL.mds now instruct an inline
self-check instead (*"This is a checklist you run yourself — not a subagent
dispatch"*, `writing-plans/SKILL.md:143`). Independent spec review became
author-self-review, and the orphaned prompts stayed behind.

### F2 — work decomposition: the grammar is strong, the checker is 12 lines of awk

The task template (Files with exact paths, Interfaces with exact signatures, five
per-step verified TDD steps, No Placeholders) is as concrete as spec-kit's `T001`
grammar. Exactly one piece of it is machine-checked: `scripts/task-brief` extracts a
task by fence-aware heading match and **exits 3** if the heading grammar doesn't
produce text (`task-brief:28-39`) — the plan document's only executable format
constraint, and it is tested (`tests/claude-code/test-sdd-workspace.sh`). The
`**Spec:**` pointer that links plan to spec is checked by nothing (grep over
skills/scripts/tests: zero non-prose consumers). Consumption splits by executor:
SDD (the recommended path, with the ledger and review loop) or `executing-plans` —
which at this pin is 64 lines with **no batching and no checkpoint protocol**,
despite the README selling it as "batches with human checkpoints" (README.md:269).

### F3 — gap research: absent

**Surface searched:** all 51 files under `skills/`, case-insensitive, for
`research|spike|investigate|read the docs|documentation|look it up|web ?search|WebFetch|measure|benchmark`
plus a second pass for don't-guess/knowledge-gap phrasings. `websearch`/`webfetch`/
`benchmark`: zero hits. Every "don't guess" instruction routes to **asking the human
partner** or gathering local evidence (`implementer-prompt.md:45`,
`executing-plans/SKILL.md:63`, `systematic-debugging/SKILL.md:62`); "spike" is a
request classification, not a research dispatch. The framework has no concept of a
knowledge gap warranting research — its uncertainty budget is spent on *escalation*
(to the human, or to a more capable model in fix rounds 4–5), never *investigation*.
A coherent design choice, and the sharpest single contrast with GSD's researcher
agents (see the comparison below).

### F4 — verification: an authority map with one independent node

Who checks "done": the implementer self-reviews (prose→same agent); the **task
reviewer subagent** checks spec compliance and code quality in one dispatch
(prose→different agent — the only independent node); the re-reviewer verdicts each
finding ADDRESSED/NOT ADDRESSED; the final whole-branch review runs on the most
capable model; `finishing-a-development-branch` runs the suite and stops on red;
`verification-before-completion` mandates the Iron Law *"If you haven't run the
verification command in this message, you cannot claim it passes"* — 120 lines of
prose with zero executable component. **No "done" claim anywhere is checked by a hook
or script**; the reviewer's independence itself rests on prose it is free to ignore
(*"a stated rationale never downgrades a finding's severity"*,
`task-reviewer-prompt.md:64-71`), and reviewers are told **not** to re-run the
suite — they audit the implementer's self-reported RED/GREEN evidence. The scripts'
authority is exhausted by: exit 2 on bad args/revs, exit 3 on a missing task heading.

### Substrate — one bootstrap, thin adapters, and the portability bill

The category test — *methodology defined once, targeting many harnesses* — **passes
cleanly at the source level**: 14 SKILL.md files, all under `skills/`, zero copies in
any harness directory (`find . -name SKILL.md` outside .git); adapters resolve the
shared tree by relative path and confine per-harness variance to tool-name mapping
files (5 under `using-superpowers/references/`) and the bootstrap injection.
`AGENTS.md` is a symlink to `CLAUDE.md` (contributor guidelines, not delivery);
`GEMINI.md` is a 2-line `@`-include of the bootstrap skill. Re-injection after
compaction is three-tiered and the source is honest about the weakest tier: Claude
Code re-injects (matcher includes `compact`), Pi re-injects via a compaction event
(`.pi/extensions/superpowers.ts:27-29`), Hermes cannot (`README.md:257-259` says so).
The **Codex hooks incident** (fixed in this very release commit) is the clean
portability-cost specimen: Codex auto-discovers `hooks/hooks.json` when a manifest
has no `hooks` field, so Claude Code's SessionStart hook fired on Codex; deleting the
declaration made it worse (the fallback took over); the working fix is exactly
`"hooks": {}` (`.codex-plugin/plugin.json:24`) — sharing one repo root with N
harnesses makes every harness's *discovery defaults* your problem, and the original
test "passed while the hook was still being auto-discovered."
`.agents/plugins/marketplace.json` is **Codex's convention, not a cross-tool one**:
validated only by `tests/codex/test-marketplace-manifest.sh`, OpenAI-shaped schema,
consumed by no other harness (bears on issue #23 — the generic name is aspirational,
the contents are single-vendor).

**Telemetry** (read first, per the candidate row): narrower than the README paragraph
implies. One implementation, `skills/brainstorming/scripts/server.cjs:106-112,244-251` —
the user's *browser* fetches a Prime Radiant logo PNG carrying `?v=<version>`,
`referrerpolicy="no-referrer"`, only inside the optional visual companion (never in
the session hook path — grep of hooks/: zero hits), default **on**, honoring three
opt-out env vars incl. Claude Code's `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`.
The README's "does not include any details about your project" claim is supported by
the source: the version string is the only constructed payload.

## Run probe — 2026-09-09 (rule 8: docs/source/run closed same day)

File-level and executable-level only — no model calls; a live-session auto-trigger
probe (the repo's own acceptance test: "Let's make a react todo list" must fire
brainstorming, `CLAUDE.md:110-116`) is parked pending sign-off.

- **SessionStart hook, run as Claude Code would** (`CLAUDE_PLUGIN_ROOT=<clone>
  hooks/run-hook.cmd session-start`): exit 0; emits exactly one wire field
  (`hookSpecificOutput.additionalContext`); payload **3,333 bytes**, opening
  `<EXTREMELY_IMPORTANT>\nYou have superpowers.` — and the YAML frontmatter of
  using-superpowers/SKILL.md **is** injected verbatim (chars ~203+), confirming the
  source-read finding that Claude Code's own hook is the only adapter that doesn't
  strip it (OpenCode/Pi/Hermes adapters all do).
- **`sdd-workspace`** on a scratch git repo: creates `.superpowers/sdd/<plan-basename>/`
  and writes the self-ignoring `.gitignore` (`*`) at the sdd base — observed as
  documented.
- **`task-brief`**: fence-aware extraction verified against a decoy — a plan with
  `### Task 2` inside a code fence and a real `### Task 2: Gadget` after it extracts
  only the real one (3 lines); a missing task exits 3 with the documented message.
  (One probe artifact worth recording: passing `/dev/stdout` as OUTFILE hangs at the
  script's `wc -l < "$out"` read-back — not an intended usage, not a defect.)
- **`review-package`**: rejects an invalid BASE with exit 2 naming it; writes the
  named diff artifact on valid revs.

The run probe confirms the source read at every point it touched: the scripts do
artifact plumbing with honest exit codes, and nothing more.

## Bleed

Delivery is **category-6 shaped** (skills + plugin marketplaces — the same
skills-as-distribution surface the `.agents`/issue-#23 convention question tracks),
and the brainstorm visual companion is a small standalone web app. No category-2
bleed: the framework owns no loop, no context assembly, no permission surface — it
rides the host's (`context_isolation`, `parallel_orchestration`, and state all resolve
to instructions to use harness-native subagent/worktree machinery, the "execution
substrate" the taxonomy expects harnesses to absorb).

## Cost model

Free (MIT). Commercial support arm (Prime Radiant, `sales@primeradiant.com`,
README.md:52-54) — support and "managed spending", not a gated feature tier; nothing
in the tree is paywalled. The runtime token cost is unusually legible: ~800 tokens of
bootstrap per session start/clear/compact, then whatever skills the model pulls; SDD
multiplies subagent dispatches (fresh implementer + reviewer per task, five-round fix
ceiling) — the framework's own context-economy rules exist precisely to bound this
(`SKILL.md:230-233,268-271`, the 42k-char dispatch scar).

## For the daily GSD user weighing this (2026-09-09)

The two tools sell the same shape — spec → plan → subagent execution → verified
merge, delivered as skills into many harnesses — from opposite ends of the
enforcement spectrum, and the comparison (against [gsd-core](gsd-core.md), deep-read
at 182f60b4) is the category's cleanest natural experiment:

| Axis | superpowers @ b36e082 | gsd-core @ 182f60b4 |
|---|---|---|
| Engine | none, on purpose; 127 lines of plumbing bash | 121k-line TS runtime, Kahn's-algorithm waves |
| Format gates | one awk grammar check (script) | plan schema hard-errors in the runtime (engine) |
| Isolation | prose ("never inherit your session's context") | hook-ENFORCED (exit 2 on missing isolation flag) |
| Research (F3) | absent — escalate to human, never investigate | dedicated researcher agents feeding the planner |
| Retrospectives | absent in-tree; evals out of tree | milestone RETROSPECTIVE.md automatic, planner consumes it |
| Compliance theory | persuasion: Iron Laws, rationalization tables, pressure-tested prose | mechanism: engine + hooks where it mattered, prose above |
| State | ephemeral scratch, "git history is the durable record" | .planning/ tree as a durable, parsed store |
| Portability bill | Codex hook auto-discovery incident; per-harness quirk ledger | declarative capability descriptors, 18 targets |

What the convergence claim survives: both frameworks independently landed on fresh
per-task subagent contexts, file-based handoffs, plan grammars written for a
context-free executor, and worktree isolation — that is now four-of-four among the
category's deep-dived frameworks doing subagent execution, no longer a two-tool
coincidence. What it does not survive: enforcement is where the category
actually differentiates, and superpowers deliberately occupies the all-prose pole
that GSD's trajectory (prose rules hardening into hooks and engine checks, one scar
at a time) has been moving away from. The practitioner question is which failure
mode costs more in practice: superpowers' silent gate degradation under a
non-compliant model, or GSD's engine surface area.

## Surprises

1. **The enforcement inversion.** The library most preoccupied with verification
   rhetoric in this category ("Skip any step = lying") ships the least enforcement
   machinery — and documents that the mechanical version is deferred future work.
2. **Skills ship their own adversarial tests.** Pressure-test scenarios and a
   comprehension quiz live *inside* `skills/systematic-debugging/` — prose treated as
   code, with tests OF the prose. The measurement harness that runs such tests at
   scale (drill) is out of tree.
3. **Two orphaned reviewer prompts** mark a quality-gate regression (independent
   spec/plan review → self-review) that the README and release notes never state as
   a removal.
4. **No CI in a 283k-star repo** — and an inert pre-commit config linting an absent
   directory. The portability story rests on tests run by hand.
5. **The README drifts from its own source** at five+ points (two-stage review,
   worktree timing, task granularity, executing-plans checkpoints, root `npm test`)
   — all in the direction of describing an older or grander architecture.
6. **The one structural defense was built for context recovery, not correctness**
   (plan-scoped ledger) — the failure that actually got a mechanism was the
   controller losing its place, not the code being wrong.

## Scored pre-read predictions (from the 2026-09-09 candidates row)

- **"Passes the portability test SuperClaude_Framework failed" — CONFIRMED**, at
  source level: methodology defined once (14 SKILL.mds, zero per-harness copies),
  364 adapter lines total. The row's "13+ harnesses" resolves to 9/11/14 depending
  on measure (frontmatter `harness_targets`).
- **"Live specimen for issue #23's `.agents/skills` bet" — CONFIRMED, polarity
  negative**: `.agents/` here is a Codex-only marketplace manifest wearing a generic
  name; skills load through N harness-specific mechanisms, and the per-harness
  install pattern (and its Codex incident) is what the *absence* of a shared
  convention costs, exactly as the row predicted.
- **"Read the telemetry disclosure first" — done; the disclosure slightly
  overstates**: it is a browser-side image beacon on one optional path, not
  session-level telemetry.
- **"Same skills-based delivery, same subagent-execution shape as GSD — tests
  whether convergence is real" — answered**: the execution shape converges (now 4/4
  among deep-dived subagent-executing frameworks); enforcement is where
  the tools genuinely diverge, so "the category is converging" is true of workflow
  shape and false of enforcement architecture.

## Open questions

- **Does the auto-trigger actually fire?** The repo's own acceptance test ("Let's
  make a react todo list" → brainstorming auto-triggers) is the cheapest live probe
  and the whole framework hangs on it — one Claude Code session in a scratch project
  would close it. Parked for sign-off (model spend).
- **Does the bounded path eat the framework?** v6.3.0 lets the agent self-classify
  most work out of the spec/plan machinery. What fraction of real sessions take the
  architectural path? (Only observable in use; the drill evals repo may answer it.)
- **dev is 129 commits ahead** — the next release lands as one squash on main; at
  this cadence (~9 days) the pin will be behind within weeks. Re-read trigger: next
  tag (issue #32 pattern).
- The **drill eval harness** (`prime-radiant-inc/superpowers-evals`) is the missing
  measurement half of the retrospectives story and a candidate source read of its
  own — an LLM-judged tmux-session harness for testing prose skills is category-5/6
  adjacent instrument territory.
