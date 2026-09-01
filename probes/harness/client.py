#!/usr/bin/env python3
"""probes/harness/client.py — the harness's stdlib HTTP transport and single auth
choke point (D-09). No vendor SDK, no third-party HTTP or retry library is imported
here — STACK.md already vetted and rejected each candidate; SDKs normalize away the
very asymmetries this instrument measures.

    python3 probes/harness/client.py    # tiny manual smoke check of mask_url()

post_json() never raises on a 4xx/5xx response — the harness needs the vendor's error
body verbatim (D-09's verbatim-capture requirement), which scripts/fetch-citations.py's
existing retry-loop precedent never needed (it only inspected `.code`). post_json() is
a single-attempt send; retry_decision()/send_with_retry() below (plan 09-02) wrap it
without moving auth attachment, which stays entirely in the caller (runner.py) via each
adapter's auth_headers().

load_keys() returns key VALUES into a single choke point (auth_headers() in each
adapter is the only intended consumer) — nothing downstream of this function may print,
log, or write a value to disk (T-09-01/T-09-02).

retry_decision() is status-code-first and family-agnostic (HARN-04): a 2xx is a
`'verdict'`; a 429 or any 5xx is retryable-shaped; every OTHER 4xx is also a `'verdict'`
with zero retries — misfiling a 429 into that branch would corrupt Phase 11's contract
matrix with a false rejection. Anthropic's spend-cap 429 (no Retry-After, "keeps
failing until access resumes" per RESEARCH.md, possibly for days) is checked first and
returns `'fatal'` without spending the attempt budget; every other retryable status
respects an UNCONDITIONAL attempt cap — `'exhausted'` at the final permitted attempt
regardless of whether Retry-After was present. Both refine
scripts/fetch-citations.py's 429-only, linear-backoff, header-only precedent: the shape
(try/except, branch on status, sleep, loop) transfers, the semantics do not.
"""
from __future__ import annotations

import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path

_BACKOFF_CAP_S = 60.0
_ANTHROPIC_SPEND_CAP_ERROR_CODE = "enforced_spend_limit_reached"

# Matches `key=`, `api_key=`, or `access_token=` query params, case-insensitively,
# up to the next `&` or end of string. D-09: some vendors (Gemini) accept the key as
# a query param; mask_url() is the only URL form ever written to a JSONL record.
_KEY_PARAM_RE = re.compile(r"(?i)\b(key|api_key|access_token)=[^&]+")


def post_json(
    url: str, body: dict, headers: dict, timeout: int = 120
) -> tuple[int, dict, bytes, Message]:
    """POST `body` as JSON to `url` with `headers`. Single-attempt send.

    Returns (status, headers_dict, body_bytes, headers_message). `headers_message` is
    the original case-insensitive `http.client.HTTPMessage` (`.get()` works regardless
    of the vendor's header casing, which a plain `dict` conversion throws away);
    `headers_dict` is a plain-dict copy of the same data, convenient for JSON
    serialization into a log record.

    Never raises on a 4xx/5xx — `urllib.error.HTTPError` is itself a file-like object,
    so `.read()` returns the error body even though `urlopen()` raised. Also never
    raises on a connection-level failure (DNS, refused connection, TLS handshake,
    socket timeout) — `urllib.error.URLError` (HTTPError's parent, not narrowed to
    it), bare `OSError`, and `TimeoutError` are all caught and synthesized into a
    `status=0` result so `send_with_retry`/`runner.py` can classify and log it
    instead of the whole probe-set run crashing on one transient network blip
    (CR-01, phase-09 code review 2026-09-01).
    """
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), e.headers
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # No HTTP response exists at all — status=0 is a sentinel `retry_decision`
        # treats as retryable-shaped (same branch as a 5xx), never as a `verdict`.
        body_bytes = json.dumps(
            {"error": {"type": "connection_error", "message": str(e)}}
        ).encode()
        return 0, {}, body_bytes, Message()


