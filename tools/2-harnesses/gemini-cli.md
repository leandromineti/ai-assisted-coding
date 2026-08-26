---
name: gemini-cli
category: 2
surfaces: [terminal, ide]  # ide = ACP mode (packages/cli/src/acp/, docs/cli/acp-mode.md) + VS Code companion (context/diff feed, not a loop host)
execution: local  # a2a-server can SERVE the loop to remote callers but is experimental and consumed by nothing in-repo — see Architecture
environments: [host, container, worktree]  # container = docker/podman/runsc/lxc/windows-native (sandboxConfig.ts:26-33); worktree experimental, default false (settingsSchema.ts:2234-2243)
environment_relation: internalize  # primary verb; bundle/bind/inhabit streaks + the default-off caveat in the Environment section
maker: Google
url: https://github.com/google-gemini/gemini-cli
license: Apache-2.0
access: open-source
stack: [TypeScript, Node, Ink]
version: v0.49.0-preview.0-117-g64b5b79a6
commit: 64b5b79a6
first_commit: 2025-04-15
stars: 106681
stars_at: 2026-08-25
read_at: 2026-08-25
depth: deep-dive
harness_features:
  mcp: true              # client: stdio + SSE + streamable-HTTP (mcp-client.ts:16-22); per-server trust/allow/exclude + per-tool + annotation-matched policy rules (policy/config.ts:566-601); MCP OAuth subsystem; untrusted folders refuse stdio servers entirely
  lsp: false             # checked and absent: no LSP client or dependency; the VS Code companion and ACP are bespoke agent protocols, zero diagnostics plumbing
  hooks: true            # 11 lifecycle events incl. BeforeModel/AfterModel/BeforeToolSelection (hooks/types.ts:43-55), Command + Runtime types, blocking decision vocabulary, per-project trust file; mechanism default-ON, event arrays default empty
  turn_end_gates: hook   # AfterAgent can halt (continue:false) or re-prompt (decision:'block', stop_hook_active retry contract — Claude Code's Stop-hook shape byte-for-byte) at client.ts:973-1035, default-armed/empty; an ENGINE-grade next-speaker gate exists but is default-OFF (config.ts:1279); subagents get an engine gate default-ON (complete_task enforcement, local-executor.ts:362-374)
  tool_approval: true    # default decision ASK_USER interactive / DENY headless when no rule matches (policy-engine.ts:291-293), via a ~12.8k-line priority-tiered TOML policy engine; folder trust force-resets any non-DEFAULT mode
  skills: true           # SKILL.md convention, 6-root precedence incl. the cross-tool .agents/skills dirs (skillManager.ts:54-99), two-stage load (metadata in prompt, body via activate_skill), 2 builtins shipped
  subagents: true        # invoke_agent tool, markdown+YAML defs in .gemini/agents/, isolated tool/prompt registries + derived message bus, compiled depth cap of exactly 1 (local-executor.ts:192-197), 30-turn/10-min defaults
  ptc: false             # checked and absent: no sandboxed runtime where model code drives tools; grep "codeExecution *:" over packages/ → 0 product hits; only defensive handling of the Gemini API part types
  plan_mode: true        # ApprovalMode.PLAN, default-enabled tools (config.ts:1135); enforcement is policy data not prose — plan.toml catch-all deny + read-only allows; exit_plan_mode is a human checkpoint; an approved plan routes execution to Flash
  rules_files: ["GEMINI.md", "MEMORY.md"]  # GEMINI.md (configurable list) + private per-project MEMORY.md; AGENTS.md NOT loaded by default (repo-wide grep: docs example + test fixture only); three-tier placement model, JIT subdirectory loading via tool output
  model_agnostic: false  # checked: all six AuthType routes end at a Google backend or Gemini-protocol endpoint; GATEWAY swaps the host, not the wire format (@google/genai client throughout)
  session_sharing: false # no share links anywhere; local JSON export (exportSessionCommand.ts:20,72) + resume/checkpoints exist — artifact yes, link no
  evals: true            # 37 behavioral .eval.ts (ls evals/*.eval.ts | wc -l) with LLM-as-judge + self-consistency voting, ALWAYS/USUALLY_PASSES reliability tiers, 4 eval CLIs — explicitly distinguished from its unit tests
  learning_loop: false   # checked: the autonomous write path exists (background "confucius" extractor agent) but is default-OFF (experimental.autoMemory=false) AND propose-and-commit — patches land in an .inbox nothing auto-applies, extracted skills are written outside the skill-discovery path; same verified-✗ shape as Warp's
