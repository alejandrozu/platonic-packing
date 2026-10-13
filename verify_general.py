#!/usr/bin/env python3
"""Floating-point verifier for record files of any solid in src/solids.json (Archimedean, Catalan, prisms,
antiprisms, Platonic). Usage: python3 verify_general.py record.json

Checks, in double precision with explicit margins:
  * containment: every vertex of every piece lies inside every face plane of the container s_full * C
    (C = the canonical container solid of src/solids.json, centred at `container_center`, default the origin);
  * disjointness: every pair of pieces whose centres are closer than the sum of circumradii is separated by a
    separating axis -- a face normal of either piece, or the cross product of an edge of one with an edge of the
    other whose Gauss-map arcs intersect (these include every face normal of the Minkowski difference, so the test is
    exact for convex polytopes).
Prints the smallest wall gap and the smallest pair separation found and exits 1 if any check fails.
This is a float check; the proof-grade check is the exact certifier."""
import json, sys, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = json.load(open(os.path.join(HERE, 'src', 'solids.json')))


def quat(q):
    q = np.asarray(q, float)
    scale = np.max(np.abs(q))
    if not np.isfinite(scale) or scale == 0:
        raise ValueError('Quaternion must have finite, nonzero components.')
    # Scaling the proposal only avoids overflow/underflow; stored native
    # quaternions and the exact rational rotation certificate stay untouched.
    q = q / scale
    n = np.linalg.norm(q); w, x, y, z = q / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def edge_faces(faces, edges):
    m = {}
    for fi, f in enumerate(faces):
        for t, a in enumerate(f):
            b = f[(t + 1) % len(f)]; m.setdefault((min(a, b), max(a, b)), []).append(fi)
    return np.array([m[(min(i, j), max(i, j))][:2] for i, j in edges], int)


def main(fn):
    d = json.load(open(fn))
    P, C = SOL[d['piece']], SOL[d['container']]
    s = float(d['s_full']); cc = np.array(d.get('container_center', [0, 0, 0]), float)
    V = np.array(P['V']); FN = np.array(P['normals']); EF = edge_faces(P['faces'], P['edges'])
    CN = np.array(C['normals']); CV = np.array(C['V'])
    beta = np.array([CN[f] @ CV[F[0]] for f, F in enumerate(C['faces'])])
    circ = np.linalg.norm(V, axis=1).max()
    pcs = np.array(d['pieces'], float); n = len(pcs)
    assert n == d['n'], 'piece count'
    Rs = [quat(p[3:]) for p in pcs]; cs = pcs[:, :3]
    X = [cs[i] + V @ Rs[i].T for i in range(n)]
    ok = True
    # containment
    wall = min(float((s * beta - (X[i] - cc) @ CN.T).min()) for i in range(n))
    if wall <= 0: ok = False; print(f'FAIL containment: min wall gap {wall:.3e}')
    # pairs
    pg = math.inf; checked = 0
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(cs[i] - cs[j]) > 2 * circ: continue
            checked += 1
            FA, FB = FN @ Rs[i].T, FN @ Rs[j].T
            a1, a2, b1, b2 = FA[EF[:, 0]], FA[EF[:, 1]], FB[EF[:, 0]], FB[EF[:, 1]]
            cA, cB = np.cross(a2, a1), np.cross(b2, b1)
            CBA, DBA, ADC, BDC = -(cA @ b1.T), -(cA @ b2.T), a1 @ cB.T, a2 @ cB.T
            ii, jj = np.nonzero((CBA * DBA < 0) & (ADC * BDC < 0) & (CBA * BDC > 0))
            W = np.cross(cA[ii], cB[jj]); l = np.linalg.norm(W, axis=1); W = W[l > 1e-12] / l[l > 1e-12, None]
            U = np.concatenate([FA, FB, W])
            pa, pb = X[i] @ U.T, X[j] @ U.T
            g = np.maximum(pb.min(0) - pa.max(0), pa.min(0) - pb.max(0)).max()
            pg = min(pg, float(g))
            if g <= 0: ok = False; print(f'FAIL pair ({i}, {j}): best separating gap {g:.3e}')
    print(f"{d.get('record_id', fn)}: {n} pieces, {checked} near pairs tested; min wall gap {wall:.6e}, "
          f"min pair separation {pg:.6e}")
    print('VALID' if ok else 'INVALID')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
