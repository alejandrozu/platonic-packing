#!/usr/bin/env python3
"""Proof-grade certificate for a packing of regular polytopes in 4, 5 or 6 dimensions (standard library only).
usage: python3 certify_nd.py record.json

What is proved (15 Oct 2026). Let P and C be the piece and container polytopes of src/polytopes_nd.json, given exactly:
every vertex coordinate is an element of Q(sqrt2, sqrt3, sqrt5, sqrt7) (multiquad.py), every facet a list of vertex
indices. Then:

  (0) P and C are what they claim to be, checked exactly: all edges have the same length; for every listed facet, the
      exact normal m (the sum of the facet's vertices, the polytope being centred at the origin) satisfies m.v = b on
      the facet's vertices and m.v < b on all other vertices, the facet's vertices span a hyperplane (affine rank
      d - 1), the facets are distinct and their number is the facet count of that regular polytope (so the list is
      every facet, and C = {x : m_f . x <= b_f for all f}); the edge ratio mu = edge(P) / edge(C) is given exactly
      (mu > 0 and mu^2 edge(C)^2 = edge(P)^2 exactly);
  (1) each piece c_i + R_i P, R_i = D_i (I - S_i)^-1 (I + S_i) with S_i a rational skew-symmetric matrix and D_i a
      diagonal sign matrix of determinant 1 (so R_i is exactly a rotation), lies in the interior of the container
      cc + s_full mu C (container edge = s_full x piece edge): every vertex strictly inside every facet half-space;
  (2) any two pieces are disjoint: for every pair whose centres are closer than twice an upper bound of the
      circumradius, the record gives a rational vector u and a rational t with u.x < t on every vertex of one piece
      and u.x > t on every vertex of the other; the other pairs are farther apart than the sum of their circumradii.

(1) and (2) are decided with rigorous interval arithmetic (fixed-point integers with outward rounding) on enclosures
of the exact coordinates; floating point only produced the record, so a bad record can fail, never pass. A whole
piece is shown inside a facet half-space at once when its circumscribed ball is (with intervals); otherwise vertex by
vertex. Exit code 0 iff CERTIFIED."""
import json, os, sys, time, itertools
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import multiquad as MQM
MQ = MQM.MQ

K = 170
ONE = 1 << K
FACETS = {'c5': 5, 'c8': 8, 'c16': 16, 'c24': 24, 'c120': 120, 'c600': 600, 'sx5': 6, 'hc5': 10, 'op5': 32,
          'sx6': 7, 'hc6': 12, 'op6': 64}          # facet counts of the regular polytopes (Coxeter, Regular Polytopes)


def fx(q):
    if isinstance(q, MQ): lo, hi = q.enclose(K + 24)
    else: lo = hi = Fr(q)
    return (lo.numerator * ONE // lo.denominator, -(-hi.numerator * ONE // hi.denominator))


def fadd(a, b): return (a[0] + b[0], a[1] + b[1])
def fsub(a, b): return (a[0] - b[1], a[1] - b[0])


def fmul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p) >> K, -((-max(p)) >> K))


def fdot(u, v):
    s = (0, 0)
    for a, b in zip(u, v): s = fadd(s, fmul(a, b))
    return s


def mq_rank(rows):
    """exact rank of a list of vectors over Q(sqrt2, sqrt3, sqrt5, sqrt7)"""
    M = [list(r) for r in rows]; rank = 0; ncol = len(M[0]) if M else 0
    for c in range(ncol):
        piv = next((r for r in range(rank, len(M)) if M[r][c].sign() != 0), None)
        if piv is None: continue
        M[rank], M[piv] = M[piv], M[rank]
        inv = M[rank][c].inv()
        for r in range(len(M)):
            if r != rank and M[r][c].sign() != 0:
                f = M[r][c] * inv
                M[r] = [x - f * y for x, y in zip(M[r], M[rank])]
        rank += 1
    return rank


