---
name: elephant-goldfish-model
category: 4
maker: Google
url: https://github.com/google/elephant-goldfish-model
license: Apache-2.0
access: open-source
stack: [Markdown, Python]
version: v0.1.1
commit: dea7761
first_commit: 2026-10-21
stars: 17092
stars_at: 2026-11-10
read_at: 2026-11-10   # candidate 2026-11-10 → deep-dive the same day, the bmad-method/superpowers same-sitting precedent; pin = annotated tag v0.1.1 (peeled dea7761de06c, committed 2026-11-06), first-parent of main; HEAD 8f16812 is 25 commits ahead (drift section)
depth: deep-dive   # 2026-11-10: all four category-4 functions traced in source at the pin by three parallel readers (F1+F2 brainstorm/draft/resolve; F3+F4 review/review-loop/drift-report/bootstrap + 10 personas + 5 standards; delivery substrate: every manifest, adapter and executable), load-bearing claims spot-verified in the main session; RUN partial: the published-artifact probe ran (both v0.1.1 release ZIPs checksum-verified and diffed byte-for-byte against the pin); executing the packaging scripts and unit tests was blocked by this session's permission policy and is not load-bearing (no shipped code runs in a user's session); a live review run spends model quota and is parked for owner sign-off
harness_targets: "two measures @ v0.1.1, stated because they differ: 7 hosts in docs/harnesses.md's manifest table (Antigravity, Claude Code, Claude Cowork, Codex, ChatGPT, omp, Muse), 3 of which (Antigravity CLI, Claude Code, Codex) the subject says pass its automated install and end-to-end fixtures (docs/harnesses.md:143-144); 10 with the three experimental adapters that ship dedicated files but no table row (Cursor .cursor-plugin/, GitHub Copilot CLI com.github.copilot/, OpenCode adapters/opencode/install.py). omp and Muse have rows but no files of their own (they load the Claude manifest)"
workflow_features:   # deep-dive 2026-11-10 @ dea7761
  intent_pipeline: true          # /egm-brainstorm → concepts_brief.md → /egm-draft → design_draft.md → docs/designs/<FEATURE>.md → /egm-review → /egm-resolve; it ENDS at a reviewed design doc — no skill implements ("No Skill.md is required here", docs/designs/architecture.md:157-159)
  deterministic_engine: false    # checked and absent: 47 files match the executable-extension filter, 0 carry an executable bit; the 3 outside tests/ and site/ are packaging and install code (scripts/pack_plugin.py, scripts/prepare_release.py, adapters/opencode/install.py); no installed bundle contains code; stage order and output checks are SKILL.md prose
  format_gates: prose            # ADR-0011 graded: no program checks the brief or the draft; the structural Goldfish judges layout against a standard; bootstrap's worker-return.schema.json is read by the model and validated by nothing; the 7 test_scenarios.yaml files are schema-checked in CI but their assertions are never executed
  measured_gates: false          # checked and absent: no skill, persona or standard runs a build, a test or a command, and no gate compares a measured value with an expected one; the draft's Verification Plan holds commands as text; reviewers on Claude are tool-limited to Read/Grep/Glob
  process_gates: prose           # ADR-0011 graded: 15 human checkpoints in brainstorm/draft/resolve plus a checkpoint after every review stage, all self-applied text; "Proceed" is Option 0 at every review gate and a 1-re-audit cap auto-advances (egm-review/SKILL.md:271-275); the vendor: "This is a convention, and nothing enforces it" (architecture.md:164-165)
  context_isolation: true        # the product's verification instrument, not plumbing: every Goldfish is a fresh subagent (egm-review/SKILL.md:21); enforcement is host-declared per harness — Claude omitClaudeMd + Read/Grep/Glob, Copilot include-custom-instructions: false + read/search, Cursor permissionMode: readonly, OpenCode generated deny-all-but-read — and absent for Antigravity and Codex (prose plus spawn semantics; leaks reported in subject issue #237)
  parallel_orchestration: true   # reviewers within a stage fan out in parallel through egm-synthesizer, or by direct dispatch where the host cannot nest (egm-review/SKILL.md:26-27); stages stay sequential (docs/claude.md:44-46); 10 reviewer spawns per full review
  state_store: repo-files        # concepts_brief.md, design_draft.md, stage report files, docs/designs/<FEATURE>.md and SITEMAP.md; working drafts may sit in the harness's artifact directory instead (egm-brainstorm/SKILL.md:42-44)
  retrospectives: false          # checked and absent: zero non-"feedback" hits for retrospect|lessons learned|post-mortem|learnings across skills/, agents/, resources/; the settled-findings list lives one review-loop run; /egm-drift-report reconciles doc with code but captures no lessons
