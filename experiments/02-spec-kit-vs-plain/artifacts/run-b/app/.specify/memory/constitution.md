<!--
Sync Impact Report
==================
Version change: TEMPLATE → 1.0.0 (initial ratification)
Modified principles: n/a (first fill of template placeholders)
Added sections:
  - I. Code Quality
  - II. Testing Standards (NON-NEGOTIABLE)
  - III. User Experience Consistency
  - IV. Clear Error Behavior
  - Quality Gates (Section 2)
  - Governance
Removed sections: Principle 5 slot (not needed; user requested exactly four focus areas)
Templates requiring follow-up:
  - .specify/templates/plan-template.md — ⚠ pending manual review to confirm Constitution
    Check gates reference these four principles by name
  - .specify/templates/spec-template.md — ⚠ pending manual review for consistency
  - .specify/templates/tasks-template.md — ⚠ pending manual review for consistency
Deferred placeholders:
  - TODO(PROJECT_NAME): no project name found in repo (no README, package.json, or git
    remote present at ratification time). Replace once the project is named.
-->

# TODO(PROJECT_NAME) Constitution

## Core Principles

### I. Code Quality

Code MUST be kept readable, minimal, and consistent as the project grows from its current
scaffold state. Specifically:

- All code MUST pass linting/static analysis with zero unaddressed warnings; suppressions
  MUST include an inline comment explaining why.
- Every function or module MUST have a single, clear responsibility. Duplication MUST NOT be
  abstracted preemptively — extract shared logic only once a third real occurrence appears.
- Every non-trivial change MUST be reviewed (self-review against a checklist is acceptable
  for solo work) before it is considered done.
- Public interfaces (functions, APIs, CLI commands) MUST document their purpose, inputs,
  outputs, and error conditions at the point of definition.

**Rationale**: This project starts from an empty scaffold; the habits established now
determine whether the codebase stays maintainable as features accumulate. Consistent,
reviewed, minimal code prevents the drift and duplication that make later changes riskier.

### II. Testing Standards (NON-NEGOTIABLE)

- Every feature MUST have automated tests covering its primary behavior and its edge cases
  before it is marked complete.
- Bug fixes MUST include a regression test that reproduces the failure before the fix is
  applied and passes after.
- The full automated test suite MUST run on every change; a change MUST NOT merge while any
  test is failing.
- Tests MUST be deterministic; flaky tests MUST be fixed or removed, never ignored in place.

**Rationale**: Untested behavior is unverified behavior. Enforcing tests before completion
and blocking merges on failures keeps regressions from reaching users, and prevents "we'll
add tests later" from becoming permanent.

### III. User Experience Consistency

- User-facing surfaces (CLI output, API responses, UI copy, error text) MUST share one
  consistent voice, terminology, and formatting convention across the entire project.
- Naming of commands, flags, fields, and messages MUST match existing established patterns;
  introducing a new pattern requires explicit justification recorded in the change.
- Changes that alter user-facing behavior MUST be documented and, where the project has a
  versioning scheme, gated behind an appropriate version boundary.

**Rationale**: Inconsistent naming, tone, or output formatting compounds over time into a
confusing product. Deciding this early keeps every future feature aligned with the same
mental model for users.

### IV. Clear Error Behavior

- Failures MUST be surfaced immediately and explicitly. Errors MUST NOT be silently
  swallowed, retried without bound, or masked by fallback defaults that hide the underlying
  problem.
- Every error message MUST state what failed and why, and MUST state the corrective action
  when one is available to the user.
- User errors (invalid input) MUST be distinguished from system errors (internal failure);
  user-facing error messages MUST NOT leak internal implementation details (stack traces,
  internal paths, raw exception text) that aren't actionable for the user.
- Every distinct error path MUST be covered by a test asserting the expected error is raised
  and correctly reported.

**Rationale**: Clear, honest error behavior is what makes a system debuggable and
trustworthy. Swallowed or vague errors turn small bugs into long, expensive investigations
later.

## Quality Gates

Before any change is considered done, it MUST satisfy all of the following:

- Automated tests pass in full (Principle II).
- Linting/static analysis passes with no unexplained suppressions (Principle I).
- User-facing text and naming were checked against existing conventions (Principle III).
- New or changed error paths were reviewed for clarity and test coverage (Principle IV).

A change that cannot satisfy a gate MUST document why in the change description rather than
silently skipping it.

## Governance

This constitution supersedes all other informal practices for this project. Any conflict
between this document and other guidance (READMEs, comments, prior habits) is resolved in
favor of this constitution until the constitution itself is amended.

**Amendment procedure**: Amendments are proposed by editing this file, describing the
rationale for the change, and recording the version bump and date in the Sync Impact Report
at the top of the file. No separate approval body exists yet for this project; the person
merging the amendment is responsible for verifying the change is intentional and documented.

**Versioning policy**: This constitution follows semantic versioning:
- MAJOR: backward-incompatible removal or redefinition of a principle or governance rule.
- MINOR: a new principle or section is added, or existing guidance is materially expanded.
- PATCH: wording, typo, or clarification fixes with no semantic change.

**Compliance review**: Every non-trivial change MUST be checked against the Quality Gates
above before merge. Reviewers (self or peer) MUST flag any violation and either resolve it
or record an explicit, justified exception in the change description.

**Version**: 1.0.0 | **Ratified**: 2026-08-17 | **Last Amended**: 2026-08-17
