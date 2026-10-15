"""Archimedean, Catalan, prism and antiprism solids for the generalized soft-to-rigid search.

Each solid is built from a definition in high precision (mpmath, 60 digits):
  * Archimedean solids: the classical coordinates (permutations / sign patterns) of the 11 non-snub solids; the two
    snub solids as the orbit of a point under the rotation group (O or I) chosen, by Newton's method, so that the
    three Wythoff rotations move it by the same distance (Wythoff's snub construction). All scaled to unit edge.
  * Catalan solids: the canonical duals of the unit-edge Archimedean solids (polar reciprocal about the common
    midsphere: the dual vertex of a face with unit normal m at distance h is (r_m^2 / h) m).
  * Regular prisms and antiprisms (all edges 1) over the 3-, 4-, 5-, 6-, 8- and 12-gon.
Faces are derived from the convex hull, then checked: vertex/edge/face counts and Euler's formula, equal edges
(Archimedean, prisms, antiprisms), equal face distances (Catalan: an insphere), planarity, and that every face plane
supports the solid. The float data used by the search go to src/solids.json (together with the Platonic solids
from solids.py); the 50-digit coordinates go to src/solids_hp.json for the certifier.

"tangential" solids (an insphere touching every face: Platonic and Catalan) use Nakajima's soft shapes
(1 - r/rho) P (+) B(r) exactly as before. For the others the soft shape is the r-rounding of P,
  S_r = (P (-) B(r)) (+) B(r) = union of all balls of radius r inside P,
whose core P (-) B(r) = {x : n_f . x <= h_f - r} is another polytope; its combinatorial type changes at finitely many
r, and inside each interval every core vertex moves linearly in r. Those intervals ("cores") are precomputed here in
the search's internal units (inradius 1/2). For a tangential solid the r-rounding equals Nakajima's shape, so this is
a generalization of his homotopy, not a different one.
"""
import json, math, os, sys, itertools
import mpmath as mp
import numpy as np
from scipy.spatial import ConvexHull, HalfspaceIntersection

mp.mp.dps = 60
HERE = os.path.dirname(os.path.abspath(__file__))
PHI = (1 + mp.sqrt(5)) / 2

ARCH = ['truncated_tetrahedron', 'cuboctahedron', 'truncated_cube', 'truncated_octahedron', 'rhombicuboctahedron',
        'truncated_cuboctahedron', 'snub_cube', 'icosidodecahedron', 'truncated_dodecahedron',
        'truncated_icosahedron', 'rhombicosidodecahedron', 'truncated_icosidodecahedron', 'snub_dodecahedron']
DUAL = {'truncated_tetrahedron': 'triakis_tetrahedron', 'cuboctahedron': 'rhombic_dodecahedron',
        'truncated_cube': 'triakis_octahedron', 'truncated_octahedron': 'tetrakis_hexahedron',
        'rhombicuboctahedron': 'deltoidal_icositetrahedron', 'truncated_cuboctahedron': 'disdyakis_dodecahedron',
        'snub_cube': 'pentagonal_icositetrahedron', 'icosidodecahedron': 'rhombic_triacontahedron',
        'truncated_dodecahedron': 'triakis_icosahedron', 'truncated_icosahedron': 'pentakis_dodecahedron',
        'rhombicosidodecahedron': 'deltoidal_hexecontahedron', 'truncated_icosidodecahedron': 'disdyakis_triacontahedron',
        'snub_dodecahedron': 'pentagonal_hexecontahedron'}
CAT = [DUAL[a] for a in ARCH]
PRISM_N = [3, 4, 5, 6, 8, 12]
PRISMS = [f'prism{k}' for k in PRISM_N] + [f'antiprism{k}' for k in PRISM_N]
COUNTS = {   # V, E, F
    'truncated_tetrahedron': (12, 18, 8), 'cuboctahedron': (12, 24, 14), 'truncated_cube': (24, 36, 14),
    'truncated_octahedron': (24, 36, 14), 'rhombicuboctahedron': (24, 48, 26), 'truncated_cuboctahedron': (48, 72, 26),
    'snub_cube': (24, 60, 38), 'icosidodecahedron': (30, 60, 32), 'truncated_dodecahedron': (60, 90, 32),
    'truncated_icosahedron': (60, 90, 32), 'rhombicosidodecahedron': (60, 120, 62),
    'truncated_icosidodecahedron': (120, 180, 62), 'snub_dodecahedron': (60, 150, 92)}
