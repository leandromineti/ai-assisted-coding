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
