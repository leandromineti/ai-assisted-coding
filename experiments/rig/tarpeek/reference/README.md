# tarpeek — hardened reference implementation (INSTRUMENT APPARATUS)

**This is not a contestant.** It exists for exactly one purpose: the *fairness* leg of
exp-02 amendment 3's three-point instrument proof — every verifier check must be
passable by a correct-and-careful implementation before it may enter the set (the
SWE-bench-Verified lesson). It is never scored, never compared against an arm, and its
existence is disclosed in the experiment protocol.

## Behavior contract

Summarizes a tar archive without extracting it: per-member name, type
(file/dir/symlink/hardlink/device), size in bytes, last-modified date. `--min-size
BYTES` filters, `--json` emits machine-readable output. Sorted by size descending.
Never writes to the filesystem; symlink/hardlink targets are shown as metadata and
never resolved.

## Timezone

All dates are rendered in **UTC with an explicit `Z` suffix**, in both human and JSON
output. Output is therefore timezone-invariant: `TZ` has no effect.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | the path is not a tar archive |
| 3 | valid tar archive with zero members (empty) |
| 4 | corrupt or truncated archive (valid header, unreadable contents) |
| 5 | path unreadable / missing / not a regular file (directory, permission, symlink loop) |

## Escalation behaviors (2026-08-17)

Hardened for the amendment-3 escalation's candidate families, before screening:
path-level errors all land on exit 5 without a traceback (N1); with `--json`,
diagnostics go to stderr and stdout stays empty or valid JSON (N2); duplicate
member names are both listed — nothing is deduplicated (N3); `--min-size` that
filters every member out is success over an empty result, exit 0 (N4).
