---
name: kimi-k3
layer: 1
vendor: Moonshot AI
url: https://huggingface.co/moonshotai/Kimi-K3
license: "Kimi K3 License (model card's own term; third-party summaries describe it as MIT-like with a commercial MaaS revenue gate — the gate did not appear in the card text checked, so its terms are unverified here)"
open_source: true
model_id: moonshotai/Kimi-K3
release_mode: open-weights
context_window: 1048576
max_output: unverified
pricing: "weights free; hosted API via Moonshot/OpenRouter at route-dependent prices (not pinned here)"
knowledge_cutoff: unverified
checked: 2026-07-31
depth: stub
---

# Kimi K3

The largest open-weight model released as of mid-2026: **2.8T total parameters, 104B
activated** (896 experts, 16 per token), on Kimi Delta Attention + Attention Residuals
— 93 layers (69 KDA + 24 gated MLA), native vision, 1M context. Shipped **quantized by
design**: MXFP4 weights / MXFP8 activations via quantization-aware training, so the
published artifact *is* the low-precision model rather than a full-precision original
that third parties quantize down. Released July 2026.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Vendor-claimed strength ("agentic" benchmark family); the card claims **88.3 on Terminal-Bench 2.1** — above every harness+model row in this repo's stale benchmark snapshot, with harness unstated (the layer index's model+harness confound, from the other side) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1,048,576 exactly (2^20) — same power-of-two budget as GPT-5.6's "1.05M" |
| Cost per completed task | Weights free; the real cost is inference infrastructure (vLLM/SGLang on H100/H20-class GPUs) — the taxonomy's open question about whether 2.8T-scale open weights change anything *practical* for individuals stands |
| Release mode & access routes (1b) | Open weights + hosted APIs + aggregators; the full 1b spread, with quantization variance built in rather than added downstream |

## Role in this repo's work

Referenced, not run: the layer index's open-weight-parity question names it, and it
appears in llm-coding-benchmark's model roster (driven through opencode — the harness
whose per-model dispatch this repo documented upstream).

## Surprises

1. **QAT-native release**: shipping MXFP4 as the canonical artifact collapses the 1b
   "quantization changes behavior under the same name" problem — there is no
   full-precision reference to diverge from. A structural fix to route variance,
   from the weights side.
2. **The benchmark direction reversed**: an open-weight vendor claiming to *beat*
   the frontier pairings on Terminal-Bench (88.3 vs the 83.4 the index records for
   Codex+GPT-5.5) — claims now flow from open-weight labs toward closed leaders, with
   harness pairing unstated in both directions.
3. **A bespoke license with a name** ("Kimi K3 License") — neither Apache/MIT nor
   proprietary; open-weights licensing is speciating, and `open_source: true` needs
   the license field read, not assumed.

## Open questions

- The license's actual commercial terms — read the license file itself, not
  summaries, before any claim stronger than "weights downloadable".
- What harness produced the 88.3 Terminal-Bench claim? (Unstated in the card
  summary; the model+harness confound cuts both ways.)
- Does 104B-activated MoE inference actually fit any individual's budget via the
  GGUF/community route, and at what quality loss?
