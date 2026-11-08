---
name: mem0
category: 5
type: memory
maker: Mem0 (mem0ai, YC S24)
url: https://github.com/mem0ai/mem0
license: Apache-2.0
access: open-source
stack: [TypeScript, Python]
version: ts-v3.1.6-20-g001c2352
commit: 001c2352
first_commit: 2023-06-20
stars: 68403
stars_at: 2026-11-04   # gh api; 63,535 at 2026-08-18 (+62.4/day net)
read_at: 2026-08-19   # deep-dive, same pin as the 2026-08-18 survey (zero upstream drift); vendor paper separately at full depth (references/papers/2025-mem0.md)
depth: deep-dive   # 2026-08-19: three parallel readers at the pin (plugin/carrier script bodies; SDK write/read machinery incl. async + TS port; platform boundary/server/benchmark provenance), load-bearing claims spot-verified in main session; displacement gate RUN-probed with synthetic hook payloads (host + alpine/jq container)
harness_targets: "in-repo at the pin: integrations/mem0-plugin targets Claude Code, Claude Cowork, Cursor, Codex, OpenCode, Antigravity (hooks.json + codex-hooks.json + cursor-hooks.json + a Kimi shim; MCP config bundled — all four MCP manifests point at the hosted mcp.mem0.ai, no stdio/localhost option); also integrations/openclaw (the only carrier with an OSS code path) and pi-agent-plugin, plus non-harness carriers (vercel-ai-sdk — which bypasses the SDK entirely, zapier, n8n) and 17 in-repo skills (survey's six-skill count was closer to the pi-agent set)"
harness_features:
  skills: true   # 17 skill dirs in the Claude plugin (all with SKILL.md, verified by count) (context-loader, dream, import, policy, remember, …) — survey's "six" corrected at deep-dive
  learning_loop: background  # via the in-repo harness plugin: Stop/PreCompact hooks capture with infer=True → V3 LLM extraction, no human in loop; PLUS auto_capture every 3rd message uploading raw turns, and auto_import shipping CLAUDE.md/AGENTS.md/.cursorrules to the platform on session start with no consent step (deep-dive)
