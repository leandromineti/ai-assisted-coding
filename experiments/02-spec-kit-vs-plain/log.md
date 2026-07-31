# Experiment 02 — run log

Appended during the runs, never reconstructed afterwards (protocol).

## Run A — plain arm

- `2026-07-31T16:39:59-03:00` — **pre-launch.** Image `tarpeek-rig:exp02` (`c7c6587394fa`, built
  2026-07-30) confirmed present. No prior containers. Host `ANTHROPIC_API_KEY` unset;
  key injected at `docker run` from `PERSONAL_ANTHROPIC_KEY` per rig README § Auth.
- Arm config: model `claude-sonnet-5`, fresh context, task prompt only (extracted
  verbatim from `../rig/tarpeek/task.yaml`, 651 chars, includes pre-run amendment 4).
  No framework. Web tools denied at the harness layer by the image's
  `/root/.claude/settings.json`. Repo NOT mounted — the arm cannot read this repository.
- Attention split: this arm is expected to be fully autonomous (no blocking questions).
  Any blocking event gets its own entry below, verbatim.
- `2026-07-31T16:40:20-03:00` — **agent launched.** Headless: `claude -p "$(cat /root/instruction.txt)" --model claude-sonnet-5 --dangerously-skip-permissions --output-format json`, cwd `/app`.
  Note to verify post-run: `--dangerously-skip-permissions` bypasses permission *prompts*;
  whether it also overrides the image's explicit WebSearch/WebFetch deny is unverified.
  The transcript will be checked for any web tool call before scoring, and a hit recorded
  as a protocol deviation.