def _is_anthropic_spend_cap(body_bytes: bytes) -> bool:
    """True only when the response body carries Anthropic's machine-readable
    spend-limit signal, nested at `error.details.error_code` (RESEARCH.md §
    Anthropic — Messages family). Never raises on a malformed, non-JSON, or
    differently-shaped body — a body that doesn't carry this exact shape simply isn't
    a spend-cap signal, not a parse error worth surfacing from a pure function."""
    try:
        parsed = json.loads(body_bytes)
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
        return False
    if not isinstance(parsed, dict):
        return False
    error = parsed.get("error")
    if not isinstance(error, dict):
        return False
    details = error.get("details")
    return isinstance(details, dict) and details.get("error_code") == _ANTHROPIC_SPEND_CAP_ERROR_CODE


def _retry_after_wait(headers_message: Message | None) -> float | None:
    """Read `Retry-After` through the case-insensitive `Message` object's `.get()` —
    never a plain dict subscript, which loses that property. Returns None (never
    raises) when the header is absent or its value doesn't parse as a non-negative
    number, so the caller falls back to backoff instead of crashing on a malformed
    vendor header."""
    if headers_message is None:
        return None
    raw = headers_message.get("Retry-After")
    if raw is None:
        return None
    try:
        wait = float(raw)
    except (TypeError, ValueError):
        return None
    return wait if wait >= 0 else None


def _backoff_wait(attempt: int) -> float:
    """Exponential backoff with jitter, capped at `_BACKOFF_CAP_S` — used only when a
    retryable status carries no usable `Retry-After` (STACK.md's recommendation,
    RESEARCH.md's Design implication: `min(2 ** attempt + random.uniform(0, 1), 60)`).
    Grows with the attempt number and never exceeds the cap at any attempt index."""
    return min(2 ** attempt + random.uniform(0, 1), _BACKOFF_CAP_S)


def retry_decision(
    status: int,
    headers_message: Message | None,
    attempt: int,
    body_bytes: bytes,
    max_attempts: int,
) -> tuple[str, float]:
    """Pure, family-agnostic status-code-first classification (HARN-04) — the same
    function serves all three wire families; no vendor or family branches inside it.
    Returns a two-tuple `(action, wait_seconds)`. Actions: `'verdict'` (this attempt
    is the answer — record and classify it, zero retries spent), `'retry'` (sleep
    `wait_seconds` and try again), `'exhausted'` (retryable-shaped but the attempt cap
    is spent), `'fatal'` (retryable-shaped but a known unrecoverable condition — stop
    immediately without spending the retry budget).

    Classification order is load-bearing:
    1. A 2xx is a `'verdict'`.
    2. Every remaining 4xx that is NOT 429 is ALSO a `'verdict'`, with zero retries —
       HARN-04's whole discipline. Misfiling a 429 into this branch would corrupt
       Phase 11's contract matrix with a false rejection; this branch never even
       inspects the body for retryable-shaped signals, because non-429/5xx status
       codes are never retryable regardless of body content.
    3. A 429, any status >= 500, or `status == 0` (post_json's sentinel for a
       connection-level failure — no HTTP response exists at all: DNS, refused
       connection, TLS handshake, or socket timeout) is retryable-shaped.
       Anthropic's spend-cap 429 is checked FIRST, independent of the attempt count
       — it returns `'fatal'` without
       spending the retry budget, because it carries no `Retry-After` and "keeps
       failing until access resumes" (possibly for days); burning attempts on it
       wastes wall-clock time for zero benefit.
    4. The unconditional attempt cap is checked next — BEFORE any `Retry-After`
       lookup, so header presence never overrides the cap. A retryable status at the
       final permitted attempt is `'exhausted'` whether or not `Retry-After` was sent.
    5. Otherwise `'retry'`, with the wait taken verbatim from `Retry-After` when
       present and parseable, falling back to capped exponential backoff with jitter.
    """
    if 200 <= status < 300:
        return "verdict", 0.0

    retryable = status == 0 or status == 429 or status >= 500
    if not retryable:
        return "verdict", 0.0

    if status == 429 and _is_anthropic_spend_cap(body_bytes):
        return "fatal", 0.0

    if attempt >= max_attempts - 1:
        return "exhausted", 0.0

    wait = _retry_after_wait(headers_message)
    if wait is None:
        wait = _backoff_wait(attempt)
    return "retry", wait