---

# elephant-goldfish-model (EGM)

Google's open-sourced plugin for designing software with agents before any code is written,
launched on the Google Open Source Blog on 2026-10-22 ([source note](../../references/papers/2026-egm-launch.md)).
The **elephant** is the main session, which holds the project context and drafts a design
document with the human. The **goldfish** are reviewers run as fresh subagents, which see the
document but not the conversation that produced it. Seven skills (`git ls-tree -d --name-only
v0.1.1 skills/`) and ten persona files (`git ls-tree --name-only v0.1.1 agents/`) are shared by
every host. The workflow stops at a reviewed design document: building it is handed back to
whatever agent the human uses next. The repo says it is "not an officially supported Google
product" (`README.md:135`).

## The distinguishing bet

**Independence is the verifier.** The bet is that a reviewer who never saw the design
conversation finds what the designer cannot, so the framework spends its whole verification
budget on making reviewers independent. It never spends it on measuring anything. Every gate on
the user's work is prose a model applies to itself, and the packager refuses to ship anything
else: `scripts/pack_plugin.py:83-84` raises `ValueError("Directory packages cannot contain
hooks")`. The one mechanism the framework does put outside the model is **the reviewer's
isolation**. It writes that isolation into per-host agent definitions, so each host enforces it
with its own machinery. On Claude Code the eight reviewer adapters carry `omitClaudeMd: true` and
`tools: [Read, Grep, Glob]`. On Copilot they carry `include-custom-instructions: false` and
`tools: [read, search]`. On Cursor they carry `permissionMode: readonly`, and on OpenCode the
installer generates a deny-all-but-read permission map. The subject also ships probes that
check whether that isolation held (§ Substrate). Its rivals would dispute the bet from two
sides. GSD enforces its isolation in a hook and measures its gates. Conclusion 6 of this repo
located a framework's measured value in grounding and measured verification, which EGM does not
attempt (§ What it means for conclusion 6).

## Main features

- **Five-stage review** (`/egm-review`): Initial Zoom Out (zoom_out + inventive_catalyst,
  parallel) → Comprehension (one reader with the document alone, paraphrasing it back) → Critic
  (design_critic, structural, style) → Intermediate Zoom Out → Implementation Readiness
  (implementation_readiness, codebase_details, style), `egm-review/SKILL.md:286-303`. Ten reviewer
  spawns per full run, counted from the five `Reviewers:` lists plus the direct comprehension
  spawn. Presets run stages 5–8 only, or stage 9 only (`:162-177`). Distinctive: the comprehension
  stage tests whether the document stands alone, which no other tracked framework does.
- **Brainstorm with a goldfish panel** (`/egm-brainstorm`): a multi-turn interview with
  anti-sycophancy rules ("Critique First", banned adjectives, `SKILL.md:63-83`), then a 7-persona
  fan-out on a 2–3 sentence hypothesis, then `concepts_brief.md`.
- **Section-gated drafting** (`/egm-draft`): Overview/Problem/Goals → Technical Plan →
  Alternatives → Detailed Implementation, each closed by an approval question (`SKILL.md:87-139`),
  and an "Author Decides Architecture" rule that forbids the agent from ranking options even when
  asked (`:63-71`). Table stakes in the category, with an unusually strict anti-steering rule.
