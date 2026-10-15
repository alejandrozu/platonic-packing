"""Soft-to-rigid packing of regular polytopes in any dimension d (15 Oct 2026, higher-dimensional packings).

The d-dimensional generalization of src/sim.js + src/geom.js (Nakajima's soft-to-rigid scheme), compiled with numba.

Units and shapes are those of the 3D code: the piece P has inradius 1/2; at softness r it is S_r = (1 - 2r) P (+) B(r)
(r = 1/2: the inscribed ball; r = 0: P), which lies inside P (every regular polytope is tangential). The container of
size L is {x : N_f . x <= (L/2) off_f}, the container polytope at the piece's edge length scaled by s = L / (2 rho_C).

What changes with the dimension:
  * orientation: a rotation matrix R in SO(d); an increment is a skew-symmetric matrix W (d(d-1)/2 parameters) applied
    by the Cayley map R <- (I - W/2)^-1 (I + W/2) R, which stays exactly orthogonal;
  * torque: the derivative of u.(c + R y) with respect to W is the bivector u y^T - y u^T;
  * overlap of two pieces: the 3D code enumerates separating axes (face normals and edge x edge); in d dimensions the
    candidates are normals to pairs of faces of complementary dimensions, far too many for the 120-cell (600
    vertices, 1200 edges, 720 pentagons). Instead every near pair keeps a unit axis u (from piece i towards piece j)
    across steps. The pair's signed gap along u is
        g(u) = min_{y in P_j} u.y - max_{x in P_i} u.x,
    and max_u g(u) is exactly the signed distance (the Euclidean distance when apart, minus the penetration depth when
    overlapping). Each step improves u by projected super-gradient ascent (the super-gradient is the difference of
    the two support points), with a per-pair adaptive angle; a tracked axis is a lower bound of the true signed
    distance, so a legal verdict (g >= 0) always comes with a witness hyperplane;
  * support points by hill climbing on the polytope's edge graph from the previous support vertex (a linear function
    has no local maxima on a convex polytope's vertices), so a query costs O(degree) instead of O(vertices).
Energy, schedule and integrator (heavy ball, velocity cap, annealed noise, pressure on L) are those of sim.js."""
import math, os, sys, importlib.util
import numpy as np
_cov = importlib.util.find_spec('coverage')
if _cov and _cov.origin and _cov.origin.replace(os.sep, '/').endswith('scripts/coverage.py'):
    sys.modules['coverage'] = None     # the project's scripts/coverage.py is not coverage.py: numba must not import it
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polytopes_nd

_DATA = None


def data():
    global _DATA
    if _DATA is None: _DATA = polytopes_nd.load()
    return _DATA


class Problem:
    """piece and container ids of src/polytopes_nd.json (e.g. 'c24', 'c120', 'hc5')"""
    def __init__(self, piece, container):
        D = data(); P, Q = D[piece], D[container]
        assert P['dim'] == Q['dim']
        self.piece, self.container, self.d = piece, container, P['dim']
        sc = 0.5 / P['inradius']                         # internal units: piece inradius 1/2
        self.scale = sc
        self.V = np.ascontiguousarray(np.array(P['Vf']) * sc)
        self.nv = len(self.V)
        self.edge = P['edge'] * sc
        self.circ = float(np.linalg.norm(self.V, axis=1).max())
        cs = P['edge'] / Q['edge'] * sc                 # container polytope at the piece's edge length
        self.cscale = cs
        self.CV = np.array(Q['Vf']) * cs
        self.CN = np.ascontiguousarray(np.array(Q['N']))
        beta = np.array(Q['beta']) * cs
        self.rhoC = float(beta.min()); self.off = np.ascontiguousarray(beta / self.rhoC)
        self.Ccirc = float(np.linalg.norm(self.CV, axis=1).max())
        self.volume = P['volume'] * sc ** self.d; self.Cvolume = Q['volume'] * cs ** self.d
        # edge graph (CSR) for hill climbing
        nb = [[] for _ in range(self.nv)]
        for i, j in P['edges']: nb[i].append(j); nb[j].append(i)
        self.adj_ptr = np.cumsum([0] + [len(x) for x in nb]).astype(np.int64)
        self.adj_idx = np.array([j for x in nb for j in x], dtype=np.int64)
        self.F = len(self.CN)

    def s_of_L(self, L): return L / (2 * self.rhoC)
    def L_of_s(self, s): return 2 * self.rhoC * s


