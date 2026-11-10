# 5 — Memory

`checked: 2026-11-10`

Persistent cross-session state as an installable product — **the agent↔time edge**. Fed
by hooks/MCP during a session, consolidated between sessions, injected back at the next
session start, on any harness. A full category since the 2026-08-22 split
([ADR-0020](../../adrs/0020-memory-category-extensions-renumbered.md)); born 2026-08-18
as the extensions bucket's `memory` type (the bucket is now
[category 6](../6-extensions/README.md)). Reports keep `type: memory` in frontmatter as
residual data. Roster count (2026-11-10, measure: the reports under `tools/5-memory/`, this
README excluded, whose frontmatter carries `category: 5`, split by their `depth:` value): **ten**
reports carry `category: 5` — six deep-dives, one survey and three stubs — the ten rows in the
generated [tools matrix](../../comparisons/tools.md). The earlier count, kept as history,
was **eight** on 2026-08-22: openviking was one of those eight, as a stub, and is a deep-dive since
2026-11-05, and mempalace and agentmemory were added as new deep-dives on 2026-11-05. ADR-0020's
"all nine reports stay" counted the pre-split bucket's nine files, which included ecc — moved to
category 6 by the same ADR; the immutable ADR body stays as written, this note is the correction.

What the category's reports wager (2026-11-10), in one line each: markdown wiki (ai-memory), RL policy
database that mints skills (memos), knowledge graph over a tripartite store (cognee),
LLM-extraction platform sold on benchmarks (mem0), a browsable `viking://` context database
whose every autonomous memory write needs a configured model (openviking: the model-required
pole, a stub until its 2026-11-05 deep-dive), verbatim exchanges filed with no model on capture
or recall (mempalace: the verbatim, model-free store), and hook-fed events kept as synthetic
observations, with the model optional and the storage engine borrowed from a third party
(agentmemory); three stubs remain as of 2026-11-10, facts collected mechanically and no full
source read (everos, memmachine, memori). Memori's five census keys were read in source on
2026-11-06 as targeted probes, which did not change its depth: it is counted a stub by its
`depth:` value, not by how much evidence it carries.

Four consolidation postures were verified at the first cut: background cron, per-turn event
cascade, agent-invoked, hook-capture-to-platform. The 2026-11 reads add two: openviking's
client-triggered commit with a model-backed queued extraction, and agentmemory's model family,
mounted by ambient provider-key presence with no opt-in flag (`CONSOLIDATION_ENABLED=false`
switches it off). Counted 2026-11-10, **six** postures, measure: the postures this paragraph
names; no registry key enumerates them, so this is a dated reading, not a tally over cells.
**Zero shared formats** (as first counted 2026-08-18) — each
vendor pays the harness-fragmentation cost separately, in code (tracked as a dated watch
note beside the [standards scoreboard](../../docs/standards.md)). Qualified 2026-11-10: the
Open Knowledge Format (OKF) now has one conformant export, ai-memory's v0.2 `export-okf`
(its on-disk tree is not conformant by the spec's letter), and one house declaration,
openviking's `OKF_VERSION = "0.1"`, which cites no spec: a declaration, not conformance.
So two reports now name one format, but only one instance conforms to it, and the spec's own
location has skewed (a frozen copy and a live repository); the standards watch note beside the
scoreboard tracks the format question. The SDK-facing
shapes earn membership via their shims, and the shims are where the coding-agent
behavior lives — up to and including mem0's plugin *blocking the harness's native memory
writes* (the displacement finding, conclusion 8).

Since 2026-08-25 the category has an explicit component decomposition —
**capture · consolidation · recall**, each with a trust sub-question
([taxonomy §5](../../docs/tool-taxonomy.md), ADR-0023); the first-cut axes below read as views
of those components (capture path → capture; store wager → consolidation; recall
injection and trust boundary → recall), and `harness_installer` is the aperture, not
a pipeline stage.

## What we assess here

The assessed block is **`memory_features:`, 19 keys** (2026-11-08, from 15 on 2026-09-04:
[ADR-0013](../../adrs/0013-memory-features-block.md) + `memory_import` via
[ADR-0051](../../adrs/0051-memory-import-key.md) + `team_sharing` via
[ADR-0052](../../adrs/0052-team-sharing-key.md) + four keys via
[ADR-0059](../../adrs/0059-memory-vocabulary-admission.md)): `memory_store`, `capture_path`,
`write_admission`, `recall_injection`, `memory_scope`, `memory_tiers`,
`hybrid_retrieval`, `decay`, `memory_revision`, `injection_trust_boundary`,
`deployment_mode`, `team_sharing`, `harness_installer`, `rule_extraction`,
`memory_import`, `compaction_capture`, `llm_free_path`, `concurrent_write_safety`,
`agent_coordination`. They map
onto the three components above, taking the registry's own groups (store-scope, write-path,
read-path, integration) as the basis. **Capture** takes the write-path keys that act as a
memory arrives: `capture_path`, `write_admission`, `compaction_capture` (whether a handler on
the harness's pre-compaction event writes to the store) and `concurrent_write_safety` (how
concurrent writers are ordered, a key that sits between capture and the store).
**Consolidation and the store** takes the store-scope keys — `memory_store`, `memory_scope`,
`memory_tiers`, `deployment_mode` and `team_sharing` — together with `decay` and
`memory_revision`, which the registry files under write-path but which act on memories already
stored. **Recall** takes `recall_injection`, `hybrid_retrieval` and
`injection_trust_boundary`. `llm_free_path` is judged once per component and spans all three: a
list of the components whose default path makes no generative-model call. The apertures onto
the outside are the integration keys: `harness_installer` (how the tool meets a harness),
`memory_import` (whether memory made elsewhere can come in), `agent_coordination` (whether one
agent can address another through the tool) and `rule_extraction`, which sits between an
aperture and consolidation: the registry files it under integration, while this note's
2026-08 reading counted it as consolidation, because the rules are a consolidation product.

