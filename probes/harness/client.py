#!/usr/bin/env python3
"""probes/harness/client.py — the harness's stdlib HTTP transport and single auth
choke point (D-09). No vendor SDK, no third-party HTTP or retry library is imported
here — STACK.md already vetted and rejected each candidate; SDKs normalize away the
very asymmetries this instrument measures.

    python3 probes/harness/client.py    # tiny manual smoke check of mask_url()

post_json() never raises on a 4xx/5xx response — the harness needs the vendor's error
body verbatim (D-09's verbatim-capture requirement), which scripts/fetch-citations.py's
existing retry-loop precedent never needed (it only inspected `.code`). A single-attempt
send is all plan 09-01 needs; the retry loop lands in plan 09-02, structured so it can
wrap this function without moving auth attachment.

load_keys() returns key VALUES into a single choke point (auth_headers() in each
adapter is the only intended consumer) — nothing downstream of this function may print,
log, or write a value to disk (T-09-01/T-09-02).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path

# Matches `key=`, `api_key=`, or `access_token=` query params, case-insensitively,
# up to the next `&` or end of string. D-09: some vendors (Gemini) accept the key as
# a query param; mask_url() is the only URL form ever written to a JSONL record.
_KEY_PARAM_RE = re.compile(r"(?i)\b(key|api_key|access_token)=[^&]+")


def post_json(
    url: str, body: dict, headers: dict, timeout: int = 60
) -> tuple[int, dict, bytes, Message]:
    """POST `body` as JSON to `url` with `headers`. Single-attempt send.

    Returns (status, headers_dict, body_bytes, headers_message). `headers_message` is
    the original case-insensitive `http.client.HTTPMessage` (`.get()` works regardless
    of the vendor's header casing, which a plain `dict` conversion throws away);
    `headers_dict` is a plain-dict copy of the same data, convenient for JSON
    serialization into a log record.

    Never raises on a 4xx/5xx — `urllib.error.HTTPError` is itself a file-like object,
    so `.read()` returns the error body even though `urlopen()` raised.
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


def main() -> int:
    """Tiny manual smoke check: prints a masked example URL. client.py is imported by
    runner.py in normal use — this is not part of the live probe path."""
    print(mask_url("https://api.example.com/v1/x?api_key=SECRET123&other=1"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
