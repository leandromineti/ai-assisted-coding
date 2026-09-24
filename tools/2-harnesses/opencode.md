---
# PIN MOVED 017a5977d → 545f51d26 (= tag v1.18.32) at the 2026-09-24 release re-read
# (rule 4b: three Opus tracts — release substance by component, per-claim confrontation at
# both pins, provenance — main-session spot-verification; window 561 commits). The
# 2026-08-16 drift check stays dated at its own ref 03bff6500 (a 2026-08-06 commit — the
# clone was ten days stale when it ran; corrected in place). Own-pin defects corrected in place.
name: opencode
category: 2
surfaces: [terminal, desktop, ide]
execution: local
environments: [host]   # RESOLVED 2026-09-24: `packages/containers/README.md:1` reads "# CI containers" — prebuilt GitHub Actions images, five Dockerfiles; not agent isolation, at either pin. The deliberately unset environment_relation is the null case, read rather than assumed
# environment_relation: deliberately UNSET. opencode runs on the host and does nothing
# about isolation — it neither bundles, binds, internalizes, nor inhabits. None of the four
# verbs fits, and forcing one would fabricate a relationship. The null case is evidence for
# the category-3 adjudication, not a gap in the frontmatter.
maker: Anomaly
url: https://github.com/anomalyco/opencode
license: MIT
access: open-source
stack: [TypeScript, Bun, Effect]
version: 1.18.32   # packages/opencode/package.json at the pin — NOT `git describe`: every v1.x release tag is cut on an orphan commit off `dev`, so describe can only ever reach `github-v1.2.25`, the GitHub app's tag from 2026-06-03 (the 2026-07-28 field said v1.2.25 for a product at 1.18.8; corrected 2026-09-24)
commit: 545f51d26
first_commit: 2025-03-21
stars: 209850
stars_at: 2026-09-24   # gh api; 190,554 at 2026-07-28 (+333/day)
read_at: 2026-09-24   # v1.18.32 release re-read (§ Release re-read); deep-dive 2026-07-28 @ 017a5977d, drift-checked 2026-08-16 at 03bff6500 without re-reading (rule 4b) — cited surface nearly frozen (7 of 123 commits, 5 of them release syncs); all claims corroborated; pin deliberately not moved
depth: deep-dive
harness_features:
  mcp: true              # src/mcp/
  lsp: true              # src/lsp/
  hooks: true            # plugin lifecycle triggers, e.g. plugin.trigger("experimental.chat.messages.transform") in prompt.ts
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04 from the deep-dive: no index in-repo; system.ts assembles the prompt from the per-model file, skills, MCP descriptions, permission rules and location context — repo content only ever arrives via tool calls (body § context assembly)
  context_compaction: [llm-summarize, prune]  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: auto-triggered LLM summary of the head (processCompaction, session/compaction.ts; fired from prompt.ts:1319 on overflow, default-on) + a separate token-budget tool-output eraser (prune(), compaction.ts:2010-2050, PRUNE_MINIMUM=20k/PRUNE_PROTECT=40k) that is OPT-IN via compaction.prune: true — no true default in the config schema CITATION CORRECTED 2026-09-24: `compaction.ts:2010-2050` named lines that do not exist (the file is 562 lines at the pin; prune() is :243, its opt-in gate :245 — :273/:275 @ 545f51d26; constants :28-29 both pins); the overflow call is prompt.ts:1321 (:1319 is the `stop` break). CHANGED at v1.18.32: `DEFAULT_TAIL_TURNS = 2` removed — the verbatim tail carried across a compaction is now every turn bounded only by a budget that doubled (`MAX_PRESERVE_RECENT_TOKENS` 8_000 → 15_000, compaction.ts:33), and the summarizer now receives one flattened `[User]:/[Tool result]:` transcript as a single user message rather than model messages (compaction.ts:51-84, :429-446) — § Release re-read 3
  turn_end_gates: false  # 2026-08-18 targeted probe at the pin (not a re-read): the full plugin-trigger surface is 4 triggers (chat.messages/system.transform, shell.env, tool.definition) — none at stop; session/prompt.ts loop exit is plain termination logic, no veto/re-prompt path RECOUNTED 2026-09-24: the plugin-trigger surface is 13 distinct names fired from 30 call sites, 15 declared in packages/plugin/src/index.ts — not 4; the 2026-08-18 probe's single-line regex missed every multi-line `plugin.trigger(\n "name"` call (an upstream issue, #47674, made the identical miscount). VERDICT UNCHANGED: none of the 13 gates turn end; `experimental.compaction.autocontinue` (compaction.ts:500) vetoes the post-compaction auto-continue, not the turn
  tool_approval: policy  # Permission.ask reached PER TOOL, not at dispatch (corrected 2026-09-24): `ctx.ask` is bound to the service at session/tools.ts:81-89 and each tool calls it inside its own `execute` (20 sites); the only direct call site is the doom-loop escalation, processor.ts:372 — a tool that omits the call is ungated. The plugin SDK declares a `"permission.ask"` hook (plugin/src/index.ts:261, `status: ask|deny|allow`) that is fired NOWHERE at either pin — upstream issue #47674 + PR #47675 open since 2026-09-06, unmerged. permission/index.ts is byte-identical across the window; set 2026-08-25 transcribing the category-2 index absorption table's verified instance at this pin, no re-read
  skills: true           # tool/skill.ts + Skill service in system.ts
  subagents: true        # agent/subagent-permissions.ts, task tool
  ptc: true              # 2026-08-18 targeted probe at the pin: packages/codemode/ (confined JS over schema-described host tools) wired as tool/code-mode.ts `execute` tool — EXPERIMENTAL, env-flag-gated default-off (runtime-flags.ts:48 OPENCODE_EXPERIMENTAL_CODE_MODE); third verified PTC instance (ADR-0012)
  plan_mode: tool        # prompt/plan-mode.txt, plan.ts tool PRESENCE ≠ OPERATIVE (2026-09-24, both pins): the plan tool mounts only when `flags.experimentalPlanMode && flags.client === "cli"` (registry.ts:248), and that flag defaults false via OPENCODE_EXPERIMENTAL (runtime-flags.ts:4-14) — default-off and CLI-only
  rules_files: [AGENTS.md, CLAUDE.md, CONTEXT.md]   # session/instruction.ts:64-68 — CLAUDE.md unless the disable flag, CONTEXT.md marked deprecated; globals at :60-63 add <config>/AGENTS.md and ~/.claude/CLAUDE.md. UNDERCOUNT CORRECTED 2026-09-24; the file is byte-identical at both pins
  model_agnostic: true   # 75+ providers via Models.dev — TESTIMONY: "75+" is the project's own docs verbatim (providers.mdx:9), last re-derived upstream 2025-09-02 while the same file's provider sections went 49 → 53 in this window; no in-repo enumeration exists (the catalog is fetched from models.dev at runtime)
  session_sharing: true  # shareable session links (opencode.ai, checked 2026-07-28) Upgraded to SOURCE 2026-09-24: share/session.ts:26-31 → shareNext.create(sessionID) → {url}; config enum manual|auto|disabled; share-next.ts uploads session/message/part data to a remote API — qualifies "stores no code or context server-side" to "unless you share"
  headless_approval: deny  # SET 2026-09-24: `opencode run` replies "reject" to every permission request unless --auto/--yolo/--dangerously-skip-permissions (cli/cmd/run.ts:801-821 @ 545f51d26, same posture at 017a5977d); Permission.ask ends in Deferred.await with no timeout, so an unanswered request would hang rather than fail. The window's ONE functional change to run.ts is a gate bug: subagent permission requests matched no session and hung forever until 08faeb389 (2026-08-20)
