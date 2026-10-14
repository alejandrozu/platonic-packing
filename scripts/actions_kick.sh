#!/bin/bash
# Keep the GitHub Actions search running. Since 14 Oct 16:49 (Alejandro: mass production, 20 jobs instead of 4) a run
# is 20 jobs x MINUTES (300) on n <= 100, and a new run is started as soon as the previous one has finished (none
# queued or in progress). Before: one 4-job, 50-minute run an hour.
cd "$(dirname "$0")/.."
if [ -f state/STOP ]; then echo "actions: stopped (state/STOP)"; exit 0; fi
# state/ACTIONS_PAUSE pauses the search (its text says why)
if [ -f state/ACTIONS_PAUSE ]; then echo "actions: paused ($(head -c 80 state/ACTIONS_PAUSE))"; exit 0; fi
st=$(timeout 30 gh api "repos/alejandrozu/platonic-packing/actions/runs?per_page=30" 2>/dev/null | python3 -c "
import json, sys, datetime
try: runs = [r for r in json.load(sys.stdin)['workflow_runs'] if r['name'] == 'search']
except Exception: print('unknown'); sys.exit()
act = [r for r in runs if r['status'] in ('queued', 'in_progress', 'waiting', 'requested', 'pending')]
if act:
    t = min(datetime.datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) for r in act)
    print('running', int((datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() // 60)); sys.exit()
print('idle')")
case "$st" in
  running*) echo "actions: run in progress (${st#running } min)";;
  idle) timeout 30 gh api -X POST repos/alejandrozu/platonic-packing/actions/workflows/search.yml/dispatches -f ref=main -f 'inputs[minutes]=300' > /dev/null 2>&1 \
          && echo "actions: run started (20 jobs x 300 min)" || echo "actions: start FAILED";;
  *) echo "actions: status unknown";;
esac
