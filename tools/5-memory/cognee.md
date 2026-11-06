---
name: cognee
category: 5
type: memory
maker: Topoteretes (topoteretes)
url: https://github.com/topoteretes/cognee
license: Apache-2.0
access: open-source
stack: [Python, TypeScript]
version: v1.5.0-2-gb948f88d4
commit: b948f88d4
first_commit: 2023-08-16
stars: 33062
stars_at: 2026-11-04   # gh api; 30,103 at 2026-08-18 (+37.9/day net)
read_at: 2026-08-18   # survey read, same day as the stub
depth: survey   # read: README, cognee-mcp/src/server.py (tool surface + save_interaction + improve + tool modes), codingagents/coding_rule_associations.py (top), pyproject dependency spec, evals/README. Cross-examined against ai-memory's docs/issues-cognee.md (competitor testimony, 2026-05-21) with two structural claims spot-checked in source at the pin. NOT read: the core pipeline internals (cognify tasks, retrievers), the frontend, the separate cognee-integrations repo (README via GitHub API only)
harness_targets: "in-repo: cognee-mcp (MCP server, stdio/HTTP, agent-scoped datasets per client). Separate repos/packages, README-level: Claude Code marketplace plugin (cognee-integrations — hooks capture, prompt-submit injection, session-end graph sync; a Codex plugin shares its config), OpenClaw plugin (@cognee/cognee-openclaw on npm)"
harness_features:
  learning_loop: false   # checked and absent IN THIS REPO at the pin: the MCP write paths (save_interaction, remember, improve) are agent-invoked tools — heavy work runs as background asyncio tasks *after* invocation, but nothing fires without a model call; no hook receiver, no scheduler. The separate cognee-integrations Claude Code plugin automates invocation via lifecycle hooks (capture + session-end sync) — README-level, not source-verified, and it runs in API mode, where the coding-rule extraction path is explicitly skipped (server.py:517-531)
memory_features:   # ADR-0013 block, set 2026-08-19 from the existing survey read at b948f88d4 — not a re-read; core pipeline unread, plugin claims README-level
  memory_store: [graph, vector, rows]  # tripartite: knowledge graph + vector + relational
  capture_path: agent-invoked    # remember/save_interaction/improve MCP tools; no hook receiver, no scheduler in-repo (the learning_loop: false pole)
  recall_injection: pull-only    # recall/search MCP tools; prompt-submit injection exists only in the out-of-repo plugin (README-level)
  memory_scope: [agent, session] # agent-scoped datasets from MCP client identity; session vs permanent split
  memory_tiers: true             # session vs permanent, mirrored by forget
  # decay deliberately unset: forget is deletion mirroring the session/permanent split (not a lifecycle), but the core pipeline is unread at survey depth — absence not checkable
  deployment_mode: both          # direct (in-process) vs API mode — with a BEHAVIOR difference: rule extraction skipped in API mode (server.py:517-531)
  team_sharing: acl              # ADR-0052, cell set 2026-09-04 (probe-pass at the pin, source-verified at module level; surrounding pipeline unread at survey depth): one grant relation — ACL rows principal × permission × dataset (modules/users/models/ACL.py), Principal polymorphic over User/Role/Tenant, exactly four permission names (permissions/permission_types.py) with `share` the meta-permission gating authorized_give_permission_on_datasets.py; membership (UserRole/UserTenant) separate from grants so one tenant-held row covers every member; multi-tenant is the DEFAULT (ENABLE_BACKEND_ACCESS_CONTROL=true, .claude/skills/cognee-permissions/SKILL.md)
  rule_extraction: true          # coding_agent_rules NodeSet, direct mode only
  memory_import: true            # targeted probe-pass at the pin, cell set 2026-09-04 (ADR-0051): cognee/modules/migration/sources/ ships four competitor-store importers — mem0.py (82 lines, parses the platform export API AND OSS get_all() shapes), zep.py (138), letta.py (155), langmem.py (96) — via import_memory_source, beside the excluded own-format COGX archive round-trip. The most explicit competitor targeting in the column; source-verified at file level, the surrounding pipeline unread at survey depth
