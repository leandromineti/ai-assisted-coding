---
name: ai-memory
category: 5
type: memory
vendor: Fabio Akita (akitaonrails)
url: https://github.com/akitaonrails/ai-memory
license: MIT
open_source: true
stack: [Rust]
version: v1.28.1-16-gacd9c0b
commit: acd9c0b
first_commit: 2026-05-21
stars: 2596
stars_at: 2026-08-18
read_at: 2026-08-18   # deep-dive read, same day as the stub
depth: deep-dive   # capture→consolidate→handoff traced in source (hooks/, ai-memory-hooks, ai-memory-consolidate); Claude Code installer read end-to-end (install_hooks.rs + render_shared.rs + commands/hook.rs); MCP tool surface read at router + ARCHITECTURE level. NOT traced: the managed-workstream loop (`ai-memory run`, docs-level only), the web frontend, and the retrieval RRF internals beyond the store's table shapes
harness_targets: "README support matrix at acd9c0b lists ~24 targets — Supported with MCP + lifecycle hooks: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Devin CLI, Command Code, Kimi Code, Kiro CLI, OpenClaw, Antigravity CLI, Grok Build CLI, Zero, Pi, OMP; MCP-only: Claude Desktop, VS Code Copilot, Zed, Swival; community: Hermes. Counted from README; Claude Code verified in source (this read), others spot-checked at the event-table level in render_shared.rs"
features:
  learning_loop: true   # SOURCE-TRACED this read: background, harness-independent — server-side scheduler (auto_improve_schedule.rs) reviews completed sessions via LLM, stages proposals, AUTO-APPROVES wiki edits by default (require_approval=false); plus a durable session-end LLM consolidation queue. Zero-LLM install has no loop; with a provider configured the loop is default-ON. Second verified harness-independent instance after ECC
memory_features:   # ADR-0013 block, set 2026-08-19 from the existing deep-dive read at acd9c0b — not a re-read
  memory_store: files-git        # git-versioned markdown wiki is the source of truth; SQLite/vectors are derived indexes (body: store section) — the kind's only files-git wager
  capture_path: hook             # harness lifecycle hooks → closed 10-value ObservationKind → rule-based session pages, no LLM on the default path
  write_admission: evidence-gated  # MEASURED (exp-04 arm C, 2026-08-19): the auto-improve reviewer rejected all 12 conversational-fact candidates — "Offline decision acknowledged but not made or refined in session; no implementation evidence" — say-so does not earn autonomous storage; the explicit write-page path remains available for deliberate recording
  recall_injection: both         # auto: thin cwd-matched handoff baton injected via per-harness envelopes; rich wiki is pull-only via 18 MCP tools
  memory_scope: [project, user]  # .ai-memory.toml walk-up for project scoping; per-user slot namespaces
  memory_tiers: true             # working/episodic/semantic/procedural
  hybrid_retrieval: true         # RRF over FTS5 + entity index + link neighbors + optional vectors, optional reranker
  memory_revision: auto          # background consolidation auto-approves its own wiki edits by default (require_approval=false, deep-dive); rules/procedures go through proposals — mixed, but the default write path is auto
  decay: true                    # exponential-decay retention + forget sweep
  injection_trust_boundary: true # untrusted-data delimiters on observations, wiki pages, proposals, AND injected handoffs
  deployment_mode: self-host     # localhost-bound daemon, regex sanitizer at ingress, zero-LLM default
  harness_installer: true        # install-hooks --apply mutates ~/.claude/settings.json (9 CC events)
  rule_extraction: true          # _rules/ + procedures/ proposal paths, confidence-floored, audit-logged
---

# ai-memory

## What it is

Long-term, cross-harness memory for coding agents: one Rust binary that runs as a local
HTTP server, capturing sessions through each harness's own lifecycle hooks and exposing
retrieval through an MCP server. Sessions are consolidated at session end into a
plain-markdown wiki committed to a git repo (SQLite is a derived index, never the source
of truth), and the next session — in the *same or a different* harness — receives a
bounded handoff injected through that harness's context-injection contract. The pitch is
continuity across harness switches: "quit Claude Code mid-task, start Codex in the same
directory, continue without re-explaining."

## The distinguishing bet

Three, all now source-verified rather than README-claimed:

1. **Memory belongs to the project, not the harness.** Cross-harness continuity as the
   point, against every harness's native session persistence. The mechanism is real: one
   server, per-harness capture adapters, and per-harness injection envelopes
   (`hookSpecificOutput.additionalContext` for Claude Code, `ephemeralMessage` for
   OpenCode — `crates/ai-memory-cli/src/commands/hook.rs:387`).
