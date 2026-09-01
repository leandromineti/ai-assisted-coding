#!/usr/bin/env python3
"""probes/harness/ledger.py — append-only spend accounting (D-07). One line per billed
attempt in `probes/ledger.jsonl`; totals (global and per-vendor) are recomputed by
summing the whole file on every read — there is no in-place running-total file and no
cached total anywhere, matching this repo's "recompute from source of truth, never
trust a cached value" discipline (the same idiom `build-tool-index.py --check`
re-derives commit state from the live clone rather than a stored value).

    python3 probes/harness/ledger.py --selftest    # run the embedded fixtures
    python3 probes/harness/ledger.py --totals       # print recomputed totals

ceiling_verdict() (plan 09-02, D-05/D-06) is the between-probes ceiling check the
runner consults after every probe's evidence and ledger line are already on disk — a
ceiling breach must never discard a response the harness already paid for. It is a
pure function: no I/O, no ledger mutation, thresholds taken as a parameter and never
hardcoded — the caller (runner.py) loads `ceilings.yaml` and recomputes totals() the
same way it always has, then hands both to this function.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

PROBES_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROBES_DIR / "ledger.jsonl"

# Usage-object token kind -> the prices.yaml rate key it bills against. Both cache
# vocabularies are listed because different wire families name the same concept
# differently (Anthropic: cache_creation/cache_read; OpenAI-compatible: cached_tokens)
# — D-02: "omit a tier rather than inventing a rate", so a tier only contributes when
# BOTH the usage object reports a count AND prices.yaml prices it.
_OPTIONAL_TIERS = {
    "cache_creation_input_tokens": "cache_write_usd_per_mtok",
    "cache_read_input_tokens": "cache_read_usd_per_mtok",
    "cached_tokens": "cache_read_usd_per_mtok",
    "reasoning_tokens": "reasoning_usd_per_mtok",
}


def append(path: Path, record: dict) -> None:
    """Append one ledger line, flushed immediately — a killed process leaves a valid
    prefix (same append-then-flush discipline as the raw JSONL writer).

    `default=str` handles the one non-JSON-native type this record legitimately
    carries: `price_row["retrieved"]`, which PyYAML's safe loader parses an
    unquoted `YYYY-MM-DD` scalar into as a `datetime.date` object, not a string —
    `str(date(...))` reproduces the same `YYYY-MM-DD` form (Rule 1 bug fix,
    plan 09-01 Task 2: this crashed the first live tracer run)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record, default=str) + "\n")
        f.flush()


def totals(path: Path) -> dict:
    """Recompute global and per-vendor sums (cost_usd and token counts) by reading
    every line of `path`. A missing or zero-byte file returns zeroes, never raises."""
    global_cost = 0.0
    global_tokens: dict[str, int] = {}
    by_vendor: dict[str, dict] = {}
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost = rec.get("cost_usd") or 0.0
            vendor = rec.get("vendor", "unknown")
            tokens = rec.get("tokens") or {}
            global_cost += cost
            slot = by_vendor.setdefault(vendor, {"cost_usd": 0.0, "tokens": {}})
            slot["cost_usd"] += cost
            for k, v in tokens.items():
                if v is None:
                    continue
                global_tokens[k] = global_tokens.get(k, 0) + v
                slot["tokens"][k] = slot["tokens"].get(k, 0) + v
    return {"global": {"cost_usd": global_cost, "tokens": global_tokens}, "by_vendor": by_vendor}


