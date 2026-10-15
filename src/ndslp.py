"""Sequential-LP tightening in any dimension (15 Oct 2026): src/fastslp.py generalized to d dimensions.

Variables of one round (all increments, inside a trust region): every centre (d), every rotation (a skew matrix,
d(d-1)/2 parameters, applied by the Cayley map), the container size L, and for every near pair its separating
hyperplane u.(x - M) = c: the normal moves in the (d-1)-dimensional tangent space of u, the offset c freely.
Constraints: every vertex near a container wall stays inside it, every vertex near a pair's hyperplane stays on its
side (linearized at the current point). Objective: shrink L (plus, optionally, reg x the L1 norm of the moves, which
picks small steps among the many optimal ones: fastslp's 14 Oct finding). Every round is re-legalized (ndsim.legalize:
centres scaled apart until every pair again has a separating hyperplane, starting from the LP's hyperplanes, then the
tight container) and accepted only if the legal size drops."""
import math, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, vstack, identity
import ndsim


def skew_index(d):
    return [(a, b) for a in range(d) for b in range(a + 1, d)]


def tangent_basis(U):
    """orthonormal bases (P x (d-1) x d) of the complements of the unit vectors U (Householder)"""
    P, d = U.shape
    out = np.empty((P, d - 1, d))
    for p in range(P):
        u = U[p]; e = np.zeros(d); k = int(np.argmax(np.abs(u))); e[k] = 1.0
        v = u - np.sign(u[k]) * e
        H = np.eye(d) - 2 * np.outer(v, v) / max(v @ v, 1e-300) if v @ v > 1e-24 else np.eye(d)
        cols = [c for c in range(d) if c != k]
        out[p] = H[:, cols].T
    return out


def cayley(Om):
    d = len(Om); I = np.eye(d)
    return np.linalg.solve(I - Om / 2, I + Om / 2)


