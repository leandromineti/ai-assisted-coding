#!/usr/bin/env python3
"""scripts/classify-behavioral.py — reads every declared behavioral set
(probes/sets/behavioral/*.yaml) and every probes/raw/*.jsonl record, recomputes
each declared repeat entry's exact probe_id via probes/harness/runner.py's own
probe_id()/apply_omit()/apply_max_tokens_field_override() (the same join-key
discipline scripts/classify-probes.py already established for the contract
sweep), groups repeat entries by (model, param, value, mode), and reduces each
group to a rate-with-count verdict against its declared expectation. Writes
probes/classified/behavioral.yaml.

    python3 scripts/classify-behavioral.py                 # regenerate + print a counted summary
    python3 scripts/classify-behavioral.py --check          # drift-check against disk
    python3 scripts/classify-behavioral.py --selftest       # run the embedded fixture battery
    python3 scripts/classify-behavioral.py --raw-dir <dir>  # override probes/raw (testing only)

Exit codes: 0 clean, 1 problems recorded (--check/--selftest only), 2 bad
invocation or malformed/missing input — including an unresolvable citation, a
declared cell with no matching expectation, an expectation matching no declared
cell, a `prereg:` citation on a non-control row, a requirement/design outside
its closed vocabulary, or no readable raw evidence at all. The fail-loud path
never writes an empty-but-valid classified file, and a behavioral row asserted
from memory (no resolvable citation) can never be generated at all — the
mechanical form of roadmap success criterion 6.

Joins each declared repeat entry to its evidence by recomputing the EXACT
probe_id runner.probe_id() would assign it, exactly as scripts/classify-probes.py
already does for scalar contract cells (imported here rather than reimplemented,
D-11 key_link) — the generator and the harness that produced the evidence can
never independently drift apart.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBES_DIR = REPO_ROOT / "probes"
HARNESS_DIR = PROBES_DIR / "harness"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# probes/harness/runner.py's own top-level `import client` / `import ledger` and
# adapters/__init__.py's `from . import ...` only resolve once HARNESS_DIR is on
# sys.path — mirrors scripts/classify-probes.py's own insert exactly.
sys.path.insert(0, str(HARNESS_DIR))
import runner as harness_runner  # noqa: E402  probe_id(), apply_omit(), apply_max_tokens_field_override()
from adapters import ADAPTERS  # noqa: E402  build_request() per wire family

# scripts/classify-probes.py's filename is not importable with a bare `import`
# statement (a hyphen is not a valid identifier character) — loaded here via
# importlib.util from an explicit file path instead of duplicating its
# _get_message_text()/_get_finish_reason() response-shape accessors (the plan's
# own read_first instruction: import them, don't copy them). Its module-level
# code (its own sys.path insert, `import runner`, `from adapters import
# ADAPTERS`) is idempotent with the inserts above and has no other side effects.
_classify_probes_spec = importlib.util.spec_from_file_location(
    "classify_probes", SCRIPTS_DIR / "classify-probes.py"
)
classify_probes = importlib.util.module_from_spec(_classify_probes_spec)
_classify_probes_spec.loader.exec_module(classify_probes)
_get_message_text = classify_probes._get_message_text
_get_finish_reason = classify_probes._get_finish_reason

BEHAVIORAL_SETS_DIR = PROBES_DIR / "sets" / "behavioral"
MODELS_PATH = HARNESS_DIR / "models.yaml"
DOCS_CLAIMS_PATH = PROBES_DIR / "docs-claims.yaml"
CONTRACT_SWEEP_PATH = PROBES_DIR / "classified" / "contract-sweep.yaml"
PREREGISTRATION_PATH = PROBES_DIR / "PREREGISTRATION.md"
CLASSIFIED_DIR = PROBES_DIR / "classified"
CLASSIFIED_PATH = CLASSIFIED_DIR / "behavioral.yaml"
DEFAULT_RAW_DIR = PROBES_DIR / "raw"

# Closed requirement vocabulary (12-02 PLAN.md's own must_haves truth). Every
# behavioral cell's `requirement` must be one of these six BHV rows or the
# calibration control-arm's own sentinel value.
REQUIREMENTS = frozenset({
    "BHV-01", "BHV-02", "BHV-03", "BHV-04", "BHV-05", "BHV-06", "calibration",
})

# Closed design vocabulary — `control` and `repeats` compare every repeat's
# visible text against repeat 1 (the SAME reduction, shared); `seed-pairs`
# (12-03, BHV-01) reduces ten same-seed repeats into FIVE DISJOINT PAIRS
# instead — (r1,r2) (r3,r4) (r5,r6) (r7,r8) (r9,r10) — plus a different-seed
# effect control compared against repeat 1 (D-01/D-06's own pair-plus-
# effect-control design, distinct from the baseline-vs-N reduction the other
# two designs share). Grows further in 12-04/12-05 as new cell shapes
# (single-observation BHV-03/04/05, presence-only BHV-06) are added.
DESIGNS = frozenset({"control", "repeats", "seed-pairs"})

# Closed verdict vocabulary, shared by every repeat-based design (control/
# repeats/seed-pairs) — never a bare boolean anywhere in the classified file
# (the plan's own must_haves truth). `no-signal` when any repeat is missing,
# non-200, or carries empty visible text — the denominator (`comparisons` for
# control/repeats, the 5-pair denominator for seed-pairs) never silently
# shrinks to match however many repeats actually joined.
VERDICTS = frozenset({"deterministic", "varies", "partial", "no-signal"})

# Closed skip-reason vocabulary (12-03): one entry per declared-skip family
# this plan's two probe sets carry. Grows as later plans declare skips
# (mirrors scripts/classify-probes.py's own SKIP_REASONS growth pattern,
# itself mirroring probes/inventory-to-sets.py's).
SKIP_REASONS: frozenset[str] = frozenset({
    "no-request-side-seed-field",
    "wire-rejects-temperature-default-mode",
    "deferred-thinking-mode-cross-product",
})


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path this
    module shares with probes/harness/runner.py and scripts/classify-probes.py."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _load_yaml(path: Path, required_key: str | None = None) -> dict:
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if required_key is not None and (not isinstance(data, dict) or required_key not in data):
        _fail(2, f"{path}: expected a top-level `{required_key}:` key")
    return data


def load_models(path: Path = MODELS_PATH) -> dict[str, dict]:
    """slug -> row, with `_order` recording models.yaml's own row index — the
    classified output's model-ordering sort key (mirrors
    scripts/classify-probes.py's own load_models() exactly)."""
    data = _load_yaml(path, "models")
    rows: dict[str, dict] = {}
    for i, row in enumerate(data["models"]):
        rows[row["slug"]] = {**row, "_order": i}
    return rows


def load_docs_claims_index(path: Path = DOCS_CLAIMS_PATH) -> set[tuple[str, str]]:
    """The set of every (param, vendor) pair probes/docs-claims.yaml carries a
    claim for — a `docs-claims:<param>/<vendor>` citation resolves iff its pair
    is a member. Fails loud on a malformed file (missing `claims:`)."""
    data = _load_yaml(path, "claims")
    if not isinstance(data["claims"], list):
        _fail(2, f"{path}: `claims:` must be a list")
    return {(c["param"], c["vendor"]) for c in data["claims"] if "param" in c and "vendor" in c}


