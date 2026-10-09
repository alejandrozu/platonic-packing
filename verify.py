#!/usr/bin/env python3
"""Float verifier for a packing claim file (standard library only). Usage: python3 verify.py claim.json

A claim lists n poses [x, y, z, qw, qx, qy, qz]: a unit-edge copy of the piece solid (canonical coordinates in
solids.py) rotated by the quaternion q and centred at (x, y, z). The container is s_full times the canonical
unit-edge container solid, centred at `container_center` (default the origin), in its canonical orientation.
Checks every vertex lies inside every container face plane and every pair is separated (separating-axis test over
face normals and edge-direction cross products, which is exact for convex polytopes). Prints the minimum wall gap
(Euclidean distance from a vertex to the nearest container face plane) and the minimum pair separation (a lower bound
on the Euclidean distance between the two pieces; pairs whose centres are more than two circumradii apart are
separated by that fact alone and are not run through the axis test). Exits 1 on any failure. See certify_exact.py for the proof-grade
check in exact arithmetic."""
import json, sys, itertools, math
PLURAL = {'tetrahedron': 'tetrahedra', 'cube': 'cubes', 'octahedron': 'octahedra', 'dodecahedron': 'dodecahedra', 'icosahedron': 'icosahedra'}
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from solids import solid

d = json.load(open(sys.argv[1]))
P, Cs = solid(d['piece']), solid(d['container'])
s = float(d['s_full']); cc = d.get('container_center', [0, 0, 0])
PV = [[float(c) for c in v] for v in P.V]
nrm = lambda u: [x / math.sqrt(sum(y * y for y in u)) for x in u]
CN = [nrm([float(c) for c in m]) for m in Cs.normals]
rhoC = float(Cs.inradius2) ** 0.5
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
ok = True


def rot(q):
    n = math.sqrt(sum(v * v for v in q))
    if abs(n - 1) > 1e-12: print(f'note: quaternion normalized (|q| = {n:.15f})')
    w, x, y, z = (v / n for v in q)
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]


uniq = lambda L: [u for i, u in enumerate(L) if all(abs(dot(u, w)) < 1 - 1e-9 for w in L[:i])]
FA = uniq([nrm([float(c) for c in m]) for m in P.normals])
ED = uniq([nrm([PV[j][k] - PV[i][k] for k in range(3)]) for i, j in P.edges])
pieces = []
for p in d['pieces']:
    R = rot(p[3:]); mv = lambda u: [sum(R[i][k] * u[k] for k in range(3)) for i in range(3)]
    V = [[p[i] + mv(v)[i] for i in range(3)] for v in PV]
    pieces.append((V, [mv(u) for u in FA], [mv(u) for u in ED]))
wall = min(s * rhoC - dot(N, [v[k] - cc[k] for k in range(3)]) for V, _, _ in pieces for v in V for N in CN)
if wall < 0: ok = False; print('FAIL: a vertex lies outside the container')
pair = float('inf')
Rc = max(math.sqrt(dot(v, v)) for v in PV)            # circumradius of the unit-edge piece
for (i, (VA, FAa, EDa)), (j, (VB, FAb, EDb)) in itertools.combinations(enumerate(pieces), 2):
    ci, cj = d['pieces'][i][:3], d['pieces'][j][:3]
    dc = math.sqrt(sum((ci[k] - cj[k]) ** 2 for k in range(3)))
    if dc > 2 * Rc + 1e-9:                                # each piece lies in the ball of radius Rc about its centre
        pair = min(pair, dc - 2 * Rc); continue
    axes = FAa + FAb + [c for a in EDa for b in EDb for c in [cross(a, b)] if dot(c, c) > 1e-18]
    units = [nrm(u) for u in axes]
    gap = max(max(min(dot(u, v) for v in VB) - max(dot(u, v) for v in VA), min(dot(u, v) for v in VA) - max(dot(u, v) for v in VB)) for u in units)
    pair = min(pair, gap)
    if gap <= 0: ok = False; print(f'FAIL: pieces {i} and {j} overlap or touch (gap {gap:.3e})')
print(f"{d['n']} unit {PLURAL[d['piece']]} in a {d['container']} of edge s = {s:.16f}\nmin wall gap = {wall:.12e}\nmin pair gap = {pair:.12e}\n" + ('VALID' if ok else 'INVALID'))
sys.exit(0 if ok else 1)
