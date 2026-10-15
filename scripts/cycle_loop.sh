#!/bin/bash
# The main machine's cycle, unattended (16 Oct 2026): scripts/cycle.sh every 6 minutes (harvest the Actions results,
# nested packings, contributions, checks, push to GitHub, start a run when none is active, restart the local workers).
# One summary line per cycle in logs/cycle.log. Stop: touch state/STOP.
# Start: nohup setsid scripts/cycle_loop.sh > /dev/null 2>&1 < /dev/null &
cd "$(dirname "$0")/.."
exec 8> state/.cycle_loop.lock
flock -n 8 || { echo "cycle loop already running"; exit 0; }
while [ ! -f state/STOP ]; do
  line=$(timeout 1500 scripts/cycle.sh 2>&1 | tail -1)
  echo "$line" >> logs/cycle.log
  for i in $(seq 1 36); do [ -f state/STOP ] && break; sleep 10; done
done
