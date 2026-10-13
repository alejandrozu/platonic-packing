#!/usr/bin/env python3
"""Exact algebraic data for every solid of the search: src/solids_exact.json (used by certify_general.py).

For each solid a number field Q(alpha) (minimal polynomial and a rational isolating interval) and, for every vertex,
its coordinates as exact elements of Q(alpha), possibly times one common positive scale lambda = 1/sqrt(D) with D in
Q(alpha) (only the snub solids and their duals need it). The coefficients are found by integer relation detection
(PSLQ) on 60-digit coordinates; they are then *proved* right by exact arithmetic in Q(alpha) (algebraic.py): every
face is planar, every face plane supports the solid strictly, every edge lies on two faces, all edges have the same
length (D, or 1 when lambda = 1) for the Archimedean solids, prisms and antiprisms, every face touches the same sphere
for the Catalan solids, and the exact solid matches src/solids.json (the float solid used by the search and the
records) to 1e-12. A wrong coefficient cannot survive these checks.
usage: python3 scripts/exact_solids.py [name,...]"""
import json, os, sys, time
from fractions import Fraction as Fr
import mpmath as mp
import sympy as sp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import polyhedra, algebraic as A
from solids import solid as platonic_solid

mp.mp.dps = 60
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
OUT = os.path.join(ROOT, 'src', 'solids_exact.json')


def minpoly_ints(expr):
    x = sp.Symbol('x')
    mpoly = sp.Poly(sp.minimal_polynomial(expr, x), x)
    c = mpoly.all_coeffs()[::-1]
    den = sp.ilcm(*[sp.fraction(sp.nsimplify(k))[1] for k in c])
    return [int(k * den) for k in c]


def field_for(name):
    """(alpha as sympy expression, how to scale) for each solid."""
    s2, s3, s5 = sp.sqrt(2), sp.sqrt(3), sp.sqrt(5)
    phi = (1 + s5) / 2
    if name in ('cube',): return sp.Integer(1), None
    if name in ('tetrahedron', 'octahedron', 'truncated_tetrahedron', 'cuboctahedron', 'truncated_cube',
                'truncated_octahedron', 'rhombicuboctahedron', 'truncated_cuboctahedron', 'triakis_tetrahedron',
                'rhombic_dodecahedron', 'triakis_octahedron', 'tetrakis_hexahedron', 'deltoidal_icositetrahedron',
                'disdyakis_dodecahedron'): return s2, None
    if name in ('dodecahedron', 'icosahedron', 'icosidodecahedron', 'truncated_dodecahedron', 'truncated_icosahedron',
                'rhombicosidodecahedron', 'truncated_icosidodecahedron', 'rhombic_triacontahedron', 'triakis_icosahedron',
                'pentakis_dodecahedron', 'deltoidal_hexecontahedron', 'disdyakis_triacontahedron'): return phi, None
    if name in ('snub_cube', 'pentagonal_icositetrahedron'):
        t = sp.CRootOf(sp.Symbol('x') ** 3 - sp.Symbol('x') ** 2 - sp.Symbol('x') - 1, 0)
        return t, 'ref'
    if name in ('snub_dodecahedron', 'pentagonal_hexecontahedron'):
        x = sp.Symbol('x')
        roots = [r for r in sp.Poly(x ** 6 - 4 * x ** 4 - x ** 3 + 4 * x ** 2 + 2 * x - 1, x).all_roots() if r.is_real]
        xi_num = mp.findroot(lambda z: z ** 3 - 2 * z - (1 + mp.sqrt(5)) / 2, 1.7)
        xi = min(roots, key=lambda r: abs(float(r) - float(xi_num)))
        return xi, 'ref'
    if name in polyhedra.ELONGATED: return field_for(name.split('_')[0])     # same field: the height is rational
    if name in ('prism3', 'prism6'): return s3, None
    if name in ('prism5', 'antiprism5'): return 1 / (2 * sp.sin(sp.pi / 5)), None
    if name == 'prism8': return 1 / (2 * sp.sin(sp.pi / 8)), None
    if name == 'prism12': return 1 / (2 * sp.sin(sp.pi / 12)), None
    if name == 'antiprism4': return sp.root(2, 4), None
    if name == 'antiprism6': return sp.sqrt(s3 - 1), None
    if name in ('antiprism8', 'antiprism12'):
        k = int(name[9:])
        return sp.sqrt(1 - 1 / (4 * sp.cos(sp.pi / (2 * k)) ** 2)), None
    raise KeyError(name)