def send_with_retry(
    url: str, body: dict, headers: dict, max_attempts: int = 5
) -> list[dict]:
    """Loop `post_json()`, consulting `retry_decision()` after each attempt, sleeping
    when told to, and returning the ORDERED list of attempt records — one entry per
    attempt, in attempt order, the terminal attempt last. Never raises on a vendor
    status; the caller (runner.py) reads the last entry's classification to decide
    what happened.

    Each attempt record carries: `n` (1-indexed attempt number), `status`,
    `retryable` (whether retry_decision classified this attempt's status as
    retryable-shaped, i.e. NOT a `'verdict'`), `action` (the retry_decision action for
    this attempt), `wait_s` (the wait applied before the NEXT attempt, None on the
    terminal attempt), `response_headers`, `response_body_raw`, and `at` (UTC
    timestamp). `runner.py` writes this list into the record's `attempts` array
    unchanged."""
    attempts: list[dict] = []
    for attempt in range(max_attempts):
        status, resp_headers_dict, body_bytes, resp_headers_msg = post_json(url, body, headers)
        at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            resp_body = json.loads(body_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError):
            resp_body = body_bytes.decode(errors="replace")

        action, wait = retry_decision(status, resp_headers_msg, attempt, body_bytes, max_attempts)
        retryable = action != "verdict"

        record = {
            "n": attempt + 1,
            "status": status,
            "retryable": retryable,
            "action": action,
            "wait_s": wait if action == "retry" else None,
            "response_headers": resp_headers_dict,
            "response_body_raw": resp_body,
            "at": at,
        }
        attempts.append(record)

        if action == "retry":
            time.sleep(wait)
            continue
        # verdict, exhausted, or fatal — all three are terminal for this probe.
        break

    return attempts


def load_keys(path: Path) -> dict[str, str]:
    """Read `~/.secrets/model-probes.env`, tolerating a leading `export `. Returns
    only the `PERSONAL_*` names mapped to their values. A value returned here must
    never be printed, logged, or written to a record — `auth_headers()` in an adapter
    is the only intended consumer."""
    keys: dict[str, str] = {}
    text = Path(path).read_text()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name.startswith("PERSONAL_"):
            keys[name] = value
    return keys


def mask_url(url: str) -> str:
    """Replace the value of any `key`, `api_key`, or `access_token` query parameter
    with a fixed placeholder. D-09: this is the only URL form ever written to a
    JSONL record."""
    return _KEY_PARAM_RE.sub(lambda m: f"{m.group(1)}=***", url)


def _hm(**kwargs: str) -> Message:
    """Build a case-insensitive `Message` object for a selftest fixture, converting
    `Retry_After='7'`-style keyword args (Python identifiers can't contain `-`) into
    `Retry-After: 7` headers — mirrors the shape `post_json()` hands `retry_decision`
    in real use, never a plain dict."""
    m = Message()
    for k, v in kwargs.items():
        m[k.replace("_", "-")] = v
    return m


