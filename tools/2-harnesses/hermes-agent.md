---
# PIN MOVED 524ab5399 → 29112bef0 (= tag v2026.8.31) at the 2026-09-04 release re-read
# (rule 4b: a pin moves only with a re-read; this was one — three-tract release variant,
# every claim confronted at both pins). The 2026-08-12 drift check and the 2026-08-27
# reasoning-parameter read below were performed at the old pin and stay dated as such.
name: hermes-agent
category: 2
surfaces: [terminal, desktop, web, ide, messaging]   # messaging = ~20 platforms via the gateway (Telegram, Discord, Slack, WhatsApp, Signal…), see What it is. `messaging` entered the vocabulary 2026-08-27 (ADR-0047) on qwen-code's second instance; this report is the first, and until then recorded the platforms as being OUTSIDE the four-value set. Re-verified at v2026.8.31: 22 platform-plugin dirs + built-ins (Signal is a built-in, not a plugin); the A2A protocol platform added in the window is a machine-peer channel, not a human surface — deliberately NOT a surfaces value
execution: both        # local CLI/TUI + remote terminal backends. The daemon/cron half of this comment moved to `residency:` below (ADR-0047) — it was never an execution fact
residency: resident    # the gateway daemon outlives any conversation, cron delivers to any platform, serverless backends hibernate between sessions — the FIRST verified instance of the shape (deep-dive 2026-07-30). Strengthened at v2026.8.31: /loop, /heartbeat, /bg re-entry commands and bot-to-bot relay are all resident-only affordances, with /pause as their gateway-wide kill switch
environments: [host, container, remote-sandbox]   # tools/environments/: local, docker, ssh, singularity, modal (+managed), daytona, vercel_sandbox
environment_relation: bind   # attaches to independently-distributed environments: 8 terminal backends counted as concrete BaseEnvironment subclasses incl. managed_modal (the README says "seven", counting modal once) — recounted at v2026.8.31, unchanged
maker: Nous Research
url: https://github.com/NousResearch/hermes-agent
license: MIT
access: open-source
stack: [Python, TypeScript]
version: v2026.8.31
commit: 29112bef0
first_commit: 2025-07-22
stars: 241330
stars_at: 2026-09-04
read_at: 2026-09-04   # v2026.8.31 release re-read (window 7,055 commits); deep-dive 2026-07-30 @ 524ab5399, drift-checked 2026-08-12, reasoning-param targeted read 2026-08-27
depth: deep-dive
harness_features:
  mcp: true              # tools/mcp_tool.py + optional-mcps/ + committed exposure-strategy bench (mcp-research-data/)
  lsp: true              # agent/lsp/ (client, manager, servers, workspace)
  hooks: true            # plugin lifecycle hooks (pre_llm_call, pre_verify), shell hooks
  turn_end_gates: engine # ADR-0012 graded: agent/verification_stop.py — in-loop policy, ≤2 re-prompts (max_attempts=2) when the model finishes without fresh verification evidence (body §termination). CORRECTED 2026-09-04: the deep-dive wrote "≤3", wrong at its own pin — max_attempts: int = 2 at 524ab5399:210 and v2026.8.31:238 alike
  tool_approval: policy  # tools/approval.py — approval at tool dispatch; re-verified at v2026.8.31 (file grew 44% in the window; YOLO import-freeze, smart approval, timeout≠denial all intact)
  skills: true           # 58 bundled + 137 optional SKILL.md dirs at v2026.8.31 (was 70+111 — bundled SHRANK while optional grew: surface moving out of the default install); agentskills.io-compatible
  subagents: true        # delegate_task (tools/delegate_tool.py), single + parallel batch
  ptc: true              # execute_code: model-written Python calls tools via RPC; iteration budget refunds these turns (ADR-0012; refund re-verified at v2026.8.31, conversation_loop.py:7716-7720)
  plan_mode: true        # /plan is a BUILT-IN command since the window (was a bundled skill; promoted because platform command menus trim skills alphabetically at their caps and `plan` sorted past the cutoff — agent/plan_prompt.py docstring). Still prompt-only, plans under .hermes/plans/, not a core loop mode
  rules_files: [SOUL.md, HERMES.md, AGENTS.md, CLAUDE.md, .cursorrules]   # reads competitors' files too — loaders in prompt_builder.py; v2026.8.31 adds AGENTS.override.md and .cursor/rules/*.mdc
  model_agnostic: true   # 39 provider plugins (ls plugins/model-providers/ minus README; was 33)
  session_sharing: true  # `hermes sessions export --format trace --upload` → Hugging Face agent-trace dataset (private by default, forced secret redaction); no hosted live-session links. CORRECTED 2026-09-04: the deep-dive wrote "hermes trace upload", a command that existed at neither pin — the mechanism was real, the identifier invented
  evals: true            # mini_swe_runner.py, batch_runner.py, mcp-research-data/ — plus, new at v2026.8.31, evals/ with four committed A/B harnesses (compaction, browser tools, read_file design, schema diet); still none measuring the learning loop
  learning_loop: true    # ON by default (config_defaults.py:1353): interval-gated review fork (turn_finalizer.py:806-819; nudge intervals 10) + idle curator + /learn + /refine. New in window: cron sessions suppressed, whitelist widened to read_file/search_files after the fork was found starving in production (see re-read), 600K-token/16-iteration fork budgets, JSONL skill ledger with rollback
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

