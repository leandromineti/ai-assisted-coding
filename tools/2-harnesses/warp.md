---
name: warp
category: 2
surfaces: [terminal, desktop, web]   # native GPU app; crates/warp_tui (180 files) is the TUI; crates/serve-wasm compiles the client to wasm ("web-compiled Warp terminal", README)
execution: both   # OrchestrationExecutionMode::{Local, Remote{environment_id, worker_host}}
environments: [container, remote-sandbox]   # verified as *detected*, not launched — see Bleed
environment_relation: inhabit   # crates/isolation_platform detects the container Warp is ALREADY inside (Docker/DockerSandbox/Kubernetes/Namespace) for workload identity; it launches nothing
maker: Warp (warpdotdev)
url: https://github.com/warpdotdev/warp
license: AGPL-3.0   # `warpui`/`warpui_core` carved out as MIT (README, LICENSE-MIT)
access: open-source   # since 2026-04-28; the product shipped years earlier — see Stack & repo shape
stack: [Rust]
version: tui-screenshots-app5029-227-g80a20347
commit: 80a20347
first_commit: 2026-04-28   # squashed "Initial public release of Warp" — NOT the product's age
stars: 64121
stars_at: 2026-08-11
read_at: 2026-08-19   # deep-dive; survey was 2026-08-11 at the same pin. Upstream drifted 98 commits between the reads — dated drift answer in Drift, pin unmoved (rule 4b)
depth: deep-dive   # 2026-08-19, three parallel readers: loop, context assembly, orchestration+permissions; load-bearing claims spot-verified at the pin. No run probe — GUI-first Rust monorepo, a build alone exceeds any reasonable probe budget, and no in-scope claim depends on runtime behavior
harness_features:
  mcp: true            # crates/mcp (runtime.rs, oauth.rs, sse_transport/); TemplatableMCPServerManager
  lsp: true            # crates/lsp (manager.rs, install.rs); language-server selection is an onboarding step
  skills: true         # crates/ai/src/skills — SKILL.md format, WARP_SKILL_DIRS env, SkillScope precedence, 13 bundled skills
  subagents: true      # run_agents / RunAgentsRequest.agent_run_configs; warp_multi_agent_api
  rules_files: [WARP.md, AGENTS.md]   # crates/repo_metadata/src/standing_queries.rs:22; global ~/.agents/AGENTS.md. Competitors' files (CLAUDE.md, .cursorrules, …) are /init link targets only, never read at runtime
  model_agnostic: true # bounded: LLMProvider::API_KEY_PROVIDERS = OpenAI, Anthropic, Google, xAI. 2026-08-19: BYOK does NOT mean local calls — user keys are serialized into the request and used by Warp's backend (app/src/ai/agent/api/impl.rs:87; crates/ai/src/api_keys.rs:44-50)
  session_sharing: true # app/src/terminal/shared_session/ with its own permissions_manager; the one local enforcement point is viewer mode (execute.rs:594-600 WaitingOnSharer)
  hooks: false         # 2026-08-19 sharpened: no hook engine for Warp's own loop (exhaustive sweep — stop_hook/on_turn_end/PreToolUse/max_turns/… all zero hits; no hook schema in settings). Warp's answer to hooks is "it uses YOURS": it installs its own plugins into Claude Code and Codex hook systems — see Orchestration
  context_retrieval: search-tool   # ADR-0055, cell set 2026-09-04 from the deep-dive: the embedding index is real but its chain ends in a {name, path} tool result with zero surrounding context lines (RETRIEVE_FRAGMENT_CONTEXT_LENGTH = 0, codebase_index.rs:82); the only automatic contribution is a pointer saying the codebase is indexed (body § index verdict)
  # context_compaction deliberately unset (ADR-0055, 2026-09-04): compaction is entirely server-driven — /compact is the only client trigger, ToolCallResultSummary arrives opaque, and the wire/server implementation lives in an external unpublished proto repo absent from this clone; whether the server summarizes or prunes is undecidable from source (omit-with-reason). DRIFT 2026-09-24: the premise "unpublished" was WRONG — `warpdotdev/warp-proto-apis` is a public repo (`gh api … -q .private` → false) carrying 15 `.proto` files at the exact rev this pin depends on (`b0886a95…`, Cargo.toml:348), and `apis/multi_agent/v1/response.proto:95` declares `bool summarized`. Cell still unset: reading request.proto/conversation_data.proto at that rev is the parked follow-up that may decide it (§ Drift check 2026-09-24, 1)
  turn_end_gates: false # 2026-08-19, decidable after all: the 2026-08-18 probe's "loop server-side" premise was half wrong — the ITERATION loop is client-side (see Architecture), so a turn-end gate would have to be visible here, and it is verified absent. Three things run at turn end (suggestion chip, /queue drain, "Execute this plan" chip) — all advisory, none can veto. Turn extension exists only for transient errors (MAX_RETRIES=3) and wait_for_events. What the server does before emitting Finished stays unobservable, but the enforcement point (execution) is wholly client-side and ungated
  tool_approval: policy  # can_autoexecute_command six-level chain at dispatch — with the AgentDecided caveat: a model-authored is_risky:false self-authorizes and preempts the redirection guard (body §permission model); set 2026-08-25 transcribing the deep-dive's verified instance at this pin, no re-read
  gate_model_authority: self  # the acting model's `is_risky:false` returns Allowed(AgentDecided) before the redirection deny (permissions.rs:961-966 @ df5cacf89; :934-945 at the pin) — model self-authorization, unchanged across 384 commits
  plan_mode: flag      # 2026-08-19: the survey missed it by name — UserQueryMode::{Normal, Plan, Orchestrate} (app/src/ai/agent/mod.rs:2637-2653), entered via /plan. A per-query flag, not sticky state: derived from the string prefix at each submit, no mode toggle, no exit transition. planning_enabled is hardcoded true in every real request (api.rs:403) — /plan is a nudge, not a capability switch
  ptc: false           # 2026-08-18 targeted probe: "code mode" in this drop is a UI chip flag (CodeModeChip, features.rs:258) + telemetry field (is_code_mode_v2) — no model-code-drives-tools runtime anywhere in app/src or crates (execute_code/codemode/quickjs/v8-eval sweep); tool execution is client-side, so a runtime would be visible here — see The distinguishing bet
  learning_loop: proposed # regraded ✗→proposed 2026-09-04 per ADR-0056 (same evidence, 2026-08-19 sharpening): MemorySource::Manual (one variant) governs the memory-store API; but Rules have an agent-PROPOSED, human-COMMITTED flow (server-suggested rules → modal accept → AIFact::Memory, fed back as existing_suggestions for dedup). AIMemory::is_autogenerated is deprecated — they REMOVED an auto-write path. The mechanism shape that forced the enum's third value (issue #13)
  evals: false         # checked: no agent eval suite. Two near-misses: crates/input_classifier/src/bin/evaluate.rs (one component) and an eval viewer inside the bundled create-skill skill
---

# Warp

