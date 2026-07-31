---
name: openspec
layer: 4
vendor: Fission AI
url: https://github.com/Fission-AI/OpenSpec
license: MIT
open_source: true
stack: [TypeScript, Node]
version: v1.7.0-5-g2b3d368
commit: 2b3d368
first_commit: 2025-08-05
stars: 63241
stars_at: 2026-07-31
read_at: 2026-07-31
depth: deep-dive   # the runtime traced in source: delta-merge engine (specs-apply.ts), archive flow, artifact-graph DAG engine + schema loader, validator, command-generation adapters; skills read; dogfooding measured. Website/docs skimmed
harness_targets: "29 adapter modules in src/core/command-generation/adapters/ (claude, cursor, cline, continue, opencode, gemini, copilot, devin, kiro, roocode, qwen, …); 37 tool configs with skills dirs; detection by scanning for each tool's config dirs"
---

# OpenSpec

Spec-driven development via **delta specs**: spec only the change (proposal → specs →
design → tasks), archive completed changes, and let a deterministic merge accrete the
deltas into a living source-of-truth spec. The lean pole of the 2026 SDD trio
(BMAD / spec-kit / OpenSpec). Maintainer-dominated like most of the set: 516 of 723
commits (71%) from one author under the Fission AI org.

## The layer-4 questions, answered

