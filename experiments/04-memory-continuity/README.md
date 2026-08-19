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
