#!/usr/bin/env python3
"""probes/check-docs-claims.py — the fail-closed validator for
probes/docs-claims.yaml (D-03), the hand-kept first-party vendor-documentation
claims registry (D-02). Sibling of probes/audit-evidence.py: same three-layer
scan split (pure per-record classify -> per-file finding dicts -> top-level
entry point), same `_fail()`/`--check`/`--selftest` argparse shape. Unlike
audit-evidence.py (JSONL, no completeness notion), this validator ALSO checks
COMPLETENESS: every (probes/inventory.yaml row id x probes/harness/models.yaml
vendor) pair must have exactly one claim — the expected pair universe is
computed from those two files at run time, never hand-typed (the exact
discipline whose absence let scripts/classify-probes.py's CLASSIFIED_HEADER go
stale, RESEARCH.md Pitfall 1).

    python3 probes/check-docs-claims.py --check
    python3 probes/check-docs-claims.py --selftest

Exit codes: 0 clean, 1 findings recorded (--check/--selftest only), 2 bad
invocation (no flag, both flags, or a required input file missing/malformed).
"""
from __future__ import annotations

import argparse
import datetime
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yaml

PROBES_DIR = Path(__file__).resolve().parent
DOCS_CLAIMS_PATH = PROBES_DIR / "docs-claims.yaml"
INVENTORY_PATH = PROBES_DIR / "inventory.yaml"
MODELS_PATH = PROBES_DIR / "harness" / "models.yaml"
PDF_DIR = PROBES_DIR / "docs-pdf"


def _fail(code: int, msg: str) -> None:
    """Print a diagnostic and raise SystemExit(code) — the fail-loud path this
    repo's config loaders and generators all share (probes/audit-evidence.py's,
    runner.py's, inventory-to-sets.py's, classify-probes.py's `_fail` idiom,
    matched exactly)."""
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _load_yaml(path: Path, required_key: str) -> dict:
    """Fail-loud YAML loader shared by every input this module reads — never a
    silent default on a missing file, malformed YAML, or a missing top-level
    key (scripts/build-probe-matrix.py:77-88, copied verbatim)."""
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


# Closed `documented_status` vocabulary (D-02/DOCP-01). `documented` — the page
# states the parameter's contract. `absent-from-docs` — the parameter does not
# appear anywhere on the searched surface (rule 1b: `searched_surface` is
# REQUIRED). `docs-silent` — the parameter is listed but the page states
# nothing about range/default/conditionality (`searched_surface` also
# REQUIRED — the row was found, but its contract facets were not).
DOCUMENTED_STATUSES = frozenset({"documented", "absent-from-docs", "docs-silent"})

# The six facet fields a `documented` claim must carry at least one non-null
# value among — a `quote` alone (prose) is not itself a facet; DOCP-01's own
# must_haves truth: "a quote alone does not satisfy the >=1-non-null-facet
# rule."
FACET_FIELDS = (
    "documented_name",
    "documented_type",
    "documented_range",
    "documented_allowed_values",
    "documented_default",
    "conditionality",
)

