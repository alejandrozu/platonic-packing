#!/usr/bin/env python3
"""Lattice constructions (touching packings) added as candidates to results/tight.jsonl (mode 'lattice').

Tetrahedra in a tetrahedron of edge k: the edge-k tetrahedron is cut by the planes of the k-subdivision into
C(k+2,3) upright unit tetrahedra, C(k,3) inverted unit tetrahedra and C(k+1,3) unit octahedra, and each unit
octahedron holds one unit tetrahedron exactly (base on one face, apex at the centroid of the opposite face: the
distance between opposite faces of a unit octahedron is sqrt(2/3), the height of a unit tetrahedron).
So k = 2 gives 5 and k = 3 gives 15 unit tetrahedra.

Octahedra in an octahedron of edge k: unit octahedra {|x|+|y|+|z| <= a} (a = sqrt2/2) centred at a*m for integer m with
|m|_1 <= k - 1 and |m|_1 = k - 1 (mod 2); L1 distance between centres >= 2a so interiors are disjoint.
k = 2 gives 6, k = 3 gives 19.
Each construction is re-tightened (it may shrink when it is not rigid) and descended to smaller n by pipeline.py."""
import json, os, sys, itertools, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import exact
from pipeline import TIGHT, load_tight

SOL = exact.SOL


def kabsch_quat(src, dst):
    """Rotation R with R src_i ~ dst_{perm(i)} for the best vertex matching; returns (quat, rmsd)."""
    best = None
    for perm in itertools.permutations(range(len(src))):
        D = dst[list(perm)]
        H = src.T @ D
        U, S, Vt = np.linalg.svd(H)
        d = np.sign(np.linalg.det(Vt.T @ U.T))
        R = Vt.T @ np.diag([1, 1, d]) @ U.T
        err = np.sqrt(((src @ R.T - D) ** 2).sum(1).mean())
        if best is None or err < best[1]: best = (R, err)
    return exact.R_to_quat(best[0]), best[1]


def tetra(k):
    V = np.array(SOL['tetrahedron']['V'])
    C, Q = [], []
    ident = [1.0, 0, 0, 0]
    inv_q, e = kabsch_quat(V, -V); assert e < 1e-12
    for m in itertools.product(range(k + 1), repeat=4):
        s = sum(m); Qc = sum(mi * v for mi, v in zip(m, V))
        if s == k - 1: C.append(Qc); Q.append(ident)                     # upright
        if s == k - 3: C.append(Qc); Q.append(list(inv_q))               # inverted
        if s == k - 2:                                                   # octahedral hole: tetra on face V0 + {V1,V2,V3}
            verts = np.array([V[0] + V[1], V[0] + V[2], V[0] + V[3], -2 * V[0] / 3]) + Qc
            q, e = kabsch_quat(V, verts - verts.mean(0)); assert e < 1e-12, e
            C.append(verts.mean(0)); Q.append(list(q))
    return np.array(C), Q


def octa(k):
    a = np.sqrt(2) / 2
    C = [a * np.array(m, float) for m in itertools.product(range(-k + 1, k), repeat=3)
         if sum(map(abs, m)) <= k - 1 and (sum(map(abs, m)) - (k - 1)) % 2 == 0]
    return np.array(C), [[1.0, 0, 0, 0]] * len(C)


if __name__ == '__main__':
    done = load_tight(); f = open(TIGHT, 'a')
    for piece, k, gen in (('tetrahedron', 2, tetra), ('tetrahedron', 3, tetra), ('octahedron', 2, octa), ('octahedron', 3, octa)):
        C, Q = gen(k); n = len(C)
        pb = exact.Problem(piece)
        row = dict(piece=piece, container=piece, n=n, seed=k, mode='lattice', B=0, C=(C * pb.edge).tolist(), Q=Q)
        tk = (piece, piece, n, 'lattice', 0, k)
        L0, _, _ = exact.certify(pb, row['C'] if False else np.array(row['C']), [exact.quat_to_R(np.array(q)) for q in Q])
        print(f'{piece} k={k}: n={n}, certified (touching) s = {pb.s_of_L(L0):.12f}', flush=True)
        if tk in done: continue
        t0 = time.time(); out = exact.tighten_run(row, tlimit=600); out['secs'] = round(time.time() - t0, 1)
        out['construction'] = f'{piece} subdivision, k = {k}'
        f.write(json.dumps(out) + '\n'); f.flush()
        print(f'   tightened: {out["s"]:.12f} ({out["secs"]}s)', flush=True)
