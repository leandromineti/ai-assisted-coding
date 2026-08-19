---
name: spec-kit
category: 4
vendor: GitHub
url: https://github.com/github/spec-kit
license: MIT
open_source: true
stack: [Python]
version: v0.1.10-1039-g655a3cb
commit: 655a3cb
first_commit: 2025-08-21
stars: 124319
stars_at: 2026-07-28
read_at: 2026-08-18   # deep-dive date; first read 2026-07-28, drift-checked 2026-08-16, all at the SAME pin (clone re-detached to 655a3cb for the deep-dive)
depth: deep-dive   # 2026-08-18: runtime traced in source by three parallel readers (workflow engine + state machine; template compilers + 37 integrations; artifact flow + gates), load-bearing claims spot-verified in main session. Earlier: templates read in full (survey 2026-07-28); RUN 2026-08-17 (exp-02 Run B, full 7-step pipeline at this pin — rule 8 gap closed)
harness_targets: "37 registered integrations @ 655a3cb (36 named + `generic`), incl. Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, Cline, Goose, Kimi, Hermes — survey's \"44 config dirs\" did not reproduce at deep-dive"
workflow_features:   # added 2026-08-18 (survey + exp-02); context_isolation & parallel_orchestration settled by the same-day deep-dive
  intent_pipeline: true          # constitution→specify→plan→tasks→implement
  deterministic_engine: true     # 11-type workflow engine + setup scripts — but it advances its OWN run state and never parses SDD artifacts (deep-dive)
  format_gates: false            # FLIPPED ✓→✗ at deep-dive 2026-08-18: the checklist gate and ≥80% rule are prose the agent enforces on itself; script gates test existence only; no code machine-checks any artifact's structure
  measured_gates: false          # gates test the English, never measured behavior (exp-02 corroborates)
  process_gates: prose           # ADR-0011 graded: clarify cap, checklist STOP-and-ask, constitution approval — all agent-enforced; the engine's code gate is opt-in and checks nothing
  context_isolation: false       # no fresh-context instruction anywhere; handoffs `send: true` chains steps in ONE conversation (deep-dive §context)
  parallel_orchestration: false  # [P] has no code consumer; FORK_CONTEXT_COMMANDS = {} (tried, retreated #3185); fan-out engine ships unused (deep-dive)
  state_store: repo-files        # specs/NNN-*/ + .specify/ (+ .specify/workflows/runs/<id>/ for the opt-in engine)
  retrospectives: false          # none of the 10 commands closes the loop
---

# spec-kit

GitHub's toolkit for **Spec-Driven Development**: specifications are written first and
treated as executable artifacts that generate the implementation, rather than documentation
that merely guides it. Intent before mechanism.

Workflow: `/speckit.constitution` (principles) → `/speckit.specify` (requirements) →
`/speckit.plan` (technical strategy) → `/speckit.tasks` (task list) → `/speckit.implement`.
Optional `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`, plus
`/speckit.converge` and `/speckit.taskstoissues` (unread beyond frontmatter).

40+ agent integrations (44 config dirs in `src/specify_cli/integrations/` @ 655a3cb).
Install: `uv tool install specify-cli`, requiring Python 3.11+, git, and `uv`.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged, and cannot be)

123 commits / 136 files since the read. **Every countable claim is identical at both
ends.** 15 commits touch `src/specify_cli/integrations/`, and none of them changes the
integration inventory.

| Claim | `655a3cb` | HEAD (`adb2413`) |
|---|---|---|
| integration modules (`.py` under `integrations/`) | 47 files | 47 files |
| `workflows/` YAML files | 17 | 17 |
| `SkillsIntegration` references | 22 | 22 |

*Counting note:* 47 files against the report's "44 integrations" is not a discrepancy —
the directory carries base classes and registry plumbing alongside the integrations
themselves. The verified statement is that the number **did not move**.

