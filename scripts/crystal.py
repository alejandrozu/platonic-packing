"""Periodic packings ("crystals") of a piece and their cuts to a container (14 Oct 2026, large-n research).

For large n the cheapest good packings are pieces of a dense crystal cut to the container. This module
  * finds dense lattice packings (one orientation, K + Lambda) and double-lattice packings (K + Lambda together with
    the point reflection -K + t + Lambda, for pieces that are not centrally symmetric) by direct optimisation;
  * cuts a crystal (any rotation R and offset t) to a container: for each n, the smallest container scale s holding n
    complete pieces, and the packing itself.

Lattice admissibility. Two translates K and K + v overlap (interiors) iff v is inside the difference body D = K - K.
For a polytope the facet normals of D are among the separating-axis candidates of two translates: the face normals
of K and the cross products of pairs of edge directions. With w(u) = width of K along u,
    K, K + v do not overlap  <=>  max_u |u.v| / w(u) >= 1   (the gauge of D).
For the reflected copy: K and -K + y do not overlap iff y is not inside K + K = 2K, i.e. max_f (N_f.y) / (2 h_f) >= 1
with K = {x : N_f.x <= h_f}.  Density = (number of pieces per cell) * vol(K) / |det B|.

The optimiser (SLSQP from many random starts, constraints for all integer vectors m in [-2, 2]^3) is a numerical
search; every result is re-verified for |m_i| <= 4 and the cut packings are certified separately (exact.certify)."""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

CACHE = os.path.join(ROOT, 'state', 'crystals')


def _unit_rows(A):
    A = np.asarray(A, float); n = np.linalg.norm(A, axis=1); A = A[n > 1e-12] / n[n > 1e-12, None]
    out = []
    for a in A:
        if a[np.argmax(np.abs(a) > 1e-9)] < 0: a = -a
        if not any(np.abs(a - b).max() < 1e-9 for b in out): out.append(a)
    return np.array(out)


def axes_widths(pb):
    """Candidate facet normals of the difference body K - K and the widths of K along them."""
    E = pb.edirs
    cr = [np.cross(E[i], E[j]) for i in range(len(E)) for j in range(i + 1, len(E))]
    U = _unit_rows(np.vstack([pb.faxes] + ([np.array(cr)] if cr else [])))
    p = pb.V @ U.T
    w = p.max(0) - p.min(0)
    return U, w


def face_planes(pb):
    """K = {x : N_f . x <= h_f} (local frame), from the vertices' convex hull."""
    hull = ConvexHull(pb.V)
    N, h = [], []
    for eq in hull.equations:
        nrm = eq[:3]; off = -eq[3]
        if not any(np.abs(nrm - a).max() < 1e-9 for a in N): N.append(nrm); h.append(off)
    return np.array(N), np.array(h)


MSET = np.array([m for m in itertools.product(range(-2, 3), repeat=3) if m > (0, 0, 0)])        # one of +-m
MSET4 = np.array([m for m in itertools.product(range(-4, 5), repeat=3) if m > (0, 0, 0)])


def lattice_ok(B, U, w, M=MSET4, tol=1e-9):
    V = M @ B                                                                        # rows: lattice vectors
    g = (np.abs(V @ U.T) / w).max(1)
    return g.min() >= 1 - tol, float(g.min())


def double_ok(B, t, U, w, N, h, M=MSET4, tol=1e-9):
    ok1, g1 = lattice_ok(B, U, w, M, tol)
    Mz = np.array(list(itertools.product(range(-4, 5), repeat=3)))
    Y = t + Mz @ B
    g2 = ((Y @ N.T) / (2 * h)).max(1).min()
    return ok1 and g2 >= 1 - tol, min(g1, float(g2))


