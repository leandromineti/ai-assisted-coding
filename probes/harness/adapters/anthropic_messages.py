"""probes/harness/adapters/anthropic_messages.py — wire-shape translation for the
Anthropic Messages API. Three free functions, no class — matches this repo's
function-only module idiom (no class-based script exists anywhere under scripts/).

Adapters never interpret an error body and never raise (RESEARCH.md's Architectural
Responsibility Map: error-body handling belongs to client.py/runner.py) — these three
functions only translate a 2xx-shaped request/response, nothing more.
"""
from __future__ import annotations


def build_request(api_model_id: str, prompt: str, max_tokens: int, extra_params: dict) -> dict:
    """Messages body: `model`, `max_tokens`, `messages` as a single user turn.
    `max_tokens` is sent unconditionally — RESEARCH.md flags its required-ness on
    this API as unconfirmed, and including it costs nothing either way."""
    return {
        "model": api_model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        **(extra_params or {}),
    }


def auth_headers(key: str) -> dict:
    """`x-api-key` + `anthropic-version` — not `Authorization: Bearer`, Anthropic's
    own auth shape (RESEARCH.md § Anthropic wire facts)."""
    return {"x-api-key": key, "anthropic-version": "2023-06-01"}


def parse_usage(response_body: dict) -> dict:
    """Normalized usage mapping read from the response's `usage` object.
    Absent-means-not-reported semantics: a missing field is None, never a
    substituted zero."""
    usage = response_body.get("usage") or {}
    return {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
    }