A terminal emulator that became a harness. The product is a native Rust desktop app (plus a
TUI and a wasm build) whose agent ("Oz", being renamed "Warp Agent" upstream) runs over the
shell, with an embedding index of the codebase, an MCP client, LSP integration, and a
permission system built around command classification. It also detects, launches, and
programmatically drives *other* harnesses: Claude Code, Codex, Gemini CLI, and OpenCode.

Deep-dived 2026-08-19 at the survey's pin (80a20347): loop traced, index-to-prompt path
traced, permission dispatch traced. The three headline answers, each detailed below:

1. **The embedding index does not feed the prompt.** It backs one tool the model must call.
   The "genuine counter-position to grep-based context assembly" hypothesis is falsified —
   Warp's own settings copy frames the index as an optimization over grep.
2. **The loop split is client-iteration / server-policy.** The client never talks to an LLM
   provider — even BYOK keys ship to Warp's backend. One HTTP request per loop iteration.
3. **The permission model is strict for itself, absent for its delegates.** Warp runs a
   six-level precedence chain on its own shell commands, then launches child harnesses with
   `--dangerously-skip-permissions` / `--dangerously-bypass-approvals-and-sandbox` / `--yolo`.

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

The sharpest detail is in `driver/harness/codex.rs:52`: Warp installs **its own plugin hooks
into Codex** and launches it with `--dangerously-bypass-hook-trust` so those hooks run without
Codex's manual review step, then reads Codex's `SessionStart` hook event to know the session
is live. A category-2 product driving another category-2 product through that product's category-6
extension surface, deliberately bypassing its trust gate to do so.

The wager: the model and the loop are commoditizing, so own the *surface* they all run on and
the *orchestration* above them. Every rival in the set would dispute this — opencode, cline,
and codex each assume their loop is the one that matters.

## Main features

- **Oz orchestration** (`warp_multi_agent_api`, "MAA") — fan-out to child agents, local or
  remote, with the harness per child selectable. Distinctive: nothing else in the set treats a
  *competitor's* harness as a swappable execution backend. Mechanics traced 2026-08-19 — see
  Orchestration.
- **Codebase embedding index** (`crates/ai/src/index/full_source_code_embedding/` — a naive
  and a semantic chunker, plus `changed_files.rs` for incremental updates; `file_outline/`
  alongside). Traced 2026-08-19: it backs the `search_codebase` **tool**, nothing more — see
  Context assembly. Gated by an explicit consent step at project init whose "No code is
  stored on Warp servers" claim the traced data flow strains — see the same section.
- **Execution profiles + command classification permissions**
  (`app/src/ai/execution_profiles/`, `app/src/ai/blocklist/permissions.rs`). The decision is
  a typed reason on both sides — `Allowed(ExplicitlyAllowlisted | IsReadOnlyAndSettingEnabled |
  AgentDecided | AlwaysAllowed | …)` / `Denied(AutonomyForceDisabled | AlwaysAskEnabled |
  ExplicitlyDenylisted | ContainsRedirection | …)`. Traced 2026-08-19: the check runs AFTER
  the model proposes, `AgentDecided` lets the model self-authorize, and `AutonomyForceDisabled`
  is a phantom — see Permission model.
- **Skills** — the `SKILL.md` convention, not a Warp-native format; `WARP_SKILL_DIRS` adds
  directories at personal precedence; 13 skills ship bundled (`add-mcp-server`, `create-skill`,
  `claude-api`, `oz-platform`, …). Table stakes by now, but the *format adoption* is the
  finding — see Bleed.
- **Computer use** (`crates/computer_use/`) — real X11/Wayland/macOS mouse, keyboard,
  screenshot, and screen-recording implementations. Not table stakes; nothing else surveyed
  here ships it.
- **MCP** with OAuth and SSE transport; **LSP** with server install/management.

## Stack & repo shape

Rust monorepo: 3962 `.rs` of 6199 tracked files, `app/` (the client) plus **78** crates under
`crates/` (`git ls-tree -d --name-only 80a20347 crates/ | wc -l`; 75 as workspace path
dependencies in the root `Cargo.toml` — *corrected 2026-09-24: the deep-dive wrote "~50", a
figure no measure at the pin produces*). 682 `.md` (exact: `git ls-tree -r --name-only
80a20347 | grep -c '\.md$'`) — an unusual share, explained by per-ticket agent specs
committed alongside the code: **498 of them under the root `specs/` tree** (281 per-ticket
directories), 19 under `agents/specs/` (`APP-4913-tui-input-prompt-prefix.md`, …) and 32
under `.agents/` (*corrected 2026-09-24: the deep-dive attributed the count to the two
smaller directories and never mentioned `specs/`; the observation survives, the attribution
did not*). The repo dogfoods its own workflow: `AGENTS.md`, `.mcp.json`, `.claude/`,
`.agents/`, and `.warpindexingignore` at root. It even tests the dogfooding: a unit test reads
the repo's own root `AGENTS.md` through the production rules predicate and asserts `WARP.md`
no longer exists (`crates/repo_metadata/src/standing_queries_tests.rs:118-134`).

**Provenance — the `first_commit` column lies here.** History begins 2026-04-28 with a single
squashed commit, "Initial public release of Warp." The GitHub repo object dates from
2021-07-08 and the product shipped publicly years before the source drop. 2048 commits since
April 2026 measure the open-source era only; `git blame` and pickaxe archaeology cannot reach
the design decisions that predate it. This is the inverse of the gsd-core provenance case
(stars stranded by an org move) and the same trap the tool index warns about generally.

Licensing is split deliberately: AGPL-3.0 for the product, MIT for `warpui`/`warpui_core`,
its UI framework — copyleft on the thing they sell, permissive on the thing they'd like
adopted. First non-permissive harness in this repo's set.

**The load-bearing absence:** the wire protocol lives in an external git dependency —
`warp_multi_agent_api` pinned to a rev of `warpdotdev/warp-proto-apis` (`Cargo.toml:348`),
whose `.proto` files are not in this drop. Everything server-side (prompt assembly, model
routing, tool choice, summarization policy) is absent by construction; every claim below
about the server is inferred from client usage and graded accordingly.

**Corrected 2026-09-24 — half of that absence was a rule-1b failure.** The proto repo is
**public** (`gh api repos/warpdotdev/warp-proto-apis -q .private` → `false`) and at the exact
rev this pin depends on it carries 15 `.proto` files under `apis/multi_agent/v1/`
(`attachment`, `citations`, `conversation_data`, `document_content`, `file_content`,
`input_context`, `lsp`, `options`, `orchestration`, `request`, `response`, `skill`,
`suggestions`, `task`, `todo`). The *server implementation* is closed; the *wire schema*
never was — the surface searched was the clone, which structurally cannot show a git
dependency's contents. Read at that rev it already corroborates two findings from a better
source: the three top-level event types are stated in the contract
(`response.proto:19-29`, `oneof type { StreamInit init; ClientActions client_actions;
StreamFinished finished; }`), and the server meters BYOK spend separately from Warp spend
(`byok_token_usage` beside `warp_token_usage`, `response.proto:108-118`), with `bool
summarized` (`:95`) the first direct evidence for the "server silently compacts" claim. See
§ Drift check 2026-09-24, 1.