def lll(B, delta=0.75):
    """LLL reduction of the rows of a 3x3 basis."""
    B = np.array(B, float); n = len(B)
    def gs(B):
        Bs = np.zeros_like(B); mu = np.zeros((n, n))
        for i in range(n):
            Bs[i] = B[i]
            for j in range(i):
                mu[i, j] = B[i] @ Bs[j] / (Bs[j] @ Bs[j]); Bs[i] = Bs[i] - mu[i, j] * Bs[j]
        return Bs, mu
    k = 1; it = 0
    while k < n and it < 1000:
        it += 1
        Bs, mu = gs(B)
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q: B[k] = B[k] - q * B[j]; Bs, mu = gs(B)
        if Bs[k] @ Bs[k] >= (delta - mu[k, k - 1] ** 2) * (Bs[k - 1] @ Bs[k - 1]): k += 1
        else: B[[k, k - 1]] = B[[k - 1, k]]; k = max(k - 1, 1)
    return B


def densest_lattice(pb, starts=60, seed=0, double=False, verbose=False):
    """Best lattice (or double lattice) found from random starts. Returns dict(B, t, density, double)."""
    rng = np.random.default_rng(seed)
    U, w = axes_widths(pb); vol = ConvexHull(pb.V).volume
    N, h = face_planes(pb)
    Mz = np.array(list(itertools.product(range(-2, 3), repeat=3)))
    best = None
    for st in range(starts):
        # random start: a random basis scaled up until admissible (and the reflected copy far enough)
        B0 = rng.normal(size=(3, 3))
        while abs(np.linalg.det(B0)) < 0.3 * np.prod(np.linalg.norm(B0, axis=1)): B0 = rng.normal(size=(3, 3))
        g = (np.abs((MSET @ B0) @ U.T) / w).max(1).min(); B0 = B0 / g * 1.05
        x0 = B0.ravel()
        if double:
            t0 = (B0[0] + B0[1] + B0[2]) / 2 * rng.uniform(0.6, 1.0)
            B0 = B0 * 2.2; x0 = np.concatenate([B0.ravel(), t0 * 2.2])

        def unpack(x): return x[:9].reshape(3, 3), (x[9:12] if double else None)

        def obj(x): return abs(np.linalg.det(unpack(x)[0]))

        def con(x):
            B, t = unpack(x)
            c = (np.abs((MSET @ B) @ U.T) / w).max(1) - 1
            if double: c = np.concatenate([c, ((t + Mz @ B) @ N.T / (2 * h)).max(1) - 1])
            return c
        ok = False
        for rnd in range(4):                      # optimise, LLL-reduce (so |m| <= 2 sees the short vectors), repeat
            try:
                r = minimize(obj, x0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': con}],
                             options={'maxiter': 400, 'ftol': 1e-12})
            except Exception:
                break
            B, t = unpack(r.x)
            if abs(np.linalg.det(B)) < 1e-9: break
            B = lll(B)
            if double: t = t - np.round(t @ np.linalg.inv(B)) @ B
            for fac in (1.0, 1 + 1e-9, 1 + 1e-7, 1 + 1e-5):
                Bf = B * fac; tf = t * fac if double else None
                ok = double_ok(Bf, tf, U, w, N, h)[0] if double else lattice_ok(Bf, U, w)[0]
                if ok: break
            if ok: break
            x0 = np.concatenate([B.ravel()] + ([t] if double else []))
        if not ok: continue
        dens = (2 if double else 1) * vol / abs(np.linalg.det(Bf))
        if best is None or dens > best['density'] + 1e-12:
            best = {'B': Bf.tolist(), 't': tf.tolist() if double else None, 'density': float(dens), 'double': double}
            if verbose: print(f'  start {st}: density {dens:.6f}', flush=True)
    return best


def improper_symmetry(pb, tol=1e-7):
    """An improper symmetry sigma of the piece (sigma K = K, det = -1): -I if centrally symmetric, else a mirror
    reflection I - 2uu^T found among planes normal to vertex differences, face normals and edge directions.
    None if the piece is chiral (then its point reflection is a different, mirror-image solid)."""
    V = pb.V
    def maps(S):
        W = V @ S.T
        d = np.abs(W[:, None, :] - V[None, :, :]).max(2).min(1)
        return d.max() < tol
    if maps(-np.eye(3)): return -np.eye(3)
    cands = [pb.faxes, pb.edirs / np.linalg.norm(pb.edirs, axis=1, keepdims=True)]
    D = (V[:, None, :] - V[None, :, :]).reshape(-1, 3); D = D[np.linalg.norm(D, axis=1) > 1e-9]
    cands.append(D / np.linalg.norm(D, axis=1, keepdims=True))
    for u in _unit_rows(np.vstack(cands)):
        S = np.eye(3) - 2 * np.outer(u, u)
        if maps(S): return S
    return None


