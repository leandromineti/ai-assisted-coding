# 5 — Memory

`checked: 2026-08-22`

Persistent cross-session state as an installable product — **the agent↔time edge**. Fed
by hooks/MCP during a session, consolidated between sessions, injected back at the next
session start, on any harness. A full category since the 2026-08-22 split
([ADR-0020](../../adrs/0020-memory-category-extensions-renumbered.md)); born 2026-08-18
as the extensions bucket's `memory` type (the bucket is now
[category 6](../06-extensions/index.md)). Reports keep `type: memory` in frontmatter as
residual data; the category's feature vocabulary is the 13-key `memory_features` block
([ADR-0013](../../adrs/0013-memory-features-block.md)) with its
[generated matrix](../../comparisons/features.md). Roster count (2026-08-22): **eight**
reports carry `category: 5` — the eight rows in the generated
[tools matrix](../../comparisons/tools.md). ADR-0020's "all nine reports stay" counted
the pre-split bucket's nine files, which included ecc — moved to category 6 by the same
ADR; the immutable ADR body stays as written, this note is the correction.

What the category's seeds wager, in one line each: markdown wiki (ai-memory), RL policy
database that mints skills (memos), knowledge graph over a tripartite store (cognee),
LLM-extraction platform sold on benchmarks (mem0), plus four stubs (memori, everos,
memmachine, openviking). Four consolidation postures verified: background cron, per-turn
event cascade, agent-invoked, hook-capture-to-platform. **Zero shared formats** — each
vendor pays the harness-fragmentation cost separately, in code (tracked as a dated watch
note beside the [standards scoreboard](../cross-cutting/standards.md)). The SDK-facing
shapes earn membership via their shims, and the shims are where the coding-agent
behavior lives — up to and including mem0's plugin *blocking the harness's native memory
writes* (the displacement finding, conclusion 8).

## The memory matrix — first cut (2026-08-19)

The reading arc's prose comparison became a registry block
([ADR-0013](../../adrs/0013-memory-features-block.md)): 11 keys at the first cut
(13 since, same day: `memory_revision` after the mem0 deep-dive, `write_admission`
after exp-04 arm C), generated
[matrix](../../comparisons/features.md), cells
set only on the four read tools. What the first cut shows:

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

Single-instance bets stay out of the vocabulary by the two-instance rule but are the
differentiators to watch: zero-LLM default (ai-memory), git-versioned store
(ai-memory), native-memory displacement (mem0), competitor import (mem0), skill
crystallization (memos), provenance audit (ai-memory).

## Reports

