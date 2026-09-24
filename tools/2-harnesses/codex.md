---
# PIN MOVED 413492cd6c → b412ff32c4 (= tag rust-v0.156.1) at the 2026-09-24 release re-read
# (rule 4b: three Opus tracts — release substance, per-claim confrontation at all three
# pins, provenance — main-session spot-verification; window 2,347 commits). The 2026-08-16
# drift check stays dated at its own ref 57f42a8113 — a 2026-08-06 commit; the clone was ten
# days stale when it ran, corrected in place. Own-pin defects corrected in place.
name: codex
category: 2
surfaces: [terminal]   # `codex app` launches the desktop app on macOS/Windows (cli/src/desktop_app.rs); cloud Codex is the async-remote sibling, a separate product
execution: local   # cloud-tasks crate integrates the async-remote sibling from the CLI
environments: [host]   # the point: OS-level sandboxing is compiled INTO the harness (seatbelt/landlock/bwrap/windows) — see Surprises 1
environment_relation: internalize   # Seatbelt/Landlock/bwrap/Windows sandbox compiled INTO the binary, invoked per tool call — verified at deep-dive 2026-07-30
maker: OpenAI
url: https://github.com/openai/codex
license: Apache-2.0
access: open-source
stack: [Rust, TypeScript]
version: rust-v0.156.1   # `git describe` at the tag; at the old pin it read `rusty-v8-v150.4.0-94-…` because product release tags are cut on 1–7-commit spurs off main that never merge back — no rust-v* tag is an ancestor of main (0 of 5 sampled)
commit: b412ff32c4
first_commit: 2025-04-16
stars: 126329
stars_at: 2026-09-24   # gh api; 102,646 at 2026-07-30 (+423/day)
read_at: 2026-09-24   # rust-v0.156.1 release re-read (§ Release re-read); deep-dive 2026-07-30 @ 413492cd6c, drift-checked 2026-08-16 at 57f42a8113 (a 2026-08-06 commit) without re-reading (rule 4b) — three claims corroborated, two refined, the stuck-loop absence settled; pin deliberately not moved
depth: deep-dive
harness_features:
  mcp: true              # codex-mcp, mcp-server, rmcp-client crates; MCP prewarm in the turn loop
  lsp: false             # no LSP crate in the 94-crate workspace (crate list checked 2026-07-30); file-search is its own crate — RE-CHECKED 2026-09-24 at b412ff32c4: 0 hits for lsp|language.server|tower-lsp|lsp-types over codex-rs/ (150 workspace members; "94-crate" corrected — see § Release re-read)
  hooks: true            # hooks crate + hook_runtime.rs; stop hooks can veto turn termination (session/turn.rs)
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04 from the deep-dive: no index; file content arrives via model-dispatched read/search tools. WorldState diff-injection is state freshness, not retrieval (body § WorldState)
  context_compaction: [llm-summarize, truncate]  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: default path is LLM summarization (core/src/compact.rs, local/remote/remote-v2 by provider); an OPT-IN token_budget feature (Stage::UnderDevelopment, features/src/lib.rs:1337-1341) swaps in a hard non-LLM reset that "skips model/server summarization and installs a fresh context window" (compact_token_budget.rs:23, start_new_context_window at :82) At b412ff32c4: compact_remote.rs is gone (compact.rs + compact_remote_v2*, new compact_remote_history*); a fourth phase, PostTurn compaction, fires after the stop hooks (turn.rs:707-735, gated on model_post_turn_compact_threshold_percent > 0); citations moved (features/src/lib.rs:1673-1676, compact_token_budget.rs:21/:73)
  turn_end_gates: hook   # ADR-0012 graded: run_turn_stop_hooks → should_block injects a continuation prompt and loops (session/turn.rs:467-474, drift-corroborated 2026-08-16); set 2026-08-18 from the existing deep-dive read At b412ff32c4: run_turn_stop_hooks → should_block at core/src/session/turn.rs:646/:663 (the cell's :467-474 were the DRIFT pin's numbers; :464/:471 at the report's own pin — corrected 2026-09-24); NEW: a MemoryConsolidation session that a Stop hook blocks now hard-errors instead of looping ("Do not feed managed rejections back into an unattended memory loop", turn.rs:653-662) — the veto is no longer universal, and the carve-out is the closest thing to loop protection in the turn path
  tool_approval: policy  # SafetyCheck::AskUser at dispatch, inside the internalized OS sandbox — gate and sandbox stacked in one tool; set 2026-08-25 transcribing the category-2 index absorption table's verified instance at this pin, no re-read CORRECTED 2026-09-24 (true at both pins): `SafetyCheck` governs apply_patch ONLY (core/src/safety.rs; consumed by apply_patch.rs alone; `assess_patch_safety` is the one such function) — shell/command calls are classified by `ExecApprovalRequirement::{Skip, NeedsApproval, Forbidden}` (core/src/tools/sandboxing.rs:156-175 @ old, :153-171 @ new), which is where execpolicy lands; H3's three-way category survives through the other enum. At b412ff32c4 `AutoApprove` lost its `{sandbox_type, user_explicitly_approved}` payload (7750465934, 2026-08-03 — three days BEFORE the drift pin, which called it "intact" by restating variant names). Approval precedence is now written in source (tools/approvals.rs:500-502): hooks → Guardian (if routed) → user — and the GUARDIAN is a model-emitted verdict that becomes `ReviewDecision::Approved` (ext/guardian-reviewer/src/completion.rs:143,169-170; present at the old pin too, core/src/guardian/review.rs:558-613), default routed to the human (`ApprovalsReviewer` `#[default] User`, both pins) while its machinery ships on (`guardian_approval` Stable/true, both pins) and managed config can force it per model. ADR-0053's parked model-authority axis: an approve-capable, separate-reviewer-model shape — flagged, not admitted
  gate_model_authority: approve  # the Guardian reviewer — a separate session on its own model slug whose `Allow` becomes ReviewDecision::Approved (ext/guardian-reviewer/src/completion.rs:143,169-170 @ b412ff32c4; core/src/guardian/review.rs:558-613 at the old pin); default routed to the human (`ApprovalsReviewer` #[default] User, both pins), machinery on (`guardian_approval` Stable/true), forcible per model by managed config
  unbypassable_gates: false  # `--dangerously-bypass-approvals-and-sandbox` (codex's own CLI flag, cited as a child-launch flag in warp.md) and `AskForApproval::Never` remove both the ask gate and the sandbox
  skills: true           # skills + core-skills crates; SKILL.md consumed (also confirmed from spec-kit's registry, conclusion 3)
  subagents: true        # multi_agents handlers, codex_delegate.rs, agent-graph-store
  ptc: true              # code-mode* crates: model-written code in embedded V8, V8 sandbox enabled (ADR-0012; set 2026-08-18 from the existing deep-dive read) CORRECTED 2026-09-24 — "V8 sandbox enabled" was FALSE at the pin: code-mode-runtime declared `[features] sandbox = ["v8/v8_enable_sandbox"]` that nothing enabled (sole consumer code-mode-host took default features; workspace `v8 = "=150.4.0"` bare); it became unconditional in 2e32d95894 (2026-07-31, "Enable sandboxed V8 for code mode", ONE DAY after the read) and is `features = ["v8_enable_sandbox"]` at b412ff32c4 (code-mode-runtime/Cargo.toml:26). The hermes-vs-codex enforcement gap in Surprise 6 did not exist at the pin it was written at; it exists now. Also: the published artifact ships code mode as a separate 70 MB `codex-code-mode-host` binary (rule 8b, npm @openai/codex@0.156.1-linux-x64)
  plan_mode: mode        # REGRADED tool → mode 2026-09-24 (ADR-0058 pass): a sticky `CollaborationMode { mode: ModeKind::{Plan, Default}, settings }` with its own model/effort/instructions and a plan template injected as a WorldState section (protocol/src/config_types.ts:674, :705-752 @ b412ff32c4; :630 at the old pin); `update_plan` is a TODO-artifact tool. Weak enforcement: Plan does not restrict the advertised tool set. Original: plan tool (tools/handlers/plan.rs) + collaboration-mode-templates crate REGRADE CANDIDATE → `mode` (2026-09-24, both pins): a sticky `CollaborationMode { mode: ModeKind::{Plan, Default}, settings }` with its own model/effort/instructions and a plan.md template injected as a WorldState section; the `update_plan` tool is a TODO-list artifact tool. Plan mode does not restrict the advertised tool set (0 hits for ModeKind::Plan in tools/spec_plan.rs). Owner gate
  rules_files: [AGENTS.md]   # agents_md.rs: root-down AGENTS.md collection ONLY — no competitor files (contrast hermes) INCOMPLETE at both pins (corrected 2026-09-24): agents_md.rs reads `AGENTS.override.md` first, then `AGENTS.md`, plus a user-configurable `project_doc_fallback_filenames` list, default empty (:273-276 @ new; :236-237 @ old) — "no competitor files" is a default, not a structural fact; 0 hits for CLAUDE.md|.cursorrules|GEMINI.md in core/src at either pin
  model_agnostic: true   # model-provider, ollama, lmstudio crates — BYO works, but the product is OpenAI-first by design
  learning_loop: background  # OFF by default: two-phase startup pipeline (turn_processor.rs:594), feature `memories` Stage::Stable default_enabled: false At b412ff32c4: still `memories` Stable/false; the single call site moved to app-server/src/request_processors/turn_processor.rs:688 and gained an `is_primary_environment_configured()` gate — the pipeline is a property of the app-server surface, not of core