Values are **descriptive enums naming a mechanism choice, not ADR-0011 enforcement
grades**: every tool in this category stores something and recalls something, so the
finding is always *which* posture, never *whether*. Six consolidation postures are
verified as of 2026-11-10 (the opening names them), and the roster's zero shared formats
(qualified in the opening: one conformant OKF export, one house declaration) is the
population-level version of the same point.

The other half is **9 transcription fields** — `maker`, `license`, `access`, `stars`,
`first_commit`, `version`, `commit`, `stack`, `harness_targets` — facts copied from a dated
source rather than judged.

Both halves are read as **seven groups** — Identity · Provenance · Shape · Store & scope ·
Write path · Read path · Integration — the middle three following a memory in, through and
out of the store: [`feature-registry.md` § Memory](../../comparisons/feature-registry.md#memory).

Definitions:
[`comparisons/feature-registry.md`](../../comparisons/feature-registry.md). Values:
[`comparisons/features.md § Memory`](../../comparisons/features.md#memory-category-5). A
key is set **only** when verified in source or official docs — omitted means "not
checked", `false` means "checked and absent", and both are claims.

## The memory matrix — first cut (2026-08-19)

The reading arc's prose comparison became a registry block
([ADR-0013](../../adrs/0013-memory-features-block.md)): 11 keys at the first cut
(13 since, same day: `memory_revision` after the mem0 deep-dive, `write_admission`
after exp-04 arm C), generated
[matrix](../../comparisons/features.md), cells
set only on the four read tools (seven reports carry a `memory_features` block as of
2026-11-10, the last two having landed on 2026-11-05; the three stubs carry none). What the
first cut shows:

- **Where the type agrees** — *weakened by the mem0 deep-dive (2026-08-19), which
  flipped two of its survey ✓s*: typed tiers are now 3/4 (mem0's "tier" is a metadata
  tag), decay 2✓/1✗/1·, hybrid fusion and installers hold at 3/4. The survey-depth
  "engineering table stakes converged" reading was partly an artifact of reading
  client parameters as capabilities — the deep-dive found the params raise in OSS.
- **Where it splits** — the identity axes: store wager (`files-git` / `vector` /
  `rows+vector` / `graph+vector+rows`, no two alike), capture path (hook / adapter /
  agent-invoked), recall injection (auto / pull-only / both), and the trust boundary
  (2✓ / 1✗ / 1· — mem0's open question settled to a verified ✗ at deep-dive, with the
  openclaw recall protocol actively inverting the boundary; the security axis is the
  least converged, and memory injection is a prompt-injection vector).
- **The type's central pattern, as of the third deep-dive (memos, 2026-08-19): presence≠operative.** mem0's ✓s dissolved on source contact; memos' ✓s all CONFIRM in source and then ship dark — the entire evolution half (revision, rules, tiers beyond traces) sits behind a default-off flag verified in the published artifact. The matrix records capability; the default install is a separate, thinner fact the cell comments now carry.
- **The asymmetry worth flagging**: every axis above has 2–4 verified instances, but
  the type's *headline* bet — cross-harness continuity as a working mechanism — has
  exactly **one** (ai-memory's baton, and it is thin: first + last prompt + tool
  names, no LLM). The category's sales pitch rests on its least-instantiated feature.
  ~~The rig question (capture a session, switch harness, measure what the second agent
  actually knows) is what would test it.~~ **Measured 2026-08-19 (exp-04, n=1)**: the
  automatic floor is 0/10, the pull ceiling 10/10 verbatim, and the harness boundary
  costs nothing on the pull path — the bet is real and entirely **pull-shaped**
  (conclusion 14). The type's pitch says "your agent remembers"; the measurement says
  "your agent can look it up, if it asks".

Re-derived 2026-11-10 over the seven reports with a memory_features block (measure: each
report's default cells in its frontmatter, read per [ADR-0060](../../adrs/0060-options-with-default-grammar.md)
with `options:` alternatives left out; the seven are agentmemory, ai-memory, cognee, mem0,
memos, mempalace and openviking; the three stubs everos, memmachine and memori carry no block,
so they sit outside every denominator and are unset, never ✗; a value with no instance is
written 0; tools are listed alphabetically). The first cut's tallies above stay as read on
2026-08-19; these are the same axes at the final roster:

- **Where the type agrees.** Typed tiers 6 ✓ (agentmemory, ai-memory, cognee, memos, mempalace, openviking) · 1 ✗ (mem0) · 0 unset.
  Hybrid fusion (`hybrid_retrieval`) 6 ✓ · 0 ✗ · 1 unset (cognee). Installers (`harness_installer`)
  6 ✓ · 0 ✗ · 1 unset (cognee). Decay 4 ✓ (agentmemory, ai-memory, memos, openviking) · 2 ✗ (mem0, mempalace) · 1 unset (cognee),
  so decay is the most split of the four (tiers has one ✗, mem0; hybrid fusion and installers have none).
- **Where it splits.** Trust boundary 2 ✓ (ai-memory, memos) · 4 ✗ (agentmemory, mem0, mempalace, openviking) · 1 unset (cognee):
  the least converged axis moved from 2 ✓ against 1 ✗ at the first cut to ✗ outnumbering ✓ two to one among the
  cells set. Capture path: `hook` 5 (agentmemory, ai-memory, mem0, mempalace, openviking) · `adapter` 1 (memos) · `agent-invoked` 1 (cognee).
  Recall injection: `auto` 2 (mem0, memos) · `both` 2 (ai-memory, openviking) · `pull-only` 3 (agentmemory, cognee, mempalace).
- **The store wager, and whether "no two alike" holds.** It holds as the lists are written, because
  a list puts the primary store first and so order counts: 7 distinct `memory_store` values over 7 cells. Counted by members
  regardless of order it fails for one pair, agentmemory (`rows`, `graph`, `vector`) and cognee (`graph`, `vector`, `rows`),
  which hold the same three members with a different primary: 6 distinct member sets over 7 cells.

Single-instance bets stay out of the vocabulary by the two-instance rule but are the
differentiators to watch: zero-LLM default (ai-memory), git-versioned store
(ai-memory), native-memory displacement (mem0), skill crystallization (memos),
provenance audit (ai-memory). One graduated (2026-09-04,
[ADR-0051](../../adrs/0051-memory-import-key.md)): *competitor import* fired its
second instance at ai-memory's v2.0.2 re-read (the companions importer, beside mem0's
import paths) and is now the `memory_import` key — and the same-day probe-pass that
settled the remaining read seeds found it **universal**: 4-for-4 ✓ (memos imports the
host harness's native MEMORY.md and OpenClaw transcripts; cognee ships dedicated
mem0/zep/letta/langmem importers). Every mature seed pays the arrive-with-your-memory
toll; what discriminates is the *source family* — rival SaaS stores, harness-native
stores, repo rule files, transcripts — and only mem0 pairs the in-direction with
displacement on the way out. Newly watched from the same re-read, each one instance:
tombstoned deletion (ai-memory `purge-session`), temporal recall (ai-memory `as_of`),
typed relation edges (ai-memory).

Qualified 2026-11-10: the zero-LLM default is no longer a single-instance bet, and the phrase
promises less than the first cut gave it. MemPalace and agentmemory are model-free on capture
and recall by default (their reports). ai-memory, the first instance, now runs a provider-free
cross-project profile pass, default-on for a single-operator install, and is not egress-free by
default: it background-fetches a keyless embedder on install. agentmemory's model family follows
ambient provider-key presence, and MemPalace's `init` is model-on by default, a setup step
outside the three components. Counts from this README's own census table (§ Candidate-key
census, the 2026-11-06 verdicts; measure: each tool's verdict per component against the frozen
presence test): capture present 3 of the eight tools read, recall present 5 of the eight tools read,
consolidation present 6 of the eight tools read. Over the cells themselves as of 2026-11-10 (measure: the
components listed in each `llm_free_path` cell, over the five reports that carry one, memos'
having been omitted as the census section records): capture 3, consolidation 4, recall 4.

