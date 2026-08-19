---
name: warp
category: 2
surfaces: [terminal, desktop, web]   # native GPU app; crates/warp_tui (180 files) is the TUI; crates/serve-wasm compiles the client to wasm ("web-compiled Warp terminal", README)
execution: both   # OrchestrationExecutionMode::{Local, Remote{environment_id, worker_host}}
environments: [container, remote-sandbox]   # verified as *detected*, not launched — see Bleed
environment_relation: inhabit   # crates/isolation_platform detects the container Warp is ALREADY inside (Docker/DockerSandbox/Kubernetes/Namespace) for workload identity; it launches nothing
vendor: Warp (warpdotdev)
url: https://github.com/warpdotdev/warp
license: AGPL-3.0   # `warpui`/`warpui_core` carved out as MIT (README, LICENSE-MIT)
open_source: true   # since 2026-04-28; the product shipped years earlier — see Stack & repo shape
stack: [Rust]
version: tui-screenshots-app5029-227-g80a20347
commit: 80a20347
first_commit: 2026-04-28   # squashed "Initial public release of Warp" — NOT the product's age
stars: 64121
stars_at: 2026-08-11
read_at: 2026-08-11
depth: survey   # module surfaces and ~15 files read; the agent loop itself was not traced
features:
  mcp: true            # crates/mcp (runtime.rs, oauth.rs, sse_transport/); TemplatableMCPServerManager
  lsp: true            # crates/lsp (manager.rs, install.rs); language-server selection is an onboarding step
  skills: true         # crates/ai/src/skills — SKILL.md format, WARP_SKILL_DIRS env, SkillScope precedence, 13 bundled skills
  subagents: true      # run_agents / RunAgentsRequest.agent_run_configs; warp_multi_agent_api
  rules_files: [WARP.md, AGENTS.md]   # crates/repo_metadata/src/standing_queries.rs:22; global ~/.agents/AGENTS.md
  model_agnostic: true # bounded: LLMProvider::API_KEY_PROVIDERS = OpenAI, Anthropic, Google, xAI
  session_sharing: true # app/src/terminal/shared_session/ with its own permissions_manager
  hooks: false         # checked: no lifecycle-hook engine for Warp's own loop. It *installs* hooks into Codex
  # turn_end_gates deliberately NOT SET after the 2026-08-18 probe: the agent loop is server-side (only client bindings in the drop), so neither presence nor absence is decidable from this source — omitted is the honest cell
  ptc: false           # 2026-08-18 targeted probe: "code mode" in this drop is a UI chip flag (CodeModeChip, features.rs:258) + telemetry field (is_code_mode_v2) — no model-code-drives-tools runtime anywhere in app/src or crates (execute_code/codemode/quickjs/v8-eval sweep); tool execution is client-side, so a runtime would be visible here — see The distinguishing bet
  learning_loop: false # checked: MemorySource has exactly one variant, `Manual` (app/src/server/server_api/ai.rs:1080)
  evals: false         # checked: no agent eval suite. Two near-misses: crates/input_classifier/src/bin/evaluate.rs (one component) and an eval viewer inside the bundled create-skill skill
---

# Warp

A terminal emulator that became a harness. The product is a native Rust desktop app (plus a
TUI and a wasm build) that runs its own agent loop — "Oz" — over the shell, with an
embedding index of the codebase, an MCP client, LSP integration, and a permission system
built around command classification. It also detects, launches, and programmatically drives
*other* harnesses: Claude Code, Codex, Gemini CLI, and OpenCode.

## The distinguishing bet

Every other harness in this set bets on being the thing you run. Warp bets on being the
thing the others run **inside** — and then, having become that, on orchestrating them.

This is not a marketing reading; it is two distinct subsystems in the source.

