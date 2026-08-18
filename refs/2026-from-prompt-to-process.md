---
key: 2026-from-prompt-to-process
title: "From Prompt to Process: a Process Taxonomy and Comparative Assessment of Frameworks Supporting AI Software Development Agents"
authors: [Sanderson Oliveira de Macedo]
year: 2026
venue: arXiv preprint
peer_reviewed: false
arxiv: 2606.04967
citations: "0 (0 influential) — Semantic Scholar"
citations_at: 2026-08-18
url: https://arxiv.org/abs/2606.04967
kind: survey
read_depth: full
retrieved: 2026-07-31
pdf: refs/pdf/2026-from-prompt-to-process.pdf
bears_on: [conclusion-7, conclusion-6, taxonomy, gsd-core, spec-kit, openspec, bmad-method, methodology-8]
verdict: "independent convergence on conclusion 7 from docs only — and its GSD validation score of 0 is contradicted by our exp-01 run, which is rule 8 earning its keep"
---

# From Prompt to Process

`retrieved: 2026-07-31` · `read_depth: full` (pages 1–15 of 17; 16–17 are references) ·
[arXiv:2606.04967](https://arxiv.org/abs/2606.04967), v1 dated 3 Jun 2026

## What it does

Proposes a **six-dimension process taxonomy** for frameworks that run *over* a coding agent —
specification, context, roles, execution, validation, portability (§4, Table 4) — turns it
into a 0/1/2 scoring rubric, and applies it to six frameworks selected by an explicit
inclusion + traction filter. Same subject as this repo's layer 4, arrived at independently.

## Design

- **Selection is auditable** (§2), which is the paper's methodological strength: a four-part
  functional inclusion criterion (must support process, must sit over an agent the developer
  already runs, must not *be* the agent/IDE, must not be an agent-building SDK), then a
  traction filter of ≥1000 GitHub stars + a push within six months, measured via the GitHub
  API 26–28 May 2026 and snapshotted to a CSV in their repo.
- **Final set:** GitHub Spec Kit, OpenSpec, BMAD Method, Get Shit Done (GSD), Spec Kitty,
  Reversa. Excluded: `claude-code-spec-workflow` (inactive since 2025-09), Spec-Flow (85
  stars), Tessl (commercial).
- **Characterisation is from official documentation and repositories only** — the paper is
  explicit that it did not run anything (§2, §5).
- **Out-of-sample check:** applies the rubric to Spec-Flow, deliberately excluded for low
  traction, which then scores the *most* complete profile in the paper (11/12) despite 85
  stars (§6).

## Numbers worth keeping

Table 1 traction snapshot (GitHub, May 2026): Spec Kit 106,786 · GSD 63,754 · OpenSpec
51,404 · BMAD 48,209 · Spec Kitty 1,273 · Reversa 1,100.

Table 6 — dimensional assessment (0 absent/incipient · 1 partial · 2 strong/central):

| Framework | Spec | Ctx | Roles | Exec | Valid | Port | Total |
|---|---|---|---|---|---|---|---|
| GitHub Spec Kit | 2 | 1 | 1 | 1 | 1 | **2** | 8 |
| OpenSpec | 2 | 1 | 0 | 1 | 0 | **2** | 6 |
| BMAD Method | 2 | 2 | 2 | 1 | 2 | 1 | **10** |
| **Get Shit Done (GSD)** | 1 | **2** | 0 | 1 | **0** | **0** | **4** |
| Spec Kitty | 2 | 1 | 1 | 2 | 2 | 1 | 9 |
| Reversa | 2 | 2 | 0 | 0 | 1 | 1 | 6 |

Stated finding (§6): **no framework scores 2 across all six dimensions.** Specification is
nearly saturated and therefore discriminates little; **roles and validation are the most
polarised**, so they discriminate most. The most portable frameworks (Spec Kit, OpenSpec)
sacrifice roles and validation; the deepest process (BMAD) gives up portability; the most
context-centric (GSD) zeroes roles, validation *and* portability.

*(2026-08-18, post BMAD deep-dive: the BMAD Port=1 score is the second place our source
read contradicts this paper's docs-only reading — BMAD has the widest target list in the
layer (47 platform codes), achieved by refusing translation entirely (byte-identical
Agent Skills to every target). Its Valid=2 also deserves the ADR-0011 asterisk: every
framework-side gate is prose; the engine-graded gates live in the separate bmad-loop
orchestrator, outside the framework the paper scored —
[report](../notes/04-workflow-frameworks/bmad-method.md).)*

## What it means for this repo

**1. Independent convergence on conclusion 7.** "There is a structural trade-off between
process depth and portability" (§3, §6) is conclusion 7's claim, reached from documentation
where ours came from reading spec-kit's git history. Two different methods, same shape — that
strengthens it, and the paper should be cited in conclusion 7 rather than leaving ours
looking original.

**2. Its GSD validation score of 0 is contradicted by our own run — and this is rule 8
earning its keep.** The paper scores GSD **0 on validation** and 1 on specification from its
documentation. Our exp-01 *ran* gsd-core and found the opposite: measured verification gates
were among the two mechanisms carrying nearly all of GSD's quality margin (conclusion 6),
with `VERIFICATION.md` artifacts and verifier agents observable in the run. A docs-only
reading missed a mechanism that running it surfaced. That is exactly what methodology rule 8
("same subject, both directions") predicts, and it is a concrete, publishable correction we
can support with artifacts.

*Caveat before we claim a scalp:* the paper assessed `gsd-build/get-shit-done` (Table 1),
whereas exp-01 ran **gsd-core**, the 2026-05-22 community fork. Different artifact, and the
fork may have added gates the original lacked. The paper does note "a maintenance move to a
new organization" and GSD's "maintenance volatility," but its May 2026 snapshot still lists
the original repo as active, where our
[`gsd-core` report](../notes/04-workflow-frameworks/gsd-core.md) documents the archival and
its cause. Both accounts are dated; ours is more specific.

**3. Our niche is named as a research gap.** §7's process-oriented-benchmark agenda asks for
metrics including "**rate of human review required**," "number of corrections per phase," and
"quality of the audit trail," and says plainly there is "a lack of benchmarks for the complete
process." That is exp-02's attention-split instrument, requested by name. Table 7's
specification question is also a sharper phrasing of our P1: *"Do specs generated by the
framework reduce ambiguities or merely shift ambiguity to another artifact?"*

**4. Adoption ≠ process completeness.** The Spec-Flow out-of-sample result (85 stars, most
complete profile) is a caution for our own `stars` column: it measures adoption, not
capability, and we should not let it order anything.

## Limits

- Preprint; **not peer-reviewed**.
- **Single rater, no inter-rater reliability** — the paper says so, and calls its own scores
  "the authors' judgement from official documentation … not a third-party-validated empirical
  measurement" (§2). Table 6 is a reading of docs, not a measurement of behaviour.
- **Declared conflict of interest:** Reversa, one of the six, is authored by the study's
  author (§2).
- Grey-literature sources carry promotional bias, acknowledged and partly mitigated by
  confronting them with formal literature.
- Traction is a May 2026 snapshot and drifts; the paper says so.
- Nothing was executed, so every dimension score is a claim about documentation. Where we have
  run the framework, our evidence outranks it — and where we haven't, theirs is a useful prior.
