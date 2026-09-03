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
#
# 12-04 adds three single-observation designs (BHV-03/04/05) — no `repeat`
# coordinate, a single fired call (or a triggering+control pair for
# `single-stop`) settling a single verified behavior rather than a rate:
# `single-stop` pairs a triggering call against its own model's
# non-triggering control (joined via `control_value`, mirroring
# `seed-pairs`' own `effect_control_value` mechanism); `single-candidates`
# and `single-logprobs` each read ONE fired cell through the CONTRACT
# classifier's own imported detectors (`classify_probes.detect_
# candidate_count`/`detect_logprobs`) rather than reimplementing them
# (D-11 key_link: one detector per fact across the contract and behavioral
# pipelines).
#
# 12-05 adds `tier-audit` (BHV-06 + the D-07 drift annex): a single fired OR
# CITED entry, path-aware — the contract classifier's own `detect_echo()`
# reads a single top-level response key, which is why every Anthropic
# `service-tier` cell landed in the silent-acceptance hazard class in Phase
# 11 (docstring precedent: `_get_field_value` in scripts/classify-probes.py
# claims "no wire family nests service_tier", a claim this very design
# exists to confront and, for Anthropic and Gemini, refute). `tier-audit`
# walks a declared candidate response PATH (not just a top-level key name)
# and records a distinct sentinel for "missing" vs. "present but null" —
# `response_present` is one of `present`/`null-valued`/`absent`, never
# conflated. Reused unmodified for the D-07 annex's two non-service-tier
# fields (DeepSeek's `thinking` object, Qwen's `reasoning_effort`), whose
# own questions have no known response-side echo location at all — answered
# through the SAME closed `echo_relation` vocabulary's `dropped`/`rejected`
# values rather than inventing a second design (the plan's own "single-
# candidates-style acceptance" framing, expressed without a second DESIGNS
# entry).
DESIGNS = frozenset({
    "control", "repeats", "seed-pairs",
    "single-stop", "single-candidates", "single-logprobs",
    "tier-audit",
})

# `tier-audit`'s own closed `echo_relation` vocabulary (12-05): `echoed`
# (response value equals request value), `translated` (a different value
# came back), `dropped` (the request carried a value and no response field
# exists to confirm it), `absent` (neither side carried one), `rejected`
# (the request was refused).
ECHO_RELATIONS = frozenset({"echoed", "translated", "dropped", "absent", "rejected"})

# `tier-audit`'s own closed `response_present` vocabulary (12-05): a missing
# key and a present-but-null value are NEVER conflated — the entire point of
# the path-aware lookup this design adds over the contract classifier's own
# top-level-only `_get_field_value()`.
RESPONSE_PRESENCE_VALUES = frozenset({"present", "null-valued", "absent"})

# Per-(wire_family, request_field) nested response-path override (12-05).
# Absent from this table means "look up `request_field` at the response TOP
# LEVEL" — `detect_echo()`'s own generic default, correct for every row this
# design serves except the two known request-top-level/response-nested
# asymmetries this plan's own BHV-06 audit exists to confront: Anthropic's
# documented `usage.service_tier` (docs-claims.yaml's amended
# `service-tier`/anthropic claim) and Gemini's own `usageMetadata.serviceTier`
# (discovered while resolving this plan's own Gemini request-placement
# question — the SAME shape of asymmetry, on the response side this time).
TIER_NESTED_PATH_OVERRIDES: dict[tuple[str, str], tuple[str, ...]] = {
    ("anthropic_messages", "service_tier"): ("usage", "service_tier"),
    ("gemini", "serviceTier"): ("usageMetadata", "serviceTier"),
}

# Anthropic's own literal response-side field name a caller MIRRORING the
# request shape would check (and find nothing) — always `service_tier`
# regardless of `request_field`, since this asymmetry is specific to that
# one field name, not parametrized by whatever field a given cell happens
# to test (12-05's own dual-lookup requirement is scoped to Anthropic only).
ANTHROPIC_TOP_LEVEL_MIRROR_FIELD = "service_tier"

_TIER_MISSING = object()

# Closed vocabulary for `single-stop`'s own two judgement fields (12-04).
# `truncation_verdict` is derived from the returned TEXT alone (never the
# finish field) -- `stop-honored` when the triggering text ends before the
# stop token and is shorter than the control's, `stop-ignored` when the stop
# token appears in the triggering text or the two texts are equal length,
# `inconclusive` otherwise (including either call missing/empty visible
# text -- a stop-family claim from one call alone is never asserted).
TRUNCATION_VERDICTS = frozenset({"stop-honored", "stop-ignored", "inconclusive"})

# `finish_reason_honest` is a SEPARATE three-valued judgement about whether
# the wire family's OWN finish/stop-reason field can be trusted as proof --
# `honest` only at the one wire family (anthropic_messages) whose dedicated
# `stop_sequence` value is distinguishable from a natural completion AND
# whose claim matches what the text shows; `dishonest` when that field
# contradicts the text; `ambiguous` everywhere else (every other wire family
# shares one finish value for both cases, and any inconclusive-text case).
# A `stop-honored` verdict at a non-anthropic wire family MUST still record
# `ambiguous` here -- the classifier makes that impossible to violate rather
# than merely discouraging it (an acceptance criterion asserts this).
FINISH_REASON_HONEST_VALUES = frozenset({"honest", "ambiguous", "dishonest"})

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
    "wire-rejects-stop-default-mode",
    "out-of-scope-multi-sequence-contradiction",
    "wire-rejects-gemini-candidate-count",
    "no-request-side-field-for-vendor",
    "already-settled-logprobs-honored",
    # 12-05: the documented Qwen reasoning_effort/thinking_budget mutual
    # exclusion is a cheap, genuinely falsifiable claim, but firing it falls
    # outside this plan's preregistered envelope/cell list — declared rather
    # than silently dropped, a candidate for a later phase.
    "deferred-out-of-envelope",
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


def load_behavioral_sets(
    sets_dir: Path = BEHAVIORAL_SETS_DIR,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[str]]:
    """Load every probes/sets/behavioral/*.yaml file. Returns (all_probes,
    all_expectations, all_skips, all_cited_cells, checked_dates). Fails loud
    (exit 2) when a file is missing its required `probes:`/`expectations:`/
    `skips:` top-level keys, or when the directory has no *.yaml files at
    all. `cited_cells:` (12-05, a new top-level key) is OPTIONAL and defaults
    to an empty list when absent — every file predating this plan omits it,
    and that must stay a no-op — but a PRESENT `cited_cells:` key must still
    be a list, same fail-loud discipline as the three required keys."""
    files = sorted(Path(sets_dir).glob("*.yaml")) if Path(sets_dir).is_dir() else []
    if not files:
        _fail(2, f"no probes/sets/behavioral/*.yaml files found in {sets_dir}")
    all_probes: list[dict] = []
    all_expectations: list[dict] = []
    all_skips: list[dict] = []
    all_cited_cells: list[dict] = []
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
        if "cited_cells" in data and not isinstance(data["cited_cells"], list):
            _fail(2, f"{f}: `cited_cells:` must be a list")
        checked_dates.append(data.get("checked"))
        all_probes.extend(data["probes"])
        all_expectations.extend(data["expectations"])
        all_skips.extend(data["skips"])
        all_cited_cells.extend(data.get("cited_cells") or [])
    return all_probes, all_expectations, all_skips, all_cited_cells, checked_dates


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
    # 12-05: mirrors runner.py's own build_entry_request() step-for-step —
    # a declared `top_level_params` mapping (Gemini's own service-tier
    # cells, the only entries in this plan that carry it) is merged at the
    # top level AFTER the max-tokens override and BEFORE apply_omit(), or
    # this function's recomputed probe_id would silently diverge from what
    # the harness actually fired.
    top_level_params = entry.get("top_level_params") or {}
    if top_level_params:
        request_body = {**request_body, **top_level_params}
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