**1. Is the delta→source-of-truth merge deterministic or model-run? Deterministic —
and not as an afterthought.** `src/core/specs-apply.ts` (570 lines) is a compiler for
spec deltas: a formal grammar (`## ADDED/MODIFIED/REMOVED/RENAMED Requirements`
sections over `### Requirement:` headers), duplicate detection per section,
cross-section conflict detection (MODIFIED×REMOVED, ADDED×REMOVED, rename interplay
with "MODIFIED must reference the NEW header"), near-miss diagnostics ("source not
found, but «X» exists; fix the header to match it exactly"), ordered application
(RENAMED → REMOVED → MODIFIED → ADDED), hard failures on violations, warnings for
benign cases (REMOVED-already-gone). The model *authors* delta files; code merges them.

**2. Does the delta model dodge staleness or relocate it? Structurally dodge.** The
living spec is compacted *continuously*: `openspec archive` validates the change, runs
the merge, and moves the change to a dated archive. The archive is history; the specs
tree is current state. Dogfooding proves the loop at scale — see below.

**3. Portability: compile-per-harness, confirmed — but thinner than spec-kit's.**
29 per-harness adapter modules generate skill/command wrappers from one source; tools
are auto-detected by scanning for their config dirs. The generated payload is *thin by
design* because the logic doesn't live in the prose — see the bet.

## The distinguishing bet

**Same diagnosis as spec-kit (under-specified intent), inverted runtime: the prose is
a thin adapter; the state machine is code.**

Three structures carry it:

- **The workflow is data.** `schemas/spec-driven/schema.yaml` declares the artifact
  chain — each artifact with its output pattern, template, `requires:` dependencies,
  and embedded authoring instruction. `src/core/artifact-graph/` is the engine: schema
  loader, DAG, completion detection *from filesystem state*, next-artifact resolution.
  User schema dirs exist (`getUserSchemasDir`) — the methodology is pluggable data
  interpreted by one engine.
- **The gates are machine-checked.** `openspec validate` (`src/core/validation/`)
  enforces the delta grammar and rejects a change with zero deltas unless its
  `.openspec.yaml` explicitly sets `skip_specs: true` — an escape valve that demands
  explicitness, with the schema instruction adding: *"Do not invent a requirement just
  to satisfy validation."* Anti-vacuous-compliance, in the framework's own prompt.
- **The skills shell out.** Each generated skill (e.g. `openspec-apply-change`) carries
  `allowed-tools: Bash(openspec:*)` and instructs the model to get state from the CLI
  (`openspec status --json`, `openspec instructions`) rather than re-deriving it from
  prose. The model executes; the CLI knows where it is.

Contrast recorded in README conclusion 7: spec-kit fixed hook execution twice by
*rewriting instructions more forcefully*; OpenSpec's equivalent contract is a validator
error with a fix hint. Enforcement-by-typography vs enforcement-by-exit-code.

## Mechanism profile vs the stub's prediction

The stub predicted "intent-capture concentrated, bookkeeping minimal, process gates
near zero, empirical grounding absent." **Half wrong, in the informative direction:**
intent capture concentrated ✓; empirical grounding absent ✓ (nothing measures the
domain — no fixture-running, no probes; the framework validates *artifacts*, never
*behavior*); but bookkeeping and process gates are the **deterministic core of the
product**, not minimal. The correction matters for exp-03: OpenSpec's gates are
machine-checked yet still *format* gates (is the delta well-formed?), not exp-01's
*measured* gates (does the code behave as measured?). A framework can be fully
deterministic and still never touch the domain.

## Stack & repo shape

TypeScript CLI: 314 `.ts` under 635 `.md` across 1,039 tracked files; pnpm, vitest,
a Next-style `website/`. 723 commits since 2025-08-05.

**Dogfooding, measured:** the repo's own `openspec/` tree carries **83 archived + ~8
active changes over 36 living specs** — the tool's whole development history ran
through its own pipeline, including its in-flight work (`openspec/explorations/`,
`initiatives/`, a root `openspec-parallel-merge-plan.md`). After gsd-core, the second
framework whose behavior can be read from its own artifacts — and at ~10× the change
count.

## Bleed

Layer 3 by distribution (generated skills/commands into 29 harnesses' convention
dirs) and layer 2 by architecture: the CLI is a genuine runtime (state, validation,
merge), not an installer. But unlike spec-kit's `workflows/` engine or GSD's `gsd-pi`
— escape hatches grown after prose enforcement failed — OpenSpec's engine *is* the
original design. The conclusion-7 pattern arrived here as a founding decision, not a
symptom.

## Cost model

MIT, free; inference is your harness's. The lean shape is structural: one artifact
chain per change, no multi-agent fan-out, prose kept thin because state lives in the
CLI. (Third-party "cheapest of the SDD trio" claims remain unmeasured here — but the
design is consistent with them.)

## Surprises

1. **The deterministic engine is the founding architecture, not the escape hatch.**
   Both previously-read frameworks grew engines after prose failed (conclusion 7);
   OpenSpec started there. Design-principle F1's "plan the deterministic escape hatch
   from day one" has an existence proof.
2. **The methodology is pluggable data** — a schema YAML with embedded instructions,
   interpreted by a DAG engine with filesystem-state completion detection. Closest
   thing in the set to "workflow framework as declarative program," and the layer-4
   analog of codex's WorldState (state as typed, diffable structure).
3. **Machine gates ≠ measured gates.** Fully deterministic validation that never
   touches the domain — sharpens the exp-03 vocabulary: *format* gates (OpenSpec),
   *prose* gates (spec-kit), *measured* gates (GSD/exp-01) are three different
   mechanisms, and only the third traced to exp-01's quality margin.
4. **Anti-vacuous-compliance instructions in the framework's own prompts** ("do not
   invent a requirement just to satisfy validation") — the same failure mode the
   exp-02 rig's stub run exposed (vacuous T4/T5 passes), defended against from the
   authoring side.
5. **91 changes of self-hosted history** — the most complete dogfooding artifact in
   the set, and a ready-made corpus for studying how delta specs age (do old archived
   deltas still read coherently against the current spec tree?).

## Open questions

- The `openspec-parallel-merge-plan.md` at root + `explorations/` suggest multi-store
  / parallel-change work in flight — how will the deterministic merge handle
  concurrent changes touching the same requirement? (The conflict detector is
  single-change today.)
- Do the 29 generated integrations behave equivalently, or does skill-vs-command
  surface change outcomes per harness? (Same confound family as conclusion 2.)
- The archive corpus invites a measurement: sample archived deltas and check whether
  the merged spec tree actually matches what re-applying history would produce —
  a determinism audit the tool's own data makes possible.
- 63k stars vs spec-kit's 124k: substitution or coexistence? Still open; the bets are
  compatible (system-of-record vs change-unit could compose).