memory_features:   # deep-dive 2026-08-19 — two survey cells FLIPPED (memory_tiers, decay), one settled (injection_trust_boundary)
  memory_store: vector           # one shared collection + an entity store (second vector collection, spaCy-extracted, one-hop). GRAPH MEMORY REMOVED from OSS in the same commit that landed V3 (a488e190, 2026-04-14, −2,849 lines) — platform-only now; docs/platform/platform-vs-oss.mdx:65 still advertises OSS graph support and is stale
  capture_path: hook             # Stop/PreCompact/UserPromptSubmit hooks; auto_capture every 3rd message (raw turns, unsanitized); infer=True → V3 extraction
  compaction_capture: writes-to-store  # SOURCE 2026-11-06 at 001c2352, targeted probe: the plugin registers a handler on the harness pre-compaction event in 5 places (integrations/mem0-plugin/hooks/hooks.json:102 for Claude Code by plugin convention, hooks/codex-hooks.json:92, hooks/cursor-hooks.json:44, .kimi-plugin/plugin.json:66, .opencode-plugin/opencode-mem0.ts:382); the shell handler starts on_pre_compact.py in the background (scripts/on_pre_compact.sh:19-21), which posts the session state with infer true to the hosted /v3/memories/add/ endpoint (scripts/on_pre_compact.py:171-191), skipping when no API key resolves; the OpenCode hook writes and then re-injects, so the stronger value holds; judged on the in-pin plugin handler (engine per key), the hosted store being only the write target; drift: the manifests are deleted at HEAD and what HEAD writes is undecided; cell set 2026-11-08 per ADR-0059
  llm_free_path: [consolidation, recall]  # SOURCE 2026-11-06 at 001c2352, targeted probe, judged on the open Python SDK with the default MemoryConfig and no provider key; capture is not listed because add() calls a model by default (infer defaults true, mem0/memory/main.py:770, generate_response at main.py:956-961); consolidation (no process): the open SDK has no between-session process, stored records change only when a caller invokes update or delete (mem0/memory/main.py:1865, :1882); recall makes no generative call (mem0/memory/main.py:1628-1652; reranking is opt-in, rerank defaults to False at main.py:1386); model path on: capture always, the only off-switch being the per-call infer=False, and recall only with an llm_reranker block plus rerank=True; the three plugin dream passes and the hosted platform sit outside the open engine; client construction needs a provider key, which is setup and outside the components; cell set 2026-11-08 per ADR-0059
  write_admission: unfiltered    # V3 ADD-only extraction admits whatever the LLM reads as a fact from the transcript; no enactment or outcome gate; contradiction handling explicitly the caller's job; the plugin NUDGES eager writing ("Aim for 1–3 memories per substantial interaction"). Combined with the openclaw recall protocol's memories-as-mandatory-rules, this is the injection-to-authority pipeline the registry note names
  concurrent_write_safety: one-process  # SOURCE 2026-11-06 at 001c2352, targeted probe: one shared sqlite3 connection opened with check_same_thread=False behind a threading.Lock (mem0/memory/storage.py:14-15), held by every SQLiteManager method that touches it (9 sites, 7 of them writes), so contending threads block and queue; covers the history and messages tables of history.db, not vector-store records, whose adapters add no lock (mem0/vector_stores/qdrant.py:601); a second lock file shared by processes on one host excludes concurrent dream passes in the plugin (integrations/mem0-plugin/.opencode-plugin/dream.ts:155-182) and covers only that pass, so the verdict rests on the first; judged on the open SDK (engine per key); cell set 2026-11-08 per ADR-0059
  recall_injection: auto         # per-turn top_k=5 (reranked by default) + session-start 10-memory timeline + opportunistic file-read (5×150ch) and stack-trace injections — all as bare markdown in additionalContext
  memory_scope: [user, agent, session]  # query FILTERS in one shared collection, not namespaces; ≥1 scope id mandatory on every write/read (VALIDATION_001); isolation = each store adapter's filter translation
  memory_tiers: false            # FLIPPED ✓→✗ at deep-dive: procedural_memory is a metadata tag on the SAME collection with no distinct retrieval path (memory_type never read at search); MemoryType.SEMANTIC/EPISODIC are unreachable enum values; and procedural without agent_id silently falls through to the normal pipeline
  hybrid_retrieval: true         # real but conditional: additive fusion with adaptive divisor (NOT RRF, scoring.py:99-137); BM25 can only re-rank the semantic candidate pool, never add to it; spaCy+fastembed are optional extras, so a bare `pip install mem0ai` silently degrades to pure vector search; 15/25 stores implement keyword_search
  memory_revision: caller-only   # deep-dive 2026-08-19: nothing in the open SDK ever calls update/delete automatically, and caller-only stands for the open SDK (SOURCE 2026-11-06 at 001c2352: three plugin adapters ship a dream pass, an agent-driven consolidation where the harness's own model rewrites memories through the hosted store, default on in the OpenCode adapter, integrations/mem0-plugin/.opencode-plugin/dream.ts:38-46, outside the open engine and deleted at HEAD); a shifted preference is a LINKING trigger and the link is discarded; contradiction handling is the application's job
  decay: false                   # FLIPPED ✓→✗ at deep-dive: decay/timestamp/reference_date HARD-RAISE in OSS (main.py:468-471, :817, :1430) — routed through the upsell-notice path; expiration_date is post-fetch hiding on a date string (expired rows still consume top_k slots); platform-only feature. Survey's ✓ read client params to the paid API
  injection_trust_boundary: false  # SETTLED (was an open question): the sole plugin formatter emits bare markdown (_search.py:92-105) — no delimiter, no data-not-instructions framing; openclaw's tags are containers whose preambles say the OPPOSITE ("Use them to personalize your response"), and its recall protocol makes memories authoritative: "Rules are mandatory… Rules override your defaults" — staleness is questioned, provenance never
  deployment_mode: both          # load-bearing asymmetry: the core V3 algorithm IS open (BM25, entities, 6 rerankers, vision), the server is production-grade — but the coding-agent plugin is platform-HARDCODED (api.mem0.ai literal in every script, no MEM0_BASE_URL, settings loader filters unknown keys), V3 net-REMOVED OSS features (graph, temporal, decay), and the SDK ships a 1,582-line A/B-tested upsell funnel (notices.py)
  team_sharing: false            # ADR-0052, cell set 2026-09-04 (probe-pass at the pin): the OSS engine has no human-team construct — user_id is a query filter for the app's END-USERS, not a developer identity; org/project/member constructs live only in the hosted-platform client (mem0/client/main.py, client/project.py). Platform-only ⇒ ✗ per this report's own tiers/decay precedent. The platform side is docs-confirmed (retrieved 2026-09-04): orgs/projects with add_member roles READER|OWNER, member-scoped access (docs.mem0.ai/api-reference/organizations-projects); per-human write attribution not documented — identity runs through app-supplied user_id, not platform login
  harness_installer: true        # hooks.json bundle across 6 harnesses + MCP config; SessionStart also appends MEM0_API_KEY to the harness env file
  memory_import: true            # ADR-0051, cell set 2026-09-04 from the 2026-08-19 deep-dive's findings, no re-read: manual /mem0:import skill (consent in prose) + auto_import.py shipping CLAUDE.md/AGENTS.md/.cursorrules/.windsurfrules (cwd + git root, ≤100KB) to api.mem0.ai on every session start, backgrounded, no consent step — rival rule stores ingested as memories; the first instance behind the key
