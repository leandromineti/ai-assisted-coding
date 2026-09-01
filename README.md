# AI-assisted coding

A survey of the AI-assisted-coding tooling landscape, organised as a **taxonomy of tool
categories** with **dated, evidence-linked** findings — read from source and measured in
preregistered trials rather than taken from marketing pages.

Exploratory, not prescriptive. The deliverable is notes and conclusions, not a product:
every claim carries the date it was checked and a link to what it rests on, and the two
honesty columns say plainly how deeply each tool and each source was actually read. The
map that survived the first month is published as an article: [The AI-coding stack: a map
for a landscape that won't sit
still](https://mineti.dev/articles/the-ai-coding-stack/).

## Start here

**[`docs/tool-taxonomy.md`](docs/tool-taxonomy.md)** — the shared vocabulary, with a boundary rule, a
bleed/maker-span distinction, and a stress test for the many tools that straddle the
divisions. A **core triad** — categories 1–3, the three things a running agent cannot
lack — plus three **interfaces** (4, 5, and the bucket at 6) that mediate between the
triad and everything around it. Every note and comparison here declares which category
its subject occupies:

1. **[Models](tools/1-models/README.md)** — cognition: the weights, and the first-party
   API surface that prices and meters them. *Opus 5, Fable 5, Grok 4.5, Kimi K3.*
2. **[Harnesses](tools/2-harnesses/README.md)** — mediation: the program that runs the
   agent loop, assembles context, and gates permissions. *Claude Code, OpenCode, Codex
   CLI, Cursor.*
3. **[Execution environments](tools/3-execution-environments/README.md)** — situation:
   where execution lands and what it can damage. The autonomy ceiling lives here, not in
   the model. *worktrees, devcontainers, E2B.*
4. **[Workflow frameworks](tools/4-workflow-frameworks/README.md)** — the human⇄stack
   boundary: intent refined into specs and subtasks going down, research and verified
   evidence coming up. *GSD, spec-kit.*
5. **[Memory](tools/5-memory/README.md)** — the agent↔time edge: persistent
   cross-session state as an installable product, a full category since the 2026-08-22
   split. *ai-memory, mem0, MemOS, cognee.*

**[Extensions](tools/6-extensions/README.md)** is category 6, and reads apart from the
five above because it is a cross-category bucket rather than one of the fundamentals: the
distributable content an agent can see and touch — MCP servers, skills, hooks, rules
files, subagent definitions, config packs (ECC) — parameterizing the triad's remaining
edges. Its *runtimes* were always harness features, so what remains is artifacts
distributed on file conventions; portability is conferred by adoption, not intrinsic, so
the name doesn't claim it. Beside it, [`docs/`](docs/README.md) holds the **cross-cutting**
notes, which belong to no single category and appear at several at once — context
engineering, verification, cost, standards (MCP, `AGENTS.md`). How the taxonomy reached
this shape — demotions, adjudications, the 2026-08-18 renumbering, the 2026-08-22 split —
is one dated decision record each in [`adrs/`](adrs/README.md).

**[`docs/methodology.md`](docs/methodology.md)** — how work is done here: verification and honesty
rules, generated indexes, preregistered experiments, the upstream-reporting gate. Every
rule earned its place by catching a real mistake; the anti-goal section keeps it from
growing rigor for rigor's sake.

**[`docs/design-principles.md`](docs/design-principles.md)** — the synthesis layer: design
principles derived from the documented tools, per taxonomy category, each carrying a
confidence marker (convergent / single-instance / contested) and its evidence citations.
Hypotheses under revision, not best practices — every new deep-dive or experiment must
confirm, contradict, or note silence.

## Layout

```
.
├── README.md                  the map, the layout, and the conclusions index
├── CLAUDE.md                  how the repo works: where things go, the ingest and lint operations
│
├── docs/                      the constitution, the output, and the notes that span categories
│   ├── tool-taxonomy.md                category definitions + boundary rule — the canonical reference
│   ├── tool-taxonomy.yaml              its machine-readable half; the vocabulary lint's only source
│   ├── methodology.md             the working rules — verification, honesty markers, protocol
│   ├── design-principles.md       principles per category, each confidence-marked
│   ├── conclusions.md             the numbered findings — what the survey actually concluded
│   └── …                          benchmark-survey · metrics · standards · feature-taxonomy
│
├── tools/                     one report per tool, filed by category
│   ├── 1-models/ … 6-extensions/  category front door (README.md) + one report per tool
│   └── candidates.md              sighted-but-not-ingested ledger, the pre-report stage
│
├── references/                the citation library — one note per source read
│   ├── papers/                    literature; each note carries its own read_depth
│   ├── cards/                     vendor model cards; each note carries a required snapshot
│   └── index.md                   generated catalog of both halves
│
├── experiments/               preregistered A/Bs: protocol, log appended live, artifacts
│   └── rig/                       the pinned container + hidden verifier both arms run against
│
├── comparisons/               generated matrices — tools, features, models, environments, benchmarks
├── adrs/                      dated, immutable records of every structural decision
├── articles/                  public-facing drafts, written next to the evidence they cite
├── scripts/                   the two index generators, the vocabulary lint, the fact collectors
└── upstream/                  cloned study copies — gitignored; a manifest, not the code
```

**[`comparisons/tools.md`](comparisons/tools.md)** is the flat cross-category index of every
tool with a report, **[`comparisons/features.md`](comparisons/features.md)** the
harness feature matrix, and **[`comparisons/models.md`](comparisons/models.md)** the
category-1 matrix (reasoning control, caching economics, batch pricing — the API surface
that drifts fastest) — all generated from the reports' frontmatter, never hand-edited,
so they can't drift from them. In the matrices, `·` means *not yet checked*, which is
deliberately distinct from ✗ *verified absent*.

Tools queued for assessment but not yet cloned live as **GitHub issues on this repo**
([issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) is the
pattern) — candidates already weighed and passed over are recorded in the relevant
category index's "considered, not added" table instead.

One report per tool, following
[`tools/_template-tool-report.md`](tools/_template-tool-report.md) — or, for category 1,
[`tools/1-models/_template-model-report.md`](tools/1-models/_template-model-report.md), since
weights have no repository to pin or trace. Its **"distinguishing
bet"** field is the one that matters — what does this tool believe that its competitors
don't? — and **`depth`** is the honesty marker: `stub` (facts collected, source unread),
`survey` (used or skimmed), `deep-dive` (the category's components traced — defined in
[`docs/tool-taxonomy.md`](docs/tool-taxonomy.md) — the report saying which; pre-2026-08-25 deep-dives read
under the earlier loop+context definition).

The point of reusing one task across `experiments/` is to make comparisons honest instead
of impressionistic — though see the open question in
[`docs/`](docs/README.md) about whether a clean A/B is
possible here at all.

## Conventions

- Every claim about a tool carries a `checked: YYYY-MM-DD` date. This field moves fast and
  notes go stale quietly.
- Anything not confirmed against a primary source is marked `unverified` rather than
  asserted.
- A tool that hasn't actually been used gets an **empty** "my take" section. The blankness
  is the honest state.

## Conclusions

_The running answer to "what did I actually learn?" — each dated, each traceable
to a note. Revised when evidence moves. Headlines here; the full text, with the
evidence links, is [`docs/conclusions.md`](docs/conclusions.md)._

1. **"The models have converged" is contested by the people best placed to know** (2026-07-28)
2. **No public benchmark isolates model from harness** (2026-07-28)
3. **The extensions bucket (category 6; numbered 5 until the 2026-08-22 split) is "MCP plus vendor features," so far** (2026-07-28)
4. **Structural completeness does not predict runtime correctness** (2026-07-28, from llm-coding-benchmark's data)
5. **Reading source beats reading marketing, quickly** (2026-07-28)
6. **A workflow framework's value concentrates in empirical grounding, not process ceremony** (2026-07-28, n=1)
7. **A category-4 framework's portability and its enforcement power are the same tradeoff** (2026-07-28, spec-kit source read)
8. **Harnesses are absorbing the stack from the middle** (2026-07-30, from the hermes + codex deep-dives)
9. **The environments category (3) is a real category, not an axis of the harness category — decided by its own falsifier** (2026-08-16, decision record [ADR-0003](adrs/0003-environments-stay-a-rung.md))
10. **A task-level trap instrument that cannot rank same-tier runs still separates model tiers — and its items are not monotone in capability** (2026-08-17, measured)
11. **Intent capture steers trap behavior but does not add trap discovery** (2026-08-17, measured — exp-02's preregistered A/B, both predictions supported)
12. **A model tier absorbed a workflow mechanism whole — and the category-4 A/B arc closes on it** (2026-08-18, exp-03, preregistered two-tier ablation, saturation branch pre-declared)
13. **The memory extensions sell to coding agents but benchmark on chat** (2026-08-18, memory-type reading arc: one deep-dive, two surveys, three instrument full-reads)
14. **Cross-harness memory continuity is real and entirely pull-shaped** (2026-08-19, exp-04, n=1 per arm — a probe)
15. **Harnesses track models by name, so a model's own API drift silently disarms them** (2026-08-26, four harnesses read at their pins — three version-pin, one sends a parameter Anthropic now rejects; **qualified 2026-08-27** by a fifth that inverted the polarity on purpose — a denylist of superseded families, defaulting unknown models to the newest contract)
16. **Every model maker ships its own harness — the composability the taxonomy assumes is not what the market is selling** (2026-08-26, eight of eight makers, no exceptions; the last two found by falsifying this repo's own claims)
17. **The context-assembly position everyone assumed nobody held was held all along, by the oldest and most dormant tool in the set** (2026-08-27, aider — a tree-sitter symbol index ranked by PageRank, injected as source lines every turn, 71% of the assembled prompt; the claim had survived three deep-dives because all three were tool-dispatch harnesses)
18. **A harness with no tool loop ships the strongest native verification gate in the set** (2026-08-27, aider — zero-config `--auto-lint` runs a real linter on every edit and feeds failures back; "runs something fresh" turns out not to require agentic dispatch)
19. **The served API outranks its own documentation, and the tiebreak costs nothing** (2026-08-31, eight-maker probe campaign under $0.02 — docs found wrong, silent, or misleading five independent ways in one day; three of the five findings were free because rejected requests bill nothing)

## License

[MIT](LICENSE). Cloned upstream sources (`upstream/`, gitignored) and cached papers
(`references/papers/pdf/`, gitignored) belong to their respective owners.
