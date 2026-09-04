---
name: qwen-code
category: 2
surfaces: [terminal, ide, desktop, web, messaging]  # cli (terminal) · vscode-ide-companion + zed-extension + --acp (ide) · desktop-shell, 84 files · web-shell, 619 files + webui, 220 files · messaging = 11 channel packages (feishu, dingtalk, telegram, qqbot, wecom, weixin, github, gitlab, dws), each driving a spawned `--acp` child
execution: local  # the work runs on your machine; the resident half is `residency:` below, which ADR-0047 split out of this axis precisely because this report is `local` AND resident while hermes-agent is `both` AND resident
residency: resident  # `qwen serve` HTTP daemon (Stage 1 experimental), a per-session CronScheduler (acp-integration/session/Session.ts:3333), and 11 messaging channels delivering inbound with no session open — the SECOND verified instance, from an independent lineage, which is what fired the taxonomy's own trigger
environments: [host, container, worktree]  # container = docker | podman | sandbox-exec (config.ts:910); worktree is real but scoped to the `review` command (cli/src/commands/review/lib/worktree.ts), not a general execution mode
environment_relation: internalize  # configures and drives its own sandbox, same verb as the parent
maker: Alibaba (Qwen)
url: https://github.com/QwenLM/qwen-code
license: Apache-2.0
access: open-source
stack: [TypeScript, Node, Rust]  # Rust is not incidental: packages/cua-driver is a 663-file Rust workspace (crates for macOS/Windows/Linux + browser). ts(4008) tsx(793) rs(384) java(218) per repo-facts.sh
version: cua-driver-rs-v0.20.1-16-gfc0e827658   # MECHANICAL and misleading on its own: `git describe` lands on a Rust sub-tag. The PRODUCT version at this pin is 0.22.2 (package.json), confirmed by the run probe below printing 0.22.2 — the tag list carries v0.22.2, desktop-v0.2.2 and cua-driver-rs-v0.20.1 in parallel, one per shipped artifact
commit: fc0e827658
first_commit: 2025-04-15   # IDENTICAL to gemini-cli's (2025-04-16 is codex's; gemini-cli is also 2025-04-15) — this is the imported fork history, not qwen-code's own start. The product forked gemini-cli v0.8.2 and stopped syncing at Qwen Code v0.1
stars: 27405
stars_at: 2026-08-27
read_at: 2026-08-27
depth: deep-dive   # 2026-08-27, all THREE ADR-0021 components traced at the pin: the loop, context assembly, and the permission gate. Read as a DIVERGENCE STUDY against gemini-cli at its own pin (64b5b79a6, read 2026-08-25). NOT traced, and named so the gap is legible: the 663-file Rust cua-driver workspace, the individual channel implementations beyond their shared base contract, and the daemon side-channel coordination protocol
harness_features:
  mcp: true              # client: stdio + SSE + StreamableHTTP (tools/mcp-client.ts:9-17), plus a `qwen mcp` management subcommand verified at runtime
  lsp: true              # INVERSION vs the parent's verified false: packages/core/src/lsp/ ships NativeLspClient + LspServerManager + LspConnectionFactory + LspResponseNormalizer, instantiated on the real config path (cli/src/config/config.ts:2482). Servers are user-configured (LspConfigLoader), not bundled
  hooks: true            # 16 lifecycle events (hooks/types.ts:24-52) incl. PostToolBatch, UserPromptExpansion, MessageDisplay, SubagentStart/Stop, PreCompact/PostCompact — a superset of the parent's 11, with a `qwen hooks` subcommand
  turn_end_gates: hook   # Stop + StopFailure carrying `stop_hook_active` (hooks/hookEventHandler.ts:250-258, 647-687) — the same Claude Code Stop-hook retry contract the parent implements as AfterAgent
  tool_approval: policy  # four ApprovalModes (PLAN | DEFAULT | AUTO_EDIT | AUTO, config.ts:388-404). AUTO is a three-stage filter (permissions/autoMode.ts): workspace-scoped edit fast-path, read-only allowlist, then an LLM classifier — all three firing only when no user rule matched, and an explicit user `ask` rule beats every fast-path
  skills: true           # skills/ with skill-manager, skill-activation, skill-curator and a `bundled` set; `.qwen/skills/` present in-tree
  subagents: true        # subagents/ with subagent-manager, builtin-agents, agent-frontmatter-schema, validation; SubagentStart/Stop hook events exist for them
  ptc: false             # checked and absent, same negative as the parent: `grep "codeExecution *:"` over packages/ → 0 product hits. NEAR MISS recorded rather than smoothed: packages/node-repl ships a session-persistent Node REPL as a STANDALONE MCP server ("fully independent of core — any MCP client … can run it"), which is code execution reached through the ordinary tool loop, not model-emitted code driving the harness's tools
  plan_mode: mode        # ApprovalMode.PLAN as a first-class mode (client.ts:1964), with dedicated plan-mode-entry-policy.ts and plan-mode-shell-policy.ts, and plan-mode state threaded into compaction (chatCompressionService.ts:1057)
  rules_files: ["QWEN.md", "AGENTS.md"]  # INVERSION vs the parent: both load by DEFAULT (utils/memory-constants.ts:7-33, "defaults to include both"), where gemini-cli loads GEMINI.md/MEMORY.md and does NOT load AGENTS.md by default. The fork adopted the cross-tool convention its parent declined
  model_agnostic: true   # INVERSION vs the parent's verified false: 13 provider presets (providers/presets/) — deepseek, grok, minimax, moonshot, modelscope, openrouter, requesty, zai, idealab, three alibaba plans, and custom-provider — plus model-discovery and install paths
  session_sharing: false # checked and absent in the same shape as the parent: no share links anywhere (grep shareLink|shareUrl|publicUrl|/api/share over packages/ → 0 non-test hits); a local export path and `qwen sessions` resume exist — artifact yes, link no
  evals: false           # checked and absent under the registry's definition. NEAR MISS, recorded because it is the closest thing: memory/recall-eval.test.ts is a real measurement harness — a labeled corpus, Recall@5, a frozen reference scorer kept for regression comparison — but it scores the DETERMINISTIC selector and says so; the model selector is exercised by mocked cases. No agent/task-success eval harness: `git ls-files "*.eval.ts"` → 0, against the parent's 37 plus four eval CLIs
  learning_loop: true    # INVERSION vs the parent's verified false, and the sharpest one: background extraction AND a "dream" consolidation agent, both DEFAULT-ON (config.ts:1333-1335, "Defaults to true"), writing through atomicWriteFile into the same store recall.ts reads and rebuilding its index. The parent's equivalent is default-OFF and propose-and-commit into an .inbox nothing applies