A second key was probed into existence the same day, from the other direction
(2026-09-04, [ADR-0052](../../adrs/0052-team-sharing-key.md)): a stack question —
*can a team of developers share one store?* — that the vocabulary could not express
and the reports had recorded only through the isolation lens. `team_sharing` found
its two instances at the existing pins in **opposite postures**: ai-memory shares
everything and attributes (`attribution-only` — no RBAC, by design), cognee isolates
and grants (`acl` — `share` is itself a permission). Same question, inverted trust
default — the store-side rhyme of the read-path's `injection_trust_boundary` split,
and under the attribution-only posture, `write_admission` is the only gate between
one teammate's compromised session and everyone's recall. mem0 and memos settle ✗
(platform-only constructs and hub-visibility flags respectively — neither a human
identity model in the shipped artifact). A same-day docs pass over the hosted and
stub side (vendor docs, retrieved 2026-09-04) found the axis live beyond the read
seeds: mem0's and cognee's clouds both sell member-managed team scopes, memori's
docs list "Team Memory" as explicitly roadmap-only, openviking's auth docs describe
a multi-human account/role model at mechanism level, and everos/memmachine surfaces
showed nothing — stub cells stay unset (stub honesty), but the axis is worth a look
whenever one of those four is next read (openviking since was; the amendment below).

