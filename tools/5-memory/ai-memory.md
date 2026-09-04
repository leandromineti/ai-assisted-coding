---
# PIN MOVED acd9c0b → 7e787c9 (= tag v2.0.2) at the 2026-09-04 release re-read (rule 4b:
# a pin moves only with a re-read; this was one — three-tract release variant, every claim
# below confronted at the new pin). exp-04 artifacts keep their own pin (acd9c0b / the
# v1.28.1 release binary, as its log records).
name: ai-memory
category: 5
type: memory
maker: Fabio Akita (akitaonrails)
url: https://github.com/akitaonrails/ai-memory
license: MIT
access: open-source
stack: [Rust]
version: v2.0.2
commit: 7e787c9
first_commit: 2026-05-21
stars: 5712
stars_at: 2026-09-04
read_at: 2026-09-04   # v2.0.2 release re-read; deep-dive 2026-08-18 @ acd9c0b, same day as the stub
depth: deep-dive   # capture→consolidate→handoff traced in source (hooks/, ai-memory-hooks, ai-memory-consolidate); Claude Code installer read end-to-end (install_hooks.rs + render_shared.rs + commands/hook.rs); MCP tool surface read at router + ARCHITECTURE level; re-read at v2.0.2 with per-claim confrontation + release-binary run probe. NOT traced: the managed-workstream loop (`ai-memory run`, docs-level only), the web frontend, the retrieval RRF internals beyond the store's table shapes, and the new local-embeddings inference internals (candle/BERT read at config/fetch level only)
harness_targets: "23 harness targets at v2.0.2, counted from docs/support-matrix.md (moved out of the README this window) as rows naming an agent, excluding the 4 OS-platform rows, the Managed-workstreams capability row, and the 2 provider rows: 16 Supported with MCP + lifecycle hooks (adds ZCode), 4 MCP-only (Claude Desktop, VS Code Copilot, Zed, Swival), 1 Managed-only (Crush), 1 Hooks-only (Pool — new status class: capture works, no first-party MCP client, injection not demonstrated), 1 community (Hermes). Same rule at acd9c0b gives 21; the old '~24' conflated the OS-platform rows with targets and omitted Crush (corrected 2026-09-04). Claude Code verified in source, others spot-checked at the event-table level in render_shared.rs"
harness_features:
  learning_loop: true   # SOURCE-TRACED 2026-08-18, defaults RE-VERIFIED at 7e787c9 2026-09-04: background, harness-independent — server-side scheduler (auto_improve_schedule.rs) reviews completed sessions via LLM, stages proposals, AUTO-APPROVES wiki edits by default (require_approval=false, config.rs:812); plus a durable session-end LLM consolidation queue, plus (new in 2.0, opt-in: experience_every_sessions=0) a cross-session "experience" pass on the same auto-approving staging path. Zero-LLM install has no loop; with a provider configured the loop is default-ON. Second verified harness-independent instance after ECC
