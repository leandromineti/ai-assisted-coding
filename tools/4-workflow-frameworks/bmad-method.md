---
name: bmad-method
category: 4
maker: BMad Code, LLC
url: https://github.com/bmad-code-org/BMAD-METHOD
license: MIT
open_source: true
stack: [JavaScript, Node.js, Python]
version: v6.11.0-29-g86beb065
commit: 86beb065
first_commit: 2025-04-13
stars: 52030
stars_at: 2026-08-18
read_at: 2026-08-18   # deep-dive, same day and same pin as the stub — promoted stub → deep-dive directly; the read did the survey's work en route
depth: deep-dive   # 2026-08-18: source traced by three parallel readers at the pin (routing spine + plan/ship pipeline; gates/runtime/personas; installer/portability), load-bearing claims spot-verified in main session; install RUN-probed same day in a node:22 container (npm 6.11.0 = the pin's release tag, 29 commits behind the pin)
harness_targets: "47 platform codes @ 86beb065 (tools/installer/ide/platform-codes.yaml) — but only 22 distinct target dirs, and 26 of the 47 share the `.agents/skills/` cross-tool convention; 4 marked preferred (claude-code, codex, cursor, github-copilot); none deprecated or suspended at the pin"
workflow_features:   # deep-dive 2026-08-18; gates graded per ADR-0011
  intent_pipeline: true          # brief/prfaq → prd → ux → architecture → spec → epics → sprint-status.yaml → spec-{slug}.md; two handoffs machine-readable (spec `companions:` frontmatter, sprint-status keys), the rest filename-glob discovery + prose "Common next" pointers
  deterministic_engine: true     # ~2.6k lines of shipped Python (sprint_plan.py 697, sprint_status.py 746, render_skill.py 401, lint_spine.py 257, …) parse/validate/write state post-install and hard-fail — but nothing ADVANCES the workflow, and every call site is licensed to proceed by best judgment on script failure (bmad-sprint-planning/SKILL.md:29-31)
  format_gates: script           # sprint_plan.py generate normalizes illegal statuses and exits 1 on post-write validation failure — but both dedicated validators are exit-0 reporters BY DESIGN (lint_spine.py:19-21: "Exit code is always 0 — findings travel in the JSON") and document-level standards are prose checklists
  measured_gates: prose          # the spec template encodes expected values unusually well (I/O & edge-case matrix, `COMMAND -- expected:`, a matrix-test audit where a skipped test "counts as missing") — all authored, run, and judged by the LLM; failure routes to a prose HALT
  process_gates: prose           # "ALWAYS halt at checkpoints and wait for human input" (bmad-build/workflow.md:80) + <frozen-after-approval> spec regions (spec-template.md:16); no hook, no blocker; bmad-build-auto deletes them wholesale
  context_isolation: true        # designed-in and mandatory-flavored — "Using subagents when instructed is mandatory. If you cannot, HALT" (build-auto/workflow.md:52); reviewer briefs insist "the independent context is the point" — but prose-only, no hook (contrast gsd-core's exit-2 guard)
  parallel_orchestration: false  # instructed same-turn fan-out for READ-ONLY work (reviews, research) only; no worktree machinery (the sole "worktree" occurrence is the ordinary git working-tree sense, bmad-build/customize.toml:157); implementation single-threaded; backgrounding explicitly banned (build-auto/workflow.md:54)
  state_store: repo-files        # _bmad-output/implementation-artifacts/sprint-status.yaml is canonical; spec-{slug}.md frontmatter is a real 5-state machine (draft|ready-for-dev|in-progress|in-review|done, spec-template.md:5) that step dispatch routes on; four-category TOML config; no database
  retrospectives: true           # script-fed (git_evidence.py; sprint_status.py detect-epic computes pending_stories), action items persisted by id in sprint-status.yaml, next retro checks follow-through by id (acceptance-verdict.md:23) — but the loop closes into TRACKING, not planning; the designed verdict consumer is the external bmad-loop module
---

# BMAD-METHOD