def _join_flat_entry(entry: dict, models: dict[str, dict], raw_records: dict[str, dict]) -> dict:
    """Join one non-repeated declared entry (no `repeat` key) to its raw
    evidence -- shared by all three 12-04 single-observation designs, none
    of which reduce a repeat group. Returns probe_id, the FULL response
    body (single-candidates/-logprobs need the whole body, not just the
    visible text, to run the imported contract detectors), status,
    terminal, finish_reason, visible text, usage, wire_family, and
    recorded_at. A missing/unfired record degrades to an honestly empty
    shape (response_body={}, everything else None) rather than raising --
    the same never-crash-on-absence discipline `_join_seed_entry` already
    established."""
    model = models[entry["model"]]
    wire_family = model["wire_family"]
    pid = compute_behavioral_probe_id(entry, models)
    record = raw_records.get(pid)
    record_found = record is not None
    status = None
    response_body: dict = {}
    terminal = None
    recorded_at = None
    usage: dict = {}
    if record is not None:
        terminal = record.get("terminal")
        attempts = record.get("attempts") or []
        last = attempts[-1] if attempts else {}
        status = last.get("status")
        response_body = last.get("response_body_raw") or {}
        recorded_at = record.get("recorded_at")
        usage = record.get("usage") or {}
    text = None
    finish_reason = None
    if terminal == "verdict":
        text = _get_message_text(response_body, wire_family)
        finish_reason = _get_finish_reason(response_body, wire_family)
    return {
        "probe_id": pid, "response_body": response_body, "status": status,
        "terminal": terminal, "finish_reason": finish_reason, "text": text,
        "usage": usage, "wire_family": wire_family, "recorded_at": recorded_at,
        "record_found": record_found,
    }


def reduce_single_stop_group(
    triggering_entry: dict, control_entry: dict, models: dict[str, dict],
    raw_records: dict[str, dict], *, stop_token: str,
) -> dict:
    """BHV-03's own reduction (12-04): pairs a triggering call against its
    own model's non-triggering control. `truncation_verdict` is derived
    from the returned TEXT alone, in the plan's own stated order --
    `stop-ignored` if the stop token appears anywhere in the triggering
    text OR the two texts are the same length (either means the stop
    parameter did not shorten anything); `stop-honored` only when the token
    is ABSENT and the triggering text is strictly shorter than the
    control's; `inconclusive` otherwise (including either call missing or
    carrying empty visible text -- `not text` catches both, matching
    `reduce_repeat_group`'s own no-signal convention for an empty-but-200
    response).

    `finish_reason_honest` is a separate three-valued judgement: `ambiguous`
    at every wire family other than `anthropic_messages` (whose shared
    finish value cannot distinguish a triggered stop from a natural
    completion) and at any `inconclusive` verdict (nothing to honestly
    judge the field against); at `anthropic_messages`, `honest` when the
    field's own claim (`stop_reason == "stop_sequence"`) agrees with what
    the text showed, `dishonest` when it contradicts it."""
    trig = _join_flat_entry(triggering_entry, models, raw_records)
    ctrl = _join_flat_entry(control_entry, models, raw_records)
    if not trig["record_found"] or not ctrl["record_found"]:
        _fail(
            2,
            "single-stop group is missing raw evidence for its triggering or control "
            f"call (triggering={trig['probe_id']!r} found={trig['record_found']}, "
            f"control={ctrl['probe_id']!r} found={ctrl['record_found']}) — a stop cell "
            "needs BOTH calls on disk to produce a verdict, never one alone",
        )
    joined_at = [t for t in (trig["recorded_at"], ctrl["recorded_at"]) if t]

    triggering_text_length = len(trig["text"]) if trig["text"] else (0 if trig["text"] == "" else None)
    control_text_length = len(ctrl["text"]) if ctrl["text"] else (0 if ctrl["text"] == "" else None)

    if not trig["text"] or not ctrl["text"]:
        truncation_verdict = "inconclusive"
        stop_present = None
    else:
        stop_present = stop_token in trig["text"]
        if stop_present:
            truncation_verdict = "stop-ignored"
        elif triggering_text_length == control_text_length:
            truncation_verdict = "stop-ignored"
        elif triggering_text_length < control_text_length:
            truncation_verdict = "stop-honored"
        else:
            truncation_verdict = "inconclusive"

    wire_family = trig["wire_family"]
    if truncation_verdict == "inconclusive" or wire_family != "anthropic_messages":
        finish_reason_honest = "ambiguous"
    else:
        reason_says_stop = trig["finish_reason"] == "stop_sequence"
        text_shows_stop = truncation_verdict == "stop-honored"
        finish_reason_honest = "honest" if reason_says_stop == text_shows_stop else "dishonest"

    return {
        "probe_ids": [trig["probe_id"], ctrl["probe_id"]],
        "triggering_text_length": triggering_text_length,
        "control_text_length": control_text_length,
        "stop_token_in_triggering_text": stop_present,
        "truncation_verdict": truncation_verdict,
        "finish_reason_honest": finish_reason_honest,
        "ancillary": {
            "triggering_status": trig["status"], "control_status": ctrl["status"],
            "triggering_finish_reason": trig["finish_reason"], "control_finish_reason": ctrl["finish_reason"],
        },
        "joined_at": joined_at,
    }


def reduce_single_candidates_group(
    entry: dict, models: dict[str, dict], raw_records: dict[str, dict], *, requested_n: int,
) -> dict:
    """BHV-04's own reduction (12-04): a single `n>1` fired cell, read
    through `scripts/classify-probes.py`'s OWN `detect_candidate_count()`
    and `_get_candidate_count()` -- imported, never reimplemented (this
    module's own read_first instruction). A non-200/non-verdict record
    (the real, observed shape at 4 of 7 fired models: `n>1` genuinely
    REJECTED even though `n=1` classified accepted-honored in Phase 11 --
    the trivial n=1 case Phase 11 fired can never refute an n>1 claim) is
    classified `rejected` directly rather than handed to the detector,
    which has no rejected-vs-unverified distinction of its own to draw on
    an error body. `returned_count` stays an honest integer even on a
    rejection -- `_get_candidate_count`'s own `len(choices or [])` reads 0
    from an error body with no `choices` key, never None."""
    wire_family = models[entry["model"]]["wire_family"]
    joined = _join_flat_entry(entry, models, raw_records)
    if joined["terminal"] == "verdict" and joined["status"] == 200:
        state, evidence = classify_probes.detect_candidate_count(
            joined["response_body"], row_id="n", wire_family=wire_family,
            resolved_field=None, requested_value=str(requested_n), usage=joined["usage"],
        )
    else:
        state, evidence = "rejected", "none"
    returned_count = classify_probes._get_candidate_count(joined["response_body"], wire_family)
    return {
        "probe_ids": [joined["probe_id"]],
        "requested_n": requested_n,
        "returned_count": returned_count if returned_count is not None else 0,
        "state": state,
        "evidence": evidence,
        "ancillary": {"status": joined["status"], "terminal": joined["terminal"]},
        "joined_at": [joined["recorded_at"]] if joined["recorded_at"] else [],
    }


