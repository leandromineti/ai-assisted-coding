#!/usr/bin/env python3
"""scripts/check-secrets.py — published-text secret scan: the pre-commit gate
that asks "would anything this repo publishes carry a secret?".

Origin: Phase 16 carry-over (c) and the owner's question of 2026-11-05. The repo
is PUBLIC, and Phase 16 ran release binaries under scratch envs; a one-off scan
found no secret in the tree, and this script turns that one-off check into a
standing gate (quick task 261105-mud). It complements probes/audit-evidence.py,
which covers only probes/raw/*.jsonl and probes/ledger.jsonl and looks for
org/account-identifying content, not credentials. Nothing else guarded the rest
of the tree.

    python3 scripts/check-secrets.py --check
    python3 scripts/check-secrets.py --selftest

Exit codes: 0 clean, 1 findings, 2 bad invocation (no flag, both flags, an
unknown flag) or a failed `git ls-files` (an unenumerated tree is never
reported as clean).

SCOPE. Every path `git ls-files --cached --others --exclude-standard` lists:
tracked files plus untracked files that are not gitignored (a file not yet
`git add`ed is one commit from public). Gitignored paths (upstream/, .planning/,
upstream/_runtimes/) are never published and never scanned. There is no
path-level exclusion of any kind.

TWO RULE CLASSES.

1. VALUE scan: the real secret VALUES this machine holds, read in-process only.
   Candidates are (a) env vars whose NAME matches TOKEN|SECRET|KEY|PASS|AUTH|CRED
   case-insensitively (AUTH is not matched inside AUTHOR, so GIT_AUTHOR_NAME and
   GIT_AUTHOR_EMAIL are never candidates, but AUTHORIZATION still is), and
   (b) every `NAME=value` / `export NAME=value` line in a regular file directly
   inside ~/.secrets (non-recursive, symlinks skipped), whatever the NAME,
   because the file is secret by location. One layer of matching quotes is
   stripped. A missing ~/.secrets yields 0 file candidates; a secrets file that
   exists but cannot be read is a finding (rule=secrets-file-unreadable), never a
   silent skip. A candidate is kept only if it is "meaningful": at least
   MIN_VALUE_LEN (12) characters, not path-like (a leading /, ~, ./ or ../), not
   all digits, and not a boolean/null word (true, false, yes, no, on, off, null,
   none). The scan is a byte search over EVERY file, text or binary (a tracked
   .pyc is still checked for a real value). A value finding is NEVER
   allowlistable.

2. SHAPE scan: secret-shaped strings, on files with no NUL byte, line by line
   (SHAPES below: sk-api-key, github-token, aws-access-key-id, slack-token, jwt,
   google-api-key, secret-assignment). The assignment shape takes UPPER_SNAKE
   names only (see CALIBRATION). A shape match that is a documented synthetic
   value may be suppressed by a SHAPE_ALLOWLIST entry.

NEVER PRINT. A finding structurally has no field that holds a matched or candidate
value. A finding names file:line plus exactly one of: the source NAME
(env:NAME or secrets-file:<basename>:NAME), a shape class with its fingerprint,
or a rule. The fingerprint is the first 12 hex digits of the sha256 of the
matched text: a 48-bit truncation, irreversible for a real key, present only so
an allowlist entry can pin one specific match. Value findings carry no
fingerprint. --selftest captures every byte the scanner prints during its
fixtures and asserts no fixture value appears in it.

ALLOWLIST. SHAPE_ALLOWLIST entries pin (file, shape, fp) with a written reason.
An entry that matches nothing at the end of a run is a stale-allowlist finding,
so the list cannot silently accumulate. A different value in the same file and
shape still fires (a fingerprint narrows, never widens). Never edit a pattern or
add a path exclusion to silence a finding: a real secret is rotated and then
removed from the content; a synthetic match gets an allowlist entry.

CALIBRATION (re-derived 2026-11-05 at HEAD 0264145 by quick task 261105-mud):
- Value scan over the tracked tree: 0 hits.
- Shape scan, empty allowlist: exactly 1 hit, probes/audit-evidence.py:400,
  sk-api-key, that file's own selftest fixture (a synthetic value built from the
  words not-a-real-key plus zeros, planted to prove its vendor-key-fragment rule
  fires). It is the one SHAPE_ALLOWLIST entry below.
- The assignment shape, first draft: 20 extra hits, all one banner line
  ("=== PASSES ====": name PASSES contains PASS, value all `=`), same
  fingerprint across 20 experiments/03 score.txt files. Not a secret; the value
  must now start with an alphanumeric-ish character, and a selftest case proves
  the banner passes while a real-shaped value still fires.
- The assignment shape run once in a scratch copy, case-insensitively: 38 hits
  in 21 files (docs, references, probes/harness, tools), names budget_tokens,
  max_tokens, max_tokens_field, reasoning_tokens, prompt_cache_key, content_key,
  key_env_var, top_key, fake_key, key. Every one is a lowercase code or prose
  identifier, none a secret, which is the evidence for restricting the shape to
  UPPER_SNAKE names (0 hits at HEAD). A real credential still fires through the
  value scan and the other six shapes.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRETS_DIR = Path.home() / ".secrets"

MIN_VALUE_LEN = 12

USAGE = "check-secrets.py --check | --selftest"

# Env-var NAMEs that make a variable a value candidate. AUTH is not matched when
# it is the start of AUTHOR (GIT_AUTHOR_NAME/EMAIL values are never secrets and
# appear in prose), but still matches AUTHORIZATION / AUTHORISATION.
_CANDIDATE_NAME_RE = re.compile(r"TOKEN|SECRET|KEY|PASS|AUTH(?!OR(?!IZ|IS))|CRED", re.IGNORECASE)
_ASSIGN_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
_BOOL_WORDS = frozenset({"true", "false", "yes", "no", "on", "off", "null", "none"})

SHAPES = (
    ("sk-api-key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{7,}\.eyJ[A-Za-z0-9_-]{7,}\.[A-Za-z0-9_-]{10,}")),
    # audit-evidence.py already treats AIza as a vendor-key shape for this repo.
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])")),
    # UPPER_SNAKE names only, case-sensitive (see CALIBRATION). A $VAR reference
    # value never matches: `$` is outside the value class. The value must START
    # with an alphanumeric-ish character, so a banner line such as
    # "=== PASSES ====" (name PASSES, value all `=`) is not an assignment.
    ("secret-assignment", re.compile(
        r"(?<![A-Za-z0-9_])(?=[A-Z])[A-Z0-9_]*(?:TOKEN|SECRET|KEY|PASS|AUTH|CRED)[A-Z0-9_]*"
        r"[ ]*[=:][ ]*[\"']?[A-Za-z0-9_+/][A-Za-z0-9_+/=.-]{19,}"
    )),
)

# Named exemptions, each pinned by (file, shape, fp) with a written reason. The
# fp is copied from the tool's own FINDING output, never typed by hand.
SHAPE_ALLOWLIST = (
    {
        "file": "probes/audit-evidence.py",
        "shape": "sk-api-key",
        "fp": "4d5c556d828d",
        "reason": "audit-evidence.py's own selftest fixture: a synthetic value planted "
                  "to prove its vendor-key-fragment rule fires, not a credential.",
    },
)


class EnumerationError(Exception):
    """git could not enumerate the publishable files (exit 2, never 'clean')."""


def list_files(root: Path) -> list[str]:
    """Sorted unique repo-relative paths git would publish: tracked plus
    untracked-but-not-gitignored. Raises EnumerationError on any failure."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True,
        )
    except OSError as e:
        raise EnumerationError(f"cannot run git: {e.strerror or e}") from e
    if proc.returncode != 0:
        raise EnumerationError(f"git ls-files failed (exit {proc.returncode})")
    names = {p for p in proc.stdout.decode("utf-8", errors="surrogateescape").split("\0") if p}
    return sorted(names)


