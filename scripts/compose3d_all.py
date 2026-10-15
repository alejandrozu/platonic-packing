#!/usr/bin/env python3
"""Nested (composite) packings for every 3D problem (16 Oct 2026; scripts/compose3d.py did the Platonic pairs).

    python3 scripts/compose3d_all.py [--apply] [--only FAMILY[,FAMILY]] [--starts K]

s(P in C, N) <= s(P in Q, m) * s(Q in C, n) for N <= m*n (scales are container size / piece size at fixed canonical
solids, so they multiply): a copy of an m-packing of P in Q inside each piece of an n-packing of Q in C. Q runs over
every solid of the archive. A factor with m = 1 or n = 1 is a one-piece fit (the best rotation of a single piece; for
any pair of solids, cached in state/one_piece3d.json); it is computed only when the composite could beat the archive
even at the volume bound (vol P / vol Q)^(1/3) for that factor. Every composite is re-legalized (exact.certify, then
the tight container) before it is stored; the publisher certifies it exactly like any record."""
import json, math, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import engine as E
import exact
from compose3d import rotvec

ONE = os.path.join(E.STATE, 'one_piece3d.json')
SOLIDS = sorted({x for pc in E.PID.values() for x in pc})
_pb = {}


def prob(P, Q):
    k = (P, Q)
    if k not in _pb:
        p = E.pid(P, Q)
        _pb[k] = E.problem(p) if p in E.PID else exact.Problem(P, Q)
    return _pb[k]


def vol_lb(P, Q):
    return (exact.SOL[P]['volume'] / exact.SOL[Q]['volume']) ** (1 / 3)


def fit_one(P, Q, starts=60, seed=1):
    """s(P in Q, 1): random rotations, then Nelder-Mead on a rotation vector from the best few"""
    from scipy.optimize import minimize
    from scipy.spatial.transform import Rotation
    pb = prob(P, Q)
    f = lambda R: pb.s_of_L(exact.tight_container(pb, np.zeros((1, 3)), [R])[0])
    Rs = [np.eye(3)] + list(Rotation.random(starts, random_state=seed).as_matrix())
    best = None
    for v, i in sorted((f(R), i) for i, R in enumerate(Rs))[:4]:
        R0 = Rs[i]
        res = minimize(lambda w: f(rotvec(w) @ R0), np.zeros(3), method='Nelder-Mead', options=dict(xatol=1e-12, fatol=1e-14, maxiter=3000))
        R = rotvec(res.x) @ R0; s = f(R)
        if best is None or s < best[0]: best = (s, R)
    return {'s': best[0], 'Q': list(map(float, exact.R_to_quat(best[1])))}


