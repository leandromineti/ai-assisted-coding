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
read_at: 2026-08-18   # survey read, same day as the stub; vendor paper read separately at full depth (refs/2025-mem0.md)
depth: survey   # read: mem0/memory/main.py (V3 add pipeline end-to-end, search/update entry points), configs/prompts.py (additive extraction prompt), integrations/mem0-plugin (README, hooks.json, script headers for on_stop / block_memory_write / import_competing_tools). NOT read: mem0-ts, server/, reranker internals, the openclaw and pi-agent integrations, cli/ bodies
harness_targets: "in-repo at the pin: integrations/mem0-plugin targets Claude Code, Claude Cowork, Cursor, Codex, OpenCode, Antigravity (hooks.json + codex-hooks.json + cursor-hooks.json + a Kimi shim; MCP config bundled); also integrations/openclaw and pi-agent-plugin (unread), plus non-harness carriers (vercel-ai-sdk, zapier, n8n) and six in-repo SKILL.md skills"
features:
  skills: true   # six skills in-repo (skills/mem0, mem0-cli, mem0-integrate, …); SKILL.md payloads verified by listing, behavior not read
  learning_loop: true   # background, via the in-repo harness plugin: Stop/PreCompact hooks capture session summaries with infer=True → the V3 LLM extraction write path runs without human approval; SessionStart/UserPromptSubmit inject recall. Verified at hooks.json + script-header + main.py level (script bodies not fully read). Fourth harness-independent instance
memory_features:   # ADR-0013 block, set 2026-08-19 from the existing survey read at 001c2352 — not a re-read; script bodies unread caveat carries over
  memory_store: vector           # vector store + lemmatized BM25 hybrid over it, per user/agent/session
  capture_path: hook             # Stop/PreCompact hooks → infer=True → V3 ADD-only LLM extraction
  recall_injection: auto         # SessionStart + UserPromptSubmit injection scripts (verified at header level)
  memory_scope: [user, agent, session]
  memory_tiers: true             # procedural_memory type alongside episodic default
  hybrid_retrieval: true         # vector + BM25 + optional reranker, filter DSL
  decay: true                    # per-memory expiration_date, show_expired, reference_date time-travel
  # injection_trust_boundary deliberately unset: an explicit open question in this report, not a checked ✗
  deployment_mode: both          # OSS BYO-store vs managed platform — and the plugin DEFAULTS to platform
  harness_installer: true        # hooks.json bundle across 6 harnesses + MCP config
---

# mem0

## What it is

"The memory layer for personalized AI": a Python/TS SDK, a self-hostable server, and
a managed platform that LLM-extract memories from conversation history, store them
per user/agent/session in a vector store (+BM25 hybrid), and retrieve them into later
context. General-purpose by design — the personalization domain, not coding — but the
repo at the pin carries a serious coding-harness beachhead: `integrations/mem0-plugin`
installs hook capture + MCP tools + skills into Claude Code, Claude Cowork, Cursor,
Codex, OpenCode, and Antigravity.

## The distinguishing bet

**Memory is an inference problem with a benchmark** — an LLM-scored extraction
pipeline behind an API, sold on recall metrics and token efficiency; the opposite
wager from ai-memory's zero-LLM grep-able wiki, and a managed-service bet (YC company)
against local file artifacts. The vendor paper's honest version of the claim is an
*efficiency frontier*, not accuracy — see [2025-mem0](../../refs/2025-mem0.md): its
own full-context baseline beats the memory system on quality.

## The shipped pipeline is not the paper's pipeline

