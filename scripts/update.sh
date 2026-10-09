#!/bin/sh
# tighten new runs, descend, rebuild records and the site for the given problem ids (default: the four X-in-X cases)
cd "$(dirname "$0")/.."
IDS=${1:-tetintet,octinoct,icoinico,dodindod}
python3 scripts/pipeline.py tighten ${K:-3} $IDS
python3 scripts/pipeline.py descend $IDS
python3 scripts/records.py $(echo $IDS | tr ',' ' ')
python3 scripts/site.py