def selftest() -> tuple[int, int]:
    """Runs `retry_decision()` as a PURE function against a synthetic case table — no
    sockets, no sleeping (`send_with_retry`'s own sleep/loop plumbing is exercised
    indirectly by `retry_decision`'s classification correctness, not re-tested here).
    Returns (cases_run, problems)."""
    problems = 0
    cases = 0

    spend_cap_body = json.dumps({
        "type": "error",
        "error": {
            "type": "rate_limit_error",
            "message": "spend limit reached",
            "details": {"error_code": _ANTHROPIC_SPEND_CAP_ERROR_CODE},
        },
        "request_id": "req_selftest",
    }).encode()

    # --- 200 -> verdict, zero wait ---
    cases += 1
    action, wait = retry_decision(200, _hm(), 0, b"{}", 5)
    if (action, wait) != ("verdict", 0.0):
        problems += 1
        print(f"FAIL retry_decision(200): expected ('verdict', 0.0), got {(action, wait)}", file=sys.stderr)

    # --- every other 4xx -> verdict, zero wait, zero retries (HARN-04's other half) ---
    for status in (400, 401, 403, 404, 413, 422):
        cases += 1
        action, wait = retry_decision(status, _hm(), 0, b"{}", 5)
        if (action, wait) != ("verdict", 0.0):
            problems += 1
            print(f"FAIL retry_decision({status}): expected ('verdict', 0.0), got {(action, wait)}", file=sys.stderr)

    # --- 429 with a numeric Retry-After -> retry, exactly that wait ---
    cases += 1
    action, wait = retry_decision(429, _hm(Retry_After="7"), 0, b"{}", 5)
    if action != "retry" or wait != 7.0:
        problems += 1
        print(f"FAIL retry_decision(429, Retry-After=7): expected ('retry', 7.0), got {(action, wait)}", file=sys.stderr)

    # --- 429 with Retry-After in different header letter-casing -> same wait ---
    cases += 1
    m = Message()
    m["retry-after"] = "7"  # lowercase, unlike the canonical "Retry-After" casing above
    action, wait = retry_decision(429, m, 0, b"{}", 5)
    if action != "retry" or wait != 7.0:
        problems += 1
        print(f"FAIL retry_decision(429, lowercase retry-after): expected ('retry', 7.0), got {(action, wait)}", file=sys.stderr)

    # --- 429 with no Retry-After -> retry, positive wait, never over the 60s cap ---
    cases += 1
    action, wait = retry_decision(429, _hm(), 0, b"{}", 5)
    if action != "retry" or not (0 < wait <= 60):
        problems += 1
        print(f"FAIL retry_decision(429, no header): expected retry with 0<wait<=60, got {(action, wait)}", file=sys.stderr)

    # --- 429 with an unparseable Retry-After -> falls back to backoff, never raises ---
    cases += 1
    action, wait = retry_decision(429, _hm(Retry_After="not-a-number"), 0, b"{}", 5)
    if action != "retry" or not (0 < wait <= 60):
        problems += 1
        print(f"FAIL retry_decision(429, unparseable header): expected retry with 0<wait<=60, got {(action, wait)}", file=sys.stderr)

    # --- 500, 502, 503, 529 -> retry ---
    for status in (500, 502, 503, 529):
        cases += 1
        action, _wait = retry_decision(status, _hm(), 0, b"{}", 5)
        if action != "retry":
            problems += 1
            print(f"FAIL retry_decision({status}): expected 'retry', got {action}", file=sys.stderr)

    # --- status=0 (post_json's connection-error sentinel, CR-01) -> retryable-shaped
    #     exactly like a 5xx, not a silent 'verdict' that would drop the probe ---
    cases += 1
    action, wait = retry_decision(0, _hm(), 0, b'{"error": {"type": "connection_error"}}', 5)
    if action != "retry":
        problems += 1
        print(f"FAIL retry_decision(0): expected 'retry', got {action}", file=sys.stderr)

    # --- status=0 at the final permitted attempt -> exhausted, same as any other
    #     retryable-shaped status, never crashes derive_terminal on an empty list ---
    cases += 1
    action, wait = retry_decision(0, _hm(), 4, b'{"error": {"type": "connection_error"}}', 5)
    if (action, wait) != ("exhausted", 0.0):
        problems += 1
        print(f"FAIL retry_decision(0, attempt=4): expected exhausted, got {(action, wait)}", file=sys.stderr)

    # --- post_json: a connection-level failure (unreachable host) is caught and
    #     synthesized as status=0, never propagates as an uncaught exception (CR-01) ---
    cases += 1
    try:
        status, resp_headers, body_bytes, _msg = post_json(
            "http://127.0.0.1:1/unreachable-port-for-selftest", {}, {}, timeout=2
        )
        if status != 0:
            problems += 1
            print(f"FAIL post_json(unreachable): expected status=0, got {status}", file=sys.stderr)
        parsed = json.loads(body_bytes)
        if not isinstance(parsed, dict) or "error" not in parsed:
            problems += 1
            print(f"FAIL post_json(unreachable): expected a synthesized error body, got {body_bytes!r}", file=sys.stderr)
    except Exception as e:
        problems += 1
        print(f"FAIL post_json(unreachable): raised {e!r}, must never raise on a connection-level failure", file=sys.stderr)

    # --- a retryable status at the final permitted attempt -> exhausted, WITH Retry-After ---
    cases += 1
    action, wait = retry_decision(429, _hm(Retry_After="7"), 4, b"{}", 5)
    if (action, wait) != ("exhausted", 0.0):
        problems += 1
        print(f"FAIL retry_decision(429, attempt=4, with header): expected exhausted, got {(action, wait)}", file=sys.stderr)

    # --- a retryable status at the final permitted attempt -> exhausted, WITHOUT Retry-After ---
    cases += 1
    action, wait = retry_decision(429, _hm(), 4, b"{}", 5)
    if (action, wait) != ("exhausted", 0.0):
        problems += 1
        print(f"FAIL retry_decision(429, attempt=4, no header): expected exhausted, got {(action, wait)}", file=sys.stderr)

    # --- a 429 carrying Anthropic's spend-limit signal -> fatal on the FIRST attempt,
    #     without consuming the retry budget (independent of the attempt cap check) ---
    cases += 1
    action, wait = retry_decision(429, _hm(), 0, spend_cap_body, 5)
    if (action, wait) != ("fatal", 0.0):
        problems += 1
        print(f"FAIL retry_decision(429, spend-cap body, attempt=0): expected fatal, got {(action, wait)}", file=sys.stderr)

    # --- the spend-cap signal is fatal even mid-run, not just at attempt 0 ---
    cases += 1
    action, wait = retry_decision(429, _hm(), 2, spend_cap_body, 5)
    if (action, wait) != ("fatal", 0.0):
        problems += 1
        print(f"FAIL retry_decision(429, spend-cap body, attempt=2): expected fatal, got {(action, wait)}", file=sys.stderr)

    # --- backoff wait grows with the attempt number and never exceeds the 60s cap ---
    cases += 1
    low = _backoff_wait(0)
    high = _backoff_wait(20)
    if not (1.0 <= low <= 2.0):
        problems += 1
        print(f"FAIL _backoff_wait(0): expected in [1.0, 2.0), got {low}", file=sys.stderr)
    if high != _BACKOFF_CAP_S:
        problems += 1
        print(f"FAIL _backoff_wait(20): expected the {_BACKOFF_CAP_S}s cap exactly, got {high}", file=sys.stderr)
    if not all(0 < _backoff_wait(a) <= _BACKOFF_CAP_S for a in range(15)):
        problems += 1
        print("FAIL _backoff_wait: a sampled attempt exceeded the 60s cap", file=sys.stderr)

    # --- _is_anthropic_spend_cap: malformed/non-JSON/non-dict bodies never raise ---
    cases += 1
    for bad_body in (b"not json", b"[]", b'{"error": "a string, not a dict"}', b""):
        try:
            if _is_anthropic_spend_cap(bad_body):
                problems += 1
                print(f"FAIL _is_anthropic_spend_cap({bad_body!r}): expected False", file=sys.stderr)
        except Exception as e:  # pragma: no cover - the whole point is this never raises
            problems += 1
            print(f"FAIL _is_anthropic_spend_cap({bad_body!r}): raised {e!r}, must never raise", file=sys.stderr)

    return cases, problems


def main() -> int:
    args = sys.argv[1:]
    if len(args) > 1 or (args and args[0] != "--selftest"):
        print("usage: client.py [--selftest]", file=sys.stderr)
        return 2

    if args and args[0] == "--selftest":
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    # Tiny manual smoke check: prints a masked example URL. client.py is imported by
    # runner.py in normal use — this is not part of the live probe path.
    print(mask_url("https://api.example.com/v1/x?api_key=SECRET123&other=1"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
