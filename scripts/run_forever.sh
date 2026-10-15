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
  # 15 Oct 06:12 (Alejandro): all search on the higher polytopes (4D/5D/6D, scripts/engine_nd.py)
  while [ ! -f state/STOP ]; do
    python3 scripts/engine_nd.py work "c$1" >> "logs/worker_nd$1.out" 2>&1
    echo "$(date) worker $1 exited ($?)" >> logs/supervisor.out; sleep 10
  done
}
worker3d() {
  # 16 Oct (Alejandro: "keep all cores working"): a low-priority 3D worker on the Platonic problems takes whatever the
  # publisher leaves of the second core (it waits 5 minutes between publishes)
  while [ ! -f state/STOP ]; do
    PP_FAMILIES=platonic nice -n 15 python3 scripts/engine.py work "c3d$1" >> "logs/worker3d$1.out" 2>&1
    echo "$(date) 3D worker $1 exited ($?)" >> logs/supervisor.out; sleep 10
  done
}
publisher() {
  sleep "${FIRST_PUBLISH:-1800}"
  while [ ! -f state/STOP ]; do
    PP_PUBLISH_PROCS=2 nice -n 5 python3 scripts/publish.py >> logs/publish.out 2>&1
    for i in $(seq 1 30); do [ -f state/STOP ] && break; sleep 10; done    # 5 min between publishes since 15 Oct 08:30 (nD records keep coming)
  done
}
echo "$(date) supervisor started (pid $$)" >> logs/supervisor.out
worker 0 & worker3d 1 & publisher &     # 14 Oct 23:00: one search worker (Actions does the bulk), the other core certifies n <= 100
wait
