"""Search crystal cuts (rotation x offset) for a problem: s_cut(n) for n = 2..NMAX (14 Oct 2026, large-n research).

    python3 scripts/crystal_cut.py PROBLEM [NMAX] [ROTATIONS] [--insert]

For every dense crystal of the piece (scripts/crystal.py), rotations R are sampled as (a) random rotations and
(b) 'aligned' rotations that put a dense lattice plane (short reciprocal vector) parallel to a container face, spun
about that face normal; for each R the fractional offset o runs over a 5^3 grid. For each n the best (R, o) is then
refined by a local random search. A cut is legal by construction (crystal + every piece inside the container); the
packing is re-legalized and measured by exact.certify before it is reported or inserted."""
import itertools, json, math, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import engine, exact, crystal


def rot_axis(u, a):
    u = u / np.linalg.norm(u); K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def align(a, b):
    """A rotation taking unit vector a to unit vector b."""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    if np.linalg.norm(v) < 1e-12: return np.eye(3) if c > 0 else rot_axis(np.cross(a, [1, 0, 0]) if abs(a[0]) < .9 else np.cross(a, [0, 1, 0]), math.pi)
    return rot_axis(v, math.atan2(np.linalg.norm(v), c))


class Cutter:
    def __init__(self, p, cry, nmax, smax):
        self.pb = pb = engine.problem(p); self.cry = cry; self.nmax = nmax
        self.B0 = np.array(cry['B']); self.motif0 = [(np.zeros(3), np.eye(3))]
        if cry.get('double'): self.motif0.append((np.array(cry['t']), np.array(cry['flip'])))
        self.den = pb.rhoC * pb.off
        Rc = smax * pb.rhoC * float(np.max(np.linalg.norm(self._cverts(), axis=1))) + pb.circ
        Binv = np.linalg.inv(self.B0)
        k = np.ceil(Rc * np.linalg.norm(Binv, axis=0)).astype(int) + 2
        I = np.array(list(itertools.product(*[range(-kk, kk + 1) for kk in k])), float)
        self.I = I[np.linalg.norm(I @ self.B0, axis=1) < Rc + np.linalg.norm(self.B0, axis=1).sum()]

    def _cverts(self):
        pb = self.pb   # container vertices at scale s = 1 (L = 2 rhoC): intersect the face planes
        from scipy.spatial import HalfspaceIntersection
        hs = np.hstack([pb.CN, -pb.rhoC * pb.off[:, None]])
        return HalfspaceIntersection(hs, np.zeros(3)).intersections / pb.rhoC

    def scales(self, R, O):
        """O: (m, 3) fractional offsets -> (m, k) sorted fitting scales of the k = nmax smallest pieces, and the
        piece indices (into the motif-stacked point list)."""
        pb = self.pb; B = self.B0 @ R.T; out = []
        for tm, Rm in self.motif0:
            Rw = R @ Rm
            hp = ((pb.V @ Rw.T) @ pb.CN.T).max(0)
            A = (self.I @ B + tm @ R.T) @ pb.CN.T + hp                      # P x F
            OB = (O @ B) @ pb.CN.T                                          # m x F
            out.append(((A[None, :, :] + OB[:, None, :]) / self.den).max(2))  # m x P
        S = np.concatenate(out, axis=1)
        k = min(self.nmax, S.shape[1])
        idx = np.argpartition(S, k - 1, axis=1)[:, :k]
        part = np.take_along_axis(S, idx, 1); o = np.argsort(part, axis=1)
        return np.take_along_axis(part, o, 1), np.take_along_axis(idx, o, 1)

    def packing(self, R, o, n):
        pb = self.pb; B = self.B0 @ R.T; C, Rs = [], []
        for tm, Rm in self.motif0:
            C.append((self.I + o) @ B + tm @ R.T); Rs += [R @ Rm] * len(self.I)
        S, idx = self.scales(R, o[None, :]); sel = idx[0, :n]
        C = np.concatenate(C)
        return C[sel], [Rs[i] for i in sel], float(S[0, n - 1])