So conclusion 7's evidence is intact, and conclusion 3's `SkillsIntegration` → `SKILL.md`
witness is intact. The git-history claims that carry conclusion 7 (#2901 and #2713 fixing
hook execution by rewriting instructions more forcefully, #2460's eight-month unenforced
constitution, #3185's reverted context isolation) are statements about *past commits* and
cannot drift at all — worth noting as a property: **archaeological claims are the only
kind that never go stale**, which is an argument for making them where possible.

**This pin is structurally frozen.** `655a3cb` is exp-02's preregistered framework control,
so it is not re-pinnable even if a re-read happens — a re-read would produce a *second*
dated reading at a new commit, leaving the experiment's reference intact. Recorded here so
nobody later "tidies" it.

## The distinguishing bet

That agents fail from **under-specified intent**, not insufficient intelligence — so the
leverage is in forcing the "what" to be settled before the "how" begins. Compare GSD, which
shares the diagnosis but locates the failure in context management instead. Same disease,
different organ.

Source reading confirms the prediction from the category-4 index: spec-kit's mechanism mix is
**intent-capture-heavy** and almost empty on empirical grounding and context discipline —
the profile section below is the detail.

## Main features

The product is the **artifact chain**, each stage a prompt that reads the previous stage's
files and writes the next:

- **`spec.md`** (`spec-template.md`) — user stories carrying explicit priorities (P1/P2…)
  and an *independent-test criterion* each; functional requirements as `FR-###` MUST
  statements; measurable, technology-agnostic success criteria as `SC-###`; an explicit
  Assumptions section. Unknowns are embedded inline as `[NEEDS CLARIFICATION: …]` markers
  — **budgeted to a maximum of 3** (`specify.md:128`), with instructions to prefer
  informed guesses plus documented assumptions over questions.
- **`/speckit.specify` self-validation** — after writing the spec, the same command
  generates `checklists/requirements.md` and iterates the spec against it (max 3
  iterations), then interactively resolves remaining clarification markers as
  multiple-choice questions (`specify.md:144-234`).
- **`/speckit.clarify`** — a structured ambiguity scan over ~10 fixed categories
  (scope, data model, UX flow, non-functional attributes, integrations, edge cases…),
  producing at most 5 questions, asked strictly one at a time, each with a recommended
  answer the user can accept with "yes"; every accepted answer is immediately written
  back into the relevant spec section plus a dated `## Clarifications` log
  (`clarify.md:73-191`).
- **`plan.md` + design artifacts** — Phase 0 `research.md` (each unknown → a dispatched
  "research best practices" task), Phase 1 `data-model.md`, `contracts/`,
  `quickstart.md`. Contains a **Constitution Check gate evaluated twice** — before and
  after design (`plan-template.md:39`, `plan.md:67-72`).
- **`tasks.md`** — a strict task grammar: `- [ ] T001 [P] [US1] Description with file
  path`, phases organized **by user story** so each story is an independently testable
  increment, with explicit dependency and parallel-execution sections
  (`tasks.md:149-213`). Tests are **opt-in**: "Only generate test tasks if explicitly
  requested" (`tasks.md:147`).
- **`/speckit.analyze`** — read-only cross-artifact consistency pass over
  spec/plan/tasks: duplication, ambiguity, underspecification, constitution alignment,
  coverage gaps (requirements with zero tasks, tasks with no requirement), terminology
  drift; findings in a severity table capped at 50 rows; constitution conflicts are
  automatically CRITICAL (`analyze.md:60`, `115-160`).
- **`/speckit.checklist`** — generates "**unit tests for requirements**": every item must
  interrogate the *written spec* ("Is 'fast loading' quantified? [Clarity, Spec §NFR-2]"),
  with an explicit prohibition list on implementation testing — no "Verify/Test/Confirm +
  behavior" items allowed (`checklist.md:140-246`). ≥80% of items must carry a
  traceability reference.
- **`/speckit.implement`** — checklist gate first (incomplete checklists require explicit
  user override to proceed), then phase-by-phase execution of tasks.md, marking tasks
  `[X]` as they complete (`implement.md:56-174`).
- **Extensions & hooks** — `.specify/extensions.yml` declares before/after hooks per
  command (`before_specify`, `after_plan`, …); bundled extensions include `git` (branch
  creation is a hook, opt-in since v0.10.0), `agent-context`, `bug`, `assess`.
- **Presets, bundles, workflows** *(ARCHITECTURE-level read only)* — presets override
  templates through a priority stack (override → preset → extension → default);
  `specify workflow run` is a deterministic YAML step engine that can drive the slash
  commands from outside the chat loop. *(Corrected at deep-dive 2026-08-18: the survey's
  "command/shell/gate/if/loop" list was wrong — 11 step types are registered
  (`workflows/__init__.py:59-69`), incl. `switch`, `do-while`, `fan-out`, `fan-in`,
  `prompt`, `init`, plus an `exec_module` plugin loader for community step types.)*

## Stack & repo shape

Python — 284 `.py` across 521 tracked files, the second-smallest repo here. 135 `.md` files
are the command and template definitions, which is where a category-4 tool's actual product
lives. Ships `presets/ARCHITECTURE.md` and `workflows/ARCHITECTURE.md`, plus 11 `.sh` and
10 `.ps1` — cross-platform shell scaffolding.

1603 commits since 2025-08-21 — the smallest history in the set, and second-youngest
(gsd-core's first commit is 2025-12-14). 131 of those
commits touch `templates/commands/` alone: the prompts are debugged like code, with
regression-style fixes landing monthly.

## Architecture

The split is stark: **~3,200 lines of markdown are the product; the Python around it is
not a thin compiler but a large runtime** *(figure corrected at deep-dive: the workflow
engine alone is 10,678 lines + a 14,509-line/602-function test file; presets add 6,257 —
see the deep-dive section for what that inverts)*.

### How one definition targets 40+ harnesses (the portability mechanism)

Each command exists once, in `templates/commands/*.md`: YAML frontmatter (description,
`handoffs` to next commands, `scripts` with `sh`/`ps`/`py` variants of the same helper)
plus a prose body containing placeholder tokens — `$ARGUMENTS`, `{SCRIPT}`, `__AGENT__`,
and `__SPECKIT_COMMAND_<NAME>__` for cross-references.

`CommandRegistrar.register_commands` (`agents.py:594`) compiles that source per harness,
driven by a declarative ~15-line config each integration declares
(`integrations/<agent>/__init__.py`), e.g. Claude:
`{"dir": ".claude/skills", "format": "markdown", "args": "$ARGUMENTS", "extension": "/SKILL.md"}`
vs Gemini: `{"dir": ".gemini/commands", "format": "toml", "args": "{{args}}", "extension": ".toml"}`.
The compile step rewrites argument placeholders, resolves `{SCRIPT}` to the right
platform variant, rewrites repo paths to `.specify/…`, resolves command cross-references
per naming convention (dotted `/speckit.plan` vs hyphenated `/speckit-plan` — the
`invoke_separator`), and renders to the target format (markdown command, TOML `prompt`,
Goose YAML recipe, or `SKILL.md` with rebuilt frontmatter).

The portability claim is real but rests on a convergence: **every harness has
independently adopted "slash command = prompt file in a magic directory."** The variance
spec-kit absorbs is format, directory, and naming — not semantics. The lowest common
denominator (markdown prose + an args placeholder) is also the ceiling: nothing in the
methodology can depend on any harness capability beyond "read this prompt and obey it."
That's why forks/subagents, hooks-as-code, and context isolation are all absent (see
profile below).

### The runtime is the model

The only deterministic execution at run time is ~1.5k lines of shell (`scripts/bash/`,
mirrored in PowerShell/Python): resolve feature paths, copy a template, emit JSON. Prompts
call these via `{SCRIPT}`. Everything else — including the extension **hook system** — is
executed by the LLM interpreting prose. Every command carries ~60 lines instructing the
model to read `.specify/extensions.yml`, filter enabled hooks, emit an
`EXECUTE_COMMAND:` block, and *actually invoke* the hook.

The git history documents what that costs (see Surprises): hook dispatch has been
strengthened twice by rewriting prose more forcefully, because there is no other
enforcement mechanism available at this level.


### Deep-dive — 2026-08-18 (same pin; three-tract source read)

*Method: three parallel Opus readers (workflow runtime · compilers/integrations ·
artifact flow), every load-bearing claim spot-verified in the main session at 655a3cb.*

#### Entry point → one full trace

`pyproject.toml:19-20` (`specify = "specify_cli:main"`) → `workflows/_commands.py:1025-1156`
(`workflow_run`: source resolution, symlink-storage refusal, disabled-workflow gate that
fails closed) → `engine.py:757-806` `load_workflow` (direct YAML → overlay resolver →
legacy path) → `validate_workflow` (`engine.py:143-314`) → `execute` (`engine.py:813-912`),
which copies the definition into the run dir and walks `_execute_steps`
(`engine.py:1008-1241`). State: `.specify/workflows/runs/<run_id>/` — `state.json`
(atomic temp-file + `os.replace`, saved **before every step**), `inputs.json`, a
`workflow.yml` copy, and an append-only `log.jsonl`. Resume (`engine.py:914-991`)
accepts only PAUSED/FAILED and re-executes `current_step_index` so gates re-prompt —
which means **a hard-killed run (SIGKILL, power loss) is unresumable by construction**:
`state.json` stays `"running"` forever with no recovery path, despite the per-step saves.
Nested steps don't update the index, so a pause inside `if`/`while` replays the parent
and its whole body (`engine.py:1143-1148`, `workflows/ARCHITECTURE.md:73-76`).

#### The engine: 11 step types, radically underused

11 registered types (`workflows/__init__.py:59-69`): `command`, `prompt`, `shell`, `init`,
`gate`, `if`, `switch`, `while`, `do-while`, `fan-out`, `fan-in` — plus community step
types loaded by `spec.loader.exec_module` at run time (`workflows/__init__.py:75-201`,
arbitrary Python by design). Fan-out is genuinely concurrent: bounded sliding-window
`ThreadPoolExecutor`, per-item context copies, halt attribution taken from the item's own
result because a later concurrent item may already have flipped the shared status
(`engine.py:1242-1405`). There is a bespoke sandboxed expression language with operator
precedence and pipe filters (`expressions.py`), and an overlay system (insert/replace/
remove edits with anchors and priorities) layered on top.

**And almost none of it is used.** The one shipped workflow (`workflows/speckit/workflow.yml`,
78 lines) is six sequential steps — specify → gate → plan → gate → tasks → implement —
using 2 of the 11 types, **omitting clarify/checklist/analyze** (the commands
`docs/quickstart.md:26` calls "quality gates") and placing **no gate before implement**.
The first-party step catalog is literally empty (`workflows/step-catalog.json`:
`"steps": {}`); community catalogs hold 1 workflow and 0 steps. Meanwhile the engine
carries a 14,509-line, 602-test suite. Capability-to-content ratio is the single most
striking fact of the read.

`gate` steps check **nothing** — no file state, no prior step result: render a message,
`input()` a choice (`steps/gate/__init__.py:38-126`). Non-TTY → PAUSED unconditionally,
so a gated workflow in CI pauses forever; there is no auto-approve flag, env var, or any
non-interactive path past a gate. `continue_on_error` explicitly does not override an
abort ("Aborts are deliberate operator decisions", `engine.py:1084-1090`), and
`requires.permissions` is rejected with a message stating no capability gate exists
(`engine.py:283-289`) — the runtime *declines* to pretend it enforces things it doesn't.

#### Context assembly — what the model actually receives

**The shipped templates are not the source templates.** At install, a regex pass rewrites
`/memory/` → `.specify/memory/`, `scripts/` → `.specify/scripts/`, `templates/` →
`.specify/templates/` (`agents.py:200-227`, verified by executing the regex; `specs/` is
deliberately not in the table). Auditing `templates/commands/*.md` raw is reading
pre-processor input. There are **two parallel compilers** — `IntegrationBase.
process_template` (`base.py:744-856`) for core commands and `CommandRegistrar` for
extensions/presets — sharing only the path rewrite and command-ref resolver; nothing
enforces their equivalence. Placeholder inventory: `{SCRIPT}`, `{ARGS}`, `$ARGUMENTS`,
`__SPECKIT_COMMAND_<NAME>__` (40 occurrences, 7 commands — load-bearing and absent from
`AGENTS.md`'s placeholder docs), and `__AGENT__` (documented, resolved in two code paths,
tested by ~14 files — **zero occurrences in any shipped template**).

**The lowest-common-denominator ceiling, measured:** compiled `speckit.plan` bodies for
Claude (skills family) and amp (plain markdown) differ by 3 lines out of ~200 — the
body a rich harness receives is byte-identical to the thinnest target's; per-harness
differentiation is frontmatter wrapper + slash-separator. 21 of 37 integrations discard
frontmatter richness entirely (the skills family rebuilds it to a fixed 5-field shape,
`base.py:1673-1700`). The `handoffs:` graph authored in 5 templates is consumed by zero
lines of interpreting code, hangs Forge (whose fix is a strip-list of length one), and —
the irony — cannot survive into Claude's own `SKILL.md` despite being "a Claude Code
feature": authored for the flagship, deleted by the flagship's own format family.

**One conversation by design:** no template instructs a fresh session anywhere (searched
exhaustively); `handoffs: send: true` chains specify→clarify→plan→tasks→implement in
place; the documented remedy for context exhaustion is the *human* hand-scoping runs
("/speckit.implement only execute tasks T001-T010", `docs/concepts/complex-features.md`).
This settles `context_isolation: false`.

#### Tool surface & permissions — who enforces what

Complete gate inventory: **19 gates; 15 are prose the agent may reinterpret; 4 are
script-enforced file-EXISTENCE checks** (`check-prerequisites.sh:121-138`,
`setup-tasks.sh:31-41` — "does plan.md exist", never "is it any good"); 1 is a real
code-enforced approval (the workflow engine's gate — opt-in, and a human prompt, not an
artifact check). Notably `setup-plan.sh` never checks that `spec.md` exists — **a plan
without a spec is possible in Spec-Driven Development**; only tasks and later steps
hard-fail. The task grammar (`T001 [P] [US1]`, three-altitude spec in `tasks.md:151-179`)
has **no machine consumer**: nothing in `src/` or `scripts/` parses IDs, `[P]`, or
checkboxes; the regexes that exist are written in English, addressed to the model
(`taskstoissues.md:67`). `[P]`'s only parallel-execution consumer is a sentence the docs
suggest the *user* type. Subagent fan-out was shipped for `/analyze` (#2511) and
retreated (#3185: report re-injection "compounding overhead until the chat freezes") —
`FORK_CONTEXT_COMMANDS = {}` with three tests asserting it stays empty
(`integrations/claude/__init__.py:25-35`). Hooks are re-implemented as prompt prose
("The actual execution is delegated to the AI agent", `extensions/__init__.py:4725-4726`)
— native harness hook mechanisms are used by zero integrations; the only harness-native
config spec-kit ever writes is Copilot's `.vscode/settings.json`.

#### Category boundaries in the code

An integration is a ~21-line config: 5 `config` keys + 4 `registrar_config` keys, four
format families (18 skills, 16 markdown, 2 toml, 1 yaml), median zero methods
(`integration_scaffold.py:32-58` generates exactly this shape). **There is no field for
hooks, subagents, permissions, model selection, or any harness capability** — the
escape hatches are subtractive or cosmetic (strip a key, rename, change separator).
Invocation style lives in three parallel sources of truth (per-integration
`invoke_separator`, `_invocation_style.py`'s four frozensets, `HookExecutor`'s inline
branches). Count at pin: 37 packages / 37 catalog entries (36 named + `generic`);
community integration catalog empty. The sh/ps/py script trio has real behavioral
divergences (PowerShell mutates caller env where bash/py print hints; PS JSON and text
modes can disagree with each other; case-folding differs three ways) and the parity
suite holds only bash↔python to byte equality — PowerShell is JSON-only and skipped
entirely without `pwsh`.

#### Verdict

spec-kit is **two systems**: a prose methodology interpreted solely by the LLM, and a
seriously engineered orchestration runtime that dispatches that prose *by name* and
never reads it (`steps/command/__init__.py:14-19`). The survey's "thin scaffolding"
framing was right about the payload and wrong about the plumbing — thin *semantically*,
thick *operationally*, and radically underused: the engine is built for orchestration
nobody (including GitHub) has yet authored. For conclusion 7 this is a third pattern:
OpenSpec was *founded* on its deterministic engine, GSD *grew* one as bookkeeping —
spec-kit **built one and left it disconnected from its own methodology**.

#### Deep-dive surprises

1. **The most consequential filesystem operation was moved OUT of tested code into
   prose.** `create-new-feature.sh` (392 lines, three-variant trio, 780-line parity
   suite) is referenced by no command template; `specify.md:82-105` instructs the model
   to number the feature, `mkdir`, copy the template, and write `feature.json` by hand.
   The tested script is maintained and orphaned.
2. **`spec-driven.md` documents a gate architecture that no longer exists** — "Phase -1
   Pre-Implementation Gates" (Simplicity/Anti-Abstraction/Integration-First,
   `spec-driven.md:206-224`) versus the actual `plan-template.md:39-43`, whose gate
   section is the placeholder "[Gates determined based on constitution file]". The
   manifesto describes machinery the templates dropped.
3. **Two checklist systems coexist and the implement gate can't tell them apart** —
   `specify.md` writes a hard-coded 16-item `requirements.md` (no CHK IDs, ignoring the
   checklist template); `checklist.md` writes CHK###-ID'd domain files with the ≥80%
   traceability rule; `implement.md:57-61` counts raw checkboxes across ALL of
   `checklists/` on equal footing.
4. **Stale-doc drift inside the pin**: `workflows/ARCHITECTURE.md` misorders
   validate/resolve, cites a nonexistent `RunState.create()`, omits `overlays/` — while
   `docs/reference/workflows.md` is accurate down to the gate's verbatim-message
   behavior. The reference docs track the code; the architecture doc doesn't.

## Mechanism profile

Against the mechanism classes from experiment 01 (see
[`index.md`](index.md#mechanisms--the-unit-of-value)); source-read assessment, not a run:

| Mechanism class | spec-kit's position |
|---|---|
| **Intent capture** *(new class — spec-kit's center of mass)* | The heavy column: ID'd requirements (FR-###/SC-###), prioritized user stories each with an independent-test criterion, a *rationed* clarification budget (max 3 markers, max 5 clarify questions, one at a time, each with an acceptable-by-"yes" recommendation), checklists that unit-test the English, immediate write-back of answers into the spec |
| **Empirical grounding** | Nearly absent. Phase-0 "research" dispatches *best-practices lookups* — consulting training data, not measuring the domain. No fixture-running, no probes, no measured expected values anywhere in the chain |
| **Verification gates** | Present but **document-vs-document only**: spec self-validation loop, analyze's coverage/severity tables, the checklist gate before implement. All checks compare artifacts to artifacts; none re-derives from the world. The one hard gate (incomplete checklists) is soft — user can override with "yes" |
| **Context discipline** | Weakest column, and knowingly so: "progressive disclosure" and token-budget instructions inside analyze/checklist are *prose requests*, everything runs in the main context, and the one attempt at real isolation (Claude `context: fork` for analyze) was **reverted** after reports piled 300–500-line reports into compounding forked contexts until sessions froze (#3185) |
| **Process gates** | Moderate: hook ceremonies on every command, constitution governance (semver, ratification dates, sync-impact reports), checklist gate. The governance wrapper matches exp-01's "process gates ≈ cost" profile |
| **Bookkeeping** | Strong and grammar-enforced: task ID/[P]/[US] format with wrong/right examples, ≥80% traceability floor, coverage-% metrics in analyze, `[X]` task marking during implement |

The comparison with GSD is now sharp: **GSD spends its structure on the execution side
(fresh contexts, measured verification); spec-kit spends it on the intake side (extracting
and pinning intent before execution).** Each is thin exactly where the other is thick.
Neither has both halves.

### Profile validated by run (2026-08-17 — exp-02, this pin, full 7-step pipeline)

The A/B measured exactly what the table above predicted (README conclusion 11; both
preregistered predictions supported). Intent capture performed as profiled: 21
numbered MUST-form requirements, 5 recorded clarifications, 6 explicit assumptions —
beating the plain arm on every rubric item. And the grounding/verification thinness
showed up precisely where predicted: **trap score identical to plain** (19/21, same
two failures, both at the n=5 baseline mean), at 7.8× the cost ($4.43 vs $0.57). The
sharpest mechanism observation: clarify surfaced the right exit-code question and
*recommended the trap-failing answer* — its document-vs-document machinery converts
ambiguity into decisions and enforces them faithfully (tests asserted the generic
exit code), but nothing in the chain ever measures which decision is right. It also
pinned ISO-8601-UTC output pre-plan, deciding the ambient-config traps in the
passing direction. Steering, both directions; discovery, none. One blocking question
in the whole run (the rationed budget is real); analyze's remediation offer was the
only other human touchpoint. Run details:
[`exp-02 log`](../../experiments/02-spec-kit-vs-plain/log.md), results in its README.

## Bleed

Category 5 — it installs slash commands and templates into whichever harness you point it at;
the `specify` CLI itself is a thin installer/compiler, not a harness.

Category 2 — the `workflows/` engine (`specify workflow run`) is a deterministic YAML
orchestrator (11 step types, persisted run state) that can drive
the whole pipeline non-interactively. Same pattern as GSD's `gsd-pi`: the framework
growing its own runtime because prose-level control keeps slipping.

## Cost model

Free and open source. Inference cost is whatever your harness charges. Note the chain
runs entirely in the main context (no subagent isolation), so long features accumulate.

## Surprises

1. **The hook executor is the model, and the patches prove it.** #2901 (`bb37b18`,
   2026-06-25): "tell agent to *run* mandatory hooks, not just emit the directive" — the
   model was printing the ceremony block and skipping the hook. #2713 (`7a7843b`):
   compliance was improved by *promoting the section to H2 and using directive language*.
   Enforcement-by-typography is the honest signature of a category with no deterministic
   runtime underneath it.
2. **The constitution wasn't loaded during implementation until 2026-05** (#2460,
   `b4060d5`) — for eight months the governance document governed planning documents but
   not the code being written. Strong evidence for the ceremony-vs-consumer distinction
   (below).
3. **The context-isolation retreat** (#3185, recorded in
   `integrations/claude/__init__.py`): `/speckit.analyze` was given a forked subagent
   context, then reverted because its 300–500-line report re-entered the main
   conversation anyway and each later fork inherited the growing context, compounding
   until the chat froze. A framework betting on intent capture ran head-first into the
   problem GSD bets on — and backed off rather than solving it.
4. **The intent-capture framework rations its questions.** Max 3 clarification markers,
   max 5 clarify questions, "make informed guesses, document assumptions" as the default.
   The delta over a plain agent isn't *asking more* — it's that guesses become recorded,
   reviewable Assumptions instead of silent ones.
5. **Tests are opt-in** (`tasks.md:147`). For a methodology whose artifact chain exists
   to make requirements testable, not generating tests by default is a striking
   concession — presumably to cost/adoption.
6. **"Unit tests for English" is a genuinely novel artifact type**: checklist items are
   prohibited from testing behavior ("Verify/Confirm/Click/render" all banned) and must
   interrogate the spec's own completeness, clarity, consistency, measurability
   (`checklist.md:232-246`). Nothing in GSD corresponds to it.

## Answers to the former open questions

- **How does one definition target 30+ harnesses?** A compile step over placeholder-token
  markdown, driven by ~15-line declarative per-agent configs (dir/format/args/separator).
  Verified in `agents.py` + `integrations/`. The deeper answer: portability is cheap
  because all harnesses converged on prompt-files-as-commands, and the methodology is
  deliberately confined to that lowest common denominator.
- **Where's the line between a `/speckit.*` command and an ordinary prompt template?**
  Thinner than the branding suggests. A command *is* a prompt template plus (a) compiled
  multi-harness distribution, (b) a frontmatter contract (`scripts`, `handoffs`), and
  (c) file-mediated shared state (`specs/NNN-*/`, `.specify/feature.json`,
  `memory/constitution.md`). The "framework" property lives entirely in (c) — prompts
  passing artifacts to prompts. Same refinement-funnel shape as GSD.
- **Does the constitution step do real work, or is it ceremony?** Half and half, and the
  halves separate cleanly. Real: it's a user-authored rule store with two mechanical-ish
  consumers — the plan template's twice-evaluated Constitution Check gate and analyze's
  auto-CRITICAL escalation for violations. Ceremony: the governance wrapper (semantic
  versioning, ratification dates, sync-impact reports, amendment procedures) has no
  consumer anywhere in the chain — nothing reads a constitution version. And all
  enforcement is model-interpreted prose; see surprise 2 for how long a gap in it went
  unnoticed.

## Open questions

- Does the artifact chain's quality margin survive contact with a real task? Exp-01
  showed GSD's margin came from empirical grounding + measured gates — the two columns
  spec-kit is thinnest in. Prediction to test (experiment 02 candidate): spec-kit
  produces better *requirements* and equal-or-worse *code* vs plain, on the same task
  class.
- The `workflows/` engine (deterministic YAML runner) is unread at source level — how
  much of the prose-enforcement problem does it actually solve, and does GateStep check
  anything machine-verifiable?
- `converge.md` and the presets/bundles system (multi-persona: business-analyst,
  product-manager examples) suggest a push beyond dev workflows — unread.