"Agile AI Driven Development": an encoded delivery methodology installed as Agent Skills
into the user's harness via `npx bmad-method install`. 29 real skills plus
20 deprecated shims (49 `SKILL.md` total; the source predicts fresh installs get 29 —
`shim-policy.js:96` — but the run probe below observed all 49 installed), ~123k words of
methodology prose (12,185 lines across 182 markdown files in `src/`), a ~2.6k-line Python
`script layer` the skills call at runtime, and a 10.4k-line Node installer. 52k stars in
~16 months. MIT but trademarked (TRADEMARK.md, "BMad Code, LLC") — open method, protected
brand.

## The right-sizing verdict — the stub's live question, answered

The stub asked whether v6's "right-sized process" is real routing logic or a
default-heavy funnel. The answer is **neither cleanly — and the ledger's "process-gates-heavy
funnel" prediction is falsified on the funnel half, confirmed on the enforcement half**:

- **The funnel is genuinely bypassable, and the docs tell you to bypass it.** The
  documented entry point is `bmad-build`, not a planner: "Open your project in your AI
  coding tool, invoke `bmad-build` with what you want to change" (README.md:19). Build
  loads planning artifacts by filename glob only "if any look relevant"
  (`bmad-build/step-01-clarify-and-route.md:82`) — nothing requires any to exist, and the
  workflow map is explicit: "Those artifacts add context; they do not select another
  implementation workflow" (`docs/reference/workflow-map.md:97`). Build runs fine on an
  empty planning directory.
- **The fork is real and materially configured, not just narrated.** One-shot vs
  plan-code-review is a genuine split: the full route ships three review passes
  (`bmad-build/customize.toml:92,111,127`) and the one-shot route exactly one (`:143`);
  one-shot also skips planning, the approval checkpoint, and the present step — ~403
  lines of instruction prose vs ~810 for full build, ~3.9k for the full planned path
  (roughly a 10× spread, cumulative across just-in-time step loads, not simultaneous
  context).
- **But the sizing decision itself is one binary prose judgment, biased heavy.** The
  entire procedure is `step-01-clarify-and-route.md:98-106`: "one-shot — zero blast
  radius … plan-code-review — everything else. When uncertain whether blast radius is
  truly zero, choose this path." No code evaluates it, nothing validates the choice
  afterward, and the `required=true` flags in `module-help.csv` are declared "soft
  suggestions, not hard gates" by `bmad-help` itself.
- **The fork vanishes exactly where it would matter most.** `bmad-build-auto` — the
  unattended variant — has no `step-oneshot.md` and no present step at all (directory
  listing at the pin); every autonomous change takes the full plan-implement-review
  path. Right-sizing is a courtesy the interactive LLM extends, not a property of the
  system.

## A runtime without authority

This is the category's fourth engine shape, and it extends [conclusion 7](../../README.md)'s
divergence pattern. BMAD ships real post-install code — Python installed into the user's
project at `_bmad/scripts/` and per-skill `scripts/`, run via `uv run`: `sprint_plan.py`
(697 lines; atomic writes with post-write validation that exits 1 on mismatch),
`sprint_status.py` (746), `render_skill.py` (401; content-addressed immutable snapshot
renderer), `lint_spine.py` (257), plus memlog, git-evidence, and config resolvers, each
with a paired test file. This is far more runtime than spec-kit shipped *connected to its
methodology*, and unlike spec-kit's engine it actually parses the methodology's artifacts
(epics → sprint-status.yaml, deterministically).

But **no code owns control flow, by explicit design**:

- Every script call site licenses the LLM to route around failure: "when `sprint_plan.py`
  errors … do not stop at the error … Read the files yourself, deliver the same outcome
  by best judgment" (`bmad-sprint-planning/SKILL.md:29-31`; the same pattern in
  qa-generate-e2e-tests, checkpoint-preview, party-mode, brainstorming, the agents).
- The two dedicated validators are exit-0 reporters *by design*: "Exit code is always 0 —
  findings travel in the JSON; the caller (Reviewer Gate / rubric walker) decides what to
  do with them" (`lint_spine.py:19-21`); `sprint_plan.py validate` likewise never fails.
