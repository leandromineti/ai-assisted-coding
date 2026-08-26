#!/usr/bin/env python3
"""Observed session throughput (tok/s) from committed harness transcripts.

Scans experiments/*/artifacts/ for Claude Code headless result JSONs (anything
with `usage` + `duration_api_ms`) and prints per-model throughput:

    output_tokens(dominant model) / duration_api_ms

This is SESSION-level agent throughput, not decode speed: the denominator
includes per-turn TTFT, tool-result processing, and inter-turn overhead, so it
is a lower bound on raw generation and the honest number for planning agent-run
wall-clock. Defined in tools/cross-cutting/metrics.md § Observed session
throughput; recorded values in model reports cite this script — never hand-type
the numbers (methodology rule 3's spirit applied to observed data).

Sessions are attributed to the model that produced the most output tokens
(`modelUsage`); the harness's tiny internal haiku call (~18 tok) rides along in
every session and is ignored by that rule. Runs under ~500 output tokens are
excluded — they are latency-bound, not throughput-bound.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_OUTPUT_TOKENS = 500


def collect() -> dict[str, list[tuple[str, int, float, float]]]:
    by_model: dict[str, list] = {}
    for path in sorted(ROOT.glob("experiments/*/artifacts/**/*.json")):
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(d, dict) or "duration_api_ms" not in d:
            continue
        ms = d.get("duration_api_ms") or 0
        mu = d.get("modelUsage") or {}
        if mu:
            model, usage = max(
                mu.items(), key=lambda kv: kv[1].get("outputTokens", 0)
            )
            out = usage.get("outputTokens", 0)
        else:
            model, out = "unknown", (d.get("usage") or {}).get("output_tokens", 0)
        if not ms or out < MIN_OUTPUT_TOKENS:
            continue
        rel = str(path.relative_to(ROOT))
        by_model.setdefault(model, []).append((rel, out, ms / 1000, out / (ms / 1000)))
    return by_model


def main() -> int:
    by_model = collect()
    if not by_model:
        print("no harness result JSONs found", file=sys.stderr)
        return 1
    for model, rows in sorted(by_model.items()):
        tps = [r[3] for r in rows]
        print(f"\n== {model} (n={len(rows)}) ==")
        for rel, out, s, t in rows:
            print(f"  {rel:70s} out={out:6d} api={s:6.1f}s {t:6.1f} tok/s")
        print(
            f"  mean {statistics.mean(tps):.0f} · median {statistics.median(tps):.0f}"
            f" · range {min(tps):.0f}-{max(tps):.0f} tok/s"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
