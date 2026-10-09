#!/bin/bash
# Phase 1: same-solid problems (two tightening workers, split by problem) until their sweep (queue 3) is done,
#          then one final tighten + descend pass, records and site.
# Phase 2: mixed pairs + cube-in-cube: sweep (queue 4, two workers) with one tightening worker alongside,
#          records and site refreshed after every pass; final pass at the end.
cd "$(dirname "$0")/.."
XINX="tetintet octinoct icoinico dodindod"
MIXED=$(python3 -c "
A={'tetrahedron':'tet','cube':'cub','octahedron':'oct','dodecahedron':'dod','icosahedron':'ico'}
print(','.join(a+'in'+b for p,a in A.items() for c,b in A.items() if p!=c or p=='cube'))")
refresh() { flock logs/records.lock -c "python3 scripts/records.py $1 >> logs/records.log 2>&1; python3 scripts/site.py >> logs/records.log 2>&1"; }
half() {
  while pgrep -f "runqueue.sh runs_queue3" > /dev/null; do
    python3 scripts/pipeline.py tighten 2 $1 >> logs/upd_$2.log 2>&1
    python3 scripts/pipeline.py descend $1 >> logs/upd_$2.log 2>&1
    refresh "$(echo $1 | tr ',' ' ')"
    sleep 60
  done
  python3 scripts/pipeline.py tighten 2 $1 >> logs/upd_$2.log 2>&1
  python3 scripts/pipeline.py descend $1 >> logs/upd_$2.log 2>&1
}
half tetintet,octinoct A &
half icoinico,dodindod B &
wait
refresh "$XINX"
echo "PHASE 1 DONE $(date)" >> logs/orchestrate.log

scripts/runqueue.sh runs_queue4.txt logs/queue4.log &
sleep 600
while pgrep -f "runqueue.sh runs_queue4" > /dev/null; do
  python3 scripts/pipeline.py tighten 2 $MIXED >> logs/upd_M.log 2>&1
  python3 scripts/pipeline.py descend $MIXED >> logs/upd_M.log 2>&1
  refresh "$(echo $MIXED | tr ',' ' ')"
  sleep 120
done
python3 scripts/pipeline.py tighten 2 $MIXED >> logs/upd_M.log 2>&1
python3 scripts/pipeline.py descend $MIXED >> logs/upd_M.log 2>&1
refresh "$(echo $MIXED | tr ',' ' ')"
echo "PHASE 2 DONE $(date)" >> logs/orchestrate.log
