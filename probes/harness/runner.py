#!/usr/bin/env python3
"""probes/harness/runner.py — CLI entry point: parses a probe-set YAML, dispatches
each declared probe through the wire-family adapter registered in adapters/, fires
the request via client.py, and writes the result as one JSONL record per vendor
(D-08) plus one ledger line per billed attempt (D-07).

    python3 probes/harness/runner.py --set probes/sets/smoke.yaml [--dry-run]
    python3 probes/harness/runner.py --selftest

Exit codes: 0 clean, 1 problems recorded (a probe errored, or a ceiling-adjacent issue
— see plan 09-02 for ceiling enforcement itself), 2 bad invocation (including a
malformed probes/sets/*.yaml, models.yaml, or prices.yaml — the fail-loud path never
returns a partial work list).

Secrets: keys are loaded once via client.load_keys() into a single in-process dict;
auth_headers() (in each adapter) is the only consumer of a key VALUE. build_record()
never accepts a header VALUE into the record — only a header NAME. After a record is
serialized and before it is written, assert_no_secrets() greps the serialized form for
every one of the eight loaded key values (not just the vendor being probed) and aborts
the whole run on a hit (D-09, T-09-01).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import client
import ledger
from adapters import ADAPTERS

PROBES_DIR = Path(__file__).resolve().parent.parent
MODELS_PATH = PROBES_DIR / "harness" / "models.yaml"
PRICES_PATH = PROBES_DIR / "harness" / "prices.yaml"
RAW_DIR = PROBES_DIR / "raw"
LEDGER_PATH = PROBES_DIR / "ledger.jsonl"
SECRETS_PATH = Path.home() / ".secrets" / "model-probes.env"

HARNESS_VERSION = "0.1.0"

# Each wire family's URL suffix, appended to models.yaml's base_url. Gemini (plan
# 09-02) embeds the model id in the path instead and dispatches through its own
# adapter's endpoint_url() — not needed by this tracer, which only fires Anthropic.
_WIRE_FAMILY_URL_SUFFIX = {
    "anthropic_messages": "/messages",
    "openai_compat": "/chat/completions",
}

# D-09 refinement (Task 1 checkpoint resolution, 2026-09-01): org/account-identifying
# response headers are excluded from the logged record ENTIRELY — not just their
# values. Rate-limit headers and request-ids are research-relevant and are kept.
# Case-insensitive; everything not listed here passes through unchanged.
_ORG_IDENTIFYING_RESPONSE_HEADERS = {
    "openai-organization",
    "openai-project",
    "anthropic-organization-id",
    "anthropic-workspace-id",  # observed live on the tracer probe, 2026-09-01 —
                                 # Anthropic's actual account-identifying header;
                                 # the guessed `anthropic-organization-id` above was
                                 # never observed on the wire, kept as a defensive
                                 # guess for a differently-shaped account signal
    "x-organization-id",
}


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path every
    config loader below uses. Named `_fail`, not `die`, only to keep it distinct
    from any future process-signal handling in this file. Callers in `main()` let
    this propagate naturally (correct CLI exit-code behavior); `selftest()` below
    catches it with `except SystemExit` to verify the path without killing the
    self-test process itself."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def probe_id(model_slug: str, param: str, value: str, mode: str, request_body: dict) -> str:
    """D-04: semantic slug + short hash of the canonical request body. Canonical =
    sorted keys, no whitespace — the same body always hashes the same regardless of
    the probe-set YAML's key order, and a corrected body (e.g. a typo fixed) changes
    the hash, so a fixed probe re-fires without manual JSONL surgery."""
    canonical = json.dumps(request_body, sort_keys=True, separators=(",", ":"))
    body_hash = hashlib.sha256(canonical.encode()).hexdigest()[:8]
    return f"{model_slug}--{param}--{value}--{mode}--{body_hash}"


def seen_probe_ids(path: Path) -> set[str]:
    """Scan `probes/raw/{vendor}.jsonl` for already-logged probe_ids (D-08, HARN-02).
    A missing file, a zero-byte file, and a file whose final line is a truncated
    partial record are all handled without raising — every complete line populates
    the seen-set, the trailing partial line is ignored."""
    p = Path(path)
    seen: set[str] = set()
    if not p.exists() or p.stat().st_size == 0:
        return seen
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            # Truncated trailing line from a killed process — ignore it; every
            # complete line before it already populated `seen`.
            continue
        pid = rec.get("probe_id")
        if pid:
            seen.add(pid)
    return seen


def filter_response_headers(headers: dict) -> dict:
    """Drop org/account-identifying response headers before they reach a record
    (D-09 refinement). Everything else — rate-limit headers, request-ids — passes
    through unchanged."""
    return {k: v for k, v in headers.items() if k.lower() not in _ORG_IDENTIFYING_RESPONSE_HEADERS}


def build_record(
    *,
    pid: str,
    vendor: str,
    model_slug: str,
    api_model_id: str,
    wire_family: str,
    set_file: str,
    param: str,
    value: str,
    mode: str,
    method: str,
    url: str,
    headers_sent: dict,
    request_body: dict,
    attempts: list[dict],
    terminal: str,
    retries: int,
    usage: dict,
    cost: float | None,
) -> dict:
    """Build the JSONL record from an explicit field allowlist (D-09). `headers_sent`
    is the FULL headers dict actually sent (name -> value) — this function only ever
    reads `.keys()` from it; there is no code path here that copies a header VALUE
    into the record."""
    return {
        "probe_id": pid,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vendor": vendor,
        "model_slug": model_slug,
        "api_model_id": api_model_id,
        "wire_family": wire_family,
        "set_file": set_file,
        "param": param,
        "value": value,
        "mode": mode,
        "request": {
            "method": method,
            "url": url,
            "headers_sent": sorted(headers_sent.keys()),
            "body": request_body,
        },
        "attempts": attempts,
        "terminal": terminal,
        "retries": retries,
        "usage": usage,
        "cost_usd": cost,
        "harness_version": HARNESS_VERSION,
    }


def assert_no_secrets(serialized: str, key_values: list[str]) -> None:
    """Post-serialization tripwire (D-09, T-09-01): abort the whole run if ANY
    currently loaded PERSONAL_* key value — not just the vendor being probed — is
    found in the serialized record. Structural exclusion (the field allowlist in
    build_record) is the primary defense; this is the backstop, never relied on
    alone."""
    for kv in key_values:
        if kv and kv in serialized:
            _fail(1, "SECURITY ABORT: a loaded key value was found in a record about "
                      "to be written — aborting before any write (D-09 tripwire).")


def load_models(path: Path = MODELS_PATH) -> dict[str, dict]:
    """Parse models.yaml -> {slug: row}. Required keys: slug, maker, vendor,
    wire_family, api_model_id, base_url, key_env_var. Fails loud (exit 2) on any
    parse or validation error — never a silent default (T-09-03)."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        _fail(2, f"{path}: expected a top-level `models:` list")
    required = {"slug", "maker", "vendor", "wire_family", "api_model_id", "base_url", "key_env_var"}
    rows: dict[str, dict] = {}
    for row in data["models"]:
        missing = required - set(row)
        if missing:
            _fail(2, f"{path}: model row missing required key(s) {sorted(missing)}: {row}")
        rows[row["slug"]] = row
    return rows