---

# opencode

An open-source agent harness that runs in the terminal, as a desktop app, and as an IDE
extension. Among the most-starred agents on GitHub (see frontmatter; hermes-agent passed
it during 2026 — [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1)).
Provider-agnostic by design: 75+ LLM
providers through Models.dev, including local models, plus GitHub Copilot and ChatGPT
Plus/Pro accounts. Stores no code or context server-side (TESTIMONY, enterprise.mdx:11 — and the same docs set says sharing "Syncs your conversation history to our servers", share.mdx:19; the posture holds with sharing off).

Formerly `sst/opencode`; the repo now lives under `anomalyco/`.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

123 commits / 461 files since the read (exact — but at ref `03bff6500`, a **2026-08-06**
commit: the clone was ten days and 95 commits stale when this check ran; corrected
2026-09-24), ~~but **only 7 touch a file this report cites, and 5 of those are
release-version syncs**~~ (*reproduces under no measure: one commit touches a cited
file:line path, five touch the widest reconstruction of the cited surface, and the range
contains zero release commits — corrected 2026-09-24*). The cited surface is close to frozen. Everything
checked is corroborated; nothing is contradicted.

- **Conclusion 1's flagship data point is byte-identical at both ends.** The per-model
  prompt directory holds the same 14 `.txt` files at `017a5977d` and at HEAD — same
  names, no additions, no deletions — of which nine are model-selectable (`anthropic`,
  `beast`, `codex`, ~~`copilot-gpt-5`~~ `meta`, `default`, `gemini`, `gpt`, `kimi`, `trinity`); the
  rest are mode prompts (`plan`, `plan-mode`, `plan-reminder-anthropic`, `build-switch`)
  plus one orphan, `copilot-gpt-5` (*roster corrected 2026-09-24: `meta.txt` is dispatched
  on `muse-spark` at system.ts:28; `copilot-gpt-5.txt` is imported nowhere in the tree at
  either pin — the body's list of nine below was right*). Three weeks on, opencode is still paying the nine-prompt maintenance cost that
  cline paid and abandoned. That is the strongest form this evidence can take: not an
  assertion that the position is *right*, but confirmation that it is still *held*.
- **H3's two chokepoints are intact:** `Permission.visibleTools`
  (`packages/opencode/src/permission/index.ts:216`) still filters the tool list
  pre-decision, `Permission.ask` (`:67`) still gates at call time.
- **H2's opencode half is intact and precise:** `DOOM_LOOP_THRESHOLD = 3`
  (`session/processor.ts:29`) with escalation raised as `permission: "doom_loop"`
  (`:373`) — the loop guard really is routed through the permission subsystem to a human,
  exactly as the report describes. Checked deliberately, because codex's guard was
  verified *absent* on the same day and H2 now rests on the contrast between these two.
- **Not a refactor, despite appearances:** `packages/core/` sits alongside
  `packages/opencode/` with 489 files — and it did at the pin too, identically. Worth
  recording because the two-package layout reads like a fresh extraction and isn't one.

**What a re-read should cost:** low, and it is not due. Of the 123 commits, the ones
landing outside the cited surface are the interesting question, but nothing in this
report currently claims anything about them.

## The distinguishing bet

**That every model needs its own prompt.**

Its competitors are vendor-native harnesses that co-design loop and model. opencode's answer
isn't to write one neutral prompt that works everywhere — it's to keep a *separate system
prompt per model family* and dispatch on the model ID at runtime
(`packages/opencode/src/session/system.ts:27`; `:28` @ 545f51d26). Nine of them, **945** lines total
(`wc -l` over the nine files system.ts imports — *corrected 2026-09-24: the "1256" first
printed here is the total of all fourteen `.txt` files in `prompt/`, mode prompts and the
never-imported `copilot-gpt-5.txt` included; ten prompts, 991 lines at v1.18.32*):
`anthropic.txt`, `gpt.txt`, `codex.txt`, `gemini.txt`, `kimi.txt`, `trinity.txt`,
`meta.txt`, `beast.txt`, `default.txt`.

That's a real wager, and a costly one — every new model family is a prompt to write and
maintain. The claim underneath it is that model-agnosticism is achievable *but not free*,
and that pretending one prompt fits all is where portable harnesses actually lose.

It also quietly contradicts the mid-2026 consensus recorded in
[`README.md`](README.md) that "the models have converged." A team maintaining nine prompts
does not believe that — and the prompts themselves settle how seriously to take it.

### How far apart are they? (measured 2026-07-28, commit `017a5977d`)

Not variants of a shared base. **`anthropic.txt` and `gpt.txt` share exactly zero
substantive lines** — Jaccard 0.00 over lines longer than 20 characters. They are
independently authored documents that happen to drive the same agent loop.

| Pair | Shared lines | Jaccard |
|---|---|---|
| anthropic ∩ gpt | **0** | 0.00 |
| gpt ∩ codex | 10 | 0.09 |
| anthropic ∩ default | 7 | 0.07 |
| anthropic ∩ trinity | 5 | 0.05 |
| trinity ∩ default | 40 | **0.73** |

Every pair except one is near-disjoint. The exception is instructive: **trinity has six
lines `default.txt` lacks — and drops nine that `default.txt` has**, with four more
rewritten (*corrected 2026-09-24: "plus six lines" hid the deletions, and "all six are
serialization constraints" overstated — three are; one is a repeat-tool-call guard, one
routes vague requests to the question tool, one is an example line*); the constraint is — *"Use exactly
one tool per assistant message. After each tool call, wait for the result before
continuing."* A model that can't handle parallel tool calls gets a forked prompt that
forbids them. That's not stylistic variation; that's a capability difference in the model
being papered over in the harness.

The openings show what each file is actually imitating — each mimics the house idiom of
that model's *own vendor harness*:

| Prompt | Opens with |
|---|---|
| `anthropic` | "You are OpenCode, the best coding agent on the planet." |
| `gpt` | "You and the user share the same workspace and collaborate…" |
| `beast` | "please keep going until the user's query is completely resolved…" |
| `gemini` | "an interactive CLI agent specializing in software engineering tasks" |
| `meta` | "You are powered by Muse Spark…" (at v1.18.32: `{{MODEL_NAME}}`, substituted to Muse Spark or Muse Glimmer at system.ts:29-32 — the first templating in the directory) |

`anthropic.txt` reads like Claude Code's own prompt — TodoWrite discipline, tone-and-style
rules, professional-objectivity section, `<system-reminder>` handling. `gpt.txt` reads like
Codex's — `multi_tool_use.parallel`, a mandate to use `apply_patch` for every edit,
dirty-worktree etiquette, and an explicit ban on conversational openers. Substantively
different theories of how to drive an agent, not one theory in two dialects.

**This is strong evidence that opencode's team believes the models haven't converged** —
a model-agnostic harness, with every incentive to write one prompt, concluded it needed
nine, one of which must forbid parallel tool calls outright. But it is one side of a
live disagreement: cline *dismantled* exactly this architecture, and continue never
built it (see the three-way comparison in [`README.md`](README.md)). Practitioner behavior
is split; nobody's position is backed by a published eval.

## Main features

| Feature | Distinctive? |
|---|---|
| 75+ providers via Models.dev, incl. local | Distinctive at this breadth |
| Per-model system prompts | **Unique in this set** |
| Terminal + desktop + IDE from one core | Distinctive |
| LSP integration (`src/lsp/`) | Increasingly table stakes |
| MCP client | Table stakes |
| Skills, subagents, plan mode | Table stakes by mid-2026 |
| Shareable session links, multi-session | Distinctive |
| No server-side code/context storage | Distinctive as a stated posture |

## Stack & repo shape

Bun 1.3.14 (`packageManager`), TypeScript, and **Effect** — the runtime core is written in
Effect-TS (*measured 2026-09-24: 227 of 353 `.ts` in packages/opencode/src and 233 of 316 in
packages/core/src import from `effect`; repo-wide 1,056 of 2,533 — "the whole codebase" was
an overstatement*), with services, `Layer`-based dependency injection, and typed errors rather than plain async/await. UI is
SolidJS with OpenTUI for the terminal; server is Hono; persistence is Drizzle + SQLite;
model calls go through the Vercel AI SDK (`ai@6`).

6347 tracked files: 2533 `.ts`, 1261 `.svg`, 627 `.mdx`, 604 `.tsx` (all five exact at the pin;
6632 / 2727 / 1262 / 627 / 608 at v1.18.32). A monorepo of **32 directories under
`packages/`**, 26 with a `package.json`, 36 workspace members by the root globs (*corrected
2026-09-24: "33-package" reproduced under none of those measures*) — `cli`, `opencode` (the core), `tui`, `desktop`, `web`, `server`, `llm`,
`plugin`, `containers`, `enterprise`, `sdk`, and more.

15215 commits since 2025-03-21.

## Architecture

### Entry point → one full trace

`packages/cli/src/index.ts` — a Bun shebang, 32 lines (*corrected 2026-09-24; byte-identical at both pins*). It builds an Effect runtime, maps
each command to a **lazily imported** handler module, and hands off:

```
index.ts → Runtime.run(Commands, Handlers) → commands/handlers/default
```

Lazy imports mean the CLI only loads the code path you invoked — a startup-time decision
visible right at the entry point.

From a user turn, the path is:

```
SessionPrompt.loop        session/prompt.ts       drives turns until break
  └ SessionProcessor      session/processor.ts    processes ONE provider turn
      └ LLM.stream        packages/llm           provider call
      └ ToolRegistry      tool/registry.ts       resolves + filters tools
      └ Permission.ask    permission/index.ts    gates side effects
  └ Compaction.create     session/compaction.ts  when the turn says so
```

### The agent loop

The loop lives in `session/prompt.ts`; one iteration of it is `session/processor.ts`.

The processor's return type is the most informative line in the codebase:

```ts
// processor.ts:30
export type Result = "compact" | "stop" | "continue"
```

**Compaction is a first-class loop outcome, not an error path.** Running out of context is
modeled as a normal thing that happens, alongside finishing and continuing — the loop
handles it at `prompt.ts:1320-1328` by calling `compaction.create({ auto: true })` (`:1321`;
*citation corrected 2026-09-24 — `:1319` is the `stop` break*) and going
around again.

Termination is a set of explicit `break` conditions rather than a step budget
(`prompt.ts:1290–1330`): a `stop` result, a finish reason outside `tool-calls`/`unknown`,
a provider content filter, or a failure to produce required structured output. The
content-filter branch carries a comment recording the bug it fixed — refusals used to leave
the session silently idle.

**The doom-loop guard** is the sharpest detail here. `DOOM_LOOP_THRESHOLD = 3`
(`processor.ts:29`): if the last three parts are all the same tool with *byte-identical*
JSON input (`processor.ts:356–366`), it doesn't abort — it escalates to the human:

```ts
// processor.ts:372-379 (corrected 2026-09-24; :371 is the preceding agents.get — the drift check's :373 was the accurate pointer; the block is byte-identical at v1.18.32)
yield* permission.ask({ permission: "doom_loop", patterns: [value.name], ... })
```

Treating a stuck agent as a *permission* question rather than a crash is a real design
position: the loop's escape hatch and its safety mechanism are the same subsystem.

### Context assembly

Two files carry it: `session/overflow.ts` (when to compact) and `session/compaction.ts`
(what survives).

```ts
// overflow.ts:8
const COMPACTION_BUFFER = 20_000
```

`usable()` (`overflow.ts:10`) computes the real budget as the model's *input* limit minus a
reserve — 20k tokens by default, configurable via `cfg.compaction.reserved`, and clamped to
the model's max output. `isOverflow()` (`overflow.ts:22`) counts `input + output +
cache.read + cache.write` against it. **Cache reads count toward overflow**, which is the
correct-but-non-obvious choice: cached tokens are cheap, not free of context.

The system prompt is assembled in `session/system.ts` from the per-model file plus skills,
MCP tool descriptions, permission rules, and location context. `session/reminders.ts`
injects mid-conversation reminders, loading `plan.txt`, `build-switch.txt` and
`plan-mode.txt` (`reminders.ts:11-13`) — ~~and there's a `plan-reminder-anthropic.txt`, so even
the *reminders* are model-specific~~ (*corrected 2026-09-24: that file is imported nowhere
in the tree at either pin; the filename was the whole evidence — a filename is weaker
testimony than a docstring, rule 4a in a new shape*).

### Tool surface & permissions

Tools live in `packages/opencode/src/tool/`, each a `.ts` paired with a `.txt`:

```ts
// tool/read.ts:7
import DESCRIPTION from "./read.txt"
```

**Tool descriptions are data, not string literals** — versioned as prose files, diffable
independently of the code that implements them. Bun's native text imports make it free.
For a project whose distinguishing bet is prompt-per-model, keeping prompts out of source
strings is a consistent choice rather than a stylistic one.

On the template's question of whether permission is checked before or after the model
decides, opencode answers **both**:

```ts
// session/llm/request.ts:208-213 — called from :148 (citation corrected 2026-09-24)
function resolveTools(input) {
  const disabled = Permission.disabled(Object.keys(input.tools), Permission.merge(input.agent.permission, input.permission ?? []))
  return Record.filter(input.tools, (_, k) => input.user.tools?.[k] !== false && !disabled.has(k))
}
```

`resolveTools` strips denied tools from the request *before it reaches the model* — a
disallowed tool is invisible, not refused. Then the permission service gates execution at
call time. *(Corrected 2026-09-24: the citation first printed here, `registry.ts:281`
`Permission.visibleTools(yield* mcp.tools(), ruleset)`, sits inside `describeCodeMode`, whose
first statement is `if (!codeMode) return` — the default-off PTC path — and filters MCP tools
only; both `visibleTools` call sites are code-mode paths. The conclusion survived, the
citation did not, and the 2026-08-16 drift check re-affirmed the wrong line. Also true at
both pins: `Permission.ask` is not a dispatch chokepoint — see the `tool_approval` cell —
and the plugin SDK's `"permission.ask"` hook is declared and never fired.)* Hiding rather than refusing avoids spending turns on the model attempting
something it will never be allowed to do.

### Category boundaries in the code

- **category 1 (models):** cleanly abstracted behind `packages/llm` and the AI SDK — *except*
  the per-model prompts, which are a deliberate leak. The abstraction is over the API, not
  over model behavior.
- **category 6 (extensions):** first-class. `src/mcp/`, `src/plugin/`, `tool/skill.ts`,
  `agent/subagent-permissions.ts`.
- **category 3 (execution):** **nothing** — `packages/containers/` is CI build images
  (README:1 "# CI containers", five Dockerfiles; byte-identical at both pins). *Corrected
  2026-09-24: the claim that isolation is "a modeled concern" was wrong at the pin, not
  drift; opencode runs on the host and models isolation nowhere.*

`packages/llm/DESIGN.md` is a **proposed redesign**, not documentation of what's there — a
discussion draft for a public `@opencode-ai/ai` package. Its non-goals are revealing:
permission handling, session history, and durable orchestration are all explicitly *out*.
They're drawing a line between "call a model" and "run an agent."

## Bleed

Category 5 (ships an MCP client, plugin system, skills, subagents) ~~and category 3 (`containers`)~~ (*withdrawn 2026-09-24 — CI images*).
Reaches upward into category 4 too: plan mode with its own prompts (`prompt/plan-mode.txt`,
`plan.txt`, `build-switch.txt`) is process methodology living inside a harness — the same
absorption noted in [`../4-workflow-frameworks/README.md`](../4-workflow-frameworks/README.md).

## Cost model

Free and open source (MIT). You pay for inference against whichever of the 75+ providers you
configure, or bring a Copilot / ChatGPT Plus subscription. Cost shape is therefore whatever
you attach — which is itself the product's position.

## Surprises

1. **Nine per-model system prompts.** Expected one neutral prompt with small adapters. The
   real answer is a maintained prompt per model family, including one for OpenAI's *Codex*
   models specifically. Strongest evidence found so far that the "models have converged"
   claim is overstated.
2. **Compaction is a loop outcome.** `"compact" | "stop" | "continue"` puts running out of
   context on equal footing with finishing. Most designs treat it as an exception.
3. **A stuck agent is a permission prompt.** Doom-loop detection escalates to the human
   through the same channel as "may I delete this file?" rather than erroring out.
4. **Tool descriptions are `.txt` files.** Prompts as versioned data throughout.
5. **Cache reads count toward overflow.** Cheap ≠ absent.
6. **Written entirely in Effect.** An unusual bet for a project this size — worth watching
   whether it helps or just raises the contribution barrier.
7. **Reasoning effort is a chain of per-model-id string matches, and it version-pins**
   (2026-08-26, at this report's pin `017a5977d`, not a re-read of the whole report).
   `ProviderTransform.variants()` in `packages/opencode/src/provider/transform.ts` maps an
   effort name to request params through ~100 lines of `id.includes(...)` branches (80,
   `:721-800`, before the per-SDK switch; measure supplied 2026-09-24) —
   `minimax-m3`, `glm-5.2`, Kimi-on-Anthropic-transports, `grok-3-mini`, then a per-SDK
   switch. GLM's branches match the literal set `["glm-5.2", "glm-5-2", "glm-5p2"]`
   (`transform.ts:725`; `:781` @ 545f51d26, literals unchanged), so **GLM-5.3 matches none of them** and falls to
   `(id.includes("glm") && !glm52) → return {}` (`:779`) — an empty variant map, meaning no
   effort parameter is sent at all. Same short-circuit for `kimi`, `deepseek-*`, `minimax`,
   `qwen`.

   The consequence lands on cost, not correctness, and it lands hardest on exactly the two
   models where it is most expensive: **GLM-5.3 and Kimi K3 are the sweep's only
   default-to-`max` models** (see [`comparisons/models.md`](../../comparisons/models.md) —
   `levels:low/high/max@max` on both). Send no effort parameter and the server applies its
   own default, so those two run at their most expensive setting with no way to step down
   from here. DeepSeek V4 takes the same path but defaults to `high`, so it costs less to
   be wrong about.

   This is not a bug report — sending nothing is defensible, and the request still
   succeeds. It is the **verified instance** that `tools/1-models/glm-5.3.md` surprise #3
   predicted in the abstract on 2026-08-26 (*"version-pinning behavior worth remembering
   when a harness hardcodes thinking params"*), scored the same day: prediction landed,
   mechanism as described, on the first harness checked. Found via
   [issue #39](https://github.com/leandromineti/ai-assisted-coding/issues/39); verified at
   the pin with `git show 017a5977d:…` after the clone was found sitting on drifted HEAD
   (`03bff6500`) — the finding holds at both.

## Release re-read — v1.18.32 (2026-09-24; pin 017a5977d → 545f51d26)

Three Opus tracts (release substance by component · per-claim confrontation at both pins ·
provenance), load-bearing claims re-run in the main session. Window
`git rev-list --count 017a5977d..v1.18.32` = **561** (515 first-parent, 11 merges — a
squash shop), `git diff --stat -- packages` 933 files, +110,638 / −12,045. **The tag is an
orphan**: `545f51d26` is one release-bump commit off `origin/dev` at `f5ce4f881`
(2026-09-21), contained in no branch, with `dev` re-absorbing the bump as a separate
"sync release versions" commit — drift arithmetic must use the merge-base. 24 releases in
55 days (one every 2.3 days), patch-only, 14 in the first 28 days and 10 in the last 29;
commits 12.1/day → 7.7/day across the same split. Authors: `opencode-agent[bot]` 200 of
561 (35.7%; 104 housekeeping, **96 real fixes and features** landed under the bot identity
with the human in a trailer) + the release bot 24; top five humans 40%; 60 authors. AI-named
trailers: **4 of 561** — a trailer-counting method reads this repo as 0.7% agent-assisted
and the committer identity says 35.7%. Stars 190,554 → 209,850; 4,669 open issues, 1,571
open PRs.

**1. The bet was raised.** `gpt-astra.txt` (46 lines) joined as the **tenth**
model-selectable prompt (`5cd8e68fd`, 2026-09-08, "port Astra system prompt from v2";
`system.ts:11`, dispatched for `gpt-6` at `:36`), disjoint from all three of its GPT
siblings under the report's own Jaccard measure (0/0.00 against `gpt`, `codex`,
`anthropic`), and the five measured pairs reproduce 5-for-5 at the new pin because
`anthropic`, `gpt`, `default` and `trinity` are byte-identical across the window. Two
months on, a model-agnostic harness added a prompt instead of generalizing one. The
counter-signal: `meta.txt` went the other way — `{{MODEL_NAME}}` templating serves a second
Meta model (`system.ts:29-32`), the first templating in the directory; and the Kimi branch
now matches `providerID` too (`:45-49`). The bet is per model *family*, and its cost at these
two pins was one file added, one edited, twelve untouched.

**2. The permission engine did not change by a byte.** `permission/index.ts` blob
`2e27ff24…` at both pins (`Permission.ask` `:67`, `visibleTools` `:216`); so did
`overflow.ts`, `instruction.ts`, `reminders.ts`, `runtime-flags.ts`, `share/*`, `skill/`,
`lsp/`, `ide/`, `containers/` and the plugin SDK. 110,638 insertions landed almost entirely
in i18n (`packages/app/src/i18n` 19 → 65 locales), `console` and `stats` — the hosted
surfaces, 27% of the window and in none of the 24 release notes. What the confrontation
found instead were defects at the report's own pin: `Permission.ask` is per-tool, not a
dispatch chokepoint; the "answers both" citation was dead code on the default path; the
plugin `"permission.ask"` hook has never fired (upstream #47674/#47675, open since
2026-09-06); the plugin-trigger surface is 13, not 4; `containers/` is CI images. Two new
gate-adjacent mechanisms, neither a gate: the one functional change to `opencode run` in
the window fixed subagent permission requests **hanging forever** on an unanswered
`Deferred` (`08faeb389`, 2026-08-20) — a loop⇄gate bug; and `Orchestrate`-style
introspection did not appear here, but `tool/task.ts:213-223` now fails a crashed subagent
loudly where the old pin returned an empty string.

**3. Compaction was rebuilt.** `DEFAULT_TAIL_TURNS = 2` deleted — the verbatim tail across
a compaction is now every turn, bounded by a budget that doubled (`MAX_PRESERVE_RECENT_TOKENS`
8,000 → 15,000) and estimated lazily per retained turn; the summarizer receives one
flattened `[User]:`/`[Tool result]:` transcript as a single user message instead of model
messages; `buildPrompt` in `packages/core` wraps the conversation and the prior summary in
tags and states the lossiness to the model outright ("anything you do not carry into the
new summary is lost", `SUMMARY_UPDATE_INSTRUCTIONS`); `select()` stopped splitting
mid-message. `SUMMARY_TEMPLATE`'s fixed five sections (Objective / Important Details /
Work State / Next Move / Relevant Files) answer the old open question "what does compaction
keep". Auto-compaction still default-on (`overflow.ts:28`), prune still opt-in
(`compaction.ts:275`). New: the harness logs when Anthropic silently drops signed thinking
blocks because "opencode changed history behind a signed block" (`processor.ts:438-451`)
and asks for `prefixMismatchBehavior: "drop_block"` (`transform.ts:706`) — a harness
instrumenting its own context churn against provider-side state.

**4. Release notes vs. tree.** All 24 bodies are generated from merged PRs with a
contributor block; four claims spot-checked all land in the tree. One rule-8 inversion
inside a single vendor: the v1.18.32 note says Bedrock image attachments are hoisted
"only for Claude, Nova, and Llama 4"; the commit subject (`c10134729`) says "except"; the
source (`message-v2.ts:151-155`) is an allowlist — the note was right, the engineer's own
summary wrong.

**5. Provenance defects in the report, corrected in place.** The `version:` field named a
different product (`git describe` can only reach the GitHub app's tag; the product was
1.18.8); the 2026-08-16 drift check ran on a ref ten days older than its date; "1256 lines"
was the 14-file directory total; "33-package" reproduced under no measure; three prompt
files are orphans (`copilot-gpt-5.txt` 143 lines, `plan-reminder-anthropic.txt` 67,
`tool/plan-enter.txt`), two of which generated wrong claims.

**6. The re-read's own audit.** Counts stated with a measure: **14 of 14** reproduced at
the pin (the five Jaccard pairs, the trinity-minus-default six, 123/461, the 14 files, the
489 core files, the loop and compaction constants, 15,215 commits, the five file counts).
Without a measure: **2 of 9** ("75+" — a docs quote — and "~100 lines"; failed: 1256, 33,
31, "7 of 123 / 5 syncs", "4 triggers", "each .ts paired", "the whole codebase"). The
repo's split, again. Citation hygiene: two off-by-one line pointers, one citation into
a dead branch, one claim (containers) inferred from a package name, one from a filename.

**Predictions, scored at the next re-read (dated, falsifiable).**
- **P-1.** On **2026-12-01**, `git grep -c -F '"permission.ask"' origin/dev` returns exactly
  **1** (the declaration) and PR #47675 is still unmerged. Falsified by a second hit or a
  merge. Measures whether a documented-but-dead security-path hook gets closed when the fix
  is free; the backlog (1,571 open PRs) is the bet.
- **P-2.** On **2026-12-01**, `packages/opencode/src/session/prompt/` holds **16 or 17**
  `.txt` files (14 → 15 in 55 days; GPT-6 Sol/Luna already on `dev`). ≤15 = the bet is
  being abandoned; ≥18 = accelerating.
- Next trigger: the first **v1.19.0** minor (24 patches without a minor bump in the window),
  or 2026-12-01, whichever first.

## Open questions

- ~~Do the nine prompts actually diverge in strategy, or is it cosmetic reformatting?~~
  **Answered 2026-07-28** — zero shared lines between `anthropic.txt` and `gpt.txt`. See
  the measurement above. This finding produced an upstream report: the per-model dispatch
  is an undocumented confound in akitaonrails/llm-coding-benchmark
  ([issue #12](https://github.com/akitaonrails/llm-coding-benchmark/issues/12),
  [PR #13](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)) — bespoke
  prompts for Claude/GPT/Gemini/Kimi vs `default.txt` for DeepSeek/Qwen/GLM/Grok et al.,
  in a table read as a model-capacity ranking.
- Are the prompts *derived* from each vendor's published harness prompts, or independently
  arrived at? The stylistic mimicry is strong enough to ask. `git log` on
  `prompt/anthropic.txt` might show whether it was written at once or accreted.
- Does each prompt measurably outperform `default.txt` on its own model? Nine prompts is a
  large maintenance bet with, as far as the repo shows, no eval backing it. *Re-priced
  2026-09-24: in 561 commits the cost was one file added and one edited by two template
  lines; 13 of 14 prompt files are byte-identical. The bet is cheaper to hold than "costly
  wager" implied — and it was paid again anyway (§ Release re-read 1).*
- **Does `gpt-astra.txt` reach anyone?** (added 2026-09-24) Its gate is
  `model.api.id.includes("gpt-6")`; whether any models.dev entry matched at the tag is a
  registry question, not a source one. GPT-6 Sol/Luna landed on `dev` 2026-09-22.
- **Is the per-tool `ctx.ask` pattern complete?** (added 2026-09-24) Twenty call sites
  were enumerated; nobody has audited every side-effecting `Tool.define` for a missing one.
- **What is `packages/app`?** (added 2026-09-24) 192 files and 51.5% of the window's
  insertions went into a package this report never names, while the agent package took
  6.2%; `v2-compat.ts` (449 lines, new) is a v2-config → v1 migration shim — the
  "transitional?" question now has a handle.
- What does compaction *keep*? `overflow.ts` decides when; `compaction.ts` decides what, and
  that's where the real context-engineering position lives. Not yet read.
- `DOOM_LOOP_THRESHOLD = 3` and `COMPACTION_BUFFER = 20_000` are unexplained constants.
  Tuned empirically, or guessed and never revisited? `git log` on those lines would say.
- Recent history is dominated by large refactors — a typed application layer graph,
  event-sourced session inputs, an Effect logging migration. A rewrite appears to be in
  progress; how much of what's described here is transitional?
- The lazily-imported command handlers suggest startup time was a real problem. Was it Bun,
  or the Effect `Layer` graph?
