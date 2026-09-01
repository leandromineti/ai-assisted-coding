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


def build_content_request(api_model_id: str, block: dict, max_tokens: int) -> dict:
    """Messages body from an already-substituted content-block template
    (runner.py's `build_entry_request`, MODAL-01): `model`, `max_tokens`, and
    `messages` as a single user turn whose `content` is `block["content"]`. Same
    identical signature across all three adapters — the call-site-parity
    convention build_request() above already holds — so runner.py dispatches
    through ADAPTERS[wire_family] with no vendor-name conditional. Never
    interprets an error body and never raises (this module's docstring's shared
    rule). parse_usage() needs no companion change: a response's `usage` object
    has the same shape regardless of what request content produced it."""
    return {
        "model": api_model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": block["content"]}],
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
