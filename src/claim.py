"""Turn a tightened packing (internal units, see exact.py) into a claim file with explicit clearance.

Unit-edge coordinates; container = s_full x canonical unit-edge container solid, centred at the origin.
Centres are spread apart about their mean until every pair is separated by at least GAP (SAT separation), the
container is fitted by an LP over translations with a wall gap of at least WALL on every face, and s_full is
rounded UP at the 13th decimal. Usage: python3 src/claim.py tightened.json out.json [GAP=1e-6] [WALL=1e-6]"""
import json, math, sys, os, itertools, datetime
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact import Problem, quat_to_R, R_to_quat, sat_gap, SOL

NAMES = {'tetrahedron': 'tetrahedra', 'cube': 'cubes', 'octahedron': 'octahedra', 'dodecahedron': 'dodecahedra', 'icosahedron': 'icosahedra'}


def make_claim(rec, GAP=1e-6, WALL=1e-6, meta=None):
    piece, container = rec['piece'], rec['container']
    pbi = Problem(piece, container)                       # internal units
    # unit-edge problem: same geometry divided by the internal edge
    Vu = np.array(SOL[piece]['V']); CN = np.array(SOL[container]['normals']); CV = np.array(SOL[container]['V'])
    beta = np.array([CN[f] @ CV[F[0]] for f, F in enumerate(SOL[container]['faces'])])
    C = np.array(rec['C']) / pbi.edge
    Q = [np.array(q) / np.linalg.norm(q) for q in rec['Q']]
    Q = [q if q[0] >= 0 else -q for q in Q]
    R = [quat_to_R(q) for q in Q]

    class U:  # minimal unit-edge problem object for sat_gap
        V = Vu; faxes = pbi.faxes; edirs = pbi.edirs; prune = False   # full axis set (no Gauss-map pruning)
        @staticmethod
        def verts(c, Rm): return c + Vu @ Rm.T
    lim = (2 * float(np.linalg.norm(Vu, axis=1).max())) ** 2 + 1e-9

    def min_gap(Cc):
        g = np.inf
        for i, j in itertools.combinations(range(len(Cc)), 2):
            if np.sum((Cc[i] - Cc[j]) ** 2) > lim: continue
            g = min(g, sat_gap(U, Cc[i], R[i], Cc[j], R[j])[0])
        return g
    cen = C.mean(0); lo = hi = 1.0
    while min_gap(cen + hi * (C - cen)) < GAP: hi = 1 + (hi - 1) * 2 if hi > 1 else 1 + 1e-9
    for _ in range(60):
        m = (lo + hi) / 2
        if min_gap(cen + m * (C - cen)) >= GAP: hi = m
        else: lo = m
    C2 = cen + hi * (C - cen)
    X = np.concatenate([C2[i] + Vu @ R[i].T for i in range(len(C2))])
    S = (X @ CN.T).max(0)
    res = linprog([0, 0, 0, 1], A_ub=np.hstack([CN, -beta[:, None]]), b_ub=-S, bounds=[(None, None)] * 4, method='highs')
    t = res.x[:3]; C2 = C2 + t
    X = np.concatenate([C2[i] + Vu @ R[i].T for i in range(len(C2))])
    s = math.ceil(float(((X @ CN.T).max(0) + WALL) .__truediv__(beta).max()) * 1e13) / 1e13
    wall = float((s * beta[None, :] - X @ CN.T).min())
    pg = min_gap(C2)
    claim = {
        'problem': f'min/{NAMES[piece]}_in_{container}', 'piece': piece, 'container': container, 'n': len(C2),
        's': math.floor(s * 1e5) / 1e5, 's_plus': f'{math.floor(s * 1e5) / 1e5:.5f}+', 's_full': s,
        'measure': 'edge length of the container divided by the edge length of the pieces',
        'clearance': {'min_pair_gap_target': GAP, 'wall_gap_target': WALL, 'min_pair_gap': pg, 'min_wall_gap': wall},
        'format': '[x, y, z, qw, qx, qy, qz] per piece: unit-edge copy of the canonical piece solid (solids.py) rotated by the '
                  'scalar-first quaternion q and centred at (x, y, z); container = s_full x canonical unit-edge container solid, '
                  'centred at the origin, canonical orientation',
        'method': 'soft-to-rigid homotopy (inscribed balls hardened into the solid under inward pressure), then SLSQP '
                  'tightening with per-pair separating planes',
        'date': datetime.date.today().isoformat(),
        'pieces': [[*map(float, C2[i]), *map(float, Q[i])] for i in range(len(C2))]}
    if meta: claim.update(meta)
    return claim


