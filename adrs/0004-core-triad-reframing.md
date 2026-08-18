# ADR-0004 — The core-triad reframing; numbers kept as storage keys

`decided: 2026-08-17` · `recorded: 2026-08-19 (backfill — text extracted verbatim from
taxonomy.md's preamble as of commit fd9f189)` · status: **reframing accepted; the
storage-keys rule is superseded by [ADR-0007](0007-renumber-core-triad-first.md)**

## Decision

Reframe the stack as a **core triad and its two interfaces**: a running agent system
requires exactly three things — model (cognition), harness (mediation), environment
(situation) — and everything else either parameterizes them or mediates between them
and the human. Extensions parameterize the triad's edges; workflow frameworks sit on
the human⇄stack boundary. A reframing rather than a reclassification: no tool changed
its home. The numbers stayed at their historical values as storage keys.

## Record (extracted from taxonomy.md, as written — numbers are the pre-ADR-0007 ones)

> **Reframed 2026-08-17 — the core triad and its two interfaces.** A recorded
> revision, and a *reframing rather than a reclassification*: no tool changes its
> home, the stress test stands unchanged, and the numbers remain storage keys (3 kept
> its number at the 2026-07-30 demotion for the same reason — renumbering breaks dated
> cross-references for zero information gain).
>
> - **Model (1)** — cognition. The weights.
> - **Harness (2)** — mediation. Runs the loop, assembles context, gates permissions,
>   fronts the user, reaches tools and files.
> - **Environment (5)** — situation. Where execution lands and what it can damage; the
>   autonomy ceiling lives here (principle E1), not in the model.
>
> **The necessity asymmetry** is why the layers feel so different to study: the model
> has **no degenerate form**, the harness degenerates to a bare while-loop around the
> API, and the environment degenerates to the host.
>
> **Countervailing evidence and falsifiers, recorded at reframing time:** (a) ECC is a
> 236k-star business built entirely on edge content, and the instinct-exchange
> re-check (~2027-01) can still force artifacts back from "interface detail" to a
> layer. (b) Warp shows the mediation role *nests* (a harness driving other
> harnesses), so "harness" names a function, not a unique slot. (c) The frame itself
> is falsifiable: it fails if artifacts standardize into an independently exchanged
> layer, or if a framework's measured value ever concentrates in intent-capture with
> the grounding and verification stripped out.

## Consequences

The reframing put the conceptual order (triad first) at odds with the storage order
(environments numbered last) — the mismatch ADR-0007 resolved. Falsifier (c)'s
framework half was subsequently tested by exp-02/exp-03 (README conclusions 11–12):
measured framework value concentrated in *written artifacts*, not intent-capture-owned
code quality, so the frame survived its first test. The falsifiers remain live in the
taxonomy.
