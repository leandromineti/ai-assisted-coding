---
name: hermes-agent
layer: 2
surfaces: [terminal, desktop, web, ide]   # + ~20 messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal…) via the gateway — beyond the fixed vocabulary, see What it is
execution: both        # local CLI/TUI + persistent gateway daemon on a VPS, cron jobs, remote terminal backends
environments: [host, container, remote-sandbox]   # tools/environments/: local, docker, ssh, singularity, modal (+managed), daytona, vercel_sandbox
environment_relation: bind   # attaches to independently-distributed environments: 8 terminal backends (local, docker, ssh, singularity, modal x2, daytona, vercel_sandbox)
vendor: Nous Research
url: https://github.com/NousResearch/hermes-agent
license: MIT
open_source: true
stack: [Python, TypeScript]
version: v2026.7.20-3084-g524ab5399
commit: 524ab5399
first_commit: 2025-07-22
stars: 222863
stars_at: 2026-07-30
read_at: 2026-07-30   # drift-checked 2026-08-12 at 0957277f2 without re-reading (rule 4b) — one claim overtaken since the pin, three corroborated; pin deliberately not moved
depth: deep-dive
features:
  mcp: true              # tools/mcp_tool.py + optional-mcps/ + committed exposure-strategy bench (mcp-research-data/)
  lsp: true              # agent/lsp/ (client, manager, servers, workspace)
  hooks: true            # plugin lifecycle hooks (pre_llm_call, pre_verify), shell hooks
  skills: true           # 70 bundled + 111 optional SKILL.md dirs; agentskills.io-compatible
  subagents: true        # delegate_task (tools/delegate_tool.py), single + parallel batch
  plan_mode: true        # bundled /plan *skill* (plans under .hermes/plans/), not a core loop mode
  rules_files: [SOUL.md, HERMES.md, AGENTS.md, CLAUDE.md, .cursorrules]   # reads competitors' files too — prompt_builder.py
  model_agnostic: true   # 33 provider plugins (plugins/model-providers/)
  session_sharing: true  # `hermes trace upload` → Hugging Face agent-trace dataset (private by default); no hosted live-session links
  evals: true            # mini_swe_runner.py, batch_runner.py, committed bench data (mcp-research-data/)
  learning_loop: true    # ON by default: interval-gated review fork (turn_finalizer.py:653) + idle curator + /learn
---

# hermes-agent

Nous Research's open-source personal agent: one Python agent core driven from a CLI/TUI,
an Electron desktop app, a web dashboard, editors over ACP, and — through a single
gateway daemon — Telegram, Discord, Slack, WhatsApp, Signal and ~20 other messaging
platforms. It persists memory and skills across sessions, spawns subagents, runs cron
jobs unattended, and executes commands through eight terminal-backend implementations
(local, Docker, SSH, Singularity, Modal ×2, Daytona, Vercel Sandbox). Third-largest tool
in this study by stars (see frontmatter; passed opencode during 2026 —
[issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1)).

The layer question the issue flagged is settled: **layer 2 confirmed**. spec-kit installs
*into* it (`~/.hermes/skills` in spec-kit's own integration tests — verified in
`upstream/spec-kit/tests/test_extension_skills.py`), and the repo's `AGENTS.md`
self-describes as a platform extended "through plugins and skills, not by growing the
core". But it is the least coding-centric harness on the shelf — see Surprises.

## Drift check — 2026-08-12 (not a re-read; the pin is unchanged)

1248 commits / 1456 files since the read — the largest drift in the set. **49 of those
commits touch a file this report cites**, which is the set that was checked. Nothing
below is wrong *at the pin*; one claim has been overtaken since, and the reason it was
overtaken is the most interesting thing in the drift.

**1. The skills index moved from the `stable` band to `volatile` — because this
harness's flagship feature was defeating its flagship design law.** Verified at both
ends rather than taken from the commit message: at `524ab5399`,
`stable_parts.append(skills_prompt)` (`agent/system_prompt.py:329`); at HEAD the module
docstring lists volatile as "skills index, memory snapshot, USER.md profile, external
memory". The move landed 2026-08-03, four days after the read (authored 2026-06-02 on a
long-lived branch — author dates are not landing dates, and `git log <pin>..HEAD` is the
only reliable membership test). Upstream's stated reason:

> The skills index is runtime-mutable: the agent adds and patches skills mid-session, so
> it is not byte-stable. Keeping it in the stable band breaks that band's prefix-cache
> contract, because every skill edit changes the stable band and invalidates the entire
> cached prefix in front of it.

