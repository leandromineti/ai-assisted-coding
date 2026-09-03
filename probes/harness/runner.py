#!/usr/bin/env python3
"""probes/harness/runner.py — CLI entry point: parses a probe-set YAML, dispatches
each declared probe through the wire-family adapter registered in adapters/, fires
the request via client.py, and writes the result as one JSONL record per vendor
(D-08) plus one ledger line per billed attempt (D-07).

    python3 probes/harness/runner.py --set probes/sets/smoke.yaml [--dry-run] [--refire-exhausted] [--refire-ceiling-skipped]
    python3 probes/harness/runner.py --selftest

Exit codes: 0 clean, 1 problems recorded (a probe errored, exhausted its retry budget,
was dropped by a vendor sub-ceiling breach, or the global ceiling stopped the run — D-06,
ledger.ceiling_verdict consulted strictly BETWEEN probes, never mid-flight), 2 bad
invocation (including a malformed probes/sets/*.yaml, models.yaml, prices.yaml, or
ceilings.yaml — the fail-loud path never returns a partial work list).

Secrets: keys are loaded once via client.load_keys() into a single in-process dict;
auth_headers() (in each adapter) is the only consumer of a key VALUE. build_record()
never accepts a header VALUE into the record — only a header NAME. After a record is
serialized and before it is written, assert_no_secrets() greps the serialized form for
every one of the eight loaded key values (not just the vendor being probed) and aborts
the whole run on a hit (D-09, T-09-01).

Stdlib-only scope (WR-01, phase-09 code review 2026-09-01): client.py's "no vendor SDK,
no third-party HTTP or retry library" claim is about the WIRE TRANSPORT/RETRY path
only. This module imports PyYAML (`import yaml`, not part of the standard library) to
parse models.yaml, prices.yaml, ceilings.yaml, and every probes/sets/*.yaml file —
config/probe-declaration parsing is a scoped, documented exception to the stdlib-only
principle, not covered by it. PyYAML must be installed in the environment this runs in.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import client
import fixtures
import ledger
from adapters import ADAPTERS

PROBES_DIR = Path(__file__).resolve().parent.parent
MODELS_PATH = PROBES_DIR / "harness" / "models.yaml"
PRICES_PATH = PROBES_DIR / "harness" / "prices.yaml"
CEILINGS_PATH = PROBES_DIR / "harness" / "ceilings.yaml"
INVENTORY_PATH = PROBES_DIR / "inventory.yaml"
SWEEP_STAGES_PATH = PROBES_DIR / "sweep-stages.yaml"
GENERATED_DIR = PROBES_DIR / "sets" / "generated"
CONTRACT_SWEEP_GENERATED_PATH = GENERATED_DIR / "contract-sweep.yaml"
CONTENT_BLOCKS_GENERATED_PATH = GENERATED_DIR / "content-blocks.yaml"
RAW_DIR = PROBES_DIR / "raw"
LEDGER_PATH = PROBES_DIR / "ledger.jsonl"
SECRETS_PATH = Path.home() / ".secrets" / "model-probes.env"

HARNESS_VERSION = "0.1.0"

# Default unconditional attempt cap for client.send_with_retry (HARN-04). Not a
# per-vendor value — the same cap serves all three wire families; retry_decision's
# classification (not this number) is what carries the family-agnostic discipline.
DEFAULT_MAX_ATTEMPTS = 5

# Each wire family's URL suffix, appended to models.yaml's base_url. Gemini embeds the
# model id in the path instead and has no fixed suffix here — endpoint_url() below
# dispatches to its adapter's own endpoint_url() when a family has no entry in this
# table (checked via hasattr, never a vendor-name conditional).
_WIRE_FAMILY_URL_SUFFIX = {
    "anthropic_messages": "/messages",
    "openai_compat": "/chat/completions",
}

# D-09 refinement (Task 1 checkpoint resolution, 2026-09-01): org/account-identifying
# response headers are excluded from the logged record ENTIRELY — not just their
# values. Rate-limit headers and request-ids are research-relevant and are kept.
# Case-insensitive; everything not listed here passes through unchanged.
_ORG_IDENTIFYING_RESPONSE_HEADERS = {
    "openai-organization",
    "openai-project",
    "anthropic-organization-id",
    "anthropic-workspace-id",  # observed live on the tracer probe, 2026-09-01 —
                                 # Anthropic's actual account-identifying header;
                                 # the guessed `anthropic-organization-id` above was
                                 # never observed on the wire, kept as a defensive
                                 # guess for a differently-shaped account signal
    "x-organization-id",
    # Added 2026-09-01, Phase 11 plan 11-03 (Rule 2 deviation): OBSERVED live at
    # Moonshot AI (Kimi) in probes/raw/kimi.jsonl's Phase 9 smoke-test record
    # (probe_id kimi-k3--baseline--none--default--b3540b5c), found while
    # authoring probes/audit-evidence.py's D-05 scanner — reading that exact
    # record per this plan's own instructions surfaced a whole `Msh-*` header
    # family carrying org/user/project/group identifiers this filter never
    # covered (WR-04's exact gap, now closed for this one additional vendor;
    # the pre-existing record itself predates this fix and is flagged by the
    # scanner, not retroactively cleaned — see 11-03-SUMMARY.md). `msh-request-id`
    # and `x-msh-trace-id` are request-tracing, not account-identifying, and
    # stay unfiltered, matching every other vendor's kept rate-limit/request-id
    # headers.
    "msh-org-id",
    "msh-uid",
    "msh-project-id",
    "msh-gid",
    # Added 2026-09-01, Phase 11 plan 11-04 (Rule 2 deviation): OBSERVED live
    # during the stage-1/2 calibration batch — `set-cookie` (and its
    # capitalized `Set-Cookie` form at zai) carries edge/CDN
    # session-tracking tokens (Cloudflare's `__cf_bm` bot-management cookie
    # at openai/kimi; Alibaba Cloud WAF's `acw_tc` anti-crawler cookie at
    # qwen/zai), never an account identifier by the header NAME this filter
    # otherwise targets, but a per-session/per-request tracking value that is
    # exactly the class probes/audit-evidence.py's D-05 tripwire exists to
    # catch. Not request-tracing (unlike `msh-request-id`, kept above) — a
    # session cookie is reusable state, not a static id naming this request.
    "set-cookie",
}


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path every
    config loader below uses. Named `_fail`, not `die`, only to keep it distinct
    from any future process-signal handling in this file. Callers in `main()` let
    this propagate naturally (correct CLI exit-code behavior); `selftest()` below
    catches it with `except SystemExit` to verify the path without killing the
    self-test process itself."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def probe_id(
    model_slug: str, param: str, value: str, mode: str, request_body: dict, repeat: int | None = None
) -> str:
    """D-04: semantic slug + short hash of the canonical request body. Canonical =
    sorted keys, no whitespace — the same body always hashes the same regardless of
    the probe-set YAML's key order, and a corrected body (e.g. a typo fixed) changes
    the hash, so a fixed probe re-fires without manual JSONL surgery.

    D-09 / Phase 12 extension: `repeat` carries a behavioral repeat index. When
    `repeat` is `None` (the default, every pre-Phase-12 call site), the return value
    is BYTE-IDENTICAL to what this function returned before this extension — every
    probe_id already cited in probes/classified/contract-sweep.yaml keeps resolving.
    When `repeat` is an integer, an `r`-prefixed segment is inserted between `mode`
    and the body hash: `{model_slug}--{param}--{value}--{mode}--r{repeat}--{body_hash}`.
    A byte-identical request body fired N times with `repeat=1..N` therefore produces
    N distinct ids sharing the same trailing hash segment — the identity coordinate
    that makes a repeated identical request body individually addressable and
    individually resumable (seen_probe_ids() below needs no change: it just sees N
    different strings)."""
    canonical = json.dumps(request_body, sort_keys=True, separators=(",", ":"))
    body_hash = hashlib.sha256(canonical.encode()).hexdigest()[:8]
    if repeat is None:
        return f"{model_slug}--{param}--{value}--{mode}--{body_hash}"
    return f"{model_slug}--{param}--{value}--{mode}--r{repeat}--{body_hash}"


def seen_probe_ids(
    path: Path, *, refire_exhausted: bool = False, refire_ceiling_skipped: bool = False
) -> set[str]:
    """Scan `probes/raw/{vendor}.jsonl` for already-logged probe_ids (D-08, HARN-02).
    A missing file, a zero-byte file, and a file whose final line is a truncated
    partial record are all handled without raising — every complete line populates
    the seen-set, the trailing partial line is ignored.

    Default-skip choice for `terminal == "retry_exhausted"` (HARN-04 idempotency):
    a retry-exhausted record is a LOGGED terminal outcome, not a dropped one — by
    default it is included in the seen-set exactly like any other terminal record, so
    re-running a probe set does not silently re-fire a probe that already spent its
    full retry budget against (for example) a still-in-effect spend-cap 429. Pass
    `refire_exhausted=True` to exclude those specific ids from the seen-set instead,
    so a transient rate-limit window can be re-attempted deliberately via
    `--refire-exhausted` rather than by accident on every ordinary run.

    Same idea for `terminal == "skipped_ceiling"` (WR-02, phase-09 code review
    2026-09-01): a probe dropped by a vendor sub-ceiling breach was never actually
    fired, but by default its probe_id still permanently populates the seen-set —
    without this flag it can never be re-attempted even after `ceilings.yaml` is
    raised specifically to unblock it, forcing a hand-edit of the append-only JSONL
    file this repo's own conventions forbid. Pass `refire_ceiling_skipped=True`
    (`--refire-ceiling-skipped`) to exclude those ids from the seen-set instead — a
    separate flag from `refire_exhausted` because the two failure modes have
    different root causes (a transient rate limit vs. a budget policy someone
    deliberately raised) and a caller may want to refire only one of them."""
    p = Path(path)
    seen: set[str] = set()
    if not p.exists() or p.stat().st_size == 0:
        return seen
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            # Truncated trailing line from a killed process — ignore it; every
            # complete line before it already populated `seen`.
            continue
        pid = rec.get("probe_id")
        if not pid:
            continue
        terminal = rec.get("terminal")
        if refire_exhausted and terminal == "retry_exhausted":
            continue
        if refire_ceiling_skipped and terminal == "skipped_ceiling":
            continue
        seen.add(pid)
    return seen


def derive_terminal(attempts: list[dict]) -> tuple[str, int]:
    """From an ordered attempts list (client.send_with_retry's return shape), derive
    the record's `terminal` — the FINAL attempt's action ('verdict' | 'exhausted' |
    'fatal'; 'retry' never appears here, since a 'retry' action always causes the loop
    to continue to a next attempt) — and `retries`, the count of non-terminal
    ('retry') attempts. Pure and reused directly by main(); exercised directly by
    --selftest so the derivation logic itself is covered, not only through a live
    send_with_retry call."""
    terminal = attempts[-1]["action"]
    retries = sum(1 for a in attempts if a["action"] == "retry")
    return terminal, retries


def filter_response_headers(headers: dict) -> dict:
    """Drop org/account-identifying response headers before they reach a record
    (D-09 refinement). Everything else — rate-limit headers, request-ids — passes
    through unchanged."""
    return {k: v for k, v in headers.items() if k.lower() not in _ORG_IDENTIFYING_RESPONSE_HEADERS}


def build_record(
    *,
    pid: str,
    vendor: str,
    model_slug: str,
    api_model_id: str,
    wire_family: str,
    set_file: str,
    param: str,
    value: str,
    mode: str,
    method: str,
    url: str,
    headers_sent: dict,
    request_body: dict,
    attempts: list[dict],
    terminal: str,
    retries: int,
    usage: dict,
    cost: float | None,
) -> dict:
    """Build the JSONL record from an explicit field allowlist (D-09). `headers_sent`
    is the FULL headers dict actually sent (name -> value) — this function only ever
    reads `.keys()` from it; there is no code path here that copies a header VALUE
    into the record."""
    return {
        "probe_id": pid,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vendor": vendor,
        "model_slug": model_slug,
        "api_model_id": api_model_id,
        "wire_family": wire_family,
        "set_file": set_file,
        "param": param,
        "value": value,
        "mode": mode,
        "request": {
            "method": method,
            "url": url,
            "headers_sent": sorted(headers_sent.keys()),
            "body": request_body,
        },
        "attempts": attempts,
        "terminal": terminal,
        "retries": retries,
        "usage": usage,
        "cost_usd": cost,
        "harness_version": HARNESS_VERSION,
    }


def assert_no_secrets(serialized: str, key_values: list[str]) -> None:
    """Post-serialization tripwire (D-09, T-09-01): abort the whole run if ANY
    currently loaded PERSONAL_* key value — not just the vendor being probed — is
    found in the serialized record. Structural exclusion (the field allowlist in
    build_record) is the primary defense; this is the backstop, never relied on
    alone."""
    for kv in key_values:
        if kv and kv in serialized:
            _fail(1, "SECURITY ABORT: a loaded key value was found in a record about "
                      "to be written — aborting before any write (D-09 tripwire).")


def load_models(path: Path = MODELS_PATH) -> dict[str, dict]:
    """Parse models.yaml -> {slug: row}. Required keys: slug, maker, vendor,
    wire_family, api_model_id, base_url, key_env_var. Fails loud (exit 2) on any
    parse or validation error — never a silent default (T-09-03)."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        _fail(2, f"{path}: expected a top-level `models:` list")
    required = {"slug", "maker", "vendor", "wire_family", "api_model_id", "base_url", "key_env_var"}
    rows: dict[str, dict] = {}
    for row in data["models"]:
        missing = required - set(row)
        if missing:
            _fail(2, f"{path}: model row missing required key(s) {sorted(missing)}: {row}")
        rows[row["slug"]] = row
    return rows


def load_prices(path: Path = PRICES_PATH) -> dict[str, dict]:
    """Parse prices.yaml -> {slug: row}. Required keys: slug, input_usd_per_mtok,
    output_usd_per_mtok, retrieved, source. Fails loud (exit 2) on any parse or
    validation error."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("prices"), list):
        _fail(2, f"{path}: expected a top-level `prices:` list")
    required = {"slug", "input_usd_per_mtok", "output_usd_per_mtok", "retrieved", "source"}
    rows: dict[str, dict] = {}
    for row in data["prices"]:
        missing = required - set(row)
        if missing:
            _fail(2, f"{path}: price row missing required key(s) {sorted(missing)}: {row}")
        rows[row["slug"]] = row
    return rows


def load_ceilings(path: Path = CEILINGS_PATH) -> dict:
    """Parse ceilings.yaml -> the thresholds mapping ledger.ceiling_verdict() expects.
    Required keys: global_hard_usd, global_warn_usd, vendor_soft_usd_default,
    vendor_soft_usd. Fails loud (exit 2) on any parse or validation error — D-05: no
    dollar figure is ever hardcoded as a Python fallback if the file is malformed."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict):
        _fail(2, f"{path}: expected a top-level mapping")
    required = {"global_hard_usd", "global_warn_usd", "vendor_soft_usd_default", "vendor_soft_usd"}
    missing = required - set(data)
    if missing:
        _fail(2, f"{path}: missing required key(s) {sorted(missing)}")
    return data


def flatten_totals(raw_totals: dict) -> dict:
    """ledger.totals()'s own return shape is nested (`{"global": {"cost_usd": ...},
    "by_vendor": {vendor: {"cost_usd": ...}}}`) — that shape and its recompute-by-
    summing contract are plan 09-01's and are never touched here. ceiling_verdict()
    takes the simpler flat shape `{"global_usd": float, "by_vendor": {vendor:
    float}}` instead; this is the one-line adapter between the two, called fresh
    every time totals() is recomputed (D-07: no cached total anywhere)."""
    return {
        "global_usd": raw_totals["global"]["cost_usd"],
        "by_vendor": {v: d["cost_usd"] for v, d in raw_totals["by_vendor"].items()},
    }


def build_skipped_ceiling_record(
    *, pid: str, vendor: str, model_slug: str, api_model_id: str, wire_family: str,
    set_file: str, param: str, value: str, mode: str, reason: str,
) -> dict:
    """One record for a probe DROPPED by a vendor sub-ceiling breach (D-06) — never
    fired, so there is no request/response to log. `attempts` is empty and `terminal`
    is `skipped_ceiling`; `reason` names the vendor and the numeric threshold that
    triggered the skip (D-06: a skipped probe is visible evidence, never a silent
    absence — the whole point of writing a record here instead of just not writing
    one)."""
    return {
        "probe_id": pid,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vendor": vendor,
        "model_slug": model_slug,
        "api_model_id": api_model_id,
        "wire_family": wire_family,
        "set_file": set_file,
        "param": param,
        "value": value,
        "mode": mode,
        "request": None,
        "attempts": [],
        "terminal": "skipped_ceiling",
        "retries": 0,
        "usage": {},
        "cost_usd": None,
        "reason": reason,
        "harness_version": HARNESS_VERSION,
    }


# Probe-set entry keys, split required vs optional (plan 09-03 documentation aid —
# load_probe_set only enforces REQUIRED_PROBE_ENTRY_KEYS below; this set exists so a
# reader can see the full recognized vocabulary in one place). `omit` is the newest
# addition: a list of top-level request-body keys the runner removes from the
# adapter's built body immediately before canonicalization and sending — it exists
# so a probe can deliberately test the ABSENCE of a field, which is the only way to
# settle whether a vendor requires one (D-04: the omission changes the canonical
# body, so it changes the probe_id hash too).
#
# `repeat` (D-09, Phase 12): an optional positive integer naming this entry's
# repeat index within a repeat group — the same byte-identical request body
# declared N times, each carrying a distinct `repeat: 1..N`, so the harness fires
# it N times instead of resume-skipping repeats 2..N as already logged. The
# identity must carry it (probe_id()'s `repeat` keyword) precisely because the
# request body itself is deliberately unchanged across the group; without a
# distinguishing coordinate in the id, only the first fired copy would ever be
# addressable. Validated in load_probe_set() below: must be an int, not a bool,
# and >= 1, or the run aborts before any HTTP request — a silently coerced or
# ignored repeat would corrupt the denominator of every rate this phase publishes.
# `top_level_params` (Phase 12 plan 12-05, BHV-06): an additive optional entry
# key for a field a vendor documents at the REQUEST TOP LEVEL, sibling to
# `generationConfig`/`messages` — a location `extra_params` cannot reach for the
# `gemini` family, whose adapter merges `extra_params` INSIDE `generationConfig`
# (adapters/gemini.py's own `build_request()`). Confirmed necessary by reading
# Gemini's own `GenerateContentRequest` field list directly (ai.google.dev/api/
# generate-content, retrieved 2026-09-03): `serviceTier` is a top-level sibling
# of `generationConfig`, `systemInstruction`, `cachedContent` and `store` — NOT
# a `GenerationConfig` field. A mapping merged into the built request body at
# the top level, applied in `build_entry_request()` AFTER
# `apply_max_tokens_field_override()` and BEFORE `apply_omit()` — mirroring
# `omit`'s own precedent exactly (an additive request-shape adjustment applied
# after the adapter builds the base body, before the final probe_id hash is
# taken, so a declared value here changes the probe_id like any other body
# change). Validated fail-loud in `load_probe_set()` below: a non-mapping value
# aborts with exit 2, before any HTTP request is sent — the same discipline
# `repeat`'s own validation already established for a different optional key.
REQUIRED_PROBE_ENTRY_KEYS = {"model", "param", "value", "mode"}
OPTIONAL_PROBE_ENTRY_KEYS = {"prompt", "max_tokens", "extra_params", "omit", "repeat", "top_level_params"}

# Content-block entry keys (Phase 11 plan 11-03, MODAL-01), the second grammar
# runner.py recognizes alongside REQUIRED_PROBE_ENTRY_KEYS/OPTIONAL_PROBE_ENTRY_KEYS
# above — both grammars declared beside each other so the full recognized
# vocabulary is visible in one place. `max_tokens` is REQUIRED here (unlike the
# scalar grammar, where it's optional with a 16-token default): a content-block
# probe's max_tokens is always generator-emitted (inventory-to-sets.py's
# max_tokens_for()/max_tokens_override), never defaulted by the runner. No
# optional content-block entry keys exist today.
REQUIRED_CONTENT_BLOCK_KEYS = {"model", "param", "value", "mode", "max_tokens", "body_template"}
OPTIONAL_CONTENT_BLOCK_KEYS: set[str] = set()

# Each wire family's content key inside a substituted body_template block —
# anthropic_messages and openai_compat both carry `content` (a content-block
# list), gemini carries `parts`. Table-driven, matching _WIRE_FAMILY_URL_SUFFIX's
# idiom above — no vendor-name conditional anywhere on this path.
_WIRE_FAMILY_CONTENT_KEY = {
    "anthropic_messages": "content",
    "openai_compat": "content",
    "gemini": "parts",
}

CONTENT_BLOCK_IMAGE_PLACEHOLDER = "{{IMAGE_BASE64_PLACEHOLDER}}"


def apply_omit(request_body: dict, omit_keys: list[str] | None) -> dict:
    """D-04 extension (plan 09-03): remove the listed top-level keys from a built
    request body, immediately before probe_id canonicalization and before sending —
    the only way to settle on the wire whether a vendor requires a field. Never
    mutates the caller's dict in place; always returns a fresh dict (even when
    `omit_keys` is empty/None) so a caller can never accidentally alias the
    adapter's returned body."""
    if not omit_keys:
        return dict(request_body)
    return {k: v for k, v in request_body.items() if k not in omit_keys}


def load_probe_set(path) -> list[dict]:
    """Parse a probes/sets/*.yaml declaration. A missing/empty `probes:` list, or an
    entry missing a required key, aborts before any HTTP request is sent: exit code
    2, a named diagnostic naming the file and the missing key, zero new JSONL lines
    (HARN-01 empty). See REQUIRED_PROBE_ENTRY_KEYS / OPTIONAL_PROBE_ENTRY_KEYS above
    for the full recognized entry-key vocabulary — only the required subset is
    enforced here; an unrecognized key is not an error (forward-compatible), it is
    simply never read."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    probes = (data or {}).get("probes") if isinstance(data, dict) else None
    if not isinstance(probes, list) or not probes:
        _fail(2, f"{path}: `probes:` must be a non-empty list")
    for entry in probes:
        missing = REQUIRED_PROBE_ENTRY_KEYS - set(entry)
        if missing:
            _fail(2, f"{path}: probe entry missing required key(s) {sorted(missing)}: {entry}")
        if "repeat" in entry:
            repeat_value = entry["repeat"]
            # isinstance(True, int) is True in Python — bools must be rejected
            # explicitly, or `repeat: true` would silently pass as repeat=1.
            if isinstance(repeat_value, bool) or not isinstance(repeat_value, int) or repeat_value < 1:
                _fail(
                    2,
                    f"{path}: probe entry has an invalid `repeat` value {repeat_value!r} "
                    f"(must be an int >= 1, not a bool): {entry}",
                )
        if "top_level_params" in entry and not isinstance(entry["top_level_params"], dict):
            _fail(
                2,
                f"{path}: probe entry has an invalid `top_level_params` value "
                f"{entry['top_level_params']!r} (must be a mapping): {entry}",
            )
    return probes


def endpoint_url(wire_family: str, base_url: str, api_model_id: str) -> str:
    """Suffix a family's base_url per RESEARCH.md's per-family URL convention.
    Anthropic and OpenAI-compat append a fixed suffix; a family whose adapter defines
    its own `endpoint_url()` (Gemini, plan 09-02 — the model id lives in the path,
    not the body) is dispatched there instead."""
    suffix = _WIRE_FAMILY_URL_SUFFIX.get(wire_family)
    if suffix is not None:
        return base_url.rstrip("/") + suffix
    adapter = ADAPTERS.get(wire_family)
    if adapter is not None and hasattr(adapter, "endpoint_url"):
        return adapter.endpoint_url(base_url, api_model_id)
    raise ValueError(f"no endpoint_url rule for wire_family={wire_family}")


def load_content_block_set(path=CONTENT_BLOCKS_GENERATED_PATH) -> list[dict]:
    """Like load_probe_set, but for probes/sets/generated/content-blocks.yaml's
    deliberately-different `content_block_probes:` top-level key — the file
    load_probe_set refuses loudly (D-12). Mirrors load_probe_set's fail-loud
    contract exactly: a missing/empty `content_block_probes:` list, or an entry
    missing a required key (REQUIRED_CONTENT_BLOCK_KEYS above), aborts before
    any HTTP request is sent — exit 2, a diagnostic naming the file and the
    missing key, zero new JSONL lines. --check-stages (Phase 11 plan 11-02) and
    the `--content-block-set` firing path (Phase 11 plan 11-03, MODAL-01) are
    this loader's two callers."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    entries = (data or {}).get("content_block_probes") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        _fail(2, f"{path}: `content_block_probes:` must be a non-empty list")
    for entry in entries:
        missing = REQUIRED_CONTENT_BLOCK_KEYS - set(entry)
        if missing:
            _fail(2, f"{path}: content-block entry missing required key(s) {sorted(missing)}: {entry}")
    return entries


def substitute_image_payload(block, payload: str):
    """Pure (Phase 11 plan 11-03, MODAL-01): returns a NEW structure with every
    occurrence of CONTENT_BLOCK_IMAGE_PLACEHOLDER replaced by `payload`, walking
    mappings, lists, and strings generically. Never mutates its argument — the
    cache-control entries carry no placeholder at all and pass through
    unchanged, byte-for-byte, as a NEW (not aliased) structure all the same."""
    if isinstance(block, dict):
        return {k: substitute_image_payload(v, payload) for k, v in block.items()}
    if isinstance(block, list):
        return [substitute_image_payload(v, payload) for v in block]
    if isinstance(block, str):
        return block.replace(CONTENT_BLOCK_IMAGE_PLACEHOLDER, payload)
    return block


def apply_max_tokens_field_override(request_body: dict, row: dict) -> dict:
    """(Phase 11 plan 11-04, D-09 "fix-before-fire" deviation) A models.yaml
    row may declare `max_tokens_field`: the request body key that model's
    wire family's `max_tokens` value must actually be sent under, when the
    family default field name is rejected outright by that ONE model —
    gpt-5-6-sol's calibration-batch 400: "Unsupported parameter: 'max_tokens'
    is not supported with this model. Use 'max_completion_tokens' instead."
    (`param: "max_tokens"` in the error JSON).

    The rename happens HERE, in the runner's per-entry request assembly,
    deliberately OUTSIDE the wire-family adapter modules — those modules'
    own docstrings state no per-vendor/per-model conditional belongs inside
    them (openai_compat.py: "No conditional in this file branches on a
    vendor or maker name"). A per-model field-name override is exactly that
    kind of conditional, so it lives in the one place that already varies
    per (entry, row) pair: this function, called right after
    adapter.build_request()/build_content_request() return, before
    apply_omit(). Absent (the default, every model but gpt-5-6-sol): the
    request body is returned unchanged, so this is a no-op everywhere else."""
    field = row.get("max_tokens_field")
    if field is None or field == "max_tokens" or "max_tokens" not in request_body:
        return request_body
    request_body = dict(request_body)
    request_body[field] = request_body.pop("max_tokens")
    return request_body


def build_entry_request(entry: dict, row: dict, adapter) -> dict:
    """Pure (Phase 11 plan 11-03, MODAL-01): the final request body for either
    grammar a probes/sets/*.yaml entry can carry.

    Content-block entry (carries `body_template`): deep-copy
    entry["body_template"][row["wire_family"]] FIRST — unconditionally,
    regardless of what plan 11-02 fixed at generation time, because a
    hand-authored or older set file can still alias (RESEARCH.md Pattern 2) —
    then substitute fixtures.TINY_PNG_BASE64 for the placeholder token, assert
    the substituted block carries its family's expected content key
    (_WIRE_FAMILY_CONTENT_KEY), and dispatch through
    adapter.build_content_request(). A family key absent from body_template is
    a registry defect (inventory-to-sets.py's firing_scope should make this
    unreachable) — fail loud (exit 2), naming the entry, never a silently-empty
    body.

    Scalar entry (no `body_template`): the existing
    adapter.build_request(...) + apply_omit(...) construction, with one
    Phase 12 plan 12-05 addition — a declared `top_level_params` mapping is
    merged into the built body AFTER apply_max_tokens_field_override() and
    BEFORE apply_omit(), for a field a vendor documents at the request TOP
    LEVEL that the `gemini` family's own `extra_params` merge (nested inside
    `generationConfig`) cannot reach. Absent (every entry but the ones that
    declare it): a no-op, byte-identical to the pre-extension construction.

    Both branches route their final body through
    apply_max_tokens_field_override() (plan 11-04) before returning — a
    per-model request-field rename, a no-op for every model that doesn't
    declare one."""
    wire_family = row["wire_family"]

    if "body_template" in entry:
        content_key = _WIRE_FAMILY_CONTENT_KEY.get(wire_family)
        if content_key is None:
            _fail(2, f"no content key registered for wire_family={wire_family!r} (entry: {entry})")
        template = entry["body_template"].get(wire_family)
        if template is None:
            _fail(
                2,
                f"content-block entry has no body_template for wire_family={wire_family!r}: "
                f"model={entry.get('model')!r} param={entry.get('param')!r}",
            )
        block = copy.deepcopy(template)
        block = substitute_image_payload(block, fixtures.TINY_PNG_BASE64)
        if content_key not in block:
            _fail(
                2,
                f"content-block entry's substituted body is missing its family's expected "
                f"key {content_key!r} for wire_family={wire_family!r}: "
                f"model={entry.get('model')!r} param={entry.get('param')!r}",
            )
        request_body = adapter.build_content_request(row["api_model_id"], block, entry["max_tokens"])
        return apply_max_tokens_field_override(request_body, row)

    prompt = entry.get("prompt", "Reply with one word.")
    max_tokens = entry.get("max_tokens", 16)
    extra_params = entry.get("extra_params") or {}
    request_body = adapter.build_request(row["api_model_id"], prompt, max_tokens, extra_params)
    request_body = apply_max_tokens_field_override(request_body, row)
    top_level_params = entry.get("top_level_params") or {}
    if top_level_params:
        request_body = {**request_body, **top_level_params}
    return apply_omit(request_body, entry.get("omit"))


REQUIRED_STAGE_KEYS = {"stage", "name", "set", "expect_cells", "selectors"}
STAGE_SET_NAMES = {"contract-sweep", "content-blocks"}


def load_sweep_stages(path: Path = SWEEP_STAGES_PATH) -> dict:
    """Parse probes/sweep-stages.yaml — the hand-kept, dated firing-order
    declaration (Phase 11 plan 11-02). Same fail-loud idiom as load_ceilings:
    read, parse, type-check the top-level mapping, check required keys,
    _fail(2, ...) with a named diagnostic on anything malformed. Returns the
    parsed document unchanged (`{"checked": ..., "stages": [...]}`)."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict):
        _fail(2, f"{path}: expected a top-level mapping")
    missing = {"checked", "stages"} - set(data)
    if missing:
        _fail(2, f"{path}: missing required top-level key(s) {sorted(missing)}")
    if not isinstance(data["stages"], list) or not data["stages"]:
        _fail(2, f"{path}: `stages:` must be a non-empty list")
    for stage in data["stages"]:
        if not isinstance(stage, dict):
            _fail(2, f"{path}: each stage entry must be a mapping, got {stage!r}")
        missing_stage = REQUIRED_STAGE_KEYS - set(stage)
        if missing_stage:
            _fail(2, f"{path}: stage {stage.get('stage', '?')!r} missing required key(s) {sorted(missing_stage)}")
        if stage["set"] not in STAGE_SET_NAMES:
            _fail(
                2,
                f"{path}: stage {stage['stage']!r} has unknown set {stage['set']!r}, "
                f"expected one of {sorted(STAGE_SET_NAMES)}",
            )
        if not isinstance(stage["selectors"], list) or not stage["selectors"]:
            _fail(2, f"{path}: stage {stage['stage']!r} `selectors:` must be a non-empty list")
        for sel in stage["selectors"]:
            if not isinstance(sel, dict) or "param" not in sel:
                _fail(2, f"{path}: stage {stage['stage']!r} has a selector missing `param`: {sel!r}")
    return data


def load_registry_row_ids(path: Path = INVENTORY_PATH) -> set[str]:
    """The set of every row id declared in probes/inventory.yaml's `params:`
    list (swept or excluded) — used only by --check-stages to catch a
    sweep-stages.yaml selector naming a row id absent from the registry."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("params"), list):
        _fail(2, f"{path}: expected a top-level `params:` list")
    return {row.get("id") for row in data["params"] if isinstance(row, dict)}


def stage_for_entry(entry: dict, stages: list[dict]) -> int | None:
    """Pure (Phase 11 plan 11-02): the first (ascending `stage:` order) stage
    whose selectors match this probe-set entry, or None if no stage's
    selectors match at all. A selector with no `values:` matches every cell
    of that row; a selector with `values:` matches only cells whose `value`
    is IN the list. First-match-wins: a cell matched by both a value-
    restricted early stage and an unrestricted later stage belongs to the
    earlier stage."""
    for stage in sorted(stages, key=lambda s: s["stage"]):
        for sel in stage["selectors"]:
            if sel["param"] != entry.get("param"):
                continue
            values = sel.get("values")
            if values is None or entry.get("value") in values:
                return stage["stage"]
    return None


def check_stages(
    contract_entries: list[dict],
    content_block_entries: list[dict],
    stages: list[dict],
    registry_ids: set[str],
) -> tuple[int, int, int, int]:
    """--check-stages' core: partitions every declared cell (both generated
    set files) across the declared stages and reports every violation named
    by Phase 11 plan 11-02's own spec:
      - any cell assigned to no stage (stage_for_entry returns None)
      - any stage whose owned count differs from its declared expect_cells
      - any selector naming a row id absent from the registry
      - any stage whose matched cells were drawn from a set file other than
        the one it declares (`set:` vs the entry's actual origin file)
    Returns (checks, problems, total_cells, stage_count)."""
    checks = 0
    problems = 0
    tagged = [(e, "contract-sweep") for e in contract_entries] + [
        (e, "content-blocks") for e in content_block_entries
    ]
    total_cells = len(tagged)
    stages_by_num = {s["stage"]: s for s in stages}
    owned_counts: dict[int, int] = {s["stage"]: 0 for s in stages}

    for entry, origin_set in tagged:
        checks += 1
        stage_num = stage_for_entry(entry, stages)
        if stage_num is None:
            problems += 1
            print(
                f"FAIL check-stages: cell model={entry.get('model')!r} "
                f"param={entry.get('param')!r} value={entry.get('value')!r} "
                f"mode={entry.get('mode')!r} (from {origin_set}) is owned by no declared stage",
                file=sys.stderr,
            )
            continue
        owned_counts[stage_num] += 1
        stage_def = stages_by_num[stage_num]
        if stage_def["set"] != origin_set:
            problems += 1
            print(
                f"FAIL check-stages: stage {stage_num} ({stage_def['name']}) matched a cell "
                f"from set={origin_set!r} but declares set={stage_def['set']!r}",
                file=sys.stderr,
            )

    for s in stages:
        checks += 1
        actual = owned_counts.get(s["stage"], 0)
        if actual != s["expect_cells"]:
            problems += 1
            print(
                f"FAIL check-stages: stage {s['stage']} ({s['name']}) owns {actual} cells, "
                f"expected {s['expect_cells']}",
                file=sys.stderr,
            )

    for s in stages:
        for sel in s["selectors"]:
            checks += 1
            if sel["param"] not in registry_ids:
                problems += 1
                print(
                    f"FAIL check-stages: stage {s['stage']} ({s['name']}) selector names row id "
                    f"{sel['param']!r}, absent from the registry",
                    file=sys.stderr,
                )

    return checks, problems, total_cells, len(stages)


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    # --- probe_id: key-order-independent canonicalization ---
    cases += 1
    body_a = {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]}
    body_b = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 16, "model": "x"}
    pid_a = probe_id("x", "baseline", "none", "default", body_a)
    pid_b = probe_id("x", "baseline", "none", "default", body_b)
    if pid_a != pid_b:
        problems += 1
        print(f"FAIL probe_id: declared-key-order independence broke: {pid_a} != {pid_b}", file=sys.stderr)

    # --- probe_id: a single-character body change produces a different probe_id ---
    cases += 1
    body_c = {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hj"}]}
    pid_c = probe_id("x", "baseline", "none", "default", body_c)
    if pid_c == pid_a:
        problems += 1
        print("FAIL probe_id: a single-character body change did not change the hash", file=sys.stderr)

    # --- probe_id: repeat=None is byte-identical to the pre-Phase-12 5-argument
    #     result, and splits into exactly five `--`-separated segments (D-09) ---
    cases += 1
    pid_no_repeat = probe_id("x", "baseline", "none", "default", body_a, repeat=None)
    if pid_no_repeat != pid_a:
        problems += 1
        print(
            f"FAIL probe_id: repeat=None must be byte-identical to the pre-extension "
            f"result, got {pid_no_repeat!r} != {pid_a!r}",
            file=sys.stderr,
        )
    if len(pid_no_repeat.split("--")) != 5:
        problems += 1
        print(
            f"FAIL probe_id: no-repeat form must split into exactly 5 segments, "
            f"got {pid_no_repeat.split('--')!r}",
            file=sys.stderr,
        )

    # --- probe_id: two calls with the same body and different repeat indices
    #     produce different ids, sharing the same trailing hash segment; the
    #     repeat form splits into six segments whose fifth segment is the
    #     `r`-prefixed index (D-09) ---
    cases += 1
    pid_r1 = probe_id("x", "baseline", "none", "default", body_a, repeat=1)
    pid_r2 = probe_id("x", "baseline", "none", "default", body_a, repeat=2)
    if pid_r1 == pid_r2:
        problems += 1
        print("FAIL probe_id: two different repeat indices produced the same id", file=sys.stderr)
    segments_r1 = pid_r1.split("--")
    segments_r2 = pid_r2.split("--")
    if len(segments_r1) != 6 or len(segments_r2) != 6:
        problems += 1
        print(f"FAIL probe_id: repeat form must split into exactly 6 segments, got {segments_r1!r}", file=sys.stderr)
    if segments_r1[4] != "r1" or segments_r2[4] != "r2":
        problems += 1
        print(
            f"FAIL probe_id: fifth segment must be the r-prefixed repeat index, "
            f"got {segments_r1[4]!r} and {segments_r2[4]!r}",
            file=sys.stderr,
        )
    if segments_r1[-1] != segments_r2[-1]:
        problems += 1
        print("FAIL probe_id: two repeat indices of the same body must share the trailing hash segment", file=sys.stderr)

    # --- load_probe_set: `repeat` validation rejects 0, -1, a string, and a bool
    #     (bool first, since isinstance(True, int) is True in Python) — exit 2,
    #     before any HTTP request (D-09) ---
    for label, bad_repeat_yaml in [
        ("repeat: 0", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    repeat: 0\n"),
        ("repeat: -1", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    repeat: -1\n"),
        ("repeat: a string", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    repeat: \"3\"\n"),
        ("repeat: a boolean", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    repeat: true\n"),
    ]:
        cases += 1
        with tempfile.TemporaryDirectory() as td:
            bad_repeat = Path(td) / "bad-repeat.yaml"
            bad_repeat.write_text(bad_repeat_yaml)
            try:
                load_probe_set(bad_repeat)
                problems += 1
                print(f"FAIL load_probe_set({label}): expected a fail-loud exit, got a return", file=sys.stderr)
            except SystemExit as e:
                if e.code != 2:
                    problems += 1
                    print(f"FAIL load_probe_set({label}): expected exit code 2, got {e.code}", file=sys.stderr)

    # --- apply_omit: omitting a key changes the canonical body -> changes the
    #     probe_id hash (D-04: this is the whole point — a probe can deliberately
    #     test the ABSENCE of a field, and the omission must be visible as a
    #     distinct, re-firable probe_id, never silently collapsed into the same id
    #     as the with-the-key version) ---
    cases += 1
    body_full = {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]}
    body_omitted = apply_omit(body_full, ["max_tokens"])
    if "max_tokens" in body_omitted:
        problems += 1
        print("FAIL apply_omit: the listed key was not removed", file=sys.stderr)
    if body_full != {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]}:
        problems += 1
        print("FAIL apply_omit: mutated the caller's original dict in place", file=sys.stderr)
    pid_full = probe_id("x", "max-tokens", "present", "default", body_full)
    pid_omitted = probe_id("x", "max-tokens", "omitted", "default", body_omitted)
    if pid_full == pid_omitted:
        problems += 1
        print("FAIL apply_omit: omitting a key did not change the probe_id hash", file=sys.stderr)

    # --- apply_omit: no omit_keys returns an equal-but-not-aliased dict ---
    cases += 1
    body_unomitted = apply_omit(body_full, None)
    if body_unomitted != body_full or body_unomitted is body_full:
        problems += 1
        print("FAIL apply_omit: with no omit keys, expected an equal but distinct dict object", file=sys.stderr)

    # --- seen_probe_ids: nonexistent path / zero-byte file -> empty set, no raise ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        missing = Path(td) / "does-not-exist.jsonl"
        s1 = seen_probe_ids(missing)
        if s1 != set():
            problems += 1
            print("FAIL seen_probe_ids: nonexistent file should yield an empty set", file=sys.stderr)
        zero = Path(td) / "zero-byte.jsonl"
        zero.write_text("")
        s2 = seen_probe_ids(zero)
        if s2 != set():
            problems += 1
            print("FAIL seen_probe_ids: zero-byte file should yield an empty set", file=sys.stderr)

        # --- seen_probe_ids: truncated final line is ignored, complete lines kept ---
        cases += 1
        truncated = Path(td) / "truncated.jsonl"
        truncated.write_text(
            json.dumps({"probe_id": "a--baseline--none--default--aaaaaaaa"}) + "\n"
            + json.dumps({"probe_id": "b--baseline--none--default--bbbbbbbb"}) + "\n"
            + '{"probe_id": "c--baseline--none--defau'
        )
        s3 = seen_probe_ids(truncated)
        if s3 != {"a--baseline--none--default--aaaaaaaa", "b--baseline--none--default--bbbbbbbb"}:
            problems += 1
            print(f"FAIL seen_probe_ids: truncated-line handling wrong, got {s3}", file=sys.stderr)

    # --- probe-set fail-loud paths: no probes key / empty list / missing required key ---
    for label, content in [
        ("no probes key", "not_probes: []\n"),
        ("empty probes list", "probes: []\n"),
        ("entry missing required key", "probes:\n  - model: x\n    param: baseline\n"),
    ]:
        cases += 1
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.yaml"
            bad.write_text(content)
            try:
                load_probe_set(bad)
                problems += 1
                print(f"FAIL load_probe_set({label}): expected a fail-loud exit, got a return", file=sys.stderr)
            except SystemExit as e:
                if e.code != 2:
                    problems += 1
                    print(f"FAIL load_probe_set({label}): expected exit code 2, got {e.code}", file=sys.stderr)

    # --- build_record: header VALUES never reach the serialized record, only NAMES ---
    cases += 1
    # Deliberately NOT prefixed `sk-`/`AIza` — the repo's own "no key VALUE in the
    # registries" lint (`grep -rnE '(sk-|AIza)[A-Za-z0-9_-]{12,}' probes/harness/`)
    # scans this whole directory tree, and a realistic-looking fixture secret here
    # would false-positive that check. The tripwire logic under test only cares
    # that an arbitrary string value is found in a serialized record — the prefix
    # shape is irrelevant to what's being verified.
    fake_key = "FAKESELFTESTVALUE-not-a-real-key-0000000000"
    record = build_record(
        pid="x--baseline--none--default--deadbeef",
        vendor="anthropic",
        model_slug="x",
        api_model_id="x-api",
        wire_family="anthropic_messages",
        set_file="probes/sets/smoke.yaml",
        param="baseline",
        value="none",
        mode="default",
        method="POST",
        url="https://api.example.com/v1/messages",
        headers_sent={"x-api-key": fake_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        request_body={"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]},
        attempts=[{
            "n": 1, "status": 200, "retryable": False, "wait_s": None,
            "response_headers": {"request-id": "req_123"},
            "response_body_raw": {"usage": {"input_tokens": 8, "output_tokens": 4}},
            "at": "2026-09-01T00:00:00Z",
        }],
        terminal="verdict",
        retries=0,
        usage={"input_tokens": 8, "output_tokens": 4},
        cost=0.001,
    )
    serialized = json.dumps(record)
    if fake_key in serialized:
        problems += 1
        print("FAIL build_record: a header VALUE leaked into the serialized record", file=sys.stderr)
    if "x-api-key" not in record["request"]["headers_sent"]:
        problems += 1
        print("FAIL build_record: header NAME missing from headers_sent", file=sys.stderr)
    if not (isinstance(record["request"]["headers_sent"], list)
            and all(isinstance(h, str) for h in record["request"]["headers_sent"])):
        problems += 1
        print("FAIL build_record: headers_sent must be a list of strings", file=sys.stderr)

    # --- assert_no_secrets: a leaked key value aborts the run ---
    cases += 1
    leaked_serialized = json.dumps({"note": f"oops leaked {fake_key} here"})
    try:
        assert_no_secrets(leaked_serialized, [fake_key])
        problems += 1
        print("FAIL assert_no_secrets: expected an abort on a leaked key value, got a return", file=sys.stderr)
    except SystemExit:
        pass

    # --- filter_response_headers: org headers dropped, rate-limit/request-id
    #     kept — extended Phase 11 plan 11-03 with Kimi's Msh-* family
    #     (observed live, see the constant's own comment above), and plan
    #     11-04 with set-cookie (observed live: Cloudflare's __cf_bm at
    #     openai/kimi, Alibaba WAF's acw_tc at qwen/zai — both casings) ---
    cases += 1
    raw_headers = {
        "openai-organization": "org-should-not-appear",
        "anthropic-workspace-id": "wrkspc-should-not-appear",
        "msh-org-id": "org-should-not-appear-2",
        "set-cookie": "__cf_bm=should-not-appear; path=/; HttpOnly",
        "Set-Cookie": "acw_tc=should-not-appear-2; path=/; HttpOnly",
        "retry-after": "5",
        "request-id": "req_abc",
        "msh-request-id": "req-should-be-kept",
        "anthropic-ratelimit-requests-remaining": "99",
    }
    filtered = filter_response_headers(raw_headers)
    if "openai-organization" in filtered or "anthropic-workspace-id" in filtered or "msh-org-id" in filtered:
        problems += 1
        print("FAIL filter_response_headers: an org/account header was not dropped", file=sys.stderr)
    if "set-cookie" in filtered or "Set-Cookie" in filtered:
        problems += 1
        print("FAIL filter_response_headers: a set-cookie header was not dropped", file=sys.stderr)
    if "retry-after" not in filtered or "request-id" not in filtered or "msh-request-id" not in filtered:
        problems += 1
        print("FAIL filter_response_headers: rate-limit/request-id header incorrectly dropped", file=sys.stderr)

    # --- ADAPTERS dispatch: every models.yaml row resolves to a registered adapter ---
    cases += 1
    for slug, row in load_models().items():
        if row["wire_family"] not in ADAPTERS:
            problems += 1
            print(f"FAIL ADAPTERS dispatch: {slug} wire_family={row['wire_family']!r} not registered", file=sys.stderr)

    # --- ADAPTERS dispatch: an unknown wire_family is never silently substituted ---
    cases += 1
    if ADAPTERS.get("not-a-real-wire-family") is not None:
        problems += 1
        print("FAIL ADAPTERS dispatch: unknown wire_family unexpectedly resolved to an adapter", file=sys.stderr)

    # --- endpoint_url: an unknown wire_family raises rather than defaulting ---
    cases += 1
    try:
        endpoint_url("not-a-real-wire-family", "https://example.com", "x")
        problems += 1
        print("FAIL endpoint_url: unknown wire_family should raise, not default", file=sys.stderr)
    except ValueError:
        pass

    # --- endpoint_url: exact base_url + family suffix, one model per family ---
    url_cases = [
        ("anthropic_messages", "https://api.anthropic.com/v1", "claude-x",
         "https://api.anthropic.com/v1/messages"),
        ("openai_compat", "https://api.openai.com/v1", "gpt-x",
         "https://api.openai.com/v1/chat/completions"),
        ("gemini", "https://generativelanguage.googleapis.com/v1beta", "gemini-x",
         "https://generativelanguage.googleapis.com/v1beta/models/gemini-x:generateContent"),
    ]
    for family, base, model_id, expected in url_cases:
        cases += 1
        got = endpoint_url(family, base, model_id)
        if got != expected:
            problems += 1
            print(f"FAIL endpoint_url({family}): expected {expected}, got {got}", file=sys.stderr)

    # --- Gemini puts the model id in the URL path, NOT the request body ---
    cases += 1
    gem_body = ADAPTERS["gemini"].build_request("gemini-x", "hi", 16, {})
    if "model" in gem_body:
        problems += 1
        print("FAIL gemini build_request: body must not carry a top-level model field", file=sys.stderr)
    gem_url = ADAPTERS["gemini"].endpoint_url("https://example.com", "gemini-x")
    if "gemini-x" not in gem_url:
        problems += 1
        print("FAIL gemini endpoint_url: model id missing from the URL path", file=sys.stderr)

    # --- The other two families put the model id in the body, NOT the URL path ---
    cases += 1
    for family in ("anthropic_messages", "openai_compat"):
        body = ADAPTERS[family].build_request("model-x", "hi", 16, {})
        if body.get("model") != "model-x":
            problems += 1
            print(f"FAIL {family} build_request: body must carry model at the top level", file=sys.stderr)

    # --- parse_usage: Anthropic fixture, absent cache fields are None, never 0 ---
    cases += 1
    anth_usage = ADAPTERS["anthropic_messages"].parse_usage({"usage": {"input_tokens": 8, "output_tokens": 4}})
    if anth_usage["input_tokens"] != 8 or anth_usage["output_tokens"] != 4:
        problems += 1
        print(f"FAIL anthropic_messages parse_usage: wrong base counts, got {anth_usage}", file=sys.stderr)
    if anth_usage["cache_creation_input_tokens"] is not None or anth_usage["cache_read_input_tokens"] is not None:
        problems += 1
        print("FAIL anthropic_messages parse_usage: an absent field must be None, not 0/other", file=sys.stderr)

    # --- parse_usage: OpenAI-compatible fixture, normalized keys read correctly.
    #     output_tokens (WR-04) is completion_tokens NET of reasoning_tokens (40 =
    #     50 - 10), not the raw completion_tokens value — reasoning_tokens is a
    #     SUBSET of completion_tokens for this family, so netting it here is what
    #     keeps output_tokens/reasoning_tokens additive for ledger.cost_usd ---
    cases += 1
    oc_usage = ADAPTERS["openai_compat"].parse_usage({
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "completion_tokens_details": {"reasoning_tokens": 10},
            "prompt_tokens_details": {"cached_tokens": 20},
        }
    })
    if (oc_usage["input_tokens"], oc_usage["output_tokens"], oc_usage["reasoning_tokens"], oc_usage["cached_tokens"]) != (100, 40, 10, 20):
        problems += 1
        print(f"FAIL openai_compat parse_usage: wrong normalized counts, got {oc_usage}", file=sys.stderr)

    # --- parse_usage: OpenAI-compatible fixture with NO reasoning_tokens reported —
    #     output_tokens must pass completion_tokens through unchanged, never net
    #     against a None it can't subtract ---
    cases += 1
    oc_usage_no_reasoning = ADAPTERS["openai_compat"].parse_usage({
        "usage": {"prompt_tokens": 100, "completion_tokens": 50}
    })
    if oc_usage_no_reasoning["output_tokens"] != 50 or oc_usage_no_reasoning["reasoning_tokens"] is not None:
        problems += 1
        print(f"FAIL openai_compat parse_usage: no-reasoning case should pass completion_tokens through unchanged, got {oc_usage_no_reasoning}", file=sys.stderr)

    # --- parse_usage: Gemini fixture with thoughtsTokenCount present ---
    cases += 1
    gem_usage_full = ADAPTERS["gemini"].parse_usage({
        "usageMetadata": {
            "promptTokenCount": 12,
            "candidatesTokenCount": 6,
            "thoughtsTokenCount": 3,
            "cachedContentTokenCount": 0,
        }
    })
    if gem_usage_full["reasoning_tokens"] != 3:
        problems += 1
        print(f"FAIL gemini parse_usage: thoughtsTokenCount not read, got {gem_usage_full}", file=sys.stderr)

    # --- parse_usage: Gemini fixture with thoughtsTokenCount ABSENT -> None, never 0 ---
    cases += 1
    gem_usage_absent = ADAPTERS["gemini"].parse_usage({
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 6}
    })
    if gem_usage_absent["reasoning_tokens"] is not None:
        problems += 1
        print("FAIL gemini parse_usage: absent thoughtsTokenCount must be None, not 0", file=sys.stderr)

    # --- parse_usage: OpenAI-compatible fed a DeepSeek-shaped body, agreeing cache signals ---
    cases += 1
    dseek_agree = ADAPTERS["openai_compat"].parse_usage({
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "prompt_tokens_details": {"cached_tokens": 20},
            "prompt_cache_hit_tokens": 20,
            "prompt_cache_miss_tokens": 80,
        }
    })
    if dseek_agree["cache_hit_tokens"] != 20 or dseek_agree["cache_miss_tokens"] != 80 or dseek_agree["cached_tokens"] != 20:
        problems += 1
        print(f"FAIL openai_compat parse_usage: DeepSeek dual-cache fields not read, got {dseek_agree}", file=sys.stderr)
    if dseek_agree.get("cache_disagreement") is not None:
        problems += 1
        print("FAIL openai_compat parse_usage: agreeing cache signals must not be flagged as a disagreement", file=sys.stderr)

    # --- parse_usage: OpenAI-compatible fed a DeepSeek-shaped body, DISAGREEING cache signals ---
    cases += 1
    dseek_disagree = ADAPTERS["openai_compat"].parse_usage({
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "prompt_tokens_details": {"cached_tokens": 20},
            "prompt_cache_hit_tokens": 15,
            "prompt_cache_miss_tokens": 85,
        }
    })
    if dseek_disagree.get("cache_disagreement") is None:
        problems += 1
        print("FAIL openai_compat parse_usage: disagreeing cache signals must be flagged, not silently resolved", file=sys.stderr)

    # --- derive_terminal / build_record: a synthetic multi-attempt result is stored
    #     in attempt order, the terminal attempt last, retries = non-terminal count ---
    cases += 1
    synthetic_attempts = [
        {"n": 1, "status": 429, "retryable": True, "action": "retry", "wait_s": 1.0,
         "response_headers": {}, "response_body_raw": {}, "at": "2026-09-01T00:00:00Z"},
        {"n": 2, "status": 429, "retryable": True, "action": "retry", "wait_s": 2.0,
         "response_headers": {}, "response_body_raw": {}, "at": "2026-09-01T00:00:02Z"},
        {"n": 3, "status": 200, "retryable": False, "action": "verdict", "wait_s": None,
         "response_headers": {}, "response_body_raw": {"usage": {}}, "at": "2026-09-01T00:00:05Z"},
    ]
    syn_terminal, syn_retries = derive_terminal(synthetic_attempts)
    if (syn_terminal, syn_retries) != ("verdict", 2):
        problems += 1
        print(f"FAIL derive_terminal: expected ('verdict', 2), got {(syn_terminal, syn_retries)}", file=sys.stderr)
    syn_record = build_record(
        pid="x--baseline--none--default--deadbeef",
        vendor="anthropic",
        model_slug="x",
        api_model_id="x-api",
        wire_family="anthropic_messages",
        set_file="probes/sets/smoke.yaml",
        param="baseline",
        value="none",
        mode="default",
        method="POST",
        url="https://api.example.com/v1/messages",
        headers_sent={"x-api-key": "irrelevant-for-this-fixture"},
        request_body={"model": "x", "max_tokens": 16, "messages": []},
        attempts=synthetic_attempts,
        terminal=syn_terminal,
        retries=syn_retries,
        usage={},
        cost=None,
    )
    if syn_record["attempts"] != synthetic_attempts:
        problems += 1
        print("FAIL build_record: attempts array was not written in attempt order, unchanged", file=sys.stderr)
    if syn_record["attempts"][-1]["action"] != "verdict":
        problems += 1
        print("FAIL build_record: the terminal attempt must be last in the attempts array", file=sys.stderr)
    if syn_record["retries"] != 2:
        problems += 1
        print(f"FAIL build_record: retries should equal 2 (non-terminal attempts), got {syn_record['retries']}", file=sys.stderr)
    if syn_record["terminal"] != "verdict":
        problems += 1
        print(f"FAIL build_record: terminal should name the final branch ('verdict'), got {syn_record['terminal']!r}", file=sys.stderr)

    # --- resume: a terminal:retry_exhausted record is skipped by default, and
    #     re-included via --refire-exhausted's refire_exhausted=True ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        exhausted_fixture = Path(td) / "vendor.jsonl"
        exhausted_pid = "y--baseline--none--default--eeeeeeee"
        exhausted_fixture.write_text(json.dumps({"probe_id": exhausted_pid, "terminal": "retry_exhausted"}) + "\n")

        default_seen = seen_probe_ids(exhausted_fixture)
        if exhausted_pid not in default_seen:
            problems += 1
            print("FAIL seen_probe_ids: a retry_exhausted record must be in the default seen-set (resume-skipped)", file=sys.stderr)

        refire_seen = seen_probe_ids(exhausted_fixture, refire_exhausted=True)
        if exhausted_pid in refire_seen:
            problems += 1
            print("FAIL seen_probe_ids: refire_exhausted=True must exclude retry_exhausted ids from the seen-set", file=sys.stderr)

    # --- resume (WR-02): a terminal:skipped_ceiling record is skipped by default,
    #     re-included via --refire-ceiling-skipped's refire_ceiling_skipped=True, and
    #     the two refire flags are independent (each excludes only its own terminal) ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        ceiling_fixture = Path(td) / "vendor.jsonl"
        ceiling_pid = "z--baseline--none--default--cccccccc"
        exhausted_pid2 = "y--baseline--none--default--eeeeeeee"
        ceiling_fixture.write_text(
            json.dumps({"probe_id": ceiling_pid, "terminal": "skipped_ceiling"}) + "\n"
            + json.dumps({"probe_id": exhausted_pid2, "terminal": "retry_exhausted"}) + "\n"
        )

        default_seen = seen_probe_ids(ceiling_fixture)
        if ceiling_pid not in default_seen:
            problems += 1
            print("FAIL seen_probe_ids: a skipped_ceiling record must be in the default seen-set (resume-skipped)", file=sys.stderr)

        refire_ceiling_seen = seen_probe_ids(ceiling_fixture, refire_ceiling_skipped=True)
        if ceiling_pid in refire_ceiling_seen:
            problems += 1
            print("FAIL seen_probe_ids: refire_ceiling_skipped=True must exclude skipped_ceiling ids from the seen-set", file=sys.stderr)
        if exhausted_pid2 not in refire_ceiling_seen:
            problems += 1
            print("FAIL seen_probe_ids: refire_ceiling_skipped=True must NOT also exclude retry_exhausted ids (independent flags)", file=sys.stderr)

    # --- build_skipped_ceiling_record: terminal + a reason naming vendor and threshold ---
    cases += 1
    skip_reason = "zai total $1.500000 reached its $1.50 soft sub-ceiling"
    skip_record = build_skipped_ceiling_record(
        pid="s--baseline--none--default--ffffffff",
        vendor="zai",
        model_slug="glm-5.3",
        api_model_id="glm-5.3",
        wire_family="openai_compat",
        set_file="probes/sets/smoke.yaml",
        param="baseline",
        value="none",
        mode="default",
        reason=skip_reason,
    )
    if skip_record["terminal"] != "skipped_ceiling":
        problems += 1
        print(f"FAIL build_skipped_ceiling_record: terminal should be 'skipped_ceiling', got {skip_record['terminal']!r}", file=sys.stderr)
    if "zai" not in skip_record["reason"] or "1.5" not in skip_record["reason"]:
        problems += 1
        print(f"FAIL build_skipped_ceiling_record: reason must name the vendor and the numeric threshold, got {skip_record['reason']!r}", file=sys.stderr)
    if skip_record["attempts"] != []:
        problems += 1
        print("FAIL build_skipped_ceiling_record: a dropped probe was never fired, attempts must be empty", file=sys.stderr)

    # --- structural: ceiling_verdict is consulted AFTER both the JSONL append and
    #     the ledger append in the same loop body (D-06 — evidence is always logged
    #     and counted before any ceiling check can act on it) ---
    cases += 1
    main_src = inspect.getsource(main)
    jsonl_write_idx = main_src.find('with raw_path.open("a") as f:\n            f.write(serialized')
    ledger_append_idx = main_src.find("ledger.append(LEDGER_PATH")
    ceiling_check_idx = main_src.find("ledger.ceiling_verdict(")
    if not (0 <= jsonl_write_idx < ledger_append_idx < ceiling_check_idx):
        problems += 1
        print(
            "FAIL main(): ledger.ceiling_verdict must be consulted strictly AFTER "
            "both the JSONL append and the ledger append in the same loop body "
            f"(indices: jsonl={jsonl_write_idx}, ledger={ledger_append_idx}, ceiling={ceiling_check_idx})",
            file=sys.stderr,
        )

    # --- stage_for_entry (Phase 11 plan 11-02): first-match-wins precedence —
    #     a cell matched by BOTH an early value-restricted selector and a
    #     later unrestricted selector for the same row belongs to the
    #     EARLIER stage, never the later one ---
    cases += 1
    precedence_stages = [
        {
            "stage": 1,
            "name": "early",
            "set": "contract-sweep",
            "expect_cells": 1,
            "selectors": [{"param": "fixture-row", "values": ["500"]}],
        },
        {
            "stage": 5,
            "name": "late",
            "set": "contract-sweep",
            "expect_cells": 2,
            "selectors": [{"param": "fixture-row"}],
        },
    ]
    restricted_entry = {"model": "m1", "param": "fixture-row", "value": "500", "mode": "default"}
    unrestricted_entry = {"model": "m1", "param": "fixture-row", "value": "999", "mode": "default"}
    stage_num = stage_for_entry(restricted_entry, precedence_stages)
    if stage_num != 1:
        problems += 1
        print(
            f"FAIL stage_for_entry: a cell matched by both stage 1's restricted "
            f"selector and stage 5's unrestricted selector expected stage 1, got {stage_num}",
            file=sys.stderr,
        )
    stage_num2 = stage_for_entry(unrestricted_entry, precedence_stages)
    if stage_num2 != 5:
        problems += 1
        print(
            f"FAIL stage_for_entry: a cell matched only by stage 5's unrestricted "
            f"selector expected stage 5, got {stage_num2}",
            file=sys.stderr,
        )

    # --- stage_for_entry: a cell matched by no selector at all returns None ---
    cases += 1
    no_match_entry = {"model": "m1", "param": "no-such-row", "value": "1", "mode": "default"}
    if stage_for_entry(no_match_entry, precedence_stages) is not None:
        problems += 1
        print("FAIL stage_for_entry: a cell matched by no selector should return None", file=sys.stderr)

    # --- load_sweep_stages: fail-loud on a malformed file (missing required
    #     top-level key) ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        bad_stages_path = Path(td) / "sweep-stages.yaml"
        bad_stages_path.write_text("checked: 2026-09-01\n")
        try:
            load_sweep_stages(bad_stages_path)
            problems += 1
            print("FAIL selftest: load_sweep_stages did not abort on a file missing `stages:`", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL selftest: load_sweep_stages(missing stages) expected exit 2, got {e.code}", file=sys.stderr)

    # --- --stage: an out-of-range stage argument exits 2, a named diagnostic,
    #     not a silently empty run — via subprocess so this never mutates this
    #     process's own sys.argv or state ---
    cases += 1
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--set",
            str(CONTRACT_SWEEP_GENERATED_PATH),
            "--stage",
            "9",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 2:
        problems += 1
        print(f"FAIL selftest: --stage 9 (out of range) expected exit 2, got {result.returncode}", file=sys.stderr)
    if not result.stderr.strip():
        problems += 1
        print("FAIL selftest: --stage 9 (out of range) printed nothing to stderr", file=sys.stderr)

    # --- substitute_image_payload: pure, replaces the token at any nesting
    #     depth, never mutates its argument (Phase 11 plan 11-03, MODAL-01) ---
    cases += 1
    original_block = {
        "content": [
            {"type": "image", "source": {"type": "base64", "data": "{{IMAGE_BASE64_PLACEHOLDER}}"}},
            {"type": "text", "text": "hi"},
        ]
    }
    before_snapshot = copy.deepcopy(original_block)
    substituted_block = substitute_image_payload(original_block, "PAYLOAD")
    if original_block != before_snapshot:
        problems += 1
        print("FAIL substitute_image_payload: mutated its argument in place", file=sys.stderr)
    if substituted_block["content"][0]["source"]["data"] != "PAYLOAD":
        problems += 1
        print("FAIL substitute_image_payload: token not substituted at a nested depth", file=sys.stderr)
    if "{{IMAGE_BASE64_PLACEHOLDER}}" in json.dumps(substituted_block):
        problems += 1
        print("FAIL substitute_image_payload: placeholder token survived substitution", file=sys.stderr)

    # --- build_entry_request: two entries sharing the SAME body_template object
    #     (the exact YAML-anchor-sharing hazard, RESEARCH.md Pattern 2) must
    #     produce independent bodies — mutating one must never leak into the
    #     other, and the shared source object itself must stay unmutated ---
    cases += 1
    shared_template = {
        "anthropic_messages": {
            "content": [{"type": "image", "source": {"type": "base64", "data": "{{IMAGE_BASE64_PLACEHOLDER}}"}}]
        }
    }
    aliased_entry_a = {
        "model": "m", "param": "image-input", "value": "content-block", "mode": "default",
        "max_tokens": 64, "body_template": shared_template,
    }
    aliased_entry_b = {
        "model": "m", "param": "image-input", "value": "content-block", "mode": "default",
        "max_tokens": 64, "body_template": shared_template,
    }
    fake_row = {"wire_family": "anthropic_messages", "api_model_id": "m-api"}
    fake_adapter = ADAPTERS["anthropic_messages"]
    body_a = build_entry_request(aliased_entry_a, fake_row, fake_adapter)
    body_b = build_entry_request(aliased_entry_b, fake_row, fake_adapter)
    body_a["messages"][0]["content"][0]["source"]["data"] = "MUTATED"
    if body_b["messages"][0]["content"][0]["source"]["data"] == "MUTATED":
        problems += 1
        print("FAIL build_entry_request: two entries sharing one body_template object leaked a mutation", file=sys.stderr)
    if "{{IMAGE_BASE64_PLACEHOLDER}}" not in json.dumps(shared_template):
        problems += 1
        print("FAIL build_entry_request: mutated the original shared body_template object", file=sys.stderr)

    # --- build_entry_request: a family key absent from body_template is a
    #     registry defect — fail loud (exit 2), naming the entry, never a
    #     silently-empty body (Phase 11 plan 11-03) ---
    cases += 1
    entry_missing_family = {
        "model": "m", "param": "image-input", "value": "content-block", "mode": "default",
        "max_tokens": 64, "body_template": {"gemini": {"parts": [{"text": "hi"}]}},
    }
    try:
        build_entry_request(entry_missing_family, fake_row, fake_adapter)
        problems += 1
        print(
            "FAIL build_entry_request: expected a fail-loud exit when the family key "
            "is absent from body_template",
            file=sys.stderr,
        )
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_entry_request: expected exit code 2, got {e.code}", file=sys.stderr)

    # --- apply_max_tokens_field_override: a row declaring max_tokens_field
    #     renames the key; absent (every model but gpt-5-6-sol) is a no-op
    #     (Phase 11 plan 11-04, D-09 "fix-before-fire") ---
    cases += 1
    body_before = {"model": "m", "max_tokens": 64, "messages": []}
    overridden_row = {"max_tokens_field": "max_completion_tokens"}
    body_after = apply_max_tokens_field_override(body_before, overridden_row)
    if "max_tokens" in body_after or body_after.get("max_completion_tokens") != 64:
        problems += 1
        print(
            f"FAIL apply_max_tokens_field_override: expected max_tokens renamed to "
            f"max_completion_tokens, got {body_after!r}",
            file=sys.stderr,
        )
    if body_before != {"model": "m", "max_tokens": 64, "messages": []}:
        problems += 1
        print("FAIL apply_max_tokens_field_override: mutated the caller's original dict in place", file=sys.stderr)

    cases += 1
    no_override_row = {"wire_family": "anthropic_messages"}
    body_unchanged = apply_max_tokens_field_override(body_before, no_override_row)
    if body_unchanged != body_before:
        problems += 1
        print(
            f"FAIL apply_max_tokens_field_override: a row with no max_tokens_field "
            f"should be a no-op, got {body_unchanged!r}",
            file=sys.stderr,
        )

    # --- load_probe_set: `top_level_params` validation rejects a non-mapping
    #     value (a string, a list) — exit 2, before any HTTP request
    #     (Phase 12 plan 12-05, mirrors `repeat`'s own validation battery
    #     above for a different optional key) ---
    for label, bad_tlp_yaml in [
        ("top_level_params: a string", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    top_level_params: \"not-a-mapping\"\n"),
        ("top_level_params: a list", "probes:\n  - model: x\n    param: baseline\n    value: none\n    mode: default\n    top_level_params: [1, 2]\n"),
    ]:
        cases += 1
        with tempfile.TemporaryDirectory() as td:
            bad_tlp = Path(td) / "bad-top-level-params.yaml"
            bad_tlp.write_text(bad_tlp_yaml)
            try:
                load_probe_set(bad_tlp)
                problems += 1
                print(f"FAIL load_probe_set({label}): expected a fail-loud exit, got a return", file=sys.stderr)
            except SystemExit as e:
                if e.code != 2:
                    problems += 1
                    print(f"FAIL load_probe_set({label}): expected exit code 2, got {e.code}", file=sys.stderr)

    # --- build_entry_request: a declared `top_level_params` mapping is
    #     merged into the built body AT THE TOP LEVEL and changes the
    #     probe_id hash (Phase 12 plan 12-05) — the whole point of the
    #     grammar addition is reaching a field the `gemini` family's own
    #     `extra_params` merge (nested inside `generationConfig`) cannot ---
    cases += 1

    class _FakeGeminiAdapter:
        @staticmethod
        def build_request(api_model_id, prompt, max_tokens, extra_params):
            return {"contents": [], "generationConfig": {"maxOutputTokens": max_tokens, **(extra_params or {})}}

    tlp_row = {"wire_family": "gemini", "api_model_id": "g-api"}
    entry_without_tlp = {"model": "g", "param": "service-tier-audit", "value": "omitted", "mode": "default", "max_tokens": 16}
    entry_with_tlp = {
        "model": "g", "param": "service-tier-audit", "value": "standard", "mode": "default",
        "max_tokens": 16, "top_level_params": {"serviceTier": "standard"},
    }
    body_without_tlp = build_entry_request(entry_without_tlp, tlp_row, _FakeGeminiAdapter)
    body_with_tlp = build_entry_request(entry_with_tlp, tlp_row, _FakeGeminiAdapter)
    if body_with_tlp.get("serviceTier") != "standard":
        problems += 1
        print(f"FAIL build_entry_request(top_level_params): expected serviceTier at the top level, got {body_with_tlp!r}", file=sys.stderr)
    if "serviceTier" in body_with_tlp.get("generationConfig", {}):
        problems += 1
        print("FAIL build_entry_request(top_level_params): serviceTier leaked into generationConfig, must be top-level only", file=sys.stderr)
    pid_without_tlp = probe_id("g", "service-tier-audit", "omitted", "default", body_without_tlp)
    pid_with_tlp = probe_id("g", "service-tier-audit", "standard", "default", body_with_tlp)
    if pid_without_tlp == pid_with_tlp:
        problems += 1
        print("FAIL build_entry_request(top_level_params): merging a top_level_params key did not change the probe_id hash", file=sys.stderr)

    # --- load_content_block_set: fail-loud paths — empty list, absent key,
    #     entry missing a required key (mirrors load_probe_set's own battery
    #     above, Phase 11 plan 11-03) ---
    for label, content in [
        ("no content_block_probes key", "not_content_block_probes: []\n"),
        ("empty content_block_probes list", "content_block_probes: []\n"),
        (
            "entry missing required key",
            "content_block_probes:\n  - model: x\n    param: image-input\n",
        ),
    ]:
        cases += 1
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.yaml"
            bad.write_text(content)
            try:
                load_content_block_set(bad)
                problems += 1
                print(
                    f"FAIL load_content_block_set({label}): expected a fail-loud exit, got a return",
                    file=sys.stderr,
                )
            except SystemExit as e:
                if e.code != 2:
                    problems += 1
                    print(
                        f"FAIL load_content_block_set({label}): expected exit code 2, got {e.code}",
                        file=sys.stderr,
                    )

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="runner.py",
        usage="runner.py --set <probes/sets/*.yaml> [--dry-run] [--stage N] [--refire-exhausted] "
        "[--refire-ceiling-skipped] | runner.py --content-block-set <probes/sets/generated/"
        "content-blocks.yaml> [--dry-run] [--stage N] | --check-stages | --selftest",
    )
    parser.add_argument("--set", dest="set_path")
    parser.add_argument(
        "--content-block-set",
        dest="content_block_set_path",
        help="fire probes/sets/generated/content-blocks.yaml's content_block_probes: "
        "grammar (MODAL-01, image-input/anthropic-cache-control-block) — mutually "
        "exclusive with --set, which refuses this grammar loudly",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument(
        "--stage",
        type=int,
        help="filter the loaded --set probe set to only the cells "
        "probes/sweep-stages.yaml assigns to this stage number, before firing "
        "(combine with --dry-run to inspect the slice before it is billed)",
    )
    parser.add_argument(
        "--check-stages",
        action="store_true",
        help="no-firing mode: load both generated set files plus "
        "probes/sweep-stages.yaml and report any cell owned by no stage, any "
        "stage whose owned count differs from its declared expect_cells, any "
        "selector naming a row id absent from the registry, or any stage "
        "drawing from a set file whose entries it cannot own",
    )
    parser.add_argument(
        "--refire-exhausted",
        action="store_true",
        help="exclude terminal:retry_exhausted probe_ids from the resume-skip set, "
        "so a probe that spent its full retry budget can be deliberately re-fired "
        "(default: those ids stay in the seen-set and are skipped, HARN-04)",
    )
    parser.add_argument(
        "--refire-ceiling-skipped",
        action="store_true",
        help="exclude terminal:skipped_ceiling probe_ids from the resume-skip set, "
        "so a probe dropped by a vendor sub-ceiling breach can be deliberately "
        "re-fired after ceilings.yaml is raised (default: those ids stay in the "
        "seen-set and are permanently skipped, WR-02)",
    )
    args = parser.parse_args()

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if args.check_stages:
        stages_doc = load_sweep_stages()
        registry_ids = load_registry_row_ids()
        contract_entries = load_probe_set(str(CONTRACT_SWEEP_GENERATED_PATH))
        content_block_entries = load_content_block_set(CONTENT_BLOCKS_GENERATED_PATH)
        checks, problems, total_cells, stage_count = check_stages(
            contract_entries, content_block_entries, stages_doc["stages"], registry_ids
        )
        print(f"{total_cells} cells across {stage_count} stages ({checks} checks run)")
        print(f"{problems} problem(s)")
        return 1 if problems else 0

    if args.set_path and args.content_block_set_path:
        _fail(2, "--set and --content-block-set are mutually exclusive")

    if not args.set_path and not args.content_block_set_path:
        print(
            "usage: runner.py --set <probes/sets/*.yaml> [--dry-run] [--stage N] "
            "[--refire-exhausted] [--refire-ceiling-skipped] | runner.py --content-block-set "
            "<probes/sets/generated/content-blocks.yaml> [--dry-run] [--stage N] | "
            "--check-stages | --selftest",
            file=sys.stderr,
        )
        return 2

    # Either grammar's file path is used identically downstream for the
    # `set_file` field every JSONL record carries (D-08) — the loader called
    # above is the only place the two grammars actually diverge.
    active_set_path = args.content_block_set_path or args.set_path
    if args.content_block_set_path:
        probes = load_content_block_set(args.content_block_set_path)
    else:
        probes = load_probe_set(args.set_path)

    if args.stage is not None:
        stages_doc = load_sweep_stages()
        stage_numbers = sorted(s["stage"] for s in stages_doc["stages"])
        if args.stage not in stage_numbers:
            _fail(2, f"--stage {args.stage}: not a declared stage (declared stages: {stage_numbers})")
        kept = [e for e in probes if stage_for_entry(e, stages_doc["stages"]) == args.stage]
        print(f"--stage {args.stage}: kept {len(kept)} of {len(probes)} cells")
        probes = kept

    models = load_models()
    prices = load_prices()
    ceilings = load_ceilings()

    all_keys = client.load_keys(SECRETS_PATH)
    all_key_values = list(all_keys.values())

    # Vendor -> the skip_vendor reason that triggered dropping its remaining probes
    # (D-06). Populated only by a ceiling check between probes, below; never
    # pre-populated, since the whole point is that this is discovered mid-run.
    skipped_vendors: dict[str, str] = {}

    problems = 0
    for entry in probes:
        model_slug = entry["model"]
        if model_slug not in models:
            print(f"unknown model slug in probe set: {model_slug}", file=sys.stderr)
            problems += 1
            continue
        row = models[model_slug]
        vendor = row["vendor"]
        wire_family = row["wire_family"]
        adapter = ADAPTERS.get(wire_family)
        if adapter is None:
            print(f"no adapter registered for wire_family={wire_family}", file=sys.stderr)
            problems += 1
            continue

        # build_entry_request (Phase 11 plan 11-03, MODAL-01) is the single point
        # where either grammar's request body is built — a content-block entry
        # (carries body_template) or a scalar entry (adapter.build_request() +
        # apply_omit(), unchanged). Everything below this line is shared by both
        # paths unmodified: probe_id, the dry-run print, the resume-skip scan,
        # the vendor-skip record, the send, the per-attempt header filter,
        # build_record, assert_no_secrets, the JSONL append, the ledger append
        # and the between-probes ceiling check.
        request_body = build_entry_request(entry, row, adapter)
        pid = probe_id(
            model_slug, entry["param"], entry["value"], entry["mode"], request_body,
            repeat=entry.get("repeat"),
        )

        # Rule 1 fix (plan 09-02): dry-run is checked BEFORE the resume-skip scan, not
        # after. Dry-run never touches disk, so an already-logged probe_id has nothing
        # to protect it from — showing every declared entry's would-be request is the
        # whole point of --dry-run, including one whose live record already exists
        # (e.g. the smoke set's claude-haiku-4-5 entry, fired in plan 09-01).
        if args.dry_run:
            print(f"DRY-RUN {pid}")
            print(json.dumps(request_body, sort_keys=True, separators=(",", ":")))
            continue

        raw_path = RAW_DIR / f"{vendor}.jsonl"
        seen = seen_probe_ids(
            raw_path,
            refire_exhausted=args.refire_exhausted,
            refire_ceiling_skipped=args.refire_ceiling_skipped,
        )
        if pid in seen:
            print(f"SKIP {pid} (already logged)")
            continue

        if vendor in skipped_vendors:
            # D-06: this vendor's sub-ceiling was already breached by an earlier
            # probe in this same run — drop this one WITHOUT firing it, but write a
            # record so the skip is visible evidence, never a silent absence.
            skip_reason = skipped_vendors[vendor]
            skip_record = build_skipped_ceiling_record(
                pid=pid,
                vendor=vendor,
                model_slug=model_slug,
                api_model_id=row["api_model_id"],
                wire_family=wire_family,
                set_file=str(active_set_path),
                param=entry["param"],
                value=entry["value"],
                mode=entry["mode"],
                reason=skip_reason,
            )
            skip_serialized = json.dumps(skip_record)
            assert_no_secrets(skip_serialized, all_key_values)
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            with raw_path.open("a") as f:
                f.write(skip_serialized + "\n")
                f.flush()
            print(f"SKIP-CEILING {pid}: {skip_reason}")
            problems += 1
            continue

        key_env_var = row["key_env_var"]
        key_value = all_keys.get(key_env_var)
        if not key_value:
            print(f"missing key: {key_env_var} not found in {SECRETS_PATH}", file=sys.stderr)
            problems += 1
            continue

        headers_sent = {**adapter.auth_headers(key_value), "Content-Type": "application/json"}
        url = endpoint_url(wire_family, row["base_url"], row["api_model_id"])

        attempts = client.send_with_retry(url, request_body, headers_sent, max_attempts=DEFAULT_MAX_ATTEMPTS)
        for a in attempts:
            # D-09 header hygiene applies to EVERY attempt's response headers, not
            # just the terminal one — an org/account-identifying header could arrive
            # on a retried-away attempt just as easily as the final one.
            a["response_headers"] = filter_response_headers(a["response_headers"])

        last = attempts[-1]
        status = last["status"]
        resp_body = last["response_body_raw"]
        at = last["at"]
        terminal, retries = derive_terminal(attempts)
        if terminal == "exhausted":
            terminal = "retry_exhausted"

        usage: dict = {}
        cost = None
        if terminal == "verdict" and status == 200 and isinstance(resp_body, dict):
            usage = adapter.parse_usage(resp_body)
            price_row = prices.get(model_slug)
            if price_row:
                cost = ledger.cost_usd(usage, price_row)
        else:
            problems += 1

        record = build_record(
            pid=pid,
            vendor=vendor,
            model_slug=model_slug,
            api_model_id=row["api_model_id"],
            wire_family=wire_family,
            set_file=str(active_set_path),
            param=entry["param"],
            value=entry["value"],
            mode=entry["mode"],
            method="POST",
            url=client.mask_url(url),
            headers_sent=headers_sent,
            request_body=request_body,
            attempts=attempts,
            terminal=terminal,
            retries=retries,
            usage=usage,
            cost=cost,
        )

        serialized = json.dumps(record)
        assert_no_secrets(serialized, all_key_values)

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        with raw_path.open("a") as f:
            f.write(serialized + "\n")
            f.flush()

        if cost is not None:
            price_row = prices.get(model_slug, {})
            ledger.append(LEDGER_PATH, {
                "probe_id": pid,
                "vendor": vendor,
                "model_slug": model_slug,
                "tokens": usage,
                "price_row": price_row,
                "cost_usd": cost,
                "recorded_at": at,
            })

        print(f"OK {pid} status={status} terminal={terminal} retries={retries} cost_usd={cost}")

        # Ceiling check strictly BETWEEN probes (D-06) — this line runs only after
        # BOTH the JSONL record and (when applicable) the ledger line for THIS probe
        # are already flushed to disk above, never before: a ceiling breach must
        # never discard a response the harness already paid for. totals() recomputes
        # by summing the whole ledger file (D-07) — no running total is carried
        # across the loop.
        raw_totals = ledger.totals(LEDGER_PATH)
        verdict_action, verdict_reason, verdict_vendors = ledger.ceiling_verdict(flatten_totals(raw_totals), ceilings)
        if verdict_action == "stop_global":
            print(f"STOP (global ceiling breached): {verdict_reason}", file=sys.stderr)
            print(json.dumps(raw_totals, indent=2, default=str))
            return 1
        elif verdict_action == "skip_vendor":
            # D-03 (2026-09-01, CR-02 fix): `verdict_vendors` is the authoritative,
            # machine-readable breaching-vendor list — every one of them is added,
            # never just a reason-string parse of the first (the retired
            # first-word-of-the-reason-string convention silently dropped every
            # simultaneous breach after the first).
            for breach_vendor in verdict_vendors:
                skipped_vendors[breach_vendor] = verdict_reason
            print(f"CEILING skip_vendor: {verdict_reason}", file=sys.stderr)
        elif verdict_action == "warn":
            print(f"CEILING warn: {verdict_reason}", file=sys.stderr)

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
