#!/bin/sh
# wait for any running queue to finish, then run the given queue
cd "$(dirname "$0")/.."
while pgrep -f "runqueue.sh runs_queue" > /dev/null; do sleep 30; done
exec scripts/runqueue.sh "$1" "$2"
