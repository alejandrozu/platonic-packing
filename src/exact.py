"""Exact-contact tightening and legalization for packings of a convex polytope in a scaled convex polytope container.

Generalizes Yohei Nakajima's src/cubes/exact3.py (unit cubes in a cube) to any Platonic piece/container.
Internal units are those of src/sim.js: the piece has inradius 1/2; the container of size L is
{x : N_f . x <= (L/2) off_f} (centred at the origin), and the edge ratio is s = L / (2 rho_C).

solve(): minimize L subject to hard constraints
  - every vertex of every piece lies in the container,
  - for every nearby pair (i, j) a plane u.x = c has all vertices of i on one side and all vertices of j on the other.
Orientations R_i = Rod(phi_i) R0_i with phi re-based every outer iteration; plane normals are parametrized in the tangent
plane of the current normal. SLSQP with an analytic Jacobian, trust region on every variable. After each outer iteration
the result is independently legalized (centres scaled apart until the SAT test reports no overlap, then the tight
container is found by a 4-variable LP) and only accepted if that certified size decreased.
"""
import json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize, linprog

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK_JAC = []   # set to [None] to record the max |analytic - numeric| Jacobian error at the first outer iteration
SOL = json.load(open(os.path.join(HERE, 'solids.json')))


def _uniq(dirs):
    out = []
    for u in dirs:
        u = np.asarray(u, float); u = u / np.linalg.norm(u)
        if not any(abs(u @ w) > 1 - 1e-9 for w in out): out.append(u)
    return np.array(out)


class Problem:
    def __init__(self, piece, container=None):
        container = container or piece
        P = SOL[piece]; C = SOL[container]
        self.piece, self.container = piece, container
        self.edge = 0.5 / P['inradius']                      # internal piece edge
        self.V = np.array(P['V']) * self.edge                # local vertices (nv x 3)
        self.nv = len(self.V)
        self.edges = P['edges']
        self.faxes = _uniq(P['normals'])
        self.edirs = _uniq([self.V[j] - self.V[i] for i, j in P['edges']])
        self.circ = float(np.linalg.norm(self.V, axis=1).max())
        self.CN = np.array(C['normals'])                     # container face normals
        CV = np.array(C['V']) * self.edge
        beta = np.array([self.CN[f] @ CV[F[0]] for f, F in enumerate(C['faces'])])
        self.rhoC = float(beta.min())
        self.off = beta / self.rhoC                          # 1 for Platonic containers

    def s_of_L(self, L): return L / (2 * self.rhoC)

    def verts(self, c, R): return c + self.V @ R.T


