#!/usr/bin/env python3
"""Coverage of the active families: cases with a packing, cases with >= min_attempts attempts (cloud archive's
statistics; remote attempts are not counted per case), per family."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
need = int(engine.policy().get('min_attempts', 10))
fams = {}
for p in engine.PID:
    f = engine.FAM[p]
    if f == 'platonic': continue
    d = fams.setdefault(f, [0, 0, 0])
    for n in range(engine.NMIN, engine.NMAX + 1):
        c = engine._read(engine._path('best', p, n)); d[2] += 1
        if c and c.get('best'):
            d[0] += 1
            if c['stats'].get('attempts', 0) >= need: d[1] += 1
tot = [sum(v[i] for v in fams.values()) for i in range(3)]
print(f"filled {tot[0]}/{tot[2]}, >={need} attempts {tot[1]}/{tot[2]} | " +
      ', '.join(f"{f} {v[0]}/{v[2]} ({v[1]} at {need}+)" for f, v in fams.items()))
