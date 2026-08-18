---
name: memos
layer: 5
kind: memory
vendor: MemTensor
url: https://github.com/MemTensor/MemOS
license: Apache-2.0
open_source: true
stack: [TypeScript, Python]
version: v2.0.30-20-g85532420
commit: 85532420
first_commit: 2025-07-06
stars: 10762
stars_at: 2026-08-18
read_at: 2026-08-18   # survey read; the stub (same pin) was stamped 2026-08-19 by a clock-skewed session
depth: survey   # read in full: top README, memos-local-plugin/ARCHITECTURE.md (module map + data flow), adapters/README.md, deepseek-harness adapter README; spot-checked in source: the orchestrator's subscriber chain wiring (core/pipeline/orchestrator.ts). NOT traced: the per-module math (reward backprop, induction, crystallization), the Python core beyond its directory shape, the OpenClaw/OpenWork apps
harness_targets: "verified in-repo at the pin: OpenClaw (two plugins — MemOS-Cloud-OpenClaw-Plugin and memos-local-openclaw — plus an openclaw adapter in memos-local-plugin), DeepSeek Harness (in-process Cordis adapter), hermes-agent (out-of-process Python adapter over JSON-RPC), OpenWork (openwork-memos-integration)"
features:
  learning_loop: true   # background, harness-independent — event-driven subscriber cascade (capture → reward → L2 policy induction → L3 world models → skill crystallization) in a per-session serial background queue; wiring spot-checked at core/pipeline/orchestrator.ts:138 + the flush chain at :1611, per-stage math read at ARCHITECTURE.md level only. Third harness-independent instance (after ECC, ai-memory)
---

# memos (MemOS)

## What it is

MemTensor's "memory operating system" — but for this repo's purposes it is **two
products in one repo**. `src/memos` is the Python research core (the paper lineage:
MemCube, mem_scheduler, mem_reader, a `dream/` module), an API/platform product. The
coding-harness story lives entirely in `apps/memos-local-plugin`: a standalone
TypeScript core implementing an algorithm spec called **Reflect2Evolve V7**, wrapped by
per-harness adapters (OpenClaw and DeepSeek Harness in-process, hermes-agent
out-of-process over JSON-RPC) behind one `MemoryCore` facade. The stub's "repo is mostly
harness plugins" undersold it: the plugin is not a shim over the Python core, it is a
second full implementation with its own spec, storage, and viewer.

## The distinguishing bet

**Memory as a scored, evolving policy database, not prose.** Where ai-memory
accumulates a human-readable markdown wiki and ECC writes instinct files, memos'
learning products are typed rows in SQLite + vectors: L1 traces with propagated values,
L2 policies with measured `gain`, L3 world models, and crystallized skills with
`invocationGuide` and `procedureJson`, each governed by explicit lifecycle states
(candidate → active → retired; probationary skills under a Beta(1,1) posterior). The
math is the spec — "γ, α, V, η, support, gain" are required to carry the same names in
code, docs, and prompts. No other seed in the kind formalizes memory as reinforcement:
this is an RL-flavored value-propagation pipeline wearing a memory product's clothes.

## The learning loop (the issue-#13 read)

Documented in `memos-local-plugin/ARCHITECTURE.md` §3 and wired, verifiably, in
`core/pipeline/orchestrator.ts` ("Algorithm subscribers (capture → reward → L2 → L3 →
skill + feedback)", line 138; the `flush()` chain drains them in that order, line
1611). Per turn-end, in a per-session serial **background** queue:

1. **Capture** — episode finalized → L1 trace rows: step extraction, reflection
   extraction (adapter/regex/optional LLM), α scoring, embeddings.
2. **Reward** — per-episode `R_human ∈ [−1,1]` from a rubric LLM (goal / process /
   satisfaction, heuristic fallback), then reflection-weighted backprop
   `V_t = α_t·R + (1−α_t)·γ·V_{t+1}` with exponential time decay.
3. **L2 policy induction** — high-V traces associate with existing policies; unmatched
   ones pool by signature (`tag|tag|tool|errCode`); ≥N distinct episodes in a bucket
   triggers an LLM induction call; `gain = weightedMean(with) − mean(without)` drives
   candidate → active → retired.
4. **L3 world-model abstraction** — active L2s cluster by domain + centroid cosine; an
   LLM abstraction call per cluster; merge-or-insert with cooldowns.
5. **Skill crystallization** — eligible policies get an LLM-drafted callable skill,
   checked by a *heuristic* verifier (no LLM), with η seeded from policy gain and a
   probationary lifecycle driven by feedback.