# ------------------------------------------------------------------------------------------------ kernels
@njit(cache=True)
def _support(P, aptr, aidx, w, start):
    """argmax_v w . P[v] by steepest ascent on the edge graph from `start`; returns (index, value)"""
    d = P.shape[1]
    best = start; bv = 0.0
    for t in range(d): bv += w[t] * P[start, t]
    while True:
        nxt = -1; nv = bv
        for e in range(aptr[best], aptr[best + 1]):
            v = aidx[e]; val = 0.0
            for t in range(d): val += w[t] * P[v, t]
            if val > nv + 1e-15 * (1.0 + abs(nv)): nv = val; nxt = v
        if nxt < 0: return best, bv
        best = nxt; bv = nv


@njit(cache=True)
def _pair_gap(C, R, P, aptr, aidx, k, i, j, u, si, sj):
    """gap along u between core i (below) and core j (above), with warm-start support indices; returns gap, ia, ib"""
    d = C.shape[1]
    bi = np.zeros(d); bj = np.zeros(d)
    for a in range(d):
        s1 = 0.0; s2 = 0.0
        for b in range(d):
            s1 += R[i, b, a] * u[b]; s2 -= R[j, b, a] * u[b]
        bi[a] = s1; bj[a] = s2
    ia, hA = _support(P, aptr, aidx, bi, si)
    ib, hB = _support(P, aptr, aidx, bj, sj)
    ci = 0.0; cj = 0.0
    for a in range(d): ci += u[a] * C[i, a]; cj += u[a] * C[j, a]
    return (cj - k * hB) - (ci + k * hA), ia, ib


@njit(cache=True)
def _world(C, R, P, k, i, v, out):
    d = C.shape[1]
    for a in range(d):
        s = 0.0
        for b in range(d): s += R[i, a, b] * P[v, b]
        out[a] = C[i, a] + k * s


@njit(cache=True)
def _track(C, R, P, aptr, aidx, k, i, j, U, TH, SI, iters):
    """improve the axis U[i, j] by `iters` super-gradient steps; returns the gap"""
    d = C.shape[1]
    u = U[i, j].copy()
    g, ia, ib = _pair_gap(C, R, P, aptr, aidx, k, i, j, u, SI[i, j], SI[j, i])
    xa = np.zeros(d); xb = np.zeros(d); u2 = np.zeros(d)
    for _ in range(iters):
        _world(C, R, P, k, i, ia, xa); _world(C, R, P, k, j, ib, xb)
        wu = 0.0
        for a in range(d): wu += (xb[a] - xa[a]) * u[a]
        tn = 0.0
        for a in range(d):
            u2[a] = (xb[a] - xa[a]) - wu * u[a]; tn += u2[a] * u2[a]
        tn = math.sqrt(tn)
        if tn < 1e-14 * (1.0 + abs(wu)): break
        th = TH[i, j]; c = math.cos(th); s = math.sin(th) / tn
        nn = 0.0
        for a in range(d):
            u2[a] = c * u[a] + s * u2[a]; nn += u2[a] * u2[a]
        nn = math.sqrt(nn)
        for a in range(d): u2[a] /= nn
        g2, ia2, ib2 = _pair_gap(C, R, P, aptr, aidx, k, i, j, u2, ia, ib)
        if g2 > g:
            for a in range(d): u[a] = u2[a]
            g = g2; ia = ia2; ib = ib2; TH[i, j] = min(th * 1.5, 0.5)
        else:
            TH[i, j] = max(th * 0.5, 1e-9)
    for a in range(d): U[i, j, a] = u[a]
    SI[i, j] = ia; SI[j, i] = ib
    return g


@njit(cache=True)
def _cayley_left(Wm, Rm, out):
    """out = (I - W/2)^-1 (I + W/2) Rm, by Gaussian elimination with partial pivoting (d <= 8)"""
    d = Wm.shape[0]
    A = np.empty((d, 2 * d))
    for a in range(d):
        for b in range(d):
            A[a, b] = (1.0 if a == b else 0.0) - 0.5 * Wm[a, b]
            s = 0.0
            for c in range(d): s += ((1.0 if a == c else 0.0) + 0.5 * Wm[a, c]) * Rm[c, b]
            A[a, d + b] = s
    for c in range(d):
        p = c
        for r in range(c + 1, d):
            if abs(A[r, c]) > abs(A[p, c]): p = r
        if p != c:
            for t in range(2 * d):
                x = A[c, t]; A[c, t] = A[p, t]; A[p, t] = x
        pv = A[c, c]
        for t in range(2 * d): A[c, t] /= pv
        for r in range(d):
            if r != c and A[r, c] != 0.0:
                f = A[r, c]
                for t in range(2 * d): A[r, t] -= f * A[c, t]
    for a in range(d):
        for b in range(d): out[a, b] = A[a, d + b]