| Tool | Depth | One-line |
|---|---|---|
| [**ai-memory**](ai-memory.md) | deep-dive (2026-08-18) | Cross-harness memory as one Rust daemon: hook capture (closed 10-type vocabulary) → rule-based session pages in a git-versioned markdown wiki → heuristic handoff injected at next session start, any harness. Zero-LLM default path; with a provider, a **source-verified background learning loop** auto-approves its own wiki edits (`_rules/`, `procedures/`) — second harness-independent instance after ECC. Surprise: the continuity baton is first + last prompt + tool names, no LLM; the rich memory is pull-only via 18 MCP tools. |
| [**mem0**](mem0.md) | **deep-dive (2026-08-19)** | The type's commercial pole (YC-backed platform + OSS SDK). Shipped write path ≠ the 553-citation paper: V3 is ADD-only extraction with linking, the paper's ADD/UPDATE/DELETE/NOOP phase is retired. In-repo plugin installs hook capture into six harnesses with a **background learning loop** (Stop-hook capture, `infer=True`) — fourth verified instance — plus the type's most aggressive move: a PreToolUse gate that **blocks the harness's native MEMORY.md writes** and redirects to mem0's tool. Displacement, not just colonization. Vendor paper graded separately ([2025-mem0](../../refs/2025-mem0.md)): its own full-context baseline beats the memory system on quality. **Deep-dive 2026-08-19** (same pin): two matrix cells flipped (tiers, decay — both platform-only or tag-deep in OSS); trust boundary settled ✗ (openclaw protocol makes memories authoritative: "Rules override your defaults"); the displacement gate run-probed — narrow path glob, fails open without jq, broader on Cursor than Claude Code, prose carries the real intent; V3 removed graph from OSS in the commit that added it; and the SDK ships a 1,582-line remotely-scripted A/B upsell funnel (notices.py) with 5× the add-pipeline's test coverage. |
| [**cognee**](cognee.md) | survey (2026-08-18) | The type's incumbent (2023-08, 30.1k stars) and its knowledge-graph pole — at the price of a tripartite graph+vector+relational consistency surface. Membership verdict: the SDK sits in the category **via its shims**, and the shims are where the coding-agent product lives (agent-scoped datasets, session/permanent split, agent-invoked `improve` consolidation, coding-rule extraction). No autonomous loop in-repo (`learning_loop: false`); the marketplace plugin automates capture but runs in API mode, where rule extraction is explicitly skipped. ai-memory's opposition dossier spot-checked: both structural claims corroborated (LiteLLM/Instructor churn guard; the Ladybug fork's costs written into pyproject). |
| [**memori**](memori.md) | stub (2026-08-18) | "Memory from what agents do, not just what they say" — Rust core with Python/Node bindings, BYODB or cloud, 16.1k stars in ~13 months. Action-capture framing, embeddable-engine shape. |
| [**everos**](everos.md) | stub (2026-08-18) | EverMind's "Ever OS": durable writes + retrieval, Claude Code plugin shipped in-repo. Youngest seed (first commit 2026-06-05; 12.1k stars in ~10 weeks, on only 88 commits — read its numbers with that ratio in mind). |
| [**memos**](memos.md) | **deep-dive (2026-08-19)** | Two products in one repo: the Python research OS (MemCube, paper lineage) and — what harnesses actually install — a standalone TS core ("Reflect2Evolve V7") behind OpenClaw/DSH/hermes adapters. **Learning loop verified: background**, an event-driven cascade (trace capture → reward backprop → policy induction → world models → skill crystallization) — the type's formal ceiling: memory as a scored, evolving policy database that *mints skills*, not prose. Third harness-independent instance; issue #13's trigger still unfired. **Deep-dive 2026-08-19** (same pin): the anti-mem0 — every survey cell CONFIRMED in source (golden-tested backprop, genuinely distinct tier stores, three live demotion paths, the type's strongest trust boundary) — and then the twist: `lightweightMemory: true` ships as default in code, templates, AND the published npm artifact (probed), unmounting the entire evolution cascade; the installer is the study's most aggressive (a `.pth` hook monkey-patching hermes' profile creation, no uninstall); and telemetry credentials are injected at npm publish — the pin doesn't describe the artifact. |
| [**memmachine**](memmachine.md) | stub (2026-08-18) | "The open-source memory layer for AI agents" — plain store-and-retrieve SDK (Python), OpenClaw/Strands integrations. The type's commodity baseline. |
| [**openviking**](openviking.md) | stub (2026-08-21) | ByteDance/Volcengine's "context database": memories + resources + skills as one `viking://` virtual filesystem the agent browses (`ls`/`tree`/`find`), tiered L0/L1/L2 loading, observable retrieval trajectories. 31.6k stars in ~7 months; the set's only AGPL-3.0. Filesystem-as-interface is a bet no other seed makes. |

## The distinction that matters

- **category 5 governs continuity** — what survives the session.
- **category 6 governs reach** — what the agent can access.
- **category 2 is the absorption pressure** — harnesses ship native memory loops
  (conclusion 8), and this category's survival bet is the one thing a single harness
  cannot absorb: cross-harness continuity.

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
- Issue #13's `learning_loop` promotion trigger: **ai-memory verified in source
  (2026-08-18)** as the second harness-independent autonomous loop after ECC — mechanism
  `background` (server-side scheduler, default-on with a provider, auto-approving). The
  promotion trigger itself still hasn't fired: `background` now has four instances,
  `in-loop` and `manual` still one each.
- A memory-interchange convention would be the next MCP-shaped event — watched from the
  [standards scoreboard](../cross-cutting/standards.md)'s side (zero shared formats as
  of 2026-08-18).