memory_features:   # ADR-0013 block, set 2026-08-19 from the deep-dive read at acd9c0b; every cell re-verified at 7e787c9 (2026-09-04 release re-read, tract B: all HOLDS)
  memory_store: files-git        # git-versioned markdown wiki is the source of truth; SQLite/vectors are derived indexes (body: store section) — the type's only files-git wager. Since 2.0 the pages are natively OKF v0.2-shaped (Google Cloud's Open Knowledge Format) — page schema, not substrate: bodies, ids, git history untouched by the backup-gated migration
  capture_path: hook             # harness lifecycle hooks → closed 10-value ObservationKind (re-verified at 7e787c9: observation.rs:19-40, still 10, still closed) → rule-based session pages, no LLM on the default path
  write_admission: evidence-gated  # MEASURED (exp-04 arm C, 2026-08-19): the auto-improve reviewer rejected all 12 conversational-fact candidates — "Offline decision acknowledged but not made or refined in session; no implementation evidence" — say-so does not earn autonomous storage; the explicit write-page path remains available for deliberate recording. Structural gate unchanged at v2.0.2 (evidence-quote requirement + reject-say-so prompt, auto_improve.rs)
  recall_injection: both         # auto: thin cwd-matched handoff baton injected via per-harness envelopes; rich wiki is pull-only via 18 MCP tools (run-verified 2026-09-04: 18 served)
  memory_scope: [project, user]  # .ai-memory.toml walk-up for project scoping; per-user slot namespaces. Since v1.39.0 the active-project default flipped single → per_actor, and 2.0 refuses unscoped MCP writes whose project pointer doesn't resolve rather than misfiling them into the server default (#564, outside-contributor PR)
  memory_tiers: true             # working/episodic/semantic/procedural
  hybrid_retrieval: true         # RRF over FTS5 + entity index + link neighbors + vectors, optional reranker. Since 2.0 DEFAULT-ON: an unconfigured install background-fetches an in-process 384-dim MiniLM embedder (~87 MB from huggingface.co, run-observed 2026-09-04) and enables hybrid on the next start; opt out embedding_provider="none". Vendor's own LongMemEval-S: hit@5 0.617 FTS-only → 0.823 with it
  memory_revision: auto          # background consolidation auto-approves its own wiki edits by default (require_approval=false, re-verified at 7e787c9 config.rs:812); rules/procedures go through proposals — mixed, but the default write path is auto
  decay: true                    # exponential-decay retention + forget sweep (formula gained a breadth_weight factor in the window)
  injection_trust_boundary: true # untrusted-data delimiters on observations, wiki pages, proposals, AND injected handoffs (re-verified at 7e787c9: router.rs:1537-1585)
  deployment_mode: self-host     # localhost-bound daemon, regex sanitizer at ingress, zero-LLM default — but since 2.0 no longer zero-egress by default (the background embedder fetch above); 2.0 also added password web sessions + separated API credentials, a first step toward multi-user server posture
  harness_installer: true        # install-hooks --apply mutates ~/.claude/settings.json (9 CC events, re-verified at render_shared.rs:36)
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
   Antigravity CLI — `crates/ai-memory-cli/src/commands/hook.rs:436-447`; OpenCode
   injects via its generated TS plugin's `system.push`, `install_hooks.rs:3319`).
   *(Correction 2026-09-04: the deep-dive attributed `ephemeralMessage` to OpenCode; at
   the cited line it was Antigravity at both pins — an attribution slip, the same file's
   Surprise 4 had it right.)*
2. **Plain markdown in git beats a vector store.** The wiki is the only source of truth;
   all 58 SQL files are migrations for the derived index
   (`git ls-files '*.sql'` = the migrations dir; 49 at the old pin). Vectors are an
   add-on stream inside RRF retrieval, not the substrate. mem0 wagers the opposite.
   Since 2.0 the wager has external validation: the on-disk pages are natively
   conformant to Google Cloud's Open Knowledge Format v0.2 (published 2026-06-12, three
   weeks after this repo's first commit) — "the wiki files *are* the OKF files — no
   export step forks the truth" (`docs/okf.md:27-31`), with a backup-gated in-place
   migration that touches frontmatter only.
3. **Zero-LLM default.** Carved as cross-cutting invariant 13 in `docs/ARCHITECTURE.md`
   (byte-identical at both pins): capture, rule-based session pages, handoffs, retrieval,
   and decay all work with no provider configured. LLM is strictly additive
   (consolidation, auto-improvement, rerank, prose briefings). None of the other six
   seeds in the type makes this bet — mem0/cognee/memori put an LLM in the extraction
   path itself. **Qualifier since 2.0** (2026-09-04): the invariant survives on its
   letter — an embedder is not an `LlmProvider`, nothing generative runs — but a default
   install is no longer FTS-only or egress-free: it background-fetches an ~87 MB MiniLM
   model from huggingface.co (run-observed) and turns hybrid retrieval on at the next
   start; hosts that can't fetch degrade to the pre-2.0 FTS-only behaviour with a warning.

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

Rust workspace, ten shipped crates with a one-line dependency discipline (declared at
`docs/ARCHITECTURE.md:361-363` and `AGENTS.md:193-195`, not CI-enforced): `core` (domain
types, no IO), `store` (SQLite, single-writer actor), `wiki` (atomic markdown writes +
git2 + file watcher), `mcp`, `hooks` (payload schemas, sanitizer, `/hook` ingress),
`llm` (provider trait boundary), `consolidate` (ingest/lint/sweep/auto-improve),
`workstream`, `web`, `cli` — plus `evals/` as an eleventh workspace member (the
benchmark harness, explicitly not part of the shipped binary) and
`companions/ai-memory-importer`, a deliberately workspace-isolated crate that replays
external corpora (OMC wikis, generic conversation exports) through the public hook
pipeline — a migrate-your-memory-in path. The stub's "4 crates" was wrong — corrected
at the deep-dive. 92 `.sh` + 82 `.ps1` (`git ls-files`; 84/77 at the old pin) are
per-harness hook scripts and installers; `docs/` carries an unusually complete
`ARCHITECTURE.md` (692 lines; its own crate-layout block lists 9, omitting `web` —
upstream doc staleness, not a miscount here) plus per-competitor research notes.

