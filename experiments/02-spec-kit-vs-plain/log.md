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

### Post-Run-A protocol changes (2026-07-31)

- **Network condition now enforced, not asserted.** The v1 tool-layer deny was measured
  half-effective (web tools absent, `curl` returning HTTP 200). The rig now runs
  `package-hosts-only`: arms on an `--internal` Docker network with no route off-host, PyPI
  reachable only via an allowlist CONNECT proxy, denials logged. Four probes recorded in the
  rig README, including `pip install .` of a src-layout project succeeding end-to-end — which
  is why the condition is `package-hosts-only` rather than `closed` (`--network none` breaks
  the build-isolation download the task's installability requirement needs).
- **Run A is reclassified as a calibration run, not the scored baseline.** Two reasons, and the
  second is the honest one:
  1. It ran under the *old* nominal condition. Its transcript shows zero network calls beyond
     the model API, so its **realized** condition was equivalent to no-web — Run A is not
     contaminated.
  2. But the *affordances* differed: Run A could have reached the web and chose not to; a Run B
     under enforcement cannot. If a framework's research phase would have used lookup, denying
     it changes that arm's behavior in a way Run A was never subject to. Comparing them would
     violate methodology 8a's "held identical across arms" on a technicality that happens to
     matter exactly where the experiment is trying to measure.
  Methodology 5d says the baseline arm *is* the instrument calibration, and that is precisely
  what Run A delivered: it revealed the trap ceiling, proved the driver, and priced the arm at
  $0.374. Re-running it under the final instrument + enforced condition costs ~$0.37 and 2
  minutes — cheaper than defending a mismatched pair.
- **Unchanged and still blocking:** the trap-ceiling decision above. Do not run Run B until the
  instrument question is settled; a re-run of Run A should happen under the *same* decision, so
  both arms share one instrument and one network condition.

## 2026-08-17 — amendment-3 instrument work: densification + three-point proof

Executed per amendment 3 (committed e932206 before any of the below). All scoring runs
are instrument work against existing artifacts in local venvs — no experiment arm ran.

**Instrument v2 built:** 21 binary machine checks (was 8 monolithic): F1–F4 functional ·
T1a–c · T2a–c · T3a–d · T4a–c · T5a–d. Original 8 preserved in substance. New fixtures,
all within preregistered families: `traps2.tar` (PAX long-name 169 chars — T1; hardlink +
char-device members — T5), `truncated.tar` (valid header, cut body — T3).
`expected.json` regenerated from measurement (13 members + truncated identity), mirrors
synced. New apparatus: hardened reference implementation at `../rig/tarpeek/reference/`
(never a contestant; documents exit codes 0/2/3/4/5; UTC-always output).

**Three-point proof, under the declared condition (TZ=UTC, LANG=LC_ALL=C.UTF-8):**

| Leg | Requirement | Result |
|---|---|---|
| Fails-closed | do-nothing stub fails every check | **21/21 fail** ✓ |
| Fairness | reference passes every check | **21/21 pass** ✓ |
| Headroom | Run A artifact fails ≥ 3 | **1/21 fail** ✗ (T4c only) |

**Incidental finding (recorded, not exploited):** under the scoring host's default
locale (strict UTF-8 stdio), Run A's artifact crashes on the T1 member — 5/20 checks
fail (T1a, T1b, T2a, T2b, T5a all victims of one `UnicodeEncodeError` on the surrogate).
Under the rig's pinned `C.UTF-8` (surrogateescape stdio) it passes cleanly. The
declared condition is C.UTF-8, so the passing result is the honest one; switching the
condition to manufacture headroom after seeing which condition fails the artifact would
be post-hoc instrument selection. The legitimate residue is `T4c` (ambient-config
family): `PYTHONIOENCODING=utf-8:strict` reproduces the fragility portably; reference
passes it, stub fails it, Run A fails it. Provenance disclosed in the check's docstring.

**Verdict per amendment 3 item 5: the EvalPlus step is exhausted.** Headroom 1 < 3.
The informative content of the negative result: Run A's 8/8 was *not* a
shallow-verifier artifact — under 13 additional, strictly harder checks the calibration
artifact still clears the five families on their own terms (its one failure is
environmental fragility, not domain logic). The trap families are genuinely consumed at
this task size, exactly what the escalation exists for.

**Escalation gate (preregistered, not yet begun):** Aider move — candidate pool of NEW
trap families, screened by 5 fresh unaided baseline runs in the rig under
`package-hosts-only`, keep-if-failed-in-≥2-of-5, fairness-screened against the
reference. Costs ~5 × Run A ≈ $1.9 in API spend at intro rates plus rig time.
**Awaiting owner sign-off before any screening run.** Until then the instrument stands
as: 21 checks, fails-closed and fair, headroom insufficient for P2; P1 (requirements
rubric) unaffected throughout.

## 2026-08-17 — escalation (the Aider move): owner sign-off + candidate pool

- **Owner sign-off received** ("Lets do the aider move") — the ~$1.9 screening spend is
  authorized. Execution follows amendment 3 item 5 exactly: candidate pool of NEW
  families → 5 fresh unaided baseline runs under `package-hosts-only` → keep candidates
  failed in ≥ 2 of 5 → fairness screen against the reference. Screening runs are
  instrument calibration, never scored arms.
- **Candidate pool authored and committed BEFORE any screening run** so the pool cannot
  be shaped by what the runs produce. 7 candidate checks in 4 new families, in
  `../rig/tarpeek/tests/candidate_checks.py` (mirrored in `fixtures/`), deliberately
  outside the five preregistered families:

  | Family | Candidates | Sharp edge targeted |
  |---|---|---|
  | N1 hostile paths | n1a directory · n1b missing path · n1c dangling symlink | path-level `OSError`s escape a `tarfile.ReadError`-only handler as tracebacks |
  | N2 stream discipline | n2a `--json` error keeps stdout clean | error text printed into the machine-readable stream |
  | N3 duplicate members | n3a both listed (human) · n3b both in JSON — or dedup documented | name-keyed dict silently drops one of two same-named members |
  | N4 filter semantics | n4a filter-to-empty is success (or distinct documented code) | empty-result conflated with empty-archive error; `max()` over empty rows raises |

  One new fixture, `dup.tar` (same name twice: 100 B then 200 B a minute later),
  built by `build_candidate_fixtures.py`, ground truth measured into
  `candidate_expected.json` (rule 5a). Reference hardened for N1 (broad `OSError` →
  exit 5, dated comment in source) — apparatus hardening before screening, recorded.
- **Candidate pre-screen (venv, TZ=UTC, LANG=LC_ALL=C.UTF-8):**

  | Leg | Result |
  |---|---|
  | Fails-closed: stub vs candidates | **7/7 fail** ✓ |
  | Fairness: reference vs candidates | **7/7 pass** ✓ |
  | Regression: reference vs accepted 21 | **21/21 pass** ✓ |
  | Calibration preview: Run A artifact vs candidates | **7/7 pass** — Run A fails none |

- **The preview is recorded, not acted on.** Run A passing the whole pool predicts a
  possible null screening result, and that is fine: the keep criterion is failure in
  ≥ 2 of 5 *fresh* runs — the Aider method selects on baseline variance, which one
  careful calibration artifact cannot measure. The alternative (inflating the pool
  with checks no careful implementation passes) is the exact unfairness
  SWE-bench-Verified documented; not doing that. If screening keeps nothing, the
  verdict is that the trap approach is consumed at this task size and the instrument
  question moves to task scale — a distinct, honest finding.
- Screening runs will additionally be scored against the accepted 21 (free variance
  data on T1c/T3d/T4c across samples); that scoring is calibration bookkeeping, not
  part of the keep rule.

### Screening pre-launch (2026-08-17)

- The server hosting the rig was **rebuilt 2026-08-06** (post-Run-A): the pinned image
  and the key file were gone. Restored and re-verified rather than assumed:
  - Image `tarpeek-rig:exp02` rebuilt from the committed Dockerfile. Base digest
    re-verified **identical to the 2026-07-30 pin** (`sha256:236734f0…`); Node again
    22.23.2 (no drift); Claude Code 2.1.220 (pinned).
  - `package-hosts-only` re-created and **re-probed**: raw egress without proxy → no
    route; `example.com` via proxy → `DENY` logged; PyPI via proxy → 200;
    `api.anthropic.com` via proxy → reached (405 on a bare GET, TLS established).
  - **Rig change, recorded:** `api.anthropic.com` added to the proxy allowlist — the
    screening runs are the first *agent* runs under the enforced condition (the
    2026-07-31 probes were curl/pip only, so the in-container harness never needed
    egress before). Telemetry hosts deliberately not added; their denials in
    `/proxy.log` are probe records.
  - Driver smoke-tested end to end through the proxy per methodology 5e — and it
    caught a real failure: the harness returned `subtype: success` while the result
    text read "Not logged in" (exit-status success, nothing done — the exact 5e
    failure shape). Cause: `~/.secrets/personal-anthropic.env` did not survive the
    server rebuild, so no key reached the container. **Screening runs blocked on
    restoring the key file**; no scored spend occurred (the smoke prompt cost $0).
- `2026-08-17T11:38Z` — key file restored by owner; smoke config verified; screening
  begins. Per-run protocol: fresh container `exp02-screen-N` on the internal network,
  allow-list settings, instruction verbatim (651 chars) at `/root/instruction.txt`,
  `claude -p … --model claude-sonnet-5 --output-format json`; artifacts + transcript +
  per-run proxy-log slice to `artifacts/screening-N/`; scored immediately in a fresh
  venv under TZ=UTC / C.UTF-8 against the accepted 21 + the 7 candidates.

### Screening runs (2026-08-17, live)

- `11:42–11:44Z` — **run 1** complete: `subtype success`, 16 turns, 2m25s api,
  **$0.4669**. Proxy: only PyPI allows + Datadog telemetry denials — no web reads.
  Score: **accepted 19/21** (fails `T3c` truncated-archive, `T4c` strict-stdio) ·
  **candidates 7/7 pass**. First variance vs Run A appears on the accepted set, not
  the candidate pool.
- `11:46–11:48Z` — **run 2** complete: success, 20 turns, 2m42s, **$0.5115**. Proxy
  clean (PyPI + telemetry denials only). Score: **accepted 20/21** (fails `T4c` only —
  same profile as Run A) · **candidates 7/7 pass**.
- `11:49–11:51Z` — **run 3** complete: success, 12 turns, 1m50s, **$0.3120**. Proxy
  clean. Score: **accepted 20/21** (fails `T4c` only) · **candidates 7/7 pass**.
- `11:51–11:53Z` — **run 4** complete: success, 13 turns, 2m02s, **$0.3500**. Proxy
  clean. Score: **accepted 18/21** (fails `T3a` distinct exit codes — an *original
  amendment-1 check* — plus `T3c`, `T4c`) · **candidates 7/7 pass**.
- `11:54–11:56Z` — **run 5** complete: success, 15 turns, 2m14s, **$0.3993**. Proxy
  clean. Score: **accepted 18/21** (fails `T3a`, `T3c`, `T4c`) · **candidates 7/7
  pass**.

### Screening verdict (2026-08-17)

**Candidate keep rule (preregistered, amendment 3 item 5): no candidate reached ≥ 2
failures in 5 runs — no candidate failed even once. All 7 candidates are DISCARDED.**
The files stay in the repo as the record of the screen, marked as discarded; nothing
enters `test_outputs.py`. The instrument remains the accepted 21 checks.

Failure mechanics verified in the artifacts (not inferred): runs 4 and 5 give
not-a-tar and empty-archive the same exit code 1 (T3a); runs 1, 4, 5 let an unhandled
`Traceback` escape on the truncated archive (T3c); T4c's strict-stdio crash reproduced
in all five.

**What the screen actually bought — the baseline distribution (n=5 + Run A):**

| Check | Baseline failures | Note |
|---|---|---|
| T3a distinct exit codes | 2/5 | original amendment-1 check |
| T3c truncated archive | 3/5 | amendment-3 densification |
| T4c strict stdio | 5/5 (and Run A) | amendment-3, provenance disclosed |
| all 18 others | 0/5 | consumed at this task size |
| per-run accepted score | 19 · 20 · 20 · 18 · 18 (mean 19.0/21) | Run A scored 20/21 |

**Dated correction to the 2026-08-17 morning verdict.** "The trap families are
genuinely consumed at this task size" was measured against a single calibration
point and is now shown to be **partly wrong**: encoding (T1), time (T2), and safety
(T5) are consumed (0/5 failures anywhere), but the exit-code and ambient-config
families retain real discrimination — Run A was simply a strong draw. The
single-point headroom estimate (1/21) understated true headroom (mean 2.0/21,
range 1–3). The escalation's value was not the new families (clean null: unaided
baselines handle path errors, stream discipline, duplicates, and filter edges
without being asked) — it was replacing a point estimate with a distribution,
which is what instrument calibration means (methodology 5d).