## Architecture — the traced loop *(deep-dive 2026-08-19)*

**Client-iteration, server-policy.** The 2026-08-18 probe's "the agent loop is server-side"
needs splitting into two claims, one per half:

- **Policy is server-side.** The client's single LLM egress point is
  `warp_multi_agent_client::generate_multi_agent_output` (`app/src/ai/agent/api/impl.rs:141-142`)
  → POST `{server_root_url}/ai/multi-agent`, protobuf over SSE. No provider endpoint appears
  anywhere in the client (`api.anthropic.com`/`api.openai.com`/… sweep: zero hits). **BYOK
  keys are serialized into the request** (`impl.rs:87`; `crates/ai/src/api_keys.rs:44-50`)
  and spent by Warp's backend — bring-your-own-key does not mean local inference, a
  distinction the feature matrix's `model_agnostic` column doesn't currently capture.
- **Iteration is client-side.** The response protocol has exactly three top-level event
  types — `Init`, `ClientActions`, `Finished` (`response_stream.rs:493-524`). The client
  executes every action locally, wraps each result as `AIAgentInput::ActionResult`
  (`app/src/ai/agent/mod.rs:2783-2788` — "relayed back to the LLM for it to continue"), and
  re-submits: one HTTP request per loop iteration, driven by a model subscription
  (`controller.rs:496-566`), continuity via an opaque server-issued conversation token.

The request is a **capability declaration, not a plan**: `supported_tools`,
`supports_parallel_tool_calls`, `autonomy_level` (coarse Supervised/Unsupervised),
`isolation_level`, ~20 `supports_*` booleans (`impl.rs:67-106`). The server picks from what
the client says it can execute. Server-side tools (web search/fetch, seven subagent types
including Research and Summarization) pass through as
`Tool::Server(_) → NoClientRepresentation` (`convert_from.rs:794-796`) — the client renders
their status without understanding them, and the pinned commit's own subject line ("Don't
hard-fail message conversion on an unrecognized citation type") shows the server ships
vocabulary ahead of client releases.

**Turn end, decided.** Because iteration is client-side, the turn-end-gate question the
probe left undecidable is decidable: **there is no gate.** Exhaustive sweep (stop_hook,
on_turn_end, TurnEnd, veto, verification_step, max_turns, PreToolUse/PostToolUse, hook
schema in settings — all zero hits). What does run at turn end is advisory: a
passive-suggestion request for a next-prompt chip, the `/queue` drain, and an "Execute this
plan" chip when the turn ended in document edits (`terminal/view.rs:5321-5407`). Turn
*extension* exists only as transient-error auto-resume (`MAX_RETRIES = 3`) and the
`wait_for_events` yield state. The only verification machinery in the loop is per-edit, not
per-turn: `crates/ai/src/diff_validation/` fuzzy-validates model-emitted edits against file
content before applying.

**Plan mode exists** — the survey missed it because it is named `UserQueryMode`, not
`PlanMode`: `{Normal, Plan, Orchestrate}`, entered by `/plan` prefix, attached per-query
with no sticky state (`app/src/ai/agent/mod.rs:2637-2653`). `planning_enabled` is hardcoded
`true` in every real request (`api.rs:403`), so `/plan` is a nudge to the server, not a
capability switch. The PLAN artifact is client-constructed: `CreateDocuments`/`EditDocuments`
**always auto-execute** ("Document operations are always auto-executed",
`execute/create_documents.rs:34-40` — no permission gate on plan writes), stream into a
rich-text document, optionally auto-sync to a Warp Drive "Plans" folder, and a user-edited
plan re-attaches itself dirty to the next query.

## Context assembly — the index is a tool, not context *(deep-dive 2026-08-19)*

**Verdict on the survey's headline question: the embedding index does NOT feed the prompt.**
The full chain: the server issues a `SearchCodebase` tool call → client executor →
`retrieve_relevant_files` → three server round-trips (hash candidates → local metadata map →
content re-upload for reranking) → results return as a **tool result**
(`SearchCodebaseResult::Success { files }`), never as context. The only automatic
contribution is a `{name, path}` *pointer* saying "this codebase is indexed"
(`AIAgentContext::Codebase`, double-flag-gated), and retrieval returns chunks with
**zero surrounding context lines** (`RETRIEVE_FRAGMENT_CONTEXT_LENGTH: usize = 0`,
`codebase_index.rs:82`). Sweeps for any auto-injection path (all `retrieve_relevant_files`
consumers, all `AIAgentContext::File` constructors) came back empty — the sole consumer is
the tool executor.

So the strongest counter-position candidate in the category collapses under inspection:
tree-sitter semantic chunking, Merkle-tree incremental sync, server-side reranking — wired
to a single tool the model must decide to call. On the automatic-context axis Warp is
architecturally closer to the grep-based harnesses than to indexed context assembly, and its
own settings copy says so: "If a codebase is unable to be indexed, Warp can still navigate
your codebase and gain insights via grep and find tool calling" (`code_page.rs:82`).

**What does enter the prompt at turn start** (complete enumeration, `AIAgentContext`,
`app/src/ai/agent/mod.rs:2229-2309` + `input_context.rs` + `context_model.rs`): cwd/home
paths, git head+branch, repo identity, PR metadata (no diff), **full contents of rules
files** (WARP.md/AGENTS.md at every directory level, case-insensitive, plus global
`~/.agents/AGENTS.md`; resent every turn), the codebase pointer, a skills index (names and
descriptions, no bodies — and only when the set changed since last turn, the one
cache-friendly measure found client-side), clock, shell/OS, user-attached blocks and images,
and — conditionally but automatically — **terminal scrollback**: with
`FeatureFlag::AgentViewBlockContext` on and the conversation fullscreen, every completed
user command block is auto-attached (truncated, secret-redacted at block completion). The
client assembles all of this as structured protobuf, not prompt text; there is **no Warp
system prompt in this repository** (the only `system_prompt` in the drop is one *received*
from the server to hand to third-party child harnesses).

**The consent gate vs the traced data flow.** Three UI strings promise "No code is stored on
Warp servers" / "Code is never stored on the server" (`init_project/mod.rs:45`,
`codebase_index_speedbump_banner.rs:18`, `code_page.rs:82`). The code: raw chunk content is
uploaded at index time (`Fragment { content: String }` in the `generateCodeEmbeddings`
mutation, batches up to 4MB) because **embeddings are computed server-side by third-party
models** (Voyage 3.5/4, OpenAI text-small-3 — chosen by the server); chunk content plus
absolute file paths are uploaded **again on every query** for reranking (`rerankFragments`);
and the Merkle sync protocol only uploads nodes the server *lacks*, implying a persistent
hash-keyed server store. "Not stored" is thus doc-level and unverifiable from here, while
"nothing leaves the machine" is refuted: content transits Warp's servers twice, and the
absolute repo path rides along with every call. Also: the org admin setting `Enable` forces
indexing on regardless of the user's toggle (`user_workspaces.rs:1827-1829`) — the consent
dialog's framing is only accurate under `RespectUserSetting`.

