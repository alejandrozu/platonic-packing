"""Symmetrize a Platonic record at fixed container size (14 Nov 2026, Alejandro Zarzuelo's idea).

The container is held fixed at the record's s_full. Pieces are moved one at a time, the outermost first, onto
symmetric placements of the container: a piece is put on the fixed set of a subgroup K of the container's symmetry
group (a vertex, edge or face axis, or a mirror plane), oriented so that K maps the piece onto itself. A move is
kept only if the whole packing stays legal with the record's clearances (pair gap and wall gap >= 1e-7), so the
container never grows. On an axis the piece is pushed as deep as it goes first (nested in the corner, against the
edge or the face), then as close as possible to where it was.

For a subgroup K and a piece (c, R) whose orientation is close to K-symmetric, phi(h) in the piece's group is the
symmetry with R^-1 h R ~ phi(h). The K-symmetric placement nearest to it is the group average
    c* = mean_h h c,    R* = polar(mean_h h R phi(h)^T),
which satisfies h c* = c* and h R* = R* phi(h) exactly whenever phi is a homomorphism (both are averages over K).

Symmetry is measured by the stabilizer of each piece (the container symmetries that map the piece onto itself) and
by the symmetry group of the whole packing (container symmetries that permute the pieces).

Usage: python3 scripts/symmetrize.py RECORD.json [OUT.json]            # one record
       python3 scripts/symmetrize.py --all OUTDIR [problem ...]        # every Platonic record (n = 2..100)
       python3 scripts/symmetrize.py --families OUTDIR [problem ...]   # every prism, Archimedean and Catalan record
"""
import json, os, sys, math, itertools, time, glob
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from exact import Problem, quat_to_R, R_to_quat, sat_gap, SOL
from symmetry import sym_group

GAP = WALL = 1e-7          # the records' clearances; a move must keep both
MARGIN = 2e-9              # numerical margin on top (the exact certifier decides in the end)
MOVE = 0.35                # largest centre move (unit edge) for one piece
ANGLE = math.radians(25)   # largest rotation for one piece
TOL_C, TOL_R = 1e-6, 1e-6  # symmetry detection tolerances (exact symmetric placements)
PLATONIC = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico'}


def polar(M):
    U, _, Vt = np.linalg.svd(M)
    R = U @ Vt
    if np.linalg.det(R) < 0: U[:, -1] *= -1; R = U @ Vt
    return R


def key(M): return tuple(np.round(np.asarray(M), 6).ravel())


class Geo:
    def __init__(self, piece, container):
        self.piece, self.container = piece, container
        self.Vp = np.array(SOL[piece]['V'], float)
        self.CN = np.array(SOL[container]['normals'], float)
        self.CN /= np.linalg.norm(self.CN, axis=1)[:, None]
        CV = np.array(SOL[container]['V'], float)
        self.beta = np.array([self.CN[f] @ CV[F[0]] for f, F in enumerate(SOL[container]['faces'])])
        pbi = Problem(piece, container)
        Vp = self.Vp

        class U:   # unit-edge copy of the problem; Gauss-map pruning of edge axes for solids with many edge directions
            V = Vp; faxes = pbi.faxes; edirs = pbi.edirs; prune = pbi.prune; FNl = pbi.FNl; eface = pbi.eface
            @staticmethod
            def verts(c, Rm): return c + Vp @ Rm.T
        self.U = U
        self.lim = (2 * float(np.linalg.norm(Vp, axis=1).max())) ** 2 + 1e-9
        self.G = [np.array(g, float) for g in sym_group(container)]
        self.P = [np.array(p, float) for p in sym_group(piece)]
        self.Gk = {key(g): i for i, g in enumerate(self.G)}
        self.subgroups = self._subgroups(CV, SOL[container])

    # -- geometry
    def wall(self, c, R, s):
        X = c + self.Vp @ R.T
        return float((s * self.beta - (X @ self.CN.T).max(0)).min())

    def gap(self, ci, Ri, cj, Rj):
        if np.sum((ci - cj) ** 2) > self.lim: return math.inf
        return sat_gap(self.U, ci, Ri, cj, Rj)[0]

    def legal_piece(self, i, c, R, C, Rs, s):
        if self.wall(c, R, s) < WALL + MARGIN: return False
        for j in range(len(C)):
            if j != i and self.gap(c, R, C[j], Rs[j]) < GAP + MARGIN: return False
        return True

    # -- symmetry
    def _closure(self, gens):
        S = {key(np.eye(3)): np.eye(3)}
        frontier = list(S.values())
        while frontier:
            new = []
            for a in frontier:
                for g in gens:
                    m = g @ a; k = key(m)
                    if k not in S: S[k] = m; new.append(m)
            frontier = new
        return list(S.values())

    def _subgroups(self, CV, sol):
        """site stabilizers (vertices, edge midpoints, face centres), their rotation parts and single mirrors,
        cyclic groups of each element: as lists of matrices, largest first, with their fixed subspace"""
        pts = [v for v in CV]
        pts += [(CV[a] + CV[b]) / 2 for a, b in sol['edges']]
        pts += [CV[F].mean(0) for F in sol['faces']]
        groups = {}

        def add(H):
            k = frozenset(key(h) for h in H)
            if len(H) > 1 and k not in groups: groups[k] = H
        for x in pts:
            st = [g for g in self.G if np.linalg.norm(g @ x - x) < 1e-9]
            add(st)
            add([g for g in st if np.linalg.det(g) > 0])
            for g in st:
                if np.linalg.det(g) < 0 and abs(np.trace(g) - 1) < 1e-9:      # a mirror through the site
                    add([np.eye(3), g])
        for g in self.G:
            add(self._closure([g]))
        out = []
        for H in groups.values():
            Pi = sum(H) / len(H)
            w, v = np.linalg.eigh((Pi + Pi.T) / 2)
            B = v[:, w > 0.5]                     # basis of the fixed subspace
            out.append((H, Pi, B))
        out.sort(key=lambda t: -len(t[0]))
        return out

    def stabilizer(self, c, R):
        n = 0
        for g in self.G:
            if np.linalg.norm(g @ c - c) > TOL_C: continue
            M = R.T @ g @ R
            if min(np.linalg.norm(M - p) for p in self.P) < TOL_R: n += 1
        return n

    def packing_group(self, C, Rs, tc=TOL_C, tr=TOL_R):
        """order of the group of container symmetries that permute the pieces"""
        n = 0
        for g in self.G:
            gc = C @ g.T; ok = True
            for i in range(len(C)):
                d = np.linalg.norm(C - gc[i], axis=1); j = int(d.argmin())
                if d[j] > tc: ok = False; break
                M = Rs[j].T @ g @ Rs[i]
                if min(np.linalg.norm(M - p) for p in self.P) > tr: ok = False; break
            n += ok
        return n

    def target(self, c, R, H, Pi):
        """the K-symmetric placement nearest to (c, R), or None if the orientation is not close to K-symmetric"""
        phi = []
        for h in H:
            M = R.T @ h @ R
            d = [np.linalg.norm(M - p) for p in self.P]
            k = int(np.argmin(d))
            if d[k] > 2 * math.sqrt(2) * math.sin(ANGLE / 2): return None
            phi.append(self.P[k])
        idx = {key(h): a for a, h in enumerate(H)}
        for a, b in itertools.product(range(len(H)), repeat=2):      # phi must be a homomorphism
            ab = idx.get(key(H[a] @ H[b]))
            if ab is None or np.linalg.norm(phi[a] @ phi[b] - phi[ab]) > 1e-6: return None
        Rs = polar(sum(h @ R @ p.T for h, p in zip(H, phi)) / len(H))
        if any(np.linalg.norm(h @ Rs - Rs @ p) > 1e-9 for h, p in zip(H, phi)): return None
        if math.acos(max(-1.0, min(1.0, (np.trace(R.T @ Rs) - 1) / 2))) > ANGLE: return None
        return Pi @ c, Rs

    def symmetrize_piece(self, i, C, Rs, s):
        """move piece i onto the most symmetric legal placement within MOVE / ANGLE; returns (c, R, |K|) or None"""
        c0, R0 = C[i], Rs[i]
        cur = self.stabilizer(c0, R0)
        for H, Pi, B in self.subgroups:
            if len(H) <= cur: break
            if np.linalg.norm(c0 - Pi @ c0) > MOVE: continue
            t = self.target(c0, R0, H, Pi)
            if t is None: continue
            cs, Rt = t
            for c in self.positions(cs, Rt, B, s, c0):
                if self.legal_piece(i, c, Rt, C, Rs, s):
                    return c, Rt, len(H)
        return None

    def positions(self, cs, Rt, B, s, c0):
        """candidate centres on the fixed set: deepest first on an axis, then nearest to the projection"""
        X = self.Vp @ Rt.T
        hf = (X @ self.CN.T).max(0)
        if B.shape[1] == 0:
            yield np.zeros(3); return
        if B.shape[1] == 1:
            u = B[:, 0]; t0 = float(cs @ u)
            a = self.CN @ u; rhs = s * self.beta - WALL - MARGIN * 2 - hf
            hi = min([r / x for r, x in zip(rhs, a) if x > 1e-12] or [math.inf])
            lo = max([r / x for r, x in zip(rhs, a) if x < -1e-12] or [-math.inf])
            cand = []
            for t in [hi, lo]:
                if abs(t - t0) <= MOVE and math.isfinite(t): cand.append(t)
            grid = sorted(np.linspace(t0 - MOVE, t0 + MOVE, 57), key=lambda t: abs(t - t0))
            cand += [t for t in grid if lo <= t <= hi]
            for t in cand: yield t * u
            return
        if B.shape[1] == 2:
            yield cs
            for r in (0.002, 0.005, 0.01, 0.02, 0.04, 0.08, 0.15):
                for k in range(8):
                    a = 2 * math.pi * k / 8
                    yield cs + r * (math.cos(a) * B[:, 0] + math.sin(a) * B[:, 1])


