---
name: opencode
layer: 2
surfaces: [terminal, desktop, ide]
execution: local
environments: [host]   # a `containers` package exists; its role unverified — see Bleed
vendor: Anomaly
url: https://github.com/anomalyco/opencode
license: MIT
open_source: true
stack: [TypeScript, Bun, Effect]
version: github-v1.2.25-1492-g017a5977d
commit: 017a5977d
first_commit: 2025-03-21
stars: 190554
stars_at: 2026-07-28
read_at: 2026-07-28
depth: deep-dive
features:
  mcp: true              # src/mcp/
  lsp: true              # src/lsp/
  hooks: true            # plugin lifecycle triggers, e.g. plugin.trigger("experimental.chat.messages.transform") in prompt.ts
  skills: true           # tool/skill.ts + Skill service in system.ts
  subagents: true        # agent/subagent-permissions.ts, task tool
  plan_mode: true        # prompt/plan-mode.txt, plan.ts tool
  rules_files: [AGENTS.md]   # session/instruction.ts
  model_agnostic: true   # 75+ providers via Models.dev
  session_sharing: true  # shareable session links (opencode.ai, checked 2026-07-28)
---

# opencode

An open-source agent harness that runs in the terminal, as a desktop app, and as an IDE
extension. The most-starred agent on GitHub (~190k). Provider-agnostic by design: 75+ LLM
providers through Models.dev, including local models, plus GitHub Copilot and ChatGPT
Plus/Pro accounts. Stores no code or context server-side.

Formerly `sst/opencode`; the repo now lives under `anomalyco/`.

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
[`index.md`](index.md) that "the models have converged." A team maintaining nine prompts
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
built it (see the three-way comparison in [`index.md`](index.md)). Practitioner behavior
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
Effect-TS, with services, layers, and typed errors rather than plain async/await. UI is
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

### Layer boundaries in the code

- **Layer 1 (models):** cleanly abstracted behind `packages/llm` and the AI SDK — *except*
  the per-model prompts, which are a deliberate leak. The abstraction is over the API, not
  over model behavior.
- **Layer 3 (extensions):** first-class. `src/mcp/`, `src/plugin/`, `tool/skill.ts`,
  `agent/subagent-permissions.ts`.
- **Layer 5 (execution):** a `containers` package exists, so isolation is a modeled concern
  rather than an assumption of the host.

`packages/llm/DESIGN.md` is a **proposed redesign**, not documentation of what's there — a
discussion draft for a public `@opencode-ai/ai` package. Its non-goals are revealing:
permission handling, session history, and durable orchestration are all explicitly *out*.
They're drawing a line between "call a model" and "run an agent."

## Bleed

Layer 3 (ships an MCP client, plugin system, skills, subagents) and layer 5 (`containers`).
Reaches upward into layer 4 too: plan mode with its own prompts (`prompt/plan-mode.txt`,
`plan.txt`, `build-switch.txt`) is process methodology living inside a harness — the same
absorption noted in [`../04-workflow-frameworks/index.md`](../04-workflow-frameworks/index.md).

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
  or the Effect layer graph?