def search(p, nmax=100, nrand=150, seed=0, verbose=False, crys=None, refine=60):
    pb = engine.problem(p); piece = engine.PID[p][0]
    rng = np.random.default_rng(seed)
    rec40 = engine.load_case(p, min(nmax, 40))['best']['s']
    smax = 1.6 * rec40 * (nmax / min(nmax, 40)) ** (1 / 3)
    crys = crys if crys is not None else crystal.crystals(exact.Problem(piece), piece)
    grid = np.array(list(itertools.product(np.arange(5) / 5, repeat=3)))
    best = {n: (np.inf, None) for n in range(2, nmax + 1)}           # n -> (s, (ci, R, o))
    t0 = time.time()
    # container face normals (distinct up to sign)
    CNu = crystal._unit_rows(pb.CN)
    for ci, cry in enumerate(crys):
        cut = Cutter(p, cry, nmax, smax)
        B = np.array(cry['B']); G = np.linalg.inv(B).T                  # reciprocal vectors (rows)
        Mz = np.array([m for m in itertools.product(range(-2, 3), repeat=3) if m > (0, 0, 0)])
        recip = Mz @ G; order = np.argsort(np.linalg.norm(recip, axis=1))
        rots = []
        for g in recip[order[:4]]:
            for f in CNu[:4]:
                A = align(g, f)
                for a in np.arange(0, math.pi, math.pi / 12): rots.append(rot_axis(f, a) @ A)
        rots += [crystal.rand_rot(rng) for _ in range(nrand)]
        for R in rots:
            S, _ = cut.scales(R, grid)
            k = S.shape[1]
            j = S.argmin(0)                                               # best offset per n
            for n in range(2, min(nmax, k) + 1):
                s = S[j[n - 1], n - 1]
                if s < best[n][0]: best[n] = (s, (ci, R, grid[j[n - 1]]))
        if verbose: print(f'  crystal {ci} ({"double" if cry["double"] else "lattice"} {cry["density"]:.4f}): {len(rots)} rotations, {time.time() - t0:.0f}s', flush=True)
    # local refinement of the best (R, o) per n
    cuts = {ci: Cutter(p, cry, nmax, smax) for ci, cry in enumerate(crys)}
    for n in range(2, nmax + 1):
        s0, arg = best[n]
        if arg is None: continue
        ci, R, o = arg; cut = cuts[ci]
        for it in range(refine):
            sc = 0.2 * (1 - it / refine) + 0.01
            R2 = rot_axis(rng.normal(size=3), rng.normal() * sc * 0.5) @ R
            o2 = (o + rng.normal(size=(8, 3)) * sc) % 1.0
            S, _ = cut.scales(R2, o2)
            if S.shape[1] < n: continue
            j = S[:, n - 1].argmin()
            if S[j, n - 1] < s0: s0, R, o = S[j, n - 1], R2, o2[j]
        best[n] = (s0, (ci, R, o))
    return best, cuts


def certify_cut(p, cuts, arg, n):
    pb = engine.problem(p); ci, R, o = arg
    C, Rs, s_est = cuts[ci].packing(R, o, n)
    L, k, C0 = exact.certify(pb, C, Rs)
    Q = [list(map(float, exact.R_to_quat(r))) for r in Rs]
    return pb.s_of_L(L), C0, Q, s_est


def insert(p, n, s, C0, Q, raw, info):
    with engine.locked():
        case = engine.load_case(p, n); cur = case['best']
        if cur is not None and s >= cur['s'] - 1e-9: return False
        case['best'] = {'s': s, 'C': np.asarray(C0).tolist(), 'Q': Q, 'src': dict(info, move='latcut', raw=raw), 't': time.time(), 'tightened': False}
        st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time(); st['needs_tighten'] = True; st['fails'] = {}
        engine.save_case(case)
        engine.pool_insert(p, n, {'s': s, 'C': case['best']['C'], 'Q': Q, 'src': 'latcut', 't': time.time()})
        engine.enforce_monotone(p, lambda m: None)
        with open(os.path.join(engine.STATE, 'attempts.jsonl'), 'a') as f:
            f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': 'latcut', 'raw': raw, 's': s,
                                'best_before': cur['s'] if cur else None, 'improved': True, 'secs': 0, 'raw_secs': 0}) + '\n')
    return True


if __name__ == '__main__':
    p = sys.argv[1]; nmax = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 40
    nrand = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 150
    t0 = time.time()
    best, cuts = search(p, nmax, nrand, verbose=True)
    res = {}
    for n in range(2, nmax + 1):
        s_est, arg = best[n]
        cb = engine.load_case(p, n)['best'] if n <= engine.NMAX else None
        rec = cb['s'] if cb else (float('inf') if n <= engine.NMAX else None)
        line = f'{p} n={n} cut {s_est:.6f}' + (f' record {rec:.6f}' if rec is not None else '')
        if rec is not None and np.isfinite(s_est) and s_est < rec - 1e-9:
            s, C0, Q, _ = certify_cut(p, cuts, arg, n)
            line += f' certified {s:.10f}' + (' BETTER' if s < rec - 1e-9 else '')
            if '--insert' in sys.argv and s < rec - 1e-9:
                insert(p, n, s, C0, Q, s_est, {'crystal': arg[0]})
        res[n] = s_est
        print(line, flush=True)
    print(f'done {time.time() - t0:.0f}s')