def hp_vertices(name):
    if name in ('tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron'):
        S = platonic_solid(name)
        return [[mp.mpf(float(c.a)) + mp.mpf(float(c.b)) * mp.sqrt(2) + mp.mpf(float(c.c)) * mp.sqrt(5) + mp.mpf(float(c.d)) * mp.sqrt(10)
                 for c in v] for v in S.V], S.faces
    S = polyhedra.build(name)
    return [list(p) for p in S.Vh], S.faces


def build(name):
    t0 = time.time()
    alpha_expr, scaling = field_for(name)
    if name in ('tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron'):
        # exact Platonic coordinates straight from solids.py (Q(sqrt2) or Q(sqrt5) with phi)
        S = platonic_solid(name)
        F = A.Field(*_field_args(alpha_expr))
        V = []
        for v in S.V:
            row = []
            for c in v:
                if F.d == 1: row.append(F.elem([c.a]))
                elif name in ('tetrahedron', 'octahedron'): row.append(F.elem([c.a, c.b]))      # a + b sqrt2
                else: row.append(F.elem([c.a - c.c, 2 * c.c]))                                  # a + c sqrt5 = (a - c) + 2c phi
            V.append(tuple(row))
        faces = S.faces; lam = None
    else:
        Vh, faces = hp_vertices(name)
        av = mp.mpf(sp.N(alpha_expr, 70))
        F = A.Field(*_field_args(alpha_expr))
        lam = None
        if scaling == 'ref':
            ref = min(abs(c) for v in Vh for c in v if abs(c) > mp.mpf(10) ** -30)
            if name in ('pentagonal_icositetrahedron', 'pentagonal_hexecontahedron'):
                arch = 'snub_cube' if name == 'pentagonal_icositetrahedron' else 'snub_dodecahedron'
                Va, _ = hp_vertices(arch)
                ref = min(abs(c) for v in Va for c in v if abs(c) > mp.mpf(10) ** -30)
            lam = ref
        basis = [av ** k for k in range(F.d)]
        cache = {}

        def coeffs(c):
            u = c / lam if lam is not None else c
            key = mp.nstr(u, 45)
            if key in cache: return cache[key]
            if abs(u) < mp.mpf(10) ** -40: cache[key] = F.zero(); return cache[key]
            rel = mp.pslq([u] + basis, maxcoeff=10 ** 9, maxsteps=10 ** 6)
            if rel is None or rel[0] == 0: raise RuntimeError(f'{name}: no relation for {mp.nstr(u, 20)}')
            e = F.elem([Fr(-r, rel[0]) for r in rel[1:]])
            approx = sum(mp.mpf(e[k].numerator) / e[k].denominator * basis[k] for k in range(F.d))
            assert abs(approx - u) < mp.mpf(10) ** -45, (name, 'relation inexact')
            cache[key] = e; return e
        V = [tuple(coeffs(c) for c in v) for v in Vh]
    D = None
    if lam is not None:
        # D = 1/lambda^2 in Q(alpha) (found by PSLQ, checked below through the edge lengths)
        av = mp.mpf(sp.N(alpha_expr, 70)); basis = [av ** k for k in range(F.d)]
        rel = mp.pslq([1 / lam ** 2] + basis, maxcoeff=10 ** 9, maxsteps=10 ** 6)
        D = F.elem([Fr(-r, rel[0]) for r in rel[1:]])
    checks = self_check(name, F, V, faces, D)
    # match with the float solid used by the search
    Ff = A.Field(F.p, F.lo, F.hi); Ff.refine(Fr(1, 2 ** 80))
    lamf = 1.0 if D is None else 1 / float(A.isqrt_interval(Ff.interval(D)).lo)
    Vf = [[float(Ff.interval(c).lo) * lamf for c in v] for v in V]
    Vs = SOL[name]['V']
    for v in Vs:
        assert min(max(abs(v[k] - w[k]) for k in range(3)) for w in Vf) < 1e-12, (name, 'does not match solids.json')
    assert len(Vs) == len(Vf)
    print(f'{name:28s} degree {F.d} {"lambda=1/sqrt(D)" if D else ""} {checks}  {time.time() - t0:.1f}s', flush=True)
    return {'minpoly': [str(c) for c in F.p], 'interval': [str(F.lo), str(F.hi)], 'D': None if D is None else [str(c) for c in D],
            'V': [[[str(c) for c in x] for x in v] for v in V], 'faces': faces, 'checks': checks}


