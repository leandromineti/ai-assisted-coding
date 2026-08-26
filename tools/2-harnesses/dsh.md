---
name: dsh
category: 2
surfaces: [web]
execution: local
environments: [host, remote-sandbox]  # remote-sandbox = the e2b POC packages, verified in source, opt-in, no shipped bundle
environment_relation: internalize
vendor: DeepSeek
url: https://github.com/deepseek-ai/deepseek-harness
license: MIT
open_source: true
stack: [TypeScript, Node.js]
version: dsh-v0.1.1-rc.2
commit: b150a551b8
first_commit: 2026-06-10
stars: 190941
stars_at: 2026-08-24
read_at: 2026-08-24
depth: deep-dive
harness_features:
  mcp: true              # client only, tools-only bridge, NOT default-mounted ("each server command is trusted executable code outside the agent sandbox", apps/cli/reference/README.md:93)
  lsp: true              # agent-consumed `lsp` tool, 4 read-only ops; diagnostics explicitly discarded (lsp-stdio/src/connection.ts:254); not in any shipped bundle
  hooks: true            # typed engine events default-on; PLUS bridges that run unmodified Claude Code hooks.json / Codex hook configs (packages/hooks/*) — bridges in no shipped bundle
  turn_end_gates: engine # agent/turn-stopping serial boundary, "data decides" (agent-loop/src/agent.ts:294-300); hook grade also reachable via the CC-bridge Stop mapping
  tool_approval: false   # checked and absent (2026-08-24 deep-dive): tools/pre-execute default is allow (core/tools/src/index.ts:1477); the gate is the compiled per-call sandbox, and the sole prompt in a stock run is a model-initiated one-shot sandbox escalation
  skills: true           # SKILL.md convention, 6-root precedence, digest-gated catalog; on in standard/code/cordis presets
  subagents: true        # 6 providers incl. real Codex and Claude Code children; spawn/fork in base bundle, depth cap 3 (bypassed via workflow/ralph — host.ts:352)
  ptc: true              # run_code in a Node worker thread, tools bound as typed fns from the live registry; default mode `native`, opt-in via DSH_TOOLS_MODE or the shipped "PTC 模式" preset
  plan_mode: true        # sticky LOGGED session state + prompt section + exit tool; deliberately NOT a tool restriction (plan-mode/src/index.ts:1-7)
  rules_files: ["AGENTS.md", "CLAUDE.md", "AGENTS.local.md", "CLAUDE.local.md"]  # + user-global ~/.dsh/AGENTS.md; per-preset (the `minimal` preset omits the loader entirely)
  model_agnostic: true   # llm seam + pi-ai adapter (3 wire protocols); DeepSeek privileged in every default (agent-default-model → deepseek-v4-flash)
  session_sharing: true  # export/artifact only: session ZIP export + resume; share LINKS verified absent (no shareUrl anywhere; loopback-bound server)
  evals: false           # checked and absent: no model/agent benchmark harness anywhere (find over eval|bench dirs → empty); 872 unit specs + transcript-replay snapshots are software tests, not evals
  learning_loop: false   # checked and absent: no native agent-written memory or store; agent-instructions is a pure reader; vendor ships default-off third-party MCP memory examples with "no memory server is present in the shipped composition"
---

# dsh (DeepSeek Harness)

