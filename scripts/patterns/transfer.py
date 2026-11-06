#!/usr/bin/env python3
"""Transfer by inclusion (6 Nov 2026): the web of upper bounds that composition with a single piece gives.

If one copy of K fits in mu K' (mu = s1(K in K')), every packing of n copies of K' in s C gives n copies of K in
(mu s) C; if one copy of C' fits in lam C, n copies of K in s C' give n copies in (lam s) C. Both are
Packing.compose with m = 1 (Lean: Patterns.lean). For the 25 Platonic families this computes every such bound and
reports records it beats (new records) and records it matches (records explained by transfer).

    python3 scripts/patterns/transfer.py [--starts 40]      # writes docs/patterns/transfer.json
"""
import csv, json, os, sys, itertools
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'optimality'))
from one_piece import solve
PL = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico'}


def main():
    starts = int(sys.argv[sys.argv.index('--starts') + 1]) if '--starts' in sys.argv else 40
    out = os.path.join(ROOT, 'docs', 'patterns', 'transfer.json')
    data = json.load(open(out)) if os.path.exists(out) else {}
    mu = data.get('s1', {})
    for a, b in itertools.permutations(PL, 2):
        key = f'{AB[a]}in{AB[b]}'
        if key not in mu:
            mu[key] = float(solve(a, b, starts=starts)[0]); print(key, mu[key], flush=True)
            data['s1'] = mu; json.dump(data, open(out, 'w'), indent=1)
    for a in PL: mu[f'{AB[a]}in{AB[a]}'] = 1.0
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv'))))
    rec = {}
    for r in rows:
        if r['piece'] in PL and r['container'] in PL:
            rec[(AB[r['piece']], AB[r['container']], int(r['n']))] = float(r['s_tight'])
    beats, matches, best = [], [], {}
    for (k, c, n), s in rec.items():
        cands = []
        for k2 in AB.values():               # piece inclusion: K in mu K', packing of K' in C
            if k2 != k and (k2, c, n) in rec: cands.append((mu[f'{k}in{k2}'] * rec[(k2, c, n)], f'piece {k}<{k2}'))
        for c2 in AB.values():               # container inclusion: C' in lam C, packing of K in C'
            if c2 != c and (k, c2, n) in rec: cands.append((mu[f'{c2}in{c}'] * rec[(k, c2, n)], f'container {c2}<{c}'))
        if not cands: continue
        t, how = min(cands)
        best[f'{k}in{c}_n{n:02d}'] = {'record': s, 'transfer': t, 'via': how, 'ratio': t / s}
        if t < s - 1e-9: beats.append((f'{k}in{c}_n{n:02d}', s, t, how))
        elif t < s + 1e-7: matches.append((f'{k}in{c}_n{n:02d}', s, t, how))
    data.update(s1=mu, best=best, beats=beats, matches=matches,
                ratio_hist=np.histogram([v['ratio'] for v in best.values()], bins=[1, 1.01, 1.05, 1.1, 1.2, 1.5, 2, 3, 100])[0].tolist())
    json.dump(data, open(out, 'w'), indent=1)
    print('beats', len(beats), beats[:20]); print('matches', len(matches), matches[:20])
    print('ratio histogram', data['ratio_hist'])


if __name__ == '__main__':
    main()
