# The feature taxonomy

`created: 2026-08-18` · decision record: [ADR-0010](../../adrs/0010-two-taxonomies.md)

This repo carries **two taxonomies**. The [tool taxonomy](../../taxonomy.md) classifies
what a tool *is* (the layers, plus sub-categories like layer 5's `kind` and layer 4's
poles). This file is the **feature taxonomy**: every characteristic we assess on tools,
defined **once**, with an applicability map saying which layers it can occur in. The
generator (`scripts/build-tool-index.py`) reads the YAML block below as its single
source of truth for valid frontmatter keys — the per-layer matrices in
[`comparisons/features.md`](../../comparisons/features.md) and its cross-layer table
are derived from here plus report frontmatter. **Do not add a key anywhere else.**

Conventions:

- A feature is a **presence-claim** verified in source or docs (omitted = not checked,
  `false` = checked and absent) — the same discipline as everywhere in this repo.
  Whether a present feature *pays* is a mechanism question (see each layer's index).
- New keys follow **issue #2's two-verified-instances rule**: a key enters the
  registry only after the characteristic is verified in at least two tools.
- `block` names the frontmatter block that carries the key (`features` for harnesses,
  `workflow_features` for layer 4). `applies_to` lists tool-taxonomy layers.
- `kind_link` records the **demand↔supply correspondence**: a harness feature (demand
  side) whose supply side is an installable layer-5 artifact kind. This is the bleed —
  quantified in the generated cross-layer table.
- "Vocabulary" remains the mechanism phrase for this closed key list; the *concept* is
  the feature taxonomy (naming settled 2026-08-18, ADR-0010).

```yaml
features:
  # --- harness block (`features:`), applies to layer 2 ---
  - id: mcp
    block: features
    applies_to: [2]
    definition: MCP client support
    kind_link: mcp-server
  - id: lsp
    block: features
    applies_to: [2]
    definition: language-server integration
  - id: hooks
    block: features
    applies_to: [2]
    definition: deterministic lifecycle hooks / plugin triggers
    kind_link: hook
    note: "supply side also carries layer-4 verification mechanisms — ECC finding: gates can arrive as installable Stop hooks"
  - id: skills
    block: features
    applies_to: [2]
    definition: on-demand packaged instructions
    kind_link: skill
  - id: subagents
    block: features
    applies_to: [2]
    definition: spawnable isolated agents
    kind_link: subagent-def
  - id: plan_mode
    block: features
    applies_to: [2]
    definition: built-in plan/act split
  - id: rules_files
    block: features
    applies_to: [2]
    definition: standing-instruction files (value may list filenames)
    kind_link: rules-file
  - id: model_agnostic
    block: features
    applies_to: [2]
    definition: bring-your-own-model by design
  - id: session_sharing
    block: features
    applies_to: [2]
    definition: shareable session links/artifacts
  - id: evals
    block: features
    applies_to: [2]
    definition: ships its own evaluation suite
  - id: learning_loop
    block: features
    applies_to: [2]
    definition: AUTONOMOUS agent-written memory/skills (background/spawned write path) — distinct from `skills` and from user-curated memory files
    kind_link: memory
    note: "added 2026-07-30 per issue #2's two-verified-instances rule (hermes, codex); note default-on vs default-off when setting"
  # --- layer-4 block (`workflow_features:`) ---
  - id: intent_pipeline
    block: workflow_features
    applies_to: [4]
    definition: staged requirements→implementation artifact pipeline (the SDD spine)
  - id: deterministic_engine
    block: workflow_features
    applies_to: [4]
    definition: a program — not prose — parses/validates/advances workflow state
  - id: format_gates
    block: workflow_features
    applies_to: [4]
    definition: machine-checkable artifact-structure gates
    note: "calibration lesson 2026-08-18: spec-kit's ✓ flipped to ✗ at deep-dive — a gate stated in prose looks like machinery until you check who enforces it"
  - id: measured_gates
    block: workflow_features
    applies_to: [4]
    definition: acceptance criteria with measured expected values (behavior, not format)
    kind_link: hook
    note: "the ECC finding — this mechanism can be delivered as installable layer-5 Stop hooks, independent of any framework"
  - id: process_gates
    block: workflow_features
    applies_to: [4]
    definition: human approval checkpoints encoded in the flow
  - id: context_isolation
    block: workflow_features
    applies_to: [4]
    definition: fresh/right-sized agent context per unit of work, by design
    note: "supply side is layer-2 machinery (subagents, fresh sessions) — a framework can only instruct it"
  - id: parallel_orchestration
    block: workflow_features
    applies_to: [4]
    definition: concurrent agents/work-packages machinery (worktrees, fan-out)
  - id: state_store
    block: workflow_features
    applies_to: [4]
    definition: "where workflow state lives: repo-files | database"
  - id: retrospectives
    block: workflow_features
    applies_to: [4]
    definition: encoded learning step feeding completed work back into the process
    note: "the framework-side cousin of the harness `learning_loop`"
```
