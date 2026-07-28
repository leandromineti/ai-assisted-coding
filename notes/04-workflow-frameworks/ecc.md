---
name: ecc
layer: 4   # provisional — see the classification question below; layer-3 config pack is the live alternative
vendor: Affaan Mustafa (affaan-m)
url: https://github.com/affaan-m/ECC
license: MIT
open_source: true
stack: [Markdown, Node]
version: v2.1.0-11-g4e973d3e
commit: 4e973d3e
first_commit: 2026-01-17
stars: 234750
stars_at: 2026-07-28
read_at: 2026-07-28
depth: stub
---

# ECC — everything-claude-code

Self-described "agent harness performance optimization system": skills, "instincts",
memory, security scanning, and research-first development for Claude Code, Codex,
OpenCode, Cursor "and beyond". Started as a personal Claude Code config dump
("everything-claude-code", later renamed ECC) and became **the fastest-adopted tool in
this study set: 234,750 stars in ~6 months** — larger than opencode (190k), spec-kit
(124k), and every harness here except the closed ones.

## The layer question (why this stub exists)

ECC is filed on layer 4 **provisionally, as a boundary test**. The layer-4 test is an
encoded *methodology* — an operating loop — portable across harnesses. ECC may instead
be a layer-3 **config pack at scale**: a bundle of skills/agents/hooks/rules with no
process spine. The source read should answer: is there a prescribed loop (like GSD's
plan→execute→verify or spec-kit's specify→plan→tasks→implement), or a toolbox you reach
into? If the latter, it moves shelves — and either way it stress-tests the taxonomy,
which is worth more than the classification.

Its headline mechanisms — **"instincts", memory, continuous learning** — have no column
in the layer-4 mechanism table. If they survive a source read as real mechanisms (rather
than branding over rules files), the table grows a column; that's the other reason this
stub earns its place.

## The distinguishing bet

*(Inferred from positioning; source unread.)* That harness-level configuration —
accumulated skills, learned rules, memory hygiene — is where agent performance actually
lives; less "follow this process" (GSD/spec-kit) and more "install these reflexes."

## Main features

_TODO — source unread. Marketing claims ~60 agents / 230 skills / 75 command shims; none
verified._

## Stack & repo shape

2,506 `.md` against 432 `.js` and 63 `.py` across 3,377 tracked files — the most extreme
markdown-majority in the set, plus a Rust component (`ecc2/Cargo.toml`) and an OpenCode
package (`.opencode/package.json`). 2,331 commits since 2026-01-17 (~390/month).
CONTRIBUTING is localized into es, ja-JP, ko-KR, pt-BR — the same localization
investment gsd-core makes, unusual for the set.

## Architecture

_TODO — source unread. Key question: how does one repo target Claude Code, Codex,
OpenCode, and Cursor — a spec-kit-style compile step, per-harness duplicates, or
symlinked convention dirs?_

## Bleed

_Unverified. The Rust `ecc2/` component suggests a runtime being grown (the layer-2
bleed pattern seen in spec-kit's workflow engine and GSD's gsd-pi) — to confirm._

## Cost model

Free and open source (MIT). Inference cost unknown; "memory optimization" and
"selective-install" features suggest context cost is a design concern.

## Surprises

_Source unread._

## Open questions

- Layer 3 or layer 4? (See above — the answer recalibrates the taxonomy either way.)
- What is an "instinct", concretely, in the source? Rules file, generated hook, or
  something genuinely new?
- 235k stars in six months — what need is being met? Methodology, or the ready-made
  config people don't want to author themselves? The answer says a lot about what the
  market thinks the bottleneck is.
