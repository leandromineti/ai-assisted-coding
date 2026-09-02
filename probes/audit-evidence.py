#!/usr/bin/env python3
"""probes/audit-evidence.py — D-05's fail-closed evidence privacy gate: the
tripwire-layer analog of probes/harness/runner.py's assert_no_secrets(), but for
the org/account-identifying content CLASS instead of a fixed list of loaded API
key values. runner.py already implements a STRUCTURAL exclusion for one slice of
this class (`_ORG_IDENTIFYING_RESPONSE_HEADERS`, filtered per-attempt before a
record is ever built) — this script is the missing tripwire LAYER: it scans the
finished evidence and catches anything the structural filter missed, whether
because a header name was never added to that denylist or because the leak takes
a shape no fixed denylist could anticipate.

Scans every `probes/raw/*.jsonl` record plus `probes/ledger.jsonl`, read-only,
for two rule classes:
  - DENYLIST_FIELD_NAMES: header/JSON-key NAMES that must never appear anywhere
    in a record, matched case-insensitively at any depth.
  - PII_PATTERNS: compiled regexes for a shape class (emails, vendor
    API-key-shaped fragments, generic organization/account identifier field
    names) — each entry carries a short rule name used in the finding output.

Exit codes: 0 clean, 1 non-empty findings recorded, 2 bad invocation (an
unrecognized flag, or a raw-dir/ledger path argument that is not a usable
path at all). A file that exists but cannot be READ, or a line that is not
valid JSON, is a FINDING (exit 1 territory), never a silent skip — the one
documented exception is a file's own final line being a truncated partial
record from a killed process, tolerated exactly like
probes/harness/runner.py's seen_probe_ids() already tolerates it.

    python3 probes/audit-evidence.py --check [--raw-dir DIR] [--ledger PATH]
    python3 probes/audit-evidence.py --selftest

Wired into CLAUDE.md's four-command pre-commit lint battery as of plan 11-06,
which also closed the human-reviewed denylist-completeness pass against all 8
vendors' real captured response headers (WR-04, phase-09 code review) — see
DENYLIST_FIELD_NAMES' own per-entry annotations below for the observed-live/
documented-guess status of every name, each dated and sourced.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

PROBES_DIR = Path(__file__).resolve().parent
DEFAULT_RAW_DIR = PROBES_DIR / "raw"
DEFAULT_LEDGER_PATH = PROBES_DIR / "ledger.jsonl"

# fixtures.py lives in probes/harness/, a sibling directory to this script —
# not importable with a bare `import fixtures` from probes/ itself, so the
# harness directory is added to sys.path first (the same shape
# scripts/classify-probes.py already uses to reach probes/harness/ modules).
sys.path.insert(0, str(PROBES_DIR / "harness"))
import fixtures  # noqa: E402 — sys.path must be extended first, see above


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path this
    repo's config loaders and generators all share (runner.py's, inventory-
    to-sets.py's, classify-probes.py's `_fail` idiom, matched exactly)."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


# Header/JSON-key NAMES that must never appear anywhere in a record, matched
# case-insensitively against every recorded header name and every JSON key at
# any depth.
#
# CLOSED 2026-09-02, Phase 11 plan 11-06, WR-04 (phase-09 code review): every
# entry below is now annotated with its own status — OBSERVED-LIVE (a named
# vendor and date it was actually seen on the wire) or a DOCUMENTED GUESS
# (never seen, with the surface searched, per methodology rule 1b — an
# absence is only as good as the surface you searched). The per-vendor
# response-header inventory this review is read against was derived by
# command, not hand-typed:
#
#   python3 -c "import json,glob,pathlib,collections; v=collections.defaultdict(set); \
#   [v[json.loads(l)['vendor']].add(k.lower()) for p in glob.glob('probes/raw/*.jsonl') \
#   for l in pathlib.Path(p).read_text().splitlines() if l.strip() \
#   for a in json.loads(l).get('attempts',[]) for k in (a.get('response_headers') or {})]; \
#   print(len(v), {k: sorted(s) for k,s in v.items()})"
#
# → 8 vendors, 359 captured raw records total (all 8 present as of 2026-09-02;
# exact per-vendor line counts: anthropic 80, dseek 23, gemini 20, kimi 29,
# openai 46, qwen 93, xai 34, zai 34). Every header name across all 8 vendors'
# real captured evidence was read and classified into benign / org-account-
# identifying / uncertain; this review found ZERO new org/account-identifying
# names beyond what was already here — the two closest candidates, xAI's
# `x-data-retention`/`x-zero-data-retention` (a boolean data-retention POLICY
# flag, not an identifier naming who the account is), were classified benign,
# the same class as `x-gemini-service-tier`'s subscription-tier flag — neither
# names an organization/workspace/project/team/tenant/user. The one real gap
# this review found was NOT a missing header name at all — it was
# `set-cookie` (below), already present in runner.py's structural filter but
# never mirrored into this scanner (a parity gap, not a coverage gap).
#
# - `openai-organization`, `openai-project`, `anthropic-organization-id`,
#   `x-organization-id`: DOCUMENTED GUESSES, never observed on the wire.
#   Searched: all 359 captured records / 8 vendors as of 2026-09-02 (the
#   command above) — none of these four names appears anywhere in captured
#   evidence. This is expected if they are ever sent, since runner.py's
#   structural filter (`_ORG_IDENTIFYING_RESPONSE_HEADERS`) drops them before
#   a record is ever built — this scanner's job is the second, independent
#   layer that catches a name the filter doesn't yet know about, not to prove
#   a filtered name was never sent.
# - `anthropic-workspace-id`: OBSERVED LIVE at Anthropic, 2026-09-01 (Phase
#   9's tracer probe, the finding that motivated D-05's whole scanner). Never
#   seen again since — structurally filtered from every one of anthropic's 80
#   captured records that followed.
# - `msh-org-id`, `msh-uid`, `msh-project-id`, `msh-gid`: OBSERVED LIVE at
#   Moonshot AI (Kimi), 2026-09-01 (Phase 9's smoke-test record, probe_id
#   `kimi-k3--baseline--none--default--b3540b5c`), found reading
#   probes/raw/kimi.jsonl's real captured record end to end during Phase 11
#   plan 11-03's authoring of this scanner — WR-04's exact gap, closed for
#   this vendor in 11-03. The one pre-existing record that leaked them was
#   repaired (redacted in place) during THIS plan (11-06) — see the Run log
#   entry in probes/PREREGISTRATION.md. `msh-request-id` and
#   `x-msh-trace-id` are request-tracing, not account-identifying, and are
#   kept — the same distinction drawn for every other vendor's rate-limit/
#   request-id headers.
# - `set-cookie`: OBSERVED LIVE at Cloudflare (openai, kimi — the `__cf_bm`
#   bot-management cookie) and Alibaba Cloud WAF (qwen, zai — the `acw_tc`
#   anti-crawler cookie), 2026-09-01, Phase 11 plan 11-04's stage-1/2
#   calibration firing. Already added to runner.py's structural filter
#   (`_ORG_IDENTIFYING_RESPONSE_HEADERS`) in 11-04, but never mirrored into
#   THIS scanner's own denylist until now — this review's own set-parity
#   check (this task's own `<verify>`) is what caught the gap. Three
#   additional stale records this review found still carrying it (predating
#   11-04's fix, missed by that task's own redaction pass) were repaired
#   (redacted in place) during THIS plan — see the Run log entry.
DENYLIST_FIELD_NAMES = frozenset({
    "openai-organization",
    "openai-project",
    "anthropic-organization-id",
    "anthropic-workspace-id",
    "x-organization-id",
    "msh-org-id",
    "msh-uid",
    "msh-project-id",
    "msh-gid",
    "set-cookie",
})

# The two named exemptions in this file (CLAUDE.md § Growing the deny-list: an
# exemption is a named constant with a written reason, never a loosened
# pattern — the vendor-key-fragment REGEX itself is never touched by either
# exemption below; only a specific, documented VALUE or FIELD NAME is excluded
# from it). MODAL-01's image payload is a long base64 string sent verbatim in
# every image-input request body — PII_PATTERNS' vendor-key-fragment rule
# below deliberately includes a generic long-base64-blob shape (the same shape
# a real leaked key VALUE would have), so without this exemption the scanner
# would fire on all 12 image records for carrying exactly the fixture payload
# this repo itself generated, never a real secret.
_EXEMPT_KEY_FRAGMENT_VALUES = frozenset({fixtures.TINY_PNG_BASE64})

# Second named exemption, added 2026-09-02, Phase 11 plan 11-06 (WR-04's
# denylist/pattern-completeness review — WINDOWS.md #3/#5/#6). Three
# vendor-documented response fields happen to be long base64-shaped strings
# that trip the SAME generic vendor-key-fragment pattern above, none of them a
# secret: Anthropic's `signature` (a thinking-content-block integrity token,
# present on every accepted response with thinking active), Gemini's
# `thoughtSignature` (a documented reasoning-continuation token), and
# DeepSeek's `X-Amz-Cf-Id` response header (a CloudFront per-request routing/
# tracing id, the same non-identifying class as the already-kept
# request-id/msh-request-id headers). Exempted BY FIELD NAME, not by value —
# unlike the tiny-PNG constant above (one fixed, known value), these fields'
# VALUES differ on every response, so only a name-scoped exemption can work;
# the pattern itself keeps firing on a base64-shaped blob under any OTHER key,
# including a key named `signature`/`thoughtSignature`/`x-amz-cf-id` that
# happens to belong to a DIFFERENT vendor or a genuinely new leaked value —
# scan_record() re-checks the value's shape every time, this only narrows
# WHICH key names are exempt, never widens what counts as a match.
_EXEMPT_KEY_FRAGMENT_FIELD_NAMES = frozenset({
    "signature",
    "thoughtsignature",
    "x-amz-cf-id",
})

# Pattern-class rules (D-05): compiled regexes, each paired with a short rule
# NAME used in the finding output so a reader knows which rule fired. Run
# against each record's own serialized JSON text — the key-fragment/account-
# identifier-shape rules exist precisely because a fixed NAME denylist (above)
# can only ever cover names already observed or guessed; a shape-based pattern
# catches an unanticipated field wherever it appears, at the cost of needing
# the one named exemption above.
PII_PATTERNS = (
    ("email-address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    # Vendor API-key-shaped fragments: known vendor prefixes this harness's
    # own PERSONAL_*_KEY env vars imply (Anthropic sk-ant-*, Google AIza*,
    # xAI xai-*), plus a generic long base64-charset blob — the same shape any
    # of the eight vendors' actual key VALUES has, independent of vendor.
    # This is the pattern the tiny-PNG exemption above protects against.
    ("vendor-key-fragment", re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[A-Za-z0-9_-]{16,}|xai-[A-Za-z0-9_-]{16,}|"
        r"[A-Za-z0-9+/]{40,}={0,2})\b"
    )),
    # Generic organization/account/workspace/customer/tenant identifier field
    # NAME shapes, matched against serialized `"<key>":` text — catches an
    # unanticipated vendor field (like Msh-Org-Id above, before it was added
    # to DENYLIST_FIELD_NAMES) that the fixed-name denylist hasn't been told
    # about yet, by matching the SHAPE of the key rather than one vendor's
    # exact spelling of it.
    ("account-identifier-shape", re.compile(
        r'"[^"]*\b(?:org(?:ani[sz]ation)?|workspace|account|customer|tenant)[-_]?(?:id)?\b[^"]*"\s*:',
        re.IGNORECASE,
    )),
)


def _walk_field_names(obj):
    """Yield every mapping-key NAME (lowercased) found at any depth in `obj`,
    plus every string element of a list found under a key literally named
    `headers_sent` (build_record's own field allowlist stores SENT header
    names as a list of strings, not a dict — the one shape DENYLIST_FIELD_NAMES
    needs a second walk rule for). Pure, read-only, never mutates `obj`."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, str):
                yield key.lower()
            if key == "headers_sent" and isinstance(value, list):
                for h in value:
                    if isinstance(h, str):
                        yield h.lower()
            yield from _walk_field_names(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_field_names(item)


def _walk_string_values(obj, parent_key: str | None = None):
    """Yield (parent_key_lower_or_none, value) for every STRING leaf found at
    any depth in `obj`, carrying the nearest enclosing dict key (lowercased) —
    a list element inherits its containing dict's key (there is no per-element
    key inside a list). Pure, read-only, never mutates `obj`. This is what lets
    vendor-key-fragment's exemption be scoped BY FIELD NAME (see
    `_EXEMPT_KEY_FRAGMENT_FIELD_NAMES` above) — `_walk_field_names` above only
    yields key names, not the (key, value) pairing this needs."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_key = key.lower() if isinstance(key, str) else parent_key
            yield from _walk_string_values(value, next_key)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_string_values(item, parent_key)
    elif isinstance(obj, str):
        yield (parent_key, obj)


def scan_record(record: dict) -> list[str]:
    """Pure: classify ONE parsed JSON record against both rule classes.
    Returns a list of rule names that fired (empty when clean). Never edits
    `record`."""
    findings: list[str] = []

    for name in _walk_field_names(record):
        if name in DENYLIST_FIELD_NAMES:
            findings.append(f"denylisted-field-name:{name}")

    # vendor-key-fragment is evaluated per STRING VALUE, with its nearest
    # enclosing key name available, so a documented field can be exempted BY
    # NAME (see _EXEMPT_KEY_FRAGMENT_FIELD_NAMES) without touching the
    # regex — the same base64-blob shape under any other key still fires.
    vendor_key_fragment_pattern = next(
        pattern for rule_name, pattern in PII_PATTERNS if rule_name == "vendor-key-fragment"
    )
    for key, value in _walk_string_values(record):
        for match in vendor_key_fragment_pattern.finditer(value):
            fragment = match.group(0)
            if fragment in _EXEMPT_KEY_FRAGMENT_VALUES:
                continue
            if key in _EXEMPT_KEY_FRAGMENT_FIELD_NAMES:
                continue
            findings.append("vendor-key-fragment")

    serialized = json.dumps(record)
    for rule_name, pattern in PII_PATTERNS:
        if rule_name == "vendor-key-fragment":
            continue  # handled per-value above, not on the serialized blob
        for match in pattern.finditer(serialized):
            findings.append(rule_name)

    return findings


def scan_file(path: Path) -> list[dict]:
    """Scan one JSONL file. Returns a list of finding dicts:
    {"file": str(path), "line": int | None, "probe_id": str | None,
    "rule": str}. Fail-closed: a file that cannot be read at all is ONE
    finding naming the file and the read error; a line that fails to parse as
    JSON is ONE finding naming the file and line number — EXCEPT the file's
    own FINAL line, which may be a truncated partial record from a killed
    process (the one documented exception probes/harness/runner.py's
    seen_probe_ids() already tolerates, applied identically here). Read-only:
    never writes to `path`."""
    findings: list[dict] = []
    try:
        text = path.read_text()
    except OSError as e:
        return [{"file": str(path), "line": None, "probe_id": None, "rule": f"unreadable-file:{e}"}]

    lines = text.splitlines()
    for i, raw_line in enumerate(lines):
        line_no = i + 1
        is_final_line = i == len(lines) - 1
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            if is_final_line:
                # Truncated trailing line from a killed process — the one
                # documented exception, tolerated rather than reported.
                continue
            findings.append({"file": str(path), "line": line_no, "probe_id": None, "rule": "malformed-json-line"})
            continue
        probe_id = record.get("probe_id") if isinstance(record, dict) else None
        for rule in scan_record(record):
            findings.append({"file": str(path), "line": line_no, "probe_id": probe_id, "rule": rule})
    return findings


def scan_evidence(raw_dir: Path = DEFAULT_RAW_DIR, ledger_path: Path = DEFAULT_LEDGER_PATH) -> list[dict]:
    """Scan every `raw_dir/*.jsonl` file plus `ledger_path` (if present).
    Read-only. A raw_dir/ledger_path that does not exist yet is zero findings
    — no evidence captured yet is trivially clean, not a failure — but a path
    that exists and fails to open is a finding via scan_file()'s own
    fail-closed rule above."""
    findings: list[dict] = []
    raw_dir = Path(raw_dir)
    if raw_dir.is_dir():
        for path in sorted(raw_dir.glob("*.jsonl")):
            findings.extend(scan_file(path))
    ledger_path = Path(ledger_path)
    if ledger_path.exists():
        findings.extend(scan_file(ledger_path))
    return findings


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        line = f["line"] if f["line"] is not None else "?"
        pid = f["probe_id"] if f["probe_id"] is not None else "?"
        print(f"FINDING {f['file']}:{line} probe_id={pid} rule={f['rule']}", file=sys.stderr)


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems). Fixtures are
    written to a tempfile.TemporaryDirectory() per case — the house style
    every fail-loud loader/generator in this repo already uses for its
    file-loading tests."""
    problems = 0
    cases = 0

    # --- a denylisted header name is reported, naming that rule ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--aaaaaaaa",
                "attempts": [{"response_headers": {"anthropic-workspace-id": "wrk_should_be_flagged"}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        rules = [f["rule"] for f in findings]
        if not any(r.startswith("denylisted-field-name:anthropic-workspace-id") for r in rules):
            problems += 1
            print("FAIL selftest: a denylisted header name was not reported", file=sys.stderr)
        elif not any(f["probe_id"] == "x--baseline--none--default--aaaaaaaa" for f in findings):
            problems += 1
            print("FAIL selftest: a finding did not carry the record's probe_id", file=sys.stderr)

    # --- an email address is reported ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--bbbbbbbb",
                "attempts": [{"response_body_raw": {"note": "contact ops@example.com for help"}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if not any(f["rule"] == "email-address" for f in findings):
            problems += 1
            print("FAIL selftest: an email address was not reported", file=sys.stderr)

    # --- a key-fragment-shaped value is reported ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--cccccccc",
                "attempts": [{"response_body_raw": {"leaked": "sk-ant-not-a-real-key-0000000000000000"}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if not any(f["rule"] == "vendor-key-fragment" for f in findings):
            problems += 1
            print("FAIL selftest: a vendor-key-shaped fragment was not reported", file=sys.stderr)

    # --- a base64-shaped value under a documented, named-exempt field
    #     (Anthropic's `signature`, Gemini's `thoughtSignature`, DeepSeek's
    #     `X-Amz-Cf-Id`) produces NO finding — the second named exemption,
    #     matched case-insensitively by key name (added 2026-09-02, plan
    #     11-06, WR-04/WINDOWS.md #3/#5/#6) ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--12121212",
                "attempts": [{
                    "response_body_raw": {"content": [{"type": "thinking", "signature": "A" * 60}]},
                    "response_headers": {"X-Amz-Cf-Id": "B" * 60},
                }],
            }) + "\n"
        )
        (raw / "vendor2.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--13131313",
                "attempts": [{"response_body_raw": {"candidates": [{"content": {"parts": [
                    {"thoughtSignature": "C" * 60}
                ]}}]}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if findings:
            problems += 1
            print(f"FAIL selftest: a named-exempt field's base64-shaped value was reported: {findings}", file=sys.stderr)

    # --- the SAME base64-shaped value under an UNRELATED key, even sitting
    #     right next to an exempt field in the same record, STILL fires —
    #     proves the field-name exemption narrows by name only, never widens
    #     what counts as a match under any other key ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--14141414",
                "attempts": [{"response_body_raw": {"content": [
                    {"type": "thinking", "signature": "A" * 60},
                    {"type": "other", "unrelated_field": "D" * 60},
                ]}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if not any(f["rule"] == "vendor-key-fragment" for f in findings):
            problems += 1
            print("FAIL selftest: a base64-shaped value under a non-exempt key sitting beside an exempt field was not reported", file=sys.stderr)

    # --- a record whose only long base64 run is fixtures.TINY_PNG_BASE64
    #     produces NO finding — the one named exemption ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--image-input--content-block--default--dddddddd",
                "request": {"body": {"messages": [{"content": [
                    {"type": "image", "source": {"data": fixtures.TINY_PNG_BASE64}}
                ]}]}},
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if findings:
            problems += 1
            print(f"FAIL selftest: the exempt tiny-PNG payload was reported as a finding: {findings}", file=sys.stderr)

    # --- a clean record is not reported ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({
                "probe_id": "x--baseline--none--default--eeeeeeee",
                "vendor": "anthropic",
                "attempts": [{"response_headers": {"request-id": "req_abc", "retry-after": "5"}}],
            }) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if findings:
            problems += 1
            print(f"FAIL selftest: a clean record was reported as a finding: {findings}", file=sys.stderr)

    # --- an unreadable/malformed line is reported — EXCEPT the documented
    #     truncated-final-line exception, which is tolerated, not reported ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        (raw / "vendor.jsonl").write_text(
            json.dumps({"probe_id": "x--baseline--none--default--ffffffff"}) + "\n"
            + "{not valid json, and not the final line\n"
            + json.dumps({"probe_id": "x--baseline--none--default--00000000"}) + "\n"
        )
        findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
        if not any(f["rule"] == "malformed-json-line" and f["line"] == 2 for f in findings):
            problems += 1
            print("FAIL selftest: a malformed non-final JSON line was not reported", file=sys.stderr)

        truncated = Path(td) / "raw2"
        truncated.mkdir()
        (truncated / "vendor.jsonl").write_text(
            json.dumps({"probe_id": "x--baseline--none--default--11111111"}) + "\n"
            + '{"probe_id": "x--baseline--none--default--truncat'
        )
        findings2 = scan_evidence(truncated, Path(td) / "no-ledger.jsonl")
        if any(f["rule"] == "malformed-json-line" for f in findings2):
            problems += 1
            print("FAIL selftest: a truncated FINAL line was reported instead of tolerated", file=sys.stderr)

    # --- an unreadable file (not merely absent) is one finding, never a
    #     silent skip ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.mkdir()
        unreadable = raw / "vendor.jsonl"
        unreadable.write_text(json.dumps({"probe_id": "x"}) + "\n")
        unreadable.chmod(0o000)
        try:
            findings = scan_evidence(raw, Path(td) / "no-ledger.jsonl")
            if not any(f["rule"].startswith("unreadable-file") for f in findings):
                problems += 1
                print("FAIL selftest: an unreadable file was silently skipped instead of reported", file=sys.stderr)
        finally:
            unreadable.chmod(0o644)

    # --- a missing raw_dir/ledger_path is zero findings, never a crash —
    #     absence of evidence is trivially clean, not a failure ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        missing_raw = Path(td) / "does-not-exist"
        missing_ledger = Path(td) / "no-ledger.jsonl"
        findings = scan_evidence(missing_raw, missing_ledger)
        if findings:
            problems += 1
            print(f"FAIL selftest: a missing raw_dir/ledger produced findings instead of an empty list: {findings}", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="audit-evidence.py",
        usage="audit-evidence.py --check [--raw-dir DIR] [--ledger PATH] | --selftest",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--raw-dir", dest="raw_dir", default=str(DEFAULT_RAW_DIR))
    parser.add_argument("--ledger", dest="ledger", default=str(DEFAULT_LEDGER_PATH))
    args = parser.parse_args()

    if args.check and args.selftest:
        print("usage: audit-evidence.py --check [--raw-dir DIR] [--ledger PATH] | --selftest", file=sys.stderr)
        return 2

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if args.check:
        findings = scan_evidence(Path(args.raw_dir), Path(args.ledger))
        _print_findings(findings)
        print(f"{len(findings)} problem(s)")
        return 1 if findings else 0

    print("usage: audit-evidence.py --check [--raw-dir DIR] [--ledger PATH] | --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