def quat_to_R(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def R_to_quat(m):
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1) * 2; q = [.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]) * 2; q = [(m[2, 1] - m[1, 2]) / s, .25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s]
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]) * 2; q = [(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, .25 * s, (m[1, 2] + m[2, 1]) / s]
    else:
        s = math.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]) * 2; q = [(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, .25 * s]
    q = np.array(q); q /= np.linalg.norm(q)
    return q if q[0] >= 0 else -q


def skew(v): return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def rod(phi):
    th = np.linalg.norm(phi)
    if th < 1e-14: return np.eye(3) + skew(phi)
    K = skew(phi / th)
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def jac_left(phi):
    """Left Jacobian of SO(3): exp([phi + d]x) = exp([J_l d]x) exp([phi]x) + O(d^2)."""
    th = np.linalg.norm(phi); K = skew(phi)
    if th < 1e-7: return np.eye(3) + 0.5 * K + K @ K / 6
    return np.eye(3) + (1 - math.cos(th)) / th ** 2 * K + (th - math.sin(th)) / th ** 3 * K @ K


# ------------------------------------------------------------------ separating-axis machinery (floats)
def sat_axes(pb, RA, RB):
    EA, EB = pb.edirs @ RA.T, pb.edirs @ RB.T                     # world edge directions
    W = np.cross(EA[:, None, :], EB[None, :, :]).reshape(-1, 3)
    l = np.linalg.norm(W, axis=1); W = W[l > 1e-9] / l[l > 1e-9, None]
    return np.concatenate([pb.faxes @ RA.T, pb.faxes @ RB.T, W])


def sat_gap(pb, cA, RA, cB, RB):
    """Largest separation over the SAT axes (> 0 iff the closed pieces are disjoint; then it is a lower bound on the
    distance), with the oriented axis u (A below B) and the plane offset halfway between them."""
    VA, VB = pb.verts(cA, RA), pb.verts(cB, RB)
    U = sat_axes(pb, RA, RB)
    pa, pb_ = VA @ U.T, VB @ U.T
    g1 = pb_.min(0) - pa.max(0)          # A below B along u
    g2 = pa.min(0) - pb_.max(0)          # A above B
    i1, i2 = int(g1.argmax()), int(g2.argmax())
    if g1[i1] >= g2[i2]:
        return float(g1[i1]), U[i1], (pb_.min(0)[i1] + pa.max(0)[i1]) / 2
    return float(g2[i2]), -U[i2], -(pa.min(0)[i2] + pb_.max(0)[i2]) / 2


def overlap(pb, cA, RA, cB, RB, tol=1e-12):
    return sat_gap(pb, cA, RA, cB, RB)[0] < -tol


def tight_container(pb, P, R):
    """Smallest container size L over all translations t (LP in t, z); returns L, t (positions + t fit)."""
    X = np.concatenate([pb.verts(P[i], R[i]) for i in range(len(P))])
    S = (X @ pb.CN.T).max(0)
    F = len(S)
    res = linprog([0, 0, 0, 1], A_ub=np.hstack([pb.CN, -pb.off[:, None]]), b_ub=-S,
                  bounds=[(None, None)] * 4, method='highs')
    t = res.x[:3]
    z = float(((S + pb.CN @ t) / pb.off).max())     # feasible by construction at this t
    return 2 * z, t


def certify(pb, C, R):
    """Legalize: scale centres apart about their mean until no pair overlaps; return tight L and fitted centres."""
    C = np.array(C, float); n = len(C); cen = C.mean(0)
    lim = (2 * pb.circ) ** 2 + 1e-9

    def ok(k):
        P = cen + k * (C - cen)
        for i in range(n):
            for j in range(i + 1, n):
                if np.sum((P[i] - P[j]) ** 2) > lim: continue
                if overlap(pb, P[i], R[i], P[j], R[j]): return False
        return True

    lo = hi = 1.0
    if not ok(1.0):
        hi = 1.0001
        while not ok(hi): hi = 1 + (hi - 1) * 2
        for _ in range(60):
            m = (lo + hi) / 2
            if ok(m): hi = m
            else: lo = m
    P = cen + hi * (C - cen)
    L, t = tight_container(pb, P, R)
    return L, hi, P + t


def tangent_basis(u):
    a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(u, a); e1 /= np.linalg.norm(e1)
    return e1, np.cross(u, e1)


def solve(pb, C, R, L, outer=40, trust=0.03, verbose=False, tlimit=None, method='slsqp', slp_floor=1e-8):
    """method 'slsqp': each round runs SLSQP to convergence inside the trust region (Nakajima's scheme).
    method 'slp': each round solves ONE sparse LP of the linearized constraints (HiGHS) inside the trust region;
    the trust region grows on success and halves on failure. Both accept a round only if the certified size drops."""
    if method == 'slp' and outer == 40: outer = 600
    trust0 = trust; small = 0
    C = np.array(C, float); R = [np.array(r) for r in R]; n = len(C); nv = pb.nv
    t_start = time.time(); hist = []; fails = 0
    Fc = len(pb.CN)
    for it in range(outer):
        if tlimit and time.time() - t_start > tlimit: break
        lim = (2 * pb.circ + 4 * trust + 0.05) ** 2
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((C[i] - C[j]) ** 2) < lim]
        P = len(pairs)
        U0, E1, E2, c0, M0 = [], [], [], [], []
        for i, j in pairs:
            _, u, c = sat_gap(pb, C[i], R[i], C[j], R[j]); e1, e2 = tangent_basis(u)
            m0 = (C[i] + C[j]) / 2                                   # planes are u.(x - m0) = c
            U0.append(u); E1.append(e1); E2.append(e2); c0.append(c - u @ m0); M0.append(m0)
        U0, E1, E2, M0 = (np.array(A).reshape(P, 3) for A in (U0, E1, E2, M0)); c0 = np.array(c0)
        LG = np.stack([pb.V @ R[i].T for i in range(n)])          # n x nv x 3, world offsets at phi = 0
        Xc = C[:, None, :] + LG
        # Only constraints that can become active inside the trust region are passed to SLSQP (each step is
        # re-legalized and certified afterwards, so this pruning can never produce an invalid result).
        dmax = trust * (math.sqrt(3) + 3 * math.sqrt(3) * pb.circ)  # max vertex displacement in one step
        reach = dmax + 2 * trust + 1e-3
        slack = (L / 2) * pb.off[None, None, :] - Xc @ pb.CN.T    # n x nv x F
        ci, cv, cf = np.nonzero(slack < reach)
        nc = len(ci)
        cb = 2 * dmax + 1e-3                                       # bound on plane-offset moves
        rp, rs, rv, ri = [], [], [], []
        for p, (i, j) in enumerate(pairs):
            for sg, k in ((-1.0, i), (1.0, j)):
                rel = Xc[k] - M0[p]
                sl = sg * (rel @ U0[p] - c0[p])
                marg = cb + 3 * math.sqrt(2) * trust * (np.linalg.norm(rel, axis=1) + dmax) + dmax + 1e-3
                for v in np.nonzero(sl < marg)[0]:
                    rp.append(p); rs.append(sg); rv.append(v); ri.append(k)
        rp, rs, rv, ri = np.array(rp, int), np.array(rs), np.array(rv, int), np.array(ri, int)
        npr = len(rp)
        iL = 6 * n; ia = iL + 1; ic = ia + 2 * P
        nvar = ic + P
        z0 = np.concatenate([C.ravel(), np.zeros(3 * n), [L], np.zeros(2 * P), c0])

        def unpack(z):
            Cz = z[:3 * n].reshape(n, 3); Ph = z[3 * n:6 * n].reshape(n, 3)
            Rs = np.stack([rod(Ph[i]) for i in range(n)])
            Y = np.einsum('nab,nvb->nva', Rs, LG)                  # world offsets
            return Cz, Ph, Y

        def planes(z):
            ab = z[ia:ic].reshape(P, 2)
            Uraw = U0 + ab[:, :1] * E1 + ab[:, 1:] * E2
            nr = np.linalg.norm(Uraw, axis=1, keepdims=True)
            return Uraw / nr, nr

        def cons(z):
            Cz, Ph, Y = unpack(z); X = Cz[:, None, :] + Y
            g = [(z[iL] / 2) * pb.off[cf] - np.einsum('kd,kd->k', X[ci, cv], pb.CN[cf])]
            if npr:
                U, _ = planes(z); c = z[ic:]
                # side A (rs = -1): c - u.(x - m0) >= 0 ; side B (rs = +1): u.(x - m0) - c >= 0
                g.append(rs * (np.einsum('kd,kd->k', X[ri, rv] - M0[rp], U[rp]) - c[rp]))
            return np.concatenate(g)

        def jac(z):
            Cz, Ph, Y = unpack(z); X = Cz[:, None, :] + Y
            JL = np.stack([jac_left(Ph[i]) for i in range(n)])
            J = np.zeros((nc + npr, nvar))
            # container rows: g = (L/2) off - N.x ; dg/dc = -N ; dg/dphi = (N x y)^T J_l ; dg/dL = off/2
            rows = np.arange(nc)
            for d in range(3): J[rows, 3 * ci + d] = -pb.CN[cf, d]
            Gphi = np.einsum('kd,kde->ke', np.cross(pb.CN[cf], Y[ci, cv]), JL[ci])
            for d in range(3): J[rows, 3 * n + 3 * ci + d] = Gphi[:, d]
            J[rows, iL] = pb.off[cf] / 2
            if npr:
                U, nr = planes(z)
                rows = nc + np.arange(npr)
                dUa = (E1 - U * np.sum(U * E1, 1, keepdims=True)) / nr      # dU/da = (I - u u^T) E1 / |Uraw|
                dUb = (E2 - U * np.sum(U * E2, 1, keepdims=True)) / nr
                Ur = U[rp]; rel = X[ri, rv] - M0[rp]
                for d in range(3): J[rows, 3 * ri + d] = rs * Ur[:, d]
                # dx/dphi = -[y]x J_l  =>  dg/dphi = -rs (u x y)^T J_l
                Gp = np.einsum('kd,kde->ke', np.cross(Ur, Y[ri, rv]), JL[ri])
                for d in range(3): J[rows, 3 * n + 3 * ri + d] = -rs * Gp[:, d]
                J[rows, ia + 2 * rp] = rs * np.einsum('kd,kd->k', rel, dUa[rp])
                J[rows, ia + 2 * rp + 1] = rs * np.einsum('kd,kd->k', rel, dUb[rp])
                J[rows, ic + rp] = -rs
            return J

        bounds = ([(v - trust, v + trust) for v in C.ravel()] + [(-3 * trust, 3 * trust)] * (3 * n) +
                  [(L - 2 * trust, L + 0.01)] + [(-3 * trust, 3 * trust)] * (2 * P) + [(c - cb, c + cb) for c in c0])
        if CHECK_JAC and it == 0:   # compare the analytic Jacobian with central differences at a random point
            rng = np.random.default_rng(0)
            zt = z0 + rng.uniform(-1, 1, nvar) * np.r_[[trust] * 3 * n, [3 * trust] * 3 * n, [trust], [3 * trust] * 2 * P, [cb] * P]
            Ja = jac(zt); Jn = np.zeros_like(Ja); h = 1e-7
            for v in range(nvar):
                e = np.zeros(nvar); e[v] = h; Jn[:, v] = (cons(zt + e) - cons(zt - e)) / (2 * h)
            CHECK_JAC.append(float(np.abs(Ja - Jn).max()))
        if method == 'slp':
            from scipy.sparse import csr_matrix
            J0 = jac(z0); g0 = cons(z0); cvec = np.zeros(nvar); cvec[iL] = 1.0
            res = linprog(cvec, A_ub=csr_matrix(-J0), b_ub=g0 - J0 @ z0, bounds=bounds, method='highs')
            z = res.x if res.status == 0 else z0
        else:
            res = minimize(lambda z: z[iL], z0, jac=lambda z: np.eye(nvar)[iL], method='SLSQP', bounds=bounds,
                           constraints=[{'type': 'ineq', 'fun': cons, 'jac': jac}], options={'maxiter': 300, 'ftol': 1e-15})
            z = res.x
        Cn = z[:3 * n].reshape(n, 3); Ph = z[3 * n:6 * n].reshape(n, 3)
        Rn = [rod(Ph[i]) @ R[i] for i in range(n)]
        Ln, k, Cc = certify(pb, Cn, Rn)
        viol = -min(0.0, cons(z).min())
        hist.append((it, float(z[iL]), Ln, viol, P, res.status))
        if verbose: print(f'  it {it} L {z[iL]:.12f} certified {Ln:.12f} (s {pb.s_of_L(Ln):.12f}) viol {viol:.1e} pairs {P} cons {nc + npr} status {res.status} {time.time() - t_start:.0f}s', flush=True)
        if method == 'slp':
            if Ln < L - 1e-14:
                imp = L - Ln; C, R, L = Cc, Rn, Ln
                trust = min(trust0, trust * 1.5)
                small = small + 1 if imp < 1e-12 else 0
                if small >= 3: break
            else:
                trust *= 0.5
                if trust < slp_floor: break
            continue
        if Ln < L - 1e-13:
            imp = L - Ln
            C, R, L = Cc, Rn, Ln; fails = 0
            if imp < 1e-12: break
        else:
            trust *= 0.5; fails += 1
            if trust < 1e-4 or fails >= 3: break
    return float(L), C, R, hist