def _get_logprobs_entries(response_body: dict, wire_family: str) -> list:
    """The raw per-token logprobs entries array, read directly -- every
    12-04 `single-logprobs` target model shares the `openai_compat` wire
    shape, so this stays scoped to that family rather than generalizing
    past what this plan's own cells actually exercise."""
    if wire_family == "openai_compat":
        content = ((response_body.get("choices") or [{}])[0].get("logprobs") or {}).get("content")
        return content or []
    return []


def _logprobs_alternatives_honored(entries: list, requested_top_logprobs: int) -> bool:
    """True iff every per-token entry carries at least the requested number
    of alternatives (a vendor MAY return fewer than requested per its own
    documented hedge -- recorded as a fact, never raised on)."""
    if not entries:
        return False
    for e in entries:
        alts = e.get("top_logprobs") if isinstance(e, dict) else None
        if not alts or len(alts) < requested_top_logprobs:
            return False
    return True


def reduce_single_logprobs_group(
    entry: dict, models: dict[str, dict], raw_records: dict[str, dict], *, requested_top_logprobs: int,
) -> dict:
    """BHV-05's own reduction (12-04): a single combined `logprobs`+
    `top_logprobs` fired cell, read through `scripts/classify-probes.py`'s
    OWN `detect_logprobs()` (imported) for `logprobs_present`, plus a local
    per-token entry count/alternatives-honored reading -- the contract
    classifier's own detector is boolean-only (`_get_logprobs_present`), so
    the entry-count/alternatives detail this design's own must_haves truth
    requires is read locally, never a second presence detector."""
    wire_family = models[entry["model"]]["wire_family"]
    joined = _join_flat_entry(entry, models, raw_records)
    state, evidence = classify_probes.detect_logprobs(
        joined["response_body"], row_id="logprobs-reverify", wire_family=wire_family,
        resolved_field=None, requested_value="true", usage=joined["usage"],
    )
    entries = _get_logprobs_entries(joined["response_body"], wire_family)
    return {
        "probe_ids": [joined["probe_id"]],
        "logprobs_present": state == "accepted-honored",
        "logprobs_token_entries": len(entries),
        "logprobs_alternatives_honored": _logprobs_alternatives_honored(entries, requested_top_logprobs),
        "state": state,
        "evidence": evidence,
        "ancillary": {"status": joined["status"], "terminal": joined["terminal"]},
        "joined_at": [joined["recorded_at"]] if joined["recorded_at"] else [],
    }


def _get_path_value(response_body: dict, path: tuple[str, ...]):
    """Walk a declared key PATH through a response body, one segment at a
    time. Returns the sentinel `_TIER_MISSING` the instant any segment is
    absent or the current value is not a mapping -- distinguishing a
    genuinely MISSING key from a key present with an explicit `null` value,
    which a bare `.get(path, None)` chain could never tell apart (12-05's
    own must_haves truth: "a response carrying no tier field at all is
    recorded as absent, distinguished from a tier field present with a null
    value")."""
    cur = response_body
    for seg in path:
        if not isinstance(cur, dict) or seg not in cur:
            return _TIER_MISSING
        cur = cur[seg]
    return cur


def _tier_presence(value) -> str:
    """The three-valued `response_present` vocabulary this design's rows
    carry: `absent` (the sentinel from `_get_path_value` above), `null-valued`
    (the key exists, its value is Python `None`/YAML/JSON `null`), or
    `present` (any other value, including an empty string or `0`)."""
    if value is _TIER_MISSING:
        return "absent"
    if value is None:
        return "null-valued"
    return "present"


def _tier_error_names_field(response_body: dict, field_name: str | None) -> bool | None:
    """Whether a rejected request's own returned error body mentions the
    field name being tested, read as a case-insensitive substring search
    over the serialized body -- the mechanical reading of D-15's own trap
    question ("whether the rejection names the field is recorded from the
    returned error body"). `None` (not a boolean) when there is no field
    name to search for at all (should not occur for a real cell, kept as an
    honest degrade rather than a crash)."""
    if not field_name:
        return None
    try:
        text = json.dumps(response_body)
    except (TypeError, ValueError):
        return False
    return field_name.lower() in text.lower()


def _reduce_tier_audit_core(
    *, response_body: dict, status: int | None, terminal: str | None, wire_family: str,
    request_field: str | None, request_value,
) -> dict:
    """The shared tier-audit reduction core (12-05) -- given a response body
    plus its status/terminal and the declared request field/value, computes
    every `tier-audit` row field. Called identically by a FIRED entry
    (`reduce_tier_audit_group`, below) and a CITED entry
    (`reduce_tier_audit_cited`, below) reading an existing raw record
    directly -- one reduction, two ways to reach it, so a fired and an
    audited-by-citation row are never scored by two independently-drifting
    code paths."""
    omitted = request_value is None
    rejected = terminal != "verdict" or status != 200

    if rejected:
        return {
            "request_field_path": request_field,
            "request_value": request_value,
            "response_field_path": None,
            "response_value": None,
            "response_present": "absent",
            "echo_relation": "rejected",
            "rejection_names_field": _tier_error_names_field(response_body, request_field),
            "response_top_level_present": None,
            "response_top_level_value": None,
            "note": None,
        }

    path = TIER_NESTED_PATH_OVERRIDES.get((wire_family, request_field), (request_field,)) if request_field else (request_field,)
    value = _get_path_value(response_body, path)
    presence = _tier_presence(value)
    response_value = value if presence == "present" else None

    if omitted:
        # Neither side carried a value UNLESS the vendor injected a resolved
        # default despite no request-side field at all -- distinct from a
        # request-carried value with no response confirmation ("dropped"
        # below), since there was nothing here TO drop.
        echo_relation = "absent" if presence == "absent" else "translated"
    elif presence in ("absent", "null-valued"):
        # The request carried a value; nothing confirms it landed (a null
        # value is treated the same as absent for echo purposes -- the
        # DISTINCTION between the two lives in `response_present` itself,
        # never collapsed here).
        echo_relation = "dropped"
    elif str(response_value) == str(request_value):
        echo_relation = "echoed"
    else:
        echo_relation = "translated"

    note = None
    if omitted and presence == "present":
        note = (
            "A tier field appeared in the response despite the request omitting it "
            "entirely -- for a vendor whose documentation states no service-tier "
            "concept exists, this refutes the documented-absence prior directly; for "
            "a documented vendor it reveals the field's own default value. Either way "
            "this is a finding, not decoration."
        )

    result = {
        "request_field_path": request_field,
        "request_value": request_value,
        "response_field_path": ".".join(path) if request_field else None,
        "response_value": response_value,
        "response_present": presence,
        "echo_relation": echo_relation,
        "rejection_names_field": None,
        "response_top_level_present": None,
        "response_top_level_value": None,
        "note": note,
    }

    if wire_family == "anthropic_messages" and request_field:
        # 12-05's own dual-lookup requirement, scoped to Anthropic alone: a
        # caller who mirrors the REQUEST shape (checking the response TOP
        # LEVEL under the same field name) finds nothing, because the real
        # answer is nested at `usage.service_tier` -- both lookups are
        # recorded as separate fields so the asymmetry itself is visible in
        # the classified row, not just asserted in prose.
        top_value = _get_path_value(response_body, (ANTHROPIC_TOP_LEVEL_MIRROR_FIELD,))
        top_presence = _tier_presence(top_value)
        result["response_top_level_present"] = top_presence
        result["response_top_level_value"] = top_value if top_presence == "present" else None

    return result