def load_contract_probe_ids(path: Path = CONTRACT_SWEEP_PATH) -> set[str]:
    """The set of every non-null probe_id in probes/classified/contract-sweep.yaml
    — a `phase11:<probe_id>` citation resolves iff its probe_id is a member."""
    data = _load_yaml(path, "cells")
    return {c["probe_id"] for c in data["cells"] if c.get("probe_id")}


def load_prereg_text(path: Path = PREREGISTRATION_PATH) -> str:
    try:
        return Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")


def resolve_citation(
    citation: str,
    *,
    docs_claims_index: set[tuple[str, str]],
    contract_probe_ids: set[str],
    prereg_text: str,
    allow_prereg: bool,
) -> None:
    """Resolve one `expected_source`/`cited_source` citation against its named
    surface. Fails loud (exit 2) on any unresolvable form — a behavioral row
    asserted from memory can never be generated (roadmap criterion 6). The
    three accepted prefixes: `docs-claims:<param>/<vendor>`,
    `phase11:<probe_id>`, `prereg:<section anchor text>` — the third ONLY when
    `allow_prereg` is true (a `design: control` row's own `expected_source`, or
    a skip's `cited_source`, which carries no `design` field at all and is
    therefore never subject to the control-only restriction)."""
    if citation.startswith("docs-claims:"):
        rest = citation[len("docs-claims:"):]
        if "/" not in rest:
            _fail(2, f"malformed docs-claims citation (expected <param>/<vendor>): {citation!r}")
        param, vendor = rest.rsplit("/", 1)
        if (param, vendor) not in docs_claims_index:
            _fail(2, f"docs-claims citation does not resolve to a probes/docs-claims.yaml claim: {citation!r}")
        return
    if citation.startswith("phase11:"):
        pid = citation[len("phase11:"):]
        if pid not in contract_probe_ids:
            _fail(2, f"phase11 citation does not resolve to a probes/classified/contract-sweep.yaml row: {citation!r}")
        return
    if citation.startswith("prereg:"):
        if not allow_prereg:
            _fail(2, f"prereg: citation is only accepted on a design=control row: {citation!r}")
        anchor = citation[len("prereg:"):]
        if anchor not in prereg_text:
            _fail(2, f"prereg citation anchor not found in probes/PREREGISTRATION.md: {citation!r}")
        return
    _fail(2, f"expected_source/cited_source citation has an unrecognized prefix (expected docs-claims:/phase11:/prereg:): {citation!r}")


def load_behavioral_sets(sets_dir: Path = BEHAVIORAL_SETS_DIR) -> tuple[list[dict], list[dict], list[dict], list[str]]:
    """Load every probes/sets/behavioral/*.yaml file. Returns (all_probes,
    all_expectations, all_skips, checked_dates). Fails loud (exit 2) when a
    file is missing its required `probes:`/`expectations:`/`skips:` top-level
    keys, or when the directory has no *.yaml files at all."""
    files = sorted(Path(sets_dir).glob("*.yaml")) if Path(sets_dir).is_dir() else []
    if not files:
        _fail(2, f"no probes/sets/behavioral/*.yaml files found in {sets_dir}")
    all_probes: list[dict] = []
    all_expectations: list[dict] = []
    all_skips: list[dict] = []
    checked_dates: list[str] = []
    for f in files:
        try:
            text = f.read_text()
        except OSError as e:
            _fail(2, f"cannot read {f}: {e}")
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            _fail(2, f"{f} is not valid YAML: {e}")
        if not isinstance(data, dict) or "expectations" not in data:
            _fail(2, f"{f}: missing required `expectations:` key")
        if not isinstance(data.get("probes"), list):
            _fail(2, f"{f}: `probes:` must be a list")
        if not isinstance(data.get("skips"), list):
            _fail(2, f"{f}: `skips:` must be a list")
        if not isinstance(data.get("expectations"), list):
            _fail(2, f"{f}: `expectations:` must be a list")
        checked_dates.append(data.get("checked"))
        all_probes.extend(data["probes"])
        all_expectations.extend(data["expectations"])
        all_skips.extend(data["skips"])
    return all_probes, all_expectations, all_skips, checked_dates


def group_key(entry: dict) -> tuple:
    return (entry["model"], entry["param"], entry["value"], entry["mode"])


def compute_behavioral_probe_id(entry: dict, models: dict[str, dict]) -> str:
    """Recompute the EXACT probe_id runner.py's main() would have assigned this
    declared repeat entry — same adapter.build_request(), same
    apply_max_tokens_field_override(), same apply_omit(), same probe_id() hash
    threading `repeat` — mirroring scripts/classify-probes.py's own
    scalar_probe_id() step-for-step, so this can never independently drift from
    the harness that produced the evidence being joined against."""
    model = models[entry["model"]]
    adapter = ADAPTERS[model["wire_family"]]
    prompt = entry.get("prompt", "Reply with one word.")
    max_tokens = entry.get("max_tokens", 16)
    extra_params = entry.get("extra_params") or {}
    request_body = adapter.build_request(model["api_model_id"], prompt, max_tokens, extra_params)
    request_body = harness_runner.apply_max_tokens_field_override(request_body, model)
    request_body = harness_runner.apply_omit(request_body, entry.get("omit"))
    return harness_runner.probe_id(
        entry["model"], entry["param"], entry["value"], entry["mode"], request_body,
        repeat=entry.get("repeat"),
    )


def reduce_repeat_group(
    entries: list[dict], models: dict[str, dict], raw_records: dict[str, dict]
) -> dict:
    """Join a repeat-group's entries to their evidence and reduce to a
    rate-with-count verdict. Returns a dict of the fields build_behavioral_cell
    needs beyond the group's own declared identity: probe_ids (repeat order),
    matches, comparisons, distinct_outputs, verdict, ancillary, joined_at
    (list of recorded_at timestamps actually joined)."""
    model_slug = entries[0]["model"]
    wire_family = models[model_slug]["wire_family"]
    entries_sorted = sorted(entries, key=lambda e: e["repeat"])
    comparisons = len(entries_sorted) - 1

    probe_ids: list[str] = []
    texts: dict[int, str | None] = {}
    statuses: list[int | None] = []
    finish_reasons: list[str | None] = []
    output_tokens_list: list[int | None] = []
    system_fingerprints: list[str | None] = []
    joined_at: list[str] = []
    no_signal = False

    for e in entries_sorted:
        pid = compute_behavioral_probe_id(e, models)
        probe_ids.append(pid)
        record = raw_records.get(pid)
        if record is None:
            no_signal = True
            texts[e["repeat"]] = None
            statuses.append(None)
            finish_reasons.append(None)
            output_tokens_list.append(None)
            system_fingerprints.append(None)
            continue
        if record.get("recorded_at"):
            joined_at.append(record["recorded_at"])
        terminal = record.get("terminal")
        attempts = record.get("attempts") or []
        last = attempts[-1] if attempts else {}
        status = last.get("status")
        statuses.append(status)
        response_body = last.get("response_body_raw") or {}
        text = None
        finish_reason = None
        if terminal == "verdict":
            text = _get_message_text(response_body, wire_family)
            finish_reason = _get_finish_reason(response_body, wire_family)
        finish_reasons.append(finish_reason)
        usage = record.get("usage") or {}
        output_tokens_list.append(usage.get("output_tokens"))
        system_fingerprints.append(response_body.get("system_fingerprint") if isinstance(response_body, dict) else None)
        texts[e["repeat"]] = text
        if terminal != "verdict" or status != 200 or not text:
            no_signal = True

    repeat_order = sorted(texts)
    baseline_repeat = repeat_order[0] if repeat_order else None
    baseline_text = texts.get(baseline_repeat) if baseline_repeat is not None else None
    matches = 0
    for r in repeat_order[1:]:
        t = texts.get(r)
        if t is not None and baseline_text is not None and t == baseline_text:
            matches += 1
    distinct_outputs = len({t for t in texts.values() if t is not None})

    if no_signal:
        verdict = "no-signal"
    elif matches == comparisons:
        verdict = "deterministic"
    elif matches == 0:
        verdict = "varies"
    else:
        verdict = "partial"

    rate_pct = round(100 * matches / comparisons, 1) if comparisons > 0 else None

    return {
        "probe_ids": probe_ids,
        "matches": matches,
        "comparisons": comparisons,
        "rate": f"{matches}/{comparisons}",
        "rate_pct": rate_pct,
        "distinct_outputs": distinct_outputs,
        "verdict": verdict,
        "ancillary": {
            "statuses": statuses,
            "finish_reasons": finish_reasons,
            "output_tokens": output_tokens_list,
            "system_fingerprints": system_fingerprints,
        },
        "joined_at": joined_at,
    }