def cost_usd(usage: dict, price_row: dict) -> float | None:
    """Compute (tokens * rate) / 1_000_000 per token kind, summed. Returns None —
    never a misleading 0.0 — when a base token count price_row needs (input/output)
    is absent from the usage object, or when price_row lacks a base rate. Optional
    tiers (cache write/read, reasoning) are added only when both the usage object and
    price_row carry them.

    Does NOT read `usage.get("cost_in_usd_ticks")` (WR-03, phase-09 code review
    2026-09-01) even though `openai_compat.parse_usage()` passes it through: xAI's
    tick-to-USD divisor is not vendor-documented anywhere this repo has confirmed
    (see `openai_compat.py`'s `parse_usage` docstring), so every vendor — including
    xAI — is priced from the flat `prices.yaml` rate here, never a vendor-reported
    figure, until that divisor is confirmed from vendor docs."""
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_tokens is None or output_tokens is None:
        return None
    if "input_usd_per_mtok" not in price_row or "output_usd_per_mtok" not in price_row:
        return None
    total = (
        input_tokens * price_row["input_usd_per_mtok"]
        + output_tokens * price_row["output_usd_per_mtok"]
    ) / 1_000_000
    for usage_key, price_key in _OPTIONAL_TIERS.items():
        count = usage.get(usage_key)
        rate = price_row.get(price_key)
        if count and rate is not None:
            total += (count * rate) / 1_000_000
    return total


def _find_vendor_breach(by_vendor: dict, vendor_default: float, vendor_overrides: dict) -> list[tuple[str, float, float]]:
    """Module-private helper: EVERY vendor (in `by_vendor`'s iteration order) whose
    total has reached its soft sub-ceiling, as a list of `(vendor, vendor_usd,
    sub_ceiling)` triples — an empty list when none has breached. Kept private —
    `ceiling_verdict` is this module's only intended export (D-05) — but factored out
    so `ceiling_verdict`'s own precedence logic reads as a flat sequence of checks.

    D-03 (2026-09-01, CR-02 fix): promoted from returning only the FIRST breaching
    vendor to returning every one of them. The single-breach shape silently masked
    any second-or-later simultaneously-breaching vendor — the $0.50 sub-ceiling
    (D-02) makes that scenario materially more plausible for this sweep."""
    breaches: list[tuple[str, float, float]] = []
    for vendor, vendor_usd in by_vendor.items():
        sub_ceiling = vendor_overrides.get(vendor, vendor_default)
        if vendor_usd >= sub_ceiling:
            breaches.append((vendor, vendor_usd, sub_ceiling))
    return breaches