---

# cognee

## What it is

The memory type's oldest seed (first commit 2023-08-16, predating the coding-agent
wave) and its knowledge-graph pole: a Python platform that ingests arbitrary data,
runs a "cognify" pipeline (entity/relation extraction, optional ontology grounding),
and serves retrieval over a **tripartite store** — graph + vector + relational —
behind `add / cognify / search`. For this repo's question, the interesting object is
not the SDK but `cognee-mcp/`: an in-repo MCP server that turns the platform into a
coding-agent memory layer, with agent-scoped datasets (e.g. `cursor_vscode_memory`
derived from the MCP client identity), a session-vs-permanent memory split, and an
LLM path that extracts *coding rules* from saved interactions.

## The membership verdict (the arc's step-3 question)

The type's membership test — independent distribution *into harnesses* — survives the
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
most-committed repo in the type, with a real contributor base (unlike the type's
solo-author entries). `cognee-mcp/` is its own package (pyproject + uv.lock).
`evals/` archives head-to-head HotpotQA runs against mem0, graphiti, and falkor
(2025-04 vintage) and points to a current "BEAM" 100K/10M-context report. BEAM is
now cataloged ([2026-beam](../../references/papers/2026-beam.md), full read 2026-08-18): cognee's
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
   (direct mode only). The feature the type cares most about is disabled in the
   install path most users will take.
3. **Consolidation is agent-invoked.** `improve` inverts the type's dominant posture:
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
  ([2026-beam](../../references/papers/2026-beam.md), plus [2024-locomo](../../references/papers/2024-locomo.md)
  and [2025-longmemeval](../../references/papers/2025-longmemeval.md)). The catalog's cross-cutting
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

The type's incumbent, and the clearest illustration of its central trade: the
knowledge-graph bet maximizes what memory *could* express and pays for it in a
three-store consistency surface a solo-shaped rival (ai-memory) simply refuses to
have. For coding harnesses specifically, the product is the MCP server plus
out-of-repo plugins, and the seams between them are where the interesting failures
live.

## Candidate vocabulary collected

2026-11-06, targeted probe at the pin, not a re-read: five candidate keys Phase 19 weighs (`llm_free_path`, judged per component, `concurrent_write_safety`, `compaction_capture`, the OKF open-format axis and `agent_coordination`) were read at the pin `b948f88d4` with `git show b948f88d4:<path>` and `git grep … b948f88d4`. The clone's HEAD (`eb90d03`, v1.6.1) was not evidence, nothing was installed or run, and the frontmatter above is untouched. Prose only: the keys are unregistered, so no cell exists, and the verdicts are against the presence tests frozen before the reads in the [category README](README.md#candidate-key-census-at-existing-pins-2026-11-06); no shape or value label is written (Phase 19 settles those). The engine the default path means is the `cognee` Python package as `cognee.remember()` and `cognee.recall()` run it, plus the MCP server `cognee-mcp/src/server.py` in direct mode, with the shipped defaults (provider `openai`, model `openai/gpt-5-mini`, no key set: `cognee/infrastructure/llm/config.py:86-89`) and no provider key in the launching environment; the hosted Cognee Cloud is a named route and decides nothing. Grades are SOURCE unless tagged. Drift notes are dated and are not census evidence.

