"""Turn a d-dimensional packing (internal units of src/ndsim.py) into a record with explicit clearance and witnesses,
for certify_nd.py (15 Oct 2026).

Exact frame: the piece is the polytope of src/polytopes_nd.json as given there (vertex coordinates V); the container
is cc + s_full mu C, C the container polytope as given there and mu = edge(P) / edge(C) exactly, so s_full is the
container edge divided by the piece edge. Each rotation is replaced by an exactly orthogonal rational one,
R = D (I - S)^-1 (I + S) (Cayley transform of a skew-symmetric S with 2^-44-rounded entries, times a diagonal sign
matrix D of determinant 1 chosen so that the Cayley parameters are well conditioned). Centres are spread apart until
every near pair has a separating hyperplane with gap >= GAP (in piece edges), the container is fitted by an LP over
translations with wall gap >= WALL, s_full is rounded up at the 13th decimal, and every near pair's hyperplane is
stored as a rational witness u.x = t (mid-gap)."""
import json, math, datetime, itertools, os, sys
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ndsim

# exact edge lengths of the polytopes in src/polytopes_nd.json (checked: EDGE^2 = edge2 exactly, EDGE > 0)
EDGE = {'c5': '2*sqrt2', 'c8': '1', 'c16': 'sqrt2', 'c24': 'sqrt2', 'c600': '-1/2+1/2*sqrt5', 'c120': '7-3*sqrt5',
        'sx5': 'sqrt2', 'hc5': '1', 'op5': 'sqrt2', 'sx6': 'sqrt2', 'hc6': '1', 'op6': 'sqrt2'}


def mu_of(piece, container):
    """edge(piece) / edge(container polytope), exactly, as a string of multiquad.py"""
    from multiquad import parse
    return repr(parse(EDGE[piece]) / parse(EDGE[container]))


DEN = 2 ** 44


def rational_rotation(R):
    """(S entries as Fractions, D signs, exact float matrix) with D Cayley(S) = R up to ~1e-13"""
    d = len(R); best = None
    for sg in itertools.product((1, -1), repeat=d):
        if sg.count(-1) % 2: continue
        Q = np.diag(sg) @ R
        sv = np.linalg.svd(Q + np.eye(d), compute_uv=False).min()
        if best is None or sv > best[0]: best = (sv, sg, Q)
    _, sg, Q = best
    I = np.eye(d)
    S = (Q - I) @ np.linalg.inv(Q + I); S = (S - S.T) / 2
    Sq = [[Fr(round(S[a, b] * DEN), DEN) for b in range(d)] for a in range(d)]
    for a in range(d):
        Sq[a][a] = Fr(0)
        for b in range(a): Sq[a][b] = -Sq[b][a]
    Sf = np.array([[float(x) for x in r] for r in Sq])
    Rx = np.diag(sg) @ np.linalg.solve(I - Sf, I + Sf)
    return [Sq[a][b] for a in range(d) for b in range(a + 1, d)], list(sg), Rx


