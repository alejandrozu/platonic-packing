#!/usr/bin/env python3
"""Cheap lower bounds for every 3D record against its certified value (6 Nov 2026).

For n = 2: the facet-width bound W_P / R_C (Lean: FacetWidth.centre_of_facet_width) and the two-ball bound (Lean:
BallBound). For every n: the volume bound and, through deletion, any proven smaller-n value. A record whose value
meets a bound is optimal once the construction is checked exactly; this script only finds the candidates.

    python3 scripts/optimality/scan_lower_bounds.py [--n 2]
"""
import csv, json, os, sys, itertools
import numpy as np
from scipy.spatial import HalfspaceIntersection, ConvexHull
from scipy.optimize import linprog
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))


def geom(name):
    V = np.array(S[name]['V'], float); V -= V.mean(0) * 0      # canonical solids are centred
    H = ConvexHull(V)
    eq = np.unique(np.round(H.equations, 10), axis=0)          # rows n.x + c <= 0, |n| = 1
    return V, eq


def facet_width(V, eq):
    return min(float(np.max(V @ -e[:3]) - np.min(V @ -e[:3])) for e in eq)


def inball(eq):
    """largest ball inside {n.x <= -c}: maximize r s.t. n.x + r <= -c."""
    A = np.hstack([eq[:, :3], np.ones((len(eq), 1))]); b = -eq[:, 3]
    r = linprog([0, 0, 0, -1], A_ub=A, b_ub=b, bounds=[(None, None)] * 3 + [(0, None)])
    return -r.fun


def diam_inner(eq, s, r):
    b = -eq[:, 3] * s - r                                       # n.x <= b
    if np.min(b) <= 1e-12: return 0.0
    hs = np.hstack([eq[:, :3], -b[:, None]])
    try: P = HalfspaceIntersection(hs, np.zeros(3)).intersections
    except Exception: return 0.0
    D = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    return float(D.max())


def two_ball(Vp, eqp, Vc, eqc):
    r = inball(eqp); lo, hi = 1e-6, 50.0
    for _ in range(80):
        m = (lo + hi) / 2
        if diam_inner(eqc, m, r) >= 2 * r: hi = m
        else: lo = m
    return hi


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv')))) + \
           list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY_families.csv'))))
    nsel = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 2
    cache, out = {}, []
    for r in rows:
        if int(r['n']) != nsel: continue
        p, c = r['piece'], r['container']
        if p not in S or c not in S: continue
        if p not in cache: cache[p] = geom(p)
        if c not in cache: cache[c] = geom(c)
        Vp, eqp = cache[p]; Vc, eqc = cache[c]
        rec = float(r['s_tight'])
        Rc = float(np.max(np.linalg.norm(Vc, axis=1)))
        fw = facet_width(Vp, eqp) / Rc
        tb = two_ball(Vp, eqp, Vc, eqc) if nsel == 2 else 0
        vb = float(r['volume_lower_bound'])
        best = max(fw, tb, vb)
        out.append((best / rec, r['record_id'], rec, fw, tb, vb))
    out.sort(reverse=True)
    for o in out[:60]:
        print(f'{o[0]:.6f} {o[1]:28s} rec {o[2]:.9f}  facetwidth {o[3]:.9f}  twoball {o[4]:.9f}  volume {o[5]:.6f}')


if __name__ == '__main__':
    main()
