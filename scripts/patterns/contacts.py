#!/usr/bin/env python3
"""Contact graphs of the 3D records (6 Nov 2026).

For each published record (n <= NMAX): pair contacts (max-margin separating plane with |u|_inf <= 1 has margin
below DELTA), wall contacts (a container facet within DELTA of a piece), rattlers (pieces with no contact at
all), coordination and the excess  c - (6n + 1)  over the degrees of freedom of the scale problem.
Records carry a 1e-7 clearance, so contacts sit at about 1e-7 and DELTA = 1e-5 separates them from gaps.

    python3 scripts/patterns/contacts.py [NMAX]          # writes docs/patterns/contacts3d.json
"""
import csv, json, os, sys
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
DELTA = 1e-5


def hrep(V):
    H = ConvexHull(V); eq = np.unique(np.round(H.equations, 12), axis=0)
    return eq[:, :3], -eq[:, 3]


def margin(A, B):
    """max t: u.a + t <= c <= u.b - t for all a in A, b in B, |u|_inf <= 1 (t < 0 if they overlap)."""
    nA, nB = len(A), len(B)
    # variables u(3), c, t ; maximize t
    Aub = np.vstack([np.hstack([A, -np.ones((nA, 1)), np.ones((nA, 1))]),
                     np.hstack([-B, np.ones((nB, 1)), np.ones((nB, 1))])])
    r = linprog([0, 0, 0, 0, -1], A_ub=Aub, b_ub=np.zeros(nA + nB), bounds=[(-1, 1)] * 3 + [(None, None), (None, 1)],
                method='highs')
    return -r.fun if r.status == 0 else -1.0


def analyse(path):
    d = json.load(open(path)); n = int(d['n'])
    piece, cont = d['piece'], d['container']
    if piece not in S or cont not in S: return None
    Vp = np.array(S[piece]['V'], float); Vc = np.array(S[cont]['V'], float)
    Nc, hc = hrep(Vc); s = float(d['s_full']); cen = np.array(d.get('container_center') or [0, 0, 0], float)
    W = []
    for q in d['pieces']:
        R = Rotation.from_quat([q[4], q[5], q[6], q[3]]).as_matrix()
        W.append(Vp @ R.T + np.array(q[:3]) - cen)
    rp = float(np.max(np.linalg.norm(Vp, axis=1)))
    ctr = np.array([w.mean(0) for w in W])
    pairs, deg, walls = [], np.zeros(n, int), np.zeros(n, int)
    for i in range(n):
        slack = s * hc - (W[i] @ Nc.T).max(0)
        walls[i] = int((slack < DELTA).sum())
        for j in range(i + 1, n):
            if np.linalg.norm(ctr[i] - ctr[j]) > 2 * rp + 1e-6: continue
            if margin(W[i], W[j]) < DELTA:
                pairs.append((i, j)); deg[i] += 1; deg[j] += 1
    rattlers = [i for i in range(n) if deg[i] == 0 and walls[i] == 0]
    c = len(pairs) + int(walls.sum())
    return {'record_id': d['record_id'], 'n': n, 'pair_contacts': len(pairs), 'wall_contacts': int(walls.sum()),
            'contacts': c, 'excess': c - (6 * n + 1), 'rattlers': len(rattlers), 'max_degree': int(deg.max()) if n else 0,
            'pairs': pairs}


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv')))) + \
           list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY_families.csv'))))
    files = [os.path.join(ROOT, r['file']) for r in rows if 2 <= int(r['n']) <= nmax]
    with Pool(2) as pool:
        res = [x for x in pool.imap_unordered(analyse, files, chunksize=4) if x]
    res.sort(key=lambda x: x['record_id'])
    json.dump(res, open(os.path.join(ROOT, 'docs', 'patterns', 'contacts3d.json'), 'w'))
    print(len(res), 'records;', sum(r['rattlers'] > 0 for r in res), 'with rattlers')


if __name__ == '__main__':
    main()
