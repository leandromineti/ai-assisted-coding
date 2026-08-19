---
name: memori
category: 5
type: memory
vendor: MemoriLabs
url: https://github.com/MemoriLabs/Memori
license: Apache-2.0
open_source: true
stack: [Rust, Python, TypeScript]
version: v3.3.6-24-g538b61f
commit: 538b61f
first_commit: 2025-07-24
stars: 16128
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README skim; source not read
---

# memori

## What it is

Agent memory engine with the tagline "memory from what agents do, not just what
they say" — i.e. capturing actions/tool use, not only conversation. Rust core
(`core/Cargo.toml`) with Python and Node bindings; "LLM, datastore and framework
agnostic," offered both as bring-your-own-DB (`memori-byodb` docs tree) and as a
cloud product (`memori-cloud`; quickstart wants a `MEMORI_API_KEY`). In-repo
`benchmarks/` tree. 16.1k stars in ~13 months. (README + file listing at the pin;
source unread.)

## Notes for the type comparison

The action-capture framing overlaps ai-memory's lifecycle-hook observation bet, but
delivered as an embeddable engine rather than a harness installer — a middle point
between ai-memory (harness-facing) and mem0 (API-facing). Rust-core-with-bindings is
a distribution shape none of the other seeds use.

## Stack & repo shape

Rust core (52 `.rs`) + Python SDK (309 `.py`) + TS (104), MDX docs; 630 commits
since 2025-07.

## My take

*(empty — not yet used; stub honesty)*
