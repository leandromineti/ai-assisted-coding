---
name: pi
category: 2
surfaces: [terminal]  # TUI (packages/tui, differential rendering); RPC/JSON modes are local headless control, not a surface
execution: local  # no async-remote: packages/server (unix-socket, experimental, runServer unimplemented) + packages/client are latent scaffolding, unreachable from the shipped CLI
environments: [host]  # runs with the launching user's permissions; no worktree/container machinery in-product (containerization is advisory docs)
# environment_relation deliberately UNSET — the null case is the finding: pi ships no sandbox and no
# environment abstraction, recommends external containerization in docs (README ## Permissions & Containerization).
# The template says leave it unset when none of bundle/bind/internalize/inhabit fits; that null is data.
maker: Earendil Works
url: https://github.com/earendil-works/pi
license: MIT
access: open-source
stack: [TypeScript, Node]
version: v0.84.3-20-g8fa7eebd2
commit: 8fa7eebd2
first_commit: 2025-08-09
stars: 97226
stars_at: 2026-08-26
read_at: 2026-08-26
depth: deep-dive
harness_features:
  mcp: false             # checked and absent: no MCP client anywhere (grep modelcontextprotocol over packages/{coding-agent,ai,agent}/src → 0; the one "MCP" token is a comment naming MCP bridges as a hypothetical image source). ai-memory's "pi via hooks+MCP" claim was made at ai-memory's pin — MCP would ride an extension, not core. STRENGTHENED 2026-08-27 at this same pin (no re-read, prompted by the aider read's MCP work): the surface is now the whole tree, not three src dirs, and the subject STATES the refusal — README.md:498 under ## Philosophy, "**No MCP.** Build CLI tools with READMEs, or build an extension that adds MCP support", linking an argued rationale; docs/usage.md:308 "intentionally does not include built-in MCP". Dependency-scan trap recorded: @modelcontextprotocol/sdk IS in package-lock.json but purely TRANSITIVELY (required by @google/genai) — no pi package.json declares it, so a manifest scan reports MCP where source and docs both deny it. README.md:394's "MCP server integration" is in a "What's possible" list of things EXTENSIONS can build, not a shipped feature
  lsp: false             # checked and absent: no LSP client, no vscode-languageserver/jsonrpc/tree-sitter/ast-grep dependency (two independent reader greps → 0 files each)
  hooks: true            # 34-event extension lifecycle system (types.ts:1237-1279), 14 with a blocking/modifying return contract; dispatch is ordered + first-block-wins + fail-closed (runner.ts:936-950). DEFAULT-OFF: the only default-mounted extension (llama.cpp) registers zero handlers
  turn_end_gates: hook   # DEFAULT-OFF: an extension agent_end handler can queue a follow-up and force another turn (agent-session.ts:1125-1127), but the handler has NO return contract (no {block,reason}); the engine-grade shouldStopAfterTurn seam exists in pi-agent-core but the CLI never assigns it (referenced only in packages/agent tests)
  tool_approval: false   # checked and absent (README:40 states it; grep confirm|approve|permission over core/tools/*.ts → 0): no ask-before-execute, no allowlist gate at dispatch. The SECOND verified absent after dsh — but a different shape: dsh replaces it with a compiled sandbox, pi replaces it with NOTHING (runs as the launching user; the --tools/--exclude-tools flags are launch-config, not runtime approval; --approve gates project-local FILE trust, not tool calls)
  skills: true           # full SKILL.md / Agent Skills standard (skills.ts:355-381), 6 discovery roots incl. cross-tool ~/.agents/skills and documented ~/.claude/skills / ~/.codex/skills interop; name+description in prompt, body read on demand; DEFAULT-ON
  subagents: false       # checked and absent from the product: 8 built-in tools (read bash powershell edit write grep find ls), no Task/spawn tool. Present only as an example extension (process-isolated pi subprocesses, 8 parallel/4 concurrent, NO depth cap, NO budget), manually symlinked to activate
  ptc: false             # checked and absent: no sandboxed code-execution channel (grep pyodide|quickjs|isolated-vm|code_execution|codemode → 0). Agent-authored extension TypeScript runs in-process via jiti, but that is authored-then-/reload plugin code with no sandbox, not a per-turn code tool
  plan_mode: false       # checked and absent from the product; example extension only (examples/extensions/plan-mode, built entirely on the public API: setActiveTools + a tool_call block hook + [DONE:n] scraping)
  rules_files: ["AGENTS.override.md", "AGENTS.md", "CLAUDE.md"]  # 5 candidates incl. .MD casings (resource-loader.ts:72); first match per directory; walked to FILESYSTEM ROOT with no cap and NO trust gate (contrast the sibling .agents/skills walk, which stops at git root); --no-context-files to disable, DEFAULT-ON
  model_agnostic: true   # BYO-model by design: pi-ai is a unified multi-provider client (32 API adapter files, ~9 distinct families: OpenAI/Anthropic/Google/Mistral/Bedrock/xAI/OpenRouter/Copilot/Codex); 40 providers, 7 with OAuth. Default provider google, but no privileged default vendor in the loop. Maker Earendil Works has no category-1 model stake (Radius is a gateway, not weights)
  session_sharing: true  # /share POSTs the session JSONL (system prompt + full tool schemas included) to radius.pi.dev at visibility=organization when a Radius credential exists (session-share.ts:113), else a private gh gist rendered at pi.dev/session/; /export writes HTML/JSONL locally. Vendor-hosted share links exist — but org-visible under a "secret gist"-labelled command
  evals: true            # model-backed behavioral eval harness on vitest-evals (real AgentSession vs a live provider, LLM/rubric judge) — small: 2 suites / 2 cases (grep describeEval → 2). The substantive one A/Bs the self-extension system prompt. Software tests are separate and not counted
  learning_loop: false   # checked and absent as an AUTONOMOUS path: no memory tool, no background/spawned writer, no subagent. BUT the highest self-authorship ceiling in the tracked set — see the report: agent-written skills/extensions/SYSTEM.md land in ~/.pi/agent/ and auto-load in every future session with no trust gate and no permission system; human-invited ("ask it to build one"), not self-initiated
