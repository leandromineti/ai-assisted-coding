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
read_at: 2026-08-19
depth: stub   # facts from repo-facts.sh + README skim; source not read
harness_targets: "in-repo apps at the pin: OpenClaw plugins (cloud + local), a DeepSeek Harness (dsh) plugin with auto-recall/background capture, an OpenWork integration, and a local Memory Viewer; not verified per-target"
---

# memos

## What it is

"MemOS 2.0 Stardust" (MemTensor): a memory operating system for agents — "give
your agent persistent memory and the ability to grow" — with hybrid retrieval,
background capture, and a viewer UI, shipped through per-harness plugins (OpenClaw,
DeepSeek Harness, OpenWork integrations all in-repo). Bilingual docs (en/cn);
MemTensor is a research-affiliated vendor and MemOS has an associated paper
lineage. (README + file listing at the pin; source unread.)

## Notes for the kind comparison

The most harness-plugin-forward of the SDK-side seeds — its `apps/` tree is mostly
integrations, which puts it closer to ai-memory's install-into-harnesses posture
than mem0's pure API. Second "memory OS" brand in the set. The DeepSeek Harness
plugin's "automatic recall + background capture" is learning-loop-shaped; not
counted for issue #13 without a source read.

## Stack & repo shape

TS-heavy (742 `.ts`) + Python core (624 `.py`), 238 markdown docs; 2,044 commits
since 2025-07; apps/ monorepo of integrations.

## My take

*(empty — not yet used; stub honesty)*
