"""probes/harness/adapters/gemini.py — wire-shape translation for Google's Gemini
`generateContent` family. Free functions, no class — matches anthropic_messages.py and
openai_compat.py's shared idiom.

Gemini is the one family whose model id lives in the URL path rather than the request
body — this module exports `endpoint_url()` in addition to the shared three-function
surface for exactly that reason.

Adapters never interpret an error body and never raise (see anthropic_messages.py's
module docstring for the shared rationale) — these functions only translate a
2xx-shaped request/response, nothing more.
"""
from __future__ import annotations


def build_request(api_model_id: str, prompt: str, max_tokens: int, extra_params: dict) -> dict:
    """`contents` as a role/parts structure (NOT `messages` — the other two families'
    shape) with sampling and thinking parameters nested under `generationConfig`
    rather than the top level. `api_model_id` is accepted for call-site parity with
    the other two adapters' identical signature but is deliberately NOT placed
    anywhere in the returned body — the model id belongs in the URL path via
    `endpoint_url()` below, never in the body, on this family alone."""
    generation_config = {"maxOutputTokens": max_tokens, **(extra_params or {})}
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }


def build_content_request(api_model_id: str, block: dict, max_tokens: int) -> dict:
    """`contents` from an already-substituted content-block template (runner.py's
    `build_entry_request`, MODAL-01): a single user turn whose `parts` is
    `block["parts"]`, plus `generationConfig.maxOutputTokens`. Same identical
    signature as the other two adapters' build_content_request — call-site parity
    lets runner.py dispatch through ADAPTERS[wire_family] with no vendor-name
    conditional. `api_model_id` is accepted for that parity but deliberately NOT
    placed anywhere in the returned body — same convention build_request() above
    already documents for this family alone. Never interprets an error body and
    never raises. parse_usage() needs no companion change: a response's
    `usageMetadata` object has the same shape regardless of what request content
    produced it."""
    return {
        "contents": [{"role": "user", "parts": block["parts"]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }


def auth_headers(key: str) -> dict:
    """`x-goog-api-key` header — the current recommended method. The `?key=` query
    param still works for backward compatibility but is deliberately not used here:
    D-09's URL-masking exists for URLs the harness does not control, not as licence to
    put a key in one when a header alternative is available."""
    return {"x-goog-api-key": key}


def endpoint_url(base_url: str, api_model_id: str) -> str:
    """The model id lives in the URL path, suffixed `:generateContent` — the one
    family whose endpoint the shared runner.py suffix table cannot build; the runner
    dispatches here via `hasattr(adapter, "endpoint_url")` when no fixed suffix is
    registered for this wire_family."""
    return f"{base_url.rstrip('/')}/models/{api_model_id}:generateContent"


def parse_usage(response_body: dict) -> dict:
    """Normalized usage mapping read from `usageMetadata`. Absent-means-not-reported
    semantics: a missing field is None, never a substituted zero — this matters most
    for `thoughtsTokenCount`, which RESEARCH.md flags as possibly absent even with
    thinking enabled on some models; treating that absence as 0 would silently claim
    "no reasoning tokens billed" when the true answer is "not reported"."""
    meta = response_body.get("usageMetadata") or {}
    return {
        "input_tokens": meta.get("promptTokenCount"),
        "output_tokens": meta.get("candidatesTokenCount"),
        "reasoning_tokens": meta.get("thoughtsTokenCount"),
        "cached_tokens": meta.get("cachedContentTokenCount"),
    }