Amended 2026-11-10 (fold-in), from the cells (measure: default cells over the seven reports with
a memory_features block; the three stubs carry none and stay unset): `team_sharing` reads
`attribution-only` 3 (agentmemory, ai-memory, mempalace), `acl` 2 (cognee, openviking),
✗ 2 (mem0, memos), 0 unset. The 2026-09-04 text above stays as the record of that day's two
instances; four things moved since. (1) ai-memory still ships `attribution-only` as its default
and now offers `acl` beside it: per-project `restricted` grants since 2.5.0, behind a root-only
switch, so "no RBAC" holds within a project and no longer at the project boundary. (2) openviking
is no longer a stub: read in source on 2026-11-05 it is `acl` by design (accounts, groups and
per-container grants on `viking://resources` only), default-unmounted (the shipped auth is
`dev`, one ROOT principal on a loopback bind), and its memories stay per-user private rather
than shared. (3) mempalace and agentmemory are `attribution-only` and default-unmounted, both
with a weaker attribution than ai-memory's authenticated-user kind: mempalace's is a
caller-supplied `added_by` string, agentmemory's is the server process's configured user id.
(4) What stays unread is the stub side, memori, everos and memmachine; memori's "Team Memory is
roadmap-only" reading above is a vendor-docs claim of 2026-09-04 and was never source-read.

## Reports

