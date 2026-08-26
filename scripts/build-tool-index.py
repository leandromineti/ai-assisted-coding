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
VENDORS_OUT = ROOT / "comparisons" / "vendors.md"
MODELS_OUT = ROOT / "comparisons" / "models.md"
FEATURE_REGISTRY_OUT = ROOT / "comparisons" / "feature-registry.md"

# Category-5 bindings: which execution environments a tool can run its agent in.
# Order defines the matrix columns.
ENV_KEYS = ["host", "worktree", "container", "remote-sandbox"]

# How a tool relates to the environment it runs in — the category-3 relationship
# vocabulary, one verb per instance, each earned at a different deep-dive. Defined
# in tools/3-execution-environments/index.md; listed here only to validate spelling.
ENV_RELATIONS = ["bundle", "bind", "internalize", "inhabit"]

# Fixed vocabulary — order defines the matrix columns. Keep small and axis-aligned;
# vendor pet names don't get columns.
# The feature taxonomy is the single source of truth for feature keys — one entry
# per assessed characteristic, with definitions, applicability, and demand↔supply
# kind links (ADR-0010). Do NOT hardcode keys here; edit the registry.
FEATURE_REGISTRY_PATH = ROOT / "tools" / "cross-cutting" / "feature-taxonomy.md"


