# The rig — standardized task + sandbox for layer-4 framework comparisons

`created: 2026-07-28` · status: **network condition enforced + probed 2026-07-31; image built 2026-07-30 (Docker 29.1.3, digests in the
pins table); verifier proven fails-closed on the host 2026-07-28 (no-binary → 8/8 error;
do-nothing stub → 8/8 fail, after a hardening pass — the first stub run exposed vacuous
T4/T5 passes, fixed same day) and re-proven inside the container 2026-07-30**

A reusable, pinned execution environment for comparing workflow frameworks fairly. First
consumer: [`../02-spec-kit-vs-plain/`](../02-spec-kit-vs-plain/README.md) (see its
pre-run amendment). Design rationale researched and decided 2026-07-28.

## What it is

Tasks are packaged in the **Terminal-Bench task format** (verified against
`harbor-framework/terminal-bench` samples, 2026-07-28 — the org moved from
`laude-institute`; task = `task.yaml` instruction + `Dockerfile` + hidden
`tests/` + `run-tests.sh`). The format was chosen because it is community-standard and
because its conventions match this repo's needs exactly:

- **Short natural-language instruction** — ambiguity is preserved, which is what
  workflow frameworks claim to handle (a fully-specified benchmark task would neutralize
  intent capture).
- **Pinned Docker environment** — the sandbox. Fixes exp-01's scars structurally: no
  ambient-cwd leakage into the host (the container *is* the blast radius), fixed
  `TZ`/locale, reproducible toolchain.
- **Hidden verifier over final container state** — complete ground truth the arms never
  see, measured (not assumed) per methodology rule 5a.
- **Canary GUID lines** — T-Bench's convention for keeping benchmark data out of
  training corpora; adopted in our task files since this repo is public.

## Pins (recorded here; placeholders resolved at first build)

