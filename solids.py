"""Exact unit-edge Platonic solids (standard library only).

Every coordinate is an exact element of Q(sqrt2, sqrt5): the cube is rational, the tetrahedron and octahedron live in
Q(sqrt 2), the dodecahedron and icosahedron in Q(sqrt 5) (golden ratio phi = (1 + sqrt 5)/2).
Signs are decided exactly, so every geometric statement made with these numbers (edge lengths, which vertices
lie on which face plane, which side of a plane a point is on) is a proof, not a floating-point estimate.

Faces are not typed in by hand: they are *derived* by brute force over vertex triples (a triple spans a face plane
iff every vertex lies weakly on one side of it), and `self_check` then confirms, exactly,
  * every edge (pair of vertices at minimum distance) has squared length 1,
  * the face/edge/vertex counts are those of the solid and V - E + F = 2,
  * every face is a regular polygon of the right size whose vertices are coplanar, its plane supports the solid,
  * the face list is complete: every edge lies on exactly two listed faces (a closed surface),
  * all faces are at the same distance from the centre (the solid has an insphere centred at the origin).
Each solid is centred at the origin.
"""
from fractions import Fraction as Fr
from itertools import combinations, product

__all__ = ['QF', 'SOLIDS', 'solid', 'self_check']


def _s2(a, b):
    """Exact sign of a + b sqrt2 (a, b rational)."""
    if b == 0: return (a > 0) - (a < 0)
    if a >= 0 and b >= 0: return 1
    if a <= 0 and b <= 0: return -1
    return (1 if a > 0 else -1) if a * a > 2 * b * b else (1 if b > 0 else -1)   # a^2 != 2 b^2 (sqrt2 irrational)


class QF:
    """Exact element a + b sqrt2 + c sqrt5 + d sqrt10 of the field Q(sqrt2, sqrt5) (a, b, c, d rational).
    It contains every coordinate needed here: Q (cube), Q(sqrt2) (tetrahedron, octahedron), Q(sqrt5) (dodecahedron,
    icosahedron) and mixed products. Constructor: QF(a) rational, QF(a, b, 2) = a + b sqrt2, QF(a, b, 5) = a + b sqrt5.
    Sign: write x = p + q sqrt5 with p, q in Q(sqrt2); if p, q have the same sign that is the sign of x, otherwise
    it is the sign of whichever of p^2 and 5 q^2 is larger -- an exact comparison in Q(sqrt2) (equality is impossible
    because sqrt5 is not in Q(sqrt2))."""
    __slots__ = ('a', 'b', 'c', 'd')

    def __init__(self, a, b=0, d=0, _raw=None):
        if _raw is not None:
            self.a, self.b, self.c, self.d = _raw; return
        a, b = Fr(a), Fr(b)
        z = Fr(0)
        if b == 0 or d == 0: self.a, self.b, self.c, self.d = a, z, z, z
        elif d == 2: self.a, self.b, self.c, self.d = a, b, z, z
        elif d == 5: self.a, self.b, self.c, self.d = a, z, b, z
        elif d == 10: self.a, self.b, self.c, self.d = a, z, z, b
        else: raise ValueError(f'sqrt{d} not supported')

    @staticmethod
    def _c(o): return o if isinstance(o, QF) else QF(o)

    def __add__(s, o):
        o = QF._c(o); return QF(None, _raw=(s.a + o.a, s.b + o.b, s.c + o.c, s.d + o.d))
    __radd__ = __add__

    def __neg__(s): return QF(None, _raw=(-s.a, -s.b, -s.c, -s.d))

    def __sub__(s, o): return s + (-QF._c(o))

    def __rsub__(s, o): return (-s) + o

    def __mul__(s, o):
        if not isinstance(o, QF):
            o = Fr(o); return QF(None, _raw=(s.a * o, s.b * o, s.c * o, s.d * o))
        # (p1 + q1 sqrt5)(p2 + q2 sqrt5) with p = a + b sqrt2, q = c + d sqrt2
        def m2(x0, x1, y0, y1): return (x0 * y0 + 2 * x1 * y1, x0 * y1 + x1 * y0)
        pp = m2(s.a, s.b, o.a, o.b); qq = m2(s.c, s.d, o.c, o.d)
        pq = m2(s.a, s.b, o.c, o.d); qp = m2(s.c, s.d, o.a, o.b)
        return QF(None, _raw=(pp[0] + 5 * qq[0], pp[1] + 5 * qq[1], pq[0] + qp[0], pq[1] + qp[1]))
    __rmul__ = __mul__

    def sign(s):
        sp, sq = _s2(s.a, s.b), _s2(s.c, s.d)
        if sq == 0: return sp
        if sp == 0 or sp == sq: return sq if sp == 0 else sp
        # p^2 - 5 q^2 in Q(sqrt2)
        p2 = (s.a * s.a + 2 * s.b * s.b, 2 * s.a * s.b); q2 = (s.c * s.c + 2 * s.d * s.d, 2 * s.c * s.d)
        return sp if _s2(p2[0] - 5 * q2[0], p2[1] - 5 * q2[1]) > 0 else sq

    @property
    def field(s):
        """Smallest of 1, 2, 5, 10 (meaning Q, Q(sqrt2), Q(sqrt5), Q(sqrt2, sqrt5)) containing this number."""
        r2, r5 = bool(s.b or s.d), bool(s.c or s.d)
        return 10 if (r2 and r5) or s.d else 2 if r2 else 5 if r5 else 1

    def __float__(s): return float(s.a) + float(s.b) * 2 ** 0.5 + float(s.c) * 5 ** 0.5 + float(s.d) * 10 ** 0.5

    def __eq__(s, o): return (s - o).sign() == 0
    def __lt__(s, o): return (s - o).sign() < 0
    def __le__(s, o): return (s - o).sign() <= 0
    def __gt__(s, o): return (s - o).sign() > 0
    def __ge__(s, o): return (s - o).sign() >= 0
    def __hash__(s): return hash((s.a, s.b, s.c, s.d))

    def __repr__(s):
        t = [f'{v}' + n for v, n in ((s.a, ''), (s.b, '*sqrt2'), (s.c, '*sqrt5'), (s.d, '*sqrt10')) if v]
        return '(' + ' + '.join(t) + ')' if len(t) > 1 else (t[0] if t else '0')


