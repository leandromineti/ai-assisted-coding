#!/usr/bin/env python3
"""probes/inventory-to-sets.py — reads probes/inventory.yaml (the parameter registry,
D-01) and probes/harness/models.yaml, and expands the registry into three generated
files under probes/sets/generated/: contract-sweep.yaml (scalar parameter probes,
runner.py's own `probes:` grammar), content-blocks.yaml (kind: content-block rows,
D-12, deliberately keyed `content_block_probes:` instead), and skipped-cells.yaml
(every param x model cell NOT emitted, with a declared reason, D-11).

    python3 probes/inventory-to-sets.py              # regenerate + print a counted summary
    python3 probes/inventory-to-sets.py --check       # validate the registry + drift-check
    python3 probes/inventory-to-sets.py --selftest    # run the embedded fixture battery

Exit codes: 0 clean, 1 problems recorded (--check/--selftest only), 2 bad invocation
(a malformed inventory.yaml/models.yaml, an unknown flag, or a registry row that
fails validation during generation — the fail-loud path never writes a partial set).

Stdlib-only scope (WR-01, phase-09 code review 2026-09-01, restated here): this repo's
wire transport/retry path is stdlib-only by design. PyYAML (`import yaml`) is NOT part
of the standard library — it is the repo's one shared, documented exception, scoped to
config/registry parsing (models.yaml, prices.yaml, ceilings.yaml, probes/sets/*.yaml,
and now probes/inventory.yaml). This module reads registry YAML and writes generated
YAML; it never touches the wire path and never imports from probes/harness/.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

# Path(__file__).resolve().parent so this runs correctly from any cwd — this module
# lives directly under probes/, so its parent IS the probes/ directory.
PROBES_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = PROBES_DIR / "inventory.yaml"
MODELS_PATH = PROBES_DIR / "harness" / "models.yaml"
GENERATED_DIR = PROBES_DIR / "sets" / "generated"

REASONING_TOGGLES = {"always-on", "default-on", "opt-in", "none"}
FIRING_SCOPES = {"all", "wire-family", "home-vendor"}
KINDS = {"parameter", "content-block"}

# Which thinking-toggle mode labels a model's reasoning_toggle actually supports
# (INV-02/D-06) — the mode-collapse-prevention table this whole generator exists to
# enforce mechanically. `default-on`/`opt-in` both accept the toggle either
# direction, so both emit; `always-on`/`none` each emit exactly one real cell and the
# missing one becomes a declared skip, never a silent absence.
MODE_LABELS_BY_TOGGLE = {
    "always-on": ("thinking-on",),
    "default-on": ("thinking-off", "thinking-on"),
    "opt-in": ("thinking-off", "thinking-on"),
    "none": ("thinking-off",),
}
SKIP_REASON_BY_TOGGLE = {
    "always-on": "no-thinking-off-toggle",
    "none": "no-thinking-capability",
}
_ALL_THINKING_MODES = {"thinking-on", "thinking-off"}

# D-08/D-11/T-10-06 (plan 10-02); extended plan 10-04 (CR-01) — the closed
# vocabulary of every reason a param x model x mode cell can be skipped
# instead of emitted. All six, named:
#
#   `no-thinking-off-toggle` / `no-thinking-capability` — from
#     modes_for_model(): a model's reasoning_toggle (always-on / none) only
#     supports one real thinking mode; the other mode is a declared skip.
#   `wire-shape-incompatible` — from firing_models(): a firing_scope of
#     wire-family or home-vendor never reaches a model outside that scope, or
#     (from axis_fragment_availability()) no axis shape exists for a model's
#     wire family at all. (These first three come from plan 10-01, unchanged.)
#   `toggle-shape-unknown` — a `vendor_overrides` entry declares an explicit
#     null on/off fragment because no documented request shape exists (e.g.
#     Kimi — an admitted unknown, not a guessed fragment).
#   `toggle-not-a-request-parameter` — a `vendor_overrides` entry declares an
#     explicit null on/off fragment because the vendor's thinking mode is not
#     a request parameter at all (e.g. DeepSeek — selected by model id).
#     (These last two are plan 10-02's — axis_fragment_availability() aborts
#     generation (fail-loud) if a null-fragment override names a reason
#     outside this set.)
#   `no-request-field-for-vendor` — plan 10-04's, closing CR-01: see below.
#
# `no-request-field-for-vendor` (added 2026-09-01, plan 10-04, closing CR-01):
# the row's parameter has no request field at this model's wire family — an
# explicit null in `names:` (D-02's checked-absence marker) with no
# `name_overrides:` entry supplying one — so there is no request body key that
# could carry the parameter at all. Before this reason existed,
# `firing_scope: all` fired these (row, model) pairs anyway and
# build_extra_params() silently omitted the key, producing a billed cell whose
# request body never contained the parameter under test (67 of 396 emitted
# scalar cells). resolve_param_name() returning None is now routed to a skip
# record with this reason (expand_params(), before mode expansion) instead of
# reaching the emit path at all.
SKIP_REASONS = frozenset({
    "no-thinking-off-toggle",
    "no-thinking-capability",
    "wire-shape-incompatible",
    "toggle-shape-unknown",
    "toggle-not-a-request-parameter",
    "no-request-field-for-vendor",
})

# Generated-file headers — module-level constants so write_generated_files() (the
# writer) and check_generated_drift() (the --check re-render-and-compare gate) share
# exactly one copy of each header string. A header defined twice would let the two
# copies drift, silently defeating the drift gate they're both part of.
CONTRACT_HEADER = (
    "# probes/sets/generated/contract-sweep.yaml — GENERATED by\n"
    "# probes/inventory-to-sets.py from probes/inventory.yaml — do not edit by\n"
    "# hand. Edit the registry, then re-run\n"
    "# `python3 probes/inventory-to-sets.py`.\n"
    "#\n"
    "# Scalar parameter probes only (kind: parameter, D-12) — runner.py's own\n"
    "# `probes:` grammar, consumed unchanged (load_probe_set)."
)
CONTENT_BLOCKS_HEADER = (
    "# probes/sets/generated/content-blocks.yaml — GENERATED by\n"
    "# probes/inventory-to-sets.py from probes/inventory.yaml — do not edit by\n"
    "# hand. Edit the registry, then re-run\n"
    "# `python3 probes/inventory-to-sets.py`.\n"
    "#\n"
    "# kind: content-block rows only (D-12). Deliberately keyed\n"
    "# `content_block_probes:`, NOT `probes:` — runner.py's load_probe_set\n"
    "# requires a `probes:` list and refuses this file loudly (exit 2, its own\n"
    "# diagnostic) rather than firing an image/cache-control row through the\n"
    "# scalar accept/reject template. A content-block-aware loader is Phase\n"
    "# 11's work (MODAL-01), not this generator's."
)
SKIPPED_HEADER = (
    "# probes/sets/generated/skipped-cells.yaml — GENERATED by\n"
    "# probes/inventory-to-sets.py from probes/inventory.yaml — do not edit by\n"
    "# hand. Edit the registry, then re-run\n"
    "# `python3 probes/inventory-to-sets.py`.\n"
    "#\n"
    "# Every param x model cell NOT emitted, with its declared reason (D-11) —\n"
    "# a skipped cell is visible evidence, never a silent absence."
)

# INV-03's nine named vendor-exotic rows (plan 10-01 Task 2) — each must exist with
# requirement: INV-03 and status: swept. check_inv03_traceability() reported
# findings when plan 10-01 wrote this comment (none of the nine rows existed
# yet, deliberately, per that plan's own dated note); the gate went green
# 2026-09-01 when plan 10-03 landed all nine (probes/inventory.yaml's header
# comment records the same scoring, dated).
INV03_ROW_IDS = frozenset({
    "openai-verbosity",
    "openai-prediction",
    "openai-service-tier-values",
    "anthropic-thinking-budget-floor",
    "gemini-media-resolution",
    "gemini-candidate-count",
    "kimi-partial-mode",
    "glm-do-sample",
    "qwen-repetition-penalty",
})

# id / row-id slug shape (D-04 encoding case): feeds probe_id's canonical hash, so
# byte-exact equality is the only equality that applies.
ROW_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REQUIRED_ROW_FIELDS = {"id", "group", "kind", "status", "canonical_name", "names", "source", "retrieved"}
REQUIRED_WIRE_FAMILIES = {"anthropic_messages", "openai_compat", "gemini"}
STATUS_ENUM = {"swept", "excluded"}
CONFIDENCE_ENUM = {"high", "medium", "low"}
AXIS_ENUM = {"none", "thinking"}


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path every
    loader/validator below uses, matching runner.py's `_fail` idiom exactly."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_yaml_mapping(path: Path) -> dict:
    """Parse a YAML file that must be a top-level mapping. Fails loud (exit 2) on
    any read, parse, or shape error — never a silent default."""
    try:
        text = path.read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict):
        _fail(2, f"{path}: expected a top-level mapping")
    return data


def load_inventory(path: Path = INVENTORY_PATH) -> dict:
    """Parse probes/inventory.yaml. Required top-level keys: checked, axes, groups,
    defaults, params. `params:` must be a non-empty list — an empty (or
    all-excluded) params list aborts before any generated file is written (edge:
    empty), matching the whole-file "never emit a partial/empty set silently"
    discipline."""
    data = load_yaml_mapping(path)
    required = {"checked", "axes", "groups", "defaults", "params"}
    missing = required - set(data)
    if missing:
        _fail(2, f"{path}: missing required top-level key(s) {sorted(missing)}")
    if not isinstance(data["params"], list):
        _fail(2, f"{path}: `params:` must be a list")
    if not data["params"]:
        _fail(2, f"{path}: `params:` is empty — refusing to write an empty generated set")
    if not isinstance(data["groups"], list):
        _fail(2, f"{path}: `groups:` must be a list")
    return data


def load_models(path: Path = MODELS_PATH) -> list[dict]:
    """Parse probes/harness/models.yaml, validating that every row's
    reasoning_toggle is present and in the closed enum. A missing or
    out-of-enum reasoning_toggle aborts (exit 2) rather than defaulting to a flat
    cell — the mode-collapse failure this whole phase exists to prevent."""
    data = load_yaml_mapping(path)
    if not isinstance(data.get("models"), list):
        _fail(2, f"{path}: expected a top-level `models:` list")
    rows = data["models"]
    for row in rows:
        toggle = row.get("reasoning_toggle")
        if toggle not in REASONING_TOGGLES:
            _fail(
                2,
                f"{path}: model {row.get('slug', '?')!r} has reasoning_toggle="
                f"{toggle!r}, expected one of {sorted(REASONING_TOGGLES)}",
            )
    return rows


def firing_models(row: dict, models: list[dict]) -> tuple[list[dict], list[tuple[dict, str]]]:
    """D-11: vendor-exotic firing scope. `all` fires everywhere. `wire-family`
    fires only at models sharing the row's one non-null `names:` wire family.
    `home-vendor` fires only at models matching the row's one `name_overrides:`
    vendor key. Every non-firing pair is returned as (model, reason) for the
    caller to record as a skipped cell (D-11: never a silent absence)."""
    scope = row.get("firing_scope", "all")
    if scope not in FIRING_SCOPES:
        _fail(2, f"row {row['id']!r}: unknown firing_scope {scope!r}, expected one of {sorted(FIRING_SCOPES)}")

    if scope == "all":
        return list(models), []

    if scope == "wire-family":
        home_families = [fam for fam, name in (row.get("names") or {}).items() if name is not None]
        if len(home_families) != 1:
            _fail(
                2,
                f"row {row['id']!r}: firing_scope=wire-family requires exactly one "
                f"non-null wire_family key in `names:`, found {home_families}",
            )
        home_family = home_families[0]
        fire = [m for m in models if m["wire_family"] == home_family]
        skip = [m for m in models if m["wire_family"] != home_family]
        return fire, [(m, "wire-shape-incompatible") for m in skip]

    # scope == "home-vendor"
    home_vendors = list((row.get("name_overrides") or {}).keys())
    if len(home_vendors) != 1:
        _fail(
            2,
            f"row {row['id']!r}: firing_scope=home-vendor requires exactly one "
            f"vendor key in `name_overrides:`, found {home_vendors}",
        )
    home_vendor = home_vendors[0]
    fire = [m for m in models if m["vendor"] == home_vendor]
    skip = [m for m in models if m["vendor"] != home_vendor]
    return fire, [(m, "wire-shape-incompatible") for m in skip]


def modes_for_model(row: dict, model: dict) -> tuple[list[str], list[tuple[str, str]]]:
    """(INV-02/D-06) A row with no axis (or axis: none) emits a single 'default'
    mode and never skips. A row with axis: thinking emits per the model's
    reasoning_toggle — see MODE_LABELS_BY_TOGGLE. Returns (emitted_modes,
    [(skipped_mode, reason), ...])."""
    axis = row.get("axis") or "none"
    if axis == "none":
        return ["default"], []
    if axis != "thinking":
        _fail(2, f"row {row['id']!r}: unknown axis {axis!r}, expected 'none' or 'thinking'")

    toggle = model["reasoning_toggle"]
    emitted = list(MODE_LABELS_BY_TOGGLE[toggle])
    reason = SKIP_REASON_BY_TOGGLE.get(toggle)
    missing = sorted(_ALL_THINKING_MODES - set(emitted))
    skipped = [(m, reason) for m in missing] if reason else []
    return emitted, skipped


def axis_fragment_availability(row: dict, model: dict, inventory: dict, mode: str) -> tuple[bool, str | None]:
    """(D-08/T-10-06, plan 10-02) Whether a REAL request fragment can be
    constructed for this row's axis at this model's wire family + vendor +
    mode, BEFORE axis_fragment() is called. A `vendor_overrides` entry whose
    on/off value is an explicit null means no fragment exists — the caller
    must record a skipped cell with the override's own declared `reason`
    instead of emitting one. Never called for a row with no axis (or a
    'default' mode); only thinking-on/thinking-off cells reach here."""
    wire_family = model["wire_family"]
    shapes = inventory["axes"][row["axis"]]["shapes"]
    shape = shapes.get(wire_family)
    if shape is None:
        return False, "wire-shape-incompatible"
    key = "on" if mode == "thinking-on" else "off"
    vendor_overrides = shape.get("vendor_overrides") or {}
    override = vendor_overrides.get(model["vendor"])
    if override is not None and key in override and override[key] is None:
        reason = override.get("reason")
        if reason not in SKIP_REASONS:
            _fail(
                2,
                f"row {row['id']!r}: vendor override for {model['vendor']!r} declares "
                f"a null {key!r} fragment but its `reason:` {reason!r} is not in the "
                f"closed skip-reason vocabulary {sorted(SKIP_REASONS)}",
            )
        return False, reason
    return True, None


def axis_fragment(row: dict, model: dict, inventory: dict, mode: str) -> dict:
    """The fixed request fragment (D-08) for this wire family + mode, with any
    vendor override applied. Only called for a thinking-on/thinking-off mode —
    'default' mode never reaches here."""
    wire_family = model["wire_family"]
    shapes = inventory["axes"][row["axis"]]["shapes"]
    shape = shapes.get(wire_family)
    if shape is None:
        _fail(2, f"row {row['id']!r}: no axis shape declared for wire_family={wire_family!r}")
    key = "on" if mode == "thinking-on" else "off"
    vendor_overrides = shape.get("vendor_overrides") or {}
    override = vendor_overrides.get(model["vendor"])
    if override is not None and key in override:
        return override[key]
    return shape[key]


def resolve_param_name(row: dict, model: dict) -> str | None:
    """The single name-resolution path for a (row, model) pair (D-02): the
    row's per-wire-family `names:` value, unless a `name_overrides:` entry for
    the model's vendor wins over the family default. A wire_family key OMITTED
    from `names:` is a registry authoring error — fail loud (exit 2) with the
    existing "omitted means not-checked" diagnostic, never treated as a skip.
    An explicit null with no vendor override returns None: the row's parameter
    has no request field at this model's wire family (D-02's checked-absence
    marker) — the caller (expand_params(), via CR-01's fix) routes that to a
    skipped-cells.yaml record with reason `no-request-field-for-vendor` rather
    than reaching the emit path with nothing to emit."""
    wire_family = model["wire_family"]
    names = row.get("names") or {}
    if wire_family not in names:
        _fail(
            2,
            f"row {row['id']!r}: `names:` omits wire_family={wire_family!r} — "
            "omitted means not-checked (use an explicit null for checked-and-absent, D-02)",
        )
    param_name = names[wire_family]
    override_name = (row.get("name_overrides") or {}).get(model["vendor"])
    if override_name is not None:
        param_name = override_name
    return param_name


def build_extra_params(row: dict, model: dict, inventory: dict, mode: str, value) -> dict:
    """extra_params = the row's per-family parameter name (resolve_param_name())
    mapped to the probe value, merged with the axis fragment for that family
    (with the vendor override applied when one exists). For a
    thinking-on/thinking-off cell the axis fragment is always present; for
    'default' it is absent (D-06).

    CR-01 (plan 10-04): expand_params() routes a None-resolving (row, model)
    pair to a skip record BEFORE calling this function, so `param_name is
    None` here should be unreachable. The write below is unconditional, with a
    fail-loud guard on that unreachable case, on purpose — a future regression
    that re-introduces a silent `if param_name is not None:` omission turns
    loud instead of shipping a zero-signal billed cell again."""
    param_name = resolve_param_name(row, model)
    if param_name is None:
        _fail(
            2,
            f"row {row['id']!r}: resolve_param_name() returned None for model "
            f"{model['slug']!r} inside build_extra_params() — expand_params() "
            "should have routed this (row, model) pair to a "
            "no-request-field-for-vendor skip before reaching here (CR-01)",
        )

    extra: dict = {param_name: value}
    if mode in _ALL_THINKING_MODES:
        # deepcopy: the same axis-shape fragment dict is looked up for every
        # (family, mode) pair across many entries — without a copy, every entry
        # sharing a fragment would hold the SAME nested dict object, and PyYAML's
        # dumper would render that shared identity as an anchor/alias pair
        # (&id001 / *id001) rather than independent, self-contained entries.
        extra.update(copy.deepcopy(axis_fragment(row, model, inventory, mode)))
    return extra


def render_value(value) -> str:
    """Probe value rendered as a string for the `value:` entry field (matching
    probes/sets/*.yaml's existing string-value convention, e.g. `value: none`,
    `value: invalid-negative`) and for probe_id's canonical hash input.

    A non-scalar value (dict/list — logit-bias, stream-options-include-usage,
    and other rows whose probe_values are containers) renders via
    `json.dumps(value, sort_keys=True, separators=(",", ":"))` (WR-01, plan
    10-04), not `str(value)`. The rendered string is therefore deterministic
    across Python versions BECAUSE it is JSON — a fixed, spec-defined text
    format — rather than a CPython container repr (`str(dict)`/`str(list)`),
    whose quoting (single vs double), capitalization (`True` vs `true`), and
    key order have no cross-version or cross-implementation guarantee. Scalars
    (str, int, float) still render via `str(value)` unchanged; bool keeps its
    existing lowercase `true`/`false` branch (runner.py's probe-set
    convention), which `json.dumps` would also produce for a bare bool but the
    explicit branch is kept so this function's scalar path is unchanged."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def max_tokens_for(defaults: dict, model_slug: str) -> int:
    overrides = defaults.get("max_tokens_overrides") or {}
    return overrides.get(model_slug, defaults["max_tokens"])


def _skip_record(row: dict, model: dict, mode: str, reason: str) -> dict:
    return {"model": model["slug"], "param": row["id"], "mode": mode, "reason": reason}


def expand_params(inventory: dict, models: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Expand every swept row in probes/inventory.yaml's `params:` list against
    the 12 models.yaml rows. Returns (scalar_entries, content_block_entries,
    skipped_entries), each already in deterministic emission order (sort by
    group order, row id, models.yaml row index, mode label — never a dict or set
    iteration order, so regeneration with no inventory edit is byte-stable)."""
    groups_by_id = {g["id"]: g for g in inventory["groups"]}
    model_index = {m["slug"]: i for i, m in enumerate(models)}
    row_sort_key = {
        row["id"]: (groups_by_id[row["group"]]["order"], row["id"])
        for row in inventory["params"]
        if row.get("group") in groups_by_id
    }

    scalar_entries: list[dict] = []
    content_block_entries: list[dict] = []
    skipped_entries: list[dict] = []

    defaults = inventory["defaults"]
    prompt = defaults["prompt"]

    for row in inventory["params"]:
        if row.get("status") != "swept":
            # D-09: excluded rows are visible in inventory.yaml but never emit —
            # the generator skips rows by status.
            continue
        if row["group"] not in groups_by_id:
            _fail(2, f"row {row['id']!r}: unknown group {row['group']!r}")
        kind = row.get("kind", "parameter")
        if kind not in KINDS:
            _fail(2, f"row {row['id']!r}: unknown kind {kind!r}, expected one of {sorted(KINDS)}")

        fire, scope_skips = firing_models(row, models)
        for model, reason in scope_skips:
            skipped_entries.append(_skip_record(row, model, "n/a", reason))

        if kind == "content-block":
            # D-12: never enters the scalar accept/reject template. Not exercised
            # in this plan (no content-block row exists yet — that authoring is
            # Phase 11's MODAL-01), but routed correctly now so a future row needs
            # no generator change.
            for model in fire:
                content_block_entries.append({
                    "model": model["slug"],
                    "param": row["id"],
                    "body_template": row.get("body_template"),
                })
            continue

        # kind == "parameter"
        probe_values = row.get("probe_values") or []
        if not probe_values:
            _fail(2, f"row {row['id']!r}: status=swept, kind=parameter requires a non-empty probe_values list")
        for model in fire:
            # CR-01 (plan 10-04): resolve the row's parameter name for this
            # model BEFORE mode expansion. A None resolution (an explicit null
            # in `names:` with no vendor override — D-02's checked-absence
            # marker) means no request body key exists that could carry the
            # parameter at all, for EVERY mode this (row, model) pair would
            # otherwise fire. One record at mode `n/a` — a name that does not
            # resolve is a property of the pair, not of a mode, mirroring the
            # existing firing_models() scope-skip records above; recording it
            # per mode would double-count the same cause.
            if resolve_param_name(row, model) is None:
                skipped_entries.append(_skip_record(row, model, "n/a", "no-request-field-for-vendor"))
                continue
            emitted_modes, skip_pairs = modes_for_model(row, model)
            for skip_mode, reason in skip_pairs:
                skipped_entries.append(_skip_record(row, model, skip_mode, reason))
            for mode in emitted_modes:
                if mode in _ALL_THINKING_MODES:
                    # D-08/T-10-06 (plan 10-02): a vendor override may declare
                    # no real fragment (null on/off) — skip with its own
                    # reason rather than crash or invent a request body.
                    available, reason = axis_fragment_availability(row, model, inventory, mode)
                    if not available:
                        skipped_entries.append(_skip_record(row, model, mode, reason))
                        continue
                for value in probe_values:
                    scalar_entries.append({
                        "model": model["slug"],
                        "param": row["id"],
                        "value": render_value(value),
                        "mode": mode,
                        "prompt": prompt,
                        "max_tokens": max_tokens_for(defaults, model["slug"]),
                        "extra_params": build_extra_params(row, model, inventory, mode, value),
                    })

    def sort_key(entry: dict) -> tuple:
        group_order, row_id = row_sort_key[entry["param"]]
        return (group_order, row_id, model_index[entry["model"]], entry.get("mode", ""))

    scalar_entries.sort(key=sort_key)
    content_block_entries.sort(key=lambda e: (row_sort_key[e["param"]], model_index[e["model"]]))
    skipped_entries.sort(key=sort_key)

    return scalar_entries, content_block_entries, skipped_entries


def render_generated_file(*, header: str, checked, top_key: str, payload: list) -> str:
    """Every generated file: a header comment (generator, input registry, the
    instruction that it is generated and never hand-edited), a `checked:` date
    carried straight from the input registry (never wall-clock time — a
    generation-timestamp header would make idempotent regeneration impossible to
    prove byte-stable across days), then its single top-level key."""
    doc = {"checked": checked, top_key: payload}
    body = yaml.safe_dump(doc, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
    return header.rstrip("\n") + "\n\n" + body


def write_generated_files(
    inventory: dict,
    scalar_entries: list[dict],
    content_block_entries: list[dict],
    skipped_entries: list[dict],
    generated_dir: Path = GENERATED_DIR,
) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)
    checked = inventory["checked"]

    (generated_dir / "contract-sweep.yaml").write_text(
        render_generated_file(header=CONTRACT_HEADER, checked=checked, top_key="probes", payload=scalar_entries)
    )
    (generated_dir / "content-blocks.yaml").write_text(
        render_generated_file(
            header=CONTENT_BLOCKS_HEADER, checked=checked, top_key="content_block_probes", payload=content_block_entries
        )
    )
    (generated_dir / "skipped-cells.yaml").write_text(
        render_generated_file(header=SKIPPED_HEADER, checked=checked, top_key="skipped", payload=skipped_entries)
    )


def print_summary(
    inventory: dict,
    scalar_entries: list[dict],
    content_block_entries: list[dict],
    skipped_entries: list[dict],
) -> None:
    """A counted summary that states each count's measure (CLAUDE.md: "a count
    carries its measure") — row counts by status, emitted scalar/content-block
    counts, and a skipped-cell count broken down by reason. Plan 10-03's
    SWEEP-DESIGN.md derives its expected cell count from this printed summary."""
    status_counts: dict[str, int] = {}
    for row in inventory["params"]:
        status = row.get("status", "?")
        status_counts[status] = status_counts.get(status, 0) + 1
    total_rows = len(inventory["params"])
    status_str = ", ".join(f"{k}={v}" for k, v in sorted(status_counts.items()))
    print(f"params rows: {total_rows} total ({status_str})")
    print(f"emitted scalar probes (one row x model x mode x value expansion each): {len(scalar_entries)}")
    print(f"emitted content-block probes: {len(content_block_entries)}")

    reason_counts: dict[str, int] = {}
    for skip in skipped_entries:
        reason_counts[skip["reason"]] = reason_counts.get(skip["reason"], 0) + 1
    reason_str = ", ".join(f"{k}={v}" for k, v in sorted(reason_counts.items())) or "none"
    print(f"skipped cells (param x model pairs never emitted, D-11): {len(skipped_entries)} ({reason_str})")


# -----------------------------------------------------------------------------------
# Validators (plan 10-01 Task 2). Each returns (checks_run, problems) — the same
# shared shape scripts/check-taxonomy.py's checker functions use — so --check and
# --selftest fold them into one trailing "N problem(s)" line with a single
# implementation and two entry points (D-04).
# -----------------------------------------------------------------------------------


def check_required_fields(rows: list[dict]) -> tuple[int, int]:
    """Every row: id, group, kind, status, canonical_name, names, source,
    retrieved. Plus excluded_reason/excluded_at when status=excluded; body_template
    when kind=content-block; probe_values/firing_scope when status=swept and
    kind=parameter (or omitted kind, which defaults to parameter)."""
    checks = 0
    problems = 0
    for row in rows:
        checks += 1
        missing = set(REQUIRED_ROW_FIELDS) - set(row)
        if row.get("status") == "excluded":
            missing |= {"excluded_reason", "excluded_at"} - set(row)
        if row.get("kind") == "content-block":
            missing |= {"body_template"} - set(row)
        if row.get("status") == "swept" and row.get("kind", "parameter") == "parameter":
            missing |= {"probe_values", "firing_scope"} - set(row)
        if missing:
            problems += 1
            print(
                f"FAIL required fields: row {row.get('id', '?')!r} missing {sorted(missing)}",
                file=sys.stderr,
            )
    return checks, problems


def check_id_format(rows: list[dict]) -> tuple[int, int]:
    """A row id is a lowercase ASCII slug matching ^[a-z0-9][a-z0-9-]*$ — it feeds
    runner.probe_id's canonical hash, so byte-exact equality is the only equality
    that applies (edge: adjacency, encoding)."""
    checks = 0
    problems = 0
    for row in rows:
        checks += 1
        rid = row.get("id")
        if not isinstance(rid, str) or not ROW_ID_RE.match(rid):
            problems += 1
            print(
                f"FAIL id format: row id {rid!r} is not a lowercase ASCII slug "
                "matching ^[a-z0-9][a-z0-9-]*$",
                file=sys.stderr,
            )
    return checks, problems


def check_duplicate_ids(rows: list[dict]) -> tuple[int, int]:
    """Two rows may not share an id — exact-equality collision, not a merge
    (edge: adjacency)."""
    checks = 1
    seen: set = set()
    dupes: set = set()
    for row in rows:
        rid = row.get("id")
        if rid in seen:
            dupes.add(rid)
        seen.add(rid)
    if dupes:
        print(f"FAIL duplicate ids: {sorted(dupes)}", file=sys.stderr)
        return checks, 1
    return checks, 0


def check_enums(rows: list[dict]) -> tuple[int, int]:
    """status/kind/firing_scope/confidence/axis outside their closed enum are
    flagged, never coerced."""
    checks = 0
    problems = 0
    for row in rows:
        checks += 1
        bad = []
        if "status" in row and row["status"] not in STATUS_ENUM:
            bad.append(("status", row["status"]))
        if "kind" in row and row["kind"] not in KINDS:
            bad.append(("kind", row["kind"]))
        if "firing_scope" in row and row["firing_scope"] not in FIRING_SCOPES:
            bad.append(("firing_scope", row["firing_scope"]))
        if "confidence" in row and row["confidence"] not in CONFIDENCE_ENUM:
            bad.append(("confidence", row["confidence"]))
        if "axis" in row and row["axis"] not in AXIS_ENUM:
            bad.append(("axis", row["axis"]))
        if bad:
            problems += 1
            print(f"FAIL enum: row {row.get('id', '?')!r} has out-of-enum value(s) {bad}", file=sys.stderr)
    return checks, problems


def check_names_map(rows: list[dict]) -> tuple[int, int]:
    """(D-02) A `names:` map with an OMITTED family key is flagged (means
    not-checked, and the generator would abort on it at expansion time); an
    explicit `null` for a family is accepted (means checked-and-absent, and
    produces a skipped cell for that family, never a silent omission)."""
    checks = 0
    problems = 0
    for row in rows:
        if row.get("kind", "parameter") != "parameter":
            continue
        checks += 1
        names = row.get("names")
        if not isinstance(names, dict):
            problems += 1
            print(f"FAIL names map: row {row.get('id', '?')!r} has no `names:` mapping", file=sys.stderr)
            continue
        missing = REQUIRED_WIRE_FAMILIES - set(names)
        if missing:
            problems += 1
            print(
                f"FAIL names map: row {row.get('id', '?')!r} omits wire_family "
                f"key(s) {sorted(missing)} — omitted means not-checked; use an "
                "explicit null for checked-and-absent (D-02)",
                file=sys.stderr,
            )
    return checks, problems


def check_boundary_contract(rows: list[dict]) -> tuple[int, int]:
    """(D-03) A swept parameter row with more than one probe_values entry but no
    boundary_contract: true is flagged — extra values are allowed only where the
    row's finding IS the boundary contract."""
    checks = 0
    problems = 0
    for row in rows:
        if row.get("kind", "parameter") != "parameter" or row.get("status") != "swept":
            continue
        checks += 1
        values = row.get("probe_values") or []
        if len(values) > 1 and not row.get("boundary_contract"):
            problems += 1
            print(
                f"FAIL boundary_contract: row {row.get('id', '?')!r} declares "
                f"{len(values)} probe_values but no boundary_contract: true (D-03)",
                file=sys.stderr,
            )
    return checks, problems


def check_axis_declaration(rows: list[dict]) -> tuple[int, int]:
    """(INV-02's own success criterion) The `sampling` group is where D-07 says the
    thinking axis applies broadly, not only where a vendor documented
    mode-dependence — so every swept parameter row in that group must declare an
    explicit `axis:` key (even `axis: none` for a genuine exception), rather than
    silently omitting it. A row in any other group is not required to."""
    checks = 0
    problems = 0
    for row in rows:
        if row.get("kind", "parameter") != "parameter" or row.get("status") != "swept":
            continue
        checks += 1
        if row.get("group") == "sampling" and "axis" not in row:
            problems += 1
            print(
                f"FAIL axis declaration: row {row.get('id', '?')!r} is in the "
                "sampling group (mode-dependent by D-07) but declares no `axis:` key",
                file=sys.stderr,
            )
    return checks, problems


def check_inv03_traceability(rows: list[dict]) -> tuple[int, int]:
    """INV-03: the nine named vendor-exotic rows must each exist with
    requirement: INV-03 and status: swept. Expected to report findings until plan
    10-03 authors them — wired as a normal finding, recorded red-by-design in
    probes/inventory.yaml's header comment (dated), never silently weakened."""
    checks = 1
    by_id = {row.get("id"): row for row in rows}
    missing = [
        rid
        for rid in sorted(INV03_ROW_IDS)
        if by_id.get(rid) is None
        or by_id[rid].get("requirement") != "INV-03"
        or by_id[rid].get("status") != "swept"
    ]
    if missing:
        print(
            f"FAIL INV-03 traceability: {len(missing)} of {len(INV03_ROW_IDS)} "
            f"named exotic rows not yet authored/traceable: {missing}",
            file=sys.stderr,
        )
        return checks, 1
    return checks, 0


def run_registry_checks(inventory: dict) -> tuple[int, int]:
    """Fold every row-level validator above into one (checks_run, problems) pair —
    shared by --check (against the real registry) and --selftest (against
    synthetic fixtures)."""
    rows = inventory["params"]
    checks = 0
    problems = 0
    for fn in (
        check_required_fields,
        check_id_format,
        check_duplicate_ids,
        check_enums,
        check_names_map,
        check_boundary_contract,
        check_axis_declaration,
        check_inv03_traceability,
    ):
        c, p = fn(rows)
        checks += c
        problems += p
    return checks, problems


def check_generated_drift(inventory: dict, models: list[dict], generated_dir: Path = GENERATED_DIR) -> tuple[int, int]:
    """(rule 3 drift gate) Re-render all three generated files in memory from the
    real registry and compare them byte-for-byte with what is on disk. A
    hand-edited (or stale) generated file no longer matches its registry, and this
    is what makes the check say so."""
    scalar_entries, content_block_entries, skipped_entries = expand_params(inventory, models)
    checked = inventory["checked"]
    expected = {
        generated_dir / "contract-sweep.yaml": render_generated_file(
            header=CONTRACT_HEADER, checked=checked, top_key="probes", payload=scalar_entries
        ),
        generated_dir / "content-blocks.yaml": render_generated_file(
            header=CONTENT_BLOCKS_HEADER, checked=checked, top_key="content_block_probes", payload=content_block_entries
        ),
        generated_dir / "skipped-cells.yaml": render_generated_file(
            header=SKIPPED_HEADER, checked=checked, top_key="skipped", payload=skipped_entries
        ),
    }
    checks = 0
    problems = 0
    for path, expected_text in expected.items():
        checks += 1
        if not path.exists():
            problems += 1
            print(f"FAIL drift: {path} does not exist — run the generator", file=sys.stderr)
            continue
        actual_text = path.read_text()
        if actual_text != expected_text:
            problems += 1
            print(
                f"FAIL drift: {path} does not match a fresh render of "
                f"{INVENTORY_PATH} — it was hand-edited or is stale (rule 3)",
                file=sys.stderr,
            )
    return checks, problems


def _carries_param_problems(rows_by_id: dict, models_by_slug: dict, entries: list[dict]) -> tuple[int, int]:
    """The pure check underlying check_emitted_carries_param() — takes an
    already-built scalar entry list directly, so --selftest can hand it a
    synthetic no-op cell without routing it through expand_params() (which
    now refuses to produce one, CR-01). One check counted per entry."""
    checks = 0
    problems = 0
    for entry in entries:
        checks += 1
        row = rows_by_id[entry["param"]]
        model = models_by_slug[entry["model"]]
        resolved_name = resolve_param_name(row, model)
        if resolved_name is None or resolved_name not in (entry.get("extra_params") or {}):
            problems += 1
            print(
                f"FAIL emitted carries param (CR-01): row {entry['param']!r} at "
                f"model {entry['model']!r}, mode {entry.get('mode')!r} — resolved "
                f"parameter name {resolved_name!r} is not a key of extra_params "
                f"{entry.get('extra_params')!r}",
                file=sys.stderr,
            )
    return checks, problems


def check_emitted_carries_param(inventory: dict, models: list[dict]) -> tuple[int, int]:
    """(CR-01, plan 10-04) Every emitted scalar entry must carry its own row's
    resolved parameter name as a key in `extra_params` — the class of defect
    this check exists to catch closed with an escaped no-op cell (67 of 396
    emitted scalar cells carried no trace of their own parameter, silently,
    because `firing_scope: all` fired regardless of whether the row's `names:`
    map resolved for the model's wire family).

    Expands the registry in memory via expand_params() (mirroring
    check_generated_drift()'s in-memory re-render), then delegates the actual
    per-entry check to _carries_param_problems() — the shared pure function
    --selftest also exercises directly with synthetic entries."""
    rows_by_id = {row["id"]: row for row in inventory["params"]}
    models_by_slug = {m["slug"]: m for m in models}
    scalar_entries, _content_block_entries, _skipped_entries = expand_params(inventory, models)
    return _carries_param_problems(rows_by_id, models_by_slug, scalar_entries)


# -----------------------------------------------------------------------------------
# --selftest (plan 10-01 Task 2) — embedded fixtures, no external test framework,
# following probes/harness/ledger.py's and runner.py's own selftest() house style:
# tempfile.TemporaryDirectory() for cases that exercise a file-loading fail-loud
# path or the on-disk drift gate; direct in-memory dicts for cases that exercise a
# pure validator function (matching runner.py's own mix, e.g. probe_id/build_record
# vs seen_probe_ids).
# -----------------------------------------------------------------------------------


def _valid_row(**overrides) -> dict:
    """A minimal, fully valid swept-parameter row — every selftest fixture starts
    here and mutates/deletes exactly the field(s) under test, so a fixture failure
    is never accidentally caused by an unrelated missing field."""
    row = {
        "id": "fixture-param",
        "group": "structural",
        "kind": "parameter",
        "status": "swept",
        "canonical_name": "fixture_param",
        "names": {"anthropic_messages": "fixture_param", "openai_compat": "fixture_param", "gemini": "fixture_param"},
        "source": "https://example.com/docs",
        "retrieved": "2026-09-01",
        "probe_values": [1],
        "firing_scope": "all",
        "confidence": "high",
    }
    row.update(overrides)
    return row


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    # --- required fields: a row missing `source` is flagged, naming the row id
    #     and the missing field ---
    cases += 1
    row = _valid_row()
    del row["source"]
    _, p = check_required_fields([row])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_required_fields did not flag a row missing `source`", file=sys.stderr)

    # --- required fields: status=excluded requires excluded_reason + excluded_at ---
    cases += 1
    excluded_row = _valid_row(status="excluded")
    del excluded_row["probe_values"]
    del excluded_row["firing_scope"]
    _, p = check_required_fields([excluded_row])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_required_fields did not flag an excluded row missing excluded_reason/excluded_at", file=sys.stderr)
    excluded_row["excluded_reason"] = "out of scope"
    excluded_row["excluded_at"] = "2026-09-01"
    _, p = check_required_fields([excluded_row])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_required_fields flagged a correctly-excluded row", file=sys.stderr)

    # --- duplicate ids: two rows sharing an id are flagged ---
    cases += 1
    row_a = _valid_row(id="dup-id")
    row_b = _valid_row(id="dup-id")
    _, p = check_duplicate_ids([row_a, row_b])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_duplicate_ids did not flag two rows sharing an id", file=sys.stderr)
    _, p = check_duplicate_ids([_valid_row(id="a"), _valid_row(id="b")])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_duplicate_ids flagged two rows with distinct ids", file=sys.stderr)

    # --- id format: a non-slug id is flagged (uppercase, underscore, leading
    #     digit-then-dot — none match ^[a-z0-9][a-z0-9-]*$) ---
    cases += 1
    bad_ids = ["Temperature", "temp_erature", "temperature!", ""]
    _, p = check_id_format([_valid_row(id=bad) for bad in bad_ids])
    if p != len(bad_ids):
        problems += 1
        print(f"FAIL selftest: check_id_format expected {len(bad_ids)} findings for {bad_ids}, got {p}", file=sys.stderr)
    _, p = check_id_format([_valid_row(id="a-valid-slug-99")])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_id_format flagged a valid slug", file=sys.stderr)

    # --- empty params list (or all-excluded-so-effectively-empty) aborts before
    #     any file is written, rather than emitting an empty/partial set ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        bad_path = Path(td) / "empty.yaml"
        bad_path.write_text(yaml.safe_dump({
            "checked": "2026-09-01", "axes": {}, "groups": [], "defaults": {"prompt": "hi", "max_tokens": 16}, "params": [],
        }))
        try:
            load_inventory(bad_path)
            problems += 1
            print("FAIL selftest: load_inventory did not abort on an empty params list", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL selftest: load_inventory(empty params) expected exit 2, got {e.code}", file=sys.stderr)

    # --- names map: an omitted family key is flagged; an explicit null is
    #     accepted (D-02: omitted=not-checked, null=checked-and-absent) ---
    cases += 1
    omitted_row = _valid_row(names={"anthropic_messages": "x", "openai_compat": "x"})  # gemini key omitted
    _, p = check_names_map([omitted_row])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_names_map did not flag an omitted wire_family key", file=sys.stderr)
    null_row = _valid_row(names={"anthropic_messages": "x", "openai_compat": "x", "gemini": None})
    _, p = check_names_map([null_row])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_names_map flagged an explicit null wire_family value", file=sys.stderr)

    # --- names map with explicit null produces a DECLARED SKIP for that family
    #     (CR-01, plan 10-04) — zero scalar entries for the null-family model,
    #     exactly one skipped record with reason no-request-field-for-vendor at
    #     mode n/a, and the non-null-family model still carrying its parameter.
    #     (Pre-CR-01 this case asserted only "gemini_entries emit no `x` key" —
    #     satisfied vacuously once the fix landed, since gemini_entries becomes
    #     an empty list. Rewritten to pin the real post-fix contract instead of
    #     a check that now passes for free.) ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        null_family_row = _valid_row(
            id="null-family-param",
            names={"anthropic_messages": "x", "openai_compat": "x", "gemini": None},
        )
        fixture_inventory = {
            "checked": "2026-09-01",
            "axes": {},
            "groups": [{"id": "structural", "title": "Structural", "order": 20, "blurb": "x"}],
            "defaults": {"prompt": "hi", "max_tokens": 16},
            "params": [null_family_row],
        }
        fixture_models = [
            {"slug": "m-anthropic", "vendor": "anthropic", "wire_family": "anthropic_messages", "reasoning_toggle": "none"},
            {"slug": "m-gemini", "vendor": "gemini", "wire_family": "gemini", "reasoning_toggle": "none"},
        ]
        scalar, _cb, skipped = expand_params(fixture_inventory, fixture_models)
        gemini_entries = [e for e in scalar if e["model"] == "m-gemini"]
        if gemini_entries:
            problems += 1
            print("FAIL selftest: a null names entry emitted a scalar cell instead of a declared skip", file=sys.stderr)
        gemini_skips = [
            s for s in skipped
            if s["model"] == "m-gemini" and s["param"] == "null-family-param"
        ]
        if len(gemini_skips) != 1 or gemini_skips[0]["reason"] != "no-request-field-for-vendor" or gemini_skips[0]["mode"] != "n/a":
            problems += 1
            print(
                f"FAIL selftest: expected exactly one no-request-field-for-vendor "
                f"skip at mode n/a for the null-family model, got {gemini_skips}",
                file=sys.stderr,
            )
        anthropic_entries = [e for e in scalar if e["model"] == "m-anthropic"]
        if not anthropic_entries or "x" not in anthropic_entries[0]["extra_params"]:
            problems += 1
            print("FAIL selftest: a non-null names entry did not emit the parameter", file=sys.stderr)

    # --- enums: status/kind/firing_scope/confidence/axis outside their closed
    #     enum are flagged, never coerced ---
    cases += 1
    bad_enum_row = _valid_row(status="maybe", kind="widget", firing_scope="everywhere", confidence="medium-ish", axis="vibes")
    _, p = check_enums([bad_enum_row])
    if p != 1:  # one row, one finding naming all five bad values
        problems += 1
        print("FAIL selftest: check_enums did not flag a row with five out-of-enum values", file=sys.stderr)
    _, p = check_enums([_valid_row(axis="thinking")])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_enums flagged valid enum values", file=sys.stderr)

    # --- boundary_contract: >1 probe_values without boundary_contract: true is
    #     flagged; the same row with boundary_contract: true is accepted (D-03) ---
    cases += 1
    multi_value_row = _valid_row(probe_values=[1, 2, 3])
    _, p = check_boundary_contract([multi_value_row])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_boundary_contract did not flag >1 probe_values with no boundary_contract", file=sys.stderr)
    multi_value_row["boundary_contract"] = True
    _, p = check_boundary_contract([multi_value_row])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_boundary_contract flagged a row that declares boundary_contract: true", file=sys.stderr)

    # --- axis declaration: a sampling-group row with no `axis` key is flagged —
    #     and REMOVING the axis key from a passing fixture flips it to a finding,
    #     proving the check discriminates (methodology rule 5d) ---
    cases += 1
    sampling_row = _valid_row(group="sampling", axis="thinking")
    _, p = check_axis_declaration([sampling_row])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_axis_declaration flagged a sampling row that DOES declare axis", file=sys.stderr)
    del sampling_row["axis"]
    _, p = check_axis_declaration([sampling_row])
    if p != 1:
        problems += 1
        print("FAIL selftest: removing `axis` from a sampling-group fixture did not make the axis check report a problem (INV-02 has no teeth)", file=sys.stderr)
    structural_row = _valid_row(group="structural")  # _valid_row never sets `axis`
    _, p = check_axis_declaration([structural_row])
    if p != 0:
        problems += 1
        print("FAIL selftest: check_axis_declaration flagged a non-sampling row with no axis key (only sampling is required)", file=sys.stderr)

    # --- INV-03 traceability: a fixture missing all nine named rows is flagged;
    #     a fixture declaring all nine (requirement: INV-03, status: swept) is not ---
    cases += 1
    _, p = check_inv03_traceability([_valid_row(id="unrelated-row")])
    if p != 1:
        problems += 1
        print("FAIL selftest: check_inv03_traceability did not flag a fixture missing all nine named rows", file=sys.stderr)
    complete_inv03_rows = [_valid_row(id=rid, requirement="INV-03") for rid in INV03_ROW_IDS]
    _, p = check_inv03_traceability(complete_inv03_rows)
    if p != 0:
        problems += 1
        print("FAIL selftest: check_inv03_traceability flagged a fixture declaring all nine named rows", file=sys.stderr)

    # --- model reasoning_toggle: missing or out-of-enum aborts load_models,
    #     rather than defaulting to a flat cell ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        bad_models_path = Path(td) / "models.yaml"
        bad_models_path.write_text(yaml.safe_dump({"models": [{"slug": "x", "vendor": "x", "wire_family": "openai_compat", "reasoning_toggle": "sometimes"}]}))
        try:
            load_models(bad_models_path)
            problems += 1
            print("FAIL selftest: load_models did not abort on an out-of-enum reasoning_toggle", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL selftest: load_models(bad reasoning_toggle) expected exit 2, got {e.code}", file=sys.stderr)

    # --- cell emission: always-on yields no thinking-off cell; none yields no
    #     thinking-on cell; default-on and opt-in yield both — each asserted
    #     against a synthetic two-model fixture ---
    cases += 1
    axis_row = _valid_row(axis="thinking")
    toggle_expectations = {
        "always-on": (["thinking-on"], [("thinking-off", "no-thinking-off-toggle")]),
        "none": (["thinking-off"], [("thinking-on", "no-thinking-capability")]),
        "default-on": (["thinking-off", "thinking-on"], []),
        "opt-in": (["thinking-off", "thinking-on"], []),
    }
    for toggle, (expected_emitted, expected_skipped) in toggle_expectations.items():
        emitted, skipped = modes_for_model(axis_row, {"reasoning_toggle": toggle})
        if emitted != expected_emitted or skipped != expected_skipped:
            problems += 1
            print(
                f"FAIL selftest: modes_for_model(reasoning_toggle={toggle!r}) "
                f"expected {(expected_emitted, expected_skipped)}, got {(emitted, skipped)}",
                file=sys.stderr,
            )

    # --- axis fragment availability: a vendor override with an explicit null
    #     on/off fragment is unavailable and reports its own declared reason,
    #     one case per new reason (T-10-06, plan 10-02 D-08) — never a crash,
    #     never an invented fragment ---
    cases += 1
    avail_inventory = {
        "axes": {
            "thinking": {
                "shapes": {
                    "openai_compat": {
                        "on": {"reasoning_effort": "low"},
                        "off": {"reasoning_effort": "none"},
                        "vendor_overrides": {
                            "dseek": {"on": None, "off": None, "reason": "toggle-not-a-request-parameter"},
                            "kimi": {"on": None, "off": None, "reason": "toggle-shape-unknown"},
                        },
                    },
                },
            },
        },
    }
    avail_row = _valid_row(axis="thinking")
    available, reason = axis_fragment_availability(avail_row, {"wire_family": "openai_compat", "vendor": "dseek"}, avail_inventory, "thinking-on")
    if available or reason != "toggle-not-a-request-parameter":
        problems += 1
        print(
            f"FAIL selftest: axis_fragment_availability(dseek) expected "
            f"(False, 'toggle-not-a-request-parameter'), got {(available, reason)}",
            file=sys.stderr,
        )

    cases += 1
    available, reason = axis_fragment_availability(avail_row, {"wire_family": "openai_compat", "vendor": "kimi"}, avail_inventory, "thinking-on")
    if available or reason != "toggle-shape-unknown":
        problems += 1
        print(
            f"FAIL selftest: axis_fragment_availability(kimi) expected "
            f"(False, 'toggle-shape-unknown'), got {(available, reason)}",
            file=sys.stderr,
        )

    # --- a vendor with no override still gets a real fragment (family default) ---
    cases += 1
    available, reason = axis_fragment_availability(avail_row, {"wire_family": "openai_compat", "vendor": "openai"}, avail_inventory, "thinking-on")
    if not available or reason is not None:
        problems += 1
        print(
            f"FAIL selftest: axis_fragment_availability(openai, no override) "
            f"expected (True, None), got {(available, reason)}",
            file=sys.stderr,
        )

    # --- a null fragment whose reason is outside the closed vocabulary aborts
    #     (exit 2) rather than silently accepting free text ---
    cases += 1
    bad_reason_inventory = {
        "axes": {"thinking": {"shapes": {"openai_compat": {
            "on": {"reasoning_effort": "low"}, "off": {"reasoning_effort": "none"},
            "vendor_overrides": {"dseek": {"on": None, "off": None, "reason": "made-up-reason"}},
        }}}},
    }
    try:
        axis_fragment_availability(avail_row, {"wire_family": "openai_compat", "vendor": "dseek"}, bad_reason_inventory, "thinking-on")
        problems += 1
        print("FAIL selftest: axis_fragment_availability did not abort on an out-of-vocabulary skip reason", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL selftest: axis_fragment_availability(bad reason) expected exit 2, got {e.code}", file=sys.stderr)

    # --- --check detects a hand-edited generated file: it re-renders in memory
    #     and compares against what is on disk, flagging any difference ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        drift_inventory = {
            "checked": "2026-09-01",
            "axes": {},
            "groups": [{"id": "structural", "title": "Structural", "order": 20, "blurb": "x"}],
            "defaults": {"prompt": "hi", "max_tokens": 16},
            "params": [_valid_row(id="drift-param", group="structural")],
        }
        drift_models = [{"slug": "m1", "vendor": "v1", "wire_family": "openai_compat", "reasoning_toggle": "none"}]
        td_path = Path(td)
        scalar, cb, skipped = expand_params(drift_inventory, drift_models)
        write_generated_files(drift_inventory, scalar, cb, skipped, generated_dir=td_path)
        _, p_clean = check_generated_drift(drift_inventory, drift_models, generated_dir=td_path)
        if p_clean != 0:
            problems += 1
            print("FAIL selftest: check_generated_drift flagged a freshly-written, unmodified generated set", file=sys.stderr)
        (td_path / "contract-sweep.yaml").write_text(
            (td_path / "contract-sweep.yaml").read_text() + "\n# hand-edited drift probe\n"
        )
        _, p_dirty = check_generated_drift(drift_inventory, drift_models, generated_dir=td_path)
        if p_dirty == 0:
            problems += 1
            print("FAIL selftest: check_generated_drift did not flag a hand-edited generated file", file=sys.stderr)

    # --- check_emitted_carries_param has teeth (CR-01, plan 10-04): a synthetic
    #     scalar entry list containing one cell whose extra_params omits its
    #     row's resolved name is flagged; the same fixture with the parameter
    #     key present is not. Hand-built directly against the shared
    #     _carries_param_problems() helper (not routed through expand_params(),
    #     which now refuses to produce a no-op cell) — a validator that only
    #     ever sees green output is not a validator. ---
    cases += 1
    teeth_row = _valid_row(id="teeth-param", names={"anthropic_messages": "x", "openai_compat": "x", "gemini": "x"})
    teeth_model = {"slug": "m-teeth", "vendor": "anthropic", "wire_family": "anthropic_messages", "reasoning_toggle": "none"}
    teeth_rows_by_id = {"teeth-param": teeth_row}
    teeth_models_by_slug = {"m-teeth": teeth_model}
    missing_entry = {"model": "m-teeth", "param": "teeth-param", "mode": "default", "extra_params": {}}
    _, p_missing = _carries_param_problems(teeth_rows_by_id, teeth_models_by_slug, [missing_entry])
    if p_missing != 1:
        problems += 1
        print(
            f"FAIL selftest: check_emitted_carries_param did not flag a "
            f"synthetic cell whose extra_params omits its resolved name "
            f"(expected 1 problem, got {p_missing})",
            file=sys.stderr,
        )
    present_entry = {"model": "m-teeth", "param": "teeth-param", "mode": "default", "extra_params": {"x": 1}}
    _, p_present = _carries_param_problems(teeth_rows_by_id, teeth_models_by_slug, [present_entry])
    if p_present != 0:
        problems += 1
        print(
            f"FAIL selftest: check_emitted_carries_param flagged a cell "
            f"whose extra_params DOES carry its resolved name "
            f"(expected 0 problems, got {p_present})",
            file=sys.stderr,
        )

    # --- emit-site fail-loud guard (CR-01, plan 10-04): calling
    #     build_extra_params() directly with a row whose name resolves to None
    #     for the given model raises SystemExit(2) — the branch expand_params()'s
    #     routing is meant to make unreachable stays loud if it is ever reached
    #     anyway, rather than silently regressing to the old `if param_name is
    #     not None:` omission. ---
    cases += 1
    null_name_row = _valid_row(
        id="null-name-param",
        names={"anthropic_messages": None, "openai_compat": "x", "gemini": "x"},
    )
    null_name_model = {"slug": "m-null", "vendor": "anthropic", "wire_family": "anthropic_messages", "reasoning_toggle": "none"}
    try:
        build_extra_params(null_name_row, null_name_model, {"axes": {}}, "default", 1)
        problems += 1
        print("FAIL selftest: build_extra_params did not abort on a None-resolving param_name", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL selftest: build_extra_params(None-resolving) expected exit 2, got {e.code}", file=sys.stderr)

    # --- bad invocation: --check and --selftest together, and an unrecognized
    #     flag, both exit 2 with a usage line on stderr — via subprocess so this
    #     never mutates this process's own sys.argv or state ---
    cases += 1
    for bad_args in (["--check", "--selftest"], ["--bogus-flag"]):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), *bad_args],
            capture_output=True, text=True,
        )
        if result.returncode != 2:
            problems += 1
            print(
                f"FAIL selftest: `inventory-to-sets.py {' '.join(bad_args)}` "
                f"expected exit 2, got {result.returncode}",
                file=sys.stderr,
            )
        if not result.stderr.strip():
            problems += 1
            print(f"FAIL selftest: `inventory-to-sets.py {' '.join(bad_args)}` printed nothing to stderr", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="inventory-to-sets.py",
        usage="inventory-to-sets.py [--check|--selftest]",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.check and args.selftest:
        print("usage: inventory-to-sets.py [--check|--selftest]", file=sys.stderr)
        return 2

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if args.check:
        inventory = load_inventory()
        models = load_models()
        checks, problems = run_registry_checks(inventory)
        d_checks, d_problems = check_generated_drift(inventory, models)
        checks += d_checks
        problems += d_problems
        c_checks, c_problems = check_emitted_carries_param(inventory, models)
        checks += c_checks
        problems += c_problems
        print(f"{problems} problem(s)")
        return 1 if problems else 0

    inventory = load_inventory()
    models = load_models()
    scalar_entries, content_block_entries, skipped_entries = expand_params(inventory, models)
    write_generated_files(inventory, scalar_entries, content_block_entries, skipped_entries)
    print_summary(inventory, scalar_entries, content_block_entries, skipped_entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