def is_meaningful_value(value: str) -> bool:
    if len(value) < MIN_VALUE_LEN:
        return False
    if value.startswith(("/", "~", "./", "../")):
        return False
    if value.isdigit():
        return False
    if value.lower() in _BOOL_WORDS:
        return False
    return True


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def collect_candidates(environ, secrets_dir):
    """Returns ({value: sorted source labels}, [problem findings]). Values stay
    in memory; only labels ever leave this function through a finding."""
    found: dict[str, set[str]] = {}
    problems: list[dict] = []
    for name, value in environ.items():
        if _CANDIDATE_NAME_RE.search(name) and is_meaningful_value(value):
            found.setdefault(value, set()).add(f"env:{name}")
    if secrets_dir is not None:
        sdir = Path(secrets_dir)
        if sdir.is_dir():
            for path in sorted(sdir.iterdir()):
                if path.is_symlink() or not path.is_file():
                    continue
                try:
                    text = path.read_text(errors="replace")
                except OSError:
                    problems.append({"file": f"~/.secrets/{path.name}", "line": None,
                                     "rule": "secrets-file-unreadable"})
                    continue
                for raw in text.splitlines():
                    m = _ASSIGN_LINE_RE.match(raw)
                    if not m:
                        continue
                    value = _strip_quotes(m.group(2))
                    if is_meaningful_value(value):
                        found.setdefault(value, set()).add(f"secrets-file:{path.name}:{m.group(1)}")
    return {v: sorted(labels) for v, labels in found.items()}, problems