---

# mem0

## What it is

"The memory layer for personalized AI": a Python/TS SDK, a self-hostable server, and a
managed platform that LLM-extract memories from conversation history, store them per
user/agent/session in a vector store, and retrieve them into later context. The repo at
the pin carries a serious coding-harness beachhead (`integrations/mem0-plugin`, six
harnesses) — and the deep-dive's headline is that the *product boundary runs through the
middle of the open code*: a genuinely open V3 core, ringed by platform-only features,
instrumented end-to-end for conversion.

## The write path, traced to its dead ends

The survey's V3-ADD-only finding is **confirmed structurally, not just behaviorally** —
the machinery that could do anything else is dead code:

- The "anti-hallucination" integer→UUID mapping is built and never read: `uuid_mapping`
  has exactly four occurrences in the SDK, all assignments (`main.py:935,937,2591,2593`).
  No LLM-returned ID is ever resolved. Nothing the model says can touch an existing
  memory.
- `linked_memory_ids` — the mechanism the additive design offers *instead of* UPDATE —
  is prompt theatre in OSS: three prompt passages and an output-schema field, parsed and
  then discarded (the record loop reads only `text` and `attributed_to`,
  `main.py:1024-1041`). The prompt even tells the model the IDs are UUIDs while the code
  passes `"0"`, `"1"`. The platform client's docstring references "the v3
  `linked_memory_ids` chain" as a real feature — real *there*, not here.
- The prompt's `## Summary` and `## Recently Extracted Memories` sections are **always
  empty**: the builder accepts them, both call sites pass neither (`main.py:948`), and no
  summarizer exists in OSS. Observation Date — "your ONLY temporal anchor" per the
  prompt — is always *now, UTC*; `add(timestamp=…)` raises. Roughly a third of the
  described input contract is unfilled platform-port scaffolding.
- Dedup (MD5 over extracted text alone) is checked only against the same top-10
  neighbours the prompt saw, and only on the V3 path — `infer=False` and procedural
  writes can duplicate freely.
- Contradiction handling is the caller's job, confirmed: nothing in the SDK ever calls
  `update()`/`delete()` automatically (the OpenAI-proxy wrapper calls only `add` and
  `search`); a shifted preference is a *linking* trigger in the prompt, and the link is
  discarded. The SQLite `history` audit table has UPDATE/DELETE event types that `add()`
  never produces.

The test suite pins almost none of this: no golden prompt, zero dedup tests, zero
`uuid_mapping` tests, and the only structural guard is four `call_count == 1`
assertions — while ~2,900 lines test the upsell-notice subsystem (~5× the add pipeline)
and `tests/configs/test_prompts.py` still tests the *retired* ADD/UPDATE/DELETE prompt
in full. Living tests for dead code, no tests for live code.

## The read path — hybrid, conditionally

Fusion is real but it is **additive with an adaptive divisor, not RRF**
(`scoring.py:99-137`): `min((semantic + bm25 + 0.5·entity) / max_possible, 1.0)`, with
the divisor growing per signal present. Two structural limits: candidates come **only**
from semantic search (BM25 re-ranks the pool, can never add to it), and `threshold`
gates the semantic score *before* fusion, so a strong keyword match with weak embedding
similarity is dropped. Both lemmatization/entities (spaCy, English-only
`en_core_web_sm`, auto-downloads at first use) and BM25 encoding (fastembed) are
optional extras — **a bare `pip install mem0ai` silently degrades to pure vector
search** (the SDK warns only when the *store* lacks keyword search, not when the extras
are missing). 15 of 25 stores implement `keyword_search`; only 4 of 25 implement the
advanced filter DSL's `$or`/`$not`/`icontains` — the parser accepts what most backends
then drop.

## Graph memory: removed, not absent

`a488e190` (2026-04-14) — the same commit that landed V3 in OSS — deleted the entire
graph subsystem (9 files, 2,849 lines; no `graph_store` in `MemoryConfig`, no graph
extra in pyproject). Docs say it moved to the platform as an always-on feature;
`docs/platform/platform-vs-oss.mdx:65` still advertises OSS graph support (stale), and
`examples/graph-db-demo/` ships 5 notebooks configuring a key the SDK no longer has.
What replaced it in OSS is an *entity store*: a second vector collection of
spaCy-extracted entities with one-hop links and a capped 0.5 retrieval boost — an
association mechanism, not a graph.

## The displacement gate, run-probed

The survey's headline ("blocks the harness's native memory writes") survives the probe
**narrowed**. Measured with synthetic PreToolUse payloads (host + alpine/jq container):