---

# Gemini CLI

Deep-dive 2026-08-25, three readers at the pin, one tract per ADR-0021 component —
**all three components traced**: the loop, context assembly, and the permission gate.
Claims below carry file:line at `64b5b79a6` (main, commit-dated 2026-08-25; release
tags live on branches, so `git describe` anchors v0.49.0-preview.0 while
`package.json` says 0.59.0-nightly). **The pin was moved** from the stub's
bef611950 (read 2026-07-28) — deliberate: the stub asserted repo shape only, no
experiment coherence was at stake, and the Antigravity transition makes currency the
value here. Stub claims re-verified at both ends: `.tsx` 418→418, `.ts` 1726→1738,
tracked 2933→2997, so nothing the stub said is contradicted by the move.

## What it is

Google's vendor-native terminal harness: an Ink/React TUI (`packages/cli`) over a
published core library (`packages/core`), driving Gemini models through six Google-only
auth routes. Mid-2026 positioning said "the long-context harness"; the source says
something else (see the bet). At this pin it is simultaneously a well-engineered,
eval-cultured harness and a product whose own maker is migrating users off it — the
migration to Antigravity CLI ships *inside* the product as a builtin skill and an
undismissable server-controlled banner.

## The distinguishing bet

**The stub's pre-registered bet is falsified.** The stub predicted (2026-07-28) that
Gemini CLI bets on "a large enough context window makes retrieval strategy
irrelevant", testable as markedly simpler context assembly than peers. The source
shows close to the opposite: one of the most elaborate context-management stacks in
the tracked set, oriented entirely around *conserving* context —

- a system-prompt "Context Efficiency" doctrine guarded by a committed
  benchmark-regression warning: *"You must run the major benchmarks, such as
  SWEBench, prior to committing any changes to the Context Efficiency section"*
  (`packages/core/src/prompts/snippets.ts:209-212`);
- the "stuff everything in" flag (`--all-files`) removed outright
  (`docs/changelogs/index.md:842`; zero source hits);
- retrieval done by **delegation, not index**: the builtin `codebase_investigator`
  subagent (read-only tools, 50 turns, on Flash) is "the primary mechanism for
  initial discovery", with the motive stated in the prompt: *"Your own context window
  is your most precious resource… use sub-agents to 'compress' complex or repetitive
  work"* (`snippets.ts:290, 735`);
- embeddings are **dead code** — `generateEmbedding` has zero production callers
  (10 grep hits: 1 definition, 9 in its own test file); no repo map, no index. The
  only real retriever in the picture is **server-side RAG** the CLI merely observes
  (`metadata.ragStatus`/`snippets` with relevance scores on the response stream,
  `packages/core/src/core/turn.ts:326-357`) and never queries or injects.

What the source actually bets on: **aggressive context management + model-driven
search + subagent compression**, plus a second wager no peer makes this way — **an
eval-cultured, policy-data-driven harness**: 37 behavioral evals with LLM-as-judge
scoring, and a permission gate that is a ~12.8k-line rule engine reading TOML policy
files rather than either prose or hardcoded checks.

## Stack & repo shape

6,389 commits · 2,997 tracked files · `ts(1738) tsx(418) md(168)` (repo-facts.sh,
2026-08-25). npm workspaces: `packages/{cli,core,a2a-server,sdk,test-utils,
vscode-ide-companion}` — core is a genuinely consumed library (four in-repo
dependents plus a documented third-party SDK, `packages/sdk/README.md:1-40`), not an
organizational split. `evals/` at root is a separate vitest project. The monthly
commit histogram is the platform story in one row (`git log --since=2026-01-01
--date=format:'%Y-%m' --format='%ad' | sort | uniq -c`):

