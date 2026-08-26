# 6 — Extensions & protocols (cross-category bucket)

> Renamed from "Portable artifacts" 2026-08-17: portability is not an intrinsic
> property of an extension but a status the ecosystem confers by adoption — unevenly
> across the types below (see the Standards scoreboard and the dated rename note in
> [`../../taxonomy.md`](../../taxonomy.md)). Renumbered 5 → 6 at the 2026-08-22 split
> ([ADR-0020](../../adrs/0020-memory-category-extensions-renumbered.md)): the memory
> type left this bucket to become category 5 — [Memory](../5-memory/index.md).

`checked: 2026-08-22`

What the agent can **see and touch**, as distributable content. **A bucket, not a
category-of-fundamentals, since the 2026-07-30 taxonomy revision** (trigger fired at the
ECC deep-dive — see the executed-revision note in
[`../../taxonomy.md`](../../taxonomy.md)). The membership test is unchanged: independent
distribution — authored, versioned, and installed separately from any harness. The "6"
is a storage key (3 → 5 by [ADR-0007](../../adrs/0007-renumber-core-triad-first.md),
5 → 6 by ADR-0020).

This index covers the **installable things**. The specifications they implement — MCP the
protocol, the `AGENTS.md` convention — are not category entries; they live in
[`../standards/`](../cross-cutting/standards.md).

## Types

Reports in this bucket carry a `type:` frontmatter key from this table's vocabulary
(`mcp-server · skill · hook · subagent-def · rules-file · config-pack`) — added
2026-08-18 so the bucket can be sliced by type as it grows. *(The seventh value,
`memory`, left with the split — memory reports are category 5 and keep `type: memory`
as residual data, ADR-0020.)*

| Type | What it does | Portability |
|------|--------------|-------------|
| **MCP servers** | Expose external systems (filesystems, APIs, databases, browsers, SaaS) as tools over the Model Context Protocol. | High — one server works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Devin. |
| **Skills** | Packaged instructions loaded on demand for a class of task. | Converging (2026-07-28): `SKILL.md` consumed by ≥4 harnesses per spec-kit's integration registry — convention-level, like rules files. See [standards](../cross-cutting/standards.md). |
| **Hooks** | Deterministic code the harness runs at lifecycle points (pre/post tool use, session start/stop). Not model-mediated — the harness executes them, so they *always* fire. | Harness-specific. |
| **Subagent definitions** | Named agents with their own prompt, tools, and model, spawned for isolated work. | Harness-specific format; the pattern is universal. |
| **Rules files** | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — standing instructions injected into context. | Convention-level only — see [standards](../cross-cutting/standards.md). |
| **Config packs** | Curated bundles of the other types at scale (skills + agents + rules + hooks), installed as a set. | Rides on the file conventions of what it bundles — ECC's ~13 install targets are the measured case. |

**Coverage note (2026-08-19, renumbered 2026-08-22).** This bucket has one report (ECC)
— the other types' `0 tracked` in the generated supply table is *not-checked*, not
checked-absent. The [candidates ledger](../candidates.md)'s category-6 section (first
five rows sighted 2026-08-19, all in this bucket's types) is where that gap is being
worked; the balance arc is issue #30, and the recorded decision point for the bucket's
shape stays the ~2027-01 [standards re-check](../cross-cutting/standards.md). Coverage
depth per type follows the surviving strata semantics
([ADR-0019](../../adrs/0019-category-5-coverage-strata.md), carried forward by
ADR-0020): content types get Standards tracking plus exemplar reads; reach-side (MCP
servers) gets capped exemplars, never censuses; `hook` is the port mechanisms arrive
through; `config-pack` is graded by payload (ECC: mechanism-grade).

## The bucket's boundary — discussion record (2026-08-19/20; decided 2026-08-22)

*(A running record of a live taxonomy discussion, checkpointed 2026-08-20 mid-stream.
The thread closed 2026-08-22 in two decisions: cuts 1–2 and the coverage strata were
decided as [ADR-0019](../../adrs/0019-category-5-coverage-strata.md); the same day the
owner decided [ADR-0020](../../adrs/0020-memory-category-extensions-renumbered.md),
promoting the mechanism stratum's core — the memory type — to category 5 and
renumbering this bucket to 6. Cut 3, the absorption bet, is registered as principle X3
in [design-principles.md](../../design-principles.md). The cuts' text below stays as
the primary record both ADRs condense; it predates the split, so "category 5" below
reads as "this bucket".)*

