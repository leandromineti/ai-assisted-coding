---
# PIN MOVED 29112bef0 → f97608f178 (= tag v2026.9.24) at the 2026-09-24 release re-read
# (rule 4b: three Opus tracts — release substance by component, per-claim confrontation at
# all three pins, provenance/scoreables — main-session spot-verification; window 14,831
# commits). The 2026-09-04 release assessment and its sections stay dated at 29112bef0;
# the sections below it stay dated at 524ab5399 as their own header says.
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
version: v2026.9.24   # tag subject "chore: release v0.21.5 (2026.9.24)"
commit: f97608f178
first_commit: 2025-07-22
stars: 248666
stars_at: 2026-09-24   # repo-facts.sh; 241,330 at 2026-09-04
read_at: 2026-09-24   # v2026.9.24 release re-read (window 14,831 commits, three regimes — § Release re-read v2026.9.24); v2026.8.31 release re-read 2026-09-04 (window 7,055 commits); deep-dive 2026-07-30 @ 524ab5399, drift-checked 2026-08-12, reasoning-param targeted read 2026-08-27
depth: deep-dive
harness_features:
  mcp: true              # tools/mcp_tool.py + optional-mcps/ + committed exposure-strategy bench (mcp-research-data/) DRIFT 2026-09-24: `mcp-research-data/` was deleted upstream 2026-09-13 (0c0875b746, "delete orphaned bench data") — the value holds on 25 `tools/mcp_*.py` modules + `optional-mcps/` at f97608f178; Surprise 7's exhibit is no longer in-tree
  lsp: true              # agent/lsp/ (client, manager, servers, workspace)
  hooks: true            # plugin lifecycle hooks (pre_llm_call, pre_verify), shell hooks
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: no codebase index of any kind — read_extract/read_preview/read_window/file_operations are model-dispatched tools, and the only content index in the repo is FTS5 over the agent's OWN session history (tools/session_search_tool.py), not source; confirmed absent by targeted grep (embed|repo-map|code-index|vector-store|semantic-search @ 29112bef0) alongside the context-assembly section's tier inventory
  context_compaction: [llm-summarize, prune]  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: agent/context_compressor.py runs an auxiliary-model summary by default (in-place compaction replaced session rotation as the default); a deterministic tool-result pruner (_prune_old_tool_results, :3993) ships OFF — proactive_prune_tokens: 0 in config_defaults.py:874, an opt-in trigger At v2026.9.24: proactive_prune_tokens still 0 (config_defaults.py:592), micro_compact False (:603); ONE changed default — `threshold_tokens` None → 256_000 (:570), an absolute trigger so 1M-window models compact at all
  turn_end_gates: engine # ADR-0012 graded: agent/verification_stop.py — in-loop policy, ≤2 re-prompts (max_attempts=2) when the model finishes without fresh verification evidence (body §termination). CORRECTED 2026-09-04: the deep-dive wrote "≤3", wrong at its own pin — max_attempts: int = 2 at 524ab5399:210 and v2026.8.31:238 alike At v2026.9.24: max_attempts=2 at verification_stop.py:159 (third pin in a row); gates now run as one ordered pipeline, agent/turn_stop_gates.py:105 (verify-on-stop → pre_verify hook → kanban terminal-tool guard). CORRECTION 2026-09-24, true at BOTH pins: verify-on-stop ships **default OFF** — `"verify_on_stop": False` at config_defaults.py:201 (:264 @ 29112bef0); the grade is the mechanism's, a fresh install does not run it (presence ≠ operative)
  tool_approval: policy  # tools/approval.py — approval at tool dispatch; re-verified at v2026.8.31 (file grew 44% in the window; YOLO import-freeze, smart approval, timeout≠denial all intact) At v2026.9.24: tools/approval.py 5,971 → 1,354 lines with seven approval_*.py siblings; YOLO import-freeze at :43-45, unified bypass predicate at :484-488, `approvals` config block key-identical across pins
  skills: true           # 58 bundled + 137 optional SKILL.md dirs at v2026.8.31 (was 70+111 — bundled SHRANK while optional grew: surface moving out of the default install); agentskills.io-compatible At v2026.9.24: 58 bundled + **150** optional (`git ls-tree -r --name-only v2026.9.24 skills/ | grep -c SKILL.md$`, same over optional-skills/) — bundled flat, optional +13
  subagents: true        # delegate_task (tools/delegate_tool.py), single + parallel batch
  ptc: true              # execute_code: model-written Python calls tools via RPC; iteration budget refunds these turns (ADR-0012; refund re-verified at v2026.8.31, conversation_loop.py:7716-7720) At v2026.9.24 the refund is agent/turn_tool_round.py:185-188
  plan_mode: prompt      # /plan is a BUILT-IN command since the window (was a bundled skill; promoted because platform command menus trim skills alphabetically at their caps and `plan` sorted past the cutoff — agent/plan_prompt.py docstring). Still prompt-only, plans under .hermes/plans/, not a core loop mode
  rules_files: [SOUL.md, HERMES.md, AGENTS.md, CLAUDE.md, .cursorrules]   # reads competitors' files too — loaders in prompt_builder.py; v2026.8.31 adds AGENTS.override.md and .cursor/rules/*.mdc
  model_agnostic: true   # 39 provider plugins (ls plugins/model-providers/ minus README; was 33) At v2026.9.24: **38** (`opencode-free` removed, nothing added)
  session_sharing: true  # `hermes sessions export --format trace --upload` → Hugging Face agent-trace dataset (private by default, forced secret redaction); no hosted live-session links. CORRECTED 2026-09-04: the deep-dive wrote "hermes trace upload", a command that existed at neither pin — the mechanism was real, the identifier invented At v2026.9.24 the `--format trace` subparser is hermes_cli/subcommands/sessions.py:76; still no hosted live-session link
  evals: true            # mini_swe_runner.py, batch_runner.py, mcp-research-data/ — plus, new at v2026.8.31, evals/ with four committed A/B harnesses (compaction, browser tools, read_file design, schema diet); still none measuring the learning loop At v2026.9.24: `evals/` is 69 top-level entries (was 4), incl. codebase_navigability/, postmortem/, memory/ — and still none takes skill/memory accumulation as its dependent variable (`git grep -l skill_ledger v2026.9.24 -- evals` → 0; evals/memory/honcho_current_query.py:6 disclaims "not memory quality")
  learning_loop: background  # ON by default (config_defaults.py:1353): interval-gated review fork (turn_finalizer.py:806-819; nudge intervals 10) + idle curator + /learn + /refine. New in window: cron sessions suppressed, whitelist widened to read_file/search_files after the fork was found starving in production (see re-read), 600K-token/16-iteration fork budgets, JSONL skill ledger with rollback At v2026.9.24: default still ON (config_defaults.py:789), fork call site turn_finalizer.py:700-710, budgets background_review.py:150/:157; NEW: review_idle_queue.py defers reviews bound for the managed local llama-server until the machine is idle (`auxiliary.background_review.defer`); the loop STARVED AGAIN by a different mechanism (#115299) — § Release re-read v2026.9.24
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
| Trajectory export for training (`hermes sessions export --format trace --upload`, batch_runner — *identifier corrected 2026-09-24; the 09-04 audit retracted `hermes trace upload` in the frontmatter but not here*) | Distinctive — the research-lab tell |

