# <Tool> — architecture

- **Layer:** <1–5>
- **Source:** <repo URL> · commit `<sha>` · `read: YYYY-MM-DD`
- **Language / stack:**
- **Size:** <LOC or file count, and how you counted>

> Pin the commit. Notes on a moving target rot silently, and "it works like X" is
> unfalsifiable without a revision to check it against.

## Entry point → one full trace

Follow a single request from invocation to completion. Name the actual files and
functions. This section is the spine of the document; if it's vague, nothing below it
can be trusted.

## The agent loop

The core cycle. Where it lives, what one iteration does, what terminates it.

- **Termination:** what ends the loop — task completion, step budget, token budget, error?
- **Error handling:** what happens when a tool call fails? Retry, surface, abandon?
- **Streaming vs. batch:** does it act on partial output?

## Context assembly

What goes into the model call, in what order, and what gets dropped under pressure. The
least documented and most differentiating part of any harness.

- What's loaded eagerly vs. on demand
- How files are selected (repo map? embeddings? grep? the model asking?)
- Compaction/summarization strategy, and what it silently loses
- Caching, and whether the prompt is structured to make caching possible

## Tool surface

How tools are defined, described to the model, and dispatched. How permission is checked —
and whether it's checked *before* or *after* the model decides.

## Layer boundaries in the code

Where the taxonomy's seams appear concretely. Is the model provider swappable, and at what
cost? Is there an execution-environment abstraction, or does it shell out to the host? Can
layer 3 extensions attach, and where?

## Design decisions worth stealing

Specific and transferable. "Good architecture" is not an entry.

## Design decisions worth avoiding

Including the ones that look clever and aren't.

## What the history says

Read `git log` on the loop and context files. Retries, guards, and truncations are bug
reports in disguise — the commit that added one tells you what broke in production.

## Surprises

What contradicted your expectations. **The most valuable section.** If it's empty, you
either skimmed or you already knew this tool — say which.

## Open questions

- 
