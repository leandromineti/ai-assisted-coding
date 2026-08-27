# ADR-0047 — the resident agent gets a field, and messaging gets a surface

`decided: 2026-08-27` · status: **accepted**

## Decision

The **resident-agent strain**, recorded against the category-2 descriptive axes on
2026-07-30 and left unresolved by design, is resolved in the two halves it always had:

1. **`messaging` becomes a fifth `surfaces` value.** `surfaces` is a list, so the value
   composes with the existing four and nothing has to be dropped. It names a *class* of
   platforms; each report's cell comment says which.
2. **`residency` becomes a new transcription field** — `session | resident`, `applies_to: [2]`,
   `group: shape`, `verification: source-or-docs`, `rendered_in: [tools.md]` — carrying the
   persistence half that `execution` was never asking about.

`execution` is **unchanged**: still `local | async-remote | both`.

Validated by `check_shape_axes` in `scripts/build-tool-index.py` — the seventh cell-value
check, and the first to validate `surfaces`, which was a free list until this ADR widened it.

## Context — the trigger this paragraph wrote for itself

The hermes-agent deep-dive (2026-07-30) found a shape neither `execution` value described: a
persistent gateway daemon outliving any conversation, ~20 messaging platforms, cron jobs
running unattended, serverless backends hibernating between sessions. The taxonomy recorded
it and deliberately did not act:

> Not promoted to a third value on one instance — recorded here so the second instance
> triggers the revision. Same read strained **surfaces**: messaging platforms don't fit the
> four-value vocabulary and are recorded as an annotation, not a fifth value.

The [qwen-code deep-dive](../tools/2-harnesses/qwen-code.md) (2026-08-27) is that instance:
`qwen serve` (a local HTTP daemon), a per-session `CronScheduler`, and eleven messaging
channel packages — feishu, dingtalk, telegram, qqbot, wecom, weixin, github, gitlab, dws —
each driving a spawned `--acp` child, with permission prompts routed back out to the
platform.

Two things make it a real trigger rather than a coincidence. It is an **independent lineage**
(Nous Research and Alibaba, converging on the same architecture with no shared code), and the
two reports had already begun to **contradict each other in the data**: hermes-agent recorded
the shape as a comment on `execution: both`, qwen-code as a comment on `execution: local`.
The same fact, annotated onto two different enum values, is what leaving a strain in prose
eventually costs.

## Why not a third `execution` value

`resident` as a fourth enum value was the smaller edit and is **rejected on collision**, not
on accuracy. The two verified instances are the proof:

| | `execution` | resident? |
|---|---|---|
| hermes-agent | `both` — local CLI/TUI **and** remote terminal backends | yes |
| qwen-code | `local` — the work runs on your machine | yes |

A closed enum carries one value (the `pricing.regime` precedent, ADR-0033: *"the second
regime lives in note rather than making regime list-valued, because a matrix column sorts on
one thing"*). Adding `resident` would have forced hermes-agent to choose between its remote
backends and its daemon, and qwen-code to choose between `local` and its channels — each
losing a true fact to record another. That is the shape of a **conflated axis**, and the fix
for a conflated axis is a second axis, not a longer enum.

The two questions really are independent: `execution` asks *where does the work run*,
`residency` asks *does the agent outlive the conversation*. Nothing prevents a local session
agent, a local resident agent, a remote session agent, or a remote resident agent — and two
of those four cells are already occupied.

## Scope

- **Category 2 only.** `residency` is a harness fact. Whether a category-3 environment or a
  category-5 memory service is "resident" is a different question in each, and this ADR does
  not answer it by extension.
- **Verified-only, like every transcribed field.** Two reports carry `residency` today; the
  other ten predate the field and omit it, which honestly means *not checked* rather than
  `session`. A default-filled column would manufacture ten claims nobody made.
- **`session` is defined but unused.** The first harness verified as *not* resident earns it.
  A vocabulary with an unused value is honest here: the enum states the axis, and the empty
  side is a work queue rather than a gap in the definition.

## Consequences

- **Two frontmatter comments became false and were rewritten.** hermes-agent's surfaces
  comment said messaging platforms were "beyond the fixed vocabulary" and qwen-code's said
  the enum "has no value for" the resident streak. Both were accurate when written and are
  now wrong — the cost of a resolved strain, paid where it was recorded.
- **`surfaces` gets a checker.** It was validated by nothing until now. Widening a
  vocabulary is the moment to start checking it: a typo would otherwise invent a surface
  silently, and the field renders straight into `comparisons/tools.md`.
- **The `tools.md` shape cell shows `· **resident**` only when true.** `session` and omitted
  both render nothing, so the column carries two new facts without adding ten empty ones.
- **One open question is deliberately left open**, in the qwen-code report: both instances
  bundle a daemon, scheduled work, and inbound messages. Nothing yet shows whether those
  separate. A harness with cron and no messaging — or messaging and no daemon — would say
  whether `residency` is one axis or a collapsed pair, and that is the next trigger.
