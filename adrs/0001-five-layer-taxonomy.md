# ADR-0001 — A five-layer taxonomy for AI-assisted-coding tooling

`decided: 2026-07-28` · `recorded: 2026-08-19 (backfill, reconstructed from commit
c662b92 and the taxonomy as then written)` · status: **superseded by
[ADR-0007](0007-renumber-core-triad-first.md)** (the numbering; the layers themselves
stand)

## Decision

Organize the survey as a layered stack, one directory and index per layer, so that
comparisons stay like-for-like ("Claude Code vs. GSD vs. Opus 5" is a category error):

1. **Models** — the weights.
2. **Harnesses** — the program that runs the agent loop.
3. **Capability extensions** — what the agent can see and touch, as distributable
   content (MCP servers, skills, rules files).
4. **Workflow frameworks** — an encoded methodology riding on top of a harness.
5. **Execution environments** — where the agent's code runs and what it can damage.

Every note declares a **primary layer** plus an explicit **bleed** note (the layers
are analytic, not physical). Cross-cutting concerns and standards sit outside the
ladder.

## Context

The ordering followed the dependency direction as then understood: each layer rides on
the one below. Layer tests were defined per layer (e.g. layer 4's harness-portability
test; layer 3's independent-distribution test) so hard cases could be classified by
kind rather than by marketing.

## Consequences

Directory names `notes/01-…` through `notes/05-…`, `layer:` frontmatter ints consumed
by the generators, and "layer N" as prose vocabulary throughout the repo — the coupling
that later made renumbering a recorded decision rather than a cheap edit
([ADR-0007](0007-renumber-core-triad-first.md)).
