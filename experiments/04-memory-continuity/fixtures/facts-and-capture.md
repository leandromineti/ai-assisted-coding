# Planted facts + capture script (committed before any run — rule 5a)

Ten facts, established conversationally in harness A, never written to workspace
files. Middle-turn placement is deliberate: ai-memory's baton carries first + last
prompt + tool names, so an honest floor test requires facts in turns 2–5 only.
The workspace code CONTRADICTS C3 (parseRange throws today) and CONTAINS the T1 bug
behavior (2..2 → empty) — but the quiz asks for the non-derivable halves (the
decision; the reporter).

| # | Fact (verbatim, as spoken in capture) | Turn |
|---|---|---|
| D1 | For the 2.0 release we target Deno first, not Node | 2 |
| D2 | Share-link ids use Crockford base32, because of case-insensitive filesystems | 2 |
| C3 | parseRange must never throw on user input in 2.0 — return null instead (today it throws; that changes) | 2 |
| D3 | We vendor the date parser for the changelog tooling instead of depending on luxon | 3 |
| C1 | Never bump the planned schemaVersion field without adding a migration note to MIGRATIONS.md | 3 |
| P1 | I prefer table-driven tests over one-assertion-per-test | 3 |
| D4 | The 2.0 branch gets cut on September 12 | 4 |
| C2 | CI budget caps total test runtime at 90 seconds | 4 |
| P2 | Commit messages: conventional-commit prefixes with a scope, like fix(parser): | 4 |
| T1 | The open parseRange('2..2') empty-range bug was reported by the Fastly team; fix promised for 2.0.x | 5 |

## Capture turns (exact prompts; driver feeds them via `claude -p` / `--continue`)

1. "Let's work on rangekit today. Look at the project structure and summarize what's
   here in two sentences. Don't change any files."
2. "Before we plan anything, three decisions from our offline discussion — just
   acknowledge briefly, and do NOT write them into any file: for the 2.0 release we
   target Deno first, not Node. Share-link ids will use Crockford base32 because of
   case-insensitive filesystems. And parseRange must never throw on user input in
   2.0 — it will return null instead of throwing like it does today."
3. "Three more, same deal — acknowledge, don't write them anywhere: we vendor the
   date parser for the changelog tooling instead of depending on luxon. Never bump
   the planned schemaVersion field without adding a migration note to MIGRATIONS.md.
   And I prefer table-driven tests over one-assertion-per-test."
4. "Last batch — acknowledge only: the 2.0 branch gets cut on September 12. CI
   budget caps total test runtime at 90 seconds. Commit messages use
   conventional-commit prefixes with a scope, like fix(parser):."
5. "One open item to remember: the parseRange('2..2') empty-range bug — the one the
   Fastly team reported — is still unfixed; we promised them a fix in 2.0.x. Just
   acknowledge it."
6. "Good, wrapping up for today. Nothing to change in the files. See you next
   session."

## Post-capture fixture check (5d strengthener)

After the capture session, grep the workspace for fact tokens
(deno, base32, crockford, luxon, schemaversion, migration, september, fastly,
table-driven, "90 seconds"). Any hit = fixture broken → stop, rebuild, re-run
calibration.
