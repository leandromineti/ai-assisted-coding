---
name: cognee
category: 5
type: memory
vendor: Topoteretes (topoteretes)
url: https://github.com/topoteretes/cognee
license: Apache-2.0
open_source: true
stack: [Python, TypeScript]
version: v1.5.0-2-gb948f88d4
commit: b948f88d4
first_commit: 2023-08-16
stars: 30103
stars_at: 2026-08-18
read_at: 2026-08-18   # survey read, same day as the stub
depth: survey   # read: README, cognee-mcp/src/server.py (tool surface + save_interaction + improve + tool modes), codingagents/coding_rule_associations.py (top), pyproject dependency spec, evals/README. Cross-examined against ai-memory's docs/issues-cognee.md (competitor testimony, 2026-05-21) with two structural claims spot-checked in source at the pin. NOT read: the core pipeline internals (cognify tasks, retrievers), the frontend, the separate cognee-integrations repo (README via GitHub API only)
harness_targets: "in-repo: cognee-mcp (MCP server, stdio/HTTP, agent-scoped datasets per client). Separate repos/packages, README-level: Claude Code marketplace plugin (cognee-integrations — hooks capture, prompt-submit injection, session-end graph sync; a Codex plugin shares its config), OpenClaw plugin (@cognee/cognee-openclaw on npm)"
features:
  learning_loop: false   # checked and absent IN THIS REPO at the pin: the MCP write paths (save_interaction, remember, improve) are agent-invoked tools — heavy work runs as background asyncio tasks *after* invocation, but nothing fires without a model call; no hook receiver, no scheduler. The separate cognee-integrations Claude Code plugin automates invocation via lifecycle hooks (capture + session-end sync) — README-level, not source-verified, and it runs in API mode, where the coding-rule extraction path is explicitly skipped (server.py:517-531)
memory_features:   # ADR-0013 block, set 2026-08-19 from the existing survey read at b948f88d4 — not a re-read; core pipeline unread, plugin claims README-level
  memory_store: [graph, vector, rows]  # tripartite: knowledge graph + vector + relational
  capture_path: agent-invoked    # remember/save_interaction/improve MCP tools; no hook receiver, no scheduler in-repo (the learning_loop: false pole)
  recall_injection: pull-only    # recall/search MCP tools; prompt-submit injection exists only in the out-of-repo plugin (README-level)
  memory_scope: [agent, session] # agent-scoped datasets from MCP client identity; session vs permanent split
  memory_tiers: true             # session vs permanent, mirrored by forget
  # decay deliberately unset: forget is deletion mirroring the session/permanent split (not a lifecycle), but the core pipeline is unread at survey depth — absence not checkable
  deployment_mode: both          # direct (in-process) vs API mode — with a BEHAVIOR difference: rule extraction skipped in API mode (server.py:517-531)
  rule_extraction: true          # coding_agent_rules NodeSet, direct mode only
---

# cognee

## What it is

The memory kind's oldest seed (first commit 2023-08-16, predating the coding-agent
wave) and its knowledge-graph pole: a Python platform that ingests arbitrary data,
runs a "cognify" pipeline (entity/relation extraction, optional ontology grounding),
and serves retrieval over a **tripartite store** — graph + vector + relational —
behind `add / cognify / search`. For this repo's question, the interesting object is
not the SDK but `cognee-mcp/`: an in-repo MCP server that turns the platform into a
coding-agent memory layer, with agent-scoped datasets (e.g. `cursor_vscode_memory`
derived from the MCP client identity), a session-vs-permanent memory split, and an
LLM path that extracts *coding rules* from saved interactions.

## The membership verdict (the arc's step-3 question)

The kind's membership test — independent distribution *into harnesses* — survives the
SDK-facing shape, but only through carriers. `import cognee` is upstream
infrastructure, not an installable extension; what earns bucket membership is the MCP
server (in-repo), the Claude Code marketplace plugin (hooks + skills + agents, in the
separate `cognee-integrations` repo), and the OpenClaw plugin (npm). The index's
hypothesis stands, now with source evidence: **the SDK shape sits in the bucket via
its shims, and the shims are where the coding-agent behavior actually lives** — the
rules extraction, the agent scoping, and the session bridge all live in `cognee-mcp/`
and the plugins, not in the platform core.

## The distinguishing bet

**Memory as a knowledge graph with ontology ambitions.** Against ai-memory's markdown
wiki and memos' policy database, cognee wagers that entity/relation structure — one
graph connecting everything ingested — is what makes memory compound. The cost of
that bet is architectural: a three-store consistency problem the vendor owns forever
(see the cross-examination below). Second-order bet visible in the dependency spec:
platform breadth over depth — six-plus DB backends, LiteLLM+Instructor as a universal
LLM gateway — which buys integrations and pays in wire-level brittleness.

## The MCP surface (what a coding agent actually gets)

Read in source at `cognee-mcp/src/server.py`:

- **Two-speed memory.** `remember` with a `session_id` writes a fast session cache
  (no entity extraction); without one it runs the full add+cognify graph build.
  `recall`/`forget` mirror the split. `improve` is the explicit consolidation
  bridge: apply session feedback weights to graph nodes/edges, persist session Q&A
  into the permanent graph, enrich with triplet embeddings, sync back to session
  caches. Consolidation is a *tool the agent calls*, not a background process — the
  inverse of ai-memory's and memos' posture.