def main():
    apply = '--apply' in sys.argv
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    starts = int(sys.argv[sys.argv.index('--starts') + 1]) if '--starts' in sys.argv else 60
    S1 = json.load(open(ONE)) if os.path.exists(ONE) else {}
    S = {}
    for p in E.PID:
        for n in range(E.NMIN, E.NMAX + 1):
            c = E._read(E._path('best', p, n))
            if c and c.get('best'): S[(p, n)] = c['best']['s']

    def factor(P, Q, k, exact_one=True):
        """(value, is_lower_bound) of s(P in Q, k), or None"""
        if k == 1:
            if P == Q: return 1.0, False
            key = E.pid(P, Q)
            if key in S1: return S1[key]['s'], False
            if not exact_one: return vol_lb(P, Q), True
            S1[key] = fit_one(P, Q, starts); json.dump(S1, open(ONE, 'w'), indent=1)
            return S1[key]['s'], False
        v = S.get((E.pid(P, Q), k))
        return (v, False) if v else None

    took = 0
    for p, (P, C) in E.PID.items():
        if only and E.FAM[p] not in only: continue
        for N in range(E.NMIN, E.NMAX + 1):
            cur = S.get((p, N)); cands = []
            for Q in SOLIDS:
                for m in range(1, E.NMAX + 1):
                    n = -(-N // m)
                    if n > E.NMAX: continue
                    if (m == 1 and Q == P) or (n == 1 and Q == C): continue
                    a = factor(P, Q, m, False); b = factor(Q, C, n, False)
                    if not a or not b: continue
                    cands.append((a[0] * b[0], a[1] or b[1], Q, m, n))
            cands.sort()
            for v, lb, Q, m, n in cands[:6]:
                if cur and v >= cur * (1 - 1e-9): break
                if lb and '--no-one-piece' in sys.argv: continue
                if lb:                                       # a bound only: compute the one-piece fit(s), re-rank later
                    a = factor(P, Q, m); b = factor(Q, C, n); v = a[0] * b[0]
                    if cur and v >= cur * (1 - 1e-9): continue
                s, CC, QQ, lin = compose(P, Q, C, m, n, N, S1)
                line = f'{p} N={N} via {Q} (m={m}, n={n}): product {v:.10f}, built {s:.10f}, archive {cur}'
                if cur and s >= cur - 1e-12: print(line, '-> not better', flush=True); continue
                print(line, '-> ' + ('NEW BEST' if cur else 'FILLED') + ('' if apply else ' (dry run)'), flush=True)
                if apply:
                    store(p, N, s, CC, QQ, lin, P, Q, C, m, n, v)
                    S[(p, N)] = s; cur = s
                took += 1
                break
        if apply: E.enforce_monotone(p, lambda m: None)
    print(f'{took} composite packings ' + ('stored' if apply else '(dry run)'))


def component(P, Q, k, S1):
    if k == 1:
        if P == Q: return np.zeros((1, 3)), [[1.0, 0, 0, 0]], {}
        return np.zeros((1, 3)), [S1[E.pid(P, Q)]['Q']], {}
    b = E.load_case(E.pid(P, Q), k)['best']
    return np.array(b['C'], float), b['Q'], b.get('src') or {}


def compose(P, Q, C, m, n, N, S1):
    pbi, pbo, pb = prob(P, Q), prob(Q, C), prob(P, C)
    Ci, Qi, si = component(P, Q, m, S1); Co, Qo, so = component(Q, C, n, S1)
    Ri = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in Qi]; Ro = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in Qo]
    Li, ti = exact.tight_container(pbi, Ci, Ri)
    X = Ci + ti; s_in = pbi.s_of_L(Li)
    k = s_in * pbi.edge / pbo.edge                        # (Q in C) internal units -> (P in C) internal units
    CC = np.array([k * Co[j] + Ro[j] @ X[i] for j in range(len(Co)) for i in range(len(X))])[:N]
    RR = [Ro[j] @ Ri[i] for j in range(len(Co)) for i in range(len(X))][:N]
    L, _, C0 = exact.certify(pb, CC, RR)
    Lt, t = exact.tight_container(pb, C0, RR)
    lin = next((x.get('contributor') or x.get('lineage') for x in (si, so) if isinstance(x, dict) and (x.get('contributor') or x.get('lineage'))), None)
    return pb.s_of_L(Lt), (C0 + t), [list(map(float, exact.R_to_quat(R))) for R in RR], lin


def store(p, N, s, CC, QQ, lin, P, Q, C, m, n, v):
    with E.locked():
        case = E.load_case(p, N); b0 = case['best']
        if b0 and s >= b0['s'] - 1e-12: return
        src = {'move': 'compose', 'via': Q, 'inner': [E.pid(P, Q), m], 'outer': [E.pid(Q, C), n]}
        if lin: src['lineage'] = lin
        case['best'] = {'s': s, 'C': CC.tolist(), 'Q': QQ, 't': time.time(), 'tightened': False, 'src': src}
        st = case['stats']; st['improvements'] = st.get('improvements', 0) + 1; st['since'] = 0
        st['last_improve'] = time.time(); st['needs_tighten'] = True
        E.save_case(case)
        E.pool_insert(p, N, {'s': s, 'C': CC.tolist(), 'Q': QQ, 'src': 'compose', 't': time.time()})
        with open(os.path.join(E.STATE, 'attempts.jsonl'), 'a') as f:
            f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': N, 'move': 'compose', 'raw': v, 's': s,
                                'best_before': b0['s'] if b0 else None, 'improved': True, 'secs': 0, 'raw_secs': 0,
                                'host': 'compose'}) + '\n')


if __name__ == '__main__':
    main()