1,580 commits in ~3.5 months (1,276 at the old pin), **single-maintainer-led but not
solo** *(correction 2026-09-04: the deep-dive's "known solo author" was wrong at its own
pin — `git shortlog` showed 54 distinct authors at acd9c0b, 82 at v2.0.2; Akita is 64%
of non-merge commits and the sole merge gatekeeper, and 67 of the 132 PRs merged in the
re-read window came from 34 outside contributors)*. The repo is visibly — now provably —
agent-built: 123 of the 304 window commits (40%) carry `Co-Authored-By: Claude <model>`
trailers naming specific models, `CLAUDE.md` is a 7-line redirect to a 446-line
`AGENTS.md`, and that `AGENTS.md` opens with ai-memory's own `<!-- ai-memory:start -->`
managed block — the project dogfoods its own installer on its own repo. The
merge-PR-from-own-branch pattern persists alongside genuine outside merges.

## Architecture

### Entry point → one full trace (Claude Code, default local install)

1. **Install**: `ai-memory install-hooks --apply --agent claude-code` →
   `apply_to_claude_code_settings` (`crates/ai-memory-cli/src/commands/install_hooks.rs:1442`)
   stages the script bundle and rewrites `~/.claude/settings.json`, registering nine
   events (`CLAUDE_CODE_EVENTS`, `crates/ai-memory-cli/src/commands/render_shared.rs:36`):
   SessionStart, UserPromptSubmit, Pre/PostToolUse, PreCompact, Stop, SessionEnd,
   SubagentStart/Stop. On local installs the registered command is the **native binary**
   (`ai-memory hook --event … --agent claude-code`), not the shell scripts — 
   `HookCommandPlatform::current()` defaults to `PosixNative`
   (`render_shared.rs:1262`); the `.sh` bundle is the fallback for docker/setup-agent
   contexts where only scripts are copied.
2. **Capture**: each lifecycle event runs the hook command with JSON on stdin. The
   native command spools the event locally with a minted idempotency key, never blocks
   the agent (bounded timeouts, incremental drain only on post-tool-use backlog —
   `commands/hook.rs:119`), and hands session-end delivery to a detached `hook-drain`
   helper. The script path is a fire-and-forget `curl` to
   `POST /hook?event=…&agent=claude-code` (`hooks/claude-code/session-end.sh`), with a
   POSIX-only `_lib.sh` that walks up from cwd for a `.ai-memory.toml` marker (bounded
   at `$HOME` or the git root) to route the event to the right workspace/project.
3. **Ingest**: the server's hook router sanitizes the payload — the typed
   `Sanitized<NewObservation>` boundary whose only constructor is `Sanitized::new`
   (`crates/ai-memory-core/src/sanitize.rs:265`, ordered regex redaction with an
   allowlist; the vendor's own invariant 6 calls the constructor `sanitize()`, a name
   that exists at neither pin — the deep-dive copied the doc's wording unchecked,
   corrected 2026-09-04) — assigns an `ObservationKind`, and enqueues to the
   single-writer SQLite actor. Content caps are enforced client-side *and* re-applied
   server-side (16 KiB prompts, 2 KB tool excerpts).
4. **Session end**: one SQLite transaction inserts the automatic handoff, stamps the
   session ended, and records the covered-observation count. The wiki gets a rule-based
   `sessions/<id>.md` (`crates/ai-memory-hooks/src/synth.rs:29` — title from first user
   prompt, tool counts, 500-line head/tail body cap, tier episodic; since 2.0 its
   frontmatter carries the OKF keys, run-observed: `type`, `sources`,
   `generated: {by: process:ai-memory/2.0.2, at: …}`) and an auto-commit.
   With a provider configured, a durable `session_consolidation_jobs` row queues the LLM
   rewrite; provider failure degrades back to the rule-based page, policy failure fails
   closed (`router.rs`, `checkpoint_degrades_to_synth`, now at `router.rs:3159`).
