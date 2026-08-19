---
name: mem0
layer: 5
kind: memory
vendor: Mem0 (mem0ai, YC S24)
url: https://github.com/mem0ai/mem0
license: Apache-2.0
open_source: true
stack: [TypeScript, Python]
version: ts-v3.1.6-20-g001c2352
commit: 001c2352
first_commit: 2023-06-20
stars: 63535
stars_at: 2026-08-18
read_at: 2026-08-19   # deep-dive, same pin as the 2026-08-18 survey (zero upstream drift); vendor paper separately at full depth (refs/2025-mem0.md)
depth: deep-dive   # 2026-08-19: three parallel readers at the pin (plugin/carrier script bodies; SDK write/read machinery incl. async + TS port; platform boundary/server/benchmark provenance), load-bearing claims spot-verified in main session; displacement gate RUN-probed with synthetic hook payloads (host + alpine/jq container)
harness_targets: "in-repo at the pin: integrations/mem0-plugin targets Claude Code, Claude Cowork, Cursor, Codex, OpenCode, Antigravity (hooks.json + codex-hooks.json + cursor-hooks.json + a Kimi shim; MCP config bundled — all four MCP manifests point at the hosted mcp.mem0.ai, no stdio/localhost option); also integrations/openclaw (the only carrier with an OSS code path) and pi-agent-plugin, plus non-harness carriers (vercel-ai-sdk — which bypasses the SDK entirely, zapier, n8n) and 17 in-repo skills (survey's six-skill count was closer to the pi-agent set)"
features:
  skills: true   # 17 skill dirs in the Claude plugin (all with SKILL.md, verified by count) (context-loader, dream, import, policy, remember, …) — survey's "six" corrected at deep-dive
  learning_loop: true   # background, via the in-repo harness plugin: Stop/PreCompact hooks capture with infer=True → V3 LLM extraction, no human in loop; PLUS auto_capture every 3rd message uploading raw turns, and auto_import shipping CLAUDE.md/AGENTS.md/.cursorrules to the platform on session start with no consent step (deep-dive)
memory_features:   # deep-dive 2026-08-19 — two survey cells FLIPPED (memory_tiers, decay), one settled (injection_trust_boundary)
  memory_store: vector           # one shared collection + an entity store (second vector collection, spaCy-extracted, one-hop). GRAPH MEMORY REMOVED from OSS in the same commit that landed V3 (a488e190, 2026-04-14, −2,849 lines) — platform-only now; docs/platform/platform-vs-oss.mdx:65 still advertises OSS graph support and is stale
  capture_path: hook             # Stop/PreCompact/UserPromptSubmit hooks; auto_capture every 3rd message (raw turns, unsanitized); infer=True → V3 extraction
  write_admission: unfiltered    # V3 ADD-only extraction admits whatever the LLM reads as a fact from the transcript; no enactment or outcome gate; contradiction handling explicitly the caller's job; the plugin NUDGES eager writing ("Aim for 1–3 memories per substantial interaction"). Combined with the openclaw recall protocol's memories-as-mandatory-rules, this is the injection-to-authority pipeline the registry note names
  recall_injection: auto         # per-turn top_k=5 (reranked by default) + session-start 10-memory timeline + opportunistic file-read (5×150ch) and stack-trace injections — all as bare markdown in additionalContext
  memory_scope: [user, agent, session]  # query FILTERS in one shared collection, not namespaces; ≥1 scope id mandatory on every write/read (VALIDATION_001); isolation = each store adapter's filter translation
  memory_tiers: false            # FLIPPED ✓→✗ at deep-dive: procedural_memory is a metadata tag on the SAME collection with no distinct retrieval path (memory_type never read at search); MemoryType.SEMANTIC/EPISODIC are unreachable enum values; and procedural without agent_id silently falls through to the normal pipeline
  hybrid_retrieval: true         # real but conditional: additive fusion with adaptive divisor (NOT RRF, scoring.py:99-137); BM25 can only re-rank the semantic candidate pool, never add to it; spaCy+fastembed are optional extras, so a bare `pip install mem0ai` silently degrades to pure vector search; 15/25 stores implement keyword_search
  memory_revision: caller-only   # deep-dive 2026-08-19: nothing in the SDK ever calls update/delete automatically; a shifted preference is a LINKING trigger and the link is discarded; contradiction handling is the application's job
  decay: false                   # FLIPPED ✓→✗ at deep-dive: decay/timestamp/reference_date HARD-RAISE in OSS (main.py:468-471, :817, :1430) — routed through the upsell-notice path; expiration_date is post-fetch hiding on a date string (expired rows still consume top_k slots); platform-only feature. Survey's ✓ read client params to the paid API
  injection_trust_boundary: false  # SETTLED (was an open question): the sole plugin formatter emits bare markdown (_search.py:92-105) — no delimiter, no data-not-instructions framing; openclaw's tags are containers whose preambles say the OPPOSITE ("Use them to personalize your response"), and its recall protocol makes memories authoritative: "Rules are mandatory… Rules override your defaults" — staleness is questioned, provenance never
  deployment_mode: both          # load-bearing asymmetry: the core V3 algorithm IS open (BM25, entities, 6 rerankers, vision), the server is production-grade — but the coding-agent plugin is platform-HARDCODED (api.mem0.ai literal in every script, no MEM0_BASE_URL, settings loader filters unknown keys), V3 net-REMOVED OSS features (graph, temporal, decay), and the SDK ships a 1,582-line A/B-tested upsell funnel (notices.py)
  harness_installer: true        # hooks.json bundle across 6 harnesses + MCP config; SessionStart also appends MEM0_API_KEY to the harness env file
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
association layer, not a graph.

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
  same. On ADR-0011's ladder: `script`-graded enforcement for a narrow path set, with
  prose carrying the intent.

## What the plugin injects, and what it captures

Injection is **bare markdown, no trust framing** — settled as the kind's negative pole
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
kind's commercial pole is *more* open at the core than the survey credited (BM25,
entities, rerankers, vision — all real OSS) and *more* enclosed at the edges than it
knew (V3 removed OSS capabilities; the plugin is platform-hardcoded; the carriers
bypass the SDK). The new third finding is the instrumentation: mem0 is the only tool in
this repo whose open-source artifact contains a live, remotely-controlled marketing
experiment on its own users — the boundary between product and funnel runs *inside*
`pip install mem0ai`. And the displacement story matured from a headline into a
mechanism reading: a narrow, fail-open path gate whose real force is prose — which is,
fittingly, the same enforcement grade this repo keeps finding everywhere prose is
cheaper than code.
