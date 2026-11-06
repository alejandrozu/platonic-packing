#!/usr/bin/env python3
"""One-piece problems behind n = 2 lower bounds (6 Nov 2026).

s1(P, C):       smallest scale s with a congruent copy of P inside s C (the n = 1 problem).
s_avoid(P, C, c): smallest s with a copy of P inside s C whose interior misses the point c. If every copy at a
                smaller scale contains c, no two copies fit (common-point lemma), so s(2) >= s_avoid.
For a fixed rotation both are linear programs in (translation, s); the rotation is searched by multistart
Nelder-Mead. Numerical only: an upper estimate of the true minimum over rotations.

    python3 scripts/optimality/one_piece.py PROBLEM [--starts 200]
"""
import json, os, sys
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))


def hrep(V):
    H = ConvexHull(V); eq = np.unique(np.round(H.equations, 12), axis=0)
    return eq[:, :3], -eq[:, 3]                                       # n.x <= h


def lp_fit(Vr, Nc, hc, avoid=None):
    """min s: Vr + t inside s C (Nc.x <= s hc); avoid=(Np_rot, hp, c, j): c beyond facet j of the placed piece."""
    m = len(Nc); A, b = [], []
    for v in Vr:
        for f in range(m): A.append([*Nc[f], -hc[f]]); b.append(-Nc[f] @ v)
    if avoid is not None:
        Npr, hp, c, j = avoid                                         # placed facet j: Npr[j].(x - t) <= hp[j]
        A.append([*Npr[j], 0.0]); b.append(Npr[j] @ c - hp[j])       # Npr[j].(c - t) >= hp[j]
    r = linprog([0, 0, 0, 1], A_ub=np.array(A), b_ub=np.array(b), bounds=[(None, None)] * 3 + [(0, None)],
                method='highs')
    return r.fun if r.status == 0 else np.inf


def solve(piece, cont, c=None, starts=200, seed=0):
    Vp = np.array(S[piece]['V'], float); Vc = np.array(S[cont]['V'], float)
    Np, hp = hrep(Vp); Nc, hc = hrep(Vc)
    rng = np.random.default_rng(seed); best = (np.inf, None, None)
    js = [None] if c is None else range(len(Np))
    def f(rv, j):
        R = Rotation.from_rotvec(rv).as_matrix(); Vr = Vp @ R.T
        return lp_fit(Vr, Nc, hc, None if j is None else (Np @ R.T, hp, c, j))
    for j in js:
        for k in range(starts):
            rv = Rotation.random(random_state=rng.integers(1 << 30)).as_rotvec()
            r = minimize(f, rv, args=(j,), method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 4000})
            if r.fun < best[0]: best = (r.fun, r.x, j)
    return best


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import csv
    prob = sys.argv[1]; starts = int(sys.argv[sys.argv.index('--starts') + 1]) if '--starts' in sys.argv else 60
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv')))) + \
           list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY_families.csv'))))
    r2 = [r for r in rows if r['problem'] == prob and r['n'] == '2'][0]
    piece, cont = r2['piece'], r2['container']
    s1 = solve(piece, cont, starts=starts)[0]
    sa = solve(piece, cont, c=np.zeros(3), starts=max(4, starts // 6))[0]
    print(f'{prob}: s1 {s1:.9f}  s_avoid(centre) {sa:.9f}  record s(2) {float(r2["s_tight"]):.9f}')
