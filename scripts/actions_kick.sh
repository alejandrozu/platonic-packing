#!/bin/bash
# Make sure the hourly GitHub Actions search runs: GitHub's cron trigger is best-effort (it can be late or skipped),
# so if no 'search' run was created in the last 55 minutes, start one (workflow_dispatch). Never more than one an hour.
cd "$(dirname "$0")/.."
if [ -f state/STOP ]; then echo "actions: stopped (state/STOP)"; exit 0; fi
age=$(timeout 30 gh api "repos/alejandrozu/platonic-packing/actions/runs?per_page=20" 2>/dev/null | python3 -c "
import json, sys, datetime
try: runs = [r for r in json.load(sys.stdin)['workflow_runs'] if r['name'] == 'search']
except Exception: print(-1); sys.exit()
if not runs: print(99999); sys.exit()
t = max(datetime.datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) for r in runs)
print(int((datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() // 60))")
if [ "$age" = "-1" ] || [ -z "$age" ]; then echo "actions: status unknown"; exit 0; fi
if [ "$age" -ge 55 ]; then
  timeout 30 gh api -X POST repos/alejandrozu/platonic-packing/actions/workflows/search.yml/dispatches -f ref=main > /dev/null 2>&1 && echo "actions: run started (last was ${age} min ago)" || echo "actions: start FAILED"
else echo "actions: last run ${age} min ago"; fi