def dot(u, v): return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
def sub(u, v): return (u[0] - v[0], u[1] - v[1], u[2] - v[2])
def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _cyc(p):  # the three cyclic permutations of a 3-tuple
    return [p, (p[1], p[2], p[0]), (p[2], p[0], p[1])]


def _vertices(name):
    if name == 'cube':  # (+-1/2)^3
        return [tuple(QF(Fr(s, 2)) for s in g) for g in product((1, -1), repeat=3)]
    if name == 'tetrahedron':  # (sqrt2/4)(s1,s2,s3), s1 s2 s3 = +1 ; edge = (sqrt2/4)*2*sqrt2 = 1
        return [tuple(QF(0, Fr(s, 4), 2) for s in g) for g in product((1, -1), repeat=3) if g[0] * g[1] * g[2] == 1]
    if name == 'octahedron':  # +-(sqrt2/2) e_i ; edge = (sqrt2/2)*sqrt2 = 1
        V = []
        for i in range(3):
            for s in (1, -1):
                V.append(tuple(QF(0, Fr(s, 2), 2) if k == i else QF(0) for k in range(3)))
        return V
    if name == 'icosahedron':  # (1/2)(0, +-1, +-phi) and cyclic ; edge 1
        h = QF(Fr(1, 2)); hp = QF(Fr(1, 4), Fr(1, 4), 5)  # 1/2, phi/2
        return [p for s1, s2 in product((1, -1), repeat=2) for p in _cyc((QF(0), s1 * h, s2 * hp))]
    if name == 'dodecahedron':  # (phi/2)(+-1,+-1,+-1) and (phi/2)(0, +-1/phi, +-phi) cyclic ; edge 1
        hp = QF(Fr(1, 4), Fr(1, 4), 5)            # phi/2
        h = QF(Fr(1, 2))                           # (phi/2)(1/phi) = 1/2
        hpp = QF(Fr(3, 4), Fr(1, 4), 5)           # (phi/2) phi = phi^2/2 = (3 + sqrt5)/4
        V = [tuple(s * hp for s in g) for g in product((1, -1), repeat=3)]
        V += [p for s1, s2 in product((1, -1), repeat=2) for p in _cyc((QF(0), s1 * h, s2 * hpp))]
        return V
    raise KeyError(name)