5. **Next session start** (any supported harness, same project): the hook fetches
   `GET /handoff?agent=…` synchronously and emits it in the harness's injection
   envelope — for Claude Code, `hookSpecificOutput.additionalContext`
   (`hooks/claude-code/session-start.sh`; native path `commands/hook.rs:436`). Delivery
   is single-use and claimed transactionally (a managed-workstream `managed_run` param
   added in the window bypasses, and never consumes, the legacy single-use handoff).

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
  (`crates/ai-memory-hooks/src/router.rs:2909`): summary = first user prompt + last user
  prompt, each capped at 1,500 chars; next steps = a sorted list of tool names used;
  `files_touched` is left empty. That paragraph — not the wiki — is the
  session-to-session baton. One field grew in the window: `open_questions` went from a
  blind "Continue from: <last prompt>" to a 4-branch zero-LLM heuristic
  (`derive_open_questions`, `router.rs:3009` — unresolved-question / abnormal mid-file
  exit / mid-task exit / normal end, with a 26-phrase acknowledgment filter) — shipped
  2026-08-19, **the day after the deep-dive pin and the day exp-04 ran**. Scored as a
  prediction: the implicit "the baton is thin and will stay thin" held on summary,
  next_steps, and files_touched, and was falsified within 24 h on open_questions.
  Nothing in the change reaches mid-session facts, so exp-04's 0/10-injection /
  10/10-pull result is not disturbed.
- The richer memory (compiled concepts/decisions/gotchas, briefings, slots) enters only
  when the agent *pulls* it via MCP tools, or via the opt-in
  `[briefing] inject_on_session_start` compiled project brief.
- Retrieval (`memory_query`) fuses four RRF streams — FTS5, entity index, link
  neighbors, optional vectors — then applies a bounded authority multiplier favoring
  rules/decisions/procedures/gotchas; raw observation FTS is the bounded fallback when
  compiled pages miss.

### Tool surface & permissions

18 MCP tools (read-only vs destructive hints declared per tool; run-verified 2026-09-04:
18 served), grown from a documented "narrow on purpose" cut of **8** — each addition
argued in `docs/ARCHITECTURE.md` against §10 of `design-decisions.md`
*(correction 2026-09-04: the deep-dive wrote "cut of 10"; 10 is the number of tools
ARCHITECTURE.md names as post-dating the cut, so the original cut was 18 − 10 = 8 —
true at both pins)*. Capture and injection ride hooks; explicit read/write
rides MCP; the two never mix transports. Server binds localhost by default; multi-user
deployments get bearer auth, per-operator handoff ownership, and per-user slot
namespaces framed explicitly as a prompt-injection boundary, not access control.

### Category boundaries in the code