2. **Plain markdown in git beats a vector store.** The wiki is the only source of truth;
   all 49 SQL files are migrations for the derived index
   (`crates/ai-memory-store/migrations/`). Vectors are an optional add-on stream inside
   RRF retrieval, not the substrate. mem0 wagers the opposite.
3. **Zero-LLM default.** Carved as cross-cutting invariant 13 in `docs/ARCHITECTURE.md`:
   capture, rule-based session pages, handoffs, FTS5 retrieval, and decay all work with
   no provider configured. LLM is strictly additive (consolidation, auto-improvement,
   rerank, prose briefings). None of the other six seeds in the kind makes this bet —
   mem0/cognee/memori put an LLM in the extraction path itself.

## Main features

- **Lifecycle-hook capture** into a closed 10-value `ObservationKind` vocabulary
  (session-start, user-prompt, pre/post-tool-use, pre-compact, post-compaction,
  notification, stop, session-end, other). Unknown harness events collapse to `other` —
  the enum does not grow per vendor.
- **Rule-based session pages** (no LLM): `sessions/<id>.md` from deterministic
  heuristics. Opt-in LLM consolidation rewrites them into `concepts/`, `decisions/`,
  `gotchas/` pages with wikilinks.
- **Automatic cross-agent handoffs** opened at session end, delivered once at the next
  session start (cwd-matched, newer expires older).