# First-party docs domain(s) per vendor (DOCP-03), one dated entry per vendor
# with the reason inline. Matched by `host_is_first_party()` below on a LABEL
# BOUNDARY (host equals the domain, or ends with "." + domain) — never a bare
# suffix test, which would admit a lookalike registration
# (e.g. "evilopenai.com" ending in "openai.com" as a bare substring).
#
# anthropic: claude.com — the product-docs brand domain OpenAI-style migration
#   this repo already standardized on (probes/inventory.yaml's own `source:`
#   fields); anthropic.com — the corporate/API-key domain, kept as a first-
#   party fallback.
# openai: openai.com only, matched as a domain SUFFIX so it admits BOTH
#   `platform.openai.com` and `developers.openai.com` — RESEARCH.md Pitfall 2:
#   `platform.openai.com` 403'd a plain fetch this phase, `developers.openai.com`
#   rendered cleanly and is this phase's actual source; an exact-host allowlist
#   would reject a future legitimate citation of either subdomain.
# gemini: `ai.google.dev` ONLY — the Gemini Developer API's own docs domain.
#   Deliberately excludes `cloud.google.com` (Vertex AI, a DIFFERENT product
#   with different parameters/auth/quota, RESEARCH.md Pitfall 7) and a bare
#   `google.com` (would also admit Vertex AI and everything else Google ships).
# xai: x.ai — docs.x.ai is this vendor's one documented API-reference domain.
# dseek: deepseek.com — api-docs.deepseek.com is this vendor's docs subdomain.
# kimi: kimi.ai (platform.kimi.ai, this phase's actual source) and moonshot.ai
#   (the API host's own domain, RESEARCH.md/models.yaml: api.moonshot.ai) —
#   both first-party, distinct domains for the same maker (Moonshot AI).
# zai: z.ai — docs.z.ai is this vendor's docs subdomain.
# qwen: alibabacloud.com AND qwencloud.com — settled 2026-09-02 by an owner
#   decision at plan 11.1-03's Task 2 blocking-human checkpoint (reply, verbatim:
#   "add-qwencloud"). `docs.qwencloud.com` carries no explicit ownership
#   sentence of its own, but a live re-check of its footer/consent bundle
#   resolves the qwencloud-tenant copyright to "Intelligent Cloud Computing
#   (Singapore) Private Limited", lists aliyun/alibabacloud/qwencloud as sibling
#   tenants, calls a consent API hosted on www.alibabacloud.com, and rides
#   Alibaba CDN/analytics — inferred shared-Alibaba ownership (evidence grade:
#   inferred-from-plumbing, not a direct attribution statement), accepted by
#   owner decision rather than an independently confirmed fact. It also matches
#   `inventory.yaml`'s existing `source:` citations for the qwen-repetition-penalty
#   and Qwen thinking-toggle rows and the `dashscope-intl.aliyuncs.com` endpoints
#   the harness actually calls. `alibabacloud.com` remains admitted too — both
#   domains are first-party for this vendor from here on.
FIRST_PARTY_DOMAINS: dict[str, tuple[str, ...]] = {
    "anthropic": ("claude.com", "anthropic.com"),
    "openai": ("openai.com",),
    "gemini": ("ai.google.dev",),
    "xai": ("x.ai",),
    "dseek": ("deepseek.com",),
    "kimi": ("kimi.ai", "moonshot.ai"),
    "zai": ("z.ai",),
    "qwen": ("alibabacloud.com", "qwencloud.com"),
}


def host_is_first_party(host: str, domain: str) -> bool:
    """A label-boundary match: `host` equals `domain`, or `host` ends with
    "." + `domain`. Deliberately NOT a bare suffix test (`host.endswith(domain)`
    alone) — that would admit a lookalike registration like "evilopenai.com"
    for domain "openai.com" (T-11.1-03, DOCP-03's whole guarantee rests on this
    one predicate)."""
    host = host.lower()
    domain = domain.lower()
    return host == domain or host.endswith("." + domain)


def _load_inventory_ids(inventory: dict) -> set[str]:
    return {row["id"] for row in inventory["params"]}


def _load_vendors(models: dict) -> set[str]:
    return {m["vendor"] for m in models["models"]}


def check_claim(claim: dict, *, inventory_ids: set[str], vendors: set[str], source_ids: set[str]) -> list[str]:
    """Pure: classify ONE claim dict. Returns the list of every rule name that
    fired (collecting ALL violated rules — never returns at the first,
    DOCP-02/ordering must_haves truth: a claim breaking two rules produces two
    findings, both named). Never mutates `claim`."""
    findings: list[str] = []

    param = claim.get("param")
    vendor = claim.get("vendor")
    status = claim.get("documented_status")
    source_ref = claim.get("source_ref")

    if param not in inventory_ids:
        findings.append("unknown-param")
    if vendor not in vendors:
        findings.append("unknown-vendor")
    if status not in DOCUMENTED_STATUSES:
        findings.append("unrecognized-documented-status")

    if status == "documented":
        if not claim.get("quote"):
            findings.append("documented-missing-quote")
        if not any(claim.get(f) is not None for f in FACET_FIELDS):
            findings.append("documented-missing-facet")
    elif status in ("absent-from-docs", "docs-silent"):
        surface = claim.get("searched_surface")
        if not surface or not str(surface).strip():
            findings.append("missing-searched-surface")
    # An unrecognized status already fired unrecognized-documented-status above
    # and falls through to neither branch — never guessed into one.

    if source_ref not in source_ids:
        findings.append("dangling-source-ref")

    return findings