---

# Codex CLI

OpenAI's vendor-native harness: a Rust workspace of **128 declared member crates** (`members = […]` in codex-rs/Cargo.toml; 93 top-level directories carry a Cargo.toml; 150 / 108 at rust-v0.156.1 — *corrected 2026-09-24: "94 crates" reproduced under none of seven measures, and 94 is the commits-since-tag count in the old `version:` string*) compiled into a single
`codex` binary (arg0 dispatch multiplexes subcommand personalities), fronting a TUI, a
headless `exec` mode, and an app-server daemon that the desktop app, SDK, and editors
talk to. The only harness in this set written in a systems language — and the read shows
that's load-bearing, not aesthetic. Leads Terminal-Bench 2.1 (with its own models; the
benchmark can't separate the two — README conclusion 2).

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

206 commits / 1058 files since the read; **60 of them touch a file this report cites**,
which is the set that was checked. Nothing here was wrong at the pin. The substantive
outcome is that the report's one open *absence* is now settled.

**1. Settled: the missing stuck-loop guard is a verified absence, not an unverified one.**
The read checked `turn.rs` and the tool-router surface and recorded "possibly elsewhere".
Checked properly this time: a pattern grep across the **entire `codex-rs/` Rust
workspace** at HEAD for `repeated_call` / `repeat_count` / `doom.?loop` / `stuck.?loop` /
`loop_detect` / `identical_call` returns **zero** non-test hits, as does a search for any
iteration or step cap (`max_iterations`, `max_steps`, `iteration_limit`, `step_budget`).
No commit in the 206 mentions a loop, repeat, stuck, doom, spin or runaway guard.