- **Model provider**: swappable behind `LlmProvider`/`Embedder` traits
  (`ai-memory-llm`), eight `ProviderChoice` variants incl. openai-compat for local
  engines *(correction 2026-09-04: the deep-dive's "seven" reproduced only the README's
  folded list; `factory.rs:25-42` has 8 at both pins — Anthropic, OpenAI, Gemini,
  OpenAI-compat, OpenAI-OAuth, Copilot, Anthropic-OAuth, OpenCode)*; provider auth
  resolves before construction (invariant 14). The system runs with none. New in 2.0:
  `llm_reasoning_effort`, a 9-value typed enum each chat provider maps to its native
  wire field (`types.rs:145-181`) — category-1 wire-behavior vocabulary independently
  rebuilt inside a category-5 tool.
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
growing inside a category-5 tool, the same direction of travel as ECC's `ecc2` — and it
kept growing in the window (interactive `resume` picker, `rename-workstream`). Of the 15
cross-cutting invariants, **10 cite a specific competitor bug** (cognee #2717, agentmemory
#456/#469, basic-memory #763/#578…) — the vendor read its rivals' issue trackers and
wrote the findings into `docs/issues-*.md`; directly useful when this arc reaches cognee
*(correction 2026-09-04: the deep-dive wrote "each cite", echoing the section's own
"Each comes from a documented prior-art bug" header; recounted at both pins, invariants
10/13/14 cite nothing and 6 cites an internal doc)*. The archaeology grew a sequel in
the window: `docs/research-2026-landscape.md` (232 lines) surveys ten systems the
original notes never covered — Zep/Graphiti, Letta/MemGPT, MemOS, Mem0, MIRIX and
friends — and self-places ai-memory in a "file-first wiki memory" camp.

## Cost model

MIT, self-hosted, no commercial ring visible at either pin (re-checked 2026-09-04: no
pricing, sponsors file, or homepage; every "subscription/enterprise" hit in docs refers
to third-party LLM backends the operator supplies). Zero marginal cost in the default
path — since 2.0 that includes hybrid retrieval, because the default embedder is
in-process and keyless; configuring a provider makes consolidation + auto-improvement +
rerank metered per-token on your own key. That shape means the learning loop's
depth scales with willingness to pay inference — the default-on scheduler at 3600s ticks
with `max_sessions_per_tick = 1` is sized to stay cheap.

## Surprises

1. **The continuity baton is thin.** The automatic handoff — the headline feature — is
   first prompt + last prompt + tool names, no LLM, no files. Expected a compiled
   summary; got a heuristic paragraph. The wiki is rich, but the agent must pull it.
   *(2026-09-04: still true at v2.0.2 minus one field — `open_questions` grew a 4-branch
   heuristic the day after this was written; see Context assembly.)*
2. **The learning loop auto-approves its own edits by default.** `require_approval =
   false` on a loop that writes `_rules/` — pages that then steer future sessions.
   Guardrails are budgets, confidence floors, audit rows, and prompt-level trust
   delimiters, not human review.
3. **Competitor archaeology as engineering method.** Ten of fifteen invariants pinned to
   a named bug in a rival memory tool, with per-rival research docs in-repo. The most
   systematic prior-art discipline seen in the study so far. *(Corrected 2026-09-04:
   originally "each pinned … in a solo-author repo" — both halves were overclaims at
   the original pin; see Bleed and Stack & repo shape.)*
4. **The hook-fragmentation surface is the real product.** `install_hooks.rs` alone is
   7,801 lines *(9,875 at v2.0.2 — +2,074 in 16 days for two new harness targets)*. Per-harness quirks are encoded as code and comments: Kimi Code discards
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

- ~~Does the thin heuristic handoff actually sustain "continue without re-explaining" in
  practice, or does real continuity depend on the agent proactively querying the wiki?~~
  **Answered 2026-08-19 (exp-04)**: continuity is real and entirely pull-shaped — see
  the run-probe section below.
- What do auto-approved `_rules/` pages look like after weeks of real use — convergent
  standing instructions or drift? The `page_feedback`/lint loop is the built-in check;
  no external account of it yet. **Raised stakes since 2.0**: the opt-in experience pass
  extends the same auto-approving path from single-session evidence to cross-session
  abstraction, and the one interposable eval gate is still default-off.
- The managed-workstream loop (`ai-memory run`) was read at docs level only — it claims
  transcript import and cross-harness event ledgers, which would make this a category-2
  orchestrator. Verify in source if the arc's cross-harness question stays live. (Grew
  in the window: `resume` picker, `rename-workstream`, a handoff-bypassing
  `managed_run` delivery path — still untraced.)
