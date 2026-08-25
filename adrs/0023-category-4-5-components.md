# ADR-0023 — Components for categories 4 and 5; tracing discipline goes category-generic

`decided: 2026-08-25` · status: **accepted**

## Decision

The component treatment ADR-0021 gave category 2 extends to the remaining non-bucket
categories, asymmetrically — matching what the record already holds:

- **Category 4 (Workflow frameworks): the four functions ARE the components.** The
  decomposition recorded 2026-08-17 and *tested* by preregistered experiments
  (conclusion 6, upheld with a model-tier caveat by exp-03) is not re-derived — it
  gains the ADR-0021 treatment on top: an agent-shaped question per function, and the
  key-sort validity test. The sort produces a finding rather than a clean partition:
  `intent_pipeline` → F1/F2, `format_gates` + `measured_gates` → F4,
  `process_gates` → the human boundary itself, `retrospectives` → F3-adjacent — but
  `context_isolation`, `parallel_orchestration`, and `state_store` sort onto an
  **execution substrate outside the four functions**. That substrate is exactly the
  stratum the category-2 absorption table shows harnesses absorbing natively, while
  the unabsorbed remainder is the F1/F2 artifact spine plus format gates. The
  decomposition *predicts* the absorption boundary — the same validity standard that
  carried ADR-0021.
- **Category 5 (Memory): three pipeline components — capture · consolidation ·
  recall** — lifted from the category's own definition sentence ("fed by hooks/MCP
  during a session, consolidated between sessions, injected back at the next session
  start"). Each is an agent-shaped question with a source-traced anchor:
  1. **Capture** — *what enters the store, and who admitted it?* Anchors: the
     `capture_path` axis (hook / adapter / agent-invoked, no two vendors alike),
     mem0's native-write displacement (conclusion 8's counter-current),
     `write_admission` (added after exp-04 arm C).
  2. **Consolidation** — *what happens to it between sessions, and does that run by
     default?* Anchors: the store wager (files-git / vector / rows+vector /
     graph+vector+rows — the identity axis), memos' presence≠operative finding (the
     entire evolution half shipped dark behind a default-off flag), `memory_revision`.
  3. **Recall** — *what reaches the next session's prompt — pushed or pulled, framed
     as data or as authority?* Anchors: exp-04's pull-shaped measurement
     (conclusion 14: automatic floor 0/10, pull ceiling 10/10, harness boundary free
     on the pull path), `injection_trust_boundary`, the openclaw recall-protocol
     inversion.
  **Trust is deliberately not a fourth component**: it is each component's boundary
  sub-question — admission at write, revision authority in the middle, injection
  framing at read.
- **Key-sort validity, category 5**: all 13 `memory_features` keys sort —
  `capture_path`, `write_admission` → capture; `memory_store`, `memory_tiers`,
  `memory_scope`, `decay`, `deployment_mode`, `memory_revision`, `rule_extraction` →
  consolidation; `recall_injection`, `hybrid_retrieval`, `injection_trust_boundary` →
  recall; and **`harness_installer` is the aperture analog** — the shim/installer is
  to a memory product what the kind-linked keys are to the harness (ADR-0021's
  "extensibility is the aperture"), the pluggable seam rather than a component.
- **The tracing discipline goes category-generic**: `deep-dive` now means the
  category's component decomposition actually traced, with the report declaring which
  components — categories 2, 4, and 5 define components in taxonomy.md; category 3's
  blast-radius/fidelity/parallelism questions serve the same role. The 2026-08-25
  decoder clause from the ADR-0021 reconciliation is unchanged (earlier deep-dives
  read under the loop+context definition).

## Why, honestly

Category 4's treatment is augmentation because discarding measured structure to chase
symmetry would be vandalism — the four functions are the only decomposition in this
repo that preregistered experiments have tested. Category 5's is creation, but from
found material: the pipeline was already the category's one-sentence definition, the
matrix's identity axes (store wager, capture path, recall injection, trust boundary)
were already views of it, and the template's depth note had already improvised
"capture, store, recall" as the memory translation of the harness components — this
ADR replaces that improvisation with a decided form. The validity test did real work
in both categories: for 4 it exposed the substrate remainder and its coincidence with
the absorption boundary; for 5 it placed `harness_installer` outside the pipeline,
which is what makes the aperture analogy exact.

## Considered and not taken

- **A fifth category-4 "execution substrate" component.** The substrate is what
  harnesses absorb (session-scoped state, isolation, fan-out are native machinery in
  the tracked set); naming it a component of category 4 would classify borrowed ground
  as owned. It is recorded as a named remainder with the conclusion-8 tie instead.
- **Trust as a fourth category-5 component.** Its keys split across the pipeline
  (write_admission at capture, memory_revision at consolidation,
  injection_trust_boundary at recall); a component whose evidence lives inside the
  other three is a label, not a tracing unit.
- **Matrix axes as the components.** The first-cut axes are measurement columns —
  what the matrix compares; components are tracing units — what a deep-dive follows
  through source. The axes remain the matrix's organizing view.
