---
# PIN MOVED 7e787c9 → 8c39e4e67 (= tag v3.3.3) at the 2026-11-05 release re-read (rule 4b:
# a pin moves only with a re-read; this was one — three Opus tracts: release substance by
# component and the 16 cells · per-claim confrontation at both pins · velocity, tracker and
# predictions; 25 load-bearing tract claims spot-verified, 1 failed and was corrected; window
# 44 releases, first-parent counts re-derived). v3.4.0 (2026-11-04) and origin/main are
# post-pin and appear only as dated drift. exp-04's artifacts keep their own pin (acd9c0b /
# the v1.28.1 release binary, as its log records).
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
version: v3.3.3
commit: 8c39e4e67
first_commit: 2026-05-21
stars: 15119
stars_at: 2026-11-04   # gh api; 5,712 at 2026-09-04 (+154/day net)
read_at: 2026-11-05   # v3.3.3 release re-read (7e787c9 → 8c39e4e67); earlier history: v2.0.2 re-read 2026-09-04, deep-dive 2026-08-18 @ acd9c0b (same day as the stub)
depth: deep-dive   # 2026-11-05 v3.3.3 release re-read — components traced: capture (hooks/ scripts, crates/ai-memory-hooks router.rs + log.rs + recap.rs, the native hook command hook.rs, ObservationKind in core/observation.rs, the PreCompact checkpoint path), consolidation (crates/ai-memory-consolidate auto_improve.rs + auto_improve_schedule.rs + profile.rs, crates/ai-memory-wiki admission.rs, the OKF export in mcp/admin.rs), recall (build_auto_handoff, the SessionStart envelopes in hook.rs, the profile digest, the MCP tool registry against the served tools/list, retrieval defaults in config.rs and retrieval_tuning.rs), plus per-project authorization (store project_authz.rs + scope.rs) and 162 claim units confronted at both pins. Earlier reads: v2.0.2 re-read 2026-09-04, deep-dive 2026-08-18 @ acd9c0b. NOT traced: the managed-workstream loop (`ai-memory run`, docs level only), the web frontend, the RRF internals beyond defaults and table shapes, the candle/BERT inference internals, the boot-time transcript backfill internals (commands/backfill.rs, changelog level only), the profile pass in a live run (source only — the probe wrote 0 candidates), whether every web and /api/v1 read path funnels through the scope resolver (confirmed for MCP and seven web route files, not exhaustive), and the v3.4.0 compaction fix
harness_targets: "40 harness targets at v3.3.3, counted from docs/support-matrix.md at the tag as table rows naming an agent, excluding the 5 OS-platform rows (adds NixOS), the 2 capability rows (Managed workstreams, and the new `--yolo` safety + ai-jail row — a stated extension of the old rule) and the 2 provider rows: 25 Supported, 6 MCP-only, 4 MCP-only (documented: hand-written recipes not yet run end to end), 2 Hooks-only, 2 Hooks + MCP, 1 Managed-only; 39 if the Claude Desktop (Code tab) row folds into Claude Code. The same rule (helper script over `git show <rev>:docs/support-matrix.md`) gives 23 at v2.0.2 (16 Supported, 4 MCP-only, 1 Managed-only, 1 Hooks-only, 1 community) and 21 at acd9c0b; Hermes moved community to Supported. Claude Code verified in source, others spot-checked at the event-table level in render_shared.rs"
harness_features:
  learning_loop: background  # SOURCE-TRACED 2026-08-18, RE-VERIFIED at 8c39e4e67 2026-11-05 (the value holds, a qualifier does not): background, harness-independent — a server-side scheduler (auto_improve_schedule.rs) reviews completed sessions via LLM and AUTO-APPROVES wiki edits by default (require_approval: false, config.rs:1814; runs only with a provider, serve.rs:2461-2463), plus a durable session-end LLM consolidation queue, plus an opt-in cross-session experience pass (experience_every_sessions: 0, config.rs:1802). The old sentence "Zero-LLM install has no loop" is FALSE at v3.3.3: the cross-project profile pass (2.6.0) is a provider-free background writer — ProfileEnabled::Auto resolves ON when the deployment does not distinguish operators (core/profile.rs:298), and the worker is spawned on the HTTP transport (serve.rs:1559). SOURCE only: the probe never exercised it (profile_candidates 0), so nothing here is OBSERVED. default-on on a single-operator install, default-off on a multi-user one; the provider-gated loop is default-on once a provider exists. Second verified harness-independent instance after ECC  # options: background (default) | false ([profile] enabled = false with no provider configured, core/profile.rs:60-66, serve.rs:2461-2463)
memory_features:   # ADR-0013 block, set 2026-08-19 from the deep-dive read at acd9c0b; every cell re-verified at 8c39e4e67 (2026-11-05 release re-read): 16 cells (the 15 below plus learning_loop) — 9 HOLDS, 4 MOVED (the comment cites a moved location), 3 CHANGED (a comment sentence no longer holds: team_sharing, write_admission, learning_loop); no cell value changed. A config-dependent cell carries the shipped default (what a fresh install gets: no provider, no database users, HTTP transport, embedder unset) and the switch in a trailing options comment; one stated exception, write_admission, keeps the value of the provider path that exp-04 measured (evidence-gated) and names the zero-LLM fresh-install path in its options comment
  memory_store: files-git        # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: crates/ai-memory-wiki/src/lib.rs:1-5 (markdown-on-disk source of truth, write-through to the store) — the git-versioned markdown wiki is the source of truth, SQLite/vectors are derived indexes; the category's only per-write git-versioned store (OpenViking's cell also reads files-git, as plain files plus a caller-requested git snapshot service, openviking.md `memory_store`; Corrected 2026-11-05 (report-conventions audit): this first read "the type's only files-git wager"); default-on. Qualifier: the per-month event ledgers (log-YYYY-MM.md) are kept out of git (crates/ai-memory-hooks/src/log.rs:13-15), so "plain markdown in git" is true of the concept pages, not of every .md in a project directory. Since 2.0 the pages carry OKF v0.2 frontmatter — page schema, not substrate (see Re-traces, OKF)
  capture_path: hook             # MOVED, SOURCE 2026-11-05, re-verified at 8c39e4e67: harness lifecycle hooks → closed 10-value ObservationKind (crates/ai-memory-core/src/observation.rs:33-54; was :19-40 at 7e787c9, still 10, still closed) → rule-based session pages, no LLM on the default path; OBSERVED 202 queued on four runs; default-on. Adjacent routes into the same /hook ingress: boot-time transcript backfill for an empty project, default-on with opt-out AI_MEMORY_BACKFILL_ON_START=false (TESTIMONY docs/changelog/2.x.md:3338-3352), marketplace plugins, the relay companion
  write_admission: evidence-gated  # CHANGED sentence, value holds for the path it was measured on. MEASURED (exp-04 arm C, 2026-08-19, at acd9c0b): the auto-improve reviewer rejected all 12 conversational-fact candidates ("no implementation evidence"). SOURCE 2026-11-05, re-verified at 8c39e4e67: that gate is unchanged — non-empty evidence required (crates/ai-memory-consolidate/src/auto_improve.rs:2152), reject-say-so prompt (:2466) — and runs only with a provider (serve.rs:2461-2463), so it is unmounted on a zero-LLM install. The general sentence "say-so does not earn autonomous storage" FAILS: the zero-LLM cross-project profile pass admits a standing preference on ONE prompt sentence carrying an explicit marker such as "in all my projects" or "everywhere" (crates/ai-memory-consolidate/src/profile.rs:128-138, :1585-1586) or on recurrence in 2 independent projects (:1588), default-on on a single-operator install, SOURCE only (probe: 0 candidates). Admission webhooks can add a deny or mutate gate (crates/ai-memory-wiki/src/admission.rs:84-137) but the default chain is empty (crates/ai-memory-cli/src/config.rs:1476); the cell classifies the shipped gate only  # options: evidence-gated (default) | unfiltered (a fresh zero-LLM single-operator install, where the only autonomous writer is the profile pass and it admits on one marked sentence; SOURCE only); (default) here is the provider path exp-04 measured, the stated exception to the fresh-install rule in the block comment above
  recall_injection: both         # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: auto — a thin cwd-matched handoff baton (build_auto_handoff, crates/ai-memory-hooks/src/router.rs:5746), plus since 2.6 a profile digest (router.rs:3007) and a non-consuming inbox notice (:2465-2481), injected through per-harness envelopes (crates/ai-memory-cli/src/commands/hook.rs:1216-1251); pull — the wiki through 25 MCP tools (OBSERVED: 25 served, none-2.tools-list.json); default-on. After a compaction nothing is re-injected automatically at v3.3.3 (see Re-traces, compaction)
  memory_scope: [project, user]  # HOLDS (list incomplete at its own pin), SOURCE 2026-11-05, re-verified at 8c39e4e67: project — the .ai-memory.toml walk-up (hooks/_lib.sh:17-34), default-on; user — per-user slot namespaces only on a multi-user server (crates/ai-memory-mcp/src/server.rs:3865-3880), default-off on a single-operator install. Two scopes outside the key's legal list exist and are named in the candidate section, never as cell values: _global (crates/ai-memory-core/src/lib.rs:55, present at v2.0.2 too) and _profile (core/profile.rs:22-23). agent and session are absent as store axes — searched the 25 served tools/list input schemas (the only agent parameter is memory_message_pop) and memory_write_page, which refuses session_id together with scope (server.rs:4780-4785)
  memory_tiers: true             # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: crates/ai-memory-core/src/page.rs:22-31 (Working, Episodic, Semantic, Procedural); OBSERVED episodic and semantic tiers in none-2.store-dump.txt; default-on
  hybrid_retrieval: true         # HOLDS, richer, SOURCE+OBSERVED 2026-11-05, re-verified at 8c39e4e67: RRF over FTS5 + entity index + link neighbors + the observation stream (on by default since 3.0.0, crates/ai-memory-store/src/retrieval_tuning.rs:86) + vectors, optional reranker (off). DEFAULT-ON: an unconfigured install resolves embedding_provider to "local" (crates/ai-memory-cli/src/config.rs:3084-3087), background-fetches the ~87 MB MiniLM weights on first start (OBSERVED: 3 of 3 sha256 match) and embeds from the next start (OBSERVED: page_embeddings=2 on the second start, 0 on the first); opt out with embedding_provider = "none". Vendor's own LongMemEval-S: local hit@5 0.943 at 3.3.3 (docs/benchmarks/longmemeval-s-3.3.3-release.md:50, TESTIMONY)
  memory_revision: auto          # MOVED, SOURCE 2026-11-05, re-verified at 8c39e4e67: background consolidation auto-approves its own wiki edits by default (require_approval: false, crates/ai-memory-cli/src/config.rs:1814; the comment cited :812 at 7e787c9); the profile pass also supersedes by "latest ruling wins" with no approval step (crates/ai-memory-consolidate/src/profile.rs:13-15); rules and procedures go through proposals — mixed, but the default write path is auto; default-on  # options: auto (default) | proposed ([auto_improve] require_approval = true stages proposals for a human, config.rs:1684-1687, auto_improve_schedule.rs:564-568)
  decay: true                    # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: exponential-decay retention + a daily forget sweep ([maintenance] forget_sweep_interval_secs 86_400, 0 disables, crates/ai-memory-cli/src/config.rs:1936); the opt-in aging set (compact_cold_episodic, dedup_cold_clusters, config.rs:154-155) is default-off; default-on for the sweep
  injection_trust_boundary: true # MOVED, SOURCE 2026-11-05, re-verified at 8c39e4e67: untrusted-data delimiters on the injected handoff (crates/ai-memory-hooks/src/router.rs:2609-2612 recovery snapshot, :3556-3559 main handoff — "Security boundary" + UNTRUSTED_HISTORY_START), the profile digest (crates/ai-memory-core/src/profile.rs:642-645), the inbox notice (router.rs:2470) and the auto-improve prompt (auto_improve.rs:2454); the comment cited router.rs:1537-1585 at 7e787c9; default-on
  deployment_mode: self-host     # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: localhost-bound daemon (DEFAULT_BIND 127.0.0.1:49374, crates/ai-memory-cli/src/config.rs:29), regex sanitizer at ingress, zero-LLM default — not zero-egress by default (OBSERVED: the first start with the default embedder made 26 non-loopback connects). 3.0.0 changed the fresh-install posture: `ai-memory init` mints a root bearer token (crates/ai-memory-cli/src/commands/init.rs:75-81), which the probe did not exercise (it started `serve` without `init`, auth=false). No hosted offering found — searched README.md for hosted, saas, cloud, pricing, subscription: only competitor-comparison rows; default-on
  team_sharing: attribution-only # CHANGED sentence, shipped default holds. SOURCE 2026-11-05, re-verified at 8c39e4e67 (ADR-0052 posture, set 2026-09-04): a fresh install has no database users, so the per-project gate short-circuits (crates/ai-memory-store/src/project_authz.rs:210-213) and every project is `open` (V68__project_grants.sql:38-40) — one store, writes attributed, no access control; default-on. The old sentence "RBAC absent BY DESIGN ... attribution records who wrote, never gates whether" no longer holds at the project boundary: per-project access modes `open|restricted` with read/write grants shipped in 2.5.0 (project_authz.rs:58-63, :224-238), root-only administration (docs/users.md:771-774), enforced in the scope resolver (crates/ai-memory-store/src/scope.rs:413-445), the writer actor and the hook router (router.rs:4837-4851). The `open` default is SOURCE, never OBSERVED (none-2.store-dump.txt lists projects: 3 without a row dump). Per-page RBAC is still absent (docs/users.md:820-823)  # options: attribution-only (default) | acl (per-project grants — `ai-memory project access --mode restricted`, root-only, projects.access_mode V68__project_grants.sql:38-40; or [auth] new_projects_restricted = true, config.rs:1037)
  harness_installer: true        # MOVED, SOURCE 2026-11-05, re-verified at 8c39e4e67: install-hooks --apply mutates ~/.claude/settings.json (apply_to_claude_code_settings, crates/ai-memory-cli/src/commands/install_hooks.rs:2329); the event array is now 10 (CLAUDE_CODE_EVENTS, render_shared.rs:44-58; PostToolUseFailure added), the comment cited render_shared.rs:36 for 9; unmounted — nothing is installed until the operator runs `install-hooks --apply` or `ai-memory setup`
  rule_extraction: true          # HOLDS, SOURCE 2026-11-05, re-verified at 8c39e4e67: _rules/ + procedures/ proposal paths, confidence-floored, audit-logged (crates/ai-memory-consolidate/src/auto_improve.rs:2412-2420, :2466); default-off on a zero-LLM install (the auto-improve path needs a provider, serve.rs:2461-2463). The profile pass writes profile/ pages and a digest, not rules files; `ai-memory profile apply` writes a managed block into AGENTS.md/CLAUDE.md on an explicit command only (TESTIMONY docs/cross-project-profile.md:167)
  memory_import: true            # HOLDS, source family grew, SOURCE 2026-11-05, re-verified at 8c39e4e67: companions/ai-memory-importer (ADR-0051, set 2026-09-04) replays external corpora — OMC wikis, a generic conversation-export envelope and, new since 2.0.2, the rival agentmemory store (companions/ai-memory-importer/src/agentmemory/mod.rs:1-14) — through the public hook pipeline as agent=external-import sessions; unmounted (a separate workspace-isolated crate run on demand). The boot-time backfill of pre-hook harness transcripts is default-on for an empty project (TESTIMONY docs/changelog/2.x.md:3338-3352; commands/backfill.rs exists, not traced)
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