def _fp(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]


def scan_bytes(rel: str, data: bytes, cand_pairs, allowlist, used: set):
    """Pure: scan one file's bytes. Returns (findings, is_binary). cand_pairs is
    [(value_bytes, 'label,label')]. Findings never carry a value."""
    findings: list[dict] = []
    for vbytes, source in cand_pairs:
        start = 0
        seen_lines: set[int] = set()
        while True:
            idx = data.find(vbytes, start)
            if idx < 0:
                break
            line = data.count(b"\n", 0, idx) + 1
            if line not in seen_lines:
                seen_lines.add(line)
                findings.append({"file": rel, "line": line, "source": source})
            start = idx + 1
    is_binary = b"\x00" in data
    if not is_binary:
        text = data.decode("utf-8", errors="replace")
        for lineno, line in enumerate(text.split("\n"), 1):
            for shape, pattern in SHAPES:
                for m in pattern.finditer(line):
                    fp = _fp(m.group(0))
                    hit = next((i for i, e in enumerate(allowlist)
                                if e["file"] == rel and e["shape"] == shape and e["fp"] == fp), None)
                    if hit is not None:
                        used.add(hit)
                        continue
                    findings.append({"file": rel, "line": lineno, "shape": shape, "fp": fp})
    return findings, is_binary


def scan_repo(root: Path, environ, secrets_dir, allowlist=SHAPE_ALLOWLIST) -> dict:
    """Enumerate, collect candidates, scan, and report stale allowlist entries.
    Raises EnumerationError. environ/secrets_dir are injected (selftest never
    reads the real ones)."""
    files = list_files(root)
    cands, findings = collect_candidates(environ, secrets_dir)
    cand_pairs = [(v.encode("utf-8"), ",".join(labels)) for v, labels in cands.items()]
    used: set[int] = set()
    scanned = binary = skipped = 0
    for rel in files:
        path = Path(root) / rel
        if path.is_symlink():
            skipped += 1
            continue
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            skipped += 1
            continue
        except IsADirectoryError:
            skipped += 1
            continue
        except OSError:
            findings.append({"file": rel, "line": None, "rule": "unreadable-file"})
            continue
        scanned += 1
        file_findings, is_bin = scan_bytes(rel, data, cand_pairs, allowlist, used)
        findings.extend(file_findings)
        binary += 1 if is_bin else 0
    for i, entry in enumerate(allowlist):
        if i not in used:
            findings.append({"file": "allowlist", "line": None, "rule": "stale-allowlist",
                             "entry_file": entry["file"], "shape": entry["shape"], "fp": entry["fp"]})
    n_sources = len({label for labels in cands.values() for label in labels})
    return {"findings": findings, "files": scanned, "binary": binary, "skipped": skipped,
            "candidates": len(cands), "sources": n_sources}


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        if f.get("rule") == "stale-allowlist":
            print(f"FINDING allowlist rule=stale-allowlist file={f['entry_file']} "
                  f"shape={f['shape']} fp={f['fp']}", file=sys.stderr)
        elif "source" in f:
            print(f"FINDING {f['file']}:{f['line']} source={f['source']}", file=sys.stderr)
        elif "shape" in f:
            print(f"FINDING {f['file']}:{f['line']} shape={f['shape']} fp={f['fp']}", file=sys.stderr)
        else:
            print(f"FINDING {f['file']} rule={f['rule']}", file=sys.stderr)