Deep-dive 2026-08-24, three readers at the pin, one tract per ADR-0021 component —
**all three components traced**: the loop, context assembly, and the permission gate.
Claims below carry file:line at `b150a551b8` (v0.1.1-rc.2, 2026-08-21). Registered
2026-08-18 at README level ([issue #19](https://github.com/leandromineti/ai-assisted-coding/issues/19));
this read executes that ticket. One registration correction: the repo was *published*
2026-08-13 but `first_commit` is 2026-06-10 — the five-day figure is the star ramp
(159.6k at +5d; 190.9k at +11d), not the code's age.

## What it is

DeepSeek's vendor-native harness: a TypeScript plugin container (vendored Cordis, 227
packages counted by `ls -d packages/*/*/ | wc -l`) that composes an agent from ordered
YAML patch overlays over an **empty root**, launched as a locally served web UI
(`npx @deepseek-ai/dsh web`, 127.0.0.1:3080) or a headless profile. Developer preview,
breaking-changes warning, `SESSION_FORMAT_VERSION: 0` with no compatibility promise.

## The distinguishing bet

**"Everything is a plugin" — and at this pin the claim is structurally true and
mechanically checkable, including for the agent loop itself.** The loop is row 65 of 78
in the base bundle patch (`packages/bundle/base/cordis.patch.yml:436-439`), loaded with
the same two keys as `tool-bash`; it publishes itself through an `AgentFactory` seam
(`agent-loop/src/index.ts:350`) that a six-line user patch could fill with a different
implementation, and stub factories in the product's own tests prove the seam. Three
honest qualifications, all from dsh's own source: the factory is a **singleton** (a
second registration throws, `core/agent/src/index.ts:373-374`) — replaceable, not
stackable; editing it is governed by policy ("Plugins, not loop changes", root
AGENTS.md) — a plugin by construction, a de-facto kernel by convention; and its
internals are sealed (the concrete `ReactLoopAgent` is not exported). The intended
extension path is interception: five published decision points (`agent/pre-step`,
`agent/request`, `agent/request-error`, `agent/turn-stopping`, and the tool-result
channel), 59 typed events in a generated, CI-gated producer/consumer census
(`docs/event-producer-consumer.md`).

A second bet rides on the first: **KV-cache discipline as an enforced, repo-wide design
constraint** — see Context assembly.

## Stack & repo shape

13,147 commits · 7,903 tracked files · `md(2506) ts(2472) yaml(1154)` (repo-facts.sh,
2026-08-24). pnpm workspaces: `packages/<group>/<pkg>` (227), `vendor/` (Cordis, pinned
source copies with an upstream-SHA manifest), `native/landlock-run` (a static C sandbox
launcher published as its own npm family), `python/` (SDK driving a bundled Node
runtime), `apps/cli`, `apps/web`. Two shipped profiles: `web` = base+web-app bundles,
`headless` = base+headless (`boot/app-boot/src/profile.ts:113-117`). Four shipped agent
presets: `standard` (default), `code` ("PTC 模式"), `minimal`, `cordis`. Test posture:
per-file **100%** coverage thresholds in CI, 872 `.spec.ts`, 136 `.e2e.ts`, 22
boot-the-real-binary transcript-replay snapshot suites — and **zero model evals**.

## Architecture — the traced loop *(deep-dive 2026-08-24)*

- **Turn-end gate, grade `engine`, and a novel shape.** `agent/turn-stopping` is a
  serial boundary awaited before a turn may close (`agent-loop/src/agent.ts:294-300`);
  an objecting listener does not return a veto — it **steers real messages into the
  inbox**, and the loop re-reads the inbox after all listeners settle: *"Data decides,
  so listener order cannot change the outcome"* (`core/agent/src/runtime-types.ts:269`).
  Every boolean-returning Stop hook in the tracked set is order-dependent; dsh made
  multiple stop-blockers compose by construction.
- **No iteration budget, stated on purpose.** `grep` for
  `maxSteps|maxTurns|maxIterations` over non-test source → 0 product hits;
  `agent-loop/README.md:134`: *"No built-in turn budget — … a policy that bounds
  runaway turns must cancel from an existing lifecycle extension point."* One found
  bypass: children started via `workflow`/`ralph` pass no `maxDepth`
  (`workflow-worker-thread/src/host.ts:352-365`), escaping the subagent depth cap of 3.
