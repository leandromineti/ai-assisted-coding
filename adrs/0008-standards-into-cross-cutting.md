# ADR-0008 — Standards folded into cross-cutting

`decided: 2026-08-19` · status: **accepted**

## Decision

`notes/standards/` merges into `notes/cross-cutting/` as
[`standards.md`](../notes/cross-cutting/standards.md). The repo keeps **one**
non-layer bucket (cross-cutting) instead of two.

## Context

Standards ("specifications, not installable things") and cross-cutting concerns
("appear at several layers at once") are both ✕-marked non-layers in the taxonomy, and
the standards directory held a single file. The conceptual distinction survives the
merge: a standard is a cross-cutting concern whose subject is interoperability — the
spec lives in the note, its implementations live in the layers. The structural role is
unchanged: the standardization scoreboard still gates the extensions bucket's
re-promotion trigger ([ADR-0002](0002-extensions-demoted-to-bucket.md), ~2027-01
re-check).

## Consequences

Old public URLs to `notes/standards/index.md` 404 (repo public since 2026-08-18);
taxonomy's Standards section, README's structure table, and conclusion 3's link now
point at the new path. The taxonomy's "Layer indexes" table shows one ✕ row.