def crystals(pb, name, starts=60, recompute=False):
    """Cached dense lattice (and, for pieces without central symmetry, double-lattice) packings of a piece."""
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f'{name}.json')
    if os.path.exists(fn) and not recompute: return json.load(open(fn))
    out = []
    lat = densest_lattice(pb, starts=starts)
    if lat: out.append(lat)
    sig = improper_symmetry(pb)
    cs = sig is not None and np.allclose(sig, -np.eye(3))
    if sig is not None and not cs:                    # achiral, not centrally symmetric: -K is the rotated copy R(-sigma)K
        dl = densest_lattice(pb, starts=starts, double=True)
        if dl: dl['flip'] = (-sig).tolist(); out.append(dl)
    json.dump(out, open(fn, 'w'), indent=1)
    return out


# ------------------------------------------------------------------ cutting a crystal to a container
def rand_rot(rng):
    q = rng.normal(size=4); q /= np.linalg.norm(q); w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def cut_curve(pb, cry, R, offsets, nmax, smax):
    """For crystal `cry` rotated by R: for each offset (fractional, 3-vector) the sorted fitting scales s_i of its
    pieces. Returns best[n] (n = 1..nmax) and the argmin offset per n."""
    B = np.array(cry['B']) @ R.T                      # rotated lattice vectors (rows)
    motif = [(np.zeros(3), R)]
    if cry.get('double'): motif.append((np.array(cry['t']) @ R.T, R @ np.array(cry['flip'])))   # -RK = R(-sigma)K
    CN = pb.CN; den = pb.rhoC * pb.off
    reach = smax * pb.rhoC * np.abs(np.asarray(pb.off)).max() * 2 + 2 * pb.circ
    Binv = np.linalg.inv(B)
    # integer box covering the container ball of radius `reach`
    k = np.ceil(reach * np.linalg.norm(Binv, axis=0)).astype(int) + 1
    I = np.array(list(itertools.product(*[range(-kk, kk + 1) for kk in k])))
    best = np.full(nmax + 1, np.inf); arg = [None] * (nmax + 1)
    hP = [((pb.V @ Rm.T) @ CN.T).max(0) for _, Rm in motif]
    for o in offsets:
        ss = []
        for (tm, Rm), hp in zip(motif, hP):
            pts = (I + o) @ B + tm
            si = ((pts @ CN.T + hp[None, :]) / den[None, :]).max(1)
            ss.append(si)
        si = np.sort(np.concatenate(ss))[:nmax]
        m = len(si)
        upd = si < best[1:m + 1]
        best[1:m + 1] = np.where(upd, si, best[1:m + 1])
        for n in np.nonzero(upd)[0] + 1: arg[n] = o
    return best, arg


def cut_packing(pb, cry, R, o, n):
    """The n pieces of crystal `cry` (rotation R, fractional offset o) that fit the smallest container."""
    B = np.array(cry['B']) @ R.T
    motif = [(np.zeros(3), R)]
    if cry.get('double'): motif.append((np.array(cry['t']) @ R.T, R @ np.array(cry['flip'])))
    CN = pb.CN; den = pb.rhoC * pb.off
    k = int(np.ceil(4 * n ** (1 / 3) + 6))
    I = np.array(list(itertools.product(range(-k, k + 1), repeat=3)))
    C, Rs, S = [], [], []
    for tm, Rm in motif:
        pts = (I + o) @ B + tm
        hp = ((pb.V @ Rm.T) @ CN.T).max(0)
        si = ((pts @ CN.T + hp[None, :]) / den[None, :]).max(1)
        C.append(pts); S.append(si); Rs += [Rm] * len(pts)
    C = np.concatenate(C); S = np.concatenate(S); sel = np.argsort(S)[:n]
    return C[sel], [Rs[i] for i in sel], float(S[sel].max())