- `llm_free_path` — judged on the SDK and its MCP server in direct mode with the shipped defaults; the hosted cloud is a named route; the three components follow, each with its own verdict.
  - capture — ✗. Default capture makes generative calls: `remember()` without a session id runs `add`, then `cognify`, then `improve` (`cognee/api/v1/remember/remember.py:1262-1291`); the default `cognify` task list is commented as LLM extraction of entities and relationships and LLM summarizing of each chunk (`cognee/api/v1/cognify/cognify.py:381-390`) and reaches the model through `LLMGateway.acreate_structured_output(` (`cognee/infrastructure/llm/extraction/knowledge_graph/extract_content_graph.py:41-43`). `add` also runs through a pipeline runner whose first-run environment check sends a generative connection prompt, skipped only when `COGNEE_SKIP_CONNECTION_TEST` is truthy (`cognee/modules/pipelines/layers/setup_and_check_environment.py:39-47`, `cognee/modules/pipelines/layers/setup_and_check_environment.py:64`); the prompt asks the model to answer with a fixed string and any failure is re-raised (`cognee/infrastructure/llm/utils.py:87-113`), and the default provider requires a key and raises `LLMAPIKeyNotSetError` without one (`cognee/infrastructure/llm/structured_output_framework/litellm_instructor/llm/get_llm_client.py:198-199`). Placement: `cognify` is capture here because the default `remember()` runs it in the same call as `add` (the comment reads permanent memory, add plus cognify plus optional improve, `cognee/api/v1/remember/remember.py:1260`), as model extraction at write time; a separate `cognify` run could be read as graph building after ingest, and consolidation is ✗ either way. A model-free route exists and is not the default: `remember(content_type="code")` takes a graph-only pipeline that performs no model call and skips the connection test (`cognee/api/v1/remember/remember.py:1040-1043`). Model path on: always on the default text path (the key is read as `LLM_API_KEY` into the `llm_api_key` field of `LLMConfig`, `cognee/infrastructure/llm/config.py:89`); `COGNEE_SKIP_CONNECTION_TEST=true` removes only the connection test. Egress: the provider endpoint for every chunk. Spend: per chunk, for the graph extraction and the summary. Drift (2026-11-06): HEAD adds a local extraction backend that needs no model and defaults to it when no key is set (`aba8ee2cb`, `54db3c102`, neither an ancestor of the pin; `git rev-list --count b948f88d4..HEAD -- cognee/api/v1/cognify/cognify.py` prints 12), so the HEAD capture verdict may differ. Surface searched: `git grep -n -I -E 'LLMGateway\.acreate_structured_output|acreate_structured_output\(' b948f88d4 -- cognee/infrastructure/llm/extraction cognee/tasks/graph cognee/tasks/summarization cognee/api/v1/cognify` prints 9 lines in 9 files (the extraction, summary, category, event and cascade modules and the opt-in contradiction pass at `cognee/tasks/graph/detect_contradictions.py:178`). Control: `git grep -c -I -E '\bdef ' b948f88d4 -- cognee/api/v1/cognify/cognify.py` prints 5.
  - consolidation — ✗. Consolidation is `improve()`, which `remember()` runs after `cognify` by default (`self_improvement: bool = True` at `cognee/api/v1/remember/remember.py:660`, the call at `cognee/api/v1/remember/remember.py:1284-1291`). Without session ids only the memify stage runs (`cognee/api/v1/improve/improve.py:76`), which calls `memify(…)` (`cognee/api/v1/improve/improve.py:238-260`); its default extraction tasks are empty unless `triplet_embedding` is set, default false (`cognee/memify_pipelines/memify_default_tasks.py:8-13`, `cognee/modules/cognify/config.py:11`), and its enrichment task is `index_data_points` (`cognee/memify_pipelines/memify_default_tasks.py:16-17`), which makes no model call. `memify` runs through `run_pipeline` (`cognee/modules/memify/memify.py:123-138`), whose first statement is the environment check that sends the generative connection prompt (`cognee/modules/pipelines/operations/pipeline.py:87-89`). Clause met: a standalone `improve()` in a fresh process sends that prompt and raises without a key, which is the test's fails-without-one wording; clause not met: the consolidation tasks themselves are model-free. With session ids the stages that extract agent context and distill sessions are commented as model passes (bodies unread, INFERENCE). Named and not counted: an opt-in cron-scheduled web scraper (`cognee/tasks/web_scraper/web_scraper_task.py:41`, `cognee/tasks/web_scraper/web_scraper_task.py:85`, `cognee/tasks/web_scraper/web_scraper_task.py:182`), which ingests new content and does not act on stored records, so it is capture. Contradiction (2026-11-06): the frontmatter comments (`cognee.md:19`, `cognee.md:22`) and the body (`cognee.md:73-78`, `cognee.md:138-141`) call consolidation a tool the agent calls and not a background process; that holds for the MCP surface, where `improve` is defined without `@registry.tool` (`cognee-mcp/src/server.py:1348`; an unregistered function is not an MCP tool is INFERENCE, FastMCP not read), but the SDK `remember()` runs `improve` by default and `remember(session_id=…)` starts `improve(session_ids=[…])` as a background task (`cognee/api/v1/remember/remember.py:1232-1249`); the report is left as read on 2026-08-18. Model path on: always on the permanent path through the connection test, removable by the explicit flag `COGNEE_SKIP_CONNECTION_TEST=true`; always on the session path. Surface searched: `git grep -n -I -E 'LLMGateway|acreate' b948f88d4 -- cognee/tasks/storage/index_data_points.py` prints nothing, and `git grep -n -I -E 'apscheduler|AsyncIOScheduler|crontab' b948f88d4 -- cognee ':!cognee/tests' ':!cognee/eval_framework'` prints 8 lines, all in the opt-in scraper (measure: the wider pattern that adds `create_task` loops and `while True` prints 34 lines). Control: `git grep -c -I -E 'LLMGateway|generate_completion|acreate' b948f88d4 -- cognee/modules/retrieval/graph_completion_retriever.py cognee/modules/retrieval/utils/completion.py` prints 7 and 9, the retrievers that do call the gateway.
  - recall — ✗. The default recall path ends in a generative answer: the MCP `recall` tool calls the client with `auto_route` true (`cognee-mcp/src/cognee_client.py:718-722`), `recall` defaults `query_type` to none and `auto_route` to true (`cognee/api/v1/recall/recall.py:338-345`, `cognee/api/v1/recall/recall.py:608-612`), and the rule-based router, which classifies without calling a model (`cognee/api/v1/recall/query_router.py:4`), returns `GRAPH_COMPLETION` when no rule matches (`cognee/api/v1/recall/query_router.py:149`, `cognee/api/v1/recall/query_router.py:194-196`) or the best score is below threshold (`cognee/api/v1/recall/query_router.py:203-216`). `GRAPH_COMPLETION` answers through `generate_completion` and `LLMGateway.acreate_structured_output(` (`cognee/modules/retrieval/utils/completion.py:32`), and the search entry point's own default is the same type (`cognee/api/v1/search/search.py:42`). Model path on: always on the router default; it is avoided by asking for the `CHUNKS` or `CHUNKS_LEXICAL` search type, whose retrievers hold no model call. Egress and spend: the provider endpoint, one answer call per query. Drift (2026-11-06): HEAD makes the default search hybrid, narrows the router to three rules and stops auto-routing to CYPHER (`f4218f647`, `2c660fb40`, `4825e54e9`, none an ancestor of the pin; `git rev-list --count b948f88d4..HEAD -- cognee/api/v1/recall/query_router.py` prints 6), not diffed, so the HEAD recall verdict is undecided. Surface searched: `git grep -n -c -E 'LLMGateway|generate_completion|acreate' b948f88d4 -- cognee/modules/retrieval/chunks_retriever.py cognee/modules/retrieval/lexical_retriever.py` prints nothing. Control: `git grep -c -E 'LLMGateway|generate_completion|acreate' b948f88d4 -- cognee/modules/retrieval/graph_completion_retriever.py cognee/modules/retrieval/utils/completion.py` prints 7 and 9.
