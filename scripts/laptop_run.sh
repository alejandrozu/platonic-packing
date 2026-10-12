#!/bin/bash
# One bounded run of the two laptop workers. The laptop workspace ends every background process when a command
# returns (at most ~3 minutes), so the workers run in back-to-back bounded runs: no new attempt after SECS seconds,
# hard stop 28 s later. Code: ~/pp-code (snapshot), archive: ~/pp-state. Afterwards the cases where the laptop
# beats the main archive (as last synced into the Desktop clone) are written to <clone>/.laptop/export-<time>.txt
# for the 10-minute cycle to import (scripts/remote.py import -> engine.py harvest).
# PP_FAST=1 (12 Oct): an attempt on a large case outlasts a bounded run, so the laptop skips the fill phase and
# brings the smallest cases toward min_attempts (fewest attempts first, then smallest n).
# usage: ~/pp-code/scripts/laptop_run.sh [SECS] [CLONE]
cd "$(dirname "$0")/.."
export PP_STATE=$HOME/pp-state
secs=${1:-140}; clone=${2:-$HOME/mnt/Desktop/platonic-packing}
export PP_DEADLINE=$(( $(date +%s) + secs ))
t0=$(date +%s); a0=$(wc -l < "$PP_STATE/attempts.jsonl" 2>/dev/null || echo 0)
mkdir -p logs
PP_FAST=1 PP_SHARD=2/8 timeout $((secs + 28)) nice -n 5 python3 scripts/engine.py work L0 >> logs/workerL0.out 2>&1 &
PP_FAST=1 PP_SHARD=3/8 timeout $((secs + 28)) nice -n 5 python3 scripts/engine.py work L1 >> logs/workerL1.out 2>&1 &
wait
a1=$(wc -l < "$PP_STATE/attempts.jsonl"); imp=$(tail -n $((a1 - a0)) "$PP_STATE/attempts.jsonl" | grep -c '"improved": true')
mkdir -p "$clone/.laptop"
out="$clone/.laptop/export-$(date +%s).txt"
python3 scripts/remote.py export "$PP_STATE" "$clone/state/best" > "$out"
echo "laptop run: $((a1 - a0)) attempts, $imp improvements in $(( $(date +%s) - t0 ))s; export $(cut -d' ' -f2 "$out") cases -> $(basename "$out")"