for a in ARCH: COUNTS[DUAL[a]] = (COUNTS[a][2], COUNTS[a][1], COUNTS[a][0])
for k in PRISM_N:
    COUNTS[f'prism{k}'] = (2 * k, 3 * k, k + 2); COUNTS[f'antiprism{k}'] = (2 * k, 4 * k, 2 * k + 2)
# elongated prisms (13 Oct 2026, crystal-growth variants packed in a cube): base edge 1, height l = 1.5, 2, 3
ELONG = {'l15': mp.mpf(3) / 2, 'l2': mp.mpf(2), 'l3': mp.mpf(3)}
ELONG_TXT = {'l15': '1.5', 'l2': '2', 'l3': '3'}
ELONGATED = [f'prism{k}_{t}' for k in (3, 5, 6, 8, 12) for t in ELONG]
for k in PRISM_N:
    for t in ELONG: COUNTS[f'prism{k}_{t}'] = (2 * k, 3 * k, k + 2)
TITLE = {s: s.replace('_', ' ') for s in ARCH + CAT}
POLY = {3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal'}
for k in PRISM_N:
    TITLE[f'prism{k}'] = f'{POLY[k]} prism'; TITLE[f'antiprism{k}'] = f'{POLY[k]} antiprism'
    for t in ELONG: TITLE[f'prism{k}_{t}'] = f'{POLY[k]} prism of height {ELONG_TXT[t]}'


# ------------------------------------------------------------------ coordinate definitions
def _perms(p, even_only=False):
    out = set()
    for q in itertools.permutations(range(3)):
        par = sum(1 for i in range(3) for j in range(i + 1, 3) if q[i] > q[j]) % 2
        if even_only and par: continue
        out.add(tuple(p[i] for i in q))
    return out


def _signs(p):
    out = set()
    for s in itertools.product((1, -1), repeat=3):
        out.add(tuple(s[i] * p[i] for i in range(3)))
    return out


def _allp(gens, even_only=False, sign_rule=None):
    pts = set()
    for g in gens:
        for p in _perms(g, even_only):
            for q in _signs(p):
                if sign_rule and not sign_rule(q): continue
                pts.add(q)
    return [tuple(mp.mpf(x) for x in p) for p in pts]


def _uniq(points, tol=1e-30):
    out = []
    for p in points:
        if not any(max(abs(p[i] - q[i]) for i in range(3)) < tol for q in out): out.append(p)
    return out


def _rot(axis, ang):
    ax = mp.matrix(axis); ax = ax / mp.norm(ax)
    x, y, z = ax; c, s = mp.cos(ang), mp.sin(ang); C = 1 - c
    return mp.matrix([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                      [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                      [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def _group(gens):
    key = lambda M: tuple(round(float(M[i, j]), 9) for i in range(3) for j in range(3))
    G = {key(mp.eye(3)): mp.eye(3)}
    frontier = [mp.eye(3)]
    while frontier:
        nxt = []
        for A in frontier:
            for g in gens:
                B = g * A; k = key(B)
                if k not in G: G[k] = B; nxt.append(B)
        frontier = nxt
    return list(G.values())


def _snub(kind):
    """Wythoff snub: v in the fundamental triangle (p-fold axis P, 3-fold axis Q, 2-fold axis R) with
    |v - g_P v| = |v - g_Q v| = |v - g_R v|; the snub solid is the convex hull of the orbit of v under the rotations."""
    if kind == 'cube':
        P, Q, R, p = [0, 0, 1], [1, 1, 1], [1, 0, 1], 4
        G = _group([_rot([0, 0, 1], mp.pi / 2), _rot([1, 1, 1], 2 * mp.pi / 3)])
        want = 'snub_cube'
    else:
        P, Q, R, p = [0, 1, PHI], [1, 1, 1], [PHI, 1, PHI + 1], 5
        G = _group([_rot([0, 1, PHI], 2 * mp.pi / 5), _rot([1, 1, 1], 2 * mp.pi / 3)])
        want = 'snub_dodecahedron'
    nrm = lambda u: [x / mp.sqrt(sum(y * y for y in u)) for x in u]
    P, Q, R = nrm(P), nrm(Q), nrm(R)
    for sp, sq in itertools.product((1, -1), repeat=2):
        gP, gQ, gR = _rot(P, sp * 2 * mp.pi / p), _rot(Q, sq * 2 * mp.pi / 3), _rot(R, mp.pi)

        def F(x, y, z):
            v = mp.matrix([x, y, z])
            d = lambda g: mp.norm(v - g * v) ** 2
            return [d(gP) - d(gQ), d(gQ) - d(gR), x * x + y * y + z * z - 1]
        v0 = nrm([P[i] + Q[i] + R[i] for i in range(3)])
        try:
            sol = mp.findroot(F, v0)
        except Exception:
            continue
        v = mp.matrix([sol[0], sol[1], sol[2]])
        pts = _uniq([tuple((g * v)[i] for i in range(3)) for g in G])
        try:
            s = _solid_from_points(want, pts, check_uniform=True)
            return pts
        except AssertionError:
            continue
    raise RuntimeError('snub solve failed for ' + kind)


def _vertices(name):
    one = mp.mpf(1); r2 = mp.sqrt(2); phi = PHI
    if name == 'truncated_tetrahedron':
        return _allp([(3, 1, 1)], sign_rule=lambda q: sum(1 for x in q if x < 0) % 2 == 0)
    if name == 'cuboctahedron': return _allp([(1, 1, 0)])
    if name == 'truncated_cube': return _allp([(r2 - 1, 1, 1)])
    if name == 'truncated_octahedron': return _allp([(0, 1, 2)])
    if name == 'rhombicuboctahedron': return _allp([(1, 1, 1 + r2)])
    if name == 'truncated_cuboctahedron': return _allp([(1, 1 + r2, 1 + 2 * r2)])
    if name == 'icosidodecahedron': return _allp([(0, 0, phi), (one / 2, phi / 2, phi ** 2 / 2)], even_only=True)
    if name == 'truncated_dodecahedron':
        return _allp([(0, 1 / phi, 2 + phi), (1 / phi, phi, 2 * phi), (phi, 2, phi + 1)], even_only=True)
    if name == 'truncated_icosahedron':
        return _allp([(0, 1, 3 * phi), (1, 2 + phi, 2 * phi), (phi, 2, 2 * phi + 1)], even_only=True)
    if name == 'rhombicosidodecahedron':
        return _allp([(1, 1, phi ** 3), (phi ** 2, phi, 2 * phi), (2 + phi, 0, phi ** 2)], even_only=True)
    if name == 'truncated_icosidodecahedron':
        return _allp([(1 / phi, 1 / phi, 3 + phi), (2 / phi, phi, 1 + 2 * phi), (1 / phi, phi ** 2, -1 + 3 * phi),
                      (-1 + 2 * phi, 2, 2 + phi), (phi, 3, 2 * phi)], even_only=True)
    if name == 'snub_cube': return _snub('cube')
    if name == 'snub_dodecahedron': return _snub('dodecahedron')
    if name.startswith('prism'):
        base, _, tag = name.partition('_')
        k = int(base[5:]); R = 1 / (2 * mp.sin(mp.pi / k)); hgt = ELONG[tag] if tag else one
        return [(R * mp.cos(2 * mp.pi * j / k), R * mp.sin(2 * mp.pi * j / k), s * hgt / 2) for j in range(k) for s in (1, -1)]
    if name.startswith('antiprism'):
        k = int(name[9:]); R = 1 / (2 * mp.sin(mp.pi / k))
        h = mp.sqrt(1 - 1 / (4 * mp.cos(mp.pi / (2 * k)) ** 2))
        return ([(R * mp.cos(2 * mp.pi * j / k), R * mp.sin(2 * mp.pi * j / k), h / 2) for j in range(k)] +
                [(R * mp.cos(2 * mp.pi * (j + mp.mpf(1) / 2) / k), R * mp.sin(2 * mp.pi * (j + mp.mpf(1) / 2) / k), -h / 2) for j in range(k)])
    raise KeyError(name)


# ------------------------------------------------------------------ structure from points
class HSolid:
    pass


def _solid_from_points(name, pts, check_uniform=False, check_tangential=False):
    """Faces from the convex hull of high-precision points; returns HSolid with mp coordinates and float data."""
    X = np.array([[float(c) for c in p] for p in pts])
    hull = ConvexHull(X)
    planes = []                    # (unit normal mp, offset mp, set of vertex ids)
    for eq in hull.equations:
        nf, hf = eq[:3], -eq[3]
        if any(np.allclose(nf, q[3], atol=1e-7) and abs(hf - q[4]) < 1e-7 for q in planes): continue
        on = [i for i in range(len(X)) if abs(X[i] @ nf - hf) < 1e-7]
        # high-precision plane through three of its points
        a, b, c = (mp.matrix(pts[i]) for i in on[:3])
        best = None
        for t in itertools.combinations(on, 3):
            a, b, c = (mp.matrix(pts[i]) for i in t)
            n = _crossm(b - a, c - a)
            if best is None or mp.norm(n) > mp.norm(best[0]): best = (n, a)
        n, a = best; n = n / mp.norm(n)
        if mp.fdot(n, a) < 0: n = -n
        h = mp.fdot(n, a)
        planes.append((n, h, set(on), nf, hf))
    S = HSolid(); S.name = name; S.Vh = pts; S.V = X
    S.faces, S.Nh, S.hh = [], [], []
    for n, h, on, nf, hf in planes:
        # exactness checks at 60 digits: coplanar vertices on the plane, every other vertex strictly inside
        for i, p in enumerate(pts):
            d = mp.fdot(n, mp.matrix(p)) - h
            if i in on: assert abs(d) < mp.mpf(10) ** -40, (name, 'not coplanar', float(d))
            else: assert d < -mp.mpf(10) ** -6, (name, 'plane does not support', float(d))
        # cyclic order (CCW seen from outside)
        idx = sorted(on); cen = sum((mp.matrix(pts[i]) for i in idx), mp.matrix([0, 0, 0])) / len(idx)
        u = mp.matrix(pts[idx[0]]) - cen; u = u / mp.norm(u); w = _crossm(n, u)
        ang = {i: mp.atan2(mp.fdot(mp.matrix(pts[i]) - cen, w), mp.fdot(mp.matrix(pts[i]) - cen, u)) for i in idx}
        loop = sorted(idx, key=lambda i: ang[i])
        S.faces.append(loop); S.Nh.append(n); S.hh.append(h)
    edges = set()
    for loop in S.faces:
        for a, b in zip(loop, loop[1:] + loop[:1]): edges.add((min(a, b), max(a, b)))
    S.edges = sorted(edges)
    # every edge on exactly two faces (closed surface: the faces are all the facets)
    for e in S.edges:
        on = sum(1 for loop in S.faces if any({a, b} == set(e) for a, b in zip(loop, loop[1:] + loop[:1])))
        assert on == 2, (name, 'edge on', on, 'faces')
    V, E, F = len(pts), len(S.edges), len(S.faces)
    if name in COUNTS: assert (V, E, F) == COUNTS[name], (name, (V, E, F), COUNTS[name])
    assert V - E + F == 2
    L = [mp.norm(mp.matrix(pts[a]) - mp.matrix(pts[b])) for a, b in S.edges]
    S.edge_min, S.edge_max = min(L), max(L)
    if check_uniform: assert S.edge_max - S.edge_min < mp.mpf(10) ** -40, (name, 'edges not equal', float(S.edge_max - S.edge_min))
    S.inradius = min(S.hh); S.insphere_gap = max(S.hh) - min(S.hh)
    if check_tangential: assert S.insphere_gap < mp.mpf(10) ** -40, (name, 'not tangential')
    return S


def _crossm(a, b):
    return mp.matrix([a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]])


def build(name):
    if name in ELONGATED:                                     # base edge 1, height l (not uniform: no rescaling)
        pts = _uniq(_vertices(name))
        S = _solid_from_points(name, pts)
        assert abs(S.edge_min - 1) < mp.mpf(10) ** -40 and abs(S.edge_max - ELONG[name.split('_')[1]]) < mp.mpf(10) ** -40
        S.unit = 'base edge (height ' + ELONG_TXT[name.split('_')[1]] + ')'
        return S
    if name in ARCH or name in PRISMS:
        pts = _uniq(_vertices(name))
        S0 = _solid_from_points(name, pts, check_uniform=True)
        sc = 1 / S0.edge_min                                  # unit edge
        pts = [tuple(sc * c for c in p) for p in pts]
        S = _solid_from_points(name, pts, check_uniform=True)
        assert abs(S.edge_min - 1) < mp.mpf(10) ** -40
        S.unit = 'edge'
        return S
    if name in CAT:
        a = [k for k, v in DUAL.items() if v == name][0]
        A = build(a)
        # midsphere radius of the Archimedean solid: distance from the centre to every edge midpoint
        mids = [mp.norm((mp.matrix(A.Vh[i]) + mp.matrix(A.Vh[j])) / 2) for i, j in A.edges]
        rm = mids[0]; assert max(mids) - min(mids) < mp.mpf(10) ** -40
        pts = [tuple(rm ** 2 / h * n[i] for i in range(3)) for n, h in zip(A.Nh, A.hh)]
        S = _solid_from_points(name, pts, check_tangential=True)
        S.unit = 'canonical dual of the unit-edge ' + TITLE[a] + ' (common midsphere)'
        return S
    raise KeyError(name)


def volume(S):
    tot = mp.mpf(0)
    for loop, n, h in zip(S.faces, S.Nh, S.hh):
        p0 = mp.matrix(S.Vh[loop[0]])
        for a, b in zip(loop[1:-1], loop[2:]):
            tot += mp.norm(_crossm(mp.matrix(S.Vh[a]) - p0, mp.matrix(S.Vh[b]) - p0)) / 2 * h / 3
    return tot


# ------------------------------------------------------------------ cores of the r-rounding (non-tangential)
def _core_at(N, H, r, tol=1e-9):
    """Vertices of {x : N x <= H - r} (internal units) with their active plane sets."""
    hs = HalfspaceIntersection(np.hstack([N, -(H - r)[:, None]]), np.zeros(3))
    pts = []
    for p in hs.intersections:
        if not any(np.abs(p - q).max() < 1e-8 for q in pts): pts.append(p)
    out = []
    for p in pts:
        act = frozenset(np.nonzero(np.abs(N @ p - (H - r)) < tol)[0].tolist())
        out.append((p, act))
    return out


def _signature(core): return frozenset(a for _, a in core)


def cores(S, rcap=0.49, samples=240):
    """Intervals [r0, r1] of constant combinatorial type of the core P (-) B(r), r in internal units (inradius 1/2);
    in each, vertex v(r) = V0 + r W exactly (intersection of three of its active planes)."""
    sc = 0.5 / float(S.inradius)
    N = np.array([[float(c) for c in n] for n in S.Nh]); H = np.array([float(h) for h in S.hh]) * sc
    grid = list(np.linspace(1e-6, rcap, samples))
    sigs = [_signature(_core_at(N, H, r)) for r in grid]
    bounds = [0.0]
    for i in range(1, len(grid)):
        if sigs[i] != sigs[i - 1]:
            lo, hi = grid[i - 1], grid[i]
            for _ in range(50):
                m = (lo + hi) / 2
                if _signature(_core_at(N, H, m)) == sigs[i - 1]: lo = m
                else: hi = m
            bounds.append((lo + hi) / 2)
    bounds.append(rcap)
    out = []
    for r0, r1 in zip(bounds[:-1], bounds[1:]):
        rm = (r0 + r1) / 2
        core = _core_at(N, H, rm)
        V0, W, acts = [], [], []
        for p, act in core:
            act = sorted(act)
            best = None
            for t in itertools.combinations(act, 3):
                M = N[list(t)]
                d = abs(np.linalg.det(M))
                if best is None or d > best[0]: best = (d, t)
            M = N[list(best[1])]; Minv = np.linalg.inv(M)
            V0.append(Minv @ H[list(best[1])]); W.append(-Minv @ np.ones(3)); acts.append(set(act))
        V0, W = np.array(V0), np.array(W)
        Vm = V0 + rm * W
        faces, fids = [], []
        for f in range(len(N)):
            on = [i for i in range(len(acts)) if f in acts[i]]
            if len(on) < 3: continue
            cen = Vm[on].mean(0); u = Vm[on[0]] - cen; u /= np.linalg.norm(u); w = np.cross(N[f], u)
            loop = sorted(on, key=lambda i: math.atan2((Vm[i] - cen) @ w, (Vm[i] - cen) @ u))
            faces.append(loop); fids.append(f)
        edges = set()
        for loop in faces:
            for a, b in zip(loop, loop[1:] + loop[:1]): edges.add((min(a, b), max(a, b)))
        # sanity: at both ends of the interval the linear vertices satisfy every half-space
        for r in (r0 + 1e-9 * (r1 - r0), r1):
            Vr = V0 + r * W
            viol = float((Vr @ N.T - (H - r)).max())
            assert viol <= 1e-7, (S.name, 'core vertex outside at r', r, viol)
        out.append({'r0': r0, 'r1': r1, 'V0': V0.tolist(), 'W': W.tolist(), 'faces': faces, 'fid': fids,
                    'edges': [list(e) for e in sorted(edges)]})
    return out


# ------------------------------------------------------------------ export
def float_data(S, with_cores):
    V = [[float(c) for c in p] for p in S.Vh]
    N = [[float(c) for c in n] for n in S.Nh]
    d = dict(name=S.name, V=V, faces=S.faces, normals=N, inradius=float(S.inradius),
             circumradius=max(float(mp.norm(mp.matrix(p))) for p in S.Vh), edges=[list(e) for e in S.edges],
             volume=float(volume(S)), offsets=[float(h) for h in S.hh], tangential=bool(S.insphere_gap < 1e-30),
             edge_min=float(S.edge_min), edge_max=float(S.edge_max), unit=S.unit)
    if with_cores and not d['tangential']: d['cores'] = cores(S)
    return d


def main():
    names = ARCH + CAT + [p for p in PRISMS if p not in ('prism4', 'antiprism3')]
    if len(sys.argv) > 1 and sys.argv[1] != 'all': names = sys.argv[1].split(',')
    sol_path = os.path.join(HERE, 'src', 'solids.json'); hp_path = os.path.join(HERE, 'src', 'solids_hp.json')
    sol = json.load(open(sol_path)); hp = json.load(open(hp_path)) if os.path.exists(hp_path) else {}
    for name in names:
        S = build(name)
        d = float_data(S, True)
        sol[name] = d
        hp[name] = dict(V=[[mp.nstr(c, 50) for c in p] for p in S.Vh], faces=S.faces, unit=S.unit)
        print(f"{name:28s} V={len(S.Vh):3d} E={len(S.edges):3d} F={len(S.faces):3d}  inradius {float(S.inradius):.6f} "
              f"circ {d['circumradius']:.6f} vol {d['volume']:.6f} tangential={d['tangential']} edges {float(S.edge_min):.6f}-{float(S.edge_max):.6f}"
              + (f"  cores {len(d['cores'])}" if 'cores' in d else ''), flush=True)
    json.dump(sol, open(sol_path, 'w'))
    json.dump(hp, open(hp_path, 'w'))


if __name__ == '__main__':
    main()