def solve(pb, C, R, L, pairs, U, outer=600, trust=0.03, tlimit=None, slp_floor=1e-6, abort=None, verbose=False,
          stall=50, stall_rel=1e-7, reg=0.0, lp_limit=None):
    d = pb.d; n = len(C); SK = skew_index(d); m = len(SK)
    C = np.array(C, float); R = np.array(R, float)
    hint = {tuple(p): u for p, u in zip(pairs.tolist(), U)} if len(pairs) else {}
    trust0 = trust; small = 0; acc = []; hist = []; t_start = time.time()
    CN, off = pb.CN, pb.off
    for it in range(outer):
        if tlimit and time.time() - t_start > tlimit: break
        pairs = ndsim.near_pairs(C, (2 * pb.circ + 4 * trust + 0.05) ** 2); P = len(pairs)
        LG = np.einsum('vd,ned->nve', pb.V, R)                      # n x nv x d world offsets
        Xc = C[:, None, :] + LG
        if P:
            U0 = np.array([hint.get(tuple(p)) if tuple(p) in hint else C[p[1]] - C[p[0]] for p in pairs.tolist()], float)
            U0 /= np.linalg.norm(U0, axis=1, keepdims=True)
            g, U0, mid = ndsim.planes(pb, C, R, pairs, U0=U0)
            M0 = (C[pairs[:, 0]] + C[pairs[:, 1]]) / 2
            c0 = mid - np.einsum('pd,pd->p', U0, M0)
            E = tangent_basis(U0)                                    # P x (d-1) x d
        dmax = trust * (math.sqrt(d) + 3 * math.sqrt(2 * m) * pb.circ)
        reach = dmax + 2 * trust + 1e-3
        slack = (L / 2) * off[None, None, :] - Xc @ CN.T             # n x nv x F
        ci, cv, cf = np.nonzero(slack < reach); nc = len(ci)
        cb = 2 * dmax + 1e-3
        if P:
            rp, rs, rv, ri = [], [], [], []
            for sg, col in ((-1.0, 0), (1.0, 1)):
                k = pairs[:, col]
                rel = Xc[k] - M0[:, None, :]
                sl = sg * (np.einsum('pvd,pd->pv', rel, U0) - c0[:, None])
                marg = cb + 3 * math.sqrt(d) * trust * (np.linalg.norm(rel, axis=2) + dmax) + dmax + 1e-3
                pp, vv = np.nonzero(sl < marg)
                rp.append(pp); rv.append(vv); ri.append(k[pp]); rs.append(np.full(len(pp), sg))
            rp, rs, rv, ri = (np.concatenate(a) for a in (rp, rs, rv, ri))
        else:
            rp = rv = ri = np.zeros(0, int); rs = np.zeros(0)
        npr = len(rp)
        nd_ = d + m                                                    # per piece: centre + rotation
        iL = nd_ * n; ia = iL + 1; ic = ia + (d - 1) * P; nvar = ic + P
        rows, cols, vals = [], [], []
        # container rows: g = (L/2) off - N.x >= 0
        Yc = LG[ci, cv]; Nc = CN[cf]
        g_c = (L / 2) * off[cf] - np.einsum('kd,kd->k', Xc[ci, cv], Nc)
        r = np.arange(nc)
        for a in range(d):
            rows.append(r); cols.append(nd_ * ci + a); vals.append(-Nc[:, a])
        for t, (a, b) in enumerate(SK):
            rows.append(r); cols.append(nd_ * ci + d + t); vals.append(-(Nc[:, a] * Yc[:, b] - Nc[:, b] * Yc[:, a]))
        rows.append(r); cols.append(np.full(nc, iL)); vals.append(off[cf] / 2)
        if npr:
            Ur = U0[rp]; relr = Xc[ri, rv] - M0[rp]; Yr = LG[ri, rv]
            g_p = rs * (np.einsum('kd,kd->k', relr, Ur) - c0[rp])
            r = nc + np.arange(npr)
            for a in range(d):
                rows.append(r); cols.append(nd_ * ri + a); vals.append(rs * Ur[:, a])
            for t, (a, b) in enumerate(SK):
                rows.append(r); cols.append(nd_ * ri + d + t); vals.append(rs * (Ur[:, a] * Yr[:, b] - Ur[:, b] * Yr[:, a]))
            for t in range(d - 1):
                rows.append(r); cols.append(ia + (d - 1) * rp + t); vals.append(rs * np.einsum('kd,kd->k', relr, E[rp, t]))
            rows.append(r); cols.append(ic + rp); vals.append(-rs)
            g0 = np.concatenate([g_c, g_p])
        else:
            g0 = g_c
        J = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nc + npr, nvar))
        per = np.concatenate([np.full(d, trust), np.full(m, 3 * trust)])
        lb = np.concatenate([-np.tile(per, n), [-2 * trust], np.full((d - 1) * P, -3 * trust), np.full(P, -cb)])
        ub = np.concatenate([np.tile(per, n), [0.01], np.full((d - 1) * P, 3 * trust), np.full(P, cb)])
        cvec = np.zeros(nvar); cvec[iL] = 1.0
        tl = lp_limit or min(30.0, max(5.0, (tlimit - (time.time() - t_start)) if tlimit else 120.0))
        if reg > 0:
            mm = nd_ * n
            Sel = csr_matrix((np.ones(mm), (np.arange(mm), np.arange(mm))), shape=(mm, nvar))
            I6 = identity(mm, format='csr')
            A = vstack([hstack([-J, csr_matrix((nc + npr, mm))]), hstack([Sel, -I6]), hstack([-Sel, -I6])]).tocsr()
            b = np.concatenate([g0, np.zeros(2 * mm)])
            cv2 = np.concatenate([cvec, np.full(mm, reg)])
            bnd = np.concatenate([np.stack([lb, ub], 1), np.stack([np.zeros(mm), np.tile(per, n)], 1)])
            res = linprog(cv2, A_ub=A, b_ub=b, bounds=bnd, method='highs', options={'time_limit': tl})
            dz = res.x[:nvar] if res.status == 0 else np.zeros(nvar)
        else:
            res = linprog(cvec, A_ub=-J, b_ub=g0, bounds=np.stack([lb, ub], 1), method='highs', options={'time_limit': tl})
            dz = res.x if res.status == 0 else np.zeros(nvar)
        Z = dz[:nd_ * n].reshape(n, nd_)
        Cn = C + Z[:, :d]
        Rn = np.empty_like(R)
        for i in range(n):
            Om = np.zeros((d, d))
            for t, (a, b) in enumerate(SK): Om[a, b] = Z[i, d + t]; Om[b, a] = -Z[i, d + t]
            Rn[i] = cayley(Om) @ R[i]
        newhint = {}
        if P:
            Un = U0 + np.einsum('pt,ptd->pd', dz[ia:ic].reshape(P, d - 1), E)
            Un /= np.linalg.norm(Un, axis=1, keepdims=True)
            newhint = {tuple(p): u for p, u in zip(pairs.tolist(), Un)}
        lg = ndsim.legalize(pb, Cn, Rn, hint=newhint)
        Ln = lg['L']
        zL = L + dz[iL]
        hist.append((it, float(zL), Ln, P, res.status))
        if verbose: print(f'  it {it} L {zL:.12f} legal {Ln:.12f} (s {pb.s_of_L(Ln):.12f}) pairs {P} cons {nc + npr} status {res.status} {time.time() - t_start:.1f}s', flush=True)
        if abort is not None and abort(it, min(L, Ln)): break
        acc.append(min(L, Ln))
        if len(acc) > stall and acc[-stall - 1] - min(L, Ln) < stall_rel * L:
            if Ln < L - 1e-14: C, R, L = lg['C'], lg['R'], Ln; hint = _hint(lg)
            break
        if Ln < L - 1e-14:
            imp = L - Ln; C, R, L = lg['C'], lg['R'], Ln; hint = _hint(lg)
            trust = min(trust0, trust * 1.5)
            small = small + 1 if imp < 1e-12 else 0
            if small >= 3: break
        else:
            trust *= 0.5
            if trust < slp_floor: break
    return float(L), C, R, hist


def _hint(lg):
    return {tuple(p): u for p, u in zip(lg['pairs'].tolist(), lg['U'])} if len(lg['pairs']) else {}


def tighten(pb, C, R, tlimit=None, reg=0.0, verbose=False, **kw):
    """legalize, SLP, legalize; returns dict(s_start, s, C, R, iters)"""
    lg0 = ndsim.legalize(pb, C, R)
    pairs = lg0['pairs']; U = lg0['U']
    L, C1, R1, hist = solve(pb, lg0['C'], lg0['R'], lg0['L'], pairs, U, tlimit=tlimit, reg=reg, verbose=verbose, **kw)
    lg = ndsim.legalize(pb, C1, R1)
    if lg['L'] > L * (1 + 1e-12):            # the final re-legalization lost more than float noise: keep the SLP's own
        lg = dict(L=L, C=C1, R=R1)
    return dict(s_start=pb.s_of_L(lg0['L']), s=pb.s_of_L(lg['L']), C=np.asarray(lg['C']), R=np.asarray(lg['R']), iters=len(hist))
