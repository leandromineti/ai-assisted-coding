# Standards — not a category

`checked: 2026-08-25`

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
| Hooks | No — harness-specific. Best fragmentation evidence to date: ai-memory deep-dive (2026-08-18), a vendor that must consume ~15 harnesses' hook surfaces — event vocabularies differ per harness (Devin ships PostCompaction not PreCompact; Zero execs without a shell), lifecycle coverage differs (Codex and Antigravity lack a true session-end; Antigravity lacks SessionStart), and *semantics* differ for the same event (Kimi Code discards SessionStart stdout and fires PostToolUse only on success; Claude Code wants JSON stdout). Each quirk is worked around in per-harness installer code | **First movement, 2026-08-24 — and it is bridging, not standardization**: dsh executes *unmodified* Claude Code `hooks.json` (7 events, matchers, `${CLAUDE_PLUGIN_ROOT}` substitution) and Codex's snake_case dialect via bridge plugins (`packages/hooks/hooks-{claude-code,codex}`, shipped but mounted in no bundle) — the first cross-vendor consumer of a hooks format ([dsh deep-dive](../tools/2-harnesses/dsh.md)). Adoption of one vendor's format by a rival is how `AGENTS.md` started; watch whether a second consumer follows |
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