- **Zero harness hooks anywhere** — grepped `src/` and `tools/` for
  PreToolUse/PostToolUse/UserPromptSubmit at the pin: no hits. The marketplace manifest
  declares skills only. The one place hooks enter the ecosystem is the external
  `bmad-loop` module ("installs the bmad-loop orchestrator tool and wires up the
  per-project hooks and policy", `bmad-modules.yaml`) — out of this repo, behind a git
  clone + npm install.
- An internal inconsistency that sharpens the point: the build flow hand-edits
  `sprint-status.yaml` in prose ("load the YAML, find the key, set the value … preserving
  ALL comments", `bmad-build/sync-sprint-status.md:13-17`) — the same file
  sprint-planning and retrospective manage through scripts.

So on the enforcement ladder: gsd-core migrates enforcement *out of* prose into hooks and
a runtime that blocks; OpenSpec was *born* engine-first; spec-kit built an engine that
never reads its prose; **BMAD builds honest deterministic bookkeeping and then
deliberately subordinates it to the model's judgment**. The scripts are advisors, not
enforcers — "script-graded gates with an engine's build quality and a prose gate's
authority."

The price of that `script layer` is a universal dependency: `uv`/Python ≥3.11 is "a
requirement, not a preference: the rendered skills … HALT on activation if `uv` is
unavailable — there is no interpreter fallback" (`tools/installer/core/uv-check.js:9-11`)
— identical on all 47 platforms, including any that have no shell to run it.

## Personas — ceremony got cheap

The ledger predicted "role-playing agent teams." Mechanically, an "agent" here is a
persona the main session *adopts* — nothing is spawned. There are exactly five (analyst
"Mary", PM "John", UX "Sally", architect "Winston", dev "Amelia"), each a 76-line
`SKILL.md` differing from its siblings in only ~7 lines, with the persona content as
small data in `customize.toml` (role, identity, communication style, 3–6 principles) plus
a menu that routes to skills the user could invoke directly. **No plan or ship skill
requires, invokes, or checks a persona** — grepping `src/` for `bmad-agent-` outside the
agents' own directory finds only the customization guide. Party mode is genuinely
engineered (four execution modes including a real subagent-per-persona mode) and entirely
decorative — nothing in the delivery workflow touches it; its deliverable is "a keepsake."

The repo visibly contains **two generations of design**. Old-generation ceremony
survives: `bmad-create-epics-and-stories/steps/step-01` still ends with "🚨 SYSTEM
SUCCESS/FAILURE METRICS" (`:256`) and 🚫-FORBIDDEN bullets (`:28,37`) — enforcement by
typography. The newer skills (build, spec, architecture, forge-idea, retrospective) are
markedly disciplined and evidence-oriented — bmad-retrospective: "A claim you cannot
point at … is not a finding. Drop it." The ledger's prediction fits the generation that
is being replaced.

## Portability — 47 destinations, one artifact, zero translation

The category test is portability by design, and BMAD's mechanism is unlike either
neighbour: **there is no `translation layer` at all**. All 47 platforms are served by a
single config-driven handler class; the transform is a verbatim recursive directory copy
— "The source SKILL.md is used directly — no frontmatter transformation or file
generation" (`tools/installer/ide/_config-driven.js:408-410`). What varies per platform
is the destination path and nothing else (two platforms additionally get tiny pointer
files). The 47-row `platform-codes.yaml` is a routing table, not a capability model —
verified at the pin: 47 codes, **22 distinct target dirs, 26 of 47 sharing
`.agents/skills/`**, 4 preferred, zero deprecated/suspended. The installer dedupes by
directory: selecting Cursor + Codex + Warp writes one directory once.

Compare the category's three portability mechanisms: gsd-core models platform *capability*
(declarative `capability.json` per runtime, 18 targets); spec-kit *compiles* per-target
dialects (37 integrations); BMAD *refuses to model platforms at all* and rides the
emerging `.agents/skills/` cross-tool convention — Anthropic's Agent Skills format
(`name`/`description` frontmatter only, across all 49 files) shipped byte-identical
everywhere, with capability negotiation delegated entirely to the host tool. So
conclusion 7's "measured portability price" pattern — the Nth platform gets a worse
translation — **does not apply, because there is no translation to degrade**. The price
surfaces elsewhere, in two honest-to-trace places:

- **The install can't know if it worked.** No post-install verification exists; the
  installer reports success for a platform that may never read the directory it wrote.
  `--list-tools` prints id, name, target dir — the full extent of BMAD's knowledge of
  each platform. (Notably, the README never claims a platform count; the 47 is a source
  artifact, not a marketing number.)
- **Chat-only platforms get a hand-maintained fork, not a build.** `web-bundles/` is 6 of
  29 skills, hand-kept ("the bundle directories … are the files you edit",
  `web-bundles/README.md:42`; the tooling only zips them), frontmatter-stripped, with the
  entire script runtime removed — e.g. the PRD bundle is a 1,540-word rewrite of the
  1,962-word source with zero `uv run` references. That divergent fork is the real
  measured portability price, quarantined outside the 47-platform path.

Module ecosystem: only `core` + `bmm` are in-repo; Builder, Creative Intelligence Suite,
Test Architect, Game Dev Studio, and — most significantly — the entire unattended
orchestration loop (`bmad-loop`, with its hooks and orchestrator binary) live in separate
repos, resolved by shallow git clone + `npm install`. Claude Code install footprint:
everything lands in the project — `.claude/skills/` (3.0M) plus a light `_bmad/` (196K:
config, manifests, 5 shared scripts, per-module help CSVs); nothing touches `~/.claude`
or settings/hooks/MCP config unless a global install is chosen. *(Corrected by the run
probe: the source-read prediction that every skill is written twice under
`_bmad/<module>/` did not reproduce — skills land once, under the platform dir.)*

## The learning loop closes into tracking, not planning

`retrospectives: true`, but with a sharp boundary. The retro is script-fed (git evidence,
`sprint_status.py detect-epic` computing `pending_stories` — a non-empty list forces the
machine verdict to rejected, "including in headless mode") and writes action items into
`sprint-status.yaml` with stable ids. Two consumers exist: the sprint status view, and
the *next retrospective*, which checks follow-through item by item
(`references/acceptance-verdict.md:23`). **Nothing in the plan pipeline reads retro
output** — grepped across `src/`: zero hits in prd, architecture, epics, spec, ux, brief.
The retro explicitly "proposes; it does not auto-apply fixes or edit the project spec,"
and the document's own template warns that "a gate or orchestrator that acts on the
verdict must read this document's frontmatter" — a consumer this repo does not ship. The
designed loop-closer is the external `bmad-loop` module. Within this repo, Learn feeds
accountability, not planning.

The README's Clarify → Plan → Build & verify → Learn loop, for the record, exists only as
README narrative and an SVG — the encoded decomposition is `plan/` + `ship/` and the
workflow map's four phases, which do not correspond one-to-one to the diagram.

## The v6 → v6.11 pivot — verbs → nouns, stories → specs

The 20 `v6-shims` are not a v4/v5 bridge; they map **v6 skill ids onto v6.11's
consolidated skills** — three PRD command-skills collapsed into one `bmad-prd` with
intents, six review skills into `bmad-review` with lenses, `bmad-quick-dev` →
`bmad-build`. Verb-named commands became noun-named skills that infer intent, which is
why every consolidated skill opens with an intent-detection step. Two shims are "retained
in full" (`bmad-create-story`, `bmad-dev-story`): the older story-centric dev loop still
ships whole alongside the newer spec-centric `bmad-build` flow — the clearest marker of
the transition, and the same two-generations seam the ceremony section describes.

## Run probe — 2026-08-18 (rule 8: docs/source/run closed same day)

`npx -y bmad-method@latest install --yes --tools claude-code` in a clean `node:22-slim`
container (npm delivered 6.11.0, the pin's release tag — 29 commits behind the pin), git
repo initialized, no `uv`/python on PATH. Findings, read from artifacts:

- **The first attempt was a rule-5e specimen**: `--yes` still stopped at an interactive
  "Installation directory:" prompt, the process exited 0, and *nothing was installed*
  (empty footprint, 0 skills). `--directory <path>` is required for a truly
  non-interactive run. A harness reading exit status would have called this a success.
- **49 skill directories installed, not the predicted 29** — every deprecated shim
  included, under `--yes` defaults. The `shim-policy.js:96` inference ("fresh installs
  default shims off") does not describe the observed non-interactive path. Source
  prediction, falsified by the artifact; not re-traced — recorded as observed.
- **Footprint**: `.claude/skills/` 3.0M (49 dirs, per-skill `scripts/` included —
  `sprint_plan.py` lands inside `bmad-sprint-planning/scripts/`, with its tests);
  `_bmad/` 196K (manifests incl. `manifest.yaml` recording version/date/ides, 5 shared
  scripts, module config + help CSVs). No skill duplication. `~/.claude` untouched.
- **The uv warning behaves as documented**: a prominent "REQUIRED: uv" panel including
  the instruction to "ask your AI agent to install and set up uv for me"; the install
  completes without it, exactly as `uv-check.js` promises — 49 perfectly-copied skills
  whose build/plan flows would HALT on activation.

## My take

The most interesting thing about BMAD at this pin is that it is **mid-molt, and every
part of it shows the same molt**: FORBIDDEN-typography ceremony next to
evidence-discipline prose; five theatrical personas reduced to 76-line wrappers around
skill menus; a real script runtime denied any authority over control flow; the
process-heavy funnel of its reputation demoted to an optional context supply behind a
build-first entry point. The v4-era caricature the candidates ledger predicted is still
visible in the tree, but it is the part being shed.

Two design bets distinguish it from everything else in the category. First, the
authority inversion: where GSD's thesis is "a prose backstop cannot fix a prose defect,"
BMAD's is the opposite — deterministic tools should *serve* the model's judgment, never
constrain it (every script failure ends in "deliver the same outcome by best judgment").
That makes BMAD the purest large-scale test of the model-trust position, and it is
falsifiable: if exp-01's mechanism finding generalizes — self-enforced prose gates
measure near zero — BMAD's entire gate structure rests on the model's goodwill, at
whatever scale its 52k stars imply. Second, the anti-translation portability bet: shipping one byte-exact
artifact to 47 destinations is either the cheapest portability in the category or not
portability at all, depending entirely on whether the `.agents/skills/` convention
consolidates — a bet worth a dated re-check in six months.

Not adopted for daily use; nothing here displaces GSD for a practitioner who wants
enforcement. But as a specimen, it is the category's best evidence that "ceremony pole" and
"prose pole" are separable axes — BMAD is simultaneously getting *less* ceremonial and
staying *maximally* prose-governed.

## Open questions

- ~~**Does `bmad-loop` actually close the loops this repo designs for?**~~ *Answered
  same day at stub depth — [report](bmad-loop.md): the enforcement story inverts
  wholesale (engine-graded measured and process gates, "No LLM in the control loop"),
  but the retro-verdict consumer does not exist there either — retro items are parsed
  and explicitly "not yet driven as work" (roadmap). Learn → Plan stays unshipped
  ecosystem-wide.*
- ~~**Is the long platform tail real?**~~ *Sampled same day: `bob`, `adal`,
  `codewhale` all resolve to real tools whose public docs document exactly the claimed
  skills directories (IBM Bob: project `.bob/skills` + global `~/.bob/skills`; AdaL
  `~/.adal/skills`; CodeWhale `~/.codewhale/skills`). 3/3 — the tail reads as verified,
  not aspirational.*
- **Is the one-shot route ever taken in practice?** The tiebreak text biases against it;
  source can only show the fork exists. A live-run probe (rule 8) would need a real
  project and both a trivial and a non-trivial change.
- ~~**Install not executed**~~ *Run same day in a node:22 container — see the run-probe
  section: 49 skills (not 29), no `_bmad/` skill duplication, `--yes` alone is not
  non-interactive.*
