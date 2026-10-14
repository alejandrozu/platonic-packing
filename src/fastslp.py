"""Vectorized sequential-LP tightening (14 Oct 2026, large-n research).

The same algorithm as exact.solve(method='slp') -- one sparse LP of the linearized constraints per round inside a
trust region, every round re-legalized and certified (exact.certify-equivalent) and accepted only if the certified
size drops -- but with every per-pair Python loop replaced by array code:
  * near pairs from one vectorized distance test (not an n^2 Python loop);
  * separating planes of all pairs at once (exact.pair_gaps_pruned, the same values as exact.sat_gap);
  * constraint selection, constraint values and the Jacobian (evaluated at the current point, where the rotation
    increments are zero, so the left Jacobian is the identity and the plane-normal derivatives are the tangent basis)
    assembled directly in sparse form;
  * the LP is posed in the step dz (better scaled than in z);
  * legalization (certify_fast) uses the vectorized pruned gaps for every solid.
The certified size of every accepted round is computed exactly as in exact.certify, so results are drop-in."""
import math, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
import exact


def near_pairs(C, lim2):
    n = len(C); iu, ju = np.triu_indices(n, 1)
    d2 = ((C[iu] - C[ju]) ** 2).sum(1)
    s = d2 < lim2
    return np.stack([iu[s], ju[s]], 1)


def gaps(pb, P, R, pairs):
    """gap and oriented axis for many pairs (vectorized for every solid; Gauss-map pruned edge axes only where that
    pays, as in exact.pair_gaps)."""
    if not len(pairs): return np.zeros(0), np.zeros((0, 3))
    if not pb.prune: return exact.pair_gaps(pb, P, R, pairs, want_axis=True)
    g, u, _ = exact.pair_gaps_pruned(pb, P, R, pairs)
    return g, u


def planes(pb, P, R, pairs, X=None):
    """Separating planes u.x = c (piece A = pairs[:, 0] below) of many pairs: best SAT axis, mid-plane offset."""
    if pb.prune: return exact.pair_gaps_pruned(pb, P, R, pairs)
    g, u = exact.pair_gaps(pb, P, R, pairs, want_axis=True)
    if X is None: X = np.asarray(P)[:, None, :] + np.einsum('vd,ned->nve', pb.V, np.stack(R))
    a = np.einsum('pvd,pd->pv', X[pairs[:, 0]], u).max(1); b = np.einsum('pvd,pd->pv', X[pairs[:, 1]], u).min(1)
    return g, u, (a + b) / 2


def certify_fast(pb, C, R):
    """exact.certify with vectorized pair lists and gaps: scale centres apart about their mean until no pair overlaps
    (SAT, tolerance 1e-12), then the tight container."""
    C = np.array(C, float); n = len(C); cen = C.mean(0)
    lim = (2 * pb.circ) ** 2 + 1e-9
    near = near_pairs(C, lim * 1.1 ** 2)

    def check(k):
        P = cen + k * (C - cen)
        if not len(near): return True, 0.0
        d2 = np.sum((P[near[:, 0]] - P[near[:, 1]]) ** 2, axis=1)
        sel = near[d2 <= lim]
        g, u = gaps(pb, P, R, sel)
        bad = g < -1e-12
        if not bad.any(): return True, 0.0
        dc = (C[sel[bad, 1]] - C[sel[bad, 0]])
        proj = np.abs(np.sum(u[bad] * dc, axis=1))
        need = np.where(proj > 1e-9, -g[bad] / np.maximum(proj, 1e-9), np.inf)
        return False, float(need.max())

    k, ok = 1.0, False
    for _ in range(12):
        ok, step = check(k)
        if ok: break
        k = k + (step * (1 + 1e-6) + 1e-15 if np.isfinite(step) else max(1e-4, (k - 1)))
    if not ok:
        lo, hi = 1.0, max(k, 1.0001)
        while not check(hi)[0]: hi = 1 + (hi - 1) * 2
        for _ in range(48):
            m = (lo + hi) / 2
            if check(m)[0]: hi = m
            else: lo = m
            if hi - lo < 1e-14: break
        k = hi
    P = cen + k * (C - cen)
    L, t = exact.tight_container(pb, P, R)
    return L, k, P + t


