"""Structural features of the 4D-6D catalogue records (7 Nov 2026): the 3D measures of features.py, rotations.py
and inherit.py, extended to the regular polytopes of src/polytopes_nd.json.

A record places each piece as c + R V with R = diag(D) (I - S)^-1 (I + S) (see the record's `format`), inside
s_full x mu x the container polytope, centred at the origin. Tolerances are in piece edges.

For each record:
  orient     orientation classes: i ~ j when R_i V = R_j V as vertex sets (R_i^-1 R_j is a piece symmetry)
  rel        for 2-8 classes, the relative rotation R_a^-1 R_b of two class representatives, reduced modulo the proper
             piece symmetries (the representative closest to the identity); its rotation angles (one per invariant
             plane, largest first), whether each angle is a rational turn p/q with q <= 60, whether the rotation is
             simple (one nonzero angle) or isoclinic (all angles equal, 4D and 6D)
  sym        configuration symmetry: container symmetries h (reflections included) mapping the set of placed
             pieces onto itself; order and proper count, and the same at a loose tolerance
  layers     for each container facet normal, centres grouped by height (gap > ltol edges starts a layer);
             the direction with the fewest layers
  lattice    for each orientation class with >= d + 1 pieces: are all centres integer combinations of d short
             difference vectors
Per family, subset inheritance f(k, N) for k < N <= k + gap (k <= kmax): the largest fraction of record k matched
one-to-one into record N by one container symmetry and one translation (centres and orientations agreeing).

The symmetry groups are computed from the vertex sets (backtracking over vertex images with the Gram matrix of a
basis of neighbouring vertices), so |G| is checked against the known orders.

Usage: python3 scripts/patterns/features_nd.py [--families c5inc5,...] [--kmax 40] [--gap 6]
Output: docs/patterns/features_nd.json, docs/patterns/inherit_nd.json
"""
import json, os, sys, glob, argparse, time, math, csv
from fractions import Fraction
import numpy as np
from scipy.spatial import cKDTree

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ND = json.load(open(os.path.join(ROOT, 'src', 'polytopes_nd.json')))
ORDERS = {'c5': 120, 'c8': 384, 'c16': 384, 'c24': 1152, 'c600': 14400, 'c120': 14400,
          'sx5': 720, 'hc5': 3840, 'op5': 3840, 'sx6': 5040, 'hc6': 46080, 'op6': 46080}


def poly(name):
    p = ND[name]
    V = np.array(p['Vf'], float)
    return V, float(p['edge']), np.array(p['N'], float), np.array(p['beta'], float)


def sym_group(V, tol=1e-6):
    """All orthogonal Q with Q V = V (as a set), for a centred vertex set V."""
    V = np.asarray(V, float); n, d = V.shape
    nrm = np.linalg.norm(V, axis=1).max()
    G = V @ V.T
    # basis: vertex 0 and its nearest neighbours, greedily independent, then any independent vertices
    order = np.argsort(np.linalg.norm(V - V[0], axis=1))
    basis = [0]
    for i in list(order[1:]) + list(range(n)):
        if len(basis) == d: break
        M = V[basis + [int(i)]]
        if np.linalg.matrix_rank(M, 1e-8 * nrm) == len(M): basis.append(int(i))
    B = V[basis]                                   # d x d
    GB = B @ B.T
    Binv = np.linalg.inv(B)                        # Q B^T = W^T -> Q = W^T B^-T
    tree = cKDTree(V)
    out = []
    t = tol * max(1.0, nrm * nrm)

    def rec(k, imgs):
        if k == d:
            W = V[imgs]
            Q = W.T @ Binv.T
            if np.abs(Q @ Q.T - np.eye(d)).max() > 1e-6: return
            dd, _ = tree.query(V @ Q.T)
            if dd.max() < 1e-6 * max(1.0, nrm): out.append(Q)
            return
        for c in range(n):
            if abs(G[c, c] - GB[k, k]) > t: continue
            if any(abs(G[c, imgs[j]] - GB[k, j]) > t for j in range(k)): continue
            if c in imgs: continue
            rec(k + 1, imgs + [c])
    rec(0, [])
    return np.array(out)