*Scope, stated because rule 4a demands it:* this is a pattern grep over the Rust
workspace at HEAD, not a reading of every dispatch path, and the pin's full tree was not
grepped (a blobless clone makes a historical whole-tree grep expensive). Absence at HEAD
plus a silent drift implies absence at the pin unless a guard was removed without saying
so, which the log does not support. That is enough to stop calling it unknown: **codex
ships no repeated-call guard.** This settles the deferral in design-principle H2 — codex
now counts as a verified counter-instance rather than a silence.

**2. Corroborated — all three claims other notes cite.** The stop-hook veto that
conclusion 8 rests on is intact (`run_turn_stop_hooks` → `should_block` at
`session/turn.rs:467–474`). H3's decision category is intact (`SafetyCheck::{Reject,
AskUser, AutoApprove}`, `core/src/safety.rs:20+`). Conclusion 1's per-model-slug data
point survives: `ModelInstructionsState` and `get_model_instructions(personality)` are
present in `session/world_state.rs` at **both** the pin and HEAD.

**3. Refined — how model instructions are sourced.** #36787 (landed 2026-08-03) removed
`ModelInfo.base_instructions` as an in-memory instruction source, consolidating on
`model_messages.instructions_template`, with legacy values promoted for compatibility.
Per-model swapping survives — the commit's own tests cover "canonical-template
precedence… and model switching" — so conclusion 1's reading holds, but the mechanism is
now a rendered template rather than a per-slug string. Worth knowing before anyone
quotes this report on *how* codex varies prompts by model.

**4. Refined — permissions are read live, not snapshotted.** #36912 (2026-08-04) removed
a duplicated approval-policy field from `TurnContext` because "thread settings can update
the approval policy after a turn context is created… tool approval checks [could use] the
previous policy." Policy is now resolved through the turn's current configuration
everywhere it is needed — tool execution, Guardian routing, MCP handling, permission
requests. This is concrete support for H3's third category rather than a contradiction: an
enforcement category that reads a stale snapshot of policy is not an enforcement category, and
the fix is upstream discovering exactly that.

**What a re-read should cost:** moderate. The permission and tool-namespace subsystems
took the heaviest churn (strict tool-name collisions, per-surface MCP exposure controls,
turn-environment permissions), so the tool-surface section is the one describing the
most-changed component.

## The distinguishing bet

**That the harness is a security boundary, and a security boundary must be compiled.**

The stub predicted the Rust bet was about latency; the source says otherwise. Every
other harness here delegates isolation: hermes to Docker/remote backends, opencode to a
`containers` package, frameworks to whatever the host harness does. Codex compiles the
boundary *into the process*:

- **`sandboxing/`** — macOS Seatbelt (the `.sbpl` policies ship as data files in the
  crate), Linux Landlock + a bwrap path, `windows-sandbox-rs`. Sandboxing is a
  *library the loop calls per tool execution*, not an environment you run the agent in.
- **`process-hardening/`** — runs **pre-`main()`** via `#[ctor]`: disables core dumps
  and ptrace attach, strips `LD_PRELOAD`/`DYLD_*` from the environment. The binary
  distrusts its own host before executing a line of application code.