def check_source(source: dict) -> list[str]:
    """Pure: classify ONE `sources:` entry. Returns every violated rule name
    (never returns at the first)."""
    findings: list[str] = []

    if source.get("id") is None:
        findings.append("missing-source-id")

    if source.get("first_party") is not True:
        findings.append("not-first-party")

    vendor = source.get("vendor")
    url = str(source.get("url") or "")
    host = urlparse(url).netloc.split(":")[0] if url else ""
    domains = FIRST_PARTY_DOMAINS.get(vendor, ())
    if not domains or not any(host_is_first_party(host, d) for d in domains):
        findings.append(f"non-first-party-host:{host or '(none)'}")

    snap = source.get("snapshot")
    snap_str = str(snap) if snap is not None else ""
    if not snap_str:
        findings.append("missing-snapshot")
    elif snap_str == "unarchivable":
        pdf_path = PDF_DIR / f"{source.get('id')}.pdf"
        if not pdf_path.exists():
            findings.append("unarchivable-missing-pdf")
    elif "web.archive.org/web/" not in snap_str:
        findings.append("snapshot-not-an-archive-url")

    retrieved = source.get("retrieved")
    if retrieved:
        try:
            retrieved_date = datetime.date.fromisoformat(str(retrieved))
        except ValueError:
            findings.append("unparseable-retrieved-date")
        else:
            if retrieved_date > datetime.date.today():
                findings.append("future-retrieved-date")
    else:
        findings.append("missing-retrieved-date")

    return findings


def check_completeness(claims: list[dict], *, inventory_ids: set[str], vendors: set[str]) -> list[tuple[str, str]]:
    """The one check probes/audit-evidence.py has no analog for: every
    (param, vendor) pair in the cross product of `inventory.yaml`'s row ids and
    `models.yaml`'s vendor set must have exactly one claim. Returns the sorted
    list of MISSING (param, vendor) pairs — the expected universe is computed
    from the loaded data, never a hand-typed integer (RESEARCH.md Pattern 3;
    the exact discipline scripts/classify-probes.py's CLASSIFIED_HEADER bug is
    this repo's own cautionary tale for skipping)."""
    expected = {(row_id, vendor) for row_id in inventory_ids for vendor in vendors}
    actual = {(c.get("param"), c.get("vendor")) for c in claims}
    return sorted(expected - actual)


def check_duplicate_pairs(claims: list[dict]) -> list[tuple[str, str]]:
    """Every (param, vendor) pair appearing more than once — collided, never
    merged and never last-wins (DOCP-01/adjacency must_haves truth)."""
    seen: dict[tuple, int] = {}
    for c in claims:
        key = (c.get("param"), c.get("vendor"))
        seen[key] = seen.get(key, 0) + 1
    return sorted(k for k, n in seen.items() if n > 1)


def check_duplicate_source_ids(sources: list[dict]) -> list[str]:
    seen: dict[str, int] = {}
    for s in sources:
        sid = s.get("id")
        seen[sid] = seen.get(sid, 0) + 1
    return sorted(k for k, n in seen.items() if n > 1 and k is not None)


