#!/usr/bin/env python3
"""Nested (composite) packings of the Platonic solids (15 Oct 2026, Alejandro: the Platonic problems up to n = 100).

    python3 scripts/compose3d.py one-piece          # s(P in Q, 1) for every Platonic pair -> state/one_piece3d.json
    python3 scripts/compose3d.py compose [--apply]  # composites that beat (or fill) the archive

Scales are container edge / piece edge, so they multiply: n copies of Q in C at s(Q in C, n), and m copies of P in Q
at s(P in Q, m), give n*m copies of P in C at s(P in Q, m) * s(Q in C, n) (a copy of the P-packing inside each Q).
The same construction as scripts/compose_nd.py in 4-6 dimensions. Every composite is re-legalized (exact.certify:
scaled apart until no pair overlaps, then the tight container) before it is stored, and certified exactly by the
publisher like every other record. With --apply a composite becomes the case's best when the case is empty or the
composite is smaller (src move 'compose'; credit passes on from contributed components as lineage)."""
import json, math, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import engine as E
import exact

PLAT = E.PLATONIC
ONE = os.path.join(E.STATE, 'one_piece3d.json')


def pid(P, Q): return E.pid(P, Q)


def rotvec(v):
    a = float(np.linalg.norm(v))
    if a < 1e-15: return np.eye(3)
    k = v / a; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def one_piece(starts=300, seed=1):
    """s(P in Q, 1): the best rotation of a single piece (random rotations, then Nelder-Mead on a rotation vector)"""
    from scipy.optimize import minimize
    from scipy.spatial.transform import Rotation
    rng = np.random.default_rng(seed); out = {}
    for P in PLAT:
        for Q in PLAT:
            if P == Q: continue
            p = pid(P, Q); pb = E.problem(p)
            f = lambda R: pb.s_of_L(exact.tight_container(pb, np.zeros((1, 3)), [R])[0])
            Rs = [np.eye(3)] + list(Rotation.random(starts, random_state=rng.integers(1 << 30)).as_matrix())
            vals = sorted(((f(R), i) for i, R in enumerate(Rs)))[:12]
            best = None
            for v, i in vals:
                R0 = Rs[i]
                res = minimize(lambda w: f(rotvec(w) @ R0), np.zeros(3), method='Nelder-Mead',
                               options=dict(xatol=1e-12, fatol=1e-14, maxiter=4000))
                R = rotvec(res.x) @ R0; s = f(R)
                if best is None or s < best[0]: best = (s, R)
            out[p] = {'s': best[0], 'Q': list(map(float, exact.R_to_quat(best[1])))}
            print(p, round(best[0], 10), flush=True)
    json.dump(out, open(ONE, 'w'), indent=1)
    return out


def component(p, n, S1):
    if n == 1:
        P, Q = E.PID[p]
        if P == Q: return np.zeros((1, 3)), [[1.0, 0, 0, 0]], {}
        return np.zeros((1, 3)), [S1[p]['Q']], {}
    b = E.load_case(p, n)['best']
    return np.array(b['C'], float), b['Q'], b.get('src') or {}


def compose(P, Q, C, m, n, N, S1):
    pq, qc, pc = pid(P, Q), pid(Q, C), pid(P, C)
    pbi, pbo, pb = E.problem(pq), E.problem(qc), E.problem(pc)
    Ci, Qi, si = component(pq, m, S1); Co, Qo, so = component(qc, n, S1)
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


def main_compose(apply):
    S1 = json.load(open(ONE))
    S = {}
    for P in PLAT:
        for Q in PLAT:
            p = pid(P, Q)
            S[(p, 1)] = 1.0 if P == Q else S1[p]['s']
            for n in range(E.NMIN, E.NMAX + 1):
                c = E._read(E._path('best', p, n)) if hasattr(E, '_read') else None
                if c is None:
                    try: c = E.load_case(p, n)
                    except Exception: c = None
                if c and c.get('best'): S[(p, n)] = c['best']['s']
    took = 0
    for P in PLAT:
        for C in PLAT:
            p = pid(P, C)
            for N in range(E.NMIN, E.NMAX + 1):
                cur = S.get((p, N)); cands = []
                for Q in PLAT:
                    pq, qc = pid(P, Q), pid(Q, C)
                    for m in range(1, E.NMAX + 1):
                        n = -(-N // m)
                        if n > E.NMAX or not S.get((pq, m)) or not S.get((qc, n)): continue
                        if (m == 1 and Q == P) or (n == 1 and Q == C): continue
                        cands.append((S[(pq, m)] * S[(qc, n)], Q, m, n))
                cands.sort()
                for v, Q, m, n in cands[:3]:
                    if cur and v >= cur * (1 - 1e-9): break
                    s, CC, QQ, lin = compose(P, Q, C, m, n, N, S1)
                    line = f'{p} N={N} via {Q} (m={m}, n={n}): product {v:.10f}, built {s:.10f}, archive {cur if cur else "-"}'
                    if cur and s >= cur - 1e-12: print(line, '-> not better'); continue
                    print(line, '-> ' + ('NEW BEST' if cur else 'FILLED') + ('' if apply else ' (dry run)'), flush=True)
                    if apply:
                        with E.locked():
                            case = E.load_case(p, N); b0 = case['best']
                            if b0 and s >= b0['s'] - 1e-12: break
                            src = {'move': 'compose', 'via': Q, 'inner': [pid(P, Q), m], 'outer': [pid(Q, C), n]}
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
                    took += 1
                    if apply: S[(p, N)] = s; cur = s
                    break
            if apply: E.enforce_monotone(p, lambda m: None)
    print(f'{took} composite packings ' + ('stored' if apply else '(dry run)'))


if __name__ == '__main__':
    if sys.argv[1] == 'one-piece': one_piece()
    else: main_compose('--apply' in sys.argv)
