---
name: aider
category: 2
surfaces: [terminal]
execution: local
maker: Aider-AI
url: https://github.com/Aider-AI/aider
license: Apache-2.0
open_source: true
stack: [Python]
version: v0.86.3.dev-53-g5dc9490b
commit: 5dc9490b
first_commit: 2023-04-03
stars: 47763
stars_at: 2026-07-28
read_at: 2026-07-28
depth: stub
---

# Aider

Git-native terminal harness: it commits after each change and builds a "repo map" to decide
what the model sees. The oldest project in the set — first commit 2023-04-03, predating the
current harness generation by well over a year.

Classified category 2 despite having real opinions about process — see the stress test in
[`../../docs/tool-taxonomy.md`](../../docs/tool-taxonomy.md). Its methodology isn't installable on another
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

**Reasoning capability is declared data, not code branches — the best architecture of the
eight harnesses read for [issue #40](https://github.com/leandromineti/ai-assisted-coding/issues/40)**
(2026-08-26, verified at this report's pin `5dc9490b`; a targeted read of the reasoning
path only — this report's `depth: stub` is unchanged, nothing else was read). Each model
carries an `accepts_settings` list in `aider/resources/model-settings.yml` (233 entries),
and `--check-model-accepts-settings` refuses to send a setting the model has not declared.
Capability is a per-model fact in a data file that ships with the release, and the default
on an unknown model is *don't send* — the inverse of opencode's and cline's approach, where
capability is inferred from a substring match in code and the fallthrough is silent.

It still version-pins in one place, and the shape is instructive — an **exclusion** list
rather than an inclusion list (`aider/models.py`, the OpenRouter branch):

```python
if ("thinking_tokens" not in self.accepts_settings
    and "claude-opus-4.7" not in self.name
    and "claude-opus-4-7" not in self.name):
    self.accepts_settings.append("thinking_tokens")
```

OpenRouter models are auto-granted `thinking_tokens` unless they are **Opus 4.7
specifically** — the one model observed to have removed it. Opus 4.8, Opus 5, Sonnet 5 and
Fable 5 removed the same parameter and are all auto-granted it here. A carve-out added
reactively for one model id does not generalise to the next one, which is the same failure
as an inclusion list that stops at 4.8 — only reached from the opposite direction.

## Open questions

- Is the low commit velocity a sign of maturity or of decline? Check the contributor graph
  before drawing a conclusion.
- The repo map is the oldest serious answer to context assembly in this set. Does it still
  hold up against embedding- or agent-driven file selection?
- What accounts for the size difference — genuine simplicity, or scope the others took on?
