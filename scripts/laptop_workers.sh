#!/bin/bash
# Two extra search workers on Alejandro's laptop (the Claude desktop app's Linux workspace).
# They run a snapshot of the code in ~/pp-code with their own archive in ~/pp-state (PP_STATE), so syncing the
# Desktop clone never conflicts with them. Every 10-minute cycle: the laptop archive takes in the main archive's
# improvements (engine.py harvest), and the laptop's own improvements go to the main archive (scripts/remote.py).
# Start: nohup setsid ~/pp-code/scripts/laptop_workers.sh > ~/pp-code/logs/laptop.out 2>&1 &
# Stop:  touch ~/pp-state/STOP
cd "$(dirname "$0")/.."
export PP_STATE=${PP_STATE:-$HOME/pp-state}
mkdir -p "$PP_STATE" logs
rm -f "$PP_STATE/STOP"
w() { while [ ! -f "$PP_STATE/STOP" ]; do nice -n 5 python3 scripts/engine.py work "L$1" >> "logs/workerL$1.out" 2>&1; sleep 10; done; }
echo "$(date) laptop workers started (pid $$)"
w 0 & w 1 & wait