**Instrument settled.** Fails-closed ✓ (stub 21/21 + candidates 7/7 fail) · fair ✓
(reference passes everything) · discriminating ✓ (three items with baseline failure
rates 40–100%, per-run scores spanning 18–20). Any future Run A′ vs Run B
comparison must be read against this measured noise band: a framework arm at 21/21
would exceed every observed baseline; an arm at 19–20 is within baseline variance.
n=5 is still a small sample; the band is a calibration reference, not a
significance test.

**Cost ledger:** five screening runs $0.4669 + $0.5115 + $0.3120 + $0.3500 +
$0.3993 = **$2.0397** (intro rates), vs the ~$1.9 estimate — 7% over, from run 2's
20-turn session. All runs `subtype: success`, fully autonomous, zero blocking
questions, proxy logs clean (PyPI + denied telemetry only; no web reads).

## 2026-08-17 — model-tier calibration (known-groups validity), preregistered

Owner-approved follow-up, declared **before any run**. Question: does the settled
21-check instrument separate model tiers? If it measures real capability, a weaker
tier should sit measurably below the Sonnet baseline distribution
(19 · 20 · 20 · 18 · 18, mean 19.0/21). **Calibration, not an exp-02 arm** — the
A/B remains Sonnet-only per amendment 1; these runs never enter it.

