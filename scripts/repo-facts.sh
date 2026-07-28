#!/usr/bin/env bash
# Emit verified, frontmatter-ready facts about a cloned upstream tool.
#
#   ./scripts/repo-facts.sh opencode      # one tool
#   ./scripts/repo-facts.sh               # all tools in the manifest
#
# Nothing here should ever be typed by hand into a report — a hand-copied SHA
# goes stale silently and invalidates every claim in the document below it.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$root/upstream/repos.txt"

facts_for() {
  local name="$1"
  local dir="$root/upstream/$name"

  [[ -d "$dir/.git" ]] || { echo "not cloned: $name (run scripts/sync-upstream.sh)" >&2; return 1; }

  # Layer and URL come from the manifest so there is one source of truth.
  local layer url
  layer=$(awk -F'|' -v n="$name" '$2==n {print $1}' "$manifest" | head -1)
  url=$(awk -F'|' -v n="$name" '$2==n {print $3}' "$manifest" | head -1)

  echo "# --- $name ---"
  echo "name: $name"
  echo "layer: ${layer:-UNKNOWN}"
  echo "url: ${url:-UNKNOWN}"
  echo "version: $(git -C "$dir" describe --tags --always 2>/dev/null || echo unknown)"
  echo "commit: $(git -C "$dir" rev-parse --short HEAD)"
  echo "commit_date: $(git -C "$dir" log -1 --format=%ad --date=short)"
  echo "commits_total: $(git -C "$dir" rev-list --count HEAD)"
  echo "first_commit: $(git -C "$dir" log --reverse --format=%ad --date=short | head -1)"
  echo "tracked_files: $(git -C "$dir" ls-files | wc -l)"

  # Stars come from the GitHub API (needs `gh` auth); dated because they drift.
  local gh_slug
  gh_slug=$(sed -E 's#https?://github.com/##; s#/$##' <<<"${url:-}")
  if [[ "$gh_slug" =~ ^[^/]+/[^/]+$ ]]; then
    local stars
    stars=$(gh api "repos/$gh_slug" --jq .stargazers_count 2>/dev/null || echo "")
    if [[ -n "$stars" ]]; then
      echo "stars: $stars"
      echo "stars_at: $(date +%F)"
    else
      echo "stars: UNKNOWN (gh api failed — not authenticated?)"
    fi
  fi

  printf 'extensions:'
  git -C "$dir" ls-files \
    | sed -n 's/.*\.\([a-zA-Z0-9]\+\)$/\1/p' \
    | sort | uniq -c | sort -rn | head -6 \
    | awk '{printf " %s(%s)", $2, $1}'
  echo

  printf 'manifests:'
  git -C "$dir" ls-files \
    | grep -iE '(^|/)(package\.json|pyproject\.toml|Cargo\.toml|go\.mod|deno\.json)$' \
    | head -5 | awk '{printf " %s", $0}'
  echo

  printf 'arch_docs:'
  git -C "$dir" ls-files \
    | grep -iE '(^|/)(ARCHITECTURE|DESIGN|CONTRIBUTING)\.mdx?$' \
    | head -5 | awk '{printf " %s", $0}'
  echo

  echo "license: $(ls "$dir" | grep -iE '^(LICENSE|LICENCE|COPYING)' | head -1 || echo none)"
  echo
}

if [[ $# -gt 0 ]]; then
  for n in "$@"; do facts_for "$n"; done
else
  while IFS='|' read -r layer name _; do
    [[ -z "${layer// }" || "${layer:0:1}" == "#" ]] && continue
    facts_for "$name" || true
  done < "$manifest"
fi
