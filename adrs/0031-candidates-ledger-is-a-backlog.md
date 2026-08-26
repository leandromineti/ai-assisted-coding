# ADR-0031 — The candidates ledger is a backlog: promotion removes the row

`decided: 2026-08-26` · status: **accepted**

## Decision

`tools/candidates.md` holds **open work only**. When a candidate is ingested and gets a
report, its row is **removed**, not annotated. Anything in the row that is still
load-bearing after the read — a licensing finding, a pre-read prediction the report will
score — moves into the report first. Removed rows remain in git history.

This supersedes ADR-0009's append-mostly clause ("promotion annotates the row with a
dated pointer to the new report rather than deleting it; refusal reasoning stays"). The
rest of ADR-0009 stands, including the clause this decision follows from: **"The ledger
owns everything before a report exists; the generator owns everything after."** Refusal
reasoning still stays for tools that were *declined* — which is what that convention was
written for.

Six already-promoted rows were removed on acceptance: BMAD-METHOD, hermes-agent,
Conductor, pilot-shell, spec-kitty, haft. They are present through commit `10fcb78`.

## Why

Owner observation (2026-08-26): the file was neither one thing nor the other. Read as a
history of every tool assessed it was radically incomplete — 6 of 45 reports had ever
been ledger rows, because the other 39 were ingested before the ledger existed or without
a sighting step. Read as a backlog it was polluted, six closed rows interleaved with
thirteen open ones and no way to tell them apart without reading to the end of each cell.

The ambiguity was internal to a single ADR-0009 paragraph: the ownership sentence says the
ledger stops owning a tool the moment a report exists, and the sentence after it keeps the
row anyway.

The competing option — make it the complete list of every tool analysed — is already
served, and by a generator: `comparisons/tools.md` lists every tool with a report, built
from frontmatter. Hand-keeping a second copy would violate methodology rule 3, and
back-filling the 39 missing tools would mean writing dated sightings that never happened,
the opposite of what a ledger row is ("primary dated observations, miniature decision
records").

## What the removal cost, checked before doing it

Each of the six rows was diffed against its report before deletion. **Every load-bearing
fact was already restated in the report** — which is itself the evidence the rows had
become duplication:

- pilot-shell's EULA finding → `pilot-shell.md` frontmatter and § licensing
  ("internal use and modification permitted per §2(c)").
- haft's licence discrepancy → `haft.md` frontmatter ("LICENSE file is plain MIT; GitHub
  API reports NOASSERTION").
- spec-kitty's imported spec-kit history → `spec-kitty.md` (commit count "imported history
  included").
- Conductor's plugin-distribution and SDD-set claims → `conductor.md`.
- hermes-agent's category question → `hermes-agent.md` ("category 2 confirmed").
- BMAD's prediction → `bmad-method.md` scores it explicitly in two places.

One traceability detail: `bmad-method.md` cites the ledger by quoting it — *"The ledger
predicted 'role-playing agent teams.'"* That citation now points at a removed row, so the
prediction is preserved verbatim here, in an immutable record: **"its predicted profile
(role-playing agent teams, process-gates-heavy) is the mechanism column exp-01 measured
near zero"**, entered 2026-08-18, scored the same day as half-falsified (build-first
entry, ceremony being shed) and half-confirmed (every framework gate prose — enforcement
sold separately in bmad-loop).

## Boundary

No paths, names, or numbers changed, so there is **no decoder**. Material dated on or
before 2026-08-26 may cite ledger rows for the six tools above; those rows were real, and
are in git history at `10fcb78` and earlier. The ledger header now states the exit rule so
the next promotion does not have to rediscover it.
