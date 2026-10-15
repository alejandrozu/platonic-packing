#!/usr/bin/env python3
"""The regular polytopes of dimensions 4, 5 and 6, exactly (15 Oct 2026, higher-dimensional packings).

    python3 src/polytopes_nd.py        # rebuild and self-check src/polytopes_nd.json

4D: 5-cell, tesseract (8-cell), 16-cell, 24-cell, 120-cell, 600-cell; 5D and 6D: simplex, hypercube, orthoplex.
Every vertex coordinate is an element of Q(sqrt2, sqrt3, sqrt5, sqrt7) (multiquad.py), written as a string:
  tesseract / d-cube   (+-1/2, ..., +-1/2)                                  edge 1
  16-cell / orthoplex  +-e_i                                                 edge sqrt2
  24-cell              all permutations of (+-1, +-1, 0, 0)                  edge sqrt2
  600-cell             (+-1/2)^4, perm. of (+-1, 0, 0, 0), even perm. of (+-phi, +-1, +-1/phi, 0)/2   edge 1/phi
  120-cell             its polar dual (vertices = the 600 cell centroids / |centroid|^2)
  5-cell / d-simplex   c e_i (i = 1..d) and a (1, ..., 1), a = c (1 - sqrt(d + 1)) / d, then centred
Each polytope is centred at the origin. Facets are found numerically (convex hull) and then checked exactly: the
exact outward normal of a facet is the sum of its vertices (the foot of the perpendicular from the centre of a regular
polytope is the facet's centroid), every facet vertex lies on the facet hyperplane and every other vertex strictly
inside; all edges have exactly the same length. The JSON stores the exact vertices, the facets (vertex index lists),
the edges, and float data (vertices, unit normals, offsets, radii, volume) in this exact frame."""
import json, os, sys, itertools, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import multiquad as M
MQ = M.MQ
OUT = os.path.join(HERE, 'polytopes_nd.json')

S5 = MQ.sqrt(5); PHI = (1 + S5) / 2; IPHI = PHI - 1
HALF = MQ(M.Fr(1, 2))
NAMES = {  # id: (display name, dimension)
    'c5': ('5-cell', 4), 'c8': ('tesseract', 4), 'c16': ('16-cell', 4), 'c24': ('24-cell', 4),
    'c120': ('120-cell', 4), 'c600': ('600-cell', 4),
    'sx5': ('5-simplex', 5), 'hc5': ('5-cube', 5), 'op5': ('5-orthoplex', 5),
    'sx6': ('6-simplex', 6), 'hc6': ('6-cube', 6), 'op6': ('6-orthoplex', 6)}
DUAL = {'c5': 'c5', 'c8': 'c16', 'c16': 'c8', 'c24': 'c24', 'c120': 'c600', 'c600': 'c120',
        'sx5': 'sx5', 'hc5': 'op5', 'op5': 'hc5', 'sx6': 'sx6', 'hc6': 'op6', 'op6': 'hc6'}


def even_perms(k):
    out = []
    for p in itertools.permutations(range(k)):
        inv = sum(1 for i in range(k) for j in range(i + 1, k) if p[i] > p[j])
        if inv % 2 == 0: out.append(p)
    return out


def signs(v):
    """all sign changes of the nonzero entries"""
    nz = [i for i, x in enumerate(v) if x != 0]
    out = []
    for s in itertools.product((1, -1), repeat=len(nz)):
        w = list(v)
        for i, g in zip(nz, s): w[i] = w[i] * g
        out.append(tuple(w))
    return out


def uniq(vs):
    seen, out = set(), []
    for v in vs:
        k = tuple(round(float(x), 9) for x in v)
        if k not in seen: seen.add(k); out.append(tuple(MQ.of(x) for x in v))
    return out


def cube(d): return uniq(itertools.product((HALF, -HALF), repeat=d))


def orthoplex(d):
    out = []
    for i in range(d):
        for g in (1, -1):
            v = [MQ(0)] * d; v[i] = MQ(g); out.append(tuple(v))
    return out


def simplex(d):
    c = MQ(2) if d == 4 else MQ(1)
    a = c * (1 - MQ.sqrt(d + 1)) / d
    V = []
    for i in range(d):
        v = [MQ(0)] * d; v[i] = c; V.append(v)
    V.append([a] * d)
    cen = [sum((v[k] for v in V), MQ(0)) / (d + 1) for k in range(d)]
    return [tuple(v[k] - cen[k] for k in range(d)) for v in V]


def c24():
    out = []
    for i, j in itertools.combinations(range(4), 2):
        for a in (1, -1):
            for b in (1, -1):
                v = [MQ(0)] * 4; v[i] = MQ(a); v[j] = MQ(b); out.append(tuple(v))
    return out


def c600():
    out = list(cube(4)) + orthoplex(4)
    base = (PHI / 2, HALF, IPHI / 2, MQ(0))
    for p in even_perms(4):
        for v in signs(base):
            out.append(tuple(v[p[k]] for k in range(4)))
    return uniq(out)


def facets_float(Vf):
    """facets of the convex hull (vertex index sets), merging coplanar hull simplices"""
    from scipy.spatial import ConvexHull
    h = ConvexHull(Vf)
    seen, out = set(), []
    for eq in h.equations:
        n, b = eq[:-1], -eq[-1]
        F = tuple(np.nonzero(Vf @ n >= b - 1e-7)[0].tolist())
        if F not in seen: seen.add(F); out.append(list(F))
    return out, h.volume


