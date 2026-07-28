# Standards — not a layer

`checked: 2026-07-28`

Specifications, not installable things. A standard has no layer of its own; it is recorded
here once and referenced from the layers that implement it. See
[`../../taxonomy.md`](../../taxonomy.md).

This category exists because the taxonomy's stress test broke on MCP: it has no defensible
home in the stack, because *the protocol* and *the servers that speak it* are different
kinds of object. The servers are layer 3. The protocol is this.

**The general test:** can you install it? If yes, it's a layer entry. If it's a document
that other people implement, it belongs here.

---

## MCP — Model Context Protocol

An open protocol for exposing external systems (filesystems, APIs, databases, browsers,
SaaS) to agents as callable tools.

**Implemented by:** Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode, and
Devin — i.e. every major harness. One server, set up once, works across all of them.

**Why it matters structurally:** MCP is the only part of layer 3 that has fully cleared the
independent-distribution bar. It's the existence proof that capability extensions can be a
real layer rather than a bag of per-harness features. Everything else in layer 3 is
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

The *files* are layer 3 artifacts; the *convention* is what lives here.

**Open questions**

- Is a filename convention enough to be called a standard? It coordinates behavior with no
  specification at all — which is either elegant or a sign the category is too loose.
- Rules files are the cheapest context intervention and the least measured anywhere. What
  is the marginal value of a longer one, and where does it turn negative? (Candidate first
  experiment — see [`../cross-cutting/index.md`](../cross-cutting/index.md).)

---

## Agent-permission conventions *(unverified)*

How agents declare and request what they're allowed to do — file writes, network access,
shell execution. Conventions appear to be emerging here, but nothing was confirmed as a
named standard at check date. Recorded as a placeholder, deliberately, so the gap stays
visible.

---

## The convergence thesis

This is the prediction the standards category is really for, and it's testable:

> If skills and rules files converge on standards the way MCP did, layer 3 solidifies as a
> genuine layer. If they don't, part of it collapses back into layer 2 as per-harness
> features.

Current state of the evidence:

| Layer-3 kind | Standardized? | Trend |
|---|---|---|
| MCP servers | Yes — full protocol, universal adoption | Settled |
| Rules files | Weakly — filename convention only | Converging on `AGENTS.md` |
| Skills | **Emerging** — `SKILL.md` consumed by ≥4 harnesses (evidence below, 2026-07-28) | Converging |
| Hooks | No — harness-specific | No sign of movement |
| Subagent definitions | No — harness-specific format, universal pattern | Watch |

**Skills evidence (2026-07-28, from spec-kit's integration registry @ `655a3cb`):** a
third party that must *install into* every harness is a good witness for what harnesses
actually consume, and spec-kit's registry renders commands as `SKILL.md` for Claude Code
and Codex (its `SkillsIntegration` subclasses), treats Kimi as a *native* skills
integration, targets Hermes at `~/.hermes/skills`, and handles a shared `.agents/skills`
directory that multiple integrations resolve to. Like rules files, this is
convention-level (a filename + frontmatter shape, no schema) — but it's no longer
Claude-Code-shaped. See
[`../04-workflow-frameworks/spec-kit.md`](../04-workflow-frameworks/spec-kit.md).

Two and a half of five have moved (the half being skills, at 2026-07-28). That's the
number to re-check in six months: if hooks are still harness-specific and skills stall at
convention level, layer 3 is really "MCP plus a pile of vendor features," and the
taxonomy should say so.
