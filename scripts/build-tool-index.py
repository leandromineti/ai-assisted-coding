#!/usr/bin/env python3
"""Generate comparisons/tools.md from the YAML frontmatter of every tool report.

The index is generated, never hand-edited: a hand-kept index drifts from the
reports it describes, and you find out when it's already wrong.

    python3 scripts/build-tool-index.py            # write the index
    python3 scripts/build-tool-index.py --check    # verify frontmatter, write nothing

--check verifies each report's pinned `commit` is still **reachable** in its clone — a pin
that no longer resolves means the claims beneath it can't be checked against their source,
which is an error. Upstream having moved on is reported separately and is *not* an error: a
pin records the commit that was read, so re-pointing it at HEAD without re-reading would
turn a dated observation into a false claim about current code.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
OUT = ROOT / "comparisons" / "tools.md"
FEATURES_OUT = ROOT / "comparisons" / "features.md"
ENVIRONMENTS_OUT = ROOT / "comparisons" / "environments.md"
MODELS_OUT = ROOT / "comparisons" / "models.md"
FEATURE_REGISTRY_OUT = ROOT / "comparisons" / "feature-registry.md"

# Category-5 bindings: which execution environments a tool can run its agent in.
# Order defines the matrix columns.
ENV_KEYS = ["host", "worktree", "container", "remote-sandbox"]

# How a tool relates to the environment it runs in — the category-3 relationship
# vocabulary, one verb per instance, each earned at a different deep-dive. Defined
# in tools/3-execution-environments/README.md; listed here only to validate spelling.
ENV_RELATIONS = ["bundle", "bind", "internalize", "inhabit"]

# Fixed vocabulary — order defines the matrix columns. Keep small and axis-aligned;
# vendor pet names don't get columns.
# The feature taxonomy is the single source of truth for feature keys — one entry
# per assessed characteristic, with definitions, applicability, and demand↔supply
# kind links (ADR-0010). Do NOT hardcode keys here; edit the registry.
FEATURE_REGISTRY_PATH = ROOT / "docs" / "feature-taxonomy.yaml"

# What shape a cell's VALUE takes — the registry's own vocabulary, reified from prose
# that already said it (ADR-0032). Not generic types: `closed-enum` vs `open-descriptive`
# is an ADR-0017 distinction (a closed set you can validate against vs an open vocabulary
# with a required family:specific shape), and `graded` is ADR-0011's ordered enforcement
# scale, not merely an enum. A key that is scalar but accepts a list of named instances
# (rules_files, memory_store) keeps its scalar type and says so in its definition.
VALUE_TYPES = {
    "presence",          # ✓/✗ presence-claim (omitted = not checked, false = checked-absent)
    "graded",            # ADR-0011 ordered scale: engine | hook | script | prose | true | false
    "closed-enum",       # one value from a closed set stated in the definition
    "open-descriptive",  # open vocabulary with a required shape (family:specific)
    "list",              # several values from a stated set
    "free-text",         # the vendor's or subject's own words; no controlled vocabulary
    "string",            # a single identifier or name
    "number",            # a bare count
    "date",              # a date
    "structured",        # SEVERAL facts in one cell (pricing: input AND output). Not a
                         # wrapper for provenance — value_type types the FACT, and a cell
                         # that adds `note` for the matrix flags `renders_note` instead
                         # (ADR-0033 introduced it, ADR-0039 narrowed it)
}

# `pricing:`'s sub-schema (ADR-0033). The base-rate rule lives in the registry definition;
# these are the shape constraints a cell must satisfy — the repo's first CELL-value check,
# the follow-on ADR-0032 named and deferred.
PRICING_REGIMES = {
    "flat", "context-tiered", "time-of-day", "variant-priced", "route-dependent",
}
# What kind of claim a knowledge-cutoff date is (ADR-0037). `inherited` exists because a
# vendor can delegate the underlying fact — Gemini 3.1 Pro's card sends its training
# dataset to the Gemini 3 Pro card — and that is neither stated-for-this-model nor absent.
CUTOFF_BASIS = {"vendor-stated", "inherited", "not-stated", "retracted"}
DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
# The reasoning keys' controlled values (ADR-0040) — the repo's fourth cell-value check.
# `reasoning_type` is a closed enum of TOGGLEABILITY. `reasoning_effort` is
# open-descriptive: the FAMILY is closed (who sizes the reasoning), the specific is free.
REASONING_TYPES = {"always-on", "default-on", "opt-in", "none"}
REASONING_EFFORT_FAMILIES = {"levels", "budget"}
# `access:`'s closed enum (ADR-0044) — what the public can OBTAIN, paired with `license:`,
# which says under what terms. The repo's fifth cell-value check and the first that is
# REQUIRED on every report in every category: the field it replaced (`open_source:`) was
# already universal, and a missing openness cell would read as "closed" to any eye.
ACCESS_VALUES = {"open-source", "closed-source", "open-weights"}


def _load_feature_registry() -> tuple[list[dict], list[dict]]:
    try:
        text = FEATURE_REGISTRY_PATH.read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"feature taxonomy missing: {FEATURE_REGISTRY_PATH} ({e})")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        sys.exit(f"feature taxonomy YAML unparsable: {e}")
    entries = (data or {}).get("features")
    if not isinstance(entries, list) or not entries:
        sys.exit("feature taxonomy: `features:` must be a non-empty list")
    t_fields = (data or {}).get("transcription_fields") or []
    feature_ids = {e.get("id") for e in entries}
    for t in t_fields:
        for req in ("id", "applies_to", "definition", "verification", "value_type"):
            if req not in t:
                sys.exit(f"transcription field missing `{req}`: {t}")
        if t["value_type"] not in VALUE_TYPES:
            sys.exit(
                f"transcription field `{t['id']}` has unknown value_type "
                f"`{t['value_type']}` (known: {sorted(VALUE_TYPES)})"
            )
        if t["verification"] not in {"dated-docs", "mechanical", "source-or-docs"}:
            sys.exit(
                f"transcription field `{t['id']}` has unknown verification "
                f"`{t['verification']}` (known: dated-docs, mechanical, source-or-docs)"
            )
        if t["id"] in feature_ids:
            sys.exit(
                f"`{t['id']}` is both a transcription field and a registry key — "
                "the placement test forbids giving the same fact two homes"
            )
    known_blocks = {
        "harness_features",
        "workflow_features",
        "memory_features",
        "model_features",
        "environment_features",
    }
    for e in entries:
        for req in ("id", "block", "applies_to", "definition", "value_type"):
            if req not in e:
                sys.exit(f"feature taxonomy entry missing `{req}`: {e}")
        if e["value_type"] not in VALUE_TYPES:
            sys.exit(
                f"feature taxonomy entry `{e['id']}` has unknown value_type "
                f"`{e['value_type']}` (known: {sorted(VALUE_TYPES)})"
            )
        if e["block"] not in known_blocks:
            sys.exit(
                f"feature taxonomy entry `{e['id']}` has unknown block `{e['block']}` "
                f"(known: {sorted(known_blocks)}) — a typo here silently empties a matrix"
            )
    return entries, t_fields


FEATURE_REGISTRY, TRANSCRIPTION_FIELDS = _load_feature_registry()
HARNESS_FEATURE_KEYS = [
    e["id"] for e in FEATURE_REGISTRY if e["block"] == "harness_features"
]
WORKFLOW_FEATURE_KEYS = [
    e["id"] for e in FEATURE_REGISTRY if e["block"] == "workflow_features"
]
MEMORY_FEATURE_KEYS = [
    e["id"] for e in FEATURE_REGISTRY if e["block"] == "memory_features"
]

# Category-1 API-feature keys: registry-driven since ADR-0014 (definitions and
# verified-only semantics live in the feature taxonomy; reports carry them in a
# nested `model_features:` block).
MODEL_FEATURE_KEYS = [
    e["id"] for e in FEATURE_REGISTRY if e["block"] == "model_features"
]

# Category-3 execution-environment keys: registry-driven since ADR-0017 (definitions,
# enum regimes, and provenance live in the feature taxonomy; reports carry them in a
# nested `environment_features:` block). Order is inherited from registry entry order.
ENVIRONMENT_FEATURE_KEYS = [
    e["id"] for e in FEATURE_REGISTRY if e["block"] == "environment_features"
]

# Category-1 lifecycle key (added 2026-08-17): first-availability date plus lifecycle
# stage, in the vendor's own vocabulary (GA / Preview / beta / launch), since stages
# don't align across vendors (Google ships flagships as Preview; DeepSeek previews
# then GAs; xAI documents no stage at all). Free text, verified-only like the rest:
# a date needs a primary source, and "GA" vs "preview" is a claim, not a default.
MODEL_LIFECYCLE_KEYS = ["released"]

REQUIRED = ("name", "category", "depth")
DEPTH_ORDER = {"deep-dive": 0, "survey": 1, "stub": 2}
CATEGORY_NAMES = {
    1: "Models",
    2: "Harnesses",
    3: "Execution environments",
    4: "Workflow frameworks",
    5: "Memory",  # full category since the 2026-08-22 split (ADR-0020); was "Extensions"
    6: "Extensions",  # the residual bucket, renumbered 5->6 per ADR-0020 (2026-08-22); bucket status per ADR-0002; renamed from "Portable artifacts" 2026-08-17
}


def read_frontmatter(path: Path) -> dict | None:
    """Return the YAML frontmatter of a markdown file, or None if it has none."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