def reduce_tier_audit_group(
    entry: dict, models: dict[str, dict], raw_records: dict[str, dict],
    *, request_field: str | None, request_value,
) -> dict:
    """`tier-audit`'s own reduction for a FIRED entry (12-05): joins one
    non-repeated declared entry via `_join_flat_entry` (shared with the
    12-04 single-observation designs) and hands its response body/status/
    terminal to `_reduce_tier_audit_core` above."""
    joined = _join_flat_entry(entry, models, raw_records)
    wire_family = models[entry["model"]]["wire_family"]
    core = _reduce_tier_audit_core(
        response_body=joined["response_body"], status=joined["status"], terminal=joined["terminal"],
        wire_family=wire_family, request_field=request_field, request_value=request_value,
    )
    core["probe_ids"] = [joined["probe_id"]]
    core["ancillary"] = {"status": joined["status"], "terminal": joined["terminal"]}
    core["joined_at"] = [joined["recorded_at"]] if joined["recorded_at"] else []
    core["audited_from_existing_evidence"] = False
    core["cited_probe_id"] = None
    return core


def reduce_tier_audit_cited(
    cited_probe_id: str, wire_family: str, raw_records: dict[str, dict],
    *, request_field: str | None, request_value,
) -> dict:
    """`tier-audit`'s own reduction for a CITED entry (12-05, D-13's
    every-vendor audit without re-spending on already-fired values): reads
    an EXISTING raw record directly by its probe_id -- never re-derived via
    `compute_behavioral_probe_id`, since a cited entry has no declared
    `probes:` entry of its own to recompute from. Fails loud (exit 2) when
    the cited probe_id has no readable raw record -- an audit row with no
    evidence behind it is worse than an absent row (this plan's own
    must_haves truth)."""
    record = raw_records.get(cited_probe_id)
    if record is None:
        _fail(2, f"cited_cells entry cites probe_id {cited_probe_id!r}, which has no raw record on disk")
    terminal = record.get("terminal")
    attempts = record.get("attempts") or []
    last = attempts[-1] if attempts else {}
    status = last.get("status")
    response_body = last.get("response_body_raw") or {}
    recorded_at = record.get("recorded_at")
    core = _reduce_tier_audit_core(
        response_body=response_body, status=status, terminal=terminal,
        wire_family=wire_family, request_field=request_field, request_value=request_value,
    )
    core["probe_ids"] = [cited_probe_id]
    core["ancillary"] = {"status": status, "terminal": terminal}
    core["joined_at"] = [recorded_at] if recorded_at else []
    core["audited_from_existing_evidence"] = True
    core["cited_probe_id"] = cited_probe_id
    return core