class Poly:
    def __init__(self, D, pid, check=True):
        p = D[pid]; self.id = pid; self.d = d = p['dim']
        self.V = [[MQM.parse(x) for x in v] for v in p['V']]
        self.facets = p['facets']; self.edges = p['edges']
        self.E2 = MQM.parse(p['edge2'])
        self.M, self.B = [], []
        msg = []
        for i, j in self.edges:
            assert sum(((self.V[i][k] - self.V[j][k]) ** 2 for k in range(d)), MQ(0)) == self.E2, 'edge lengths differ'
        msg.append(f'{len(self.edges)} edges of equal length')
        seen = set()
        for F in self.facets:
            m = [sum((self.V[i][k] for i in F), MQ(0)) for k in range(d)]
            b = sum((m[k] * self.V[F[0]][k] for k in range(d)), MQ(0))
            if check:
                Fs = set(F)
                for i, v in enumerate(self.V):
                    t = sum((m[k] * v[k] for k in range(d)), MQ(0))
                    if i in Fs: assert t == b, 'facet vertex off the facet hyperplane'
                    else: assert t < b, 'vertex outside a facet half-space'
                assert mq_rank([[self.V[i][k] - self.V[F[0]][k] for k in range(d)] for i in F[1:]]) == d - 1, 'facet not spanning'
            key = tuple(sorted(F)); assert key not in seen, 'repeated facet'; seen.add(key)
            self.M.append(m); self.B.append(b)
        assert len(self.facets) == FACETS[pid], 'facet count differs from the regular polytope'
        msg.append(f'{len(self.facets)} = all facets, each supporting and spanning (exact)')
        self.check = f"{p['name']} ({d}D, {len(self.V)} vertices): " + ', '.join(msg)
        self.Vi = [tuple(fx(c) for c in v) for v in self.V]
        self.R2up = max(sum(fmul(c, c)[1] for c in v) for v in self.Vi)          # circumradius^2, upper (fixed point)
        self.Mi = [tuple(fx(c) for c in m) for m in self.M]
        self.Bi = [fx(b) for b in self.B]
        self.M2 = [sum(fmul(c, c)[1] for c in m) for m in self.Mi]               # |m|^2 upper


def frac(x):
    """a JSON number is the exact rational it denotes; a string may be any rational 'p/q'"""
    return Fr(x)


