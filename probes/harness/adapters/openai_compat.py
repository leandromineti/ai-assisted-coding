"""probes/harness/adapters/openai_compat.py — wire-shape translation shared by every
maker whose chat/completions surface follows the OpenAI-compatible shape: OpenAI, xAI,
DeepSeek, Moonshot AI (Kimi), Z.ai (GLM) and Alibaba/Qwen (DashScope International). One
module for six makers is the whole point of the family split (RESEARCH.md, D-01) — the
six differ only in models.yaml config (base URL, key env var, model id), never in code
here. No conditional in this file branches on a vendor or maker name.

Adapters never interpret an error body and never raise (see anthropic_messages.py's
module docstring for the shared rationale) — these three functions only translate a
2xx-shaped request/response, nothing more.
"""
from __future__ import annotations


def build_request(api_model_id: str, prompt: str, max_tokens: int, extra_params: dict) -> dict:
    """Chat-completions body: `model`, `max_tokens`, a single-user-turn `messages`
    array, and any declared extra parameters merged at the top level — mirrors
    anthropic_messages.build_request's shape and call-site signature exactly, so the
    runner can dispatch through either adapter with no branching of its own."""
    return {
        "model": api_model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        **(extra_params or {}),
    }


def auth_headers(key: str) -> dict:
    """`Authorization: Bearer <key>` — the standard bearer shape every one of the six
    makers this module serves confirmed (RESEARCH.md § per-vendor wire facts)."""
    return {"Authorization": f"Bearer {key}"}


def parse_usage(response_body: dict) -> dict:
    """Normalized usage mapping read from the response's `usage` object.
    Absent-means-not-reported semantics throughout: a missing field is None, never a
    substituted zero — matching anthropic_messages.parse_usage's discipline.

    Two fields are read opportunistically because only one maker in this family
    populates them: `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`, DeepSeek's
    own top-level cache counters, present alongside (not instead of) the
    family-standard `prompt_tokens_details.cached_tokens` subset field. Where both
    surfaces report a cached-token count and they disagree, the disagreement is
    recorded verbatim rather than silently preferring one — a contradiction between a
    vendor's own accounting and the family baseline is itself a finding this
    instrument exists to surface, not something to reconcile away.

    `cost_in_usd_ticks` (xAI-only, observed self-priced responses per conclusion 19)
    is captured for future use — `ledger.cost_usd()` does NOT yet consume it (WR-03,
    phase-09 code review 2026-09-01): the tick-to-USD divisor is not vendor-documented
    anywhere this repo has found (`tools/1-models/grok-4-5.md` § Probed records only
    an arithmetic inference, $1e-10/tick, explicitly not treated as vendor fact), so
    wiring an unconfirmed divisor into spend-ceiling accounting would risk silently
    mis-stating real spend rather than fixing it. `ledger.cost_usd()` still derives
    cost from `input_tokens`/`output_tokens` x the flat `prices.yaml` rate for every
    vendor, including xAI, until the divisor is confirmed from vendor docs."""
    usage = response_body.get("usage") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}

    cached_tokens = prompt_details.get("cached_tokens")
    cache_hit_tokens = usage.get("prompt_cache_hit_tokens")
    cache_miss_tokens = usage.get("prompt_cache_miss_tokens")

    cache_disagreement = None
    if (
        cached_tokens is not None
        and cache_hit_tokens is not None
        and cached_tokens != cache_hit_tokens
    ):
        cache_disagreement = {
            "family_cached_tokens": cached_tokens,
            "vendor_cache_hit_tokens": cache_hit_tokens,
        }

    return {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": completion_details.get("reasoning_tokens"),
        "cached_tokens": cached_tokens,
        "cache_hit_tokens": cache_hit_tokens,
        "cache_miss_tokens": cache_miss_tokens,
        "cache_disagreement": cache_disagreement,
        "cost_in_usd_ticks": usage.get("cost_in_usd_ticks"),
    }