def _join_seed_entry(
    entry: dict, models: dict[str, dict], raw_records: dict[str, dict], wire_family: str,
    *, joined_at: list[str],
) -> tuple[str, str | None, int | None, str | None, int | None, str | None]:
    """Join one declared repeat/effect-control entry to its raw evidence.
    Returns (probe_id, text, status, finish_reason, output_tokens,
    system_fingerprint). `text`/`status` are None when the probe never joined
    (missing, non-200, or empty visible text) — the caller decides what that
    means for its own no-signal flag; this helper never sets one itself,
    since a missing EFFECT-CONTROL record does not by itself invalidate the
    main same-seed rate (it only makes seed_effect_control itself
    unreadable — reduce_seed_pair_group handles that distinction)."""
    pid = compute_behavioral_probe_id(entry, models)
    record = raw_records.get(pid)
    if record is None:
        return pid, None, None, None, None, None
    if record.get("recorded_at"):
        joined_at.append(record["recorded_at"])
    terminal = record.get("terminal")
    attempts = record.get("attempts") or []
    last = attempts[-1] if attempts else {}
    status = last.get("status")
    response_body = last.get("response_body_raw") or {}
    text = None
    finish_reason = None
    if terminal == "verdict":
        text = _get_message_text(response_body, wire_family)
        finish_reason = _get_finish_reason(response_body, wire_family)
    usage = record.get("usage") or {}
    system_fingerprint = response_body.get("system_fingerprint") if isinstance(response_body, dict) else None
    if terminal != "verdict" or status != 200 or not text:
        text = None
    return pid, text, status, finish_reason, usage.get("output_tokens"), system_fingerprint


def reduce_seed_pair_group(
    entries: list[dict], effect_control_entry: dict, models: dict[str, dict], raw_records: dict[str, dict],
) -> dict:
    """D-01/D-06's seed-pairs reduction: the ten same-seed `entries` (repeat
    1..10) are compared as FIVE DISJOINT PAIRS — (r1,r2) (r3,r4) (r5,r6)
    (r7,r8) (r9,r10) — never a flat ten-way comparison against repeat 1 (that
    is the `repeats` design's own baseline-vs-N reduction, used by BHV-02/D-03
    instead, in `reduce_repeat_group` above). `effect_control_entry` is the
    single different-seed probe (no `repeat` key) joined separately and
    compared against repeat 1's own text: if a DIFFERENT seed still
    reproduces repeat 1's exact text, the observed same-seed stability is not
    seed-driven (D-06) — surfaced via `seed_effect_control` plus a `note` on
    the misleading case (a full 5/5 pair-match rate whose effect control ALSO
    matched). The 5-pair denominator NEVER shrinks on a missing repeat (same
    denominator-preservation discipline as `reduce_repeat_group`'s own
    `no-signal` path) — a missing repeat marks the WHOLE group `no-signal`,
    it does not silently drop that repeat's pair from the count."""
    model_slug = entries[0]["model"]
    wire_family = models[model_slug]["wire_family"]
    entries_sorted = sorted(entries, key=lambda e: e["repeat"])

    probe_ids: list[str] = []
    texts: dict[int, str | None] = {}
    statuses: list[int | None] = []
    finish_reasons: list[str | None] = []
    output_tokens_list: list[int | None] = []
    system_fingerprints: list[str | None] = []
    joined_at: list[str] = []
    no_signal = False

    for e in entries_sorted:
        pid, text, status, finish_reason, out_tokens, sysfp = _join_seed_entry(
            e, models, raw_records, wire_family, joined_at=joined_at
        )
        probe_ids.append(pid)
        texts[e["repeat"]] = text
        statuses.append(status)
        finish_reasons.append(finish_reason)
        output_tokens_list.append(out_tokens)
        system_fingerprints.append(sysfp)
        if text is None:
            no_signal = True

    repeat_order = sorted(texts)
    pairs = list(zip(repeat_order[0::2], repeat_order[1::2]))
    matching_pairs = 0
    for a, b in pairs:
        ta, tb = texts.get(a), texts.get(b)
        if ta is not None and tb is not None and ta == tb:
            matching_pairs += 1

    ec_pid, ec_text, ec_status, ec_finish, ec_out_tokens, ec_sysfp = _join_seed_entry(
        effect_control_entry, models, raw_records, wire_family, joined_at=joined_at
    )
    baseline_repeat = repeat_order[0] if repeat_order else None
    baseline_text = texts.get(baseline_repeat) if baseline_repeat is not None else None
    if ec_text is None or baseline_text is None:
        ec_result = "no-signal"
    elif ec_text == baseline_text:
        ec_result = "matched"
    else:
        ec_result = "differed"

    if no_signal:
        verdict = "no-signal"
    elif matching_pairs == len(pairs):
        verdict = "deterministic"
    elif matching_pairs == 0:
        verdict = "varies"
    else:
        verdict = "partial"

    rate_pct = round(100 * matching_pairs / len(pairs), 1) if pairs else None

    note = None
    if verdict == "deterministic" and ec_result == "matched":
        note = (
            "Effect control matched repeat 1 despite firing with a different "
            "seed value — a full same-seed pair-match rate here is NOT "
            "demonstrated as seed-driven (the model reproduced repeat 1's "
            "exact text under a different seed too, D-06)."
        )

    return {
        "probe_ids": probe_ids,
        "matching_pairs": matching_pairs,
        "rate": f"{matching_pairs}/{len(pairs)}",
        "rate_pct": rate_pct,
        "verdict": verdict,
        "seed_effect_control": {"result": ec_result, "probe_id": ec_pid},
        "note": note,
        "ancillary": {
            "statuses": statuses,
            "finish_reasons": finish_reasons,
            "output_tokens": output_tokens_list,
            "system_fingerprints": system_fingerprints,
            "effect_control_status": ec_status,
            "effect_control_finish_reason": ec_finish,
            "effect_control_output_tokens": ec_out_tokens,
            "effect_control_system_fingerprint": ec_sysfp,
        },
        "joined_at": joined_at,
    }


