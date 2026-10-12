#!/usr/bin/env python3
"""Attempts and new bests in the archive log since a time: python3 scripts/window_stats.py T0 [T1]
Prints: cloud attempts, cloud new bests, harvested new bests by host (actions, laptop), per-family new bests."""
import json, sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from engine import FAM
t0 = float(sys.argv[1]); t1 = float(sys.argv[2]) if len(sys.argv) > 2 else 1e18
att = best = 0; hb = collections.Counter(); fam = collections.Counter(); cases = set()
for l in open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'state', 'attempts.jsonl')):
    try: a = json.loads(l)
    except Exception: continue
    if not (t0 < a['t'] <= t1): continue
    if a['move'] == 'harvest':
        if a.get('improved'): hb[a.get('host', 'remote')] += 1; fam[FAM.get(a['p'], '?')] += 1; cases.add((a['p'], a['n']))
        continue
    att += 1
    if a.get('improved'): best += 1; fam[FAM.get(a['p'], '?')] += 1; cases.add((a['p'], a['n']))
print(json.dumps({'cloud_attempts': att, 'cloud_bests': best, 'harvest_bests': dict(hb), 'by_family': dict(fam), 'cases_improved': len(cases)}))
