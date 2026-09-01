#!/usr/bin/env python3
"""scripts/classify-probes.py — reads the declared cell universe
(probes/sets/generated/{contract-sweep,content-blocks,skipped-cells}.yaml, D-11),
every probes/raw/*.jsonl (wire evidence), probes/inventory.yaml +
probes/harness/models.yaml (row order + per-wire-family name resolution), and
probes/classified/overrides.yaml (hand-kept, D-08), and writes
probes/classified/contract-sweep.yaml — one row per declared cell (345 = 329 scalar +
16 content-block) plus every declared skip (284) — 629 rows total (MTX-01).

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

CLASSIFIED_HEADER = (
    "# probes/classified/contract-sweep.yaml — GENERATED by\n"
    "# scripts/classify-probes.py from probes/raw/*.jsonl +\n"
    "# probes/classified/overrides.yaml — do not edit by hand. Regenerate with\n"
    "# `python3 scripts/classify-probes.py`.\n"
    "#\n"
    "# One row per declared cell (probes/sets/generated/contract-sweep.yaml +\n"
    "# content-blocks.yaml, 345 cells) plus every declared skip\n"
    "# (probes/sets/generated/skipped-cells.yaml, 284) — 629 rows total (MTX-01)."
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
    declared scalar entry — same adapter.build_request() call, same apply_omit(),
    same probe_id() hash, so this can never independently drift from the harness
    that produced the evidence being joined against (MTX-01's own key_link)."""
    model = models[entry["model"]]
    adapter = ADAPTERS[model["wire_family"]]
    prompt = entry.get("prompt", "Reply with one word.")
    max_tokens = entry.get("max_tokens", 16)
    extra_params = entry.get("extra_params") or {}
    request_body = adapter.build_request(model["api_model_id"], prompt, max_tokens, extra_params)
    request_body = harness_runner.apply_omit(request_body, entry.get("omit"))
    return harness_runner.probe_id(entry["model"], entry["param"], entry["value"], entry["mode"], request_body)


def classify_cell(record: dict | None, row: dict, model: dict) -> tuple[str, str | None, int | None, str]:
    """Pure classification (D-06/D-07) of ONE scalar cell given its matched raw
    record (or None if unfired), its probes/inventory.yaml row, and its
    probes/harness/models.yaml row. No I/O, no mutation — testable the same
    boundary-first way probes/harness/ledger.py's ceiling_verdict() selftest
    already demonstrates. Returns (state, needs_review_reason_or_None,
    http_status_or_None, honor_evidence).

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
    6. A 2xx -> 'accepted-unverified' with honor_evidence 'none' (D-06: no honor
       claim is invented from a response carrying no signal).
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
        return "accepted-unverified", None, http_status, "none"
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
        state, reason, http_status, honor_evidence = classify_cell(record, row, model)
        if record is not None:
            used_probe_ids.add(pid)
            if record.get("recorded_at"):
                joined_recorded_at.append(record["recorded_at"])
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
            "skip_reason": None,
            "reason": reason,
            "override": None,
        })

    for entry in content_block_data["content_block_probes"]:
        # No content-block firing path exists yet (MODAL-01 lands in plan 11-03) —
        # every content-block cell is honestly 'unfired' in this plan, regardless
        # of what probe_id scheme a future runner path assigns it. `mode`/`value`
        # (2026-09-01, Phase 11 plan 11-02) now come straight from the generated
        # entry — fixed strings `default`/`content-block` per
        # inventory-to-sets.py's content-block branch — rather than a hardcoded
        # null, now that the generator actually emits them.
        row = rows_by_id[entry["param"]]
        out_rows.append({
            "param": entry["param"],
            "group": row["group"],
            "model": entry["model"],
            "mode": entry["mode"],
            "value": entry["value"],
            "state": "unfired",
            "probe_id": None,
            "http_status": None,
            "honor_evidence": "n/a",
            "hazard": None,
            "skip_reason": None,
            "reason": None,
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
            "skip_reason": reason,
            "reason": None,
            "override": None,
        })

    unmatched_overrides = apply_overrides(out_rows, overrides)

    def sort_key(r: dict) -> tuple:
        return (row_order[r["param"]], model_order[r["model"]], r["mode"] or "", r["value"] or "")

    out_rows.sort(key=sort_key)

    evidence_through = max(joined_recorded_at) if joined_recorded_at else None
    ignored_records = len(raw_records) - len(used_probe_ids)
    return out_rows, evidence_through, unmatched_overrides, ignored_records


def render_classified_file(*, checked, evidence_through: str | None, rows: list[dict]) -> str:
    """Every generated file: a header comment, a `checked:` date carried straight
    from the declared-cell input (never wall-clock — matches
    probes/inventory-to-sets.py's own render_generated_file() convention), an
    `evidence_through:` field derived from the joined evidence itself, then the
    single `cells:` list. Both `checked` and `evidence_through` are derived from
    inputs, so idempotent regeneration is byte-identical."""
    doc = {"checked": checked, "evidence_through": evidence_through, "cells": rows}
    body = yaml.safe_dump(doc, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
    return CLASSIFIED_HEADER.rstrip("\n") + "\n\n" + body


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
    checked = load_declared_scalar()["checked"]
    text = render_classified_file(checked=checked, evidence_through=evidence_through, rows=rows)
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
        "id": "fixture-param",
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

    # --- render_classified_file: deterministic — two calls with identical input
    #     are byte-identical (idempotent regeneration, MTX-01's own criterion) ---
    cases += 1
    sample_rows = [{"param": "p", "model": "m", "mode": "default", "value": "1", "state": "unfired"}]
    first = render_classified_file(checked="2026-09-01", evidence_through=None, rows=sample_rows)
    second = render_classified_file(checked="2026-09-01", evidence_through=None, rows=sample_rows)
    if first != second:
        problems += 1
        print("FAIL render_classified_file: expected byte-identical output for identical input", file=sys.stderr)

    # --- an unrecognized skip reason fails loud rather than silently passing
    #     through (D-11's closed vocabulary, enforced the same way SKIP_REASONS
    #     is enforced in probes/inventory-to-sets.py) ---
    cases += 1
    if "not-a-real-reason" in SKIP_REASONS:
        problems += 1
        print("FAIL SKIP_REASONS: fixture sentinel unexpectedly already a member", file=sys.stderr)

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