def build_rows(
    probes: list[dict],
    expectations: list[dict],
    skips: list[dict],
    models: dict[str, dict],
    raw_records: dict[str, dict],
    *,
    docs_claims_index: set[tuple[str, str]],
    contract_probe_ids: set[str],
    prereg_text: str,
) -> tuple[list[dict], list[dict], str | None]:
    """The full group + match-to-expectation + citation-resolve + reduce
    pipeline. Returns (cells, skip_rows, evidence_through)."""
    groups: dict[tuple, list[dict]] = {}
    for entry in probes:
        groups.setdefault(group_key(entry), []).append(entry)

    expectations_by_key: dict[tuple, dict] = {}
    for exp in expectations:
        key = group_key(exp)
        if key in expectations_by_key:
            _fail(2, f"duplicate expectation declared for group {key!r}")
        expectations_by_key[key] = exp

    # A `design: seed-pairs` expectation's `effect_control_value` names a
    # SECOND declared probe group (same model/param/mode, a genuinely
    # different `value`) that is the different-seed effect control for THIS
    # expectation's own same-seed group — joined here via that field, never
    # via a second `expectations:` entry (Task 1's own "one expectations:
    # entry per model's same-seed group" design). Popped out of `groups`
    # BEFORE the generic "every declared group needs a matching expectation"
    # check below, so the effect-control group is never mistaken for an
    # orphan.
    effect_control_groups: dict[tuple, dict] = {}
    for key, exp in expectations_by_key.items():
        if exp.get("design") != "seed-pairs":
            continue
        ecv = exp.get("effect_control_value")
        if ecv is None:
            _fail(2, f"group {key!r}: a seed-pairs expectation requires `effect_control_value`")
        model, param, _value, mode = key
        ec_key = (model, param, ecv, mode)
        if ec_key not in groups:
            _fail(
                2,
                f"group {key!r}: no declared probe group for its effect_control_value "
                f"{ecv!r} (expected group_key {ec_key!r})",
            )
        ec_entries = groups.pop(ec_key)
        if len(ec_entries) != 1:
            _fail(2, f"group {ec_key!r}: effect-control group must have exactly 1 entry, got {len(ec_entries)}")
        effect_control_groups[key] = ec_entries[0]

    for key in groups:
        if key not in expectations_by_key:
            _fail(2, f"declared probe group {key!r} has no matching `expectations:` entry")
    for key in expectations_by_key:
        if key not in groups:
            _fail(2, f"expectation for group {key!r} matches no declared probe group")

    cells: list[dict] = []
    all_joined_at: list[str] = []

    for key, entries in groups.items():
        model, param, value, mode = key
        expectation = expectations_by_key[key]
        requirement = expectation.get("requirement")
        design = expectation.get("design")
        if requirement not in REQUIREMENTS:
            _fail(2, f"group {key!r}: requirement {requirement!r} is outside the closed vocabulary {sorted(REQUIREMENTS)}")
        if design not in DESIGNS:
            _fail(2, f"group {key!r}: design {design!r} is outside the closed vocabulary {sorted(DESIGNS)}")
        expected_source = expectation.get("expected_source")
        if not expected_source:
            _fail(2, f"group {key!r}: expectation missing required `expected_source`")
        resolve_citation(
            expected_source,
            docs_claims_index=docs_claims_index,
            contract_probe_ids=contract_probe_ids,
            prereg_text=prereg_text,
            allow_prereg=(design == "control"),
        )
        expected = expectation.get("expected")
        if not expected:
            _fail(2, f"group {key!r}: expectation missing required `expected`")

        if design == "seed-pairs":
            declared_calls = expectation.get("calls")
            declared_pairs = expectation.get("pairs")
            if not isinstance(declared_calls, int) or declared_calls < 2 or declared_calls % 2 != 0:
                _fail(2, f"group {key!r}: seed-pairs expectation `calls` must be an even int >= 2, got {declared_calls!r}")
            if declared_pairs != declared_calls // 2:
                _fail(
                    2,
                    f"group {key!r}: seed-pairs expectation `pairs` must equal calls/2 "
                    f"(calls={declared_calls!r}), got pairs={declared_pairs!r}",
                )
            if len(entries) != declared_calls:
                _fail(
                    2,
                    f"group {key!r}: expectation declares calls={declared_calls} but "
                    f"{len(entries)} probe entr{'y' if len(entries) == 1 else 'ies'} were found",
                )
            reduced = reduce_seed_pair_group(entries, effect_control_groups[key], models, raw_records)
            all_joined_at.extend(reduced.pop("joined_at"))
            cells.append({
                "cell_id": f"{model}--{param}--{value}--{mode}",
                "requirement": requirement,
                "design": design,
                "model": model,
                "vendor": models[model]["vendor"],
                "mode": mode,
                "param": param,
                "value": value,
                "pairs": declared_pairs,
                "calls": declared_calls,
                "matching_pairs": reduced["matching_pairs"],
                "rate": reduced["rate"],
                "rate_pct": reduced["rate_pct"],
                "verdict": reduced["verdict"],
                "seed_effect_control": reduced["seed_effect_control"],
                "expected": expected,
                "expected_source": expected_source,
                "probe_ids": reduced["probe_ids"],
                "ancillary": reduced["ancillary"],
                "note": reduced["note"],
            })
            continue

        declared_repeats = expectation.get("repeats")
        if not isinstance(declared_repeats, int) or declared_repeats < 2:
            _fail(2, f"group {key!r}: expectation `repeats` must be an int >= 2, got {declared_repeats!r}")
        if len(entries) != declared_repeats:
            _fail(
                2,
                f"group {key!r}: expectation declares repeats={declared_repeats} but "
                f"{len(entries)} probe entr{'y' if len(entries) == 1 else 'ies'} were found",
            )

        reduced = reduce_repeat_group(entries, models, raw_records)
        all_joined_at.extend(reduced.pop("joined_at"))

        cells.append({
            "cell_id": f"{model}--{param}--{value}--{mode}",
            "requirement": requirement,
            "design": design,
            "model": model,
            "vendor": models[model]["vendor"],
            "mode": mode,
            "param": param,
            "value": value,
            "repeats": declared_repeats,
            "comparisons": reduced["comparisons"],
            "matches": reduced["matches"],
            "rate": reduced["rate"],
            "rate_pct": reduced["rate_pct"],
            "distinct_outputs": reduced["distinct_outputs"],
            "verdict": reduced["verdict"],
            "expected": expected,
            "expected_source": expected_source,
            "probe_ids": reduced["probe_ids"],
            "ancillary": reduced["ancillary"],
            "note": None,
        })

    def sort_key(c: dict) -> tuple:
        return (c["requirement"], models[c["model"]]["_order"], c["cell_id"])

    cells.sort(key=sort_key)

    skip_rows: list[dict] = []
    for s in skips:
        has_pid = "cited_probe_id" in s and s["cited_probe_id"]
        has_src = "cited_source" in s and s["cited_source"]
        if has_pid == has_src:
            _fail(2, f"skip entry carries neither or both citations (exactly one required): {s}")
        requirement = s.get("requirement")
        if requirement not in REQUIREMENTS:
            _fail(2, f"skip entry: requirement {requirement!r} is outside the closed vocabulary {sorted(REQUIREMENTS)}")
        reason = s.get("reason")
        if reason not in SKIP_REASONS:
            _fail(2, f"skip entry: reason {reason!r} is outside the closed skip-reason vocabulary {sorted(SKIP_REASONS)}")
        if has_pid and s["cited_probe_id"] not in contract_probe_ids:
            _fail(2, f"skip entry: cited_probe_id does not resolve to a probes/classified/contract-sweep.yaml row: {s['cited_probe_id']!r}")
        if has_src:
            resolve_citation(
                s["cited_source"],
                docs_claims_index=docs_claims_index,
                contract_probe_ids=contract_probe_ids,
                prereg_text=prereg_text,
                allow_prereg=True,
            )
        skip_rows.append({
            "model": s.get("model"),
            "param": s.get("param"),
            "mode": s.get("mode"),
            "requirement": requirement,
            "reason": reason,
            "cited_probe_id": s.get("cited_probe_id"),
            "cited_source": s.get("cited_source"),
        })

    evidence_through = max(all_joined_at) if all_joined_at else None
    return cells, skip_rows, evidence_through


