#!/usr/bin/env python3
"""probes/harness/ledger.py — append-only spend accounting (D-07). One line per billed
attempt in `probes/ledger.jsonl`; totals (global and per-vendor) are recomputed by
summing the whole file on every read — there is no in-place running-total file and no
cached total anywhere, matching this repo's "recompute from source of truth, never
trust a cached value" discipline (the same idiom `build-tool-index.py --check`
re-derives commit state from the live clone rather than a stored value).

    python3 probes/harness/ledger.py --selftest    # run the embedded fixtures
    python3 probes/harness/ledger.py --totals       # print recomputed totals

Ceiling enforcement (D-05/D-06) is plan 09-02's job — this module does not stub a
ceiling function that would later have to move.
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
    price_row carry them."""
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