---

# Qwen Code

Deep-dive 2026-08-27, at the pin, **all three ADR-0021 components traced** — the loop,
context assembly, and the permission gate. Read as the **divergence study** the candidates
ledger specified: qwen-code against [gemini-cli](gemini-cli.md) at its own pin
(`64b5b79a6`, read 2026-08-25), the question being what a year of independent evolution did
to a shared architecture.

## What it is

Alibaba's terminal coding agent, forked from Gemini CLI v0.8.2 and independent since Qwen
Code v0.1. The fork history is visible in the mechanical facts: `first_commit: 2025-04-15`
is *gemini-cli's* first commit, imported wholesale. The Apache-2.0 licence, the
`@google/genai` types still imported across `packages/core`, and the `Copyright 2025 Google
LLC` headers on files as recent as the auto-memory subsystem all mark the lineage.

What it is *now* is not a CLI. It is a 19-package platform — terminal, VS Code and Zed
extensions, a desktop shell, a web shell, a Chrome extension, three ACP SDKs (TypeScript,
Python, **Java** — `com.alibaba.acp.sdk`), a 663-file **Rust** computer-use driver with
per-platform crates, and eleven messaging-channel integrations.

## The distinguishing bet

**That the harness is a service, not a session.** Everything specific to qwen-code follows
from that: the messaging channels, the `qwen serve` daemon, the cron scheduler, the
background memory agents that run whether or not you are watching. Gemini CLI bets on a
strong local turn; qwen-code bets on an agent that is *reachable* — from Feishu, from
DingTalk, from a cron entry, from a mobile MCP bridge — and keeps working between the times
you talk to it.

## Stack & repo shape

8,953 commits, 7,249 tracked files at the pin. `ts(4008) tsx(793) md(779) rs(384)
java(218) js(172)`.

The `version:` field deserves its frontmatter comment: `git describe` resolves to
`cua-driver-rs-v0.20.1-16-gfc0e827658`, a **Rust sub-tag**, because the repo tags each
shipped artifact on its own line — `v0.22.2`, `desktop-v0.2.2`, `cua-driver-rs-v0.20.1` all
live in the same tag namespace. The product version at this pin is **0.22.2**
(`package.json`), which the run probe independently confirms. A count carries its measure:
the mechanical field is correct and would still mislead anyone reading it as the product
version.

## Architecture — the traced loop *(component 1)*