Read that against the two things this report praises in separate sections. The
distinguishing bet is that **the agent writes its own skills**; the context-assembly
section opens with **"per-conversation prompt caching is sacred"** as a design law. They
were in direct conflict: every autonomous skill write blew away the cached prefix in
front of the stable band. Neither this read nor upstream had noticed at pin time. The
lesson is not that the design was bad — it is that **a self-modifying agent and a
byte-stable prompt prefix are structurally in tension**, and the tension surfaces
exactly where the agent's write path crosses its own cache tiers. Any harness pairing an
autonomous learning loop with prompt-cache discipline inherits this problem.

**2. The learning loop is intact and being actively hardened — conclusion 8 corroborated,
not just unfalsified.** The gate structure at `turn_finalizer.py` is unchanged in
substance (now ~`:700–718`): still interval counters, still `final_response and not
interrupted`, still `except Exception: pass` best-effort — i.e. the rule-4a-corrected
description holds at HEAD, which is worth recording because that claim was wrong once
already. Two additions since: `/refine` (2026-08-05) fires the same fork **on demand**
with optional focus instructions, explicitly keeping automatic reviews byte-identical so
the prompt cache is untouched; and a fix on 2026-07-31 — the day after the read —
**rejects unresolved failures as skills**, a quality gate on what the loop is allowed to
write. The trajectory is toward more autonomous authorship, with guardrails on output
quality.

**3. Also corroborated:** `agent/verification_stop.py` survives at HEAD and is still
policy-only ("It never runs checks itself"), which is the leg conclusion 8 cites for
turn-end verification gates; `background_review.py`, `curator.py` and
`iteration_budget.py` all still exist.

**4. Refined, not contradicted — the permission model.** Approval timeouts are now
classified separately from explicit denials on the CLI/TUI/ACP surfaces (2026-08-02),
bringing them to parity with the gateway's existing position: *"timed out without user
response… Silence is not consent."* Still fail-closed either way. The report's
permission claims stand; the vocabulary underneath them got sharper.

**What a re-read should cost:** more than ECC's, less than 1248 commits suggests. The
compression subsystem took heavy churn (feasibility skips, durable prune runways,
tail-budget fixes) and is the one area where this report's context-assembly claims are
now describing a much-changed component.

## The distinguishing bet

**That an agent should accumulate capability across sessions — autonomously.**

Every harness here has memory files and skill folders. Hermes' wager is that *writing
them is the agent's job, not the user's*. The machinery is concrete, not marketing:

1. **Interval-gated background review** (`agent/background_review.py`; call site
   `agent/turn_finalizer.py:653`) — after a successful, non-interrupted turn, if the
   memory/skill nudge intervals have elapsed, the agent forks itself in a daemon thread,
   replays the conversation snapshot ("already warm in the prompt cache, so cheap cache
   reads"), and asks "should any skill/memory be saved or updated?". Writes go straight
   to the stores; the fork runs under a tool whitelist limited to memory + skill
   management, and the spawn is best-effort (exceptions swallowed). *Not* per-turn —
   the module docstring's "after every turn, may call" resolves at the call site to
   nudge-counter gating.
2. **Idle-time curator** (`agent/curator.py`) — an inactivity-triggered auxiliary-model
   task that reviews *agent-created* skills: pin / archive / consolidate / patch. Strict
   invariants in the module docstring: only touches agent-created skills, **never
   auto-deletes** (archive is recoverable), pinned skills bypass everything.
3. **`/learn`** (`agent/learn_prompt.py`) — user-triggered skill authoring from anything
   describable (a directory, a URL, "what I just did"), enforced against "HARDLINE"
   authoring standards embedded in the prompt.
4. **Recall** — FTS5 full-text search over its own session history (`session_search`
   tool) plus optional [Honcho](https://github.com/plastic-labs/honcho) dialectic user
   modeling as an external memory provider.

Claude Code's memory is user-curated files; opencode ships skills but no autonomous
writer. Hermes makes the write path itself agentic and then adds a *maintenance* agent
on top of it. Whether the loop compounds value or accumulates cruft is exactly what the
curator exists to manage — and nothing in the repo measures which one wins (see Open
questions).

The second, quieter bet: **the agent is a persistent companion process, not a per-repo
session.** The gateway daemon outlives any conversation; cron delivers to any platform;
coding is a *posture* the agent shifts into when it finds itself in a git repo
(`agent/coding_context.py`), not the product's identity.

## Main features

| Feature | Distinctive? |
|---|---|
| Autonomous learning loop (review fork + curator + /learn) | **Unique in this set** |
| One agent core across CLI/TUI/desktop/web/ACP + ~20 messaging platforms | **Unique at this breadth** |
| 8 terminal-backend implementations incl. serverless (Modal, Daytona) | Distinctive — deepest layer-3 bleed in the set |
| Programmatic tool calling (`execute_code`: model-written Python calls tools via RPC) | Distinctive |
| 33 provider plugins, model-agnostic | Table stakes at this point; breadth notable |
| MCP client, LSP, subagents, skills | Table stakes by mid-2026 |
| Built-in cron with natural-language jobs | Distinctive |
| Trajectory export for training (`hermes trace upload`, batch_runner) | Distinctive — the research-lab tell |

## Stack & repo shape

Python 3.11+ (uv), with TypeScript for the desktop app (Electron), web dashboard, and a
Tauri bootstrap installer. 8,071 tracked files: 3,660 `.py`, 1,477 `.md`, 1,297 `.ts`,
597 `.tsx`. 19,628 commits in ~12.5 months — dominated by Nous' Teknium (~7,350 commits
across two identities), so it's maintainer-led, not drive-by-scaled.

The shape is the opposite of opencode's 33-package monorepo: a **flat Python core with
megafiles**. `cli.py` is 17,976 lines; `hermes_cli/main.py` 11,031; `run_agent.py`
7,410; `agent/conversation_loop.py` 7,040. The `agent/` package is one directory of
~180 modules. Capability lives at the edges as data: 70 bundled + 111 optional skills
(`SKILL.md` dirs), 33 model-provider plugins, plugin platforms for the gateway.

## Architecture

### Entry point → one full trace

```
hermes                      pyproject [project.scripts] → hermes_cli.main:main
  └ cmd_chat                hermes_cli/main.py:2495
      └ cli.main            cli.py (17,976-line interactive REPL)
          └ AIAgent         run_agent.py:409 (constructed once, cached across turns)
              └ run_conversation   agent/conversation_loop.py:1084
                  └ build_turn_context   agent/turn_context.py (per-turn prologue)
                  └ [loop]  API call → tool dispatch → guardrails → repeat
                  └ turn_finalizer / background_review fork
```

The gateway (`gateway/`), TUI (`tui_gateway/`, `ui-tui/`), desktop app, ACP adapter
(`acp_adapter/` — `hermes acp` for editors), cron, and batch runner all funnel into the
same `run_conversation`.

### The agent loop

`conversation_loop.py:1258`:

```python
while (api_call_count < agent.max_iterations and agent.iteration_budget.remaining > 0) or agent._budget_grace_call:
```

Iteration-budgeted, not token-budgeted: **500 iterations for the parent, 50 per
subagent** (`agent/iteration_budget.py`), thread-safe consume/refund. The refund is the
interesting part: `execute_code` turns are *refunded* — the model writing a Python
script that chains ten tool calls over RPC costs zero budget, while ten individual tool
turns cost ten. The budget structurally rewards the collapsed form.

Stuck-loop handling lives in `agent/tool_guardrails.py`: a side-effect-free controller
tracks per-turn call signatures (hashed canonical args), classifies tools as idempotent
vs mutating, and escalates repeated identical calls through warning guidance → synthetic
tool results → controlled turn halts. Compare opencode's doom-loop-as-permission-prompt:
hermes resolves it in-band with the model rather than escalating to the human.

Termination adds two coding-specific gates: `agent/verification_stop.py` ("policy-only —
never runs checks itself") nudges the model back up to 3 times when it tries to finish
right after editing code without fresh verification evidence, with an explicit
suppression list for non-code extensions so a README edit "must never demand a /tmp
verification script"; and a `pre_verify` plugin hook lets user policy inject one more
turn. This is exp-01's "measured verification gate" mechanism living *inside a layer-2
harness* — evidence-ledger-driven, though the evidence bar is "ran something", not a
hidden verifier.

### Context assembly

The governing rule is stated in `AGENTS.md` as a design law: **"Per-conversation prompt
caching is sacred."** Everything else follows from it.

`build_system_prompt_parts` (`agent/system_prompt.py:152`) assembles **three explicit
cache tiers**:

- **stable** — identity (SOUL.md or hardcoded fallback), task-completion and
  parallel-tool-call guidance, per-tool behavioral blocks (only for tools actually
  loaded), the skills index, environment hints, the coding operating brief;
- **context** — the workspace snapshot (git state, built **once** and never re-probed —
  the brief tells the model to re-check with `git` because the snapshot is allowed to go
  stale rather than shatter the cache), context files, caller system message;
- **volatile** — memory snapshot (`MEMORY.md`), user profile (`USER.md`), external
  memory provider block, and a **date-only** timestamp — minute precision was removed
  because it "invalidates prefix-cache KV on every rebuild path" (credited to a
  community PR in the comment).

The prompt is cached on the agent instance and never re-rendered mid-session; even
`/coding` mode flips are deferred to the next session. Context files: it loads its own
`HERMES.md` **and** `AGENTS.md`, `CLAUDE.md`, and `.cursorrules` — a harness that reads
its competitors' rules files as first-class input.

Compression (`agent/context_compressor.py`, 5,696 lines) is the stated single exception
to cache sanctity: an auxiliary cheap model summarizes middle turns behind a pluggable
`ContextEngine` ABC (`context.engine` in config — the compressor is just the default
implementation, with a documented lifecycle for third-party engines).

### Tool surface & permissions

**89 `registry.register()` calls across 38 tool modules; 61 tools in the shared core
set** (`_HERMES_CORE_TOOLS`, `toolsets.py`); **78 registrations carry a `check_fn`**
availability gate (TTL-cached) that removes tools from the schema when their service
isn't present (no `HASS_TOKEN` → no Home Assistant tools; no `HERMES_DESKTOP` → no GUI
pane tools). 58 named toolsets compose them. Schemas live in the central registry
(`tools/registry.py`), declared at module level by each tool file.

Permissions are **dangerous-command approval at dispatch time** (`tools/approval.py`):
pattern detection, per-session approval state, a *smart-approval* path where an
auxiliary LLM auto-approves low-risk commands, and a permanent allowlist in config. Two
details worth recording:

- `HERMES_YOLO_MODE` is **frozen at module import** — the comment is explicit that
  reading the env var per-call "would allow any skill running inside the process to set
  this variable and instantly bypass all approval checks — a prompt-injection escalation
  path". Prompt-injection is modeled as a threat *from the agent's own extensions*.
- Hard write-denials (`agent/file_safety.py`) protect `~/.ssh/*`, the active profile's
  `.env`, and Hermes' own state regardless of approval outcome.

So on the template's question: the permission check is **after the model decides**
(dispatch-time), but the tool *schema* is filtered before the model ever sees it
(check_fn) — availability-filtered, not permission-filtered, the inverse emphasis of
opencode's `visibleTools`.

### Layer boundaries in the code

- **Layer 1 (models):** provider profiles are plugins (`plugins/model-providers/<name>/`,
  33 bundled) read by one registry (`providers/`); adapters in `agent/` normalize
  Anthropic, Gemini-native, Bedrock, Vertex, Codex-responses APIs. Model-agnostic, but
  *not* prompt-agnostic — see the per-family appendices in Surprises.
- **Layer 5 (extensions):** first-class and the designated growth path — MCP client +
  OAuth manager, plugin system with lifecycle hooks, the skills standard
  (agentskills.io-compatible), LSP (`agent/lsp/`).
- **Layer 4 (methodology):** absorbed in pieces: `/plan` as a bundled skill, todo tool,
  verification-stop gates, kanban multi-agent coordination tools — process opinions
  shipped inside the harness, same absorption noted for opencode.
- **Layer 3 (execution):** the deepest bleed in the set. `tools/environments/base.py`
  is a real abstraction with 8 implementations, including serverless-persistent ones
  (Daytona/Modal hibernate between sessions). `execute_code` even has a file-based RPC
  transport so programmatic tool calling works *inside* remote backends.

## Bleed

Layers 3, 4, and 5 as above — plus a bleed no other tool in the study has: **layer 1
training data**. `batch_runner.py`, `trajectory_compressor.py`, and
`hermes trace upload` (exports sessions in Claude Code JSONL shape to Hugging Face,
private by default, secret-redacted) exist "for training the next generation of
tool-calling models". The harness is also a data-collection instrument for its
maker's models — stated openly in the README ("Research-ready").

## Cost model

MIT, free; you pay inference. Provider-agnostic (33 plugins) with Nous' own Portal
subscription as the promoted default — the system prompt includes a subscription-status
block for Nous users. The "runs on a $5 VPS / hibernates on serverless" pitch makes the
*hosting* cost shape part of the product, not just the token bill: a persistent
companion has an idle-time cost problem that a per-invocation CLI doesn't, and two of
the eight backends exist specifically to solve it.

## Surprises

1. **It's not a coding harness that grew a chat mode — it's a personal assistant that
   grew a coding posture.** Coding is a runtime *mode* (`agent/coding_context.py`)
   activated when an interactive surface sits in a git repo, injecting an operating
   brief and workspace snapshot, prompt-only by default. The 221k-star "rival" sitting
   next to opencode in the index competes with it for maybe a third of its surface.
2. **The learning loop is real machinery with real invariants** — interval-gated
   background review fork, idle curator that never deletes (only archives), tool
   whitelists on the fork. Expected marketing; found engineering. What's *absent* is any
   measurement that the loop improves outcomes.
3. **A fourth position in the per-model-prompt split** (index.md three-way). Hermes
   keeps ONE shared prompt but appends small per-family appendices: ~4.4KB total —
   tool-use enforcement for a listed model set (`gpt, codex, gemini, gemma, grok, glm,
   qwen, deepseek`), a 2,694-char OpenAI/Grok execution-discipline block, an 860-char
   Google block (`agent/prompt_builder.py:309–470`). Between opencode's nine full
   prompts (~1,256 lines) and cline's one: the shared-base-plus-patches position. And
   the model list is a tell — the appendices target every major family *except*
   Anthropic's, i.e. the patches paper over deviations from the behavior Claude exhibits
   by default.
4. **Prompt-cache discipline is the constitution.** "Sacred" is `AGENTS.md`'s own word;
   the date-only timestamp, the never-re-probed workspace snapshot, deferred mode
   flips, and the review fork riding the warm cache are all the same principle applied
   four times. This is the most cache-conscious design in the study — consistent with
   a self-hosting lab that pays its own inference bill.
5. **The iteration budget refunds programmatic tool calling.** `execute_code` turns
   give their iteration back — a structural incentive for the model to collapse tool
   chains into scripts whose intermediate results never enter context.
6. **YOLO mode is frozen at import time** to close a prompt-injection escalation path
   from the agent's own skills. Security reasoning about the extension surface itself,
   not just about user commands.
7. **They benchmark their own design decisions and commit the data.**
   `mcp-research-data/` holds bench rows comparing three MCP exposure strategies
   (eager / bridge / listing) across schema sizes — e.g. `full|eager`: 810k input
   tokens, $4.05 vs `full|bridge`: 161k, $0.80. Empirical grounding as an internal
   practice, exp-01's load-bearing mechanism, done by a vendor on its own harness.
8. **Repo-root artifacts of heavy dogfooding**: a Portuguese-language debugging report
   (`relatorio-issue-69678-sqlite-fd-leaks.md`), a screenshot (`sqlite_leak_fix.png`),
   and a competitive-response essay (`hermes-already-has-routines.md` — "Anthropic just
   announced Claude Code Routines… We shipped it two months ago") all committed at the
   top level. The repo is visibly a working surface for agents, not just a product.

## Open questions

- **Does the learning loop pay?** No eval in the repo measures skill/memory accumulation
  against a baseline. A natural experiment for this repo's rig: same task battery, fresh
  Hermes vs one seeded with N sessions of use. (Large: park unless the layer-2 arc
  continues.)
- The issue asked what 221k stars in ~12 months represents vs ECC's 235k in 6. The
  authorship distribution (maintainer-dominated, ~7.3k commits from one person) says
  Hermes is a *product* with a community, not a prompt-pack phenomenon; a real answer
  needs traffic/fork/issue-shape comparison at ECC read time.
- Does the `execute_code` refund actually shift model behavior toward programmatic tool
  calling, or do models ignore the affordance? Their own trajectory data could answer
  it; nothing committed does.
- `conversation_loop.py` at 7k lines with ~15 concern-specific companions
  (`turn_context`, `turn_finalizer`, `turn_retry_state`…) looks like a monolith being
  strangler-figged module by module. Worth a `git log` pass to see if the extraction is
  agent-driven refactoring.
- The `contributors/emails` directory and the automated "triage sweeper" in `AGENTS.md`
  (allowed to close PRs as `implemented_on_main` / `cannot_reproduce` / `incoherent`,
  explicitly barred from taste-based closes) — how much of the 19.6k-commit velocity is
  agent-operated maintenance? The governance design for it is unusually explicit.