This section and the ones below describe v3.3.3 (tag, `8c39e4e67`) as current state. The
v2.0.2 text they replace survives in git history, in the verdict table
([claims confronted](#claims-confronted-at-v333)) and in the release-history rows at the
end. What is new since v2.0.2 in one paragraph: a provider-free background learner (the
cross-project profile pass, 2.6.0) so a zero-LLM install is no longer loop-free; a
per-project access model (`open`/`restricted` with grants, 2.5.0) over a store that is
otherwise still single-tenant; a served MCP surface of 25 tools where it was 18; cross-project
agent messaging; a root bearer token minted by a fresh `init` (3.0.0); and an installer that
keeps compounding (`install_hooks.rs` 9,875 → 18,351 lines). The verdicts on the old text
are in the table; the release assessment scores the old predictions.

## The distinguishing bet

Three, all source-verified rather than README-claimed — and the second is weaker at
v3.3.3 than the report said at v2.0.2:

1. **Memory belongs to the project, not the harness.** Cross-harness continuity as the
   point, against every harness's native session persistence. The mechanism is real: one
   server, per-harness capture adapters, and per-harness injection envelopes selected in
   `session_start_handoff_envelope` (`crates/ai-memory-cli/src/commands/hook.rs:1216-1239`):
   Claude Code gets `hookSpecificOutput.additionalContext` (`:1231-1238`), Copilot CLI a bare
   `additionalContext` (`:1225-1231`), and Antigravity CLI `injectSteps`/`systemMessage` — its
   comment says an `ephemeralMessage` "would be dropped after the first one", so the envelope
   the v2.0.2 report named for Antigravity is gone ([#21], [#23]). OpenCode injects through its
   generated TS plugin's `system.push` (`install_hooks.rs:5509`, [#22]).
2. **Plain markdown in git beats a vector store.** The wiki is the source of truth; the
   store is derived (`crates/ai-memory-wiki/src/lib.rs:1-5`). `git ls-tree -r --name-only
   v3.3.3 | grep -c '\.sql$'` is 98 and the same count under `crates/ai-memory-store/migrations`
   is 97 (the extra is a test fixture), so "all SQL files are migrations" no longer holds as an
   equality ([#24]) — the derived-index claim is unaffected. Vectors are an add-on stream
   inside RRF retrieval, not the substrate. mem0 wagers the opposite. The external validation
   the v2.0.2 read credited — pages natively conformant to Google Cloud's Open Knowledge
   Format v0.2 — is partial at v3.3.3: the *export* is conformant (observed on a three-file
   bundle) and the on-disk tree is not by the spec's letter, because the hooks' per-month
   event ledgers (`log-YYYY-MM.md`) carry no frontmatter and sit outside git; the doc line
   that says "no export step forks the truth" (`docs/okf.md:39-41`) is contradicted by its own
   file two screens later (`:70-71`, [#27]). The spec location ai-memory cites is a copy its
   owner calls frozen. The full account is under Re-traces, OKF.
3. **Zero-LLM default.** Invariant 13 in `docs/ARCHITECTURE.md` (the "Zero-LLM default path"
   entry, `:1150-1151`): capture, rule-based session pages, handoffs, retrieval and decay all
   work with no provider configured. LLM is strictly additive (consolidation, auto-improvement,
   rerank, prose briefings). Two qualifiers now stand beside the bet. Since 2.0 a default
   install is not egress-free: it background-fetches an ~87 MB MiniLM embedder from
   huggingface.co on the first start (OBSERVED at v3.3.3: 26 non-loopback connects and 4
   resolver contacts under `strace -f`; none on the embedder-off run or on the second start)
   and turns hybrid retrieval on at the next start. And zero-LLM no longer means zero-learner:
   the profile pass runs with no provider and admits on say-so (see Architecture, the agent
   loop). Two later deep-dives record a zero-LLM default path too: MemPalace (verbatim filing, no
   model on capture or recall) and agentmemory (synthetic observations, keyless by default). mem0,
   cognee and memori put an LLM in the extraction path itself (checked for those three when
   this sentence was written; `git ls-tree --name-only HEAD tools/5-memory/` lists nine reports besides this one
   on 2026-11-05, seven at 4f336e1, [#29]). Corrected 2026-11-05 (report-conventions audit): this sentence first read
   "No other report in the category records this bet at depth".

## Main features

- **Lifecycle-hook capture** into a closed 10-value `ObservationKind` vocabulary
  (`crates/ai-memory-core/src/observation.rs:33-54`: session-start, user-prompt,
  pre/post-tool-use, pre-compact, post-compaction, notification, stop, session-end, other).
  Unknown harness events collapse to `other` — the enum did not grow in the window. Adjacent
  routes into the same `/hook` ingress: a default-on boot-time backfill of an empty project's
  existing harness transcripts (changelog level, opt-out `AI_MEMORY_BACKFILL_ON_START=false`),
  marketplace plugins for Claude Code and Codex (3.0.0), and an `ai-memory-relay` companion.
- **Rule-based session pages** (no LLM): `sessions/<id>.md` from deterministic heuristics,
  carrying OKF v0.2 frontmatter (OBSERVED: `type`, `sources`, `generated`). PreCompact and
  PostCompaction refresh the page without ending the session.
- **Automatic cross-agent handoffs** opened at session end, delivered once at the next
  session start (cwd-matched, newer expires older). Session-start injection now carries
  three things — the baton, a profile digest, and a non-consuming inbox notice for
  cross-project mail (`router.rs:2465-2481`, `:3007`).
- **Two autonomous learners.** The provider-gated auto-improvement scheduler (reviews completed
  sessions, stages proposals, auto-approves by default) and, new in 2.6.0, the provider-free
  cross-project profile pass. Detail under Architecture.
- **Hybrid retrieval** via 25 MCP tools (OBSERVED: 25 served by `tools/list`; the registry
  count of `#[tool(` attributes inside the `#[tool_router]` impl is the same 25): FTS5 +
  entity index + link-neighbor graph + the observation stream (on by default since 3.0.0),
  fused by RRF, plus the default local-embedder vector stream and an optional LLM reranker;
  memory tiers (working/episodic/semantic/procedural) with exponential-decay retention and a
  daily forget sweep.
- **Per-project access control** (`open`/`restricted`, grants), **cross-project agent
  messaging** (a directed, claim-once mailbox, four tools), **admission webhooks** (an
  operator-configured deny/mutate chain on wiki writes; present since before v2.0.2, never
  mentioned until this read).
- **Per-harness installers** (`install-hooks --apply`, `ai-memory setup`) that mutate each
  harness's own config (for Claude Code: `~/.claude/settings.json` in place, merging around
  third-party hooks).

Table stakes in the kind: store + retrieve + MCP. Distinctive: the hook-capture breadth,
the zero-LLM path, git-versioned markdown as substrate, and two auto-approving learners.

## Stack & repo shape

Rust workspace, eleven crates under `crates/` at v3.3.3 (`git ls-tree --name-only v3.3.3
crates/ | wc -l`; ten at v2.0.2 — the new one is `ai-memory-test-support`) with a one-line
dependency discipline (`docs/ARCHITECTURE.md:767-769` and `AGENTS.md:267-269`, not
CI-enforced, [#34], [#35]): `core` (domain types, no IO), `store` (SQLite, single-writer
actor), `wiki` (atomic markdown writes + git2 + file watcher), `mcp`, `hooks` (payload
schemas, sanitizer, `/hook` ingress), `llm` (provider trait boundary), `consolidate`
(ingest/lint/sweep/auto-improve/profile), `workstream`, `web`, `cli`. Beside them, `evals/` as
a workspace member (the benchmark harness, explicitly not in the shipped binary) and seven
directories under `companions/` (`git ls-tree --name-only v3.3.3 companions/`: client, desktop,
importer, macos, relay, ts, wikisync; one at v2.0.2). The importer is a deliberately
workspace-isolated crate that replays external corpora (OMC wikis, generic conversation
exports and, new, the agentmemory store) through the public hook pipeline.
`git ls-tree -r --name-only v3.3.3 | grep -c '\.sh$'` is 120 and `'\.ps1$'` is 103 (92/82
at v2.0.2, [#38], [#39]): per-harness hook scripts and installers. `docs/ARCHITECTURE.md` is
1,833 lines (`git show v3.3.3:docs/ARCHITECTURE.md | wc -l`; 692 at v2.0.2) and its crate-layout
block now lists 11 including `web` ([#41], [#42]).

5,396 commits in about 5.5 months (`git rev-list --count v3.3.3`; first commit 2026-05-21,
tag 2026-11-03; 1,580 at v2.0.2, [#43], [#44]), **single-maintainer-led but not solo**:
`git log --no-merges --format=%an v3.3.3` gives 3,668 non-merge commits, 1,727 of them under
the author name `AkitaOnRails` (a second identity, `Fabio Akita`, adds 30; 47.9% for both,
[#49]), the next author at 294. In the v2.0.2 → v3.0.0 window the owner's share of non-merge
commits was 50.0% and in v3.0.0 → v3.3.3 it was 30.2% (release assessment). The repo is visibly
agent-built, with a floor measure: AI co-author trailers (Anthropic, OpenAI, Google, Cursor and
Copilot trailer addresses, read by git's trailer parser) on 730 of 1,289 non-merge commits in
the first sub-window and 220 of 1,219 in the second — a fall with no policy change, so trailers
are a floor on agent involvement, never a measure of it. `CLAUDE.md` is 17 lines (an
`@AGENTS.md` import plus a comment, [#54], [#55]) and `AGENTS.md` is 845 lines ([#56], [#57]);
`AGENTS.md` opens with ai-memory's own `<!-- ai-memory:start -->` managed block, so the
project dogfoods its own installer on its own repo.

## Architecture

### Entry point → one full trace (Claude Code, default local install)

1. **Install**: `ai-memory install-hooks --apply --agent claude-code` (or the two-command
   `install.sh` + `ai-memory setup`) → `apply_to_claude_code_settings`
   (`crates/ai-memory-cli/src/commands/install_hooks.rs:2329`, [#59]) stages the script bundle
   and rewrites `~/.claude/settings.json`, registering ten events (`CLAUDE_CODE_EVENTS`,
   `crates/ai-memory-cli/src/commands/render_shared.rs:44-58`, [#60], [#61]): SessionStart,
   UserPromptSubmit, Pre/PostToolUse, PostToolUseFailure (new), PreCompact, Stop, SessionEnd,
   SubagentStart/Stop. On local installs the registered command is the **native binary**
   (`ai-memory hook --event … --agent claude-code`), not the shell scripts —
   `HookCommandPlatform::current()` returns `PosixNative` unless an override is set
   (`render_shared.rs:2115-2121`, [#62]); the `.sh` bundle is the fallback for docker and
   setup-agent contexts where only scripts are copied.
2. **Capture**: each lifecycle event runs the hook command with JSON on stdin. The native
   command spools the event locally with a minted idempotency key, never blocks the agent
   (bounded timeouts; incremental drain only on a `post-tool-use` backlog,
   `commands/hook.rs:139-143`, [#63]), and hands session-end delivery to a detached
   `hook-drain` helper. The script path is a fire-and-forget `curl` to
   `POST /hook?event=…&agent=claude-code` (`hooks/claude-code/session-end.sh`), with a
   POSIX-only `_lib.sh` that walks up from cwd for a `.ai-memory.toml` marker to route the
   event to the right workspace and project.
3. **Ingest**: the server's hook router sanitizes the payload — the typed
   `Sanitized<NewObservation>` boundary whose only constructor is `Sanitized::new`
   (`crates/ai-memory-core/src/sanitize.rs:878`, [#67]; ordered regex redaction with an
   allowlist; the vendor's own invariant 6 calls it `sanitize()`, a name that exists at no pin —
   an identifier a docs-view claim got wrong about its own code) — authorizes the write against
   the target project (a hook event resolved to a project its author may not write is dropped
   as final and counted `dropped_unauthorized`, `router.rs:4837-4851`, `:966`), assigns an
   `ObservationKind`, and enqueues to the single-writer SQLite actor.
4. **Session end**: one SQLite transaction inserts the automatic handoff, stamps the session
   ended, and records the covered-observation count. The wiki gets a rule-based
   `sessions/<id>.md` (`crates/ai-memory-hooks/src/synth.rs:54`, [#71]: title from first user
   prompt, tool counts, a 500-line head/tail body cap at `:37-39`, tier episodic; frontmatter
   carries the OKF keys, OBSERVED: `type: Session Summary`, `sources`,
   `generated: {by: process:ai-memory/3.3.3, at: …}`) and an auto-commit. With a provider
   configured, a durable `session_consolidation_jobs` row queues the LLM rewrite; a
   non-transient provider failure ends the job terminal and the heuristic page the hook
   already wrote remains (`serve.rs:868-883`, [#73]). The v2.0.2 function
   `checkpoint_degrades_to_synth` is gone: PreCompact LLM work moved onto that durable worker
   (`git grep -n checkpoint_degrades v3.3.3 -- crates/` prints nothing, [#74]).
5. **Next session start** (any supported harness, same project): the hook fetches
   `GET /handoff?agent=…` synchronously and emits it in the harness's envelope (see the
   distinguishing bet; native path `commands/hook.rs:1216-1251`, [#76]). Delivery is
   single-use and claimed transactionally; a managed-workstream `managed_run` param bypasses,
   and never consumes, the legacy single-use handoff. A SessionStart whose source is a
   compaction takes this same ordinary path at v3.3.3 — nothing distinguishes it (see
   Re-traces, compaction).

### The agent loop (analog: capture → consolidate → learn)

ai-memory has no agent loop of its own; its runtime analog is the pipeline above plus two
**background learners**, and the load-bearing finding of this re-read is that the second one
needs no provider.

- **Auto-improvement (provider-gated).** `crates/ai-memory-consolidate/src/auto_improve_schedule.rs`:
  the server-side scheduler ticks non-overlapping every `interval_secs` (default 3,600,
  `config.rs:1798-1800`), claims newly completed sessions at-most-once per session, runs an LLM
  review over a deterministic bounded observation projection, and stages proposals targeting
  `concepts/`, `decisions/`, `gotchas/`, `procedures/`, `notes/`, `_rules/` and
  `_slots/current-focus.md` (`auto_improve.rs:2412-2420`). Proposals carry immutable target
  snapshots and append-only decision events, pass `min_confidence` and a stack of size budgets,
  and are **auto-approved through the normal wiki write path by default** —
  `require_approval: false` (`config.rs:1814`, [#13]). The scheduler runs only when an LLM is
  configured (`serve.rs:2461-2463`). The gate that exp-04 measured is unchanged: the system
  prompt is identical to v2.0.2's except an appended output-language section, and
  `validate_proposal` still requires non-empty evidence (`auto_improve.rs:2152`) — the quote is
  required to be present; no code was found that checks it against the source text (searched
  `auto_improve.rs` only for `evidence` plus empty/missing/required/must). An optional eval
  gate (`[auto_improve.eval]`, default off, `config.rs:1760`) can be interposed for `_rules/`
  and `procedures/`; a built-in `structure` scorer arrived in 3.3.0 (a structural check, not a
  semantic one).
- **The cross-project profile pass (provider-free, new in 2.6.0).** Settings default to
  `enabled: ProfileEnabled::Auto`, `inject_on_session_start: true`, `min_projects: 2`
  (`crates/ai-memory-core/src/profile.rs:272-283`); `Auto` resolves ON when the deployment does
  not distinguish operators (`:298`), i.e. a fresh install with no database users; the worker is
  spawned unconditionally on the HTTP transport (`serve.rs:1559-1570`), first pass after 120 s,
  then debounced after every SessionEnd and hourly. It harvests the user's **own prompts**
  shaped as preferences or corrections, plus curated pages and stack signals, never tool
  output, and writes `profile/<category>/<slug>.md` pages into `default/_global`; a SessionStart
  digest then injects them into every project, fenced as untrusted data
  (`core/profile.rs:642-645`). Admission: a topic group becomes a page when any statement in it
  carries an explicit cross-project marker (`GENERAL_MARKERS`: "in all my projects", "every
  project", "across projects", "everywhere" and pt-BR equivalents,
  `crates/ai-memory-consolidate/src/profile.rs:128-138`; `projects_short` is 0 when general,
  `:1585-1586`) **or** it recurs in at least `min_projects` independent projects (`:1588`).
  The newest statement wins and the replaced page stays on the supersession chain (`:10-15`).
  The zero-LLM path is complete; with a provider and `[profile] llm = true` (default) an LLM
  classifies and merges. SOURCE only: the probe stored `profile_candidates: 0`, so the pass
  was never observed to fire. It falsifies two sentences of the v2.0.2 report — "Zero-LLM install
  has no loop" and "say-so does not earn autonomous storage" ([#5], [#8]).
- Mechanism classification for the `learning_loop` vocabulary: **background** — a
  server-side scheduled fork entirely outside any harness process, harness-independent like
  ECC's instinct pipeline, default-on once a provider is configured (auto-improvement) and
  default-on without one on a single-operator install (profile pass).
  `docs/auto-improvement-loop.md` names Hermes Agent as the inspiration.

Every LLM prompt in the pipeline treats observations, wiki pages and prior proposals as
untrusted data with explicit trust delimiters (`auto_improve.rs:2454`); the same boundary
precedes injected handoffs (`router.rs:2609-2612`, `:3556-3559`), the profile digest and the
inbox notice (`router.rs:2470`).

### Context assembly

What the next session actually receives is narrower than the pitch suggests, and the pitch's
automatic part grew by two small items rather than a compiled summary:

- **The automatic handoff is heuristic, not LLM-written.** `build_auto_handoff`
  (`crates/ai-memory-hooks/src/router.rs:5746`, [#82]): summary = first user prompt + last user
  prompt, each capped at 1,500 chars (`:5759-5762`); next steps = a sorted list of tool names
  used, now led by a "Last failed tool call" entry; an opt-in "Latest assistant response" line
  (behind the assistant-capture double opt-in, `:5813-5819`, [#107]); `files_touched` is still
  `Vec::new()` (`:5847`). `derive_open_questions` (`:5870`, [#85]) is a 4-branch zero-LLM
  heuristic with a 27-phrase acknowledgment filter (`ACK_PHRASES`, `:5945-5973`; 27 at v2.0.2
  too — the "26-phrase" figure never reproduced, [#86]). That paragraph — not the wiki — is the
  session-to-session baton, and the prediction "the baton stays thin" held. Nothing in the
  change reaches mid-session facts, so exp-04's 0/10-injection / 10/10-pull result at its own
  pin is not disturbed.
- Session-start injection also carries the **profile digest** (`router.rs:3007`) and an
  **inbox notice** (`:2465-2481`, a one-line count of pending cross-project messages, fenced
  as "untrusted input from another project").
- The richer memory (compiled concepts/decisions/gotchas, briefings, slots) enters only when
  the agent *pulls* it via MCP tools, or via the opt-in `[briefing] inject_on_session_start`
  compiled project brief.
- Retrieval (`memory_query`) fuses RRF streams — FTS5, entity index, link neighbors, the
  observation stream (default-on since 3.0.0, `retrieval_tuning.rs:86`), and the vector stream
  once the default embedder has been fetched and the server restarted — then applies a bounded
  authority multiplier favoring rules/decisions/procedures/gotchas; raw observation FTS is the
  bounded fallback when compiled pages miss. After a compaction nothing is re-injected
  automatically; a user prompt opening with "reload context" fetches a recap (see Re-traces).

### Tool surface & permissions

25 MCP tools (OBSERVED: 25 served; read-only vs destructive hints declared per tool), grown
from 18 at v2.0.2 (+7, −0): `memory_handoff_list`, four cross-project messaging tools
(`memory_message_send/list/pop/cancel`), `memory_patch_page` and `memory_restore_page`
([#32], [#89], [#132], [#162]). The original `design-decisions.md` §10 cut lists **10** tools
(the file's adding commit, 2026-05-21), as the deep-dive said — the 2026-09-04 correction
"18 − 10 = 8" was wrong, and the vendor now writes "the count is now 25, not 10"
(`docs/ARCHITECTURE.md:851`, [#92]); the rationale paragraph names 12 later tools but none of
the five messaging and handoff-listing tools that are served ([#90]). Capture and injection
ride hooks; explicit read/write rides MCP; the two never mix transports. The server binds
localhost by default (`DEFAULT_BIND 127.0.0.1:49374`, `config.rs:29`). A fresh `ai-memory init`
mints a root bearer token (3.0.0, `init.rs:75-81`) so a new install's server requires it on
every route but `/healthz`; the probe started `serve` without `init` (`auth=false`), so that
posture is source-read, not observed. Multi-user deployments get per-operator handoff ownership,
per-user slot namespaces framed as a prompt-injection boundary, and — new — per-project
grants enforced in the scope resolver, the writer actor and the hook router (see Re-traces,
team_sharing).

### Category boundaries in the code

- **Model provider**: swappable behind `LlmProvider`/`Embedder` traits (`ai-memory-llm`), ten
  `ProviderChoice` variants (`crates/ai-memory-llm/src/factory.rs:29-51`: the eight of v2.0.2
  plus `Codex` and `Cursor`, [#93], [#94], [#95]); provider auth resolves before construction
  (invariant 14). The system runs with none. `llm_reasoning_effort`, a 9-value typed enum each
  chat provider maps to its native wire field (`types.rs:250-269`, [#97]) — category-1
  wire-behavior vocabulary independently rebuilt inside a category-5 tool.
- **Harness boundary**: per-harness event tables + installer functions in
  `render_shared.rs`/`install_hooks.rs`, normalized into the closed `ObservationKind` enum at
  ingress; 40 harness targets under the counting rule in the frontmatter (23 at v2.0.2, [#4]).
  Third parties get an `extension=<namespace>` seam on `/hook`, not a plugin system.
- **Environment**: none — a host-local daemon; the docker packaging is for the server itself.

## Bleed

Reaches category 2 (harness) twice: capture rides each harness's hook surface, and injection
rides each harness's context-injection contract — both catalogued per-harness in source. The
managed-workstream mode (`ai-memory run`, docs-read only) goes further and *launches*
harnesses, importing their native transcripts; that is category-2 orchestration growing
inside a category-5 tool, the same direction of travel as ECC's `ecc2`. It kept growing:
`enum RunHarnessChoice` went 11 → 13 → 13 variants and `crates/ai-memory-workstream` Rust lines
7,039 → 15,253 → 17,947 at v2.0.2 / v3.0.0 / v3.3.3 (release assessment, prediction 7). The
cross-project messaging tools are agent-coordination machinery in the same direction: a
directed mailbox addressed to a project with an optional harness recipient and an epistemic
`nature` tag.

Of the 15 numbered cross-cutting invariants in `docs/ARCHITECTURE.md`, **11 cite a specific
competitor bug** (cognee #2717, agentmemory #456/#469, basic-memory #763/#578…): items 1, 2, 3,
4, 5, 7, 8, 9, 11, 12 and 15 name a rival and an issue number — the same count at v2.0.2 and
v3.3.3; 6 cites an internal issue and 10, 13, 14 cite none ([#109], [#110]; the v2.0.2 read's
"10" was itself a miscount). The vendor read its rivals' issue trackers and wrote the findings
into `docs/issues-*.md`; `docs/research-2026-landscape.md` (1,106 lines, [#104]) surveys a wider
field and self-places ai-memory in a "file-first wiki memory" camp. Note that code and docs cite
an "invariant #16" that the numbered list in `ARCHITECTURE.md` (which stops at 15) does not
carry; its text lives in `AGENTS.md:513-542`.

## Cost model

MIT, self-hosted, no commercial ring visible at either pin (re-checked at v3.3.3: no pricing,
sponsors file or homepage; the README's `hosted|saas|cloud|pricing|subscription|managed service`
hits are competitor-comparison rows and a reverse-proxy doc link). Zero marginal cost in the
default path — that includes hybrid retrieval, because the default embedder is in-process and
keyless, and the profile pass, which is provider-free. Configuring a provider makes
consolidation, auto-improvement, rerank and the profile pass's optional LLM classification
metered per-token on your own key. The learning loop's depth therefore scales with willingness
to pay inference; the default-on scheduler at 3,600 s ticks with `max_sessions_per_tick = 1`
is sized to stay cheap. The vendor's own per-release LongMemEval-S reports (12 in the window)
put local-embedding `hit@5` at 0.943 for 3.3.3 (`docs/benchmarks/longmemeval-s-3.3.3-release.md:50`,
TESTIMONY, inside its stated run-to-run variance).

## Surprises

1. **The continuity baton is thin, and stayed thin.** The automatic handoff — the headline
   feature — is first prompt + last prompt + tool names, no LLM, no files. The wiki is rich, but
   the agent must pull it. Three more heuristic signals joined it in the window (a failed-call
   line, an opt-in assistant excerpt, a turn-checkpoint variant); none reaches mid-session facts.
2. **Both learners admit without a human, on opposite evidence.** Auto-improvement writes
   `_rules/` and `procedures/` pages with `require_approval: false` — guardrails are budgets,
   confidence floors, audit rows and prompt-level trust delimiters, not review — behind an
   evidence gate exp-04 measured. The profile pass, with no provider at all, mints a standing
   cross-project preference from one prompt sentence that says "everywhere", and a digest of it
   rides every project's SessionStart. The vendor guards the *shape* (preference grammar,
   own-prompt only, capability-disabling sentences need the general marker), not the evidence.
3. **Per-project access control shipped quietly.** V68 grants, `restricted` mode, a root-only
   grant CLI and enforcement in the resolver, writer and hooks are in the tree from v2.5.0 with
   no introducing changelog bullet found (searched the 2.5.0 section of `docs/changelog/2.x.md`
   for `grant|restrict|access|authoriz|708`: only two `(#708)` repository-identity bullets), and
   `docs/users.md`'s own header (`:6-8`) still says every authenticated request sees the same
   pages.
4. **Competitor archaeology as engineering method.** Eleven of fifteen invariants pinned to a
   named bug in a rival memory tool, with per-rival research docs in-repo. The most systematic
   prior-art discipline seen in the study so far.
5. **The hook-fragmentation surface is the real product.** `install_hooks.rs` is 18,351 lines
   (`git show <rev>:… | wc -l`: 9,875 at v2.0.2, 15,191 at v3.0.0) and the installer's agent
   registry went 18 → 29 (`enum AgentChoice`). Per-harness quirks are encoded as code and
   comments: Kimi Code discards SessionStart stdout (the brief rides the first user prompt
   instead, `commands/hook.rs:422-426`, [#116]) and fires PostToolUse only on success; Codex and
   Antigravity lack a true session end (explicit `ai-memory finalize-session`); Antigravity has
   no SessionStart (PreInvocation `invocationNum == 0` mapped instead); Devin ships PostCompaction
   instead of PreCompact; Zero execs commands with no shell; Claude Code logs a warning unless
   hook stdout starts with `{`. The standards-scoreboard row made concrete.
6. **A session-aware MCP bridge exists for Claude Code** (`mcp-bridge`) solely to smuggle
   `CLAUDE_CODE_SESSION_ID` into an HTTP header — identity plumbing MCP itself doesn't carry.
7. **Two stale code comments contradict the profile writer.** `crates/ai-memory-core/src/lib.rs:47-51`
   still says `_global` "is written only through explicit `scope: \"global\"` requests"; the
   profile pass writes `default/_global/profile/` itself.

## Open questions

- ~~Does the thin heuristic handoff actually sustain "continue without re-explaining" in
  practice?~~ **Answered 2026-08-19 (exp-04)**: continuity is real and entirely pull-shaped —
  see the release history. Not re-measured at v3.3.3 (exp-04 keeps its own pin).
- What do auto-approved `_rules/` pages look like after weeks of real use — convergent
  standing instructions or drift? Undecidable by source (release assessment, prediction 3);
  needs a lived store or an outside account. **Stakes rose twice since 2.0**: the opt-in
  experience pass extends the auto-approving path to cross-session abstraction, and the profile
  pass does the same with no provider and no eval gate; the one interposable eval gate is still
  default-off.
- Does the profile pass's prompt harvest fire on real captured prompts? The probe did not
  exercise it (startup delay 120 s; the synthetic prompts carried no preference markers). A
  cheap probe: two synthetic projects, one prompt "always use pnpm in all my projects", wait
  past 120 s, dump `profile_candidates` and the `_global` wiki tree, then start a session and
  read the injected digest.
- Does the "one choke point" claim for project authorization (`project_authz.rs:6-8`) hold for
  every web and `/api/v1` read path, and does a restricted project leak through
  `memory_query(global=true)` or `/web/search`? Confirmed for MCP and seven web route files, not
  exhaustively; 3.0.0 Security bullets (`CHANGELOG.md:3880-3889`) fixed one such leak.
- The managed-workstream loop (`ai-memory run`) is still read at docs level only — it claims
  transcript import and cross-harness event ledgers, which would make this a category-2
  orchestrator. Verify in source if the arc's cross-harness question stays live.
- What do a fresh `init` + `setup` install's server log and defaults look like (auth on,
  profile on)? Not observed; the probe started `serve` without `init`.
- ~~Does the vendor's own eval say anything falsifiable about consolidation quality?~~
  **Answered 2026-09-04, for retrieval**: `docs/benchmarks/` publishes dated,
  provenance-stamped LongMemEval-S runs from the in-repo `evals/` harness — and prints a
  competitor beating it (agentmemory 0.967 R@5). Still open at v3.3.3: an offline abstention
  benchmark exists (`evals/src/abstention.rs`, 3.3.0) but no abstention report is published
  (`docs/benchmarks/` holds none), and the stale 0.779 survives in the archived 2.x changelog
  (`docs/changelog/2.x.md:4501`, [#127]). Consolidation *quality* is measured only by the `ab`
  A/B harness — no published numbers.

## Candidate vocabulary collected

Collected for Phase 19, prose only: no cell exists for anything below, and no value outside a
key's legal set is written into any cell.

**Options census** (cells whose value depends on configuration carry the shipped default and a
trailing `# options:` comment in the frontmatter; each bullet is one instance, collected for
Phase 19's options-with-default grammar decision):

- `team_sharing` — default `attribution-only`; alternative `acl`. Switch: `ai-memory project
  access --mode restricted` (root-only) or `[auth] new_projects_restricted = true`
  (`crates/ai-memory-cli/src/config.rs:1037`); column `projects.access_mode`
  (`crates/ai-memory-store/migrations/V68__project_grants.sql:38-40`).
- `memory_revision` — default `auto`; alternative `proposed`. Switch: `[auto_improve]
  require_approval = true` (`config.rs:1684-1687`, default false at `:1814`; the gate at
  `crates/ai-memory-consolidate/src/auto_improve_schedule.rs:564-568`).
- `learning_loop` — default `background`; alternative `false`. Switch: `[profile] enabled =
  false` together with no provider configured (`crates/ai-memory-core/src/profile.rs:60-66`;
  provider gate `serve.rs:2461-2463`).
- `write_admission` — default `evidence-gated` (the stated exception to the fresh-install rule:
  it is the provider path exp-04 measured); alternative `unfiltered`, the posture of a fresh
  zero-LLM install, where only the profile pass writes autonomously. Switch: configuring a
  provider mounts the auto-improve evidence gate (`auto_improve.rs:2152`, `serve.rs:2461-2463`).

**Candidate axes** (each with ai-memory's evidence or "no instance" plus the searched surface;
none is a cell):

- `llm_free_path` — ai-memory has an instance, with a qualifier. The zero-LLM default is
  invariant 13 (`docs/ARCHITECTURE.md:1150-1151`; `AGENTS.md:506`). On the default path
  nothing generative runs: capture, rule-based session pages, the heuristic baton, retrieval,
  the daily forget sweep and the profile pass's zero-LLM branch are provider-free; the embedder
  is a non-generative candle BERT (`crates/ai-memory-llm/src/local.rs`) fetched from
  huggingface.co on first start (OBSERVED: 26 non-loopback connects, 4 resolver contacts). The
  axis would have to say that "LLM-free" and "egress-free" are separate facts.
- `concurrent_write_safety` — three mechanisms: the single-writer SQLite actor ("exactly one
  writer at all times, by construction", `crates/ai-memory-store/src/writer.rs:1-8`); optimistic
  preconditions on page writes, `expected_page_id` and `create_only` on `memory_write_page` and
  `memory_patch_page` (served `tools/list` schemas; `CHANGELOG.md:3495`); and "a divergent
  concurrent write supersedes, never destroys" (`AGENTS.md:523-526`). Client side, the hook
  spool takes exclusive file locks (`crates/ai-memory-cli/src/commands/hook_spool.rs:307`).
- `compaction_capture` — an instance. PreCompact (and Devin's PostCompaction) refresh
  `sessions/<id>.md` without ending the session or creating a handoff
  (`crates/ai-memory-hooks/src/router.rs:5129-5142`); with a provider an LLM checkpoint job is
  queued (`:4566-4581`); nothing is re-injected automatically after a compaction at v3.3.3.
  OBSERVED on the probe: 202, one empty `pre-compact` observation, page re-versioned. The
  axis would separate capture-at-compaction from re-injection-after-compaction.
- the OKF open-format axis — an instance: pages carry OKF v0.2 frontmatter
  (`crates/ai-memory-core/src/okf.rs:220-225`), an export command and a conformance gate, and
  the spec location cited is a frozen copy. The axis would have to separate "conformant
  export" from "conformant on-disk tree". See Re-traces, OKF.
- `agent_coordination` — an instance. Cross-project agent messaging
  (`docs/agent-messaging.md:1-40`): a directed, claim-once mailbox addressed to a project with an
  optional harness recipient (`to_agent`, V93), states `pending → claimed|cancelled`
  (`V64__agent_messages.sql:12-15`), a 256-message inbox cap, an epistemic `nature`
  (`measured|reported|inferred|unknown`, `measured` refused without `evidence`, V90), popped
  messages fenced as untrusted (`router.rs:2470-2480`), four MCP tools, a web inbox (3.3.0), and
  grants respected (a restricted inbox needs `write`).

**Out-of-enum findings** (facts for the admission pass, not cell values): `memory_scope` has two
scopes outside its legal list — the global scope `default/_global`
(`crates/ai-memory-core/src/lib.rs:55`, addressable by MCP `scope: "global"` at
`crates/ai-memory-mcp/src/server.rs:4798-4821`, present at v2.0.2 so the old cell was already
incomplete at its own pin) and the workspace-wide profile project `_profile`
(`crates/ai-memory-core/src/profile.rs:22-23`, `ProfileShare::Workspace`). `write_admission`
has no value for "assertion suffices on an explicit marker, otherwise recurrence in two
projects" as one posture; the registry's `unfiltered` fits the first branch and `scored` is the
nearest to the second.

## Release assessment — v3.3.3 (2026-11-05; pin 7e787c9 → 8c39e4e67)

*Method: the release-re-read variant of the three-tract pattern — release substance by component and the 16 cells, a per-claim confrontation of every claim unit at both pins (next section), and velocity, tracker and predictions — with 25 load-bearing tract claims re-run against the clone before any writing (24 held, one failed and was corrected) and a same-day release-binary run probe (below). Window: 7e787c9 (= tag v2.0.2, 2026-09-03) → 8c39e4e67 (= tag v3.3.3, 2026-11-03), 44 releases, clean ancestry (`git merge-base --is-ancestor v2.0.2 v3.3.3` succeeds). `v3.3.3` is an annotated tag that is an ancestor of `origin/main` but not on its first-parent line, so every window below is a first-parent walk from the tag. Every number was re-derived from the clone for this write-up, with its command beside it; dates are tagger dates. The earlier assessments are compressed into the release-history table at the end.*

### Character: a feature run into a major, then a fix-dominated hardening run at twice the throughput

Forty-four releases in 61.11 days (tagger dates 2026-09-03 13:48 -0300 to 2026-11-03 16:23 -0300), one of them a major: 3.0.0 (2026-10-13) removed the 1.x compatibility-token commands (migration V79), changed the fresh-install default (`ai-memory init` now mints a root bearer token and records it, so a new install's server requires it on every route but `/healthz`) and made the repository a plugin marketplace for Claude Code and Codex. The changelog says what the train was: 704 of 1,009 top-level bullets are `Fixed` (704 ÷ 1,009 = 69.8%; the same count by heading is Added 223 · Changed 59 · Security 16 · Docs 4 · Removed 2 · Deprecated 1; measure: top-level `- ` bullets under each `### ` heading of the window's version sections, `docs/changelog/2.x.md` 2.6.7 → 2.0.3 plus `CHANGELOG.md` 3.3.3 → 3.0.0, both read at v3.3.3). Fixed per Added is 324 ÷ 110 = 2.9 before 3.0.0 and 380 ÷ 113 = 3.4 after it. Two things that look like trends are measurement artifacts to carry forward: the share of non-merge commits with an AI co-author trailer fell from 730 ÷ 1,289 = 56.6% to 220 ÷ 1,219 = 18.0% across v3.0.0 with no policy change (the identity set is the trailer e-mails of Anthropic, OpenAI, Google, Cursor and Copilot, read from git's own trailer parser), so trailers are a floor on agent involvement, never a measure of it; and the owner's share of non-merge commits fell from 644 ÷ 1,289 = 50.0% to 368 ÷ 1,219 = 30.2% (author name `AkitaOnRails`), while two outside contributors each merged more PRs in sub-window 2 than the owner did (100 and 62 against 59 of 443 merged PRs; `gh pr list -R akitaonrails/ai-memory --state merged --search "merged:<v3.0.0 tag time>..<v3.3.3 tag time>" --limit 1000`, authors counted by login, 2026-11-05).

Churn by top-level directory (`git diff --no-renames --numstat <a> <b>`, insertions and deletions summed per directory, `crates/` split per crate; whole tree: 877 files +356,691 / −56,534 for v2.0.2 → v3.0.0 and 703 files +168,215 / −13,206 for v3.0.0 → v3.3.3 by `git diff --no-renames --shortstat`):

| Path | v2.0.2 → v3.0.0 (+ / −, files) | v3.0.0 → v3.3.3 (+ / −, files) |
|---|---|---|
| `crates/ai-memory-cli` | +89,361 / −8,509 (134) | +38,032 / −3,094 (114) |
| `crates/ai-memory-store` | +40,378 / −6,236 (89) | +22,124 / −1,081 (58) |
| `crates/ai-memory-mcp` | +39,601 / −12,809 (64) | +14,056 / −860 (31) |
| `companions/` | +33,886 / −250 (121) | +12,100 / −397 (78) |
| `docs/` | +31,791 / −2,200 (104) | +9,778 / −1,323 (95) |
| `crates/ai-memory-hooks` | +30,563 / −9,630 (21) | +20,550 / −2,933 (20) |
| `crates/ai-memory-consolidate` | +22,026 / −4,205 (58) | +12,910 / −667 (43) |
| `crates/ai-memory-web` | +14,893 / −3,649 (46) | +11,840 / −405 (79) |

### Sub-window 1: v2.0.2 → v3.0.0

- First-parent commits: **452** (`git rev-list --first-parent --count v2.0.2..v3.0.0`). All commits: 1,940 (`git rev-list --count v2.0.2..v3.0.0`, the all-commit measure: it includes every commit reachable through merged branches). Non-merge commits on the all-commit walk: 1,289 (`git rev-list --no-merges --count`), by 97 distinct author names (`git shortlog -sn --no-merges v2.0.2..v3.0.0 | wc -l`, an upper bound on people: it includes `dependabot[bot]`).
- Releases: **25** (`git tag --merged v3.0.0 --no-merged v2.0.2 -l 'v*' | wc -l`: v2.0.3 … v2.6.7, 24 tags, plus v3.0.0 which closes this sub-window); the GitHub release list gives the same 25 by tag membership (149 releases in all, none a prerelease or draft, listed 2026-11-05T01:52Z by `gh release list -R akitaonrails/ai-memory --limit 300`).
- Cadence: 25 releases ÷ 40.28 days between the v2.0.2 and v3.0.0 tagger dates (2026-09-03 13:48 -0300, 2026-10-13 20:36 -0300) = 0.62 releases/day (4.34/week, 1.61 days per release); first-parent 452 ÷ 40.28 = 11.2 commits/day; all-commit 1,940 ÷ 40.28 = 48.2 commits/day. Tracker, by GitHub search with the tag times as bounds (2026-11-05): 232 issues created (232 ÷ 40.28 = 5.8/day), 357 PRs merged.

### Sub-window 2: v3.0.0 → v3.3.3

- First-parent commits: **444** (`git rev-list --first-parent --count v3.0.0..v3.3.3`). All commits: 1,876 (`git rev-list --count v3.0.0..v3.3.3`). Non-merge: 1,219, by 68 distinct author names.
- Releases: **19** (`git tag --merged v3.3.3 --no-merged v3.0.0 -l 'v*' | wc -l`: v3.0.1 … v3.3.3); the GitHub list agrees. The 3.2.x line is a patch run: v3.2.0 published 2026-10-22T01:37:56Z and v3.2.10 on 2026-10-29T16:26:24Z, ten patches in 7.6 days (`publishedAt`).
- Cadence: 19 releases ÷ 20.82 days between the v3.0.0 and v3.3.3 tagger dates (2026-10-13 20:36 -0300, 2026-11-03 16:23 -0300) = 0.91 releases/day (6.39/week, 1.10 days per release); first-parent 444 ÷ 20.82 = 21.3 commits/day; all-commit 1,876 ÷ 20.82 = 90.1 commits/day. Tracker: 217 issues created (217 ÷ 20.82 = 10.4/day), 443 PRs merged. Cadence did not fall monotonically: releases per day went 1.13 (the 2026-08-18 → 2026-09-03 window: 18 tags ÷ 15.98 days) to 0.62 to 0.91, and first-parent commits per day rose 10.1 → 11.2 → 21.3.

### Whole window: v2.0.2 → v3.3.3

First-parent commits **896** (`git rev-list --first-parent --count v2.0.2..v3.3.3`) = 452 + 444: v3.0.0 lies on the v3.3.3 first-parent walk (`git rev-list --first-parent v3.3.3 | grep -c dbe928e3b64414c619435df887ed344ff83887a5` prints 1, that being the peeled v3.0.0). All commits 3,816 (`git rev-list --count v2.0.2..v3.3.3`) = 1,940 + 1,876. Releases 44 (`git tag --merged v3.3.3 --no-merged v2.0.2 -l 'v*' | wc -l`) = 25 + 19; 44 ÷ 61.11 days = 0.72 releases/day; 896 ÷ 61.11 = 14.7 first-parent commits/day. No prerelease and no tag with `rc`, `beta` or `alpha` in its name has ever existed (`git tag -l | grep -c -i -E 'rc|beta|alpha|-'` prints 0). Open work at 2026-11-05T01:54Z: 17 open issues and 7 open PRs (GitHub search `is:issue is:open`, `is:pr is:open`); 14 of the 17 were filed before the v3.3.3 tag time.

### What moved, ranked by what it does to this report's claims

1. **A zero-LLM learner that admits on say-so.** The cross-project profile pass (2.6.0) is a provider-free background writer, on by default for a single-operator server, that turns the user's own preference-shaped prompt sentences into `profile/` pages under the global scope and injects a digest at every SessionStart; one sentence with an explicit "everywhere" marker is admitted alone, otherwise recurrence in two projects is. It falsifies "Zero-LLM install has no loop" and "say-so does not earn autonomous storage" ([#5], [#8]). SOURCE only — the probe never exercised it.
2. **Per-project authorization.** `open`/`restricted` access modes with read/write grants, enforced in the scope resolver, the writer actor and the hook router, administered by root only; every project still starts `open` and per-page RBAC stays absent ([#17]). Shipped in 2.5.0 with no introducing changelog bullet found.
3. **The hook-fragmentation surface kept compounding.** `install_hooks.rs` 9,875 → 18,351 lines; the installer's agent registry 18 → 29; harness targets 23 → 40 by the report's own rule ([#4]); Claude Code events nine → ten ([#60]); Antigravity's envelope changed ([#21], [#23]).
4. **The MCP surface grew 18 → 25** ([#32], [#89], [#132], [#162]): five cross-project messaging and handoff-listing tools plus `memory_patch_page` and `memory_restore_page`. The messaging tools are agent-coordination machinery inside a category-5 tool (a directed, claim-once mailbox addressed to a project, with an epistemic `nature` tag).
5. **Capture and compaction.** PreCompact and PostCompaction refresh the session page without ending the session or creating a handoff; nothing is re-injected after a compaction except on a user's explicit "reload context" prompt (a recap built from the PreCompact row as its window boundary, native hooks only). Observed in the probe (run section, item 3). The report said nothing about either.
6. **OKF is weaker than the report's "native" bet** ([#27]): the export is conformant (observed) and the on-disk tree is not by the spec's letter (frontmatter-less ledgers outside git); the spec location the vendor cites is a copy its owner calls frozen (read 2026-11-05).
7. **Default posture.** A fresh `init` now mints a root bearer token (3.0.0). The probe started `serve` without `init` (`auth=false`), so every deployment sentence drawn from it describes the 2.x-shaped, token-less posture.
8. **Retrieval and store.** The observation stream is on by default in the RRF fusion since 3.0.0; migrations 58 → 97 ([#24]); consolidation sources 13 → 27 files, the opt-in "memory aging" set (extractive tier-down, cold-cluster dedup, entropy filter, dream merge) all default-off; `ProviderChoice` 8 → 10 ([#93]). The vendor's own per-release LongMemEval-S reports (12 in the window) put local-embedding `hit@5` at 0.943 for 3.3.3 (`docs/benchmarks/longmemeval-s-3.3.3-release.md:50`, TESTIMONY, inside the vendor's stated run-to-run variance).

### Scored predictions

The 2026-09-04 re-read carried no numeric forecast ("The deep-dive carried no numeric forecast"), so every band below is *reconstructed at scoring*, both sides stated, and verdicts use held, failed, mixed or undecidable by source.

| # | original sentence | band | measured at v3.3.3 | verdict |
|---|---|---|---|---|
| 1 | "the hook-fragmentation surface is the real product" compounded at "~130 lines/day" | no band at writing; reconstructed at scoring: true if `install_hooks.rs` grows at least 65 lines/day (half the recorded rate) — per-harness quirk code stays the main work; false below that; and true if the hook surface keeps its share of the Rust code, false if the rest outgrows it | `git show <rev>:crates/ai-memory-cli/src/commands/install_hooks.rs \| wc -l` = 9,875 → 15,191 → 18,351 at v2.0.2 / v3.0.0 / v3.3.3: +132/day (5,316 lines ÷ 40.28 days), +152/day (3,160 ÷ 20.82), +139/day whole (8,476 ÷ 61.11); `enum AgentChoice` 18 → 23 → 29. Share of all `crates/**/*.rs` lines (`git grep -c '' <rev> -- 'crates/**/*.rs'`, summed): 9,875 ÷ 218,110 = 4.53% → 15,191 ÷ 439,180 = 3.46% → 18,351 ÷ 561,238 = 3.27% | mixed |
| 2 | the implicit "the baton is thin and will stay thin" held on summary, next_steps, and files_touched | no band at writing; reconstructed: true if `build_auto_handoff` stays a zero-LLM heuristic with `files_touched` empty (continuity stays pull-shaped); false if it gains an LLM-written summary or fills `files_touched` | `crates/ai-memory-hooks/src/router.rs:5746@v3.3.3`: no LLM call, summary still first and last prompt capped at 1,500 chars (`:5761`), `files_touched: Vec::new()` (`:5847`); three more heuristic signals (a turn-checkpoint variant, an opt-in "Latest assistant response", "Last failed tool call" in next steps) | held |
| 3 | What do auto-approved `_rules/` pages look like after weeks of real use — convergent standing instructions or drift? | no band at writing; a question, not a forecast | preconditions unchanged by source: `require_approval: false` (`config.rs:1814`), patchable prefixes `_rules/` and `procedures/` (`auto_improve.rs:52`), governed promotion is a design doc only ("Status: design proposal, not implemented", `docs/design-rules-promotion.md:6`), open issues #1427, #1429 and #1471 ask for the gates; what weeks of use produce needs a lived store or an outside account, and the probes ran with no provider so the reviewer never fired | undecidable by source |
| 4 | An optional executable eval gate (`[auto_improve.eval]`, default off) can be interposed for `_rules/` and `procedures/` proposals | no band at writing; reconstructed: true if the gate is still default-off (the vendor keeps autonomous learning ungated by default); false if default-on | `impl Default for AutoImproveEvalSettings` → `enabled: false` (`config.rs:1760`); targets `_rules` and `procedures`; a built-in `builtin = "structure"` scorer was added (a structural check, not a semantic one; absent at v2.0.2) | held |
| 5 | the promised separate abstention report doesn't exist yet; the CHANGELOG still carries a stale 0.779 from a superseded run | no band at writing; reconstructed: true if both gaps persist; false if a published abstention result exists and 0.779 is corrected | the instrument landed (an offline `ai-memory-eval abstention` benchmark in 3.3.0, `evals/src/abstention.rs`, fixture `evals/fixtures/abstention/v1.json`) but `evals/runs` has no tracked files and `docs/benchmarks/` holds no abstention report; 0.779 survives verbatim in the archived 2.x changelog (`docs/changelog/2.x.md:4501`) | mixed |
| 6 | Doc gap at the pin: the support matrix's embedding-providers row doesn't list `local`. | no band at writing; reconstructed: true if the gap persists; false if the row lists `local` | `docs/support-matrix.md:62@v3.3.3` is word-for-word the v2.0.2 row (`:38`; `:59` at v3.0.0); `local` is the source default (`config.rs:3087`) and the probe embedded with it (`local / all-MiniLM-L6-v2 / 384`) | held |
| 7 | The managed-workstream loop (`ai-memory run`) was read at docs level only — it claims transcript import and cross-harness event ledgers | no band at writing; reconstructed: true if the loop keeps growing (stakes rise: run targets and the workstream crate); false if it stalls or is removed | `enum RunHarnessChoice` 11 → 13 → 13 variants; `crates/ai-memory-workstream` Rust lines 7,039 → 15,253 → 17,947 at v2.0.2 / v3.0.0 / v3.3.3 (grew, then flat on targets); whether `ai-memory run` implements the claimed transcript import is still untraced | mixed |

### Predictions for the next re-read

Each is scored at the first `v*` tag whose tagger date is on or after the stated date, read after a fresh fetch, with the commands above.

- **Hook-install surface (scored 2026-12-05).** true if `git show <tag>:crates/ai-memory-cli/src/commands/install_hooks.rs | wc -l` (summed with any `install_hooks/` submodule files if it is split) is between 20,500 and 25,000 lines and `enum AgentChoice` has 31 to 36 variants by 2026-12-05 — the world where harness intake continues at the observed rate (139 lines/day, 11 variants ÷ 61.11 days = 0.18/day); false if lower (under 20,500 lines or 30 variants or fewer: the plateau world, intake stalled or the installer went table-driven, in which case switch to the registry and say the line measure died) or higher (over 25,000 lines or 37 variants or more: the acceleration world).
- **Release cadence (scored 2026-12-05).** true if the number of `v*` tags with tagger dates from 2026-11-05 to 2026-12-04 inclusive (`git for-each-ref --format='%(refname:short) %(taggerdate:iso-strict)' 'refs/tags/v*'`) is between 11 and 34 (0.37 to 1.13 per day; this window ran 0.62 and 0.91) — the continuing-train world; false if 10 or fewer (the maintenance or slowdown world) or 35 or more (a patch storm beyond any observed rate).
- **Autonomy defaults (scored at the first tag on or after 2026-12-31).** true if `impl Default for AutoImproveSettings` still sets `require_approval: false` and `impl Default for AutoImproveEvalSettings` still sets `enabled: false` (`crates/ai-memory-cli/src/config.rs`) by 2026-12-31 — the world where the vendor leaves the learning loop ungated; false if either flips — the world where it moves to human-reviewed or eval-gated by default (open issues #1427 and #1429 are the visible pressure).
- **Maintainer share (scored 2026-12-05).** true if `AkitaOnRails`-authored non-merge commits are between 20% and 45% of `git rev-list --no-merges --count v3.3.3..<tag>` (author name after `.mailmap`, `git log --no-merges --format=%an`) by 2026-12-05 — the shared-maintenance world (the last two windows ran 50.0% and 30.2%); false if under 20% (the handover world: the project is carried by outside contributors) or over 45% (the re-centralisation world, back toward sub-window 1).

### Post-pin drift (dated)

Drift, 2026-11-04: `v3.4.0` is an annotated tag peeled `7bb659ceda9cad1c3867079313d6667e2abeb321`, tagger date 2026-11-04 17:25:15 -0300, one day after v3.3.3; `v3.3.3..v3.4.0` is 54 first-parent commits (`git rev-list --first-parent --count v3.3.3..v3.4.0`) and 129 all-commit (`git rev-list --count v3.3.3..v3.4.0`). This is post-pin, never a correction of a v3.3.3 claim.

Drift, 2026-11-04, the compaction fix: issue #1983 ("Re-ground on ai-memory after a context compaction") was opened by the owner at 2026-11-04T16:00:03Z and closed at 2026-11-04T17:10:47Z as completed, and 13 commits reference it between the tags (`git log --oneline --grep=1983 v3.3.3..v3.4.0 | wc -l`). By subject they add a post-compaction anchor (`feat(recap): add the post-compaction anchor and Devin's boundary`), inject it on a compact SessionStart (`feat(hook): inject the post-compaction anchor on a compact SessionStart`), accept `session_id "current"` in `memory_read_session_observations`, add an instruction-surface rule to re-ground after a compaction, and make compact starts claim nothing (`fix(hooks): never repeat inbox-notice query keys; compaction starts claim nothing`). The issue body's own account of the pre-fix behaviour ("Every PreCompact/PostCompaction hook returns `{}`") matches what the probe observed at v3.3.3 (run section, item 3); the fix itself is a v3.4.0 fact, read from commit subjects (TESTIMONY) and not traced here.

Drift, 2026-11-05T02:18Z: `gh api repos/akitaonrails/ai-memory/compare/v3.3.3...main --jq .ahead_by` prints 131 (all-commit measure): the 129 of the v3.4.0 range plus 2 beyond it; the clone's local `origin/main` (8e122ef8, 2026-11-04, from the last sync before this read) is 56 first-parent commits past the pin (`git rev-list --first-parent --count v3.3.3..origin/main`). The pin does not move.

## Re-traces at v3.3.3

*Five questions the cells could not answer from the release assessment alone, each read from source at v3.3.3 (`git show v3.3.3:<path>`, no checkout) from the release-substance tract (the first three) and the per-claim tract (the last two), with the load-bearing citations of each re-run against the clone before use (the spot-check recorded in the claims section). Grades: SOURCE, OBSERVED, TESTIMONY, INFERENCE.*

### team_sharing — per-project grants vs "no RBAC"

**What a fresh install shares.** Everything, with attribution. A fresh install has no database users, so `distinguishes_operators` is false (`crates/ai-memory-store/src/reader.rs:14118-14128`) and the per-project gate short-circuits to allow (`crates/ai-memory-store/src/project_authz.rs:210-213`, `if !self.distinguishes_operators { return Ok(()); }`). With database users added, every project is still `open` (`crates/ai-memory-store/migrations/V68__project_grants.sql:38-40`, `DEFAULT 'open'`; `project_authz.rs:222`, `AccessMode::Open => Ok(())`), so all authenticated users read and write every project and writes are attributed (`pages.author_id`). SOURCE. The `open` default is *not* observed: the kept store dump lists `projects: 3` and `project_grants: 0` without a row dump, so a claim of an observed `access_mode=open` (made in a draft of the per-claim table) failed its spot-check and was regraded SOURCE.

**The grant model is an option, and it is real.** `project_grants (workspace, project, user) → level IN ('read','write')` (`V68__project_grants.sql:27-35`); `projects.access_mode` is `open` or `restricted` (`project_authz.rs:58-63`); a `restricted` project admits root, its creator and grantees, a read needs any grant and a write needs `write` (`project_authz.rs:224-238`); an unknown mode degrades to `open` while a store failure refuses ("an authorization dependency must never fail open", `:29-35`). An operator restricts one project with `ai-memory project access --mode restricted` or makes new projects restricted with `[auth] new_projects_restricted = true` (`crates/ai-memory-cli/src/config.rs:1037`, off by default per its doc comment at `:1029-1036`; wired at `crates/ai-memory-cli/src/commands/serve.rs:1754-1758`). The reserved `scratch` and global-preferences projects are always open (same doc comment). Administration is root-only: "There is no per-project administrator" (`docs/users.md:771-774`, TESTIMONY), and the grant commands are thin HTTP clients over root-only `/admin/*` routes (`crates/ai-memory-cli/src/commands/grant.rs:1-7`, `project.rs:1-7`). So the registry's "sharing is itself a permission" holds only in the sense that *granting* is the root capability; no non-root user can hold a `share` permission (`GrantLevel` has `Read` and `Write` only, `project_authz.rs:91-115`).

**Where enforcement sits.** In the scope resolver — `decide_scope` (`crates/ai-memory-store/src/scope.rs:413-445`), reached through `resolve_read_args` and `resolve_write_args` — which the store module doc calls "the one place every scoped MCP/API/web path funnels through" (`project_authz.rs:5-9`; that "every" is TESTIMONY: the re-trace confirmed resolver use in the MCP server and seven web route files, not that no path bypasses it); in the writer actor as defense in depth (`crates/ai-memory-store/src/writer.rs:958`, `authorize_project`); and in the hook router, which drops a capture resolved to a project its author may not write and counts it `dropped_unauthorized` (`crates/ai-memory-hooks/src/router.rs:4837-4851`, `:966`). Bounded exceptions, all TESTIMONY from `docs/users.md`: the reserved global scope is read-open and write-gated to root or a `write` grant (`:790-800`; SOURCE `project_authz.rs:214-220`); proxied non-root end-users under trusted-proxy auth are not subject to `restricted` grants, "by design" (`:163-172`); and "No database users, no checks" (`:814-815`).

**When it landed.** `V68`, `grants.rs`, `grant.rs`, `project.rs` and `new_projects_restricted` are present at `v2.5.0` and absent at `v2.4.2` (`git cat-file -e <tag>:<path>`), i.e. shipped 2026-09-30, 26 days after the report's 2026-09-04 read set `attribution-only`. No introducing changelog bullet was found (searched the 2.5.0 section of `docs/changelog/2.x.md` for `grant|restrict|access|authoriz|708`: two `(#708)` repository-identity bullets only).

**Against `docs/users.md` and ADR-0052.** The doc contradicts itself: its header (`docs/users.md:6-8`) still says "Every authenticated request sees the same wiki pages; there is no per-page RBAC or group permission model", and the same file's "Per-project access" section (`:749-815`) documents `restricted` projects a non-grantee cannot read; per-page RBAC *within* a project stays absent (`:820-823`: `pages.author_id` is "attribution, never a read filter"). [ADR-0052](../../adrs/0052-team-sharing-key.md) records ai-memory as `attribution-only` at 7e787c9 and quotes the header sentence; that was true at its pin and is a dated record, never edited. What no longer follows from it is the registry note and the category README paragraph that restate "RBAC absent by design" as ai-memory's current posture: at v3.3.3 the project boundary *is* gated, once an operator turns it on. Both go to the ripple worklist for Phase 19.

**Consequence for the cell.** The shipped default is `attribution-only` and the cell keeps it; `acl` is an available option behind a root-only switch, recorded in the cell's `# options:` comment. No value changed, so the registry's `team_sharing` note is not amended in this phase. The old comment sentence "RBAC absent BY DESIGN … attribution records who wrote, never gates whether" is no longer true at the project boundary and is replaced; it remains true within a project.

### write_admission — admission webhooks

**What they are.** Operator-configured HTTP hooks invoked inside `Wiki::write_page` and the destructive and handoff operations just before the durable mutation: `write_page`, `consolidate`, `delete`, `delete_event_ledger`, `purge_project`, `purge_session`, `purge_workspace`, `move_project`, `move_session`, `handoff_begin|accept|cancel` (`crates/ai-memory-wiki/src/admission.rs:84-137`). A blocking webhook can **mutate** the page (a 200 with `{page}`) and, when its `failure_policy = "reject"`, **deny** by answering non-2xx or being unreachable (`admission.rs:492-525`); the default policy is `Ignore` (`:176-184`, `#[default] Ignore`), under which a non-2xx is logged and the write proceeds. Cap 16 webhooks (`:311`). It is a gate for plumbing — it sees one page at a time and has no built-in policy about evidence.

**Default state: empty.** `admission_webhooks: Vec::new()` (`crates/ai-memory-cli/src/config.rs:1476`) and "Empty config = no chain attached, zero overhead" (`serve.rs:1360-1366`). Configure with `[[admission_webhooks]]` or `AI_MEMORY_ADMISSION_WEBHOOKS_JSON` (`config.rs:2448-2453`). When configured they do sit on the autonomous paths: auto-improve approval passes `AdmissionOp::WritePage` (`auto_improve_schedule.rs:579-582`), the consolidator writes as `Consolidate` (`crates/ai-memory-consolidate/src/consolidator.rs:304`, `:423`), and the profile writer's missing admission context is treated as a default context when a chain exists (`crates/ai-memory-wiki/src/wiki.rs:695`). They are an option that can *add* a gate, not the gate the cell classifies. They were present at v2.0.2 as well (`admission.rs` 817 lines, `docs/admission-webhooks.md` 466 lines at `v2.0.2`) and unmentioned in the 2026-09-04 report.

**Does the cell stay `evidence-gated`?** Yes, for the path it was measured on, with the general sentence replaced. The auto-improve gate is unchanged in substance: same evidence-rejecting prompt (`auto_improve.rs:2450-2470`, identical to v2.0.2's except an appended output-language section), non-empty evidence required (`:2152`), `require_approval: false`, eval gate off. exp-04's 12 of 12 rejections were at acd9c0b and nothing in the window weakens the path; it runs only with a provider (`serve.rs:2461-2463`). What changed is that a *second* autonomous writer exists whose admission is different: the profile pass admits a standing preference on one prompt sentence carrying an explicit cross-project marker (`crates/ai-memory-consolidate/src/profile.rs:1585-1586`), or on recurrence in two independent projects (`:1588`; same-hour fan-out counts once, `:1566-1568`), with no provider. It is narrow — preference-shaped sentences from the user's own prompts, capability-disabling sentences need the general marker (`CAPABILITY_WORDS`, `:145`, check at `:898`) — but on the marker branch say-so suffices, which is the registry's own definition of `unfiltered` ("assertion suffices"); the recurrence branch is a count threshold, not "reward/confidence thresholds with probation" (`scored`). INFERENCE: on a zero-LLM default install the only autonomous synthesizer is the profile pass, so the shipped default's autonomous admission there is assertion-based, while a provider-configured install has both paths. The cell's comment states both paths, and its options comment lists `unfiltered` for the zero-LLM fresh install; the cell keeps `evidence-gated`, the value that describes the path exp-04 measured (the one stated exception to the block's fresh-install rule); that the registry has no single value for the combined posture is recorded under the candidate vocabulary, not forced into the cell. Session summary pages are deterministic transcripts of all capture, not an admission decision; the old report did not count them either.

### memory_scope — the global scope

**The literal and its operations.** `pub const GLOBAL_SCOPE_PROJECT: &str = "_global";` (`crates/ai-memory-core/src/lib.rs:55`), in the workspace named by `DEFAULT_WORKSPACE_NAME = "default"` (`:41`); its doc comment (`:47-51`) says default `memory_query` reads union it with the current project and that it is "written only through explicit `scope: "global"` requests" (stale: the profile pass writes there too). It is addressed by MCP `scope: "global"` (`crates/ai-memory-mcp/src/server.rs:4798-4821`), which refuses a workspace or project beside it and resolves through the same choke point as naming `default/_global` explicitly, so both spellings are gated alike. Writes to it are root-or-`write`-grant only on a multi-user server and open on a single-operator one (`project_authz.rs:214-220`, `reserved_global`). The hook router does not attribute capture to it: an event whose project resolves to `_global` falls back to the server-default project (`crates/ai-memory-hooks/src/router.rs:1906-1909@v2.0.2`; the doc comment states the same at v3.3.3). A second reserved scope, the workspace-wide profile project `_profile` (`crates/ai-memory-core/src/profile.rs:22-23`, `ProfileShare::Workspace`), and the per-user `_profile.<user id>` (`:25-36`) hold profile pages.

**Out of the key's legal list.** `memory_scope` is a list of `project | agent | user | session`; neither `global` nor `workspace` is in it. `_global` existed at v2.0.2 (`crates/ai-memory-core/src/lib.rs:41@v2.0.2`), so the 2026-08-19 cell `[project, user]` was already incomplete at its own pin — an own-pin gap, not drift. The legal axes at v3.3.3: `project` yes and default (the `.ai-memory.toml` walk-up and `ScopeResolver`); `user` yes on a multi-user server only (per-user `_slots/u-<identity_key>/` redirection, `server.rs:3865-3880`: "a single-operator server … is unaffected"); `agent` absent as a store axis — searched the 25 served `tools/list` input schemas, where the only `agent` parameter is on `memory_message_pop` (a harness-addressed message claim, V93 `to_agent`) and `memory_query`, `memory_read_page` and `memory_write_page` carry no agent filter; `session` not a page-store scope — `memory_write_page` refuses `session_id` together with `scope` ("a session belongs to one project", `server.rs:4780-4785`), and the active-project pointer's `PerSession` mode is routing, not storage (`crates/ai-memory-core/src/active_project.rs:28`).

**Consequence for the cell.** The cell keeps legal values only, `[project, user]`; `global` and `workspace` are named as out-of-enum facts under the candidate vocabulary and on the ripple worklist for the admission pass. The cell's comment says `user` is default-off on a single-operator install.

### Compaction capture — issue #1983

**What PreCompact does at v3.3.3.** The shell hook (`hooks/claude-code/pre-compact.sh:19-27`) POSTs the payload to `/hook?event=pre-compact&agent=claude-code` fire-and-forget and prints `{}` — its own comment: "This hook only POSTs (fire-and-forget) and injects no context". The native hook command treats `pre-compact` as one of the events that spawn the background drainer (`crates/ai-memory-cli/src/commands/hook.rs:151`) and is not a context-delivering event (`delivers_context`, `:1426-1447`, names the SessionStart, UserPrompt, PostToolUse, SubagentStart and Antigravity PreInvocation paths; PreCompact is not among them), so it writes the empty success reply. On the server (`crates/ai-memory-hooks/src/router.rs:5129-5193`) the observation row is written (kind `pre-compact`), the event ledger is appended, and `write_checkpoint_page` refreshes `sessions/<id>.md` — "Does NOT end the session and does NOT create a handoff. The eventual SessionEnd supersedes this page" (`:5129-5132`). With a consolidator configured it also enqueues durable LLM consolidation (`enqueue_session_checkpoint_consolidation`, `:4554-4583`). Devin's `PostCompaction` takes the same branch with label `post-compaction` (`:5134-5142`). SOURCE.

**Observed.** On the embedder-off run (no provider), a PreCompact for the none-1 session answered `202 queued` with no server-log line; observations went 3 → 4 (one new `pre-compact` row with an empty body) and pages 1 → 2 (the old `sessions/<id>.md` row `is_latest=0`, a new one `is_latest=1`); nothing came back for injection (run probe, item 3). The probe sent it after that session's `session-end`, and the server re-versioned the ended session's page anyway. OBSERVED.

**Is anything injected back after a compaction?** Not automatically at v3.3.3. Claude Code fires SessionStart with `source: "compact"` after a compaction, and neither `session-start.sh` (`:29-44`, no `source` read) nor the native hook distinguishes it: `git grep -n '"compact"\|source.*compact' v3.3.3 -- crates/ai-memory-hooks/src crates/ai-memory-cli/src/commands/hook.rs` hits only a managed-run test (`router.rs:14798`). A compact start therefore runs the ordinary start path — `GET /handoff` — which can deliver and claim a pending handoff, recovery snapshot or brief, not a compaction recap. SOURCE (absence, searched as stated) plus INFERENCE. **A manual recap exists:** a user prompt opening with "reload context" (`crates/ai-memory-core/src/compaction_recap.rs:6,16`, anchored at the start, ASCII case-insensitive, whole words) makes the native UserPromptSubmit hook drain the spool and `GET /recap` (`hook.rs:2081-2110`), injected as a `UserPromptSubmit` `additionalContext` envelope (`user_prompt_recap_envelope`, `hook.rs:1207-1214`) for Claude Code, Codex, Qwen Code and Qoder (`crates/ai-memory-core/src/ids.rs:565-569`; Cursor payloads are excluded, `hook.rs:2087-2091`); OpenCode plugins get the same trigger as a JS regex (`compaction_recap.rs:10`). The shell fallback hooks have no recap (`git grep -n -i 'recap\|reload' v3.3.3 -- hooks/claude-code/ hooks/_lib.sh` prints nothing). The recap (`crates/ai-memory-hooks/src/recap.rs:37-41`) is read-only — never claims a handoff, never publishes the active project, never records an observation — and rebuilds "the window of the session that ended at its latest compaction" from rows of kinds `UserPrompt | Stop | PreCompact` (`recap.rs:119-128`), newest first up to `RECAP_ROW_LIMIT = 400`, behind the project read grant (`:85-90`). So the PreCompact observation row, empty body and all, is load-bearing: it is the window boundary. Devin's `PostCompaction` is not a boundary at v3.3.3 (absent from that kinds list). SOURCE.

**Consequence for the cell.** `capture_path: hook` holds; the report's compaction statements hold where it made them (PreCompact and PostCompaction are capture kinds; Devin ships PostCompaction), and it said nothing about the recap, which is new since v2.0.2. v3.3.3's answer is "captured and checkpointed, re-injected only on a user's explicit 'reload context' prompt, native hooks only".

**Dated drift, not a correction (2026-11-04, v3.4.0).** Issue #1983 was opened by the owner at 2026-11-04T16:00:03Z and closed at 17:10:47Z; 13 commits reference it between the tags. By subject they add an automatic post-compaction anchor (`GET /recap?mode=anchor`: first and latest operator prompts, default 2,000 chars) injected on a compact SessionStart for Claude Code, Codex and Factory Droid, with compact starts claiming nothing, and Devin's PostCompaction joins the recap boundary (`5e87a308`, `451e4fc0`, `ca67719c`, `08d128a0`; commit messages, TESTIMONY, not traced here). The issue body's own account of the pre-fix behaviour matches what the v3.3.3 probe observed. This is post-pin and corrects nothing above.

### OKF spec skew — frozen snapshot vs live repository

**What ai-memory cites, and when it verified it.** `docs/okf.md:43-58` — "Target: OKF v0.2 … Spec: `GoogleCloudPlatform/knowledge-catalog`, `okf/SPEC.md` (verified 2026-09-01)" — unchanged since v2.0.2 (`docs/okf.md:33-36@v2.0.2`); the code cites the same location (`crates/ai-memory-core/src/okf.rs:7-8`, `export_okf.rs`, `m2026_09_okf_conformance.rs:1-6`). The conformance summary it gives is three bullets plus tolerance of unknown keys (`docs/okf.md:51-58`, TESTIMONY). The gate in code is `okf::is_conformant`, a non-empty string `type` and nothing else (`crates/ai-memory-core/src/okf.rs:220-225`); parseability is enforced by the caller treating a parse failure as empty frontmatter. SOURCE.

**The spec side (read 2026-11-05 02:39 UTC, `gh api repos/<repo>/contents/<path>`, base64-decoded).** `GoogleCloudPlatform/knowledge-catalog`'s `okf/SPEC.md` and `GoogleCloudPlatform/open-knowledge-format`'s `SPEC.md` are **byte-identical** today: the same git blob `c06e3eede0c910d0ecf12524c34204156f8795ac`, 37,748 bytes, decoded sha256 `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101` for both. So today the skew is one of *location*, not content. `knowledge-catalog/okf/README.md` opens with an IMPORTANT banner: "OKF now lives in its own repository: GoogleCloudPlatform/open-knowledge-format … **Stop using the copy under `okf/` in this repository.** It is a frozen snapshot, no longer maintained, and anything built against it will drift out of date." ai-memory's citation, in docs and in code, points at the frozen copy, and its "verified 2026-09-01" is the only date; the standing risk is content skew at the next spec revision, which this read cannot see. TESTIMONY, read 2026-11-05 02:39 UTC: the `gh api` responses (blob, size, digest, banner text) were not saved to the kept evidence directory, so this is a dated read of a remote document, not kept evidence.

**How the pages meet the spec's three conformance criteria** (SPEC §11, "A bundle is conformant with OKF v0.2 if": every non-reserved `.md` has a parseable YAML frontmatter block; every frontmatter block has a non-empty `type`; reserved `index.md` and `log.md` follow §8 and §9 when present; §3.1 reserves only those two filenames, "All other `.md` files are concept documents"):

| Criterion | Exported bundle (OBSERVED, a three-file bundle from the probe) | On-disk project directory (the bundle per `docs/okf.md:85`) |
|---|---|---|
| 1. every non-reserved `.md` has parseable frontmatter | met: `_meta.md` and the session page both carry frontmatter | **not met by the letter**: each project root carries `log-YYYY-MM.md` ledgers (observed `log-2026-11.md` in the store listing) written as `## [ts] event \| title` lines with no frontmatter (`crates/ai-memory-hooks/src/log.rs:3-6`; `docs/okf.md:93-96`, "no frontmatter … the conformance gate never sees it (#748)"). The name is not reserved by §3.1, so it is a concept document without frontmatter. SOURCE + OBSERVED (the ledger's content was not kept; its format is read from source) |
| 2. non-empty `type` | met: `type: Scope Manifest`, `type: Session Summary` | met for concept pages (`conform_frontmatter` at the one write choke point, `docs/okf.md:101-110`; OBSERVED on a session page); not met for the ledger (no frontmatter) |
| 3. reserved `index.md`/`log.md` per §8 and §9 | met: the root `index.md` has only `okf_version: "0.2"` as frontmatter (§8 allows exactly that at the bundle root) over a heading and a list; no `log.md` | no `index.md` on a fresh store (OBSERVED; §11 forbids rejecting a bundle for a missing `index.md`); `log.md` "not adopted: git is the log" (`docs/okf.md:91`) |

**Native pages vs the exported bundle.** The export is a client of `POST /admin/export-okf` (`crates/ai-memory-cli/src/commands/export_okf.rs:3,34`; server `crates/ai-memory-mcp/src/admin.rs:656`). The server's `build_okf_bundle_file` (`admin.rs:965-1060`) skips `_pending/`, skips `index.md` and `log.md` by name ("regenerated / not adopted", `:1003-1004`), skips rotated event ledgers (`ai_memory_wiki::is_rotated_event_ledger`, `:1005-1015`, #748), refuses the whole export if any remaining page fails `is_conformant` (`:1020-1026`), writes a fresh root `index.md` with only `okf_version: "0.2"` as frontmatter and a list body with no stray prose ("some strict OKF validators read §11.3 as rejecting a stray sentence — issue #960 item 1", `:1038-1046`), and augments each page in the tarred copy only (`augment_page_for_export`, `:1074`): a missing `title` is backfilled from the H1 or path stem, and `description` falls back to `abstract` — "only in the exported copy … the on-disk wiki file is never touched" (`docs/okf.md:70-71`; both rows absent at v2.0.2: `git grep -n 'backfills\|only in the exported copy' v2.0.2 -- docs/okf.md` prints nothing). The migration (`crates/ai-memory-wiki/src/migrations/m2026_09_okf_conformance.rs:1-19`) is backup-gated and idempotent, "fresh installs never create archives", and writes an on-disk project `index.md` only when absent on a migrating store (`:390-408`), with a body sentence ("Concept files live in these directories:", `:405`) of the shape the export path removed for #960. SOURCE.

**Net.** The **export is conformant** (observed on a three-file bundle); the **on-disk tree is not, by the spec's letter**, because of the rotated ledger files, which the vendor knows and gates around in every consumer it owns (export, migration scan, watcher; `crates/ai-memory-wiki/src/ledger.rs:1-13`). Together with the export-time augmentation, the sentence the 2026-09-04 report quoted as bet 2's validation — "the wiki files *are* the OKF files … no export step forks the truth" (`docs/okf.md:39-41`) — is contradicted by its own file at v3.3.3: the export does fork (drops ledgers, regenerates the index, backfills fields). A second, smaller skew: the ledgers sit outside git (`log.rs:13-15`), so "plain markdown in git" is true of concept pages, not of every `.md` in a project directory. This changes the strength of the report's bet 2 and its "native" wording, not any cell value (`memory_store: files-git` holds); the category README and the standards watch note that cite OKF adoption as external validation go to the ripple worklist for Phase 20. INFERENCE from SOURCE and TESTIMONY.

## Claims confronted at v3.3.3

*Enumeration measure:* every claim unit of the report as it stood on 2026-11-04 (the 491-line text this re-read started from, before any edit) was enumerated mechanically — a small stdlib script, run under `python3 -I`, that reads the committed text and prints its regexes, every unit and the totals — and then confronted at v3.3.3, in the script's order (frontmatter first, then body in line order). Five unit kinds: **cell** (frontmatter values: the 15 `memory_features` cells, `learning_loop`, `harness_targets`, `depth`, `version`, `commit`), **citation** (a backticked file name with an optional `:line` or `:a-b`), **count** (a number or spelled cardinal beside a unit noun, an `N of M` pair, `N/M`, `N%`, or an elliptical `N at the old pin`), **correction** (a dated in-place note: `correction`/`corrected` plus a date, `corrected at the deep-dive`, or an italic `*(2026-MM-DD:` amendment) and **other** (benchmark values `0.ddd` and stated numeric config defaults — a fifth kind beyond the four the plan names, kept because eleven units fit no other). Totals: cell 20 · citation 44 · count 77 · correction 10 · other 11 = 162 units. Units are occurrences, so a figure repeated in the text counts each time it appears ("18 tools" five times, "~87 MB" three). `L<n>` in the table is the line in that text. The regexes, as the script prints them:

```
CITE_RE = `([A-Za-z0-9_./*-]+\.(?:rs|md|sh|ps1|toml|json|sql|yaml|yml))(:\d+(?:-\d+)?)?`
COUNT_RE = (?<![\w.:#/@`-])(?:(?P<of>(?:(?:~|\+)?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?|(?i:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|eighteen|twenty|eleventh))\s+of\s+(?:the\s+)?(?:(?:~|\+)?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?|(?i:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|eighteen|twenty|eleventh))(?:\s+(?:distinct|outside|window|SQL|MCP|OKF|cross-cutting|shipped|served|abstention|merged|non-merge|OS-platform|rival|harness|new|competitor)){0,2}\s+(?:lines?|line|commits?|files?|authors?|PRs?|contributors?|tools?|tags?|crates?|events?|invariants?|chars?|char|phrase|branch|values?|value|KiB|KB|MB|dim|systems?|days?|hours?|targets?|schemas?|questions?|variants?|points|months|`\.sh`|`\.ps1`|ProviderChoice|ObservationKind|slice|metric|lines/day|rows?|providers?|seeds|weeks|keys|patches))|(?P<plain>(?:(?:~|\+)?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?|(?i:\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|eighteen|twenty|eleventh)))(?:-|\s+)(?:(?:distinct|outside|window|SQL|MCP|OKF|cross-cutting|shipped|served|abstention|merged|non-merge|OS-platform|rival|harness|new|competitor)(?:-|\s+))?(?:`?[A-Za-z]+`?\s+)?(?:lines?|line|commits?|files?|authors?|PRs?|contributors?|tools?|tags?|crates?|events?|invariants?|chars?|char|phrase|branch|values?|value|KiB|KB|MB|dim|systems?|days?|hours?|targets?|schemas?|questions?|variants?|points|months|`\.sh`|`\.ps1`|ProviderChoice|ObservationKind|slice|metric|lines/day|rows?|providers?|seeds|weeks|keys|patches)(?![\w]))|(?P<pinned>(?:~|\+)?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?\s+at\s+(?:the\s+old\s+pin|v\d|acd9c0b))|(?P<ratio>\d+/\d+(?![\w/]))|(?P<pct>\d+(?:\.\d+)?%))
OTHER_RE = (?<![\w.])0\.\d{3}(?![\d])|\bdefault\s+\d[\d.]*(?![\w.])|`?[a-z_]+\s*=\s*\d+`?
CORR_RE = [Cc]orrect(?:ion|ed)\s+2026-\d\d-\d\d|[Cc]orrect(?:ion|ed)\s+at\s+the\s+deep-dive|\*\(2026-\d\d-\d\d:
```

Figures this definition misses are not units and are not scored: `49 SQL`, `**10** cite`, `cut of **8**`, `18 served)` (two places), `+2,074` and `18 − 10 = 8`; those that changed are carried by the unit that makes the same claim (the "cut of 8" and "18 − 10 = 8" by [#92], the `**10** cite` by [#109], the "18 served" figures by [#89] and [#132]). *Own pin* asks whether a count reproduces at 7e787c9, or at the rev it names; a count is *with* measure when its sentence or the next names the command or definition it came from, and *without* otherwise; a unit with no own-pin test (a quoted wrong figure, a repo-side count, the experiment's own results) carries `—` in both columns.

Verdicts, one sentence each. HOLDS means the claim is still true at v3.3.3 (a figure the report pins to an older rev holds when it reproduces at that rev and is still a true historical statement; the v3.3.3 figure sits beside it in the evidence cell). MOVED means the claim holds but its cited location (file, line, path) moved. CHANGED means the content is no longer true at v3.3.3 (for a cell, the value or the load-bearing sentence in its comment). GONE means the cited subject is removed. When more than one could apply the precedence is GONE > CHANGED > MOVED > HOLDS, and each unit carries exactly one verdict. Grades in the evidence cells are the repo's: SOURCE (read in code or schema at the rev), OBSERVED (the kept run evidence, or a dated `gh` query of repository counts, whose response is not kept), TESTIMONY (the vendor's docs, changelog or commit text, not confirmed in code, and a remote document read once and not kept, such as the OKF spec read of 2026-11-05), INFERENCE.

The per-claim rows came from the confrontation tract and were sampled before use: 25 claims across the three tracts were re-run against the clone, and one failed (the `team_sharing` row had cited an observed `access_mode` value that the kept files do not contain; it is regraded SOURCE). Seven verdicts were changed on the traced chain: [#5], [#8] and [#27] to CHANGED, [#7], [#13], [#15] and [#18] to MOVED.

Tally: 162 claim units — HOLDS 95 · MOVED 22 · CHANGED 44 · GONE 1; with-measure counts reproduced at 7e787c9 60/61, without-measure 1/9.

*(2026-11-05, post-review correction: the tally first read HOLDS 99 · CHANGED 40. Rows [#50], [#51], [#139] and [#140] were scored HOLDS although their own-pin column says "not reproduced"; by the verdict definition above a figure holds only when it reproduces at its rev, so they are CHANGED, like the other not-reproduced counts [#86], [#105], [#109] and [#134]. The total, MOVED, GONE and the with/without-measure figures are unchanged.)*

*Corrected 2026-11-05 (report-conventions audit). Two wording breaks found by a read of all four category-5 deep-dives
against each other, fixed in place with no pin, cell value or verdict moved: the `memory_store`
comment's "only files-git wager" is now "only per-write git-versioned store", because OpenViking's
cell also reads files-git (as plain files plus a caller-requested git snapshot service); and the
zero-LLM bet no longer claims that no other report records it, because the MemPalace and
agentmemory deep-dives do.*

The split is the one the 2026-09-04 re-read recorded (8-for-8 with a measure, 0-for-5 without), and it held on this report's own record again. The single with-measure miss, [#47], stated its `git shortlog` but not its population (55 authors at acd9c0b with `dependabot[bot]`, 54 without; the neighbouring "82" includes the bot). Of the nine without-measure counts, one reproduced — [#49] "64%", and only by merging two author identities; the others did not: [#86] (27 phrases, not 26, at both pins), [#105] ("ten systems" matches no definition), [#109] (11 invariants cite a rival's bug, not ten), [#134] ("24 commits" past an unpinned `main`), and four GitHub-API population figures whose window the sentence never named ([#50], [#51], [#139], [#140]; re-queried, the nearest cut gives 126 merged PRs, 68 from non-owners, 34 logins, against the report's 132, 67 and 34). Two of those misses ([#86], [#109]) were written by the 2026-09-04 audit itself, and one correction, [#92], failed even with a measure — an arithmetic measure over two vendor lists (18 served − 10 named later) measures the subtraction, not the original set.

What moved, by area (every non-HOLDS unit is named here; the table below has the evidence):

- **The pin and the targets.** [#1] and [#2] change by design. [#4]: the same counting rule over `docs/support-matrix.md` gives 40 targets at v3.3.3 (39 if the Claude Desktop Code-tab row folds into Claude Code) against 23 at v2.0.2, which the same script reproduces — drift, not a counting slip. The rule needed one stated extension: the new `--yolo` safety + ai-jail capability row is excluded like the Managed-workstreams row.
- **Cells.** Three cell texts no longer hold. [#17] `team_sharing`: per-project `open`/`restricted` access with read/write grants shipped in 2.5.0; every project still starts `open` and per-page RBAC is still absent. [#5] `learning_loop`: the value `background` holds, but the sentence "Zero-LLM install has no loop" fails — a provider-free cross-project profile pass has been default-on for a single-operator server since 2.6.0 (SOURCE only; the probe never exercised it). [#8] `write_admission`: the evidence gate still describes auto-improve, which needs a provider, but the profile pass admits a standing preference on one sentence carrying an explicit marker, so "say-so does not earn autonomous storage" no longer holds in general. Four cells hold with a moved citation in their comment: [#7], [#13], [#15], [#18]. [#6] to [#20] otherwise hold.
- **Store and migrations.** [#24]: `.sql` files are 98 against 97 migrations (one test fixture), so "all are migrations" no longer holds as an equality; the claim that SQLite is a derived index is unaffected.
- **MCP surface.** 18 served tools became 25: [#32], [#89], [#132] and [#162]. [#90]: the rationale paragraph for the additions names 12 later tools but not the five messaging and handoff-listing tools that are served. [#92]: the original cut was 10, as the deep-dive said, and the 2026-09-04 correction that replaced it with 8 was wrong.
- **Hooks, installer and delivery.** [#21] and [#23]: Antigravity no longer receives `ephemeralMessage`; the native hook emits `injectSteps`, and the vendor's comment says why. [#60]: nine registered Claude Code events became ten. [#22], [#59], [#61], [#62], [#63], [#76] and [#116] are citations that moved (`install_hooks.rs` is 18,351 lines, from 9,875).
- **Ingest and session end.** [#67], [#71] and [#73] moved; [#74] is GONE — `checkpoint_degrades_to_synth` was removed when PreCompact LLM work moved onto the durable worker.
- **Baton and retrieval.** [#82] and [#85] moved; [#107]: the baton also gained "Latest assistant response" and "Last failed tool call"; [#86] is the 27-phrase filter; [#142] the embedder announcement moved into `configure_embedder`; [#127] the stale 0.779 moved into the archived 2.x changelog.
- **Providers.** [#93] and [#94]: ten `ProviderChoice` variants (adds Codex and Cursor); [#95] and [#97] moved.
- **Docs, OKF and repo shape.** [#27]: "no export step forks the truth" is contradicted by its own file at v3.3.3 (the export drops ledgers, regenerates the index and backfills fields; the on-disk tree carries frontmatter-less ledgers outside git). [#34] and [#35] moved. [#41] and [#42]: `ARCHITECTURE.md` is 1,833 lines and its layout block lists 11 crates including `web`. [#54], [#55], [#56] and [#57]: `CLAUDE.md` is 17 lines (an `@AGENTS.md` import plus a comment) and `AGENTS.md` is 845. [#104]: the landscape note is 1,106 lines. [#147]: the stale `active_project.rs` doc comment was fixed.
- **Provenance and velocity.** [#29] (a repo-side count), [#38] and [#39] (120 `.sh`, 103 `.ps1` by `git ls-tree`), [#43] and [#44] (5,396 commits over about 5.5 months), [#47], [#49], [#50], [#51], [#139] and [#140] (GitHub-API population figures that did not reproduce at any cut tried), [#105], [#109], [#110] (the corrected figure is itself 11) and [#134].

Nothing here is a v3.4.0 claim: post-pin material (2026-11-04 onward) is drift and sits only in the release assessment's dated drift subsection.

<details>
<summary>Per-claim verdicts (162 claim units)</summary>

| # | claim unit | kind | measure | own pin | verdict | old wording | evidence at v3.3.3 |
|---|---|---|---|---|---|---|---|
| 1 | `version` (L14) | cell | — | — | CHANGED | "version: v2.0.2" | [OBSERVED] the probe's `ai-memory --version` printed `ai-memory 3.3.3` beside the pin's Cargo.toml 3.3.3 (rule 8b) |
| 2 | `commit` (L15) | cell | — | — | CHANGED | "commit: 7e787c9" | [SOURCE] tag peel `8c39e4e6…` |
| 3 | `depth` (L20) | cell | — | — | HOLDS | — | [INFERENCE] a process cell: it states what the 2026-09-04 re-read traced and what it did not; this re-read did not trace the managed-workstream loop or the retrieval internals, so the "NOT traced" list stays accurate |
| 4 | `harness_targets` (L21) | cell | — | — | CHANGED | "23 harness targets at v2.0.2, counted from docs/support-matrix.md (moved out of the README this window) as rows naming an agent" | [SOURCE] the same rule over `docs/support-matrix.md@v3.3.3` gives **40** (table_rows 49): 25 Supported, 6 MCP-only, 4 MCP-only (documented), 2 Hooks-only, 2 Hooks + MCP, 1 Managed-only; excluded 9 = 5 OS rows (adds NixOS), 2 capability rows (Managed workstreams, and `--yolo` safety + ai-jail, new, excluded by the rule's capability-row logic: a stated extension), 2 provider rows. 39 if the Claude Desktop Code-tab row folds into Claude Code. The same rule reproduces 23 at v2.0.2 and 21 at acd9c0b; Hermes moved Community → Supported |
| 5 | `learning_loop` = `background` (L23) | cell | — | — | CHANGED | "Zero-LLM install has no loop" | [SOURCE] the value holds: `crates/ai-memory-cli/src/config.rs:1797-1803` (scheduler `enabled: true`, `interval_secs: 3_600`, `max_sessions_per_tick: 1`, `experience_every_sessions: 0`), `:1814` `require_approval: false` (the comment's `config.rs:812` moved). The qualifier fails: the cross-project profile pass (since 2.6.0) is a provider-free background writer, default-on for a single-operator server (`crates/ai-memory-core/src/profile.rs:298`, spawned `crates/ai-memory-cli/src/commands/serve.rs:1559`) that injects a digest at SessionStart. The probe never exercised it (`profile_candidates: 0` in `none-2.store-dump.txt`): SOURCE only |
| 6 | `memory_store` = `files-git` | cell | — | — | HOLDS | — | [SOURCE] `docs/ARCHITECTURE.md:756@v3.3.3` "atomic markdown writes, file watcher, git"; nuance: event ledgers are kept out of git, `crates/ai-memory-hooks/src/log.rs:13-15` "Wiki checkpoints leave ledgers out of git" The comment's "natively OKF v0.2-shaped" is about concept pages; see the OKF unit below |
| 7 | `capture_path` = `hook` | cell | — | — | MOVED | — | [SOURCE] `crates/ai-memory-core/src/observation.rs:33-54` — `ObservationKind`, still 10 variants, closed; the comment cites `observation.rs:19-40` |
| 8 | `write_admission` = `evidence-gated` | cell | — | — | CHANGED | "say-so does not earn autonomous storage" | [SOURCE] the value still describes the auto-improve path (`crates/ai-memory-consolidate/src/auto_improve.rs:2152` non-empty evidence required; `:2466` prompt; the path needs a provider, `serve.rs:2461-2463`). The general sentence fails: the profile pass admits a standing cross-project preference on one prompt sentence carrying an explicit marker (`crates/ai-memory-consolidate/src/profile.rs:1585-1586`, markers `:128-138`) or on recurrence in 2 projects (`:1588`), with no provider. Admission webhooks exist since v2.0.2 (`crates/ai-memory-wiki/src/admission.rs`), default chain empty (`config.rs:1476`) |
| 9 | `recall_injection` = `both` | cell | — | — | HOLDS | — | [SOURCE] auto: `crates/ai-memory-cli/src/commands/hook.rs:1216-1251` (`session_start_handoff_envelope`); pull: 25 served tools [OBSERVED `none-2.tools-list.json`]. Comment's "18 served" is now 25 The auto side now carries three items (baton, profile digest, inbox notice) [SOURCE `router.rs:3007`, `:2465-2481`] |
| 10 | `memory_scope` = `[project, user]` | cell | — | — | HOLDS | — | [SOURCE] `hooks/_lib.sh:17-34` (`.ai-memory.toml` walk-up); [TESTIMONY] `docs/users.md:286` "Per-operator memory slots"; new scopes beyond the vocabulary: `_global` and per-user `_profile.<user id>` (`docs/users.md:795-805`) `_global` (written to by explicit `scope: "global"` and by the profile pass) and the per-user `_profile.<user id>` are axes outside the key's legal list; `GLOBAL_SCOPE_PROJECT` exists at v2.0.2 (`crates/ai-memory-core/src/lib.rs:41`), so the old list was already incomplete at its own pin, which is not drift [SOURCE] |
| 11 | `memory_tiers` = `true` | cell | — | — | HOLDS | — | [SOURCE] `crates/ai-memory-core/src/page.rs:22-30` `enum Tier { Working, Episodic, Semantic, …}` |
| 12 | `hybrid_retrieval` = `true` | cell | — | — | HOLDS | — | [OBSERVED] `default-2.embeddings.txt` 2 rows `local / all-MiniLM-L6-v2 / 384`; `default-1.fetch-log-lines.txt` default fetch announcement. Vendor hit@5 now 0.943 local (`docs/benchmarks/longmemeval-s-3.3.3-release.md:50`) [TESTIMONY] `[retrieval] observation_stream` is on by default since 3.0.0 [SOURCE `retrieval_tuning.rs:86`]; unset `embedding_provider` selects `local` (`config.rs:3084-3087`) |
| 13 | `memory_revision` = `auto` | cell | — | — | MOVED | — | [SOURCE] `crates/ai-memory-cli/src/config.rs:1814` `require_approval: false`; the comment cites `config.rs:812` |
| 14 | `decay` = `true` | cell | — | — | HOLDS | — | [SOURCE] `config.rs:1896` `forget_sweep_interval_secs`; `docs/ARCHITECTURE.md:755` "decay math" [TESTIMONY] |
| 15 | `injection_trust_boundary` = `true` | cell | — | — | MOVED | — | [SOURCE] `crates/ai-memory-hooks/src/router.rs:3539-3560` (`render_handoff_markdown_with_budget` pushes "**Security boundary:**" + `UNTRUSTED_MEMORY_NOTICE` + `UNTRUSTED_HISTORY_START`) and the recovery-snapshot renderer at `:2608-2612`; the comment cites `router.rs:1537-1585` |
| 16 | `deployment_mode` = `self-host` | cell | — | — | HOLDS | — | [SOURCE] `config.rs:29` `DEFAULT_BIND: &str = "127.0.0.1:49374"` |
| 17 | `team_sharing` = `attribution-only` | cell | — | — | CHANGED | "RBAC absent BY DESIGN (design-decisions.md §13): attribution records who wrote, never gates whether" | [SOURCE] `crates/ai-memory-store/migrations/V68__project_grants.sql` (`project_grants` user×project → `read`/`write`; `projects.access_mode` `open`/`restricted`), `crates/ai-memory-store/src/project_authz.rs:58-63` `enum AccessMode { Open, Restricted }`, `crates/ai-memory-cli/src/commands/project.rs:44` `access`, enforcement call `crates/ai-memory-hooks/src/recap.rs:85-90` (`grants::authorize_resolved … ProjectAccess::Read`); [TESTIMONY] `docs/users.md:749-770` "each project's **access mode** decides what they may reach (#708)". Default stays `open` [SOURCE `V68__project_grants.sql:38-40` `DEFAULT 'open'`; `[auth] new_projects_restricted` off by default, `config.rs:1037` — no run row was read: `none-2.store-dump.txt` lists `projects: 3` without a row dump]; per-page RBAC still absent (`docs/users.md:820-823`). By the registry definition ("acl (per-container grants; sharing is itself a permission)") the capability is now acl, the default posture attribution-only [INFERENCE] |
| 18 | `harness_installer` = `true` | cell | — | — | MOVED | — | [SOURCE] `crates/ai-memory-cli/src/commands/install_hooks.rs:2329` `fn apply_to_claude_code_settings`; the comment cites `render_shared.rs:36`, now `render_shared.rs:44`, where the array holds 10 events (see the "nine events" unit) |
| 19 | `rule_extraction` = `true` | cell | — | — | HOLDS | — | [SOURCE] `auto_improve.rs:2466` "Rule paths must start with `_rules/`" |
| 20 | `memory_import` = `true` | cell | — | — | HOLDS | — | [SOURCE] `git ls-tree --name-only v3.3.3 companions/` lists `companions/ai-memory-importer` The importer's source family grew (adds agentmemory; `companions/ai-memory-importer/src/agentmemory/mod.rs:1-14`) [SOURCE] |
| 21 | `crates/ai-memory-cli/src/commands/hook.rs:436-447` (L63) | citation | — | — | CHANGED | "`ephemeralMessage` for Antigravity CLI — `crates/ai-memory-cli/src/commands/hook.rs:436-447`" | [SOURCE] `hook.rs:1216-1224`: Antigravity now gets `{"injectSteps":[{"systemMessage":{"systemMessage": handoff}}]}`, comment "an `ephemeralMessage` would be dropped after the first one"; Claude Code `hookSpecificOutput.additionalContext` at `hook.rs:1231-1238` (the final `else` branch of `session_start_handoff_envelope`; `:1243-1250` is `subagent_start_brief_envelope`, a different event, cited here by mistake until the 2026-11-05 post-review correction); new Copilot CLI bare `additionalContext` at :1225-1231 |
| 22 | `install_hooks.rs:3319` (L64) | citation | — | — | MOVED | — | [SOURCE] `install_hooks.rs:5509` `if (handoff) (output as any).system.push(handoff);`; V2 plugin pushes at :4417/:4421 |
| 23 | Correction 2026-09-04 (L65, ephemeralMessage attribution) | correction | — | — | CHANGED | "at the cited line it was Antigravity at both pins" | [SOURCE] the corrected statement no longer holds at v3.3.3: Antigravity no longer receives `ephemeralMessage` (`hook.rs:1217-1224`); `git grep -n ephemeralMessage v3.3.3 -- crates/ai-memory-cli/src/commands/hook.rs` → comment line 1219 only |
| 24 | "58 SQL files" (L69) | count | with | reproduced | CHANGED | "all 58 SQL files are migrations for the derived index (`git ls-files '*.sql'` = the migrations dir; 49 at the old pin)" | [SOURCE] 98 `.sql` vs 97 in `crates/ai-memory-store/migrations` (P1) |
| 25 | "49 at the old pin" (L70) | count | with | reproduced | HOLDS | — | [SOURCE] 49/49 at acd9c0b |
| 26 | "three weeks" (L73) | count | with | reproduced | HOLDS | — | [INFERENCE] 2026-05-21 (first commit, `git log --reverse v3.3.3`) → 2026-06-12 (OKF date as stated, not re-verified) = 22 days |
| 27 | `docs/okf.md:27-31` (L75) | citation | — | — | CHANGED | "the wiki files *are* the OKF files — no export step forks the truth" | [TESTIMONY] the sentence survives at `docs/okf.md:39-41@v3.3.3` (an em dash became a comma) but its own file now contradicts it (`:70-71`): the export drops rotated ledgers, regenerates the root `index.md` and backfills `title`/`description` only in the exported copy; the on-disk tree carries frontmatter-less `log-YYYY-MM.md` ledgers outside git (`crates/ai-memory-hooks/src/log.rs:3-6,13-15`), and the spec location cited is a copy its owner calls frozen [OBSERVED 2026-11-05]. The export is conformant (observed, `none-2.okf-export.txt`); the on-disk tree is not by the spec's letter [INFERENCE] |
| 28 | `docs/ARCHITECTURE.md` (L77, invariant 13 byte-identical) | citation | — | — | HOLDS | — | [SOURCE] invariant 13 block md5 identical at v2.0.2 and v3.3.3 (`awk` extract, 2 lines); now at `docs/ARCHITECTURE.md:1150-1151` |
| 29 | "six seeds" (L80) | count | — | — | CHANGED | "None of the other six seeds in the type makes this bet" | [INFERENCE] repo-side, not a subject count: `git ls-tree --name-only 4f336e1 tools/5-memory/` holds 7 other reports (cognee, everos, mem0, memmachine, memori, memos, openviking) |
| 30 | "~87 MB" (L84) | count | with | reproduced | HOLDS | — | [OBSERVED] `default-1.fetch-log-lines.txt` "fetching the default local embedding model in the background (~87 MB, one time)"; string at `crates/ai-memory-cli/src/commands/serve.rs:3062` |
| 31 | "10-value" (L90) | count | with | reproduced | HOLDS | — | [SOURCE] `observation.rs:33-54` |
| 32 | "18 MCP tools" (L102) | count | with | reproduced | CHANGED | "via 18 MCP tools" | [OBSERVED] 25 served (`none-2.tools-list.json`) |
| 33 | "ten shipped crates" (L116) | count | with | reproduced | HOLDS | — | [SOURCE] `Cargo.toml@v3.3.3` members: 10 shipped crates + `crates/ai-memory-test-support` ("Dev-dependency only; never shipped", its `Cargo.toml:3`) + `evals` (12 members; 11 at v2.0.2) |
| 34 | `docs/ARCHITECTURE.md:361-363` | citation | — | — | MOVED | — | [TESTIMONY] `docs/ARCHITECTURE.md:767-769` "Each crate has a single responsibility …" |
| 35 | `AGENTS.md:193-195` | citation | — | — | MOVED | — | [TESTIMONY] `AGENTS.md:267-269` |
| 36 | "4 crates" (L125, the stub's figure) | count | — | — | HOLDS | — | quoted wrong figure; the statement "it was wrong" still holds (10 shipped) [SOURCE] |
| 37 | corrected at the deep-dive (L125) | correction | — | — | HOLDS | — | [SOURCE] as #33 |
| 38 | "92 `.sh`" (L126) | count | with | reproduced | CHANGED | "92 `.sh` + 82 `.ps1` (`git ls-files`; 84/77 at the old pin)" | [SOURCE] `git ls-tree -r --name-only v3.3.3 \| grep -c '\.sh$'` = 120 |
| 39 | "82 `.ps1`" | count | with | reproduced | CHANGED | "82 `.ps1`" | [SOURCE] same measure = 103 |
| 40 | "84/77" (L126) | count | with | reproduced | HOLDS | — | [SOURCE] 84/77 at acd9c0b |
| 41 | `ARCHITECTURE.md` (L128, 692 lines; layout lists 9 omitting `web`) | citation | — | — | CHANGED | "(692 lines; its own crate-layout block lists 9, omitting `web`" | [TESTIMONY] `docs/ARCHITECTURE.md:750-765@v3.3.3` layout lists 11 incl. `ai-memory-web/` and `ai-memory-test-support/`; file is 1,833 lines |
| 42 | "692 lines" | count | with | reproduced | CHANGED | "(692 lines" | [SOURCE] `git show v3.3.3:docs/ARCHITECTURE.md \| wc -l` = 1833 |
| 43 | "1,580 commits" (L131) | count | with | reproduced | CHANGED | "1,580 commits in ~3.5 months (1,276 at the old pin)" | [SOURCE] `git rev-list --count v3.3.3` = 5396 |
| 44 | "~3.5 months" | count | with | reproduced | CHANGED | "~3.5 months" | [SOURCE] 2026-05-21 → 2026-11-03 ≈ 5.5 months |
| 45 | "1,276 at the old pin" | count | with | reproduced | HOLDS | — | [SOURCE] `git rev-list --count acd9c0b` = 1276 |
| 46 | correction 2026-09-04 (L132, "solo author") | correction | — | — | HOLDS | — | [SOURCE] `git shortlog -s v3.3.3 \| wc -l` = 207 authors; substance (not solo) strengthened |
| 47 | "54 distinct authors" (L133) | count | with | not reproduced | CHANGED | "`git shortlog` showed 54 distinct authors at acd9c0b" | [SOURCE] `git shortlog -s acd9c0b \| wc -l` = 55 (also 55 under each pin's `.mailmap`); 54 only if `dependabot[bot]` is excluded — a population the sentence does not name |
| 48 | "82 at v2" | count | with | reproduced | HOLDS | — | [SOURCE] `git shortlog -s v2.0.2 \| wc -l` = 82 (this one *includes* `dependabot[bot]`: two populations in one sentence) |
| 49 | "64%" (L133) | count | without | reproduced | CHANGED | "Akita is 64% of non-merge commits" | [SOURCE] at v2.0.2 (AkitaOnRails 715 + Fabio Akita 29)/1160 non-merge = 64.1% (61.6% for the single identity); at v3.3.3 (1727 + 30)/3668 = 47.9% |
| 50 | "67 of the 132 PRs" (L134) | count | without | not reproduced | CHANGED | — | Closed-window figure the new pin cannot change, but a historical figure holds only when it reproduces at its own rev and this one does not, so it takes CHANGED (2026-11-05 post-review correction; first scored HOLDS). Re-queried 2026-11-05 (`gh pr list -R akitaonrails/ai-memory --state merged --search "merged:<acd9c0b committer time>..<end>"`, authors by login): to the v2.0.2 tag time 121 merged, 63 non-owner, 32 logins; to 2026-09-04T23:59:59Z 126 / 68 / 34 — no obvious window gives 132 / 67 / 34 [OBSERVED, closed window] |
| 51 | "34 outside contributors" (L135) | count | without | not reproduced | CHANGED | — | as #50 (34 outside contributors: 34 logins at the 2026-09-04T23:59:59Z cut, 32 at the tag time; the PR count beside it does not reproduce). |
| 52 | "123 of the 304 window commits" (L136) | count | with | reproduced | HOLDS | — | [SOURCE] 123 commits in acd9c0b..v2.0.2 whose body matches `co-authored-by:.*claude` case-insensitively (104 with case-sensitive `^Co-Authored-By: Claude`) |
| 53 | "40%" | count | with | reproduced | HOLDS | — | 123/304 = 40.5% |
| 54 | `CLAUDE.md` (L137, "7-line redirect") | citation | — | — | CHANGED | "`CLAUDE.md` is a 7-line redirect to a 446-line `AGENTS.md`" | [SOURCE] `CLAUDE.md:1@v3.3.3` is `@AGENTS.md` (an import) + a 15-line comment; 17 lines |
| 55 | "7-line" | count | with | reproduced | CHANGED | "7-line redirect" | 17 lines |
| 56 | "446-line" | count | with | reproduced | CHANGED | "446-line `AGENTS.md`" | `AGENTS.md` 845 lines |
| 57 | `AGENTS.md` (L138, 446-line) | citation | — | — | CHANGED | "a 446-line `AGENTS.md`" | 845 lines |
| 58 | `AGENTS.md` (L138, opens with managed block) | citation | — | — | HOLDS | — | [SOURCE] `AGENTS.md:1` `<!-- ai-memory:start -->` |
| 59 | `crates/ai-memory-cli/src/commands/install_hooks.rs:1442` | citation | — | — | MOVED | — | [SOURCE] `install_hooks.rs:2329` |
| 60 | "nine events" (L148) | count | with | reproduced | CHANGED | "registering nine events" | [SOURCE] `render_shared.rs:44` `[(&str, &str); 10]` — adds `("PostToolUseFailure", "post-tool-use.sh")` (:49) |
| 61 | `crates/ai-memory-cli/src/commands/render_shared.rs:36` | citation | — | — | MOVED | — | [SOURCE] `render_shared.rs:44` |
| 62 | `render_shared.rs:1262` | citation | — | — | MOVED | — | [SOURCE] `render_shared.rs:2115-2121` `fn current()` → `Self::PosixNative` |
| 63 | `commands/hook.rs:119` | citation | — | — | MOVED | — | [SOURCE] `hook.rs:139-142` `fn should_incremental_drain` |
| 64 | `hooks/claude-code/session-end.sh` | citation | — | — | HOLDS | — | [SOURCE] `session-end.sh:20` via `ai_memory_post_hook` → `hooks/_lib.sh:976-1000` (`curl … --max-time 0.2`) |
| 65 | `_lib.sh` | citation | — | — | HOLDS | — | [SOURCE] `hooks/_lib.sh:17-34` (walk up to `$HOME`, or checkout root outside HOME) |
| 66 | `.ai-memory.toml` | citation | — | — | HOLDS | — | [SOURCE] `hooks/_lib.sh:17` |
| 67 | `crates/ai-memory-core/src/sanitize.rs:265` | citation | — | — | MOVED | — | [SOURCE] `sanitize.rs:878` `pub fn new(mut obs: NewObservation, sanitizer: &Sanitizer) -> Self` in `impl Sanitized<NewObservation>` (:865) |
| 68 | corrected 2026-09-04 (L169, `sanitize()`) | correction | — | — | HOLDS | — | [SOURCE] invariant 6 still says "no other constructor than `sanitize()`" (`docs/ARCHITECTURE.md:1113-1114`); `git grep -n 'fn sanitize\b\|fn sanitize(' v3.3.3 -- crates/` → nothing |
| 69 | "16 KiB" (L171) | count | with | reproduced | HOLDS | — | [SOURCE] `sanitize.rs:72` `OBSERVATION_BODY_MAX_BYTES: usize = 16 * 1024` |
| 70 | "2 KB tool" | count | with | reproduced | HOLDS | — | [SOURCE] `crates/ai-memory-hooks/src/payload.rs:25` `TOOL_EXCERPT_MAX_BYTES: usize = 2_000` |
| 71 | `crates/ai-memory-hooks/src/synth.rs:29` | citation | — | — | MOVED | — | [SOURCE] `synth.rs:54` `pub fn synthesize_session_page(`; caps `:37-39`; `tier: Tier::Episodic` `:89` |
| 72 | "500-line" | count | with | reproduced | HOLDS | — | [SOURCE] `synth.rs:37` `RAW_OBSERVATION_MAX_LINES: usize = 500` |
| 73 | `router.rs` (L180, degrade-to-rule-based) | citation | — | — | MOVED | — | [SOURCE] mechanism now in the durable worker: `crates/ai-memory-cli/src/commands/serve.rs:875-883` `is_terminal_session_consolidation_error` (non-transient LLM errors terminal; "the heuristic page the SessionEnd hook already wrote remains", :871) |
| 74 | `router.rs:3159` (`checkpoint_degrades_to_synth`) | citation | — | — | GONE | "(`router.rs`, `checkpoint_degrades_to_synth`, now at `router.rs:3159`)" | [SOURCE] `git grep -n 'checkpoint_degrades\|degrades_to_synth' v3.3.3 -- crates/` → nothing; removed in `ad1ff4331` "Merge PR #1243: fix(hooks): queue PreCompact LLM work on the durable worker (#1229)" |
| 75 | `hooks/claude-code/session-start.sh` | citation | — | — | HOLDS | — | [SOURCE] `session-start.sh:38-41` |
| 76 | `commands/hook.rs:436` | citation | — | — | MOVED | — | [SOURCE] `commands/hook.rs:436` was the head of `session_start_handoff_envelope` at 7e787c9 (`git show 7e787c9:crates/ai-memory-cli/src/commands/hook.rs`, lines 436-450); at v3.3.3 the same function starts at `hook.rs:1216` (Claude Code branch `:1231-1238`). The first scoring mapped it to `:1243-1250`, which is `subagent_start_brief_envelope`; the MOVED verdict holds at the right target (2026-11-05 post-review correction) |
| 77 | `crates/ai-memory-consolidate/src/auto_improve_schedule.rs` | citation | — | — | HOLDS | — | [SOURCE] file present at v3.3.3; defaults `config.rs:1795-1806` |
| 78 | "default 3600" (L194) | other | — | — | HOLDS | — | [SOURCE] `config.rs:1799` `interval_secs: 3_600` |
| 79 | `projection.rs` | citation | — | — | HOLDS | — | [SOURCE] `crates/ai-memory-consolidate/src/projection.rs` present |
| 80 | "default 0.75" (L201) | other | — | — | HOLDS | — | [SOURCE] `auto_improve.rs:93` `DEFAULT_AUTO_IMPROVE_MIN_CONFIDENCE: f32 = 0.75` |
| 81 | `docs/auto-improvement-loop.md` | citation | — | — | HOLDS | — | [TESTIMONY] `:51` "An ai-memory equivalent of Hermes Agent's self-improvement loop", `:76` "## Hermes Findings" |
| 82 | `crates/ai-memory-hooks/src/router.rs:2909` | citation | — | — | MOVED | — | [SOURCE] `router.rs:5746` `fn build_auto_handoff(`; still first+last prompt, tool names, `files_touched: Vec::new()` (:5847); grew "Last failed tool call" and "Latest assistant response" (double opt-in) (:5813-5825) |
| 83 | "1,500 chars" (L223) | count | with | reproduced | HOLDS | — | [SOURCE] `router.rs:5761` `const MAX: usize = 1500;` |
| 84 | "4-branch" (L226) | count | with | reproduced | HOLDS | — | [SOURCE] `router.rs:5870ff` comments "Heuristic 1" … "Heuristic 4" |
| 85 | `router.rs:3009` | citation | — | — | MOVED | — | [SOURCE] `router.rs:5870` `fn derive_open_questions(` |
| 86 | "26-phrase" (L228) | count | without | not reproduced | CHANGED | "with a 26-phrase acknowledgment filter" | [SOURCE] `ACK_PHRASES` has **27** entries at `router.rs:3089-3117@v2.0.2` (19 Latin + 8 CJK) and identically at `router.rs:5945-5973@v3.3.3` (`diff` empty) |
| 87 | "0/10" (L232) | count | — | — | HOLDS | — | repo experiment (exp-04 at acd9c0b-era), `experiments/04-memory-continuity/README.md:97-98@4f336e1`; not re-measured at v3.3.3 |
| 88 | "10/10" (L233) | count | — | — | HOLDS | — | same, `:99` |
| 89 | "18 MCP tools" (L244) | count | with | reproduced | CHANGED | "18 MCP tools (read-only vs destructive hints declared per tool; run-verified 2026-09-04: 18 served)" | [OBSERVED] 25 served |
| 90 | `docs/ARCHITECTURE.md` (L246, "each addition argued … against §10") | citation | — | — | CHANGED | "each addition argued in `docs/ARCHITECTURE.md` against §10 of `design-decisions.md`" | [TESTIMONY] the rationale paragraph `docs/ARCHITECTURE.md:818-851` names 12 later tools but none of `memory_message_send/list/pop/cancel` or `memory_handoff_list`, which are served; it closes "the count is now 25, not 10" (:851) |
| 91 | `design-decisions.md` (§10) | citation | — | — | HOLDS | — | [TESTIMONY] `docs/design-decisions.md:206` "## 10. MCP tool surface - narrow on purpose" |
| 92 | correction 2026-09-04 (L247, "cut of 8") | correction | — | — | CHANGED | "the original cut was 18 − 10 = 8 — true at both pins" | [TESTIMONY] the original §10 (`docs/design-decisions.md:154ff@836d8e68`, the file's adding commit, 2026-05-21) lists **10** tools; the vendor now writes "the count is now 25, not 10" (`docs/ARCHITECTURE.md:851@v3.3.3`). The subtraction 18 − 10 failed because original tools were renamed or retired (`memory_forget`, `memory_remember`, `memory_session_summary` are absent from the 25 served). The deep-dive's original "cut of 10" was right; the correction introduced the error |
| 93 | "eight `ProviderChoice` variants" (L257) | count | with | reproduced | CHANGED | "eight `ProviderChoice` variants" | [SOURCE] `crates/ai-memory-llm/src/factory.rs:29-51`: 10 (adds `Codex`, `Cursor`) |
| 94 | correction 2026-09-04 (L258, providers) | correction | — | — | CHANGED | "`factory.rs:25-42` has 8 at both pins — Anthropic, OpenAI, Gemini, OpenAI-compat, OpenAI-OAuth, Copilot, Anthropic-OAuth, OpenCode" | [SOURCE] as #93 |
| 95 | `factory.rs:25-42` | citation | — | — | MOVED | — | [SOURCE] `factory.rs:29-51` |
| 96 | "9-value" (L262) | count | with | reproduced | HOLDS | — | [SOURCE] `crates/ai-memory-llm/src/types.rs:250-269` `enum ReasoningEffort` (None … Persistent, 9) |
| 97 | `types.rs:145-181` | citation | — | — | MOVED | — | [SOURCE] `types.rs:250-269` |
| 98 | `render_shared.rs` (L266) | citation | — | — | HOLDS | — | [SOURCE] per-harness event arrays still there (`render_shared.rs:8`, `:44`) |
| 99 | `install_hooks.rs` (L266) | citation | — | — | HOLDS | — | [SOURCE] present, 18,351 lines |
| 100 | "15 cross-cutting invariants" (L279) | count | with | reproduced | HOLDS | — | [TESTIMONY] `docs/ARCHITECTURE.md:1088-1159`, items 1–15 |
| 101 | `docs/issues-*.md` | citation | — | — | HOLDS | — | [SOURCE] 4 `docs/issues-*` files at both pins |
| 102 | correction 2026-09-04 (L283, invariants) | correction | — | — | HOLDS | — | [TESTIMONY] exceptions still exact: invariants 10/13/14 cite nothing, 6 cites `#196` (internal). Note: those four exceptions imply 11 citing, not 10 (#109) |
| 103 | `docs/research-2026-landscape.md` | citation | — | — | HOLDS | — | [TESTIMONY] `:129` "**File-first wiki memory** \| **us**, basic-memory, OKF, …" |
| 104 | "232 lines" | count | with | reproduced | CHANGED | "`docs/research-2026-landscape.md` (232 lines)" | [SOURCE] 1,106 lines |
| 105 | "ten systems" | count | without | not reproduced | CHANGED | "surveys ten systems the original notes never covered" | [TESTIMONY] no definition yields ten: the §3 camp table at `:74-80@v2.0.2` names 15+ representatives; at v3.3.3 §3 adds "New entrants raised in issue #810" (:377) and two refreshes (:553, :667) |
| 106 | "`max_sessions_per_tick = 1`" (L299) | other | — | — | HOLDS | — | [SOURCE] `config.rs:1800` |
| 107 | dated note 2026-09-04 (L306, "minus one field") | correction | — | — | CHANGED | "still true at v2.0.2 minus one field — `open_questions` grew a 4-branch heuristic" | [SOURCE] `router.rs:5813-5835`: the baton also gained "Latest assistant response" (Stop excerpt, double opt-in) and "Last failed tool call"; turn-checkpoint batons `router.rs:5265-5278` |
| 108 | "4-branch" (L306) | count | with | reproduced | HOLDS | — | as #84 |
| 109 | "Ten of fifteen invariants" (L312) | count | without | not reproduced | CHANGED | "Ten of fifteen invariants pinned to a named bug in a rival memory tool" | [TESTIMONY] items naming a rival project + issue number: 1,2,3,4,5,7,8,9,11,12,15 = **11** at v2.0.2 and v3.3.3 |
| 110 | Corrected 2026-09-04 (L314, Surprise 3) | correction | — | — | CHANGED | "originally "each pinned … in a solo-author repo"" | the corrected figure is itself 11 (#109); the solo half holds |
| 111 | `install_hooks.rs` (L317) | citation | — | — | HOLDS | — | historical (7,801 at acd9c0b) |
| 112 | "7,801 lines" (L318) | count | with | reproduced | HOLDS | — | [SOURCE] acd9c0b 7801 (v3.3.3: 18,351) |
| 113 | "9,875 at v2" | count | with | reproduced | HOLDS | — | [SOURCE] v2.0.2 9875 |
| 114 | "16 days" | count | with | reproduced | HOLDS | — | 2026-08-18 → 2026-09-03 |
| 115 | "two new harness targets" | count | with | reproduced | HOLDS | — | 21 → 23 (ZCode, Pool) [SOURCE] |
| 116 | `commands/hook.rs:160` | citation | — | — | MOVED | — | [SOURCE] `hook.rs:424` "kimi-code discards SessionStart …" |
| 117 | `docs/llm-provider-comparison.md` | citation | — | — | HOLDS | — | present |
| 118 | "7-slice" (L350) | count | with | reproduced | HOLDS | — | [TESTIMONY] `docs/benchmarks/longmemeval-s-2026-09-01-local.md:11-17` (6 slices + overall) |
| 119 | "8-metric" | count | with | reproduced | HOLDS | — | same file `:9` header (hit@1/3/5/10, recall@1/3/5/10) |
| 120 | "0.823" (L350) | other | — | — | HOLDS | — | historical run file present; current release run 0.943 local (`longmemeval-s-3.3.3-release.md:50`) [TESTIMONY] |
| 121 | "0.668" | other | — | — | HOLDS | — | historical file present |
| 122 | "0.617" | other | — | — | HOLDS | — | historical file present |
| 123 | "0.967" | other | — | — | HOLDS | — | still cited in `docs/benchmarks/` (7 hits) |
| 124 | "6.6 points" | count | with | reproduced | HOLDS | — | [TESTIMONY] `docs/benchmarks/README.md:144` (was :24) |
| 125 | "2 KB" (L353) | count | with | reproduced | HOLDS | — | as #70 |
| 126 | "30 abstention questions" | count | with | reproduced | HOLDS | — | `longmemeval-s-2026-09-01-local.md:7`; still no separate abstention report (`git ls-tree -r --name-only v3.3.3 docs \| grep -i abstention` → nothing) |
| 127 | "0.779" (L357, stale CHANGELOG figure) | other | — | — | MOVED | — | [TESTIMONY] `CHANGELOG.md` no longer carries it; `docs/changelog/2.x.md:4501` "from 0.617 (FTS-only) to 0.779 with local embeddings" (still stale) |
| 128 | "0/10" (L364) | count | — | — | HOLDS | — | as #87 |
| 129 | "10/10" (L365) | count | — | — | HOLDS | — | as #88 |
| 130 | "~80-char" (L368) | count | with | reproduced | HOLDS | — | [SOURCE] `sanitize.rs:904-905` `truncate_for_title` `MAX: usize = 80` (at v2.0.2 in `payload.rs:906-907`) |
| 131 | dated note 2026-09-04 (L372, schema scar) | correction | — | — | HOLDS | — | [SOURCE] `config.rs:500` `strip_root_combinators`, default `false` `:1442`; [OBSERVED] PROBE `TOOLS none-2 served=25 root_combinators=0` |
| 132 | "18 served schemas" (L375) | count | with | reproduced | CHANGED | "18 served schemas, zero root combinators, no flag" | 25 served, zero root combinators [OBSERVED] |
| 133 | "304 commits" (L385) | count | with | reproduced | HOLDS | — | `git rev-list --count acd9c0b..v2.0.2` = 304 |
| 134 | "24 commits" (L385) | count | without | not reproduced | CHANGED | "`main` is 24 commits past the tag, outside this pin" | unpinned ref; `git rev-list --count --first-parent --until=<t> v2.0.2..origin/main` gives 11 (09-04 00:00) → 21 (09-05 00:00), all-parents 30 → 63; no cut gives 24 [INFERENCE] |
| 135 | "18 tags" (L391) | count | with | reproduced | HOLDS | — | `git tag --merged v2.0.2 \| wc -l` − same for acd9c0b = 108 − 90; still no rc/beta/alpha tag at v3.3.3 (152 tags) |
| 136 | "16-day" | count | with | reproduced | HOLDS | — | as #114 |
| 137 | "25 hours" (L392) | count | with | reproduced | HOLDS | — | v2.0.0 2026-09-02T12:51 → v2.0.2 2026-09-03T13:48 = 24 h 57 min |
| 138 | "17 days" (L396) | count | with | reproduced | HOLDS | — | 2026-08-18 → 2026-09-04 |
| 139 | "67 of 132 merged window PRs" (L396) | count | without | not reproduced | CHANGED | — | as #50. |
| 140 | "34 outside contributors" (L396) | count | without | not reproduced | CHANGED | — | as #51. |
| 141 | "~87 MB" (L402) | count | with | reproduced | HOLDS | — | as #30 |
| 142 | `serve.rs:1817-1887` | citation | — | — | MOVED | — | [SOURCE] `serve.rs:3026` `async fn configure_embedder(`; announcement `:3062` |
| 143 | "0.617" (L407) | other | — | — | HOLDS | — | as #122 |
| 144 | "0.823" (L407) | other | — | — | HOLDS | — | as #120 |
| 145 | "default 0" (L415, `experience_every_sessions`) | other | — | — | HOLDS | — | [SOURCE] `config.rs:1802` |
| 146 | `docs/temporal.md` | citation | — | — | HOLDS | — | present |
| 147 | `active_project.rs:22` (stale doc) | citation | — | — | CHANGED | "`active_project.rs:22` still narrates `Single` as the default its own enum no longer has" | [SOURCE] `crates/ai-memory-core/src/active_project.rs:22` now "The `Single` mode keeps the pre-v1.39 behaviour"; `#[default] PerActor` `:103-104` — the doc was fixed |
| 148 | "~130 lines" (L457) | count | with | reproduced | HOLDS | — | 2,074 / 16 = 129.6 |
| 149 | `install_hooks.rs` (L457) | citation | — | — | HOLDS | — | historical |
| 150 | "two new targets" (L457) | count | with | reproduced | HOLDS | — | as #115 |
| 151 | "seven providers" (L464, audit list) | count | — | — | HOLDS | — | quoted wrong figure; the audit statement stands |
| 152 | "84/77" (L466) | count | with | reproduced | HOLDS | — | as #40 |
| 153 | "619 lines" | count | with | reproduced | HOLDS | — | `docs/ARCHITECTURE.md` at acd9c0b = 619 lines |
| 154 | "1,276 commits" | count | with | reproduced | HOLDS | — | as #45 |
| 155 | "7,801 lines" | count | with | reproduced | HOLDS | — | as #112 |
| 156 | "18 tools" (L467, audit list) | count | with | reproduced | HOLDS | — | the audit record stands; current figure 25 |
| 157 | "15 invariants" | count | with | reproduced | HOLDS | — | as #100 |
| 158 | "10 ObservationKind values" | count | with | reproduced | HOLDS | — | as #31 |
| 159 | "~87 MB" (L477) | count | with | reproduced | HOLDS | — | as #30 |
| 160 | "three of the four OKF keys" (L483) | count | with | reproduced | HOLDS | — | [OBSERVED] `none-1.session-page.md`: `type`, `sources`, `generated` present, no `stale_after`; adds `description` |
| 161 | `index.md` (L485, none in a fresh store) | citation | — | — | HOLDS | — | [OBSERVED] `none-1.store-dump.txt` wiki listing: no `index.md` on disk |
| 162 | "18 tools" (L487) | count | with | reproduced | CHANGED | "served 18 tools with" | 25 served, 0 root combinators [OBSERVED] |

</details>

## Run probe — 2026-11-05 (v3.3.3 official release binary; tag = release, so probing the release probes the pin)

The sha256-verified `ai-memory-linux-x86_64.tar.gz` (22,577,275 bytes, sha256 `726616b3e389beeef073001411603154c512812d49a2a6b1195e93ad25579a14`; the release's companion checksum file passes `sha256sum -c` and the GitHub release API's asset digest is the same value), listed with `tar -tzf` before extraction (no absolute or `..` path) and extracted into an empty directory. `ai-memory --version` printed `ai-memory 3.3.3`, and the pin's Cargo.toml version is 3.3.3 (rule 8b: the observed binary and the pinned source agree). Four server runs, each from a scratch environment (scratch `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `AI_MEMORY_HOME` and `--data-dir`, `PATH=/usr/bin:/bin`) under `strace -f` (connect, sendto, sendmsg, openat); the success of each run is read from that run's own store copy, `<data_dir>/db/memory.sqlite` plus the wiki listing, never from an exit code (rule 5e). The evidence is kept, not committed: the gitignored `upstream/_runtimes/`, described in [`upstream/README.md`](../../upstream/README.md). `<scratch>` stands for any scratch path below.

1. **Embedder off, one synthetic session (run none-1).** `serve --transport http --bind 127.0.0.1:<port>` with `AI_MEMORY_EMBEDDING_PROVIDER=none` and no LLM provider (the server log says `AI_MEMORY_LLM_PROVIDER unset`). Three hook events (session-start, user-prompt, session-end over `POST /hook`) each answered 202 `queued` with a 6-byte body. Store: `sessions=1 observations=3 pages=1 page_embeddings=0 wiki_files=5`; the page is `sessions/<id>.md`, tier episodic, with `type: Session Summary`, `sources:` (an `ai-memory://session/…` resource), and `generated: {by: process:ai-memory/3.3.3, at: …}`. Three separate claims. *zero-LLM: yes* — no provider is configured and the page is the deterministic synthesis. *zero-egress: yes, as observed* — strace over the server process tree shows no non-loopback `connect` and no resolver contact (0 and 0); the instrument covers the server process tree only (`strace -f`), the thin-client commands of item 4 are not traced (their traffic is loopback by configuration, not by measurement), and "none observed over one short run" is not a proof of absence. *zero-spend: yes* — no provider, no key, no metered call. The readiness line reads `auth=false`: the probe started `serve` without `init`, so it exercised the token-less posture of a 2.x-shaped install, not the fresh-`init` root-bearer-token default 3.0.0 introduced.
2. **The served MCP surface (run none-2).** `tools/list` over `POST /mcp` (stateless HTTP, `Accept: application/json, text/event-stream`) served **25** tools, 0 with a root `oneOf`/`anyOf`/`allOf` (v2.0.2 served 18, also 0). The 25 equals the registry count of `#[tool(` attributes inside the `#[tool_router]` impl, read from source; a grep of `Tool::new|#[tool(` gives 26 code sites and is not the served count.
3. **PreCompact, the run half of the #1983 re-trace (run none-2, same data dir, so counts are cumulative).** A `POST /hook?event=pre-compact&agent=claude-code` for the none-1 session answered 202 `queued` and produced no server-log line. Store before: `observations=3 pages=1`; after 5 s: `observations=4 pages=2` — one new `pre-compact` observation with an empty body, and a re-versioned `sessions/<id>.md` (the old row `is_latest=0`, the new one `is_latest=1`). Nothing came back for injection. The probe sent it after that session's `session-end`, and the server re-versioned the ended session's page anyway. After the run: `sessions=2 observations=7 pages=4 page_embeddings=0 wiki_files=9`.
4. **Thin clients and the OKF export (run none-2).** `write-page` and `search` reached the server through a one-line `<data_dir>/config.toml` (`bind = …`). `export-okf --workspace default --project <name>` is an HTTP client of `POST /admin/export-okf`, so it needs a running server (loopback, no LLM); it produced a 663-byte tarball of three files: a root `index.md` whose frontmatter is only `okf_version: "0.2"` over a heading and a list, `_meta.md` (`type: Scope Manifest`) and the session page (`type: Session Summary`); no `log.md`.
5. **Default embedder, first start (run default-1).** No `AI_MEMORY_EMBEDDING_PROVIDER` set — the as-shipped path. The log announces "fetching the default local embedding model in the background (~87 MB, one time); hybrid search enables on the next start" and then one fetch line per file (`model.safetensors`, `tokenizer.json`, `config.json`); all three landed within 15 s in `<data_dir>/models/all-MiniLM-L6-v2/` (90,868,376, 466,247 and 612 bytes), and the sha256 of each equals the digest pinned in `MODEL_FILES` in `crates/ai-memory-llm/src/local.rs` at the pin (3 of 3). This boot wrote 0 embedding rows: store `sessions=1 observations=3 pages=1 page_embeddings=0 wiki_files=5`. Three separate claims. *zero-LLM: yes* — the embedder is a non-generative candle BERT; nothing generative ran. *zero-egress: no* — the as-shipped fetch: 26 non-loopback `connect` lines and 4 resolver contacts under strace (2 on port 443, 24 on port 0 — by INFERENCE libc address-selection connects after name resolution; the trace holds addresses, not host names, and the destination is huggingface.co by the log line and the base URL in `local.rs`, not by the trace). *zero-spend: yes* — keyless download, no provider, no metered call.
6. **Default embedder, second start (run default-2).** The log says `embedder enabled provider="local" model="all-MiniLM-L6-v2" dim=384` and a startup backfill (`scopes=2 embedded=1 skipped=0 failed=0`) embedded the first run's page; the new session page was embedded too. `page_embeddings=2`, one (provider, model, dim) triple, `local / all-MiniLM-L6-v2 / 384`, 1,536-byte vectors (384 × 4 bytes); store `sessions=2 observations=6 pages=2 wiki_files=8`. *zero-LLM: yes; zero-egress: yes, as observed* — the weights were already on disk, and strace shows 0 non-loopback connects and 0 resolver contacts, with the instrument limit of item 1. *zero-spend: yes.*
7. **The operator's live state was not touched.** The strace `openat` scan shows 0 hits on the operator's real ai-memory data, agent-config and secret locations for every one of the four runs; no installer, `setup`, `run` or `init` command was executed.
8. **Probe mechanics for the next re-read.** The scratch variables above and `--data-dir`; `serve --transport http --bind 127.0.0.1:<port>` (stdio is the default transport and exits when stdin closes); two starts for the default embedder (the fetching start, then the embedding start); the data dir's `models` entry pointed by symlink at a kept weights directory so the ~87 MB fetch happens once across probes — the server accepted it, and the weights landed straight in the kept directory. `HF_HOME` is read nowhere (`git grep -n HF_HOME v3.3.3` prints nothing, nor at v2.0.2), so it cannot redirect the weights. Thin clients find the server through the data dir's `config.toml`.

## Release history

One dated row per read of this tool, oldest first. The three sections that carried the first rows in full (the 2026-08-19 run probe, the v2.0.2 release assessment and the 2026-09-04 run probe) are compressed here; their claims were each confronted at v3.3.3 in the verdict table above, and [experiment 04](../../experiments/04-memory-continuity/README.md) keeps its own artifacts at its own pin.

| Date | Version · pin | What was observed or assessed | What it settled |
|---|---|---|---|
| 2026-08-18 | after v1.28.1 · acd9c0b | Stub and same-day deep-dive: capture → consolidate → handoff traced in source (`hooks/`, `ai-memory-hooks`, `ai-memory-consolidate`), the Claude Code installer read end-to-end, the MCP surface read at router and architecture level. | The zero-LLM pipeline, the hook-fragmentation surface and a handoff baton that is a heuristic paragraph, not a compiled summary; the auto-approving learning loop (`require_approval = false`); the ADR-0013 cell block was set from this read. |
| 2026-08-19 | v1.28.1 release binary · acd9c0b | Run probe, exp-04: planted facts, a second harness. The auto-improve reviewer rejected all 12 conversational-fact candidates; v1.28.1's `memory_read_page` schema (top-level `oneOf`) was rejected by the Anthropic API and fixed at that pin by `strip_root_combinators`, shipped default-off. | Continuity is real and entirely pull-shaped: the baton buys nothing for mid-session facts (0/10 even with injection enabled), pull recovers everything (10/10 verbatim, cross-harness equal to same-harness) — [exp-04](../../experiments/04-memory-continuity/README.md), conclusion 14; `write_admission: evidence-gated` measured; the docs/source/run triple (rule 8). |
| 2026-09-04 | v2.0.2 · 7e787c9 | Release assessment acd9c0b → 7e787c9 (304 commits, 18 tags in 16 days): hybrid retrieval default-on (an unconfigured install fetches a MiniLM embedder), OKF v0.2 native pages, the opt-in experience pass, temporal `as_of` (non-functional on zero-LLM stores until 2.0.2), typed relation edges, scope hardening, `purge-session`, a multi-user posture. | Five claims that never reproduced at their own pin were corrected in place (solo author; "each" invariant cites a bug; `ephemeralMessage` for OpenCode; cut of 10; seven providers) and counts that carry a measure reproduced 8-for-8 against 0-for-5 without one; two of those corrections were themselves re-corrected on 2026-11-05 (the cut of 10 was right, and the invariants count is 11). |
| 2026-09-04 | v2.0.2 · 7e787c9 | Run probe of the sha256-verified release binary (`ai-memory 2.0.2`): the default embedder fetch announced and begun; OKF keys live on a zero-LLM session page (three of four); `tools/list` served 18 tools with zero root combinators, no flag; `serve` speaks MCP on stdio by default and the HTTP MCP endpoint is stateless. | The default is no longer egress-free; the interop scar was fixed at the source (#577), not by the flag; the probe mechanics reused on 2026-11-05. |
| 2026-11-05 | v3.3.3 · 7e787c9 → 8c39e4e67 | Release re-read: 44 releases, 896 first-parent commits (452 + 444 across v3.0.0), 162 claim units confronted, four zero-LLM runs of the official release binary — see the release assessment, the claims-confronted table and the run probe above. | A provider-free profile pass changes what a zero-LLM install learns, per-project grants change `team_sharing`, the served MCP surface is 25 tools, and the hook-installer surface keeps compounding; the pin moved under rule 4b. |