- **`execpolicy/`** — a policy engine classifying commands *before* execution, feeding
  `SafetyCheck::{AutoApprove{sandbox_type}, AskUser, Reject}` (`core/src/safety.rs:21`).
- **`code-mode*/`** — programmatic tool calling runs model-written code inside an
  **embedded V8 with the V8 sandbox enabled** (`code-mode-runtime` carries a
  `sandbox = ["v8/v8_enable_sandbox"]` feature; `v8-poc` exists solely to verify the
  linked V8 was built sandboxed).

This answers the stub's seeded question — **why Rust?** Because Landlock, Seatbelt
spawning, Job objects, pre-main ctors, and an embedded V8 are syscall-level engineering.
A Node or Python harness can *invoke* a sandbox; a Rust harness can *be* one. The other
seeded question — **`agent-graph-store`?** — resolves to something much smaller than the
name suggests: a storage-neutral parent/child topology store for thread-spawned agents
(multi-agent bookkeeping, not a knowledge graph).

## Main features

| Feature | Distinctive? |
|---|---|
| In-process OS sandboxing (Seatbelt/Landlock/bwrap/Windows) + pre-main hardening | **Unique in this set** |
| WorldState: sectioned, snapshot-diffed ambient context (see Architecture) | **Unique in this set** |
| code-mode: PTC in embedded sandboxed V8 | Convergent mechanism (hermes' `execute_code`), unique enforcement |
| Autonomous two-phase memory pipeline (stable, default-off) | Convergent with hermes' learning loop — see Surprises 3 |
| ~~104~~ **102** feature flags (`^    FeatureSpec {` entries; "104" also counted the struct declaration and a fn signature — corrected 2026-09-24; 149 at rust-v0.156.1) with staged rollout (`Stable`/`UnderDevelopment`/`Removed`) | Distinctive — vendor product discipline in an open repo |
| App-server protocol + daemon + SDK (harness as a service) | Distinctive |
| Model-queryable context economics (`get_context_remaining`, `new_context_window` tools) | **Unique in this set** |
| MCP client + server, skills, hooks, plan tool, subagents | Table stakes by mid-2026 |

## Stack & repo shape

Rust: 2,819 `.rs` files across a **94-crate** Cargo workspace under `codex-rs/`, built
with both Cargo and **Bazel** (MODULE.bazel, remote-build-execution config — CI at a
scale no one else in the set needs). 676 `.snap` files — snapshot-test culture via
`insta`. TypeScript (656 files) lives in the SDK, the npm distribution wrapper
(`codex-cli/`), and devcontainer tooling. 8,764 commits since 2025-04-16.

The version tag (`rusty-v8-v150.4.0`) is itself evidence: the repo's most recent tags
pin their own V8 builds — a vendored, sandbox-enabled V8 is maintained as part of the
product.

Crate names sketch the roadmap: `chronicle` (under development), `personality`,
`realtime_conversation` (voice), `collaboration-mode-templates`, `cloud-tasks`,
`external-agent-migration` (importing competitors' state), `guardian` (follow-up review
reminders).

## Architecture

### Entry point → one full trace

```
codex                       arg0_dispatch_or_else (one binary, multiple personalities)
  └ cli/src/main.rs         clap Subcommand: (default→TUI) | exec | app-server | login | …
      └ codex-tui           interactive; or codex-exec headless; both →
          └ core: ThreadManager → CodexThread
              └ tasks/regular.rs          one user submission = a Task
                  └ session/turn.rs:150   run_turn — the spine
                      └ [step loop] capture_step_context → WorldState diff →
                        run_sampling_request → tool router → repeat
```

The app-server daemon wraps the same core behind a JSON-RPC protocol
(`app-server-protocol`) — the TUI, desktop app, SDK, and MCP server are all clients of
one loop implementation.

### The agent loop

`run_turn` (`core/src/session/turn.rs:150`). Each iteration: capture a **step context**
(a request-scoped snapshot of environments, AGENTS.md, capability roots), rebuild
**WorldState**, diff it (below), assemble history, run one sampling request, dispatch
tools. Termination (`turn.rs:430–560`, verified at the branch sites):

- **No step or iteration budget.** The loop ends when the model needs no follow-up and
  no pending input is queued — like opencode's explicit conditions, unlike hermes'
  500-cap.
- **Stop hooks can veto the stop**: `run_turn_stop_hooks` may return `should_block`,
  which injects a continuation prompt and loops again — user-policy gates at turn end,
  the same architectural slot as hermes' `verification_stop`/`pre_verify` (second
  category-2-native instance for the cross-cutting verification note).