The category question the issue flagged is settled: **category 2 confirmed**. spec-kit installs
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
   `agent/turn_finalizer.py:806-819` at v2026.8.31, was :653) — after a successful,
   non-interrupted turn, if the memory/skill nudge intervals (default 10) have elapsed,
   the agent forks itself in a daemon thread, replays the conversation snapshot
   ("already warm in the prompt cache, so cheap cache reads"), and asks "should any
   skill/memory be saved or updated?". Writes go straight to the stores; the fork runs
   under a tool whitelist, and the spawn is best-effort (exceptions swallowed). *Not*
   per-turn — nudge-counter gating at the call site. **Re-read findings (2026-09-04)**:
   cron sessions now skip the fork entirely (~30K tokens/event, no human in the loop);
   the whitelist was **widened to include `read_file`/`search_files`** after production
   telemetry showed the loop *starving* — ~142 denials + ~204 read-before-write refusals
   over two days on one deployment meant "almost no patch landed"
   (`background_review.py:1549-1565`; write tools stay denied, and the widening is
   dispatch-side only so the advertised schema stays cache-stable); forks now carry a
   600K-token aggregate input budget and a 16-iteration cap; and a JSONL **skill ledger**
   (`tools/skill_ledger.py`, content-addressed before/after blobs,
   `hermes curator rollback`) makes even user hard-deletes recoverable — closing the one
   hole in the curator's never-delete invariant.
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
| 8 terminal-backend implementations incl. serverless (Modal, Daytona) | Distinctive — deepest category-3 bleed in the set |
| Programmatic tool calling (`execute_code`: model-written Python calls tools via RPC) | Distinctive |
| 33 provider plugins, model-agnostic | Table stakes at this point; breadth notable |
| MCP client, LSP, subagents, skills | Table stakes by mid-2026 |
| Built-in cron with natural-language jobs | Distinctive |
| Trajectory export for training (`hermes trace upload`, batch_runner) | Distinctive — the research-lab tell |

## Stack & repo shape