def tighten_run(row, outer=40, verbose=False, tlimit=None, method='slsqp', slp_floor=1e-8):
    """row: a runs/*.jsonl record. Returns dict with certified start/end sizes and the tightened configuration."""
    pb = Problem(row['piece'], row['container'])
    C = np.array(row['C']); R = [quat_to_R(q) for q in row['Q']]
    L0, _, C0 = certify(pb, C, R)
    if method == 'hybrid':      # fast sequential-LP descent, then SLSQP polish from there
        t0 = time.time()
        L1, C1, R1, h1 = solve(pb, C0, R, L0, verbose=verbose, tlimit=tlimit, method='slp', slp_floor=1e-4)
        rest = None if not tlimit else max(30, tlimit - (time.time() - t0))
        L, C1, R1, h2 = solve(pb, C1, R1, L1, outer=outer, trust=0.01, verbose=verbose, tlimit=rest, method='slsqp')
        hist = h1 + h2
    else:
        L, C1, R1, hist = solve(pb, C0, R, L0, outer=outer, verbose=verbose, tlimit=tlimit, method=method, slp_floor=slp_floor)
    L2, k, C2 = certify(pb, C1, R1)
    return dict(piece=row['piece'], container=row['container'], n=row['n'], seed=row['seed'], mode=row['mode'],
                B=row['B'], s_start=pb.s_of_L(L0), s=pb.s_of_L(L2), C=np.asarray(C2).tolist(),
                Q=[R_to_quat(r).tolist() for r in R1], iters=len(hist))


if __name__ == '__main__':
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    seed = int(sys.argv[2])
    row = next(r for r in rows if r['seed'] == seed)
    t0 = time.time()
    out = tighten_run(row, verbose=True)
    print(f"{row['piece']} n={row['n']} seed={seed}: s {out['s_start']:.12f} -> {out['s']:.12f} ({time.time() - t0:.1f}s)")
