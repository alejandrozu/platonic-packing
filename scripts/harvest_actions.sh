#!/bin/bash
# Merge the GitHub Actions search results (branches search-results-0..19, see .github/workflows/search.yml) into the
# archive. Each branch holds one export.txt (scripts/remote.py format); a branch commit is imported once.
cd "$(dirname "$0")/.."
timeout 60 git fetch -q origin '+refs/heads/search-results-*:refs/remotes/origin/search-results-*' 2>/dev/null || { echo "actions: fetch failed"; exit 0; }
seen=state/.actions_seen; touch "$seen"; tot=0; att=0; new=0; ndt=0
for ref in $(git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/search-results-*'); do
  c=$(git rev-parse "$ref"); grep -q "$c" "$seen" && continue
  echo "$c" >> "$seen"; new=$((new + 1))
  a=$(git show "$ref:meta.json" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('attempts', 0))" 2>/dev/null || echo 0)
  att=$((att + a))
  git show "$ref:export.txt" > /tmp/actions_export.txt 2>/dev/null || continue
  k=$(python3 scripts/remote.py import /tmp/actions_export.txt actions | grep -o 'harvest from actions: [0-9]*' | grep -o '[0-9]*$')
  tot=$((tot + ${k:-0}))
  # 4D/5D/6D results of the same job (15 Oct): engine_nd.py import re-legalizes every packing
  if git show "$ref:export_nd.txt" > /tmp/actions_export_nd.txt 2>/dev/null; then
    kn=$(python3 scripts/engine_nd.py import /tmp/actions_export_nd.txt "actions-j${ref##*-}" | grep -o 'nd harvest from actions-j[0-9]*: [0-9]*' | grep -o '[0-9]*$')
    ndt=$((ndt + ${kn:-0}))
  fi
done
[ "$new" -gt 0 ] && echo "{\"t\": $(date +%s), \"local\": \"$(date '+%Y-%m-%d %H:%M')\", \"jobs\": $new, \"attempts\": $att, \"merged\": $tot}" >> state/actions_log.jsonl
echo "actions: $new new job results, $att attempts, $tot improvements merged (+$ndt in 4D/5D/6D)"
