#!/bin/sh
# keep records current while the X-in-X queue runs; one final pass after it ends
cd "$(dirname "$0")/.."
while pgrep -f "pipeline.py tighten 2 tetra" > /dev/null; do sleep 20; done
while pgrep -f "runqueue.sh runs_queue3" > /dev/null; do
  K=2 scripts/update.sh >> logs/update.log 2>&1
  sleep 300
done
K=3 scripts/update.sh >> logs/update.log 2>&1
echo "FINAL X-in-X PASS DONE $(date)" >> logs/update.log
