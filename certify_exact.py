#!/usr/bin/env python3
"""Exact certificate for a packing claim file (standard library only). Usage: python3 certify_exact.py claim.json

What it proves. Every number in the file is converted to an exact rational (Fraction(float) is exact). Each
quaternion q (not assumed unit) gives the rotation R = H(q)/|q|^2, where H is the homogeneous quaternion matrix; R is
exactly orthogonal with det 1 for every q != 0, so every piece is exactly congruent to the canonical unit-edge solid.
The canonical solids have coordinates in Q, Q(sqrt 2) or Q(sqrt 5) (solids.py, which re-derives and checks their
faces and unit edges exactly at import), so every vertex of every piece is an exact element of Q(sqrt2, sqrt5)^3 and
every sign below is decided exactly (solids.QF.sign). The script checks, with no rounding:
  (1) containment: every vertex x of every piece satisfies m_f . (x - centre) < s_full * beta_f for every face f of the
      container, where {y : m_f . y <= beta_f} are the exact face half-spaces of the canonical unit-edge container;
      as pieces and container are convex, each piece lies inside s_full * container (strictly);
  (2) disjointness: for every pair of pieces an explicit rational vector u is exhibited with
      max_{x in A} u . x  <  min_{y in B} u . y   (over vertices, which suffices by convexity), so the pair is strictly
      separated by a plane.
Hence the n pieces are pairwise disjoint unit-edge copies of the piece solid inside the container of edge s_full,
i.e. s_full is a rigorous upper bound for the smallest such container. Floating point is only used to *propose* the
vectors u (any proposal is checked exactly), so a wrong proposal can only make certification fail, never succeed.
Exit status 0 iff (1) and (2) hold."""
import json, sys, os, itertools, math
PLURAL = {'tetrahedron': 'tetrahedra', 'cube': 'cubes', 'octahedron': 'octahedra', 'dodecahedron': 'dodecahedra', 'icosahedron': 'icosahedra'}
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solids import solid, QF, dot

d = json.load(open(sys.argv[1]))
P, Cs = solid(d['piece']), solid(d['container'])
s = Fr(d['s_full']); cc = [Fr(v) for v in d.get('container_center', [0, 0, 0])]


def H(q):
    w, x, y, z = (Fr(v) for v in q); n = w * w + x * x + y * y + z * z
    M = [[w*w+x*x-y*y-z*z, 2*(x*y-w*z), 2*(x*z+w*y)], [2*(x*y+w*z), w*w-x*x+y*y-z*z, 2*(y*z-w*x)], [2*(x*z-w*y), 2*(y*z+w*x), w*w-x*x-y*y+z*z]]
    return [[e / n for e in row] for row in M]


pieces = []
for p in d['pieces']:
    c = [Fr(v) for v in p[:3]]; R = H(p[3:])
    pieces.append([tuple(QF(c[i]) + R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2] for i in range(3)) for v in P.V])
n = len(pieces)

# (1) containment, exactly
wall_ok, wall_min = True, None
for V in pieces:
    for x in V:
        y = tuple(x[i] - cc[i] for i in range(3))
        for m, b in zip(Cs.normals, Cs.beta):
            slack = s * b - dot(m, y)                     # exact, in Q(sqrt d)
            if slack.sign() <= 0: wall_ok = False
            g = float(slack) / math.sqrt(sum(float(c) ** 2 for c in m))
            wall_min = g if wall_min is None else min(wall_min, g)

# (2) a strictly separating rational plane for every pair, checked exactly
Vf = [[[float(c) for c in x] for x in V] for V in pieces]
def propose(A, B):
    """Float search over SAT axes for the best separating direction (A below B); returns a rational vector."""
    def axes(V):
        # face normals and edge directions of a piece, recovered from its float vertices
        out = []
        for loop in P.faces:
            a, b, c = (V[loop[0]], V[loop[1]], V[loop[2]])
            out.append(('f', [(b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]), (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]), (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])]))
        for i, j in P.edges: out.append(('e', [V[j][k] - V[i][k] for k in range(3)]))
        return out
    aa, bb = axes(A), axes(B)
    cand = [u for t, u in aa + bb if t == 'f']
    ea = [u for t, u in aa if t == 'e']; eb = [u for t, u in bb if t == 'e']
    cand += [[a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]] for a in ea for b in eb]
    best = None
    for u in cand:
        l = math.sqrt(sum(c * c for c in u))
        if l < 1e-12: continue
        u = [c / l for c in u]
        for sg in (1, -1):
            v = [sg * c for c in u]
            g = min(sum(v[k] * y[k] for k in range(3)) for y in B) - max(sum(v[k] * x[k] for k in range(3)) for x in A)
            if best is None or g > best[0]: best = (g, v)
    return [Fr(c).limit_denominator(10 ** 12) for c in best[1]]

pair_ok, pair_min, bad = True, None, []
for i, j in itertools.combinations(range(n), 2):
    u = propose(Vf[i], Vf[j])
    hiA = [sum((u[k] * x[k] for k in range(3)), QF(0)) for x in pieces[i]]   # exact projections
    loB = [sum((u[k] * y[k] for k in range(3)), QF(0)) for y in pieces[j]]
    hi, lo = max(hiA, key=float), min(loB, key=float)          # floats only choose the plane offset ...
    t = (hi + lo) * Fr(1, 2)                                    # ... plane u . x = t; every vertex is then checked exactly
    sep = all((t - a).sign() > 0 for a in hiA) and all((b - t).sign() > 0 for b in loB)
    if not sep: pair_ok = False; bad.append((i, j))
    m = (float(lo) - float(hi)) / math.sqrt(sum(float(c) ** 2 for c in u))
    pair_min = m if pair_min is None else min(pair_min, m)

print(f"{n} unit-edge {PLURAL[d['piece']]} in s_full x unit-edge {d['container']},  s_full = {d['s_full']!r}")
fld = {(1, 1): 'Q'}.get((P.field, Cs.field)) or ('Q(sqrt2, sqrt5)' if {P.field, Cs.field} >= {2, 5} else f'Q(sqrt{max(P.field, Cs.field)})')
print(f"exact solid self-check: edges = 1 exactly, {len(P.faces)} + {len(Cs.faces)} faces verified; arithmetic in {fld}")
print(f"(1) containment, exact, {n * len(P.V) * len(Cs.normals)} vertex/face tests: {'ok' if wall_ok else 'FAILED'};  min wall gap ~ {wall_min:.12e}")
print(f"(2) separation, exact, {n * (n - 1) // 2} pairs, each with an explicit rational plane: {'ok' if pair_ok else 'FAILED ' + str(bad[:5])};  min plane margin ~ {pair_min:.12e}")
print('CERTIFIED' if wall_ok and pair_ok else 'NOT CERTIFIED')
sys.exit(0 if wall_ok and pair_ok else 1)
