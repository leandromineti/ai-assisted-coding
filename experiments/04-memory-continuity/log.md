# exp-04 log — appended live during runs (rule 5)

## 2026-08-19 — gates closed, chain started

- **Spend sign-off, quoted verbatim**: "Go on" — Leandro, 2026-08-19, given immediately
  after the remaining gates (protocol review + sign-off) were restated with the cost
  estimate (<$2 realistic, $5 ceiling, metered). Protocol review: implicit in the same
  reply; the draft had been presented twice with an explicit request for changes.
  Auth decision trail: subscription OAuth for opencode REJECTED by owner (illegal —
  opencode removed it per Anthropic legal request, PR #18186); metered API key placed
  in opencode's own auth store instead ("Done", 2026-08-19).
- **Versions**: opencode 1.18.18 (installed 2026-08-19, curl installer). ai-memory
  v1.28.1 official release binary (sha256-verified) at ~/.local/opt/ai-memory-v1.28.1;
  pin acd9c0b is v1.28.1+16 commits — drift examined: merges, docs, install-hint fixes
  (PI/OMP env var, hint tail), one off-by-default MCP toggle (strip_root_combinators);
  none touch capture/handoff/injection. Accepted for the probe per protocol's
  binary-if-matching clause, with this note as the record. Harness A: Claude Code
  (this box's daily install). Model for opencode arms: pinned per-arm in this log at
  run time.
- **Auth**: opencode → metered Anthropic API key, scoped to
  ~/.local/share/opencode/auth.json (mode 600); deliberately NOT exported as
  ANTHROPIC_API_KEY (rig README's credential-precedence hazard — would hijack Claude
  Code's subscription auth). Connectivity verified with a one-line haiku ping
  ("auth-ok", ~fraction of a cent, 2026-08-19).
- **Network condition (8a)**: host network, ai-memory daemon loopback-bound, Anthropic
  egress open, no egress enforcement — as declared in the protocol; identical across
  all arms. This is a probe, not a rig comparison.

## 2026-08-19 — smoke (5e) + B0 calibration

- **Smoke** (~10:30 UTC): full driver end-to-end, empty memory, opencode +
  claude-haiku-4-5-20251001 (cheap model — driver validation only). Exit 0 AND
  artifact-verified: smoke.scored.json with all 10 questions evaluated; 0/10 hits,
  0/10 non-UNKNOWN — the model honestly declines to guess. Driver validated.
- **B0 calibration** (scored, arm model anthropic/claude-sonnet-5): **0/10 hits,
  0/10 non-UNKNOWN. GATE PASS (≤2/10).** The instrument discriminates — no fact is
  derivable from the workspace; the quiz's no-guessing instruction holds at Sonnet
  tier. Artifacts: scratchpad exp04/{smoke,B0}/ (raw output + scored JSON), copied
  into artifacts/ at arc end.

## 2026-08-19 — capture + arms B1/B1b, B2 blocked then unblocked

- **Capture session** (~10:21–10:24 UTC): 6 turns via `claude -p` / `--continue` in the
  fixture workspace (Claude Code, subscription; project-scoped hooks via
  `install-hooks --config-file` — global ~/.claude untouched; daemon on loopback:41414
  with a dedicated --data-dir). Post-capture fixture check: workspace clean, no fact
  tokens in files. Store: each -p turn registered as its OWN session (6 handoffs); the
  zero-LLM session page stores ~80-char PROMPT PREFIXES (facts truncated mid-sentence);
  assistant turns not captured (--capture-assistant is double-opt-in, off). FULL prompt
  text survives in observations.body + observations_fts. All 10 fact tokens present in
  exactly one handoff each; ZERO in the latest (turn-6 wrap-up) handoff — ground truth
  for the floor.
- **B1 baton-only (scored, sonnet-5): 0/10, all UNKNOWN.** Out-of-box opencode plugin
  config — no `.ai-memory.toml` marker, so session-start briefing not even requested.
  Amendment (dated, pre-B2): **B1b** added with `inject_on_session_start = true`
  marker — **also 0/10**, consistent with ground truth (the served handoff is the
  innocuous latest; verified via GET /handoff: a well-formed briefing with an explicit
  untrusted-data security boundary — ai-memory's trust cell observed live — but no
  facts). The automatic floor for mid-session conversational facts is ZERO.
- **B2 baton+pull, first attempt: RUN FAILED (exit 1)** — Anthropic API rejected
  ai-memory v1.28.1's MCP tool schema: "tools.13 input_schema does not support oneOf at
  the top level". This is precisely what upstream fixed in the 16-commit drift window
  (strip_root_combinators, commit 68d650d) — the release binary predates the fix; the
  PIN contains it. Building at the pin (docker rust, read-only clone) and re-running
  B2 with the pinned binary. A probe finding in its own right: MCP tool schemas vs
  schema-strict model APIs is a live interop seam.

## 2026-08-19 — arms complete, arc closed

B2 10/10 and A-control 10/10 (A-driver failed once on `claude -p` flag parsing —
prompt swallowed, caught by artifact check, re-run via stdin, deviation recorded in
results). Results appended below the untouched protocol; artifacts archived in-repo;
conclusion 14 added; ai-memory report + bucket index updated. Daemon stopped after
runs. Total metered spend ~ $1 (5 sonnet sessions + 2 haiku).