- **Bounded auto-continuation with split authority.** `goal-round-driver` (default-on)
  re-prompts an idle agent toward an armed goal; the **model proposes** `maxGoalRounds`
  via the goal tools, a **human arms** the goal (direct-human root authority,
  `docs/tool-catalog.md`). The Ralph technique ships as a native default-on tool
  (`tool-ralph`, `maxRounds: 64`, ceiling 256): one fresh structured-output child per
  round, 16 KiB bounded handoff. Exactly one leaf tool in the repo can end a turn
  (`structured_output.concludeTurn()`); a *failed* tool result can never conclude.
- **`ptc`**: `run_code` is a reserved name outside the filterable registry tiers;
  model TypeScript is type-stripped and run in a fresh Node **worker thread** with all
  other tools bound as typed functions generated from the live registry (a Python
  flavour exists); sub-calls re-enter the full guarded executor and are logged without
  re-entering model history. Default presentation is `native`; the `code` preset flips
  it, collapsing the wire schema to `run_code` alone.
- **Dispatch**: parallel-capable, fail-closed exclusive (`isConcurrencySafe` must
  return exact `true`; only 8 tools opt in — `glob`/`grep` notably do not), cap 10,
  live-editable as a user setting; results always commit in model order; cancelled
  calls get synthetic `ABORTED_BEFORE_DISPATCH` results so replay stays valid.
- **Subagents**: deliberately thin schema (description/prompt/background only — no
  model, tools, or type choice for the model); six providers — in-process spawn/fork
  plus **real Codex (`app-server --stdio`), the official Claude Agent SDK, ACP, and a
  second dsh over stdio**. The `standard` preset carries `subagent_codex` and
  `subagent_claude_code` rows shipped `disabled: true`.
- **Hooks**: lifecycle hooks are just plugins on the typed events — and dsh ships
  bridges that run **unmodified Claude Code `hooks.json` and Codex hook configs**
  (`packages/hooks/hooks-{claude-code,codex}`), mapping `PreToolUse`→`tools/pre-execute`
  `deny/ask`, `Stop`→`agent/turn-stopping` steering, with durable
  `hook/invoked`/`hook/result` audit events. Bridges are in no shipped bundle.
- **`evals: false` is a verified absence with an interesting shape**: BENCHMARK.md is
  3 lines addressed to *external* benchmark drivers; the rigor budget went entirely to
  determinism (transcript replay, failure-injection LLM server, 100% coverage), none
  to capability scoring.

## Context assembly — cache discipline as architecture *(deep-dive 2026-08-24)*

