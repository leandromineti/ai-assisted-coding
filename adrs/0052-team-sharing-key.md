# ADR-0052 — team_sharing joins the memory_features block

`decided: 2026-09-04` · `status: accepted`

## Decision

`team_sharing` becomes the 15th key in the category-5 `memory_features:` block —
`group: store-scope`, `value_type: closed-enum`:

> can multiple humans read/write one store as designed behavior, and under which
> regime: `attribution-only` (single-tenant shared data — every authenticated user
> sees the same memories; writes attribute to named users; no access control) |
> `acl` (per-container grants — sharing is an explicit permission a holder extends
> to another principal)

Explicitly NOT this fact, each already on the record as something else:

- **multi-agent isolation** — per-agent ownership columns and boundaries
  (memos' `owner_*` schema) keep agents apart; this key asks how humans come together;
- **multi-operator auth alone** — login machinery without a designed shared surface
  is deployment posture, already carried by `deployment_mode` cell comments;
- **vendor-format interchange** — tool-to-tool portability is `memory_import` and the
  standards watch note, a different axis.

## The two-instance trigger

Unlike ADR-0051's graduation of a watched single-instance fact, this key was
probed into existence: the owner's own stack decision (2026-09-04) asked a question
the vocabulary could not express — *can a team of developers share one memory
store?* — and a record sweep found the reports silent: the closest passages
(ai-memory's multi-user auth, memos' `share_scope` columns) were all glossed as
isolation. A targeted probe-pass at the existing pins then found the fact itself
present in two artifacts, in **opposite postures**:

1. **ai-memory** @ 7e787c9 — `attribution-only`. `docs/users.md` (in-artifact,
   title "Multi-user attribution"): "single-tenant wiki data with optional
   multi-user attribution... Every authenticated request sees the same wiki
   pages — there is no per-page RBAC or group permission model"; the enable-it-when
   list names "a small team's homelab"; README carries a "Teams and multiple
   machines" section ("point every machine and every teammate at it"). RBAC is
   absent **by design** (`design-decisions.md` §13): attribution records *who*
   wrote, it does not gate *whether*. The one carve-out is operational: handoffs
   and open-session recovery are owner-scoped.
2. **cognee** @ b948f88d4 — `acl`. Source-verified at module level:
   one grant relation (`modules/users/models/ACL.py`, principal × permission ×
   dataset), `Principal` polymorphic over User/Role/Tenant, exactly four
   permission names in `permissions/permission_types.py` — `read`, `write`,
   `delete`, **`share`**, the meta-permission gating
   `authorized_give_permission_on_datasets.py`. Multi-tenant mode is the default
   (`ENABLE_BACKEND_ACCESS_CONTROL=true`); membership (`UserRole`/`UserTenant`)
   is separate from grants, so one tenant-held ACL row covers every member.

Merits check: the same underlying fact — a shipped mechanism for multiple human
identities on one store, with sharing as the designed behavior — not a rhyme.
And it discriminates *here*: the two instances answer the same question with
opposite trust postures (share-everything-and-attribute vs isolate-and-grant),
which is exactly the shape of finding the category's read-path keys
(`injection_trust_boundary`) record on the agent side. The security surface
also differs by value: under `attribution-only`, admission gates
(`write_admission`) are the *only* thing between one teammate's compromised
session and everyone's recall.

The other two read seeds settle ✗, keeping the enum honest:

- **mem0** @ 001c2352 — the OSS engine has no human-team construct
  (`user_id` is a query filter for the app's end-users); org/project/member
  constructs live only in the hosted-platform client (`mem0/client/main.py`,
  `client/project.py`). Platform-only, so ✗ with a cell comment — the
  tiers/decay precedent from its own deep-dive, reaffirmed by the owner for
  this key (2026-09-04).
- **memos** @ 85532420 — no human identity model in the local artifact;
  `ShareScope = "private" | "public" | "hub"`
  (`apps/memos-local-plugin/agent-contract/dto.ts:12`) is per-memory visibility
  toward the vendor cloud hub, not member management.

Stubs stay omitted (ADR-0051 precedent: cells only on read seeds).

## Argued and not admitted (with triggers)

- **A `team` value on `memory_scope` instead of a new key.** Rejected: `memory_scope`
  lists scoping *axes* the store supports; neither instance expresses team sharing as
  a scope value (ai-memory shares the whole tenant, cognee shares per-dataset via
  grants), so a list item would have flattened the one thing the two instances
  disagree about — the regime. The group blurb's uninstantiated "organisation"
  gloss on `memory_scope` is corrected in the same change: blast radius reads
  session · project · user, and the team question now has its own key.
- **A separate access-control/RBAC key.** Not while the enum carries it: the regime
  values already encode gate-vs-no-gate. Trigger: a third posture that the enum
  cannot name (e.g. role-scoped *memory visibility* rather than container grants).
- **Recording cross-user write attribution as its own key.** One instance
  (ai-memory); parked. Trigger: a second tool ships per-human attribution on a
  shared store.

## Consequences

- Registry entry in `docs/feature-taxonomy.yaml` (store-scope group; blurb extended,
  memory row count 23 → 24); registry and matrices regenerate.
- Cells set: ai-memory `attribution-only`, cognee `acl`, mem0 `false`, memos `false`.
  Stub reports unchanged.
- `tools/5-memory/README.md` "What we assess here" advances 14 → 15 keys and the
  category prose gains the opposite-postures finding.
- No decoder needed: no prior prose used another name for this fact — the sweep
  found the fact itself unrecorded, which is what prompted the key.