| Path | Claude gate | Cursor gate |
|---|---|---|
| `~/.claude/projects/<key>/memory/MEMORY.md` | **exit 2** | deny |
| `~/.claude/memory/*` | **exit 2** | deny |
| `~/.claude/MEMORY.md` | allow | deny |
| repo-level `MEMORY.md` | allow | **deny** |
| `CLAUDE.md` anywhere | allow | allow |

- Registered only on `Write|Edit|MultiEdit` — Bash-mediated writes bypass it entirely;
  no content inspection; no gate on any non-mem0 memory MCP tool.
- **Fails open without `jq`**: on a host lacking jq the path extraction falls back to
  empty and the script exits 0 for everything, silently (run-verified). An undeclared
  dependency is the gate's real availability condition.
- **Cursor users get a strictly broader gate than Claude Code users** (`*/MEMORY.md`
  anywhere on disk) from the same plugin, undocumented as a divergence.
- The *actual* displacement work is prose, not the gate: SessionStart injects "Native
  MEMORY.md detected … Add autoMemoryEnabled:false to settings.json or run
  /mem0:import" (`on_session_start.sh:178-180`), and the import skill instructs the
  same. On ADR-0011's enforcement ladder: `script`-graded enforcement for a narrow path set, with
  prose carrying the intent.

## What the plugin injects, and what it captures

Injection is **bare markdown, no trust framing** — settled as the type's negative pole
(frontmatter cell). Volume per session: a 10-memory timeline + directive banner at
SessionStart (including a standing write-nudge: "Aim for 1–3 memories per substantial
interaction"), top-5 reranked recall per qualifying prompt, plus opportunistic
injections on file reads (5×150 chars) and stack traces. The openclaw recall protocol
goes further than unframed — it *inverts* the boundary: "Identity memories are ground
truth… Rules are mandatory… **Rules override your defaults**." Staleness is the only
skepticism; that a memory might have been written by something other than the user is
never contemplated — while memories are auto-captured from transcripts and auto-imported
from repo files.

Capture is broader than the survey knew: `auto_capture.py` uploads **raw user and
assistant turns** (8×2000 chars) every 3rd message with *no* tag sanitization, while the
session-summary path carefully strips `<system-reminder>`-class tags first — an
inconsistency with data-exfiltration implications. `auto_import.py` ships `CLAUDE.md`,
`AGENTS.md`, `.cursorrules`, `.windsurfrules` (≤100KB, cwd + git root) to
`api.mem0.ai` on every session start, backgrounded, no consent step (the consent lives
only in the *skill* prose for the manual importer). `enforce_metadata_defaults.sh`
silently rewrites the agent's tool arguments via `updatedInput` — including replacing
the agent's search filters wholesale under `global_search`. And the plugin is
**platform-hardcoded**: `api.mem0.ai` is a literal in every script, no `MEM0_BASE_URL`
anywhere, and the settings loader actively filters unknown keys — the self-host
redirect is structurally unreachable from the coding-agent product, while the CLI and
openclaw integration both support it.

## The OSS/platform boundary — open core, fenced ring, instrumented gap

The generous reading is verified in source: V3's substance (single-pass extraction,
BM25 + lemmatization, entity extraction/boost, six rerankers, vision) is real OSS code;
"works with any LLM" holds (20 LLM / 26 vector-store / 15 embedder providers); the
self-host server is production-grade (bcrypt'd API keys, timing-safe login with
burn-equal-cycles dummy verify, Alembic migrations, rate limiting) — though the only
shipped compose file is the dev variant (`--reload`, source bind-mount).

The critical reading is equally verified:

- **V3 was a net removal for OSS** — graph gone, temporal/decay shipped as stubs that
  raise. The open surface narrowed in exactly the paid direction.
- **The gap is monetised inside the library**: `mem0/memory/notices.py` (1,582 lines)
  detects scale (2,000 memories), ambition (top_k>50), latency pain (>2s), and even
  **temporal language in the user's own query strings** (regex on the success path,
  `main.py:1441`), then serves remotely-controlled marketing copy fetched at runtime
  from a PostHog feature flag — with `displayed`/`holdout` experiment arms and
  `notice_displayed` telemetry. The copy is not in the source and cannot be reviewed at
  any pin. Telemetry defaults ON (`telemetry.py:14`). The self-hosted dashboard
  independently ships four paywalled pages with UTM-tagged "Talk to sales" CTAs over
  blurred mockups.
- **The carriers bypass the open code**: the Vercel AI provider has no `mem0ai`
  dependency at all (raw fetch to `api.mem0.ai/v3/`); of all carriers only openclaw has
  an OSS code path. The 30k-line TS OSS engine — a genuine full port, quirks and dead
  code included — has one consumer.

## Benchmark provenance

