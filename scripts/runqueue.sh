#!/bin/sh
# usage: scripts/runqueue.sh <queue file> <log>  — runs every line "piece container n seedFrom seedTo budget mode" with 2 workers
cd "$(dirname "$0")/.."
cat "$1" | xargs -P 2 -L 1 sh -c 'node scripts/batch.js $0 $1 $2 $3 $4 $5 $6 2>>logs/batch_err.log' > "$2" 2>&1