---

# Pi

Deep-dive 2026-08-26, three readers at the pin (Tract C ran a second reader and
self-corrected), one tract per ADR-0021 component — **all three components traced**:
the loop, context assembly, and the permission gate. Claims below carry file:line at
`8fa7eebd2` (v0.84.3-20, committed 2026-08-25). Executes [issue #28](https://github.com/leandromineti/ai-assisted-coding/issues/28)
(registered 2026-08-19 at README level; sighted four times as an integration target —
gsd-core, haft, ai-memory, mem0 — before registration). npm-artifact run probe:
`@earendil-works/pi-coding-agent@0.84.3`, the tag 20 commits behind the pin.

## What it is

Earendil Works' "self-extensible coding agent" — a TypeScript TUI harness
(`pi-coding-agent`) sitting on published SDK packages (`pi-agent-core` runtime,
`pi-ai` multi-provider client, `pi-tui`). It is simultaneously a usable product and a
kit, which is why it is category 2 and not an excluded SDK (the membership test:
`pi-coding-agent` is a shipped, installable, documented CLI, not an SDK demo). Its
governing design choice is subtractive: **it ships no permission system, no sandbox,
no MCP, and a stock loop with zero active interception points**, and leans the entire
safety story on external containerization plus an extension API through which the user
(or the agent) adds back whatever they want.

## The distinguishing bet

**"Everything is an extension, and the agent can write its own" — a narrow-waist (H8)
harness taken further than any tracked peer, and the wager cuts both ways.** The core
loop is deliberately minimal (four default tools — `read`, `bash`, `edit`, `write`;
no budget, no loop detection, no gate), and capability arrives as data: 34 lifecycle
events, model-provider registration, CLI-flag registration, whole-prompt replacement,
per-call message rewriting — all reachable from a loaded extension
(`packages/coding-agent/src/core/extensions/types.ts:1237-1323`). The "self" in
self-extensible is literal: the default system prompt ships pi's own extension-API
docs *inside the installed package* and points the model at them
(`system-prompt.ts:138-145`), so "ask it to build a skill/extension" is a documented
workflow, and the project evals exactly that (`packages/evals/src/extensions.eval.ts`).

The bet's cost is the finding: an agent that authors its own loadable extensions,
skills, or a whole-prompt-replacing `SYSTEM.md` — with **no permission system, no path
containment, and no trust gate on the user-global directory** — is a self-modification
mechanism with higher authority than any memory product this repo tracks. Pi resolves
the hermes cache-vs-self-modification tension not by preventing it but by **quantising
it to session boundaries**: within a session the agent's writes are inert until a
human `/reload`; across the boundary they load wholesale.

## Stack & repo shape

5,804 commits · 1,408 tracked files · `ts(1167) md(97) json(47)` (repo-facts.sh,
2026-08-26). pnpm monorepo `packages/{agent,ai,client,coding-agent,evals,protocol,
server,session-backends,telemetry,tui}`. Two harness trees coexist: the **operative**
one is `packages/coding-agent/src/core/*` (the shipped CLI path via `AgentSession`);
`packages/agent/src/harness/*` is a **v4 rewrite whose `AgentHarness` throws
`HarnessNotImplemented` on every operation** (`agent-harness.ts:219-235, 365-407`) and
has one non-test consumer — the class the project is named after is designed-but-unwired
at this pin. Authorship: 297 all-time authors, Mario Zechner 65% all-time but **third
over the last 30 days** behind Christian Klotz and Armin Ronacher — a funded
multi-engineer team (six humans at 69–131 commits/month) with a founder-heavy history
and a gated-community contribution model (new-contributor issues/PRs auto-closed
against a 261-name allowlist). ~690 commits / 5 releases per 30 days: this pin degrades
fast.

## Architecture — the traced loop *(deep-dive 2026-08-26)*

- **The stock loop has zero active gates.** Entry `cli.ts:21` → `main.ts` →
  `InteractiveMode.run()` → `while(true){ getUserInput(); session.prompt() }`
  (`interactive-mode.ts:1177`) → `AgentSession._runAgentPrompt` (`agent-session.ts:1085`)
  → `Agent.prompt` → `runLoop` (`packages/agent/src/agent-loop.ts:155-275`, an outer
  `while(true)` around an inner tool-call loop). The only default-mounted extension is
  a hidden llama.cpp provider that registers **no** lifecycle handlers
  (`extensions/llama/index.ts`), so `beforeToolCall` short-circuits and the loop runs
  ungated.
- **No budget, no loop detection, anywhere.** `grep` for
  `maxTurns|maxSteps|maxIterations|turnLimit|maxToolCalls` over all `packages/*/src`
  → **0**; loop-detection identifiers → **0**. A stock `pi` iterates as long as the
  model keeps emitting tool calls, bounded only by provider errors, default-on
  auto-compaction, and Ctrl+C. Consistent with the no-permission philosophy, but it
  means the autonomy ceiling is set entirely by the (absent) environment bounds.
- **Turn-end gate `hook`, default-off.** An extension `agent_end` handler can queue a
  follow-up message that makes the session re-enter the loop
  (`agent-session.ts:1125-1127` → `agent.continue()`), but the handler has **no return
  contract** — no `{block, reason}` veto like Claude Code's Stop or gemini-cli's
  AfterAgent; it must construct the re-prompt itself. The engine-grade
  `shouldStopAfterTurn` seam exists in `pi-agent-core` and is unit-tested, but the CLI
  **never assigns it** (all four non-core references are `packages/agent` test files) —
  unmounted, verified by grep.
- **Hooks are real, 34 events, 14 blocking/modifying, fail-closed** (`emitToolCall`
  deliberately does not catch handler exceptions and the session rethrows "Extension
  failed, blocking execution"), first-`block:true`-wins across ordered extensions
  (`extensions/runner.ts:936-950`). But default-off: nothing mounts a handler in a
  stock run.
- **Subagents, plan mode: absent from the product, present as shipped-unmounted
  examples.** 78 example extensions ship in the npm tarball; **exactly one auto-loads**
  (llama). The subagent example spawns process-isolated `pi --mode json -p
  --no-session` subprocesses (8 parallel / 4 concurrent) with **no depth cap and no
  cost budget** — activated only by a manual symlink. Plan mode is 390 lines of
  example built entirely on the public API.
- **PTC absent; dispatch parallel by default** (`Agent.toolExecution: "parallel"`),
  falling to sequential if any tool declares it. Tool failures are always encoded as
  results, never thrown out of the loop. A genuine correctness nicety: on
  `stopReason === "length"` the whole tool batch is failed unexecuted, because streamed
  arguments finalized by a salvage JSON parser can schema-validate while silently
  truncated (`agent-loop.ts:207-214`).
- **Evals are model-backed and self-referential**: `packages/evals` runs a real
  `AgentSession` against a live provider with a rubric judge — 2 suites, 2 cases; the
  substantive one A/Bs whether the self-documentation prompt sections make the model
  successfully author a working extension.
- **No async-remote.** `packages/server` (unix-socket, CBOR) is self-labelled
  experimental, its `runServer` is an unimplemented interface method, and nothing in
  the CLI imports it; `--mode rpc` is *local* headless control. The remote-session
  machinery (`packages/{protocol,client}`) is scaffolding for a future the CLI does not
  yet take.

## Context assembly — minimal prefix, best-in-set cache discipline *(deep-dive 2026-08-26)*

- **One shared system prompt, ~1.4 KB, zero model/family branching** — the convergence
  pole alongside dsh. A multi-provider client covering ~9 API families with a single
  prompt body and no family-conditional prose is a strong vote in the tracked
  "have the frontier models converged?" question. Notably, **8 of the prompt's 18
  skeleton lines are about operating pi itself** (pointers to its bundled README/docs/
  examples); only 2 guidelines are unconditional and neither is about coding — coding
  guidance is delegated to tool descriptions and the user's `AGENTS.md`.
- **Rules files: `AGENTS.md`/`CLAUDE.md`, walked to the filesystem root, ungated by
  trust.** 5 candidates, first match per directory, `~/.pi/agent/` then every ancestor
  with no depth cap and no size cap (`resource-loader.ts:72, 140-152`). `AGENTS.md` is
  **absent** from the trust-required resource list (`trust-manager.ts:30-38`) — cloning
  a hostile repo and running `pi` loads its `AGENTS.md` into the system prompt with no
  prompt. The adjacent `.agents/skills` walk *does* stop at the git root: same
  codebase, opposite containment discipline, and the unbounded walk is the ungated one.
- **Skills: full `SKILL.md` / Agent Skills standard**, 6 discovery roots (two of them —
  `~/.pi/agent/skills`, `~/.agents/skills` — ungated), progressive disclosure
  (name+description in prompt, body read on demand), documented `~/.claude/skills` and
  `~/.codex/skills` interop. This is gsd-core's install surface: global skills or
  prompt-templates (`/name` with `$ARGUMENTS` substitution), no `.claude/`-style command
  dir and no subagent-definition format to port onto.
- **No memory subsystem, no repo map, no index, no embeddings.** File-into-context is
  model-driven search (the default four tools shell out; `grep`/`find` are opt-in and
  bind ripgrep/fd). `packages/agent/src/search/*` is *session-transcript* search, not
  file search, and has zero consumers in the shipped CLI — a stricter cousin of Warp's
  calibration case: it feeds nothing and was never about files.
- **Cache discipline is the strongest observed in this repo, and it is instrumented.**
  The system prompt is deliberately clock-free (no date/OS/git/model — only cwd), so
  the prefix is stable by construction; `cache_control` is default-on at 3–4 correct
  Anthropic breakpoints (stable-prefix + moving-tail), with cross-provider cache keys
  for OpenAI/Bedrock/Mistral; summarization requests explicitly set
  `cacheRetention: "none"` with a documented rationale
  (`compaction.ts:587-593`); deferred tool loading is chosen to protect the prefix,
  **with the residual leak documented in pi's own docs** (a tool activation that
  rebuilds the prompt invalidates the prefix even where the provider supports deferred
  schemas). The distinctive part: **pi measures its own cache waste and shows the user
  the dollar figure inline** — `Cache miss after 12m idle: 84.2k tokens re-billed
  (~$0.31)` in the transcript by default, plus a cumulative re-billed total in
  `/session` (`cache-stats.ts`, `interactive-mode.ts:3825-3839`). No other tracked
  harness instruments its own cache economics.
- **Compaction: default-on, absolute-reserve trigger** (`contextTokens > contextWindow
  − 16384`), which floats to ~98% on a 1M-window model; keeps a **fixed 20k-token
  tail** (not a fraction), same-model summarization into a 6-section template.
  Pre-cut tool results are **deleted, not summarized** — the model's only disclosure is
  a bare "history was compacted" line plus a path list drawn from `read`/`write`/`edit`
  only (files touched by `bash`/MCP/extension tools never appear).

## Permission model — there isn't one *(deep-dive 2026-08-26)*

**`tool_approval: false` — the second verified absent in the tracked set, and a
different shape from the first.** README states it (`README.md:40`); grep for
`confirm|approve|permission` over `core/tools/*.ts` returns **0**. In a stock run,
`bash`, `write`, and `edit` dispatch **unprompted**, running with the full permissions
of the launching user and inheriting the full shell environment (`bash` scrubs only
pi's own `PI_*` session vars — every `*_API_KEY` passes through). The category-2
absorption table's `process_gates` row claimed approval-at-dispatch was universal
machinery; **dsh was the first counterexample (2026-08-24) and pi is the second — but
they diverge on what replaces it**: dsh substitutes a compiled per-call OS sandbox
(the gate moved down a level), whereas **pi substitutes nothing** and defers to external
containerization by policy. Two absents, two different philosophies; the axis is now
firmly discriminating, not a near-uniform ✓.

The launch-config knobs are real but are not a gate: `--tools`/`--exclude-tools`/
`--no-tools` set which tools exist at startup, and `--approve`/`--no-approve` trusts
project-local *files* (extensions/skills/settings) for the run — neither asks before a
tool call. Project trust is folder-granular, boolean, remembered
(`~/.pi/agent/trust.json`), and **content-unhashed**: trust a repo once and every
`.pi/extensions/*.ts` written into it afterwards — including one the agent wrote —
loads silently next session.

**Boundary test inverts (no gate → what affects the agent's own authority?), and the
answer is: a great deal, through the extension/config surface, ungated.**

- **The agent's `write` tool has no path containment.** It can write
  `~/.pi/agent/skills/x/SKILL.md` (auto-loaded, description injected into every future
  prompt in every project), `~/.pi/agent/extensions/x.ts` (arbitrary in-process
  TypeScript executed at every future startup), or `~/.pi/agent/SYSTEM.md` (**total
  system-prompt replacement**) — none of the three passes a trust check or a permission
  prompt (`package-manager.ts:2470-2500`, `resource-loader.ts:1029-1032`). Activation
  is the one brake: a human `/reload` or restart — and a shipped example
  (`reload-runtime.ts`) is a recipe for removing even that.
- **Extensions read every provider credential.** The `ModelRegistry` handed to every
  loaded extension exposes `getApiKeyForProvider(provider)` → the raw key, for all 40
  providers, with no capability scoping (`model-registry.ts:115-124`).
- **`auth.json` is a code-execution vector by design.** Config values support a leading
  `!command` executed via `execSync` (`resolve-config-value.ts:6,16`), so a model that
  can write that file (it can) plants a command that runs whenever a credential
  resolves.
- **Credentials are hardened, transcripts are not.** `auth.json` is written `0600` in a
  `0700` dir with lockfile concurrency; session JSONL and HTML exports get no `chmod` at
  all (umask default) — pi's threat model treats credentials as sensitive and
  conversations, which embed file contents and the system prompt, as not.

## Environment relationship & surfaces

**`environment_relation` deliberately unset — the null case, and it is the point.** Pi
ships no sandbox, no worktree machinery, no container launcher, and no
environment-detection code; it runs on the bare host as the launching user and
**recommends external containerization in docs** as the entire isolation story
(`README.md ## Permissions & Containerization`). Against codex/dsh (internalize) and
gemini-cli (internalize+bundle+bind+inhabit, all default-off), pi is the clean opposite
pole: not "confinement shipped but dormant" but "confinement is your problem, here is
the advice." Autonomy (principle E1) is therefore *entirely* environment-determined —
the gate factor is 1. Surfaces: terminal TUI only; RPC/JSON are local headless control.

Providers: BYO-model by design (`model_agnostic: true`) — ~9 API families, 40
providers, 7 with OAuth (5 of them *subscription* auth). Default provider `google`, but
no privileged vendor in the loop; maker Earendil Works holds no category-1 weights, so
pi is the **non-vendor pole** of the harness roster — which makes the next finding
sharper.

## The Claude Code impersonation — the data-instrument note from the other side *(2026-08-26)*

tool-taxonomy.md records "who a harness's maker is at category 1 predicts what the harness
collects", tracked from the *vendor* pole (Cursor→Grok, hermes trajectory export). Pi
supplies the **non-vendor mirror image, and it is an authenticity finding rather than a
collection one.** On Anthropic **OAuth** credentials (i.e. a Claude Pro/Max
subscription, not an API key), pi-ai:

- prepends `"You are Claude Code, Anthropic's official CLI for Claude."` as the first
  system block, demoting pi's own prompt to `system[1]`
  (`anthropic-messages.ts:1010-1024`);
- **renames pi's tools to Claude Code's 2.x tool names** from a public prompt-history
  scrape, under the source comment *"Stealth mode: Mimic Claude Code's tool naming
  exactly"* (`anthropic-messages.ts:76-105`);
- sends `anthropic-beta: claude-code-20250219,oauth-2025-04-20`
  (`anthropic-messages.ts:936`).

This bears directly on this repo's standing note that **subscription auth is for
official clients only** (the opencode PR #18186 memory): here is a third-party harness
engineered to be indistinguishable from the official client to the vendor's own
billing surface, keyed on auth mode, and `docs/security.md` does not mention it. It is
the strongest single reason to treat pi's `model_agnostic: true` as carrying an
asterisk — the seam is genuinely provider-neutral, but one provider path is neutral by
impersonation.

## Run probe — 2026-08-26

Probe target: `@earendil-works/pi-coding-agent@0.84.3` (dist-tag `latest`, published
2026-08-24), the tag 20 commits behind the pin (`git rev-list --count v0.84.3..pin` =
20). Node v22.23.2; success read from output, not exit status (5e).

- **Install: 128 packages in 8 s, 136 MB** — no npx trap, 20 direct deps. The package
  ships `dist/` + full `docs/` + 78 example extensions + a bundled llama extension.
- **Boots**: `pi --version` → `0.84.3`, exit 0. No-auth headless (`HOME=fakehome pi -p`)
  fails loud — "No API key found… Use /login" — **exit 1**, not a 5e specimen.
- **The `--help` surface corroborated three source claims at the artifact**: plan mode
  is announced as an *extension* flag ("--plan from plan-mode extension"); a built-in
  extension package manager (`pi install/remove/update/list/config`); and a credential
  broker (`pi auth print-api-key`, `print-bearer-token --provider openai-codex` — prints
  provider tokens "for an external client"). Rules-file kill switch `--no-context-files`
  confirms `AGENTS.md`/`CLAUDE.md` as the loaded names.
- No scored agent run: no credentials on this box and no free tier — omit-with-reason.

## Bleed

- **category 1↔2**: the non-vendor pole (no first-party weights) — but with the
  OAuth-impersonation seam above, which reaches *into* a category-1 vendor's billing
  identity rather than being reached by it. A new shape for the maker-span discussion:
  not integration, but authenticity spoofing.
- **category 6**: the whole product is an extension host. Consumes the SKILL.md /
  Agent Skills standard and documents cross-tool interop (`~/.claude/skills`,
  `~/.codex/skills`); has no MCP client, so the one convention it *doesn't* speak is the
  one the extensions bucket is named for. gsd-core installs into it as skills/prompts.
- **category 5**: `learning_loop: false` as an autonomous path, but the self-authorship
  ceiling (agent-written auto-loading skills/extensions/SYSTEM.md, ungated) is higher
  than any tracked memory product's write authority — a data point that the
  "continuity across harnesses" pitch of category 5 is, here, absorbed as raw
  filesystem authorship with no admission control.
- **category 3**: the null relation — confinement declined, delegated to the user. The
  autonomy-ceiling-is-environment claim (category-3 scope note) in its purest form: pi
  is a harness whose safety is *defined* to live in category 3.

## Cost model

BYO-provider: metered per-token against whichever of 40 providers holds a credential,
or subscription auth via 7 OAuth flows (5 subscription: Claude Pro/Max, ChatGPT
Plus/Pro, Copilot, xAI, Kimi). No pi-hosted inference and no pi subscription; Radius is
Earendil's own gateway/share endpoint, not a required path. The distinctive cost
behavior is instrumentation, not price: pi is the only tracked harness that shows the
user a running dollar figure for cache misses.

## Surprises

1. **The class the project is named after is a throwing stub.** `AgentHarness` rejects
   every operation with `HarnessNotImplemented`; the operative runtime is the older
   `Agent` class. A package-tree survey would report features (v4 hooks incl.
   `before_run_end`) that do not run.
2. **Ships 78 extensions, mounts one, and the one it mounts has no hooks.** The stock
   loop has literally zero active interception points; every "pi feature" a survey
   would list (plan mode, subagents, permission gates, git checkpointing, sandboxing)
   is default-off shelf stock.
3. **No permission system and no path containment, with a self-authoring agent** — the
   write tool reaches `~/.pi/agent/SYSTEM.md` (replaces the whole prompt) and
   `~/.pi/agent/extensions/*.ts` (arbitrary in-process code at every startup), ungated.
4. **Anthropic OAuth = impersonating Claude Code**, by a source comment that says so
   ("Stealth mode: Mimic Claude Code's tool naming exactly") — the non-vendor pole
   reaching into a vendor's official-client identity.
5. **`/share` uploads at `visibility=organization`** under a command labelled "secret
   GitHub gist" — the largest label-vs-behavior gap in the read; the payload includes
   the system prompt and every tool schema.
6. **`--auth-token` is a second silently-inert shipped auth control** after gemini-cli's
   dropped safety checker — parsed, typed, validated, unit-tested, and read by nothing.
   Two independent instances make it a category-level hazard: *a flag's presence in
   `--help` is not evidence of a consumer*.
7. **Best-in-set cache discipline paired with the latest-firing compaction** — clock-free
   prefix, default-on breakpoints, and an inline dollar-denominated cache-miss meter,
   yet compaction waits until ~98% on a 1M model and then discards ~98% of context in
   one step.
8. **Two ancestor walks, opposite stopping rules** — `AGENTS.md` to the filesystem root
   ungated; `.agents/skills` to the git root; the unbounded walk is the ungated one.

## Open questions

- **The silently-inert-flag pattern is now two-for-two** (gemini-cli's dropped checker,
  pi's `--auth-token`). Proposed standing addition to the deep-dive recipe: for any
  gate-shaped flag or config key, grep for its *consumer*, not its definition — an
  absence claim needs the consumer trail. (Recorded to the pattern memory.)
- Does the CLI ever repoint at the v4 `AgentHarness`/`packages/agent/src/harness`
  tree? Dated prediction to score at re-read: by **2027-02-28** the shipped interactive
  path still constructs sessions through `packages/coding-agent/src/core/session-manager.ts`
  (v3), *or* it has cut over and `CURRENT_SESSION_VERSION ≥ 4`. The reader predicts the
  cutover happens; either way it is checkable with one grep.
- Does `--auth-token` acquire a consumer, or `runServer` an implementation? Either would
  wake the latent remote surface and move `execution` off pure `local`. One-line greps
  at the next drift check.
- `tool_approval` now has two absents with two philosophies (dsh sandbox, pi nothing) —
  is there a third shape, or does the axis bifurcate cleanly into "sandbox-instead" vs
  "containment-is-your-problem"? Watch pi-adjacent minimal harnesses.
- MCP absent at this pin, but ai-memory/mem0 ship pi integrations — do those ride an
  extension that adds an MCP client, making pi's MCP support a category-6 artifact
  rather than a harness feature? (Consistent with the taxonomy's "the runtime is a
  category-2 feature" line — here the runtime is simply absent and outsourced.)
  *(Partly answered 2026-08-27 at this same pin, no re-read.)* The route the question
  posits **exists and is named in-tree**: `test/settings-manager-bug.test.ts:45,52,53`
  uses `npm:pi-mcp-adapter` as its example package, and the README directs users to
  "build an extension that adds MCP support" (`:498`). So MCP support for pi *is* a
  category-6 artifact by the maker's own design, not merely by omission — pi is the
  clean specimen for "the harness declines the protocol and the ecosystem supplies it".
  What remains open is the narrower half: whether the specific ai-memory/mem0
  integrations take that route, which needs a read at *their* pins, not pi's.