- `2026-07-31T16:41:11-03:00` — **launch FAILED, no agent work performed.** `claude` refused to start:
  `--dangerously-skip-permissions cannot be used with root/sudo privileges for security
  reasons`. The image runs as root, so that flag is unusable here. Ran 2s; `/app` untouched;
  no tokens spent. (The wrapper's exit 0 was misleading — the failure was on stderr.)
- `2026-07-31T16:41:11-03:00` — **fix chosen: pre-authorize tools in `settings.json` instead of skipping
  permissions.** Better on the merits than defeating the root guard: in headless mode a tool
  call needing permission is denied rather than prompted, so an explicit `permissions.allow`
  list is the intended mechanism — and unlike the skip flag it *preserves* the image's
  WebSearch/WebFetch deny, which resolves the network-policy doubt logged above rather than
  leaving it to a post-hoc transcript check.
  This is a rig change: it will be applied identically to both arms and recorded in the rig README.
- `2026-07-31T16:42:14-03:00` — **mechanism probed in a throwaway container** (`exp02-probe`, discarded;
  the scored arm runs in a fresh container so this cannot contaminate it). Two findings:
  1. Allow-list works: with `permissions.allow = [Bash, Read, Write, Edit, Glob, Grep]` the
     headless agent executed a Bash command as root and returned its output. No skip flag needed.
  2. `WebFetch`/`WebSearch` are **absent from the tool set entirely** — the harness-layer deny
     holds. But raw egress is open: `curl https://example.com` from the Bash tool returned
     HTTP 200. The rig README's acknowledged v1 gap (harness-level, not egress-level) is hereby
     **confirmed empirically, not merely assumed**: an arm that reaches for `curl` can still
     read the web. Not closed mid-experiment (`--network none` would likely break the
     `pip install` the task instruction requires); instead each arm's transcript is checked
     for outbound curl/wget to non-package hosts, and any hit recorded as a deviation.
  Probe cost: ~$0.10 total, billed to the personal key; excluded from the arms' cost ledger.
- `2026-07-31T16:42:26-03:00` — **Run A relaunched** in fresh container `exp02-run-a`, `/app` empty, allow-list settings in place, instruction at /root/instruction.txt (outside the workspace). Model `claude-sonnet-5`.
- `2026-07-31T16:45:09-03:00` — **Run A complete**, `subtype: success`, no error. Wall-clock 2m13s
  (16:42:35 → 16:44:48 -03:00), 13 turns, api time 109.7s.
  Cost ledger (from the harness result object, model `claude-sonnet-5`):
  output 11,109 · cache write 15,636 · cache read 493,367 · uncached input 26 ·
  **total_cost_usd 0.3741**.
  Attention split: **fully autonomous, zero blocking events** — no question was asked of the
  orchestrator, so attention-required time is 0s for this arm. (This is the baseline the
  spec-kit arm's clarify loop gets priced against.)
- `2026-07-31T16:45:47-03:00` — artifacts copied to `artifacts/run-a/` **before** scoring (generated caches/egg-info pruned; 146 LOC product excl. tests). `tarpeek` resolves from `/usr/local/bin`, runs from any cwd → amendment 4 satisfied. Transcript + harness result in `artifacts/run-a-transcript/`. Hidden verifier now copied in and run.
- **Run A score: 8/8, all checks pass.** Machine-checked against the preregistered
  `expected.json` (the session fixture's drift assertion also passed, so the rebuilt archives
  match the protocol's ground truth).

  | Check | Result | Note |
  |---|---|---|
  | normal listing | PASS | |
  | sort by size desc | PASS | |
  | `--min-size` filter | PASS | |
  | `--json` output | PASS | |
  | T1/T2 encoding + epoch/2106 mtime | PASS | lists without crash |
  | T3 distinct non-zero exit codes | PASS | separate codes for not-a-tar vs empty |
  | T4 timezone | PASS | **invariant, not merely documented** — pins `tz=timezone.utc` in `core.py:54` |
  | T5 never writes | PASS | header-only reads, no `extract*` |

- **Methodological problem this creates — logged now, before Run B, so it can't be rationalised
  after the fact.** The plain baseline scored a perfect 8/8. The trap instrument therefore has
  **no headroom**: spec-kit cannot score better than plain on traps, only equal or worse. That
  breaks one of the protocol's two preregistered damage conditions. "If spec-kit's code *beats*
  plain on traps materially → conclusion 6 is damaged" is now **unfalsifiable in that direction**
  on this task. P2 (spec-kit equal-or-worse) can still be confirmed, but only trivially — an
  8/8 tie tells us nothing about mechanism, because a ceiling result is consistent with both
  "intent capture doesn't help code quality" and "intent capture helps, but the instrument
  can't see it."

  This is an instrument-design failure, not a spec-kit finding, and it was foreseeable: the
  traps were drawn from exp-01's *families*, which a competent Sonnet 5 run on a smaller task
  clears without help. Options (a decision for the next session, not something to quietly
  paper over): score on a harder trap set, add a graded rubric where partial credit is
  possible, keep the 8/8 tie and report P2 as untested-by-ceiling, or accept the task as
  measuring only the *requirements* rubric (P1) where headroom demonstrably remains.
  Run B is NOT started; the P1 requirements comparison is unaffected by this and remains live.
- **Pricing in force at Run A (recorded per methodology 5c, since it changes soon):** Sonnet 5
  **introductory** rates, $2/MTok input and $10/MTok output, which run through **2026-08-31**.
  Standard rates ($3/$15) resume after that, so a Run B executed in September is NOT
  cost-comparable to this arm at face value — compare tokens, and reprice both arms at whichever
  rate is being quoted. The `total_cost_usd 0.3741` above is an intro-rate figure.
- **Model verification (checked against the artifacts, not against the launch command).** All
  **25** assistant turns in the transcript are `claude-sonnet-5`; it produced all 11,109 output
  tokens, all 493,367 cache reads, and $0.3734 of the $0.3741.
  **Caveat on amendment 1's "sole model" wording:** the harness's `modelUsage` also records
  `claude-haiku-4-5` at 18 output / 684 input tokens, $0.00077 — Claude Code's internal
  auxiliary call (session-title-class work). It contributed **zero assistant turns and no task
  work**. Immaterial to the comparison (0.2% of cost, 0.16% of output tokens) and it will recur
  identically in Run B, but recorded because "sole model" is not literally accurate: the arm's
  *task* work was exclusively Sonnet 5, while the harness around it was not.