def collect() -> list[dict]:
    reports = []
    for path in sorted(TOOLS.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue  # templates and category front doors are not reports
        fm = read_frontmatter(path)
        if fm is None:
            continue
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            print(f"warn: {path.relative_to(ROOT)} missing {missing}", file=sys.stderr)
            continue
        fm["_path"] = path
        reports.append(fm)
    return sorted(
        reports,
        key=lambda r: (r["category"], DEPTH_ORDER.get(r["depth"], 9), r["name"]),
    )


def check_cutoff(reports: list[dict]) -> None:
    """Validate `knowledge_cutoff:` on every category-1 report (ADR-0037).

    Second cell-value check, same standing as check_pricing: a date that does not sort is
    worse than no date, and a date next to `basis: not-stated` is a contradiction that
    would render as fact.
    """
    for r in reports:
        if r.get("category") != 1:
            continue
        rel = r["_path"].relative_to(ROOT)
        c = r.get("knowledge_cutoff")
        if c is None:
            continue
        if not isinstance(c, dict):
            sys.exit(f"{rel}: `knowledge_cutoff:` must be a mapping since ADR-0037")
        if c.get("basis") not in CUTOFF_BASIS:
            sys.exit(f"{rel}: `knowledge_cutoff.basis` is {c.get('basis')!r} — "
                     f"known: {sorted(CUTOFF_BASIS)}")
        v = c.get("date")
        if v is not None and not DATE_RE.match(str(v)):
            sys.exit(f"{rel}: `knowledge_cutoff.date` must be YYYY-MM or YYYY-MM-DD, got {v!r}")
        absent = c["basis"] in ("not-stated", "retracted")
        if absent and c.get("date") is not None:
            sys.exit(f"{rel}: `knowledge_cutoff.date` is set while basis is "
                     f"`{c['basis']}` — a date the vendor does not stand behind")
        if not absent and c.get("date") is None:
            sys.exit(f"{rel}: `knowledge_cutoff.date` is required when basis is "
                     f"`{c['basis']}`")
        if not c.get("note"):
            sys.exit(f"{rel}: `knowledge_cutoff.note` is required — the surface checked, "
                     f"the search scope, or the delegation")


def check_reasoning(reports: list[dict]) -> None:
    """Validate the three reasoning cells on every category-1 report (ADR-0040).

    Fourth cell-value check. `reasoning_effort` is `open-descriptive`, and this is what
    that type means in practice: the family is closed and checked here, the specific is
    free and is not. Without it the shape rots one report at a time — `low/high/max`
    written bare, a default dropped — and the column stops being comparable, which was
    the whole reason the level set and default live in the cell rather than in prose.
    """
    for r in reports:
        if r.get("category") != 1:
            continue
        rel = r["_path"].relative_to(ROOT)
        feats = r.get("model_features") or {}
        if not isinstance(feats, dict):
            continue

        t = feats.get("reasoning_type")
        if t is not None and t not in REASONING_TYPES:
            sys.exit(f"{rel}: `reasoning_type` is {t!r} — known: {sorted(REASONING_TYPES)}")

        e = feats.get("reasoning_effort")
        if e is not None and e != "none":
            family, _, specific = str(e).partition(":")
            if family not in REASONING_EFFORT_FAMILIES or not specific:
                sys.exit(
                    f"{rel}: `reasoning_effort` is {e!r} — must be `none` or "
                    f"`family:specific` with family in {sorted(REASONING_EFFORT_FAMILIES)}"
                )
            if family == "levels" and "@" not in specific:
                sys.exit(
                    f"{rel}: `reasoning_effort` is {e!r} — a `levels:` dial carries its "
                    f"default after `@` (a level set without one understates cost: "
                    f"kimi-k3 and glm-5.3 default to `max`)"
                )

        # A model that does not reason cannot carry a dial, and one that does cannot be
        # `none` on either — the contradiction the split exists to make visible.
        if feats.get("reasoning") is False:
            for k in ("reasoning_type", "reasoning_effort"):
                if feats.get(k) not in (None, "none"):
                    sys.exit(f"{rel}: `reasoning: false` but `{k}: {feats[k]!r}`")
        if feats.get("reasoning") is True:
            for k in ("reasoning_type", "reasoning_effort"):
                if feats.get(k) == "none":
                    sys.exit(f"{rel}: `reasoning: true` but `{k}: none`")


def check_pricing(reports: list[dict]) -> None:
    """Validate the `pricing:` mapping on every category-1 report (ADR-0033).

    The first check in this repo that reads a CELL rather than a registry key. Fails the
    run rather than warning: an unparseable price is worse than a missing one, because it
    renders as something that looks like a number and isn't.
    """
    for r in reports:
        if r.get("category") != 1:
            continue
        rel = r["_path"].relative_to(ROOT)
        p = r.get("pricing")
        if p is None:
            continue  # omitted = not checked, same discipline as every other field
        if not isinstance(p, dict):
            sys.exit(f"{rel}: `pricing:` must be a mapping since ADR-0033, got {type(p).__name__}")
        for k in ("input", "output"):
            v = p.get(k)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
                sys.exit(f"{rel}: `pricing.{k}` must be a positive number (USD per MTok), got {v!r}")
        if not p.get("currency"):
            sys.exit(f"{rel}: `pricing.currency` is required")
        if p.get("regime") not in PRICING_REGIMES:
            sys.exit(
                f"{rel}: `pricing.regime` is {p.get('regime')!r} — "
                f"known: {sorted(PRICING_REGIMES)}"
            )
        if p["regime"] != "flat" and not p.get("note"):
            sys.exit(
                f"{rel}: `pricing.note` is required when regime is "
                f"`{p['regime']}` — the numbers alone would misstate the price"
            )


def check_access(reports: list[dict]) -> None:
    """Validate `access:` on every report, every category (ADR-0044).

    Unlike the other four cell-value checks, absence is a failure rather than an
    "omitted = not checked": `access` replaced a boolean that was already on all 45
    reports, and an empty openness cell does not read as unchecked — it reads as closed.
    `open-weights` is category-1-only by construction; `open-source` on a model would
    mean its TRAINING SOURCE is public, which no report claims yet, so it is allowed
    rather than gated (a zero, not an impossibility).
    """
    for r in reports:
        rel = r["_path"].relative_to(ROOT)
        v = r.get("access")
        if v is None:
            sys.exit(
                f"{rel}: `access:` is required on every report since ADR-0044 — "
                f"one of {sorted(ACCESS_VALUES)}"
            )
        if v not in ACCESS_VALUES:
            sys.exit(f"{rel}: `access:` is {v!r} — known: {sorted(ACCESS_VALUES)}")
        if v == "open-weights" and r.get("category") != 1:
            sys.exit(
                f"{rel}: `access: open-weights` outside category 1 — weights are a "
                "model's artifact; a tool's is its source"
            )


def check(reports: list[dict]) -> int:
    """Verify each report's pinned commit is still *reachable*, and report upstream drift.

    Two different conditions, deliberately separated (2026-07-31):

    * **UNVERIFIABLE (an error).** The pinned commit no longer resolves in the clone — a
      force-push, a rewritten history, a wrong or missing remote. Every claim beneath the
      report is now uncheckable against the code it came from. This is the real failure.
    * **BEHIND (information, not an error).** The pin resolves but upstream has moved on.
      The report is still fully verifiable; it just describes older code.

    The earlier version treated *any* divergence from clone HEAD as "STALE … silently
    invalidates every architecture claim", which was wrong in a way that mattered: a pin
    records **the commit that was read**, so the only action that silenced the warning was
    re-pointing the pin at HEAD without re-reading — converting "I read commit X" into a
    false claim that the report describes HEAD. The check now refuses to invite that.
    Deciding to re-read after drift is a judgement call for a human; it is not a lint error.
    """
    problems = 0
    behind = []
    for r in reports:
        pinned = r.get("commit")
        # A recorded pin with a clone present is checked regardless of `access:`: a
        # closed *product* can still expose an open, pinned artifact (Modal — closed infra,
        # open client), and its verified claims drift with that clone. Genuinely closed
        # tools carry no `commit` and skip via `not pinned`; the clone-existence guard below
        # keeps a pinned-but-uncloned entry a warning, not a crash. (Decoupled 2026-08-16.)
        if not pinned:
            continue
        clone = ROOT / "upstream" / r["name"]
        if not (clone / ".git").is_dir():
            print(f"warn: {r['name']} pinned to {pinned} but not cloned", file=sys.stderr)
            continue
        g = lambda *a: subprocess.run(  # noqa: E731
            ["git", "-C", str(clone), *a], capture_output=True, text=True
        )
        if g("cat-file", "-e", f"{pinned}^{{commit}}").returncode != 0:
            print(
                f"UNVERIFIABLE: {r['name']} pins {pinned}, which no longer resolves in "
                f"upstream/{r['name']} — history rewritten or wrong remote. Claims in "
                f"{r['_path'].relative_to(ROOT)} cannot be checked against their source.",
                file=sys.stderr,
            )
            problems += 1
            continue
        n = g("rev-list", "--count", f"{pinned}..HEAD").stdout.strip()
        if n and n != "0":
            head = g("rev-parse", "--short", "HEAD").stdout.strip()
            files = g("diff", "--name-only", f"{pinned}..HEAD").stdout.split()
            behind.append((r["name"], pinned, head, int(n), len(files), r.get("read_at", "?")))
    for name, pinned, head, n, nfiles, read_at in sorted(behind, key=lambda b: -b[3]):
        print(
            f"behind: {name} read at {read_at} on {pinned}; upstream is {n} commits ahead "
            f"({head}), {nfiles} files changed — re-read if the drift touches what the "
            f"report claims; do NOT re-pin without re-reading.",
            file=sys.stderr,
        )
    return problems


def render(reports: list[dict]) -> str:
    date = max((str(r.get("read_at", "")) for r in reports), default="")
    lines = [
        "# Tool index",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit the frontmatter of the reports in tools/, then re-run the script. -->",
        "",
        f"Every tool with a report, one subsection per category in repo order. Newest read: `{date}`.",
        "",
        "`depth` is the honesty column: **stub** means facts were collected mechanically but "
        "nobody read the source; **survey** means it was used or skimmed; **deep-dive** means "
        "the category's component decomposition (defined in tool-taxonomy.md) was actually traced, "
        "the report saying which components (pre-2026-08-25 deep-dives read under the earlier "
        "loop+context definition).",
        "",
        "`Stars` is from the GitHub API on the date in each report's `stars_at` (drifts daily; "
        "refresh with `scripts/repo-facts.sh`). `Since` is the repo's first commit date — the "
        "*public* history's start, which for open-sourced-later tools postdates the product. "
        "Both columns describe the *current* repo only: a fork or org move strands the "
        "predecessor's stars while keeping its history — see each report's provenance notes "
        "(gsd-core is the live case).",
        "",
        "`Harness targets` applies to category-4/5 tools (which harnesses they officially "
        "install into) — set in frontmatter only when verified in source or docs; `·` "
        "means not yet checked, `—` not applicable.",
        "",
        "`Access` and `License` are a **pair** (ADR-0044): access says what the public can "
        "*obtain* — `open-source` (the subject's source is public, whatever the terms) · "
        "`open-weights` (a model's weights are published; its training source is not) · "
        "`closed-source` (neither) — and license says under what *terms*. Read them "
        "together: `open-source` beside a non-OSI license is what the ecosystem calls "
        "source-available (pilot-shell), and an OSI license beside `closed-source` means "
        "the license covers an accessory, not the product (modal's client SDK). The "
        "subject is the tool as shipped, so a public issues-and-releases repo is not "
        "source access (claude-code).",
        "",
        "`Version read` is `git describe --tags --always` of the clone at read time — the "
        "tree the report's claims were checked against, not a release the vendor "
        "advertises. `—` means there was no clone to describe, which is every category-1 "
        "row: weights have no working tree. One row is neither: claude-code has no clone "
        "but does report a version, so its cell is what the shipped binary says about "
        "itself (`claude --version`) and nothing in it is machine-checked — the report's "
        "own field comment says so.",
        "",
    ]
    header_row = ("| Tool | Surfaces · exec | Stack | License | Access | Stars | Since | "
                  "Harness targets | Version read | Depth | Report |")
    divider = "|---|---|---|---|---|---|---|---|---|---|---|"
    current_cat = None
    for r in reports:
        if r["category"] != current_cat:
            current_cat = r["category"]
            if lines[-1] != "":
                lines.append("")
            lines += [
                f"## {current_cat} · {CATEGORY_NAMES.get(current_cat, '?')}",
                "",
                header_row,
                divider,
            ]
        stack = r.get("stack") or []
        stack = ", ".join(stack) if isinstance(stack, list) else str(stack)
        rel = r["_path"].relative_to(ROOT)
        link = f"[{r['name']}](../{rel})"
        version = r.get("version") or "—"
        # This column says ONE thing: which tree the report read. Until ADR-0044 it also
        # substituted an openness literal ("closed source") for the version whenever
        # `open_source: false` — an openness fact rendered in a column named for versions,
        # and the reason eight of eleven category-1 rows read `closed source` where they
        # have no clone at all. Openness now has its own `Access` column, and the cell
        # falls back to `—` like any other unknown. `closed_source_pin_note` survives the
        # change with a narrower job: it ANNOTATES the version rather than replacing it
        # (Daytona reads "v0.189.0-9-g4ee2c6365 (pre-closure pin)"), so a reader meeting a
        # closed subject with a readable pin learns why — CR-01's point, kept. Still
        # opt-in and still Daytona-only by design.
        pin_note = r.get("closed_source_pin_note")
        if pin_note and version != "—":
            version = f"{version} ({pin_note})"
        surfaces = r.get("surfaces") or []
        if surfaces:
            shape = " + ".join(surfaces)
            if r.get("execution"):
                shape += f" · {r['execution']}"
        else:
            shape = "—"
        stars = f"{r['stars']:,}" if isinstance(r.get("stars"), int) else "—"
        since = str(r.get("first_commit") or "—")
        targets = r.get("harness_targets")
        if isinstance(targets, list):
            targets = ", ".join(str(t) for t in targets)
        elif targets is not None:
            targets = str(targets)
        else:
            targets = "·" if r["category"] in (4, 5, 6) else "—"
        lines.append(
            f"| {r['name']} | {shape} | "
            f"{stack or '—'} | {r.get('license') or '—'} | `{r.get('access') or '—'}` | "
            f"{stars} | {since} | {targets} | "
            f"`{version}` | {r['depth']} | {link} |"
        )

    counts = {}
    for r in reports:
        counts[r["depth"]] = counts.get(r["depth"], 0) + 1
    summary = " · ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    lines += ["", f"**{len(reports)} tools** — {summary}.", ""]
    return "\n".join(lines)


def _render_cross_category(reports: list[dict]) -> list[str]:
    """The bleed, quantified: demand-side presence counts vs tracked category-5 supply
    for every feature that spans categories or has a kind_link (ADR-0010)."""
    rows = [e for e in FEATURE_REGISTRY
            if e.get("kind_link") or len(e.get("applies_to", [])) > 1]
    if not rows:
        return []
    lines = [
        "",
        "## Cross-category features",
        "",
        "The bleed, quantified. **Demand** counts presence among reports of the",
        "feature's `applies_to` categories (✓ / checked); **supply** counts tracked",
        "category-5 tools of the linked `kind`. Zeros are honest — no supply-side tool",
        "tracked yet. Definitions and links live in the",
        "[feature taxonomy](../docs/feature-taxonomy.md).",
        "",
        "| Feature | Category | Demand (✓/checked) | Supply (category-5 kind) | Note |",
        "|---|---|---|---|---|",
    ]
    for e in rows:
        block, key = e["block"], e["id"]
        present = checked = 0
        for r in reports:
            if r.get("category") not in e["applies_to"]:
                continue
            v = (r.get(block) or {}).get(key) if isinstance(r.get(block), dict) else None
            if v is None:
                continue
            checked += 1
            if v is not False:
                present += 1
        kind = e.get("kind_link")
        if kind:
            # supply split per ADR-0020: the memory kind supplies from category 5
            # (Memory); every other artifact kind supplies from category 6 (Extensions)
            supply_cat = 5 if kind == "memory" else 6
            supply_n = sum(1 for r in reports
                           if r.get("category") == supply_cat and r.get("type") == kind)
            supply = f"`{kind}` · {supply_n} tracked"
        else:
            supply = "—"
        categories = "+".join(str(x) for x in e["applies_to"])
        note = e.get("note", "")
        lines.append(f"| {key.replace('_', ' ')} | {categories} | {present}/{checked} | {supply} | {note} |")
    return lines


def render_features(reports: list[dict]) -> str:
    lines = [
        "# Feature matrix",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit the `harness_features:` frontmatter of the reports in tools/, then re-run. -->",
        "",
        "Cells: **✓** verified present · **✗** verified absent · **·** not yet checked.",
        "The dot is load-bearing — it is *not* a no. A feature key is only set in a",
        "report's frontmatter when confirmed in source or official docs. Keys are",
        "defined once in the [feature taxonomy](../docs/feature-taxonomy.md)",
        "(ADR-0010); the [tool taxonomy](../docs/tool-taxonomy.md) classifies the tools themselves.",
        "",
    ]

    def _feature_row(r: dict, unknown: set) -> str:
        feats = r.get("harness_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        unknown.update(k for k in feats if k not in HARNESS_FEATURE_KEYS)
        cells = [fmt_feature_cell(feats.get(key)) for key in HARNESS_FEATURE_KEYS]
        rel = r["_path"].relative_to(ROOT)
        # the license+access PAIR, rendered as two cells (ADR-0044): terms, then reach
        pair = f"{r.get('license') or '·'} | `{r.get('access') or '·'}`"
        return f"| [{r['name']}](../{rel}) | {pair} | " + " | ".join(cells) + " |"

    # license is rendered from the reports' existing top-level frontmatter field
    # (single source of truth; NOT a registry key — it is a tool-taxonomy fact)
    header_row = "| Tool | license | access | " + " | ".join(
        k.replace("_", " ") for k in HARNESS_FEATURE_KEYS
    ) + " |"
    divider = "|---|---|---|" + "---|" * len(HARNESS_FEATURE_KEYS)
    unknown_keys: set[str] = set()

    lines += [
        "## Models (category 1)",
        "",
        "The category-1 slice — `model_features:` frontmatter (ADR-0014). The three",
        "reasoning keys are typed (presence · closed-enum · `family:specific`, ADR-0040);",
        "the two economics keys stay free-text in the vendor's own terms. All verified",
        "against the report's `url` on its `checked` date. Quantitative surface (context,",
        "pricing, cutoff, lifecycle) stays in [models.md](models.md).",
        "",
        "| Model | license | access | context window | " + " | ".join(k.replace("_", " ") for k in MODEL_FEATURE_KEYS) + " |",
        "|---|---|---|---|" + "---|" * len(MODEL_FEATURE_KEYS),
    ]
    m_unknown: set[str] = set()
    for r in reports:
        if r.get("category") != 1:
            continue
        feats = r.get("model_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        m_unknown.update(k for k in feats if k not in MODEL_FEATURE_KEYS)
        cells = [fmt_feature_cell(feats.get(k)) for k in MODEL_FEATURE_KEYS]
        rel = r["_path"].relative_to(ROOT)
        # the license+access PAIR, rendered as two cells (ADR-0044): terms, then reach
        pair = f"{r.get('license') or '·'} | `{r.get('access') or '·'}`"
        cw = r.get("context_window")
        cw = f"{cw:,}" if isinstance(cw, int) else (cw or "·")
        lines.append(f"| [{r['name']}](../{rel}) | {pair} | {cw} | " + " | ".join(cells) + " |")
    for k in sorted(m_unknown):
        print(f"warn: model feature key '{k}' not in the feature taxonomy — not rendered", file=sys.stderr)
    lines += [
        "",
        "## Harnesses (category 2)",
        "",
        header_row,
        divider,
    ]
    for r in reports:
        if r.get("category") != 2:
            continue
        lines.append(_feature_row(r, unknown_keys))

    lines += [
        "",
        "## Environments, memory & extensions on the harness vocabulary (categories 3, 5 & 6)",
        "",
        "Category-3, category-5, and category-6 reports may verify harness-vocabulary keys where the",
        "characteristic genuinely applies (an extension shipping a learning loop, an",
        "environment exposing session sharing). Same columns, same discipline; rows",
        "here do NOT count toward the cross-category table's demand side (that filter is",
        "`applies_to`).",
        "",
        header_row,
        divider,
    ]
    for r in reports:
        if r.get("category") not in (3, 5, 6):
            continue
        lines.append(_feature_row(r, unknown_keys))
    # category 1 is excluded throughout: models have their own matrix (models.md);
    # category 4 has its own vocabulary — next section
    for k in sorted(unknown_keys):
        print(f"warn: feature key '{k}' not in the feature taxonomy — not rendered", file=sys.stderr)

    lines += [
        "",
        "## Workflow frameworks (category 4)",
        "",
        "The category-4 slice of the feature taxonomy — `workflow_features:` frontmatter,",
        "defined in `docs/feature-taxonomy.yaml`. Structural",
        "presence-claims, not value-claims:",
        "a ✓ says the machinery exists in source/docs, not that it pays (that is the",
        "mechanism table's job, tools/4-workflow-frameworks/README.md).",
        "",
        "| Tool | license | access | " + " | ".join(k.replace("_", " ") for k in WORKFLOW_FEATURE_KEYS) + " |",
        "|---|---|---|" + "---|" * len(WORKFLOW_FEATURE_KEYS),
    ]
    wf_unknown: set[str] = set()
    for r in reports:
        if r.get("category") != 4:
            continue
        feats = r.get("workflow_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        wf_unknown.update(k for k in feats if k not in WORKFLOW_FEATURE_KEYS)
        cells = []
        for key in WORKFLOW_FEATURE_KEYS:
            v = feats.get(key)
            if v is True:
                cells.append("✓")
            elif v is False:
                cells.append("✗")
            elif v is None:
                cells.append("·")
            else:
                cells.append(f"`{v}`")
        rel = r["_path"].relative_to(ROOT)
        # the license+access PAIR, rendered as two cells (ADR-0044): terms, then reach
        pair = f"{r.get('license') or '·'} | `{r.get('access') or '·'}`"
        lines.append(f"| [{r['name']}](../{rel}) | {pair} | " + " | ".join(cells) + " |")
    for k in sorted(wf_unknown):
        print(f"warn: workflow feature key '{k}' not in the feature taxonomy — not rendered", file=sys.stderr)

    lines += [
        "",
        "## Memory (category 5)",
        "",
        "The category-5 slice of the feature taxonomy — `memory_features:` frontmatter",
        "(ADR-0013; a full category since ADR-0020). Values are",
        "descriptive enums (mechanism choices), not ADR-0011 enforcement grades. Rows",
        "of dots are stub-depth reports — unread, honestly unclaimed.",
        "",
        "| Tool | license | access | " + " | ".join(k.replace("_", " ") for k in MEMORY_FEATURE_KEYS) + " |",
        "|---|---|---|" + "---|" * len(MEMORY_FEATURE_KEYS),
    ]
    mem_unknown: set[str] = set()
    for r in reports:
        if r.get("category") != 5 or r.get("type") != "memory":
            continue
        feats = r.get("memory_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        mem_unknown.update(k for k in feats if k not in MEMORY_FEATURE_KEYS)
        cells = []
        for key in MEMORY_FEATURE_KEYS:
            v = feats.get(key)
            if v is True:
                cells.append("✓")
            elif v is False:
                cells.append("✗")
            elif isinstance(v, list):
                cells.append(", ".join(f"`{x}`" for x in v))
            elif v is None:
                cells.append("·")
            else:
                cells.append(f"`{v}`")
        rel = r["_path"].relative_to(ROOT)
        # the license+access PAIR, rendered as two cells (ADR-0044): terms, then reach
        pair = f"{r.get('license') or '·'} | `{r.get('access') or '·'}`"
        lines.append(f"| [{r['name']}](../{rel}) | {pair} | " + " | ".join(cells) + " |")
    for k in sorted(mem_unknown):
        print(f"warn: memory feature key '{k}' not in the feature taxonomy — not rendered", file=sys.stderr)

    lines += [
        "",
        "## Execution environments (category 3)",
        "",
        "The category-3 slice of the feature taxonomy — `environment_features:`",
        "frontmatter (ADR-0017), assessed on every category-3 report. Cells carry a",
        "grammar: evidence-grade suffixes, a `family:specific` colon tag on three keys,",
        "and lists that mean conjunction only — see the ADR. Rows of dots are not yet",
        "checked, honestly unclaimed.",
        "",
        "| Tool | license | access | " + " | ".join(k.replace("_", " ") for k in ENVIRONMENT_FEATURE_KEYS) + " |",
        "|---|---|---|" + "---|" * len(ENVIRONMENT_FEATURE_KEYS),
    ]
    env_unknown: set[str] = set()
    for r in reports:
        if r.get("category") != 3:
            continue
        feats = r.get("environment_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        env_unknown.update(k for k in feats if k not in ENVIRONMENT_FEATURE_KEYS)
        cells = []
        for key in ENVIRONMENT_FEATURE_KEYS:
            v = feats.get(key)
            if v is True:
                cells.append("✓")
            elif v is False:
                cells.append("✗")
            elif isinstance(v, list):
                cells.append(", ".join(f"`{x}`" for x in v))
            elif v is None:
                cells.append("·")
            else:
                cells.append(f"`{v}`")
        rel = r["_path"].relative_to(ROOT)
        # the license+access PAIR, rendered as two cells (ADR-0044): terms, then reach
        pair = f"{r.get('license') or '·'} | `{r.get('access') or '·'}`"
        lines.append(f"| [{r['name']}](../{rel}) | {pair} | " + " | ".join(cells) + " |")
    for k in sorted(env_unknown):
        print(f"warn: environment feature key '{k}' not in the feature taxonomy — not rendered", file=sys.stderr)

    lines += _render_cross_category(reports)
    lines.append("")
    return "\n".join(lines)


def render_models(reports: list[dict]) -> str:
    """Category-1 matrix: API features + the spec fields that drift fastest.

    Feature cells come from MODEL_FEATURE_KEYS frontmatter (verified-only; · =
    not checked). Spec cells come from the existing frontmatter fields. `checked`
    is a column because a model row with a stale date is a rumor.
    """
    cols = MODEL_LIFECYCLE_KEYS + MODEL_FEATURE_KEYS + [
        "context_window", "max_output", "pricing",
        "knowledge_cutoff", "checked", "depth"]
    lines = [
        "# Model matrix (category 1)",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit the frontmatter of tools/1-models/*.md, then re-run. -->",
        "",
        "API-feature cells are set only when verified against the report's `url` on",
        "its `checked` date — **·** means not checked, never absent. The reasoning keys",
        "are typed (ADR-0040): `reasoning` is ✓/✗, `reasoning_type` a closed enum, and",
        "`reasoning_effort` a `family:specific` dial where the family says who sizes the",
        "reasoning — a level set the model spends against (`levels:<set>@<default>`) or a",
        "budget the caller allocates (`budget:<unit>`). The caching and batch keys stay",
        "free-text because the economics differ structurally across vendors.",
        "`released` carries first-availability date **plus lifecycle stage** in the",
        "vendor's own vocabulary (GA / Preview / beta) — stages don't align across",
        "vendors, so the stage word is part of the fact, same verified-only rule.",
        "",
        "| Model | " + " | ".join(c.replace("_", " ") for c in cols) + " |",
        "|---|" + "---|" * len(cols),
    ]
    for r in reports:
        if r.get("category") != 1:
            continue
        cells = []
        model_feats = r.get("model_features") or {}
        for c in cols:
            v = model_feats.get(c) if c in MODEL_FEATURE_KEYS else r.get(c)
            if v is None:
                cells.append("·")
            elif c == "pricing":
                cells.append(fmt_pricing(v))
            elif c == "knowledge_cutoff":
                cells.append(fmt_cutoff(v))
            else:
                cells.append(
                    fmt_feature_cell(v) if c in MODEL_FEATURE_KEYS else str(v)
                )
        rel = r["_path"].relative_to(ROOT)
        lines.append(f"| [{r['name']}](../{rel}) | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def fmt_feature_cell(v) -> str:
    """One registry cell, rendered. Shared by every feature matrix so a `presence`
    key reads the same wherever it appears — `·` is not-checked, `✗` is
    checked-and-absent, and the two are never collapsed. Extracted from
    `render_features`'s harness rows when ADR-0040 gave the `model_features` block
    its first boolean (`reasoning`): the models matrices formatted every cell as
    code, so a bare True would have rendered as `` `True` ``.
    """
    if v is True:
        return "✓"
    if v is False:
        return "✗"
    if isinstance(v, list):
        return ", ".join(f"`{x}`" for x in v)
    if v is None:
        return "·"
    return f"`{v}`"


def fmt_cutoff(c) -> str:
    """Date first so the column sorts by eye, then what kind of claim it is, then the
    prose the date cannot hold (ADR-0037)."""
    if not isinstance(c, dict):
        return str(c)
    head = f"**{c['date']}**" if c.get("date") else "**—**"
    head += f" · `{c.get('basis')}`"
    return f"{head} — {c['note']}" if c.get("note") else head


def fmt_pricing(p) -> str:
    """`$5 / $25` first, then the regime, then the note — the column leads with the
    comparable numbers and still carries everything the prose held (ADR-0033)."""
    if not isinstance(p, dict):
        return str(p)
    def money(x):
        # Money reads with two decimals or none — never "$1.4", which looks like a typo.
        return f"{x:,.2f}" if isinstance(x, float) and not x.is_integer() else f"{int(x):,}"
    sym = "$" if p.get("currency") == "USD" else f"{p.get('currency')} "
    head = f"**{sym}{money(p['input'])} / {sym}{money(p['output'])}** per MTok"
    regime = p.get("regime")
    if regime and regime != "flat":
        head += f" · `{regime}`"
    note = p.get("note")
    return f"{head} — {note}" if note else head


def render_feature_registry() -> str:
    """A readable rendering of the feature taxonomy's YAML registry.

    The registry lives in docs/feature-taxonomy.yaml —
    machine-read as the single source of truth for valid keys, but rendered by GitHub
    as a raw code block. This file is that block re-rendered as linked tables, one per
    category in repo order (1→6), each merging the placement test's two halves —
    assessed registry keys and transcription fields — told apart by the Basis column.
    Generated so it cannot drift (rule 3). Definitions and notes are carried verbatim —
    the notes are the registry's institutional memory, and the scannability comes from
    the table structure, not from shortening the evidence.
    """
    # Static per-block framing: the value regime — the one piece of block-level
    # semantics the per-entry YAML doesn't carry. These change only when a block's
    # ADR does; the keys/definitions/notes below them are fully registry-driven.
    block_framing = {
        "harness_features": (
            "Assessed rows are presence-claims; `turn_end_gates` is graded (engine \\| "
            "hook \\| script \\| prose) per ADR-0011/0012. Cells render in "
            "[features.md → Harnesses](features.md#harnesses-category-2).",
        ),
        "model_features": (
            "Assessed rows split by what the fact is (ADR-0040): the three reasoning "
            "keys are typed — `reasoning` a presence-claim, `reasoning_type` a closed "
            "enum of TOGGLEABILITY, `reasoning_effort` a `family:specific` dial whose "
            "family (`levels:` \\| `budget:`) says who sizes the reasoning — while "
            "`prompt_caching` and `batch_discount` stay free-text in the vendor's own "
            "terms, because the economics differ structurally across vendors. All "
            "verified against each report's `url` on its `checked` date (ADR-0014). "
            "Cells render in [features.md → Models](features.md#models-category-1) "
            "and [models.md](models.md).",
        ),
        "workflow_features": (
            "Assessed rows are presence-claims; the three gate keys are graded (engine "
            "\\| hook \\| script \\| prose) per ADR-0011 — a bare ✓ is an unanswered "
            "who-enforces question. Cells render in "
            "[features.md → Workflow frameworks](features.md#workflow-frameworks-category-4).",
        ),
        "memory_features": (
            "Assessed rows are descriptive enums — mechanism choices, not ADR-0011 "
            "enforcement grades — and apply to `type: memory` reports only (ADR-0013). "
            "Cells render in [features.md → Memory](features.md#memory-category-5).",
        ),
        "environment_features": (
            "Assessed cell values carry their own grammar: evidence-grade suffixes, a "
            "`family:specific` colon tag on three keys, lists meaning conjunction only — "
            "see ADR-0017. Cells render in "
            "[features.md → Execution environments](features.md#execution-environments-category-3).",
        ),
    }
    esc = lambda s: str(s).replace("|", "\\|")  # noqa: E731 — registry text uses ` | ` in enums
    lines = [
        "# Feature registry, rendered",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit docs/feature-taxonomy.yaml, then re-run. -->",
        "",
        "Every characteristic recorded on tools, one table per category in repo order",
        "(1→6) — a readable rendering of the",
        "[feature taxonomy](../docs/feature-taxonomy.md)'s YAML registry,",
        "which stays the single editable source of truth (its conventions — the",
        "placement test, the two-verified-instances rule, omitted = not checked vs",
        "`false` = checked-absent — live there and are not repeated here). Each table",
        "merges the placement test's two halves, told apart by **Basis**:",
        "",
        "- **assessed** — a registry key: a capability assessed by reading, comparable",
        "  across tools under one definition, carried in the category's feature block.",
        "- **transcribed** — a fact with an external ground truth: a top-level",
        "  frontmatter field, transcribed and dated, never duplicated as a key",
        "  (enforced: the generator refuses an id that appears in both lists). A",
        "  transcribed field spanning categories (`maker`, `license`, `access`) appears",
        "  in every section it applies to.",
        "",
        "**Type** is the shape a cell's value takes — the registry's own",
        "`value_type` vocabulary rather than generic types (ADR-0032), because two of",
        "these distinctions are load-bearing and `boolean`/`enum`/`text` would erase",
        "them:",
        "",
        "- **`presence`** — a ✓/✗ presence-claim. Omitted means *not checked*,",
        "  `false` means *checked and absent*; both are claims.",
        "- **`graded`** — ADR-0011's **ordered** enforcement scale, strongest verified",
        "  enforcer wins: `engine` > `hook` > `script` > `prose`. A bare `true` is an",
        "  explicit unanswered question. Not merely an enum: the order is the finding.",
        "- **`closed-enum`** — exactly one value from a closed set, spelled out in the",
        "  definition (`mount | clone | upload`). A checker could validate against it.",
        "- **`open-descriptive`** — an open vocabulary constrained only in *shape*,",
        "  `family:specific` with the family closed and the specific free (ADR-0017).",
        "  Used where the population keeps producing new mechanisms; the distinction",
        "  from `closed-enum` is exactly what a generic \"enum\" would flatten.",
        "- **`list`** — several values from a stated set, all of them true at once.",
        "- **`free-text`** — the vendor\'s or subject\'s own words, no controlled",
        "  vocabulary, because flattening them would destroy the comparison (model",
        "  economics differ structurally across vendors).",
        "- **`string`** · **`number`** · **`date`** — a single identifier or name, a",
        "  bare count, a date. Transcription fields, mostly.",
        "",
        "A key that is scalar but accepts a list of named instances where naming them",
        "is informative (`rules_files`, `memory_store`) keeps its scalar type and says",
        "so in its definition — list-ness is a property of an instance, not a type.",
        "",
        "**Kind link** names the demand↔supply correspondence: the installable artifact",
        "kind that supplies the feature — `memory` from category 5, every other kind",
        "from category 6 (ADR-0020). **Provenance** carries an assessed key's `note:`",
        "verbatim (when it entered, which verified instances earned it, the calibration",
        "lessons attached to it) — and a transcribed field's verification route:",
        "**dated-docs** — verified against the report's `url` on its `checked` date; for",
        "vendor-defined facts (a price, a context window) the docs *are* the ground",
        "truth, the one place rule 1a's source-beats-testimony ordering inverts ·",
        "**mechanical** — script-collected (`repo-facts.sh`, GitHub API), never",
        "hand-typed · **source-or-docs** — read in the pinned clone or official docs.",
        "Honesty/meta columns (`depth`, `checked`, `read_at`) and tool-taxonomy",
        "classification fields (`category`, `type`) are deliberately absent — they are",
        "not facts about the subject.",
        "",
    ]
    # Sections follow the repo's category order (tool-taxonomy.md, 1→6). Each category's
    # assessed block is found via the min of its entries' applies_to; a category with
    # no assessed block (6 — Extensions) still gets a section for its transcribed rows.
    block_cat: dict[str, int] = {}
    for e in FEATURE_REGISTRY:
        cat = min(e["applies_to"])
        block_cat[e["block"]] = min(block_cat.get(e["block"], cat), cat)
    cat_block = {c: b for b, c in block_cat.items()}
    categories = sorted(
        set(cat_block) | {c for t in TRANSCRIPTION_FIELDS for c in t["applies_to"]}
    )
    header = "| Key | Basis | Type | Definition | Kind link | Provenance |"
    divider = "|---|---|---|---|---|---|"
    for cat in categories:
        block = cat_block.get(cat)
        name = CATEGORY_NAMES.get(cat, "?")
        if block:
            title = f"{name} (category {cat}) — `{block}:` + transcription fields"
            (framing,) = block_framing.get(block, (f"Assessed rows: `{block}:`.",))
        else:
            title = f"{name} (category {cat}) — transcription fields only"
            framing = (
                "No assessed key block exists for this category"
                + (
                    " — its `type` vocabulary is tool-taxonomy classification "
                    "(ADR-0020), not an assessed feature"
                    if cat == 6
                    else ""
                )
                + ". The rows below are the transcription facts collected on its reports."
            )
        lines += [f"## {title}", "", framing, "", header, divider]
        if block:
            for e in (e for e in FEATURE_REGISTRY if e["block"] == block):
                kind = e.get("kind_link")
                kind_cell = f"`{kind}` (cat {5 if kind == 'memory' else 6})" if kind else "—"
                lines.append(
                    f"| `{e['id']}` | assessed | `{e['value_type']}`"
                    f"{' + note' if e.get('renders_note') else ''} | "
                    f"{esc(e['definition'])} | {kind_cell} | "
                    f"{esc(e.get('note', '')) or '—'} |"
                )
        for t in TRANSCRIPTION_FIELDS:
            if cat not in t["applies_to"]:
                continue
            rendered = ", ".join(f"[{x}]({x})" for x in t.get("rendered_in") or [])
            where = f"renders in {rendered}" if rendered else "frontmatter only"
            lines.append(
                f"| `{t['id']}` | transcribed | `{t['value_type']}`"
                f"{' + note' if t.get('renders_note') else ''} | "
                f"{esc(t['definition'])} | — | "
                f"`{t['verification']}` · {where} |"
            )
        lines.append("")
    lines += [
        f"**{len(FEATURE_REGISTRY)} assessed keys across {len(block_cat)} blocks · "
        f"{len(TRANSCRIPTION_FIELDS)} transcription fields.**",
        "",
    ]
    return "\n".join(lines)


def render_environments(reports: list[dict]) -> str:
    """Category-5 bindings, from the `environments:` and `environment_relation:` keys.

    Only tools that declare `environments:` appear. That excludes tools with no report
    (Devin, the `bundle` exemplar), which is a real gap and is stated in the prose rather
    than papered over with a stub.
    """
    rows = [r for r in reports if r.get("environments")]
    lines = [
        "# Execution-environment bindings (category 3)",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit the `environments:` / `environment_relation:` frontmatter, then re-run. -->",
        "",
        "Which category-3 environments a tool can run its agent in, and **how it relates to "
        "them** — see the relationship vocabulary in "
        "[`../tools/3-execution-environments/README.md`](../tools/3-execution-environments/README.md).",
        "",
        "Cells: **✓** verified · **·** not yet checked. Same discipline as the feature "
        "matrix — a value is set only when confirmed in source or official docs, so a dot "
        "is *not* a no.",
        "",
        "**This table can only show tools that have reports.** Devin — the clearest "
        "`bundle` case — has no report and so does not appear; the vocabulary below is "
        "therefore wider than the evidence in this table. That gap is the point of the "
        "category-3 adjudication, not an oversight.",
        "",
        "| Tool | Category | " + " | ".join(ENV_KEYS) + " | Relation |",
        "|---|---|" + "---|" * (len(ENV_KEYS) + 1),
    ]
    unknown: set[str] = set()
    bad_relation: set[str] = set()
    for r in rows:
        declared = r.get("environments") or []
        if not isinstance(declared, list):
            declared = [declared]
        declared = [str(x) for x in declared]
        unknown.update(e for e in declared if e not in ENV_KEYS)
        cells = ["✓" if k in declared else "·" for k in ENV_KEYS]
        relation = r.get("environment_relation")
        if relation is not None and str(relation) not in ENV_RELATIONS:
            bad_relation.add(str(relation))
        rel = r["_path"].relative_to(ROOT)
        lines.append(
            f"| [{r['name']}](../{rel}) | {r['category']} | " + " | ".join(cells)
            + f" | {f'**{relation}**' if relation else '·'} |"
        )
    for e in sorted(unknown):
        print(f"warn: environment '{e}' not in ENV_KEYS — rendered as absent", file=sys.stderr)
    for v in sorted(bad_relation):
        print(f"warn: environment_relation '{v}' not in ENV_RELATIONS", file=sys.stderr)
    lines += ["", f"**{len(rows)} of {len(reports)} reports declare `environments:`.**", ""]
    return "\n".join(lines)



def main() -> int:
    reports = collect()
    if not reports:
        print("no reports with frontmatter found", file=sys.stderr)
        return 1
    # Runs under BOTH invocations: --check must catch a malformed price, and a plain
    # run must refuse to render one.
    check_pricing(reports)
    check_cutoff(reports)
    check_reasoning(reports)
    check_access(reports)

    if "--check" in sys.argv:
        problems = check(reports)
        print(f"{len(reports)} reports checked, {problems} unverifiable "
              f"(drift is reported above and is not a failure)")
        return 1 if problems else 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(reports), encoding="utf-8")
    FEATURES_OUT.write_text(render_features(reports), encoding="utf-8")
    ENVIRONMENTS_OUT.write_text(render_environments(reports), encoding="utf-8")
    MODELS_OUT.write_text(render_models(reports), encoding="utf-8")
    FEATURE_REGISTRY_OUT.write_text(render_feature_registry(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(reports)} tools")
    print(f"wrote {FEATURES_OUT.relative_to(ROOT)}")
    print(f"wrote {ENVIRONMENTS_OUT.relative_to(ROOT)}")
    print(f"wrote {MODELS_OUT.relative_to(ROOT)}")
    print(f"wrote {FEATURE_REGISTRY_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