def cayley(S, Dg):
    """exact D (I - S)^-1 (I + S) over Q"""
    d = len(Dg)
    A = [[(Fr(1) if a == b else Fr(0)) - S[a][b] for b in range(d)] + [(Fr(1) if a == b else Fr(0)) + S[a][b] for b in range(d)]
         for a in range(d)]
    for c in range(d):
        p = next(r for r in range(c, d) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [x / pv for x in A[c]]
        for r in range(d):
            if r != c and A[r][c] != 0:
                f = A[r][c]; A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [[Dg[a] * A[a][d + b] for b in range(d)] for a in range(d)]


_POLY = {}


def poly(pid):
    """each polytope is checked exactly once per process (the check is printed with every certificate)"""
    if pid not in _POLY:
        D = json.load(open(os.path.join(HERE, 'src', 'polytopes_nd.json')))
        _POLY[pid] = Poly(D, pid)
    return _POLY[pid]


def main(fn):
    t0 = time.time()
    rec = json.load(open(fn))
    P = poly(rec['piece']); C = P if rec['container'] == rec['piece'] else poly(rec['container'])
    d = P.d; n = rec['n']; m = d * (d - 1) // 2
    assert C.d == d == rec['dim'], 'dimension'
    print('polytope check:', P.check)
    if C is not P: print('polytope check:', C.check)
    mu = MQM.parse(rec['mu']) if isinstance(rec['mu'], str) else MQ(Fr(rec['mu']))
    assert mu > 0 and mu * mu * C.E2 == P.E2, 'mu is not edge(P) / edge(C)'
    print(f"edge ratio mu = {rec['mu']} = edge(piece) / edge(container polytope), exact")
    s = frac(rec['s_full']); cc = [frac(x) for x in rec.get('container_center', [0] * d)]
    pcs = rec['pieces']; assert len(pcs) == n, 'piece count'
    cs, Rs = [], []
    for p in pcs:
        c = [frac(x) for x in p[:d]]; Sv = [frac(x) for x in p[d:d + m]]; Dg = [int(x) for x in p[d + m:d + m + d]]
        assert all(x in (1, -1) for x in Dg) and Dg.count(-1) % 2 == 0, 'D must be a sign matrix of determinant 1'
        S = [[Fr(0)] * d for _ in range(d)]; t = 0
        for a in range(d):
            for b in range(a + 1, d): S[a][b] = Sv[t]; S[b][a] = -Sv[t]; t += 1
        cs.append(c); Rs.append(cayley(S, Dg))
    Rf = [[[fx(e) for e in row] for row in R] for R in Rs]
    cf = [[fx(x) for x in c] for c in cs]
    ok = True
    # (1) containment: m_f . (x - cc) < s mu b_f  for x = c + R v
    smu = fmul(fx(s), fx(mu))
    ccf = [fx(x) for x in cc]
    R2 = P.R2up
    worst = None; whole = vert = 0
    for i in range(n):
        rel = [fsub(cf[i][k], ccf[k]) for k in range(d)]
        for f in range(len(C.M)):
            mf = C.Mi[f]
            bound = fsub(fmul(smu, C.Bi[f]), fdot(mf, rel))            # s mu b - m.(c - cc)
            if bound[0] > 0:
                b2 = fmul(bound, bound)[0]
                if b2 > ((C.M2[f] * R2) >> K) + 2: whole += 1; continue  # circumscribed ball inside (|m|^2 R^2 < bound^2)
            w = [fdot([Rf[i][a][k] for a in range(d)], mf) for k in range(d)]   # R^T m
            hmax = max(fdot(w, v)[1] for v in P.Vi)
            slack = bound[0] - hmax
            vert += 1
            if worst is None or slack < worst: worst = slack
            if slack <= 0: ok = False
    print(f'containment: {n} pieces x {len(C.M)} facets; {whole} piece/facet pairs by the circumscribed ball, {vert} vertex '
          f'by vertex, smallest slack >= {(worst if worst is not None else 0) / ONE:.3e} (times |normal|)' + ('' if ok else '  FAILED'))
    # (2) disjointness
    planes = {}
    for pl in rec.get('planes', []):
        i, j = int(pl[0]), int(pl[1]); planes[(min(i, j), max(i, j))] = (i, j, [frac(x) for x in pl[2:2 + d]], frac(pl[2 + d]))
    lim = 4 * R2
    near = far = 0; margin = None; failed = []
    for i in range(n):
        for j in range(i + 1, n):
            dd = [fsub(cf[i][k], cf[j][k]) for k in range(d)]
            d2 = fdot(dd, dd)
            if d2[0] > lim: far += 1; continue
            near += 1
            if (i, j) not in planes: ok = False; failed.append((i, j)); continue
            a, b, u, t = planes[(i, j)]
            uf = [fx(x) for x in u]; tf = fx(t)
            wa = [fdot([Rf[a][r][k] for r in range(d)], uf) for k in range(d)]
            wb = [fdot([Rf[b][r][k] for r in range(d)], uf) for k in range(d)]
            ua, ub = fdot(uf, cf[a]), fdot(uf, cf[b])
            amax = ua[1] + max(fdot(wa, v)[1] for v in P.Vi)                 # max over piece a of u.x (upper)
            bmin = ub[0] + min(fdot(wb, v)[0] for v in P.Vi)                 # min over piece b of u.x (lower)
            if amax < tf[0] and bmin > tf[1]:
                g = min(tf[0] - amax, bmin - tf[1]); margin = g if margin is None else min(margin, g)
            else:
                ok = False; failed.append((i, j))
    print(f'disjointness: {near} near pairs separated by explicit rational hyperplanes (smallest margin >= '
          f'{(margin or 0) / ONE:.3e} along the normal), {far} pairs farther apart than twice the circumradius'
          + (f'  FAILED for {failed[:10]}' if failed else ''))
    print(f"{'CERTIFIED' if ok else 'NOT CERTIFIED'}: {n} x {rec['piece']} in s = {rec['s_full']} x {rec['container']} "
          f"({d}D, {time.time() - t0:.1f}s)")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(max(main(f) for f in sys.argv[1:]))
