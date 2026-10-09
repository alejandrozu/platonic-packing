"""Checks the tightening Jacobian and both checkers.

1. Analytic Jacobian of the SLSQP constraints vs central differences, for every solid.
2. Known-good files certify: Yohei Nakajima's 12 cubes in a cube of side 2.9315185094797 (copied from
   soft-to-rigid-packing, MIT) and the Hyra-results record of 21 unit octahedra in a cube of side 2.592849935818519
   (Tencent-Hunyuan/Hyra-results), both re-expressed with container_center = (s/2, s/2, s/2).
3. Every record in records/ certifies (both checkers).
4. Broken files are rejected: container shrunk by 3e-5, a piece pushed 1e-4 past its best separating plane, two
   pieces made coincident, a piece moved outside. Each must make BOTH checkers exit nonzero."""
import json, os, sys, subprocess, glob, copy, math, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
import numpy as np
import exact

fails = 0
def run(script, path):
    return subprocess.run([sys.executable, os.path.join(ROOT, script), path], capture_output=True, text=True).returncode

# 1. Jacobian
rng = np.random.default_rng(1)
for piece in ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']:
    pb = exact.Problem(piece)
    # three pieces in a loose row, random orientations
    C = np.array([[0, 0, 0], [1.6 * pb.circ, 0.1, 0], [0.8 * pb.circ, 1.5 * pb.circ, 0.2]])
    R = [exact.quat_to_R(q / np.linalg.norm(q)) for q in rng.normal(size=(3, 4))]
    L, _, C0 = exact.certify(pb, C, R)
    exact.CHECK_JAC[:] = [None]
    exact.solve(pb, C0, R, L, outer=1)
    err = exact.CHECK_JAC[1]
    print(f'jacobian {piece:13s} max |analytic - numeric| = {err:.2e}')
    if err > 1e-6: fails += 1
exact.CHECK_JAC[:] = []

# 2. known-good external files
fixtures = os.path.join(ROOT, 'test', 'fixtures')
for name in sorted(os.listdir(fixtures)):
    p = os.path.join(fixtures, name)
    a, b = run('verify.py', p), run('certify_exact.py', p)
    print(f'external {name}: verify {"ok" if a == 0 else "FAIL"}, certify {"ok" if b == 0 else "FAIL"}')
    fails += (a != 0) + (b != 0)

# 3. every record
for p in sorted(glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json'))):
    a, b = run('verify.py', p), run('certify_exact.py', p)
    if a or b: print('claim FAILED', p); fails += 1
print(f'records: {len(glob.glob(os.path.join(ROOT, "records", "*", "*_n[0-9][0-9].json")))} files checked')

# 3b. monotonicity: certified sizes never decrease with n, for every problem (records and archive)
import csv as _csv
rows = list(_csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv'))))
byp = {}
for r in rows: byp.setdefault(r['problem'], []).append((int(r['n']), float(r['s_full'])))
mono_bad = 0
for prob, v in byp.items():
    v.sort()
    for (n1, s1), (n2, s2) in zip(v, v[1:]):
        if n2 == n1 + 1 and s1 > s2: print('NOT MONOTONE', prob, n1, s1, '>', n2, s2); mono_bad += 1
fails += mono_bad
r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'engine.py'), 'check'], capture_output=True, text=True)
print('monotonicity: records', 'ok' if not mono_bad else 'FAILED', '| archive', r.stdout.strip())
fails += r.returncode != 0

# 4. broken files must be rejected
base = sorted(glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json')) + glob.glob(os.path.join(fixtures, '*.json')))
tmp = tempfile.mkdtemp()
def rotq(q, ax, th):
    h = th / 2; d = [math.cos(h), *(math.sin(h) * a for a in ax)]; w, x, y, z = q; dw, dx, dy, dz = d
    return [dw * w - dx * x - dy * y - dz * z, dw * x + dx * w + dy * z - dz * y, dw * y - dx * z + dy * w + dz * x, dw * z + dx * y - dy * x + dz * w]
nbroken = 0
for p in base[:12]:
    c = json.load(open(p))
    P = c['pieces']
    # nearest pair
    i, j = min(((i, j) for i in range(len(P)) for j in range(i + 1, len(P))), key=lambda ij: sum((P[ij[0]][k] - P[ij[1]][k]) ** 2 for k in range(3)))
    bad = []
    a = copy.deepcopy(c); a['s_full'] = c['s_full'] - 3e-5; bad.append(('shrunk', a))
    # push piece j into piece i along their best separating axis by (gap + 1e-4)
    pb = exact.Problem(c['piece'])
    Vu = np.array(exact.SOL[c['piece']]['V'])
    class U:
        V = Vu; faxes = pb.faxes; edirs = pb.edirs
        @staticmethod
        def verts(cc, Rm): return cc + Vu @ Rm.T
    Ri, Rj = (exact.quat_to_R(np.array(P[t][3:]) / np.linalg.norm(P[t][3:])) for t in (i, j))
    g, u, _ = exact.sat_gap(U, np.array(P[i][:3]), Ri, np.array(P[j][:3]), Rj)
    b = copy.deepcopy(c)
    for k in range(3): b['pieces'][j][k] -= (g + 1e-4) * u[k]
    bad.append(('pushed', b))
    f = copy.deepcopy(c); f['pieces'][j][:3] = f['pieces'][i][:3]; bad.append(('coincident', f))
    e = copy.deepcopy(c); e['pieces'][0][0] += 10 * c['s_full']; bad.append(('outside', e))
    for tag, obj in bad:
        q = os.path.join(tmp, f'{tag}_{os.path.basename(p)}'); json.dump(obj, open(q, 'w'))
        r1, r2 = run('verify.py', q), run('certify_exact.py', q)
        nbroken += 1
        if r1 == 0 or r2 == 0: print('NOT REJECTED', tag, p, r1, r2); fails += 1
print(f'broken files: {nbroken} variants, all rejected' if not fails else f'FAILURES: {fails}')
sys.exit(1 if fails else 0)