FIELD = {'cube': 1, 'tetrahedron': 2, 'octahedron': 2, 'dodecahedron': 5, 'icosahedron': 5}   # sqrt needed
COUNTS = {'tetrahedron': (4, 6, 4, 3), 'cube': (8, 12, 6, 4), 'octahedron': (6, 12, 8, 3),
          'dodecahedron': (20, 30, 12, 5), 'icosahedron': (12, 30, 20, 3)}   # V, E, F, vertices per face
SOLIDS = list(COUNTS)


class Solid:
    """Exact solid: vertices V (tuples of QF), edges (index pairs), faces (cyclically ordered index lists, CCW seen
    from outside), and for each face an exact outward normal m_f and offset beta_f = m_f . v (any v on the face),
    so that the solid is exactly {x : m_f . x <= beta_f for all f}."""

    def __init__(self, name):
        self.name = name; self.field = FIELD[name]
        V = self.V = _vertices(name)
        n = len(V)
        d2 = {(i, j): dot(sub(V[i], V[j]), sub(V[i], V[j])) for i, j in combinations(range(n), 2)}
        m = min(d2.values())
        self.edges = sorted(p for p, v in d2.items() if v == m)
        self.edge2 = m
        faces = {}
        Vf = [[float(c) for c in v] for v in V]
        for i, j, k in combinations(range(n), 3):
            # float prescreen: skip triples whose plane clearly cuts the solid. Unsound only in the direction of
            # *missing* a face, which the exact completeness check in check() (every edge on two faces) catches.
            a = [Vf[j][t] - Vf[i][t] for t in range(3)]; b = [Vf[k][t] - Vf[i][t] for t in range(3)]
            nf = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
            sf = [sum(nf[t] * (Vf[q][t] - Vf[i][t]) for t in range(3)) for q in range(n)]
            if max(sf) > 1e-9 and min(sf) < -1e-9: continue
            nrm = cross(sub(V[j], V[i]), sub(V[k], V[i]))
            if all(c == 0 for c in nrm): continue
            side = [dot(nrm, sub(V[t], V[i])).sign() for t in range(n)]
            if all(s <= 0 for s in side) or all(s >= 0 for s in side):
                if all(s >= 0 for s in side): nrm = tuple(-c for c in nrm)
                on = frozenset(t for t in range(n) if side[t] == 0)
                faces.setdefault(on, nrm)
        self.faces, self.normals, self.beta = [], [], []
        for on, nrm in faces.items():
            idx = sorted(on)
            # order the face vertices cyclically (CCW seen from outside): walk along polytope edges
            es = [e for e in self.edges if e[0] in on and e[1] in on]
            loop = [idx[0]]
            while len(loop) < len(idx):
                nxt = [b if a == loop[-1] else a for a, b in es if loop[-1] in (a, b)]
                nxt = [t for t in nxt if t not in loop]
                if len(loop) == 1:  # choose direction so that the loop is CCW about the outward normal
                    a, b = nxt[0], nxt[1]
                    # (v1 - v0) x (v_last - v0) . n > 0 for a CCW loop v0, v1, ..., v_last
                    if dot(cross(sub(V[a], V[loop[0]]), sub(V[b], V[loop[0]])), nrm).sign() > 0:
                        nxt = [a]
                    else:
                        nxt = [b]
                loop.append(nxt[0])
            self.faces.append(loop); self.normals.append(nrm); self.beta.append(dot(nrm, V[loop[0]]))

    # ---- exact self-check ----------------------------------------------------------------------------------
    def check(self):
        V, E, F, k = COUNTS[self.name]
        assert len(self.V) == V and len(self.edges) == E and len(self.faces) == F, 'counts'
        assert V - E + F == 2
        assert self.edge2 == 1, 'edge length is not exactly 1'
        for f, (loop, m, b) in enumerate(zip(self.faces, self.normals, self.beta)):
            assert len(loop) == k
            for t, v in enumerate(self.V):           # face plane supports the solid; exactly the loop lies on it
                s = (dot(m, v) - b).sign()
                assert (s == 0) == (t in loop) and s <= 0
            for a, c in zip(loop, loop[1:] + loop[:1]):   # consecutive face vertices are joined by an edge
                assert (min(a, c), max(a, c)) in self.edges
        # completeness: every edge lies on exactly two of the listed faces, so the listed faces form a closed surface,
        # i.e. they are all the facets (the solid equals the intersection of their half-spaces)
        for e in self.edges:
            on = sum(1 for loop in self.faces if any({a, c} == set(e) for a, c in zip(loop, loop[1:] + loop[:1])))
            assert on == 2, f'edge {e} lies on {on} faces'
        # insphere: distance from origin to every face plane is the same: beta_f^2 / |m_f|^2 constant, beta_f > 0
        r2 = [b * b * _inv(dot(m, m)) for m, b in zip(self.normals, self.beta)]
        assert all(b.sign() > 0 for b in self.beta) and all(x == r2[0] for x in r2)
        self.inradius2 = r2[0]
        # every vertex is at the same distance from the centre
        R2 = [dot(v, v) for v in self.V]
        assert all(x == R2[0] for x in R2)
        self.circumradius2 = R2[0]
        return True

    # ---- floats for the simulator --------------------------------------------------------------------------
    def float_data(self):
        V = [[float(c) for c in v] for v in self.V]
        N = []
        for m in self.normals:
            mf = [float(c) for c in m]; l = sum(c * c for c in mf) ** 0.5; N.append([c / l for c in mf])
        rho = float(self.inradius2) ** 0.5
        return dict(name=self.name, V=V, faces=self.faces, normals=N, inradius=rho,
                    circumradius=float(self.circumradius2) ** 0.5, edges=[list(e) for e in self.edges],
                    volume=_volume(V, self.faces, N, rho))


