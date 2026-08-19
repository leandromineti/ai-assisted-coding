---
name: pilot-shell
category: 4
vendor: Max Ritter
url: https://github.com/maxritter/pilot-shell
license: proprietary   # "Pilot Shell Software License Agreement" — source-available EULA
open_source: false
stack: [TypeScript, Python, React]
version: v10.3.1
commit: c8c8243
first_commit: 2025-10-24
stars: 2019
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + README + LICENSE read; source unread
harness_targets: [Claude Code, Codex]
workflow_features:   # added 2026-08-18; stub — README-level claims only
  intent_pipeline: true          # /prd → /spec → /build
  deterministic_engine: true     # pilot binary + quality-hook runtime
  measured_gates: true           # lint/typecheck/tests enforced as gates; /build judge loops until criterion passes
---

# pilot-shell

## What it is

A spec-driven operating layer for Claude Code and Codex: `/prd` (requirements) →
`/spec` (plan, implement, verify with enforced TDD) → `/build` (autonomous judge loops
until a criterion passes) → `/fix` (TDD bugfix lane with a complexity bail-out), plus
quality hooks (lint/format/typecheck/tests as gates), persistent memory with team
sharing, semantic code search ("Semble"), a code knowledge graph ("CodeGraph"), token
compression ("RTK"), a background automation agent ("Pilot Bot"), and a local web
dashboard. Claude Code is the primary target (full feature coverage); Codex gets all
workflows with fewer platform features. (README at the pin; source unread.)

## Notes for the layer-4 comparison

The open question from the candidates ledger stands: spine or catalog? The command
pipeline is a real process spine, but the surface area around it (console, bot, search,
graph, own `pilot` binary and launcher) is ECC-shaped, and ECC's deep-dive verdict
("config pack with a runtime, not an encoded methodology") is the live precedent. The
licensing is itself a layer-4 datapoint: the only non-OSI subject in the layer — a
source-available EULA (internal use and modification permitted per §2(c); redistribution
and derivative distribution prohibited per §4) with an Enterprise source tier. Cloning
for private research is within §2(c); the clone is gitignored regardless.

## Stack & repo shape

Monorepo: `pilot/` (TS core, package.json), `console/` (React dashboard), `installer/` +
`launcher/` + `install.sh`, `benchmarks/`, Docusaurus docs. ts(485) tsx(203) py(208)
md(279); 1456 commits since 2025-10 — very high velocity for one primary author
(~95% single-author at sighting).

## My take

*(empty — not yet used; stub honesty)*