`packages/core/src/core/client.ts` is 4,692 lines and holds the turn engine, the parent's
shape preserved: `sendMessageStream` (client.ts:2615) drives iterations against
`MAX_TURNS = 100` (client.ts:175), clamped again at the call site (client.ts:3308-3312), with
a `LoopDetectionService` (services/loopDetectionService.ts:177) reset per iteration.

What the fork **added** to the loop is a goal machine. `packages/core/src/goals/` carries
`activeGoalStore`, `goal-checkpoint`, `goal-checkpoint-verifier`, `goal-continuation-prompt`
and `goal-evidence` — a long-running task that survives turns, carries checkpoints, and has
its own verifier running side queries against claimed evidence. `goal.turnCount`
(client.ts:283) is counted separately from the turn budget. This is the machinery a
service-shaped agent needs and a session-shaped one does not.

Subagents are present (`subagents/subagent-manager.ts`, `builtin-agents.ts`, a frontmatter
schema and validation) and are visible to the hook system through dedicated
`SubagentStart`/`SubagentStop` events — the parent has subagents but no subagent lifecycle
hooks.

Turn-end enforcement grades **hook**, not engine: `Stop` and `StopFailure` events carry
`stop_hook_active` (hooks/hookEventHandler.ts:250-258, 647-687), the same retry contract
Claude Code shipped and gemini-cli implements as `AfterAgent`. Both forks landed on the same
borrowed vocabulary independently.

## Context assembly *(component 2)*

Two inversions here, both on defaults rather than mechanisms.

**Rules files.** `DEFAULT_CONTEXT_FILENAME = 'QWEN.md'` and `AGENT_CONTEXT_FILENAME =
'AGENTS.md'`, and the loader "defaults to include both" (utils/memory-constants.ts:7-33),
QWEN.md first for backward compatibility with `/init`. The parent, read two days earlier,
carries the opposite verified finding: AGENTS.md is *not* loaded by default, present only as
a docs example and a test fixture. The fork adopted the cross-tool convention its parent
declined — the clearest single instance of divergence-by-default in this read.

**Autonomous memory.** `packages/core/src/memory/` ships an extraction agent and a **dream**
consolidation agent (`dream.ts`, `dreamAgentPlanner.ts`, `extract.ts`,
`extractionAgentPlanner.ts`), with per-agent turn and time budgets exposed in the settings
schema (settingsSchema.ts:2138-2180). Both are **default-on**: *"Enable managed auto-memory
background extraction and dream. Defaults to true"* (config.ts:1333-1335). They write via
`atomicWriteFile` into the store `recall.ts` reads and rebuild its index — an auto-apply
path, not a proposal queue.

That single default is what separates `learning_loop: true` here from the parent's verified
`false`. Gemini CLI's background extractor exists but is off, and even when on it writes
patches into an `.inbox` nothing applies. Same lineage, same idea, opposite posture on the
most contested key in the category.

Compaction is `services/chatCompressionService.ts` with `postCompactAttachments.ts` and
`PreCompact`/`PostCompact` hook events — plan-mode state is threaded through compaction
explicitly (chatCompressionService.ts:1057, 1088), so a compaction cannot silently drop the
fact that the agent is planning rather than acting.

## Permission model — a deny-only classifier *(component 3)*

Four approval modes (`PLAN | DEFAULT | AUTO_EDIT | AUTO`, config.ts:388-404) over a rule
engine (`permissions/permission-manager.ts`, `rule-parser.ts`, `dangerousRules.ts`,
`destructive-commands.ts`, `shell-semantics.ts`).

The interesting part is AUTO. `permissions/autoMode.ts` documents a three-stage filter (its own comments number the
stages 1-3):
workspace-scoped `Edit`/`Write` fast-path, a read-only tool allowlist, then an **LLM
classifier** — and all three fire *only* when the rule engine returned `default` (no rule
matched). An explicit user `ask` rule skips every fast-path: "user intent takes precedence."

The classifier itself (`permissions/classifier.ts`) is where this read pays off, because it
is the **exact inverse of the taxonomy's anchor for this component**. Warp's `AgentDecided`
crack is a model-authored `is_risky: false` that self-authorizes. Qwen-code's classifier
returns `shouldBlock: boolean` — it has **no vocabulary for allowing anything**. It can only
veto. And it fails closed: `unavailable` (API error, timeout, schema failure, context
overflow) carries the comment *"The caller MUST treat this as a block."* Two stages, fast
then thinking, at 10s and 30s timeouts.

Two further details make it a stronger gate than a bolt-on classifier usually is:

- `dangerousRules.ts` defines **classifier-bypass criteria** — a set of actions that never
  reach the model stage at all.
- `permission-manager.ts:1512` removes *"any allow rules whose breadth would defeat the AUTO
  classifier"* — the engine defends the classifier against the **user's own** over-broad
  allowlist. Nothing else tracked in this category protects its gate from the operator.

So the model does influence the gate, which by the taxonomy's boundary test keeps this
firmly component 3 — but it influences it in one direction only. Recorded as the
counter-instance to Warp: model-in-the-gate is not inherently a crack; the crack is
letting the model's word *widen* the permission.

## The divergence study — scoring the ledger's prediction

The candidates row carried a dated, falsifiable prediction (2026-08-25):

> The divergence is likely large and asymmetric: the policy engine, hooks system, skills,
> and subagents all postdate the v0.8.2-era fork point, so the study would mostly measure
> what qwen-code *didn't* inherit.

**Scored: half right, and wrong on its operative claim.** Large — yes. Asymmetric — yes. But
the asymmetry runs the *other way*. Qwen-code has a permission engine, a hooks system (16
events to the parent's 11), skills and subagents. It did not fail to inherit them; it built
or absorbed equivalents independently, and in two cases went further. The study did not
mostly measure absence — it mostly measured **addition**:

| | gemini-cli @ `64b5b79a6` | qwen-code @ `fc0e827658` |
|---|---|---|
| `lsp` | `false` (verified absent) | **`true`** — native LSP client, wired |
| `model_agnostic` | `false` (all routes end at Google) | **`true`** — 13 provider presets |
| `learning_loop` | `false` (default-off, propose-only) | **`true`** — default-on, auto-apply |
| `rules_files` | GEMINI.md, MEMORY.md (no AGENTS.md) | **QWEN.md + AGENTS.md**, both default |
| `evals` | `true` (37 `.eval.ts`, 4 eval CLIs) | `false` (0; one recall measurement harness) |
| messaging channels | none | 11 packages, shipped subcommand |
| computer use | none | 663-file Rust driver, 3 platforms |

Five of fourteen feature cells differ, four of them **inversions of a verified value** —
which is only meaningful because the parent was deep-read two days earlier and its `false`s
are checked-absent rather than unchecked. The one inversion running the parent's way is
`evals`, and it is not close: 37 behavioural evals with LLM-as-judge against zero.

The prediction's error is instructive and worth keeping: it reasoned from *fork-point
chronology* (features postdating v0.8.2 can't have been inherited) and concluded the fork
would be a subset. Chronology bounded what could be inherited; it said nothing about what
would be built. **A divergence forecast needs a second term — the fork's own direction —
and this one had only the parent's timeline.**

## Environment relationship & surfaces — the resident strain, second instance

Sandboxing is `docker | podman | sandbox-exec` (config.ts:910), configured and driven by the
harness: **internalize**, the parent's verb.

The surfaces axis strains, and the execution axis strains harder. `packages/channels/`
ships eleven channel packages — `dingtalk`, `feishu`, `telegram`, `qqbot`, `wecom`,
`weixin`, `github`, `gitlab`, `dws`, plus `base` and `plugin-example` — over a shared
contract (`ChannelBase`, `ChannelAgentBridge`, `ChannelLoopScheduler`, `ChannelLoopStore`,
`ChannelLoopTools`). They reach the agent by **spawning the CLI with `--acp`**
(`base/src/AcpBridge.ts:122-128`) and route permission prompts back out to the platform
(`acp-permission-${randomUUID()}`, AcpBridge.ts:475). Alongside them: a `CronScheduler`
started per session (`acp-integration/session/Session.ts:3333`), and `qwen serve`, "a local
HTTP daemon (Stage 1 experimental)".

The taxonomy recorded this exact shape at the hermes-agent deep-dive (2026-07-30) and wrote
its own trigger:

> a **resident** agent: a persistent daemon that outlives any conversation, receives
> messages from ~20 platforms, and runs cron jobs unattended … Not promoted to a third value
> on one instance — recorded here so the second instance triggers the revision. Same read
> strained **surfaces**: messaging platforms don't fit the four-value vocabulary.

**This is that second instance**, independently arrived at by a different vendor in a
different lineage: persistent daemon, messaging platforms, unattended cron. Both strains
fire. **Resolved the same day (ADR-0047)**, in the two halves the taxonomy had already
separated: `messaging` becomes a fifth `surfaces` value — the list composes, so nothing has
to be dropped — and a new `residency: session | resident` field carries the persistence that
`execution` was never asking about. This report's `execution: local` and hermes-agent's
`execution: both` are both true and both keep their value; a third execution value would
have forced one of them to give up a fact, which is why it was rejected.

## Run probe — 2026-08-27

Cheap probe against the **published** artifact rather than a monorepo build:
`npm install @qwen-code/qwen-code` (16 packages, 7s) → `qwen --version` → **0.22.2**, matching
`package.json` at the pin. `qwen --help` lists the shipped subcommands: `channel`,
`extensions`, `hooks`, `mcp`, `review`, `serve`, `sessions`, `update`.

The probe earns its place by confirming at runtime what source suggested: `qwen channel` is
a **user-facing shipped command**, not in-tree scaffolding, and `qwen serve` announces its
own experimental status in its help text.

It also produced a small rule-8 discrepancy worth recording: the help string reads *"Manage
messaging channels (Telegram, **Discord**, etc.)"* and no Discord channel exists. Bounded
search: `git grep -il discord` → 12 files, all help text, a design doc, settings-schema
comments, test fixtures and one unrelated Rust doc; `packages/channels/` has eleven
directories and none is Discord. Advertised in the interface, absent from the tree.

## Bleed

- **category 3.** Sandbox configuration is internalized as in the parent, but worktrees are
  scoped to one command (`review`), not offered as a general execution mode — a narrower
  category-3 posture than gemini-cli's experimental general worktree setting.
- **category 5.** The auto-memory subsystem (extraction, dream, recall, index, team-index,
  channel-memory) is a memory *product* inside a harness, default-on. It is the strongest
  demand-side instance of `learning_loop` tracked, and the first where the write path is on
  by default.
- **category 6.** Ships an MCP **server** of its own (`packages/node-repl`, explicitly
  vendor-neutral: "any MCP client — Qwen Code, Claude, Codex"), plus `mobile-mcp` and a
  Chrome extension. A harness distributing extensions other harnesses can consume.
- **ACP.** Fourth tracked speaker after gemini-cli, hermes-agent and dsh — and the first to
  ship ACP **SDKs** in three languages, including Java, which is a bid to make the protocol
  an integration surface rather than an internal detail.

## Cost model

Open weights are not the point here; the harness is Apache-2.0 and free, and routes to
whichever provider you configure (13 presets, or a custom one). The cost that matters is the
one the defaults choose for you: **background memory agents are on by default** and run
against a configurable lightweight model (config.ts:1360). A default-on background write
path is a default-on token bill, and the settings schema's per-agent turn (5–8) and time
(2–5 min) budgets exist because of it.

## Surprises

1. **A fork out-featured its parent on the parent's own axes.** Four verified `false`s
   became `true`. The received framing of a vendor fork — downstream, behind, catching up —
   is simply wrong here, and the only way to know that was to read both at pins two days
   apart.
2. **A gate that protects itself from the operator.** `permission-manager.ts:1512` strips
   user allow-rules broad enough to defeat the classifier. Every other permission system
   tracked here treats the user's allowlist as the final word.
3. **Deny-only model authority.** The classifier is the clean counter-example to Warp's
   crack, and it makes the anchor sharper: the failure was never "the model touched the
   permission decision" but "the model's word could widen it."
4. **Java.** A TypeScript coding agent shipping a Java ACP SDK (`com.alibaba.acp.sdk`) is a
   statement about who the integrator is expected to be — enterprise JVM shops, not CLI
   users.
5. **The tag namespace lies to `git describe`.** Three product lines tagged in one
   namespace means the mechanical `version:` field resolves to a Rust driver's tag. Caught
   only because the run probe printed a different number.

## Open questions

- **Is `resident` one shape or two?** The vocabulary landed (ADR-0047), but both instances
  bundle three things — a daemon, scheduled work, and inbound messages — and nothing yet
  shows whether they separate. A harness with cron and no messaging, or messaging and no
  daemon, would say whether `residency` is one axis or a collapsed pair.
- **What is the cua-driver's actual capability?** 663 Rust files across macOS, Windows,
  Linux and browser crates, untraced in this read. Computer use inside a coding harness is
  either a serious second product or an unshipped bet, and the file count alone cannot tell
  which.
- **Does the dream agent improve recall, or just spend tokens?** The repo ships a
  measurement harness for the *deterministic* selector and none for the agents that write
  the corpus. The one place it evaluates itself is the one place the model is not involved.
- **Is `AGENTS.md`-by-default a divergence or a preview?** If gemini-cli adopts it later,
  this read dated the fork leading its parent on a cross-tool convention — worth re-checking
  at the parent's next drift review.
