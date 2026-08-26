---
name: codex
category: 2
surfaces: [terminal]   # `codex app` launches the desktop app on macOS/Windows (cli/src/desktop_app.rs); cloud Codex is the async-remote sibling, a separate product
execution: local   # cloud-tasks crate integrates the async-remote sibling from the CLI
environments: [host]   # the point: OS-level sandboxing is compiled INTO the harness (seatbelt/landlock/bwrap/windows) — see Surprises 1
environment_relation: internalize   # Seatbelt/Landlock/bwrap/Windows sandbox compiled INTO the binary, invoked per tool call — verified at deep-dive 2026-07-30
maker: OpenAI
url: https://github.com/openai/codex
license: Apache-2.0
open_source: true
stack: [Rust, TypeScript]
version: rusty-v8-v150.4.0-94-g413492cd6c
commit: 413492cd6c
first_commit: 2025-04-16
stars: 102646
stars_at: 2026-07-30
read_at: 2026-07-30   # drift-checked 2026-08-16 at 57f42a8113 without re-reading (rule 4b) — three claims corroborated, two refined, the stuck-loop absence settled; pin deliberately not moved
depth: deep-dive
harness_features:
  mcp: true              # codex-mcp, mcp-server, rmcp-client crates; MCP prewarm in the turn loop
  lsp: false             # no LSP crate in the 94-crate workspace (crate list checked 2026-07-30); file-search is its own crate
  hooks: true            # hooks crate + hook_runtime.rs; stop hooks can veto turn termination (session/turn.rs)
  turn_end_gates: hook   # ADR-0012 graded: run_turn_stop_hooks → should_block injects a continuation prompt and loops (session/turn.rs:467-474, drift-corroborated 2026-08-16); set 2026-08-18 from the existing deep-dive read
  tool_approval: true    # SafetyCheck::AskUser at dispatch, inside the internalized OS sandbox — gate and sandbox stacked in one tool; set 2026-08-25 transcribing the category-2 index absorption table's verified instance at this pin, no re-read
  skills: true           # skills + core-skills crates; SKILL.md consumed (also confirmed from spec-kit's registry, conclusion 3)
  subagents: true        # multi_agents handlers, codex_delegate.rs, agent-graph-store
  ptc: true              # code-mode* crates: model-written code in embedded V8, V8 sandbox enabled (ADR-0012; set 2026-08-18 from the existing deep-dive read)
  plan_mode: true        # plan tool (tools/handlers/plan.rs) + collaboration-mode-templates crate
  rules_files: [AGENTS.md]   # agents_md.rs: root-down AGENTS.md collection ONLY — no competitor files (contrast hermes)
  model_agnostic: true   # model-provider, ollama, lmstudio crates — BYO works, but the product is OpenAI-first by design
  learning_loop: true    # OFF by default: two-phase startup pipeline (turn_processor.rs:594), feature `memories` Stage::Stable default_enabled: false
---

# Codex CLI

OpenAI's vendor-native harness: a Rust workspace of **94 crates** compiled into a single
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
| 104 feature flags with staged rollout (`Stable`/`UnderDevelopment`/`Removed`) | Distinctive — vendor product discipline in an open repo |
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

## Open questions

- What exactly do `analytics`/`otel` collect and where does it go? The
  training-data-instrument pattern (taxonomy boundary rule) predicts one answer;
  untraced here.
- Is there a stuck-loop guard anywhere? Its absence from the turn path is recorded
  above as unverified — a targeted grep for repeated-call detection is cheap and would
  settle it.
- `chronicle`, `guardian`, `personality`, `realtime` — how much of the chat product is
  migrating into the harness, and does that dilute or compound the security bet?
- Does code-mode's sandboxed-V8 PTC actually get used by the models (same question as
  hermes' refund incentive), and do intermediate results stay out of context the same
  way?
- The Bazel + RBE + 676 snapshot tests infrastructure — what does CI catch that the
  other harnesses' setups can't? (cline's `evals/` remains the only *behavioral* suite
  claim in the set.)