def _inv(x):
    """Exact inverse in Q(sqrt2, sqrt5): 1/(p + q sqrt5) = (p - q sqrt5)/(p^2 - 5 q^2), then invert in Q(sqrt2)."""
    conj5 = QF(None, _raw=(x.a, x.b, -x.c, -x.d))
    n = x * conj5                                   # lies in Q(sqrt2)
    den = n.a * n.a - 2 * n.b * n.b                 # 1/(u + v sqrt2) = (u - v sqrt2)/(u^2 - 2 v^2)
    return conj5 * QF(n.a / den, -n.b / den, 2)


def _volume(V, faces, N, rho):
    # sum over faces of (1/3) * area * inradius
    tot = 0.0
    for loop in faces:
        p0 = V[loop[0]]
        for a, b in zip(loop[1:-1], loop[2:]):
            u = [V[a][i] - p0[i] for i in range(3)]; w = [V[b][i] - p0[i] for i in range(3)]
            c = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
            tot += 0.5 * sum(x * x for x in c) ** 0.5 * rho / 3
    return tot


_cache = {}


def solid(name):
    if name not in _cache:
        s = Solid(name); s.check(); _cache[name] = s
    return _cache[name]


def self_check():
    out = []
    for name in SOLIDS:
        s = solid(name)
        out.append(f'{name:13s} V={len(s.V):2d} E={len(s.edges):2d} F={len(s.faces):2d}  edge^2 = {s.edge2}  '
                   f'inradius^2 = {s.inradius2}  circumradius^2 = {s.circumradius2}')
    return out


if __name__ == '__main__':
    import json, sys
    for line in self_check(): print(line)
    if len(sys.argv) > 1:
        json.dump({n: solid(n).float_data() for n in SOLIDS}, open(sys.argv[1], 'w'), indent=1)
        print('wrote', sys.argv[1])