def tangent_bases(U):
    A = np.where(np.abs(U[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    E1 = np.cross(U, A); E1 /= np.linalg.norm(E1, axis=1, keepdims=True)
    return E1, np.cross(U, E1)


def rods(Ph):
    th = np.linalg.norm(Ph, axis=1)
    out = np.empty((len(Ph), 3, 3))
    for i in range(len(Ph)): out[i] = exact.rod(Ph[i])
    return out


def solve(pb, C, R, L, outer=600, trust=0.03, tlimit=None, slp_floor=1e-6, abort=None, verbose=False, lp_limit=None,
          stall=50, stall_rel=1e-7, reg=0.0):
    C = np.array(C, float); R = [np.array(r) for r in R]; n = len(C)
    trust0 = trust; small = 0; acc = []; hist = []
    t_start = time.time()
    CN, off = pb.CN, pb.off
    for it in range(outer):
        if tlimit and time.time() - t_start > tlimit: break
        pairs = near_pairs(C, (2 * pb.circ + 4 * trust + 0.05) ** 2); P = len(pairs)
        Rs = np.stack(R)
        LG = np.einsum('vd,ned->nve', pb.V, Rs)                     # n x nv x 3 world offsets (V @ R_i^T)
        Xc = C[:, None, :] + LG
        if P:
            _, U0, Cpl = planes(pb, C, R, pairs, Xc)
            M0 = (C[pairs[:, 0]] + C[pairs[:, 1]]) / 2
            c0 = Cpl - np.einsum('pd,pd->p', U0, M0)
            E1, E2 = tangent_bases(U0)
        dmax = trust * (math.sqrt(3) + 3 * math.sqrt(3) * pb.circ)
        reach = dmax + 2 * trust + 1e-3
        slack = (L / 2) * off[None, None, :] - Xc @ CN.T              # n x nv x F
        ci, cv, cf = np.nonzero(slack < reach); nc = len(ci)
        cb = 2 * dmax + 1e-3
        if P:
            rp, rs, rv, ri = [], [], [], []
            for sg, col in ((-1.0, 0), (1.0, 1)):
                k = pairs[:, col]
                rel = Xc[k] - M0[:, None, :]                          # P x nv x 3
                sl = sg * (np.einsum('pvd,pd->pv', rel, U0) - c0[:, None])
                marg = cb + 3 * math.sqrt(2) * trust * (np.linalg.norm(rel, axis=2) + dmax) + dmax + 1e-3
                pp, vv = np.nonzero(sl < marg)
                rp.append(pp); rv.append(vv); ri.append(k[pp]); rs.append(np.full(len(pp), sg))
            rp, rs, rv, ri = (np.concatenate(a) for a in (rp, rs, rv, ri))
        else:
            rp = rv = ri = np.zeros(0, int); rs = np.zeros(0)
        npr = len(rp)
        iL = 6 * n; ia = iL + 1; ic = ia + 2 * P; nvar = ic + P
        # constraint values at the current point and the sparse Jacobian there (phi = 0, a = b = 0)
        Yc = LG[ci, cv]; Nc = CN[cf]
        g_c = (L / 2) * off[cf] - np.einsum('kd,kd->k', Xc[ci, cv], Nc)
        rows, cols, vals = [], [], []
        r = np.arange(nc)
        Gphi = np.cross(Nc, Yc)
        for d in range(3):
            rows += [r, r]; cols += [3 * ci + d, 3 * n + 3 * ci + d]; vals += [-Nc[:, d], Gphi[:, d]]
        rows.append(r); cols.append(np.full(nc, iL)); vals.append(off[cf] / 2)
        if npr:
            Ur = U0[rp]; relr = Xc[ri, rv] - M0[rp]
            g_p = rs * (np.einsum('kd,kd->k', relr, Ur) - c0[rp])
            r = nc + np.arange(npr)
            Gp = np.cross(Ur, LG[ri, rv])
            for d in range(3):
                rows += [r, r]; cols += [3 * ri + d, 3 * n + 3 * ri + d]; vals += [rs * Ur[:, d], -rs * Gp[:, d]]
            rows += [r, r, r]; cols += [ia + 2 * rp, ia + 2 * rp + 1, ic + rp]
            vals += [rs * np.einsum('kd,kd->k', relr, E1[rp]), rs * np.einsum('kd,kd->k', relr, E2[rp]), -rs]
            g0 = np.concatenate([g_c, g_p])
        else:
            g0 = g_c
        J = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nc + npr, nvar))
        # LP in the step dz:  g0 + J dz >= 0,  minimise dL
        lb = np.concatenate([np.full(3 * n, -trust), np.full(3 * n, -3 * trust), [-2 * trust], np.full(2 * P, -3 * trust), np.full(P, -cb)])
        ub = np.concatenate([np.full(3 * n, trust), np.full(3 * n, 3 * trust), [0.01], np.full(2 * P, 3 * trust), np.full(P, cb)])
        cvec = np.zeros(nvar); cvec[iL] = 1.0
        tl = lp_limit or max(5.0, (tlimit - (time.time() - t_start)) if tlimit else 120.0)
        if reg > 0:      # prefer small moves among the many optimal steps: + reg * sum |dC| + |dphi| (split variables)
            from scipy.sparse import hstack, vstack, identity, csr_matrix as csr
            m6 = 6 * n
            Sel = csr((np.ones(m6), (np.arange(m6), np.arange(m6))), shape=(m6, nvar))
            I6 = identity(m6, format='csr')
            A = vstack([hstack([-J, csr((nc + npr, m6))]), hstack([Sel, -I6]), hstack([-Sel, -I6])]).tocsr()
            b = np.concatenate([g0, np.zeros(2 * m6)])
            cv2 = np.concatenate([cvec, np.full(m6, reg)])
            bnd = np.concatenate([np.stack([lb, ub], 1), np.tile([0, 3 * trust], (m6, 1))])
            res = linprog(cv2, A_ub=A, b_ub=b, bounds=bnd, method='highs', options={'time_limit': tl})
            dz = res.x[:nvar] if res.status == 0 else np.zeros(nvar)
        else:
            res = linprog(cvec, A_ub=-J, b_ub=g0, bounds=np.stack([lb, ub], 1), method='highs', options={'time_limit': tl})
            dz = res.x if res.status == 0 else np.zeros(nvar)
        Cn = C + dz[:3 * n].reshape(n, 3)
        Ph = dz[3 * n:6 * n].reshape(n, 3)
        Rn = [exact.rod(Ph[i]) @ R[i] for i in range(n)]
        Ln, k, Cc = certify_fast(pb, Cn, Rn)
        zL = L + dz[iL]
        hist.append((it, float(zL), Ln, 0.0, P, res.status))
        if verbose: print(f'  it {it} L {zL:.12f} certified {Ln:.12f} (s {pb.s_of_L(Ln):.12f}) pairs {P} cons {nc + npr} status {res.status} {time.time() - t_start:.0f}s', flush=True)
        if abort is not None and abort(it, min(L, Ln)): break
        acc.append(min(L, Ln))
        if len(acc) > stall and acc[-stall - 1] - min(L, Ln) < stall_rel * L:
            if Ln < L - 1e-14: C, R, L = Cc, Rn, Ln
            break
        if Ln < L - 1e-14:
            imp = L - Ln; C, R, L = Cc, Rn, Ln
            trust = min(trust0, trust * 1.5)
            small = small + 1 if imp < 1e-12 else 0
            if small >= 3: break
        else:
            trust *= 0.5
            if trust < slp_floor: break
    return float(L), C, R, hist


def tighten_run(row, outer=600, tlimit=None, slp_floor=1e-6, abort=None, verbose=False, **kw):
    """Drop-in for exact.tighten_run(row, method='slp', ...)."""
    pb = exact.Problem(row['piece'], row['container'])
    C = np.array(row['C']); R = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in row['Q']]
    L0, _, C0 = certify_fast(pb, C, R)
    L, C1, R1, hist = solve(pb, C0, R, L0, outer=outer, tlimit=tlimit, slp_floor=slp_floor, abort=abort, verbose=verbose, **kw)
    L2, k, C2 = certify_fast(pb, C1, R1)
    return dict(piece=row['piece'], container=row['container'], n=row['n'], seed=row.get('seed'), mode=row.get('mode'),
                B=row.get('B'), s_start=pb.s_of_L(L0), s=pb.s_of_L(L2), C=np.asarray(C2).tolist(),
                Q=[exact.R_to_quat(r).tolist() for r in R1], iters=len(hist))
