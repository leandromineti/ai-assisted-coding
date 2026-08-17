---
key: swebench-verified-2024
title: "Introducing SWE-bench Verified"
authors: [OpenAI, et al.]
year: 2024
venue: "OpenAI blog (with SWE-bench authors)"
peer_reviewed: false
url: https://openai.com/index/introducing-swe-bench-verified/
kind: benchmark
read_depth: abstract   # search-level summaries with specific figures; the post itself was not fetched
retrieved: 2026-08-17
bears_on: [exp-02, methodology-5d, issue-4]
verdict: "supplies the validity half issue #4's option 1 needs — an instrument must be screened for unfair items, not just hard ones: 68.3% of SWE-bench was filtered out, 61.1% for tests that rejected valid solutions"
---

# SWE-bench Verified

`retrieved: 2026-08-17` · `read_depth: abstract` · [openai.com](https://openai.com/index/introducing-swe-bench-verified/)

## What it does

Human-screens the SWE-bench test set for item validity: 93 experienced Python developers
annotated 1,699 sampled tasks for (a) underspecified problem statements and (b) unit
tests that unfairly reject valid solutions, producing a filtered 500-instance subset
plus per-item difficulty estimates.

## Numbers worth keeping (from search-level summaries — verify against the post before citing precisely)

- 38.3% of samples had underspecified problem statements.
- 61.1% had unit tests that could unfairly mark valid solutions incorrect.
- 68.3% of the original samples were filtered out overall.
- Severity labels 0–3 per criterion; 2–3 = discard. Annotators also estimated
  time-to-solve as a difficulty rating.

## What it means for this repo

The complement to the Aider recipe: baseline screening proves **headroom** (items the
baseline fails), but this proves **validity** (items a correct solution passes). exp-02's
trap set passed fails-closed proofs and still saturated — the reverse failure, an unfair
trap that no valid solution clears, is the one nobody has checked for yet, and SWE-bench's
61.1% figure says it is the *most common* defect in machine-checked instruments, not an
edge case. Any new trap set needs both screens: baseline-fails (headroom) AND
reference-solution-passes (fairness). Difficulty-as-time-estimate is also a cheap habit
worth copying into trap annotations.

## Limits

read_depth is abstract — the figures above came through search summaries and should be
re-verified against the post before appearing in any conclusion; corporate blog, not
peer-reviewed; the annotation cost (93 developers) is far beyond an n=1 experiment's
budget, so only the *criteria*, not the scale, transfer.
