# Experiment 04 — cross-harness memory continuity: does the kind's headline bet survive contact?

`preregistration drafted: 2026-08-19` · status: **RUN COMPLETE 2026-08-19** *(status
field updated at arc close — the only post-run edit; protocol body below is unedited.
Binding from the sign-off quoted in log.md; the ordered chain — review → sign-off →
fixtures → calibration → scored arms — was followed as written, see log.md.)*

Protocol follows the template line of [`../03-minimal-harness/`](../03-minimal-harness/README.md);
results append below the untouched protocol. `log.md` appended live during runs.

## Question

The memory kind's verified identity bet is **cross-harness continuity** — the one thing
no single harness can absorb (conclusion 8 counter-current; conclusion 13). The
[ADR-0013 matrix](../../comparisons/features.md) showed it is also the kind's
*least-instantiated* feature: exactly one source-verified mechanism (ai-memory's
handoff baton), and that mechanism is thin by design — first prompt + last prompt +
tool names, no LLM, rich memory pull-only via MCP
([ai-memory report](../../notes/05-capability-extensions/ai-memory.md)). The bucket
index's standing rig question: *"capture a session, switch harness, measure what the
second agent actually knows."* This probe answers it for the only tool that can
currently attempt it.

## Subject & pin

ai-memory at report pin `acd9c0b` (deep-dive 2026-08-18). The probe builds/runs the
daemon from the pinned clone (prebuilt release binary acceptable if it matches the
pin's version; record which in log.md). Harness A = Claude Code (installed). Harness
B = opencode (to be installed at a recorded version; issue #17's fallback harness).

## Design

**Fixture: planted facts, not derivable from the workspace (5d's discriminating
instrument).** A scratch project (small TS utility, ~10 files) plus a scripted working
session in harness A that establishes **10 facts conversationally** — never written to
any file by the protocol: 4 decisions (D1–D4, e.g. "we chose base32 ids because of
case-insensitive filesystems"), 3 constraints (C1–C3, e.g. "never bump the schema
field without a migration note"), 2 preferences (P1–P2), 1 task-state item (T1, "the
edge-case in parseRange is unfixed"). The exact fact texts, the capture-session
script, and the 10-question quiz **with a fails-closed binary answer key** are written
and committed BEFORE the capture session runs (5a). A fact scores 1 only if the arm's
answer contains the key's required tokens (regex, case-insensitive); anything else —
including "I don't know" and plausible invention — scores 0.

**Arms** (all n=1 — this is a probe and says so; same workspace snapshot, fresh agent
context per arm):

| Arm | Order | What | Expected if bet holds |
|---|---|---|---|
| **B0 calibration** | FIRST | opencode, fresh session, **no ai-memory**, quiz | ≤2/10 — else facts leak from the workspace and the instrument cannot discriminate (5d): STOP, fix fixtures, re-run B0 before any scored arm |
| **B1 baton-only** | second | opencode + ai-memory hooks, **MCP pull tools denied** (permission config), quiz | the automatic floor — measures what switching harnesses gives you for free |
| **B2 baton+pull** | third | full ai-memory (baton + MCP tools allowed), quiz | the ceiling — measures what an agent that *knows to ask* recovers |
| **A-control** | last | Claude Code (the capture harness), fresh session, full ai-memory, quiz | same-harness comparison — is cross-harness worse than same-harness? |

**Also recorded per arm**: bytes of memory-derived context actually injected (from
hook logs / transcript), whether B2 actually called pull tools unprompted, wall-clock.

**Smoke test (5e)**: the full driver (session spawn → quiz → transcript scoring) runs
once end-to-end with empty memory before anything is scored; success read from
artifacts (a scored quiz JSON exists and every check evaluated), never exit status.

**Declared network condition (8a, honest limitation)**: this probe runs on the HOST,
not the egress-controlled rig — ai-memory's daemon is localhost-bound; model traffic
goes to Anthropic. Declared as: host network, daemon loopback, no egress enforcement.
This is weaker than the rig standard and is why the result is a probe, not a
comparison. Identical condition across all arms.

**What would falsify what** (5f): B0 high → instrument broken (no claim possible).
B1 ≈ B0 → the automatic floor is negligible; the baton buys ~nothing and the bet
rests entirely on agent-initiated pulls. B2 >> B1 → continuity is real but *pull-
shaped* — it depends on the receiving agent's tool use, corroborating the report's
"rich memory is pull-only" reading. B2 ≈ B0 → the headline bet fails contact for the
only tool that ships it. A-control >> B2 → continuity degrades across harness
boundaries specifically, i.e. the cross-harness claim is the weak link.

## Spend & gates

- Scored arms: ~5 short sessions total (1 capture + 4 quiz) + 1 smoke. Claude Code
  sessions ride the subscription; opencode arms need an Anthropic API key on this box
  — estimate **< $5** at Sonnet-tier pricing, zero if a key is not available (then the
  probe blocks on the harness-B question and says so).
- **No scored arm runs before**: owner protocol review, spend sign-off quoted verbatim
  in `log.md`, B0 calibration passing its gate.
- Amendments: dated, appended, labelled pre-/post-run; protocol text above never
  edited (rule 5).

---

## Results — 2026-08-19 (all arms complete; protocol above unedited)

**Scoreboard** (fails-closed binary key, n=1 per arm — a probe, and it says so):

| Arm | Harness | Memory | Score | Non-UNKNOWN answers |
|---|---|---|---|---|
| smoke (5e) | opencode/haiku | none | 0/10 | 0 — honest UNKNOWNs, driver validated |
| **B0 calibration** | opencode/sonnet-5 | none | **0/10** | 0 — **gate PASS**, instrument discriminates |
| **B1 baton-only** | opencode/sonnet-5 | hooks, out-of-box | **0/10** | 0 |
| **B1b** *(dated pre-B2 amendment)* | opencode/sonnet-5 | hooks + `inject_on_session_start=true` | **0/10** | 0 |
| **B2 baton+pull** | opencode/sonnet-5 | hooks + MCP | **10/10** | 10 — every fact verbatim |
| **A-control** | Claude Code | hooks + MCP | **10/10** | 10 |

**Reading, per the preregistered falsification map:** B1 ≈ B0 and B2 ≫ B1 —
**continuity is real and entirely pull-shaped.** The automatic floor is zero: the
handoff baton injected at session start is the *latest* session's first/last prompts,
and mid-session conversational facts never reach it (ground-truthed in the DB: all 10
facts sit in exactly one handoff each, none in the latest). The ceiling is perfect:
`memory_search` over `observations_fts` — where full prompt text survives — recovered
all 10 facts across the harness boundary, verbatim. And A-control = B2: **the harness
boundary costs nothing on the pull path**. The kind's headline bet survives contact,
but it rests entirely on the receiving agent knowing to ask — corroborating the
ai-memory deep-dive's "the baton is thin by design; rich memory is pull-only" from
source-read to measured.

**Capture-side mechanics behind the floor** (recorded for the report): each headless
`claude -p --continue` turn registered as its own session (6 handoffs, not 1); the
zero-LLM session page stores ~80-char prompt prefixes (facts truncated mid-sentence);
assistant acknowledgments are not captured (double-opt-in `--capture-assistant`).

**Incidental findings:**
1. **MCP schema strictness is a live interop seam**: the Anthropic API rejected
   v1.28.1's `memory_read_page` schema (top-level `oneOf`); the fix
   (`strip_root_combinators`) landed in the 16 commits between release and pin, is
   **default-off**, and needed `AI_MEMORY_STRIP_ROOT_COMBINATORS=true` — a
   presence≠operative echo, observed blocking a real run. B2 ran on the pin-built
   binary (docker rust, read-only clone) with the toggle enabled.
2. The opencode plugin requests the session-start briefing only when a per-project
   `.ai-memory.toml` sets `inject_on_session_start` — out-of-box, injection is not
   even attempted (B1 vs B1b: same score, different mechanism — not-requested vs
   requested-but-factless).
3. The served briefing carries an explicit untrusted-data security boundary — the
   `injection_trust_boundary: true` cell observed live in a real payload.

**Deviations, dated:** B1b added pre-B2 as a labelled amendment (arm plan, not
protocol text). A-control's first invocation failed on `claude -p` flag parsing
(prompt swallowed; the A-driver variant had not been smoke-tested — a 5e gap, caught
by the artifact check not exit status) and was re-run via stdin. Quiz arms each
appended their own (factless) handoffs before later arms; answers exist only in
observations, so contamination surface is nil for the key.

**Cost:** ~5 opencode sonnet-5 sessions + 1 haiku ping + 1 haiku smoke (metered,
well under the $5 ceiling — realistically ~$1); capture + A-control on subscription.

---

## Post-run amendment — 2026-08-19: arm C (LLM-enabled capture), issue #27 arm 1

*(Dated post-run amendment per rule 5; protocol and results above unedited. Sign-off:
"Do 1" — Leandro, 2026-08-19, approving this arm with its ~$1 estimate.)*

**Question**: is the 0/10 automatic floor a design property or a zero-LLM artifact?
The deep-dive notes session-end LLM consolidation enriches pages/handoffs when a
provider is configured (`llm_provider`; config.rs:131-144).

**Design**: fresh data dir (`aimem-data-llm`) so consolidation artifacts are cleanly
attributable; `llm_provider = "anthropic"` in config.toml, key via `ANTHROPIC_API_KEY`
on the daemon process ONLY (the metered experiment key, read from opencode's auth
store; never exported globally — rig credential-precedence hazard); same capture
workspace path (cwd-matching), with `.mcp.json`/`opencode.json` removed first so the
capture harness matches the original capture (no memory tools visible). Re-run the
committed 6-turn capture script; verify consolidation actually ran (daemon log + fact
tokens in wiki/handoff — the mechanical check); then **arm C** = the B1b quiz
configuration exactly (opencode, plugin + `inject_on_session_start` marker, NO MCP).

**Falsification**: C > B1b → the floor is a zero-LLM artifact; conclusion 14 gains a
configuration tier. C = 0 → the floor is a design property (baton shape), and
"pull-shaped" hardens. Scored with the committed key, artifact-read, n=1 (probe).

### Arm C results — 2026-08-19

**C = 0/10, all UNKNOWN** — and the mechanism evidence is stronger than the score.
With `llm_provider=anthropic` live (consolidation on claude-haiku-4-5, verified in the
daemon log), the automatic path still carried nothing:

1. **Session-end consolidation never fired on its own**: the scheduler interval is
   3600s and the default gates (`min_observations=8`, `min_session_duration_secs=120`)
   exclude short headless sessions anyway. (Time-compressed per the amendment: manual
   `auto-improve` runs with `--min-observations 1 --min-session-duration-secs 0`.)
2. **The LLM reviewer saw the facts and REJECTED them, with reasons.** Two runs, 4 and
   8 rejected candidates, zero proposals. Verbatim rejection reason (from
   `auto_improve_runs.rejected_candidates_json`): *"Offline decision acknowledged but
   not made or refined in session; no implementation evidence or policy change
   documented in session itself."* ai-memory's background loop applies an
   evidence bar — acknowledged-but-not-implemented conversational facts are
   deliberately not minted into wiki knowledge.

**Answer to the amendment's question: the floor is a DESIGN PROPERTY at both tiers** —
the zero-LLM path structurally cannot carry mid-session facts (prefix truncation,
latest-handoff-only), and the LLM path deliberately will not (evidence bar).
"Pull-shaped" hardens from a configuration observation into a design reading.

**Correction (dated)**: the main results said each `-p` turn "registered as its own
session (6 handoffs, not 1)". The handoff count is right; the session claim is not —
the daemon's TTL-based mapping folds all six turns into ONE session row (34
observations). Six handoffs, one session. The floor mechanism (latest-handoff-only
injection) is unchanged.

**Also hit and recorded**: appending TOML keys to config.toml lands them in the last
`[section]` (first arm-C round silently ran zero-LLM; caught via the daemon's own
"AI_MEMORY_LLM_PROVIDER unset" line — env vars are the reliable route). Additional
capture round + reviewer runs ≈ $0.30; arm total ≈ $0.60.