Mechanism classification: **background** — not interval-scheduled (hermes), not a
startup pipeline (codex), not a server-side cron (ai-memory), but an event-driven
subscriber cascade that runs after each turn ends. Default-on once the plugin is
installed; auxiliary LLM calls delegate to the host harness's own provider (in DSH's
case explicitly without copying credentials). The `learning_loop` boolean now flattens
four *different* background shapes — noted on issue #13.

## Retrieval & injection posture

The V7 spec's stated golden rule is **injection timing, not quantity**: five retrieval
entry points (turn-start, tool-driven, skill-invoke, sub-agent start, decision-repair),
three tiers (skills / traces+episodes / world models) fused by RRF + MMR. Tool hooks
observe but never inject mid-decision. The DSH adapter is the strictest: one bounded
automatic recall per accepted direct-user turn under a hard `min(recallTimeoutMs, 3000)`
ms foreground deadline, malformed LLM output falling back to a mechanical cutoff, the
recall block appended after the query wrapped in `<memos_context>` and system-prompted
as untrusted historical data — the same trust-delimiter discipline ai-memory applies to
its injected handoffs. Foreground never joins background work; a turn's recall sees only
previously committed state.

## Main features

- Three-adapters-one-core: `MemoryCore` facade + agent-contract DTOs; in-process TS for
  OpenClaw/DSH, JSON-RPC stdio bridge for Python hosts (hermes).
- Six embedding providers (incl. local MiniLM) and six LLM providers (incl. `host` —
  delegate to the harness's own model route) behind facades.
- HTTP/SSE viewer dashboard sharing the core (loopback-only for DSH, port 18801).
- Supply-chain posture in the installer: pnpm build-script allowlist, fails closed on
  unreviewed scripts, documented reviewed set (`better-sqlite3`, `esbuild`,
  `onnxruntime-node`, `sharp`).
- The Python core's separate surface (API, MemCube, scheduler, `dream/`) — unread here.

## Stack & repo shape

TS-heavy (742 `.ts`) + Python core (624 `.py`), 238 markdown docs; 2,044 commits since
2025-07. `apps/` holds the four integrations; `packages/` a second, newer-looking core
split (`memos-core`, `memos-schema`, `adapter-base`) whose relation to
`memos-local-plugin/core` was not established at this depth. Bilingual docs throughout;
research-affiliated vendor with a paper lineage.

## Surprises

1. **The loop is a formal RL pipeline.** Expected "background capture + auto-recall"
   (the stub's phrasing); found value backprop, gain-measured policy lifecycles, and a
   candidate-pool induction trigger. By formal ambition this is the most elaborate
   learning loop in the study — hermes/codex/ai-memory write prose notes by comparison.
2. **Memory that mints skills.** Stage 5 emits callable skills — the memory kind
   manufacturing artifacts of the *skills* kind. The kinds are not silos; the loop's
   output crosses them.
3. **A harness with its own learning loop hosts a rival's.** The hermes adapter installs
   memos as a hermes `MemoryProvider` — hermes' native loop and memos' loop can run in
   the same agent. Conclusion 8's absorption story meets its counter-current: extensions
   don't just get absorbed, they colonize harnesses that already absorbed the feature.
4. **DSH-first posturing.** The HEAD commit at the pin is "announce DeepSeek Harness
   support"; the DSH adapter README pins exact rc versions, documents host-side
   optimistic-rendering caveats, and ships a one-command installer — five days after
   dsh's public launch (dsh created 2026-08-13; registered here as issue #19). Memory
   vendors are racing to new harnesses at launch speed.
5. **Two cores, one brand.** The TS plugin does not call the Python OS at all — the
   flagship "MemOS" research product and the thing coding agents actually install share
   a name and a repo but not an implementation.

## Open questions

- Does Reflect2Evolve's formal machinery outperform prose wikis in practice, or is it
  formalism-as-marketing? The repo ships an `evaluation/` tree — check what it measures
  before citing any vendor numbers (benchmark-survey discipline; same gate as mem0's
  LoCoMo claims).
- What is `packages/memos-core` (vs `memos-local-plugin/core`) — an in-flight
  extraction? If the core is being re-platformed, a deep-dive should wait for it to
  settle.
- The Python core's `dream/` module — offline consolidation during idle time? If so it
  is a sixth loop shape (sleep-time compute) not yet in any vocabulary here.
- hermes + memos in one agent: do the two loops interfere (double capture, conflicting
  injections)? A cheap rig probe if the cross-loop question ever matters.

## My take

The kind's technical ceiling so far. Whether the ceiling is load-bearing is exactly what
its own `evaluation/` tree should be forced to answer.
