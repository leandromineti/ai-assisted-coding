# ADR-0019 — Coverage strata for category 5

`decided: 2026-08-22` · status: **superseded in part by
[ADR-0020](0020-memory-category-extensions-renumbered.md) (2026-08-22): the mechanism
stratum is promoted to category 5 (Memory); the content/reach strata carry forward as
category-6 coverage semantics**

## Decision

Category 5 keeps its full seven-type scope (ADR-0016, untouched), and gains **three
coverage strata** — per-type *coverage semantics*, deciding how deeply this repo engages
each type, not what belongs in the bucket:

1. **Mechanism extensions** — artifacts that add a harness-native *mechanism*: write
   paths, consolidation loops, cross-session state, enforcement gates, learning
   runtimes. Types: `memory`, plus gate/learning runtimes however delivered. Coverage:
   **tool-grade** — full engagement ladder (candidate → stub → survey → deep-dive),
   per-type feature blocks (ADR-0013's `memory_features` is the template), reading arcs.
2. **Content types** — slot-fillers for loaders the harness already ships. Types:
   `skill`, `rules-file`, `subagent-def`. Coverage: **formats tracked in the
   [Standards scoreboard](../notes/cross-cutting/standards.md); exemplar reads only,
   never censuses.**
3. **Reach-side** — the population an agent reaches through an unchanged interface.
   Type: `mcp-server`. Coverage: **exemplars only, capped, each read to answer a
   registered question** (the live one: conclusion 3 rests on "MCP settled" and no
   server has ever been read). The population is world, not stack — having an MCP
   client doesn't make every MCP server stack, any more than having a shell makes
   ripgrep stack.

Two types are **graded by payload, not slotted**:

- `hook` is the **port mechanisms arrive through** (the memory tools themselves install
  via hooks; "gates can arrive as installable Stop hooks" is the registry's ECC
  finding). It is tracked via the Standards scoreboard and the `kind_link` demand side;
  a hook *pack* earns mechanism-grade coverage only if it ships a mechanism.
- `config-pack` bundles across strata and takes the grade of what it ships: ECC is
  mechanism-grade (instinct pipeline, enforcement gates) even though most of its bulk
  is content (the catalog).

No new frontmatter key: a report's stratum is derivable from `type:` plus the payload
judgment above, and the judgment belongs in the report's prose, not in a schema cell.

## Why

The narrowing instinct — "category 5 is really the memory category" — recurred on
2026-08-22 after being rejected by ADR-0016 (arc-sample bias) three days earlier. The
checkpointed boundary discussion
([bucket index](../notes/05-capability-extensions/index.md), 2026-08-19/20) had already
processed that instinct into two cuts that survive where the narrowing fails:

- **Configure vs reach** bounds the bucket on the world side and explains why an MCP
  census is illegitimate (MCP servers are *agent-native world* — partially authored in
  prompt-space, which makes them feel stack-adjacent without making a census
  legitimate).
- **Mechanism vs content** captures what is *true* in the narrowing: memory tools are
  mechanism-adders, which is why exactly they are being absorbed natively
  (the `learning_loop` column). The "only memory" version is **falsified by one case,
  which sharpens rather than kills it**: ECC ships a learning pipeline (third verified
  `learning_loop` instance) and enforcement gates, so the mechanism stratum is memory
  *plus gate/learning runtimes* — and hooks are the port they arrive through.

Strata deliver the clean memory-centric reading the instinct wants — the mechanism
stratum already has its own feature block and generated matrix — without redrawing the
category boundary around one arc's sample, orphaning the seven `kind_link` demand→supply
rows, or removing the falsifying case to make the theory clean.

## Explicit non-decisions

- **The type list does not change** — ADR-0016 stands unreversed; this ADR is the
  successor it left room for ("types thicken inside category 5; they do not secede").
- **No report moves, none is de-categorized.** ECC stays `category: 5`,
  `type: config-pack`, mechanism-grade. The orca candidates row and its
  orchestrator-above-harnesses two-instance trigger stay armed and untouched.
- **The ~2027-01 standards re-check and ADR-0002's re-promotion trigger** keep their
  roles; strata do not pre-empt either arm.
- The absorption hypothesis (harnesses absorb mechanisms, bundle content, never absorb
  reach) is **registered as principle X3 in
  [design-principles.md](../design-principles.md)** with its three falsifiers and the
  ~2027-01 re-check — resolving the discussion's open thread about where the bet lives.

## Number drift

The bucket index's checkpoint sketched this decision under the name "ADR-0017"; that
number was taken by `0017-environment-features-block.md` (2026-08-20) before this was
written. References to a coverage-strata "ADR-0017" decode to this ADR.

## Consequences

- Issue #30's balance arc reads under strata semantics: reach-side sightings are
  designated exemplars (already stated in the 2026-08-19 candidates rows), content
  types get exemplar reads, `config-pack` is already covered at mechanism grade by ECC.
- The census temptation for MCP servers is now refused by a decision, not a discussion.
- A future second config-pack or a mechanism-shipping hook pack slots into the strata
  without new vocabulary; only a genuinely new *mechanism kind* would reopen this.