**Context lifecycle:** summarization is entirely server-driven — `/compact` is the only
client trigger; the server silently compacts long tool results (`ToolCallResultSummary`
arrives with nothing renderable) and reports `context_window_usage` back. No client-side
cache discipline (no `cache_control`, no breakpoint placement — consistent with never
building a prompt), but the server's token accounting vocabulary (SystemPrompt →
ToolDefinitions → ConversationHistory → LatestInput) is exactly the canonical cache-friendly
prefix ordering — inferred, not verified, since prompt assembly is server-side.

## Permission model — strict for itself, absent for delegates *(deep-dive 2026-08-19)*

**Ordering: the check runs after the model proposes, before the spawn.** Nothing pre-filters
what the model may propose, and the model is never told the policy in advance (the only
autonomy signal sent upstream is the coarse Supervised/Unsupervised level). Denials reach
the model after the fact as tool results ("Command (…) was on denylist and so was not
allowed to run").

**The model is an authority inside its own permission chain.** `is_read_only` and `is_risky`
are **model-authored fields on the tool call** ("`Some(true)` iff the LLM thinks that the
command is risky", `crates/ai/src/agent/action/mod.rs:44-47`). Under the `AgentDecides`
profile setting (default **for the TUI**; the GUI defaults to `AlwaysAsk`), with
`FeatureFlag::AgentDecidesCommandExecution` (in the default build set), `is_risky == Some(false)`
auto-executes — the classifier and the classified are the same model, same turn, no second
opinion. And the ordering has a bug-shaped edge: the `AgentDecided` fast path
(`permissions.rs:934-939`) sits **above** the `ContainsRedirection` check (`:941-945`), so a
model asserting `is_risky: false` on a command containing `>` bypasses the redirection guard
that would otherwise deny it. What bounds self-authorization: the denylist (checked first,
nothing overrides it: bash/curl/ssh/rm/… by default), the feature flag, and the profile
setting. Also noted: `AutonomyForceDisabled` — the enterprise-kill-switch-looking variant —
is declared three times and **constructed nowhere**; org policy actually works by overriding
the profile getters (org value first, user fallback; denylists are *merged*, not overridden).

**Child harnesses do not inherit any of this — orchestration is a privilege-escalation
path.** Every launch disables the child's own guardrails and installs none of Warp's:
Claude Code gets `--dangerously-skip-permissions` (plus `hasTrustDialogAccepted` and
`skipDangerousModePermissionPrompt` written into `~/.claude.json` / `settings.json`); Codex
gets `--dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust` plus
`trust_level = "trusted"` written for the working dir *and every immediate child git repo*;
Gemini gets `--yolo` plus `trustedFolders.json`. The stated reason is UI, not security:
children run in hidden panes where an approval prompt would hang unseen
(`local_harness_launch.rs:122-125`). A comment claims run-wide permissions carry over via
`inherit_child_agent_settings` — **true only for Oz children** (whose actions route back
through the same blocklist); a third-party child's tool calls never touch
`BlocklistAIPermissions`. The gate on the whole fan-out is a single `RunAgentsPermission`
approval card — which vanishes in autonomous mode (early `return None`,
`execute/run_agents.rs`) and for child-spawned grandchildren (a hidden pane can't show a
card; only `FeatureFlag::MultiLevelOrchestration` gates depth). Warp also writes into three
other vendors' config files as collateral state of a launch, including seeding
`OPENAI_API_KEY` into `~/.codex/auth.json` in the driver path (deliberately skipped for
*local* Codex children; **not** skipped for local Claude, whose `~/.claude.json` is mutated
globally).

One hard veto no setting lifts: MCP config files are protected write paths, checked before
the auto-approve flag — but only on the file-write path; a denylist-passing shell command
can still write them. And the default allow/deny lists are compiled out under `cfg(test)`,
so no unit test exercises the shipped regexes.

## Orchestration mechanics *(deep-dive 2026-08-19)*

`run_agents` is **fire-and-forget with no client-side fan-out cap** — the tool result is
`Launched { agents: [ids] }` at spawn (30s spawn timeout, runtime unbounded), never child
output; the only quota is server-side ("Concurrent cloud agent limit reached… upgrade your
plan"). Child output returns asynchronously over an SSE event stream and is injected into
the parent's next request as first-class inputs (`AIAgentInput::MessagesReceivedFromAgents`
/ `EventsFromAgents`) — closer to a message bus than to a subagent call that returns a
value. The parent synthesizes; delivery is at-least-once with retry and echo-confirmation.

**The follow channel is OSC 777 escape sequences through the PTY.** Warp's plugins inside
each child harness emit a fixed JSON notification schema into the terminal
(`session_start`, `prompt_submit`, `tool_complete`, `stop`, `permission_request`,
`permission_replied`, … — `cli_agent_sessions/event/v1.rs`), which Warp parses into typed
session events. This is effectively a cross-vendor harness telemetry protocol — the listener
recognizes agents Warp ships no installer for (Auggie, Droid, Pi, OhMyPi) — and it includes
permission events, so Warp can *observe* child permission prompts it has just disabled.
Codex transcript capture is load-bearing on the plugin: no `session_start` event → no
session UUID → the transcript is never uploaded (the pre-plugin fallback collapses every
notification to `Stop`).

The Claude driver is the deepest: transcript-file parsing (Claude's own JSONL, uploaded and
rehydrated on resume), a required platform plugin from a Warp-owned marketplace
(`warpdotdev/claude-code-warp` — hook internals live there, outside this drop; a public
repo, checked 2026-09-24, so outside is not closed), and
`parent_bridge.rs`, a three-stage on-disk mailbox under `.claude-code/oz-parent-bridge/`
that a Claude hook drains into next-turn context (capped 6000 chars), with a `wake_driver`
that relaunches a dormant session when mail arrives. PTY scraping is used only for runtime
error patterns and `--version`; scrollback is archived, not parsed for state.

**OpenCode occupies a fourth support tier** the survey's question didn't anticipate:
accepted as a local child but launched as a raw shell command (`opencode --prompt …`, no
driver, no permission flags — it alone keeps its own defaults), explicitly rejected for
remote runs ("Remote child agents do not support the opencode harness yet"), marked
`Unsupported` in the driver dispatch, hidden from CLI help — yet fully wired into the
session listener with its own plugin manager. Not unimplemented, not routed elsewhere:
deliberately half-supported.

## Bleed

- **→ category 6 (artifacts).** Consumes `AGENTS.md` and the `SKILL.md` convention rather than
  inventing formats. Stronger: `app/src/terminal/view/init_project/mod.rs:50` defines
  `LINKABLE_FILES = [CLAUDE.md, .cursorrules, AGENT.md, GEMINI.md, .clinerules,
  .windsurfrules, .github/copilot-instructions.md]` — seven *competitors'* rules files, which
  Warp offers to link into `WARP.md`. Direct evidence for the standards question: rules files
  have converged enough to be treated as an interoperable format by a rival implementation.
  *(2026-08-19: confirmed link-targets only — the runtime rules predicate reads exactly
  WARP.md and AGENTS.md.)*
- **→ category 2 (other harnesses).** The novel one. See The distinguishing bet and
  Orchestration mechanics.
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
(`LLMProvider::API_KEY_PROVIDERS`). *(2026-08-19)* BYOK is **routing, not locality**: the
key travels to Warp's backend and the loop still runs there — see Architecture. Specific
tiers and prices **not checked** — pricing drifts faster than anything else in this repo and
should be read from the site with a `checked:` date, not from source.

## Surprises

*(Survey, 2026-08-11:)*

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
4. **The agent's memory is manual-only.** *(Sharpened 2026-08-19 — see `learning_loop` in
   frontmatter: no autonomous writes, but the agent proposes and the human commits, and a
   deprecated `is_autogenerated` field shows an auto-write path was built and removed.)*

*(Deep-dive, 2026-08-19:)*

5. **The strongest counter-position candidate collapses under inspection.** The index is a
   tool, `RETRIEVE_FRAGMENT_CONTEXT_LENGTH = 0`, and the settings copy frames it as
   grep-plus. The category's axis-1 outlier turns out to sit on the majority side of the
   axis.
6. **"No code is stored on Warp servers" coexists with code transiting them twice per
   search.** Server-side embedding by third-party models, content re-upload at query time,
   hash-keyed dedup implying a persistent store. The claim is unverifiable from the client;
   its plain reading is strained by the traced flow.
7. **The model is an authority in its own permission chain** — `is_risky` is a
   model-authored field the client trusts as an allowlist token, and it preempts the
   redirection guard. A taxonomy cell distinct from both "static allowlist" and "human
   approval."
8. **Autonomy discipline stops at the process boundary.** Six-level precedence for its own
   commands; `--dangerously-*` for every delegate. "Permission model" needs a per-tier
   answer for orchestrating harnesses: strict for self, none for children.
9. **BYOK ships your key to the vendor.** The loop runs on Warp's backend regardless of
   whose key pays for the tokens. The `model_agnostic` matrix column conflates two things
   this case splits: provider choice and call locality.
10. **The cross-vendor telemetry protocol nobody announced.** OSC 777 JSON notifications as
    a de facto standard for following any CLI agent in a terminal — including
    `permission_request` events for prompts Warp itself disabled.

## Reasoning-parameter handling — targeted read 2026-08-27 (not a re-read; the pin is unchanged)

The "while you're there" half of [issue #41](https://github.com/leandromineti/ai-assisted-coding/issues/41).
Warp was characterised but not traced in the [#40](https://github.com/leandromineti/ai-assisted-coding/issues/40)
sweep because it presents a shape none of the others do: **a harness setting a reasoning
parameter for a harness it is driving**. Traced at this pin, the answer is that it does not
handle the parameter at all, and that turns out to be the finding.

`set_codex_model_reasoning_effort` (`app/src/ai/agent_sdk/driver/harness/codex.rs:777-789`)
takes the user's `HarnessModelConfig.reasoning_level`, filters out the empty string, and
writes it verbatim into Codex's `config.toml` as `model_reasoning_effort`. If it is unset,
the key is **removed** so Codex applies its own default. No model-id check, no vendor
branch, no vocabulary validation, no version pin — the string the user picked in Warp's UI
lands in another product's config file untouched.

That is a fourth position on [conclusion 15](../../docs/conclusions.md)'s axis, and it is
locally correct: the parameter's validity is Codex's problem, and Codex is OpenAI's own
client for OpenAI's own models. Warp's exposure is zero because it holds no model-capability
knowledge to go stale. The same instinct is written down one function over
(`:806-810`), for the model key rather than the effort key — *"We do this unconditionally
rather than enumerating a list of 'old' models on the client"* — which is the same
conclusion hermes reached independently and stated in its Anthropic adapter, from the
opposite direction.

**But delegation moves the obligation rather than discharging it.** Warp cannot detect that
the value it forwarded is wrong, cannot clamp it, and cannot report the resulting 400 as
anything but a child-process failure — and Codex's own handling is one of the cases
conclusion 15 covers. Read alongside the child-launch finding in § Permission model
(Warp launches every child harness with its guardrails disabled), the pattern is consistent:
**Warp's orchestration is strict about its own surface and pass-through about everything it
delegates.** That is a coherent position; it is not a defence.

## Drift check — 2026-08-19 (not a re-read; the pin is unchanged)

*(2026-08-19, pin unmoved per rule 4b.)* Upstream is 98 commits past the pin; 27 touch the
paths this deep-dive traced. Reviewed by subject: orchestration plumbing consolidation
("Orchestration unified stack" M1+M2, checkpoint coordinator wired into AgentDriver, shared
MAA retry/resume budget), UX ("Rename Oz Agent UI to Warp Agent", settings page split with a
"Third-Party CLI Agents" page), and one security-shaped fix (Sentry PII/typed-content leak).
Nothing in the subjects contradicts the structural findings (index-as-tool, client-iteration
loop, permission ordering, child-launch flags); the checkpoint/retry work extends the
orchestration story rather than changing its shape. Re-check the child-launch flags
specifically on any future re-pin — that is the finding most likely to be "fixed."

## Drift check — 2026-09-24 (not a re-read; the pin is unchanged)

384 commits / 1368 files since the pin; **145 of them touch a file or directory this report
cites**, which is the set that was checked
(`git log --format='%h %cs %s' 80a20347..df5cacf89 -- <49 cited paths>`; the path list is
every `*.{rs,toml,md,json}` string in this report resolved to its full path at the pin, plus
the 14 directory-level citations — `crates/{mcp,lsp,computer_use,isolation_platform,warp_tui}`,
`crates/ai/src/{skills,diff_validation,index/full_source_code_embedding,file_outline}`,
`app/src/ai/execution_profiles`, `app/src/terminal/{cli_agent_sessions,shared_session}`,
`app/src/billing`, `app/src/ai/agent_sdk/driver/harness`). Every one of the six structural
findings survives. What the check turned up instead are **two claims that were wrong at the
pin** — both counts stated without the measure that produced them, and one of them an
*absence* that was never an absence.

**1. CONTRADICTED — the proto repo is public, so the "load-bearing absence" is not one.**
§ Stack & repo shape says the wire protocol "lives in an external git dependency … whose
`.proto` files are not in this drop. Everything server-side … is absent **by construction**",
and § Open questions says the server-side prompt assembly and tool-choice policy are
"**Undecidable by construction** — the proto repo and backend are closed." The first half is
true and the second is false. `warpdotdev/warp-proto-apis` is a **public** repository
(`gh api repos/warpdotdev/warp-proto-apis -q .private` → `false`), and at the exact rev the
pin depends on — `b0886a9523e2e05d102f61bd0a212dc15ade4835`, `Cargo.toml:348 @ 80a20347` —
it carries **15 `.proto` files** under `apis/multi_agent/v1/` (`attachment`, `citations`,
`conversation_data`, `document_content`, `file_content`, `input_context`, `lsp`, `options`,
`orchestration`, `request`, `response`, `skill`, `suggestions`, `task`, `todo`), counted with
`gh api repos/warpdotdev/warp-proto-apis/git/trees/b0886a95…?recursive=1 -q '[.tree[].path | select(endswith(".proto"))] | length'`.
The *server implementation* is still closed; the *wire schema* never was. This is a rule-1b
failure — the surface searched was the clone, and the clone structurally cannot show a git
dependency's contents.

Read at that rev, the schema immediately **corroborates two findings from a better source
than the one the report used**, and the correction should say so rather than just retract:

- § Architecture's three top-level event types were read off the client's match arms
  (`response_stream.rs:493-524`). The schema states them directly:
  `oneof type { StreamInit init = 1; ClientActions client_actions = 2; StreamFinished finished = 3; }`
  (`apis/multi_agent/v1/response.proto:19-29 @ b0886a95`). SOURCE-grade, from the contract
  rather than from one consumer of it.
- Surprise 9 ("BYOK ships your key to the vendor") gains wire-level confirmation: the
  server's own usage metadata meters BYOK spend separately from Warp spend —
  `map<string, ModelTokenUsage> warp_token_usage = 6;` beside
  `map<string, ModelTokenUsage> byok_token_usage = 7;` and
  `map<string, ModelTokenUsage> custom_endpoint_token_usage = 9;`
  (`apis/multi_agent/v1/response.proto:108-118 @ b0886a95`). A server can only meter BYOK
  tokens it spent itself. The same message carries `bool summarized = 2;` (`:95`) — the
  first direct evidence for § Context assembly's "the server silently compacts".

  *The `context_compaction` omit-with-reason (frontmatter, ADR-0055, 2026-09-04) should be
  revisited on this basis — it was justified by "the wire/server implementation lives in an
  external unpublished proto repo absent from this clone", and the repo is not unpublished.
  Reading `request.proto` and `conversation_data.proto` at the pinned rev may make the cell
  decidable. Not done here: this is a drift check, not a re-read.*

  `warpdotdev/claude-code-warp` (§ Orchestration mechanics, "hook internals live there,
  outside this drop") is public too (`gh api repos/warpdotdev/claude-code-warp -q .private`
  → `false`, last pushed 2026-08-17). Same correction applies: outside the drop, not closed.

**2. CONTRADICTED — two counts in § Stack & repo shape do not reproduce at the pin.**
The scar this repo already records ("a count carries its measure") fires on both:

- *"~50 crates under `crates/`."* At the pin there are **78** crate directories, each with
  its own `Cargo.toml` (`git ls-tree -d --name-only 80a20347 crates/ | wc -l` → 78;
  `git ls-tree -r --name-only 80a20347 crates/ | grep -c '^crates/[^/]*/Cargo\.toml$'` → 78).
  The only other candidate measure is the workspace's local-path dependency list
  (`git show 80a20347:Cargo.toml | grep -c 'path = "crates/'` → **75**). Neither is ~50, and
  the root `Cargo.toml` has no enumerable member list to have produced one
  (`members = ["crates/*", "app"]`). At HEAD: 80 crates (`+ai_types`, `+regex_dfas`,
  `+secret_redaction`, `+warp_harness_usage`; `−command-signatures-v2`, `−warp_js`).
- *"682 `.md` … explained by `agents/specs/` and `.agents/specs/`."* The 682 is exact
  (`git ls-tree -r --name-only 80a20347 | grep -c '\.md$'`), but the explanation names the
  wrong directories. **498 of the 682 (73%) live in the root `specs/` tree** — 281 per-ticket
  directories the report never mentions — against **19** in `agents/specs/` and **32** under
  `.agents/` (`git ls-tree -r --name-only 80a20347 <dir> | grep -c '\.md$'`). The cited
  example file is genuine and is one of the 19 (`agents/specs/APP-4913-tui-input-prompt-prefix.md`).
  The observation ("the repo dogfoods its own workflow") survives; the attribution does not.

  Both numbers that *did* carry an implicit measure reproduce exactly: 3962 `.rs` / 6199
  tracked files at the pin, and the frontmatter's `crates/warp_tui (180 files)` is exactly
  the `.rs` count under `crates/warp_tui/src` (184 including `benches/`). Worth stating the
  measure in place so the next check does not have to re-derive it.

**3. Corroborated — the child-launch flags did not get "fixed", and the report predicted
they might.** The 2026-08-19 Drift note ended "Re-check the child-launch flags specifically
on any future re-pin — that is the finding most likely to be 'fixed.'" Scored at 384 commits
and 44 days: **it was not fixed, in any of the five launch sites.** All present at HEAD,
byte-identical in substance: `claude --dangerously-skip-permissions`
(`claude_code.rs:222 @ df5cacf89`, was `:211 @ 80a20347`), `--dangerously-bypass-hook-trust`
as a named constant (`codex.rs:62`, was `:52`),
`codex --dangerously-bypass-approvals-and-sandbox` in both the driver (`codex.rs:204,209`)
and the local pane launch (`local_harness_launch.rs:127,136`), and `gemini --yolo`
(`gemini.rs:107`). The collateral config writes are all intact too: `hasTrustDialogAccepted`
and `skipDangerousModePermissionPrompt` into Claude's files, `trust_level = "trusted"`
stamped per project key (`codex.rs:854,861`), `trustedFolders.json` for Gemini
(`gemini.rs:328`), and the `OPENAI_API_KEY` seed into `~/.codex/auth.json`
(`codex.rs:571,607`). The prediction was correct and is now dated evidence, not a hunch.

**4. Corroborated, and sharpened — upstream shipped a mechanism that only makes sense if
the hidden-pane finding is right.** § Permission model's stated reason for disabling the
children's guardrails is UI: "children run in hidden panes where an approval prompt would
hang unseen". Upstream then hit exactly that failure and built a workaround for it. #15728
(`51a74992a`, 2026-09-02, "Pass confirmation dialogs in 3p harnesses, and ensure driver
exits") adds a **bounded shutdown sequence**: send `/exit`; after 1s send "a bare Enter to
retry a dropped write **or accept the default confirmation option**"; after 15s `SIGKILL`
the proved descendant process group. The new modules are
`app/src/ai/agent_sdk/driver/harness/exit_escalation.rs` ("Bounded shutdown sequence for a
third-party harness") and `process_control.rs`, with the per-harness comments naming what is
being dismissed — `claude_code.rs:545 @ df5cacf89`: *"'Exit anyway' is the default-highlighted
option, so a bare Enter…"*. So Warp now *blind-presses Enter at a child's confirmation
dialog*, which is the same finding one step further: not only are the child's approval gates
disabled at launch, the ones that survive are answered by keystroke injection. The
autonomous-mode and child-conversation bypasses are intact at HEAD, with the reason written
in the code: *"Child conversations live in hidden panes where a confirmation card would be
invisible and hang the run. Always auto-execute"*
(`app/src/ai/blocklist/action_model/execute/run_agents.rs:462-475 @ df5cacf89`).

**5. Corroborated — `AgentDecided` still sits above `ContainsRedirection`. Open question
answered.** § Open questions asked whether the ordering bug survives upstream. It does, and
untouched: the model-authored `is_risky == Some(false)` fast path returns `Allowed(AgentDecided)`
at `permissions.rs:961-966 @ df5cacf89` and the `contains_redirection` deny is at `:968-972`
— the same eight lines in the same order as `permissions.rs:934-945 @ 80a20347`. 44 days and
385 commits of exposure did not reclassify it, which is itself information: it is a decision,
or at least a tolerated one, not a fresh slip. `AutonomyForceDisabled` is still declared
three times and **constructed nowhere** (`git grep -n AutonomyForceDisabled df5cacf89 -- app crates`
→ three hits, all enum declarations at `permissions.rs:52,87,124`). The default allow/deny
lists and their `cfg(test)` compile-out are byte-identical
(`git diff 80a20347 df5cacf89 -- crates/cloud_object_models/src/ai_execution_profile.rs` →
empty), so the 18-entry shipped denylist still has no unit test over it.

*One mechanical change worth a reader's note:* every permission accessor now threads a team
scope — `get_execute_commands_setting(ctx, terminal_view_id)` became
`get_execute_commands_setting(terminal_view_id, scope, ctx)` — from the ~20-commit
`[multi-team]` series (`e2a080210` P0 through `93b4f91e9`). Policy *resolution* is now
per-window-team; the precedence chain and its ordering are unchanged.

**6. Corroborated — index-as-tool, unchanged down to the constant.**
`RETRIEVE_FRAGMENT_CONTEXT_LENGTH: usize = 0` at both
`codebase_index.rs:82` and `get_relevant_files/remote_search/native.rs:281`, identical at pin
and HEAD. `codebase_index.rs`'s 35 changed lines are one `Vec<Gitignore>` → `Vec<Arc<Gitignore>>`
refactor (`c6609ef23`, gitignore matcher sharing) with no retrieval-path change. The
`generateCodeEmbeddings` / `rerankFragments` GraphQL surface is unchanged
(`crates/warp_graphql_schema/api/schema.graphql`), so the § Context assembly privacy trace
still holds. The three consent strings are **verbatim identical** at HEAD, including "No code
is stored on Warp servers" (`init_project/mod.rs:45`) and "Code is never stored on the
server" (`codebase_index_speedbump_banner.rs:18`). The org-forces-indexing override survived
the `user_workspaces.rs` split intact — `AdminEnablementSetting::Enable => ai_globally_enabled`
now at `app/src/workspaces/user_workspaces/mod.rs:1640-1649 @ df5cacf89`, with
`team_allows_codebase_context()` pluralised to `teams_allow_codebase_context()` and now
folding over every team the user belongs to.

**7. Corroborated — the turn-start context enumeration is exactly right, and exhaustively
so.** § Context assembly claims a *complete* enumeration of `AIAgentContext`. Both revisions
carry the same 13 variants in the same order — `Directory`, `SelectedText`,
`ExecutionEnvironment`, `CurrentTime`, `Image`, `Codebase`, `ProjectRules`, `File`, `Git`,
`Repository`, `PullRequest`, `Skills`, `Block` (`app/src/ai/agent/mod.rs:2229 @ 80a20347`,
`:2213 @ df5cacf89`) — despite `mod.rs` taking 348 changed lines. `AgentViewBlockContext`
(the auto-attached scrollback gate) appears at the same three sites with the same counts.
The rules predicate is byte-identical (`git diff … -- crates/repo_metadata/src/standing_queries.rs`
→ empty): still exactly `["WARP.md", "AGENTS.md"]` at `standing_queries.rs:22`, and
`LINKABLE_FILES: [&str; 7]` is unchanged at `init_project/mod.rs:50-58` — the category-6
bleed finding (competitors' rules files are link targets only) stands.

**8. Corroborated — `ptc: false` got stronger by subtraction.** The pin's PTC sweep found a
UI chip flag and a telemetry field and no runtime. Since then upstream **deleted the only
embedded JS runtime in the drop**: `crates/warp_js` is gone at HEAD
(`git ls-tree -d --name-only df5cacf89 crates/warp_js` → empty), removed with
`a06279712` (2026-09-12, "Rip out completions v2 and associated code"), along with
`app/src/plugin/host/native/js_api/`, `.../plugin.rs`, `.../runner.rs` and
`crates/warp_completer/src/signatures/v2/js.rs`. `CodeModeChip` survives as a feature flag
only (`crates/warp_features/src/lib.rs:394`, gated at `app/src/features.rs:261`), and
`is_code_mode_v2` remains a telemetry field. The negative claim now has a stronger surface
behind it, not a weaker one.

**9. Corroborated — `hooks: false`, `turn_end_gates: false`, and the exhaustive sweep hold,
including across all 384 subjects.** The pin's sweep tokens still return **zero files** at
HEAD across `app/src` and `crates`: `stop_hook`, `on_turn_end`, `TurnEnd`, `PreToolUse`,
`PostToolUse`, `max_turns`, `verification_step` — same zero as at the pin. Scanning all 384
subject lines for the report's headline vocabulary
(`git log --format='%h %s' 80a20347..df5cacf89 | grep -icE …`) returns: **1** hit on
`hook` and it is the word "webhook" (`066ec71b7`, a skill validator); **0** on
`compact|summariz`; **0** on `reasoning|effort`; **0** on `plan mode|/plan|UserQueryMode|planning`;
**0** on `scrollback|block context`. `UserQueryMode { Normal, Plan, Orchestrate }` is
unchanged (`mod.rs:2828 @ df5cacf89`) and `planning_enabled: true` is still hardcoded in the
real request path (`api.rs:438 @ df5cacf89`, was `:403`). `MemorySource` still has the one
variant `Manual` and `is_autogenerated` is still present-and-deprecated at the same five
sites — the `learning_loop: proposed` regrade's evidence is intact.

**10. Corroborated and extended — the distinguishing bet grew in exactly its own direction.**
Three independent extensions, none of which change the shape of the bet:

- The `CLIAgent` enum gained **`Grok`** — 16 → 17 recognised agents
  (`app/src/terminal/cli_agent.rs:164 @ df5cacf89`, `2718b6658`, 2026-09-08, "Adds
  first-class Grok Build support"). `crates/warp_cli/src/agent.rs`'s
  `enum Harness { Oz, Claude, OpenCode, Gemini, Codex, Unknown }` is unchanged
  (`:278-291 @ df5cacf89`), so orchestration backends stayed at five while *recognised*
  agents grew.
- **Warp now publishes its own skills into its children's skill roots.** New module
  `app/src/ai/agent_sdk/driver/harness/skill_dirs_publish.rs @ df5cacf89` — "Makes
  Warp-provided skills available to third-party harnesses (Claude Code, Codex) by symlinking
  them into a skill root each harness already searches on its own", reading the same
  `WARP_SKILL_DIRS`. Its conflict policy is the child-launch pattern in miniature: *"In a
  sandbox, we own the whole filesystem, so the published skill wins: the conflicting entry is
  renamed aside with a `.backup` suffix"*; outside a sandbox it falls back to a `warp-<name>`
  alias. § Permission model's "Warp also writes into three other vendors' config files as
  collateral state of a launch" now extends to their skill directories.
- **Warp now extracts and reports usage metrics out of its children's native transcripts.**
  New `usage_reporting.rs`, `transcript_persistence.rs`, `save_coordinator.rs` and the new
  crate `warp_harness_usage` (`4a7740e81`, "[APP-5545] Extract native Claude and Codex usage
  metrics"; `c0380ce89`, "Publish metrics from native transcript captures"). Warp meters what
  its delegates spend.

  The **OpenCode fourth tier is unchanged**: still `HarnessKind::Unsupported(Harness::OpenCode)`
  in driver dispatch (`driver/harness/mod.rs:308 @ df5cacf89`), still rejected for remote runs
  with the same string ("Remote child agents do not support the opencode harness yet.",
  `run_agents.rs:729,807`), still fully wired in the session listener with its own plugin
  manager. And the **OSC 777 event schema is byte-identical** —
  `git diff 80a20347 df5cacf89 -- app/src/terminal/cli_agent_sessions/event/v1.rs` is empty.
  A cross-vendor protocol that does not move in 384 commits is a protocol.

**11. Corroborated — the reasoning-parameter section is byte-identical.**
`set_codex_model_reasoning_effort` moved from `codex.rs:777-789 @ 80a20347` to
`codex.rs:888-900 @ df5cacf89` with **not one character changed**: still no model-id check,
no vendor branch, no vocabulary validation, no version pin — the user's string still lands
verbatim in another product's `config.toml`, and an unset value still removes the key. The
comment one function over (*"We do this unconditionally rather than enumerating a list of
'old' models on the client"*) is also unchanged, now at `:917-923`. Across all 384 subject
lines there is **no commit mentioning reasoning or effort**. Conclusion 15's fourth position
is stable at the 44-day mark.

**12. Corroborated and quantified — the dogfooding claim, measured.** § Stack & repo shape
says "the repo dogfoods its own workflow" from the presence of `AGENTS.md`, `.mcp.json`,
`.claude/`, `.agents/`. The commit log measures it: **253 of the 384 commits (66%) are
authored by `warp-agent-staging[bot]`** (`git log --format='%an' 80a20347..df5cacf89 | sort |
uniq -c | sort -rn`), across 41 distinct authors, the next-largest being a human at 18 and
`dependabot[bot]` at 13. In the 98-commit window *before* the pin the same bot authored
**60 (61%)**. Warp's own agent writes two of every three commits to Warp, and the share is
rising. The bot's subjects are ordinary product work, not automation chores — "Remove stable
orchestration feature flags (#15887)", "Add Neovim 0.13 line text objects (#16105)", "Avoid
panic when /model targets a closed window (#16102)". This is the strongest available evidence
for the report's dogfooding observation and it was free.

**13. Untouched.** The MCP protected-write-path hard veto (`check_protected_write_paths`,
`permissions.rs:768/1233 @ df5cacf89`); `crates/isolation_platform`'s detect-don't-launch
shape (28 added lines, all new tests and plumbing, `environment_relation: inhabit` intact);
`CreateDocuments`/`EditDocuments` always-auto-execute
(`git diff … -- execute/create_documents.rs` → empty); `crates/ai/src/agent/orchestration_config.rs`
(→ empty); `LLMProvider::API_KEY_PROVIDERS = [OpenAI, Anthropic, Google, Xai]`, still
`[Self; 4]` at `crates/ai/src/llm_provider.rs:17 @ df5cacf89` despite the Grok work; the
capability-declaration request shape (`api_keys` still a request field, `supports_*` booleans
17 → 20); `crates/computer_use` (large churn, all Windows recording backends —
`environments`/`surfaces` unaffected); `crates/mcp`, `crates/lsp`, `crates/ai/src/diff_validation`,
`app/src/billing` (no claim-bearing change). Also **still no agent eval suite** — but the
reason is now visible: `385cc203c` ("Support benchmark repository preparation overrides")
lands "the Warp client half of benchmark repository substitution" against a companion PR in
the closed `warpdotdev/warp-server`. `evals: false` is a fact about this drop's boundary, not
about the product; worth one clause in the frontmatter comment.

**Citation hygiene — four line references in this report no longer resolve at HEAD**, though
all remain correct at the pin. `app/src/settings_view/code_page.rs:82` (the "grep and find
tool calling" settings copy) is now `app/src/settings_view/code_indexing_page.rs:77`
(`c9e562294` split the Code page); `app/src/workspaces/user_workspaces.rs:1827-1829` is now
`app/src/workspaces/user_workspaces/mod.rs:1640-1649` (`8cbb01d45` split the file into a
module); `app/src/settings_view/ai_page.rs` is now `warp_agent_page.rs` (`42effe840`, "Rename
Oz Agent UI to Warp Agent" — the rename § the intro anticipated has landed); and
`permissions.rs:934-945` is `:961-972`. No correction is owed — a pinned citation is a
citation at its pin — but a reader who greps at HEAD will come up empty on the first two.

**What a re-read should cost:** moderate-to-high, and it should start somewhere new. The
permission chain, the loop, the index path, the OSC-777 protocol, and the reasoning-parameter
function are all unchanged, so a re-read buys little there. What has changed is the
*orchestration periphery* — skill publication into children, transcript-derived usage
metering, the exit-escalation sequence, team-scoped policy resolution — and, more importantly,
what is now known to be readable: **the 15-file proto repo at the pinned rev**, which is the
cheapest unexploited evidence surface this subject has and which would settle both the
`context_compaction` omit-with-reason and § Open questions' "undecidable by construction".

## Open questions

- ~~Does the embedding index actually feed the prompt, or only the file-search tool?~~
  **Answered 2026-08-19: only the tool.** See Context assembly.
- ~~`parse_local_child_harness` accepts OpenCode but there is no opencode.rs driver — 
  unimplemented, routed elsewhere, or server-side?~~ **Answered 2026-08-19: deliberately
  half-supported** — local-only raw command launch, remote rejected, listener fully wired.
- ~~Is there a plan/act split?~~ **Answered 2026-08-19: yes** — `UserQueryMode::Plan`,
  per-query, `planning_enabled` always on. See Architecture.
- What does Oz's terminal-native loop do that a repo-native loop can't? Sharpened by the
  deep-dive: the concrete answers found are auto-attached scrollback context, PTY handoff
  (`TransferShellCommandControlToUser`), and the OSC-777 follow channel — all
  terminal-substrate capabilities. Whether they pay for the thick-client/thin-protocol costs
  (server dependency, protocol drift) is a use question, not a source question.
- What do the server-side prompt assembly and tool-choice policy actually do? ~~Undecidable by
  construction — the proto repo and backend are closed.~~ *Half-corrected 2026-09-24: the
  backend is closed, the proto repo is public and readable at the pinned rev — the wire
  schema is decidable, the policy behind it is not.* The token-accounting vocabulary
  (SystemPrompt → ToolDefinitions → History → LatestInput) is the only aperture found in
  the clone; `request.proto` and `conversation_data.proto` at `b0886a95` are the unread
  aperture.
- ~~Does `AgentDecided`-above-`ContainsRedirection` survive upstream?~~ **Answered 2026-09-24:
  it survives, same eight lines in the same order at `permissions.rs:961-972 @ df5cacf89`,
  after 384 commits — a tolerated ordering, not a fresh slip** (§ Drift check 2026-09-24, 5).