| Tool | Depth | One-line |
|---|---|---|
| [**ai-memory**](ai-memory.md) | deep-dive (2026-08-18; **v3.3.3 release re-read 2026-11-05**) | Cross-harness memory as one Rust daemon: hook capture (closed 10-type vocabulary) → rule-based session pages in a git-versioned markdown wiki → heuristic handoff injected at next session start, any harness. Zero-LLM default path, but no longer loop-free: a provider-free cross-project profile pass is default-on for a single-operator install and admits a standing preference on one prompt sentence that says "everywhere" (source-read, not observed); with a provider, a **source-verified background learning loop** auto-approves its own wiki edits (`_rules/`, `procedures/`) — second harness-independent instance after ECC. Surprise: the continuity baton is still first + last prompt + tool names, no LLM; the rich memory is pull-only via 25 served MCP tools (18 at v2.0.2). The default install background-fetches an ~87 MB keyless embedder from huggingface.co and turns hybrid retrieval on, so it is not egress-free. Pages carry Google-Cloud-OKF v0.2 frontmatter, but only the export is conformant by the spec's letter (the on-disk event ledgers are not) and the spec location ai-memory cites is a frozen copy. `team_sharing` default stays attribution-only; per-project `restricted` access with root-only grants ships since 2.5.0. 162 claim units confronted across 44 releases; stars 5.7k → 15.1k in two months (2026-09-04 → 2026-11-04). |
| [**mem0**](mem0.md) | **deep-dive (2026-08-19)** | The type's commercial pole (YC-backed platform + OSS SDK). Shipped write path ≠ the 553-citation paper: V3 is ADD-only extraction with linking, the paper's ADD/UPDATE/DELETE/NOOP phase is retired. In-repo plugin installs hook capture into six harnesses with a **background learning loop** (Stop-hook capture, `infer=True`) — fourth verified instance — plus the type's most aggressive move: a PreToolUse gate that **blocks the harness's native MEMORY.md writes** and redirects to mem0's tool. Displacement, not just colonization. Vendor paper graded separately ([2025-mem0](../../references/papers/2025-mem0.md)): its own full-context baseline beats the memory system on quality. **Deep-dive 2026-08-19** (same pin): two matrix cells flipped (tiers, decay — both platform-only or tag-deep in OSS); trust boundary settled ✗ (openclaw protocol makes memories authoritative: "Rules override your defaults"); the displacement gate run-probed — narrow path glob, fails open without jq, broader on Cursor than Claude Code, prose carries the real intent; V3 removed graph from OSS in the commit that added it; and the SDK ships a 1,582-line remotely-scripted A/B upsell funnel (notices.py) with 5× the add-pipeline's test coverage. |
| [**cognee**](cognee.md) | survey (2026-08-18) | The type's incumbent (2023-08, 33.1k stars at 2026-11-04) and its knowledge-graph pole — at the price of a tripartite graph+vector+relational consistency surface. Membership verdict: the SDK sits in the category **via its shims**, and the shims are where the coding-agent product lives (agent-scoped datasets, session/permanent split, agent-invoked `improve` consolidation, coding-rule extraction). No autonomous loop in-repo (`learning_loop: false`); the marketplace plugin automates capture but runs in API mode, where rule extraction is explicitly skipped. ai-memory's opposition dossier spot-checked: both structural claims corroborated (LiteLLM/Instructor churn guard; the Ladybug fork's costs written into pyproject). |
| [**memori**](memori.md) | stub (2026-08-18) | "Memory from what agents do, not just what they say" — Rust core with Python/Node bindings, BYODB or cloud, 17.4k stars at 2026-11-04, about 15 months after its first commit of 2025-07-24. Action-capture framing, embeddable-engine shape. |
| [**everos**](everos.md) | stub (2026-08-18) | EverMind's "Ever OS": durable writes + retrieval, Claude Code plugin shipped in-repo. Youngest seed (first commit 2026-06-05; 13.8k stars at 2026-11-04, about 22 weeks after it). The stub read's note of a very high stars-to-commits ratio dates from 2026-08-18 and is not restated here as a figure, because its commit count has no date at this pin. |
| [**memos**](memos.md) | **deep-dive (2026-08-19)** | Two products in one repo: the Python research OS (MemCube, paper lineage) and — what harnesses actually install — a standalone TS core ("Reflect2Evolve V7") behind OpenClaw/DSH/hermes adapters. **Learning loop verified: background**, an event-driven cascade (trace capture → reward backprop → policy induction → world models → skill crystallization) — the type's formal ceiling: memory as a scored, evolving policy database that *mints skills*, not prose. Third harness-independent instance; issue #13's trigger still unfired. **Deep-dive 2026-08-19** (same pin): the anti-mem0 — every survey cell CONFIRMED in source (golden-tested backprop, genuinely distinct tier stores, three live demotion paths, the type's strongest trust boundary) — and then the twist: `lightweightMemory: true` ships as default in code, templates, AND the published npm artifact (probed), unmounting the entire evolution cascade; the installer is the study's most aggressive (a `.pth` hook monkey-patching hermes' profile creation, no uninstall); and telemetry credentials are injected at npm publish — the pin doesn't describe the artifact. |
| [**memmachine**](memmachine.md) | stub (2026-08-18) | "The open-source memory layer for AI agents" — plain store-and-retrieve SDK (Python), OpenClaw/Strands integrations. The type's commodity baseline. |
| [**openviking**](openviking.md) | **deep-dive (2026-11-05)** | ByteDance/Volcengine's "context database": memories, resources and skills in one `viking://` virtual filesystem the agent browses (`ls`/`tree`/`grep`) and an operator can inspect, with per-directory L0/L1 sidecars. The stub's retrieval claim did not survive: directory-recursive search with a browsing trajectory was removed on 2026-09-29, and recall is now one global vector search scoped by a path prefix. The model-required pole: every autonomous memory write needs a configured VLM, the commit is client-triggered by default, and one shared installer reaches 14 harnesses (ai-memory's `install-hooks` registry is wider: 29 agent variants, 40 documented targets). OKF is a house name rather than a followed standard (v0.1-shaped, spec never cited, no conformance gate). The degraded-mode run (no VLM) stopped at server start on a musl-linked embedder wheel, so commit, resource and search are source-read only. 41.5k stars at 2026-11-04 (the report's `stars:` pair); the set's only AGPL-3.0. |
| [**mempalace**](mempalace.md) | **deep-dive (2026-11-05)** | Local-first, verbatim conversation memory: every exchange is filed unchanged as a "drawer" in a chromadb collection (wings and rooms are labels; the knowledge graph is a separate, optional SQLite file) and found by vector search blended with BM25, with no chat model on capture or recall. The finding that matters: every named write path reaches one cross-process lock at the collection seam (retrofitted after field corruption, in `v3.3.5`), but the lock refuses instead of queueing, so a long-lived server or daemon starves other writers' autonomous captures, and `migrate`, the readers' own chroma client and the SQLite stores sit outside it; the four pre-read predictions score 3 true and 1 false. `init` is LLM-on by default (a local Ollama, falling back to heuristics); the zero-LLM probe (`init --no-llm`, mine, search, wake-up, audit) was zero-spend but not zero-egress. The 96.6% headline benchmark builds no MemPalace code path and the held-out label is contradicted by the vendor's own split file (testimony, not reproduced). Read at the `v3.11.0` tag; the default branch `develop` is 406 commits ahead. 60.4k stars at 2026-11-05. |
| [**agentmemory**](agentmemory.md) | **deep-dive (2026-11-05)** | A hook-fed memory server for coding agents (TypeScript, Apache-2.0): hooks post every tool event to one local REST server, which stores a synthetic observation with no model and fuses BM25, a heuristic graph and, with an embedding provider, vectors, behind 54 MCP tools. The retraction essay's three named defects score changed 2 and gone 1 at the pin, each fix an ancestor of the tag: the keyword index is rebuilt at every start by design, with no save left to fail; the "5-second loss window" is answered by a retained-copy, boot-identifier and deadline protocol, with six residual paths named from source and not tested; the wrong-hook field read is fixed; the ~47% fraction is undecidable by source and is not estimated. The pre-read predictions' six units come out 2 true, 3 false and 1 undecidable. The ceiling: every durable write goes through iii, a separate engine downloaded as a binary and licensed in part under Elastic-2.0, whose internals are not read. A provider key in the launching shell mounts a background model loop with no opt-in flag (`CONSOLIDATION_ENABLED=false` switches it off); the default is zero-LLM and zero-spend, not zero-egress on its first boot, and the full server booted without /dev/kvm. Read at the `v0.9.31` tag, 46 commits behind `origin/main` on 2026-11-05. 30.2k stars at 2026-11-05. |

## The distinction that matters

- **category 5 governs continuity** — what survives the session.
- **category 6 governs reach** — what the agent can access.
- **category 2 is the absorption pressure** — harnesses ship native memory loops
  (conclusion 8), and this category's survival bet is the one thing a single harness
  cannot absorb: cross-harness continuity.

## Candidate-key census at existing pins (2026-11-06)

Phase 19 decides which candidate keys the registry admits, and it starts from the whole roster, not from the four reports read in Phases 16 and 17. This section counts five candidate keys (`llm_free_path`, judged per component, `concurrent_write_safety`, `compaction_capture`, the OKF open-format axis and `agent_coordination`) across the eight tools that have a source read of them. It is prose only: the keys are unregistered, so no cell exists (as of 2026-11-06), and nothing here changes a report's frontmatter or a generated page. Cells set 2026-11-08 ([ADR-0059](../../adrs/0059-memory-vocabulary-admission.md)): see [the matrix](../../comparisons/features.md#memory-category-5).

Measure: each tool's verdict word, present, ✗ or omitted, against the presence test frozen below, once per component for `llm_free_path` (capture, consolidation and recall) and never as one verdict for the whole key; `(no process)` marks a present consolidation with no default-path process. The default-path rule: the open engine as a fresh install runs it, with shipped configuration and no provider key in the launching environment; a hosted route is named in the entry and is never source evidence. The population is eight tools at named pins: ai-memory `8c39e4e67`, openviking `178a8cdfb`, mempalace `602d796c6` and agentmemory `c5b8ebfb3`, mapped from their own committed sections and not re-read here, and mem0 `001c2352`, memos `85532420`, cognee `b948f88d4` and memori `538b61f`, read at their pins on 2026-11-06 as targeted probes, not re-reads (memori is a stub and stays one). everos and memmachine are stubs whose source was not searched for these keys, so they are unset, not ✗. A tool with several mechanisms for one key is counted once in that row, and its report names each mechanism.

Presence tests, frozen 2026-11-06 before the four reads at the pins (each names its sources and where they disagree):

- `llm_free_path` — judged per component, never as one verdict: for each of capture, consolidation and recall (ADR-0023), present when the component's default path (shipped configuration, no provider key in the launching environment) makes no call to a generative model, and ✗ when it makes one or fails without one; each entry also names what turns the model path on (an explicit flag, ambient API-key presence, or always), and a component with no default-path process counts present, marked "(no process)". An embedding model is not a generative model, and model-free is stated apart from egress-free and spend-free. Sources disagree on the parts: MemPalace's section adds setup and agentmemory's adds maintenance; here setup sits outside the three components and maintenance is consolidation.
- `concurrent_write_safety` — present when the tool's own source adds a mechanism whose evident purpose is to order or exclude concurrent writes to its store (a lock within one process or across processes, a single-writer owner or write queue, an optimistic precondition or version check, a transaction mode chosen for concurrent writers), the entry naming each mechanism, its scope (one process, processes on one host, several hosts) and the write paths it covers; ✗ when the write paths searched show none. A storage engine's own guarantee that the tool only relies on, and a routine commit, are recorded as the engine's and not counted. Source: ADMIT-01's "mechanism-and-scope". Sources disagree on shape: the planning research and agentmemory's report each propose a different four-value shape set, and no shape is assigned here.
- `compaction_capture` — present when the tool ships and registers, in a hook manifest, plugin or installer at the pin, a handler on its harness's pre-compaction event (Claude Code's `PreCompact` or another harness's equivalent) that writes to the tool's store, directly or through the store's own write endpoint, at once or by starting a job; ✗ when no registered handler exists or the registered handler writes nothing to the store. A handler that only re-injects context, a compaction inside the store (of a graph, an index or vectors) and an unregistered handler are not instances; the entry names any it finds. Source: ADMIT-01's strict definition, "writes to the store from the harness's pre-compaction event". Sources disagree on facets: ai-memory's section adds re-injection after compaction and the MemPalace and agentmemory sections propose capture shapes; neither is counted here.
- The OKF open-format axis — present when the tool's source at the pin names the Open Knowledge Format (OKF) as a format it writes, reads or declares (a frontmatter writer, a version constant, an export or an import parser); ✗ when a case-insensitive search for `\bokf\b|open knowledge format`, binaries skipped, prints nothing beside a positive control. Conformance to the OKF specification is recorded in the entry and not counted, and a house format that is not OKF is named by file and not counted. Sources disagree on conformance: ai-memory's section separates a conformant export from a conformant on-disk tree, and OpenViking's calls its instance OKF-shaped rather than conforming; the count is of declarations.
- `agent_coordination` — present when the tool exposes to agents (as an MCP tool, a CLI command or an API) a mechanism by which one agent addresses or hands work to another through the tool: directed messages or a mailbox, a task, action or lease queue, signals, or a shared event log whose entries agents address or claim; ✗ when a search in the subject's own vocabulary for such a mechanism prints none beside a positive control. Per-agent isolation (agent-scoped records, ownership columns, agent ids used as filters) and sharing between humans are not coordination. Sources: the ai-memory, MemPalace and agentmemory instances and OpenViking's searched absence; they differ in delivery semantics, which no entry classifies.

| Key | Present | ✗ | Omitted | Unset |
|---|---|---|---|---|
| `llm_free_path` · capture | 3 — ai-memory, mempalace, agentmemory | 4 — openviking, mem0, memos, cognee | 1 — memori | 2 — everos, memmachine |
| `llm_free_path` · consolidation | 6 — ai-memory, mempalace, agentmemory, mem0 (no process), memos (no process), memori (no process) | 1 — cognee | 1 — openviking | 2 — everos, memmachine |
| `llm_free_path` · recall | 5 — ai-memory, mempalace, agentmemory, mem0, memori | 2 — memos, cognee | 1 — openviking | 2 — everos, memmachine |
| `concurrent_write_safety` | 8 — ai-memory, openviking, mempalace, agentmemory, mem0, memos, cognee, memori | 0 — none | 0 — none | 2 — everos, memmachine |
| `compaction_capture` | 4 — ai-memory, openviking, mempalace, mem0 | 3 — agentmemory, memos, memori | 1 — cognee | 2 — everos, memmachine |
| OKF open-format axis | 2 — ai-memory, openviking | 6 — mempalace, agentmemory, mem0, memos, cognee, memori | 0 — none | 2 — everos, memmachine |
| `agent_coordination` | 3 — ai-memory, mempalace, agentmemory | 1 — memos | 4 — openviking, mem0, cognee, memori | 2 — everos, memmachine |

Omission recorded 2026-11-10: memos' `llm_free_path` cell, set 2026-11-08 as `[consolidation]`, was omitted on 2026-11-10 (the 2026-11-09 decision, landed in the fold-in), under the key's undecided-component rule: a cell is omitted when any component is undecided, and memos' capture and recall verdicts differ by adapter, model-free on OpenClaw and model-backed on hermes and DSH through the host bridge, a chain nobody ran, so the per-adapter verdict is INFERENCE. The census row for memos stays as read on 2026-11-06: this table is a dated table of verdicts and was not recounted. [The memos report](memos.md) carries the correction; the matrix renders its cell as `·`, and five reports carry an `llm_free_path` cell as of 2026-11-10.

Verdicts for the four reports read in Phases 16 and 17, mapped from their own sections against the tests above (not re-read here):

- [ai-memory](ai-memory.md) — capture present · consolidation present · recall present · concurrent_write_safety present · compaction_capture present · OKF present · agent_coordination present. Its section says "nothing generative runs" on the default path for capture, rule-based session pages, retrieval, the forget sweep and the profile pass's model-free branch, so consolidation counts present with its processes (the sweep and the pass) and not `(no process)`; the embedder it fetches is not generative, so egress is stated apart; write safety rests on its "three mechanisms"; the pre-compaction handlers "refresh `sessions/<id>.md` without ending the session", a write to the store; pages carry "OKF v0.2 frontmatter"; and coordination is "a directed, claim-once mailbox addressed to a project".
- [openviking](openviking.md) — capture ✗ · consolidation omitted · recall omitted · concurrent_write_safety present · compaction_capture present · OKF present · agent_coordination omitted. Capture: the section says "every autonomous memory write does" need a generative model, "with no availability guard before the completion call"; model extraction at write time belongs to capture, so that write is the capture verdict, and the store, the archive and the queue it calls model-free are not the write. Premise: for consolidation and recall the section says "directory L0 and L1 generation degrades to empty text" and "the query planner fails open", and lists a "digest-before-inject" step in which "a model rewrites recalled memories before injection (the host CLI by default in Claude Code and Codex, the server planner optionally)", but it does not say whether a model call is made in sidecar generation or in recall when no model is configured, because the degraded run stopped at start; test: read the sidecar generation and the planner default at the pin, or run the degraded mode past start. Write safety is a "path-lock subsystem"; compaction is "the strongest instance seen", with "9 of the 12 installer products commit at a pre-compaction boundary"; OKF is a declaration, so it is counted, and conformance is recorded and not counted ("OKF-shaped rather than conforming"); coordination is omitted, not ✗ (corrected 2026-11-06 after review): the section reads "no instance found", but its search "returns lock hand-off code only", names no positive control and carries the caveat that "`bot/` channels and the Hermes and OpenClaw plugins were not searched", so the frozen ✗ clause (nothing printed beside a positive control) is not met. Premise: the unsearched in-pin channels and plugins may expose a mechanism by which one agent addresses another. Test: the section's search over `bot/` and the two plugins at the pin, beside a positive control.
- [mempalace](mempalace.md) — capture present · consolidation present · recall present · concurrent_write_safety present · compaction_capture present · OKF ✗ · agent_coordination present. Its section calls MemPalace "the model-free pole on capture and recall" and says maintenance (`sync`, `dedup`, `repair`, `compress`, `rooms apply`) carries no chat-model request, which the frozen test counts as consolidation; the setup command that calls a model ("`init` is LLM-on by default") sits outside the three components. Write safety is a cross-process guard ("through the seam lock"); the PreCompact handler the Claude Code and Codex plugins register "starts a detached transcript mine", a job that writes to the store; OKF reads "no instance", with a whole-tree search that "prints no line" beside a positive control; coordination is "An append-only SQLite event log" with task, event and artifact exchange between agents.
- [agentmemory](agentmemory.md) — capture present · consolidation present · recall present · concurrent_write_safety present · compaction_capture ✗ · OKF ✗ · agent_coordination present. Its section says agentmemory is "model-free on the default path in all three parts": capture, recall and maintenance (auto-forget, the decay sweeps, heuristic graph extraction) make no chat-model request in the keyless default, and the model family that ambient key presence mounts is outside the default-path rule. Write safety is in-process guards inside one worker ("a map of promises with an async-local frame") plus a spool lock file; the PreCompact hook "captures nothing" (it posts to a bridge route and to `/context` and prints recalled context), so the registered handler writes nothing to the store; OKF reads "no instance"; coordination is the "`V050_TOOLS` array holds 10 orchestration tools by name", including `memory_lease` and `memory_signal_send`, with the caveat that "Semantics, delivery and concurrency" were not read.

The census sections of the four probed reports: [mem0](mem0.md), [memos](memos.md), [cognee](cognee.md), [memori](memori.md).

## Open questions

- **What the extension buys over the native loop (arc verdict 2026-08-18):** confirmed
  as cross-harness continuity — the one thing a single harness cannot absorb — and the
  mechanism is real in source (ai-memory: one server, per-harness injection envelopes).
  Two qualifications keep it open: the *automatic* continuity floor is thin
  (ai-memory's baton is first + last prompt + tool names; the rich memory is
  pull-only), and absorption runs both ways — memos installs into hermes alongside
  hermes' own loop (conclusion 8's counter-current). ~~The falsifiable residue is a rig
  question: capture a session, switch harness, measure what the second agent actually
  knows.~~ **Ran 2026-08-19 as exp-04 (conclusion 14)**: floor 0/10, pull ceiling
  10/10, harness boundary free on the pull path — the bet holds as a pull mechanism
  only; the "thin automatic floor" qualification is now a measurement.
- ~~The memory-authorship fourth position~~ — resolved into design-principles
  (2026-08-18): independent storage *stacks* authorships rather than picking one; the
  sharpened question is who approves writes, not who makes them.
- ~~Issue #13's `learning_loop` promotion trigger~~ — **fired 2026-09-04**
  ([ADR-0056](../../adrs/0056-learning-loop-mechanism-enum.md)), once issue #34's
  key-scope decision dissolved the value-scope deferral. The key is now a mechanism
  enum — background \| in-loop \| proposed — and every set cell in this category reads
  `background` (ai-memory, mem0, memos; cognee stays ✗): the type's entire verified
  supply side auto-applies out-of-loop. (Re-derived 2026-11-10 over the seven reports with
  a `learning_loop` cell, measure: `harness_features.learning_loop` in each report's frontmatter:
  `background` 6 — agentmemory, ai-memory, mem0, memos, mempalace, openviking — and cognee `false`,
  no loop; the three stubs, everos, memmachine and memori, carry no cell and are unset.) The `proposed` value's two instances are both
  harnesses (warp, gemini-cli) — propose-and-commit is, so far, a harness posture,
  not a memory-vendor one.
- A memory-interchange convention would be the next MCP-shaped event — watched from the
  [standards scoreboard](../../docs/standards.md)'s side (zero shared formats as
  of 2026-08-18). Qualified 2026-11-10: one conformant OKF export (ai-memory v0.2,
  `export-okf`; its on-disk tree is not conformant by the spec's letter) and one house
  declaration (openviking's `OKF_VERSION = "0.1"`, which cites no spec: a declaration, not
  conformance). The spec itself is skewed between a frozen copy, the one ai-memory cites, and
  its live repository; a read of 2026-11-05 found the two byte-identical, so the skew is of
  location today and not of content. The watch note beside the scoreboard carries the
  standing count.
- **Non-admissions of 2026-11-08 ([ADR-0059](../../adrs/0059-memory-vocabulary-admission.md)):**
  candidates the census read and the ADR argued and did not admit, each with the trigger
  that would reopen it.
  - **The OKF open-format axis** — one conformant instance (ai-memory); openviking's is a
    declaration of a house version, not conformance. Trigger: a second conformant OKF
    adopter on the roster.
  - **Harness-native agent messaging** — prose in category-2 reports, traced to no cell.
    Trigger: a second harness read whose messaging is traced in source.
  - **`several-hosts` on `concurrent_write_safety`** — no observed cell; the only lead
    is a non-default, unrun lock provider. Trigger: a cell or verified option whose
    default guard spans hosts.
  - **Tenant, peer, group, wing and room labels and `_profile` as `memory_scope`
    values** — labels within one tool. Trigger: a second tool with the same axis.
  - **`single-principal` as a `team_sharing` value**, **an injection-posture enum**,
    **a bare numeric threshold on `write_admission`**, **splitting expiry from decay**,
    **an MCP-entry merge as its own `harness_installer` value** and **sub-typing
    `learning_loop`'s `background`** — each with its trigger in the ADR.
  - **A delivery-shape regrade of `agent_coordination`.** Trigger: delivery semantics
    traced in source for two tools.
- **Next re-read triggers, parked 2026-11-10:** the four 2026-11 reads' next triggers and
  their two-sided falsifiers (ai-memory, OpenViking, MemPalace, agentmemory) are in
  [issue #57](https://github.com/leandromineti/ai-assisted-coding/issues/57), and the
  non-admission triggers above are checked at each re-read.