- **Compaction is a loop outcome** (third convergent instance of design-principle H1):
  `token_limit_reached` → `run_auto_compact(…, CompactionPhase::MidTurn)` → `continue`.
  There's also *pre-sampling* compaction before the turn starts, and the model itself
  can request a fresh window via the `new_context_window` tool.
- Mid-turn **steering** via an input queue drained between steps (deferred right after
  turn start and after auto-compact so continuations aren't hijacked).

No doom-loop/repeated-call guard was found in the loop path (checked `turn.rs` and the
tool router surface; possibly elsewhere — recorded as unverified absence, not verified).
**Settled 2026-08-16 → verified absent**: a workspace-wide pattern grep at HEAD returns
zero non-test hits for repeated-call/loop-detection or any iteration cap, and no commit
in the 206-commit drift adds one. See the drift check above for the search scope.

### Context assembly

The most distinctive design in the set: **`WorldState`** (`session/world_state.rs`) is a
list of typed sections — model instructions (per model slug, so switching models
mid-thread swaps instructions), personality, AGENTS.md content, permissions
instructions, tools state, environments, plugins, token-budget guidance. Per step:

1. rebuild WorldState from the step context;
2. snapshot it and **diff against the previous snapshot**
   (`record_step_world_state_if_changed`, `session/mod.rs:2989`);
3. inject **only the rendered diff** into history as developer/contextual-user messages
   (merged by role, `context_manager/updates.rs`);
4. persist the patch to the rollout for replay.

This is a third position on the cache-vs-freshness tradeoff that design-principle H5
recorded as two: hermes freezes the prefix and accepts staleness; codex keeps the
prefix append-only *and* gets fresh state by appending deltas — cache warmth and
freshness both, paid for in machinery and history growth. AGENTS.md is collected
root-down per directory (`agents_md.rs`) — and *only* AGENTS.md: no CLAUDE.md, no
`.cursorrules` (the inverse of hermes' read-everyone's-files posture). Memories, when
enabled, inject with **citations** (`memories/read`), and the model can interrogate its
own budget via `get_context_remaining`.

Compaction is a subsystem, not a function: `compact.rs` plus remote variants
(`compact_remote_v2`), a token-budget module, model fallback, and rollout truncation —
with its own prompt templates in the `prompts` crate.

### Tool surface & permissions

Tools live in `core/src/tools/`: a registry + router + orchestrator with genuine
**parallel dispatch** (`parallel.rs`), ~30 handlers across 57 files (shell, unified
exec, apply_patch with a formal `.lark` grammar, plan, view_image, multi-agents,
request_user_input, `tool_search` for deferred discovery, `wait_for_environment`,
`sleep`).

The permission architecture is **three-layered**, extending the two-chokepoint pattern
(design-principle H3) downward:

1. **Visibility**: the advertised tool set is finalized per step (`spec_plan.rs`) from
   feature flags, collaboration mode, and available capability roots.
2. **Decision**: `assess_*_safety` (`safety.rs`) classifies each call —
   `AutoApprove{sandbox_type}` / `AskUser` / `Reject` — driven by the `AskForApproval`
   policy (including `Granular`), the execpolicy engine, and writable-paths analysis.
3. **Enforcement**: approved commands still execute **inside the OS sandbox** chosen in
   step 2, with an escalation path (`shell-escalation`) when a sandboxed run fails for
   sandbox reasons, network approval as its own flow, and hard denials (approval can't
   grant what Landlock/Seatbelt won't).

The harness asks the human *while holding the model inside a cage it built itself* —
the approval prompt is a UX courtesy on top of enforcement, not the enforcement.

### Category boundaries in the code

- **category 1:** OpenAI-native (Responses API, `responses-api-proxy`), but
  `model-provider`, `ollama`, `lmstudio`, `aws-auth` make BYO real. Notably
  model-*conditioned*: instructions swap per model slug inside WorldState — a fifth
  data point for the per-model-prompt question (the vendor-native pole: one vendor,
  many of its own models, instructions per model).
- **category 6:** MCP client *and* server; skills; hooks; plugins with an install-request
  tool. `external-agent-migration` imports competitors' state — category-6 interop as a
  product feature.
- **category 4:** plan tool, collaboration-mode templates, `guardian` review reminders —
  the usual absorption.
- **category 3:** **internalized, not bundled** — the taxonomy's "harness binds to
  environments" framing inverts here; see Surprises 1.

## Bleed

Categories 3 and 4 as above. The category-3 relationship is the notable one: not a binding to
external environments but an *absorption of the environment category into the harness
binary* (in-process OS sandboxes + embedded sandboxed V8). Category 1 bleed runs in both
directions: vendor-native models, and telemetry crates (`otel`, `analytics`) feeding
the maker — same pattern class as the taxonomy's training-data-instrument note, though
what's actually collected wasn't traced in this read.

## Cost model

Apache-2.0, free; inference via ChatGPT subscription plans or API key — the
flat-vs-metered choice inside one product. BYO local models (Ollama, LM Studio) make
the zero-marginal-cost end real. The cloud sibling meters separately.

## Surprises

1. **category 3 lives inside the binary.** The taxonomy models execution environments as
   external products a harness *binds to*; codex compiles Seatbelt policies, Landlock,
   bwrap, and a Windows sandbox into the harness and hardens its own process pre-main.
   That's a stress-test-worthy case: not bundling (Devin), not binding (hermes) —
   *internalization*.
2. **WorldState diffing** — ambient context as a snapshot-diffed state machine,
   resolving the cache-vs-freshness tradeoff by appending deltas instead of choosing.
   Design-principle H5 needs a third position.
3. **An autonomous memory pipeline, shipped but off.** Two-phase (extraction from
   rollouts → spawned consolidation agents), verified at the call site
   (`turn_processor.rs:594` — fires at turn start for eligible root sessions), feature
   `memories`: `Stage::Stable, default_enabled: false`. With hermes, that's **two
   verified autonomous learning loops** — issue #2's decision-rule threshold, met one
   read early. The posture difference is the finding: hermes ships it on; OpenAI built
   it, stabilized it, and left it off.
4. **104 feature flags** with lifecycle stages, in an open-source repo — the release
   engineering of a hosted product applied to a CLI. Also the first tool here whose
   *flag list* is a roadmap leak (chronicle, realtime, personality).
5. **The model manages its own context window** — `get_context_remaining` and
   `new_context_window` as tools. Context economics promoted from harness-internal
   bookkeeping to model-visible affordances.
6. **PTC convergence with a security twist**: hermes and codex independently built
   "model writes code that calls tools" (hermes: Python over UDS/file RPC, iterations
   refunded; codex: JS in embedded V8 *with the V8 sandbox on*). Two instances make
   programmatic tool calling a pattern, and the enforcement gap between them is the two
   products' bets in miniature.
7. **`external-agent-migration`** — a crate whose job is importing other agents' state.
   Competitor interop as a first-class feature, the offensive counterpart of hermes
   reading `CLAUDE.md`.

## Release re-read — rust-v0.156.1 (2026-09-24; pin 413492cd6c → b412ff32c4)

Three Opus tracts, load-bearing claims re-run at three pins. Window
`git rev-list --count 413492cd6c..rust-v0.156.1` = **2,347**, 0 merges; `git diff --stat --
codex-rs` 5,920 files, +801,325 / −150,508; `.rs` files 2,819 → 4,698; workspace members 128 →
150 (+25 −3: `mxc-sandbox`, `windows-sandbox-service`, `voice-host`, `guardian-context`,
`worktree`… in; `mcp-server`, `core-skills`, `ext/guardian` out). The tag is a two-commit spur
off `d583e73c4d` (2026-09-21); main is 245 past that.

**1. The public repo is a projection.** 2,346 of 2,347 window commits carry `GitOrigin-RevId:`;
every sampled PR (23/23, incl. #36787 and #36912 the drift check cites) was opened *and*
merged by `copyberry[bot]` within ~2 minutes from a `copyberry/codex-internal-to-codex-oss/…`
branch; the export baseline commit ("Initialize Copyberry export baseline", 2026-07-10) is
20 days before the old pin. Consequences: 0 merges, 1:1 commit↔PR, **3 open PRs against
18,455 open issues** (5.6:1 inflow:outflow in the window), and the export strips trailers —
`Co-authored-by` 914/8,084 pre-export vs 2/3,270 after: codex's history *cannot* report
agent authorship since 2026-07-10, and a naive bot-share read (0%) is exactly backwards.
Velocity 18.0/day pre-export → 42.7/day; top five authors 44%; 97.5% `@openai.com`.

**2. The loop.** Same `run_turn` (turn.rs:163), same stop-hook veto (:646-693) with a new
`should_stop` sibling and the MemoryConsolidation carve-out; a fourth compaction phase
(PostTurn); an 11th hook event, `Interrupt` (notify-only); a one-shot compaction retry
with the comment "so ineffective compaction cannot loop". **Stuck-loop guard: absent at all
three pins**, now measured rather than inferred (the drift check declined the historical
grep as "expensive"; it runs in seconds): the ten-pattern grep returns 0 non-test hits at
413492cd6c, 57f42a8113 and b412ff32c4, 0 window subjects, 0 in `docs/`, no step/turn key in
`config.schema.json`. **But a token-denominated session budget exists at both pins** —
`rollout_budget.rs` (blob present at the old pin) returns `CodexErr::SessionBudgetExceeded`
when weighted tokens exceed `limit_tokens`; feature `rollout_budget` UnderDevelopment/false
both pins. The corrected sentence: no repetition guard, no step cap, an opt-in token ceiling.
Upstream #33294 asks for `--max-steps`, filed 15 days before the old pin, 0 comments at 71
days. The only "stuck loop" in the tree is a memories prompt telling the model to label one.

**3. Context assembly.** `get_model_instructions` is **gone** (0 hits) → `codex_prompts::
render_model_instructions` (prompts/src/model_instructions.rs:8), rendered by
`ModelInstructionsState::render_diff` only when the model changes; `BaseInstructions` returned
as a protocol type *with provenance* (`Custom` survives model swaps; `Model{model}` does not).
Conclusion 1's data point is strengthened and now measured: distinct per-model instruction
templates in models.json **5 → 8** (8 → 11 models carrying one). WorldState sections +4/−1
(`personality` removed — flag Stable/true → Removed; `realtime_conversation`
UnderDevelopment/false → Stable/true: personality died, voice shipped). A BM25 ranked index
exists at both pins over *skills and tools* (`ext/skills/src/dynamic_skill_selector/
fielded_bm25.rs`, `tool_search.rs`; `skill_search` Stable/true) — `context_retrieval:
model-driven` stands because the key scopes repo content; flagged as candidate vocabulary.

**4. The gate.** See the `tool_approval` and `ptc` cells: `SafetyCheck` is patch-only and lost
its payload; the Guardian is a model that can approve; the V8 sandbox was off at the pin.
`SandboxType` gained a fifth platform, `WindowsMxc` (new crate `mxc-sandbox`), seatbelt
learned to deny its own daemon sockets, `protocol/src/permissions.rs` 3,415 → 4,488 lines with
policy now resolved against an explicit context; `process-hardening/` changed by **zero
bytes** in 2,347 commits — and its pre-`main()` `#[ctor]` claim is TESTIMONY at both pins:
the only production `#[ctor::ctor]` site is `responses-api-proxy/src/main.rs:4`; the `cli`
crate does not depend on the hardening crate (rule 4a; recorded, not retracted). A fourth
enforcement surface the report never named: the egress credential broker
(`network-proxy/src/credential_broker*`, present at both pins, +1,631 lines) hands the agent
placeholder secrets and substitutes real ones on the wire.

**5. Release notes vs tree.** The release commit's message *is* the notes (why it alone lacks
`GitOrigin-RevId`); 8 of 8 v0.156.0 claims land in the tree; the notes narrate TUI and
voice and never name the sandbox generation that took 5.5% of window subjects. **8b**: the
published `@openai/codex@0.156.1` is a 13 KB, 3-file launcher whose `package.json` in the
tree says `0.0.0-dev` with no `optionalDependencies` — the six platform packages (linux-x64:
387 MB, a 284 MB musl `codex` plus a 70 MB `codex-code-mode-host` and a voice host) are
injected at publish by `build_npm_package.py:297-307`.

**6. The re-read's own audit.** With-measure counts **7/7** (2,819 / 676 / 656 / 8,764 / 206
/ 1,058 / the absence grep); without **1/5** ("94 crates", "104 flags", "57 files" = directory
entries, "60 commits" ≈ 61, stars n/a). Never-reproduced at own pin: `cli/src/desktop_app.rs`
(a directory), `new_context_window` (the wire tool is `new_context`), "crate names sketch the
roadmap" (three of seven are flag keys), `v8-poc` "exists solely to…" (one of three
exports), "V8 sandbox enabled". The 2026-08-16 drift check corroborated a *paraphrase*
(bare variant names) of a claim (the payload) that had been false for 13 days, and ran on a
2026-08-06 clone (true drift then: 585 commits, not 206). Its one forward claim — "a
re-read should cost moderate; the tool-surface section is the most-changed" — scored right on
the component, wrong on magnitude, and inherited the 2.8× undercount beneath it.