def make_claim_fast(rec, GAP=1e-7, WALL=1e-7, meta=None):
    """Same claim as make_claim for any solid of src/solids.json, with the centres spread by Newton-like steps on the
    vectorized separating-axis gaps (exact.pair_gaps) instead of bisection: every near pair ends with a separating
    axis showing a gap >= GAP (unit edge), then the container is fitted with wall gap >= WALL."""
    from exact import pair_gaps
    piece, container = rec['piece'], rec['container']
    pbi = Problem(piece, container); e = pbi.edge
    Vu = np.array(SOL[piece]['V']); CN = np.array(SOL[container]['normals']); CV = np.array(SOL[container]['V'])
    beta = np.array([CN[f] @ CV[F[0]] for f, F in enumerate(SOL[container]['faces'])])
    C = np.array(rec['C'], float)
    Q = [np.array(q) / np.linalg.norm(q) for q in rec['Q']]
    Q = [q if q[0] >= 0 else -q for q in Q]
    R = [quat_to_R(q) for q in Q]
    n = len(C); cen = C.mean(0); lim = (2 * pbi.circ) ** 2 * 1.0001
    k = 1.0
    for _ in range(60):
        P = cen + k * (C - cen)
        pairs = np.array([(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((P[i] - P[j]) ** 2) <= lim], int).reshape(-1, 2)
        if not len(pairs): break
        g, u = pair_gaps(pbi, P, R, pairs, want_axis=True)
        bad = g < GAP * e * (1 + 1e-9)
        if not bad.any(): break
        dc = C[pairs[bad, 1]] - C[pairs[bad, 0]]
        proj = np.abs(np.sum(u[bad] * dc, axis=1))
        need = np.where(proj > 1e-9, (GAP * e * (1 + 1e-6) - g[bad]) / np.maximum(proj, 1e-9), 1e-4)
        k += float(need.max()) * (1 + 1e-6) + 1e-15
    else:
        raise RuntimeError('could not spread the centres to the clearance')
    P = cen + k * (C - cen)
    pairs = np.array([(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((P[i] - P[j]) ** 2) <= lim], int).reshape(-1, 2)
    pg = float(pair_gaps(pbi, P, R, pairs).min()) / e if len(pairs) else float('inf')
    C2 = P / e
    X = np.concatenate([C2[i] + Vu @ R[i].T for i in range(n)])
    S = (X @ CN.T).max(0)
    res = linprog([0, 0, 0, 1], A_ub=np.hstack([CN, -beta[:, None]]), b_ub=-S, bounds=[(None, None)] * 4, method='highs')
    t = res.x[:3]; C2 = C2 + t
    X = np.concatenate([C2[i] + Vu @ R[i].T for i in range(n)])
    s = math.ceil(float(((X @ CN.T).max(0) + WALL).__truediv__(beta).max()) * 1e13) / 1e13
    wall = float((s * beta[None, :] - X @ CN.T).min())
    claim = {
        'problem': f'min/{piece}_in_{container}', 'piece': piece, 'container': container, 'n': n,
        's': math.floor(s * 1e5) / 1e5, 's_plus': f'{math.floor(s * 1e5) / 1e5:.5f}+', 's_full': s,
        'measure': ('edge length of the container divided by the edge length of the pieces' if SOL[piece].get('unit', 'edge') == 'edge'
                    else 'linear size of the container divided by the linear size of the pieces (same canonical solid)'),
        'clearance': {'min_pair_gap_target': GAP, 'wall_gap_target': WALL, 'min_pair_gap': pg, 'min_wall_gap': wall},
        'format': '[x, y, z, qw, qx, qy, qz] per piece: a copy of the canonical piece solid (src/solids.json, 50-digit '
                  'coordinates in src/solids_hp.json) rotated by the scalar-first quaternion q and centred at (x, y, z); '
                  'container = s_full x canonical container solid, centred at the origin, canonical orientation',
        'method': 'generalized soft-to-rigid homotopy (r-rounding of the solid hardened under inward pressure), basin '
                  'hopping, then sequential-LP / SLSQP tightening with per-pair separating planes',
        'date': datetime.date.today().isoformat(),
        'pieces': [[*map(float, C2[i]), *map(float, Q[i])] for i in range(n)]}
    if meta: claim.update(meta)
    return claim


if __name__ == '__main__':
    rec = json.load(open(sys.argv[1]))
    GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-6
    WALL = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-6
    c = make_claim(rec, GAP, WALL)
    json.dump(c, open(sys.argv[2], 'w'), indent=1)
    print('s_full', repr(c['s_full']), 'pair gap', c['clearance']['min_pair_gap'], 'wall gap', c['clearance']['min_wall_gap'])