- **Coding-rule learning exists, but is dark in the newest deployment shape.**
  `save_interaction` add+cognifies the exchange and then LLM-extracts developer
  rules into a `coding_agent_rules` NodeSet (`codingagents/coding_rule_associations.py`)
  — but only when the MCP server runs the library in-process: `if not
  cognee_client.use_api` (server.py:517), with an explicit "not available in API
  mode" warning. The Claude Code plugin bootstraps a local *API* and talks HTTP, so
  the marketplace-installed path skips exactly this learning feature. Nothing in the
  plugin README says so.
- **Tool-catalog economy as a feature.** `apply_tool_mode` (server.py:189) gates
  `tools/list` behind a BM25 search transform: default mode advertises a pinned
  memory API plus `search_tools`/`call_tool` instead of the full catalog. A memory
  vendor independently reinventing deferred tool loading is a datum for the
  MCP-context-cost story.

## Cross-examination: a rival's opposition research, spot-checked

ai-memory ships `docs/issues-cognee.md` (captured 2026-05-21) — 163 lines of ranked
pain points from cognee's own tracker, feeding 4 of its 15 engineering invariants.
That is competitor **testimony** (rule 1a), so two of its structural claims were
spot-checked at our pin, three months later:

- **"LiteLLM + Instructor as the universal gateway causes wire-level churn"** —
  corroborated as still the architecture: `pyproject.toml:36-37`, now with a
  defensive upper bound (`instructor>=1.9.1,<1.15.3`) that itself testifies to the
  churn.
- **"They replaced archived Kuzu with Ladybug, their own fork — the forked-DB risk
  has played out"** — corroborated and now a visible maintenance surface:
  platform-conditional version pins with multi-line apology comments
  (`pyproject.toml:60-78`), a dedicated `cognee_db_workers.ladybug_migrate` storage
  version mapper, and a top-level `kuzu/` compatibility shim.

The rest of the dossier (tripartite-store integrity bugs, the #2717 SQLite
lock-under-parallel-cognify issue ai-memory cites for its single-writer invariant,
retrieval-quality regressions) is left as testimony — plausible, dated, unverified
here.

## Stack & repo shape

Python-dominant (2,168 `.py`) monorepo with a TS frontend; 9,781 commits — the
most-committed repo in the kind, with a real contributor base (unlike the kind's
solo-author entries). `cognee-mcp/` is its own package (pyproject + uv.lock).
`evals/` archives head-to-head HotpotQA runs against mem0, graphiti, and falkor
(2025-04 vintage) and points to a current "BEAM" 100K/10M-context report. BEAM is
now cataloged ([2026-beam](../../refs/2026-beam.md), full read 2026-08-18): cognee's
0.79-at-100K sits far above the BEAM paper's own best configurations (~0.36 average
at 100K), so the vendor number needs eval-config reconciliation before it is
repeated — and the report itself flags the 10M figure (0.67) as in-sample/exploratory.

## Surprises

1. **The platform repo contains a purpose-built coding-agent product.** Expected
   generic add/cognify/search shims; found agent-scoped datasets, a session/permanent
   split with an explicit bridge tool, and coding-rule extraction — the coding-agent
   memory layer is *in* the MCP server, invisible from the SDK docs.
2. **The learning path and the distribution path have diverged.** The
   marketplace-plugin deployment (API mode) cannot reach the rule-extraction path
   (direct mode only). The feature the kind cares most about is disabled in the
   install path most users will take.
3. **Consolidation is agent-invoked.** `improve` inverts the kind's dominant posture:
   where ai-memory and memos consolidate autonomously in the background, cognee makes
   the agent decide when to consolidate. With the plugin's hooks automating the calls,
   the trigger moves into the integration seam — the loop is assembled from parts
   that live in different repos.
4. **A competitor's issue-tracker dossier held up.** Both spot-checked structural
   claims from ai-memory's opposition research were corroborated in cognee's own
   dependency spec — including the Ladybug fork whose costs are now written into
   pyproject comments.

## Open questions

- ~~Catalog BEAM before any vendor-number is cited~~ — done 2026-08-18
  ([2026-beam](../../refs/2026-beam.md), plus [2024-locomo](../../refs/2024-locomo.md)
  and [2025-longmemeval](../../refs/2025-longmemeval.md)). The catalog's cross-cutting
  finding: all three instruments measure chat-assistant memory; **no coding-agent
  memory benchmark exists**. Remaining: memos' `evaluation/` tree and the archived
  HotpotQA comparative runs stay uncataloged.
- Does the Claude Code plugin's hook capture actually call `save_interaction`, or the
  lower-level remember/HTTP API? (Determines whether *any* deployed path reaches rule
  extraction.) Requires cloning `cognee-integrations` — cheap if the loop question
  matters.
- The tripartite-store integrity class from the testimony (shared-data deletes, lock
  contention): still-open at the pin? A one-hour tracker pass would grade the
  dossier's currency.

## My take

The kind's incumbent, and the clearest illustration of its central trade: the
knowledge-graph bet maximizes what memory *could* express and pays for it in a
three-store consistency surface a solo-shaped rival (ai-memory) simply refuses to
have. For coding harnesses specifically, the product is the MCP server plus
out-of-repo plugins, and the seams between them are where the interesting failures
live.
