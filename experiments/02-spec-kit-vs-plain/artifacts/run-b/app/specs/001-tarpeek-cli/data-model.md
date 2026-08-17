# Phase 1 Data Model: Tarpeek CLI

## ArchiveMember

Represents a single entry recorded inside the tar archive, derived from one `tarfile.TarInfo`.

| Field           | Type              | Source / Derivation                                                                 | Validation / Rules |
|-----------------|-------------------|--------------------------------------------------------------------------------------|---------------------|
| `name`          | `str`             | `TarInfo.name` verbatim (archive-relative path)                                     | Non-empty; used as ascending secondary sort key. |
| `type`          | `str` enum        | `"dir"` if `isdir()`, `"symlink"` if `issym()`, `"file"` if `isfile()`, else `"other"` | Exactly one of `file`, `dir`, `symlink`, `other` (FR-003). Order of checks matters: dir/symlink checked before the generic file check. |
| `size`          | `int`             | `TarInfo.size` (bytes)                                                              | `>= 0`; primary sort key, descending. |
| `last_modified` | `str` (ISO 8601)  | `TarInfo.mtime` (epoch, UTC) → `YYYY-MM-DDTHH:MM:SSZ`                               | Always UTC, seconds precision, `Z` suffix (FR-004, FR-006). |

No relationships to other entities — each `ArchiveMember` is independent and self-contained.
No state transitions — members are read-only snapshots of archive metadata at inspection time.

## ArchiveSummary

The ordered collection of `ArchiveMember` produced for one invocation.

| Field     | Type                  | Derivation                                                                 |
|-----------|-----------------------|------------------------------------------------------------------------------|
| `members` | `list[ArchiveMember]` | All members of the archive, optionally filtered by `--min-size`, then sorted. |

**Construction rules**:
1. Read all members from the archive (`TarFile.getmembers()`), map each to an `ArchiveMember`.
2. If the archive has zero members at this point → empty-archive error condition (FR-010), raised
   before any filtering/sorting is attempted.
3. If `--min-size BYTES` was given, filter to members where `size >= BYTES`. This may legitimately
   produce zero members — that is a successful, non-error result (FR-011).
4. Sort remaining members by `(-size, name)` — i.e. size descending, then name ascending, so the
   sort is a single stable operation with no separate tie-break pass needed.

## Validation errors (input, not entity fields)

These aren't data-model fields but are validated at the same boundary as archive reading, per
Principle IV (user errors distinguished, clear corrective messages):

| Input               | Invalid when                                   | Reported as |
|----------------------|------------------------------------------------|-------------|
| `path` (positional)  | Does not exist                                 | "path not found" style error |
| `path` (positional)  | Exists but unreadable (permissions)            | "permission denied" style error, distinct from not-found |
| `path` (positional)  | Exists, readable, but not a valid tar archive  | "not a valid tar archive" style error, distinct from the above two |
| `--min-size`         | Non-numeric or negative                        | "invalid --min-size value" style error, rejected before opening the archive |

All four map to the same generic non-zero exit code (FR-011a) — only the message text
distinguishes the cause, per the spec's resolved clarification.