The paper (2025-04) describes extraction + an LLM update phase choosing
ADD/UPDATE/DELETE/NOOP per fact against similar memories. The code at the pin has
replaced that: `_add_to_vector_store` (`mem0/memory/main.py:879`) is the "V3 phased
batch pipeline" — **ADD-only**. One LLM call over (conversation summary, last-k
messages, top-10 existing memories with integer anti-hallucination IDs) extracts
self-contained facts; then MD5-hash dedup, batch embedding, batch persist, and batch
entity linking. No LLM-mediated UPDATE/DELETE in the write path; relatedness is
recorded as `linked_memory_ids`, contradiction handling shifts to retrieval
(expiration dates, filters, optional reranker) and to an explicit `update()` API the
*caller* must invoke. The prompt (`configs/prompts.py:464`, "Ported from
platform/backend") enforces temporal grounding — every relative time reference must
be resolved against an Observation Date, "'User went to Paris last week' is useless
6 months later." This is the 2026 rewrite the README's 92.5/94.4 numbers refer to;
neither the paper's architecture nor its scores describe what ships.

## The harness carriers (where the kind's questions get answered)

`integrations/mem0-plugin`, verified at hooks.json + script level:

- **Capture**: five Claude Code events (SessionStart, UserPromptSubmit, PreToolUse,
  PostToolUse, Stop) with per-harness variants (codex-hooks.json, cursor `.sh`
  twins, a Kimi shim). The Stop hook parses the transcript and stores a structured
  session summary **with `infer=True`** — the V3 LLM extraction runs on it with no
  human in the loop. Subagent sessions are skipped; dedup via marker file.
- **Injection**: SessionStart and UserPromptSubmit scripts fetch and inject recall
  (script headers read; bodies not).
- **The kind's most aggressive move, source-verified**: `block_memory_write.sh` is a
  PreToolUse gate on `Write|Edit` that **exits 2 to block the harness's own native
  memory writes** (MEMORY.md, auto-memory files) and tells the model to use mem0's
  `add_memory` MCP tool instead. Conclusion 8's counter-current escalated: not just
  colonizing a harness that has native memory — actively suppressing the native
  feature to displace it.
- **Competitive import**: `import_competing_tools.py` migrates `.cursorrules`,
  Copilot instructions, cline's memory-bank, and Continue rules into mem0 as
  project-profile memories. Switching-cost engineering, in a plugin.
- **Agent self-provisioning**: `mem0 init --agent --json` mints an evaluation API
  key in seconds with no email or browser, "if you're an AI agent setting up Mem0
  autonomously" — the owner can claim it later, memories transfer. The first
  agent-first onboarding path seen in the study.

Membership verdict, sharpened from the stub: same as cognee — the SDK earns bucket
membership via carriers — but unlike cognee, the carrier with the learning loop lives
*in the same repo* and its capture path feeds the same V3 pipeline the SDK exposes.

## Main features

- Two-mode deployment: OSS SDK (BYO vector store + LLM; `infer=False` degrades to raw
  message storage) or platform API; the plugin defaults to platform.
- Hybrid retrieval: vector + lemmatized BM25, a full filter DSL (eq/ne/in/gt/…,
  AND/OR/NOT, wildcards), optional reranker, per-memory `expiration_date`,
  `show_expired` and `reference_date` for time-travel queries.
- Session summaries and compact-summaries captured at PreCompact/Stop; procedural
  memory writes for agent workflows (`memory_type="procedural_memory"`).
- Six in-repo SKILL.md skills, MCP server config, and a CLI with agent-first init.

## Stack & repo shape

TS + Python monorepo (433 `.ts`, 370 `.py`, 245 `.mdx` — docs-heavy), npm + PyPI
packages, self-hostable `server/`, `evaluation/` (empty at the pin — the benchmark
harness lives elsewhere), 2,595 commits since 2023-06. Company-backed with a real
contributor base; `marketplace.json` at root (Claude Code plugin marketplace entry).

## Surprises

1. **The plugin blocks the harness's native memory.** A PreToolUse exit-2 gate on
   MEMORY.md writes, redirecting the model to mem0's own tool — the absorption war
   fought from the extension side, mechanically. No other seed in the kind does this.
2. **The paper's signature mechanism is gone from the code.** The ADD/UPDATE/DELETE/
   NOOP tool-call the paper is cited for (553 citations) no longer exists in the
   shipped write path; V3 is ADD-only with linking. Anyone reasoning about mem0 from
   the paper is reasoning about a retired architecture.
3. **Agent-first onboarding.** `mem0 init --agent` provisions credentials for an
   unattended agent in seconds, ownership claimable later — infrastructure explicitly
   designed for agents that install their own memory.
4. **Competitor-store import ships in the plugin** — cursorrules/copilot/cline/
   continue migration as a first-class script.
5. **The OSS pipeline is a downstream port of the platform** ("Ported from
   platform/backend/shared/core/config/prompts.py") — the open code trails the paid
   service, inverting the usual OSS-first story the README implies.

## Open questions

- The plugin's recall injection (`on_session_start.sh`, `on_user_prompt.sh` bodies):
  how much context per turn, and with what trust framing? memos wraps recall in
  untrusted-data delimiters; does mem0? (Prompt-injection surface of a
  platform-backed store is larger than a local one's.)
- `integrations/openclaw/dream-gate.ts` — what gates what? (The openclaw integration
  went unread.)
- The README's LoCoMo 92.5 / LongMemEval 94.4 for this V3 rewrite: measured how, by
  whom, on which item sets? The paper's scores don't transfer to an architecture it
  doesn't describe ([2025-mem0](../../refs/2025-mem0.md) closes the paper side; the
  rewrite's numbers remain vendor-asserted and unreconciled).
- Does `block_memory_write.sh` fire in practice on Claude Code's memory-tool writes
  (which may not go through Write/Edit), or only on file-path writes? A rig probe
  would settle whether the displacement is real or symbolic.

## My take

The kind's commercial pole, and the sharpest evidence that memory extensions see
harness-native memory as a rival to *displace*, not a feature to complement. The
gap between the cited paper and the shipped V3 pipeline is also the cleanest instance
yet of why this repo pins commits and reads source: the architecture with 553
citations is not the architecture in the repo.
