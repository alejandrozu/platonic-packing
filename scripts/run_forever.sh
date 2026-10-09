#!/bin/bash
# Unattended search. Starts two engine workers (each restarted if it ever exits) and a publisher that rebuilds the
# records, tables, PROGRESS.md and the site, commits and pushes to GitHub every 90 minutes.
# Start:  nohup setsid scripts/run_forever.sh > logs/supervisor.out 2>&1 &
# Stop:   touch state/STOP   (workers finish their current attempt; the publisher exits at its next check)
# Resume after a machine loss: git clone the repo, then run the start command (state/best is in git).
cd "$(dirname "$0")/.."
mkdir -p logs state
rm -f state/STOP
[ -d state/best ] || python3 scripts/engine.py seed >> logs/seed.log 2>&1
worker() {
  while [ ! -f state/STOP ]; do
    python3 scripts/engine.py work "$1" >> "logs/worker$1.out" 2>&1
    echo "$(date) worker $1 exited ($?)" >> logs/supervisor.out; sleep 10
  done
}
publisher() {
  sleep "${FIRST_PUBLISH:-1800}"
  while [ ! -f state/STOP ]; do
    nice -n 10 python3 scripts/publish.py >> logs/publish.out 2>&1
    for i in $(seq 1 540); do [ -f state/STOP ] && break; sleep 10; done
  done
}
echo "$(date) supervisor started (pid $$)" >> logs/supervisor.out
worker 0 & worker 1 & publisher &
wait