- **Drift report** (`/egm-drift-report`): the main agent compares checked-in design docs with
  current source and writes `{YYYY-MM-DD}_DRIFT_REPORT.md`. It is the only skill that runs after
  implementation, and it reads; it does not measure.
- **Bootstrap** (`/egm-bootstrap`): parallel "goldfish-explorer" scouts read source and write
  per-directory README contracts, so a brownfield repo has documents to review against.
- **Host isolation declarations plus isolation probes** (§ Substrate) — the genuinely
  distinctive feature.

## Stack & repo shape

298 files at the pin (`git ls-tree -r --name-only v0.1.1 | wc -l`). By top-level directory:
`distributions/` 66, `site/` 48, `skills/` 38, `docs/` 33, `tests/` 29, `.github/` 14,
`.claude-plugin/` 13, `.cursor-plugin/` 11, `agents/` 10, `com.github.copilot/` 9, `resources/` 7.
The product is Markdown, YAML and JSON. Python appears only in packaging, the OpenCode installer
and the repo's own tests, and the `site/` Astro project builds the egm.dev landing page.
`distributions/claude/` is a generated copy of the Claude runtime (66 files, byte-identical at the
pin to what `pack_plugin.py --target claude` selects, checked blob-by-blob; it is the path the
Anthropic directory listing points at, while marketplace installs read the repo root).

**Provenance.** The public history begins with a root commit, `096e9ad` (2026-10-21, "feat:
initial open-source release of Elephant-Goldfish Model (EGM)", 104 files, 13,248 insertions,
`git show --shortstat`), while `docs/designs/architecture.md:5` is dated 2026-06-06. That fits the
launch post's account that the plugin "was developed internally for Google software engineers"
(INFERENCE: prior private history, squashed). GitHub's `created_at` is 2026-09-13. 159 commits
reach the pin, 84 of them first-parent. The launch post's "Thousands of Googlers use this plugin
every day" is testimony nothing in the repo bears on.

## Architecture — deep-dive 2026-11-10 (pin dea7761; three-tract source read)

Components traced: all four category-4 functions, plus the delivery substrate. Citations are
`path:line` at the pin.

### F1 — intent refinement: a strong interview, and no reading of the codebase

