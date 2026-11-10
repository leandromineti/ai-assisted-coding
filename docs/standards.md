# Standards — not a category

`checked: 2026-11-10`

Specifications, not installable things. A standard has no category of its own; it is recorded
here once and referenced from the categories that implement it. See
[`tool-taxonomy.md`](tool-taxonomy.md).

This category exists because the taxonomy's stress test broke on MCP: it has no defensible
home in the stack, because *the protocol* and *the servers that speak it* are different
kinds of object. The servers are category 6. The protocol is this.

**The general test:** can you install it? If yes, it's a category entry. If it's a document
that other people implement, it belongs here.

**How to read the scoreboard below (sharpened 2026-08-17, owner's formulation):**
portability is not an intrinsic property of an extension — it is a status the
ecosystem *confers by adoption*, and this page tracks the conferral, not the design.
The bucket's own members prove the mechanism: hooks are the control group (same kind
of artifact, no second adopter, no portability); rules files gained portability the
day a rival vendor chose to link competitors' formats (the artifact unchanged, the
market moved — Warp, 2026-08-11); MCP is the limit case, portability by
standardization. This is why conclusion 3 carries a re-check date: conferred
statuses can be conferred further, or withdrawn.

---

## MCP — Model Context Protocol

An open protocol for exposing external systems (filesystems, APIs, databases, browsers,
SaaS) to agents as callable tools.

**Implemented by:** Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode, and
Devin — i.e. every major harness. One server, set up once, works across all of them.

**Why it matters structurally:** MCP is the only part of category 6 that has fully cleared the
independent-distribution bar. It's the existence proof that capability extensions can be a
real category rather than a bag of per-harness features. Everything else in category 6 is
measured against how close it gets to this.

**Open questions**

- Does the portability hold up in practice, or do servers quietly depend on one harness's
  tool-calling quirks — so that "works everywhere" means "was tested against one client"?
- Universal adoption arrived fast. Is that convergence on a good design, or on the only
  design that existed at the moment everyone needed one?
- What does MCP *not* model well? The gaps are where the next standard comes from.

---

## `AGENTS.md` / `CLAUDE.md` — rules-file conventions

Standing instructions injected into an agent's context: project conventions, commands,
constraints.

Not a protocol but a **filename convention**, which is a much weaker form of standard —
there's no schema to conform to and no way to be non-compliant. `AGENTS.md` appears to be
converging into the cross-harness spelling, with `CLAUDE.md` and `.cursorrules` as
vendor-specific predecessors.

The *files* are category 6 artifacts; the *convention* is what lives here.

**Rival-implementation evidence (2026-08-11, Warp @ `80a20347`).** The strongest signal yet
that this is a real convention rather than one vendor's habit: Warp reads `WARP.md` *and*
`AGENTS.md` as project rules (`crates/repo_metadata/src/standing_queries.rs:22`) and
`~/.agents/AGENTS.md` as global rules — and its project-init flow defines
`LINKABLE_FILES = [CLAUDE.md, .cursorrules, AGENT.md, GEMINI.md, .clinerules, .windsurfrules,
.github/copilot-instructions.md]` (`app/src/terminal/view/init_project/mod.rs:50`), seven
competitors' rules files it offers to link into its own. A shipping harness treating rival
vendors' rules files as consumable input is what "converging on `AGENTS.md`" looks like from
the implementer's side, not the spec's. Note what it *doesn't* show: linking is a
concatenation courtesy, so it still tests nothing about schema — the convention remains
weak in exactly the way the open question below says.
[`../2-harnesses/warp.md`](../tools/2-harnesses/warp.md).

**Open questions**

- Is a filename convention enough to be called a standard? It coordinates behavior with no
  specification at all — which is either elegant or a sign the category is too loose.
- Rules files are the cheapest context intervention and the least measured anywhere. What
  is the marginal value of a longer one, and where does it turn negative? (Candidate first
  experiment — see [`README.md`](README.md).)

---

## Agent-permission conventions *(unverified)*

How agents declare and request what they're allowed to do — file writes, network access,
shell execution. Conventions appear to be emerging here, but nothing was confirmed as a
named standard at check date. Recorded as a placeholder, deliberately, so the gap stays
visible.

---

## The convergence thesis

This is the prediction the standards category is really for, and it's testable:

> If skills and rules files converge on standards the way MCP did, category 6 solidifies as a
> genuine category. If they don't, part of it collapses back into category 2 as per-harness
> features.

Current state of the evidence:

| Category-6 type | Standardized? | Trend |
|---|---|---|
| MCP servers | Yes — full protocol, universal adoption | Settled |
| Rules files | Weakly — filename convention only | Converging on `AGENTS.md` |
| Skills | **Emerging** — `SKILL.md` consumed by ≥5 harnesses (2026-07-28 evidence below; Warp added 2026-08-11) | Converging |
| Hooks | No — harness-specific. Best fragmentation evidence to date: ai-memory deep-dive (2026-08-18), a vendor that must consume ~15 harnesses' hook surfaces — event vocabularies differ per harness (Devin ships PostCompaction not PreCompact; Zero execs without a shell), lifecycle coverage differs (Codex and Antigravity lack a true session-end; Antigravity lacks SessionStart), and *semantics* differ for the same event (Kimi Code discards SessionStart stdout and fires PostToolUse only on success; Claude Code wants JSON stdout). Each quirk is worked around in per-harness installer code. *Amended 2026-11-10 (the 2026-11 memory reads): the fragmentation evidence is no longer one vendor's. ai-memory, re-measured at v3.3.3: 40 documented harness targets by the report's counting rule over `docs/support-matrix.md` (23 at v2.0.2 by the same rule), against the "~15" above ([ai-memory](../tools/5-memory/ai-memory.md), frontmatter `harness_targets`). OpenViking: one shared installer for 12 harness products plus two attached by their own setup writers, 14 in all, with a pre-compaction boundary on 9 of the 12 ([OpenViking](../tools/5-memory/openviking.md), `harness_targets` and `compaction_capture`). MemPalace: 5 plugin bundles plus Hermes and OpenClaw, 7 harnesses, three hook payload shapes, and a PreCompact whose documentation describes a blocking design that the code does not wire, a docs-versus-code drift ([MemPalace](../tools/5-memory/mempalace.md), `harness_targets` and § Hooks and the PreCompact handler). agentmemory: 22 `connect` adapters, registration files that differ in event count per harness (12 events for Claude Code, 6 for Codex, 5 for Factory Droid, 4 for Antigravity), and a PreCompact hook whose recalled-context output Claude Code sends to its debug log and not to the model, per Claude Code's own documentation (TESTIMONY; [agentmemory](../tools/5-memory/agentmemory.md), § Capture and § Recall)* | **First movement, 2026-08-24 — and it is bridging, not standardization**: dsh executes *unmodified* Claude Code `hooks.json` (7 events, matchers, `${CLAUDE_PLUGIN_ROOT}` substitution) and Codex's snake_case dialect via bridge plugins (`packages/hooks/hooks-{claude-code,codex}`, shipped but mounted in no bundle) — the first cross-vendor consumer of a hooks format ([dsh deep-dive](../tools/2-harnesses/dsh.md)). Adoption of one vendor's format by a rival is how `AGENTS.md` started; watch whether a second consumer follows |
| Subagent definitions | No — harness-specific format, universal pattern | Watch |