def rot_from(row, d):
    c = np.array(row[:d], float)
    m = d * (d - 1) // 2
    s = row[d:d + m]; D = np.array(row[d + m:d + m + d], float)
    S = np.zeros((d, d)); k = 0
    for i in range(d):
        for j in range(i + 1, d):
            S[i, j] = float(s[k]); S[j, i] = -float(s[k]); k += 1
    I = np.eye(d)
    R = np.diag(D) @ np.linalg.solve(I - S, I + S)
    return c, R


def load(f):
    try: r = json.load(open(f))
    except Exception: return None
    if not isinstance(r, dict) or 'pieces' not in r: return None
    d = int(r.get('dim', 3))
    if d < 4 or r['piece'] not in ND or r['container'] not in ND: return None
    P = r['pieces']
    CR = [rot_from(p, d) for p in P]
    C = np.array([c for c, _ in CR]); R = [Rm for _, Rm in CR]
    return r, d, C, R


class Sig:
    """Orientation signature of a placed vertex set R V: sorted projections onto two fixed generic directions."""
    def __init__(self, d, seed=7):
        g = np.random.default_rng(seed)
        self.U = g.normal(size=(2, d)); self.U /= np.linalg.norm(self.U, axis=1, keepdims=True)

    def of(self, W):                      # W: nv x d (centred)
        return np.concatenate([np.sort(W @ u) for u in self.U])


def same_set(A, B, tol):
    d, _ = cKDTree(B).query(A)
    return d.max() < tol


def orient_classes(R, V, tol):
    n = len(R); W = [V @ Ri.T for Ri in R]
    lab = list(range(n))
    def find(i):
        while lab[i] != i: lab[i] = lab[lab[i]]; i = lab[i]
        return i
    sg = Sig(V.shape[1]); S = np.array([sg.of(w) for w in W])
    for i in range(n):
        cand = np.nonzero(np.abs(S - S[i]).max(1) < tol)[0]
        for j in cand:
            if j <= i: continue
            if same_set(W[i], W[j], tol):
                a, b = find(i), find(int(j))
                if a != b: lab[a] = b
    groups = {}
    for i in range(n): groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=len, reverse=True)


