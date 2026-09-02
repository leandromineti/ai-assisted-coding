#!/usr/bin/env python3
"""scripts/classify-probes.py — reads the declared cell universe
(probes/sets/generated/{contract-sweep,content-blocks,skipped-cells}.yaml, D-11),
every probes/raw/*.jsonl (wire evidence), probes/inventory.yaml +
probes/harness/models.yaml (row order + per-wire-family name resolution), and
probes/classified/overrides.yaml (hand-kept, D-08), and writes
probes/classified/contract-sweep.yaml — one row per declared cell (scalar +
content-block) plus every declared skip (MTX-01). The written file's own header
comment states the three counts, derived at render time from the loaded
declared-cell YAMLs (classified_header()) — never hard-coded here, so this
docstring deliberately carries no digits that could go stale the way the old
CLASSIFIED_HEADER constant did (Phase 11.1 plan 01, D-08's fix).

    python3 scripts/classify-probes.py                 # regenerate + print a counted summary
    python3 scripts/classify-probes.py --check          # drift-check against disk
    python3 scripts/classify-probes.py --selftest       # run the embedded fixture battery
    python3 scripts/classify-probes.py --raw-dir <dir>  # override probes/raw (testing only)

Exit codes: 0 clean, 1 problems recorded (--check/--selftest only), 2 bad invocation
or malformed/missing input — including no readable raw evidence at all (no
probes/raw/*.jsonl file, or every one empty): the fail-loud path never writes an
empty-but-valid classified file for a missing evidence base.

Joins each declared cell to its evidence by recomputing the EXACT probe_id
runner.probe_id() would assign it: this module imports probe_id()/apply_omit()
and every wire family's adapter.build_request() directly from probes/harness/
rather than reimplementing the hash, so the generator and the harness that produced
the evidence can never independently drift apart — a join-key mismatch would
otherwise silently render every fired cell 'unfired' rather than failing loud.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBES_DIR = REPO_ROOT / "probes"
HARNESS_DIR = PROBES_DIR / "harness"

# probes/harness/runner.py's own top-level `import client` / `import ledger` and
# adapters/__init__.py's `from . import ...` only resolve once HARNESS_DIR is on
# sys.path — Python only auto-adds an ENTRY script's own directory, not an imported
# module's, so this insert is load-bearing, not decoration.
sys.path.insert(0, str(HARNESS_DIR))
import runner as harness_runner  # noqa: E402  probe_id(), apply_omit() — single source of truth for the hash
from adapters import ADAPTERS  # noqa: E402  build_request() per wire family

INVENTORY_PATH = PROBES_DIR / "inventory.yaml"
MODELS_PATH = HARNESS_DIR / "models.yaml"
CONTRACT_SWEEP_PATH = PROBES_DIR / "sets" / "generated" / "contract-sweep.yaml"
CONTENT_BLOCKS_PATH = PROBES_DIR / "sets" / "generated" / "content-blocks.yaml"
SKIPPED_CELLS_PATH = PROBES_DIR / "sets" / "generated" / "skipped-cells.yaml"
CLASSIFIED_DIR = PROBES_DIR / "classified"
OVERRIDES_PATH = CLASSIFIED_DIR / "overrides.yaml"
CLASSIFIED_PATH = CLASSIFIED_DIR / "contract-sweep.yaml"
DEFAULT_RAW_DIR = PROBES_DIR / "raw"

# Closed four-state contract vocabulary (MTX-01, D-06/D-07). This plan (11-01)
# reaches only `skipped`, `unfired`, `rejected`, `accepted-unverified`,
# `needs-review` HONESTLY — the three honor-discriminating states stay in the
# vocabulary, unreachable until plan 11-04 adds their detectors. A deliberately
# empty branch, not a missing one.
STATES = frozenset({
    "rejected",
    "accepted-honored",
    "accepted-ignored",
    "silently-translated",
    "accepted-unverified",
    "needs-review",
    "unfired",
    "skipped",
})

# Closed honor_evidence vocabulary (D-06). `none` marks an accepted cell whose
# response carries no honor-discriminating signal — structurally distinct from an
# actual honor verdict, never rendered identically. `n/a` marks every state
# honor_evidence never applies to (skipped/unfired/rejected/needs-review).
HONOR_EVIDENCE = frozenset({
    "none",
    "echoed-field",
    "translated-field",
    "candidate-count",
    "logprobs-content",
    "json-validity",
    "usage-delta",
    "n/a",
})

# Fixed hazard text (SWP-02), a constant PER STATE so regeneration stays byte-stable
# (never derived from the cell's own live fields). Conclusion 19
# (docs/conclusions.md #19) is the origin of the silent-acceptance hazard class this
# names: Moonshot's `enable_thinking: false` accepted-and-ignored, and xAI's
# priority-tier degrade (accepted-and-silently-translated) are the two real,
# documented instances this schema generalizes into two first-class states.
HAZARD_TEXT = {
    "accepted-ignored": (
        "Silent acceptance (conclusion 19): the request was accepted (2xx) but the "
        "response carries no evidence the parameter had any effect — the vendor may "
        "have silently dropped it."
    ),
    "silently-translated": (
        "Silent acceptance (conclusion 19): the request was accepted (2xx) but the "
        "vendor's response reports a DIFFERENT value than the one requested — the "
        "vendor rewrote it rather than honoring or rejecting it."
    ),
}


def hazard_for(state: str) -> str | None:
    """SWP-02: the hazard note for a FINAL rendered state — non-null for the two
    silent-acceptance states, null for every other state (including
    accepted-honored, which must never be confused with the two hazard states in
    either the classified YAML or the rendered matrix)."""
    return HAZARD_TEXT.get(state)

# Plan 11-04, Task 2 (D-06's honor-evidence rule made mechanical): every swept
# registry row id (`probes/inventory.yaml`'s `params:` list, `status: swept`) maps
# to exactly one detector NAME below — coverage is total and `--check`-gated
# (check_honor_detector_coverage()). Dispatch is on ROW ID, never on vendor/wire
# family — the detector functions themselves branch on wire_family internally where
# the response shape actually differs. `"none"` is an explicit, deliberate claim
# ("checked: no single-response signal exists for this row's contract"), not an
# omission — it covers the majority of the sampling family (a bare `temperature`/
# `top-p`/etc. value is never echoed or reflected in any response field any of the
# three wire families expose) plus every row whose only single-response signal
# would be too ambiguous to assert honestly (see `detect_finish_reason`'s own
# docstring for why `stop` itself resolves to `"none"`, not a dedicated detector).
HONOR_DETECTORS: dict[str, str] = {
    # sampling group (10 rows) — only `logprobs` and `n` have a single-response
    # signal; the other 8 (temperature/top-p/top-k/presence-penalty/
    # frequency-penalty/top-logprobs/seed/logit-bias) have no response-visible
    # trace of their own value at all, at any of the three wire families.
    "temperature": "none",
    "top-p": "none",
    "top-k": "none",
    "presence-penalty": "none",
    "frequency-penalty": "none",
    "logprobs": "logprobs",
    "top-logprobs": "none",  # requires ALSO enabling logprobs; this row alone
    # (probe value 3, no accompanying logprobs:true) has no reliable per-token
    # signal to examine — a narrower, row-specific claim than the `logprobs` row's
    # own detector, which tests the simpler boolean-enable contract.
    "seed": "none",  # no wire family echoes the requested seed value in its
    # response body; determinism itself (same seed -> same output) is a REPEAT-based
    # behavioral check, explicitly Phase 12's job (PREREGISTRATION.md § Sample size).
    "n": "candidate-count",
    "logit-bias": "none",
    # structural group (10 rows)
    "max-tokens": "usage",
    "stop": "none",  # SEE detect_finish_reason()'s docstring: openai_compat/gemini's
    # shared "stop"/"STOP" finish reason is emitted for BOTH a natural completion
    # and a triggered stop sequence — genuinely ambiguous from one response at those
    # two wire families; only anthropic_messages' dedicated "stop_sequence" value is
    # unambiguous, and the row's own probe value (stop=["the"], prompt "...hello.")
    # is unlikely to ever trigger regardless of honoring — an admitted unknown, not
    # an invented signal (rule 1b).
    "response-format": "structured-output",
    "tools": "none",
    "tool-choice": "none",
    "parallel-tool-calls": "none",
    "stream": "none",
    "stream-options-include-usage": "none",
    "anthropic-structured-output-output-config": "structured-output",
    "anthropic-structured-output-output-format": "structured-output",
    # service-tier group (1 row) — OpenAI-family responses echo the resolved
    # service_tier field at the top level (conclusion 15/19's priority->fast
    # rename precedent is exactly this row's own contract).
    "service-tier": "echo",
    # reasoning-toggle group (4 rows) — a single accepted response's
    # `usage.reasoning_tokens` count alone cannot establish whether the SPECIFIC
    # requested level (e.g. "low" vs the vendor's own default) was honored, only
    # that reasoning happened at all; no repeat/comparison request exists to
    # disambiguate (Phase 12's job, out of scope here) — Stage 2's own purpose
    # (whether the toggle MECHANISM works, i.e. is it accepted at all) is already
    # served by the classify_cell rejected/accepted split, not honor_evidence.
    "openai-reasoning-effort": "none",
    "anthropic-thinking-object": "none",
    "gemini-thinking-config": "none",
    "qwen-enable-thinking": "none",
    # exotic group (15 rows) — boundary-contract / vendor-specific rows. Only
    # `gemini-candidate-count` has a clean single-response signal (the candidates
    # array length, the same contract `n` tests for other vendors) and
    # `openai-service-tier-values` (the same echoed service_tier field `service-tier`
    # already covers, tested here across its full enum instead of just `auto`).
    "gemini-temperature-range": "none",
    "openai-verbosity": "none",
    "openai-prediction": "none",
    "openai-service-tier-values": "echo",
    "anthropic-thinking-budget-floor": "none",
    "gemini-media-resolution": "none",
    "gemini-candidate-count": "candidate-count",
    "kimi-partial-mode": "none",
    "glm-do-sample": "none",
    "qwen-repetition-penalty": "none",
    "kimi-fixed-sampling-point": "none",
    "openai-store": "none",
    "openai-metadata": "none",
    "openai-safety-identifier": "none",
    "openai-prompt-cache-key": "none",
    # content-block group (2 rows) — MODAL-01: the billed usage object is the
    # ENTIRE contract signal for both (the image payload's own input-token cost;
    # whether Anthropic's cache_creation/cache_read fields moved at all).
    "image-input": "usage",
    "anthropic-cache-control-block": "usage",
}


def _safe_get(fn):
    """Wrap a response-shape accessor so a malformed/unexpected body degrades to
    None (no signal) rather than raising — every detector below is a CLAIM about a
    specific field's presence, and a body that doesn't have the expected shape at
    all is honestly 'no signal', never a crash."""
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (KeyError, IndexError, TypeError, AttributeError):
            return None
    return wrapped


@_safe_get
def _get_message_text(response_body: dict, wire_family: str) -> str | None:
    """The single assistant-visible text output, across all 3 wire families."""
    if wire_family == "anthropic_messages":
        for block in response_body["content"]:
            if block.get("type") == "text":
                return block["text"]
        return None
    if wire_family == "openai_compat":
        return response_body["choices"][0]["message"]["content"]
    if wire_family == "gemini":
        for part in response_body["candidates"][0]["content"]["parts"]:
            if "text" in part:
                return part["text"]
        return None
    return None


@_safe_get
def _get_finish_reason(response_body: dict, wire_family: str) -> str | None:
    if wire_family == "anthropic_messages":
        return response_body.get("stop_reason")
    if wire_family == "openai_compat":
        return response_body["choices"][0].get("finish_reason")
    if wire_family == "gemini":
        return response_body["candidates"][0].get("finishReason")
    return None


@_safe_get
def _get_candidate_count(response_body: dict, wire_family: str) -> int | None:
    if wire_family == "anthropic_messages":
        return 1  # Anthropic never accepts n>1 (names[anthropic_messages] is null
        # on every row that would test it) — a defensive fallback, unreached today.
    if wire_family == "openai_compat":
        return len(response_body.get("choices") or [])
    if wire_family == "gemini":
        return len(response_body.get("candidates") or [])
    return None


@_safe_get
def _get_logprobs_present(response_body: dict, wire_family: str) -> bool:
    if wire_family == "openai_compat":
        content = ((response_body.get("choices") or [{}])[0].get("logprobs") or {}).get("content")
        return bool(content)
    if wire_family == "gemini":
        # Gemini's documented field for per-token logprobs (responseLogprobs:true
        # in the request) is `logprobsResult` on the candidate; `avgLogprobs` alone
        # (present even without the request flag on some models) is NOT treated as
        # evidence of honoring — only the dedicated per-token result is.
        cand = (response_body.get("candidates") or [{}])[0]
        return bool(cand.get("logprobsResult"))
    return False


@_safe_get
def _get_field_value(response_body: dict, field_name: str):
    """Top-level response field lookup, by name — the echo detector's own
    accessor. Every row this detector serves (service-tier,
    openai-service-tier-values) echoes at the TOP level of the response body in
    every wire family that supports it (no wire family nests service_tier)."""
    return response_body.get(field_name, _MISSING)


_MISSING = object()


def detect_none(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                 requested_value: str, usage: dict) -> tuple[str, str]:
    """The explicit no-signal claim (D-06): every accepted cell this detector
    serves is 'accepted-unverified' with honor_evidence 'none' — never an invented
    honor claim from a response this schema knows has nothing to examine."""
    return "accepted-unverified", "none"


def detect_logprobs(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                     requested_value: str, usage: dict) -> tuple[str, str]:
    present = _get_logprobs_present(response_body, wire_family)
    if present:
        return "accepted-honored", "logprobs-content"
    return "accepted-ignored", "logprobs-content"


def detect_candidate_count(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                            requested_value: str, usage: dict) -> tuple[str, str]:
    count = _get_candidate_count(response_body, wire_family)
    try:
        requested_n = int(requested_value)
    except (TypeError, ValueError):
        return "accepted-unverified", "none"
    if count is None:
        return "accepted-unverified", "none"
    if count == requested_n:
        return "accepted-honored", "candidate-count"
    if count == 1 and requested_n > 1:
        return "accepted-ignored", "candidate-count"
    return "accepted-unverified", "none"


def detect_structured_output(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                              requested_value: str, usage: dict) -> tuple[str, str]:
    text = _get_message_text(response_body, wire_family)
    if text is None:
        return "accepted-unverified", "none"
    try:
        json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return "accepted-ignored", "json-validity"
    return "accepted-honored", "json-validity"


def detect_echo(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                 requested_value: str, usage: dict) -> tuple[str, str]:
    if not resolved_field:
        return "accepted-unverified", "none"
    actual = _get_field_value(response_body, resolved_field)
    if actual is _MISSING or actual is None:
        return "accepted-ignored", "echoed-field"
    if str(actual) == str(requested_value):
        return "accepted-honored", "echoed-field"
    return "silently-translated", "translated-field"


def detect_finish_reason(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                          requested_value: str, usage: dict) -> tuple[str, str]:
    """Only `stop` would dispatch here (see HONOR_DETECTORS' own comment for why
    every OTHER structural row stays on `none`) — kept as its own named function
    per the plan's own detector list, even though HONOR_DETECTORS currently routes
    no row to it (the `stop` row itself resolves to `none` for the documented
    ambiguity reason, below). Anthropic's dedicated `stop_sequence` finish reason
    is the one wire-family signal genuinely unambiguous from a single response;
    openai_compat/gemini's shared `stop`/`STOP` value is emitted for both a
    natural completion and a triggered stop string, so this function falls back to
    `accepted-unverified`/`none` for those two families rather than overclaiming
    either honored or ignored from an inherently ambiguous field."""
    reason = _get_finish_reason(response_body, wire_family)
    if wire_family == "anthropic_messages" and reason == "stop_sequence":
        return "accepted-honored", "usage-delta"
    return "accepted-unverified", "none"


def detect_usage(response_body: dict, *, row_id: str, wire_family: str, resolved_field: str | None,
                  requested_value: str, usage: dict) -> tuple[str, str]:
    """Dispatches on `row_id`, the two rows this detector serves having genuinely
    different contracts to examine on the SAME `usage` object:

    `max-tokens` — honored when the record's own parsed `usage.output_tokens` is
    present and does not exceed the requested cap (a cap exceeded would be a
    structural anomaly no vendor in this set should ever produce, but is read as
    accepted-ignored rather than asserted impossible).

    `image-input`/`anthropic-cache-control-block` — honored whenever the relevant
    usage field is present AT ALL (MODAL-01's billed-input-token reading for the
    image row; Anthropic's cache_creation/cache_read token fields for the
    cache-control row) — presence itself is the whole contract signal for these
    two rows; there is no 'wrong value' to compare against, only presence vs
    absence."""
    if row_id == "max-tokens":
        output_tokens = usage.get("output_tokens")
        if output_tokens is None:
            return "accepted-unverified", "none"
        try:
            cap = int(requested_value)
        except (TypeError, ValueError):
            return "accepted-unverified", "none"
        if output_tokens <= cap:
            return "accepted-honored", "usage-delta"
        return "accepted-ignored", "usage-delta"
    # image-input / anthropic-cache-control-block
    if usage.get("input_tokens") is not None or usage.get("cache_creation_input_tokens") is not None \
            or usage.get("cache_read_input_tokens") is not None:
        return "accepted-honored", "usage-delta"
    return "accepted-unverified", "none"


DETECTOR_FUNCS = {
    "none": detect_none,
    "logprobs": detect_logprobs,
    "candidate-count": detect_candidate_count,
    "structured-output": detect_structured_output,
    "echo": detect_echo,
    "finish-reason": detect_finish_reason,
    "usage": detect_usage,
}

# Closed needs-review reason vocabulary (D-07's rejection-strictness rule). Every
# non-`rejected` non-429 4xx and every non-verdict/rate-limited terminal lands in
# `needs-review` with one of these, never a silent default.
NEEDS_REVIEW_REASONS = frozenset({
    "non-verdict-terminal",
    "rate-limited",
    "4xx-not-param-named",
})

# Closed skip-reason vocabulary (D-11) — mirrors probes/inventory-to-sets.py's own
# SKIP_REASONS frozenset exactly. Duplicated here, not imported: that module's
# hyphenated filename (`inventory-to-sets.py`) is not a valid Python module name and
# is not importable with a bare `import` statement. Dated, closed, checked against
# every declared skip below — any entry outside it is a registry/generator drift
# this check catches rather than silently accepting.
SKIP_REASONS = frozenset({
    "no-thinking-off-toggle",
    "no-thinking-capability",
    "wire-shape-incompatible",
    "toggle-shape-unknown",
    "toggle-not-a-request-parameter",
    "no-request-field-for-vendor",
})

def classified_header(*, scalar_count: int, content_block_count: int, skip_count: int) -> str:
    """The generated-file header comment (Phase 11.1 plan 01, D-08's stale-header
    fix): the three declared-cell-universe counts are interpolated at RENDER
    TIME from the loaded declared-cell YAMLs, never hand-pasted — the same
    count-from-loaded-data discipline scripts/build-probe-matrix.py's own
    print_summary() already uses (RESEARCH.md Pattern 3). Prose and the MTX-01
    reference are otherwise byte-identical to the original hand-pasted
    constant this function replaces; only the numbers became parameters.
    Callers must not paste a currently-correct total in as a shortcut — that
    recreates the exact staleness this fix exists to close: two evidence
    additions after the original hand-pasted constant was first written (the
    calibration batch, then Phase 11 plan 11-07's baseline-cell gap closure),
    its stated totals had silently drifted from what the input files actually
    contained, without anyone noticing until this fix's own git history
    records the before/after counts in each commit's diff."""
    total = scalar_count + content_block_count + skip_count
    return (
        "# probes/classified/contract-sweep.yaml — GENERATED by\n"
        "# scripts/classify-probes.py from probes/raw/*.jsonl +\n"
        "# probes/classified/overrides.yaml — do not edit by hand. Regenerate with\n"
        "# `python3 scripts/classify-probes.py`.\n"
        "#\n"
        "# One row per declared cell (probes/sets/generated/contract-sweep.yaml +\n"
        f"# content-blocks.yaml, {scalar_count + content_block_count} cells) plus every declared skip\n"
        f"# (probes/sets/generated/skipped-cells.yaml, {skip_count}) — {total} rows total (MTX-01)."
    )


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path every
    loader below uses (matches probes/harness/runner.py's and
    probes/inventory-to-sets.py's own `_fail` idiom). Callers in `main()` let this
    propagate naturally; `selftest()` catches it with `except SystemExit` to verify
    the path without killing the self-test process itself."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _load_yaml(path: Path, required_key: str) -> dict:
    """Fail-loud YAML loader shared by every input this module reads — never a
    silent default on a missing file, malformed YAML, or a missing top-level key."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or required_key not in data:
        _fail(2, f"{path}: expected a top-level `{required_key}:` key")
    return data


def load_inventory(path: Path = INVENTORY_PATH) -> dict:
    data = _load_yaml(path, "params")
    if not isinstance(data["params"], list):
        _fail(2, f"{path}: `params:` must be a list")
    return data


def load_models(path: Path = MODELS_PATH) -> dict[str, dict]:
    """slug -> row, with `_order` recording models.yaml's own row index (the
    classified output's model-ordering sort key, per this plan's own determinism
    criterion)."""
    data = _load_yaml(path, "models")
    rows: dict[str, dict] = {}
    for i, row in enumerate(data["models"]):
        rows[row["slug"]] = {**row, "_order": i}
    return rows


def resolve_param_name(row: dict, model: dict) -> str | None:
    """Mirrors probes/inventory-to-sets.py's own resolve_param_name() (D-02/D-07)
    exactly: the row's per-wire-family `names:` value, unless a `name_overrides:`
    entry for the model's vendor wins over the family default. Duplicated here
    rather than imported (see SKIP_REASONS above for why) because D-07's rejection
    check needs the exact resolved name the generator used to build the fired
    request, matched against the wire response's own error body."""
    wire_family = model["wire_family"]
    names = row.get("names") or {}
    param_name = names.get(wire_family)
    override_name = (row.get("name_overrides") or {}).get(model["vendor"])
    if override_name is not None:
        param_name = override_name
    return param_name


def load_declared_scalar(path: Path = CONTRACT_SWEEP_PATH) -> dict:
    return _load_yaml(path, "probes")


def load_declared_content_block(path: Path = CONTENT_BLOCKS_PATH) -> dict:
    return _load_yaml(path, "content_block_probes")


def load_declared_skips(path: Path = SKIPPED_CELLS_PATH) -> dict:
    return _load_yaml(path, "skipped")


def load_overrides(path: Path = OVERRIDES_PATH) -> dict[str, dict]:
    """probe_id -> override entry (D-08). Fails loud if the file is missing or
    malformed — `probes/classified/overrides.yaml` is hand-kept but still a
    required, validated input, never an optional one silently skipped."""
    data = _load_yaml(path, "overrides")
    overrides = data["overrides"]
    if not isinstance(overrides, list):
        _fail(2, f"{path}: `overrides:` must be a list")
    by_pid: dict[str, dict] = {}
    for entry in overrides:
        missing = {"probe_id", "state", "date", "reason"} - set(entry)
        if missing:
            _fail(2, f"{path}: override entry missing required key(s) {sorted(missing)}: {entry}")
        by_pid[entry["probe_id"]] = entry
    return by_pid


def load_raw_records(raw_dir: Path = DEFAULT_RAW_DIR) -> dict[str, dict]:
    """Every complete JSONL record across `raw_dir`'s *.jsonl files, keyed by
    probe_id. Fails loud (exit 2), writing nothing downstream, when there is no
    readable evidence at all — no *.jsonl file, or every one empty — so an absent
    evidence base can never render as an empty-but-valid classified file."""
    raw_dir = Path(raw_dir)
    files = sorted(raw_dir.glob("*.jsonl")) if raw_dir.is_dir() else []
    records: dict[str, dict] = {}
    any_content = False
    for f in files:
        try:
            text = f.read_text()
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            any_content = True
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                # Truncated trailing line from a killed process — ignore it, same
                # tolerance runner.py's own seen_probe_ids() applies.
                continue
            pid = rec.get("probe_id")
            if pid:
                records[pid] = rec
    if not any_content:
        _fail(2, f"no readable raw evidence in {raw_dir} (no *.jsonl file, or every one empty)")
    return records


def scalar_probe_id(entry: dict, models: dict[str, dict]) -> str:
    """Recompute the EXACT probe_id runner.py's main() would have assigned this
    declared scalar entry — same adapter.build_request() call, same
    apply_max_tokens_field_override() (plan 11-04's per-model request-field rename,
    a no-op for every model that doesn't declare one — Rule 1 fix, plan 11-05: this
    call was missing here, so every gpt-5-6-sol cell classified 'unfired' despite
    being correctly recorded on disk under its real fired probe_id), same
    apply_omit(), same probe_id() hash — mirroring runner.build_entry_request()'s
    own scalar branch step-for-step, so this can never independently drift from the
    harness that produced the evidence being joined against (MTX-01's own key_link)."""
    model = models[entry["model"]]
    adapter = ADAPTERS[model["wire_family"]]
    prompt = entry.get("prompt", "Reply with one word.")
    max_tokens = entry.get("max_tokens", 16)
    extra_params = entry.get("extra_params") or {}
    request_body = adapter.build_request(model["api_model_id"], prompt, max_tokens, extra_params)
    request_body = harness_runner.apply_max_tokens_field_override(request_body, model)
    request_body = harness_runner.apply_omit(request_body, entry.get("omit"))
    return harness_runner.probe_id(entry["model"], entry["param"], entry["value"], entry["mode"], request_body)


def content_block_probe_id(entry: dict, models: dict[str, dict]) -> str:
    """Recompute the EXACT probe_id runner.py's main() would have assigned this
    declared content-block entry (Rule 1 fix, plan 11-05: every content-block cell
    hard-coded 'unfired' in main()'s classification loop below — written in plan
    11-01/11-02, before the --content-block-set firing path existed; stage 6 fired
    live for the first time in this plan's Task 2, so the join was never exercised
    against real evidence until now). Delegates the WHOLE request-body construction
    to `runner.build_entry_request()` itself — the body_template deep-copy, the tiny-PNG
    substitution, `adapter.build_content_request()`, and
    `apply_max_tokens_field_override()` — rather than reimplementing any of it here,
    so a future change to that construction can never independently drift from this
    join (the same MTX-01 key_link scalar_probe_id() already relies on)."""
    model = models[entry["model"]]
    adapter = ADAPTERS[model["wire_family"]]
    request_body = harness_runner.build_entry_request(entry, model, adapter)
    return harness_runner.probe_id(entry["model"], entry["param"], entry["value"], entry["mode"], request_body)


def classify_cell(
    record: dict | None, row: dict, model: dict, requested_value: str | None = None
) -> tuple[str, str | None, int | None, str]:
    """Pure classification (D-06/D-07) of ONE scalar cell given its matched raw
    record (or None if unfired), its probes/inventory.yaml row, its
    probes/harness/models.yaml row, and the cell's own requested (rendered)
    value. No I/O, no mutation — testable the same boundary-first way
    probes/harness/ledger.py's ceiling_verdict() selftest already demonstrates.
    Returns (state, needs_review_reason_or_None, http_status_or_None,
    honor_evidence).

    Rules, in order:
    1. No matched record -> 'unfired'.
    2. A record whose terminal is not 'verdict' -> 'needs-review',
       'non-verdict-terminal' (a connection failure, retry-exhausted, or fatal
       stop carries no contract verdict at all).
    3. A 429 -> 'needs-review', 'rate-limited' (never auto-classified either way;
       a rate limit says nothing about the parameter's contract).
    4. A non-429 4xx whose serialized error body names the row's resolved
       parameter name (canonical or vendor-aliased) -> 'rejected' (D-07's
       rejection-strictness rule).
    5. Any other non-429 4xx -> 'needs-review', '4xx-not-param-named' — never
       merged into 'rejected'.
    6. A 2xx -> dispatch to this row's HONOR_DETECTORS entry (Task 2, plan
       11-04): the detector returns (state, honor_evidence) itself — one of
       accepted-honored/accepted-ignored/silently-translated/accepted-unverified,
       each with an evidence tag from the closed HONOR_EVIDENCE vocabulary. A row
       whose contract cannot be judged from one response resolves to the `none`
       detector, which always returns accepted-unverified/none (D-06: no honor
       claim is ever invented from a response carrying no signal).
    A terminal='verdict' record with any other status is a structural anomaly
    client.py's retry_decision() should never produce (it only ever assigns
    'verdict' to a 2xx or a non-429/5xx/0 4xx) — fails loud rather than silently
    guessing a state."""
    if record is None:
        return "unfired", None, None, "n/a"
    terminal = record.get("terminal")
    attempts = record.get("attempts") or []
    last = attempts[-1] if attempts else {}
    http_status = last.get("status")
    if terminal != "verdict":
        return "needs-review", "non-verdict-terminal", http_status, "n/a"
    if http_status == 429:
        return "needs-review", "rate-limited", http_status, "n/a"
    if isinstance(http_status, int) and 400 <= http_status < 500:
        expected_name = resolve_param_name(row, model)
        error_text = json.dumps(last.get("response_body_raw"), sort_keys=True)
        if expected_name and expected_name in error_text:
            return "rejected", None, http_status, "n/a"
        return "needs-review", "4xx-not-param-named", http_status, "n/a"
    if isinstance(http_status, int) and 200 <= http_status < 300:
        row_id = row["id"]
        detector_name = HONOR_DETECTORS.get(row_id)
        if detector_name is None:
            _fail(2, f"classify_cell: row id {row_id!r} is missing from HONOR_DETECTORS — coverage must be total")
        detector = DETECTOR_FUNCS[detector_name]
        response_body = last.get("response_body_raw") or {}
        wire_family = model["wire_family"]
        resolved_field = resolve_param_name(row, model)
        usage = record.get("usage") or {}
        state, honor_evidence = detector(
            response_body,
            row_id=row_id,
            wire_family=wire_family,
            resolved_field=resolved_field,
            requested_value=requested_value,
            usage=usage,
        )
        return state, None, http_status, honor_evidence
    _fail(
        2,
        f"classify_cell: unexpected http_status {http_status!r} with terminal='verdict' "
        "— client.retry_decision() only ever assigns 'verdict' to a 2xx or a non-429/5xx/0 "
        "4xx; this record is a structural anomaly, not a classifiable contract cell",
    )


def apply_overrides(rows: list[dict], overrides: dict[str, dict]) -> int:
    """Applies every override LAST and deterministically (D-08): a matching
    probe_id has its row's `state` replaced by the override's `state`, and the
    row's `override` field set to `{date, reason}` — visibly marking it.
    Regeneration never silently loses an entry (every override is looked up
    against the CURRENT declared-cell join, not cached). Returns the count of
    overrides whose probe_id resolved to no row in `rows` — `--check` reports
    this as a finding, so a stale override can never silently do nothing."""
    by_pid: dict[str, list[dict]] = {}
    for r in rows:
        if r.get("probe_id"):
            by_pid.setdefault(r["probe_id"], []).append(r)
    unmatched = 0
    for pid, entry in overrides.items():
        targets = by_pid.get(pid)
        if not targets:
            unmatched += 1
            continue
        for r in targets:
            r["state"] = entry["state"]
            r["override"] = {"date": entry["date"], "reason": entry["reason"]}
    return unmatched


def build_rows(
    inventory: dict, models: dict[str, dict], raw_records: dict[str, dict], overrides: dict[str, dict]
) -> tuple[list[dict], str | None, int, int]:
    """The full join + classify + override pipeline. Returns (rows, evidence_through,
    unmatched_override_count, ignored_record_count) — `rows` sorted in the declared
    order (inventory row order, then models.yaml row index, then mode, then value,
    never dict/set iteration order, MTX-01's determinism criterion)."""
    rows_by_id = {row["id"]: row for row in inventory["params"]}
    row_order = {row["id"]: i for i, row in enumerate(inventory["params"])}
    model_order = {slug: m["_order"] for slug, m in models.items()}

    scalar_data = load_declared_scalar()
    content_block_data = load_declared_content_block()
    skipped_data = load_declared_skips()

    out_rows: list[dict] = []
    used_probe_ids: set[str] = set()
    joined_recorded_at: list[str] = []

    for entry in scalar_data["probes"]:
        row = rows_by_id[entry["param"]]
        model = models[entry["model"]]
        pid = scalar_probe_id(entry, models)
        record = raw_records.get(pid)
        state, reason, http_status, honor_evidence = classify_cell(record, row, model, entry["value"])
        usage_input = usage_output = None
        if record is not None:
            used_probe_ids.add(pid)
            if record.get("recorded_at"):
                joined_recorded_at.append(record["recorded_at"])
            usage = record.get("usage") or {}
            usage_input = usage.get("input_tokens")
            usage_output = usage.get("output_tokens")
        out_rows.append({
            "param": entry["param"],
            "group": row["group"],
            "model": entry["model"],
            "mode": entry["mode"],
            "value": entry["value"],
            "state": state,
            "probe_id": pid if state != "unfired" else None,
            "http_status": http_status,
            "honor_evidence": honor_evidence,
            "hazard": None,
            "usage_input_tokens": usage_input,
            "usage_output_tokens": usage_output,
            "skip_reason": None,
            "reason": reason,
            "override": None,
        })

    for entry in content_block_data["content_block_probes"]:
        # The --content-block-set firing path exists as of plan 11-03 (MODAL-01);
        # Stage 6 (SWEEP-DESIGN.md § Probe ordering) fires last, after the D-09
        # checkpoint — and fired live for the first time in plan 11-05's Task 2.
        # Joined against real evidence exactly like a scalar entry (Rule 1 fix,
        # plan 11-05): this loop hard-coded every content-block cell 'unfired'
        # from plan 11-01/11-02 until now, honestly reflecting that zero
        # content-block records existed in probes/raw/*.jsonl at that time — the
        # join itself was never exercised against real evidence until this task.
        row = rows_by_id[entry["param"]]
        model = models[entry["model"]]
        pid = content_block_probe_id(entry, models)
        record = raw_records.get(pid)
        state, reason, http_status, honor_evidence = classify_cell(record, row, model, entry["value"])
        usage_input = usage_output = None
        if record is not None:
            used_probe_ids.add(pid)
            if record.get("recorded_at"):
                joined_recorded_at.append(record["recorded_at"])
            usage = record.get("usage") or {}
            usage_input = usage.get("input_tokens")
            usage_output = usage.get("output_tokens")
        out_rows.append({
            "param": entry["param"],
            "group": row["group"],
            "model": entry["model"],
            "mode": entry["mode"],
            "value": entry["value"],
            "state": state,
            "probe_id": pid if state != "unfired" else None,
            "http_status": http_status,
            "honor_evidence": honor_evidence,
            "hazard": None,
            "usage_input_tokens": usage_input,
            "usage_output_tokens": usage_output,
            "skip_reason": None,
            "reason": reason,
            "override": None,
        })

    for entry in skipped_data["skipped"]:
        reason = entry["reason"]
        if reason not in SKIP_REASONS:
            _fail(
                2,
                f"{SKIPPED_CELLS_PATH}: cell {entry.get('model')}/{entry.get('param')} carries "
                f"reason {reason!r} outside the closed skip vocabulary {sorted(SKIP_REASONS)}",
            )
        row = rows_by_id[entry["param"]]
        out_rows.append({
            "param": entry["param"],
            "group": row["group"],
            "model": entry["model"],
            "mode": entry.get("mode"),
            "value": None,
            "state": "skipped",
            "probe_id": None,
            "http_status": None,
            "honor_evidence": "n/a",
            "hazard": None,
            "usage_input_tokens": None,
            "usage_output_tokens": None,
            "skip_reason": reason,
            "reason": None,
            "override": None,
        })

    unmatched_overrides = apply_overrides(out_rows, overrides)

    # SWP-02's hazard note, computed LAST — after overrides — so hazard always
    # reflects the FINAL rendered state (an override moving a cell OUT of a
    # hazard state clears its hazard text; one moving a cell INTO one sets it).
    # A fixed constant per state (HAZARD_TEXT), never derived from the cell's own
    # live fields, keeps regeneration byte-stable.
    for r in out_rows:
        r["hazard"] = hazard_for(r["state"])

    def sort_key(r: dict) -> tuple:
        return (row_order[r["param"]], model_order[r["model"]], r["mode"] or "", r["value"] or "")

    out_rows.sort(key=sort_key)

    evidence_through = max(joined_recorded_at) if joined_recorded_at else None
    ignored_records = len(raw_records) - len(used_probe_ids)
    return out_rows, evidence_through, unmatched_overrides, ignored_records


def check_honor_detector_coverage(inventory: dict) -> list[str]:
    """`--check` gate (Task 2's must_haves truth): every swept registry row id
    must resolve to a HONOR_DETECTORS entry — an omission is a finding, never a
    silent default to 'none'. Returns the sorted list of missing row ids (empty
    when coverage is total)."""
    swept_ids = {row["id"] for row in inventory["params"] if row.get("status") == "swept"}
    return sorted(swept_ids - set(HONOR_DETECTORS))


def render_classified_file(
    *,
    checked,
    evidence_through: str | None,
    rows: list[dict],
    scalar_count: int,
    content_block_count: int,
    skip_count: int,
) -> str:
    """Every generated file: a header comment (its three declared-cell-universe
    counts derived by the caller, never hand-typed here — see
    classified_header()), a `checked:` date carried straight from the
    declared-cell input (never wall-clock — matches
    probes/inventory-to-sets.py's own render_generated_file() convention), an
    `evidence_through:` field derived from the joined evidence itself, then the
    single `cells:` list. `checked`, `evidence_through`, and the three counts
    are all derived from inputs, so idempotent regeneration is byte-identical."""
    doc = {"checked": checked, "evidence_through": evidence_through, "cells": rows}
    body = yaml.safe_dump(doc, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
    header = classified_header(
        scalar_count=scalar_count, content_block_count=content_block_count, skip_count=skip_count
    )
    return header.rstrip("\n") + "\n\n" + body


def regenerate(raw_dir: Path = DEFAULT_RAW_DIR):
    """Load every input, join, classify, apply overrides, and render — the single
    pipeline both the writer and `--check`'s drift comparator call, so the two can
    never independently drift apart."""
    inventory = load_inventory()
    models = load_models()
    raw_records = load_raw_records(raw_dir)
    overrides = load_overrides()
    rows, evidence_through, unmatched_overrides, ignored_records = build_rows(
        inventory, models, raw_records, overrides
    )
    declared_scalar = load_declared_scalar()
    checked = declared_scalar["checked"]
    scalar_count = len(declared_scalar["probes"])
    content_block_count = len(load_declared_content_block()["content_block_probes"])
    skip_count = len(load_declared_skips()["skipped"])
    text = render_classified_file(
        checked=checked,
        evidence_through=evidence_through,
        rows=rows,
        scalar_count=scalar_count,
        content_block_count=content_block_count,
        skip_count=skip_count,
    )
    return text, rows, unmatched_overrides, ignored_records


def print_summary(rows: list[dict], unmatched_overrides: int, ignored_records: int) -> None:
    scalar_declared = load_declared_scalar()["probes"]
    content_block_declared = load_declared_content_block()["content_block_probes"]
    skipped_declared = load_declared_skips()["skipped"]
    tally: dict[str, int] = {}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    print(
        f"declared cells: {len(scalar_declared) + len(content_block_declared)} "
        f"(scalar={len(scalar_declared)} content-block={len(content_block_declared)})"
    )
    print(f"declared skips: {len(skipped_declared)}")
    print(f"rows emitted: {len(rows)}")
    for state in sorted(tally):
        print(f"  {state}: {tally[state]}")
    print(f"ignored raw records (no matching declared cell): {ignored_records}")
    print(f"stale overrides (probe_id resolves to no row): {unmatched_overrides}")


def check_generated_drift(raw_dir: Path = DEFAULT_RAW_DIR) -> tuple[int, int]:
    """(rule 3 drift gate) Re-render in memory from the real inputs and compare
    byte-for-byte with what is on disk. Also reports a finding for any override
    whose probe_id resolves to no declared cell (D-08 staleness check)."""
    checks = 0
    problems = 0

    checks += 1
    expected_text, _rows, unmatched_overrides, _ignored = regenerate(raw_dir)
    if not CLASSIFIED_PATH.exists():
        problems += 1
        print(f"FAIL drift: {CLASSIFIED_PATH} does not exist — run the generator", file=sys.stderr)
    else:
        actual_text = CLASSIFIED_PATH.read_text()
        if actual_text != expected_text:
            problems += 1
            print(
                f"FAIL drift: {CLASSIFIED_PATH} does not match a fresh render of its "
                "inputs — it was hand-edited or is stale (rule 3)",
                file=sys.stderr,
            )

    checks += 1
    if unmatched_overrides:
        problems += 1
        print(
            f"FAIL overrides: {unmatched_overrides} override probe_id(s) in {OVERRIDES_PATH} "
            "resolve to no declared cell — a stale override",
            file=sys.stderr,
        )

    checks += 1
    missing_detectors = check_honor_detector_coverage(load_inventory())
    if missing_detectors:
        problems += 1
        print(
            f"FAIL honor-detector coverage: {len(missing_detectors)} swept registry row id(s) "
            f"missing from HONOR_DETECTORS: {missing_detectors} — coverage must be total (D-06)",
            file=sys.stderr,
        )

    return checks, problems


# -----------------------------------------------------------------------------------
# --selftest — embedded fixtures, no external test framework, following
# probes/inventory-to-sets.py's own selftest() house style: tempfile.TemporaryDirectory()
# for file-loading fail-loud paths, direct dict fixtures for pure functions.
# -----------------------------------------------------------------------------------


def selftest() -> tuple[int, int]:
    problems = 0
    cases = 0

    fixture_row = {
        # "temperature" is a real swept row id, mapped to the "none" honor
        # detector — needed since plan 11-04's classify_cell() now dispatches on
        # row["id"] for the 2xx branch and fails loud on any id absent from
        # HONOR_DETECTORS (coverage is total by design); every fixture below that
        # doesn't specifically exercise a NON-none detector uses this row.
        "id": "temperature",
        "names": {"anthropic_messages": "fixture_param", "openai_compat": "fixture_param", "gemini": None},
        "name_overrides": {"gemini": "fixture_override_param"},
    }
    fixture_model_anthropic = {"wire_family": "anthropic_messages", "vendor": "anthropic"}
    fixture_model_gemini = {"wire_family": "gemini", "vendor": "gemini"}

    # --- resolve_param_name: family default, and a vendor override winning over
    #     a null family entry (mirrors inventory-to-sets.py's own resolution) ---
    cases += 1
    if resolve_param_name(fixture_row, fixture_model_anthropic) != "fixture_param":
        problems += 1
        print("FAIL resolve_param_name: expected the family default name", file=sys.stderr)
    cases += 1
    if resolve_param_name(fixture_row, fixture_model_gemini) != "fixture_override_param":
        problems += 1
        print("FAIL resolve_param_name: expected the vendor override to win over a null family entry", file=sys.stderr)

    # --- classify_cell: no matched record -> unfired ---
    cases += 1
    state, reason, status, honor = classify_cell(None, fixture_row, fixture_model_anthropic)
    if (state, reason, status, honor) != ("unfired", None, None, "n/a"):
        problems += 1
        print(f"FAIL classify_cell(unfired): got {(state, reason, status, honor)}", file=sys.stderr)

    # --- classify_cell: non-verdict terminal -> needs-review, non-verdict-terminal ---
    cases += 1
    rec = {"terminal": "retry_exhausted", "attempts": [{"status": 429}]}
    state, reason, status, honor = classify_cell(rec, fixture_row, fixture_model_anthropic)
    if (state, reason) != ("needs-review", "non-verdict-terminal"):
        problems += 1
        print(f"FAIL classify_cell(non-verdict): got {(state, reason)}", file=sys.stderr)

    # --- classify_cell: 429 with terminal=verdict (defensive; not currently
    #     reachable via client.retry_decision(), but the classifier's own contract
    #     names this rule explicitly — pinned so a future harness change that DOES
    #     make it reachable is classified correctly, not left to fall through) ---
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 429, "response_body_raw": {}}]}
    state, reason, status, honor = classify_cell(rec, fixture_row, fixture_model_anthropic)
    if (state, reason) != ("needs-review", "rate-limited"):
        problems += 1
        print(f"FAIL classify_cell(429-verdict): got {(state, reason)}", file=sys.stderr)

    # --- classify_cell: 4xx naming the resolved parameter -> rejected ---
    cases += 1
    rec = {
        "terminal": "verdict",
        "attempts": [{"status": 400, "response_body_raw": {"error": {"message": "fixture_param: must be >= 0"}}}],
    }
    state, reason, status, honor = classify_cell(rec, fixture_row, fixture_model_anthropic)
    if state != "rejected" or reason is not None:
        problems += 1
        print(f"FAIL classify_cell(4xx named): got {(state, reason)}", file=sys.stderr)

    # --- classify_cell: 4xx NOT naming the resolved parameter -> needs-review,
    #     4xx-not-param-named (D-07: never silently merged into rejected) ---
    cases += 1
    rec = {
        "terminal": "verdict",
        "attempts": [{"status": 400, "response_body_raw": {"error": {"message": "some other field is invalid"}}}],
    }
    state, reason, status, honor = classify_cell(rec, fixture_row, fixture_model_anthropic)
    if (state, reason) != ("needs-review", "4xx-not-param-named"):
        problems += 1
        print(f"FAIL classify_cell(4xx unnamed): got {(state, reason)}", file=sys.stderr)

    # --- classify_cell: 200 -> accepted-unverified, honor_evidence none (D-06) ---
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}]}
    state, reason, status, honor = classify_cell(rec, fixture_row, fixture_model_anthropic)
    if (state, honor) != ("accepted-unverified", "none"):
        problems += 1
        print(f"FAIL classify_cell(200): got {(state, honor)}", file=sys.stderr)

    # --- classify_cell: an anomalous terminal=verdict status client.py should
    #     never produce -> fails loud (exit 2), not a silent guess ---
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 301, "response_body_raw": {}}]}
    try:
        classify_cell(rec, fixture_row, fixture_model_anthropic)
        problems += 1
        print("FAIL classify_cell(anomalous status): expected SystemExit(2), got no exception", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL classify_cell(anomalous status): expected exit 2, got {e.code}", file=sys.stderr)

    # --- apply_overrides: a matching probe_id replaces state and sets `override`;
    #     an unmatched probe_id is counted, never silently ignored (D-08) ---
    cases += 1
    rows = [
        {"probe_id": "a--1", "state": "rejected", "override": None},
        {"probe_id": "a--2", "state": "accepted-unverified", "override": None},
    ]
    overrides = {
        "a--1": {"probe_id": "a--1", "state": "accepted-honored", "date": "2026-09-01", "reason": "fixture"},
        "a--nonexistent": {"probe_id": "a--nonexistent", "state": "rejected", "date": "2026-09-01", "reason": "stale"},
    }
    unmatched = apply_overrides(rows, overrides)
    if rows[0]["state"] != "accepted-honored" or rows[0]["override"] != {"date": "2026-09-01", "reason": "fixture"}:
        problems += 1
        print(f"FAIL apply_overrides: matching override did not apply, got {rows[0]}", file=sys.stderr)
    if rows[1]["state"] != "accepted-unverified" or rows[1]["override"] is not None:
        problems += 1
        print(f"FAIL apply_overrides: non-matching row must be untouched, got {rows[1]}", file=sys.stderr)
    if unmatched != 1:
        problems += 1
        print(f"FAIL apply_overrides: expected 1 unmatched (stale) override, got {unmatched}", file=sys.stderr)

    # --- sort ordering: declared order (row order, model order, mode, value),
    #     never dict/set iteration order — shuffled input, deterministic output ---
    cases += 1
    row_order = {"b-param": 1, "a-param": 0}
    model_order = {"model-y": 1, "model-x": 0}
    shuffled = [
        {"param": "b-param", "model": "model-x", "mode": "default", "value": "1"},
        {"param": "a-param", "model": "model-y", "mode": "default", "value": "1"},
        {"param": "a-param", "model": "model-x", "mode": "thinking-off", "value": "1"},
        {"param": "a-param", "model": "model-x", "mode": "default", "value": "2"},
        {"param": "a-param", "model": "model-x", "mode": "default", "value": "1"},
    ]

    def _sort_key(r):
        return (row_order[r["param"]], model_order[r["model"]], r["mode"] or "", r["value"] or "")

    got_order = [
        (r["param"], r["model"], r["mode"], r["value"]) for r in sorted(shuffled, key=_sort_key)
    ]
    expect_order = [
        ("a-param", "model-x", "default", "1"),
        ("a-param", "model-x", "default", "2"),
        ("a-param", "model-x", "thinking-off", "1"),
        ("a-param", "model-y", "default", "1"),
        ("b-param", "model-x", "default", "1"),
    ]
    if got_order != expect_order:
        problems += 1
        print(f"FAIL sort order: expected {expect_order}, got {got_order}", file=sys.stderr)

    # --- load_raw_records: an empty directory (no *.jsonl at all) fails loud,
    #     exit 2, never a silently-empty result (the classifier's own precondition
    #     for "an absent evidence base never renders as an empty-but-valid file") ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        try:
            load_raw_records(Path(td))
            problems += 1
            print("FAIL load_raw_records(empty dir): expected SystemExit(2), got no exception", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL load_raw_records(empty dir): expected exit 2, got {e.code}", file=sys.stderr)

    # --- load_raw_records: a real record round-trips, keyed by its own probe_id ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        fixture_file = Path(td) / "fixture.jsonl"
        fixture_record = {"probe_id": "fixture--pid", "terminal": "verdict", "attempts": [{"status": 200}]}
        fixture_file.write_text(json.dumps(fixture_record) + "\n")
        records = load_raw_records(Path(td))
        if records.get("fixture--pid") != fixture_record:
            problems += 1
            print(f"FAIL load_raw_records(real record): expected round-trip, got {records}", file=sys.stderr)

    # --- scalar_probe_id: recomputes the SAME id runner.probe_id() would assign
    #     given the identical build_request()/apply_omit() call runner.py's main()
    #     makes — the join-key parity this whole module depends on (MTX-01 key_link) ---
    cases += 1
    models_fixture = {
        "claude-haiku-4-5": {
            "wire_family": "anthropic_messages",
            "api_model_id": "claude-haiku-4-5-20251001",
            "vendor": "anthropic",
            "_order": 3,
        }
    }
    entry = {
        "model": "claude-haiku-4-5",
        "param": "fixture-param",
        "value": "1",
        "mode": "default",
        "prompt": "Reply with exactly one word: hello.",
        "max_tokens": 64,
        "extra_params": {"fixture_param": 1},
    }
    got_pid = scalar_probe_id(entry, models_fixture)
    expected_body = ADAPTERS["anthropic_messages"].build_request(
        "claude-haiku-4-5-20251001", entry["prompt"], entry["max_tokens"], entry["extra_params"]
    )
    expected_body = harness_runner.apply_omit(expected_body, None)
    expected_pid = harness_runner.probe_id("claude-haiku-4-5", "fixture-param", "1", "default", expected_body)
    if got_pid != expected_pid:
        problems += 1
        print(f"FAIL scalar_probe_id: expected {expected_pid}, got {got_pid}", file=sys.stderr)

    # --- scalar_probe_id: a model row declaring max_tokens_field (plan 11-04's
    #     gpt-5-6-sol rename) must be reflected in the recomputed probe_id, the
    #     same way runner.build_entry_request() applies it before hashing — the
    #     Rule 1 fix, plan 11-05: this call was missing, so every gpt-5-6-sol cell
    #     classified 'unfired' despite being correctly recorded on disk ---
    cases += 1
    models_fixture_override = {
        "gpt-5-6-sol": {
            "wire_family": "openai_compat",
            "api_model_id": "gpt-5.6-sol",
            "vendor": "openai",
            "max_tokens_field": "max_completion_tokens",
            "_order": 5,
        }
    }
    entry_override = {
        "model": "gpt-5-6-sol",
        "param": "fixture-param",
        "value": "1",
        "mode": "default",
        "prompt": "Reply with exactly one word: hello.",
        "max_tokens": 64,
        "extra_params": {"fixture_param": 1},
    }
    got_pid_override = scalar_probe_id(entry_override, models_fixture_override)
    expected_body_override = ADAPTERS["openai_compat"].build_request(
        "gpt-5.6-sol", entry_override["prompt"], entry_override["max_tokens"], entry_override["extra_params"]
    )
    expected_body_override = harness_runner.apply_max_tokens_field_override(
        expected_body_override, models_fixture_override["gpt-5-6-sol"]
    )
    expected_body_override = harness_runner.apply_omit(expected_body_override, None)
    expected_pid_override = harness_runner.probe_id(
        "gpt-5-6-sol", "fixture-param", "1", "default", expected_body_override
    )
    if got_pid_override != expected_pid_override:
        problems += 1
        print(
            f"FAIL scalar_probe_id (max_tokens_field override): expected {expected_pid_override}, "
            f"got {got_pid_override}",
            file=sys.stderr,
        )
    if "max_tokens" in expected_body_override or "max_completion_tokens" not in expected_body_override:
        problems += 1
        print(
            f"FAIL scalar_probe_id (max_tokens_field override): expected body to carry "
            f"max_completion_tokens not max_tokens, got {expected_body_override!r}",
            file=sys.stderr,
        )

    # --- render_classified_file: deterministic — two calls with identical input
    #     are byte-identical (idempotent regeneration, MTX-01's own criterion) ---
    cases += 1
    sample_rows = [{"param": "p", "model": "m", "mode": "default", "value": "1", "state": "unfired"}]
    first = render_classified_file(
        checked="2026-09-01", evidence_through=None, rows=sample_rows,
        scalar_count=1, content_block_count=2, skip_count=3,
    )
    second = render_classified_file(
        checked="2026-09-01", evidence_through=None, rows=sample_rows,
        scalar_count=1, content_block_count=2, skip_count=3,
    )
    if first != second:
        problems += 1
        print("FAIL render_classified_file: expected byte-identical output for identical input", file=sys.stderr)

    # --- classified_header (Phase 11.1 plan 01, D-08's stale-header fix):
    #     calling it with a hand-built count triple returns a string containing
    #     each of those three numbers and their sum — the numbers are
    #     interpolated, not decorative ---
    cases += 1
    header_a = classified_header(scalar_count=10, content_block_count=2, skip_count=5)
    for expected_number in ("12", "5", "17"):  # scalar+content_block=12, skip=5, total=17
        if expected_number not in header_a:
            problems += 1
            print(f"FAIL classified_header: expected {expected_number!r} in the rendered header, got {header_a!r}", file=sys.stderr)

    # --- classified_header: a DIFFERENT count triple produces a DIFFERENT
    #     header string — proves regenerating after evidence grows changes the
    #     stated totals instead of silently keeping the old ones (the exact
    #     staleness this fix closes) ---
    cases += 1
    header_b = classified_header(scalar_count=20, content_block_count=2, skip_count=5)
    if header_a == header_b:
        problems += 1
        print("FAIL classified_header: two different count triples produced identical header strings", file=sys.stderr)

    # --- after the fix, a fresh render's header states totals equal to the
    #     ACTUAL lengths of the three declared-cell lists on disk, and their
    #     sum equals the real classified file's own cells: count ---
    cases += 1
    real_scalar = len(load_declared_scalar()["probes"])
    real_content_block = len(load_declared_content_block()["content_block_probes"])
    real_skip = len(load_declared_skips()["skipped"])
    real_header = classified_header(
        scalar_count=real_scalar, content_block_count=real_content_block, skip_count=real_skip,
    )
    real_total = real_scalar + real_content_block + real_skip
    if str(real_total) not in real_header:
        problems += 1
        print(f"FAIL classified_header(real counts): expected the real total {real_total} in the header, got {real_header!r}", file=sys.stderr)
    if CLASSIFIED_PATH.exists():
        actual_cells = len(yaml.safe_load(CLASSIFIED_PATH.read_text())["cells"])
        if actual_cells != real_total:
            problems += 1
            print(
                f"FAIL classified_header(real counts): declared-cell sum {real_total} does not match "
                f"{CLASSIFIED_PATH}'s own cells: count {actual_cells} — regenerate before checking",
                file=sys.stderr,
            )

    # --- an unrecognized skip reason fails loud rather than silently passing
    #     through (D-11's closed vocabulary, enforced the same way SKIP_REASONS
    #     is enforced in probes/inventory-to-sets.py) ---
    cases += 1
    if "not-a-real-reason" in SKIP_REASONS:
        problems += 1
        print("FAIL SKIP_REASONS: fixture sentinel unexpectedly already a member", file=sys.stderr)

    # =========================================================================
    # Plan 11-04, Task 2 — the honor-detector dispatch, D-07's rejection-
    # strictness rule against REAL captured evidence, hazard notes, and honor-
    # detector coverage.
    # =========================================================================

    model_openai = {"wire_family": "openai_compat", "vendor": "openai"}

    # --- D-07, against a REAL captured error body (this task's own Stage 1
    #     firing, 2026-09-01): the anthropic-thinking-budget-floor row's Claude
    #     400 names its own resolved field ("thinking") -> rejected ---
    cases += 1
    real_budget_floor_row = {
        "id": "anthropic-thinking-budget-floor",
        "names": {"anthropic_messages": "thinking", "openai_compat": None, "gemini": None},
        "name_overrides": {},
    }
    real_anthropic_400_body = {
        "type": "error",
        "error": {
            "type": "invalid_request_error",
            "message": "thinking.enabled.budget_tokens: Input should be greater than or equal to 1024",
        },
        "request_id": "req_011CedX83aWSLycJzR2NDJ9R",
    }
    rec = {"terminal": "verdict", "attempts": [{"status": 400, "response_body_raw": real_anthropic_400_body}]}
    state, reason, status, honor = classify_cell(rec, real_budget_floor_row, fixture_model_anthropic)
    if state != "rejected" or reason is not None:
        problems += 1
        print(f"FAIL classify_cell(real anthropic 400, param named): got {(state, reason)}", file=sys.stderr)

    # --- D-07 companion: the SAME status, a body naming a DIFFERENT field ->
    #     needs-review, never merged into rejected ---
    cases += 1
    companion_body = {
        "type": "error",
        "error": {"type": "invalid_request_error", "message": "max_tokens: Input should be a valid integer"},
    }
    rec = {"terminal": "verdict", "attempts": [{"status": 400, "response_body_raw": companion_body}]}
    state, reason, status, honor = classify_cell(rec, real_budget_floor_row, fixture_model_anthropic)
    if (state, reason) != ("needs-review", "4xx-not-param-named"):
        problems += 1
        print(f"FAIL classify_cell(real anthropic 400, param NOT named): got {(state, reason)}", file=sys.stderr)

    # --- detect_logprobs: content present -> honored; absent -> ignored ---
    cases += 1
    logprobs_row = {
        "id": "logprobs",
        "names": {"anthropic_messages": None, "openai_compat": "logprobs", "gemini": "responseLogprobs"},
        "name_overrides": {},
    }
    rec = {
        "terminal": "verdict",
        "attempts": [{"status": 200, "response_body_raw": {
            "choices": [{"message": {"content": "hello"}, "logprobs": {"content": [{"token": "hello", "logprob": -0.1}]}}]
        }}],
        "usage": {},
    }
    state, reason, status, honor = classify_cell(rec, logprobs_row, model_openai, "True")
    if (state, honor) != ("accepted-honored", "logprobs-content"):
        problems += 1
        print(f"FAIL detect_logprobs(present): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {
        "terminal": "verdict",
        "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "hello"}, "logprobs": None}]}}],
        "usage": {},
    }
    state, reason, status, honor = classify_cell(rec, logprobs_row, model_openai, "True")
    if (state, honor) != ("accepted-ignored", "logprobs-content"):
        problems += 1
        print(f"FAIL detect_logprobs(absent): got {(state, honor)}", file=sys.stderr)

    # --- detect_candidate_count: exact match -> honored; collapsed to 1 -> ignored ---
    cases += 1
    n_row = {"id": "n", "names": {"anthropic_messages": None, "openai_compat": "n", "gemini": "candidateCount"}, "name_overrides": {}}
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"choices": [{}, {}]}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, n_row, model_openai, "2")
    if (state, honor) != ("accepted-honored", "candidate-count"):
        problems += 1
        print(f"FAIL detect_candidate_count(match): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"choices": [{}]}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, n_row, model_openai, "2")
    if (state, honor) != ("accepted-ignored", "candidate-count"):
        problems += 1
        print(f"FAIL detect_candidate_count(collapsed): got {(state, honor)}", file=sys.stderr)

    # --- detect_structured_output: valid JSON -> honored; not JSON -> ignored ---
    cases += 1
    rf_row = {"id": "response-format", "names": {"anthropic_messages": None, "openai_compat": "response_format", "gemini": "responseMimeType"}, "name_overrides": {}}
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": '{"a":1}'}}]}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, rf_row, model_openai, '{"type":"json_object"}')
    if (state, honor) != ("accepted-honored", "json-validity"):
        problems += 1
        print(f"FAIL detect_structured_output(valid): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "not json"}}]}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, rf_row, model_openai, '{"type":"json_object"}')
    if (state, honor) != ("accepted-ignored", "json-validity"):
        problems += 1
        print(f"FAIL detect_structured_output(invalid): got {(state, honor)}", file=sys.stderr)

    # --- detect_echo: same value -> honored; different value -> silently-
    #     translated; absent -> ignored (all three states this detector reaches) ---
    cases += 1
    st_row = {"id": "service-tier", "names": {"anthropic_messages": "service_tier", "openai_compat": "service_tier", "gemini": None}, "name_overrides": {}}
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"service_tier": "auto"}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, st_row, model_openai, "auto")
    if (state, honor) != ("accepted-honored", "echoed-field"):
        problems += 1
        print(f"FAIL detect_echo(same value): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {"service_tier": "default"}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, st_row, model_openai, "auto")
    if (state, honor) != ("silently-translated", "translated-field"):
        problems += 1
        print(f"FAIL detect_echo(different value): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, st_row, model_openai, "auto")
    if (state, honor) != ("accepted-ignored", "echoed-field"):
        problems += 1
        print(f"FAIL detect_echo(absent field): got {(state, honor)}", file=sys.stderr)

    # --- detect_usage (max-tokens): output within the cap -> honored; over the
    #     cap -> ignored (a structural anomaly this repo's vendors shouldn't
    #     produce, but read honestly rather than asserted impossible) ---
    cases += 1
    mt_row = {"id": "max-tokens", "names": {"anthropic_messages": "max_tokens", "openai_compat": "max_tokens", "gemini": "maxOutputTokens"}, "name_overrides": {}}
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}], "usage": {"output_tokens": 40}}
    state, reason, status, honor = classify_cell(rec, mt_row, model_openai, "64")
    if (state, honor) != ("accepted-honored", "usage-delta"):
        problems += 1
        print(f"FAIL detect_usage(max-tokens, within cap): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}], "usage": {"output_tokens": 100}}
    state, reason, status, honor = classify_cell(rec, mt_row, model_openai, "64")
    if (state, honor) != ("accepted-ignored", "usage-delta"):
        problems += 1
        print(f"FAIL detect_usage(max-tokens, over cap): got {(state, honor)}", file=sys.stderr)

    # --- detect_usage (image-input, MODAL-01): billed input tokens present ->
    #     honored; absent -> unverified (no invented claim) ---
    cases += 1
    img_row = {"id": "image-input", "names": {"anthropic_messages": None, "openai_compat": None, "gemini": None}, "name_overrides": {}}
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}], "usage": {"input_tokens": 300}}
    state, reason, status, honor = classify_cell(rec, img_row, model_openai, "content-block")
    if (state, honor) != ("accepted-honored", "usage-delta"):
        problems += 1
        print(f"FAIL detect_usage(image-input, present): got {(state, honor)}", file=sys.stderr)
    cases += 1
    rec = {"terminal": "verdict", "attempts": [{"status": 200, "response_body_raw": {}}], "usage": {}}
    state, reason, status, honor = classify_cell(rec, img_row, model_openai, "content-block")
    if (state, honor) != ("accepted-unverified", "none"):
        problems += 1
        print(f"FAIL detect_usage(image-input, absent): got {(state, honor)}", file=sys.stderr)

    # --- hazard_for: the two silent-acceptance states carry non-null hazard text;
    #     every other state (incl. accepted-honored) carries null (SWP-02) ---
    cases += 1
    if hazard_for("accepted-ignored") is None or hazard_for("silently-translated") is None:
        problems += 1
        print("FAIL hazard_for: a hazard state returned null hazard text", file=sys.stderr)
    if hazard_for("accepted-honored") is not None or hazard_for("accepted-unverified") is not None \
            or hazard_for("rejected") is not None or hazard_for("needs-review") is not None:
        problems += 1
        print("FAIL hazard_for: a non-hazard state returned non-null hazard text", file=sys.stderr)

    # --- check_honor_detector_coverage: a swept row id absent from
    #     HONOR_DETECTORS is reported; a real row id is not; the REAL registry
    #     (probes/inventory.yaml) has TOTAL coverage today (0 missing) ---
    cases += 1
    fake_inventory = {"params": [
        {"id": "temperature", "status": "swept"},
        {"id": "totally-fake-row-11-04", "status": "swept"},
        {"id": "some-excluded-row", "status": "excluded"},
    ]}
    missing = check_honor_detector_coverage(fake_inventory)
    if missing != ["totally-fake-row-11-04"]:
        problems += 1
        print(f"FAIL check_honor_detector_coverage(fixture): expected only the fake row flagged, got {missing}", file=sys.stderr)
    cases += 1
    missing_real = check_honor_detector_coverage(load_inventory())
    if missing_real:
        problems += 1
        print(f"FAIL check_honor_detector_coverage(real inventory): expected total coverage, missing {missing_real}", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="classify-probes.py",
        usage="classify-probes.py [--check | --selftest] [--raw-dir <dir>]",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--raw-dir", dest="raw_dir", default=str(DEFAULT_RAW_DIR))
    args = parser.parse_args()

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    raw_dir = Path(args.raw_dir)

    if args.check:
        checks, problems = check_generated_drift(raw_dir)
        print(f"{problems} problem(s)")
        return 1 if problems else 0

    text, rows, unmatched_overrides, ignored_records = regenerate(raw_dir)
    CLASSIFIED_DIR.mkdir(parents=True, exist_ok=True)
    CLASSIFIED_PATH.write_text(text)
    print_summary(rows, unmatched_overrides, ignored_records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