@njit(cache=True)
def _orth(R):
    """re-orthonormalize every rotation (modified Gram-Schmidt on the rows; keeps det +1 for a near-rotation)"""
    n, d, _ = R.shape
    for i in range(n):
        for a in range(d):
            for b in range(a):
                s = 0.0
                for t in range(d): s += R[i, a, t] * R[i, b, t]
                for t in range(d): R[i, a, t] -= s * R[i, b, t]
            nn = 0.0
            for t in range(d): nn += R[i, a, t] ** 2
            nn = math.sqrt(nn)
            for t in range(d): R[i, a, t] /= nn


@njit(cache=True)
def _phase(C, R, Vel, W, Lst, U, UOK, TH, SI, WI, P, aptr, aidx, circ, CN, off, mask, wts,
           steps, r_a, r_b, mu_a, mu_b, mu_geom, nz_a, nz_b, moveL, iters, seed):
    """`steps` dynamics steps; softness r linear r_a -> r_b, pressure mu linear (or geometric) mu_a -> mu_b, noise
    linear nz_a -> nz_b. State arrays are updated in place; Lst = [L, vL]. Returns the last step's total overlap."""
    np.random.seed(seed)
    n, d = C.shape
    F = CN.shape[0]
    beta = 0.85; cap = 0.03; lr = 0.04
    GC = np.zeros((n, d)); GW = np.zeros((n, d, d))
    Rn = np.empty((d, d)); Om = np.empty((d, d))
    ya = np.zeros(d); yb = np.zeros(d); u = np.zeros(d); bd = np.zeros(d)
    tot = 0.0
    for st in range(steps):
        x = st / max(1, steps - 1) if steps > 1 else 1.0
        r = r_a + (r_b - r_a) * x
        mu = mu_a * (mu_b / mu_a) ** x if (mu_geom and mu_a > 0) else mu_a + (mu_b - mu_a) * x
        nz = nz_a + (nz_b - nz_a) * x
        k = 1.0 - 2.0 * r
        L = Lst[0]
        GC[:] = 0.0; GW[:] = 0.0
        lim = (2.0 * (k * circ + r) + 1e-3) ** 2
        tot = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                d2 = 0.0
                for a in range(d): d2 += (C[j, a] - C[i, a]) ** 2
                if d2 > lim:
                    UOK[i, j] = 0; continue
                if k <= 1e-12:
                    dist = math.sqrt(d2) + 1e-300
                    for a in range(d): u[a] = (C[j, a] - C[i, a]) / dist
                    g = dist
                    for a in range(d): ya[a] = 0.0; yb[a] = 0.0
                else:
                    extra = 0
                    if UOK[i, j] == 0:
                        dist = math.sqrt(d2) + 1e-300
                        for a in range(d): U[i, j, a] = (C[j, a] - C[i, a]) / dist
                        TH[i, j] = 0.2; UOK[i, j] = 1; extra = 6
                    g = _track(C, R, P, aptr, aidx, k, i, j, U, TH, SI, iters + extra)
                    for a in range(d): u[a] = U[i, j, a]
                    _world(C, R, P, k, i, SI[i, j], ya); _world(C, R, P, k, j, SI[j, i], yb)
                    for a in range(d): ya[a] -= C[i, a]; yb[a] -= C[j, a]
                o = 2.0 * r - g
                if o <= 0.0: continue
                tot += o
                c2 = 2.0 * o * wts[i, j]
                for a in range(d):
                    GC[i, a] += c2 * u[a]; GC[j, a] -= c2 * u[a]
                for a in range(d):
                    for b in range(d):
                        GW[i, a, b] += c2 * (u[a] * ya[b] - ya[a] * u[b])
                        GW[j, a, b] -= c2 * (u[a] * yb[b] - yb[a] * u[b])
        gL = mu
        for i in range(n):
            for f in range(F):
                cn = 0.0
                for a in range(d): cn += CN[f, a] * C[i, a]
                bound = 0.5 * L * off[f]
                if cn + k * circ + r <= bound: continue
                for a in range(d):
                    s = 0.0
                    for b in range(d): s += R[i, b, a] * CN[f, b]
                    bd[a] = s
                v, h = _support(P, aptr, aidx, bd, WI[i, f])
                WI[i, f] = v
                q = cn + k * h + r - bound
                if q <= 0.0: continue
                tot += q
                _world(C, R, P, k, i, v, ya)
                for a in range(d): ya[a] -= C[i, a]
                for a in range(d):
                    GC[i, a] += 2.0 * q * CN[f, a]
                    for b in range(d): GW[i, a, b] += 2.0 * q * (CN[f, a] * ya[b] - ya[a] * CN[f, b])
                if moveL: gL -= 2.0 * q * off[f]
        ball = r >= 0.4999
        for i in range(n):
            vm = 0.0
            for a in range(d):
                Vel[i, a] = beta * Vel[i, a] - lr * GC[i, a]; vm += Vel[i, a] ** 2
            vm = math.sqrt(vm)
            if vm > cap:
                for a in range(d): Vel[i, a] *= cap / vm
            wm = 0.0
            for a in range(d):
                for b in range(d):
                    W[i, a, b] = 0.0 if ball else beta * W[i, a, b] - lr * GW[i, a, b]
                    wm += W[i, a, b] ** 2
            wm = math.sqrt(wm / 2.0)
            if wm > cap:
                for a in range(d):
                    for b in range(d): W[i, a, b] *= cap / wm
            nzi = nz * mask[i]
            for a in range(d):
                C[i, a] += Vel[i, a] + (nzi * np.random.standard_normal() if nzi > 0 else 0.0)
            if not ball:
                for a in range(d):
                    Om[a, a] = 0.0
                    for b in range(a + 1, d):
                        e = W[i, a, b] + (1.5 * nzi * np.random.standard_normal() if nzi > 0 else 0.0)
                        Om[a, b] = e; Om[b, a] = -e
                _cayley_left(Om, R[i], Rn)
                for a in range(d):
                    for b in range(d): R[i, a, b] = Rn[a, b]
        if moveL:
            Lst[1] = beta * Lst[1] - 0.02 * gL
            if abs(Lst[1]) > cap: Lst[1] = cap if Lst[1] > 0 else -cap
            Lst[0] += Lst[1]
        if st % 500 == 499: _orth(R)
    _orth(R)
    return tot