def dual_of(V, facets):
    """polar dual: vertices m_F / b_F with m_F = sum of the facet's vertices, b_F = m_F . v"""
    out = []
    for F in facets:
        m = [sum((V[i][k] for i in F), MQ(0)) for k in range(len(V[0]))]
        b = sum((m[k] * V[F[0]][k] for k in range(len(m))), MQ(0))
        out.append(tuple(x / b for x in m))
    return out


def build(pid, cache):
    name, d = NAMES[pid]
    if pid == 'c8': V = cube(4)
    elif pid in ('hc5', 'hc6'): V = cube(d)
    elif pid in ('c16', 'op5', 'op6'): V = orthoplex(d)
    elif pid in ('c5', 'sx5', 'sx6'): V = simplex(d)
    elif pid == 'c24': V = c24()
    elif pid == 'c600': V = c600()
    elif pid == 'c120':
        P6 = cache['c600']; V = dual_of(P6['Vx'], P6['facets'])
    else: raise ValueError(pid)
    Vf = np.array([[float(x) for x in v] for v in V])
    facets, vol = facets_float(Vf)
    # edges: pairs at the minimum distance
    D2 = ((Vf[:, None, :] - Vf[None, :, :]) ** 2).sum(-1); np.fill_diagonal(D2, np.inf)
    e2 = D2.min(); I, J = np.nonzero(np.triu(D2 <= e2 * (1 + 1e-9), 1))
    edges = [[int(i), int(j)] for i, j in zip(I, J)]
    E2 = sum(((V[edges[0][0]][k] - V[edges[0][1]][k]) ** 2 for k in range(d)), MQ(0))
    return dict(id=pid, name=name, dim=d, Vx=V, Vf=Vf, facets=facets, edges=edges, E2=E2, volume=vol)


def check(P, full=True):
    """exact self-check (see the module docstring); returns the exact normals and offsets"""
    V, d = P['Vx'], P['dim']
    for i, j in P['edges']:
        assert sum(((V[i][k] - V[j][k]) ** 2 for k in range(d)), MQ(0)) == P['E2'], 'edge length'
    Ms, Bs = [], []
    for F in P['facets']:
        m = [sum((V[i][k] for i in F), MQ(0)) for k in range(d)]
        b = sum((m[k] * V[F[0]][k] for k in range(d)), MQ(0))
        if full:
            Fs = set(F)
            for i, v in enumerate(V):
                t = sum((m[k] * v[k] for k in range(d)), MQ(0))
                if i in Fs: assert t == b, 'facet vertex off its hyperplane'
                else: assert t < b, 'vertex outside a facet half-space'
        Ms.append(m); Bs.append(b)
    return Ms, Bs


def float_data(P, Ms, Bs):
    Vf = P['Vf']; N = np.array([[float(x) for x in m] for m in Ms]); B = np.array([float(b) for b in Bs])
    nn = np.linalg.norm(N, axis=1); N /= nn[:, None]; B /= nn
    return dict(N=N.round(15).tolist(), beta=B.round(15).tolist(), inradius=float(B.min()), inradius_max=float(B.max()),
                circumradius=float(np.linalg.norm(Vf, axis=1).max()), edge=float(math.sqrt(float(P['E2']))))


def main(full=True):
    out, cache = {}, {}
    for pid in ['c5', 'c8', 'c16', 'c24', 'c600', 'c120', 'sx5', 'hc5', 'op5', 'sx6', 'hc6', 'op6']:
        P = build(pid, cache); cache[pid] = P
        Ms, Bs = check(P, full=full)
        fd = float_data(P, Ms, Bs)
        assert abs(fd['inradius'] - fd['inradius_max']) < 1e-12, 'not tangential'
        fv = (len(P['Vx']), len(P['edges']), len(P['facets']))
        print(f"{pid:5s} {P['name']:12s} d={P['dim']} vertices {fv[0]} edges {fv[1]} facets {fv[2]}  edge {fd['edge']:.6f} "
              f"inradius {fd['inradius']:.6f} circumradius {fd['circumradius']:.6f} R/r {fd['circumradius'] / fd['inradius']:.4f} volume {P['volume']:.6f}", flush=True)
        out[pid] = dict(id=pid, name=P['name'], dim=P['dim'], dual=DUAL[pid], V=[[repr(x) for x in v] for v in P['Vx']],
                        Vf=P['Vf'].round(15).tolist(), facets=P['facets'], edges=P['edges'], edge2=repr(P['E2']),
                        volume=P['volume'], **{k: fd[k] for k in ('N', 'beta', 'inradius', 'circumradius', 'edge')})
    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'kB')


# exact edge lengths (EDGE^2 = edge2 exactly, EDGE > 0; checked by certify_nd.py through mu^2 edge(C)^2 = edge(P)^2)
EDGE = {'c5': '2*sqrt2', 'c8': '1', 'c16': 'sqrt2', 'c24': 'sqrt2', 'c600': '-1/2+1/2*sqrt5', 'c120': '7-3*sqrt5',
        'sx5': 'sqrt2', 'hc5': '1', 'op5': 'sqrt2', 'sx6': 'sqrt2', 'hc6': '1', 'op6': 'sqrt2'}


def mu_of(piece, container):
    """edge(piece) / edge(container polytope), exactly, as a string of multiquad.py"""
    return repr(M.parse(EDGE[piece]) / M.parse(EDGE[container]))


def load():
    return json.load(open(OUT))


if __name__ == '__main__':
    main(full='--fast' not in sys.argv)
