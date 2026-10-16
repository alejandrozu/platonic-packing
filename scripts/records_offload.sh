#!/bin/bash
# Platonic record certification on GitHub Actions when the main machine falls behind (16 Oct 2026). Called by cycle.sh:
#  - a finished records-platonic run not imported yet: download its artifacts and import the records
#    (scripts/import_records_batch.py: only records of the archive's current packings, certified);
#  - else, with no such run active and at least 200 Platonic records behind the archive: start one.
# Prints one line.
cd "$(dirname "$0")/.."
R=alejandrozu/platonic-packing; seen=state/.records_imported; touch "$seen"
last=$(timeout 30 gh run list -R $R -w records_platonic.yml -L 1 --json databaseId,status,conclusion -q '.[0] | "\(.databaseId) \(.status) \(.conclusion)"' 2>/dev/null)
id=${last%% *}; rest=${last#* }
if [ -n "$id" ] && [ "$rest" = "completed success" ] && ! grep -q "^$id$" "$seen"; then
  d=$(mktemp -d); timeout 300 gh run download "$id" -R $R -D "$d" > /dev/null 2>&1
  out=$(python3 -I scripts/import_records_batch.py "$d"/records-platonic-* 2>&1 | tail -1); rm -rf "$d"
  echo "$id" >> "$seen"; echo "records offload: run $id imported ($out)"; exit 0
fi
# a pause (state/ACTIONS_PAUSE, state/STOP) still imports a finished run but starts no new one
if [ -f state/STOP ] || [ -f state/ACTIONS_PAUSE ]; then echo "records offload: paused"; exit 0; fi
case "$rest" in queued*|in_progress*|waiting*|requested*|pending*) echo "records offload: run $id active"; exit 0;; esac
behind=$(timeout 300 python3 - <<'PY'
import sys, json, hashlib
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'src')
import engine as E
k = 0
for p in E.PID:
    if E.FAM[p] != 'platonic': continue
    for n in range(E.NMIN, E.NMAX + 1):
        c = E._read(E._path('best', p, n)); b = c and c.get('best')
        if not b: continue
        h = hashlib.sha1(json.dumps([round(b['s'], 13), b['C'], b['Q']]).encode()).hexdigest()[:16]
        try: r = json.load(open(f'records/{p}/{p}_n{n:02d}.json')); rh = (r.get('source') or {}).get('hash')
        except Exception: rh = None
        k += rh != h
print(k)
PY
)
if [ "${behind:-0}" -ge 200 ]; then
  timeout 30 gh api -X POST repos/$R/actions/workflows/records_platonic.yml/dispatches -f ref=main > /dev/null 2>&1 \
    && echo "records offload: $behind Platonic records behind, run started" || echo "records offload: start FAILED"
else echo "records offload: $behind Platonic records behind"; fi