def load_prices(path: Path = PRICES_PATH) -> dict[str, dict]:
    """Parse prices.yaml -> {slug: row}. Required keys: slug, input_usd_per_mtok,
    output_usd_per_mtok, retrieved, source. Fails loud (exit 2) on any parse or
    validation error."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("prices"), list):
        _fail(2, f"{path}: expected a top-level `prices:` list")
    required = {"slug", "input_usd_per_mtok", "output_usd_per_mtok", "retrieved", "source"}
    rows: dict[str, dict] = {}
    for row in data["prices"]:
        missing = required - set(row)
        if missing:
            _fail(2, f"{path}: price row missing required key(s) {sorted(missing)}: {row}")
        rows[row["slug"]] = row
    return rows


def load_probe_set(path) -> list[dict]:
    """Parse a probes/sets/*.yaml declaration. A missing/empty `probes:` list, or an
    entry missing a required key, aborts before any HTTP request is sent: exit code
    2, a named diagnostic naming the file and the missing key, zero new JSONL lines
    (HARN-01 empty)."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        _fail(2, f"cannot read {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        _fail(2, f"{path} is not valid YAML: {e}")
    probes = (data or {}).get("probes") if isinstance(data, dict) else None
    if not isinstance(probes, list) or not probes:
        _fail(2, f"{path}: `probes:` must be a non-empty list")
    required = {"model", "param", "value", "mode"}
    for entry in probes:
        missing = required - set(entry)
        if missing:
            _fail(2, f"{path}: probe entry missing required key(s) {sorted(missing)}: {entry}")
    return probes


def endpoint_url(wire_family: str, base_url: str, api_model_id: str) -> str:
    """Suffix a family's base_url per RESEARCH.md's per-family URL convention.
    Anthropic and OpenAI-compat append a fixed suffix; a family whose adapter defines
    its own `endpoint_url()` (Gemini, plan 09-02 — the model id lives in the path,
    not the body) is dispatched there instead."""
    suffix = _WIRE_FAMILY_URL_SUFFIX.get(wire_family)
    if suffix is not None:
        return base_url.rstrip("/") + suffix
    adapter = ADAPTERS.get(wire_family)
    if adapter is not None and hasattr(adapter, "endpoint_url"):
        return adapter.endpoint_url(base_url, api_model_id)
    raise ValueError(f"no endpoint_url rule for wire_family={wire_family}")


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    # --- probe_id: key-order-independent canonicalization ---
    cases += 1
    body_a = {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]}
    body_b = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 16, "model": "x"}
    pid_a = probe_id("x", "baseline", "none", "default", body_a)
    pid_b = probe_id("x", "baseline", "none", "default", body_b)
    if pid_a != pid_b:
        problems += 1
        print(f"FAIL probe_id: declared-key-order independence broke: {pid_a} != {pid_b}", file=sys.stderr)

    # --- probe_id: a single-character body change produces a different probe_id ---
    cases += 1
    body_c = {"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hj"}]}
    pid_c = probe_id("x", "baseline", "none", "default", body_c)
    if pid_c == pid_a:
        problems += 1
        print("FAIL probe_id: a single-character body change did not change the hash", file=sys.stderr)

    # --- seen_probe_ids: nonexistent path / zero-byte file -> empty set, no raise ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        missing = Path(td) / "does-not-exist.jsonl"
        s1 = seen_probe_ids(missing)
        if s1 != set():
            problems += 1
            print("FAIL seen_probe_ids: nonexistent file should yield an empty set", file=sys.stderr)
        zero = Path(td) / "zero-byte.jsonl"
        zero.write_text("")
        s2 = seen_probe_ids(zero)
        if s2 != set():
            problems += 1
            print("FAIL seen_probe_ids: zero-byte file should yield an empty set", file=sys.stderr)

        # --- seen_probe_ids: truncated final line is ignored, complete lines kept ---
        cases += 1
        truncated = Path(td) / "truncated.jsonl"
        truncated.write_text(
            json.dumps({"probe_id": "a--baseline--none--default--aaaaaaaa"}) + "\n"
            + json.dumps({"probe_id": "b--baseline--none--default--bbbbbbbb"}) + "\n"
            + '{"probe_id": "c--baseline--none--defau'
        )
        s3 = seen_probe_ids(truncated)
        if s3 != {"a--baseline--none--default--aaaaaaaa", "b--baseline--none--default--bbbbbbbb"}:
            problems += 1
            print(f"FAIL seen_probe_ids: truncated-line handling wrong, got {s3}", file=sys.stderr)

    # --- probe-set fail-loud paths: no probes key / empty list / missing required key ---
    for label, content in [
        ("no probes key", "not_probes: []\n"),
        ("empty probes list", "probes: []\n"),
        ("entry missing required key", "probes:\n  - model: x\n    param: baseline\n"),
    ]:
        cases += 1
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.yaml"
            bad.write_text(content)
            try:
                load_probe_set(bad)
                problems += 1
                print(f"FAIL load_probe_set({label}): expected a fail-loud exit, got a return", file=sys.stderr)
            except SystemExit as e:
                if e.code != 2:
                    problems += 1
                    print(f"FAIL load_probe_set({label}): expected exit code 2, got {e.code}", file=sys.stderr)

    # --- build_record: header VALUES never reach the serialized record, only NAMES ---
    cases += 1
    # Deliberately NOT prefixed `sk-`/`AIza` — the repo's own "no key VALUE in the
    # registries" lint (`grep -rnE '(sk-|AIza)[A-Za-z0-9_-]{12,}' probes/harness/`)
    # scans this whole directory tree, and a realistic-looking fixture secret here
    # would false-positive that check. The tripwire logic under test only cares
    # that an arbitrary string value is found in a serialized record — the prefix
    # shape is irrelevant to what's being verified.
    fake_key = "FAKESELFTESTVALUE-not-a-real-key-0000000000"
    record = build_record(
        pid="x--baseline--none--default--deadbeef",
        vendor="anthropic",
        model_slug="x",
        api_model_id="x-api",
        wire_family="anthropic_messages",
        set_file="probes/sets/smoke.yaml",
        param="baseline",
        value="none",
        mode="default",
        method="POST",
        url="https://api.example.com/v1/messages",
        headers_sent={"x-api-key": fake_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        request_body={"model": "x", "max_tokens": 16, "messages": [{"role": "user", "content": "hi"}]},
        attempts=[{
            "n": 1, "status": 200, "retryable": False, "wait_s": None,
            "response_headers": {"request-id": "req_123"},
            "response_body_raw": {"usage": {"input_tokens": 8, "output_tokens": 4}},
            "at": "2026-09-01T00:00:00Z",
        }],
        terminal="verdict",
        retries=0,
        usage={"input_tokens": 8, "output_tokens": 4},
        cost=0.001,
    )
    serialized = json.dumps(record)
    if fake_key in serialized:
        problems += 1
        print("FAIL build_record: a header VALUE leaked into the serialized record", file=sys.stderr)
    if "x-api-key" not in record["request"]["headers_sent"]:
        problems += 1
        print("FAIL build_record: header NAME missing from headers_sent", file=sys.stderr)
    if not (isinstance(record["request"]["headers_sent"], list)
            and all(isinstance(h, str) for h in record["request"]["headers_sent"])):
        problems += 1
        print("FAIL build_record: headers_sent must be a list of strings", file=sys.stderr)

    # --- assert_no_secrets: a leaked key value aborts the run ---
    cases += 1
    leaked_serialized = json.dumps({"note": f"oops leaked {fake_key} here"})
    try:
        assert_no_secrets(leaked_serialized, [fake_key])
        problems += 1
        print("FAIL assert_no_secrets: expected an abort on a leaked key value, got a return", file=sys.stderr)
    except SystemExit:
        pass

    # --- filter_response_headers: org headers dropped, rate-limit/request-id kept ---
    cases += 1
    raw_headers = {
        "openai-organization": "org-should-not-appear",
        "anthropic-workspace-id": "wrkspc-should-not-appear",
        "retry-after": "5",
        "request-id": "req_abc",
        "anthropic-ratelimit-requests-remaining": "99",
    }
    filtered = filter_response_headers(raw_headers)
    if "openai-organization" in filtered or "anthropic-workspace-id" in filtered:
        problems += 1
        print("FAIL filter_response_headers: an org/account header was not dropped", file=sys.stderr)
    if "retry-after" not in filtered or "request-id" not in filtered:
        problems += 1
        print("FAIL filter_response_headers: rate-limit/request-id header incorrectly dropped", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(prog="runner.py")
    parser.add_argument("--set", dest="set_path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if not args.set_path:
        print("usage: runner.py --set <probes/sets/*.yaml> [--dry-run] | --selftest", file=sys.stderr)
        return 2

    probes = load_probe_set(args.set_path)
    models = load_models()
    prices = load_prices()

    all_keys = client.load_keys(SECRETS_PATH)
    all_key_values = list(all_keys.values())

    problems = 0
    for entry in probes:
        model_slug = entry["model"]
        if model_slug not in models:
            print(f"unknown model slug in probe set: {model_slug}", file=sys.stderr)
            problems += 1
            continue
        row = models[model_slug]
        vendor = row["vendor"]
        wire_family = row["wire_family"]
        adapter = ADAPTERS.get(wire_family)
        if adapter is None:
            print(f"no adapter registered for wire_family={wire_family}", file=sys.stderr)
            problems += 1
            continue

        prompt = entry.get("prompt", "Reply with one word.")
        max_tokens = entry.get("max_tokens", 16)
        extra_params = entry.get("extra_params") or {}

        request_body = adapter.build_request(row["api_model_id"], prompt, max_tokens, extra_params)
        pid = probe_id(model_slug, entry["param"], entry["value"], entry["mode"], request_body)

        raw_path = RAW_DIR / f"{vendor}.jsonl"
        seen = seen_probe_ids(raw_path)
        if pid in seen:
            print(f"SKIP {pid} (already logged)")
            continue

        if args.dry_run:
            print(f"DRY-RUN {pid}")
            print(json.dumps(request_body, sort_keys=True, separators=(",", ":")))
            continue

        key_env_var = row["key_env_var"]
        key_value = all_keys.get(key_env_var)
        if not key_value:
            print(f"missing key: {key_env_var} not found in {SECRETS_PATH}", file=sys.stderr)
            problems += 1
            continue

        headers_sent = {**adapter.auth_headers(key_value), "Content-Type": "application/json"}
        url = endpoint_url(wire_family, row["base_url"], row["api_model_id"])

        status, resp_headers_dict, body_bytes, _resp_headers_msg = client.post_json(url, request_body, headers_sent)
        at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            resp_body = json.loads(body_bytes)
        except json.JSONDecodeError:
            resp_body = body_bytes.decode(errors="replace")

        attempt = {
            "n": 1,
            "status": status,
            "retryable": False,
            "wait_s": None,
            "response_headers": filter_response_headers(resp_headers_dict),
            "response_body_raw": resp_body,
            "at": at,
        }

        usage: dict = {}
        cost = None
        terminal = "verdict"
        if status == 200 and isinstance(resp_body, dict):
            usage = adapter.parse_usage(resp_body)
            price_row = prices.get(model_slug)
            if price_row:
                cost = ledger.cost_usd(usage, price_row)
        else:
            terminal = "error"
            problems += 1

        record = build_record(
            pid=pid,
            vendor=vendor,
            model_slug=model_slug,
            api_model_id=row["api_model_id"],
            wire_family=wire_family,
            set_file=str(args.set_path),
            param=entry["param"],
            value=entry["value"],
            mode=entry["mode"],
            method="POST",
            url=client.mask_url(url),
            headers_sent=headers_sent,
            request_body=request_body,
            attempts=[attempt],
            terminal=terminal,
            retries=0,
            usage=usage,
            cost=cost,
        )

        serialized = json.dumps(record)
        assert_no_secrets(serialized, all_key_values)

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        with raw_path.open("a") as f:
            f.write(serialized + "\n")
            f.flush()

        if cost is not None:
            price_row = prices.get(model_slug, {})
            ledger.append(LEDGER_PATH, {
                "probe_id": pid,
                "vendor": vendor,
                "model_slug": model_slug,
                "tokens": usage,
                "price_row": price_row,
                "cost_usd": cost,
                "recorded_at": at,
            })

        print(f"OK {pid} status={status} cost_usd={cost}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
