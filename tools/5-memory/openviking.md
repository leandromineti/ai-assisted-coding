---
name: openviking
category: 5
type: memory
maker: Volcengine (ByteDance)
url: https://github.com/volcengine/OpenViking
license: AGPL-3.0
access: open-source
stack: [Python, TypeScript, Rust]
version: v0.4.16-7-g2af48624
commit: 2af48624
first_commit: 2026-01-29
stars: 31583
stars_at: 2026-08-21
read_at: 2026-08-21
depth: stub   # facts from repo-facts.sh + README skim; source not read, no memory_features cells set
---

# openviking

## What it is

"The Context Database for AI Agents" — ByteDance/Volcengine's open-source entry into
the memory kind, and framed wider than memory: **memories, resources, and skills as one
virtual filesystem** under a `viking://` URI scheme, which the agent browses with
`ls`/`tree`/`find` "instead of querying a black-box vector store". Content is processed
on write into three loading tiers (L0 abstract / L1 overview / L2 details) and loaded
only as deep as the task needs; retrieval is directory-recursive (vector search locates
the best directory, then drills down) and each query keeps an observable
directory-browsing trajectory. "Sessions become memory": after a session commits, it
asynchronously extracts user preferences and agent experience into long-term memory.
Hosted Studio playground + cloud site exist alongside self-host. (README at the pin;
source unread.)

## Notes for the type comparison

- **The filesystem-as-interface bet is new to the set.** The seeds split between
  harness-facing installers (ai-memory), API stores (mem0), and OS-framed systems
  (memos); OpenViking's wager is that *deterministic navigation* (URIs, `ls`, watchable
  retrieval trajectories) beats opaque similarity search — the "observable retrieval"
  pitch lands on the same trust axis our `memory_revision` / `injection_trust_boundary`
  keys probe, but from the read side.
- **Skills live inside the store** (`user/{id}/skills/`), so it spans the bucket's
  artifact kinds rather than holding memories only — same broad-shape question ECC
  raised for config packs.
- **In-tree harness plugin examples** — `examples/codex-memory-plugin/`,
  `pi-coding-agent-extension/`, `zcode-memory-plugin/`, each with a DESIGN.md — the
  demand-side wiring the `harness_installer` key asks about, unverified at stub depth.
- **The only AGPL-3.0 tool in the memory set** (everything else is MIT/Apache-2.0) —
  a real adoption constraint for embedding, and the license shape that usually signals
  a vendor cloud product guarding against rehosting.
- **Big-vendor provenance, huge velocity**: 31.6k stars and 2,066 commits in under
  seven months (first commit 2026-01-29) — the fastest star accumulation in the set,
  with the vendor-backing shape memos (MemTensor) has, at ByteDance scale.

No `memory_features:` cells set — stub honesty; the README makes claims that map onto
at least `memory_store`, `capture_path`, `recall_injection`, and `deployment_mode`, but
cells here are set only when verified in source or docs actually read, and this was a
README skim.

## Stack & repo shape

Python-dominant (1,732 `.py`) with a TypeScript surface (274 `.ts` + 289 `.mjs`) and
Rust crates (156 `.rs` — `ov_cli`, a `ragfs-cache-mooncake` crate, plus a vendored
`third_party/leveldb-1.23`); 3,942 tracked files, 2,066 commits since 2026-01-29.
Docs localized to zh-CN and ja-JP READMEs.

## My take

*(empty — not yet used; stub honesty)*
