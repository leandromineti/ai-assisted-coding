# ADR-0021 — Harness decomposition: three components, two descriptive axes

`decided: 2026-08-22` · status: **accepted**

## Decision

Category 2 (Harnesses) gets an explicit decomposition, replacing taxonomy §2's
undeveloped one-liner ("loop + context assembly + permission model + UI"):

- **Three components**, each stated as an agent-shaped question and each anchored by a
  finding traced in source:
  1. **The loop** — *who can stop or steer a turn, and with what authority?* The turn
     engine: iteration, tool dispatch, stop conditions, subagent fan-out, plan-mode
     checkpoints. Tools-and-files reach folds in here as the loop's dispatch table.
     Anchor: the enforcement inversion (native `engine`/`hook` turn gates vs
     frameworks' `prose` — ADR-0011/0012, conclusion 8).
  2. **Context assembly** — *what reaches the prompt, who wrote it, and where does the
     agent's own output land?* Rules-file and skill injection, memory write-back,
     compaction, cache discipline. Anchor: the hermes cache-tension finding, which
     states this component's question verbatim.
  3. **The permission gate** — *what may the agent attempt without a human, and can
     the model influence that decision?* The harness's end of the harness↔environment
     edge: in-process policy, verified `engine`-grade in five tracked harnesses
     (hermes, codex, opencode, claude-code, Warp). Anchor: Warp's `AgentDecided`
     crack (a model-authored `is_risky: false` self-authorizes). Boundary test
     against category 3: if the model can influence it or a child process can escape
     it, it is the gate (category 2); if it holds regardless of what the software
     does, it is the bounds (category 3). Autonomy is the product of gate policy ×
     environment bounds (principle E1).
- **Two descriptive axes** — surfaces and execution — stand beside the components,
  unchanged in content. They are transcription facts (readable off product docs, per
  the feature taxonomy's placement test), not traced mechanisms, and the
  decomposition makes that standing explicit.
- **No "human front" component.** Its assessment-grade fragments already belong to
  the components (approval UI to the gate; plan-mode checkpoints to the loop), the
  axes carry its classification facts (`session_sharing` sorts there too), and the
  human⇄stack boundary is category 4's territory.
- The triad sentence in taxonomy's lead-in — previously five verbs ("runs the loop,
  assembles context, gates permissions, fronts the user, reaches tools and files"),
  disagreeing with §2's own four-part one-liner in the same document — is reconciled
  to the three components plus axes.

Live strain notes and re-open triggers stay in taxonomy §2 per this repo's ADR rule
(falsifiers live in the living docs); this record narrates them below.

## Why, honestly

The decomposition was already latent and unsettled: the same living document carried a
four-part list in §2 and a five-verb list in the triad description, never reconciled.
The environment category got its questions made explicit and load-bearing (blast
radius / fidelity / parallelism); the harness never did, despite being the category
the taxonomy itself calls the contested ground of 2026.

Each in/out call came from an existing repo discipline, not taste:

- **Reach folds into the loop by the discriminate test.** A component earns
  separation where its questions discriminate between tools. The `mcp` column is a
  uniform ✓ across every checked row — commodity, non-discriminating, the same
  situation the category-2 absorption table records for `deterministic_engine`. What
  splits is invocation shape (`ptc` 3✓/4✗, parallel dispatch, turn gates) — all loop
  mechanics.
- **The human front dissolves by the placement test** (transcription vs assessment,
  feature taxonomy, 2026-08-19). Every recorded front fact — the surfaces axis, the
  execution axis, the resident strain — is transcription: readable off product docs,
  drifts when a vendor ships a desktop app. Every retained component is anchored by a
  mechanism finding traced in source. The front has no mechanism finding; a component
  with no anchor is a hollow seat.
- **Dropping the front also removes a territorial ambiguity**: taxonomy §4 assigns
  the human⇄stack boundary to workflow frameworks. Three mechanism components plus
  descriptive axes matches the absorption finding's grain — harnesses own mechanisms;
  human-boundary methodology is category 4's.
- **Validity test**: sorting the 13 `harness_features` keys under the components
  independently reproduces the vocabulary-gap assessment made the same day — the
  loop takes six keys, context assembly takes three but none on its central
  mechanism (compaction, cache placement), and the permission gate takes **zero**
  despite being universal `engine`-grade machinery. A decomposition that both
  organizes the existing keys and predicts where the vocabulary is thin is doing
  work. (Those gaps are a work queue, not part of this decision.)
- **The role differs from category 3's questions, on purpose.** The environment's
  three questions are an ingestion lens that makes borrowed infrastructure
  agent-shaped. Harnesses are native objects here; the components are a deep-dive
  tracing discipline (which of the three did this read actually trace?) and a
  sorting frame for the vocabulary.

## Considered and not taken

- **Reach as a fourth component.** The counter-argument is real and recorded:
  taxonomy §6 assigns MCP its own harness↔world edge, which reserves a seat for
  reach if components map to edges. Deferred on the resident-strain precedent (real,
  observed, not promoted ahead of a second discriminating instance). Trigger, live
  in §2: the first reach-shaped finding that isn't loop-shaped — an edit-format
  study, or verified MCP-client divergence (aider's matrix row is unread today, and
  is the likeliest source).
- **A "human front" component.** Trigger to re-open, live in §2: a deep-dive
  mechanism finding that fits none of the three — likeliest the async-remote
  report-back path (what evidence does the agent assemble for a human who wasn't
  watching?), untraced in any current read.
- **A model-client component** (provider protocol, per-model prompts, caching
  integration; evidence: opencode's nine bespoke per-model prompts, the
  `model_agnostic` key, ECC's per-model prompts on the model↔harness edge). Folded
  into context assembly: per-model prompts *are* assembly, caching is assembly
  economics. The weakest boundary of the three; a run of provider-transport findings
  that aren't assembly-shaped would reopen it.
- **Extensibility as a component.** Rejected as a category error the kind_link data
  already resolves: the five kind-linked keys are the components' *apertures* — the
  pluggable form of each (hooks and subagent-defs extend the loop, MCP its dispatch,
  skills and rules files feed context assembly). Consistent with §6's claim that
  extensions parameterize the triad's edges, and it explains why the extensions
  bucket never read as a harness component.