- **The `PromptSection` / `PromptContext` split.** The system prompt is a composed,
  ordered registry (28 section call sites; assembly re-runs every step); *changing*
  facts are deliberately registered as `PromptContext` and land as **user-role messages
  after retained history** — documented at the registration sites as a cache decision
  (`user-approval/src/index.ts:201-203`: switching policy "does not rewrite the stable
  system-prompt cache prefix"). Runtime-context snapshots re-emit **only when changed**
  (`agent-loop/src/runtime-context.ts:64-75`).
- **Compaction is engineered to hit the warm cache.** Default-on LLM summarization
  (threshold 0.8 × contextWindow, plus overflow-retry) whose auxiliary call replays the
  conversation's own system prompt, tools, and message prefix and appends only the
  directive — *"a genuine prefix of the last routed request, so the provider's KV cache
  is reused instead of invalidated"* (`compaction-basic/src/summarizer.ts:24-30`). Two
  further reducers: a model-free tool-result pruner and an execution-time spill stage
  (oversized results → session artifact + head/tail preview; `read` excluded to avoid a
  re-read loop).
- **The discipline is CI-enforced prose**: every package README must carry a
  `#### KV Cache effect` section (append-only / prefix-stable / replacing / independent,
  with exact invalidation conditions), gated by
  `scripts/verify-package-readme-model-experience.ts:17`. 30+ packages carry it. This is
  a *process* control on context assembly — no other tracked harness has one.
- **Rules files with versioned reconciliation.** Candidates `AGENTS.md`/`CLAUDE.md`
  (+`.local`, + user-global `~/.dsh/AGENTS.md`), `.git`-rooted walk, injected as a
  `<system-reminder>`-framed user message under a 64 KiB budget with a deterministic
  degradation sequence (binary-search truncation; omissions stated to the model with
  byte counts). Touched files are tracked by `FsVersion`: the model is told *"This file
  changed after it was loaded. Use the following content instead"* / *"Instructions
  removed: … no longer apply."* (`agent-instructions/src/render.ts:171-184`).
- **No per-model prompts** — one interpolated persona string (`{{model}}`, `{{cwd}}`);
  greps for model-family branching in prompt code come back empty. The exact opposite
  of opencode's nine bespoke prompts, on the same edge.
- **Skills**: SKILL.md convention (two shapes), six watched roots with rank precedence
  (`.dsh/skills`, `.agents/skills`, custom, `~/.dsh/skills`, `~/.agents/skills`,
  bundled), catalog injected as a digest-gated user message, bodies pulled via a
  `skill` tool or a `/name` gesture. dsh dogfoods it (`.agents/skills/` in-repo).
- **Session log as epistemics**: "Model-visible ⟺ logged" is an enforced invariant
  (every frozen request reconstructable from the append-only log; a runtime invariant
  checks it), and every prompt/tool-schema change lands as a durable `request/header`
  event with reason `initial|resume|change` — prompt drift and cache invalidation are
  *auditable from the session log alone*. For anyone studying harnesses, this is the
  most instrumentable loop in the tracked set.

## Permission model — a sandbox, not a prompt *(deep-dive 2026-08-24)*

**dsh has no per-tool permission system.** The `tools/pre-execute` waterfall's terminal
default is `allow` (`core/tools/src/index.ts:1477`); the only `ask`/`deny` producers in
the whole repo are the (unmounted) Claude Code/Codex hook bridges. In a stock run,
`bash`, `write`, `web_fetch`, and `subagent` dispatch **unprompted**. The gate is a
**compiled OS sandbox invoked per tool call**: modes `read-only` /
`workspace-write` (default) / `danger-full-access`, enforced by argv-wrapping at spawn
(bwrap → Landlock on Linux, Seatbelt on macOS, a hand-built restricted-token runner on
Windows that self-reports `partial` and says exactly why) plus an in-process path fence
for the fs tools derived from the same allow-list. Fail-closed: no usable backend →
refuse to run unconfined (`sandbox/src/index.ts:131-144`). **File effects are the whole
policy vocabulary — network is never confined**, stated in the README's limitations.

- **The escalation is inverted relative to every tracked harness**: the *model* raises
  the prompt. On a sandbox denial, `bash`/`write`/`edit` expose `sandbox_permissions` +
  `justification` for a one-shot same-turn retry, and the tool description instructs
  the model that detouring through chat is wrong — "the approval prompt raised by that
  retry is how the user consents" (`tool-bash/src/index.ts:82-92`). Fail-closed chain:
  strict-widening check against per-call truth before anyone is prompted; missing
  approver/agent/answerer, rogue returns, and throws all resolve to denial
  (`sandbox/src/escalation.ts:157-189`).
- **`allowed-once` is the only grant in the vocabulary** — no allow-always, no
  persistent grant ledger anywhere; every ask/decision pair is a durable
  `approval/asked`/`approval/decided` event. No other tracked harness ships without
  remembered approvals.
- **Boundary test (can the model influence the gate?): mechanically no, in the default
  composition.** No risk field, no auto-approve heuristic, no model-callable path to
  the mode/policy setters, no permission field on delegation (a written design note
  says so). The Warp-style `is_risky:false` analogue does not exist. *Rhetorically
  yes*: the model-authored `justification` reaches the human verbatim inside the
  approval reason. *Architecturally yes, through two shipped, labelled doors*: Code
  Mode runs model TypeScript in a worker thread with full Node globals — "containment,
  not a security boundary", strictly more privileged than the Landlock-confined `bash`
  beside it — and the shipped `cordis` preset lets the model define and mount
  host-plane plugins whose host half activates **with no approval request**
  (`cordis-host-runner/src/index.ts:266-272`; the preset's own header: "Treat a session
  on this preset as shell access").
- **The gate survives process boundaries asymmetrically, by design.** The *sandbox*
  survives completely (Landlock rulesets + `no_new_privs` inherit across `execve`;
  bwrap namespaces; the token binds the tree) — the Warp child-harness crack does not
  reproduce here. The *approval* gate tightens at the in-process agent boundary:
  delegated children inherit only the parent's explicit sandbox override and are
  **pinned to `approval: 'never'`** — a decision reversing an earlier shipped design
  after observing invisible blocked children, recorded as a dated in-repo design note
  (`.agents/tools/implemented/feature/2026-08-10-subagent-approval-pinned-never.md`) —
  the publish-your-own-negative-results epistemics this repo credits. At *foreign*
  harness boundaries the parent fixes the child's native permission mode as deployment
  config (codex default `never`, claude-code default `dontAsk`), with no model-visible
  field to change it. Escapes: MCP server processes spawn outside `ctx.sandbox`; the
  two model-code doors above.
- Small novel invariant: a live persistent PTY **freezes the sandbox mode** — a
  mid-session re-scope under an open shell throws (`terminal-bash/src/index.ts:47-52`).

## Environment relationship & surfaces

**Primary verb: `internalize`** — confinement is a hard dependency of the shipped
composition, mounted by default in both profiles, invoked per tool call at the argv
boundary (Codex-shaped, plus the in-process fs fence Codex lacks). **With a mild
`bundle` streak**: the Landlock launcher is *published as its own npm product family*
(`@deepseek-ai/node-addon-landlock-run` + per-platform binaries) with a CLI contract
document and release pipeline — nobody else in the set ships their sandbox as a
separately versioned product. **`bind` available, not default**: the `e2b` POC packages
swap `ctx.fs`/`ctx.subprocess` for E2B adapters (local confinement off — the VM is the
boundary); four out-of-process subagent backends attach foreign harnesses. **`inhabit`
absent** (no container self-detection anywhere; greps empty).

Surfaces: **web only** (locally served; browser is a pure client over 52 POST methods
+ two downlink-only WebSockets; model keys never reach the browser) and headless/SDK
embedding (TypeScript and Python SDKs spawn a *local* child process). **No TUI.**
Execution is 100% `local`: `--host 0.0.0.0` is a hard usage error — *"it would expose
remote code execution to the network"* (`web-app/src/startup.ts:74-76`) — and the local
server has **no inbound authentication**, saying so twice in source (a DNS-rebinding
fence "explicitly not authentication"; privileged methods loopback-pinned with a
documented gap for `session.create`).

Credentials: BYO `DEEPSEEK_API_KEY` (env > `~/.dsh/.credentials.yaml` chmod-600-refused
otherwise > `.env`); no keychain, no vendor account login mounted. **An anonymous
random UUID rides every DeepSeek model request** as `x-deepseek-harness-user-id`
(`llm-deepseek/src/adapter.ts:519-530`) — genuinely random, never machine-derived, but
**independent of the telemetry switch** (OTel is mounted-but-disabled by default,
separately killable).

## Run probe — 2026-08-24

Probe target: the published npm artifact `@deepseek-ai/dsh@0.1.1-rc.2` — the version
string exactly matches the pinned tag, so probing the release probes the pin. Node
v22.23.2 (engines: `^22.19.0 || >=24`); success read from the served page, not exit
status (5e).

**Result: boots and serves.** `node_modules/.bin/dsh web --no-open` printed
`dsh web: http://127.0.0.1:3080` within 45 s of launch; `curl` returned HTTP 200 with
14,556 bytes of the web client's HTML (`<!doctype html>…__ModuleLoader__` bootstrap).
Loopback binding confirmed as read (`ss`: `127.0.0.1:3080`, not `0.0.0.0`).

**The install itself was the probe's finding.** The documented `npx` launch path
**OOM'd on this 8 GB host**: `npm exec` died in V8
(`FatalProcessOutOfMemory` during dependency resolution, ~2.4 GB VSZ at death) before
dsh ever ran, and a raised-heap plain `npm install` then needed **>10 minutes** to
finish (completed on a resumed run; `NODE_OPTIONS=--max-old-space-size=5120`). Final
footprint: 296 MB across 187 top-level `node_modules` entries — the entry package is
120 KB; the closure is where the cost lives. So the one-line install pitch
(`npx @deepseek-ai/dsh web`) carries an undocumented resource floor that a default
npm heap on a mid-size VPS does not clear. Dated 2026-08-24; worth re-probing at the
next drift check — a preview-stage packaging behavior, likely to change.

## Bleed

- **category 1↔2 consolidation**: DeepSeek joins Anthropic/OpenAI/Google/xAI in
  shipping a first-party harness; defaults are DeepSeek-wired everywhere
  (`agent-default-model` → `deepseek-v4-flash`, web search via DeepSeek API) while the
  seam stays genuinely provider-agnostic (three wire protocols, honest exclusions for
  auth shapes the config can't express).
- **Absorption, sideways and inward** (conclusion 8's territory): dsh *consumes
  competitors' extension surfaces* — unmodified Claude Code `hooks.json` and Codex hook
  configs run against dsh's typed events — and *delegates to competitor harnesses* as
  subagent providers (Codex, Claude Agent SDK). Warp orchestrates rivals as backends;
  dsh does both directions cheaper, as bridges.
- **Memory (category 5)**: verified **no native learning loop and no store** — the
  vendor's stance is third-party MCP memory examples, default-off ("no memory server is
  present in the shipped composition"). The memos-on-dsh adapter the memos deep-dive
  verified rides the plugin/pre-step surface. A vendor-native harness *declining* the
  memory absorption is a data point against treating conclusion 8's memory leg as
  universal gravity.
- **category 3**: the internalize + published-launcher combination above.

## Surprises

1. "Everything is a plugin" survives adversarial reading — with the singleton-factory
   and policy-kernel qualifications recorded above.
2. Turn-end gating where **data decides, not listener order** — a third engine-grade
   shape after hermes' policy and codex's stop-hooks.
3. A harness with **no per-tool permission model at all** — the gate is the sandbox;
   the honest comparator is Codex, not Claude Code. And the escalation prompt is
   *model-initiated by instruction*.
4. KV-cache discipline as a **CI-gated documentation requirement** across 30+ packages.
5. It runs **competitors' hook configs** and spawns **competitors as subagents**.
6. No iteration budget anywhere, deliberately — with a real depth-cap bypass via
   `workflow`/`ralph` (`host.ts:352`).
7. `first_commit` 2026-06-10 vs published 2026-08-13: two months of private history
   released at once; the "five-day" phenomenon is adoption, not development.
8. The anonymous-UUID request header outside the telemetry opt-out.
9. A dated, in-repo **negative result about their own design** (subagent approvals
   pinned `never` after invisible-blocked-children), plus frozen "Agent Notes" as
   decision records — a vendor running the same epistemics this repo does.

## Open questions

- Does the plugin-first bet survive contact with an ecosystem? (Cordis plugin authoring
  is the contested surface; the `dsh plugin add` path and the dormant hook bridges are
  where third-party supply would land. Re-check at the next drift check.)
- The convergence prediction from the roster registration stands: multi-surface
  expansion (TUI/IDE) from the current single web surface — `execution: local` +
  no-inbound-auth make a hosted/async-remote shape a large step. Falsifiable by ~2027-01.
- Does Code Mode actually get used by the default model tier (ADR-0012's open ptc
  question), given it ships behind a preset?