def rot_angles(M):
    """Rotation angles (degrees) of a proper orthogonal matrix, one per invariant 2-plane, largest first."""
    ev = np.linalg.eigvals(M)
    ang = np.degrees(np.abs(np.angle(ev)))
    ang = np.sort(ang)[::-1]
    d = M.shape[0]
    out = []
    used = np.zeros(len(ang), bool)
    for i in range(len(ang)):           # eigenvalues come in conjugate pairs: take every other one above 0
        if used[i]: continue
        j = next((k for k in range(i + 1, len(ang)) if not used[k] and abs(ang[k] - ang[i]) < 1e-5), None)
        used[i] = True
        if j is not None: used[j] = True
        out.append(float(ang[i]))
    out = sorted(out, reverse=True)[: d // 2]
    return out


def rational(th, qmax=60, tol=3e-6):
    f = Fraction(th / 360).limit_denominator(qmax)
    return abs(float(f) - th / 360) < tol, f


def relative(R, oc, Gp):
    reps = [R[c[0]] for c in oc]
    res = []
    for a in range(len(reps)):
        for b in range(a + 1, len(reps)):
            M0 = reps[a].T @ reps[b]
            tr = np.einsum('ij,gji->g', M0, Gp)           # tr(M0 g)
            g = Gp[int(np.argmax(tr))]
            M = M0 @ g
            ang = rot_angles(M)
            rat = [rational(t) for t in ang]
            nz = [t for t in ang if t > 1e-4]
            res.append({'angles': [round(t, 6) for t in ang],
                        'rational': all(r for r, _ in rat),
                        'turns': [str(f) if r else None for r, f in rat],
                        'simple': len(nz) == 1,
                        'isoclinic': len(ang) >= 2 and len(nz) == len(ang) and max(ang) - min(ang) < 1e-4})
    return res


def config_symmetry(C, R, V, H, tol):
    n = len(C)
    tree = cKDTree(C)
    HC = np.einsum('hij,nj->hni', H, C)                       # |H| x n x d
    dd, jj = tree.query(HC.reshape(-1, C.shape[1]))
    dd = dd.reshape(len(H), n); jj = jj.reshape(len(H), n)
    W = [V @ Ri.T for Ri in R]
    ok = []
    for h in np.nonzero(dd.max(1) < tol)[0]:
        j = jj[h]
        if len(set(j.tolist())) < n: continue
        if all(same_set(W[i] @ H[h].T, W[j[i]], tol) for i in range(n)): ok.append(int(h))
    return ok


def layers(C, normals, ltol):
    best = None
    for nrm in normals:
        z = np.sort(C @ nrm)
        cuts = np.nonzero(np.diff(z) > ltol)[0]
        sizes = np.diff(np.concatenate([[0], cuts + 1, [len(z)]])).tolist()
        if best is None or len(sizes) < len(best[0]): best = (sizes, nrm)
    return best


def lattice(P, tol):
    P = np.asarray(P, float); d = P.shape[1]
    if len(P) < d + 1: return None
    D = (P[:, None] - P[None]).reshape(-1, d)
    D = D[np.linalg.norm(D, axis=1) > 1e-6]
    D = D[np.argsort(np.linalg.norm(D, axis=1))]
    basis = []
    for v in D:
        M = np.array(basis + [v])
        if np.linalg.matrix_rank(M, 1e-6) == len(M): basis.append(v)
        if len(basis) == d: break
    if len(basis) < d: return {'dim': len(basis), 'lattice': None}
    B = np.array(basis).T
    X = np.linalg.solve(B, (P - P[0]).T).T
    res = float(np.abs(X - np.round(X)).max())
    return {'dim': d, 'lattice': res < tol, 'residual': res}


def analyze(r, d, C, R, V, edge, Gp, H, N_c, tol=1e-4, loose=2e-2, ltol=0.05):
    oc = orient_classes(R, V, 1e-3 * edge)
    rel = relative(R, oc, Gp) if 2 <= len(oc) <= 8 else None
    sy = config_symmetry(C, R, V, H, tol * edge)
    syl = config_symmetry(C, R, V, H, loose * edge)
    ly = layers(C, N_c, ltol * edge)
    lat = [lattice(C[g], 1e-3) for g in oc if len(g) >= d + 1]
    det = np.linalg.det(H)
    return {'record_id': r['record_id'], 'problem': r['problem'], 'dim': d, 'piece': r['piece'],
            'container': r['container'], 'n': int(r['n']), 's': float(r['s_full']),
            'closed_form': r.get('closed_form_conjecture') if r.get('closed_form_conjecture') not in (None, 'None') else None,
            'found_by': r.get('found_by'), 'move': (r.get('search') or {}).get('move') if isinstance(r.get('search'), dict) else None,
            'orient': [len(g) for g in oc], 'rel': rel,
            'sym': {'order': len(sy), 'proper': int(sum(det[h] > 0 for h in sy))},
            'sym_loose': {'order': len(syl), 'proper': int(sum(det[h] > 0 for h in syl))},
            'layers': {'sizes': ly[0], 'normal': np.round(ly[1], 4).tolist()} if ly else None,
            'lattice': lat}


def inherit_pair(A, B, V, H, sg, HU, tol):
    """Largest number of pieces of A matched into B by one h in H and one translation."""
    (CA, RA), (CB, RB) = A, B
    k, N = len(CA), len(CB)
    WA = [V @ R.T for R in RA]; WB = [V @ R.T for R in RB]
    SB = np.array([sg.of(w) for w in WB])
    treeB = cKDTree(CB); treeS = cKDTree(SB)
    best = 0
    for a in range(min(k, 3)):
        # signatures of h R_a V for every h:  <u, h w> = <h^T u, w>
        Pa = np.einsum('hud,vd->huv', HU, WA[a])               # |H| x 2 x nv
        Sa = np.sort(Pa, axis=2).reshape(len(H), -1)
        hits = treeS.query_ball_point(Sa, r=tol * 4)
        pairs = [(h, j) for h in range(len(H)) for j in hits[h]]
        if not pairs: continue
        allhs = np.array([p[0] for p in pairs]); alljs = np.array([p[1] for p in pairs])
        for s0 in range(0, len(pairs), 4096):                    # chunks keep memory bounded
            hs = allhs[s0:s0 + 4096]; js = alljs[s0:s0 + 4096]
            T = CB[js] - np.einsum('hij,j->hi', H[hs], CA[a])        # translations
            M = np.einsum('pij,kj->pki', H[hs], CA) + T[:, None]       # mapped centres
            dd, jj = treeB.query(M.reshape(-1, CA.shape[1]))
            dd = dd.reshape(len(hs), k); jj = jj.reshape(len(hs), k)
            cnt = (dd < tol).sum(1)
            for p in np.argsort(-cnt):
                if cnt[p] <= best: break
                h = H[hs[p]]; used = set(); m = 0
                for i in range(k):
                    if dd[p, i] >= tol or jj[p, i] in used: continue
                    if same_set(WA[i] @ h.T, WB[jj[p, i]], tol): used.add(jj[p, i]); m += 1
                best = max(best, m)
            if best == k: break
        if best == k: break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--families'); ap.add_argument('--kmax', type=int, default=40)
    ap.add_argument('--gap', type=int, default=6); ap.add_argument('--no-inherit', action='store_true')
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'patterns', 'features_nd.json'))
    ap.add_argument('--out-inherit', default=os.path.join(ROOT, 'docs', 'patterns', 'inherit_nd.json'))
    a = ap.parse_args()
    probs = {}
    for row in csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv'))):
        probs.setdefault(row['problem'], []).append(int(row['n']))
    fams = a.families.split(',') if a.families else sorted(
        p for p in probs if os.path.isdir(os.path.join(ROOT, 'records', p)) and
        any(p.startswith(x + 'in') and p[len(x) + 2:] in ND for x in ND))
    groups = {}
    def grp(name):
        if name not in groups:
            G = sym_group(poly(name)[0])
            if len(G) != ORDERS[name]: raise RuntimeError(f'{name}: |G| = {len(G)} != {ORDERS[name]}')
            groups[name] = G
        return groups[name]
    feats, inh = [], []
    t0 = time.time()
    for fam in fams:
        recs = {}
        for f in sorted(glob.glob(os.path.join(ROOT, 'records', fam, f'{fam}_n*.json'))):
            L = load(f)
            if L is None: continue
            r, d, C, R = L
            recs[int(r['n'])] = (C, R)
            V, edge, _, _ = poly(r['piece'])
            Gfull = grp(r['piece']); Gp = Gfull[np.linalg.det(Gfull) > 0]
            H = grp(r['container'])
            Nc = poly(r['container'])[2]
            feats.append(analyze(r, d, C, R, V, edge, Gp, H, Nc))
        if not a.no_inherit and recs:
            piece = fam.split('in')[0]; cont = fam[len(piece) + 2:]
            V, edge, _, _ = poly(piece); H = grp(cont)
            sg = Sig(V.shape[1]); HU = np.einsum('hji,uj->hui', H, sg.U)    # h^T u
            for k in sorted(recs):
                if k > a.kmax or k < 2: continue
                for N in range(k + 1, k + a.gap + 1):
                    if N not in recs: continue
                    m = inherit_pair(recs[k], recs[N], V, H, sg, HU, 2e-2 * edge)
                    inh.append({'problem': fam, 'k': k, 'N': N, 'matched': m, 'f': m / k})
        print(fam, len(feats), len(inh), f'{time.time() - t0:.0f}s', flush=True)
        json.dump(feats, open(a.out, 'w'), indent=0)
        if not a.no_inherit: json.dump(inh, open(a.out_inherit, 'w'), indent=0)


if __name__ == '__main__':
    main()
