---
name: opencode
category: 2
surfaces: [terminal, desktop, ide]
execution: local
environments: [host]   # a `containers` package exists; its role unverified — see Bleed
# environment_relation: deliberately UNSET. opencode runs on the host and does nothing
# about isolation — it neither bundles, binds, internalizes, nor inhabits. None of the four
# verbs fits, and forcing one would fabricate a relationship. The null case is evidence for
# the category-3 adjudication, not a gap in the frontmatter.
maker: Anomaly
url: https://github.com/anomalyco/opencode
license: MIT
open_source: true
stack: [TypeScript, Bun, Effect]
version: github-v1.2.25-1492-g017a5977d
commit: 017a5977d
first_commit: 2025-03-21
stars: 190554
stars_at: 2026-07-28
read_at: 2026-07-28   # drift-checked 2026-08-16 at 03bff6500 without re-reading (rule 4b) — cited surface nearly frozen (7 of 123 commits, 5 of them release syncs); all claims corroborated; pin deliberately not moved
depth: deep-dive
harness_features:
  mcp: true              # src/mcp/
  lsp: true              # src/lsp/
  hooks: true            # plugin lifecycle triggers, e.g. plugin.trigger("experimental.chat.messages.transform") in prompt.ts
  turn_end_gates: false  # 2026-08-18 targeted probe at the pin (not a re-read): the full plugin-trigger surface is 4 triggers (chat.messages/system.transform, shell.env, tool.definition) — none at stop; session/prompt.ts loop exit is plain termination logic, no veto/re-prompt path
  tool_approval: true    # Permission.ask at tool dispatch; set 2026-08-25 transcribing the category-2 index absorption table's verified instance at this pin, no re-read
  skills: true           # tool/skill.ts + Skill service in system.ts
  subagents: true        # agent/subagent-permissions.ts, task tool
  ptc: true              # 2026-08-18 targeted probe at the pin: packages/codemode/ (confined JS over schema-described host tools) wired as tool/code-mode.ts `execute` tool — EXPERIMENTAL, env-flag-gated default-off (runtime-flags.ts:48 OPENCODE_EXPERIMENTAL_CODE_MODE); third verified PTC instance (ADR-0012)
  plan_mode: true        # prompt/plan-mode.txt, plan.ts tool
  rules_files: [AGENTS.md]   # session/instruction.ts
  model_agnostic: true   # 75+ providers via Models.dev
  session_sharing: true  # shareable session links (opencode.ai, checked 2026-07-28)
---

# opencode

An open-source agent harness that runs in the terminal, as a desktop app, and as an IDE
extension. Among the most-starred agents on GitHub (see frontmatter; hermes-agent passed
it during 2026 — [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1)).
Provider-agnostic by design: 75+ LLM
providers through Models.dev, including local models, plus GitHub Copilot and ChatGPT
Plus/Pro accounts. Stores no code or context server-side.

Formerly `sst/opencode`; the repo now lives under `anomalyco/`.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

123 commits / 461 files since the read, but **only 7 touch a file this report cites, and
5 of those are release-version syncs**. The cited surface is close to frozen. Everything
checked is corroborated; nothing is contradicted.

- **Conclusion 1's flagship data point is byte-identical at both ends.** The per-model
  prompt directory holds the same 14 `.txt` files at `017a5977d` and at HEAD — same
  names, no additions, no deletions — of which nine are model-selectable (`anthropic`,
  `beast`, `codex`, `copilot-gpt-5`, `default`, `gemini`, `gpt`, `kimi`, `trinity`); the
  rest are mode prompts (`plan`, `plan-mode`, `plan-reminder-anthropic`, `build-switch`,
  `meta`). Three weeks on, opencode is still paying the nine-prompt maintenance cost that
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
(`packages/opencode/src/session/system.ts:27`). Nine of them, 1256 lines total:
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

Every pair except one is near-disjoint. The exception is instructive: **trinity is
`default.txt` plus six lines**, and all six are serialization constraints — *"Use exactly
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
| `meta` | "You are powered by Muse Spark…" |

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

Bun 1.3.14 (`packageManager`), TypeScript, and **Effect** — the whole codebase is written in
Effect-TS, with services, `Layer`-based dependency injection, and typed errors rather than plain async/await. UI is
SolidJS with OpenTUI for the terminal; server is Hono; persistence is Drizzle + SQLite;
model calls go through the Vercel AI SDK (`ai@6`).

6347 tracked files: 2533 `.ts`, 1261 `.svg`, 627 `.mdx`, 604 `.tsx`. A **33-package
monorepo** — `cli`, `opencode` (the core), `tui`, `desktop`, `web`, `server`, `llm`,
`plugin`, `containers`, `enterprise`, `sdk`, and more.

15215 commits since 2025-03-21.

## Architecture

### Entry point → one full trace

`packages/cli/src/index.ts` — a Bun shebang, 31 lines. It builds an Effect runtime, maps
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
handles it at `prompt.ts:1319` by calling `compaction.create({ auto: true })` and going
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
// processor.ts:371
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
injects mid-conversation reminders — and there's a `plan-reminder-anthropic.txt`, so even
the *reminders* are model-specific.

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
// registry.ts:281
const tools = Permission.visibleTools(yield* mcp.tools(), ruleset)
```

`visibleTools` (`permission/index.ts:216`) filters the tool list *before it reaches the
model* — a disallowed tool is invisible, not refused. Then `Permission.ask` gates execution
at call time. Hiding rather than refusing avoids spending turns on the model attempting
something it will never be allowed to do.

### Category boundaries in the code

- **category 1 (models):** cleanly abstracted behind `packages/llm` and the AI SDK — *except*
  the per-model prompts, which are a deliberate leak. The abstraction is over the API, not
  over model behavior.
- **category 6 (extensions):** first-class. `src/mcp/`, `src/plugin/`, `tool/skill.ts`,
  `agent/subagent-permissions.ts`.
- **category 3 (execution):** a `containers` package exists, so isolation is a modeled concern
  rather than an assumption of the host.

`packages/llm/DESIGN.md` is a **proposed redesign**, not documentation of what's there — a
discussion draft for a public `@opencode-ai/ai` package. Its non-goals are revealing:
permission handling, session history, and durable orchestration are all explicitly *out*.
They're drawing a line between "call a model" and "run an agent."

## Bleed

Category 5 (ships an MCP client, plugin system, skills, subagents) and category 3 (`containers`).
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
   effort name to request params through ~100 lines of `id.includes(...)` branches —
   `minimax-m3`, `glm-5.2`, Kimi-on-Anthropic-transports, `grok-3-mini`, then a per-SDK
   switch. GLM's branches match the literal set `["glm-5.2", "glm-5-2", "glm-5p2"]`
   (`transform.ts:725`), so **GLM-5.3 matches none of them** and falls to
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
  large maintenance bet with, as far as the repo shows, no eval backing it.
- What does compaction *keep*? `overflow.ts` decides when; `compaction.ts` decides what, and
  that's where the real context-engineering position lives. Not yet read.
- `DOOM_LOOP_THRESHOLD = 3` and `COMPACTION_BUFFER = 20_000` are unexplained constants.
  Tuned empirically, or guessed and never revisited? `git log` on those lines would say.
- Recent history is dominated by large refactors — a typed application layer graph,
  event-sourced session inputs, an Effect logging migration. A rewrite appears to be in
  progress; how much of what's described here is transitional?
- The lazily-imported command handlers suggest startup time was a real problem. Was it Bun,
  or the Effect `Layer` graph?