def load(fn):
    r = json.load(open(fn))
    P = np.array(r['pieces'], float)
    C = P[:, :3].copy()
    Rs = [quat_to_R(q / np.linalg.norm(q)) for q in P[:, 3:]]
    return r, C, Rs


def measure(geo, C, Rs):
    st = [geo.stabilizer(C[i], Rs[i]) for i in range(len(C))]
    return {'packing_group': geo.packing_group(C, Rs), 'symmetric_pieces': sum(x > 1 for x in st),
            'stabilizer_sum': int(sum(st) - len(st)), 'stabilizers': sorted(st, reverse=True)}


def run(fn, passes=3):
    r, C, Rs = load(fn)
    geo = Geo(r['piece'], r['container']); s = float(r['s_full'])
    before = measure(geo, C, Rs)
    outer = np.argsort(-((C @ geo.CN.T) / geo.beta).max(1))
    moved = {}
    for _ in range(passes):
        changed = False
        for i in outer:
            res = geo.symmetrize_piece(int(i), C, Rs, s)
            if res:
                C[i], Rs[i] = res[0], res[1]; moved[int(i)] = res[2]; changed = True
        if not changed: break
    after = measure(geo, C, Rs)
    return r, geo, C, Rs, before, after, moved


def write(r, geo, C, Rs, before, after, out, src_file):
    s = float(r['s_full'])
    q = []
    for R in Rs:
        x = np.asarray(R_to_quat(R), float); x /= np.linalg.norm(x)
        q.append(x if x[0] >= 0 else -x)
    walls = [geo.wall(C[i], Rs[i], s) for i in range(len(C))]
    gaps = [geo.gap(C[i], Rs[i], C[j], Rs[j]) for i, j in itertools.combinations(range(len(C)), 2)]
    rec = dict(r)
    rec['pieces'] = [[*map(float, C[i]), *map(float, q[i])] for i in range(len(C))]
    rec['clearance'] = dict(r['clearance'], min_pair_gap=float(min(gaps)) if gaps else None, min_wall_gap=float(min(walls)))
    rec['symmetrized'] = {'from': src_file, 'from_source_hash': r.get('source', {}).get('hash'), 'container': 'unchanged (same s_full)',
                          'before': before, 'after': after,
                          'method': 'scripts/symmetrize.py: pieces moved one at a time onto symmetric placements of the container, '
                                    'each move kept only if the packing stays legal with the same clearances'}
    for k in ('certificate', 'closed_form_source', 'closed_form_confirmation'): rec.pop(k, None)
    json.dump(rec, open(out, 'w'), indent=1)


