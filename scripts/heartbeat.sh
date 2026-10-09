#!/bin/bash
# One-line health check; restarts the supervisor if it is gone. Used to keep the session (and machine) alive.
cd "$(dirname "$0")/.."
w=$(pgrep -c -f "^python3 scripts/engine.py work")
if ! pgrep -f run_forever.sh > /dev/null && [ ! -f state/STOP ]; then
  FIRST_PUBLISH=600 nohup setsid scripts/run_forever.sh > logs/supervisor.out 2>&1 < /dev/null & sleep 5; r=" RESTARTED"; fi
a=$(wc -l < state/attempts.jsonl); i=$(grep -c '"improved": true' state/attempts.jsonl)
e=$(grep -h ERROR logs/engine*.log 2>/dev/null | wc -l)
c=$(python3 scripts/engine.py check 2>&1 | tail -1)
p=$(grep "publish:\|git:" logs/publish.log | tail -2 | tr '\n' ' ')
echo "$(date +%H:%M) workers=$w attempts=$a improvements=$i errors=$e | $c | $p$r"