def _value_line(res: dict) -> str:
    if res["candidates"] == 0:
        return "value scan: 0 candidates (no qualifying env or ~/.secrets values) — shape scan only"
    return f"value scan: {res['candidates']} candidate value(s) from {res['sources']} source name(s)"


def _summary_line(res: dict) -> str:
    return (f"{res['files']} files scanned ({res['binary']} binary: value scan only, "
            f"{res['skipped']} skipped), {len(res['findings'])} problem(s)")


# ---------------------------------------------------------------- selftest

def _blk(n: int, unit: str = "aB3dE5fG7hJ9") -> str:
    """Synthetic filler assembled at runtime (never a source literal that
    matches a shape)."""
    return (unit * (n // len(unit) + 1))[:n]


def _git(td: str, *args: str) -> None:
    subprocess.run(["git", "-C", td, *args], check=True, capture_output=True)


def _run_cases(note) -> tuple[int, int]:
    """Runs the fixture cases. `note(value)` registers every fixture value for
    the no-echo assertion. Returns (cases, problems)."""
    cases = 0
    problems = 0

    def check(ok: bool, msg: str) -> None:
        nonlocal cases, problems
        cases += 1
        if not ok:
            problems += 1
            print(f"FAIL selftest: {msg}", file=sys.stderr)

    def scan(data: bytes, cands=None, allowlist=(), rel="f.txt"):
        used: set[int] = set()
        pairs = [(v.encode(), ",".join(l)) for v, l in (cands or {}).items()]
        out, is_bin = scan_bytes(rel, data, pairs, allowlist, used)
        _print_findings(out)
        return out, is_bin, used

    # --- MUST FAIL: one fixture per shape class (assembled at runtime) ---
    shape_fixtures = {
        "sk-api-key": "s" + "k-" + "ant-" + _blk(30),
        "github-token (ghp_)": "gh" + "p_" + _blk(40),
        "github-token (gho_)": "gh" + "o_" + _blk(40),
        "github-token (github_pat_)": "github" + "_pat_" + _blk(30),
        "aws-access-key-id": "AK" + "IA" + "ABCD1234EFGH5678",
        "slack-token": "xo" + "xb-" + "1234567890-abcdefghij",
        "jwt": "ey" + "J" + _blk(20) + "." + "ey" + "J" + _blk(20) + "." + _blk(30),
        "google-api-key": "AI" + "za" + _blk(35),
        "secret-assignment": "FAKE_SERVICE" + "_TOKEN" + "=" + _blk(32, "Qw7Zx2Lm9Kp4"),
    }
    for label, val in shape_fixtures.items():
        note(val)
        out, _, _ = scan(("# header\nvalue here: " + val + "\n").encode())
        want = label.split(" ")[0]
        check(any(f.get("shape") == want and f["line"] == 2 for f in out),
              f"shape fixture not reported: {label}")

    # --- MUST FAIL: injected env value reported with NAME + right line ---
    env_val = _blk(24, "Zq8Lm2Ty5Vb")
    note(env_val)
    cands, probs = collect_candidates({"FAKE_SERVICE_TOKEN": env_val}, None)
    out, _, _ = scan(("a\nb\nuse " + env_val + " here\n").encode(), cands)
    check(not probs and any(f.get("source") == "env:FAKE_SERVICE_TOKEN" and f["line"] == 3 for f in out),
          "injected env value not reported with source NAME and line")

    # --- MUST FAIL: injected secrets dir value (export + quotes) ---
    sec_val = _blk(26, "Hn4Rt6Yu8Wc")
    note(sec_val)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "x.env").write_text("# c\nexport FAKE_KEY=\"" + sec_val + "\"\nnot an assignment line\n")
        cands, probs = collect_candidates({}, Path(td))
        out, _, _ = scan(("one\n" + sec_val + "\n").encode(), cands)
        check(not probs and any(f.get("source") == "secrets-file:x.env:FAKE_KEY" and f["line"] == 2 for f in out),
              "injected secrets-file value not reported with source NAME and line")

    # --- MUST FAIL: value inside a binary reported; shape inside it is not ---
    bin_val = _blk(22, "Jd3Fg5Hk7Lz")
    note(bin_val)
    cands, _ = collect_candidates({"FAKE_BIN_SECRET": bin_val}, None)
    shape_in_bin = "s" + "k-" + _blk(30)
    note(shape_in_bin)
    out, is_bin, _ = scan(b"\x00\x01\n" + bin_val.encode() + b"\n" + shape_in_bin.encode(), cands)
    check(is_bin and any(f.get("source") == "env:FAKE_BIN_SECRET" and f["line"] == 2 for f in out),
          "a value inside a binary was not reported")
    check(not any("shape" in f for f in out), "a shape inside a binary was reported (shape scan must skip binaries)")

    # --- MUST FAIL: unreadable secrets file ---
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "locked.env"
        p.write_text("FAKE_KEY=" + _blk(20) + "\n")
        p.chmod(0o000)
        try:
            readable = True
            try:
                p.read_text()
            except OSError:
                readable = False
            if readable:  # running as root: cannot make a file unreadable
                check(True, "")
            else:
                _, probs = collect_candidates({}, Path(td))
                check(any(f["rule"] == "secrets-file-unreadable" for f in probs),
                      "an unreadable secrets file was silently skipped")
        finally:
            p.chmod(0o644)

    # --- allowlist: stale entry, different fp, matching entry ---
    allow_val = "s" + "k-" + _blk(30, "Mn5Bv7Cx9Zq")
    other_val = "s" + "k-" + _blk(30, "Pl2Ok4Ij6Uh")
    note(allow_val)
    note(other_val)
    entry = {"file": "f.txt", "shape": "sk-api-key", "fp": _fp(allow_val), "reason": "fixture"}
    out, _, used = scan(("x " + allow_val + "\n").encode(), allowlist=(entry,))
    check(not out and used == {0}, "an allowlisted (file, shape, fp) entry was reported or not marked used")
    out, _, used = scan(("x " + other_val + "\n").encode(), allowlist=(entry,))
    check(any(f.get("shape") == "sk-api-key" for f in out) and used == set(),
          "a different value at the same file+shape as an allowlist entry was suppressed")
    with tempfile.TemporaryDirectory() as td:
        _git(td, "init", "-q")
        (Path(td) / "a.txt").write_text("nothing here\n")
        _git(td, "add", "a.txt")
        res = scan_repo(Path(td), {}, None, allowlist=(entry,))
        _print_findings(res["findings"])
        check(any(f.get("rule") == "stale-allowlist" for f in res["findings"]),
              "an allowlist entry matching nothing was not reported as stale")

    # --- MUST PASS: placeholders, short stub, $VAR reference, lowercase *_tokens ---
    passing = [
        "sk" + "-...",
        'ANTHROPIC_API_KEY="$PERSONAL_ANTHROPIC_KEY"',
        "gh" + "p_" + "abc123",
        "max_tokens: max_completion_tokens_for_this_request",
        "the sk" + "-ant- prefix is documented",
        "=" * 3 + " PASSES " + "=" * 40,
    ]
    out, _, _ = scan(("\n".join(passing) + "\n").encode())
    check(not out, "a placeholder, short stub, $VAR reference or lowercase *_tokens line was reported")

    # --- MUST PASS: non-meaningful env values; AUTHOR vs AUTHORIZATION ---
    cands, _ = collect_candidates({
        "A_TOKEN": "short", "B_KEY": "/usr/local/some/path/dir", "C_SECRET": "123456789012345",
        "D_PASS": "TRUE", "E_AUTH": "none", "F_CRED": "~/home/x/creds/file",
    }, None)
    check(not cands, "short/path/digit/boolean env values produced candidates")
    cands, _ = collect_candidates({
        "GIT_AUTHOR_NAME": "Some Person Name", "GIT_AUTHOR_EMAIL": "someone@example.invalid",
        "HTTP_AUTHORIZATION": "Bearer-token-like-value-0001",
    }, None)
    check(list(cands.values()) == [["env:HTTP_AUTHORIZATION"]],
          "GIT_AUTHOR_* was a candidate or HTTP_AUTHORIZATION was not")

    # --- END TO END in a temp git repo: tracked, untracked-unignored, ignored ---
    e2e_val = _blk(28, "Rt9Yu1Io3Pa")
    note(e2e_val)
    with tempfile.TemporaryDirectory() as td:
        _git(td, "init", "-q")
        (Path(td) / ".gitignore").write_text("ignored.txt\n")
        (Path(td) / "tracked.txt").write_text("x\n" + e2e_val + "\n")
        (Path(td) / "untracked.txt").write_text(e2e_val + "\n")
        (Path(td) / "ignored.txt").write_text(e2e_val + "\n")
        _git(td, "add", ".gitignore", "tracked.txt")
        res = scan_repo(Path(td), {"FAKE_E2E_TOKEN": e2e_val}, None, allowlist=())
        _print_findings(res["findings"])
        got = {(f["file"], f["line"]) for f in res["findings"]}
        check(got == {("tracked.txt", 2), ("untracked.txt", 1)},
              "end-to-end scan did not report exactly the tracked and untracked-unignored files")
        check(res["files"] == 3 and res["candidates"] == 1, "end-to-end counts are wrong")

    # --- non-repo directory raises the enumeration error (exit-2 path) ---
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get("GIT_CEILING_DIRECTORIES")
        os.environ["GIT_CEILING_DIRECTORIES"] = str(Path(td).parent)
        try:
            try:
                list_files(Path(td))
                raised = False
            except EnumerationError:
                raised = True
        finally:
            if old is None:
                os.environ.pop("GIT_CEILING_DIRECTORIES", None)
            else:
                os.environ["GIT_CEILING_DIRECTORIES"] = old
        check(raised, "a non-repo directory did not raise the enumeration error")

    return cases, problems


def selftest() -> tuple[int, int]:
    """Runs the embedded fixtures. Never reads os.environ for candidates or the
    real ~/.secrets: every case injects both. All scanner output produced during
    the cases is captured, asserted free of every fixture value, then replayed
    to stderr."""
    values: list[str] = []
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        cases, problems = _run_cases(values.append)
    captured = buf.getvalue()
    cases += 1
    if any(v in captured for v in values):
        problems += 1
        print("FAIL selftest: a fixture value appeared in captured scanner output", file=sys.stderr)
    sys.stderr.write(captured)
    return cases, problems


# -------------------------------------------------------------------- main

def main() -> int:
    parser = argparse.ArgumentParser(prog="check-secrets.py", usage=USAGE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.check == args.selftest:  # neither or both
        print(f"usage: {USAGE}", file=sys.stderr)
        return 2

    if args.selftest:
        cases, problems = selftest()
        print(f"{cases} cases run, {problems} problem(s)")
        return 1 if problems else 0

    try:
        res = scan_repo(REPO_ROOT, os.environ, DEFAULT_SECRETS_DIR)
    except EnumerationError as e:
        print(f"check-secrets.py: {e}", file=sys.stderr)
        return 2
    print(_value_line(res))
    _print_findings(res["findings"])
    print(_summary_line(res))
    return 1 if res["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