def _field_args(alpha_expr):
    p = minpoly_ints(alpha_expr)
    a = mp.mpf(sp.N(alpha_expr, 70))
    lo, hi = Fr(mp.nstr(a - mp.mpf(10) ** -30, 50)), Fr(mp.nstr(a + mp.mpf(10) ** -30, 50))
    return p, lo, hi


def self_check(name, F, V, faces, D):
    """Exact checks in Q(alpha); returns a short summary string (raises on failure)."""
    n = len(V)
    edges = set()
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]): edges.add((min(a, b), max(a, b)))
    for e in edges:
        on = sum(1 for f in faces if any({a, b} == set(e) for a, b in zip(f, f[1:] + f[:1])))
        assert on == 2, (name, 'edge not on two faces')
    assert n - len(edges) + len(faces) == 2
    normals, offsets = [], []
    for f in faces:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]
        m = A.vcross(F, A.vsub(F, b, a), A.vsub(F, c, a)); beta = A.vdot(F, m, a)
        for i in range(n):
            s = F.sign(F.sub(A.vdot(F, m, V[i]), beta))
            if i in f: assert s == 0, (name, 'face not planar')
            else: assert s != 0, (name, 'vertex on a face plane')
        sides = {F.sign(F.sub(A.vdot(F, m, V[i]), beta)) for i in range(n) if i not in f}
        assert len(sides) == 1, (name, 'face plane does not support the solid')
        if sides == {1}: m = tuple(F.scale(x, -1) for x in m); beta = F.scale(beta, -1)
        normals.append(m); offsets.append(beta)
    L2 = [A.vdot(F, A.vsub(F, V[i], V[j]), A.vsub(F, V[i], V[j])) for i, j in sorted(edges)]
    uniform = all(F.is_zero(F.sub(x, L2[0])) for x in L2)
    out = f'V={n} E={len(edges)} F={len(faces)}: faces planar and supporting, closed surface'
    if name in polyhedra.CAT:
        # tangential: beta_f^2 / |m_f|^2 equal for all faces  <=>  beta_f^2 |m_g|^2 = beta_g^2 |m_f|^2
        b0, m0 = F.mul(offsets[0], offsets[0]), A.vdot(F, normals[0], normals[0])
        for m, b in zip(normals, offsets):
            assert F.is_zero(F.sub(F.mul(F.mul(b, b), m0), F.mul(b0, A.vdot(F, m, m)))), (name, 'not tangential')
        out += ', insphere (all faces equidistant)'
    elif name in polyhedra.ELONGATED:
        # base edges exactly 1, lateral edges exactly l
        l = Fr(polyhedra.ELONG_TXT[name.split('_')[1]])
        lens = {F.is_zero(F.sub(x, F.one())) or F.is_zero(F.sub(x, F.elem([l * l]))) for x in L2}
        assert lens == {True}, (name, 'edges not 1 and l')
        n_base = sum(1 for x in L2 if F.is_zero(F.sub(x, F.one())))
        assert n_base == 2 * (n // 2) and len(L2) - n_base == n // 2, (name, 'edge count')
        out += f', base edges exactly 1, lateral edges exactly {l}'
    else:
        assert uniform, (name, 'edges not all equal')
        target = D if D is not None else F.one()
        assert F.is_zero(F.sub(L2[0], target)), (name, 'edge length is not 1 (after scaling)')
        out += ', all edges exactly 1'
    return out


def main():
    names = list(SOL) if len(sys.argv) < 2 else sys.argv[1].split(',')
    data = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for name in names:
        data[name] = build(name)
        json.dump(data, open(OUT, 'w'))


if __name__ == '__main__':
    main()