def _load_feature_registry() -> tuple[list[dict], list[dict]]:
    try:
        text = FEATURE_REGISTRY_PATH.read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"feature taxonomy missing: {FEATURE_REGISTRY_PATH} ({e})")
    m = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not m:
        sys.exit(f"feature taxonomy has no ```yaml block: {FEATURE_REGISTRY_PATH}")
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        sys.exit(f"feature taxonomy YAML unparsable: {e}")
    entries = (data or {}).get("features")
    if not isinstance(entries, list) or not entries:
        sys.exit("feature taxonomy: `features:` must be a non-empty list")
    t_fields = (data or {}).get("transcription_fields") or []
    feature_ids = {e.get("id") for e in entries}
    for t in t_fields:
        for req in ("id", "applies_to", "definition", "verification"):
            if req not in t:
                sys.exit(f"transcription field missing `{req}`: {t}")
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
        for req in ("id", "block", "applies_to", "definition"):
            if req not in e:
                sys.exit(f"feature taxonomy entry missing `{req}`: {e}")
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
        if path.name.startswith("_") or path.name == "index.md":
            continue  # templates and category indexes are not reports
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
        # A recorded pin with a clone present is checked regardless of open_source: a
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
        "the category's component decomposition (defined in taxonomy.md) was actually traced, "
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
    ]
    header_row = "| Tool | Surfaces · exec | Stack | License | Stars | Since | Harness targets | Version read | Depth | Report |"
    divider = "|---|---|---|---|---|---|---|---|---|---|"
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
        if not r.get("open_source", True):
            # `open_source: false` usually means "no source to pin against" and the
            # cell should say so plainly. The one exception: a report that sets
            # `closed_source_pin_note` alongside a real `commit` (Daytona's
            # before/after read — `open_source: false` there marks the product's
            # CURRENT post-closure state for narrative purposes, not an absence of
            # pinned source; see daytona.md's frontmatter comment). Opt-in via an
            # explicit field, not inferred from version/commit presence alone, so
            # this stays a one-report exception rather than silently changing
            # every other closed report that happens to carry a version pin
            # (modal, pilot-shell) — CR-01.
            pin_note = r.get("closed_source_pin_note")
            if pin_note and r.get("commit"):
                version = f"{r['commit']} ({pin_note})"
            else:
                version = "closed source"
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
            f"{stack or '—'} | {r.get('license') or '—'} | {stars} | {since} | {targets} | "
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
        "[feature taxonomy](../tools/cross-cutting/feature-taxonomy.md).",
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
        "defined once in the [feature taxonomy](../tools/cross-cutting/feature-taxonomy.md)",
        "(ADR-0010); the [tool taxonomy](../taxonomy.md) classifies the tools themselves.",
        "",
    ]

    def _feature_row(r: dict, unknown: set) -> str:
        feats = r.get("harness_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        unknown.update(k for k in feats if k not in HARNESS_FEATURE_KEYS)
        cells = []
        for key in HARNESS_FEATURE_KEYS:
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
        lic = r.get("license") or "·"
        return f"| [{r['name']}](../{rel}) | {lic} | " + " | ".join(cells) + " |"

    # license is rendered from the reports' existing top-level frontmatter field
    # (single source of truth; NOT a registry key — it is a tool-taxonomy fact)
    header_row = "| Tool | license | " + " | ".join(
        k.replace("_", " ") for k in HARNESS_FEATURE_KEYS
    ) + " |"
    divider = "|---|---|" + "---|" * len(HARNESS_FEATURE_KEYS)
    unknown_keys: set[str] = set()

    lines += [
        "## Models (category 1)",
        "",
        "The category-1 slice — `model_features:` frontmatter (ADR-0014). Free-text",
        "values in the vendor's own terms, verified against the report's `url` on its",
        "`checked` date. Quantitative surface (context, pricing, cutoff, lifecycle)",
        "stays in [models.md](models.md).",
        "",
        "| Model | license | context window | " + " | ".join(k.replace("_", " ") for k in MODEL_FEATURE_KEYS) + " |",
        "|---|---|---|" + "---|" * len(MODEL_FEATURE_KEYS),
    ]
    m_unknown: set[str] = set()
    for r in reports:
        if r.get("category") != 1:
            continue
        feats = r.get("model_features") or {}
        if not isinstance(feats, dict):
            feats = {}
        m_unknown.update(k for k in feats if k not in MODEL_FEATURE_KEYS)
        cells = ["·" if feats.get(k) is None else f"`{feats.get(k)}`" for k in MODEL_FEATURE_KEYS]
        rel = r["_path"].relative_to(ROOT)
        lic = r.get("license") or "·"
        cw = r.get("context_window")
        cw = f"{cw:,}" if isinstance(cw, int) else (cw or "·")
        lines.append(f"| [{r['name']}](../{rel}) | {lic} | {cw} | " + " | ".join(cells) + " |")
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
        "defined in `tools/cross-cutting/feature-taxonomy.md`. Structural",
        "presence-claims, not value-claims:",
        "a ✓ says the machinery exists in source/docs, not that it pays (that is the",
        "mechanism table's job, tools/4-workflow-frameworks/index.md).",
        "",
        "| Tool | license | " + " | ".join(k.replace("_", " ") for k in WORKFLOW_FEATURE_KEYS) + " |",
        "|---|---|" + "---|" * len(WORKFLOW_FEATURE_KEYS),
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
        lic = r.get("license") or "·"
        lines.append(f"| [{r['name']}](../{rel}) | {lic} | " + " | ".join(cells) + " |")
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
        "| Tool | license | " + " | ".join(k.replace("_", " ") for k in MEMORY_FEATURE_KEYS) + " |",
        "|---|---|" + "---|" * len(MEMORY_FEATURE_KEYS),
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
        lic = r.get("license") or "·"
        lines.append(f"| [{r['name']}](../{rel}) | {lic} | " + " | ".join(cells) + " |")
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
        "| Tool | license | " + " | ".join(k.replace("_", " ") for k in ENVIRONMENT_FEATURE_KEYS) + " |",
        "|---|---|" + "---|" * len(ENVIRONMENT_FEATURE_KEYS),
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
        lic = r.get("license") or "·"
        lines.append(f"| [{r['name']}](../{rel}) | {lic} | " + " | ".join(cells) + " |")
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
        "its `checked` date — **·** means not checked, never absent. Values are",
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
                cells.append(str(v))
            else:
                cells.append(f"`{v}`" if c in MODEL_FEATURE_KEYS else str(v))
        rel = r["_path"].relative_to(ROOT)
        lines.append(f"| [{r['name']}](../{rel}) | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_feature_registry() -> str:
    """A readable rendering of the feature taxonomy's YAML registry.

    The registry lives as a ```yaml block in tools/cross-cutting/feature-taxonomy.md —
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
            "Assessed rows are free-text values in the vendor's own terms (economics "
            "differ structurally across vendors), verified against each report's `url` "
            "on its `checked` date (ADR-0014). Cells render in "
            "[features.md → Models](features.md#models-category-1) "
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
        "<!-- Edit the ```yaml block in tools/cross-cutting/feature-taxonomy.md, then re-run. -->",
        "",
        "Every characteristic recorded on tools, one table per category in repo order",
        "(1→6) — a readable rendering of the",
        "[feature taxonomy](../tools/cross-cutting/feature-taxonomy.md)'s YAML registry,",
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
        "  transcribed field spanning categories (`vendor`, `license`) appears in every",
        "  section it applies to.",
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
    # Sections follow the repo's category order (taxonomy.md, 1→6). Each category's
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
    header = "| Key | Basis | Definition | Kind link | Provenance |"
    divider = "|---|---|---|---|---|"
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
                    f"| `{e['id']}` | assessed | {esc(e['definition'])} | {kind_cell} | "
                    f"{esc(e.get('note', '')) or '—'} |"
                )
        for t in TRANSCRIPTION_FIELDS:
            if cat not in t["applies_to"]:
                continue
            rendered = ", ".join(f"[{x}]({x})" for x in t.get("rendered_in") or [])
            where = f"renders in {rendered}" if rendered else "frontmatter only"
            lines.append(
                f"| `{t['id']}` | transcribed | {esc(t['definition'])} | — | "
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
        "[`../tools/3-execution-environments/index.md`](../tools/3-execution-environments/index.md).",
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


def render_vendors(reports: list[dict]) -> str:
    """Vendor coverage among TRACKED tools, grouped by exact `vendor:` string.

    This is the generated half of the vendor-span picture (taxonomy.md → Vendor span).
    It is a LOWER BOUND by construction: closed products with no report (Claude Code,
    cloud Codex, Cursor, Managed Agents) can't appear here, and those belong to the
    vendors with the MOST span — the taxonomy's hand-kept table exists for exactly them.
    """
    by_vendor: dict[str, list[dict]] = {}
    for r in reports:
        by_vendor.setdefault(str(r.get("vendor") or "?"), []).append(r)
    lines = [
        "# Vendor coverage (tracked tools only — a lower bound on vendor span)",
        "",
        "<!-- GENERATED by scripts/build-tool-index.py — do not edit by hand. -->",
        "<!-- Edit the `vendor:` frontmatter of the reports in tools/, then re-run. -->",
        "",
        "One row per `vendor:` string, columns by category. **This understates vendor span "
        "by construction**: it can only show tools that have reports, and the largest "
        "spanners' flagship products are closed with no report (Claude Code, cloud Codex, "
        "Cursor, Managed Agents). The authoritative span picture — including "
        "observation-only products — is the hand-kept table in "
        "[`../taxonomy.md`](../taxonomy.md) → *Vendor span*; this file is its generated, "
        "tracked-only floor.",
        "",
        "| Vendor | 1 · Models | 2 · Harnesses | 3 · Environments | 4 · Frameworks | 5 · Memory | 6 · Extensions | Categories |",
        "|---|---|---|---|---|---|---|---|",
    ]
    def cell(rs: list[dict], category: int) -> str:
        names = [r["name"] for r in rs if r["category"] == category]
        return ", ".join(names) if names else "—"
    # Spanners (≥2 categories) first, then alphabetical
    def sort_key(item):
        vendor, rs = item
        span = len({r["category"] for r in rs})
        return (-span, vendor.lower())
    for vendor, rs in sorted(by_vendor.items(), key=sort_key):
        span = len({r["category"] for r in rs})
        lines.append(
            f"| {vendor} | {cell(rs, 1)} | {cell(rs, 2)} | {cell(rs, 3)} | "
            f"{cell(rs, 4)} | {cell(rs, 5)} | {cell(rs, 6)} | **{span}** |"
        )
    spanners = [v for v, rs in by_vendor.items() if len({r['category'] for r in rs}) >= 2]
    lines += [
        "",
        f"**{len(by_vendor)} vendors** across {len(reports)} tracked tools; "
        f"**{len(spanners)} span ≥2 categories among tracked tools** "
        f"({', '.join(sorted(spanners)) or 'none'}). The gap between this number and the "
        "taxonomy table's is the closed-product blind spot, quantified.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    reports = collect()
    if not reports:
        print("no reports with frontmatter found", file=sys.stderr)
        return 1

    if "--check" in sys.argv:
        problems = check(reports)
        print(f"{len(reports)} reports checked, {problems} unverifiable "
              f"(drift is reported above and is not a failure)")
        return 1 if problems else 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(reports), encoding="utf-8")
    FEATURES_OUT.write_text(render_features(reports), encoding="utf-8")
    ENVIRONMENTS_OUT.write_text(render_environments(reports), encoding="utf-8")
    VENDORS_OUT.write_text(render_vendors(reports), encoding="utf-8")
    MODELS_OUT.write_text(render_models(reports), encoding="utf-8")
    FEATURE_REGISTRY_OUT.write_text(render_feature_registry(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(reports)} tools")
    print(f"wrote {FEATURES_OUT.relative_to(ROOT)}")
    print(f"wrote {ENVIRONMENTS_OUT.relative_to(ROOT)}")
    print(f"wrote {VENDORS_OUT.relative_to(ROOT)}")
    print(f"wrote {MODELS_OUT.relative_to(ROOT)}")
    print(f"wrote {FEATURE_REGISTRY_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
