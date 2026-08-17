---
key: aider-polyglot-2024
title: "o1 tops aider's new polyglot leaderboard (the polyglot benchmark construction post)"
authors: [Paul Gauthier]
year: 2024
venue: "aider.chat blog"
peer_reviewed: false
url: https://aider.chat/2024/12/21/polyglot.html
kind: benchmark
read_depth: extract   # WebFetch answered targeted construction-methodology questions against it; not read end to end
retrieved: 2026-08-17
bears_on: [exp-02, methodology-5d, issue-4]
verdict: "supplies the exact recipe issue #4's option 1 needs — select trap items empirically by baseline failure (kept problems solved by ≤3 of 7 baselines), and its saturation diagnosis matches exp-02's symptoms verbatim"
---

# Aider polyglot benchmark — construction post

`retrieved: 2026-08-17` · `read_depth: extract` · [aider.chat](https://aider.chat/2024/12/21/polyglot.html)

## What it does

Documents why aider retired its saturated 133-exercise Python benchmark and how the
replacement (225 exercises, 6 languages) was constructed to restore discrimination
between frontier models. A practitioner's saturation post-mortem plus a selection
methodology — the closest published analog to exp-02's instrument problem.

## Design

- **Saturation diagnosis** (symptoms, quoted): top score 84.2% = 112/133 solved, "leaving
  only 21 unsolved exercises"; "new champions were advancing the top score by solving
  just 1–2 more problems"; "models as old as GPT 3.5 Turbo were able to solve half of
  the 133 problems."
- **Selection method**: 7 baseline models (Sonnet, Haiku, o1-mini, DeepSeek, GPT-4o,
  Qwen-32B-Coder, GPT-4o-mini) ran all 697 Exercism problems across 6 languages; the new
  set keeps **the 225 problems solved by ≤3 of 7 baselines**. Note both exclusions: items
  solved by all (no headroom) *and* — implicitly, by the threshold band — a screen
  against items nothing solves (possibly broken/unfair).
- **Result**: top score recalibrated from ~84% to o1's 62% ("86 problems of headroom");
  design goal for frontier models to "occupy a wide range of scores between about 5%
  and 50%."

## Numbers worth keeping

- Old ceiling: 84.2% (112/133); GPT-3.5-Turbo-era models: ~50% of the old set.
- Screen: 697 candidates → 225 kept at threshold "solved by ≤3/7 baselines."
- New top score at launch: 62% (o1).

## What it means for this repo

This is issue #4's option 1 with an execution recipe: **build a candidate pool larger
than the final set, screen it empirically against baseline runs, keep only items the
baseline fails, and prove headroom by construction rather than by hope.** It also
retro-validates rule 5d (their calibration was 7 baselines × 697 items — screening *is*
calibration-first, multiplied) and matches the issue's post-mortem note that task size
and trap difficulty must be chosen together. Difference in scale to respect: they screen
with 7 models for a leaderboard; exp-02 is an n=1 A/B with one model, so the analogous
screen is multiple *runs* of the plain arm over the candidate pool.

## Limits

A blog post, not peer-reviewed; leaderboard context (many models, one axis) rather than
a two-arm experiment; no statistical treatment of the threshold choice (≤3/7 is a
judgment call, not derived); Exercism items are small and self-contained, unlike exp-02's
single larger task.