- **Config:** `claude-haiku-4-5`, n=5 sequential fresh containers, everything else
  identical to the screening runs (image/CLI 2.1.220, instruction verbatim,
  allow-list settings, `package-hosts-only` re-created and re-probed). Artifacts to
  `artifacts/haiku-cal-{1..5}/`; each run scored immediately (venv, TZ=UTC,
  C.UTF-8) against the accepted 21 + the 7 discarded candidates.
- **Predictions, fixed now:**
  1. Haiku mean accepted score **< 19.0/21**; failure rates on T3a/T3c/T4c ≥
     Sonnet's.
  2. Non-trivial chance (~1 in 5) that at least one run fails completion outright
     (no installable `tarpeek` on PATH); Sonnet completed 5/5.
  3. Haiku fails at least one of the 7 discarded candidates somewhere (Sonnet:
     0 failures in 25 check-runs). Candidates stay discarded for exp-02 regardless
     — any hit is recorded as tier-discrimination evidence, not a rule change.
- **Completion-failure accounting:** completion rate reported separately; per-check
  comparison over completed runs only; the separation verdict must cite both (a
  tier that cannot finish is separated *more*, not less).
- **Verdict rule:** known-groups validity **supported** if Haiku's mean is below
  the Sonnet minimum (18) or every discriminating item's failure rate is ≥
  Sonnet's with at least one strictly higher; **unsupported** if the distributions
  fully overlap. n=5 vs n=5 is calibration, not a significance test.
