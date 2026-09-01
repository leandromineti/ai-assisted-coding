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
import sys
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


def build_extra_params(row: dict, model: dict, inventory: dict, mode: str, value) -> dict:
    """extra_params = the row's per-family parameter name mapped to the probe
    value, merged with the axis fragment for that family (with the vendor
    override applied when one exists). For a thinking-on/thinking-off cell the
    axis fragment is always present; for 'default' it is absent (D-06)."""
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

    extra: dict = {}
    if param_name is not None:
        extra[param_name] = value
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
    `value: invalid-negative`) and for probe_id's canonical hash input."""
    if isinstance(value, bool):
        return "true" if value else "false"
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
            emitted_modes, skip_pairs = modes_for_model(row, model)
            for skip_mode, reason in skip_pairs:
                skipped_entries.append(_skip_record(row, model, skip_mode, reason))
            for mode in emitted_modes:
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
) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    checked = inventory["checked"]

    contract_header = (
        "# probes/sets/generated/contract-sweep.yaml — GENERATED by\n"
        "# probes/inventory-to-sets.py from probes/inventory.yaml — do not edit by\n"
        "# hand. Edit the registry, then re-run\n"
        "# `python3 probes/inventory-to-sets.py`.\n"
        "#\n"
        "# Scalar parameter probes only (kind: parameter, D-12) — runner.py's own\n"
        "# `probes:` grammar, consumed unchanged (load_probe_set)."
    )
    (GENERATED_DIR / "contract-sweep.yaml").write_text(
        render_generated_file(header=contract_header, checked=checked, top_key="probes", payload=scalar_entries)
    )

    content_blocks_header = (
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
    (GENERATED_DIR / "content-blocks.yaml").write_text(
        render_generated_file(
            header=content_blocks_header, checked=checked, top_key="content_block_probes", payload=content_block_entries
        )
    )

    skipped_header = (
        "# probes/sets/generated/skipped-cells.yaml — GENERATED by\n"
        "# probes/inventory-to-sets.py from probes/inventory.yaml — do not edit by\n"
        "# hand. Edit the registry, then re-run\n"
        "# `python3 probes/inventory-to-sets.py`.\n"
        "#\n"
        "# Every param x model cell NOT emitted, with its declared reason (D-11) —\n"
        "# a skipped cell is visible evidence, never a silent absence."
    )
    (GENERATED_DIR / "skipped-cells.yaml").write_text(
        render_generated_file(header=skipped_header, checked=checked, top_key="skipped", payload=skipped_entries)
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
        # Added by plan 10-01 Task 2 — not yet implemented.
        print("--selftest is not yet implemented (plan 10-01 Task 2)", file=sys.stderr)
        return 2

    if args.check:
        # Added by plan 10-01 Task 2 — not yet implemented.
        print("--check is not yet implemented (plan 10-01 Task 2)", file=sys.stderr)
        return 2

    inventory = load_inventory()
    models = load_models()
    scalar_entries, content_block_entries, skipped_entries = expand_params(inventory, models)
    write_generated_files(inventory, scalar_entries, content_block_entries, skipped_entries)
    print_summary(inventory, scalar_entries, content_block_entries, skipped_entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