**Memory watch note (row moved 2026-08-22, ADR-0020 — memory is now category 5, not a
type of this bucket; the standards question follows it unchanged):** seven vendors,
zero shared formats (2026-08-18): each of ai-memory/mem0/cognee/memori/everos/memos/
memmachine defines its own store, capture path, and injection mechanism; the only
shared surfaces are the carriers (MCP, hooks, `SKILL.md`). The fragmentation cost is
paid per-vendor in code (~7.8k lines of per-harness installer in ai-memory alone), and
the only cross-vendor data flow found in four reads is one-way competitive import
(mem0's migration script) — an acquisition funnel, not interchange. **A
memory-interchange convention would be the next MCP-shaped event** — watched from here,
reported in [category 5](../tools/5-memory/README.md).

**Amended 2026-11-10 (the 2026-11 memory reads: ai-memory v3.3.3, OpenViking v0.5.3, MemPalace v3.11.0, agentmemory v0.9.31, and the 2026-11-06 census at the existing pins):**
"zero shared formats" no longer holds as written; the paragraph above stands as the
2026-08-18 count. **Formats.** Eight tools carry a source read of the question (measure: the
2026-11-06 census in the [category 5 README](../tools/5-memory/README.md), one verdict per
tool on whether its source at the pin names the Open Knowledge Format (OKF) as a format it
writes, reads or declares), and two do. *One verified OKF-native instance, ai-memory:* it
targets OKF v0.2 and ships `export-okf`; the export is conformant (observed on a three-file
bundle from the probe), and the on-disk tree is not by the spec's letter, because the
per-month event ledgers (`log-YYYY-MM.md`) carry no frontmatter and the spec reserves only
`index.md` and `log.md` ([ai-memory](../tools/5-memory/ai-memory.md), § Re-traces at v3.3.3,
OKF spec skew). *One OKF-shaped declaration, openviking:* its `OKF_VERSION = "0.1"` is a house
version string that cites no spec, is emitted in an API result and never in a bundle, and has
no conformance gate: a declaration, not conformance ([OpenViking](../tools/5-memory/openviking.md),
§ OKF conformance checklist). *The spec skew:* ai-memory cites the frozen copy,
`GoogleCloudPlatform/knowledge-catalog` (`okf/SPEC.md`, "verified 2026-09-01"), whose own
README calls that copy frozen and unmaintained, while the live specification is
`GoogleCloudPlatform/open-knowledge-format`; read on 2026-11-05 the two files were
byte-identical, so the skew is one of location today and not of content, and the standing
risk is the next spec revision (TESTIMONY: the remote read was not kept). The `knowledge-catalog/okf`
citation is therefore the vendor's and not a second adopter's. The other six tools print
nothing for the term at their pins (a control search in each report), and everos and
memmachine are stubs with no read. **Import (qualified 2026-11-10).** "The only cross-vendor data flow found in four
reads" is superseded as a count, not as a reading. Cognee ships four competitor-store
importers (`langmem.py`, `letta.py`, `mem0.py`, `zep.py`) beside COGX, its own archive format,
which is a house format and is named and not counted ([cognee](../tools/5-memory/cognee.md),
`memory_import`); MemPalace reads ten transcript and export schemas and publishes no
interchange format of its own ([MemPalace](../tools/5-memory/mempalace.md), § Importing
memory born elsewhere); agentmemory has one importer, for Claude Code JSONL
([agentmemory](../tools/5-memory/agentmemory.md), `memory_import`); OpenViking replays eight
harness-log sources and has no rival-store importer in its searched surface
([OpenViking](../tools/5-memory/openviking.md), `memory_import`). Each of these reads another
tool's output and none is interchange, so the "acquisition funnel, not interchange" reading
holds for each one traced. **Installer cost (re-measured 2026-11-10).** The "~7.8k lines of per-harness installer in
ai-memory alone" was the figure at the 2026-08-18 read (7,801 lines at that pin); at v3.3.3
`install_hooks.rs` is 18,351 lines (measure: `git show <rev>:crates/ai-memory-cli/src/commands/install_hooks.rs | wc -l`,
9,875 at v2.0.2; [ai-memory](../tools/5-memory/ai-memory.md), § Release assessment, scored
predictions), and the Hooks row above carries the other three vendors' installer evidence.
The category's own count of these cells and the census behind them are in the
[category 5 README](../tools/5-memory/README.md); the watch stays open, and a second
conformant OKF adopter on the roster is the event that would change the count above.

**Skills evidence (2026-07-28, from spec-kit's integration registry @ `655a3cb`):** a
third party that must *install into* every harness is a good witness for what harnesses
actually consume, and spec-kit's registry renders commands as `SKILL.md` for Claude Code
and Codex (its `SkillsIntegration` subclasses), treats Kimi as a *native* skills
integration, targets Hermes at `~/.hermes/skills`, and handles a shared `.agents/skills`
directory that multiple integrations resolve to. Like rules files, this is
convention-level (a filename + frontmatter shape, no schema) — but it's no longer
Claude-Code-shaped. See
[`../4-workflow-frameworks/spec-kit.md`](../tools/4-workflow-frameworks/spec-kit.md).

*Installer-side evidence (2026-08-16, OpenSpec drift check @ `d578896`):* OpenSpec moved
**Codex's** skills directory from `.codex` to **`.agents`**, demoting `.codex` to
`legacySkillsDirs` while still detecting both — the commit is titled "install skills in
canonical agents directory" (#1511). A third-party installer relocating a *vendor's* skills
into the shared `.agents/` tree, and calling that location canonical, is the convergence
happening in the direction that matters: not a new tool adopting the convention, but an
existing vendor-specific path being retired in favour of it. Watch whether `.codex` is
eventually dropped rather than kept as legacy — that is when the convention has actually
won. [`../4-workflow-frameworks/openspec.md`](../tools/4-workflow-frameworks/openspec.md).

*Direct-consumer evidence (2026-08-11):* Warp implements the format natively —
`crates/ai/src/skills/` parses `SKILL.md`, resolves scoped skill directories with a
`WARP_SKILL_DIRS` override, and ships 13 bundled skills of its own. That's a first-party
implementation by a non-Anthropic vendor, which is a stronger witness than a third-party
installer targeting it. [`../2-harnesses/warp.md`](../tools/2-harnesses/warp.md).

Two and a half of five have moved (the half being skills, at 2026-07-28). That's the
number to re-check in six months: if hooks are still harness-specific and skills stall at
convention level, category 6 is really "MCP plus a pile of vendor features," and the
taxonomy should say so.