The README's 92.5 (LoCoMo) / 94.4 (LongMemEval) are platform numbers, explicitly and
unusually candidly disclaimed ("proprietary optimizations not available in the
open-source SDK", README.md:54). The in-repo eval harness (1,993 lines incl. zep/
langmem/RAG arms) was extracted to `mem0ai/memory-benchmarks` two months pre-pin;
`evaluation/` is an **uninitialized submodule**, not an empty dir (survey corrected).
Two contradictory number-sets coexist at the pin — 92.5/94.4 (README) vs 91.6/93.4
(migration + changelog docs), same baseline, unreconciled, undated. The
hardest-promoted benchmark (BEAM) is mem0's own — with candidly poor self-reported
scores (48.6 overall at 10M). Nothing in this repo can reproduce any headline number.

## Surprises

1. **A 1,582-line, A/B-tested, remotely-scripted upsell funnel ships inside the OSS
   SDK** — with ~5× the test coverage of the extraction pipeline it monitors.
2. **The paper's replacement mechanism is dead code too.** The survey found the
   ADD/UPDATE/DELETE phase retired; the deep-dive found its successor
   (`linked_memory_ids`) built, prompted, parsed — and discarded. OSS mem0 has *no*
   working memory-revision mechanism; the platform claims one.
3. **The displacement gate fails open without jq** and diverges per harness (Cursor
   blocks any `MEMORY.md` on disk; Claude Code only `.claude` paths) — run-verified.
4. **Session-start exfiltration**: project instruction files uploaded to the platform
   automatically, no consent; raw-turn capture skips the tag sanitization the summary
   path applies.
5. **Graph memory was traded for V3 in a single commit** — an OSS capability
   regression, with the docs still advertising it in one place.
6. **`capture_session_summary.py:180-183`** documents the exact role-confusion bug it
   avoids ("role='user' here turns Claude's opinions into the human's stated
   preferences") — and the pre-compact path still uses `role: "user"`.
7. **Python `mem0ai` 2.0.18 and npm `mem0ai` 3.1.6** — same name, same repo, different
   major versions, both documented as "v3".
8. The header-vs-body lesson recurred: `on_stop.sh`'s header documents a marker-file
   dedup its body doesn't implement (the survey had carried the header claim).

## Open questions

- Does `mem0ai/memory-benchmarks` (`--backend oss`) reproduce anything? An OSS-arm
  number would quantify what README.md:54 leaves vague. Requires cloning the sibling
  repo + paid spend for a cloud arm — preregister if pursued.
- What does the PostHog notice copy actually say? Unreviewable at any pin; determining
  it means running with telemetry on (a decision to preregister, since it transmits).
- Is the `linked_memory_ids` drop a bug or deliberate OSS/platform split? No comment,
  issue, or test decides it in-repo.
- Agent-mode shadow-account TTL: no expiry exists in CLI source; server-side unknown.
- Does the platform's `infer=True` extraction apply provenance/injection filtering
  server-side? Outside this clone — and given `injection_trust_boundary: false` on the
  client side, load-bearing for any real deployment.

## My take

The deep-dive hardened both halves of the survey's verdict and added a third. The
type's commercial pole is *more* open at the core than the survey credited (BM25,
entities, rerankers, vision — all real OSS) and *more* enclosed at the edges than it
knew (V3 removed OSS capabilities; the plugin is platform-hardcoded; the carriers
bypass the SDK). The new third finding is the instrumentation: mem0 is the only tool in
this repo whose open-source artifact contains a live, remotely-controlled marketing
experiment on its own users — the boundary between product and funnel runs *inside*
`pip install mem0ai`. And the displacement story matured from a headline into a
mechanism reading: a narrow, fail-open path gate whose real force is prose — which is,
fittingly, the same enforcement grade this repo keeps finding everywhere prose is
cheaper than code.

## Candidate vocabulary collected

2026-11-06, targeted probe at the pin, not a re-read: five candidate keys Phase 19 weighs (`llm_free_path`, judged per component, `concurrent_write_safety`, `compaction_capture`, the OKF open-format axis and `agent_coordination`) were read at the pin `001c2352` with `git show 001c2352:<path>` and `git grep … 001c2352`. The clone's HEAD (`989c7da`) was not evidence, nothing was installed or run, and the frontmatter above is untouched. Prose only: the keys are unregistered, so no cell exists, and the verdicts are against the presence tests frozen before the reads in the [category README](README.md#candidate-key-census-at-existing-pins-2026-11-06); no shape or value label is written (Phase 19 settles those). The engine the default path means is the open Python SDK `mem0` (class `Memory`, `mem0/memory/main.py`) with the default `MemoryConfig()` and no provider key in the launching environment; the coding-agent plugin `integrations/mem0-plugin` routes to the hosted platform, a named route whose closed half is never source evidence for what a component does. The engine is judged per key (engine per key, 2026-11-08, ADR-0059): the open Python SDK decides `llm_free_path` and `concurrent_write_safety`, and for `compaction_capture` the in-pin plugin handler is the evidence and the hosted store is only the write target. Grades are SOURCE unless tagged. Drift notes are dated and are not census evidence.