- **Autonomous learning loop** (the issue-#13 feature): scheduled background LLM review
  of completed sessions, staging and auto-approving wiki edits. Detail under
  Architecture.
- **Hybrid retrieval** via 18 MCP tools: FTS5 + lexical entity index + link-neighbor
  graph, fused by RRF, optional vector stream and optional LLM reranker; memory tiers
  (working/episodic/semantic/procedural) with an exponential-decay retention formula and
  a forget sweep.
- **Per-harness installers** (`install-hooks --apply`) that mutate each harness's own
  config (for Claude Code: `~/.claude/settings.json` in place, merging around
  third-party hooks).

Table stakes in the kind: store + retrieve + MCP. Distinctive: the hook-capture breadth,
the zero-LLM path, git-versioned markdown as substrate, and the auto-approving learning
loop.

## Stack & repo shape

Rust workspace, ten crates with a one-line dependency discipline (no circular deps,
enforced boundaries): `core` (domain types, no IO), `store` (SQLite, single-writer
actor), `wiki` (atomic markdown writes + git2 + file watcher), `mcp`, `hooks` (payload
schemas, sanitizer, `/hook` ingress), `llm` (provider trait boundary), `consolidate`
(ingest/lint/sweep/auto-improve), `workstream`, `web`, `cli`. The stub's "4 crates" was
wrong — corrected here. 84 `.sh` + 77 `.ps1` are per-harness hook scripts and installers;
`docs/` carries an unusually complete `ARCHITECTURE.md` (619 lines) plus per-competitor
research notes. 1,276 commits in ~3 months by a known solo author, with in-repo
`CLAUDE.md`/`AGENTS.md` and a merge-PR-from-own-branch pattern — the repo itself is
visibly agent-built.

## Architecture

### Entry point → one full trace (Claude Code, default local install)

1. **Install**: `ai-memory install-hooks --apply --agent claude-code` →
   `apply_to_claude_code_settings` (`crates/ai-memory-cli/src/commands/install_hooks.rs:1195`)
   stages the script bundle and rewrites `~/.claude/settings.json`, registering nine
   events (`CLAUDE_CODE_EVENTS`, `crates/ai-memory-cli/src/commands/render_shared.rs:36`):
   SessionStart, UserPromptSubmit, Pre/PostToolUse, PreCompact, Stop, SessionEnd,
   SubagentStart/Stop. On local installs the registered command is the **native binary**
   (`ai-memory hook --event … --agent claude-code`), not the shell scripts — 
   `HookCommandPlatform::current()` defaults to `PosixNative`
   (`render_shared.rs:1060`); the `.sh` bundle is the fallback for docker/setup-agent
   contexts where only scripts are copied.
2. **Capture**: each lifecycle event runs the hook command with JSON on stdin. The
   native command spools the event locally with a minted idempotency key, never blocks
   the agent (bounded timeouts, incremental drain only on post-tool-use backlog —
   `commands/hook.rs:118`), and hands session-end delivery to a detached `hook-drain`
   helper. The script path is a fire-and-forget `curl` to
   `POST /hook?event=…&agent=claude-code` (`hooks/claude-code/session-end.sh`), with a
   POSIX-only `_lib.sh` that walks up from cwd for a `.ai-memory.toml` marker (bounded
   at `$HOME` or the git root) to route the event to the right workspace/project.
3. **Ingest**: the server's hook router sanitizes the payload — the typed
   `Sanitized<NewObservation>` boundary whose only constructor is `sanitize()`
   (`crates/ai-memory-core/src/sanitize.rs`, ordered regex redaction with an allowlist)
   — assigns an `ObservationKind`, and enqueues to the single-writer SQLite actor.
   Content caps are enforced client-side *and* re-applied server-side (16 KiB prompts,
   2 KB tool excerpts).
4. **Session end**: one SQLite transaction inserts the automatic handoff, stamps the
   session ended, and records the covered-observation count. The wiki gets a rule-based
   `sessions/<id>.md` (`crates/ai-memory-hooks/src/synth.rs:25` — title from first user
   prompt, tool counts, 500-line head/tail body cap, tier episodic) and an auto-commit.
   With a provider configured, a durable `session_consolidation_jobs` row queues the LLM
   rewrite; provider failure degrades back to the rule-based page, policy failure fails
   closed (`router.rs`, `checkpoint_degrades_to_synth`).
5. **Next session start** (any supported harness, same project): the hook fetches
   `GET /handoff?agent=…` synchronously and emits it in the harness's injection
   envelope — for Claude Code, `hookSpecificOutput.additionalContext`
   (`hooks/claude-code/session-start.sh`; native path `commands/hook.rs:387`). Delivery
   is single-use and claimed transactionally.

### The agent loop (analog: capture → consolidate → learn)

ai-memory has no agent loop of its own; its runtime analog is the pipeline above plus
the **auto-improvement loop**, and that loop is the load-bearing finding for issue #13:

- `crates/ai-memory-consolidate/src/auto_improve_schedule.rs`: the server-side scheduler
  ticks non-overlapping every `interval_secs` (default 3600), claims newly completed
  sessions at-most-once per session (per-scope watermark seeded at startup so history is
  never retro-processed), runs an LLM review over a deterministic bounded observation
  projection (`projection.rs` — recency-scored + even-sampled, budget-capped), and
  stages proposals targeting `concepts/`, `decisions/`, `gotchas/`, `procedures/`, and
  `_rules/`.
- Proposals carry immutable target snapshots and append-only decision events
  (`auto_improve_proposals` table), pass `min_confidence` (default 0.75) and a stack of
  size budgets, and are then **auto-approved through the normal wiki write path by
  default** — `[auto_improve] require_approval = false`. An optional executable eval
  gate (`[auto_improve.eval]`, default off) can be interposed for `_rules/` and
  `procedures/` proposals.
- Mechanism classification for the `learning_loop` vocabulary: **background** —
  server-side scheduled fork, entirely outside any harness process. Same family as
  hermes and codex, but harness-independent like ECC's instinct pipeline. Default-on
  once a provider is configured (bolder than codex's built-but-off; matches hermes'
  posture). `docs/auto-improvement-loop.md` names Hermes Agent as the inspiration
  explicitly.

Every LLM prompt in the pipeline treats observations, wiki pages, and prior proposals as
untrusted data with explicit trust delimiters — the same boundary precedes injected
handoffs.

### Context assembly

What the next session actually receives is narrower than the pitch suggests:

- **The automatic handoff is heuristic, not LLM-written.** `build_auto_handoff`
  (`crates/ai-memory-hooks/src/router.rs:2861`): summary = first user prompt + last user
  prompt, each capped at 1,500 chars; open questions = "Continue from: <last prompt>";
  next steps = a sorted list of tool names used; `files_touched` is left empty. That
  paragraph — not the wiki — is the session-to-session baton.
- The richer memory (compiled concepts/decisions/gotchas, briefings, slots) enters only
  when the agent *pulls* it via MCP tools, or via the opt-in
  `[briefing] inject_on_session_start` compiled project brief.
- Retrieval (`memory_query`) fuses four RRF streams — FTS5, entity index, link
  neighbors, optional vectors — then applies a bounded authority multiplier favoring
  rules/decisions/procedures/gotchas; raw observation FTS is the bounded fallback when
  compiled pages miss.

### Tool surface & permissions

18 MCP tools (read-only vs destructive hints declared per tool), grown from a documented
"narrow on purpose" cut of 10 — each addition argued in `docs/ARCHITECTURE.md` against
§10 of `design-decisions.md`. Capture and injection ride hooks; explicit read/write
rides MCP; the two never mix transports. Server binds localhost by default; multi-user
deployments get bearer auth, per-operator handoff ownership, and per-user slot
namespaces framed explicitly as a prompt-injection boundary, not access control.

### Category boundaries in the code

- **Model provider**: swappable behind `LlmProvider`/`Embedder` traits
  (`ai-memory-llm`), seven providers incl. openai-compat for local engines; provider
  auth resolves before construction (invariant 14). The system runs with none.
- **Harness boundary**: per-harness event tables + installer functions in
  `render_shared.rs`/`install_hooks.rs`, normalized into the closed `ObservationKind`
  enum at ingress. Third parties get an `extension=<namespace>` seam on `/hook`, not a
  plugin system.
- **Environment**: none — it is a host-local daemon; the docker packaging is for the
  server itself, not for agent execution.

## Bleed

Reaches category 2 (harness) twice: capture rides each harness's hook surface, and
injection rides each harness's context-injection contract — both catalogued per-harness
in source. The managed-workstream mode (`ai-memory run`, docs-read only) goes further and
*launches* harnesses, importing their native transcripts; that is category-2 orchestration
growing inside a category-5 tool, the same direction of travel as ECC's `ecc2`. The 15
cross-cutting invariants each cite a specific competitor bug (cognee #2717, agentmemory
#456/#469, basic-memory #763/#783…) — the vendor read its rivals' issue trackers and
wrote the findings into `docs/issues-*.md`; directly useful when this arc reaches cognee.

## Cost model

MIT, self-hosted, no commercial ring visible at the pin. Zero marginal cost in the
default path; configuring a provider makes consolidation + auto-improvement +
rerank metered per-token on your own key. That shape means the learning loop's
depth scales with willingness to pay inference — the default-on scheduler at 3600s ticks
with `max_sessions_per_tick = 1` is sized to stay cheap.

## Surprises

1. **The continuity baton is thin.** The automatic handoff — the headline feature — is
   first prompt + last prompt + tool names, no LLM, no files. Expected a compiled
   summary; got a heuristic paragraph. The wiki is rich, but the agent must pull it.
2. **The learning loop auto-approves its own edits by default.** `require_approval =
   false` on a loop that writes `_rules/` — pages that then steer future sessions.
   Guardrails are budgets, confidence floors, audit rows, and prompt-level trust
   delimiters, not human review.
3. **Competitor archaeology as engineering method.** Fifteen invariants, each pinned to
   a named bug in a rival memory tool, with per-rival research docs in-repo. The most
   systematic prior-art discipline seen in the study so far — in a solo-author repo.
4. **The hook-fragmentation surface is the real product.** `install_hooks.rs` alone is
   7,801 lines. Per-harness quirks are encoded as code and comments: Kimi Code discards
   SessionStart stdout (the brief rides the first user prompt instead —
   `commands/hook.rs:160`) and fires PostToolUse only on success (separate
   `PostToolUseFailure`); Codex and Antigravity lack a true session end (explicit
   `ai-memory finalize-session`); Antigravity has no SessionStart (PreInvocation
   `invocationNum == 0` mapped instead); Devin ships PostCompaction instead of
   PreCompact; Zero execs commands with no shell; Claude Code logs a warning unless hook
   stdout starts with `{`. This is the standards-scoreboard row made concrete.
5. **A session-aware MCP bridge exists for Claude Code** (`mcp-bridge`) solely to smuggle
   `CLAUDE_CODE_SESSION_ID` into an HTTP header — identity plumbing MCP itself doesn't
   carry.

## Open questions

- Does the thin heuristic handoff actually sustain "continue without re-explaining" in
  practice, or does real continuity depend on the agent proactively querying the wiki?
  Testable on the rig: capture a session, switch harness, diff what the second agent
  knows. (Bears on the kind's central question — what the extension buys over native
  loops.)
- What do auto-approved `_rules/` pages look like after weeks of real use — convergent
  standing instructions or drift? The `page_feedback`/lint loop is the built-in check;
  no external account of it yet.
- The managed-workstream loop (`ai-memory run`) was read at docs level only — it claims
  transcript import and cross-harness event ledgers, which would make this a category-2
  orchestrator. Verify in source if the arc's cross-harness question stays live.
- `docs/llm-provider-comparison.md` and `evals/` exist in-repo — does the vendor's own
  eval say anything falsifiable about consolidation quality?

## Run probe — 2026-08-19 (exp-04; docs/source/run now all three views — rule 8)

The deep-dive's central caveat, measured: **the baton buys nothing for mid-session
facts (0/10, even with injection explicitly enabled), and pull recovers everything
(10/10 verbatim, cross-harness = same-harness)** — continuity is real and entirely
pull-shaped ([exp-04](../../experiments/04-memory-continuity/README.md), conclusion 14).
Mechanics observed live: each headless `-p` turn is its own session; zero-LLM pages
store ~80-char prompt prefixes; full text survives only in `observations_fts` (which
is what pull reaches); the served briefing carries the untrusted-data boundary this
report's trust cell claims. One interop scar: v1.28.1's `memory_read_page` schema
(top-level `oneOf`) is rejected by the Anthropic API — fixed at this report's pin by
`strip_root_combinators`, which ships **default-off**.