def summary():
    """records/symmetric/SUMMARY.csv and README.md from the symmetrized records and their checker outputs"""
    import csv
    base = os.path.join(ROOT, 'records', 'symmetric'); rows = []
    for fn in sorted(glob.glob(os.path.join(base, '*', '*_n[0-9]*.json'))):
        r = json.load(open(fn)); sm = r['symmetrized']; b, a = sm['before'], sm['after']
        orig = json.load(open(os.path.join(ROOT, sm['from'])))
        def ok(ext, word):
            try: x = open(fn.replace('.json', ext)).read()
            except FileNotFoundError: return False
            return (('\n' + word) in ('\n' + x)) and ('NOT ' + word) not in x and ('IN' + word) not in x
        rows.append(dict(record_id=r['record_id'], problem=os.path.basename(os.path.dirname(fn)), n=r['n'], s_full=r['s_full'],
                         s_full_record=orig['s_full'], symmetric_pieces_before=b['symmetric_pieces'], symmetric_pieces_after=a['symmetric_pieces'],
                         packing_group_before=b['packing_group'], packing_group_after=a['packing_group'],
                         verified=ok('.verify.txt', 'VALID'), certified=ok('.certify.txt', 'CERTIFIED'),
                         file=os.path.relpath(fn, base)))
    if not rows: return
    with open(os.path.join(base, 'SUMMARY.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); [w.writerow(x) for x in rows]
    by = {}
    for x in rows: by.setdefault(x['problem'], []).append(x)
    lines = ['# Symmetrized packings', '',
             'The same packings as the records, in **the same container** (identical `s_full`), with pieces moved onto symmetric',
             'placements of the container: nested in a corner, centred on a face or an edge, or on a mirror plane. A placement',
             'counts as symmetric when some symmetry of the container, other than the identity, maps the piece onto itself.',
             '`packing group` = the number of container symmetries that map the whole packing onto itself. Made by',
             '[`scripts/symmetrize.py`](../../scripts/symmetrize.py), checked by `verify.py` and `certify_exact.py` like the records.',
             'See [docs/SYMMETRY.md](../../docs/SYMMETRY.md).', '',
             f"{len(rows)} packings; {sum(x['certified'] for x in rows)} certified exactly; "
             f"{sum(x['symmetric_pieces_after'] - x['symmetric_pieces_before'] for x in rows)} more pieces on symmetric placements; "
             f"{sum(x['packing_group_after'] > x['packing_group_before'] for x in rows)} with a larger packing group.", '',
             '| problem | packings | symmetric pieces (before → after) | larger packing group |', '|---|---|---|---|']
    for p, xs in sorted(by.items(), key=lambda kv: -sum(x['symmetric_pieces_after'] - x['symmetric_pieces_before'] for x in kv[1])):
        lines.append(f"| {p} | {len(xs)} | {sum(x['symmetric_pieces_before'] for x in xs)} → {sum(x['symmetric_pieces_after'] for x in xs)} | "
                     f"{', '.join(str(x['n']) + ' (' + str(x['packing_group_before']) + ' → ' + str(x['packing_group_after']) + ')' for x in xs if x['packing_group_after'] > x['packing_group_before']) or '–'} |")
    lines += ['', '| record | s_full (unchanged) | symmetric pieces | packing group | certified |', '|---|---|---|---|---|']
    for x in rows:
        lines.append(f"| [{x['record_id']}]({x['file']}) | {x['s_full']} | {x['symmetric_pieces_before']} → {x['symmetric_pieces_after']} of {x['n']} | "
                     f"{x['packing_group_before']} → {x['packing_group_after']} | {'yes' if x['certified'] and x['verified'] else '**no**'} |")
    open(os.path.join(base, 'README.md'), 'w').write('\n'.join(lines) + '\n')
    print(len(rows), 'rows')


if __name__ == '__main__':
    if sys.argv[1] == '--summary':
        summary(); sys.exit()
    if sys.argv[1] in ('--all', '--families'):
        outdir = sys.argv[2]; probs = sys.argv[3:]
        if not probs:
            import engine
            probs = [p for p in engine.PID if (engine.FAM[p] == 'platonic') == (sys.argv[1] == '--all')]
        for p in probs:
            for fn in sorted(glob.glob(os.path.join(ROOT, 'records', p, f'{p}_n[0-9][0-9].json')) +
                             glob.glob(os.path.join(ROOT, 'records', p, f'{p}_n100.json'))):
                t0 = time.time()
                r, geo, C, Rs, b, a, moved = run(fn)
                os.makedirs(os.path.join(outdir, p), exist_ok=True)
                out = os.path.join(outdir, p, os.path.basename(fn))
                if moved: write(r, geo, C, Rs, b, a, out, os.path.relpath(fn, ROOT))
                print(json.dumps({'record': r['record_id'], 'n': r['n'], 'moved': len(moved), 'group': [b['packing_group'], a['packing_group']],
                                  'sym_pieces': [b['symmetric_pieces'], a['symmetric_pieces']], 'stab': [b['stabilizer_sum'], a['stabilizer_sum']],
                                  't': round(time.time() - t0, 1)}), flush=True)
    else:
        fn = sys.argv[1]
        r, geo, C, Rs, b, a, moved = run(fn)
        print('before', b); print('after ', a); print('moved', moved)
        if len(sys.argv) > 2 and moved: write(r, geo, C, Rs, b, a, sys.argv[2], os.path.relpath(fn, ROOT))


# ---------------------------------------------------------------------------------------------------------------
# Collective moves: pieces held on symmetric placements while all the others relax (container fixed at the origin).
# The tightening of src/exact.py (SLSQP with per-pair separating planes) with linear equality constraints: a held
# piece keeps its centre in the fixed subspace of its group K, (I - Pi_C) c = 0, and its rotation increment phi in
# the fixed subspace of the conjugation action, (I - Pi_O) phi = 0 with Pi_O = mean_h det(h) h, which keeps
# h R = R phi(h) exactly. Legalization spreads the centres about the origin (the container centre), so every
# symmetry of the container is preserved; there is no translation fit.
from exact import tangent_basis, rod, jac_left, pair_gaps
from scipy.optimize import minimize


def certify_origin(pb, C, R):
    C = np.array(C, float); n = len(C)
    lim = (2 * pb.circ) ** 2 + 1e-9
    near = np.array([(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((C[i] - C[j]) ** 2) <= lim * 1.3 ** 2], int).reshape(-1, 2)

    def ok(k):
        if not len(near): return True
        g = pair_gaps(pb, k * C, R, near)
        return bool((g >= -1e-12).all())
    k = 1.0
    if not ok(k):
        hi = 1.001
        while not ok(hi): hi = 1 + (hi - 1) * 2
        lo = 1.0
        for _ in range(50):
            m = (lo + hi) / 2
            if ok(m): hi = m
            else: lo = m
        k = hi
    P = k * C
    X = np.concatenate([pb.verts(P[i], R[i]) for i in range(n)])
    L = 2 * float(((X @ pb.CN.T).max(0) / pb.off).max())
    return L, P


def solve_sym(pb, C, R, L, held, outer=30, trust=0.03, tlimit=None):
    """held: {i: (PiC, PiO)}. Returns (L, C, R) with the held pieces exactly on their symmetric placements."""
    C = np.array(C, float); R = [np.array(r) for r in R]; n = len(C)
    t0 = time.time(); fails = 0
    eqA = []
    for i, (PiC, PiO) in held.items():
        for M, off in ((np.eye(3) - PiC, 3 * i), (np.eye(3) - PiO, 3 * n + 3 * i)):
            for row in M:
                if np.abs(row).max() > 1e-12: eqA.append((off, row))
    for it in range(outer):
        if tlimit and time.time() - t0 > tlimit: break
        lim = (2 * pb.circ + 4 * trust + 0.05) ** 2
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((C[i] - C[j]) ** 2) < lim]
        P = len(pairs)
        U0, E1, E2, c0, M0 = [], [], [], [], []
        for (i, j) in pairs:
            _, u, c = sat_gap(pb, C[i], R[i], C[j], R[j])
            e1, e2 = tangent_basis(u); m0 = (C[i] + C[j]) / 2
            U0.append(u); E1.append(e1); E2.append(e2); c0.append(c - u @ m0); M0.append(m0)
        U0, E1, E2, M0 = (np.array(A).reshape(P, 3) for A in (U0, E1, E2, M0)); c0 = np.array(c0)
        LG = np.stack([pb.V @ R[i].T for i in range(n)])
        Xc = C[:, None, :] + LG
        dmax = trust * (math.sqrt(3) + 3 * math.sqrt(3) * pb.circ)
        reach = dmax + 2 * trust + 1e-3
        slack = (L / 2) * pb.off[None, None, :] - Xc @ pb.CN.T
        ci, cv, cf = np.nonzero(slack < reach); nc = len(ci)
        cb = 2 * dmax + 1e-3
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
        iL = 6 * n; ia = iL + 1; ic = ia + 2 * P; nvar = ic + P
        z0 = np.concatenate([C.ravel(), np.zeros(3 * n), [L], np.zeros(2 * P), c0])

        def unpack(z):
            Cz = z[:3 * n].reshape(n, 3); Ph = z[3 * n:6 * n].reshape(n, 3)
            Rs = np.stack([rod(Ph[i]) for i in range(n)])
            return Cz, Ph, np.einsum('nab,nvb->nva', Rs, LG)

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
                g.append(rs * (np.einsum('kd,kd->k', X[ri, rv] - M0[rp], U[rp]) - c[rp]))
            return np.concatenate(g)

        def jac(z):
            Cz, Ph, Y = unpack(z); X = Cz[:, None, :] + Y
            JL = np.stack([jac_left(Ph[i]) for i in range(n)])
            J = np.zeros((nc + npr, nvar)); rows = np.arange(nc)
            for d in range(3): J[rows, 3 * ci + d] = -pb.CN[cf, d]
            Gphi = np.einsum('kd,kde->ke', np.cross(pb.CN[cf], Y[ci, cv]), JL[ci])
            for d in range(3): J[rows, 3 * n + 3 * ci + d] = Gphi[:, d]
            J[rows, iL] = pb.off[cf] / 2
            if npr:
                U, nr = planes(z); rows = nc + np.arange(npr)
                dUa = (E1 - U * np.sum(U * E1, 1, keepdims=True)) / nr
                dUb = (E2 - U * np.sum(U * E2, 1, keepdims=True)) / nr
                Ur = U[rp]; rel = X[ri, rv] - M0[rp]
                for d in range(3): J[rows, 3 * ri + d] = rs * Ur[:, d]
                Gp = np.einsum('kd,kde->ke', np.cross(Ur, Y[ri, rv]), JL[ri])
                for d in range(3): J[rows, 3 * n + 3 * ri + d] = -rs * Gp[:, d]
                J[rows, ia + 2 * rp] = rs * np.einsum('kd,kd->k', rel, dUa[rp])
                J[rows, ia + 2 * rp + 1] = rs * np.einsum('kd,kd->k', rel, dUb[rp])
                J[rows, ic + rp] = -rs
            return J
        A = np.zeros((len(eqA), nvar))
        for r_, (off, row) in enumerate(eqA): A[r_, off:off + 3] = row
        bounds = ([(v - trust, v + trust) for v in C.ravel()] + [(-3 * trust, 3 * trust)] * (3 * n) +
                  [(L - 2 * trust, L + 0.05)] + [(-3 * trust, 3 * trust)] * (2 * P) + [(c - cb, c + cb) for c in c0])
        cl = [{'type': 'ineq', 'fun': cons, 'jac': jac}]
        if len(eqA): cl.append({'type': 'eq', 'fun': lambda z: A @ z, 'jac': lambda z: A})
        res = minimize(lambda z: z[iL], z0, jac=lambda z: np.eye(nvar)[iL], method='SLSQP', bounds=bounds,
                       constraints=cl, options={'maxiter': 300, 'ftol': 1e-15})
        z = res.x
        Cn = z[:3 * n].reshape(n, 3).copy(); Ph = z[3 * n:6 * n].reshape(n, 3).copy()
        for i, (PiC, PiO) in held.items():               # exactly back on the symmetric placement
            Cn[i] = PiC @ Cn[i]; Ph[i] = PiO @ Ph[i]
        Rn = [rod(Ph[i]) @ R[i] for i in range(n)]
        Ln, Cc = certify_origin(pb, Cn, Rn)
        if Ln < L - 1e-13:
            imp = L - Ln; C, R, L = Cc, Rn, Ln; fails = 0
            if imp < 1e-12: break
        else:
            trust *= 0.5; fails += 1
            if trust < 1e-4 or fails >= 3: break
    return float(L), C, R


def legal_full(geo, C, Rs, s_cap):
    """spread about the origin until every pair gap is >= GAP; the smallest s_full (13th decimal, rounded up) with
    every wall gap >= WALL; None if it exceeds s_cap"""
    n = len(C)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((C[i] - C[j]) ** 2) <= geo.lim * 1.2]

    def mg(k): return min([geo.gap(k * C[i], Rs[i], k * C[j], Rs[j]) for i, j in pairs] or [math.inf])
    k = 1.0
    if mg(k) < GAP + MARGIN:
        lo, hi = 1.0, 1 + 1e-7
        while mg(hi) < GAP + MARGIN: hi = 1 + (hi - 1) * 2
        for _ in range(60):
            m = (lo + hi) / 2
            if mg(m) >= GAP + MARGIN: hi = m
            else: lo = m
        k = hi
    P = k * C
    X = np.concatenate([P[i] + geo.Vp @ Rs[i].T for i in range(n)])
    s = math.ceil(float((((X @ geo.CN.T).max(0) + WALL + MARGIN) / geo.beta).max()) * 1e13) / 1e13
    return (s, P) if s <= s_cap else (s, None)


def snap_plan(geo, C, Rs):
    """for each piece: its current group (kept) or the largest symmetric placement within MOVE / ANGLE"""
    plan = {}
    for i in range(len(C)):
        cur = geo.stabilizer(C[i], Rs[i]); best = None
        for H, Pi, B in geo.subgroups:
            if len(H) < cur or (best and len(H) < best[0]): break
            if np.linalg.norm(C[i] - Pi @ C[i]) > MOVE: continue
            t = geo.target(C[i], Rs[i], H, Pi)
            if t is None: continue
            PiO = sum(np.linalg.det(h) * h for h in H) / len(H)
            d = float(np.linalg.norm(C[i] - t[0])) + math.acos(max(-1.0, min(1.0, (np.trace(Rs[i].T @ t[1]) - 1) / 2)))
            if best is None or len(H) > best[0] or d < best[1]: best = (len(H), d, t[0], t[1], Pi, PiO)
        if best and best[0] > 1: plan[i] = best
    return plan


def collective(fn, tlimit=600, verbose=False):
    """hold as many pieces as possible on symmetric placements while the others relax; container <= s_full"""
    r, C, Rs = load(fn)
    geo = Geo(r['piece'], r['container']); s_rec = float(r['s_full'])
    pb = Problem(r['piece'], r['container']); e = pb.edge; rhoC = pb.rhoC
    before = measure(geo, C, Rs)
    plan = snap_plan(geo, C, Rs)
    cur = {i: geo.stabilizer(C[i], Rs[i]) for i in range(len(C))}
    keep = [i for i in plan if plan[i][0] == cur[i]]                    # already symmetric: stay so
    new = sorted([i for i in plan if plan[i][0] > cur[i]], key=lambda i: plan[i][1])
    best = None; t0 = time.time(); tried = []
    sets = []
    k = len(new)
    while k >= 1:
        sets.append(new[:k]); k = k // 2 if k > 1 else 0
    for S in sets:
        if time.time() - t0 > tlimit: break
        C1 = C.copy(); R1 = [x.copy() for x in Rs]; held = {}
        for i in keep + S:
            _, _, cs, Rt, Pi, PiO = plan[i]; C1[i] = cs; R1[i] = Rt; held[i] = (Pi, PiO)
        L0, Cc = certify_origin(pb, C1 * e, R1)
        L, Ci, Ri = solve_sym(pb, Cc, R1, L0, held, tlimit=max(30, tlimit - (time.time() - t0)))
        s_new, P = legal_full(geo, Ci / e, Ri, s_rec)
        tried.append((len(S), s_new))
        if verbose: print(f'  hold {len(keep)}+{len(S)}: s_tight {pb.s_of_L(L):.12f} s_full {s_new:.13f} vs {s_rec:.13f}', flush=True)
        if P is not None:
            best = (P, Ri, S); break
    if best is None:
        return r, geo, C, Rs, before, before, {}, tried
    P, Ri, S = best
    after = measure(geo, P, Ri)
    return r, geo, P, Ri, before, after, {i: plan[i][0] for i in S}, tried


# ---------------------------------------------------------------------------------------------------------------
# Pull towards symmetry at fixed size (Alejandro's formulation): the container is held at s_full, every constraint
# carries the record's clearances, and SLSQP minimizes the distance of the chosen pieces to their symmetric
# placements (all other pieces free). Every round is accepted only if the packing is still legal, so the
# container never grows; pieces that reach their placement are snapped exactly.
def log_rot(M):
    c = max(-1.0, min(1.0, (np.trace(M) - 1) / 2)); th = math.acos(c)
    if th < 1e-12: return np.zeros(3)
    w = np.array([M[2, 1] - M[1, 2], M[0, 2] - M[2, 0], M[1, 0] - M[0, 1]]) / (2 * math.sin(th))
    return th * w


def sym_project(geo, H, c, R):
    """exact K-symmetric projection of (c, R): (Pi c, polar(mean h R phi(h)^T)), or None"""
    t = geo.target(c, R, H, sum(H) / len(H))
    return t


def pull_sym(fn, rounds=60, trust=0.02, tlimit=900, verbose=False):
    r, C, Rs = load(fn)
    geo = Geo(r['piece'], r['container']); s = float(r['s_full'])
    pb = Problem(r['piece'], r['container']); e = pb.edge
    before = measure(geo, C, Rs)
    plan = snap_plan(geo, C, Rs)
    cur = {i: geo.stabilizer(C[i], Rs[i]) for i in range(len(C))}
    keep = [i for i in plan if plan[i][0] == cur[i]]
    targ = [i for i in plan if plan[i][0] > cur[i]]
    if not targ: return r, geo, C, Rs, before, before, {}
    groups = {}
    for i in plan:
        for H, Pi, B in geo.subgroups:
            if len(H) == plan[i][0] and np.allclose(Pi, plan[i][4]): groups[i] = H; break
    n = len(C); L = s * 2 * pb.rhoC
    gapI, wallI = GAP * e, WALL * e                       # SLSQP keeps the clearances; legal() accepts 0.99 of them
    w = pb.circ ** 2
    Cint = C * e; R = [x.copy() for x in Rs]
    t0 = time.time()

    def residual(Cint, R):
        out = {}
        for i in targ:
            Pi, PiO = plan[i][4], plan[i][5]
            pc = (np.eye(3) - Pi) @ Cint[i]
            t = geo.target(Cint[i] / e, R[i], groups[i], Pi)
            if t is None: out[i] = math.inf; continue
            d = log_rot(t[1] @ R[i].T)
            out[i] = float(pc @ pc + w * d @ d)
        return out

    def legal(Cint, R):
        Cu = Cint / e
        if min(geo.wall(Cu[i], R[i], s) for i in range(n)) < 0.99 * WALL: return False
        for i in range(n):
            for j in range(i + 1, n):
                if geo.gap(Cu[i], R[i], Cu[j], R[j]) < 0.99 * GAP: return False
        return True
    res0 = residual(Cint, R)
    best_tot = sum(v for v in res0.values() if math.isfinite(v))
    eqA = []
    for i in keep:
        Pi, PiO = plan[i][4], plan[i][5]
        for M, off in ((np.eye(3) - Pi, 3 * i), (np.eye(3) - PiO, 3 * n + 3 * i)):
            for row in M:
                if np.abs(row).max() > 1e-12: eqA.append((off, row))
    for it in range(rounds):
        if time.time() - t0 > tlimit: break
        lim = (2 * pb.circ + 4 * trust + 0.05) ** 2
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if np.sum((Cint[i] - Cint[j]) ** 2) < lim]
        P = len(pairs)
        U0, E1, E2, c0, M0 = [], [], [], [], []
        for (i, j) in pairs:
            _, u, c = sat_gap(pb, Cint[i], R[i], Cint[j], R[j])
            e1, e2 = tangent_basis(u); m0 = (Cint[i] + Cint[j]) / 2
            U0.append(u); E1.append(e1); E2.append(e2); c0.append(c - u @ m0); M0.append(m0)
        U0, E1, E2, M0 = (np.array(A).reshape(P, 3) for A in (U0, E1, E2, M0)); c0 = np.array(c0)
        LG = np.stack([pb.V @ R[i].T for i in range(n)]); Xc = Cint[:, None, :] + LG
        dmax = trust * (math.sqrt(3) + 3 * math.sqrt(3) * pb.circ); reach = dmax + 2 * trust + 1e-3
        slack = (L / 2) * pb.off[None, None, :] - Xc @ pb.CN.T
        ci, cv, cf = np.nonzero(slack < reach); nc = len(ci)
        cb = 2 * dmax + 1e-3
        rp, rs, rv, ri = [], [], [], []
        for p, (i, j) in enumerate(pairs):
            for sg, k in ((-1.0, i), (1.0, j)):
                rel = Xc[k] - M0[p]; sl = sg * (rel @ U0[p] - c0[p])
                marg = cb + 3 * math.sqrt(2) * trust * (np.linalg.norm(rel, axis=1) + dmax) + dmax + 1e-3
                for v in np.nonzero(sl < marg)[0]: rp.append(p); rs.append(sg); rv.append(v); ri.append(k)
        rp, rs, rv, ri = np.array(rp, int), np.array(rs), np.array(rv, int), np.array(ri, int); npr = len(rp)
        ia = 6 * n; ic = ia + 2 * P; nvar = ic + P
        z0 = np.concatenate([Cint.ravel(), np.zeros(3 * n), np.zeros(2 * P), c0])
        # symmetric targets of this round
        tg = {}
        for i in targ:
            t = geo.target(Cint[i] / e, R[i], groups[i], plan[i][4])
            if t is not None: tg[i] = (plan[i][4], plan[i][5], log_rot(t[1] @ R[i].T))

        def unpack(z):
            Cz = z[:3 * n].reshape(n, 3); Ph = z[3 * n:6 * n].reshape(n, 3)
            Rr = np.stack([rod(Ph[i]) for i in range(n)])
            return Cz, Ph, np.einsum('nab,nvb->nva', Rr, LG)

        def planes(z):
            ab = z[ia:ic].reshape(P, 2); Uraw = U0 + ab[:, :1] * E1 + ab[:, 1:] * E2
            nr = np.linalg.norm(Uraw, axis=1, keepdims=True); return Uraw / nr, nr

        def cons(z):
            Cz, Ph, Y = unpack(z); X = Cz[:, None, :] + Y
            g = [(L / 2) * pb.off[cf] - np.einsum('kd,kd->k', X[ci, cv], pb.CN[cf]) - wallI]
            if npr:
                U, _ = planes(z); c = z[ic:]
                g.append(rs * (np.einsum('kd,kd->k', X[ri, rv] - M0[rp], U[rp]) - c[rp]) - gapI / 2)
            return np.concatenate(g)

        def jac(z):
            Cz, Ph, Y = unpack(z); X = Cz[:, None, :] + Y
            JL = np.stack([jac_left(Ph[i]) for i in range(n)])
            J = np.zeros((nc + npr, nvar)); rows = np.arange(nc)
            for d in range(3): J[rows, 3 * ci + d] = -pb.CN[cf, d]
            Gphi = np.einsum('kd,kde->ke', np.cross(pb.CN[cf], Y[ci, cv]), JL[ci])
            for d in range(3): J[rows, 3 * n + 3 * ci + d] = Gphi[:, d]
            if npr:
                U, nr = planes(z); rows = nc + np.arange(npr)
                dUa = (E1 - U * np.sum(U * E1, 1, keepdims=True)) / nr
                dUb = (E2 - U * np.sum(U * E2, 1, keepdims=True)) / nr
                Ur = U[rp]; rel = X[ri, rv] - M0[rp]
                for d in range(3): J[rows, 3 * ri + d] = rs * Ur[:, d]
                Gp = np.einsum('kd,kde->ke', np.cross(Ur, Y[ri, rv]), JL[ri])
                for d in range(3): J[rows, 3 * n + 3 * ri + d] = -rs * Gp[:, d]
                J[rows, ia + 2 * rp] = rs * np.einsum('kd,kd->k', rel, dUa[rp])
                J[rows, ia + 2 * rp + 1] = rs * np.einsum('kd,kd->k', rel, dUb[rp])
                J[rows, ic + rp] = -rs
            return J

        def f(z):
            v = 0.0; g = np.zeros(nvar)
            for i, (Pi, PiO, D) in tg.items():
                a = (np.eye(3) - Pi) @ z[3 * i:3 * i + 3]; v += a @ a; g[3 * i:3 * i + 3] += 2 * (np.eye(3) - Pi).T @ a
                b = (np.eye(3) - PiO) @ (z[3 * n + 3 * i:3 * n + 3 * i + 3] - D); v += w * b @ b
                g[3 * n + 3 * i:3 * n + 3 * i + 3] += 2 * w * (np.eye(3) - PiO).T @ b
            return v, g
        A = np.zeros((len(eqA), nvar))
        for r_, (off, row) in enumerate(eqA): A[r_, off:off + 3] = row
        bounds = ([(v - trust, v + trust) for v in Cint.ravel()] + [(-3 * trust, 3 * trust)] * (3 * n) +
                  [(-3 * trust, 3 * trust)] * (2 * P) + [(c - cb, c + cb) for c in c0])
        cl = [{'type': 'ineq', 'fun': cons, 'jac': jac}]
        if len(eqA): cl.append({'type': 'eq', 'fun': lambda z: A @ z, 'jac': lambda z: A})
        rr = minimize(f, z0, jac=True, method='SLSQP', bounds=bounds, constraints=cl, options={'maxiter': 200, 'ftol': 1e-22})
        z = rr.x
        Cn = z[:3 * n].reshape(n, 3).copy(); Ph = z[3 * n:6 * n].reshape(n, 3).copy()
        for i in keep: Cn[i] = plan[i][4] @ Cn[i]; Ph[i] = plan[i][5] @ Ph[i]
        Rn = [rod(Ph[i]) @ R[i] for i in range(n)]
        resn = residual(Cn, Rn); tot = sum(v for v in resn.values() if math.isfinite(v))
        ok = legal(Cn, Rn)
        if verbose: print(f'  round {it}: residual {tot:.3e} (was {best_tot:.3e}) legal {ok} trust {trust:.4f} {time.time() - t0:.0f}s', flush=True)
        if ok and tot < best_tot:
            Cint, R, best_tot = Cn, Rn, tot
            trust = min(0.03, trust * 1.5)
            if tot < 1e-22: break
        else:
            trust *= 0.5
            if trust < 1e-6: break
    # snap the pieces that arrived; keep the snap only if the packing stays legal
    fin = residual(Cint, R); done = {}
    for i in sorted(fin, key=lambda i: fin[i]):
        if fin[i] > 1e-12: continue
        t = geo.target(Cint[i] / e, R[i], groups[i], plan[i][4])
        if t is None: continue
        Ct = Cint.copy(); Rt = list(R); Ct[i] = t[0] * e; Rt[i] = t[1]
        if legal(Ct, Rt): Cint, R = Ct, Rt; done[i] = plan[i][0]
    Cu = Cint / e
    after = measure(geo, Cu, R)
    return r, geo, Cu, R, before, after, done