- `llm_free_path` — judged on the open Python SDK with the default configuration; the hosted platform and the plugin that routes to it are named routes; the three components follow, each with its own verdict.
  - capture — ✗. The default `add()` makes a generative call: `infer` defaults to true (`mem0/memory/main.py:770`), the raw-text branch is `if not infer:` (`mem0/memory/main.py:880`), and the extraction branch calls `self.llm.generate_response(` with `response_format={"type": "json_object"}` (`mem0/memory/main.py:956`, `mem0/memory/main.py:961`), raising `LLMError` when the call fails (`mem0/memory/main.py:968-969`). The default provider is `openai` (`mem0/llms/configs.py:7`), the model `gpt-5-mini` (`mem0/llms/openai.py:40`) and the key is read from `OPENAI_API_KEY` (`mem0/llms/openai.py:50`); the claim that a missing key raises at construction is library behaviour (INFERENCE, nothing ran). Model path on: always, the default call; the only switch off is the explicit per-call flag `infer=False`, and `OPENROUTER_API_KEY` only reroutes the same call (`mem0/llms/openai.py:42-48`). Egress: the model endpoint, and PostHog telemetry is on by default. Spend: one model call per add. Surface searched: `git grep -n -I -E 'generate_response\(' 001c2352 -- mem0/memory/main.py` prints 2 lines (the add path and the procedural-memory path at `mem0/memory/main.py:2014`); Control: `git grep -c -I -E '\bdef (add|search|update|delete)\b' 001c2352 -- mem0/memory/main.py` prints 10.
  - consolidation — present. (no process) The open SDK has no between-session process: stored records change only when a caller invokes `update`, `delete`, `delete_all` or `reset` (`_update_memory(` is called from `mem0/memory/main.py:1865` and `mem0/memory/main.py:3515`, the public `update` in sync and async form; `_delete_memory(` from `mem0/memory/main.py:1882`, `mem0/memory/main.py:1934`, `mem0/memory/main.py:3532` and `mem0/memory/main.py:3586`). Named and kept out of the verdict because the open engine decides it: an agent-driven dream consolidation that three plugin adapters ship, default on in the OpenCode adapter (`integrations/mem0-plugin/.opencode-plugin/dream.ts:38-46`, `DREAM_DEFAULTS = { enabled: true, auto: true, minHours: 24, minSessions: 5, minMemories: 20 }`), where the harness's own model rewrites memories through the hosted store, so its model, its store and its default state sit outside the open engine; the hosted platform's own decay is likewise outside. Contradiction (2026-11-06): the frontmatter comments at `mem0.md:19` and `mem0.md:29` list a `dream` skill and say nothing in the SDK calls update or delete automatically, which holds for the SDK, but the report does not say that three integrations ship a dream pass; the report is left as read on 2026-08-19. Drift (2026-11-06): the three dream files are deleted at HEAD (`git rev-list --count 001c2352..HEAD -- integrations/mem0-plugin/.opencode-plugin/dream.ts` prints 1). Model path on: no model path found for this component in the open engine. Surface searched: `git grep -n -I -i -E 'consolidat|schedul|\bcron\b|apscheduler|BackgroundTasks|run_forever|periodic|summariz|compact' 001c2352 -- mem0 server ':!*.lock'` prints 11 lines once the prompt-text lines in `mem0/configs/prompts.py` are filtered, none a memory process (a TODO comment, a docstring word, pruning of the `request_logs` table of the server, which holds request logs and not memories, three lockfile lines and two number-format lines); `git grep -n -I -E 'threading\.(Thread|Timer)|asyncio\.(create_task|ensure_future)|ThreadPoolExecutor|atexit' 001c2352 -- mem0 server ':!*.lock'` prints 6 lines (a search pool, two exit handlers, two words and a capture thread); and `git grep -n -I -i -E 'consolidat|schedul|setInterval|cron|periodic|decay|dream' 001c2352 -- mem0-ts/src ':!*.lock' ':!package-lock.json' ':!*test*'` prints only the platform-only decay stub (`mem0-ts/src/oss/src/utils/notices.ts:33-34`) and prompt words. The mem0 vocabulary used was `update`, `delete`, `history`, `decay` and `dream`. Control: `git grep -c -I -E '\bdef (add|search|update|delete)\b' 001c2352 -- mem0/memory/main.py` prints 10.
  - recall — present. Recall makes no generative call on the default path: BM25 lemmatization, spaCy query entities, one query embedding, a vector search with over-fetch, a keyword search, entity boosts and additive fusion (`mem0/memory/main.py:1628-1652`, `raw_combined = semantic_score + bm25_score + entity_boost` at `mem0/utils/scoring.py:118`). Reranking is opt-in: `rerank: bool = False` (`mem0/memory/main.py:1386`), `if rerank and self.reranker and original_memories:` (`mem0/memory/main.py:1500`) and the reranker setting defaults to none (`mem0/configs/base.py:46-49`); the provider factory lists 5 providers (measure: its entries at `mem0/utils/factory.py:233-242`) and only `llm_reranker` calls a generative model (`mem0/reranker/llm_reranker.py:142`). Boundary: the default configuration cannot construct `Memory` without a provider key, because `__init__` builds the embedder (`mem0/memory/main.py:491-495`) and then the model client (`mem0/memory/main.py:499`), the default embedder is `openai` (`mem0/embeddings/configs.py:9`), and which of the two raises first is INFERENCE; clause met: recall's own path makes no generative call and an embedding model is not a generative model; clause failed: the test's fails-without-one wording applies to a generative model, and the construction failure is setup, outside the three components. Falsifier: a run with no key and a local embedder showing recall itself raising. Model path on: explicit flag, a `reranker` block with provider `llm_reranker` plus `rerank=True` on the call. Egress: an embedding call for every query, and PostHog telemetry. Surface searched: `git grep -n -I -E 'generate_response' 001c2352 -- mem0/reranker` prints one line (`mem0/reranker/llm_reranker.py:142`), and `git grep -n -I -E 'generate_response|\.llm\b|LlmFactory' 001c2352 -- mem0/memory/main.py` shows the model client used only by add and the procedural path and their async twins, none inside `search` or `_search_vector_store` (`mem0/memory/main.py:1379-1732`).