def behavioral_header(*, cell_count: int, skip_count: int) -> str:
    """The generated-file header — cell/skip counts derived at RENDER TIME from
    the loaded declared-cell YAMLs (matches scripts/classify-probes.py's own
    classified_header() discipline), never hand-pasted."""
    return (
        "# probes/classified/behavioral.yaml — GENERATED by\n"
        "# scripts/classify-behavioral.py from probes/sets/behavioral/*.yaml +\n"
        "# probes/raw/*.jsonl — do not edit by hand. Regenerate with\n"
        "# `python3 scripts/classify-behavioral.py`.\n"
        "#\n"
        f"# {cell_count} behavioral cell(s), {skip_count} declared skip(s) "
        f"({cell_count + skip_count} rows total)."
    )


def render_classified_file(
    *, checked: str | None, evidence_through: str | None, cells: list[dict], skips: list[dict],
) -> str:
    """Every generated field derived from an input, never wall-clock — matches
    scripts/classify-probes.py's own render_classified_file() idempotency
    contract exactly."""
    doc = {"checked": checked, "evidence_through": evidence_through, "cells": cells, "skips": skips}
    body = yaml.safe_dump(doc, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
    header = behavioral_header(cell_count=len(cells), skip_count=len(skips))
    return header.rstrip("\n") + "\n\n" + body


def regenerate(raw_dir: Path = DEFAULT_RAW_DIR, sets_dir: Path = BEHAVIORAL_SETS_DIR) -> tuple[str, list[dict], list[dict]]:
    """Load every input, group, match-to-expectation, resolve citations, reduce,
    and render — the single pipeline both the writer and `--check`'s drift
    comparator call, so the two can never independently drift apart."""
    models = load_models()
    raw_records = classify_probes.load_raw_records(raw_dir)
    probes, expectations, skips, checked_dates = load_behavioral_sets(sets_dir)
    docs_claims_index = load_docs_claims_index()
    contract_probe_ids = load_contract_probe_ids()
    prereg_text = load_prereg_text()

    cells, skip_rows, evidence_through = build_rows(
        probes, expectations, skips, models, raw_records,
        docs_claims_index=docs_claims_index,
        contract_probe_ids=contract_probe_ids,
        prereg_text=prereg_text,
    )
    checked = max(d for d in checked_dates if d) if any(checked_dates) else None
    text = render_classified_file(checked=checked, evidence_through=evidence_through, cells=cells, skips=skip_rows)
    return text, cells, skip_rows


def print_summary(cells: list[dict], skips: list[dict]) -> None:
    tally: dict[str, int] = {}
    for c in cells:
        tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1
    print(f"behavioral cells: {len(cells)}")
    print(f"declared skips: {len(skips)}")
    for verdict in sorted(tally):
        print(f"  {verdict}: {tally[verdict]}")


def check_generated_drift(raw_dir: Path = DEFAULT_RAW_DIR) -> tuple[int, int]:
    """(rule 3 drift gate) Re-render in memory from the real inputs and compare
    byte-for-byte with what is on disk."""
    checks = 0
    problems = 0
    checks += 1
    expected_text, _cells, _skips = regenerate(raw_dir)
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
    return checks, problems


# -----------------------------------------------------------------------------------
# --selftest — embedded fixtures, no external test framework, house style matching
# scripts/classify-probes.py / probes/harness/runner.py.
# -----------------------------------------------------------------------------------


def selftest() -> tuple[int, int]:
    problems = 0
    cases = 0

    fixture_models = {
        "m1": {"wire_family": "anthropic_messages", "vendor": "anthropic", "api_model_id": "m1-api", "_order": 0},
    }

    def make_group(n: int, texts: list[str | None], statuses: list[int | None] | None = None) -> tuple[list[dict], dict[str, dict]]:
        entries = [
            {"model": "m1", "param": "p", "value": "v", "mode": "default", "prompt": "x", "max_tokens": 16, "repeat": r}
            for r in range(1, n + 1)
        ]
        raw: dict[str, dict] = {}
        for i, e in enumerate(entries):
            pid = compute_behavioral_probe_id(e, fixture_models)
            text = texts[i]
            status = (statuses[i] if statuses else 200) if text is not None else (statuses[i] if statuses else None)
            if text is None and status is None:
                continue  # simulate a genuinely missing (unfired) repeat
            raw[pid] = {
                "terminal": "verdict" if status == 200 else "retry_exhausted",
                "recorded_at": "2026-09-03T00:00:00Z",
                "attempts": [{"status": status, "response_body_raw": {"content": [{"type": "text", "text": text}]} if text is not None else {}}],
                "usage": {"output_tokens": 10},
            }
        return entries, raw

    def make_seed_group(
        texts_10: list[str | None], ec_text: str | None,
        statuses_10: list[int | None] | None = None, ec_status: int | None = None,
    ) -> tuple[list[dict], dict, dict[str, dict]]:
        """Ten same-seed (value=42) repeat entries plus one different-seed
        (value=99) effect-control entry, mirroring make_group's shape for the
        seed-pairs design. `texts_10`/`statuses_10` follow make_group's own
        None-means-genuinely-missing convention; `ec_status` defaults to 200
        when `ec_text` is given."""
        entries = [
            {
                "model": "m1", "param": "seed", "value": 42, "mode": "default",
                "prompt": "x", "max_tokens": 16, "extra_params": {"seed": 42}, "repeat": r,
            }
            for r in range(1, 11)
        ]
        ec_entry = {
            "model": "m1", "param": "seed", "value": 99, "mode": "default",
            "prompt": "x", "max_tokens": 16, "extra_params": {"seed": 99},
        }
        raw: dict[str, dict] = {}
        for i, e in enumerate(entries):
            pid = compute_behavioral_probe_id(e, fixture_models)
            text = texts_10[i]
            status = (statuses_10[i] if statuses_10 else 200) if text is not None else (statuses_10[i] if statuses_10 else None)
            if text is None and status is None:
                continue
            raw[pid] = {
                "terminal": "verdict" if status == 200 else "retry_exhausted",
                "recorded_at": "2026-09-03T00:00:00Z",
                "attempts": [{"status": status, "response_body_raw": {"content": [{"type": "text", "text": text}]} if text is not None else {}}],
                "usage": {"output_tokens": 10},
            }
        ec_pid = compute_behavioral_probe_id(ec_entry, fixture_models)
        if ec_text is not None or ec_status is not None:
            st = ec_status if ec_status is not None else 200
            raw[ec_pid] = {
                "terminal": "verdict" if st == 200 else "retry_exhausted",
                "recorded_at": "2026-09-03T00:00:00Z",
                "attempts": [{"status": st, "response_body_raw": {"content": [{"type": "text", "text": ec_text}]} if ec_text is not None else {}}],
                "usage": {"output_tokens": 10},
            }
        return entries, ec_entry, raw

    # --- reduce_seed_pair_group: full match (5/5 deterministic), effect
    #     control DIFFERS — no misleading note ---
    cases += 1
    entries, ec_entry, raw = make_seed_group(["a", "a", "b", "b", "c", "c", "d", "d", "e", "e"], "different-text")
    reduced = reduce_seed_pair_group(entries, ec_entry, fixture_models, raw)
    if reduced["rate"] != "5/5" or reduced["verdict"] != "deterministic":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(full match): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)
    if reduced["seed_effect_control"]["result"] != "differed":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(effect control differ): got {reduced['seed_effect_control']!r}", file=sys.stderr)
    if reduced["note"] is not None:
        problems += 1
        print("FAIL reduce_seed_pair_group: note must be None when the effect control differs", file=sys.stderr)

    # --- reduce_seed_pair_group: full match (5/5), effect control MATCHES —
    #     the misleading case (D-06) sets a note ---
    cases += 1
    entries, ec_entry, raw = make_seed_group(["a", "a", "b", "b", "c", "c", "d", "d", "e", "e"], "a")
    reduced = reduce_seed_pair_group(entries, ec_entry, fixture_models, raw)
    if reduced["seed_effect_control"]["result"] != "matched":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(effect control match): got {reduced['seed_effect_control']!r}", file=sys.stderr)
    if reduced["note"] is None:
        problems += 1
        print("FAIL reduce_seed_pair_group: a full-rate group whose effect control also matched must carry a note (D-06)", file=sys.stderr)

    # --- reduce_seed_pair_group: zero match (0/5 varies) ---
    cases += 1
    entries, ec_entry, raw = make_seed_group(
        ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"], "k"
    )
    reduced = reduce_seed_pair_group(entries, ec_entry, fixture_models, raw)
    if reduced["rate"] != "0/5" or reduced["verdict"] != "varies":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(zero match): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)

    # --- reduce_seed_pair_group: middle value (2/5 partial) ---
    cases += 1
    entries, ec_entry, raw = make_seed_group(
        ["a", "a", "b", "b", "c", "d", "e", "f", "g", "h"], "z"
    )
    reduced = reduce_seed_pair_group(entries, ec_entry, fixture_models, raw)
    if reduced["rate"] != "2/5" or reduced["verdict"] != "partial":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(middle value): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)

    # --- reduce_seed_pair_group: a missing repeat -> no-signal, the 5-pair
    #     denominator is NEVER silently shrunk ---
    cases += 1
    entries, ec_entry, raw = make_seed_group(
        ["a", "a", "b", "b", "c", "c", "d", "d", "e", None],
        "a",
        statuses_10=[200] * 9 + [None],
    )
    reduced = reduce_seed_pair_group(entries, ec_entry, fixture_models, raw)
    if reduced["verdict"] != "no-signal":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(missing repeat): expected no-signal, got {reduced['verdict']!r}", file=sys.stderr)
    if reduced["rate"].split("/")[1] != "5":
        problems += 1
        print(f"FAIL reduce_seed_pair_group(missing repeat): denominator must stay 5, got {reduced['rate']!r}", file=sys.stderr)

    # --- reduce_repeat_group: full match (4/4 deterministic) ---
    cases += 1
    entries, raw = make_group(5, ["same"] * 5)
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["rate"] != "4/4" or reduced["verdict"] != "deterministic":
        problems += 1
        print(f"FAIL reduce_repeat_group(full match): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)

    # --- reduce_repeat_group: zero match (0/4 varies) ---
    cases += 1
    entries, raw = make_group(5, ["a", "b", "c", "d", "e"])
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["rate"] != "0/4" or reduced["verdict"] != "varies":
        problems += 1
        print(f"FAIL reduce_repeat_group(zero match): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)

    # --- reduce_repeat_group: middle value (partial) ---
    cases += 1
    entries, raw = make_group(5, ["a", "a", "b", "a", "c"])
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["rate"] != "2/4" or reduced["verdict"] != "partial":
        problems += 1
        print(f"FAIL reduce_repeat_group(partial): got {reduced['rate']!r}/{reduced['verdict']!r}", file=sys.stderr)

    # --- reduce_repeat_group: no-signal on an empty visible text (200 but blank) ---
    cases += 1
    entries, raw = make_group(5, ["a", "", "a", "a", "a"])
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["verdict"] != "no-signal" or reduced["comparisons"] != 4:
        problems += 1
        print(f"FAIL reduce_repeat_group(empty text): got verdict={reduced['verdict']!r} comparisons={reduced['comparisons']}", file=sys.stderr)

    # --- reduce_repeat_group: no-signal on a genuinely missing repeat — the
    #     denominator (comparisons) must NOT silently shrink to match however
    #     many repeats actually joined (the plan's own must_haves truth) ---
    cases += 1
    entries, raw = make_group(5, ["a", "a", "a", "a", None], statuses=[200, 200, 200, 200, None])
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["verdict"] != "no-signal" or reduced["comparisons"] != 4:
        problems += 1
        print(f"FAIL reduce_repeat_group(missing repeat): got verdict={reduced['verdict']!r} comparisons={reduced['comparisons']}", file=sys.stderr)

    # --- reduce_repeat_group: no-signal on a non-200 status ---
    cases += 1
    entries, raw = make_group(5, ["a", "a", "a", "a", "a"], statuses=[200, 200, 200, 200, 429])
    reduced = reduce_repeat_group(entries, fixture_models, raw)
    if reduced["verdict"] != "no-signal":
        problems += 1
        print(f"FAIL reduce_repeat_group(non-200): got verdict={reduced['verdict']!r}", file=sys.stderr)

    # --- resolve_citation: docs-claims:/phase11:/prereg: all resolve when present ---
    cases += 1
    docs_idx = {("temperature", "anthropic")}
    contract_ids = {"m--p--v--default--deadbeef"}
    prereg_text = "## Calibration design (rule 5d)\nsome text"
    try:
        resolve_citation("docs-claims:temperature/anthropic", docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text, allow_prereg=True)
        resolve_citation("phase11:m--p--v--default--deadbeef", docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text, allow_prereg=True)
        resolve_citation("prereg:Calibration design (rule 5d)", docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text, allow_prereg=True)
    except SystemExit:
        problems += 1
        print("FAIL resolve_citation: a resolvable citation of each form unexpectedly failed", file=sys.stderr)

    # --- resolve_citation: an unresolvable citation of each form fails loud (exit 2) ---
    for bad_citation in (
        "docs-claims:not-a-real-param/not-a-real-vendor",
        "phase11:not-a-real-probe-id",
        "prereg:not a real anchor at all",
        "unknown-prefix:something",
    ):
        cases += 1
        try:
            resolve_citation(bad_citation, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text, allow_prereg=True)
            problems += 1
            print(f"FAIL resolve_citation({bad_citation!r}): expected SystemExit(2), got a return", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL resolve_citation({bad_citation!r}): expected exit 2, got {e.code}", file=sys.stderr)

    # --- resolve_citation: a prereg: citation on a non-control row (allow_prereg=False) fails loud ---
    cases += 1
    try:
        resolve_citation("prereg:Calibration design (rule 5d)", docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text, allow_prereg=False)
        problems += 1
        print("FAIL resolve_citation: a prereg: citation on a non-control row was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL resolve_citation(prereg on non-control): expected exit 2, got {e.code}", file=sys.stderr)

    # --- build_rows: fail-loud paths — a declared group with no matching
    #     expectation, and an expectation matching no declared group ---
    cases += 1
    orphan_probes = [
        {"model": "m1", "param": "p", "value": "v", "mode": "default", "prompt": "x", "max_tokens": 16, "repeat": 1},
        {"model": "m1", "param": "p", "value": "v", "mode": "default", "prompt": "x", "max_tokens": 16, "repeat": 2},
    ]
    try:
        build_rows(orphan_probes, [], [], fixture_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
        problems += 1
        print("FAIL build_rows: a declared group with no expectation was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(no expectation): expected exit 2, got {e.code}", file=sys.stderr)

    cases += 1
    orphan_expectation = [{
        "model": "m1", "param": "no-such-group", "value": "v", "mode": "default",
        "requirement": "calibration", "design": "control", "repeats": 5,
        "expected": "x", "expected_source": "prereg:Calibration design (rule 5d)",
    }]
    try:
        build_rows([], orphan_expectation, [], fixture_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
        problems += 1
        print("FAIL build_rows: an expectation matching no declared group was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(orphan expectation): expected exit 2, got {e.code}", file=sys.stderr)

    # --- build_rows: requirement/design outside the closed vocabulary fails loud ---
    for bad_field, bad_value in (("requirement", "NOT-A-REAL-REQ"), ("design", "not-a-real-design")):
        cases += 1
        exp = {
            "model": "m1", "param": "p", "value": "v", "mode": "default",
            "requirement": "calibration", "design": "control", "repeats": 5,
            "expected": "x", "expected_source": "prereg:Calibration design (rule 5d)",
        }
        exp[bad_field] = bad_value
        try:
            build_rows(orphan_probes, [exp], [], fixture_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
            problems += 1
            print(f"FAIL build_rows(bad {bad_field}): expected SystemExit(2), got a return", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL build_rows(bad {bad_field}): expected exit 2, got {e.code}", file=sys.stderr)

    # --- build_rows: a repeats count mismatch (declared 5, only 2 entries) fails loud ---
    cases += 1
    exp_mismatch = [{
        "model": "m1", "param": "p", "value": "v", "mode": "default",
        "requirement": "calibration", "design": "control", "repeats": 5,
        "expected": "x", "expected_source": "prereg:Calibration design (rule 5d)",
    }]
    try:
        build_rows(orphan_probes, exp_mismatch, [], fixture_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
        problems += 1
        print("FAIL build_rows: a repeats-count mismatch was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(repeats mismatch): expected exit 2, got {e.code}", file=sys.stderr)

    # --- build_rows: deterministic ordering — requirement, model order, cell_id
    #     — a re-run over shuffled input never reorders rows ---
    cases += 1
    two_models = {
        "m1": {"wire_family": "anthropic_messages", "vendor": "anthropic", "api_model_id": "m1-api", "_order": 1},
        "m0": {"wire_family": "anthropic_messages", "vendor": "anthropic", "api_model_id": "m0-api", "_order": 0},
    }
    shuffled_probes = []
    shuffled_expectations = []
    raw_all: dict[str, dict] = {}
    for model_slug, req in (("m1", "BHV-01"), ("m0", "calibration"), ("m1", "calibration")):
        param = "pA" if req == "calibration" else "pB"
        entries = [
            {"model": model_slug, "param": param, "value": "v", "mode": "default", "prompt": "x", "max_tokens": 16, "repeat": r}
            for r in (2, 1)  # deliberately out of order
        ]
        shuffled_probes.extend(entries)
        design = "control" if req == "calibration" else "repeats"
        # prereg: citations are only accepted on design=control rows — the
        # non-control (BHV-01) group here cites phase11: instead, exercising
        # a second resolvable citation form in the same ordering fixture.
        source = "prereg:Calibration design (rule 5d)" if design == "control" else "phase11:m--p--v--default--deadbeef"
        shuffled_expectations.append({
            "model": model_slug, "param": param, "value": "v", "mode": "default",
            "requirement": req, "design": design,
            "repeats": 2, "expected": "x", "expected_source": source,
        })
        for e in entries:
            pid = compute_behavioral_probe_id(e, two_models)
            raw_all[pid] = {
                "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
                "attempts": [{"status": 200, "response_body_raw": {"content": [{"type": "text", "text": "same"}]}}],
                "usage": {"output_tokens": 5},
            }
    cells1, _skips1, _ev1 = build_rows(
        shuffled_probes, shuffled_expectations, [], two_models, raw_all,
        docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
    )
    cells2, _skips2, _ev2 = build_rows(
        list(reversed(shuffled_probes)), list(reversed(shuffled_expectations)), [], two_models, raw_all,
        docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
    )
    order1 = [c["cell_id"] for c in cells1]
    order2 = [c["cell_id"] for c in cells2]
    if order1 != order2:
        problems += 1
        print(f"FAIL build_rows(ordering): shuffled input produced a different order: {order1!r} vs {order2!r}", file=sys.stderr)
    if order1 != sorted(order1, key=lambda cid: (
        {c["cell_id"]: c["requirement"] for c in cells1}[cid],
        {c["cell_id"]: two_models[c["model"]]["_order"] for c in cells1}[cid],
        cid,
    )):
        problems += 1
        print(f"FAIL build_rows(ordering): output not sorted by (requirement, model order, cell_id): {order1!r}", file=sys.stderr)

    # --- render_classified_file: idempotent, byte-identical for identical input ---
    cases += 1
    sample_cells = [{"cell_id": "x", "requirement": "calibration", "design": "control", "model": "m1", "vendor": "anthropic", "mode": "default", "param": "p", "value": "v", "repeats": 5, "comparisons": 4, "matches": 4, "rate": "4/4", "rate_pct": 100.0, "distinct_outputs": 1, "verdict": "deterministic", "expected": "x", "expected_source": "prereg:x", "probe_ids": ["a", "b"], "ancillary": {}, "note": None}]
    first = render_classified_file(checked="2026-09-03", evidence_through=None, cells=sample_cells, skips=[])
    second = render_classified_file(checked="2026-09-03", evidence_through=None, cells=sample_cells, skips=[])
    if first != second:
        problems += 1
        print("FAIL render_classified_file: expected byte-identical output for identical input", file=sys.stderr)

    # --- behavioral_header: counts are interpolated, not decorative ---
    cases += 1
    header_a = behavioral_header(cell_count=3, skip_count=2)
    header_b = behavioral_header(cell_count=5, skip_count=2)
    if "3" not in header_a or "5" not in header_b or header_a == header_b:
        problems += 1
        print(f"FAIL behavioral_header: counts not reflected distinctly: {header_a!r} vs {header_b!r}", file=sys.stderr)

    # --- no verdict/rate value in a rendered cell is a YAML boolean ---
    cases += 1
    doc = yaml.safe_load(render_classified_file(checked="2026-09-03", evidence_through=None, cells=sample_cells, skips=[]))
    for c in doc["cells"]:
        if not isinstance(c["rate"], str) or not isinstance(c["verdict"], str):
            problems += 1
            print(f"FAIL render_classified_file: rate/verdict must be strings, got {c!r}", file=sys.stderr)

    # --- load_behavioral_sets: fail-loud on a missing `expectations:` key ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        bad_dir = Path(td)
        (bad_dir / "bad.yaml").write_text("probes: []\nskips: []\n")
        try:
            load_behavioral_sets(bad_dir)
            problems += 1
            print("FAIL load_behavioral_sets: a file missing `expectations:` was not rejected", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL load_behavioral_sets(missing expectations): expected exit 2, got {e.code}", file=sys.stderr)

    # --- load_behavioral_sets: an empty directory fails loud (no *.yaml at all) ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        try:
            load_behavioral_sets(Path(td))
            problems += 1
            print("FAIL load_behavioral_sets(empty dir): expected SystemExit(2), got a return", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL load_behavioral_sets(empty dir): expected exit 2, got {e.code}", file=sys.stderr)

    # --- skip validation: neither/both citation fields fails loud ---
    for bad_skip in (
        {"model": "m1", "param": "p", "mode": "default", "requirement": "calibration", "reason": "placeholder"},
        {"model": "m1", "param": "p", "mode": "default", "requirement": "calibration", "reason": "placeholder",
         "cited_probe_id": "x", "cited_source": "prereg:x"},
    ):
        cases += 1
        try:
            build_rows([], [], [bad_skip], fixture_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
            problems += 1
            print(f"FAIL build_rows(skip citation {bad_skip}): expected SystemExit(2), got a return", file=sys.stderr)
        except SystemExit as e:
            if e.code != 2:
                problems += 1
                print(f"FAIL build_rows(skip citation): expected exit 2, got {e.code}", file=sys.stderr)

    # --- skip validation: a skip citing EACH of the two citation forms
    #     succeeds (12-03's own closed SKIP_REASONS vocabulary) ---
    cases += 1
    good_skip_pid = {
        "model": "m1", "param": "temperature", "mode": "default",
        "requirement": "BHV-02", "reason": "wire-rejects-temperature-default-mode",
        "cited_probe_id": "m--p--v--default--deadbeef",
    }
    good_skip_src = {
        "model": "m1", "param": "temperature", "mode": "thinking-on/thinking-off",
        "requirement": "BHV-02", "reason": "deferred-thinking-mode-cross-product",
        "cited_source": "docs-claims:temperature/anthropic",
    }
    try:
        _cells, skip_rows, _ev = build_rows(
            [], [], [good_skip_pid, good_skip_src], fixture_models, {},
            docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
        )
        if len(skip_rows) != 2:
            problems += 1
            print(f"FAIL build_rows(valid skips, both citation forms): expected 2 skip rows, got {len(skip_rows)}", file=sys.stderr)
    except SystemExit as e:
        problems += 1
        print(f"FAIL build_rows(valid skips, both citation forms): unexpected SystemExit({e.code})", file=sys.stderr)

    # --- build_rows: design=seed-pairs end to end — the effect-control group
    #     is consumed via `effect_control_value`, never treated as an orphan
    #     declared group needing its own `expectations:` entry ---
    cases += 1
    seed_probes = [
        {
            "model": "m1", "param": "seed", "value": 42, "mode": "default",
            "prompt": "x", "max_tokens": 16, "extra_params": {"seed": 42}, "repeat": r,
        }
        for r in range(1, 11)
    ] + [
        {
            "model": "m1", "param": "seed", "value": 99, "mode": "default",
            "prompt": "x", "max_tokens": 16, "extra_params": {"seed": 99},
        }
    ]
    seed_expectation = [{
        "model": "m1", "param": "seed", "value": 42, "mode": "default",
        "requirement": "BHV-01", "design": "seed-pairs", "pairs": 5, "calls": 10,
        "effect_control_value": 99,
        "expected": "x", "expected_source": "docs-claims:temperature/anthropic",
    }]
    seed_raw: dict[str, dict] = {}
    for e in seed_probes:
        pid = compute_behavioral_probe_id(e, fixture_models)
        seed_raw[pid] = {
            "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
            "attempts": [{"status": 200, "response_body_raw": {"content": [{"type": "text", "text": "same"}]}}],
            "usage": {"output_tokens": 5},
        }
    try:
        seed_cells, _skips, _ev = build_rows(
            seed_probes, seed_expectation, [], fixture_models, seed_raw,
            docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
        )
        if (
            len(seed_cells) != 1
            or seed_cells[0]["design"] != "seed-pairs"
            or seed_cells[0]["pairs"] != 5
            or seed_cells[0]["calls"] != 10
            or len(seed_cells[0]["probe_ids"]) != 10
        ):
            problems += 1
            print(f"FAIL build_rows(seed-pairs e2e): unexpected cell shape {seed_cells!r}", file=sys.stderr)
    except SystemExit as e:
        problems += 1
        print(f"FAIL build_rows(seed-pairs e2e): unexpected SystemExit({e.code})", file=sys.stderr)

    # --- build_rows: a seed-pairs expectation missing `effect_control_value`
    #     fails loud (no effect control to join means no cell can be built) ---
    cases += 1
    bad_seed_expectation = [dict(seed_expectation[0])]
    del bad_seed_expectation[0]["effect_control_value"]
    try:
        build_rows(
            seed_probes, bad_seed_expectation, [], fixture_models, seed_raw,
            docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
        )
        problems += 1
        print("FAIL build_rows: a seed-pairs expectation missing effect_control_value was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(missing effect_control_value): expected exit 2, got {e.code}", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="classify-behavioral.py",
        usage="classify-behavioral.py [--check | --selftest] [--raw-dir <dir>]",
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

    text, cells, skips = regenerate(raw_dir)
    CLASSIFIED_DIR.mkdir(parents=True, exist_ok=True)
    CLASSIFIED_PATH.write_text(text)
    print_summary(cells, skips)
    return 0


if __name__ == "__main__":
    sys.exit(main())