def check_docs_claims(path: Path = DOCS_CLAIMS_PATH) -> list[dict]:
    """Top-level entry point: loads docs-claims.yaml + its two completeness
    inputs, runs every rule, and returns a single sorted list of finding
    dicts. Sorting makes two consecutive runs over an unchanged tree print
    byte-identical output (DOCP-01/ordering must_haves truth)."""
    doc = _load_yaml(path, "claims")
    if "sources" not in doc:
        _fail(2, f"{path}: expected a top-level `sources:` key")

    inventory = _load_yaml(INVENTORY_PATH, "params")
    models = _load_yaml(MODELS_PATH, "models")
    inventory_ids = _load_inventory_ids(inventory)
    vendors = _load_vendors(models)

    sources = doc.get("sources") or []
    claims = doc.get("claims") or []
    source_ids = {s.get("id") for s in sources if s.get("id") is not None}

    findings: list[dict] = []

    for s in sources:
        for rule in check_source(s):
            findings.append({"scope": "source", "identifier": str(s.get("id")), "rule": rule})

    for dup_id in check_duplicate_source_ids(sources):
        findings.append({"scope": "source", "identifier": str(dup_id), "rule": "duplicate-source-id"})

    for c in claims:
        identifier = f"{c.get('param')}:{c.get('vendor')}"
        for rule in check_claim(c, inventory_ids=inventory_ids, vendors=vendors, source_ids=source_ids):
            findings.append({"scope": "claim", "identifier": identifier, "rule": rule})

    for param, vendor in check_duplicate_pairs(claims):
        findings.append({"scope": "claim", "identifier": f"{param}:{vendor}", "rule": "duplicate-claim-pair"})

    for param, vendor in check_completeness(claims, inventory_ids=inventory_ids, vendors=vendors):
        findings.append({"scope": "completeness", "identifier": f"{param}:{vendor}", "rule": "missing-claim-pair"})

    findings.sort(key=lambda f: (f["scope"], f["identifier"], f["rule"]))
    return findings


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        print(f"ERROR {f['scope']}:{f['identifier']} rule={f['rule']}", file=sys.stderr)


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Returns (cases_run, problems). Fixtures are
    written to a tempfile.TemporaryDirectory() per case — the house style
    every fail-loud loader/generator in this repo already uses."""
    problems = 0
    cases = 0

    fixture_inventory_ids = {"temperature", "top-p", "seed"}
    fixture_vendors = {"anthropic", "openai"}
    fixture_source_ids = {"src-a", "src-b"}

    def run_check_claim(claim):
        return check_claim(claim, inventory_ids=fixture_inventory_ids, vendors=fixture_vendors, source_ids=fixture_source_ids)

    base_claim = {
        "param": "temperature",
        "vendor": "anthropic",
        "documented_status": "documented",
        "quote": "some quote",
        "documented_type": "number",
        "source_ref": "src-a",
    }

    # --- a param not in inventory ids fires unknown-param ---
    cases += 1
    c = dict(base_claim, param="not-a-real-param")
    if "unknown-param" not in run_check_claim(c):
        problems += 1
        print("FAIL: an unknown param did not fire unknown-param", file=sys.stderr)

    # --- a param differing only by letter case fires the SAME finding (exact
    #     equality, no folding) ---
    cases += 1
    c = dict(base_claim, param="Temperature")
    if "unknown-param" not in run_check_claim(c):
        problems += 1
        print("FAIL: a case-variant param id did not fire unknown-param", file=sys.stderr)

    # --- a vendor not in models.yaml's vendor set fires unknown-vendor ---
    cases += 1
    c = dict(base_claim, vendor="not-a-real-vendor")
    if "unknown-vendor" not in run_check_claim(c):
        problems += 1
        print("FAIL: an unknown vendor did not fire unknown-vendor", file=sys.stderr)

    # --- an unrecognized documented_status fires, and does not fall through
    #     to either the documented or non-documented branch ---
    cases += 1
    c = dict(base_claim, documented_status="not-a-real-status", quote=None, documented_type=None)
    findings = run_check_claim(c)
    if "unrecognized-documented-status" not in findings:
        problems += 1
        print("FAIL: an unrecognized documented_status did not fire", file=sys.stderr)
    if "documented-missing-quote" in findings or "missing-searched-surface" in findings:
        problems += 1
        print("FAIL: an unrecognized documented_status fell through to a branch instead of only its own rule", file=sys.stderr)

    # --- a documented claim with no quote fires ---
    cases += 1
    c = dict(base_claim, quote=None)
    if "documented-missing-quote" not in run_check_claim(c):
        problems += 1
        print("FAIL: a documented claim with no quote did not fire documented-missing-quote", file=sys.stderr)

    # --- a documented claim with a quote but every facet field null fires ---
    cases += 1
    c = dict(base_claim, documented_type=None)
    if "documented-missing-facet" not in run_check_claim(c):
        problems += 1
        print("FAIL: a documented claim with a quote but no facet did not fire documented-missing-facet", file=sys.stderr)

    # --- an absent-from-docs claim with searched_surface absent fires; with
    #     searched_surface "   " fires the SAME rule ---
    cases += 1
    c = {"param": "temperature", "vendor": "anthropic", "documented_status": "absent-from-docs", "source_ref": "src-a"}
    if "missing-searched-surface" not in run_check_claim(c):
        problems += 1
        print("FAIL: an absent-from-docs claim with no searched_surface did not fire", file=sys.stderr)
    cases += 1
    c2 = dict(c, searched_surface="   ")
    if "missing-searched-surface" not in run_check_claim(c2):
        problems += 1
        print("FAIL: an absent-from-docs claim with a whitespace-only searched_surface did not fire the same rule", file=sys.stderr)

    # --- a claim breaking two rules returns two findings, both named ---
    cases += 1
    c = {"param": "not-real", "vendor": "not-real-vendor", "documented_status": "documented", "quote": "x", "documented_type": "y", "source_ref": "src-a"}
    findings = run_check_claim(c)
    if "unknown-param" not in findings or "unknown-vendor" not in findings:
        problems += 1
        print(f"FAIL: a doubly-broken claim did not name both violated rules: {findings}", file=sys.stderr)

    # --- source_ref pointing at no sources[].id fires ---
    cases += 1
    c = dict(base_claim, source_ref="no-such-source")
    if "dangling-source-ref" not in run_check_claim(c):
        problems += 1
        print("FAIL: a dangling source_ref did not fire", file=sys.stderr)

    # --- a duplicate (param, vendor) pair fires a duplicate finding naming
    #     the pair ---
    cases += 1
    dup_claims = [dict(base_claim), dict(base_claim)]
    dups = check_duplicate_pairs(dup_claims)
    if dups != [("temperature", "anthropic")]:
        problems += 1
        print(f"FAIL: a duplicate (param, vendor) pair was not named, got {dups}", file=sys.stderr)

    # --- two sources: entries sharing an id fires ---
    cases += 1
    dup_sources = [{"id": "same-id"}, {"id": "same-id"}]
    dup_src = check_duplicate_source_ids(dup_sources)
    if dup_src != ["same-id"]:
        problems += 1
        print(f"FAIL: two sources sharing an id were not named, got {dup_src}", file=sys.stderr)

    # --- an absent/empty claims: list fires one missing-pair finding per
    #     expected pair ---
    cases += 1
    missing = check_completeness([], inventory_ids={"a", "b"}, vendors={"v1", "v2"})
    if sorted(missing) != sorted([("a", "v1"), ("a", "v2"), ("b", "v1"), ("b", "v2")]):
        problems += 1
        print(f"FAIL: an empty claims list did not fire one missing pair per expected pair, got {missing}", file=sys.stderr)

    # --- a fully covered pair universe reports zero missing pairs ---
    cases += 1
    full_claims = [
        {"param": "a", "vendor": "v1"}, {"param": "a", "vendor": "v2"},
        {"param": "b", "vendor": "v1"}, {"param": "b", "vendor": "v2"},
    ]
    missing_full = check_completeness(full_claims, inventory_ids={"a", "b"}, vendors={"v1", "v2"})
    if missing_full:
        problems += 1
        print(f"FAIL: a fully covered pair universe reported missing pairs: {missing_full}", file=sys.stderr)

    # --- source: a snapshot that is a live vendor URL fires; a
    #     web.archive.org/web/<ts>/<url> snapshot passes ---
    base_source = {
        "id": "src-a", "vendor": "anthropic", "first_party": True,
        "url": "https://platform.claude.com/docs/en/api/messages",
        "snapshot": "https://web.archive.org/web/20260902183800/https://platform.claude.com/docs/en/api/messages",
        "retrieved": "2026-01-01",
    }
    cases += 1
    s = dict(base_source, snapshot="https://platform.claude.com/docs/en/api/messages")
    if "snapshot-not-an-archive-url" not in check_source(s):
        problems += 1
        print("FAIL: a live-URL snapshot did not fire snapshot-not-an-archive-url", file=sys.stderr)
    cases += 1
    if check_source(dict(base_source)):
        problems += 1
        print(f"FAIL: a valid web.archive.org snapshot fired unexpectedly: {check_source(dict(base_source))}", file=sys.stderr)

    # --- snapshot: unarchivable with a companion PDF present passes; without
    #     the PDF fires ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        global PDF_DIR
        original_pdf_dir = PDF_DIR
        PDF_DIR = Path(td)
        try:
            s = dict(base_source, id="unarchivable-src", snapshot="unarchivable")
            findings_no_pdf = check_source(s)
            if "unarchivable-missing-pdf" not in findings_no_pdf:
                problems += 1
                print("FAIL: unarchivable with no PDF did not fire unarchivable-missing-pdf", file=sys.stderr)
            (Path(td) / "unarchivable-src.pdf").write_bytes(b"%PDF-1.4 fixture")
            findings_with_pdf = check_source(s)
            if "unarchivable-missing-pdf" in findings_with_pdf:
                problems += 1
                print("FAIL: unarchivable WITH a companion PDF still fired unarchivable-missing-pdf", file=sys.stderr)
        finally:
            PDF_DIR = original_pdf_dir

    # --- first_party: false fires ---
    cases += 1
    s = dict(base_source, first_party=False)
    if "not-first-party" not in check_source(s):
        problems += 1
        print("FAIL: first_party: false did not fire not-first-party", file=sys.stderr)

    # --- WR-02: a sources: entry missing id: fires missing-source-id ---
    cases += 1
    s = dict(base_source)
    del s["id"]
    if "missing-source-id" not in check_source(s):
        problems += 1
        print("FAIL: a source with no id: did not fire missing-source-id", file=sys.stderr)

    # --- WR-02: an id-less sources: entry must not poison source_ids with None
    #     — a claim whose own source_ref is missing/null must still fire
    #     dangling-source-ref, not pass because None ended up in source_ids ---
    cases += 1
    id_less_source_ids = {s2.get("id") for s2 in [{"vendor": "anthropic", "first_party": True}] if s2.get("id") is not None}
    if None in id_less_source_ids:
        problems += 1
        print("FAIL: source_ids construction still admits None for an id-less source", file=sys.stderr)
    c = dict(base_claim)
    del c["source_ref"]
    findings_no_ref = check_claim(c, inventory_ids=fixture_inventory_ids, vendors=fixture_vendors, source_ids=id_less_source_ids)
    if "dangling-source-ref" not in findings_no_ref:
        problems += 1
        print("FAIL: a claim with no source_ref did not fire dangling-source-ref even with an id-less source present", file=sys.stderr)

    # --- retrieved one day in the future fires; retrieved equal to today
    #     passes ---
    cases += 1
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    s = dict(base_source, retrieved=tomorrow)
    if "future-retrieved-date" not in check_source(s):
        problems += 1
        print("FAIL: a retrieved date one day in the future did not fire future-retrieved-date", file=sys.stderr)
    cases += 1
    today = datetime.date.today().isoformat()
    s = dict(base_source, retrieved=today)
    if "future-retrieved-date" in check_source(s):
        problems += 1
        print("FAIL: a retrieved date equal to today fired future-retrieved-date", file=sys.stderr)

    # --- host evilopenai.com is rejected for vendor: openai; both real
    #     openai.com subdomains pass ---
    cases += 1
    s = dict(base_source, vendor="openai", url="https://evilopenai.com/docs/api-reference")
    findings = check_source(s)
    if not any(f.startswith("non-first-party-host") for f in findings):
        problems += 1
        print("FAIL: a lookalike host (evilopenai.com) was not rejected for vendor openai", file=sys.stderr)
    cases += 1
    for good_host in ("developers.openai.com", "platform.openai.com"):
        s = dict(base_source, vendor="openai", url=f"https://{good_host}/api/docs/api-reference")
        findings = check_source(s)
        if any(f.startswith("non-first-party-host") for f in findings):
            problems += 1
            print(f"FAIL: a real openai.com subdomain ({good_host}) was rejected as non-first-party", file=sys.stderr)

    # --- host cloud.google.com is rejected for vendor: gemini;
    #     ai.google.dev passes ---
    cases += 1
    s = dict(base_source, vendor="gemini", url="https://cloud.google.com/vertex-ai/docs")
    if not any(f.startswith("non-first-party-host") for f in check_source(s)):
        problems += 1
        print("FAIL: cloud.google.com (Vertex AI) was not rejected for vendor gemini", file=sys.stderr)
    cases += 1
    s = dict(base_source, vendor="gemini", url="https://ai.google.dev/api/generate-content")
    if any(f.startswith("non-first-party-host") for f in check_source(s)):
        problems += 1
        print("FAIL: ai.google.dev was rejected as non-first-party for vendor gemini", file=sys.stderr)

    # --- a clean fixture (source + claim) returns zero findings ---
    cases += 1
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        (td_path / "inventory.yaml").write_text(yaml.safe_dump({"params": [{"id": "temperature"}]}))
        harness_dir = td_path / "harness"
        harness_dir.mkdir()
        (harness_dir / "models.yaml").write_text(yaml.safe_dump({"models": [{"vendor": "anthropic"}]}))
        docs_claims = {
            "checked": "2026-09-02",
            "scope": "fixture",
            "sources": [dict(base_source)],
            "claims": [dict(base_claim)],
        }
        (td_path / "docs-claims.yaml").write_text(yaml.safe_dump(docs_claims, sort_keys=False))

        global INVENTORY_PATH, MODELS_PATH
        original_inventory, original_models = INVENTORY_PATH, MODELS_PATH
        INVENTORY_PATH = td_path / "inventory.yaml"
        MODELS_PATH = harness_dir / "models.yaml"
        try:
            findings = check_docs_claims(td_path / "docs-claims.yaml")
        finally:
            INVENTORY_PATH, MODELS_PATH = original_inventory, original_models
        if findings:
            problems += 1
            print(f"FAIL: a clean fixture reported findings: {findings}", file=sys.stderr)

        # --- two consecutive check_docs_claims() calls over an unchanged
        #     fixture return byte-identical rendered findings output ---
        cases += 1
        INVENTORY_PATH = td_path / "inventory.yaml"
        MODELS_PATH = harness_dir / "models.yaml"
        try:
            first = check_docs_claims(td_path / "docs-claims.yaml")
            second = check_docs_claims(td_path / "docs-claims.yaml")
        finally:
            INVENTORY_PATH, MODELS_PATH = original_inventory, original_models
        if first != second:
            problems += 1
            print("FAIL: two consecutive check_docs_claims() calls over an unchanged fixture were not identical", file=sys.stderr)

    return cases, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check-docs-claims.py",
        usage="check-docs-claims.py --check | --selftest",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.check and args.selftest:
        print("usage: check-docs-claims.py --check | --selftest", file=sys.stderr)
        return 2

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    if args.check:
        findings = check_docs_claims()
        _print_findings(findings)
        print(f"{len(findings)} problem(s)")
        return 1 if findings else 0

    print("usage: check-docs-claims.py --check | --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