- `concurrent_write_safety` — present. The first mechanism is an in-process mutex on the history store: one shared `sqlite3` connection opened with `check_same_thread=False` and a `threading.Lock()` (`mem0/memory/storage.py:14-15`), held by every `SQLiteManager` method that touches the connection. Measure: 9 sites of `with self._lock:` (`git grep -n -I -E 'with self\._lock:' 001c2352 -- mem0/memory/storage.py`), 7 of them writes (a migration, two table creations, `add_history`, `batch_add_history`, `save_messages` and `reset`) and 2 reads (`get_history`, `get_last_messages`). Scope: one process, one `SQLiteManager`; write paths: the `history` and `messages` tables of `history.db`; not covered: vector-store records, whose adapters add no lock (one comment line, `mem0/vector_stores/qdrant.py:601`). The second mechanism is a lock file shared by processes on one host that excludes concurrent dream passes in the integrations: `writeFileSync(lp, JSON.stringify(lock), { flag: "wx" })` after a stale check against a one-hour limit (`integrations/mem0-plugin/.opencode-plugin/dream.ts:155-182`); it covers only that pass and not ordinary adds, and the verdict rests on the first mechanism. Drift (2026-11-06): the dream files are deleted at HEAD, successor undecided (`git rev-list --count 001c2352..HEAD -- integrations/mem0-plugin/.opencode-plugin/dream.ts` prints 1). Surface searched: `git grep -n -I -E 'threading|Lock\(|asyncio\.Lock|filelock|fcntl|flock|portalocker|Semaphore' 001c2352 -- mem0 mem0-ts/src server ':!*.lock' ':!package-lock.json' ':!*test*'` prints 15 lines, classified as imports, notice, telemetry, spaCy and server-state locks, a capture thread and a read semaphore (`mem0/memory/main.py:3418`).
- `compaction_capture` — present. The plugin registers a handler on the harness pre-compaction event in 5 places by the measure at the end of this entry, and the handler posts to the hosted store's add endpoint: Claude Code (`integrations/mem0-plugin/hooks/hooks.json:102`), Codex (`integrations/mem0-plugin/hooks/codex-hooks.json:92`), Cursor (`integrations/mem0-plugin/hooks/cursor-hooks.json:44`), Kimi (`integrations/mem0-plugin/.kimi-plugin/plugin.json:66`) and OpenCode (`integrations/mem0-plugin/.opencode-plugin/opencode-mem0.ts:382`, `"experimental.session.compacting": compactionHook`). The shell handler starts `on_pre_compact.py --source=pre-compaction` in the background (`integrations/mem0-plugin/scripts/on_pre_compact.sh:19-21`), which posts the session state with `"infer": True` to `/v3/memories/add/` (`integrations/mem0-plugin/scripts/on_pre_compact.py:171-191`), skipping when no API key resolves, when the agent already stored a memory this session or when no file was modified (`integrations/mem0-plugin/scripts/on_pre_compact.py:245-293`); the OpenCode hook calls `mem0.add(…, infer: true)` without waiting (`integrations/mem0-plugin/.opencode-plugin/opencode-mem0.ts:963-979`) and then re-injects memories, which is named and not counted. Clause met: a registered handler on the pre-compaction event writes to the store through its own write endpoint by starting a background job, and the store is the hosted platform's closed half; the Claude Code manifest path is by plugin convention (INFERENCE, `.claude-plugin/plugin.json` has no `hooks` key), and the verdict does not rest on it because the other four are wired explicitly. Named and not instances: the post-compaction capture at session start (`integrations/mem0-plugin/scripts/capture_compact_summary.py`), the OpenClaw filter text, and OpenClaw and the pi adapter, which register no compaction handler. Drift (2026-11-06): the registration moved with the plugin, `git rev-list --count 001c2352..HEAD -- integrations/mem0-plugin/hooks integrations/mem0-plugin/scripts integrations/mem0-plugin/.opencode-plugin` prints 3 and the manifests, scripts and `opencode-mem0.ts` are deleted at HEAD, while `integrations/claude-code-plugin/hooks/hooks.json:86` still registers `PreCompact`; what the HEAD handler writes is undecided. Measure: `git grep -n -I -E 'PreCompact|preCompact|compacting' 001c2352 -- integrations ':!*.lock' ':!*test*'` prints 13 lines, 5 of them the registrations above and the rest documentation, scripts and comments.
- The OKF open-format axis — ✗. No OKF declaration at the pin; the house formats are named and not counted: `integrations/mem0-plugin/scripts/parse_export_file.py:2-10` parses `mem0-export-*.md` blocks with YAML-like frontmatter, and the platform export is `create_memory_export(schema)` (`mem0/client/main.py:624`). The mem0 vocabulary used was `mem0-export-*.md`, `create_memory_export`, `export_format` and `frontmatter`. Surface searched: `git grep -n -I -i -E '\bokf\b|open knowledge format' 001c2352 -- . ':!*.lock' ':!package-lock.json'` prints nothing, and `git grep -l -I -i -E 'frontmatter|front-matter|export_format|markdown export' 001c2352 -- ':!*.lock' ':!package-lock.json'` lists 18 files, none an OKF reference. Control: `git grep -c -I -i -E '\bmemory\b' 001c2352 -- ':!*.lock' ':!package-lock.json'` prints 745 files.
- `agent_coordination` — omitted: Premise: the source-visible half has no agent-to-agent mechanism in the SDK, server, CLI, skills or plugin, but the plugin's agent-facing tool registry is a hosted MCP server that is not at the pin, so the searched surface excludes a shipped integration of exactly this key's class: `integrations/mem0-plugin/.mcp.json` points at `https://mcp.mem0.ai/mcp/`, the pin lists no server code for it (the only paths with `mcp` in their name are documentation and client configuration files), and the hosted server is premised to expose at least one tool by which one agent addresses or hands work to another. The vendor's tool lists are TESTIMONY and cannot decide; by the measure of each document's own tool table the plugin README lists 9 tools (`integrations/mem0-plugin/README.md:270-278`) and the platform document lists 11 (`docs/platform/mem0-mcp.mdx:64-74`), so the count depends on the document, and neither list describes a coordination mechanism. Test: an authenticated MCP `tools/list` against `https://mcp.mem0.ai/mcp/`, dated; if no listed tool addresses or hands work to another agent, the verdict is ✗. Isolation by `agent_id` and `run_id` query filters (`mem0/memory/main.py:1457-1461`) is named and not coordination. Drift (2026-11-06): HEAD adds a Claude Code subagent definition whose tool list includes the harness tool `SendMessage` (`integrations/claude-code-plugin/agents/sidekick.md`) and `core/mcp_server.py` (`git rev-list --count 001c2352..HEAD -- integrations/claude-code-plugin/agents core/mcp_server.py` prints 2); whether either is a hand-off mechanism on mem0's side is not read. Surface searched: `git grep -n -I -i -E '\b(mailbox|inbox|handoff|hand[_ -]off|send_message|post_message|claim_task|task_queue|work_queue|lease|delegate_to|assign_to|notify_agent|agent_to_agent|a2a)\b' 001c2352 -- mem0 server mem0-ts/src cli skills integrations ':!*.lock' ':!package-lock.json' ':!**/pnpm-lock.yaml'` prints 8 lines, none a mechanism (two sign-up messages, four email-inbox use-case lines and two hand-off steps in a workflow). Control: `git grep -l -I -E 'agent_id' 001c2352 -- mem0 server mem0-ts/src cli skills integrations ':!*.lock' ':!package-lock.json' ':!**/pnpm-lock.yaml'` lists 122 files.