@njit(cache=True)
def _planes(C, R, P, aptr, aidx, pairs, U, iters, tol):
    """for each listed pair (i, j): the best separating axis found by super-gradient ascent from U[p] (rigid pieces);
    returns the gaps and updates U in place (the witness hyperplane of pair p is u.x = mid, see planes())"""
    m = pairs.shape[0]; n, d = C.shape
    g = np.empty(m)
    Ux = np.zeros((n, n, d)); TH = np.zeros((n, n)); SI = np.zeros((n, n), dtype=np.int64)
    for p in range(m):
        i = pairs[p, 0]; j = pairs[p, 1]
        for a in range(d): Ux[i, j, a] = U[p, a]
        TH[i, j] = 0.05
        last = -1e300; gg = 0.0
        for rnd in range(iters // 10 + 1):
            gg = _track(C, R, P, aptr, aidx, 1.0, i, j, Ux, TH, SI, 10)
            if TH[i, j] < 1e-12 or (gg - last) < tol * 1e-3 and TH[i, j] < 1e-7: break
            last = gg
        g[p] = gg
        for a in range(d): U[p, a] = Ux[i, j, a]
    return g


@njit(cache=True)
def _container_support(C, R, P, aptr, aidx, CN):
    """S_f = max over all pieces and vertices of N_f . x (rigid pieces)"""
    n, d = C.shape; F = CN.shape[0]
    S = np.full(F, -1e300)
    bd = np.zeros(d)
    for i in range(n):
        for f in range(F):
            for a in range(d):
                s = 0.0
                for b in range(d): s += R[i, b, a] * CN[f, b]
                bd[a] = s
            v, h = _support(P, aptr, aidx, bd, 0)
            cn = 0.0
            for a in range(d): cn += CN[f, a] * C[i, a]
            if cn + h > S[f]: S[f] = cn + h
    return S


# ------------------------------------------------------------------------------------------------ python layer
class State:
    def __init__(self, pb, C, R, L):
        n, d, F = len(C), pb.d, pb.F
        self.pb = pb
        self.C = np.ascontiguousarray(np.array(C, float)); self.R = np.ascontiguousarray(np.array(R, float))
        self.Vel = np.zeros((n, d)); self.W = np.zeros((n, d, d)); self.Lst = np.array([float(L), 0.0])
        self.U = np.zeros((n, n, d)); self.UOK = np.zeros((n, n), np.int8); self.TH = np.zeros((n, n))
        self.SI = np.zeros((n, n), np.int64); self.WI = np.zeros((n, F), np.int64)
        self.mask = np.ones(n); self.wts = np.ones((n, n)); self.seed = 1

    def phase(self, steps, r_a, r_b, mu_a, mu_b, nz_a, nz_b, moveL=True, mu_geom=False, iters=1):
        pb = self.pb; self.seed += 1
        return _phase(self.C, self.R, self.Vel, self.W, self.Lst, self.U, self.UOK, self.TH, self.SI, self.WI, pb.V,
                      pb.adj_ptr, pb.adj_idx, pb.circ, pb.CN, pb.off, self.mask, self.wts, int(steps), float(r_a), float(r_b),
                      float(mu_a), float(mu_b), bool(mu_geom), float(nz_a), float(nz_b), bool(moveL), int(iters), int(self.seed % 2 ** 31))

    @property
    def L(self): return float(self.Lst[0])


def random_rotation(rng, d):
    A = rng.normal(size=(d, d)); Q, Rr = np.linalg.qr(A); Q = Q * np.sign(np.diag(Rr))
    if np.linalg.det(Q) < 0: Q[:, 0] = -Q[:, 0]
    return Q


def default_L0(pb, n):
    """initial container: balls (diameter 1) at packing fraction ~0.07 (the 3D rule), centres 0.7 inside every wall"""
    vb = math.pi ** (pb.d / 2) / math.gamma(pb.d / 2 + 1) * 0.5 ** pb.d
    L = 2.0
    while n * vb / (pb.Cvolume * pb.s_of_L(L) ** pb.d) > 0.07: L *= 1.02
    return max(L, 2 * (0.7 + 0.35))


def random_inside(pb, L, rng, margin):
    """a random point of the container kept `margin` inside every wall: a Dirichlet-random convex combination of the
    container's vertices, pulled towards the centre as far as the margin needs (rejection sampling from a bounding box
    fails for the pointed simplices of 5 and 6 dimensions)"""
    V = pb.CV * (pb.s_of_L(L))
    lam = rng.dirichlet(np.ones(len(V)) * 0.5)
    p = lam @ V
    lim = (L / 2) * pb.off - margin
    if np.any(lim <= 0): return np.zeros(pb.d)
    np_ = pb.CN @ p
    t = np.min(np.where(np_ > 0, lim / np.maximum(np_, 1e-300), np.inf))
    return p * min(1.0, t * (1 - 1e-9))


def near_pairs(C, lim2):
    n = len(C); iu, ju = np.triu_indices(n, 1)
    d2 = ((C[iu] - C[ju]) ** 2).sum(1); s = d2 < lim2
    return np.ascontiguousarray(np.stack([iu[s], ju[s]], 1).astype(np.int64))


def planes(pb, C, R, pairs, U0=None, iters=400, tol=1e-13):
    """best separating axes (lower bounds of the signed distances) of the listed pairs, the witness offsets (mid-gap)"""
    C = np.ascontiguousarray(C, float); R = np.ascontiguousarray(R, float)
    if not len(pairs): return np.zeros(0), np.zeros((0, pb.d)), np.zeros(0)
    if U0 is None:
        U0 = C[pairs[:, 1]] - C[pairs[:, 0]]; U0 = U0 / np.linalg.norm(U0, axis=1, keepdims=True)
    U = np.ascontiguousarray(U0.copy())
    g = _planes(C, R, pb.V, pb.adj_ptr, pb.adj_idx, pairs, U, int(iters), float(tol))
    X = C[:, None, :] + np.einsum('vd,ned->nve', pb.V, R)
    a = np.einsum('pvd,pd->pv', X[pairs[:, 0]], U).max(1); b = np.einsum('pvd,pd->pv', X[pairs[:, 1]], U).min(1)
    return b - a, U, (a + b) / 2           # exact (float) gaps along the final axes


def tight_container(pb, C, R):
    """smallest L (any translation t) with every vertex inside: min z s.t. S_f + N_f.t <= z off_f; returns L, t"""
    from scipy.optimize import linprog
    S = _container_support(np.ascontiguousarray(C, float), np.ascontiguousarray(R, float), pb.V, pb.adj_ptr, pb.adj_idx, pb.CN)
    d = pb.d
    A = np.hstack([pb.CN, -pb.off[:, None]]); c = np.zeros(d + 1); c[-1] = 1
    res = linprog(c, A_ub=A, b_ub=-S, bounds=[(None, None)] * (d + 1), method='highs')
    t = res.x[:d] if res.status == 0 else np.zeros(d)
    z = float(np.max((S + pb.CN @ t) / pb.off))          # exact feasibility at the chosen t
    return 2 * z, t


def legalize(pb, C, R, tol=1e-12, st=None, hint=None):
    """scale the centres apart about their mean until every near pair has a separating hyperplane (gap >= -tol along
    its tracked axis), then the tight container. st: the simulation state, whose tracked axes start the search (else
    the centre directions; the better of the two is kept). Returns dict(L, s, k, C, R, pairs, U)."""
    C = np.array(C, float); R = np.ascontiguousarray(np.array(R, float)); cen = C.mean(0)
    lim = (2 * pb.circ) ** 2 + 1e-9
    near = near_pairs(C, lim * 1.2 ** 2)
    Uall = C[near[:, 1]] - C[near[:, 0]] if len(near) else np.zeros((0, pb.d))
    if len(near):
        Uall /= np.linalg.norm(Uall, axis=1, keepdims=True)
        if st is not None:
            hs = st.UOK[near[:, 0], near[:, 1]] > 0
            if hs.any():
                g0, _, _ = planes(pb, C, R, near[hs], U0=Uall[hs], iters=0)
                Uh = st.U[near[hs, 0], near[hs, 1]]
                g1, _, _ = planes(pb, C, R, near[hs], U0=Uh, iters=0)
                Uall[np.nonzero(hs)[0][g1 > g0]] = Uh[g1 > g0]
        if hint is not None:          # {(i, j): axis} (e.g. the planes of a sequential-LP step)
            idx = [t for t, (i, j) in enumerate(near.tolist()) if (i, j) in hint]
            if idx:
                idx = np.array(idx); Uh = np.array([hint[tuple(near[t])] for t in idx])
                g0, _, _ = planes(pb, C, R, near[idx], U0=Uall[idx], iters=0)
                g1, _, _ = planes(pb, C, R, near[idx], U0=Uh, iters=0)
                Uall[idx[g1 > g0]] = Uh[g1 > g0]
    k = 1.0
    for it in range(80):
        P = cen + k * (C - cen)
        if not len(near): break
        sel = ((P[near[:, 0]] - P[near[:, 1]]) ** 2).sum(1) <= lim
        if not sel.any(): break
        pr = near[sel]
        g, Us, _ = planes_lp(pb, P, R, pr, U0=Uall[sel], need=-tol)
        Uall[sel] = Us
        bad = g < -tol
        if not bad.any(): break
        dc = C[pr[bad, 1]] - C[pr[bad, 0]]
        proj = np.sum(Us[bad] * dc, axis=1)
        need = np.where(proj > 1e-9, -g[bad] / np.maximum(proj, 1e-9), 0.01)
        k = k + float(need.max()) * (1 + 1e-6) + 1e-14
    P = cen + k * (C - cen)
    L, t = tight_container(pb, P, R)
    return dict(L=L, s=pb.s_of_L(L), k=k, C=P + t, R=R, pairs=near, U=Uall)


def fresh(pb, n, seed, B=1.0, iters=1):
    """full soft-to-rigid run from random balls (sim.js 'run', Nakajima's schedule)"""
    rng = np.random.default_rng(seed)
    L0 = default_L0(pb, n)
    C = np.array([random_inside(pb, L0, rng, 0.7) for _ in range(n)])
    R = np.array([random_rotation(rng, pb.d) for _ in range(n)])
    st = State(pb, C, R, L0); st.seed = seed * 7919 + 13
    mu = 0.02
    st.phase(int(5000 * B), 0.5, 0.5, mu * 3, mu * 3, 0.015, 0.0, iters=iters)
    st.phase(int(45000 * B), 0.5, 0.0, mu, mu, 0.004, 0.0, iters=iters)
    st.phase(int(3000 * B), 0.0, 0.0, mu, mu * 1e-4, 0.0, 0.0, mu_geom=True, iters=iters)
    out = legalize(pb, st.C, st.R, st=st)
    out['Lsoft'] = st.L
    return out


def best_hole(pb, C, L, rng, tries=4000):
    Rc = (L / 2) * pb.Ccirc / pb.rhoC
    P = rng.uniform(-Rc, Rc, (tries, pb.d))
    ok = np.all(P @ pb.CN.T <= (L / 2) * pb.off - 0.5, axis=1); P = P[ok]
    if not len(P): return np.zeros(pb.d)
    if not len(C): return P[0]
    d2 = ((P[:, None, :] - np.asarray(C)[None, :, :]) ** 2).sum(-1).min(1)
    return P[int(np.argmax(d2))]


def arrangement_change(pb, C0, C1, focus=None):
    n = len(C0); R2 = (2 * pb.circ) ** 2
    iu, ju = np.triu_indices(n, 1)
    d0 = ((C0[iu] - C0[ju]) ** 2).sum(1); d1 = ((C1[iu] - C1[ju]) ** 2).sum(1)
    sel = (d0 <= R2) | (d1 <= R2)
    if focus is not None: sel &= focus[iu] | focus[ju]
    if not sel.any(): return 0.0
    return float(np.sqrt(np.mean((np.sqrt(d1[sel]) - np.sqrt(d0[sel])) ** 2)) / pb.edge)


def hop(pb, C, R, L, seed, expand=0.03, rh=0.12, noise=0.004, shake=400, morph=6000, settle=1500, mu=0.02, minDiff=0.15,
        maxEsc=8, add=0, remove=(), focus=0, iters=1):
    """sim.js 'hop': remove / add pieces, expand, soften to r = rh, shake at fixed size until the arrangement changed by
    minDiff piece edges (escalating), re-sharpen under pressure, settle, legalize"""
    rng = np.random.default_rng(seed)
    keep = [i for i in range(len(C)) if i not in set(remove)]
    C = np.array(C, float)[keep]; R = np.array(R, float)[keep]
    n0 = len(C)
    f = (1 + expand) * (((n0 + add) / n0) ** (1 / pb.d) if add else 1.0)
    C = C * f; L = L * f; ref = C.copy()
    newC, newR = [], []
    for _ in range(add):
        p = best_hole(pb, np.vstack([C] + ([np.array(newC)] if newC else [])), L, rng)
        newC.append(p); newR.append(random_rotation(rng, pb.d))
    if add: C = np.vstack([C, np.array(newC)]); R = np.concatenate([R, np.array(newR)])
    n = len(C)
    st = State(pb, C, R, L); st.seed = seed * 7919 + 17
    focus_set = None
    if focus and focus < n0:
        i0 = int(rng.integers(n0)); order = np.argsort(((ref - ref[i0]) ** 2).sum(1))
        focus_set = np.zeros(n, bool); focus_set[order[:focus]] = True; focus_set[n0:] = True
        st.mask = np.where(focus_set, 1.0, 0.15)
    structural = add > 0 or len(remove) > 0
    esc = 0; diff = 0.0
    while True:
        st.phase(shake, rh, rh, 0.0, 0.0, noise, noise, moveL=False, iters=iters)
        diff = arrangement_change(pb, ref, st.C[:n0], None if focus_set is None else focus_set[:n0])
        if structural or diff >= minDiff or esc >= maxEsc: break
        esc += 1; noise *= 1.5; rh = min(0.4, rh * 1.3)
    st.phase(morph, rh, 0.0, mu, mu, noise * 0.25, 0.0, iters=iters)
    st.phase(settle, 0.0, 0.0, mu, mu * 1e-4, 0.0, 0.0, mu_geom=True, iters=iters)
    st.mask[:] = 1.0
    out = legalize(pb, st.C, st.R, st=st)
    out.update(diff=diff, esc=esc)
    return out


def planes_lp(pb, C, R, pairs, U0=None, rounds=6, rho=0.5, delta=None, verbose=False, need=None):
    """Max-gap separating hyperplanes of many pairs at once, robustly: for each pair, maximize beta - alpha over u with
    u.x_v <= alpha (vertices of piece i), u.y_w >= beta (vertices of piece j), the linear normalization u.u0 = 1 and
    the box |u - u0| <= rho; all pairs in one block-diagonal LP (HiGHS), u0 <- u/|u|, repeated while any gap grows.
    Only vertices within `delta` of the supports along u0 enter the LP; every gap is then measured exactly (all
    vertices, normalized u). Returns (gaps, U, mid) like planes(); starts from the better of U0 and the tracked axes."""
    from scipy.optimize import linprog
    from scipy.sparse import csr_matrix
    C = np.ascontiguousarray(C, float); R = np.ascontiguousarray(R, float); d = pb.d
    if not len(pairs): return np.zeros(0), np.zeros((0, d)), np.zeros(0)
    g, U, _ = planes(pb, C, R, pairs, U0=U0)
    X = C[:, None, :] + np.einsum('vd,ned->nve', pb.V, R)
    if delta is None: delta = max(0.6, 2 * pb.edge)
    XA, XB = X[pairs[:, 0]], X[pairs[:, 1]]
    for rnd_ in range(rounds):
        if need is not None and g.min() >= need: break      # every pair already has the separation asked for
        P = len(pairs)
        pa = np.einsum('pvd,pd->pv', XA, U); pb_ = np.einsum('pvd,pd->pv', XB, U)
        selA = pa >= pa.max(1, keepdims=True) - delta; selB = pb_ <= pb_.min(1, keepdims=True) + delta
        rows, cols, vals, rhs = [], [], [], []
        r = 0
        nv = d + 2
        # u.x - alpha <= 0
        pp, vv = np.nonzero(selA); m1 = len(pp)
        rr = np.arange(m1)
        for a in range(d): rows.append(rr); cols.append(nv * pp + a); vals.append(XA[pp, vv, a])
        rows.append(rr); cols.append(nv * pp + d); vals.append(-np.ones(m1))
        pp2, ww = np.nonzero(selB); m2 = len(pp2)
        rr2 = m1 + np.arange(m2)
        for a in range(d): rows.append(rr2); cols.append(nv * pp2 + a); vals.append(-XB[pp2, ww, a])
        rows.append(rr2); cols.append(nv * pp2 + d + 1); vals.append(np.ones(m2))
        A_ub = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(m1 + m2, nv * P))
        # u.u0 = 1
        er = np.repeat(np.arange(P), d); ec = (nv * np.arange(P))[:, None] + np.arange(d)[None, :]
        A_eq = csr_matrix((U.ravel(), (er, ec.ravel())), shape=(P, nv * P))
        c = np.zeros(nv * P); c[nv * np.arange(P) + d] = 1.0; c[nv * np.arange(P) + d + 1] = -1.0
        lb = np.full((P, nv), -np.inf); ub = np.full((P, nv), np.inf)
        lb[:, :d] = U - rho; ub[:, :d] = U + rho
        res = linprog(c, A_ub=A_ub, b_ub=np.zeros(m1 + m2), A_eq=A_eq, b_eq=np.ones(P),
                      bounds=np.stack([lb.ravel(), ub.ravel()], 1), method='highs')
        if res.status != 0:
            if verbose: print('planes_lp: LP status', res.status, res.message)
            break
        Un = res.x.reshape(P, nv)[:, :d]; Un /= np.linalg.norm(Un, axis=1, keepdims=True)
        gn = np.einsum('pvd,pd->pv', XB, Un).min(1) - np.einsum('pvd,pd->pv', XA, Un).max(1)
        better = gn > g + 1e-15
        if verbose: print(f'planes_lp round {rnd_}: {better.sum()} of {P} improved, min gap {min(g.min(), gn.min()):.3e} -> {np.where(better, gn, g).min():.3e}')
        if not better.any(): break
        U[better] = Un[better]; g[better] = gn[better]
        # the tracker polishes kinks the LP's box left
        g2, U2, _ = planes(pb, C, R, pairs, U0=U, iters=50)
        b2 = g2 > g; U[b2] = U2[b2]; g[b2] = g2[b2]
    a = np.einsum('pvd,pd->pv', XA, U).max(1); b = np.einsum('pvd,pd->pv', XB, U).min(1)
    return b - a, U, (a + b) / 2
