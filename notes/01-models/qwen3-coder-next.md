---
name: qwen3-coder-next
layer: 1
vendor: Alibaba (Qwen team)
url: https://huggingface.co/Qwen/Qwen3-Coder-Next
license: Apache-2.0
open_source: true
model_id: Qwen/Qwen3-Coder-Next
release_mode: open-weights
context_window: 262144
max_output: unverified
pricing: "weights free; hosted via Alibaba/aggregators at route-dependent prices"
knowledge_cutoff: unverified
checked: 2026-07-31
depth: stub
---

# Qwen3-Coder-Next

The Qwen line's current **verified** coding release (card checked 2026-07-31,
resolving the seed inventory's `unverified` row): an 80B-total / **3B-activated** MoE
(512 experts, 10 per token), 256K native context, Apache-2.0, released ~Feb 2026.
Its pitch is the inverse of Kimi K3's: not the biggest open model, but "performance
comparable to models with 10–20× more active parameters" — the local-inference story
the seed inventory attributed to the Qwen line, now with a concrete artifact.

**Note on "Qwen 4 Coder":** third-party posts claim a June 2026 successor (Apache-2.0,
82% SWE-Verified, Mac-runnable). It does **not** resolve on the official HF org
(checked 2026-07-31) and the official card names no successor — recorded as
unverified rumor, the same discipline that kept DeepSeek's row honest through the R2
cycle.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Card claims agent-oriented tuning; benchmark claims: SWE-bench Verified 70.6%, SWE-bench Pro 44.3%, Terminal-Bench 2.0 **36.2%** — the honest number in the set (a coding-agent model publishing a sub-40 terminal score) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 256K native — deliberately *not* the 1M class; the small-activated-params bet spends elsewhere |
| Cost per completed task | 3B activated params is the lowest inference cost in this sweep by far — this is the one model here an individual can genuinely self-host |
| Release mode & access routes (1b) | Open weights (Apache-2.0, the cleanest license in the sweep) + hosted routes; heavy GGUF ecosystem |

## Role in this repo's work

None run. The Qwen line appears in llm-coding-benchmark's roster (via opencode's
`default.txt` — no bespoke prompt, per upstream issue #12) and in hermes' per-family
tool-use enforcement list (`qwen` is patched, like GPT/Grok/Gemini — harness authors
treat it as needing execution-discipline correction).

## Surprises

1. **A vendor publishing a modest benchmark number** (Terminal-Bench 2.0 at 36.2)
   alongside strong SWE-bench claims — selective-but-honest disclosure, rarer than it
   should be, and more informative than Kimi's chart-topping claim precisely because
   it's believable.
2. **3B activated parameters** as a serious agent-model bet — the opposite pole from
   Kimi K3's 104B-activated within the same open-weights world. The open ecosystem is
   exploring the activated-params axis far more aggressively than the closed one.

## Open questions

- Verify or bury "Qwen 4 Coder" at the next check — if real, it supersedes this
  report's subject within months of it.
- The 10–20× efficiency claim is benchmark-relative; does it survive an agentic
  workload with real tool loops? (The rig could test a self-hosted arm cheaply.)
