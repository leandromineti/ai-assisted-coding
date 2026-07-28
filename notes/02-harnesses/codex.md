---
name: codex
layer: 2
sublayer: terminal
vendor: OpenAI
url: https://github.com/openai/codex
license: Apache-2.0
open_source: true
stack: [Rust, TypeScript]
version: codex-zsh-v0.1.0-803-gbb1af235ea
commit: bb1af235ea
read_at: 2026-07-28
depth: stub
---

# Codex CLI

OpenAI's vendor-native terminal harness. Leads Terminal-Bench 2.1 in the mid-2026 figures
recorded in [`../01-models/index.md`](../01-models/index.md) (83.4% paired with GPT-5.5).

## The distinguishing bet

_TODO_ — but the stack already hints at it: **it's the only harness in the set written in
Rust.** That's a wager that the harness's own latency and resource use matter, not just the
model's. Worth confirming against the source rather than assuming.

## Main features

_TODO_

## Stack & repo shape

Rust-dominant with a TypeScript surface — 2799 `.rs` against 648 `.ts` across 5799 tracked
files. Cargo workspace under `codex-rs/` with a striking crate list including
`agent-graph-store` and `agent-identity`; the npm-published CLI wrapper lives in
`codex-cli/`. 665 `.snap` files means heavy snapshot testing.

8658 commits since 2025-04-16.

## Architecture

_TODO — source unread._

## Bleed

_TODO_

## Cost model

Metered through OpenAI API pricing, or bundled with a ChatGPT plan. _Details TODO._

## Surprises

_Source unread — nothing earned yet. The Rust choice is the first thing to interrogate._

## Open questions

- Why Rust, when every peer chose TypeScript or Python? What did they think was the
  bottleneck?
- What are `agent-graph-store` and `agent-identity`? Neither has an obvious analogue in the
  other harnesses.
