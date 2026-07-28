#!/usr/bin/env bash
# Clone or update the upstream sources listed in upstream/repos.txt.
#
# Blobless clones (--filter=blob:none): full commit history and file listings,
# but file contents fetched on demand. Keeps `git log` and `git blame` usable
# for architecture archaeology without paying for every historical blob.
#
# Idempotent — safe to re-run. Existing clones are fast-forwarded.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$root/upstream/repos.txt"
dest="$root/upstream"

[[ -f "$manifest" ]] || { echo "missing manifest: $manifest" >&2; exit 1; }

while IFS='|' read -r layer name url; do
  [[ -z "${layer// }" || "${layer:0:1}" == "#" ]] && continue

  if [[ -d "$dest/$name/.git" ]]; then
    echo "== updating $name"
    git -C "$dest/$name" fetch --quiet --all --prune
    # Don't clobber a dirty tree or a detached exploration.
    if git -C "$dest/$name" diff --quiet && git -C "$dest/$name" diff --cached --quiet; then
      git -C "$dest/$name" pull --quiet --ff-only 2>/dev/null \
        || echo "   (not fast-forwardable — left as is)"
    else
      echo "   (local changes present — fetch only)"
    fi
  else
    echo "== cloning $name (layer $layer)"
    git clone --quiet --filter=blob:none "$url" "$dest/$name"
  fi
done < "$manifest"

echo
echo "-- disk usage --"
du -sh "$dest"/*/ 2>/dev/null | sort -h || true