def ceiling_verdict(totals: dict, thresholds: dict) -> tuple[str, str, list[str]]:
    """Pure ceiling check (D-05/D-06) — no I/O, no ledger mutation; reads only the
    `totals` and `thresholds` it was handed. `totals` is the flat per-check shape
    `{"global_usd": float, "by_vendor": {vendor: float}}` (NOT this module's own
    `totals()` nested return shape — the caller flattens before calling this).
    `thresholds` is `ceilings.yaml`'s own mapping, loaded by the caller with the safe
    loader; no dollar figure is ever hardcoded here.

    Returns `(action, reason, vendors)`. Actions, in precedence order (first match
    wins):

    1. `'stop_global'` — the recomputed global total has reached (>=) the hard
       ceiling. Checked FIRST regardless of any vendor's status, because a global
       breach must stop everything, not just one vendor. `vendors` is `[]`.
    2. `'skip_vendor'` — one or more vendors' recomputed totals have reached (>=)
       their soft sub-ceiling (its own override in `vendor_soft_usd`, or the file's
       `vendor_soft_usd_default`). `vendors` is the AUTHORITATIVE, machine-readable
       list of every breaching vendor's short name, in `by_vendor` iteration order —
       the caller must add every one of them, never just the first. `reason` is
       human-readable ONLY (D-03, 2026-09-01): it now enumerates every breaching
       vendor rather than naming a single one, and is no longer a caller-parseable
       convention — the "reason names that vendor as its FIRST word" contract this
       docstring used to document is retired; `vendors` replaces it. (CR-02: the
       retired convention meant a caller that string-parsed the reason could only
       ever recover ONE breaching vendor per call, silently masking every other
       simultaneous breach.)
    3. `'warn'` — the global total has reached (>=) the warning threshold. `vendors`
       is `[]`.
    4. `'ok'` — under every threshold. `vendors` is `[]`.

    Every comparison breaches AT equality, never strictly above — a total landing
    exactly on a threshold IS a breach, pinned on both sides by --selftest."""
    global_hard = thresholds["global_hard_usd"]
    global_warn = thresholds["global_warn_usd"]
    vendor_default = thresholds["vendor_soft_usd_default"]
    vendor_overrides = thresholds.get("vendor_soft_usd") or {}

    global_usd = totals.get("global_usd", 0.0)
    by_vendor = totals.get("by_vendor") or {}

    if global_usd >= global_hard:
        return "stop_global", f"global total ${global_usd:.6f} reached the ${global_hard:.2f} hard ceiling", []

    breaches = _find_vendor_breach(by_vendor, vendor_default, vendor_overrides)
    if breaches:
        vendor_names = [vendor for vendor, _vendor_usd, _sub_ceiling in breaches]
        reason = "; ".join(
            f"{vendor} total ${vendor_usd:.6f} reached its ${sub_ceiling:.2f} soft sub-ceiling"
            for vendor, vendor_usd, sub_ceiling in breaches
        )
        return "skip_vendor", reason, vendor_names

    if global_usd >= global_warn:
        return "warn", f"global total ${global_usd:.6f} reached the ${global_warn:.2f} warning threshold", []

    return "ok", "under every threshold", []


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    # --- totals: three synthetic lines, sum globally and per-vendor ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        fixture = Path(td) / "ledger.jsonl"
        lines = [
            {"vendor": "anthropic", "cost_usd": 0.001, "tokens": {"input_tokens": 10, "output_tokens": 5}},
            {"vendor": "anthropic", "cost_usd": 0.002, "tokens": {"input_tokens": 20, "output_tokens": 8}},
            {"vendor": "openai", "cost_usd": 0.003, "tokens": {"input_tokens": 30, "output_tokens": 12}},
        ]
        fixture.write_text("\n".join(json.dumps(l) for l in lines) + "\n")
        t = totals(fixture)
        if abs(t["global"]["cost_usd"] - 0.006) > 1e-9:
            problems += 1
            print(f"FAIL totals: expected global cost 0.006, got {t['global']['cost_usd']}", file=sys.stderr)
        if abs(t["by_vendor"].get("anthropic", {}).get("cost_usd", 0) - 0.003) > 1e-9:
            problems += 1
            print("FAIL totals: anthropic per-vendor sum wrong", file=sys.stderr)
        if t["global"]["tokens"].get("input_tokens") != 60:
            problems += 1
            print("FAIL totals: global input_tokens sum wrong", file=sys.stderr)

    # --- totals: nonexistent file returns zeroes ---
    cases += 1
    t2 = totals(Path("/nonexistent/path/that/does/not/exist-selftest.jsonl"))
    if t2["global"]["cost_usd"] != 0.0 or t2["by_vendor"]:
        problems += 1
        print("FAIL totals: nonexistent file should return zeroes", file=sys.stderr)

    # --- cost_usd: hand-checked dollar figure for a known token count and price row ---
    cases += 1
    usage = {"input_tokens": 1000, "output_tokens": 500}
    price_row = {"input_usd_per_mtok": 1.0, "output_usd_per_mtok": 5.0}
    expect = (1000 * 1.0 + 500 * 5.0) / 1_000_000  # 0.0035, hand-checked
    got = cost_usd(usage, price_row)
    if got is None or abs(got - expect) > 1e-9:
        problems += 1
        print(f"FAIL cost_usd: expected {expect}, got {got}", file=sys.stderr)

    # --- cost_usd: None (never 0.0) when a needed count is absent ---
    cases += 1
    usage_missing = {"input_tokens": 1000, "output_tokens": None}
    got2 = cost_usd(usage_missing, price_row)
    if got2 is not None:
        problems += 1
        print(f"FAIL cost_usd: expected None for missing output_tokens, got {got2}", file=sys.stderr)

    # --- ceiling_verdict: shared fixture thresholds for the boundary cases below ---
    thresholds = {
        "global_hard_usd": 10.0,
        "global_warn_usd": 8.0,
        "vendor_soft_usd_default": 1.5,
        "vendor_soft_usd": {},
    }

    # --- ceiling_verdict: everything under every threshold -> ok ---
    cases += 1
    action, _reason, _vendors = ceiling_verdict({"global_usd": 0.02, "by_vendor": {"anthropic": 0.02}}, thresholds)
    if action != "ok":
        problems += 1
        print(f"FAIL ceiling_verdict(under everything): expected 'ok', got {action}", file=sys.stderr)

    # --- ceiling_verdict: global total EXACTLY at the warn threshold -> warn; one
    #     cent below -> ok (breach is at equality, not strictly above) ---
    cases += 1
    action_at, _, _ = ceiling_verdict({"global_usd": 8.00, "by_vendor": {"anthropic": 0.10}}, thresholds)
    action_below, _, _ = ceiling_verdict({"global_usd": 7.99, "by_vendor": {"anthropic": 0.10}}, thresholds)
    if action_at != "warn":
        problems += 1
        print(f"FAIL ceiling_verdict(global==warn): expected 'warn', got {action_at}", file=sys.stderr)
    if action_below != "ok":
        problems += 1
        print(f"FAIL ceiling_verdict(global==warn-0.01): expected 'ok', got {action_below}", file=sys.stderr)

    # --- ceiling_verdict: global total EXACTLY at the hard ceiling -> stop_global;
    #     one cent below -> warn, not stop (equality boundary, hard-ceiling side) ---
    cases += 1
    action_at, _, _ = ceiling_verdict({"global_usd": 10.00, "by_vendor": {"anthropic": 0.10}}, thresholds)
    action_below, _, _ = ceiling_verdict({"global_usd": 9.99, "by_vendor": {"anthropic": 0.10}}, thresholds)
    if action_at != "stop_global":
        problems += 1
        print(f"FAIL ceiling_verdict(global==hard): expected 'stop_global', got {action_at}", file=sys.stderr)
    if action_below != "warn":
        problems += 1
        print(f"FAIL ceiling_verdict(global==hard-0.01): expected 'warn', got {action_below}", file=sys.stderr)

    # --- ceiling_verdict: one vendor EXACTLY at its soft sub-ceiling -> skip_vendor
    #     naming it (in `reason`) and listing it (in `vendors`); a SEPARATE call with
    #     only a well-under vendor still returns ok — one vendor's breach must not
    #     leak into another vendor's status ---
    cases += 1
    action, reason, vendors = ceiling_verdict({"global_usd": 2.00, "by_vendor": {"zai": 1.50, "openai": 0.01}}, thresholds)
    if action != "skip_vendor" or "zai" not in reason or vendors != ["zai"]:
        problems += 1
        print(f"FAIL ceiling_verdict(vendor==soft): expected skip_vendor naming/listing zai, got {(action, reason, vendors)}", file=sys.stderr)
    action_other, _, vendors_other = ceiling_verdict({"global_usd": 0.01, "by_vendor": {"openai": 0.01}}, thresholds)
    if action_other != "ok" or vendors_other != []:
        problems += 1
        print(f"FAIL ceiling_verdict(other vendor alone): expected 'ok' with no vendors, got {(action_other, vendors_other)}", file=sys.stderr)

    # --- ceiling_verdict: a per-vendor override in ceilings.yaml's own shape takes
    #     precedence over vendor_soft_usd_default for THAT vendor only ---
    cases += 1
    override_thresholds = dict(thresholds, vendor_soft_usd={"kimi": 3.00})
    action_kimi, _, _ = ceiling_verdict({"global_usd": 2.80, "by_vendor": {"kimi": 2.80}}, override_thresholds)
    action_other_default, _, _ = ceiling_verdict({"global_usd": 1.60, "by_vendor": {"glm": 1.60}}, override_thresholds)
    if action_kimi != "ok":
        problems += 1
        print(f"FAIL ceiling_verdict(override raises kimi's ceiling): expected 'ok' at 2.80 < 3.00 override, got {action_kimi}", file=sys.stderr)
    if action_other_default != "skip_vendor":
        problems += 1
        print(f"FAIL ceiling_verdict(non-overridden vendor still uses default): expected skip_vendor, got {action_other_default}", file=sys.stderr)

    # --- ceiling_verdict: pure — repeated calls with identical input are deterministic
    #     (the closest a unit test gets to proving "no I/O, no mutation") ---
    cases += 1
    call_totals = {"global_usd": 5.00, "by_vendor": {"anthropic": 0.50}}
    first = ceiling_verdict(call_totals, thresholds)
    second = ceiling_verdict(call_totals, thresholds)
    if first != second or call_totals != {"global_usd": 5.00, "by_vendor": {"anthropic": 0.50}}:
        problems += 1
        print("FAIL ceiling_verdict: expected deterministic output and an unmutated totals argument", file=sys.stderr)

    # --- ceiling_verdict: TWO vendors simultaneously at/over the sub-ceiling ->
    #     skip_vendor naming AND listing BOTH (D-03, the exact scenario CR-02
    #     masked: the pre-fix helper returned only the first-iterated vendor, so a
    #     second simultaneous breach was silently dropped). Uses D-02's real $0.50
    #     default (not this fixture block's $1.50) so the fixture mirrors the actual
    #     Phase 11 ceiling configuration the bug would have shipped under. ---
    cases += 1
    multi_thresholds = dict(thresholds, vendor_soft_usd_default=0.50)
    action_multi, reason_multi, vendors_multi = ceiling_verdict(
        {"global_usd": 1.25, "by_vendor": {"zai": 0.50, "kimi": 0.75, "openai": 0.01}}, multi_thresholds
    )
    if action_multi != "skip_vendor" or sorted(vendors_multi) != ["kimi", "zai"]:
        problems += 1
        print(f"FAIL ceiling_verdict(two simultaneous breaches): expected skip_vendor listing both kimi and zai, got {(action_multi, vendors_multi)}", file=sys.stderr)
    if "zai" not in reason_multi or "kimi" not in reason_multi:
        problems += 1
        print(f"FAIL ceiling_verdict(two simultaneous breaches): reason must name both vendors, got {reason_multi!r}", file=sys.stderr)

    # --- ceiling_verdict: sequential-shape pin (D-03) — the exact shape CR-02
    #     masked in runner.py's main() loop: a FIRST call reports one breaching
    #     vendor (which the caller would record in skipped_vendors); a LATER call,
    #     once totals show a second vendor has also breached, must still return that
    #     second vendor — a caller that only ever recorded the first call's single
    #     vendor (the pre-fix reason-string-first-word convention) would silently
    #     let the second vendor keep firing past its own sub-ceiling. Same $0.50
    #     default as the simultaneous-breach fixture above. ---
    cases += 1
    first_call_totals = {"global_usd": 0.60, "by_vendor": {"zai": 0.50, "kimi": 0.10}}
    action_seq1, _reason_seq1, vendors_seq1 = ceiling_verdict(first_call_totals, multi_thresholds)
    if action_seq1 != "skip_vendor" or vendors_seq1 != ["zai"]:
        problems += 1
        print(f"FAIL ceiling_verdict(sequential, first call): expected skip_vendor ['zai'], got {(action_seq1, vendors_seq1)}", file=sys.stderr)
    second_call_totals = {"global_usd": 1.35, "by_vendor": {"zai": 0.50, "kimi": 0.75}}
    action_seq2, reason_seq2, vendors_seq2 = ceiling_verdict(second_call_totals, multi_thresholds)
    if action_seq2 != "skip_vendor" or "kimi" not in vendors_seq2:
        problems += 1
        print(f"FAIL ceiling_verdict(sequential, second call): expected skip_vendor including kimi, got {(action_seq2, vendors_seq2)}", file=sys.stderr)
    if "kimi" not in reason_seq2:
        problems += 1
        print(f"FAIL ceiling_verdict(sequential, second call): reason must name kimi, got {reason_seq2!r}", file=sys.stderr)

    return cases, problems


def main() -> int:
    args = sys.argv[1:]
    valid = {"--selftest", "--totals"}
    if len(args) > 1 or (args and args[0] not in valid):
        print("usage: ledger.py [--selftest|--totals]", file=sys.stderr)
        return 2

    if args and args[0] == "--selftest":
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    t = totals(LEDGER_PATH)
    print(json.dumps(t, indent=2))
    print(f"global total: ${t['global']['cost_usd']:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
