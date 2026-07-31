---
name: <tool>
layer: <1-5>
# The next three fields are for layer-2 (harness) reports; omit where not meaningful.
surfaces: [<terminal | ide | desktop | web>]   # where you interact — multi-valued
execution: <local | async-remote | both>        # how it runs
environments: [<host | worktree | container | remote-sandbox>]  # layer-5 bindings (bleed) — only list what's verified
vendor: <who maintains it>
url: <repo or product URL>
license: <SPDX id, or "proprietary">
open_source: <true | false>
stack: [<Language>, <Runtime/Framework>]
version: <git describe --tags --always — omit if closed source>
commit: <short SHA — omit if closed source>
# The next three come from scripts/repo-facts.sh — never hand-typed. Omit if closed source.
first_commit: <YYYY-MM-DD — first commit in the public repo; postdates the product if open-sourced later>
stars: <integer, GitHub API>
stars_at: <YYYY-MM-DD the star count was fetched — stars drift daily, so they carry their own date>
read_at: <YYYY-MM-DD>
depth: <stub | survey | deep-dive>
# harness_targets: layer-4 (and layer-3) reports only — which harnesses the tool
# officially installs into. Same discipline as features: set ONLY when verified in
# source or official docs; omitted means "not yet checked". Either a list of harness
# names, or a short string for large sets (e.g. "44 integrations incl. …").
harness_targets: [<Harness>, <Harness>]
# features: set a key ONLY when verified in source or official docs — omitted means
# "not yet checked", false means "checked and absent". Both are claims; only one is safe
# to guess, and neither should be. Keep the vocabulary to this fixed set so the generated
# matrix stays comparable — don't add vendor pet names:
features:
  mcp: <true | false>              # MCP client support
  lsp: <true | false>              # language-server integration
  hooks: <true | false>            # deterministic lifecycle hooks / plugin triggers
  skills: <true | false>           # on-demand packaged instructions
  subagents: <true | false>        # spawnable isolated agents
  plan_mode: <true | false>        # built-in plan/act split
  rules_files: <true | false | [FILENAMES]>  # standing-instruction files; list names if known
  model_agnostic: <true | false>   # bring-your-own-model by design
  session_sharing: <true | false>  # shareable session links/artifacts
  evals: <true | false>            # ships its own evaluation suite
  learning_loop: <true | false>    # AUTONOMOUS agent-written memory/skills (background/spawned write path) — distinct from `skills` (packaged instructions exist) and from user-curated memory files. Added 2026-07-30 per issue #2's two-verified-instances rule (hermes, codex); note default-on vs default-off in the comment
---

# <Tool>

> Fill the frontmatter from `./scripts/repo-facts.sh <name>`. Never hand-type a SHA —
> `build-tool-index.py --check` compares it against the clone's HEAD, and a stale pin
> silently invalidates every architecture claim below it.
>
> `depth` is a promise to your future self: **stub** = facts collected, source unread ·
> **survey** = used it or skimmed it · **deep-dive** = the agent loop and context assembly
> were actually traced. Never raise it out of optimism.
>
> Relative links below are written for a report's destination, `notes/0N-<layer>/<tool>.md`
> — they resolve once copied there, not from this file's own location.

## What it is

One paragraph. Plain description, no marketing language, no feature list.

## The distinguishing bet

What does this tool believe that its competitors don't? Every serious tool wagers on some
claim about how AI-assisted coding should work. Find the wager. If you can't name one its
rivals would dispute, it's a commodity — and that is itself the finding worth recording.

## Main features

The handful that matter for comparison, not the marketing page. For each, note whether it's
genuinely distinctive or table stakes everyone ships.

## Stack & repo shape

Languages, runtime, frameworks, and how the repo is organized (monorepo? packages?). Include
the file-extension distribution — it reveals what a project actually *is* faster than its
README does.

## Architecture

*Deep-dive only. Leave the subsections marked `_TODO_` until the source has been read —
an empty section is honest, a guessed one is worse than nothing.*

### Entry point → one full trace

Follow a single invocation from CLI entry to completion, naming real files and functions.
This is the spine; if it's vague, nothing below it can be trusted.

### The agent loop

Where it lives, what one iteration does, what terminates it (task completion? step budget?
token budget? error?). What happens when a tool call fails — retry, surface, abandon?

### Context assembly

What enters the model call, in what order, and what's dropped under pressure. The least
documented and most differentiating part of any harness. How are files selected — repo map,
embeddings, grep, or the model asking? What does compaction silently lose? Is the prompt
structured so caching can work?

### Tool surface & permissions

How tools are defined and described to the model, how dispatch works, and whether the
permission check happens *before* or *after* the model decides.

### Layer boundaries in the code

Where the taxonomy's seams show up concretely. Is the model provider swappable, and at what
cost? Is there an execution-environment abstraction, or does it shell out to the host? Can
layer-3 extensions attach, and where?

## Bleed

Which other taxonomy layers this tool reaches into, and how. See
[`../../taxonomy.md`](../../taxonomy.md) — the bleed is signal, not noise.

## Cost model

Subscription, per-token, open-source-but-you-pay-inference, free. Note the *shape*, not just
the number: a flat subscription and a metered bill push behavior in opposite directions.

## Surprises

What contradicted your expectations. **The most valuable section in the document.** If it's
empty, you either skimmed or already knew this tool — say which.

## Open questions

- 
