"""Symmetric seeding (13 Oct 2026; docs/SEARCH_METHODS_REVIEW.md): symmetry groups of the solids and random cyclic
symmetries <g> of the container for an n-packing, in the format of src/sim.js symmetrize().

A configuration held symmetric under <g> during the soft phase has orbits of k = ord(g) pieces (centre g^j c0,
rotation g^j R0 m_j, with m_j a mirror symmetry of the piece when g^j is improper) plus b pieces on the fixed set of
g (axis, plane or centre). The tightening afterwards is free, so the result need not stay symmetric."""
import json, os
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
_GROUPS = {}


def sym_group(name):
    """All orthogonal 3x3 matrices mapping the solid's vertex set to itself (full group, reflections included)."""
    if name in _GROUPS: return _GROUPS[name]
    X = np.array(SOL[name]['V'], float); X = X - X.mean(0)
    nr = np.linalg.norm(X, axis=1); D = np.linalg.norm(X[:, None] - X[None], axis=2)
    idx = [0]
    for i in range(1, len(X)):
        if np.linalg.matrix_rank(X[idx + [i]], 1e-6) == len(idx) + 1: idx.append(i)
        if len(idx) == 3: break
    Ainv = np.linalg.inv(X[idx].T); gs = []
    for a in range(len(X)):
        if abs(nr[a] - nr[idx[0]]) > 1e-6: continue
        for b in range(len(X)):
            if abs(nr[b] - nr[idx[1]]) > 1e-6 or abs(D[a, b] - D[idx[0], idx[1]]) > 1e-6: continue
            for c in range(len(X)):
                if abs(nr[c] - nr[idx[2]]) > 1e-6 or abs(D[a, c] - D[idx[0], idx[2]]) > 1e-6 or abs(D[b, c] - D[idx[1], idx[2]]) > 1e-6: continue
                M = X[[a, b, c]].T @ Ainv
                if np.abs(M @ M.T - np.eye(3)).max() > 1e-6: continue
                if np.min(np.linalg.norm((X @ M.T)[:, None] - X[None], axis=2), axis=1).max() < 1e-6: gs.append(M)
    _GROUPS[name] = gs
    return gs


def sym_spec(piece, container, n, rng):
    """A random cyclic symmetry <g> for an n-packing: a orbits of size k = ord(g) and b pieces on the fixed set."""
    Gc = [g for g in sym_group(container) if np.abs(g - np.eye(3)).max() > 1e-9]
    refl = [h for h in sym_group(piece) if np.linalg.det(h) < 0]
    mref = refl[0] if refl else None
    for _ in range(200):
        g = Gc[rng.randrange(len(Gc))]
        det = np.linalg.det(g)
        if det < 0 and mref is None: continue                        # chiral piece: no mirror images
        k, P = 1, g.copy()
        while np.abs(P - np.eye(3)).max() > 1e-9 and k < 13: P = P @ g; k += 1
        w, U = np.linalg.eig(g)
        fix = np.real(U[:, np.abs(w - 1) < 1e-6]); d = fix.shape[1]
        if d:
            Qm, _ = np.linalg.qr(fix); Pm = Qm @ Qm.T
        else:
            Pm = np.zeros((3, 3))
        bmax = {0: 1, 1: 3, 2: max(2, n // 3)}[d]
        bs = [b for b in range(0, min(bmax, n) + 1) if (n - b) % k == 0 and (n - b) // k >= 1]
        if not bs: continue
        b = rng.choice(bs); a = (n - b) // k
        Gs, Ds, Ms = [], [], []
        Gj = np.eye(3)
        for j in range(k):
            Gs.append(Gj.flatten().tolist()); dj = float(np.sign(np.linalg.det(Gj))); Ds.append(dj)
            Ms.append((mref if dj < 0 else np.eye(3)).flatten().tolist()); Gj = g @ Gj
        orbits = [{'m': [o * k + j for j in range(k)], 'G': Gs, 'D': Ds, 'M': Ms} for o in range(a)]
        fixed = [{'i': a * k + t, 'P': Pm.flatten().tolist()} for t in range(b)]
        return {'orbits': orbits, 'fixed': fixed}, {'k': k, 'det': int(round(det)), 'dfix': d, 'a': a, 'b': b}
    return None, None