# ---------------------------------------------------------------------------------------------------------------
# Local pull: one target piece at a time, with only its neighbourhood free (the rest are fixed obstacles).
def _round_local(pb, Cint, R, L, act, tg, held, trust, gapI, wallI, w):
    """one SLSQP round: pieces in act move (centre, rotation), all others are fixed; tg = {i: (Pi, PiO, D)} are pulled
    to their symmetric placements, held = {i: (Pi, PiO)} stay on theirs; returns new (Cint, R) for all pieces"""
    n = len(Cint); m = len(act); loc = {g: k for k, g in enumerate(act)}
    lim = (2 * pb.circ + 4 * trust + 0.05) ** 2
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if (i in loc or j in loc) and np.sum((Cint[i] - Cint[j]) ** 2) < lim]
    P = len(pairs)
    LG = np.stack([pb.V @ R[i].T for i in range(n)])
    if P:
        U0, E1, E2, c0, M0 = [], [], [], [], []
        for (i, j) in pairs:
            _, u, c = sat_gap(pb, Cint[i], R[i], Cint[j], R[j])
            e1, e2 = tangent_basis(u); m0 = (Cint[i] + Cint[j]) / 2
            U0.append(u); E1.append(e1); E2.append(e2); c0.append(c - u @ m0); M0.append(m0)
        U0, E1, E2, M0 = (np.array(A).reshape(P, 3) for A in (U0, E1, E2, M0)); c0 = np.array(c0)
    else:
        U0 = E1 = E2 = M0 = np.zeros((0, 3)); c0 = np.zeros(0)
    dmax = trust * (math.sqrt(3) + 3 * math.sqrt(3) * pb.circ); reach = dmax + 2 * trust + 1e-3
    Xa = Cint[act][:, None, :] + LG[act]
    slack = (L / 2) * pb.off[None, None, :] - Xa @ pb.CN.T
    ck, cv, cf = np.nonzero(slack < reach); nc = len(ck)
    cb = 2 * dmax + 1e-3
    rp, rs, rv, ri, rfix = [], [], [], [], []
    Xall = Cint[:, None, :] + LG
    for p, (i, j) in enumerate(pairs):
        for sg, k in ((-1.0, i), (1.0, j)):
            rel = Xall[k] - M0[p]; sl = sg * (rel @ U0[p] - c0[p])
            marg = cb + 3 * math.sqrt(2) * trust * (np.linalg.norm(rel, axis=1) + dmax) + dmax + 1e-3
            for v in np.nonzero(sl < marg)[0]:
                rp.append(p); rs.append(sg); rv.append(v); ri.append(k)
    rp, rs, rv, ri = np.array(rp, int), np.array(rs), np.array(rv, int), np.array(ri, int); npr = len(rp)
    isact = np.array([k in loc for k in ri], bool) if npr else np.zeros(0, bool)
    rl = np.array([loc.get(k, 0) for k in ri], int) if npr else np.zeros(0, int)
    ia = 6 * m; ic = ia + 2 * P; nvar = ic + P
    z0 = np.concatenate([Cint[act].ravel(), np.zeros(3 * m), np.zeros(2 * P), c0])
    LGa = LG[act]

    def unpack(z):
        Cz = z[:3 * m].reshape(m, 3); Ph = z[3 * m:6 * m].reshape(m, 3)
        Rr = np.stack([rod(Ph[k]) for k in range(m)])
        return Cz, Ph, np.einsum('nab,nvb->nva', Rr, LGa)

    def planes(z):
        ab = z[ia:ic].reshape(P, 2); Uraw = U0 + ab[:, :1] * E1 + ab[:, 1:] * E2
        nr = np.linalg.norm(Uraw, axis=1, keepdims=True); return Uraw / nr, nr

    def verts(z):
        Cz, Ph, Y = unpack(z)
        Xa = Cz[:, None, :] + Y
        Xr = np.where(isact[:, None], Xa[rl, rv] if npr else np.zeros((0, 3)), Xall[ri, rv] if npr else np.zeros((0, 3)))
        return Cz, Ph, Y, Xa, Xr

    def cons(z):
        Cz, Ph, Y, Xa, Xr = verts(z)
        g = [(L / 2) * pb.off[cf] - np.einsum('kd,kd->k', Xa[ck, cv], pb.CN[cf]) - wallI]
        if npr:
            U, _ = planes(z); c = z[ic:]
            g.append(rs * (np.einsum('kd,kd->k', Xr - M0[rp], U[rp]) - c[rp]) - gapI / 2)
        return np.concatenate(g)

    def jac(z):
        Cz, Ph, Y, Xa, Xr = verts(z)
        JL = np.stack([jac_left(Ph[k]) for k in range(m)])
        J = np.zeros((nc + npr, nvar)); rows = np.arange(nc)
        for d in range(3): J[rows, 3 * ck + d] = -pb.CN[cf, d]
        Gphi = np.einsum('kd,kde->ke', np.cross(pb.CN[cf], Y[ck, cv]), JL[ck])
        for d in range(3): J[rows, 3 * m + 3 * ck + d] = Gphi[:, d]
        if npr:
            U, nr = planes(z); rows = nc + np.arange(npr)
            dUa = (E1 - U * np.sum(U * E1, 1, keepdims=True)) / nr
            dUb = (E2 - U * np.sum(U * E2, 1, keepdims=True)) / nr
            Ur = U[rp]; rel = Xr - M0[rp]
            ra = rows[isact]; la = rl[isact]
            for d in range(3): J[ra, 3 * la + d] = (rs * Ur[:, d])[isact]
            if isact.any():
                Gp = np.einsum('kd,kde->ke', np.cross(Ur[isact], Y[la, rv[isact]]), JL[la])
                for d in range(3): J[ra, 3 * m + 3 * la + d] = -(rs[isact]) * Gp[:, d]
            J[rows, ia + 2 * rp] = rs * np.einsum('kd,kd->k', rel, dUa[rp])
            J[rows, ia + 2 * rp + 1] = rs * np.einsum('kd,kd->k', rel, dUb[rp])
            J[rows, ic + rp] = -rs
        return J

    def f(z):
        v = 0.0; g = np.zeros(nvar)
        for i, (Pi, PiO, D) in tg.items():
            k = loc[i]
            a = (np.eye(3) - Pi) @ z[3 * k:3 * k + 3]; v += a @ a; g[3 * k:3 * k + 3] += 2 * (np.eye(3) - Pi).T @ a
            b = (np.eye(3) - PiO) @ (z[3 * m + 3 * k:3 * m + 3 * k + 3] - D); v += w * b @ b
            g[3 * m + 3 * k:3 * m + 3 * k + 3] += 2 * w * (np.eye(3) - PiO).T @ b
        return v, g
    eq = []
    for i, (Pi, PiO) in held.items():
        if i not in loc: continue
        k = loc[i]
        for M, off in ((np.eye(3) - Pi, 3 * k), (np.eye(3) - PiO, 3 * m + 3 * k)):
            for row in M:
                if np.abs(row).max() > 1e-12: eq.append((off, row))
    A = np.zeros((len(eq), nvar))
    for r_, (off, row) in enumerate(eq): A[r_, off:off + 3] = row
    bounds = ([(v - trust, v + trust) for v in Cint[act].ravel()] + [(-3 * trust, 3 * trust)] * (3 * m) +
              [(-3 * trust, 3 * trust)] * (2 * P) + [(c - cb, c + cb) for c in c0])
    cl = [{'type': 'ineq', 'fun': cons, 'jac': jac}]
    if len(eq): cl.append({'type': 'eq', 'fun': lambda z: A @ z, 'jac': lambda z: A})
    rr = minimize(f, z0, jac=True, method='SLSQP', bounds=bounds, constraints=cl, options={'maxiter': 200, 'ftol': 1e-22})
    z = rr.x
    Cn = Cint.copy(); Rn = list(R)
    Cz = z[:3 * m].reshape(m, 3); Ph = z[3 * m:6 * m].reshape(m, 3).copy()
    for k, g in enumerate(act):
        c = Cz[k].copy(); ph = Ph[k]
        if g in held: c = held[g][0] @ c; ph = held[g][1] @ ph
        Cn[g] = c; Rn[g] = rod(ph) @ R[g]
    return Cn, Rn


