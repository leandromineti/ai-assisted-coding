---
name: memmachine
layer: 5
kind: memory
vendor: MemMachine
url: https://github.com/MemMachine/MemMachine
license: Apache-2.0
open_source: true
stack: [Python]
version: v0.3.9-20-g2d28c1c
commit: 2d28c1c
first_commit: 2025-08-15
stars: 3178
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README skim; source not read
harness_targets: "integrations/openclaw/ and a Strands integration in-repo (file listing at the pin); not verified per-target"
---

# memmachine

## What it is

"The open-source memory layer for AI agents" — persistent memory behind a
five-lines-of-code SDK, Python packages (`packages/client`, `packages/common`) plus
a REST client and integrations (OpenClaw, AWS Strands). Smallest of the memory-kind
seeds (3.2k stars, first commit 2025-08-15). (README + file listing at the pin;
source unread.)

## Notes for the kind comparison

Same positioning sentence as mem0 ("the memory layer for AI agents") with the same
SDK-facing shape — useful as the kind's commodity baseline: if the distinguishing
bets of the bigger tools (graph memory, action capture, wiki-not-vector-DB,
OS-scope) don't measurably beat a plain store-and-retrieve SDK, the kind is
converging on a commodity.

## Stack & repo shape

Python-dominant (478 `.py`), MDX docs, 938 commits since 2025-08.

## My take

*(empty — not yet used; stub honesty)*
