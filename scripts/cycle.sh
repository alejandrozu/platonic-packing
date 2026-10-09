#!/bin/bash
# The 10-minute cycle (run by Claude every 10 minutes while the session is kept active):
#  1. the supervisor and both workers are alive (restart if not); attempts advanced since the last cycle (else restart
#     the workers: a hung worker is killed and the supervisor starts a fresh one);
#  2. the archive invariants hold (monotone s(n), piece counts);
#  3. PROGRESS.md is regenerated from the live archive; the archive is committed and pushed to GitHub;
#  4. an incremental git bundle (last commit confirmed on the laptop .. HEAD) is written for the laptop copy.
# usage: scripts/cycle.sh [commit hash confirmed on the laptop by the previous cycle]
cd "$(dirname "$0")/.."
[ -n "$1" ] && echo "$1" > state/.device_synced
note=""
if ! pgrep -f run_forever.sh > /dev/null && [ ! -f state/STOP ]; then
  rm -rf state/claims
  FIRST_PUBLISH=900 nohup setsid scripts/run_forever.sh > logs/supervisor.out 2>&1 < /dev/null &
  sleep 5; note="$note SUPERVISOR-RESTARTED"
fi
a=$(wc -l < state/attempts.jsonl); i=$(grep -c '"improved": true' state/attempts.jsonl)
read pa pi pt < <(cat state/.cycle 2>/dev/null || echo "0 0 0")
now=$(date +%s)
if [ "$pt" -gt 0 ] && [ "$a" -eq "$pa" ] && [ $((now - pt)) -gt 480 ]; then
  pkill -f "^python3 scripts/engine.py work"; pkill -f "src/server.js"; note="$note NO-PROGRESS:workers-restarted"
fi
echo "$a $i $now" > state/.cycle
w=$(pgrep -c -f "^python3 scripts/engine.py work")
chk=$(python3 scripts/engine.py check 2>&1 | tail -1)
python3 -c "import sys; sys.path.insert(0, 'scripts'); import publish; publish.progress()" 2>/dev/null
exec 9> state/.gitlock; flock 9
git add state/best state/attempts.jsonl PROGRESS.md STATUS.md EXPERIMENT_LOG.md README.md docs scripts src test .gitignore 2>/dev/null
git diff --cached --quiet || git commit -q -m "Checkpoint: search archive $(date '+%Y-%m-%d %H:%M') ($a attempts)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015sjhNzKTinVQnSnofRcCoP"
if timeout 90 git push -q origin HEAD:main > /dev/null 2>&1; then push=pushed; else push=PUSH-FAILED; fi
flock -u 9
head=$(git rev-parse HEAD); from=$(cat state/.device_synced 2>/dev/null)
if [ "$from" != "$head" ]; then
  mkdir -p /mnt/user-data/outputs
  rm -f /mnt/user-data/outputs/sync-*.bundle
  bn=/mnt/user-data/outputs/sync-${head:0:12}.bundle          # unique name per cycle (the upload tool caches by path)
  git bundle create -q "$bn" "$from..main" 2>/dev/null || git bundle create -q "$bn" main
  laptop="LAPTOP-BUNDLE-READY $bn"
else laptop="laptop up to date"; fi
newb=$(python3 - "$pt" <<'PY'
import json, sys
t0 = int(sys.argv[1]); out = []
for l in open('state/attempts.jsonl'):
    try: a = json.loads(l)
    except Exception: continue
    if a['t'] > t0 and a['improved']: out.append(f"{a['p']}{a['n']}:{a['s']:.4f}")
print(' '.join(out[-12:]))
PY
)
echo "$(date +%H:%M) workers=$w attempts=$a (+$((a - pa))) new bests +$((i - pi)) [$newb] | $chk | github: $push | $laptop$note"