def pull_local(fn, tlimit=600, rounds=25, verbose=False, C=None, Rs=None):
    """greedy single-piece moves first, then each remaining near-symmetric piece is pulled onto its placement while
    its neighbourhood relaxes (container fixed, clearances kept); a pull is kept only if the piece arrives"""
    r, C0, R0 = load(fn)
    if C is None: C, Rs = C0, R0
    geo = Geo(r['piece'], r['container']); s = float(r['s_full'])
    pb = Problem(r['piece'], r['container']); e = pb.edge
    n = len(C); L = s * 2 * pb.rhoC; w = pb.circ ** 2
    before = measure(geo, C0, R0)
    t0 = time.time(); done = {}

    def legal_set(Cu, R, idx):
        for i in idx:
            if geo.wall(Cu[i], R[i], s) < 0.99 * WALL: return False
            for j in range(n):
                if j != i and geo.gap(Cu[i], R[i], Cu[j], R[j]) < 0.99 * GAP: return False
        return True
    plan = snap_plan(geo, C, Rs)
    cur = {i: geo.stabilizer(C[i], Rs[i]) for i in range(n)}
    groups = {}
    for i in plan:
        for H, Pi, B in geo.subgroups:
            if len(H) == plan[i][0] and np.allclose(Pi, plan[i][4]): groups[i] = H; break
    held = {i: (plan[i][4], plan[i][5]) for i in plan if plan[i][0] == cur[i]}
    targets = sorted([i for i in plan if plan[i][0] > cur[i]], key=lambda i: plan[i][1])
    Cint = C * e; R = [x.copy() for x in Rs]
    for i in targets:
        if time.time() - t0 > tlimit: break
        Pi, PiO = plan[i][4], plan[i][5]; H = groups[i]
        nb = [j for j in range(n) if np.linalg.norm(Cint[j] - Cint[i]) < 2.6 * pb.circ]
        act = sorted(set(nb) | {k for j in nb for k in range(n) if np.linalg.norm(Cint[k] - Cint[j]) < 2.2 * pb.circ})
        Cc, Rc = Cint.copy(), list(R); trust = 0.02; prev = math.inf

        def resid(Cc, Rc):
            t = geo.target(Cc[i] / e, Rc[i], H, Pi)
            if t is None: return math.inf, None
            pc = (np.eye(3) - Pi) @ Cc[i]; d = log_rot(t[1] @ Rc[i].T)
            return float(pc @ pc + w * d @ d), d
        prev, D = resid(Cc, Rc)
        for it in range(rounds):
            if D is None: break
            Cn, Rn = _round_local(pb, Cc, Rc, L, act, {i: (Pi, PiO, D)}, held, trust, GAP * e, WALL * e, w)
            rn, Dn = resid(Cn, Rn)
            if rn < prev and legal_set(Cn / e, Rn, act):
                Cc, Rc, prev, D = Cn, Rn, rn, Dn; trust = min(0.03, trust * 1.5)
                if prev < 1e-24: break
            else:
                trust *= 0.5
                if trust < 1e-6: break
        if prev < 1e-12:
            t = geo.target(Cc[i] / e, Rc[i], H, Pi)
            Ct, Rt = Cc.copy(), list(Rc); Ct[i] = t[0] * e; Rt[i] = t[1]
            if legal_set(Ct / e, Rt, act):
                Cint, R = Ct, Rt; held[i] = (Pi, PiO); done[i] = plan[i][0]
                if verbose: print(f'  piece {i}: placed (|K| = {plan[i][0]}) {time.time() - t0:.0f}s', flush=True)
                continue
        if verbose: print(f'  piece {i}: blocked (residual {prev:.2e}) {time.time() - t0:.0f}s', flush=True)
    Cu = Cint / e
    after = measure(geo, Cu, R)
    return r, geo, Cu, R, before, after, done
