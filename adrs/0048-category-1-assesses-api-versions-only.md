# ADR-0048 — category 1 assesses the first-party API-served version only

`decided: 2026-08-27` · status: **accepted**

## Decision

Every category-1 spec and assessed key — `context_window`, `max_output`, `pricing`,
`knowledge_cutoff`, and the whole `model_features` block — describes the **first-party
API-served product**, and only it. Where a model is also published as weights, the weights
release is **acknowledged, never assessed**: its existence and terms are recorded in the
transcription fields (`access`, `license`, the HF repo id inside `model_id`) and its route
in the type-1b table, and that is the whole of the repo's claim about it. Self-hosted
serving — local runtimes, quantization variants, GGUF ecosystems, throughput on owned
hardware — earns no assessment of its own.

Concretely:

- The taxonomy gains a category-1 **Scope note** (mirroring category 3's, the repo's
  existing per-category scope precedent) and a **Deliberate exclusions** bullet.
- The planned **local open-weight throughput arm** ([issue #15]) is **killed, not
  deferred**: the program item, the metrics justification, and the article teasers carry
  dated retirement notes or are removed.
- Open questions across category-1 surfaces that promised self-hosted work are closed by
  scope, dated, in place.

[issue #15]: https://github.com/leandromineti/ai-assisted-coding/issues/15

## Context — one model name, two products, and the vendor said so

The trigger is the Qwen3.8 pair, added the same day
([qwen3.8-max](../tools/1-models/qwen3.8-max.md),
[qwen3.8-flash](../tools/1-models/qwen3.8-flash.md)). Qwen's own weights card for the
flagship states that the published checkpoint is the post-trained model behind the
commercial service and that the API **adds** *"vision input & non-thinking support, 1M
context length by default, official built-in tools"* — while the weights think always, in
`<think>` tags, and cannot be told not to. One model name, two reasoning contracts, two
context windows, two input-modality sets, split by access route — and for once documented
by the vendor rather than discovered.

That broke the framing type 1b had been carrying. Its claim — *"the same model by a
different route is a different product"* — had always meant **serving** variance:
quantization, caching support, rate limits, silent truncation. Qwen3.8-max is **artifact**
variance: the routes are not serving the same thing differently, they are handing you
different things. The day the reports landed, the strain was recorded in the qwen3.8-max
report and the category README as either a boundary case for 1b or a reason to split it.

This ADR resolves the strain **by scoping instead of by splitting**: the assessed subject
of a category-1 report is the API-served product by definition, so the weights variant is
context, not a second subject the type must classify. The owner's driving argument is
economy — *"the API access to them is already complex enough"* — and the repo's record
backs it: the taxonomy already holds that the weights are untraceable at this repo's level
of analysis regardless of release mode (the no-component-decomposition paragraph,
recorded 2026-08-25), the category README's assessed block was already defined as "the
first-party surface around them", and closed subjects cap at `survey` under methodology
rule 1a either way. The practical grounding is also real: no hardware in this repo's orbit
can serve frontier-scale weights — the study machine has no GPU and no KVM, and the three
largest open-weight releases tracked (2.8T, 2.4T, 671B-class) are datacenter-shaped.

## Rejected alternatives

- **Split type 1b into serving-variance and artifact-variance and assess both.** The
  honest version of this doubles the assessed surface per open-weights model — every spec
  field forked into an API cell and a weights cell — for a route the repo cannot run and a
  question (self-hosted behavior) no report here could verify beyond transcription. The
  distinction survives, but as prose in the reports that exhibit it, which is where an
  axis waits until it earns itself.
- **Reframe issue #15's arm as a category-2 experiment** (keep the self-hosted throughput
  work, file it under harness measurement instead of model assessment). Offered to the
  owner; rejected — killed outright. An exclusion that quietly keeps the excluded work
  under a different heading isn't an exclusion.
- **A methodology rule.** Also offered; rejected on the record's own grounds: methodology.md
  is the *how* and delegates the *what* to the taxonomy in its own preamble, and its
  anti-goals require a scar for every new rule. What we study is a taxonomy fact; the
  scope note is the taxonomy's existing instrument for exactly this.

## Scope

- **Category 1 only.** Categories 3 and 5 carry `deployment_mode`/`self_host` keys —
  registered vocabulary about *infrastructure* and *memory services*, where self-hosting
  is the assessed subject's own delivery mode. Nothing here extends to them.
- **Transcription facts about weights stay, and stay live.** `access` and `license` keep
  their ADR-0044 semantics; glm-5.3's dated prediction (HF repo by 2026-08-31, flip
  `access` to `open-weights`, read the license) survives unchanged and must still be
  scored. Acknowledging a weights release is cheap, valuable, and unaffected.
- **The exclusion is falsifiable, and the falsifier lives in the scope note**: if a
  weights-route difference ever falsifies an API-derived finding this repo relies on, the
  exclusion is wrong and comes back here as a new ADR.

## Consequences

- `docs/tool-taxonomy.md` §1 gains the Scope note (citing this ADR) and § Deliberate
  exclusions gains the self-hosted-serving bullet.
- `tools/1-models/README.md`: the assessed-block statement is anchored to this ADR; the
  1b table is marked as acknowledged routes rather than assessed subjects; the
  open-weight-parity open question is closed by scope, dated.
- Report-level open questions closed by scope, dated in place: qwen3-coder-next's
  "self-hosted arm" probe, kimi-k3's GGUF-route question. qwen3.8-max's § "The API is
  not the weights" is re-anchored: the section stays as acknowledged context, its 1b
  strain resolved by this decision.
- The local open-weight arm dies: `docs/category-2-program.md` item 3 retired,
  `docs/metrics.md`'s throughput-metric justification amended (the metric itself stays —
  it has API-side value independent of the dead arm), the two article teasers removed,
  [issue #15] closed citing this ADR.
- No schema change: no field renamed, no enum widened, no decoder needed. The spec fields
  mean what they already meant in practice; this ADR makes the practice a stated decision.