- `concurrent_write_safety` — present. Four mechanisms state their own purpose. The first is a per-dataset asyncio lock around pipeline runs and delete operations, which its docstring says serializes operations that mutate the same dataset and is process-local only, not protecting multiple processes or workers (`cognee/infrastructure/locks/dataset_lock.py:3-11`); it is taken for pipeline runs (`cognee/modules/pipelines/operations/pipeline.py:173`) and for deletes (`cognee/api/v1/forget/forget.py:287`, `cognee/api/v1/forget/forget.py:360`, `cognee/api/v1/datasets/datasets.py:118`, `cognee/api/v1/datasets/datasets.py:151`). The second is the SQLite write-ahead log with a busy timeout, chosen for concurrent writers: the comment says enabling WAL serializes writers on a single write lock while readers proceed, so concurrent writers wait, bounded by the timeout, instead of deadlocking, and cites issue #2717 (read 2026-11-06 as a citation only) (`cognee/infrastructure/databases/relational/sqlalchemy/SqlAlchemyAdapter.py:117-124`), with the pragmas at `cognee/infrastructure/databases/relational/sqlalchemy/SqlAlchemyAdapter.py:129-131`; the waiting lock itself is SQLite's and is recorded as the engine's, and the verdict does not rest on this pragma. The third is the vector store's upsert lock, `self.VECTOR_DB_LOCK = asyncio.Lock()` (`cognee/infrastructure/databases/vector/lancedb/LanceDBAdapter.py:180`), whose comment says holding it across read, build and write serializes upserts (`cognee/infrastructure/databases/vector/lancedb/LanceDBAdapter.py:439-443`) and which is taken at `cognee/infrastructure/databases/vector/lancedb/LanceDBAdapter.py:597`. The fourth is the session locks, three primitives scoped to a single-worker FastAPI server (`cognee/infrastructure/locks/session_lock.py:1-24`). Also present and named: an optional lock shared by the Ladybug graph adapter, off by default (`shared_ladybug_lock: bool = False` at `cognee/infrastructure/databases/cache/config.py:56`, read at `cognee/infrastructure/databases/graph/ladybug/adapter.py:322`), a one-by-one pipeline execution mode commented as avoiding database write conflicts (`cognee/modules/pipelines/layers/pipeline_execution_mode.py:92`) and a cross-process migration mutex (`cognee/modules/migrations/runner.py:17-24`). Scope: one process for the dataset, upsert and session locks; processes on one host for the SQLite pragma; the migration mutex is processes on one host on SQLite and several hosts on Postgres, whose advisory lock the docstring says "also serializes across hosts" (`cognee/modules/migrations/runner.py:17-24`); the optional Ladybug lock goes through the cache engine (`cognee/infrastructure/databases/graph/ladybug/adapter.py:322-325`), so its scope follows the configured cache backend, not read. Write paths: pipeline runs (`add`, `cognify`, `memify`), dataset deletes, vector upserts and session updates. Named and not counted: the inline serialization of synchronous handlers in `cognee_db_workers`, whose purpose is thread safety of a library (`cognee_db_workers/harness.py:408-415`) and whose own purpose line is a small memory footprint (`cognee_db_workers/__init__.py:1-6`), the Ladybug worker's file-lock backoff and `DatasetQueue`. Drift (2026-11-06): HEAD adds a lock-order check against `DatasetQueue` to the dataset lock and keeps the process-local note (`git rev-list --count b948f88d4..HEAD -- cognee/infrastructure/locks/dataset_lock.py` prints 4), scope and verdict unchanged; the adapter and session-lock files were not diffed. Measure: `git grep -n -E 'dataset_lock\(|get_dataset_lock\(' b948f88d4 -- cognee ':!cognee/tests' ':!cognee/infrastructure/locks'` prints 5 lines, the pipeline run and the four delete sites.
- `compaction_capture` — omitted: Premise: the pin holds no hook manifest and no hook receiver, and the only `PreCompact` text is README prose (`README.md:281`, TESTIMONY); the integration catalog names a separate repository as the home of the Claude Code plugin (`catalog/entries/integrations/claude-code.yaml:22-23`, repository `topoteretes/cognee-integrations`, path `integrations/claude-code`), so the plugin is a known shipped integration of exactly this key's class, a hook manifest and handler, that lives outside the pin; the README says it registers `PreCompact`, and whether its handler writes to the cognee store cannot be decided here. Test: read the hook manifest and handler under `integrations/claude-code` of `topoteretes/cognee-integrations` at a pinned commit for a `PreCompact` entry that calls a cognee write; if there is none, or the handler writes nothing, the verdict is ✗. Surface searched: `git grep -n -I -i -E 'precompact|pre_compact|pre-compact|hook_event_name|hookEventName' b948f88d4 -- . ':!*.lock' ':!package-lock.json' ':!README.md'` prints nothing, and `git ls-tree -r --name-only b948f88d4 | grep -i -E 'hooks\.json|settings\.json|plugin\.json|\.claude-plugin|marketplace\.json'` prints nothing. Control: `git grep -c -I -E 'SessionStart|UserPromptSubmit|PreCompact' b948f88d4 -- ':!*.lock' ':!package-lock.json'` prints 2 files, the README and the catalog entry.
- The OKF open-format axis — ✗. No OKF declaration at the pin; COGX, the Cognee eXchange format for portable memory, is the house format (`cognee/modules/migration/cogx.py:1`, an archive of `manifest.json` plus one JSONL file per record kind at `cognee/modules/migration/cogx.py:8-9`, `COGX_VERSION = "0.1"` at `cognee/modules/migration/cogx.py:20`), and the competitor import formats in `cognee/modules/migration/sources/` (`cogx_archive.py`, `langmem.py`, `letta.py`, `mem0.py`, `zep.py`) are named and not counted. The cognee vocabulary used was `cogx`, `COGX_VERSION`, `manifest.json`, `write_json`, `write_graphml` and `write_cypher`. Surface searched: `git grep -n -I -i -E '\bokf\b|open knowledge format' b948f88d4 -- . ':!*.lock' ':!package-lock.json'` prints nothing. Control: `git grep -c -I -i -E '\bcogx\b' b948f88d4 -- ':!*.lock' ':!package-lock.json'` lists 30 files, 134 lines.
- `agent_coordination` — omitted: Premise: the source-visible half has no agent-to-agent mechanism (the MCP server registers 10 tools by the measure of `git grep -c -E '@registry\.tool' b948f88d4 -- cognee-mcp/src/server.py`: `remember`, `recall`, `forget`, `visualize_graph_ui`, `upload_file_ui`, `open_cognee_workspace`, `list_datasets_json`, `list_dataset_data_json`, `get_client_info_json` and `create_dataset_json`, none a message, task or claim tool), but the searched surface excludes integrations the pin itself describes as supplying agent-callable tools from another repository: the catalog names 4 entries whose code lives in `topoteretes/cognee-integrations` (`claude-code`, `codex`, `langgraph` and `openclaw`) and 2 in `topoteretes/cognee-community` (measure: `git grep -n -I -E '^repo: ' b948f88d4 -- catalog/entries`), the `langgraph` entry describes itself as adding cognee memory to a LangGraph agent as tools it can call to store and search context (`catalog/entries/integrations/langgraph.yaml`), and the pin holds none of their tool definitions (the path listing for `integrations/<name>/` is empty). The catalog describes those tools as memory add and search (TESTIMONY, which cannot decide), so a ✗ cannot stand; the premise is that an out-of-pin integration exposes a tool by which one agent addresses or hands work to another. Test: read the tool definitions of the four `cognee-integrations` entries counted above at a pinned commit; if none addresses or hands work to another agent, the verdict is ✗. Named and not coordination: agent-scoped datasets (`_agent_scoped_default_dataset()`, `COGNEE_MCP_AGENT_SCOPED` default true, `cognee-mcp/src/server.py:1761-1796`), `create_agent`, `AgentConnection` with `COGNEE_AGENT_MODE`, and shared session reads through dataset grants, which are isolation, identity and sharing between humans. Surface searched: `git grep -n -I -i -E '\b(mailbox|inbox|send_message|handoff|hand_off|delegate_to|assign_task|claim_task|task_queue|agent_to_agent|a2a|recipient|assignee|to_agent|from_agent)\b' b948f88d4 -- cognee cognee-mcp ':!cognee/tests' ':!cognee-mcp/tests' ':!cognee/eval_framework' ':!*.lock' ':!cognee/infrastructure/llm/prompts'` prints nothing. Control: `git grep -c -I -i -E 'multi[-_ ]agent|agent_session_name|AgentConnection' b948f88d4 -- cognee cognee-mcp ':!cognee/tests' ':!cognee-mcp/tests' ':!cognee/eval_framework' ':!*.lock'` lists 12 files, 68 lines.
