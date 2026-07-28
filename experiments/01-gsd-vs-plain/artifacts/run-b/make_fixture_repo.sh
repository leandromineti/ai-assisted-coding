#!/usr/bin/env bash
# Build a deterministic fixture repository covering the four correctness
# traps gitwho must handle: a binary file, a merge commit, a rename, and a
# non-UTF-8 author name. Seven commits total. See
# .planning/phases/01-core-summary-command/01-01-PLAN.md Task 2 for the
# full recipe and the expected aggregate figures.
#
# Usage: make_fixture_repo.sh DEST

set -euo pipefail

DEST="${1:?usage: make_fixture_repo.sh DEST}"

rm -rf "$DEST"
git init -q -b main "$DEST"

COMMON_ARGS=(-c commit.gpgsign=false)

# Commit 1: Ann Adams adds a.txt (3 lines). Expected: 3 added, 0 deleted.
printf 'line one\nline two\nline three\n' > "$DEST/a.txt"
git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  add a.txt
GIT_AUTHOR_DATE="2024-01-01T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-01T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  commit -q -m "add a.txt"

# Commit 2: Ann Adams appends two lines to a.txt. Expected: 2 added, 0 deleted.
printf 'line four\nline five\n' >> "$DEST/a.txt"
git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  add a.txt
GIT_AUTHOR_DATE="2024-01-02T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-02T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  commit -q -m "extend a.txt"

# feature branch forks from here
git -C "$DEST" branch feature

# Commit 3: Bob Brown adds a binary file img.png (embedded NUL bytes).
# Expected numstat: "-" "-" (binary sentinel, DATA-02).
printf '\000\001\002\003' > "$DEST/img.png"
git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Bob Brown" -c user.email="bob@example.com" \
  add img.png
GIT_AUTHOR_DATE="2024-01-03T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-03T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Bob Brown" -c user.email="bob@example.com" \
  commit -q -m "add binary image"

# Commit 4: Ann Adams renames a.txt to renamed.txt. Under --no-renames this
# is a delete of a.txt (0 added, 5 deleted) plus an add of renamed.txt
# (5 added, 0 deleted) — never brace-expansion path syntax (DATA-03).
git -C "$DEST" mv a.txt renamed.txt
git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  add -A
GIT_AUTHOR_DATE="2024-01-04T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-04T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Ann Adams" -c user.email="ann@example.com" \
  commit -q -m "rename a.txt to renamed.txt"

# Commit 5: on feature branch, Bob Brown adds f.txt (1 line). Expected: 1 added, 0 deleted.
git -C "$DEST" checkout -q feature
printf 'feature line\n' > "$DEST/f.txt"
git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Bob Brown" -c user.email="bob@example.com" \
  add f.txt
GIT_AUTHOR_DATE="2024-01-05T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-05T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Bob Brown" -c user.email="bob@example.com" \
  commit -q -m "add f.txt on feature"

# Commit 6: back on main, Bob Brown merges feature. Merge commit emits a
# header with zero numstat lines (DATA-04).
git -C "$DEST" checkout -q main
GIT_AUTHOR_DATE="2024-01-06T00:00:00+0000" GIT_COMMITTER_DATE="2024-01-06T00:00:00+0000" \
  git -C "$DEST" "${COMMON_ARGS[@]}" -c user.name="Bob Brown" -c user.email="bob@example.com" \
  merge --no-ff --no-edit feature

# Commit 7: a raw commit object carrying a genuinely invalid UTF-8 byte in
# the author name — built without going through git's commit machinery
# (a normal `git commit --author` with an accented name does NOT reproduce
# the crash path; see 01-RESEARCH.md Common Pitfalls #4). This is the final
# step of the script — the index is intentionally left stale after this, so
# no further commits run after it.
TREE=$(git -C "$DEST" rev-parse "HEAD^{tree}")
PARENT=$(git -C "$DEST" rev-parse HEAD)
SHA=$(printf 'tree %s\nparent %s\nauthor Andr\351 Bad <bad@example.com> 1704585600 +0000\ncommitter Andr\351 Bad <bad@example.com> 1704585600 +0000\n\nnon-utf8 author commit\n' "$TREE" "$PARENT" \
  | git -C "$DEST" hash-object -t commit -w --stdin)
git -C "$DEST" update-ref refs/heads/main "$SHA"

echo "Fixture repository built at $DEST (7 commits)"