Python 3.11+ (uv), with TypeScript for the desktop app (Electron), web dashboard, and a
Tauri bootstrap installer. 10,925 tracked files at v2026.8.31 (`git ls-tree -r`; was
8,071): 4,881 `.py`, 1,951 `.ts`, 1,583 `.md`, 800 `.tsx` — plus 725 `.com` files that
are not code at all: `contributors/emails/` names each mapping file after a commit
email, a merge-conflict-avoidance structure invented for thousand-PR flow (one file per
mapping so concurrent salvage PRs never collide; CI-enforced). 26,683 commits in ~13.5
months, maintainer-led, not drive-by-scaled — Teknium is 7,421 of 19,628 at the old pin
and 9,339 of 26,683 at this one (`git shortlog -sn`, summing his two identities; the
deep-dive's "~7,350" carried no measure — corrected 2026-09-04). But a commit count for
this repo is **not a comparable unit of work**: see the re-read section's velocity
finding.

The shape is the opposite of opencode's 33-package monorepo: a **flat Python core with
megafiles**, and at this pin the finding is *more* true than at the last one —
`cli.py` 17,976 → 22,268 lines; `hermes_cli/main.py` 12,420 → 14,834 *(correction
2026-09-04: the deep-dive wrote 11,031, wrong at its own pin — the citation into the
file was read at the pin, the line count was not)*; `run_agent.py` 7,410 → 9,413;
`agent/conversation_loop.py` 7,040 → 8,830; `gateway/run.py` 25,766 → 33,539. The
`agent/` package is 155 top-level / 210 recursive `.py` modules (the deep-dive's "~180"
lands only on the recursive count, which includes `agent/lsp/` etc.). Capability lives
at the edges as data: 58 bundled + 137 optional skills (`SKILL.md` dirs — bundled
*shrank* from 70 while optional grew from 111), 39 model-provider plugins, 22 gateway
platform plugins.

## Architecture

### Entry point → one full trace

```
hermes                      pyproject [project.scripts] → hermes_cli.main:main
  └ cmd_chat                hermes_cli/main.py:3163
      └ cli.main            cli.py (22,268-line interactive REPL)
          └ AIAgent         run_agent.py:422 (constructed once, cached across turns)
              └ run_conversation   agent/conversation_loop.py:1899
                  └ build_turn_context   agent/turn_context.py (per-turn prologue)
                  └ [loop]  API call → tool dispatch → guardrails → repeat
                  └ turn_finalizer / background_review fork
```

(Line numbers repointed at the v2026.8.31 re-read; every hop re-verified.)

The gateway (`gateway/`), TUI (`tui_gateway/`, `ui-tui/`), desktop app, ACP adapter
(`acp_adapter/` — `hermes acp` for editors), cron, and batch runner all funnel into the
same `run_conversation`.

### The agent loop

`conversation_loop.py:2094` (byte-identical since the deep-dive, only the line moved):

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
never runs checks itself") nudges the model back up to **2** times when it tries to finish
right after editing code without fresh verification evidence *(correction 2026-09-04:
the deep-dive wrote "3"; `max_attempts: int = 2` at both pins — 524ab5399:210,
v2026.8.31:238)*, with an explicit suppression list for non-code extensions so a README
edit "must never demand a /tmp verification script"; and a `pre_verify` plugin hook lets
user policy inject one more turn. This is exp-01's "measured verification gate"
mechanism living *inside a category-2 harness* — evidence-ledger-driven, though the
evidence bar is "ran something", not a hidden verifier. New in the window and easy to
misread: `agent/verify/` (869 lines, ported from `superagent-ai/grok-cli` with source
URLs cited in its `__init__.py`) is a verifier that *does* run checks — build/test/
readiness recipes — but it is reachable only as the `hermes verify` CLI subcommand: not
registered as a model tool, not in any toolset. A human-invoked runner beside a
policy-only in-loop gate; the `engine` grade above describes the in-loop gate only.

### Context assembly

The governing rule is stated in `AGENTS.md` as a design law: **"Per-conversation prompt
caching is sacred."** Everything else follows from it.

`build_system_prompt_parts` (`agent/system_prompt.py:435` at v2026.8.31, was :152)
assembles **three explicit cache tiers**:

- **stable** — identity (SOUL.md or hardcoded fallback), task-completion and
  parallel-tool-call guidance, per-tool behavioral blocks (only for tools actually
  loaded), environment hints (plus, since the window, a one-line environment probe —
  `tools/env_probe.py`, default on, silent when the environment is clean), the coding
  operating brief;
- **context** — the workspace snapshot (git state, built **once** and never re-probed —
  the brief tells the model to re-check with `git` because the snapshot is allowed to go
  stale rather than shatter the cache), context files, caller system message;
- **volatile** — now led by the **skills index** (moved out of stable 2026-08-03, per
  the drift check; confirmed at this pin at `system_prompt.py:926`, with a limitation
  the drift check didn't have: the comment concedes the move has *"no effect for
  single-block `cache_control` backends"* — i.e. on Anthropic-style explicit-breakpoint
  caching, the self-modifying-agent-vs-stable-prefix tension is documented, not fixed),
  the memory snapshot (`MEMORY.md`), user profile (`USER.md`), external memory provider
  block, and a **day-granular** timestamp — minute precision was removed because it
  "invalidates prefix-cache KV on every rebuild path" (still credited to PR #20451).
  The timestamp has since grown three principled exceptions: a DST-stable zone/offset
  suffix, a rebuild-day correction line emitted only at compaction boundaries (where
  the prefix is already invalid), and a timeless mode for eternal bot-chat sessions.

The prompt is cached on the agent instance and never re-rendered mid-session; even
`/coding` mode flips are deferred to the next session. Context files: it loads its own
`HERMES.md` **and** `AGENTS.md`, `CLAUDE.md`, and `.cursorrules` — a harness that reads
its competitors' rules files as first-class input (v2026.8.31 adds
`AGENTS.override.md` and `.cursor/rules/*.mdc`).

Compression (`agent/context_compressor.py`, 8,842 lines — up 55% from 5,696 across 93
window commits, the re-read's most-changed core component as the drift check predicted)
is the stated single exception to cache sanctity: an auxiliary cheap model summarizes
middle turns behind a pluggable `ContextEngine` ABC (now its own module,
`agent/context_engine.py`, selected via `context.engine` in config). Window changes,
each with its default stated: **lean tail retention is the new default** (compaction
keeps a clamped 10–25K verbatim tail instead of 100–240K — the landing commit says so
in those words); **native provider-side compaction** (`agent/native_compaction.py`)
exists but is gated to the gpt-5.6 family on direct OpenAI/Codex routes only, because
older families fail server-side with an un-downgradeable 500/stall; **micro-compaction**
ships default-off; in-place compaction replaced session rotation as the default.
Presence ≠ operative on the pluggability: `plugins/context_engine/` contains only
`__init__.py` — the compressor is not merely the default engine, it is the only
implementation in-tree.

### Tool surface & permissions

**93 `registry.register()` calls across 45 tool modules; 53 tools in the shared core
set** (`_HERMES_CORE_TOOLS`, `toolsets.py` — AST-counted; the deep-dive's 89/38/61 were
exact at the old pin, same measures); **73 registrations carry a `check_fn`**
availability gate (TTL-cached) that removes tools from the schema when their service
isn't present (no `HASS_TOKEN` → no Home Assistant tools; no `HERMES_DESKTOP` → no GUI
pane tools). 59 named toolsets compose them. Schemas live in the central registry
(`tools/registry.py`), declared at module level by each tool file. Note the direction:
registrations grew while the core set *shrank* 61 → 53 — like the bundled-skills
pruning, default surface is being moved outward.

Permissions are **dangerous-command approval at dispatch time** (`tools/approval.py`):
pattern detection, per-session approval state, a *smart-approval* path where an
auxiliary LLM auto-approves low-risk commands, and a permanent allowlist in config. Two
details worth recording:

- `HERMES_YOLO_MODE` is **frozen at module import** — the comment is explicit that
  reading the env var per-call "would allow any skill running inside the process to set
  this variable and instantly bypass all approval checks — a prompt-injection escalation
  path". Prompt-injection is modeled as a threat *from the agent's own extensions*.
  (Verbatim at v2026.8.31, `approval.py:34-37`. The window added a second, session-scoped
  bypass axis — a gateway `/yolo` toggle — collapsed with the frozen env var and
  `approvals.mode: off` into one `is_approval_bypass_active_for_session()` predicate,
  and an operator-authored policy-text hook on the smart-approval guardian's prompt.)
- Hard write-denials (`agent/file_safety.py`) protect `~/.ssh` key material, the active
  profile's `.env` (family since expanded: `.env.local/.production/.envrc`…), and
  Hermes' own state regardless of approval outcome. One deliberate narrowing in the
  window: `~/.ssh/config` moved *out* of the unconditional deny set to approval-gated —
  editing host aliases is routine — the permission model's only loosening, argued rather
  than drifted.

So on the template's question: the permission check is **after the model decides**
(dispatch-time), but the tool *schema* is filtered before the model ever sees it
(check_fn) — availability-filtered, not permission-filtered, the inverse emphasis of
opencode's `visibleTools`.

### Category boundaries in the code

- **category 1 (models):** provider profiles are plugins (`plugins/model-providers/<name>/`,
  33 bundled) read by one registry (`providers/`); adapters in `agent/` normalize
  Anthropic, Gemini-native, Bedrock, Vertex, Codex-responses APIs. Model-agnostic, but
  *not* prompt-agnostic — see the per-family appendices in Surprises.
- **category 6 (extensions):** first-class and the designated growth path — MCP client +
  OAuth manager, plugin system with lifecycle hooks, the skills standard
  (agentskills.io-compatible), LSP (`agent/lsp/`).
- **category 4 (methodology):** absorbed in pieces: `/plan` as a bundled skill, todo tool,
  verification-stop gates, kanban multi-agent coordination tools — process opinions
  shipped inside the harness, same absorption noted for opencode.
- **category 3 (execution):** the deepest bleed in the set. `tools/environments/base.py`
  is a real abstraction with 8 implementations, including serverless-persistent ones
  (Daytona/Modal hibernate between sessions). `execute_code` even has a file-based RPC
  transport so programmatic tool calling works *inside* remote backends.

## Bleed

Categories 3, 4, and 5 as above — plus a bleed no other tool in the study has: **category 1
training data**. `batch_runner.py`, `trajectory_compressor.py`, and
`hermes trace upload` (exports sessions in Claude Code JSONL shape to Hugging Face,
private by default, secret-redacted) exist "for training the next generation of
tool-calling models". The harness is also a data-collection instrument for its
maker's models — stated openly in the README ("Research-ready").

## Cost model

MIT, free; you pay inference. Provider-agnostic (39 plugins) with Nous' own Portal
subscription as the promoted default — the system prompt includes a subscription-status
block for Nous users. The "runs on a $5 VPS / hibernates on serverless" pitch makes the
*hosting* cost shape part of the product, not just the token bill: a persistent
companion has an idle-time cost problem that a per-invocation CLI doesn't, and two of
the eight backends exist specifically to solve it. Re-checked 2026-09-04: the README —
Portal section included — is **byte-identical across the entire 7,055-commit window**,
and no new monetization surface appears in docs (rule 1b: searched README, docs/**,
AGENTS.md; source not audited for outbound calls). Distribution note: PyPI's
`hermes-agent` stopped updating at 0.19.0 (uploaded 2026-07-20 — before even the old
pin) while six git-tagged releases shipped; the promoted install is now
`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`. There is no
published artifact that matches any recent pin — the rule-8b artifact probe is
structurally unavailable here, recorded as such.

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
3. **A fourth position in the per-model-prompt split** (README.md three-way). Hermes
   keeps ONE shared prompt but appends small per-family appendices: ~4.4KB total at the
   old pin (824 + 2,694 + 860 chars, `len()` on the constants; 5,569 at v2026.8.31) —
   tool-use enforcement for a listed model set (`gpt, codex, gemini, gemma, grok, glm,
   qwen, deepseek` — byte-identical tuple at both pins, now `prompt_builder.py:419`),
   an OpenAI/Grok execution-discipline block (2,694 → 3,885 chars), an 860-char Google
   block. Between opencode's nine full prompts (~1,256 lines) and cline's one: the
   shared-base-plus-patches position. And the model list is a tell — the appendices
   target every major family *except* Anthropic's, i.e. the patches paper over
   deviations from the behavior Claude exhibits by default. *(2026-09-04: what was this
   report's inference is now upstream's own comment — `prompt_builder.py:432-433`:
   "Claude is excluded because it does not exhibit these failure modes." The gated set
   grew — kimi, minimax, mimo, mistral — still no Claude.)*
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
8. **Repo-root artifacts of heavy dogfooding** *(true at the deep-dive pin; expired in
   the window)*: a Portuguese-language debugging report
   (`relatorio-issue-69678-sqlite-fd-leaks.md`), a screenshot (`sqlite_leak_fix.png`),
   and a competitive-response essay (`hermes-already-has-routines.md` — "Anthropic just
   announced Claude Code Routines… We shipped it two months ago") all committed at the
   top level. The repo is visibly a working surface for agents, not just a product.
   *(2026-09-04: all three were removed by named `chore:` commits between 2026-08-02 and
   2026-08-21; the top level at v2026.8.31 carries product docs only, plus a new
   `SOUL.md` — the shipped persona prompt. The working-surface era is historical; the
   repo grew a tidying reflex.)*

## Reasoning-parameter handling — targeted read 2026-08-27 (not a re-read; the pin is unchanged)

The gap [conclusion 15](../../docs/conclusions.md) named. Executed for
[issue #41](https://github.com/leandromineti/ai-assisted-coding/issues/41), which was
opened because the [#40](https://github.com/leandromineti/ai-assisted-coding/issues/40)
sweep could not read this harness. **Hermes is the fifth harness read on this axis and the
first that does not fail it** — not by accident, and not everywhere.

### Method note, because the issue got the diagnosis wrong

`upstream/hermes-agent` is a **`--filter=blob:none` blobless clone with a promisor remote**
(`git config remote.origin.partialclonefilter` → `blob:none`). That, not repo size, is why
`git grep <pin>` stalled: a whole-tree grep at a non-checked-out commit must fetch every
blob in the tree from GitHub, one round trip at a time. The issue's recommended fix — a
worktree at the pin — is the *same* operation and is worse: it ran for over four minutes,
produced nothing, and earned an HTTP 429 from GitHub. The working method is the one the
issue listed second, plus a refinement:

- **`git grep <pin> -- <narrow-pathspec>`** — `-- 'agent'` returned in **0.045 s** where the
  whole-tree form timed out at 55 s+. Scope the pathspec; do not build a worktree.
- **`git show <pin>:<path>`** for anything the grep did not already have locally, one blob
  per call.

Recorded here rather than only in the issue because it applies to every large clone in
`upstream/` and the wrong diagnosis cost two attempts.

### The three questions

**1. Where is the parameter decided?** At four nested points, and only the innermost is
model-aware. User config is the source of truth — `resolve_reasoning_config(cfg, model)`
(`hermes_constants.py:972`) is a single documented chokepoint shared by *every* surface
(CLI startup, gateway, TUI, cron, `/model` switch, fallback activation), resolving
per-model overrides above a global `agent.reasoning_effort`. Below it sits a **route-keyed
capability gate**, `_supports_reasoning_extra_body()` (`run_agent.py:6436`), which picks a
strategy by how much the endpoint is willing to tell it: trusted routes answer yes
unconditionally (Nous Portal, Vercel AI Gateway); **servers that publish capabilities get
probed live and cached** (LM Studio's `allowed_options`, Ollama's `/api/show` `thinking`
capability, GitHub Models' per-model effort list); OpenRouter falls back to a prefix
allowlist; everything else defaults to *omit the field*. Below that, per-provider transports
decide only the **wire shape** — top-level `reasoning_effort` (Kimi, TokenHub, LM Studio),
`extra_body.reasoning` (the OpenAI-compatible default), `extra_body.thinking` (Kimi),
`thinking_config` (Gemini), `reasoning: {effort, summary}` (Responses). And only at the
bottom does anything match a model id.

**2. Does it version-pin? Deliberately, in whichever direction the vendor's API fails —
and the Anthropic case is a documented inversion of the exact mistake the other four
made.** `agent/anthropic_adapter.py:77-106` carries the reasoning verbatim:

> Newer Claude releases (4.8, and named models like claude-fable-5) follow the same modern
> contract — but they share no common version substring, so **an allowlist of version
> numbers ("4.6", "4.7", …) goes stale the moment a model ships without a recognized number**
> and silently routes it down the legacy manual-thinking path. Instead we DEFAULT unknown
> Claude models to the modern contract and keep an explicit *legacy* list … so each new
> Claude release works without a code change.

That is a **denylist of superseded families with a default-to-newest fallthrough**, applied
independently at three call sites — `_supports_adaptive_thinking` (`:245`),
`_supports_xhigh_effort` (`:265`), `_forbids_sampling_params` (`:282`) — plus
`_get_anthropic_max_output`, which the comment cites as the pattern's origin. Checked
against the lineup that defeated the other four: `claude-opus-5`, `claude-sonnet-5`,
`claude-fable-5` and `claude-opus-4-8` all match no legacy substring, so all four route to
adaptive thinking with `xhigh` available and sampling params omitted — correct on every one.
`claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5` match and take the manual
budget path — also correct. The 4.6 pair sits in its own list (`_NO_XHIGH_CLAUDE_SUBSTRINGS`)
and gets `xhigh` downgraded to `max`, its strongest accepted level. **This is the same
comparison continue fails outright and cline fails by omission, on the same models, at a
pin one day older than cline's.**

The polarity flips where the vendor's failure flips. On xAI, `grok_supports_reasoning_effort`
(`agent/model_metadata.py:479`) is an **allowlist** of four prefixes, and the docstring says
why: *"Conservative by design: if a future Grok model isn't listed, we send no effort dial
rather than 400."* The call site names the exact failure it is avoiding — *"xAI rejects
`reasoning.effort` on grok-4 / grok-4-fast / grok-3 / grok-code-fast / grok-4.20-0309-* with
HTTP 400 even though those models reason natively"* (`agent/transports/codex.py:347-354`).
One entry carries a dated live probe in its comment (`grok-4.5`, *"verified live against
/v1/responses 2026-07-08 — accepts effort low/medium/high (default: high when omitted) but
REJECTS 'none'"*), cross-checked against models.dev. So: denylist where the vendor 400s on
the *old* shape, allowlist where the vendor 400s on the *new* dial. The choice is made per
vendor, from the observed failure, and written down.

**3. What happens on the fallthrough?** Three different answers, each matched to its route,
and none of them is an error. Where the field is safe, a **hardcoded `medium`** is sent
(`transports/chat_completions.py:479-482`, `transports/codex.py:215`). Where the vendor
rejects an unrecognized dial, **nothing is sent and the server default applies** — grok off
the allowlist, Gemma on the Gemini provider (`_build_gemini_thinking_config` returns `None`
for any non-`gemini` model, added for issue #17426 after the polite
`{"includeThoughts": False}` form also 400'd), and every route the capability gate does not
recognize. An unrecognized *user* value never propagates: `parse_reasoning_effort`
(`hermes_constants.py:820`) returns `None` and logs `"Unknown reasoning_effort '%s', using
default (medium)"`. Where a level is real but too strong for the target, it is **clamped
rather than dropped** — `xhigh|max|ultra → high` on xAI Responses, `minimal → low`
everywhere, Gemini 3 Pro's `low|high` versus Flash's `low|medium|high`.

### What this does not say

Hermes is not immune; it is immune *where someone engineered against this specific failure*,
and carries the ordinary disease everywhere else. The clearest instance is internal and
checkable at the pin: `_supports_reasoning_extra_body`'s OpenRouter prefix list includes
`google/gemini-2` and `qwen/qwen3` (`run_agent.py:6473-6484`), while
`_build_gemini_thinking_config` two files away already branches on `gemini-3` and
`gemini-3.1`. **So a Gemini 3 model reached through OpenRouter fails the capability gate and
is sent no reasoning field at all**, in a codebase that demonstrably knows Gemini 3 exists.
Same failure shape as opencode's `glm-5.2` — the quiet one, an under-send that succeeds and
lets the server decide. `_reasoning_config_for_model` (`transports/chat_completions.py:21`)
is a second, dated instance in waiting: it maps `ultra → max` only when `"gpt-5.6" in model`,
duplicated in `codex.py:223-225`, so a successor shipping under any other id would forward the
product-tier word `ultra` as a wire value the Responses API does not define.

**Prediction, scored at the next re-read (rule: dated and falsifiable).** By **2027-02-28**,
the Anthropic denylist will still be correct for every Claude released between this pin and
then *without a code change*, while at least one of the two allowlists above
(`_GROK_EFFORT_CAPABLE_PREFIXES`, the OpenRouter vendor prefixes) will have gone stale
against a model shipped in the same window. The asymmetry, not either half alone, is the
claim.

### Re-read at v2026.8.31 (2026-09-04) — the section's diagnosis was validated by upstream's own actions

Citations above are at the old pin; at v2026.8.31 the chokepoints moved
(`resolve_reasoning_config` → `hermes_constants.py:1464`, the capability gate →
`run_agent.py:7676`, the Anthropic comment → `anthropic_adapter.py:173-192`, call sites
`:352/:372/:415`, the Grok allowlist → `model_metadata.py:636-650`) and a **fifth
decision point appeared** in the four-point stack question 1 traced:
`agent/reasoning_effort.py`, a canonical effort ladder + one
`clamp_effort` policy (nearest weaker supported level, never escalate, never invert),
with wire vocabularies declared as data constants. Its Rule 3 — "Never patch a
predicate. When a provider rejects a level, fix its declared supported set (data), never
add another vendor-name special case" — is this section's own diagnosis turned into a
house rule.

**The "instance in waiting" fired, and is scored: correct.** The `ultra → max` map keyed
on `"gpt-5.6" in model` bit exactly as described — upstream issue **#89503** — and the
fix commit (`f7d90c941`) deleted both hand maps; the clamp comment at
`transports/codex.py:605-610` names the same mechanism: hand maps "repeatedly leaked
internal levels like 'ultra' to the wire (#89503 class)". A successor under an
unrecognized id now clamps to the nearest weaker level instead of forwarding an
undefined wire value. The OpenRouter gap was **demoted, not fixed**: a live
`/v1/models` capability probe now answers first (motivated in-comment by the list going
"stale one vendor at a time — #75386"), but the static fallback still reads
`google/gemini-2` and `qwen/qwen3` (`run_agent.py:7743/:7745`) — the under-send
survives on a cold cache only.

**Evidence on the 2027-02-28 prediction, recorded, not scored** (the window stays open):
across 7,055 commits both Claude tuples are **byte-identical** — zero code changes,
through a commit that split the adapter godfile into four modules — while
`_GROK_EFFORT_CAPABLE_PREFIXES` **required a hand-extension** (`grok-4.6`,
`model_metadata.py:645-646`). Both halves currently point the predicted way.
Complication for scoring: the OpenRouter allowlist named in the prediction has been
architecturally demoted to a fallback, changing what "goes stale" means for it. New
evidence on the axis itself: two **new Anthropic allowlists** appeared —
`_MANDATORY_THINKING_CLAUDE_SUBSTRINGS = ("claude-fable",)` (families that 400 on a
thinking *disable*), whose comment reasons about allowlist risk explicitly ("the failure
here is asymmetric… **When in doubt, add the family**"), and a one-family
`_FAST_MODE_SUPPORTED_SUBSTRINGS` — the source-side counterpart of ADR-0049's
`fast_mode` key. The vendor picks list polarity per failure direction, now with the
reasoning written down on both sides.

## Open questions

- **Does the learning loop pay?** Still unmeasured, and the negative got *stronger* at
  the re-read: the window added an `evals/` directory with four committed A/B harnesses
  (compaction recall, browser-tool shape, `read_file` design, tool-schema diet) — the
  instrument now exists, and none of the four takes skill/memory accumulation as its
  dependent variable (rule 1b: searched `evals/*/README.md` subjects and grepped
  `evals/` for skill/memory). Meanwhile the starvation finding (see the distinguishing
  bet) shows the loop can run for days while silently doing nothing — so "does it pay"
  is not answerable from the code even in principle; it needs the ledger telemetry the
  window just added. A natural experiment for this repo's rig remains: same task
  battery, fresh Hermes vs one seeded with N sessions of use.
- ~~What do 221k stars represent vs ECC's 235k?~~ **Partially answered at the re-read
  (2026-09-04)**: 241,330 stars against **940 watchers (0.39%)** and a 25% lifetime PR
  merge rate over a 26,158-deep open-PR queue — viral discovery plus a product-scale
  contribution firehose, not a prompt-pack phenomenon. A full comparison still needs the
  same numbers at an ECC re-read
  ([issue #45](https://github.com/leandromineti/ai-assisted-coding/issues/45)).
- Does the `execute_code` refund actually shift model behavior toward programmatic tool
  calling, or do models ignore the affordance? Their own trajectory data could answer
  it; nothing committed does (re-checked: the four new evals don't either).
- ~~Is `conversation_loop.py` being strangler-figged?~~ **Answered: no** (2026-09-04).
  It grew 7,040 → 8,830 lines over 107 window commits; the 9 that mention
  refactor/extract are local consolidations, and the 29 new `agent/` modules are new
  concerns, not carved-out loop internals. *(Post-pin caveat: in the 4 days after the
  tag, an automated campaign cut every megafile 75–85% — see the release assessment;
  whether that decomposition holds is the next re-read's question.)*
- ~~How much of the velocity is agent-operated maintenance?~~ **Partially answered
  (2026-09-04)**: explicit `Co-Authored-By` agent trailers cover 8.7% of window commits
  (Claude Fable/Opus/Sonnet models named, plus Cursor and Junie) — but the post-tag
  burst proves the repo also runs large *uncredited* agent campaigns under the
  maintainer's identity, so the trailer count is a floor with no matching ceiling. The
  repo makes no in-repo claim about the share (rule 1b: searched AGENTS.md at both revs
  + docs/** for agent-written/AI-generated/simp). `contributors/emails` decoded: a
  per-file email→login map that exists so concurrent PR merges never conflict —
  CI-enforced, 320 → 935 files in the window.

## Release assessment — v2026.8.31 (2026-09-04; pin 524ab5399 → 29112bef0)

*Method: the release-re-read variant of the three-tract pattern — release substance,
per-claim confrontation (HOLDS/MOVED/CHANGED/GONE/NEVER-REPRODUCED), provenance
re-measurement — with load-bearing findings spot-verified in the main session. Window:
524ab5399 (2026-07-30) → 29112bef0 (= tag v2026.8.31), 7,055 commits over 31.9 days,
clean ancestry. The published-artifact probe is omitted with reason (see Cost model: no
artifact matches any recent pin). Corrections to claims wrong at their own pin are
marked in place above (≤2 re-prompts; `hermes sessions export`, not `hermes trace
upload`; main.py 12,420 lines; Teknium count re-measured); this section carries what
the window did.*

### Velocity is two different regimes, and only one of them is development

The window itself is sustained, PR-driven, and bugfix-dominated: ~221 commits/day,
2,974 merged PRs (~2.4 commits each), 3,892 `fix(` to 792 `feat(` — 55% bug-fixing,
with the one feature concentration in the desktop app (239 feats). Then, **in the four
days after the tag**, a single automated simplification campaign added 5,211 commits
(~1,353/day; 4,105 on 2026-09-02 alone, 87% under the maintainer's identity), merged
through 432 `simp/*` branches that exist nowhere before the tag, bypassing the PR
process (13 merge-PR commits in the whole burst), and netting **−219,419 lines** —
every megafile this report names was cut 75–85% (`gateway/run.py` 33,539 → 5,512;
`cli.py` 22,268 → 4,656), and the 1,784-line root `AGENTS.md` was fanned out into 12
per-directory guides. None of it carries an agent trailer; nothing in-repo documents
the campaign. Two consequences for this report: a hermes commit count is meaningless
without naming which regime produced it, and the "flat Python core with megafiles"
characterization — *more* true at this pin than at the last — was reversed wholesale
four days later. **Scoreable for the next re-read: does the post-burst decomposition
hold, or do the megafiles regrow?**
([issue #44](https://github.com/leandromineti/ai-assisted-coding/issues/44) carries
this and the section's other scoreables.)

### What the window built

- **An autonomy surface**: 11 new slash commands (registry 90 → 101), the notable
  cluster being agent re-entry — `/loop` and `/heartbeat` (recurring prompts that
  re-enter an idle session), `/bg` (background session), `/btw` (side question without
  interrupting), with `/pause` as a gateway-wide emergency stop (`agent/estop.py`).
  The resident-companion bet deepened in exactly the direction `residency: resident`
  describes.
- **Agent-to-agent, twice**: Bot Mode (`tools/bot_mode_dm.py` — agents on the user's
  gateways discover and DM each other over a synced roster; the `message_agent` schema
  is injected only into a bot's canonical Bot Chat session, kept out of the global
  registry and every toolset) and an **A2A protocol v1.0 platform**
  (`plugins/platforms/a2a/`, stdlib-only, inbound + outbound, off by default) whose
  DESIGN.md doubles as enforcement evidence for the plugin-boundary policy: it
  documents four earlier core-patching attempts rejected before `ctx.register_platform()`
  made a zero-core-edit version possible.
- **A browser overhaul** (15 browser/preview modules; `browser_exec` can replace the
  whole `browser_*` toolset behind `browser.backend: "browser-use"`) — with its own
  committed A/B eval, like the compaction and read-tool decisions. The eval habit
  (Surprise 7) generalized from MCP exposure to four more design decisions in one
  window; the learning loop stays the unmeasured one.
- **Governance hardening**: the AGENTS.md triage sweeper text grew mostly on *when not
  to close* (three enumerated close reasons; taste-based rejection reserved to humans;
  rubric "distilled from real closes"), and root AGENTS.md gained eight scar-tissue
  sections each citing issue numbers. Release cadence: 8 date-versioned tags in the
  window (~1.75/week), zero rc/beta discipline ever, `.2` suffixes as same-day
  hotfixes — plus five operational-scar refs (`premerge-oh-god`,
  `backup/opentui-prestrip-…`) from a bad 2026-05-28.
- **Competitor absorption as standing posture**: the window ported grok-cli's verify
  subsystem with source URLs in the docstring, wrote an RFC on plugin-architecture
  lessons from pi and opencode, and built `evals/readtool/` because a rival's
  ten-harness benchmark got Hermes' column wrong. Reading competitors' rules files
  (Surprise 3 of the deep-dive) was one instance of a general behavior.
- **`/plan` promoted from skill to builtin** — because messaging platforms cap command
  menus and trim the skill tier alphabetically, and `plan` sorted past the cutoff. A
  downstream UI cap forcing a capability from the extension tier into the core is the
  reverse of AGENTS.md's "extended through plugins and skills, not by growing the
  core", and worth carrying to the category-6 discussion.

### The re-read's own audit

Four claims never reproduced at their own pin — the "≤3 re-prompts" cap (2 at both
pins), the `hermes trace upload` command name (mechanism real, identifier invented),
`hermes_cli/main.py` at 11,031 lines (12,420 — provably not a clone artifact, since a
citation into the same blob lands exactly), and the Teknium count stated without its
measure. Against those, the counts that carried an implicit measure — 89/38/61/78/58
tool-surface numbers, 70/111 skills, the 2,694- and 860-char prompt blocks, the
mcp-research bench figures to the dollar, and three of the four megafile line counts —
reproduced exactly; the one with-measure miss is the fourth megafile count above. The
same split the ai-memory re-read scored 8-for-8 vs 0-for-5 holds here in kind if not
in a single clean ratio: measured counts survive their own pin, unmeasured ones are
where the errors live. One inter-doc conflict found upstream: two docstrings
disagree about which cache tier the workspace snapshot lives in (`system_prompt.py`
says context; `coding_context.py` says stable); this report follows the assembler.