- **Cost estimate:** Haiku $1/$5 per MTok vs Sonnet's intro $2/$10 → ~$0.75–1.25
  total at the Sonnet token profile; rises if Haiku needs more turns. Logged per
  run.

### Haiku calibration runs (2026-08-17, live)

Network re-created, all 4 probes correct (no-route / DENY / PyPI 200 / API
reached), preregistration committed `dfd4300` before launch.

- `15:00–15:02Z` — **run 1** complete: success, 23 turns, 1m29s, **$0.1258**.
  Proxy clean. Score: **accepted 17/21** (fails `T3a`, `T4a`, `T4b`, `T4c` — the
  whole ambient-config family) · **candidates 6/7** — fails `N4a` filter-to-empty,
  **the first candidate failure in any run** (Sonnet: 0 in 25 check-runs).
  Prediction 3 confirmed on the first sample.
- `15:02–15:04Z` — **run 2** complete: success, 32 turns, 2m05s, **$0.1726**.
  Proxy clean. Score: **accepted 17/21** (fails `T3a`, `T4a`, `T4b`, `T4c` — same
  profile as run 1) · **candidates 6/7** — fails `N1a` directory-path traceback
  (a *different* candidate than run 1's `N4a`).
- `15:05–15:07Z` — **run 3** complete: success, 34 turns, 1m58s, **$0.2002**.
  Proxy clean. Score: **accepted 17/21** (fails `T3a`, `T4a`, `T4b`, `T4c` —
  identical profile third time) · **candidates 6/7** — fails `N4a`.
- `15:08–15:09Z` — **run 4** complete as a session (success, 28 turns, 1m26s,
  **$0.1483**) but the artifact is **broken as a package: 1/21 accepted, 0/7
  candidates**. Mechanism verified in the artifact, not inferred: `cli.py` imports
  `tabulate`, the README documents it as a requirement, but `pyproject.toml`
  declares no dependencies — the agent had run `pip install -e . tabulate` by hand
  in-container, so it worked *there* and dies with `ModuleNotFoundError` on any
  fresh install. Scored per the preregistered procedure (fresh venv, identical for
  every run, Sonnet and Haiku); counted as a **completion failure** in the
  distribution-vs-completion split — the instruction's "install it so it runs from
  any directory" is exactly what an undeclared runtime dep breaks. Nuance recorded:
  the *final container state* would have passed more checks; the venv procedure is
  the declared one and is what makes runs comparable.
- `15:10–15:12Z` — **run 5** complete: success, 16 turns, 1m11s, **$0.1026**.
  Proxy clean. Score: **accepted 17/21** (fails `T3a`, `T4a`, `T4b`, `T4c`) ·
  **candidates 7/7 pass**.

### Model-tier calibration verdict (2026-08-17)

**Known-groups validity: SUPPORTED**, via the first branch of the preregistered
rule — Haiku's completed-run mean (17.0/21) sits below the Sonnet *minimum* (18).
Complete separation: every completed Haiku run scored 17; every Sonnet run scored
18–20. Plus one Haiku completion failure (run 4) against Sonnet's 5/5.

| | Sonnet 5 (n=5) | Haiku 4.5 (n=5) |
|---|---|---|
| completion (installable, runs fresh) | 5/5 | **4/5** (run 4: undeclared `tabulate` dep) |
| accepted score, completed runs | 19 · 20 · 20 · 18 · 18 (mean 19.0) | 17 · 17 · 17 · 17 (mean 17.0) |
| T3a distinct exit codes | 2/5 fail | **4/4 fail** |
| T3c truncated archive | 3/5 fail | **0/4 fail** ← reversal |
| T4a TZ-invariant-or-documented | 0/5 fail | **4/4 fail** |
| T4b `--json` TZ-stable | 0/5 fail | **4/4 fail** |
| T4c strict stdio | 5/5 fail | 4/4 fail |
| candidate failures (completed runs) | 0 in 25 check-runs | `N4a` 2/4 · `N1a` 1/4 |
| mean cost / run | $0.408 (intro $2/$10) | $0.150 ($1/$5) |
| wall-clock range | 1m50s–2m42s | 1m11s–2m05s |

**Predictions vs outcomes:** (1) mean < 19.0 ✓, but the per-item clause is
**half-wrong** — T3c *reversed* (Haiku 0/4 vs Sonnet 3/5), recorded as stated.
(2) ✓ exactly one completion failure. (3) ✓ candidates discriminate tiers:
N4a and N1a caught Haiku in completed runs; Sonnet never failed any.

**The mechanism behind the reversal is the most instructive finding.** Haiku's
implementations wrap everything in coarse blanket error handling (`rc=1`, one
message shape): no traceback ever escapes (passes T3c) but no failure is
distinguishable (fails T3a, 4/4). Sonnet differentiates exit codes (passes T3a
3/5) but 3/5 runs forgot the truncated case and let a traceback escape. Trap
items are not monotone in capability — some measure *failure style*, not skill.
The crispest tier separator is the **ambient-config family**: Haiku renders
local-time output, undocumented, in every completed run (T4a/T4b 4/4); Sonnet
never did (0/5). The whole-family failure pattern, not any single item, is what
separates tiers.

**Scope note:** candidates stay discarded for exp-02 (the A/B is Sonnet-only and
they don't discriminate Sonnet baselines); their tier-discrimination is recorded
as a finding about the *pool*, not a rule change. **Cost ledger:** $0.1258 +
$0.1726 + $0.2002 + $0.1483 + $0.1026 = **$0.7495** total, mean $0.150/run —
within the preregistered $0.75–1.25 estimate. All runs autonomous, proxy logs
clean.

## 2026-08-17 — pricing condition change (affects planning, not any recorded ledger)

Verified on the vendor pricing page (retrieved 2026-08-17): **Sonnet 5's $2/$10 is
now the standard price — the scheduled 2026-09-01 increase to $3/$15 was cancelled.**
Every "intro rate" ledger above was recorded at what is now simply list price, so no
September renormalization will ever be needed, and this log's standing warning that
"a Run B executed in September is NOT cost-comparable to this arm at face value" is
retired as of this date (it was true when written). The Run A′ + Run B decision loses
its August deadline pressure.