| What | Pin |
|---|---|
| Base image | `ghcr.io/laude-institute/t-bench/python-3-13:20250620` (T-Bench's own base) — digest recorded at first build (2026-07-30): `sha256:236734f0cafcce942ca09316d57236c2273a2b5411e116454a22cf6d718d95f5` |
| Harness | Claude Code CLI `2.1.220`, installed in-image via npm, run headless (auth: see [§ Auth](#auth-api-key-passed-in-at-run-time)) |
| Model | `claude-sonnet-5` — sole model for all *task* work, all arms, all frameworks. Measured caveat (exp-02 Run A): the harness itself also makes a small internal `claude-haiku-4-5` call (~18 output tokens, $0.0008, zero assistant turns). Immaterial and identical across arms, but "sole model" is not literally true — attribute usage per model when reporting (methodology 5c) |
| Framework versions | pinned per experiment in its preregistration (exp-02: spec-kit @ `655a3cb`) |
| Rig image digest | local image ID `sha256:c7c6587394fabae0924cf2f0bd9a4afeb74527a2223184f7dd46da1066c17155` (`tarpeek-rig:exp02`, built 2026-07-30; never pushed to a registry, so this is the config digest, not a repo digest). Build note: the base image's distro Node is 18, below Claude Code 2.1.220's floor — the Dockerfile installs NodeSource Node 22.x (22.23.2 at first build) |

## Auth: API key, passed in at run time

The in-container harness runs headless, so the interactive login path is unavailable —
there is no browser and no host home directory. Arms authenticate with an API key
supplied at `docker run`:

```sh
source ~/.secrets/personal-anthropic.env   # exports PERSONAL_ANTHROPIC_KEY; 600, outside the repo
docker run --rm -e ANTHROPIC_API_KEY="$PERSONAL_ANTHROPIC_KEY" tarpeek-rig:exp02 …
```

Two deliberate choices:

- **The host variable is `PERSONAL_ANTHROPIC_KEY`, not `ANTHROPIC_API_KEY`.** A set
  `ANTHROPIC_API_KEY` outranks every other credential source and conflicts with an
  interactive CLI login on the same machine, so the canonical name exists only inside
  the container. The name also omits the substring `ANTHROPIC_API_KEY` so that a
  `grep ANTHROPIC_API_KEY` over the host environment still correctly reports "unset" —
  no false positive for a credential probe.
- **The mapping is the audit trail.** The `-e` line is where a key crosses into the
  sandbox, visibly and on purpose, rather than being inherited ambiently from the
  shell. Which key is used determines who is billed for a run — worth being explicit
  about on any machine that holds more than one credential.

The key value is never committed, and never referenced in this repo by anything other
than the variable name.

## Network condition: declared, enforced at egress, probed

Per methodology 8a, an experiment states which of three conditions it ran under, enforces it
where traffic actually leaves the sandbox, and records a probe. **v1 of this rig did not do
that** — it denied the web *tools* in `settings.json` and the README claimed arms therefore
had model-API-only access. Measured 2026-07-31: `curl https://example.com` from the Bash
tool returned **HTTP 200**. Tool-layer denial is not a network policy.

| Condition | Meaning | Enforcement |
|---|---|---|
| `open` | arms may reach the internet | nothing to enforce; declare it |
| **`package-hosts-only`** | package registries reachable, general web not | internal Docker network + allowlist proxy (below) |
| `closed` | no egress at all | `--network none`; **breaks `pip install`**, so unusable for tasks that require installability |

**`package-hosts-only` is the rig default from 2026-07-31.** Setup — the proxy runs from the
*same pinned image*, so the condition adds no new image dependency:

```sh
docker network create --internal exp-closed-int          # no route off-host
docker run -d --name exp-proxy tarpeek-rig:exp02 sleep infinity   # on the default bridge
docker network connect exp-closed-int exp-proxy          # ...and on the internal net
docker cp allowlist_proxy.py exp-proxy:/proxy.py
docker exec -d exp-proxy bash -lc 'python3 /proxy.py > /proxy.log 2>&1'

docker run -d --name <arm> --network exp-closed-int \
  -e HTTP_PROXY=http://exp-proxy:8888 -e HTTPS_PROXY=http://exp-proxy:8888 \
  -e http_proxy=http://exp-proxy:8888 -e https_proxy=http://exp-proxy:8888 \
  -e ANTHROPIC_API_KEY="$PERSONAL_ANTHROPIC_KEY" -w /app tarpeek-rig:exp02 sleep infinity
```

Allowlist ([`allowlist_proxy.py`](allowlist_proxy.py)): `pypi.org`, `files.pythonhosted.org`,
`pypi.python.org`. Denials are logged, so `/proxy.log` **is** the probe record — copy it out
with the arm's artifacts.

The arm sits on an `--internal` network, so egress is blocked at the network layer rather than
by an environment variable: an arm that unsets `HTTPS_PROXY` gets no route, not a bypass. The
model API is reached through the proxy the same way; add the API host to the allowlist if a
future arm needs anything else, and record the change.

**Probe results (2026-07-31, this configuration):**

| Probe | Expected | Observed |
|---|---|---|
| raw egress with proxy env unset | fail | curl exit 6, host unresolvable |
| general web via proxy | blocked | `DENY CONNECT example.com:443` |
| PyPI via proxy | succeed | `pytest-8.4.1` wheel downloaded |
| `pip install .` of a src-layout project with build isolation | succeed | exit 0, console script on PATH, runs |

The last row is the load-bearing one: it is why `package-hosts-only` and not `closed` is the
default — the task instruction requires the tool be installed and runnable from any directory,
and full egress denial breaks the build-isolation download that requires.

## Harness decision: Claude Code, not an open-source harness

Recorded reasoning (2026-07-28):

1. Claude Code is the only harness where **both** current subjects are first-class:
   gsd-core officially targets Claude Code/Codex/Gemini CLI/Cursor/Windsurf/Copilot (no
   opencode; a community port exists but is unofficial), and spec-kit targets 40+
   including Claude Code. An open-source harness would introduce a framework-maturity
   confound larger than the closed-source cost.
2. Terminal-Bench itself ships Claude Code as a supported agent, so this is a
   community-benchmarked configuration.
3. Reproducibility is carried by **pins + committed transcripts** (CLI version, image
   digest, model ID, framework commits, full session transcripts in each experiment's
   `artifacts/`), not by harness source access.

**Recorded costs of this choice:** context assembly inside Claude Code is unobservable,
and vendor updates can shift behavior between experiments — mitigated by pinning the CLI
version per experiment and never comparing across CLI versions. **Fallback:** opencode
(spec-kit supports it) if a future subject lacks Claude Code support.

## Driver protocol

The T-Bench task *format* is adopted; the stock autonomous runner (`tb run`) is not —
spec-kit's clarify loop requires interaction, and pricing that interaction
(autonomous vs. attention-required time) is one of the experiment's instruments. The
orchestrator drives each arm as headless Claude Code sessions inside the container,
logging every blocking question and answer verbatim to the experiment's `log.md`.
Running a plain arm under stock `tb run` later remains possible for loose comparison
against public T-Bench baselines.

Network policy: see [§ Network condition](#network-condition-declared-enforced-at-egress-probed).
The rationale for constraining it is unchanged — with no general web access, a framework's
"research" phase can only do *local measurement*, the mechanism exp-01 found load-bearing, so
no arm can substitute web lookup for empirical grounding. What changed on 2026-07-31 is that
the constraint is now **enforced and probed** rather than asserted: the v1 tool-layer deny left
`curl` working. `open` remains a legitimate declared condition for measuring the frameworks as
users actually run them; it is simply never the silent default.

**Tool permissions.** Arms run with an explicit `permissions.allow` list written to
`/root/.claude/settings.json` at run time:

```json
{"permissions": {"allow": ["Bash","Read","Write","Edit","Glob","Grep"], "deny": ["WebSearch","WebFetch"]}}
```

Not `--dangerously-skip-permissions`: the CLI **refuses that flag outright when running as
root**, which the image does (`--dangerously-skip-permissions cannot be used with root/sudo
privileges for security reasons`), and it exits 0 while doing nothing — see methodology 5e.
The allow-list is the intended headless mechanism and, unlike the skip flag, verifiably leaves
the web-tool deny intact (probed 2026-07-31: `WebFetch` is absent from the agent's tool set
entirely). Any change to this list applies identically to every arm on the task.

## Reuse rules

- **One plain baseline per task, reused by every framework tested on that task.** The
  comparable unit across frameworks is the *delta over plain*, never raw scores across
  different tasks.
- A task is a **consumable instrument**: once its traps have been exercised and
  discussed in this repo, new frameworks get scored on it only with the contamination
  declared, and genuinely fresh comparisons get a fresh task in the same trap-class
  family (encoding, time, exit codes, ambient config, safety).
- The verifier must be proven **fails-closed** before any arm runs: it must fail against
  an empty container and against a deliberately broken stub. A verifier that passes an
  empty environment is a scorer bug (exp-01, rule 5a).
- No `solution.sh` oracle is written before the arms run — T-Bench convention deviation,
  deliberate: the orchestrator implementing the task would deepen scorer contamination.
  Verifier satisfiability is instead proven by the first passing arm (or an oracle
  written *after* both arms, if neither passes).

## Tasks

| Task | Status | Used by |
|---|---|---|
| [`tarpeek/`](tarpeek/) | image built (`tarpeek-rig:exp02`), verifier re-proven fails-closed in-container 2026-07-30 | exp-02 (spec-kit vs plain), exp-03 planned (minimal harness) |