**1. CLI agents as first-class session types.** `app/src/terminal/cli_agent.rs` defines a
`CLIAgent` enum (module doc: "detecting and working with CLI-based AI agents like Claude
Code, Gemini CLI, Codex, Amp, and Droid"), carrying each vendor's brand color, and
`app/src/terminal/cli_agent_sessions/plugin_manager/` holds a manager per agent —
`claude.rs`, `codex.rs`, `gemini.rs`, `opencode.rs`. Warp renders another harness's session
as a native tab.

**2. Other harnesses as interchangeable orchestration backends.** `crates/warp_cli/src/agent.rs`
defines `enum Harness { Oz, Claude, OpenCode, Gemini, Codex, Unknown }` — Warp's own agent is
one variant among five, and `OrchestrationConfig.harness_type` (`crates/ai/src/agent/orchestration_config.rs:13`)
selects which one a spawned child agent uses, locally or in a cloud run.
`app/src/ai/agent_sdk/driver/harness/` implements the drivers: `claude_code.rs` (with a
`parent_bridge.rs` and a `wake_driver.rs`), `codex.rs`, `gemini.rs`, plus
`claude_transcript.rs` and `codex_transcript.rs` — Warp parses the other harnesses'
transcript formats to follow what its children are doing.

The sharpest detail is in `driver/harness/codex.rs:50`: Warp installs **its own plugin hooks
into Codex** and launches it with `--dangerously-bypass-hook-trust` so those hooks run without
Codex's manual review step, then reads Codex's `SessionStart` hook event to know the session
is live. A category-2 product driving another category-2 product through that product's category-5
extension surface, deliberately bypassing its trust gate to do so.

The wager: the model and the loop are commoditizing, so own the *surface* they all run on and
the *orchestration* above them. Every rival in the set would dispute this — opencode, cline,
and codex each assume their loop is the one that matters.

## Main features

- **Oz orchestration** (`warp_multi_agent_api`, "MAA") — fan-out to child agents, local or
  remote, with the harness per child selectable. Distinctive: nothing else in the set treats a
  *competitor's* harness as a swappable execution backend.
- **Codebase embedding index** (`crates/ai/src/index/full_source_code_embedding/` — a naive
  and a semantic chunker, plus `changed_files.rs` for incremental updates; `file_outline/`
  alongside). Distinctive within this set: the traced harnesses lean on grep and
  model-driven search. Gated by an explicit consent step at project init ("Would you like to
  give me permission to index this codebase? … No code is stored on Warp servers").
- **Execution profiles + command classification permissions**
  (`app/src/ai/execution_profiles/`, `app/src/ai/blocklist/permissions.rs`). The decision is
  a typed reason on both sides — `Allowed(ExplicitlyAllowlisted | IsReadOnlyAndSettingEnabled |
  AgentDecided | AlwaysAllowed | …)` / `Denied(AutonomyForceDisabled | AlwaysAskEnabled |
  ExplicitlyDenylisted | ContainsRedirection | …)`. Two details worth noting: `AgentDecided`
  makes the *model* an allowlist authority (behind `FeatureFlag::AgentDecidesCommandExecution`),
  and `AutonomyForceDisabled` is a workspace-level org override (`AiAutonomySettings`) — a
  fleet-admin permission model, which is rare in this set.
- **Skills** — the `SKILL.md` convention, not a Warp-native format; `WARP_SKILL_DIRS` adds
  directories at personal precedence; 13 skills ship bundled (`add-mcp-server`, `create-skill`,
  `claude-api`, `oz-platform`, …). Table stakes by now, but the *format adoption* is the
  finding — see Bleed.
- **Computer use** (`crates/computer_use/`) — real X11/Wayland/macOS mouse, keyboard,
  screenshot, and screen-recording implementations. Not table stakes; nothing else surveyed
  here ships it.
- **MCP** with OAuth and SSE transport; **LSP** with server install/management.

## Stack & repo shape

Rust monorepo: 3962 `.rs` of 6199 tracked files, `app/` (the client) plus ~50 crates under
`crates/`. 682 `.md` — an unusual share, explained by `agents/specs/` and `.agents/specs/`,
directories of per-ticket agent specs (`APP-4913-tui-input-prompt-prefix.md`, …) committed
alongside the code. The repo dogfoods its own workflow: `AGENTS.md`, `.mcp.json`, `.claude/`,
`.agents/`, and `.warpindexingignore` at root.

**Provenance — the `first_commit` column lies here.** History begins 2026-04-28 with a single
squashed commit, "Initial public release of Warp." The GitHub repo object dates from
2021-07-08 and the product shipped publicly years before the source drop. 2048 commits since
April 2026 measure the open-source era only; `git blame` and pickaxe archaeology cannot reach
the design decisions that predate it. This is the inverse of the gsd-core provenance case
(stars stranded by an org move) and the same trap the tool index warns about generally.

Licensing is split deliberately: AGPL-3.0 for the product, MIT for `warpui`/`warpui_core`,
its UI framework — copyleft on the thing they sell, permissive on the thing they'd like
adopted. First non-permissive harness in this repo's set.

## Architecture

_TODO — deep-dive not done. The loop was not traced; claims above are from module surfaces,
type definitions, and doc comments._

Starting points for the deep-dive, in order: `crates/ai/src/agent/mod.rs` (action /
action_result conversion is the tool protocol), `app/src/ai/agent_sdk/driver/` (how a child
harness is spawned and followed), `crates/ai/src/index/full_source_code_embedding/` (what
actually enters the prompt — the interesting question, since this is the only indexed
context assembly surveyed so far), and `app/src/ai/blocklist/permissions.rs` (whether the
permission check precedes or follows the model's decision).

## Bleed

- **→ category 5 (artifacts).** Consumes `AGENTS.md` and the `SKILL.md` convention rather than
  inventing formats. Stronger: `app/src/terminal/view/init_project/mod.rs:50` defines
  `LINKABLE_FILES = [CLAUDE.md, .cursorrules, AGENT.md, GEMINI.md, .clinerules,
  .windsurfrules, .github/copilot-instructions.md]` — seven *competitors'* rules files, which
  Warp offers to link into `WARP.md`. Direct evidence for the standards question: rules files
  have converged enough to be treated as an interoperable format by a rival implementation.
- **→ category 2 (other harnesses).** The novel one. See The distinguishing bet.
- **→ category 3 (environments), inverted.** `crates/isolation_platform/` does **not** launch
  sandboxes — it *detects the one Warp is already inside*: `IsolationPlatformType::{Docker,
  DockerSandbox, Kubernetes, Namespace}`, read from `WARP_ISOLATION_PLATFORM` and used to
  obtain a `WorkloadToken` for workload identity. So the vocabulary needs a fourth verb
  beyond bundle (Devin), bind (hermes), and internalize (codex): Warp **inhabits** — it ships
  as the payload inside a sandbox provisioned by its own cloud service, and introspects the
  container to prove who it is. `environments:` above is recorded on that basis, which is
  weaker than the other entries' — flagged rather than smoothed over.
- **→ category 1.** OpenAI is the "founding sponsor" of the open-source repo and the agentic
  management workflows are GPT-powered (README). This is *not* the ownership case
  (xAI/Cursor) or the maker-identity case (Nous/hermes), so it does not count as a third
  instance of "who a harness's maker is at category 1 predicts what the harness collects." It is
  the adjacent, weaker form — sponsorship — and is recorded so a second sponsorship instance
  has something to pair with.

## Cost model

Subscription (`app/src/billing/`) with bring-your-own API key for four providers
(`LLMProvider::API_KEY_PROVIDERS`). Specific tiers and prices **not checked** — pricing drifts
faster than anything else in this repo and should be read from the site with a `checked:`
date, not from source.

## Surprises

1. **It is open source at all.** I expected the GitHub repo to be an issue tracker for a
   closed product — that is what `warpdotdev/warp` was. The source drop is 2026-04-28, and it
   is the real client, not a shim.
2. **A harness that runs other harnesses as backends.** The `Harness` enum putting Oz beside
   Claude, Codex, OpenCode, and Gemini as peer options is a shape the taxonomy has no row for.
   Recorded as a stress-test case.
3. **Bypassing another harness's trust gate by design.** `--dangerously-bypass-hook-trust`
   is not an incident; it is a named constant with a doc comment explaining the workflow.
   Codex's hook-trust review exists to stop exactly this, and an integration partner routes
   around it with a flag Codex itself provides.
4. **The agent's memory is manual-only.** `MemorySource` has one variant, `Manual`, despite a
   full store/version/agent CLI surface built around it. Where hermes and codex write their own
   memory autonomously (conclusion 8), Warp built the storage and left the write path to the
   user. A dated counter-instance to the autonomous-learning-loop trend, and the enum shape
   says they expect that to change.

## Open questions

- Does the embedding index actually feed the prompt, or only the file-search tool? This is the
  question that decides whether Warp is a real counter-example to grep-based context assembly,
  and it needs the deep-dive.
- `parse_local_child_harness` accepts `OpenCode` as a local child, but
  `agent_sdk/driver/harness/` has no `opencode.rs` — only `claude_code`, `codex`, `gemini`. Is
  the OpenCode path unimplemented, routed elsewhere, or server-side?
- Is there a plan/act split? `app/src/ai/artifacts/mod.rs` has a `PLAN` artifact type and there
  is a "Plan" menu item, but no `PlanMode` type — `plan_mode` is deliberately omitted from
  frontmatter rather than guessed either way.
- What does Oz's terminal-native loop do that a repo-native loop can't? The whole bet rests on
  the terminal being the right substrate, and nothing surveyed so far tests that claim.