def make_claim(problem, piece, container, C, R, GAP=1e-7, WALL=1e-7, meta=None, names=None):
    pb = ndsim.Problem(piece, container); d = pb.d; n = len(C)
    D = ndsim.data(); P, Q = D[piece], D[container]
    sc = pb.scale                                              # internal = sc x exact frame
    rots = [rational_rotation(np.asarray(r, float)) for r in R]
    Rx = np.array([x[2] for x in rots])
    # spread the centres (internal units) until every near pair has gap >= GAP x edge along a found hyperplane
    Ci = np.array(C, float); cen = Ci.mean(0); e = pb.edge
    lim = (2 * pb.circ) ** 2 * 1.0001
    k = 1.0; U = None
    for _ in range(80):
        Pp = cen + k * (Ci - cen)
        pairs = ndsim.near_pairs(Pp, lim)
        if not len(pairs): break
        g, U, mid = ndsim.planes_lp(pb, Pp, Rx, pairs, U0=U if U is not None and len(U) == len(pairs) else None)
        bad = g < GAP * e * (1 + 1e-9)
        if not bad.any(): break
        dc = Ci[pairs[bad, 1]] - Ci[pairs[bad, 0]]
        proj = np.abs(np.sum(U[bad] * dc, axis=1))
        need = np.where(proj > 1e-9, (GAP * e * (1 + 1e-6) - g[bad]) / np.maximum(proj, 1e-9), 1e-4)
        k += float(need.max()) * (1 + 1e-6) + 1e-15
    else:
        raise RuntimeError('could not spread the centres to the clearance')
    Pp = cen + k * (Ci - cen)
    pairs = ndsim.near_pairs(Pp, (2 * pb.circ) ** 2 * 1.01)
    g, U, mid = ndsim.planes_lp(pb, Pp, Rx, pairs) if len(pairs) else (np.zeros(0), np.zeros((0, d)), np.zeros(0))
    pg = float(g.min()) / e if len(g) else float('inf')
    # exact frame: divide by sc; container cc + s mu C with C's facets (unit normals N, offsets beta in its own frame)
    C2 = Pp / sc
    Vp = np.array(P['Vf']); CN = np.array(Q['N']); beta = np.array(Q['beta'])
    from multiquad import parse
    mu = float(parse(mu_of(piece, container)))
    X = np.concatenate([C2[i] + Vp @ Rx[i].T for i in range(n)])
    S = (X @ CN.T).max(0)
    res = linprog(np.r_[np.zeros(d), 1.0], A_ub=np.hstack([CN, -(mu * beta)[:, None]]), b_ub=-S, bounds=[(None, None)] * (d + 1), method='highs')
    t = res.x[:d]; C2 = C2 + t
    X = np.concatenate([C2[i] + Vp @ Rx[i].T for i in range(n)])
    eP = P['edge']
    s = math.ceil(float(((X @ CN.T).max(0) + WALL * eP).__truediv__(mu * beta).max()) * 1e13) / 1e13
    wall = float((s * mu * beta[None, :] - X @ CN.T).min()) / eP
    # witnesses in the exact frame: u.x = t, t at mid-gap (u rounded to 2^-44, t recomputed from the rounded u)
    planes = []
    for (i, j), u in zip(pairs.tolist(), U):
        uq = np.round(u * DEN) / DEN
        xa = ((C2[i] + Vp @ Rx[i].T) @ uq).max(); xb = ((C2[j] + Vp @ Rx[j].T) @ uq).min()
        planes.append([i, j, *uq.tolist(), (xa + xb) / 2])
    pieces = [[*map(float, C2[i]), *[float(x) for x in rots[i][0]], *rots[i][1]] for i in range(n)]   # S: dyadic, exact as floats
    nm = names or {}
    rec = {
        'problem': problem, 'piece': piece, 'container': container, 'dim': d, 'n': n,
        's': math.floor(s * 1e5) / 1e5, 's_plus': f'{math.floor(s * 1e5) / 1e5:.5f}+', 's_full': s,
        'mu': mu_of(piece, container),
        'measure': 'edge length of the container divided by the edge length of the pieces',
        'clearance': {'min_pair_gap_target': GAP, 'wall_gap_target': WALL, 'min_pair_gap': pg, 'min_wall_gap': wall},
        'density': n * P['volume'] / (Q['volume'] * (s * mu) ** d),
        'format': (f'per piece [c_1..c_{d}, S_12, S_13, ..., S_{d - 1}{d}, D_1..D_{d}]: the piece polytope of src/polytopes_nd.json '
                   f'(exact vertex coordinates V) placed as c + R V with R = diag(D) (I - S)^-1 (I + S), S skew-symmetric '
                   f'(upper triangle row by row, exact rationals), D = +-1 with determinant 1; container = s_full x mu x the '
                   f'container polytope of src/polytopes_nd.json, centred at the origin; planes [i, j, u_1..u_{d}, t]: '
                   f'u.x < t on piece i, u.x > t on piece j'),
        'method': 'd-dimensional soft-to-rigid homotopy (inscribed balls hardened into the polytope under inward pressure), '
                  'basin hopping, sequential-LP tightening with per-pair separating hyperplanes (src/ndsim.py, src/ndslp.py)',
        'date': datetime.date.today().isoformat(),
        'container_center': [0] * d,
        'pieces': pieces, 'planes': planes}
    if meta: rec.update(meta)
    return rec