def build_rows(
    probes: list[dict],
    expectations: list[dict],
    skips: list[dict],
    models: dict[str, dict],
    raw_records: dict[str, dict],
    *,
    cited_cells: list[dict] = (),
    docs_claims_index: set[tuple[str, str]],
    contract_probe_ids: set[str],
    prereg_text: str,
) -> tuple[list[dict], list[dict], str | None]:
    """The full group + match-to-expectation + citation-resolve + reduce
    pipeline. Returns (cells, skip_rows, evidence_through). `cited_cells`
    (12-05, default empty — every pre-existing call site omits it and gets
    byte-identical behavior) are audit rows with NO matching `probes:` entry
    at all — resolved directly against `raw_records` by their own
    `cited_probe_id`, never through the `groups`/`expectations_by_key`
    machinery below, which exists only for entries this file itself fired."""
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

    # A `design: single-stop` expectation's `control_value` names a SECOND
    # declared probe group (same model/param/mode, the non-triggering
    # control) — the same pop-before-orphan-check mechanism as seed-pairs'
    # own `effect_control_value` above, applied to BHV-03's own pairing
    # (12-04).
    single_stop_control_groups: dict[tuple, dict] = {}
    for key, exp in expectations_by_key.items():
        if exp.get("design") != "single-stop":
            continue
        cv = exp.get("control_value")
        if cv is None:
            _fail(2, f"group {key!r}: a single-stop expectation requires `control_value`")
        if not exp.get("stop_token"):
            _fail(2, f"group {key!r}: a single-stop expectation requires `stop_token`")
        model, param, _value, mode = key
        cv_key = (model, param, cv, mode)
        if cv_key not in groups:
            _fail(
                2,
                f"group {key!r}: no declared probe group for its control_value "
                f"{cv!r} (expected group_key {cv_key!r})",
            )
        cv_entries = groups.pop(cv_key)
        if len(cv_entries) != 1:
            _fail(2, f"group {cv_key!r}: control group must have exactly 1 entry, got {len(cv_entries)}")
        single_stop_control_groups[key] = cv_entries[0]

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

        if design == "single-stop":
            if len(entries) != 1:
                _fail(2, f"group {key!r}: single-stop expects exactly 1 triggering entry, got {len(entries)}")
            control_entry = single_stop_control_groups[key]
            reduced = reduce_single_stop_group(
                entries[0], control_entry, models, raw_records, stop_token=expectation["stop_token"],
            )
            all_joined_at.extend(reduced.pop("joined_at"))
            if reduced["truncation_verdict"] not in TRUNCATION_VERDICTS:
                _fail(2, f"group {key!r}: truncation_verdict {reduced['truncation_verdict']!r} outside {sorted(TRUNCATION_VERDICTS)}")
            if reduced["finish_reason_honest"] not in FINISH_REASON_HONEST_VALUES:
                _fail(2, f"group {key!r}: finish_reason_honest {reduced['finish_reason_honest']!r} outside {sorted(FINISH_REASON_HONEST_VALUES)}")
            cells.append({
                "cell_id": f"{model}--{param}--{value}--{mode}",
                "requirement": requirement,
                "design": design,
                "model": model,
                "vendor": models[model]["vendor"],
                "mode": mode,
                "param": param,
                "value": value,
                "stop_token": expectation["stop_token"],
                "triggering_text_length": reduced["triggering_text_length"],
                "control_text_length": reduced["control_text_length"],
                "stop_token_in_triggering_text": reduced["stop_token_in_triggering_text"],
                "truncation_verdict": reduced["truncation_verdict"],
                "finish_reason_honest": reduced["finish_reason_honest"],
                "expected": expected,
                "expected_source": expected_source,
                "probe_ids": reduced["probe_ids"],
                "ancillary": reduced["ancillary"],
                "note": None,
            })
            continue

        if design == "single-candidates":
            if len(entries) != 1:
                _fail(2, f"group {key!r}: single-candidates expects exactly 1 fired entry, got {len(entries)}")
            try:
                requested_n = int(value)
            except (TypeError, ValueError):
                _fail(2, f"group {key!r}: single-candidates `value` must be an int-parseable n, got {value!r}")
            reduced = reduce_single_candidates_group(entries[0], models, raw_records, requested_n=requested_n)
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
                "requested_n": reduced["requested_n"],
                "returned_count": reduced["returned_count"],
                "state": reduced["state"],
                "evidence": reduced["evidence"],
                "expected": expected,
                "expected_source": expected_source,
                "probe_ids": reduced["probe_ids"],
                "ancillary": reduced["ancillary"],
                "note": None,
            })
            continue

        if design == "single-logprobs":
            if len(entries) != 1:
                _fail(2, f"group {key!r}: single-logprobs expects exactly 1 fired entry, got {len(entries)}")
            settles_probe_id = expectation.get("settles_probe_id")
            if settles_probe_id and settles_probe_id not in contract_probe_ids:
                _fail(
                    2,
                    f"group {key!r}: settles_probe_id does not resolve to a "
                    f"probes/classified/contract-sweep.yaml row: {settles_probe_id!r}",
                )
            requested_top_logprobs = expectation.get("requested_top_logprobs", 3)
            reduced = reduce_single_logprobs_group(
                entries[0], models, raw_records, requested_top_logprobs=requested_top_logprobs,
            )
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
                "requested_top_logprobs": requested_top_logprobs,
                "logprobs_present": reduced["logprobs_present"],
                "logprobs_token_entries": reduced["logprobs_token_entries"],
                "logprobs_alternatives_honored": reduced["logprobs_alternatives_honored"],
                "state": reduced["state"],
                "evidence": reduced["evidence"],
                "settles_probe_id": settles_probe_id,
                "expected": expected,
                "expected_source": expected_source,
                "probe_ids": reduced["probe_ids"],
                "ancillary": reduced["ancillary"],
                "note": None,
            })
            continue

        if design == "tier-audit":
            if len(entries) != 1:
                _fail(2, f"group {key!r}: tier-audit expects exactly 1 fired entry, got {len(entries)}")
            request_field = expectation.get("request_field")
            request_value = expectation.get("request_value")
            reduced = reduce_tier_audit_group(
                entries[0], models, raw_records, request_field=request_field, request_value=request_value,
            )
            all_joined_at.extend(reduced.pop("joined_at"))
            if reduced["echo_relation"] not in ECHO_RELATIONS:
                _fail(2, f"group {key!r}: echo_relation {reduced['echo_relation']!r} outside {sorted(ECHO_RELATIONS)}")
            if reduced["response_present"] not in RESPONSE_PRESENCE_VALUES:
                _fail(2, f"group {key!r}: response_present {reduced['response_present']!r} outside {sorted(RESPONSE_PRESENCE_VALUES)}")
            note = reduced["note"] or expectation.get("registry_note")
            cells.append({
                "cell_id": f"{model}--{param}--{value}--{mode}",
                "requirement": requirement,
                "design": design,
                "model": model,
                "vendor": models[model]["vendor"],
                "mode": mode,
                "param": param,
                "value": value,
                "request_field_path": reduced["request_field_path"],
                "request_value": reduced["request_value"],
                "response_field_path": reduced["response_field_path"],
                "response_value": reduced["response_value"],
                "response_present": reduced["response_present"],
                "echo_relation": reduced["echo_relation"],
                "rejection_names_field": reduced["rejection_names_field"],
                "response_top_level_present": reduced["response_top_level_present"],
                "response_top_level_value": reduced["response_top_level_value"],
                "audited_from_existing_evidence": reduced["audited_from_existing_evidence"],
                "cited_probe_id": reduced["cited_probe_id"],
                "expected": expected,
                "expected_source": expected_source,
                "probe_ids": reduced["probe_ids"],
                "ancillary": reduced["ancillary"],
                "note": note,
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

    # `cited_cells:` (12-05, D-13's every-vendor audit without re-spending on
    # already-fired values): each entry names an EXISTING raw record rather
    # than a declared `probes:` group, so it never enters `groups`/
    # `expectations_by_key` above — its own citation/requirement/design
    # validation and reduction happen here instead, using the SAME
    # `_reduce_tier_audit_core` reduction a fired tier-audit row uses.
    for cc in cited_cells:
        cc_model = cc.get("model")
        cc_param = cc.get("param")
        cc_value = cc.get("value")
        cc_mode = cc.get("mode")
        cc_requirement = cc.get("requirement")
        cc_design = cc.get("design")
        if cc_model not in models:
            _fail(2, f"cited_cells entry: unknown model slug {cc_model!r}")
        if cc_requirement not in REQUIREMENTS:
            _fail(2, f"cited_cells entry: requirement {cc_requirement!r} is outside the closed vocabulary {sorted(REQUIREMENTS)}")
        if cc_design not in DESIGNS:
            _fail(2, f"cited_cells entry: design {cc_design!r} is outside the closed vocabulary {sorted(DESIGNS)}")
        if cc_design != "tier-audit":
            _fail(2, f"cited_cells entry: design {cc_design!r} is not supported for a cited cell (only 'tier-audit' reads existing evidence today)")
        cc_expected_source = cc.get("expected_source")
        if not cc_expected_source:
            _fail(2, f"cited_cells entry for model={cc_model!r} value={cc_value!r}: missing required `expected_source`")
        resolve_citation(
            cc_expected_source, docs_claims_index=docs_claims_index, contract_probe_ids=contract_probe_ids,
            prereg_text=prereg_text, allow_prereg=False,
        )
        cc_expected = cc.get("expected")
        if not cc_expected:
            _fail(2, f"cited_cells entry for model={cc_model!r} value={cc_value!r}: missing required `expected`")
        cc_cited_probe_id = cc.get("cited_probe_id")
        if not cc_cited_probe_id:
            _fail(2, f"cited_cells entry for model={cc_model!r} value={cc_value!r}: missing required `cited_probe_id`")
        cc_wire_family = models[cc_model]["wire_family"]
        reduced = reduce_tier_audit_cited(
            cc_cited_probe_id, cc_wire_family, raw_records,
            request_field=cc.get("request_field"), request_value=cc.get("request_value"),
        )
        all_joined_at.extend(reduced.pop("joined_at"))
        if reduced["echo_relation"] not in ECHO_RELATIONS:
            _fail(2, f"cited_cells entry {cc_cited_probe_id!r}: echo_relation {reduced['echo_relation']!r} outside {sorted(ECHO_RELATIONS)}")
        if reduced["response_present"] not in RESPONSE_PRESENCE_VALUES:
            _fail(2, f"cited_cells entry {cc_cited_probe_id!r}: response_present {reduced['response_present']!r} outside {sorted(RESPONSE_PRESENCE_VALUES)}")
        cells.append({
            "cell_id": f"{cc_model}--{cc_param}--{cc_value}--{cc_mode}",
            "requirement": cc_requirement,
            "design": cc_design,
            "model": cc_model,
            "vendor": models[cc_model]["vendor"],
            "mode": cc_mode,
            "param": cc_param,
            "value": cc_value,
            "request_field_path": reduced["request_field_path"],
            "request_value": reduced["request_value"],
            "response_field_path": reduced["response_field_path"],
            "response_value": reduced["response_value"],
            "response_present": reduced["response_present"],
            "echo_relation": reduced["echo_relation"],
            "rejection_names_field": reduced["rejection_names_field"],
            "response_top_level_present": reduced["response_top_level_present"],
            "response_top_level_value": reduced["response_top_level_value"],
            "audited_from_existing_evidence": reduced["audited_from_existing_evidence"],
            "cited_probe_id": reduced["cited_probe_id"],
            "expected": cc_expected,
            "expected_source": cc_expected_source,
            "probe_ids": reduced["probe_ids"],
            "ancillary": reduced["ancillary"],
            "note": reduced["note"],
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
    probes, expectations, skips, cited_cells, checked_dates = load_behavioral_sets(sets_dir)
    docs_claims_index = load_docs_claims_index()
    contract_probe_ids = load_contract_probe_ids()
    prereg_text = load_prereg_text()

    cells, skip_rows, evidence_through = build_rows(
        probes, expectations, skips, models, raw_records,
        cited_cells=cited_cells,
        docs_claims_index=docs_claims_index,
        contract_probe_ids=contract_probe_ids,
        prereg_text=prereg_text,
    )
    checked = max(d for d in checked_dates if d) if any(checked_dates) else None
    text = render_classified_file(checked=checked, evidence_through=evidence_through, cells=cells, skips=skip_rows)
    return text, cells, skip_rows


def print_summary(cells: list[dict], skips: list[dict]) -> None:
    """Tallies the primary judgement field per row -- `verdict` for the
    rate-based designs (control/repeats/seed-pairs), `truncation_verdict`
    for single-stop, `state` for single-candidates/single-logprobs, `echo_relation`
    for tier-audit (12-05: this design carries neither a `verdict` nor a
    `state` key — a bare `c["verdict"]` KeyErrors on it, same reason 12-04's
    own three single-observation designs needed this same fallback chain)."""
    tally: dict[str, int] = {}
    for c in cells:
        key = c.get("verdict") or c.get("truncation_verdict") or c.get("state") or c.get("echo_relation")
        tally[key] = tally.get(key, 0) + 1
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

    # ---------------------------------------------------------------------
    # 12-04's three single-observation designs (single-stop/-candidates/
    # -logprobs) — no repeat coordinate, joined via _join_flat_entry.
    # ---------------------------------------------------------------------
    openai_compat_models = {
        "m1": {"wire_family": "anthropic_messages", "vendor": "anthropic", "api_model_id": "m1-api", "_order": 0},
        "m2": {"wire_family": "openai_compat", "vendor": "xai", "api_model_id": "m2-api", "_order": 1},
    }

    def make_stop_entries(model: str, stop_value: str = "triggering", control_value: str = "control-no-stop"):
        trig = {"model": model, "param": "stop-truncation", "value": stop_value, "mode": "default", "prompt": "x", "max_tokens": 16, "extra_params": {"stop": ["STOP"]}}
        ctrl = {"model": model, "param": "stop-truncation", "value": control_value, "mode": "default", "prompt": "x", "max_tokens": 16}
        return trig, ctrl

    def stop_raw(pid: str, text: str | None, *, status: int = 200, finish_reason: str = "end_turn", family: str = "anthropic_messages") -> dict:
        if family == "anthropic_messages":
            body = {"content": [{"type": "text", "text": text}], "stop_reason": finish_reason} if text is not None else {}
        else:
            body = {"choices": [{"message": {"content": text}, "finish_reason": finish_reason}]} if text is not None else {}
        return {
            "terminal": "verdict" if status == 200 else "retry_exhausted",
            "recorded_at": "2026-09-03T00:00:00Z",
            "attempts": [{"status": status, "response_body_raw": body}],
            "usage": {"output_tokens": 5},
        }

    # --- reduce_single_stop_group: anthropic, honored + honest (text
    #     shorter, no stop token, field correctly claims stop_sequence) ---
    cases += 1
    trig, ctrl = make_stop_entries("m1")
    trig_pid = compute_behavioral_probe_id(trig, openai_compat_models)
    ctrl_pid = compute_behavioral_probe_id(ctrl, openai_compat_models)
    raw = {trig_pid: stop_raw(trig_pid, "abc", finish_reason="stop_sequence"), ctrl_pid: stop_raw(ctrl_pid, "abcdef")}
    reduced = reduce_single_stop_group(trig, ctrl, openai_compat_models, raw, stop_token="STOP")
    if reduced["truncation_verdict"] != "stop-honored" or reduced["finish_reason_honest"] != "honest":
        problems += 1
        print(f"FAIL reduce_single_stop_group(anthropic honest): got {reduced['truncation_verdict']!r}/{reduced['finish_reason_honest']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: anthropic, honored but DISHONEST (text
    #     shows truncation, but the field does not claim stop_sequence) ---
    cases += 1
    raw_dishonest = {trig_pid: stop_raw(trig_pid, "abc", finish_reason="end_turn"), ctrl_pid: stop_raw(ctrl_pid, "abcdef")}
    reduced = reduce_single_stop_group(trig, ctrl, openai_compat_models, raw_dishonest, stop_token="STOP")
    if reduced["truncation_verdict"] != "stop-honored" or reduced["finish_reason_honest"] != "dishonest":
        problems += 1
        print(f"FAIL reduce_single_stop_group(anthropic dishonest): got {reduced['truncation_verdict']!r}/{reduced['finish_reason_honest']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: non-anthropic wire family — ALWAYS
    #     ambiguous, even on a clean stop-honored verdict (the plan's own
    #     must_haves truth: no non-anthropic row is ever "honest") ---
    cases += 1
    trig2, ctrl2 = make_stop_entries("m2")
    trig2_pid = compute_behavioral_probe_id(trig2, openai_compat_models)
    ctrl2_pid = compute_behavioral_probe_id(ctrl2, openai_compat_models)
    raw2 = {
        trig2_pid: stop_raw(trig2_pid, "abc", finish_reason="stop", family="openai_compat"),
        ctrl2_pid: stop_raw(ctrl2_pid, "abcdef", family="openai_compat"),
    }
    reduced = reduce_single_stop_group(trig2, ctrl2, openai_compat_models, raw2, stop_token="STOP")
    if reduced["truncation_verdict"] != "stop-honored" or reduced["finish_reason_honest"] != "ambiguous":
        problems += 1
        print(f"FAIL reduce_single_stop_group(non-anthropic ambiguous): got {reduced['truncation_verdict']!r}/{reduced['finish_reason_honest']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: stop-ignored (token present in text) ---
    cases += 1
    raw_ignored = {
        trig2_pid: stop_raw(trig2_pid, "abc STOP def", finish_reason="stop", family="openai_compat"),
        ctrl2_pid: stop_raw(ctrl2_pid, "abcdef", family="openai_compat"),
    }
    reduced = reduce_single_stop_group(trig2, ctrl2, openai_compat_models, raw_ignored, stop_token="STOP")
    if reduced["truncation_verdict"] != "stop-ignored":
        problems += 1
        print(f"FAIL reduce_single_stop_group(token present): expected stop-ignored, got {reduced['truncation_verdict']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: stop-ignored (equal-length texts, no token) ---
    cases += 1
    raw_equal = {
        trig2_pid: stop_raw(trig2_pid, "same", finish_reason="stop", family="openai_compat"),
        ctrl2_pid: stop_raw(ctrl2_pid, "same", family="openai_compat"),
    }
    reduced = reduce_single_stop_group(trig2, ctrl2, openai_compat_models, raw_equal, stop_token="STOP")
    if reduced["truncation_verdict"] != "stop-ignored":
        problems += 1
        print(f"FAIL reduce_single_stop_group(equal length): expected stop-ignored, got {reduced['truncation_verdict']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: fired-but-empty text on EITHER call is
    #     inconclusive (a genuine finding, e.g. glm-5.3's own reasoning-
    #     exhaustion record) — NOT the same as a missing record below ---
    cases += 1
    raw_empty = {
        trig2_pid: stop_raw(trig2_pid, "", finish_reason="stop", family="openai_compat"),
        ctrl2_pid: stop_raw(ctrl2_pid, "abcdef", family="openai_compat"),
    }
    reduced = reduce_single_stop_group(trig2, ctrl2, openai_compat_models, raw_empty, stop_token="STOP")
    if reduced["truncation_verdict"] != "inconclusive" or reduced["finish_reason_honest"] != "ambiguous":
        problems += 1
        print(f"FAIL reduce_single_stop_group(empty text): got {reduced['truncation_verdict']!r}/{reduced['finish_reason_honest']!r}", file=sys.stderr)

    # --- reduce_single_stop_group: a MISSING control call (no raw record
    #     on disk at all) fails loud rather than producing a verdict from
    #     one call ---
    cases += 1
    raw_missing_control = {trig2_pid: stop_raw(trig2_pid, "abc", finish_reason="stop", family="openai_compat")}
    try:
        reduce_single_stop_group(trig2, ctrl2, openai_compat_models, raw_missing_control, stop_token="STOP")
        problems += 1
        print("FAIL reduce_single_stop_group: a missing control record was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL reduce_single_stop_group(missing control): expected exit 2, got {e.code}", file=sys.stderr)

    # --- reduce_single_candidates_group: honored (returned == requested) ---
    cases += 1
    n_entry = {"model": "m2", "param": "n", "value": 2, "mode": "default", "prompt": "x", "max_tokens": 16, "extra_params": {"n": 2}}
    n_pid = compute_behavioral_probe_id(n_entry, openai_compat_models)
    n_raw = {n_pid: {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "a"}}, {"message": {"content": "b"}}]}}],
        "usage": {"output_tokens": 5},
    }}
    reduced = reduce_single_candidates_group(n_entry, openai_compat_models, n_raw, requested_n=2)
    if reduced["returned_count"] != 2 or reduced["state"] != "accepted-honored":
        problems += 1
        print(f"FAIL reduce_single_candidates_group(honored): got count={reduced['returned_count']} state={reduced['state']!r}", file=sys.stderr)

    # --- reduce_single_candidates_group: ignored (only 1 returned) ---
    cases += 1
    n_raw_ignored = {n_pid: {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "a"}}]}}],
        "usage": {"output_tokens": 5},
    }}
    reduced = reduce_single_candidates_group(n_entry, openai_compat_models, n_raw_ignored, requested_n=2)
    if reduced["returned_count"] != 1 or reduced["state"] != "accepted-ignored":
        problems += 1
        print(f"FAIL reduce_single_candidates_group(ignored): got count={reduced['returned_count']} state={reduced['state']!r}", file=sys.stderr)

    # --- reduce_single_candidates_group: rejected (HTTP 400) — an honest
    #     integer returned_count (0), never None, and state='rejected'
    #     rather than the detector's own 'accepted-unverified' fallback ---
    cases += 1
    n_raw_rejected = {n_pid: {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 400, "response_body_raw": {"error": {"message": "invalid n"}}}],
        "usage": {},
    }}
    reduced = reduce_single_candidates_group(n_entry, openai_compat_models, n_raw_rejected, requested_n=2)
    if reduced["returned_count"] != 0 or reduced["state"] != "rejected":
        problems += 1
        print(f"FAIL reduce_single_candidates_group(rejected): got count={reduced['returned_count']} state={reduced['state']!r}", file=sys.stderr)

    # --- build_rows: design=single-candidates with a non-integer `value`
    #     fails loud (the group_key's own value must be int-parseable) ---
    cases += 1
    bad_n_probes = [dict(n_entry, value="not-an-int")]
    bad_n_expectation = [{
        "model": "m2", "param": "n", "value": "not-an-int", "mode": "default",
        "requirement": "BHV-04", "design": "single-candidates",
        "expected": "x", "expected_source": "docs-claims:temperature/anthropic",
    }]
    try:
        build_rows(bad_n_probes, bad_n_expectation, [], openai_compat_models, {}, docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text)
        problems += 1
        print("FAIL build_rows: a non-integer single-candidates value was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(non-integer n value): expected exit 2, got {e.code}", file=sys.stderr)

    # --- reduce_single_logprobs_group: present (real per-token content,
    #     each entry carrying the requested alternative count) ---
    cases += 1
    lp_entry = {"model": "m2", "param": "logprobs-reverify", "value": "combined", "mode": "default", "prompt": "x", "max_tokens": 16, "extra_params": {"logprobs": True, "top_logprobs": 3}}
    lp_pid = compute_behavioral_probe_id(lp_entry, openai_compat_models)
    lp_raw_present = {lp_pid: {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "a"}, "logprobs": {"content": [
            {"token": "a", "top_logprobs": [{"token": "a"}, {"token": "b"}, {"token": "c"}]},
        ]}}]}}],
        "usage": {"output_tokens": 5},
    }}
    reduced = reduce_single_logprobs_group(lp_entry, openai_compat_models, lp_raw_present, requested_top_logprobs=3)
    if not reduced["logprobs_present"] or reduced["logprobs_token_entries"] != 1 or not reduced["logprobs_alternatives_honored"]:
        problems += 1
        print(f"FAIL reduce_single_logprobs_group(present): got {reduced!r}", file=sys.stderr)

    # --- reduce_single_logprobs_group: empty payload (200, but no
    #     per-token content — the accepted-but-silently-ignored hazard) ---
    cases += 1
    lp_raw_empty = {lp_pid: {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 200, "response_body_raw": {"choices": [{"message": {"content": "a"}, "logprobs": {"content": []}}]}}],
        "usage": {"output_tokens": 5},
    }}
    reduced = reduce_single_logprobs_group(lp_entry, openai_compat_models, lp_raw_empty, requested_top_logprobs=3)
    if reduced["logprobs_present"] or reduced["logprobs_token_entries"] != 0 or reduced["logprobs_alternatives_honored"]:
        problems += 1
        print(f"FAIL reduce_single_logprobs_group(empty payload): got {reduced!r}", file=sys.stderr)

    # ---------------------------------------------------------------------
    # 12-05's `tier-audit` design — path-aware response lookup, the five-
    # valued `echo_relation` vocabulary, the Anthropic dual-lookup asymmetry
    # fields, and `cited_cells:` support (fired vs. audited-from-evidence).
    # ---------------------------------------------------------------------

    # --- _get_path_value / _tier_presence: nested-path hit ---
    cases += 1
    if _get_path_value({"usage": {"service_tier": "priority"}}, ("usage", "service_tier")) != "priority":
        problems += 1
        print("FAIL _get_path_value: nested-path hit did not return the value", file=sys.stderr)

    # --- _get_path_value / _tier_presence: top-level hit ---
    cases += 1
    if _get_path_value({"service_tier": "auto"}, ("service_tier",)) != "auto":
        problems += 1
        print("FAIL _get_path_value: top-level hit did not return the value", file=sys.stderr)

    # --- _get_path_value / _tier_presence: absent path -> the distinct
    #     _TIER_MISSING sentinel, never confused with a present None ---
    cases += 1
    missing = _get_path_value({"usage": {}}, ("usage", "service_tier"))
    if missing is not _TIER_MISSING or _tier_presence(missing) != "absent":
        problems += 1
        print(f"FAIL _get_path_value/_tier_presence(absent path): got {missing!r}", file=sys.stderr)

    # --- _get_path_value / _tier_presence: present-but-null, distinct from
    #     absent (the plan's own must_haves truth) ---
    cases += 1
    null_valued = _get_path_value({"usage": {"service_tier": None}}, ("usage", "service_tier"))
    if null_valued is not None or _tier_presence(null_valued) != "null-valued":
        problems += 1
        print(f"FAIL _get_path_value/_tier_presence(null-valued): got {null_valued!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="echoed" (response value
    #     equals the request value) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"service_tier": "auto"}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value="auto",
    )
    if core["echo_relation"] != "echoed" or core["response_present"] != "present":
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(echoed): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="translated" (a DIFFERENT
    #     value came back — OpenAI's own documented fast->priority rename) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"service_tier": "priority"}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value="fast",
    )
    if core["echo_relation"] != "translated":
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(translated): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="dropped" (the request
    #     carried a value, no response field exists to confirm it) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value="auto",
    )
    if core["echo_relation"] != "dropped" or core["response_present"] != "absent":
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(dropped): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="absent" (neither side
    #     carried a value — the omission-baseline cell at an undocumented
    #     vendor whose docs are borne out) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value=None,
    )
    if core["echo_relation"] != "absent" or core["note"] is not None:
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(absent): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: an omission-baseline cell whose response
    #     DOES carry a resolved value -- a finding, carries a note (the
    #     plan's own must_haves truth: "none of them records a value ...
    #     without a note explaining that ... is itself a finding") ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"service_tier": "standard"}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value=None,
    )
    if core["echo_relation"] != "translated" or not core["note"]:
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(omitted-but-present): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="rejected", WITH the field
    #     named in the error body (D-15's own trap question) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"error": {"message": "service_tier: invalid value 'standard'"}},
        status=400, terminal="verdict", wire_family="anthropic_messages",
        request_field="service_tier", request_value="standard",
    )
    if core["echo_relation"] != "rejected" or core["rejection_names_field"] is not True:
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(rejected, field named): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: echo_relation="rejected", WITHOUT the
    #     field named in the error body ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"error": {"message": "invalid request"}},
        status=400, terminal="verdict", wire_family="anthropic_messages",
        request_field="service_tier", request_value="standard",
    )
    if core["echo_relation"] != "rejected" or core["rejection_names_field"] is not False:
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(rejected, field not named): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: the Anthropic dual lookup — a value
    #     present at the NESTED usage.service_tier location and absent at
    #     the response TOP LEVEL is the documented asymmetry CONFIRMED,
    #     recorded as two separate fields (never collapsed into one) ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"usage": {"service_tier": "priority"}}, status=200, terminal="verdict",
        wire_family="anthropic_messages", request_field="service_tier", request_value="auto",
    )
    if (
        core["response_present"] != "present" or core["response_field_path"] != "usage.service_tier"
        or core["response_top_level_present"] != "absent"
    ):
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(anthropic asymmetry): got {core!r}", file=sys.stderr)

    # --- _reduce_tier_audit_core: a non-anthropic wire family carries NO
    #     top-level dual-lookup fields at all — the plan's own must_haves
    #     truth scopes the dual lookup to Anthropic specifically ---
    cases += 1
    core = _reduce_tier_audit_core(
        response_body={"service_tier": "auto"}, status=200, terminal="verdict",
        wire_family="openai_compat", request_field="service_tier", request_value="auto",
    )
    if core["response_top_level_present"] is not None or core["response_top_level_value"] is not None:
        problems += 1
        print(f"FAIL _reduce_tier_audit_core(non-anthropic, no dual lookup): got {core!r}", file=sys.stderr)

    # --- reduce_tier_audit_cited: a resolving probe_id reads the raw
    #     record directly, no `probes:` entry required at all ---
    cases += 1
    cited_models = {"m7": {"wire_family": "openai_compat", "vendor": "openai", "api_model_id": "m7-api", "_order": 0}}
    cited_raw = {"m7--service-tier--default--default--aaaa": {
        "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
        "attempts": [{"status": 200, "response_body_raw": {"service_tier": "default"}}],
        "usage": {},
    }}
    cited_reduced = reduce_tier_audit_cited(
        "m7--service-tier--default--default--aaaa", "openai_compat", cited_raw,
        request_field="service_tier", request_value="default",
    )
    if (
        cited_reduced["echo_relation"] != "echoed" or not cited_reduced["audited_from_existing_evidence"]
        or cited_reduced["cited_probe_id"] != "m7--service-tier--default--default--aaaa"
    ):
        problems += 1
        print(f"FAIL reduce_tier_audit_cited(resolving): got {cited_reduced!r}", file=sys.stderr)

    # --- reduce_tier_audit_cited: a NON-resolving probe_id fails loud —
    #     an audit row with no readable evidence behind it is worse than an
    #     absent row (the plan's own must_haves truth) ---
    cases += 1
    try:
        reduce_tier_audit_cited(
            "does-not-exist--service-tier--default--default--zzzz", "openai_compat", cited_raw,
            request_field="service_tier", request_value="default",
        )
        problems += 1
        print("FAIL reduce_tier_audit_cited: a non-resolving probe_id was not rejected", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL reduce_tier_audit_cited(non-resolving): expected exit 2, got {e.code}", file=sys.stderr)

    # --- build_rows: design=tier-audit end to end — a fired entry PLUS a
    #     cited_cells entry citing a probe_id with no matching `probes:`
    #     entry at all, both landing in the same requirement section ---
    cases += 1
    tier_models = {"m8": {"wire_family": "openai_compat", "vendor": "openai", "api_model_id": "m8-api", "_order": 0}}
    tier_probes = [{
        "model": "m8", "param": "service-tier-audit", "value": "scale", "mode": "default",
        "prompt": "x", "max_tokens": 80, "extra_params": {"service_tier": "scale"},
    }]
    tier_expectations = [{
        "model": "m8", "param": "service-tier-audit", "value": "scale", "mode": "default",
        "requirement": "BHV-06", "design": "tier-audit",
        "request_field": "service_tier", "request_value": "scale",
        "expected": "x", "expected_source": "docs-claims:temperature/anthropic",
    }]
    tier_pid = compute_behavioral_probe_id(tier_probes[0], tier_models)
    tier_raw = {
        tier_pid: {
            "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
            "attempts": [{"status": 200, "response_body_raw": {"service_tier": "scale"}}],
            "usage": {},
        },
        "m8--service-tier--auto--default--bbbb": {
            "terminal": "verdict", "recorded_at": "2026-09-03T00:00:00Z",
            "attempts": [{"status": 200, "response_body_raw": {"service_tier": "auto"}}],
            "usage": {},
        },
    }
    tier_cited_cells = [{
        "model": "m8", "param": "service-tier-audit", "value": "auto", "mode": "default",
        "requirement": "BHV-06", "design": "tier-audit",
        "request_field": "service_tier", "request_value": "auto",
        "expected": "x", "expected_source": "docs-claims:temperature/anthropic",
        "cited_probe_id": "m8--service-tier--auto--default--bbbb",
    }]
    try:
        tier_cells, _tier_skips, _tier_ev = build_rows(
            tier_probes, tier_expectations, [], tier_models, tier_raw,
            cited_cells=tier_cited_cells,
            docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
        )
        if len(tier_cells) != 2:
            problems += 1
            print(f"FAIL build_rows(tier-audit e2e): expected 2 cells (1 fired + 1 cited), got {len(tier_cells)}", file=sys.stderr)
        fired_row = next((c for c in tier_cells if not c["audited_from_existing_evidence"]), None)
        cited_row = next((c for c in tier_cells if c["audited_from_existing_evidence"]), None)
        if fired_row is None or cited_row is None:
            problems += 1
            print(f"FAIL build_rows(tier-audit e2e): expected one fired and one audited row, got {tier_cells!r}", file=sys.stderr)
        elif cited_row["cited_probe_id"] != "m8--service-tier--auto--default--bbbb":
            problems += 1
            print(f"FAIL build_rows(tier-audit e2e): cited row's cited_probe_id wrong, got {cited_row!r}", file=sys.stderr)
    except SystemExit as e:
        problems += 1
        print(f"FAIL build_rows(tier-audit e2e): unexpected SystemExit({e.code})", file=sys.stderr)

    # --- build_rows: a cited_cells entry citing a probe_id with NO raw
    #     record at all fails loud, end to end through build_rows() too ---
    cases += 1
    bad_cited_cells = [dict(tier_cited_cells[0], cited_probe_id="does-not-exist--x--y--default--zzzz")]
    try:
        build_rows(
            tier_probes, tier_expectations, [], tier_models, tier_raw,
            cited_cells=bad_cited_cells,
            docs_claims_index=docs_idx, contract_probe_ids=contract_ids, prereg_text=prereg_text,
        )
        problems += 1
        print("FAIL build_rows(tier-audit, non-resolving cited_probe_id): expected SystemExit(2), got a return", file=sys.stderr)
    except SystemExit as e:
        if e.code != 2:
            problems += 1
            print(f"FAIL build_rows(tier-audit, non-resolving cited_probe_id): expected exit 2, got {e.code}", file=sys.stderr)

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