**Predictions (dated, falsifiable).** P-1: on **2026-12-24** the `members` array at the
then-`latest` tag exceeds **180** (128 → 150 in 54 days). P-2: the ten-pattern loop-guard
grep still returns 0 non-test hits and `rollout_budget` is still UnderDevelopment/false.
P-3: `memories` still Stable/false — written down because it looks safe: if OpenAI flips it,
Surprise 3's hermes contrast collapses in one release. Next trigger: the next stable
`rust-v0.N.0` after the next re-read is due, or 2026-12-24.

## Open questions

- What exactly do `analytics`/`otel` collect and where does it go? The
  training-data-instrument pattern (taxonomy boundary rule) predicts one answer;
  untraced here.
- ~~Is there a stuck-loop guard anywhere?~~ **Settled 2026-08-16, re-measured at three pins
  2026-09-24: no repetition guard, no step cap — and an opt-in token session budget the greps
  could not see** (§ Release re-read 2).
- `chronicle`, `guardian`, `personality`, `realtime` — how much of the chat product is
  migrating into the harness, and does that dilute or compound the security bet?
- Does code-mode's sandboxed-V8 PTC actually get used by the models (same question as
  hermes' refund incentive), and do intermediate results stay out of context the same
  way?
- The Bazel + RBE + 676 snapshot tests infrastructure — what does CI catch that the
  other harnesses' setups can't? (cline's `evals/` remains the only *behavioral* suite
  claim in the set.)