| 2026-01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 |
|---|---|---|---|---|---|---|---|
| 610 | 588 | 682 | 376 | 233 | 49 | 48 | 58 |

A ~93% collapse from the March peak, sustained since June — yet nightly/preview/stable
release trains ran daily through the pin date (0.57.0 promoted to `latest` on
2026-08-25 itself), and security/auth fixes still land. Maintenance mode with an
in-flight succession, not abandonment. 13 of the 68 drift-window commits are
`[SSR Agent] Issue Fix (NNNNN)` — Google's own autonomous agent maintaining the repo —
and one window commit implements an **Antigravity** runner for the maintenance bot
(`c5622fec2`): the successor product already maintains the incumbent.

## Architecture — the traced loop *(deep-dive 2026-08-25)*

- **Iteration is client-side**, split between core and three drivers: `Turn.run` →
  `GeminiChat.sendMessageStream` does the model round-trip
  (`packages/core/src/core/turn.ts:284`), while the tool loop belongs to the caller
  (`packages/cli/src/nonInteractiveCli.ts:316-620` `while(true)`; the React driver
  `useGeminiStream.ts`; the SDK's `legacy-agent-session.ts`).
- **Turn-end gate, grade `hook` — and it is Claude Code's Stop-hook shape
  byte-for-byte.** The `AfterAgent` hook fires exactly at turn end (only when no
  tool calls are pending, only at the outermost frame); `continue:false` halts,
  `decision:'block'` **re-prompts the model** with the hook's reason, passing
  `stop_hook_active` (`packages/core/src/core/client.ts:973-1035`; input type
  `{prompt, prompt_response, stop_hook_active}`,
  `packages/core/src/hooks/types.ts:588-592`). Default-armed, ships empty. Exit
  codes: 0 allow, 1 allow+warn, **anything else → deny**
  (`hooks/hookRunner.ts:537-560`).
- **The signature auto-continue is default-OFF.** `checkNextSpeaker` — the
  engine-grade "who speaks next?" LLM probe that injects "Please continue." — is
  fully implemented and wired, but `skipNextSpeakerCheck` defaults `true`
  (`config/config.ts:1279`; `settingsSchema.ts:1137`). Any claim that "gemini-cli
  auto-continues its turns" is false at this pin. Subagents keep an engine gate,
  default-ON: a silent turn without `complete_task` is a protocol violation that
  forces a compiled warning turn (`agents/local-executor.ts:362-374, 747-790`).
- **Hooks are a full subsystem**: 9,069 lines (`wc -l packages/core/src/hooks/*.ts`),
  **11 events** (`BeforeTool, AfterTool, BeforeAgent, Notification, AfterAgent,
  SessionStart, SessionEnd, PreCompress, BeforeModel, AfterModel,
  BeforeToolSelection` — `hooks/types.ts:43-55`), Command (subprocess) + Runtime
  (in-process) types, per-project trust file (`trustedHooks.ts:22-31`), and a
  shipped **Claude Code hooks migrator** (`packages/cli/src/commands/hooks/migrate.ts`)
  mapping `Stop`→`AfterAgent` — with the now-stale comment "Gemini doesn't have
  sub-agents" in a tree shipping 22,430 lines of `agents/`. An `AfterTool` hook can
  even **inject a replacement tool call** (`tailToolCallRequest`,
  `scheduler.ts:776-813`) — a user script can rewrite what the model believes a tool
  did.
- **Subagents: depth cap exactly 1, structural.** `invoke_agent` + markdown/YAML
  definitions (`.gemini/agents/`, hashed and acknowledged before registration);
  each child gets a fresh tool registry with **every `Kind.Agent` tool silently
  dropped** — *"We do not allow agents to call other agents"*
  (`local-executor.ts:192-197`). No depth counter exists; nesting is 1, always.
  Defaults 30 turns / 10 minutes (`agents/types.ts:51,56`). Five invocation backends
  including remote A2A agents.
- **No default step budget; loop-detection is the guard.** `maxSessionTurns`
  defaults **-1 = unlimited** (`config.ts:1243`); `MAX_TURNS = 100` bounds only
  recursive continuations. Loop detection (default-ON) triggers on 5 identical tool
  calls / 10 repeated chunks / LLM check after turn 30 — and the **first** detection
  is a coaching re-prompt ("take a step back…"), only the second aborts
  (`client.ts:747-763, 1270-1298`).
- **Dispatch is parallel by default and the model opts out per call**:
  `wait_for_previous` is injected into every tool schema
  (`tools/tools.ts:535-558`) and taught in the prompt — the inverse of
  harness-decides-parallelism. Tool failures return as `functionResponse` errors and
  the loop continues (`scheduler/tool-executor.ts:451-476`).
- **Plan mode is policy, not prose**: `ApprovalMode.PLAN` + a catch-all `deny` TOML
  with narrow read-only allows; plan-file writes pass only ten hand-written
  `argsPattern` regexes; `exit_plan_mode` is a human checkpoint, and an approved
  plan threads into the system prompt, the compression prompt, *and model routing*
  (approved plan → execution on Flash,
  `routing/strategies/approvalModeStrategy.ts:78-94`).
- **`a2a-server` (the stub's open question): it serves gemini-cli's own loop as a
  remote A2A agent** — same `sendMessageStream` server-side with GCS-persistable
  task state — but nothing in-repo consumes it, its esbuild target is allowed to
  fail (`esbuild.config.js:182-184`), and its README calls it experimental. The
  CLI's own execution stays local; the mirror-image A2A *client* lets it call remote
  agents as subagents.
- **`evals: true` is real and self-aware**: `evals/README.md` distinguishes "does
  the model *choose* to write?" from integration tests; LLM-as-judge with
  self-consistency voting (`evals/llm-judge.ts:29-70`), reliability tiers
  (`ALWAYS_PASSES | USUALLY_PASSES | USUALLY_FAILS`), per-attempt reliability
  telemetry, four eval CLIs.

## Context assembly — conservation, tiers, and a shipped-but-unmounted pipeline *(deep-dive 2026-08-25)*

- **Two prompt bodies, switched by model *family*** — modern (gemini-3+/custom,
  26,309 chars measured from the committed snapshot) vs legacy (18,705 chars) —
  `promptProvider.ts:82`, `models.ts:493-496`. Flash and Pro get byte-identical
  prompts (verified by md5 over snapshot blocks). Position on the per-model-prompt
  spectrum: between dsh's one and codex's per-slug. Escape hatches:
  `GEMINI_SYSTEM_MD` replaces the whole prompt; every section individually killable.
- **Rules files: `GEMINI.md`, not `AGENTS.md`.** Repo-wide grep finds `AGENTS.md`
  only as a docs example and a test fixture — a notable hold-out from the
  convergence every tracked peer joined. Discovery is upward-only to the `.git`
  boundary; **subdirectory context loads JIT**, appended to the output of the five
  fs tools that touch the directory (`jit-context.ts:45-65`), not at startup.
- **An explicitly documented three-tier cache layout**
  (`environmentContext.ts:62-66`): global memory → system instruction; extension +
  project memory → first user message; subdirectory memory → tool output. This is a
  deliberate cache decision (volatile content kept out of the prefix; JIT content
  append-only), with one consciously-taken correctness-over-cache trade documented
  in source (mid-session memory saves rebuild the system instruction,
  `config.ts:2576-2577`). No explicit `cachedContent` is ever created — the design
  target is Gemini's implicit caching; cache hits are measured and displayed but
  never manufactured.
- **Two default-on features break the append-only property the layout protects**:
  tool-output **masking** rewrites history in place every turn once ~80k tokens of
  prunable tool output accumulate (`toolOutputMaskingService.ts:50-66`,
  `client.ts:1262-1264`) — the hermes cache-vs-self-modification tension in its
  sharpest local form, unacknowledged in-tree; and the agent-writable
  `[Active Topic:]` system-prompt tail, which turns out to be **inert** — the
  `update_topic` tool never triggers the rebuild that reads it (presence ≠
  operative inside a single feature).
- **Compaction (operative path): LLM summarization at 50% of the window**,
  preserving the newest 30%, spilling oversized tool outputs to temp files past a
  50k budget, with a self-correction probe turn and snapshot chaining
  (`chatCompressionService.ts:41-471`); the `<state_snapshot>` prompt admits the
  stakes: "it will become the agent's *only* memory of the past".
- **A full graph-based context pipeline ships dark**: ~15 modules, 8 registered
  processors, 3 tuning profiles, hysteresis, live token calibration —
  `experimental.contextManagement` default `false` (`config.ts:1199`). Reading the
  directory would produce a completely wrong characterization of what runs. One of
  its profiles is described in the schema as "less cache friendly" — the only place
  in the tree where cache-friendliness is named as an axis.
- **Memory: the famous `save_memory` tool was deleted, and the prompt announces
  it** — *"There is no `save_memory` tool"* (`snippets.ts:859`); persistence is now
  ordinary file edits into a four-tier routing policy (global/project/private
  GEMINI.md/MEMORY.md). The autonomous path (`experimental.autoMemory`, default
  off) is a background Flash extractor agent ("confucius") whose writes are
  **code-jailed** to an `.inbox` (`config.ts:3361-3371`), where nothing auto-applies
  and extracted skills land *outside* the skill-discovery roots until a human
  promotes them via `/memory inbox` — the most cautious autonomous write path in
  the tracked set.
- **Skills: SKILL.md, two-stage, cache-friendly** — metadata in the prompt, body via
  `activate_skill` into tool output; six roots including the cross-tool
  `.agents/skills` convention; workspace skills gated on folder trust; **two
  builtins ship: `skill-creator` and `antigravity-support`** (see the transition
  section).
- **The untrusted-data wrap is narrower than the prompt claims**: Core Mandates
  assert external tool/MCP outputs are wrapped in `<untrusted_context>`, but only
  `shell`, `mcp-tool`, and `web-fetch` wrap — file contents read from an untrusted
  repo reach the model unlabelled, and MCP server *instructions* are concatenated
  into the trusted `<project_context>` channel (`memoryContextManager.ts:123-130`).

## Permission model — a policy engine, with two model-shaped doors *(deep-dive 2026-08-25)*

**`tool_approval: true`, engine-grade.** The gate is a dedicated ~12.8k-line
subsystem (`wc -l packages/core/src/policy/*.ts`): decisions
`ALLOW | DENY | ASK_USER`, modes `PLAN < DEFAULT < AUTO_EDIT < YOLO`, default
decision **ASK_USER interactive / DENY headless** (`policy-engine.ts:291-293`).
Rules ship as **TOML data in the package** — 38 `[[rule]]` blocks across 9 files —
on a five-tier precedence (Admin > User > Workspace > Extension > Default) encoded
as fractional priorities. Statically-denied tools are additionally removed from the
schema the model ever sees (`policy-engine.ts:934-1010`). Session "always allow"
exists but **refuses blanket grants** for shell-class tools without a command
prefix or args pattern (`policy/config.ts:734-738`). Folder trust is a hard clamp:
untrusted folders force-reset any non-DEFAULT mode ("you cannot YOLO in an
untrusted directory"), force ASK on git commands, and refuse stdio MCP servers.
Argument-aware shell heuristics upgrade 28 known-safe commands to ALLOW and
downgrade dangerous ones — with unusually careful validation (`git -c` treated as
dangerous because it can execute code; `sed` limited to `-n Np`;
`commandSafety.ts:151-268, 341-410`).

**Boundary test (can the model influence the gate?): yes, twice — both contained,
one previously broken.**

- **`additional_permissions`** — a genuinely model-authored permissions field on the
  shell tool (request network or extra fs paths after a sandbox denial), the
  structural analogue of Warp's `is_risky`. Contained three ways: absent from the
  schema unless the sandbox is on (off by default), out-of-workspace paths force
  ASK_USER at the engine, and the shell tool unconditionally prompts on any use
  (`shell.ts:280-282`). Two honest cracks: the engine-level check inspects only fs
  paths — **a model-authored `{network: true}` passes the engine untouched** and is
  saved only by the tool-level prompt (`policy-engine.ts:744-764`); and in YOLO the
  override is skipped, so the sandbox is model-dissolvable there.
- **CONSECA** — an LLM writes the security policy (Flash generates a per-prompt
  least-privilege policy; a second Flash call adjudicates each tool call against
  it, `safety/conseca/policy-generator.ts:19-73`, `policy-enforcer.ts:19-39`).
  Expected to be the crack; it is not: safety checkers are **structurally one-way**
  — only DENY and ASK_USER are honored, a checker returning ALLOW changes nothing,
  a throw becomes DENY (`policy-engine.ts:768-816`) — and it is default-off.
  Model-generated policy that can only tighten is a materially better design than
  Warp's, worth naming as a pattern.
- **The gate failed silently once, fixed one day before this pin.** `write.toml`
  nested its `[rule.safety_checker]` under a key the schema silently drops, so in
  `autoEdit` mode the workspace-confinement checker on `write_file`/`replace`
  (denies `.git`/`.env`/out-of-workspace writes) **loaded 0 instead of 2
  instances** — a shipped, visible, named security control doing nothing, for an
  undetermined period, until `af687798a` (2026-08-24). The registry's sharpest
  presence≠operative specimen to date, in a *permission gate*.
- Subagent confirmations cross a **sanitizing bus boundary**: `MessageBus.derive()`
  strips `forcedDecision` and identity fields from child-published requests
  (`message-bus.ts:52-91`) — an explicit anti-spoofing seam no other tracked
  harness makes this legible.

## Environment relationship & surfaces

**Primary verb `internalize` — but default-off, which no other internalizer in the
set is.** Two independent sandbox mechanisms, both dormant without configuration
(`sandboxConfig.ts:58-63`): (A) whole-process re-execution into docker / podman /
gVisor / lxc / Seatbelt / windows-native, with Google publishing its own versioned
sandbox image (a `bundle` streak) and the lxc mode explicitly *binding* to a
user-managed container; (B) a newer per-tool-call OS sandbox compiled into core —
bwrap + **generated seccomp BPF** on Linux (`LinuxSandboxManager.ts:301-316`),
`sandbox-exec` per command on macOS, an AppContainer/Job-Object runner on Windows
with the C# helper source shipped in the package (`GeminiSandbox.cs`) — confining
fs *and* network per mode (`sandbox-default.toml`: every mode `network = false`).
It also *inhabits*: `SANDBOX` env detection stands the launcher down inside an
existing sandbox. Two macOS caveats: the default Seatbelt profile is
**`permissive-open`** — global file-read, open network — while the actually-confining
`strict-open` ships unused (`sandbox.ts:105`), and the drift window hardened all
profiles against container-daemon escape (`5411f113c`). Confinement inherits across
child processes (Seatbelt/namespace semantics, not per-call wrappers). Default
posture remains **bare host + ASK_USER gate** — gate policy carries what the
environment bounds don't, the exact E1 composition.

Surfaces: terminal TUI; ACP mode for IDE embedding; the VS Code companion feeds
open-file/cursor context (default-off, delta-encoded, append-only) and diffs — a
context feed, not a loop host. `model_agnostic: false` is a design fact: six auth
routes, all Google (`contentGenerator.ts:63-70`); `GATEWAY` re-points the host but
the wire client is `@google/genai` throughout.

## Data & telemetry — the vendor-instrument row *(2026-08-25)*

The category index's model-edge watch item ("vendor-native harnesses are where to
watch") gets its Google data point, and it is two-channel:

- **Clearcut (metadata): default-ON for every auth mode, opt-out only, no dialog.**
  59 event types POSTed to `play.googleapis.com/log`; content is honestly excluded
  (prompt *lengths*, tool names/decisions/durations, no args, no paths) — but the
  **OAuth account email is attached to every event as the sessionable ID**
  (`clearcut-logger.ts:495-501`) while `docs/reference/configuration.md:3071-3076`
  states "We do not collect any personal information, such as your name, email
  address" — both true-at-pin citations, unreconciled in the same repo. The opt-out
  (`usageStatisticsEnabled`) is `showInDialog: false`: hand-edit `settings.json` or
  keep sending.
- **Training-data collection is a separate, free-tier-only, server-side channel**
  ("collects your prompts, related code, generated output… human reviewers may
  read") — and when the server omits the opt-in value, **the client defaults it to
  `true`** (`usePrivacySettings.ts:157-163`). Paid/Vertex/API-key routes get
  link-only notices. The OTel path (default-off, default-local) is the
  content-bearing one: once a user enables it for their own observability,
  `logPrompts` defaults true and full prompts/tool args/shell strings flow.

Consistent with the two-instance pattern recorded in tool-taxonomy.md: who the maker is
at category 1 predicts what the harness collects — here, *shape from everyone,
content from the free tier*.

## The Antigravity transition — measured at the pin *(2026-08-25)*

The stub carried one external fact (individual free tier ended 2026-06-18) that a
clone can't check; this read establishes what the *repo* says:

- **The migration is productized inside Gemini CLI**: hardcoded Antigravity
  installers (`antigravityUtils.ts:9-35`), a `/help` interception, and a **builtin
  SKILL.md teaching the model to migrate users off the very harness running it**
  (`skills/builtin/antigravity-support/SKILL.md:73-87` — "Install Antigravity…
  `agy --version`… Transition Workspaces").
- **The banner is server-controlled and deliberately undismissable**: any banner
  text containing "Antigravity" is exempt from the 5-show cap
  (`useBanner.ts:45-48`); the text arrives via remote experiment flags, so Google
  can flip a permanent migration banner without a release.
- **The sunset itself left no trace in-tree**: repo-wide grep for the date finds
  nothing, and README/quota docs still advertise "Free tier: 60 requests/min and
  1,000 requests/day" (`README.md:19-20`) — the deprecation lives entirely in
  server-side flags and external messaging. A documentation reader would not know.

Prediction (dated, falsifiable): by **2027-03-01** the repo's monthly commit count
stays under 150/month (vs the 610-682 peak) *or* the repo is archived/renamed —
i.e., the succession completes rather than reverses. Score it at the next re-read.

## Run probe — 2026-08-25

Probe target: published npm artifact `@google/gemini-cli@0.56.0-nightly.20260825.g812f7a2bc`
— verified 2 commits behind the pin (`git rev-list --count` = 2), so probing the
nightly ≈ probing the pin. Node v22.23.2, this 8GB host; success read from output,
not exit status (5e).

- **Registry state contradicts "wound down"**: `latest` 0.57.0, `preview`
  0.58.0-preview.0, and the nightly all published *on the pin date*; daily
  nightlies throughout the window.
- **Install: 7 packages in 14 s**, 122 MB, 6 top-level entries — the package is one
  esbuild bundle (117 MB `bundle/`, 88 chunks). Contrast dsh's probe on the same
  host (npx OOM, >10 min, 187 entries): the bundled-artifact strategy makes install
  ~30× faster here. No npx trap.
- **Boots**: `--version` prints the nightly string. No-auth headless run fails
  loud — auth guidance naming `GEMINI_API_KEY`/`GOOGLE_GENAI_USE_VERTEXAI`/
  `GOOGLE_GENAI_USE_GCA`, **exit 41** — not a 5e specimen. No scored agent run: no
  credentials on this box and the free individual tier is gone (omit-with-reason).
- **Publish-time contents confirm three source claims at the artifact**: the 6
  Seatbelt profiles ship as data files; `bundle/builtin/` carries exactly the two
  builtin skills (`antigravity-support`, `skill-creator`) in SKILL.md format; a
  bundled `chrome-devtools-mcp.mjs` MCP server rides inside the CLI artifact.

## Bleed

- **category 1↔2 (maker span)**: the Google column's harness entry, now traced.
  Gemini-protocol by design at every seam; and the *data instrument* reading above.
  New wrinkle for the span table: this is a vendor running **two** category-2
  products through a succession, with the incumbent scripted to hand users to the
  successor.
- **category 6**: consumes the cross-vendor conventions selectively — SKILL.md yes
  (six roots incl. `.agents/skills`), Claude Code's hook shape yes (Stop→AfterAgent
  migrator ships), `AGENTS.md` no (GEMINI.md hold-out). Ships its own MCP server
  inside the CLI artifact.
- **category 3**: internalize + bundle + bind + inhabit streaks, all default-off —
  the null default posture is itself the data point (contrast codex/dsh, where
  internalized confinement is the always-on gate).
- **category-4-shaped machinery inside the harness**: plan mode as deny-by-default
  policy data; evals with reliability tiers; the maintenance bots (caretaker /
  pr-generator / SSR agent) are Google running an agent-operated repo on top of its
  own harness family.

## Cost model

Metered via Gemini API (API key / Vertex), or Code Assist tiers via OAuth
(`free-tier | legacy-tier | standard-tier` in source). The individual free tier's
2026-06-18 end (stub's external fact) remains **invisible in-tree** — README still
advertises it at the pin; treat the sunset as testimony about server-side state,
drifting on Google's schedule. The free tier that does appear in source carries the
training-data opt-in whose absent-value default is `true` client-side.

## Surprises

1. **The stub's bet inverted**: the "long context" harness spends a
   benchmark-guarded prompt section teaching the model to *conserve* context, and
   its only embedding path is dead code.
2. **The permission gate had a silently inert safety checker until one day before
   the pin** (`af687798a`) — presence≠operative inside the security boundary
   itself.
3. **CONSECA: an LLM writes the security policy and another enforces it — safely**,
   because safety checkers are structurally one-way (tighten-only). A better answer
   to Warp's `is_risky` crack than not letting the model near the gate at all.
4. **Claude Code's extension conventions are load-bearing here**: the Stop-hook
   retry contract reproduced field-for-field, a shipped `hooks migrate` command for
   Claude Code configs, SKILL.md builtins — while `AGENTS.md` is refused. Google
   adopted the competitor's *mechanisms* and declined the *file*.
5. **`save_memory` was deleted and the prompt announces its own absence** — memory
   became "edit the markdown yourself" plus a default-off, code-jailed,
   human-gated background extractor.
6. **The maintenance is agentic**: 13/68 window commits from an issue-fixing bot,
   and the bot's new runner is Antigravity — the successor maintains the incumbent.
7. **The email/no-email contradiction**: `client_email` on every telemetry event at
   `clearcut-logger.ts:495-501`; "we do not collect… email address" in the same
   repo's docs.
8. **A harness this instrumented ships with no step budget** — `maxSessionTurns`
   -1/unlimited; the guard is loop-*detection*, and its first firing is a coaching
   re-prompt, not a stop.
9. **The graph context pipeline, the a2a-server, worktrees, autoMemory, IDE
   context, next-speaker, CONSECA, both sandboxes — all shipped, all default-off.**
   The gap between what this codebase contains and what a stock run executes is the
   widest in the tracked set; any characterization of gemini-cli that doesn't say
   "at the default" is probably wrong.

## Open questions

- ~~Does the `cli`/`core` split make the core reusable as a library?~~ **Answered
  2026-08-25**: yes — published, four in-repo consumers plus a documented SDK.
- ~~What does `a2a-server` do?~~ **Answered 2026-08-25**: serves the CLI's own loop
  as an experimental A2A agent; nothing in-repo consumes it.
- ~~Does the long-context bet show up as simpler context assembly?~~ **Answered
  2026-08-25**: falsified — see the bet.
- Does the qwen-code divergence study (candidates ledger, 2026-08-18) now pay? This
  read supplies the gemini-cli side; the comparison wants qwen-code's fork point
  (v0.8.2-era) against today's policy-engine/hooks/skills architecture — most of
  which postdates the fork, so the divergence is likely *large and asymmetric*.
- The `additional_permissions` engine-level network gap
  (`policy-engine.ts:744-764`): does a second tool ever adopt the parameter without
  shell.ts's tool-level prompt? Re-check at next drift.
- Does the Antigravity succession prediction (2027-03-01, above) hold?
- exp-04's cross-harness memory question now has a Google-side answer shape (inbox
  + human promotion); if a memory-continuity arm ever runs against gemini-cli, the
  pull path is file-edits, not a tool.
