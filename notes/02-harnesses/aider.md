---
name: aider
layer: 2
sublayer: terminal
vendor: Aider-AI
url: https://github.com/Aider-AI/aider
license: Apache-2.0
open_source: true
stack: [Python]
version: v0.86.3.dev-53-g5dc9490b
commit: 5dc9490b
read_at: 2026-07-28
depth: stub
---

# Aider

Git-native terminal harness: it commits after each change and builds a "repo map" to decide
what the model sees. The oldest project in the set — first commit 2023-04-03, predating the
current harness generation by well over a year.

Classified layer 2 despite having real opinions about process — see the stress test in
[`../../taxonomy.md`](../../taxonomy.md). Its methodology isn't installable on another
harness, so it's a harness with strong defaults, not a workflow framework.

## The distinguishing bet

_TODO_ — nominally that **git is the right substrate for agent work**: if every change is a
commit, review and rollback are free and the agent can be trusted with more. Contrast with
peers that treat git as an afterthought.

## Main features

_TODO_ — repo map, auto-commit per change, voice input (111 `.mp3` files suggest audio is
first-class, not a demo).

## Stack & repo shape

Pure Python, and by far the **smallest codebase here — 691 tracked files**, 147 of them
`.py`. Compare cline at 3429 or opencode at 6347. 58 `.scm` files are tree-sitter query
files, which is how the repo map gets built.

13138 commits since 2023-04-03. Note the HEAD commit is **2026-05-22** — roughly two months
stale at read time, while every other repo in the set had commits within the week.

## Architecture

_TODO — source unread._

## Bleed

_TODO_

## Cost model

Open source; you pay for inference against whichever model you point it at.

## Surprises

_Source unread — but two things are already odd: it does more with 147 Python files than
peers do with 2000 TypeScript ones, and it may be slowing down while the field accelerates._

## Open questions

- Is the low commit velocity a sign of maturity or of decline? Check the contributor graph
  before drawing a conclusion.
- The repo map is the oldest serious answer to context assembly in this set. Does it still
  hold up against embedding- or agent-driven file selection?
- What accounts for the size difference — genuine simplicity, or scope the others took on?
