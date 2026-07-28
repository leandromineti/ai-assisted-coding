#!/usr/bin/env bash
# Head-to-head: run both gitwho implementations against identical scenarios.
# Preregistered cases (README.md) + the pitfall cases surfaced during run B.
# Usage: ./compare.sh <plain_gitwho.py> <gsd_gitwho.py>
set -u
PLAIN="$1"; GSD="$2"
PASS_A=0; PASS_B=0; N=0

check() { # name, expected_exit, impl, args...
  local name="$1" want="$2" impl="$3"; shift 3
  local out rc
  out=$(python3 "$impl" "$@" 2>&1); rc=$?
  if [ "$rc" = "$want" ]; then echo "  ok   [$name] exit=$rc"; return 0
  else echo "  FAIL [$name] exit=$rc want=$want :: $(echo "$out" | head -1)"; return 1; fi
}

fixture() { # builds one repo exercising: binary file, merge commit, rename, unicode author
  local d; d=$(mktemp -d /tmp/gw-cmp.XXXXXX)
  git -C "$d" init -q -b main
  git -C "$d" -c user.name=Alice -c user.email=a@x commit -q --allow-empty -m root
  printf 'l1\nl2\nl3\n' > "$d/a.txt"
  git -C "$d" add -A && git -C "$d" -c user.name=Alice -c user.email=a@x commit -q -m text
  printf '\x00\x01\x02' > "$d/bin.dat"
  git -C "$d" add -A && git -C "$d" -c user.name=Bob -c user.email=b@x commit -q -m binary
  git -C "$d" mv a.txt b.txt && git -C "$d" -c user.name=Bob -c user.email=b@x commit -q -m rename
  git -C "$d" checkout -q -b side && printf 'x\n' > "$d/side.txt"
  git -C "$d" add -A && git -C "$d" -c user.name=Carol -c user.email=c@x commit -q -m side
  git -C "$d" checkout -q main
  git -C "$d" -c user.name=Alice -c user.email=a@x merge -q --no-ff -m merge side
  git -C "$d" -c user.name=Zoé -c user.email=z@x commit -q --allow-empty -m unicode
  echo "$d"
}

run_suite() { # impl label
  local impl="$1" label="$2" score=0
  echo "== $label =="
  local repo; repo=$(fixture)
  local plain_dir; plain_dir=$(mktemp -d /tmp/gw-cmp.XXXXXX)
  local empty_repo; empty_repo=$(mktemp -d /tmp/gw-cmp.XXXXXX); git -C "$empty_repo" init -q

  check "normal repo table" 0 "$impl" "$repo" && score=$((score+1))
  check "--json valid" 0 "$impl" "$repo" --json && python3 "$impl" "$repo" --json 2>/dev/null | python3 -c "import sys,json;json.load(sys.stdin)" 2>/dev/null && score=$((score+1))
  check "--since filter" 0 "$impl" "$repo" --since 2020-01-01 && score=$((score+1))
  check "not-a-repo exit 2" 2 "$impl" "$plain_dir" && score=$((score+1))
  check "empty repo nonzero" 1 "$impl" "$empty_repo" || python3 "$impl" "$empty_repo" >/dev/null 2>&1; [ $? -ne 0 ] && score=$((score+1))
  # pitfall cases: crash = fail
  python3 "$impl" "$repo" >/dev/null 2>&1 && echo "  ok   [binary+merge+rename+unicode no crash]" && score=$((score+1)) || echo "  FAIL [pitfall cases crashed]"
  # merge policy: merge commit counted for Alice (4 commits incl. merge)
  # schema-agnostic: accepts dict-of-authors (run A) or list-of-objects (run B)
  local alice; alice=$(python3 "$impl" "$repo" --json 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
rows=list(d.values()) if isinstance(d,dict) else d
names=list(d.keys()) if isinstance(d,dict) else [r.get('name','') for r in d]
a=[r for n,r in zip(names,rows) if 'Alice' in n]
print(a[0]['commits'] if a else 0)" 2>/dev/null)
  if [ "$alice" = "4" ]; then echo "  ok   [merge counted: Alice=4]"; score=$((score+1)); else echo "  warn [Alice commits=$alice, expected 4 incl merge]"; fi
  echo "  score: $score/7"
  echo "$score"
}

echo "gitwho head-to-head — $(date -u +%FT%TZ)"
A=$(run_suite "$PLAIN" "RUN A (plain)" | tee /dev/stderr | tail -1)
B=$(run_suite "$GSD" "RUN B (gsd)" | tee /dev/stderr | tail -1)
echo "FINAL: plain=$A/7  gsd=$B/7"