## Stack & repo shape

Python 3.11+ (uv), with TypeScript for the desktop app (Electron), web dashboard, and a
Tauri bootstrap installer. **15,075** tracked files at v2026.9.24 (`git ls-tree -r`; 10,925 at
v2026.8.31, 8,071 at the deep-dive): 7,059 `.py`, 2,549 `.ts`, 1,613 `.md`, 1,221 `.tsx` —
plus 1,221 `.com` files that
are not code at all: `contributors/emails/` names each mapping file after a commit
email, a merge-conflict-avoidance structure invented for thousand-PR flow (one file per
mapping so concurrent salvage PRs never collide; CI-enforced; 1,545 files at v2026.9.24).
**41,514** commits in ~14 months (26,683 at v2026.8.31), maintainer-led, not drive-by-scaled
— Teknium is 7,421 of 19,628 at the deep-dive pin, 9,339 of 26,683 at v2026.8.31, and
**18,492 of 41,514 (44.5%)** at this one (`git shortlog -sn`, summing his two identities; the
deep-dive's "~7,350" carried no measure — corrected 2026-09-04). But a commit count for
this repo is **not a comparable unit of work**: see the re-read section's velocity
finding.

The shape **was** the opposite of opencode's 33-package monorepo — a flat Python core with
megafiles, *more* true at v2026.8.31 than at the deep-dive (`cli.py` 17,976 → 22,268;
`hermes_cli/main.py` 12,420 → 14,834; `run_agent.py` 7,410 → 9,413;
`agent/conversation_loop.py` 7,040 → 8,830; `gateway/run.py` 25,766 → 33,539) — **and at
this pin it is false by every one of those measures** (rewritten 2026-09-24, not
annotated: the characterization did not survive the pin move). The Sep 2026
decomposition (PR #102117, merged 2026-09-04) turned every god file into a *facade plus
`<stem>_<topic>.py` siblings*, and AGENTS.md now legislates it (`AGENTS.md:227-251 @
f97608f178`: "A file passing ~2,000 lines or a function passing ~300 lines / cyclomatic
complexity 30 is the signal to split"). `git show <rev>:<path> | wc -l`, three points:

| file | v2026.8.31 | 2026-09-04 post-campaign (`b51c055a1`) | v2026.9.24 |
|---|---|---|---|
| `cli.py` | 22,268 | 4,656 | **1,849** |
| `hermes_cli/main.py` | 14,834 | 3,433 | **3,652** |
| `run_agent.py` | 9,413 | 1,555 | **1,623** |
| `agent/conversation_loop.py` | 8,830 | 1,600 | **1,758** |
| `gateway/run.py` | 33,539 | 5,512 | **6,166** |

Megafiles are relocated, not abolished: the largest non-test `.py` is now
`agent/auxiliary_client.py` at 8,197 lines, and non-test files over 5,000 lines went 37 →
6 → **7** (PR #102117's own measure, reproduced). The `agent/` package is 245 top-level /
306 recursive `.py` modules (155 / 210 at v2026.8.31; `agent/turn_*.py` alone 4 → 31).
Capability lives at the edges as data: 58 bundled + **150** optional skills (`SKILL.md`
dirs; 137 at v2026.8.31, 111 at the deep-dive), **38** model-provider plugins (39), 22
gateway platform plugins. A 2,085-entry machine-readable compat manifest
(`COMPAT_MANIFEST.md` + `compat_manifest.json`, `scripts/check_compat_pointers.py` in CI)
declares the old import paths non-API — with a dated self-commitment the project missed:
"removed on 2026-09-14", and 338 `PLUGIN-COMPAT` blocks still in the tree at the 09-24 tag.

## Architecture

### Entry point → one full trace

```
hermes                      pyproject [project.scripts] → hermes_cli.main:main
  └ cmd_chat                hermes_cli/main.py:3163
      └ cli.main            cli.py (22,268-line interactive REPL at v2026.8.31; a 1,849-line facade at v2026.9.24, `cli.py:1647`)
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

`conversation_loop.py:2094` at v2026.8.31 (byte-identical since the deep-dive, only the line
moved — **the streak ended at v2026.9.24**: `agent/conversation_loop.py:1546` reads
`while (s.api_call_count < …`, the local became a field of a `_LoopState` dataclass, and
the loop body is gone — see § Release re-read v2026.9.24, 2):

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
  operating brief; *(at v2026.9.24 the environment hints left this tier for the END of
  volatile, `system_prompt.py:783-786`, for a prompt-integrity reason — § Release re-read
  v2026.9.24, 3)*
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
exact at the old pin, same measures — *and at v2026.9.24 the grep measure broke: 64
calls across 48 modules, because registration became table-driven (`kanban_tools.py`
14 call sites → one `for … in _TOOLS:` loop at `:1201`), while the AST-counted core set went
**53 → 59** and toolsets 59 → 61 — the "moved outward" reading below is reversed for
tools; § Release re-read v2026.9.24, 4*); **73 registrations carry a `check_fn`**
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
`hermes sessions export --format trace --upload` (*corrected 2026-09-24 — `hermes trace` was never a registered subcommand at any of the three pins*; exports sessions in Claude Code JSONL shape to Hugging Face,
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
   `mcp-research-data/` (at 29112bef0 — **deleted upstream 2026-09-13**, `0c0875b746`
   "delete orphaned bench data"; the figures below were re-verified to the dollar at that
   pin before the deletion and are no longer re-checkable in-tree) holds bench rows comparing three MCP exposure strategies
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
  battery, fresh Hermes vs one seeded with N sessions of use. **Stronger again at
  v2026.9.24**: `evals/` grew 4 → 69 entries including one literally named `memory/`,
  whose only file disclaims the question ("proves query routing, ownership and caller
  waiting, not memory quality", `evals/memory/honcho_current_query.py:6`); no eval
  references `skill_ledger`; and the ledger itself is now trimmed at 5 MB with
  oldest-entry eviction (#118696, 2026-09-22) — a rolling ~5-week horizon, so a
  ledger-based value study must capture during the run, not mine afterwards.
- ~~What do 221k stars represent vs ECC's 235k?~~ **Partially answered at the re-read
  (2026-09-04)**: 241,330 stars against **940 watchers (0.39%)** and a 25% lifetime PR
  merge rate over a 26,158-deep open-PR queue — viral discovery plus a product-scale
  contribution firehose, not a prompt-pack phenomenon. ~~A full comparison still needs
  the same numbers at an ECC re-read~~ **Fully answered 2026-09-04** (issue #45): ECC's
  pole measured — 248,417 stars on a **96-deep** open-PR queue merged at 49%. Near-equal
  stars, repos two orders of magnitude apart in contribution surface; the discriminator
  is open-queue depth, not stars. Full table:
  [`ecc.md` § Engagement re-measure](../6-extensions/ecc.md).
- Does the `execute_code` refund actually shift model behavior toward programmatic tool
  calling, or do models ignore the affordance? Their own trajectory data could answer
  it; nothing committed does (re-checked: the four new evals don't either).
- ~~Is `conversation_loop.py` being strangler-figged?~~ **Answered: no** (2026-09-04).
  It grew 7,040 → 8,830 lines over 107 window commits; the 9 that mention
  refactor/extract are local consolidations, and the 29 new `agent/` modules are new
  concerns, not carved-out loop internals. *(Post-pin caveat: in the 4 days after the
  tag, an automated campaign cut every megafile 75–85% — see the release assessment;
  whether that decomposition holds is the next re-read's question.)* **Reversed at
  v2026.9.24: yes** — the loop is a 1,758-line phase dispatcher over twelve `agent/turn_*`
  modules, and the decomposition held for 20 days (scored in § Release re-read v2026.9.24).
- ~~How much of the velocity is agent-operated maintenance?~~ **Partially answered
  (2026-09-04)**: explicit `Co-Authored-By` agent trailers cover 8.7% of window commits
  (Claude Fable/Opus/Sonnet models named, plus Cursor and Junie) — *measure corrected
  2026-09-24: 8.7% (612/7,055) is the share carrying ANY `Co-Authored-By:` trailer, 171
  of those lines `github-actions[bot]` and most of the rest humans; commits naming an AI
  co-author are 183 = 2.6%. A right number attached to the wrong sentence.* — but the post-tag
  burst proves the repo also runs large *uncredited* agent campaigns under the
  maintainer's identity, so the trailer count is a floor with no matching ceiling. The
  repo makes no in-repo claim about the share (rule 1b: searched AGENTS.md at both revs
  + docs/** for agent-written/AI-generated/simp). `contributors/emails` decoded: a
  per-file email→login map that exists so concurrent PR merges never conflict —
  CI-enforced, 320 → 935 files in the window.

## Release re-read — v2026.9.24 (2026-09-24; pin 29112bef0 → f97608f178)

Three Opus tracts (release substance by component · per-claim confrontation at all three
pins · provenance and the parked scoreables), load-bearing claims re-run in the main
session before writing. Window `git rev-list --count 29112bef0..v2026.9.24` = **14,831**;
`git diff --shortstat` 11,081 files, +1,285,800 / −1,004,361 (net +281,439). Five tags fell
inside it (9.7, 9.11, 9.14, 9.21, 9.24; ~1.5/week); the release note for v2026.9.24 covers
only v0.21.4 → v0.21.5 and defers curated notes to v0.22.0, so **no curated note covers
this pin-to-pin window**. The morning's `--check` had said 1,248 commits behind; the fetch
said 14,831 — the hermes lesson from 09-04, repeated.

**Velocity: three regimes, not two.** Per-day `%cs` histogram: a pre-tag tail of 261
commits on long-lived branches merged after the tag; the **campaign**, 5,117 commits on
09-01…09-04 (1,279/day, 65.5% `refactor`, `simp/` subjects on exactly two dates, 09-02 and
09-03); then **post-campaign PR-driven development at 473/day** (9,453 in 20 days; 574/day
in the last fortnight) — more than double the previous window's 221, with `fix:feat` at
9.3:1 (was 4.9:1). Merged PRs by the GitHub API: 3,764 in 24.6 days (153/day; 2,974 in the
previous 31.9). No second campaign: the heavy post-campaign days are mixed-author,
fix-dominated. Concentration: Teknium + teknium1 61.7% authored, Teknium **76.5% as
committer** — the maintainer is the merge button for three commits in four. Agent
trailers in the PR-driven regime: **8.81%** of commits carry any `Co-Authored-By:`
(8.67% last window — flat), AI-named co-authors 1.1% overall (2.5% in the campaign,
which the campaign itself pulls down: 0 of its 796 `simp/` commits carry one).

**1. The decomposition held — scored.** `git show <rev>:<path> | wc -l` at v2026.8.31 /
post-campaign `b51c055a1` / v2026.9.24: `cli.py` 22,268 / 4,656 / **1,849**;
`hermes_cli/main.py` 14,834 / 3,433 / 3,652; `run_agent.py` 9,413 / 1,555 / 1,623;
`agent/conversation_loop.py` 8,830 / 1,600 / 1,758; `gateway/run.py` 33,539 / 5,512 /
6,166. Four regrew +4–12% in 20 days, one fell another 60%; all five are 75–92% below
their pre-campaign size. Non-test `.py` files over 5,000 lines: 37 → 6 → **7**
(`agent/context_compressor.py` crossed at 5,576; `agent/auxiliary_client.py` is the
largest at 8,197). The repo added back 2.3× what the campaign removed (+494,790 lines
post-campaign) **into new files** — 4,881 → 7,059 `.py`, mean file size 12.5 → 11.7 KB —
which is what the facade rule asks for. The rule is prose only: no size or complexity
gate exists under `scripts/` or `.github/` (rule 1b: grepped `cyclomatic|max.?lines|
line_limit|2000 lines|god file` at the tag → 0), and `gateway/run.py` is already 3× over
it and regrowing. The campaign is documented three ways at this pin (AGENTS.md
§ Facade + siblings, `COMPAT_MANIFEST.md` naming PR #102117 with a missed 2026-09-14
removal date, `evals/codebase_navigability/` — an offline eval of what a codebase costs
an *agent* to navigate: tokens per symbol lookup, 2,000-line `read_file` windows spanned).

**2. The loop is a phase dispatcher now.** `agent/conversation_loop.py:1395` `_run_phase`
calls twelve `agent/turn_*` modules (bound at import "so a source-tree swap cannot load a
skewed phase mid-turn", `:38-39`), each returning a verdict whose `.action` is `return` /
`break` / `continue`, with one latched field family (`_LATCHED_VERDICT_FIELDS`, `:1392`)
so an error handler cannot clear an earlier arm. Entry trace: `run_conversation` `:1605` →
`_run_conversation_turn` `:1448` → `_run_api_retry_loop` `:1416` → `finalize_turn`
(`agent/turn_finalizer.py:490`); the gateway hop moved to `gateway/run_turn_runner.py:1726`.
Stuck-loop guardrails: same module, 854 → 639 lines. Budgets unchanged (500 / 50,
`agent/iteration_budget.py:4-5`); the `execute_code` refund carved out to
`agent/turn_tool_round.py:185-188`. New and default-off: `api_mode == "codex_app_server"`
hands the whole turn to a codex app-server subprocess (`:1527-1543`). **Turn-end gates
are now one ordered pipeline** — `agent/turn_stop_gates.py:105` runs verify-on-stop →
`pre_verify` plugin hook → kanban terminal-tool guard, each with its own attempt counter;
`max_attempts=2` holds for the third pin running (`verification_stop.py:159`). And the
correction this re-read owes at *both* pins: **verify-on-stop ships off** —
`"verify_on_stop": False` (`config_defaults.py:201`; `:264 @ 29112bef0`; "default OFF
(opt-in)" in the function's own docstring at both) — the report graded the mechanism and
never said a fresh install does not run it. Also at both pins: the in-loop nudge's text
tells the model to run `hermes verify --json` (`verification_stop.py:195,201`), so "not
registered as a model tool" was true and understated.

**3. Context assembly — two tier moves, one changed default.** Environment hints left the
stable tier for the *end of volatile* (`stable_parts.append(_env_hints)` at
`system_prompt.py:677 @ 29112bef0` → `volatile_parts.append(f"{RUNTIME_ENVIRONMENT_HEADING}…`
at `:783-786`), for a prompt-*integrity* reason, not a cache one: "so quoted host examples
cannot shadow it during persisted-prompt validation" — the first instance in this report
where "caching is sacred" lost an argument. Project context files moved ahead of the
worktree snapshot inside the context tier (`:762-773`) "so a shared context file can
remain in the longest common prefix across worktrees" — a sibling-worktree cache win.
Plugin prompt sections are frozen into one coarse anchor a resumed process can
reconstruct without re-running plugins (`:113`, `:170`, emitted `:779`). Compaction:
every default SAME except `threshold_tokens` None → **256_000** (`config_defaults.py:570`),
an absolute trigger added because 1M-window models "never fired" at the 50% ratio; the
lean tail gained a `TAIL_MAX_CONTEXT_FRACTION = 0.20` ceiling (`context_compressor.py:908`)
whose comment names a production failure on a local 27B where "the 'protected' tail WAS
the whole request". `plugins/context_engine/` is still only `__init__.py`. Native
compaction widened by one model (`gpt-6-astra` on official Codex OAuth). Rules files:
same precedence chain (`prompt_builder.py:1739-1740`), one carve-out — the injection
scanner now *warns* instead of blocking for a `SOUL.md` in the user's own `HERMES_HOME`
(`user_authored=False`, `:81`; #112570). Docs-vs-source, both directions:
`website/docs/developer-guide/prompt-assembly.md:33` correctly puts the skills index in
volatile and the runtime block at its end, then `:38` says skills are "part of the stable
tier"; source (`system_prompt.py:776`) settles it. The root `docs/` tree was folded into
the Docusaurus site and deleted (`0b40f5a790`, 2026-09-13) — rule-1b surfaces for this
subject are `website/docs/` + the twelve `AGENTS.md` from now on; and
`agent/system_prompt.py:8` now cites `references/system-prompt-invariant.md`, which does
not exist at the tag.

**4. Permissions and the tool surface.** Nothing loosened, nothing new in the config
surface: `tools/approval.py` 5,971 → 1,354 lines plus seven `approval_*.py` siblings, YOLO
frozen at import (`:43-45`, reworded), one bypass predicate (`:484-488`), the `approvals`
block key-identical across pins, `~/.ssh/config` still the only approval-gated carve-out
from the write deny set, root's home now added to it (`file_safety.py:80`). Three things
the previous reads under-recorded exist at *both* pins — the `approvals.deny` glob list
that blocks even under `--yolo`, the denial circuit-breaker (`denial_breaker_threshold:
3`), and the Tirith content-security scanner (`approval.py:640-670`) — gaps, not window
changes. **The tool-count measure broke**: `registry.register(` grep 93 → 64 across 45 →
48 modules while no tool was removed — registration went table-driven (`kanban_tools.py`
14 → 1, `browser_tool.py` 10 → 1); by the AST measures that survive, `_HERMES_CORE_TOOLS`
**53 → 59**, `TOOLSETS` 59 → 61, `COMMAND_REGISTRY` 101 → 102, `VALID_HOOKS` 37 → 41. The
09-04 reading "core set shrank 61 → 53, default surface moving outward" is **reversed for
tools** and holds for skills (optional 137 → 150) — a two-point trend read as a direction.
A count can carry its measure at its own pin and still die at the next one.

**5. The reasoning-parameter stack, and the 2027-02-28 prediction's evidence.** Every
chokepoint moved (`resolve_reasoning_config` → `hermes_constants.py:1415`; the capability
gate and the OpenRouter static list → a new `agent/reasoning_params.py:88` / `:15-16`;
Anthropic predicates → `anthropic_adapter.py:159-187`; Grok allowlist →
`model_metadata.py:413`; `EFFORT_LADDER` / `clamp_effort` → `reasoning_effort.py:25` /
`:120`), the architecture is intact, and Rule 3 ("never patch a predicate") now heads the
module docstring over a wall of named wire vocabularies as data, several with dated
live-probe provenance in-comment. Evidence, not a score: across 14,831 commits **all
three Claude denylists are entry-identical** (15 / 4 / 1 entries; cumulative zero content
changes across 21,886 commits and ~56 days) and `_GROK_EFFORT_CAPABLE_PREFIXES` needed
**no** hand-extension this window (same five). The OpenRouter static fallback is
byte-identical (`google/gemini-2`, `qwen/qwen3`, no `gemini-3`) with the live probe still
answering first — the cold-cache under-send survives, unfixed, and upstream #75386 is
still open at 55 days. **The sharpest instance is on Anthropic's own side and on neither
list the prediction named**: the one construct built as an *allowlist*,
`_FAST_MODE_SUPPORTED_SUBSTRINGS = ("opus-4-6","opus-4.6")` at 29112bef0, was wrong at that
pin (4.6 "silently runs and bills at standard speed"), hand-extended at 9.7/9.14/9.21 to
`("opus-4-8","opus-4.8","opus-5")`, and rewritten again on 09-23 (`78a50c28fc`, PR
#120517: "the old 'opus-5' substring matched any future Opus 5.x") to an exact-id
`_ANTHROPIC_FAST_MODE_MODELS = frozenset({"claude-opus-4-8","claude-opus-5","claude-opus-5-5"})`
(`model_metadata.py:446`) — two corrections in 24 days, versus zero for the denylists.
ADR-0049's source-side counterpart changed file, shape and polarity discipline. Adjacent:
an OpenAI *denylist* appeared for chat-era families that 400 on any `reasoning` field
(`model_metadata.py:423-426`, "fail-open"). And the `ultra` leak **recurred in an
untouched path** — #112010 (opened 2026-09-15, closed in ~10 h): the aux/MoA
chat-completions path never clamped, fixed by applying "the same entry clamp the main
transport applies (#89503)" (`auxiliary_client.py:6613`, `reasoning_effort.py:184`). The
house rule was not applied at every entry point.

**6. The learning loop starved again, by a different mechanism.** The whitelist widening
the 09-04 read documented persists verbatim (`background_review.py:1090-1104`). But
#115299 (merged 2026-09-18, "Background review fork can update skills *again*") found the
fork's `skill_view`/`read_file` hitting the parent session's repeat-view dedup stub, so the
read-before-write guard was never satisfied and skill writes were refused — a second
starvation in a second consecutive window. #106310 (2026-09-09) found the same whitelist
bug class in the other direction: a skills-only fork held the whole `memory` toolset,
allowing "standing-rule deletions with no user in the loop" on `MEMORY.md` — now staged
for approval. New: `agent/review_idle_queue.py` defers reviews bound for the managed local
llama-server until the machine is idle, because the fork "monopolizes the GPU the next
prompt needs and the next live turn cancels it (decode cost paid, learning lost)" — a
third failure mode on record: denied (fixed), unmeasured (still), preempted by the user's
own next prompt (new). Open upstream: #109375, #107850.

**7. Release notes carry their measure.** The v2026.9.24 body names the commit it was
measured at and states 1,610 non-merge commits / 4,828 files / +164,132 / −149,440 / 475
closed issues / ~460 merged PRs for v2026.9.21..v2026.9.24; **four of five reproduce to
the digit** (`git rev-list --count --no-merges`, `git diff --shortstat`, `gh api
search/issues` with the tags' exact timestamps; merged PRs 455 vs "~460"). All eight
features the body names as "undocumented here on purpose" are locatable in the tree. What
the note omits: `tests/` is 55% of the release's changed files, and the fast-mode gate
correction above lands inside it unmentioned. There is no in-repo CHANGELOG (rule 1b:
`git ls-tree -r --name-only v2026.9.24 | grep -i changelog` → a desktop-app feature file
and CI classifiers only).

**8. Provenance the reports cited was condensed away — a distinct hazard.** The
`single-block cache_control` caveat (`system_prompt.py:923-924 @ 29112bef0`), the dated
`grok-4.5` live-probe comment, `/plan`'s alphabetical-cutoff rationale, the verbatim YOLO
comment, the numbered Rules list in `reasoning_effort.py`, and the inter-doc conflict
about the workspace snapshot's cache tier (now resolved: `coding_context.py:8-9` names no
tier, `system_prompt.py:6` says `context` — the 09-04 call to follow the assembler was
right) are all gone at f97608f178 while every mechanism they described survives. A
subject that periodically rewrites its own comments rots a report's *evidence* faster
than its *claims*; those citations stay pinned to 29112bef0 and say so. `README.md` is
byte-identical at all three pins (blob `c0511226…` across 21,886 commits) — the marketing
surface is the most stable artifact in the repository.

**9. Candidate vocabulary, flagged only (owner gate).** (a) A harness that *ships a model
server*: `hermes_cli/local_runtime/` — 19 files, absent at 29112bef0 — downloads and
verifies llama.cpp release binaries, reads GGUF headers, probes VRAM, physics-checks the
requested context window and supervises a router-mode `llama-server`; default-off
(`"local_runtime": {"enabled": False}`, `config_defaults.py:2639-2641`). Adjacent to
`model_agnostic`, not the same claim; a harness fact, not a category-1 assessment
(ADR-0048). (b) The phase-verdict loop (2) — instance #1 of a "loop decomposition" shape
no key names. (c) Stacked turn-end gates (2) — `turn_end_gates` grades the strongest
carrier and cannot express a stack, the same tension `context_compaction` resolved with a
list. (d) A CI-enforced, dated deprecation manifest for an extension surface — category 6
more than 2. (e) A remote shared-metrics sender (`telemetry.shared_metrics.send`,
endpoint `telemetry.nousresearch.com`, `config_defaults.py:2298-2306`, 11 new
`hermes_cli/observability/` modules) — new egress surface, double-gated `False`; the Cost
model section's "source not audited for outbound calls" is now findable.

**10. The re-read's own audit.** Counts stated with their measure: **30 of 30**
reproduced at their own pin (48 individual figures across two pins, all exact — tool
counts ×10, skill dirs ×4, provider plugins ×2, megafile lines ×10, prompt-block chars
×6, `max_attempts` at every pin, the MCP bench to the dollar, window commits/days/rate,
tags, the `/plan` registry, fork budgets, contributors files, evals dirs). Without a
stated measure: **1 of 5** — the velocity paragraph's `fix(`/`feat(` (3,889/784 by the
nearest measure), 2,974 PRs (a GitHub-API figure, now labelled), 239 desktop feats (243),
and 8.7% agent trailers (a right number attached to the wrong population — corrected in
place); only the post-tag burst block reproduced. The split the ai-memory re-read scored
8-for-8 vs 0-for-5 reproduces here at larger n, and cleanly. Two identifiers the 09-04
audit retracted in the frontmatter survived in the body (`hermes trace upload`, twice) —
corrected. The campaign's "bypassing the PR process" was **wrong**: the branch was read on
`main` the same day PR #102117 wrapped it. One new failure shape for the ledger: 8.7% was
a stated measure that described a different population than the sentence.

**Predictions, scored at the next re-read (dated, falsifiable).**
- **P-1.** On **2026-12-24**, non-test `.py` files over 5,000 lines number **between 8 and
  13 inclusive** (37 → 6 → 7 at +1 per 20 days, against ~75 new `.py` files/day and a
  prose-only ceiling), **and** no mechanical size/complexity gate exists under `scripts/`
  or `.github/`. ≤7 = the norm grew teeth; ≥14 = the campaign was a one-off; a gate landing
  is the more interesting falsifier and should be recorded as such. Secondary:
  `gateway/run.py` > 6,166 and < 10,000 lines.
- **P-2.** The 2027-02-28 prediction stands unscored. Recorded beside it: the asymmetry
  fired *inside Anthropic* (three denylists 0 changes / one allowlist 2 corrections in 24
  days) and on neither named list.
- Next trigger (issue #32's rule): **v0.22.0**, the tag upstream promises will carry the
  curated notes from v0.21.0 onward — the first chance to score the release-note
  discipline against a curated note.

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
2,974 merged PRs (~2.4 commits each; *a GitHub-API figure — `gh api search/issues -f
q="… is:pr is:merged merged:2026-07-30..2026-08-31"` reproduces it exactly, the clone
cannot: hermes squash-merges, 275 `Merge pull request` subjects — measure stated
2026-09-24*), 3,892 `fix(` to 792 `feat(` — 55% bug-fixing (*recounted 2026-09-24 with
the measure stated: `git log --format=%B 524ab5399..29112bef0 | grep -c 'fix('` → 3,889 /
784; subject-anchored 3,617 / 719*),
with the one feature concentration in the desktop app (239 feats; 243 by
`^feat\((desktop|apps/desktop)`). Then, **in the four
days after the tag**, a single automated simplification campaign added 5,211 commits
(~1,353/day; 4,105 on 2026-09-02 alone, 87% under the maintainer's identity), merged
through 432 `simp/*` branches that exist nowhere before the tag (447 distinct names at the
next fetch), ~~bypassing the PR process (13 merge-PR commits in the whole burst)~~ —
**CORRECTED 2026-09-24: the campaign landed as PR #102117**, a two-parent merge
(`d3630f8532`, 2026-09-04, "refactor: whole-codebase simplification — −34% source LOC,
every god file decomposed, zero behavior change", 4,271 commits, +436,199/−784,430 by its
own body); the `simp/*` merges were the side branch's interior, read on `main` the same
day the wrapper landed — and netting **−219,419 lines** —
every megafile this report names was cut 75–85% (`gateway/run.py` 33,539 → 5,512;
`cli.py` 22,268 → 4,656), and the 1,784-line root `AGENTS.md` was fanned out into 12
per-directory guides. None of it carries an agent trailer (0 of 796 `simp/` commits,
re-checked 2026-09-24); ~~nothing in-repo documents the campaign~~ **it does at
v2026.9.24** — `AGENTS.md:227` "Facade + siblings layout (Sep 2026 decomposition)", added
*during* the campaign (`27a4023791`, 2026-09-03), plus `COMPAT_MANIFEST.md` and an offline
eval built to hold future refactors to the same numbers
(`evals/codebase_navigability/`). Two consequences for this report: a hermes commit count is meaningless
without naming which regime produced it, and the "flat Python core with megafiles"
characterization — *more* true at this pin than at the last — was reversed wholesale
four days later. **Scoreable for the next re-read: does the post-burst decomposition
hold, or do the megafiles regrow?** *Scored 2026-09-24: HELD — see § Release re-read
v2026.9.24, 1.*
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