- ~~`docs/llm-provider-comparison.md` and `evals/` exist in-repo — does the vendor's own
  eval say anything falsifiable about consolidation quality?~~ **Answered 2026-09-04, at
  v2.0.2, emphatically yes** — for *retrieval*: `docs/benchmarks/` publishes dated,
  provenance-stamped LongMemEval-S runs from the in-repo `evals/` harness (commit sha,
  dataset sha256, hardware, 7-slice × 8-metric breakdowns): overall hit@5 **0.823**
  with the 2.0 local-embeddings default, 0.668 stopword-filtered FTS, 0.617 pre-2.0
  FTS-only — and it prints a competitor *beating* it (agentmemory 0.967 R@5), attributes
  6.6 points of its own gain to fixing its own pooling bug, and names the 2 KB privacy
  excerpt bound as a deliberate self-handicap ("the benchmark measures the shipped
  system, not an idealised retriever"). The 30 abstention questions are excluded with a
  documented reason but the promised separate abstention report doesn't exist yet; the
  CHANGELOG still carries a stale 0.779 from a superseded run. Consolidation *quality*
  (the original question's target) remains measured only by the `ab` A/B harness — no
  published numbers for it.

## Run probe — 2026-08-19 (exp-04; docs/source/run now all three views — rule 8)

The deep-dive's central caveat, measured: **the baton buys nothing for mid-session
facts (0/10, even with injection explicitly enabled), and pull recovers everything
(10/10 verbatim, cross-harness = same-harness)** — continuity is real and entirely
pull-shaped ([exp-04](../../experiments/04-memory-continuity/README.md), conclusion 14).
Mechanics observed live: each headless `-p` turn is its own session; zero-LLM pages
store ~80-char prompt prefixes; full text survives only in `observations_fts` (which
is what pull reaches); the served briefing carries the untrusted-data boundary this
report's trust cell claims. One interop scar: v1.28.1's `memory_read_page` schema
(top-level `oneOf`) is rejected by the Anthropic API — fixed at that pin (acd9c0b) by
`strip_root_combinators`, which shipped **default-off**. *(2026-09-04: fixed
unconditionally at v2.0.2 — the struct-level `anyOf` was removed at the source (#577)
and a fence test walks every tool schema for root combinators; the strip flag still
exists, still default-off, only for other dialects. Run-verified below: 18 served
schemas, zero root combinators, no flag.)*

## Release assessment — v2.0.2 (2026-09-04; pin acd9c0b → 7e787c9)

*Method: the release-re-read variant of the three-tract pattern — release substance,
per-claim confrontation of every citation above against the v2.0.2 tree
(HOLDS/MOVED/CHANGED/GONE/NEVER-REPRODUCED), provenance re-measurement — with
load-bearing findings spot-verified in the main session and a same-day release-binary
run probe (below). Window: acd9c0b (2026-08-18) → 7e787c9 (= tag v2.0.2, 2026-09-03),
304 commits, clean ancestry (`merge-base --is-ancestor` checked); `main` is 24 commits
past the tag, outside this pin. Corrections to claims that were wrong at the old pin
are marked in place above; this section carries what the window itself did.*

### Character: a 2.0 that standardizes the substrate and turns on the second engine

Ship-then-patch discipline — 18 tags in the 16-day window (no rc/beta tag has ever
existed; 2.0.0 was patched twice within 25 hours, three of the patches being
OKF-migration crash-loops) — but the substance is coherent: the wiki format became
Google Cloud's OKF v0.2 natively, retrieval gained its vector stream *by default*, and
the whole thing was measured before shipping on a new in-repo LongMemEval-S harness.
Stars 2,596 → 5,712 in 17 days (2.2×); 67 of 132 merged window PRs came from 34 outside
contributors, including the #564 write-safety fix.

### What moved, ranked by what it does to this report's claims

- **Hybrid retrieval default-on** (the biggest posture change): an unconfigured install
  background-fetches an in-process MiniLM embedder (~87 MB, sha256-pinned, from
  huggingface.co — run-observed) and enables hybrid search on the next start; failure
  degrades to pre-2.0 FTS-only with a warning; explicit `local` config hard-fails
  instead (`serve.rs:1817-1887`). Invariant 13 ("zero-LLM default") survives verbatim —
  an `Embedder` is not an `LlmProvider` — but the default is no longer egress-free.
  Vendor's own measure of what it bought: hit@5 0.617 → 0.823. Doc gap at the pin: the
  support matrix's embedding-providers row doesn't list `local`.
- **OKF v0.2 native** — page-frontmatter schema + a per-project bundle index, not a
  substrate change: the backup-gated migration (whole data dir archived and verified
  first, or it refuses to run) rewrites frontmatter in place, same ids, same version
  rows, and a `NewerWikiFormat` guard refuses downgrade opens. Bet 2 comes out
  stronger: the file-first markdown store now conforms to a published third-party spec,
  and `export-okf` emits validated bundles whose import is just unpacking into the wiki.
- **The experience pass** (opt-in, `experience_every_sessions`, default 0): every N
  completed sessions, the last few session summaries are reviewed side by side and
  cross-trajectory knowledge (repeated workflows, re-stated preferences, contradictions
  with stored decisions, evidence required to span ≥2 sessions) is staged through
  literally the same `stage_and_apply` tail and `apply_eval_gate` as per-session
  auto-improve. With the shipped `require_approval = false`, "staged" means
  auto-approved — Surprise 2 extended from single-session evidence to cross-session
  abstraction, with the eval gate still default-off.
- **Temporal `as_of`** on `memory_query` (ingestion-time-only validity windows on entity
  links, honestly bounded in `docs/temporal.md`) — which **shipped non-functional in
  2.0.0**: the entity index it reads was fed only by LLM-consolidator frontmatter, so
  zero-LLM stores (the default!) got nothing back until 2.0.2 backfilled entities from
  tags. The zero-LLM default undermined the feature designed around it, and no
  invariant caught it.
- **Typed relation edges** (`causes`/`fixes`/`contradicts` in `relations:` frontmatter,
  riding the existing `links.link_type` column) with declared `contradicts` edges
  surfacing as zero-LLM `contradiction` lint findings — a knowledge-graph gesture made
  without a graph store, consistent with the substrate wager.
- **Scope hardening**: active-project default flipped `single` → `per_actor` (v1.39.0),
  then 2.0 made unscoped MCP writes with an unresolvable project pointer *refuse*
  rather than misfile into the server default — "a read answering from the default is a
  wrong answer the caller can see, a write is a misfile they cannot" (#564, an
  outside-contributor PR). A gate learning to refuse rather than guess. (Stale doc at
  the pin: `active_project.rs:22` still narrates `Single` as the default its own enum
  no longer has.)
- **Deletion grew real**: `purge-session` by UUID with a tombstone so a draining hook
  spool cannot resurrect the purged session, plus `--compact` (FTS rebuild + VACUUM)
  and an explicitly documented non-forensic boundary — the strongest forget-one-
  conversation story in the type so far.
- **Multi-user posture advanced**: password web sessions + separated API credentials
  (V54/V55), `/admin` + `/api/v1` accepting human session or machine bearer — the
  `deployment_mode: self-host` cell still holds, but the trajectory is toward a
  multi-operator server.
- Smaller: single-instance `.serve.lock`; `status` now reports migration state,
  embedding triples, typed-edge counts, and a wedged-writer gauge; a macOS launchd
  unit; `hook/batch` ingress; the importer's generic conversation-export replay.

### Scored predictions and the re-read's own audit

The deep-dive carried no numeric forecast, but two implicit predictions scored: the
baton stayed thin on three of four fields (the fourth grew a heuristic within 24 h of
the pin — recorded at Context assembly), and "the hook-fragmentation surface is the
real product" compounded at ~130 lines/day (`install_hooks.rs` 7,801 → 9,875, two new
targets, one of them — Pool — a new *hooks-only* integration class where ai-memory for
the first time declines to write the harness's config at all and prints a paste-ready
snippet instead).

The confrontation tract also audited this report at its own pin and found five claims
that never reproduced — "solo author", "invariants each cite a competitor bug",
"`ephemeralMessage` for OpenCode", "cut of 10", "seven providers" — all corrected in
place above with dated notes. Three of the five are counts stated without their
measure; every count that *did* carry an implicit measure (49 SQL, 84/77 scripts, 619
lines, 1,276 commits, 7,801 lines, 18 tools, 15 invariants, 10 ObservationKind values)
reproduced exactly. The methodology's "a count carries its measure" rule is now
0-for-5 vs 8-for-8 on this report's own record.

## Run probe — 2026-09-04 (v2.0.2 official release binary; tag = release, so probing the release probes the pin)

sha256-verified `ai-memory-linux-x86_64.tar.gz`, reports `ai-memory 2.0.2`. Four
observations, all from run:

1. **Default egress confirmed**: a first `serve` with no config logs "fetching the
   default local embedding model in the background (~87 MB, one time); hybrid search
   enables on the next start" and begins pulling `model.safetensors`.
2. **OKF is live on the zero-LLM path**: a synthetic hook session (session-start →
   user-prompt → session-end over `POST /hook`, embeddings off) produced
   `sessions/<id>.md` whose frontmatter carries `type: Session Summary`, `sources:`
   (an `ai-memory://session/…` resource with author), and
   `generated: {by: process:ai-memory/2.0.2, at: …}` — three of the four OKF keys
   observed on this page kind; no `stale_after` on a session page, and no bundle
   `index.md` appeared in this short-lived fresh store.
3. **The Anthropic-schema scar is gone without the flag**: `tools/list` over the HTTP
   MCP transport served 18 tools with **zero** root `oneOf`/`anyOf`/`allOf`, no
   `strip_root_combinators` set; the served `memory_query` schema carries `as_of`.
4. Probe mechanics for the next re-read: `serve` speaks MCP on **stdio by default** and
   exits when stdin closes — run `--transport http` for a detached probe; the HTTP MCP
   endpoint is stateless (`/mcp`, plain JSON-RPC, no session id needed).
