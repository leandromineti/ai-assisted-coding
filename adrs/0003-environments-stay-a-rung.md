# ADR-0003 — Execution environments stay a rung

`decided: 2026-08-16` · `recorded: 2026-08-18 (backfill — text extracted verbatim from
taxonomy.md §5 as of commit fd9f189)` · status: **accepted** (rung renumbered 5→3 by
[ADR-0007](0007-renumber-core-triad-first.md))

## Decision

Execution environments remain their own layer. A same-day adjudication had proposed
gated demotion to an axis of the harness layer; the E2B deep-dive fired the "keep it a
rung" arm of the gate.

## Record (extracted from taxonomy.md, as written — "layer 5" is the environments
layer's number at the time, "layer 2" the harness layer)

> **Adjudicated 2026-08-16, then RESOLVED the same day.** The adjudication returned a
> split verdict — *"explaining a failure"* passed via the worktree trap, *"changing a
> tool choice"* had no instance — and proposed **gated** demotion to a "fifth axis of
> layer 2," pending the first report of an agent-native environment studied as a
> product in its own right. **That report landed the same day (E2B) and fired the
> "keep it a rung" arm of the gate.** The short form: E2B produced ~26
> environment-facts against 6 attachment-restatements, every one of the 26 invisible
> from the SDK (no jailer on Firecracker; create-is-resume with no warm pool; the
> credential-injection proxy closed-source; guest `kcompactd` disabled for host
> snapshot economics). One genuine population member falsifies "fails as a
> population," so **layer 5 stays a rung and the demotion does not execute.**

Full reasoning: `notes/…-execution-environments/index.md` (path per the current
numbering); README conclusion 9 records the same decision as a finding.

## Consequences

The live successor question — whether E4-class facts are legible only when the
environment is open-source — is
[issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11). The
2026-08-17 reframing ([ADR-0004](0004-core-triad-reframing.md)) then made the
environment one of the three core fundamentals, and ADR-0007 gave it the number that
position implies.