The front half tests the English hard and the code not at all. Brainstorm makes the agent read
the user's words and `git config user.name` (`egm-brainstorm/SKILL.md:106-109`); no step tells it
to read source. Of the seven brainstorm personas, only `zoom_out` is told to search code
("Perform codebase searches to identify existing components", `agents/zoom_out.md:38`), and it
receives only the 2–3 sentence hypothesis. The persona named `codebase_details` reviews
observability in brainstorm mode (`agents/codebase_details.md:28-32`). The vendor's own design
doc mislabels it "Codebase Grounding & Existing Reuse Lens" (`docs/designs/brainstorm.md:126`).
Drafting reads the brief, git identity, existing design directories and `SITEMAP.md`. Its one
claim that drafting reads code ("the draft can be right, because drafting reads code that the
brainstorm did not", `egm-draft/SKILL.md:269-271`) is asserted, and no step implements it.

Context moves between skills by file at a conventional path and by the human typing the next
command. Draft probes for `concepts_brief.md` in `./`, the artifact directory or `scratch/`
(`egm-draft/SKILL.md:143-160`). Every skill sets `disable-model-invocation: true`, so the
model cannot chain them through the Skill tool. Two writers are specified for
`concepts_brief.md`, the elephant (`egm-brainstorm/SKILL.md:177-179`) and the synthesizer
(`agents/synthesizer.md:32-33`), and only the elephant has the template. Which write wins is
INFERENCE until a run.

### F2 — work decomposition: a file inventory, not a task grammar

The draft's last section enumerates files: "List EVERY file that will be changed, created, or
deleted", each with a rationale, "in one unified section" (`egm-draft/SKILL.md:230-235`); the
template entry is `#### 1. [File Path 1] ([Create | Modify])` with Type/Scope and Proposed
Changes (`references/design_doc.md:139-159`). The units carry no order, dependency, per-unit done
criterion or status, and the handoff goes to `/egm-review`, not to an executor
(`SKILL.md:317-321`). **The drafter and the reviewer disagree about decomposition.** The
readiness standard requires "logical, incremental phases. Each phase must leave the codebase in a
stable, buildable, and testable state" and a "Target Scope & File Boundary" list
(`resources/document_standards/implementation-readiness-standard.md:20-33`). The draft template
produces neither, so phasing is a criterion a reviewer applies at stage 9 that the drafter was
never told to meet. The template has 10 H2 sections (`grep -c '^## '`), and the drafting steps
name 7. Open Questions, Critical User Journeys and Non-Functional Requirements, plus the
Verification Plan, get no step and no approval gate.

### F3 — gap research: read-only lookup, conditional

Nothing measures the domain. Grounding is reading:

- zoom_out's code search runs only when a design proposes new components
  (`agents/zoom_out.md:45`).
- codebase_details compares document with source at stage 9 only, limited to the source files
  in its supplied context (`agents/codebase_details.md:37-38`).
- the drift report runs in the main context, not a fresh one (zero hits for
  `subagent|goldfish|fresh` in `skills/egm-drift-report/`).
- bootstrap's scouts read source in full to write documentation.

Bootstrap records a project's test command into the README it writes
(`egm-bootstrap/SKILL.md:84`) and never runs it. External research is limited to URLs the user
supplies, saved as files (`egm-review/SKILL.md:112-117`). Every persona says "You have NO tools
to … compile code" (`agents/*.md:11`). The only place that says what a review does not
establish is the README ("A review does not replace tests or human judgment", `README.md:99`);
no skill or persona says it.

### F4 — verification: independent opinions, no gate that holds

Who checks the claim that the design is ready: up to ten fresh-context reviewers on the
designer's own model (`model: inherit` on every Claude and Cursor adapter), whose findings the
elephant then triages in `/egm-resolve` with the human. The resolve skill polices its own
author: "You wrote the document under review. A wish to contest is not evidence"
(`egm-resolve/SKILL.md:81-82`). Its contest rule requires "a file and symbol" a reviewer could
read (`:54-82`). **No verdict can stop the flow.** Every stage gate offers "Proceed" as Option 0
(`egm-review/SKILL.md:236-251`). The stage-9 terminal gate's Option 0 is "Conclude review and
finalize document" (`:408-417`). After one re-audit the review must "document residual findings
as accepted trade-offs, auto-bind Option 0, and advance to the next stage" (`:271-275`), so a
Blocker cannot hold a stage. The vocabulary of a go/no-go is absent: zero hits for
`no-go|go/no|go-no|nogo` across `skills/ agents/ resources/`. Comprehension "accuracy" is judged
by the human: "The author compares it with the intent. A wrong paraphrase is a finding"
(`agents/comprehension.md:57`).

One honesty rule stands out, model-applied but well aimed. A reviewer that fails is retried once
and then recorded as `not run`, "Never count it as a reviewer with zero findings", and a missing
reviewer makes the round not clean (`egm-review-loop/SKILL.md:140-144, 169-172`). That is the
category's closest analogue to GSD's `human_needed` abstention. Two convergence regimes are left
unreconciled: review's 1 re-audit per stage, and review-loop's "Two consecutive clean rounds",
"Cap: 5 rounds" (`egm-review-loop/SKILL.md:173-175`), which stages 7 and 9 both invoke.

The guard that makes a review a goldfish review is prose too: "If your harness has no subagent
tool, stop and tell the user: a review in the same context is not a Goldfish review"
(`egm-review/SKILL.md:28`; the same text at `egm-brainstorm/SKILL.md:36` and
`egm-review-loop/SKILL.md:43-44`). No hook or script checks for the tool, and no test covers the
stop. `/egm-bootstrap` does the opposite: "run the scout steps inline" (`SKILL.md:35`). Its own
`TEST.md:14-16` expects a halt, so one of the two is stale.

### Substrate — host-declared isolation, plus probes of whether it held

The category test passes cleanly. `skills/`, `agents/` and `resources/` are shared by every
host, and host-specific files are thin adapters that point at the canonical persona
(`${CLAUDE_PLUGIN_ROOT}/agents/<file>.md` on Claude, `EGM_ROOT/agents/…` on Cursor and Copilot).
The subject states the boundary of that portability: "Skill-only installers that copy `skills/`
alone break EGM" (`docs/harnesses.md:24-26`), because the skills read `agents/` and the standards
at run time. Portability belongs to the whole package, not the skills standard.

Who enforces the reviewer's isolation, per host:

| Host | Parent conversation excluded | Instruction files excluded | Tools restricted | Whose machinery |
|---|---|---|---|---|
| Claude Code | host (subagent default) | `omitClaudeMd: true` on 8 of 10 adapters | `tools: [Read, Grep, Glob]` | host; EGM declares |
| GitHub Copilot CLI | host | `include-custom-instructions: false`, enforcement unverified by the subject | `tools: [read, search]` | host; EGM declares |
| Cursor | host + an `alwaysApply` rule | none declared | `permissionMode: readonly` | host; EGM declares |
| OpenCode | host | none declared | generated `permission` map (`install.py:65-79`) | host; EGM generates config |
| Codex / ChatGPT | the model is told to pass `fork_context: false` / `fork_turns: "none"` | none; leak reported | none | host + prose |
| Antigravity | `invoke_subagent` | none; leak reported | none | host + prose |
| Muse | host | none effective | declared, but "tool projections unsupported" | host + prose |

`omitClaudeMd` is a real field. In Claude Code 2.1.319 (the installed binary, read 2026-11-10)
its schema description reads "Run this agent without the user, project and local CLAUDE.md
instruction files when it runs as a subagent; managed policy files are kept". The plugin-agent
loader ignores only `permissionMode`, `hooks` and `mcpServers`, plus `initialPrompt` and three
observer fields, with a warning. So the Claude adapters' isolation fields apply to plugin agents
(OBSERVED in the binary's strings, not a source read; Claude Code is closed). The subject pins
"Claude Code 2.1.271 or later for `omitClaudeMd` support" (`docs/claude.md:8-9`). Two gaps the
table hides: the Claude **synthesizer** adapter has no `omitClaudeMd` and writes the reviewers'
prompts in hierarchical mode (`.claude-plugin/agents/synthesizer.md:1-8`), so instruction-file
content can reach a reviewer through its prompt (INFERENCE, not traced). And Copilot's CI probe
launches the CLI with `--no-custom-instructions` globally
(`tests/integration/copilot_controlled_probe.py:130`), so it cannot test the per-agent exclusion
it exists to back.

The evidence tooling is what EGM adds on top of what hosts provide. CI probes run Copilot and
OpenCode against scripted local models and check that a parent marker is absent and a `.env`
read is denied (`opencode_native_probe.py:200-261`). Opt-in live probes check Claude and Codex.
Post-hoc trace verifiers cover Cursor and OpenCode. The docs separate what was tested from what
was not, unusually carefully: "parent-turn isolation and host-instruction exclusion are separate
results" (`docs/harnesses.md:143-145`), and "No host-specific exclusion control is verified here
for Codex or Antigravity" (`:154-155`). The skills' own delegation preamble names only three
hosts ("Antigravity: `invoke_subagent`; Claude Code: `Agent`; Codex: `spawn_agent`",
`egm-review/SKILL.md:22`). Routing for the three experimental adapters is injected from outside
the skills.

**The hook that came and went.** A Claude PreToolUse read-approval hook was added in `a9738d4`
(2026-10-22) and removed in `f91dccb` (authored 2026-10-24, committed 2026-10-26). Tests now
assert its absence (`tests/unit/test_harnesses.py:204-209`), and the packager refuses hooks, but
`TESTING.md:48` still says "The read-hook tests require a POSIX `sh`". The one move toward
mechanical enforcement lasted four days and became a packaging rule against it.

## What it means for conclusion 6

EGM is the category's purest bet on the half of the pipeline that conclusion 6 found carried
almost none of the measured value. Its verification targets the specification, by model opinion,
against model-read standards. Grounding is read-only lookup, and nothing reaches implemented
behaviour. The launch post states the bet as a goal: "for the AI to correctly produce the code
you wanted the first time after you press Enter". That is a falsifiable claim, and the repo
ships no measurement of it: the 7 `test_scenarios.yaml` files (43 scenarios by `grep -c
'scenario_id:'`) carry `eval_type: "deterministic"` regex assertions that no code at the pin
executes. So EGM neither supports nor contradicts conclusion 6; it is a design whose value would
have to show up where conclusion 6 says value rarely shows up. A preregistered
spec-review-versus-plain arm would test it. That is parked as an idea, not proposed.

## Run probe — 2026-11-10 (rule 8: partial)

**Published artifact (rule 8b), run.** `gh release download v0.1.1` fetched `egm-claude-0.1.1.zip`
(127,909 bytes), `egm-openai-0.1.1.zip` (109,814) and `SHA256SUMS`; `sha256sum -c` passed both.
Every extracted file was hashed against the pin tree (root or `distributions/claude/`):
**66/66** Claude files and **55/55** OpenAI files are byte-identical to a pin file, with none
added. The Claude ZIP is exactly `distributions/claude/` (66 files). Nothing is injected at
publish time, and the release ships no executable code. The release notes state "Native end-to-end
verification of these exact release ZIPs remains open in #60".

**Executables, not run.** Running the pin's packaging scripts and unit suite in a scratch venv
was denied by this session's permission policy. They are packaging and the repo's own CI, and no
claim above depends on their runtime behaviour. Tract C's exact offline commands are kept for a
later sitting.

**Live review, not run (spend gate).** The open runtime questions all need a model session, and
spending model quota waits for the owner's sign-off. They are: does the same-context stop fire
when no subagent tool exists, do the gates hold or auto-advance, and which `concepts_brief.md`
write wins.

## Drift check — 2026-11-10 (HEAD 8f16812, 25 first-parent commits past the pin)

`git diff --stat v0.1.1 origin/main` over the traced paths (`skills agents resources
.claude-plugin .codex-plugin .cursor-plugin com.github.copilot adapters scripts plugin.json
.agents docs/harnesses.md`): 9 files, 40 insertions, 12 deletions. **Untouched:** every persona,
every Claude/Cursor/Copilot reviewer adapter, and the brainstorm, draft, resolve, review,
review-loop and drift-report skills, so every gate and isolation claim above holds at HEAD.
**Touched, not contradicting:** bootstrap's source-extension list grew (`51cfc42`); a Cursor
marketplace catalog (`6ec28cb`) and Copilot workspace discovery (`69fb200`) landed; and
`docs/harnesses.md` now advises committing approved specs and `AGENTS.md`. `db81378` changed a
release design doc, and `distributions/claude/` still exists at HEAD. The Copilot entry agent's
stale "seven registered EGM reviewer profiles" (8 ship) was corrected in `a7ba56a`.

## The launch post, confronted (source: [2026-egm-launch](../../references/papers/2026-egm-launch.md))

| Post claim | Verdict at v0.1.1 | Evidence |
|---|---|---|
| The elephant session: "No code is written here" | PARTLY | The rule exists in draft Step 5 (`egm-draft/SKILL.md:241-242`) and `resources/execution_instructions.md:3-14`, which only egm-draft loads. Brainstorm has none (0 hits). The vendor says it is "a convention, and nothing enforces it" |
| Goldfish are "stateless, zero-context sessions" | PARTLY | Parent conversation excluded by design. Instruction files leak on Codex and Antigravity (subject issue #237). Stage 8 is handed stage 5's report by design (`egm-review/SKILL.md:320-321`). Reviewers get personas, standards and supplied context |
| "they share no 'blind spots' with the designer" | PARTLY | No shared conversation. A shared model: `model: inherit` on every adapter that names one |
| "automates the orchestration … managing context transfer … rendering design documents" | PARTLY / FALSE | Orchestration is prose the host model runs, and context moves by file path and the human's next command. Nothing renders documents (`site/` is the egm.dev landing page) |
| The Goldfish Protocol is "a three-step validation sequence" | PARTLY | Five stages at the pin; the post's three are stages 6, 7 and 9, without the two zoom-out stages |
| Comprehension: "If the Goldfish cannot accurately summarize the plan … requires further drafting" | PARTLY | The human judges accuracy (`comprehension.md:57`), and the stage's Option 0 is Proceed |
| "A final Goldfish performs a strict go/no-go check" | FALSE as stated | Three reviewers emit severity findings. No go/no-go vocabulary exists, and the terminal gate's Option 0 concludes the review |
| Draft covers problem, technical plan, alternatives, and "a detailed implementation plan that enumerates the specific files to change" | HOLDS | `references/design_doc.md:16, 75, 89, 139-159` |
| "bring the EGM framework directly into Antigravity, with other development environments upcoming" | HOLDS at the post's date | The root commit ships only `plugin.json` plus 9 personas; by v0.1.1, 10 hosts |

## Bleed

Delivery is category-6 shaped: plugin marketplaces for Claude and Codex, a ChatGPT listing, a
Cursor `alwaysApply` rules file (`.cursor-plugin/rules/egm.mdc:3`, injected into every Cursor
session where the plugin is enabled, scoped only by prose), and Copilot agent profiles. There is
no category-2 bleed, and the absence is the point. EGM owns no loop and no permission surface; it
writes configuration for each host's. That makes it a clean specimen of the taxonomy's claim that
isolation and fan-out live on a substrate hosts provide. The framework's distinctive contribution
sits at the seam: declaring the substrate per host and testing whether it held.

## Cost model

Free (Apache-2.0); no paid tier, nothing paywalled. Runtime cost is model tokens on the user's
own plan. A full review is ten reviewer subagents plus up to four synthesizer spawns, each
re-reading the document and standards; the synthesizer may "optionally" run two instances per
reviewer (`agents/synthesizer.md:40`), so ten is a floor. The subject reports a Muse run with
"15 fresh-context reviewers" (`docs/harnesses.md:161`).

## Next to superpowers and GSD (2026-11-10)

| Axis | EGM @ dea7761 | [superpowers](superpowers.md) @ b36e082 | [gsd-core](gsd-core.md) @ 182f60b4 |
|---|---|---|---|
| Scope | design only; stops at the spec | spec → plan → execution → merge | spec → plan → execution → verify |
| Engine | none; hooks refused by the packager | none, on purpose | TypeScript runtime |
| Isolation | host-declared per harness, probed | prose | hook-enforced |
| What reviewers check | the spec, by opinion | the code, by opinion against self-reported test evidence | the code, with measured expected values |
| Gate that can stop the flow | none (Proceed is always Option 0) | none (prose) | engine and hook gates |

## Surprises

1. **The launch post's sharpest promise has no mechanism.** "A strict go/no-go check" is three
   reviewers whose findings can always be proceeded past, and after one re-audit the skill
   records Blockers as "accepted trade-offs" and advances on its own.
2. **Isolation is the only thing EGM pushes outside the model, and it pushes it into the
   host.** Every other rule is prose. Reviewer isolation is written into four hosts' agent
   schemas and probed in CI, with the docs separating parent-turn isolation from
   instruction-file exclusion more carefully than most vendors separate anything.
3. **The front half does not read the code.** A methodology sold on "system comprehension"
   designs from conversation; the persona named `codebase_details` reviews observability during
   brainstorm.
4. **The reviewer demands what the drafter was never asked for.** Incremental phases and a file
   boundary are stage-9 criteria; the draft template has neither.
5. **The vendor's own evals do not run.** 43 scenarios marked `eval_type: "deterministic"` are
   only schema-checked.
6. **The one hook lasted four days**, and its removal became a packaging rule.
7. **Text contradicts text in several places**: bootstrap's test plan expects a halt where its
   skill runs inline. The review design doc names standards the skill never passes
   (`docs/designs/review.md:84, 99`). Cursor's guide says "seven" and "eight" reviewers.

## Scored pre-read predictions (from the 2026-11-10 candidates row)

The row was written from the README and `docs/harnesses.md` at HEAD, before any source or the
launch post was read.

- **(1) `deterministic_engine` ✗ — TRUE.** Nothing a user's session executes sequences stages or
  checks outputs. The row's premise listed only `scripts/`; the pin also has
  `adapters/opencode/install.py` (a one-time config generator) and `tests/integration/` (CI and
  opt-in probes). Neither changes the score.
- **(2) The same-context guard is `prose` — TRUE.** SKILL.md text in three skills, no checker,
  no test of the stop, and hooks refused by the packager.
- **(3) Reviewer isolation machine-enforced on Claude hosts only — FALSE.** Copilot
  (`include-custom-instructions: false`, `tools: [read, search]`), Cursor
  (`permissionMode: readonly`) and OpenCode (generated permissions) each ship an equivalent
  control. The row had read the docs' Claude/Codex/Antigravity framing and generalised it to
  every host. The true statement is that **only Antigravity and Codex/ChatGPT get no declared
  control**, and only Claude and Copilot declare instruction-file exclusion.
- **(4) Front half only, no work decomposition — TRUE, borderline.** No skill hands task units
  to an executor or drives implementation. The draft does emit a per-file change inventory, which
  the vendor's readiness standard calls a "task list" (`implementation-readiness-standard.md:3`).
  A scorer adopting that vocabulary would trip the false side. It is scored TRUE because the
  inventory has no order, dependency, done criterion or executor handoff. EGM is the first
  deep-dived category-4 framework with no implementation step. The other five each ship one:
  spec-kit's `speckit.implement`, openspec's `openspec-apply-change`, gsd-core's executor,
  bmad-method's dev-story and superpowers' subagent-driven development.

## Vocabulary candidates (not admitted — owner decision)

- **A who-enforces grade for `context_isolation`.** Three deep-dived instances now give three
  different enforcers for the same presence ✓: superpowers (prose), gsd-core (hook) and EGM
  (host-declared agent fields). This is the same ambiguity ADR-0011 resolved for the three gate
  keys by grading them. It clears the two-instance bar for a value change, but it would regrade
  an existing key across every category-4 report, so it is a registry change with an ADR. Not
  admitted. Re-check trigger: the owner's call.
- **"Stops at the spec."** One instance; `intent_pipeline: true` already says where the pipeline
  starts but not where it ends. Recorded, not proposed.

## Open questions

- **Do the gates hold in a real session?** One `/egm-review` run on a seeded design document in a
  scratch project would show whether a Blocker gets proceeded past, whether stage 9 runs when the
  plan section is named "Detailed Implementation", and which brief writer wins. Parked for spend
  sign-off.
- **Does the synthesizer leak instruction files into reviewer prompts on Claude Code?** A marker
  probe through the hierarchical path would settle it. Whether the subject's own
  `tests/integration/test_claude.py` covers that path was not traced.
- **Rensin's origin essay** (Medium, cited by the README and the post) is unread. It may state
  the method's rationale in falsifiable form.
- **Re-read trigger:** the next tag after `v0.1.1`, or `distributions/claude/` being replaced by a
  release branch (`docs/designs/claude_release_branch_distribution.md`).
