---
name: conductor
layer: 4
vendor: Google (gemini-cli-extensions org)
url: https://github.com/gemini-cli-extensions/conductor
license: Apache-2.0
open_source: true
stack: [Markdown]
version: conductor-v0.4.1-16-gf06add3
commit: f06add3
first_commit: 2025-12-17
stars: 3704
stars_at: 2026-08-18
read_at: 2026-08-18
depth: stub   # facts from repo-facts.sh + full README; rules/skills prose unread
harness_targets: [Antigravity, Claude Code]
workflow_features:   # added 2026-08-18; stub — but absences here are tree-verified (28 files)
  intent_pipeline: true          # Context → Spec & Plan → Implement
  deterministic_engine: false    # nothing to run: 22 md files + plugin.json IS the framework
  format_gates: false            # follows — no machinery to check formats with
  state_store: repo-files        # "context as a managed artifact alongside your code" (README)
---

# Conductor

## What it is

Google-org SDD plugin — "measure twice, code once." A strict protocol (Context →
Spec & Plan → Implement) that turns the agent into "a proactive project manager,"
treating context as a managed artifact alongside code. Installs as a standard agent
plugin: `agy plugins install` for Antigravity, marketplace install for Claude Code
(README installation sections; `plugin.json` names it "Conductor Agent Skills").

## Notes for the layer-4 comparison

The smallest layer-4 subject by an order of magnitude: **28 tracked files, 22 of them
markdown** — the entire framework is prose (rules/ + skills/) plus a 2-line
`plugin.json`. That makes it the purest test subject available for the
conclusion-7 question (prose-only methodology, zero deterministic engine): where
OpenSpec is workflow-as-schema interpreted by a DAG engine, Conductor is
workflow-as-instructions, full stop. Two verified harness targets — passes layer-4
portability, but the narrowest pass in the set.

## Stack & repo shape

md(22) json(2) py(1); 131 commits since 2025-12. No manifests beyond `plugin.json`,
no build, no runtime. Apache-2.0.

## My take

*(empty — not yet used; stub honesty)*