The thread started as "should the bucket narrow to memory?" (rejected as arc-sample
bias, [ADR-0016](../../adrs/0016-extensions-stay-broad.md), later superseded by
ADR-0020's owner decision) and produced three sharper cuts, each surviving a test the
previous one failed:

**1. Configure vs reach — the world-side bound.** The membership test ("can you install
it?") under-specifies: ripgrep is authored, versioned, and installed independently of any
harness, and obviously isn't stack. Having a shell doesn't make every CLI tool stack;
having a web client doesn't make every website stack; **having an MCP client doesn't make
every MCP server stack**. The population reachable through a generic channel (shell,
browser, MCP) is the world. What survives: artifacts that **configure** the agent
(context-side or loop-side — remove one and the agent behaves differently on the same
task) are stack; things the agent merely **reaches** through an unchanged interface are
world. Wrinkle worth keeping: MCP servers are partially authored in prompt-space (tool
descriptions are instructions to a model, responses shaped for context windows) — they're
*agent-native world*, which explains why they feel stack-adjacent and makes the census
temptation stronger, not more legitimate. Consequence: reach-side entries are capped at
**exemplars** read to answer registered questions (the live one: conclusion 3 rests on
"MCP settled" and no server has ever been read), never censuses. The 2026-08-19
candidates rows are those designated exemplars, not the start of coverage.

**2. Mechanism vs content — inside the configure side.** Proposed 2026-08-20: maybe
memory tools are the only extensions that add a *harness-native mechanism*, which would
explain why exactly they are being absorbed natively (the `learning_loop` column).
Tested against the tracked set: skills, rules files, subagent defs, MCP servers are all
**slot-fillers** — content for loaders the harness already ships. Memory extensions are
**mechanism-adders** — they add write paths, consolidation loops, cross-session state
(the displacement finding is mechanism-level competition: mem0's plugin blocks the
harness's native memory writes). **The "only memory" version is falsified by one case,
which sharpens rather than kills it**: ECC ships a learning pipeline (third verified
`learning_loop` instance) and enforcement gates ("gates can arrive as installable Stop
hooks" — the registry's ECC finding), so the mechanism-adder stratum is memory + gate/
learning runtimes, and **hooks are the generic port mechanisms arrive through** (the
memory tools themselves install via hooks). *(This cut is what ADR-0020 promoted: the
mechanism stratum's core became category 5 — Memory. ECC, the gate/learning-runtime
case, stays here as the bucket's mechanism-grade config-pack.)*

**3. The absorption hypothesis (registered as a falsifiable bet, not yet a conclusion).**
Harnesses absorb *mechanisms* (gates, memory — both now verified native in multiple
harnesses), *bundle* content (Warp ships 13 skills; the loader was always category 2),
and never absorb reach. Independent mechanism extensions survive absorption on the one
bet a single harness cannot absorb — cross-harness continuity (conclusion 8's
counter-current). Predictions that would falsify the frame: a harness absorbing a
slot-filler *as a mechanism*; a mechanism-adder thriving long-term on a single-harness
bet; a reach-side artifact being absorbed rather than bundled.

**ECC re-tested against the new cuts (2026-08-20).** The question "isn't ECC a workflow
framework?" re-asked; the preregistered category verdict holds and the new vocabulary
strengthens it: ECC ships mechanisms (instinct pipeline, gates) and content (the
catalog); a category-4 member ships *methodology* — a prescribed spine — which is
exactly what the source lacks (opt-in catalog, `workflows/` with one file, orchestration
outsourced to the external `ccg-workflow` runtime). Same knife as conclusion 8's
boundary: mechanisms get absorbed, methodology stays category 4's own. The open lead:
**`ccg-workflow` is the bmad-loop shape** — the process spine sold separately — and
deserves its own category-4 candidates row if it has a real spine.

**Open threads for the next dig:** does `ccg-workflow` have a spine (category-4
sighting)? · the playwright-mcp exemplar read with adapter-vs-capability as its headline
question (if even the strongest capability-server specimen turns out shim-like, the
deflationary view sweeps the type) · do subagent-def packs that encode *process*
(wshobson-style role teams) leak across the mechanism/content line? · are hook packs a
type at all, or only the port other mechanisms ride (the 2026-08-19 sighting found no
large installable pack — the absence is dated in the [candidates ledger](../candidates.md))?

## Why this is a category and not a pile of harness features

An MCP server is built once and consumed by every major harness. Nothing about it belongs
to a particular agent loop. The same is *aspirationally* true of skills and rules files.

The counter-argument worth holding: hooks and subagent definitions are harness-specific
today, so this category is only partly portable — arguably it's "MCP plus a pile of vendor
features" wearing a category's clothes. Whether that resolves depends on standards adoption,
which is tracked in [`../standards/`](../cross-cutting/standards.md) rather than here.

## Reports

| Tool | Depth | One-line |
|---|---|---|
| [**ECC** (everything-claude-code)](ecc.md) | deep-dive (2026-07-30) | 236k stars in ~6.5 months; reclassified from provisional category 4, renumbered 5 → 6 at the split — a config pack at scale (281 skills, 67 agents, rules, enforcement hooks) plus a **harness-independent autonomous learning loop** (hook-observed "instincts", traced in source; the first of what are now four such instances across categories 5 and 6). Solo-author; commercial ring (Pro, GitHub App); `ecc2` Rust control plane growing toward category 2. |

## The distinction that matters

- **category 6 governs reach** — what the agent can access.
- **category 4 governs process** — what it does with that access.
- **category 5 governs continuity** — what survives the session (split out 2026-08-22).

A tool that adds a database connection is category 6. A tool that says "write the spec
before you touch the database" is category 4. ECC is the case that proved the
reach/process distinction cuts cleanly even at 236k stars: enormous reach, deliberately
no prescribed process — see the verdict section of [`ecc.md`](ecc.md).

## Open questions

*Questions about the specifications themselves live in
[`../standards/`](../cross-cutting/standards.md). These are about the installable artifacts.*

- Hooks are the only deterministic escape hatch in an otherwise probabilistic system —
  the harness executes them, so they always fire. How much of a workflow *should* be moved
  into them, and what's lost when you do?
- Subagent definitions isolate context, but each spawn pays a cold-start cost in tokens and
  re-derived understanding. When does isolation actually beat a single longer context?
- Skills load on demand rather than up front. Does just-in-time loading measurably beat a
  fat rules file, or does it just move the same tokens around?
- Is there a real difference between a skill and a well-written section of a rules file,
  other than *when* it enters the context?
