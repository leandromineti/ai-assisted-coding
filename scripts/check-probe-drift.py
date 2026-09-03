#!/usr/bin/env python3
"""scripts/check-probe-drift.py — the fail-closed, two-way drift checker for
ADR-0050's promoted `wire-behavior` keys (MTX-03, D-08). Confronts every
OBSERVED cell in `tools/1-models/*.md`'s `model_features` block against the
classified evidence it cites, in both directions: FORWARD — every promoted
key's cell, for every probed model, is parsed against ADR-0050's cell-value
grammar and its head is compared to the value re-derived from
`probes/classified/behavioral.yaml` / `probes/classified/contract-sweep.yaml`;
BACKWARD — every (promoted key, probed model) pair is confirmed to carry a
cell at all, a missing one being its own finding. Every citation token inside
a cell (`cell_id:`.../`probe_id:`...) must also resolve against the same
classified evidence. Sibling of `probes/check-docs-claims.py`: identical
`_fail()`/`_load_yaml()`/`--check`/`--selftest`/exit-code contract.

    python3 scripts/check-probe-drift.py --check
    python3 scripts/check-probe-drift.py --selftest

Exit codes: 0 clean, 1 findings recorded (--check/--selftest only), 2 bad
invocation (no flag, both flags, or a required input file missing/malformed).

Never re-derives a rate or verdict from raw evidence records — `load_classified()`
is imported by path from `scripts/build-behavioral-matrix.py` and
`scripts/build-probe-matrix.py` (both already reduce the raw run records into
the classified YAML this script's only inputs are), so the checker and the
matrices this evidence also renders into can never independently drift apart.
This script reads no path outside `docs/feature-taxonomy.yaml`,
`probes/harness/models.yaml`, `tools/1-models/*.md`, and the two classified
files those two imported readers already own. A finding here is fixed in the
report cell or in the classified evidence itself — never by loosening this
script's grammar or narrowing its domain.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
REGISTRY_PATH = REPO_ROOT / "docs" / "feature-taxonomy.yaml"
MODELS_PATH = REPO_ROOT / "probes" / "harness" / "models.yaml"
TOOLS_DIR = REPO_ROOT / "tools" / "1-models"

# scripts/build-behavioral-matrix.py's and scripts/build-probe-matrix.py's own
# filenames are not importable with a bare `import` statement (a hyphen is not
# a valid identifier character) — loaded here via importlib.util from an
# explicit file path, exactly the pattern scripts/classify-behavioral.py
# already uses to pull symbols out of scripts/classify-probes.py. Their own
# `load_classified()` is the single reduced-evidence reader for each
# classified file; re-implementing a YAML loader here would let this checker
# silently drift from the same generators that render comparisons/behavioral.md
# and comparisons/probes.md from the identical files.
_bbm_spec = importlib.util.spec_from_file_location(
    "build_behavioral_matrix", SCRIPTS_DIR / "build-behavioral-matrix.py"
)
build_behavioral_matrix = importlib.util.module_from_spec(_bbm_spec)
_bbm_spec.loader.exec_module(build_behavioral_matrix)

_bpm_spec = importlib.util.spec_from_file_location(
    "build_probe_matrix", SCRIPTS_DIR / "build-probe-matrix.py"
)
build_probe_matrix = importlib.util.module_from_spec(_bpm_spec)
_bpm_spec.loader.exec_module(build_probe_matrix)


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path this
    module shares with probes/check-docs-claims.py, runner.py, and every
    other loader/generator in this repo."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _load_yaml(path: Path, required_key: str) -> dict:
    """Fail-loud YAML loader — never a silent default on a missing file,
    malformed YAML, or a missing top-level key (copied verbatim from
    probes/check-docs-claims.py / scripts/build-probe-matrix.py)."""
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


# --- ADR-0050's cell-value grammar (§ Cell-value grammar) ------------------
#
#   <head> — OBSERVED <YYYY-MM-DD>: <context>, <citation>[, <citation> ...],
#   promoted ADR-<NNNN>.
#
# Three head forms: a rate ("N/M unit phrase" with an optional trailing
# parenthesised verdict token), a bare verdict token from the key's own
# closed vocabulary, or the not-applicable form ("n/a (<reason>)", <reason>
# one of exactly two closed phrases). Citations are backtick-delimited
# `cell_id:`id`` / `probe_id:`id`` tokens — several `stop`-param probe_ids
# literally embed a JSON array (`["the"]`), so citations are found by
# scanning for these tokens rather than by splitting the tail on commas,
# which legitimately also appear inside prose context.
CELL_RE = re.compile(
    r"^(?P<head>.+?) — OBSERVED (?P<date>\d{4}-\d{2}-\d{2}): (?P<tail>.+), "
    r"promoted ADR-(?P<adr>\d+)\.$"
)
RATE_HEAD_RE = re.compile(
    r"^(?P<num>\d+)/(?P<den>\d+) (?P<unit>[^()]+?)(?: \((?P<verdict>[a-z][a-z-]*)\))?$"
)
NA_HEAD_RE = re.compile(
    r"^n/a \((?P<reason>no request-side field|parameter rejected at the contract sweep)\)$"
)
VERDICT_HEAD_RE = re.compile(r"^[a-z][a-z-]*$")
CITATION_RE = re.compile(r"(cell_id|probe_id):`([^`]+)`")


def parse_cell(text: str) -> dict | None:
    """Parse one OBSERVED cell string against ADR-0050's grammar. Returns a
    dict with `head` (kind + fields), `date`, `citations` (list of
    (kind, id) pairs), and `adr`; returns None for anything that does not
    match — an unparseable cell is always a loud failure at the call site,
    never silently skipped."""
    m = CELL_RE.match(text)
    if not m:
        return None
    head = m.group("head")
    tail = m.group("tail")
    citations = CITATION_RE.findall(tail)
    if not citations:
        return None

    rate_m = RATE_HEAD_RE.match(head)
    na_m = NA_HEAD_RE.match(head)
    if rate_m:
        parsed_head = {
            "kind": "rate",
            "num": int(rate_m.group("num")),
            "den": int(rate_m.group("den")),
            "unit": rate_m.group("unit").strip(),
            "verdict": rate_m.group("verdict"),
        }
    elif na_m:
        parsed_head = {"kind": "na", "reason": na_m.group("reason")}
    elif VERDICT_HEAD_RE.match(head):
        parsed_head = {"kind": "verdict", "token": head}
    else:
        return None

    return {
        "head": parsed_head,
        "date": m.group("date"),
        "citations": citations,
        "adr": m.group("adr"),
        "raw": text,
    }


def compare_heads(parsed_head: dict, expected: dict) -> list[str]:
    """Compare a parsed cell's head against the re-derived expected head.
    Returns every violated rule name (never returns at the first — a cell
    breaking two rules names both)."""
    findings: list[str] = []
    pk, ek = parsed_head["kind"], expected["kind"]

    if ek == "na":
        if pk != "na":
            findings.append("mismatch-head-kind:expected-na")
        elif parsed_head["reason"] != expected["reason"]:
            findings.append("mismatch-na-reason")
    elif ek == "rate":
        if pk != "rate":
            findings.append("mismatch-head-kind:expected-rate")
        else:
            if (parsed_head["num"], parsed_head["den"]) != (expected["num"], expected["den"]):
                findings.append("mismatch-rate")
            # A zero rate that varied and a zero rate that produced no signal
            # are not interchangeable (D-08) — compared even when the rate
            # itself matches.
            if parsed_head.get("verdict") != expected.get("verdict"):
                findings.append("mismatch-verdict")
    elif ek == "verdict":
        if pk != "verdict":
            findings.append("mismatch-head-kind:expected-verdict")
        elif parsed_head["token"] != expected["token"]:
            findings.append("mismatch-verdict")

    return findings


# --- Registry / model domain, derived at runtime (never hardcoded) --------


def promoted_key_ids(registry_path: Path = REGISTRY_PATH) -> list[str]:
    """Every docs/feature-taxonomy.yaml `features:` entry whose `group` is
    `wire-behavior` — the checker's promoted-key domain. Recomputed from the
    registry every run, so a registry carrying zero wire-behavior keys makes
    the domain empty (and --check reports that explicitly, never silently),
    and a group rename in the registry changes what this returns without any
    edit to this script."""
    doc = _load_yaml(registry_path, "features")
    return [e["id"] for e in doc.get("features", []) if e.get("group") == "wire-behavior"]


def probed_model_slugs(models_path: Path = MODELS_PATH) -> list[str]:
    """The 12 probed model slugs, read from the harness's own model registry
    — the checker's model domain. A report outside this set (qwen3-coder-next,
    never probed) is never examined and never produces a finding."""
    doc = _load_yaml(models_path, "models")
    return [m["slug"] for m in doc["models"]]


def read_frontmatter(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


# --- Classified-evidence indices -------------------------------------------


def index_behavioral(cells: list[dict]) -> tuple[dict, set[str]]:
    by_model_param: dict[tuple[str, str], list[dict]] = {}
    ids: set[str] = set()
    for c in cells:
        by_model_param.setdefault((c["model"], c["param"]), []).append(c)
        ids.add(c["cell_id"])
        for pid in c.get("probe_ids") or []:
            ids.add(pid)
    return by_model_param, ids


def index_contract(cells: list[dict]) -> tuple[dict, set[str]]:
    by_model_param_mode: dict[tuple[str, str, str], list[dict]] = {}
    ids: set[str] = set()
    for c in cells:
        by_model_param_mode.setdefault((c["model"], c["param"], c["mode"]), []).append(c)
        if c.get("probe_id"):
            ids.add(c["probe_id"])
    return by_model_param_mode, ids


# --- Per-key re-derivation rules, all six keys ADR-0050 names --------------
#
# Only `stop_sequence_honesty` has registry entries and report cells as of
# this plan; the other five land in plans 13-03/13-04. Their rules are
# written here now so the checker stays green through that expansion without
# a further edit to this script (Task 3's own acceptance bar) — the
# promoted-key domain above naturally means only the keys the registry
# actually carries are ever compared against a report.
#
# Two precedence rules, both from methodology rule 1a's evidence-grade
# ordering:
#   (1) Where a model/key pair has BOTH a contract result and a behavioral
#       result, the BEHAVIORAL result governs — `qwen3.8-flash`'s
#       `logprobs_delivery` cell is the motivating case: its Phase-11
#       contract classification (`accepted-ignored`) was superseded by a
#       later, non-masking-budget behavioral reverify (`accepted-honored`).
#       An earlier reading taken at a budget that masked the real answer
#       must never win over the later, higher-grade one.
#   (2) Where a model/key pair's ONLY evidence is a contract REJECTION
#       rather than a behavioral rate (`gemini-3-1-pro`'s
#       `multi_candidate_delivery` cell), the derived head is that
#       rejection's own verdict, never a not-applicable head — a parameter
#       the maker rejects by name is a measured fact, not an absent one.


def derive_seed_determinism(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    cells = beh_idx.get((model, "seed"))
    if cells:
        c = cells[0]
        num, den = c["rate"].split("/")
        return {"kind": "rate", "num": int(num), "den": int(den), "verdict": c.get("verdict")}
    # No behavioral cell AND no contract cell at all for this model's `seed`
    # param means the vendor's API exposes no such request-side field.
    if not cs_idx.get((model, "seed", "default")):
        return {"kind": "na", "reason": "no request-side field"}
    return None


def derive_sampling_repeatability(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    real = None
    for c in beh_idx.get((model, "temperature"), []):
        if str(c.get("value")) == "0":
            real = c
            break
    if real:
        num, den = real["rate"].split("/")
        return {"kind": "rate", "num": int(num), "den": int(den), "verdict": real.get("verdict")}
    for c in beh_idx.get((model, "default-config-repeatability"), []):
        num, den = c["rate"].split("/")
        return {"kind": "rate", "num": int(num), "den": int(den), "verdict": c.get("verdict")}
    return None


def derive_stop_sequence_honesty(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    cells = beh_idx.get((model, "stop-truncation"))
    if cells:
        c = cells[0]
        token = "inconclusive" if c.get("truncation_verdict") == "inconclusive" else c.get("finish_reason_honest")
        return {"kind": "verdict", "token": token}
    for c in cs_idx.get((model, "stop", "default"), []):
        if c.get("state") == "rejected":
            return {"kind": "na", "reason": "parameter rejected at the contract sweep"}
    return None


def derive_multi_candidate_delivery(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    cells = beh_idx.get((model, "n"))
    if cells:
        return {"kind": "verdict", "token": cells[0].get("state")}
    # Contract-only rejection (e.g. gemini-3-1-pro's candidateCount) is a
    # real verdict, never a not-applicable substitute — precedence rule (2).
    for param in ("n", "gemini-candidate-count"):
        for c in cs_idx.get((model, param, "default"), []):
            if c.get("state") not in (None, "skipped"):
                return {"kind": "verdict", "token": c["state"]}
    if not cs_idx.get((model, "n", "default")) and not cs_idx.get((model, "gemini-candidate-count", "default")):
        return {"kind": "na", "reason": "no request-side field"}
    return None


def derive_logprobs_delivery(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    cells = beh_idx.get((model, "logprobs-reverify"))
    if cells:
        return {"kind": "verdict", "token": cells[0].get("state")}
    for c in cs_idx.get((model, "logprobs", "default"), []):
        if c.get("state") not in (None, "skipped"):
            return {"kind": "verdict", "token": c["state"]}
    if not cs_idx.get((model, "logprobs", "default")):
        return {"kind": "na", "reason": "no request-side field"}
    return None


def derive_service_tier_contract(model: str, beh_idx: dict, cs_idx: dict) -> dict | None:
    for c in cs_idx.get((model, "service-tier", "default"), []):
        if c.get("state"):
            return {"kind": "verdict", "token": c["state"]}
    return None


DERIVE_FUNCS = {
    "seed_determinism": derive_seed_determinism,
    "sampling_repeatability": derive_sampling_repeatability,
    "stop_sequence_honesty": derive_stop_sequence_honesty,
    "multi_candidate_delivery": derive_multi_candidate_delivery,
    "logprobs_delivery": derive_logprobs_delivery,
    "service_tier_contract": derive_service_tier_contract,
}


# --- The two-way check ------------------------------------------------------


def run_check(
    *,
    tools_dir: Path = TOOLS_DIR,
    registry_path: Path = REGISTRY_PATH,
    models_path: Path = MODELS_PATH,
    behavioral_cells: list[dict] | None = None,
    contract_cells: list[dict] | None = None,
) -> tuple[list[dict], int, int, int]:
    """Runs the full forward+backward check. Returns (findings, cells_examined,
    mismatched_cells, missing_cells). `behavioral_cells`/`contract_cells` are
    injectable for --selftest fixtures; a real run loads them via the
    imported `load_classified()` readers."""
    keys = promoted_key_ids(registry_path)
    models = probed_model_slugs(models_path)

    if behavioral_cells is None:
        behavioral_cells = build_behavioral_matrix.load_classified()["cells"]
    if contract_cells is None:
        contract_cells = build_probe_matrix.load_classified()["cells"]

    beh_idx, beh_ids = index_behavioral(behavioral_cells)
    cs_idx, cs_ids = index_contract(contract_cells)
    all_ids = beh_ids | cs_ids

    findings: list[dict] = []
    cells_examined = 0
    mismatched_cells = 0
    missing_cells = 0

    for key in keys:
        derive = DERIVE_FUNCS.get(key)
        for model in models:
            fm = read_frontmatter(tools_dir / f"{model}.md")
            value = ((fm or {}).get("model_features") or {}).get(key)
            identifier = f"{key}:{model}"

            if value is None:
                missing_cells += 1
                findings.append({"scope": "coverage", "identifier": identifier, "rule": "missing-cell"})
                continue

            cells_examined += 1
            has_finding = False

            parsed = parse_cell(value)
            if parsed is None:
                findings.append({"scope": "cell", "identifier": identifier, "rule": "unparseable-cell"})
                has_finding = True
            else:
                for kind, cid in parsed["citations"]:
                    if cid not in all_ids:
                        findings.append({
                            "scope": "citation", "identifier": identifier,
                            "rule": f"dangling-citation:{kind}:{cid}",
                        })
                        has_finding = True

                if derive is not None:
                    expected = derive(model, beh_idx, cs_idx)
                    if expected is None:
                        findings.append({"scope": "cell", "identifier": identifier, "rule": "no-derivable-evidence"})
                        has_finding = True
                    else:
                        for rule in compare_heads(parsed["head"], expected):
                            findings.append({"scope": "cell", "identifier": identifier, "rule": rule})
                            has_finding = True

            if has_finding:
                mismatched_cells += 1

    findings.sort(key=lambda f: (f["scope"], f["identifier"], f["rule"]))
    return findings, cells_examined, mismatched_cells, missing_cells


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        print(f"ERROR {f['scope']}:{f['identifier']} rule={f['rule']}", file=sys.stderr)


# --- --selftest: one deliberately-broken fixture per finding class --------


def selftest() -> tuple[int, int]:
    """Runs embedded, deliberately-broken fixtures, one per finding class this
    script's behavior contract names. Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    def check(label: str, condition: bool) -> None:
        nonlocal problems
        if not condition:
            problems += 1
            print(f"FAIL: {label}", file=sys.stderr)

    # --- parse_cell: a clean rate head with a verdict parses ---
    cases += 1
    p = parse_cell(
        "0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: five same-seed calls, "
        "cell_id:`m--seed--42--default`, promoted ADR-0050."
    )
    check("a clean rate-head cell failed to parse", p is not None and p["head"]["kind"] == "rate"
          and p["head"]["num"] == 0 and p["head"]["den"] == 5 and p["head"]["verdict"] == "varies")

    # --- parse_cell: a clean bare-verdict head parses ---
    cases += 1
    p = parse_cell(
        "honest — OBSERVED 2026-09-03: context, cell_id:`m--stop-truncation--triggering--default`, "
        "promoted ADR-0050."
    )
    check("a clean bare-verdict cell failed to parse", p is not None and p["head"] == {"kind": "verdict", "token": "honest"})

    # --- parse_cell: a clean not-applicable head with a bracket-bearing
    #     probe_id (the stop-param shape) parses ---
    cases += 1
    p = parse_cell(
        'n/a (parameter rejected at the contract sweep) — OBSERVED 2026-09-03: stop returns HTTP 400, '
        'probe_id:`m--stop--["the"]--default--deadbeef`, promoted ADR-0050.'
    )
    check(
        "a not-applicable cell with a bracket-bearing probe_id failed to parse",
        p is not None and p["head"]["kind"] == "na" and p["citations"] == [("probe_id", 'm--stop--["the"]--default--deadbeef')],
    )

    # --- parse_cell: a cell with no OBSERVED marker does not parse ---
    cases += 1
    p = parse_cell("honest: context, cell_id:`x`, promoted ADR-0050.")
    check("a cell missing the OBSERVED marker parsed anyway", p is None)

    # --- parse_cell: a cell with no citation does not parse (unparseable,
    #     never skipped) ---
    cases += 1
    p = parse_cell("honest — OBSERVED 2026-09-03: context with no citation at all, promoted ADR-0050.")
    check("a cell with no citation token parsed anyway", p is None)

    # --- parse_cell: a cell with no trailing `promoted ADR-` clause does not
    #     parse ---
    cases += 1
    p = parse_cell("honest — OBSERVED 2026-09-03: context, cell_id:`x`.")
    check("a cell missing the trailing promoted-ADR clause parsed anyway", p is None)

    # --- compare_heads: rate numerator/denominator differing from evidence
    #     produces exactly one mismatch-rate finding ---
    cases += 1
    findings = compare_heads({"kind": "rate", "num": 1, "den": 5, "verdict": "varies"}, {"kind": "rate", "num": 0, "den": 5, "verdict": "varies"})
    check("a differing rate numerator did not fire mismatch-rate", findings == ["mismatch-rate"])

    # --- compare_heads: verdict token differing from evidence fires
    #     mismatch-verdict ---
    cases += 1
    findings = compare_heads({"kind": "verdict", "token": "ambiguous"}, {"kind": "verdict", "token": "honest"})
    check("a differing verdict token did not fire mismatch-verdict", findings == ["mismatch-verdict"])

    # --- compare_heads: matching rate integers but a differing parenthesised
    #     verdict token fires mismatch-verdict even though the rate matches —
    #     a zero rate that varied and a zero rate with no signal are not
    #     interchangeable ---
    cases += 1
    findings = compare_heads(
        {"kind": "rate", "num": 0, "den": 5, "verdict": "no-signal"},
        {"kind": "rate", "num": 0, "den": 5, "verdict": "varies"},
    )
    check("a matching rate with a differing verdict token did not fire mismatch-verdict", findings == ["mismatch-verdict"])

    # --- compare_heads: a not-applicable cell for a model with real evidence
    #     (evidence expects rate/verdict) fires a head-kind mismatch — the
    #     not-applicable form cannot be used to hide a mismatch ---
    cases += 1
    findings = compare_heads({"kind": "na", "reason": "no request-side field"}, {"kind": "verdict", "token": "honest"})
    check("a not-applicable cell over real evidence did not fire a head-kind mismatch", findings == ["mismatch-head-kind:expected-verdict"])

    # --- compare_heads: a cell claiming no-request-side-field when evidence
    #     says parameter-rejected-at-the-contract-sweep fires mismatch-na-reason ---
    cases += 1
    findings = compare_heads(
        {"kind": "na", "reason": "no request-side field"},
        {"kind": "na", "reason": "parameter rejected at the contract sweep"},
    )
    check("a wrong na reason did not fire mismatch-na-reason", findings == ["mismatch-na-reason"])

    # --- run_check end-to-end: a fully clean fixture (one key, one model,
    #     matching evidence and cell) reports zero findings, 1 cell examined ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        registry = {
            "features": [
                {"id": "stop_sequence_honesty", "group": "wire-behavior", "block": "model_features"},
            ]
        }
        (td_path / "registry.yaml").write_text(yaml.safe_dump(registry, sort_keys=False))
        models_doc = {"models": [{"slug": "fixture-model"}]}
        (td_path / "models.yaml").write_text(yaml.safe_dump(models_doc, sort_keys=False))
        tools_dir = td_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "fixture-model.md").write_text(
            "---\n"
            "name: fixture-model\n"
            "model_features:\n"
            '  stop_sequence_honesty: "honest — OBSERVED 2026-09-03: context, '
            'cell_id:`fixture-model--stop-truncation--triggering--default`, promoted ADR-0050."\n'
            "---\n\nBody.\n"
        )
        beh_cells = [{
            "cell_id": "fixture-model--stop-truncation--triggering--default",
            "model": "fixture-model", "param": "stop-truncation",
            "truncation_verdict": "stop-honored", "finish_reason_honest": "honest",
            "probe_ids": [],
        }]
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check("a fully clean fixture reported findings", findings == [])
        check("a fully clean fixture did not report 1 cell examined", examined == 1)
        check("a fully clean fixture reported nonzero mismatches", mismatched == 0)
        check("a fully clean fixture reported nonzero missing cells", missing == 0)

        # --- run_check: a promoted key with no cell at all in one report
        #     produces a missing-cell finding naming that model and key ---
        cases += 1
        (tools_dir / "fixture-model.md").write_text("---\nname: fixture-model\nmodel_features: {}\n---\n\nBody.\n")
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check(
            "a missing cell did not fire a missing-cell finding naming the pair",
            findings == [{"scope": "coverage", "identifier": "stop_sequence_honesty:fixture-model", "rule": "missing-cell"}]
            and missing == 1,
        )

        # --- run_check: a citation token resolving to no cell_id/probe_id in
        #     the classified evidence produces a finding ---
        cases += 1
        (tools_dir / "fixture-model.md").write_text(
            "---\n"
            "name: fixture-model\n"
            "model_features:\n"
            '  stop_sequence_honesty: "honest — OBSERVED 2026-09-03: context, '
            'cell_id:`no-such-cell-id`, promoted ADR-0050."\n'
            "---\n\nBody.\n"
        )
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check(
            "a dangling citation did not fire a dangling-citation finding",
            any(f["rule"].startswith("dangling-citation") for f in findings),
        )

        # --- run_check: a mismatching verdict fires a cell-scope mismatch
        #     finding ---
        cases += 1
        (tools_dir / "fixture-model.md").write_text(
            "---\n"
            "name: fixture-model\n"
            "model_features:\n"
            '  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-03: context, '
            'cell_id:`fixture-model--stop-truncation--triggering--default`, promoted ADR-0050."\n'
            "---\n\nBody.\n"
        )
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check("a mismatching verdict cell did not fire mismatch-verdict", any(f["rule"] == "mismatch-verdict" for f in findings))
        check("a mismatching verdict cell was not counted in mismatched_cells", mismatched == 1)

        # --- run_check: an unparseable cell fires a finding rather than
        #     being skipped ---
        cases += 1
        (tools_dir / "fixture-model.md").write_text(
            "---\nname: fixture-model\nmodel_features:\n  stop_sequence_honesty: \"not a valid cell at all\"\n---\n\nBody.\n"
        )
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check("an unparseable cell was silently skipped instead of firing", any(f["rule"] == "unparseable-cell" for f in findings))

        # --- run_check: a not-applicable cell claiming no-request-side-field
        #     for a model with REAL evidence fires a finding — the
        #     not-applicable form cannot hide a mismatch ---
        cases += 1
        (tools_dir / "fixture-model.md").write_text(
            "---\n"
            "name: fixture-model\n"
            "model_features:\n"
            '  stop_sequence_honesty: "n/a (no request-side field) — OBSERVED 2026-09-03: context, '
            'cell_id:`fixture-model--stop-truncation--triggering--default`, promoted ADR-0050."\n'
            "---\n\nBody.\n"
        )
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check(
            "a not-applicable cell over real evidence did not fire a finding",
            any(f["rule"].startswith("mismatch-head-kind") for f in findings),
        )

        # --- run_check: a registry carrying zero wire-behavior keys reports
        #     zero cells examined EXPLICITLY (0, not a silent clean run) ---
        cases += 1
        empty_registry = {"features": [{"id": "unrelated", "group": "cost", "block": "model_features"}]}
        (td_path / "empty-registry.yaml").write_text(yaml.safe_dump(empty_registry, sort_keys=False))
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "empty-registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check("an empty wire-behavior domain did not report exactly zero cells examined", examined == 0 and findings == [])

        # --- run_check: a model report outside the probed-model domain is
        #     never examined and never produces a finding ---
        cases += 1
        (tools_dir / "unprobed-model.md").write_text(
            "---\nname: unprobed-model\nmodel_features:\n  stop_sequence_honesty: \"garbage, not even parseable\"\n---\n\nBody.\n"
        )
        findings, examined, mismatched, missing = run_check(
            tools_dir=tools_dir, registry_path=td_path / "registry.yaml", models_path=td_path / "models.yaml",
            behavioral_cells=beh_cells, contract_cells=[],
        )
        check(
            "an out-of-domain model report was examined or produced a finding",
            not any("unprobed-model" in f["identifier"] for f in findings),
        )

    # --- precedence rule: where a model+key pair has BOTH a contract result
    #     and a behavioral result, the derived expectation comes from the
    #     BEHAVIORAL one — a cell matching the superseded contract result
    #     would produce a mismatch finding against the correct (behavioral)
    #     expectation ---
    cases += 1
    beh_reverify = [{
        "cell_id": "m--logprobs-reverify--combined--default",
        "model": "m", "param": "logprobs-reverify", "state": "accepted-honored",
    }]
    cs_superseded = [{
        "model": "m", "param": "logprobs", "mode": "default", "state": "accepted-ignored",
        "probe_id": "m--logprobs--true--default--deadbeef",
    }]
    beh_idx, _ = index_behavioral(beh_reverify)
    cs_idx, _ = index_contract(cs_superseded)
    derived = derive_logprobs_delivery("m", beh_idx, cs_idx)
    check(
        "the behavioral result did not win over a superseded contract result",
        derived == {"kind": "verdict", "token": "accepted-honored"},
    )

    # --- an unreadable/malformed registry file exits 2 ---
    cases += 1
    try:
        promoted_key_ids(Path("/nonexistent/path/does-not-exist.yaml"))
        check("a missing registry file did not raise SystemExit(2)", False)
    except SystemExit as e:
        check("a missing registry file did not exit with code 2", e.code == 2)

    # --- both flags together, and neither flag, exit 2 — exercised through
    #     main()'s own dispatch, not reimplemented ---
    cases += 1
    old_argv = sys.argv
    try:
        sys.argv = ["check-probe-drift.py", "--check", "--selftest"]
        rc = main()
        check("passing both --check and --selftest did not return 2", rc == 2)
    finally:
        sys.argv = old_argv

    cases += 1
    old_argv = sys.argv
    try:
        sys.argv = ["check-probe-drift.py"]
        rc = main()
        check("passing neither flag did not return 2", rc == 2)
    finally:
        sys.argv = old_argv

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check-probe-drift.py",
        usage="check-probe-drift.py --check | --selftest",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.check and args.selftest:
        print("usage: check-probe-drift.py --check | --selftest", file=sys.stderr)
        return 2

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if args.check:
        findings, examined, mismatched, missing = run_check()
        _print_findings(findings)
        print(f"{examined} cell(s) examined, {mismatched} mismatch(es), {missing} missing cell(s)")
        print(f"{len(findings)} problem(s)")
        return 1 if findings else 0

    print("usage: check-probe-drift.py --check | --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
