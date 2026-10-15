#!/usr/bin/env python3
"""Composite (nested) packings of regular polytopes in 4-6 dimensions (15 Oct 2026).

    python3 scripts/compose_nd.py S1.json [--apply]

If n copies of Q fit in a container C at scale s(Q in C, n), and m copies of P fit in Q at scale s(P in Q, m), then
placing a copy of the P-packing inside each Q gives n*m copies of P in C at scale s(P in Q, m) * s(Q in C, n)
(scales are container edge / piece edge, so they multiply). This generalizes the whole-body inclusion behind
PingYou Ltd's contribution #79 (a 120-cell inside each 24-cell of a 24-cell packing). S1.json holds the one-piece
packings s(P in Q, 1) (scratch computation: best rotation of a single piece). For every case where a composite beats
the archive, the packing is built, re-legalized (every pair separated by a hyperplane, tight container) and, with
--apply, stored as the case's best (src move 'compose'; credit passes on from contributed components)."""
import json, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.append(os.path.join(ROOT, 'scripts'))
import engine_nd as E
import ndsim


def component(p, n, S1):
    """(C, R, src) of the archive's packing of case p with n pieces (n = 1: the one-piece packing of S1)"""
    if n == 1:
        if p.split('in')[0] == p.split('in')[1]: d = E.DIM[p]; return np.zeros((1, d)), np.eye(d)[None], {}
        v = S1[p]; return np.array(v['C'], float), np.array(v['R'], float), {}
    b = E.load_case(p, n)['best']
    return np.array(b['C'], float), np.array(b['R'], float), b.get('src') or {}


def compose(P, Q, C, m, n, N, S1):
    pq, qc, pc = f'{P}in{Q}', f'{Q}in{C}', f'{P}in{C}'
    pbi, pbo, pb = E.problem(pq), E.problem(qc), E.problem(pc)
    Ci, Ri, si = component(pq, m, S1); Co, Ro, so = component(qc, n, S1)
    Li, ti = ndsim.tight_container(pbi, Ci, Ri)            # inner pieces shifted into the origin-centred container
    X = Ci + ti
    s_in = pbi.s_of_L(Li)
    k = s_in * pbi.cscale / pbo.scale                     # (Q in C) units -> (P in C) units
    CC = np.array([k * Co[j] + Ro[j] @ X[i] for j in range(len(Co)) for i in range(len(X))])[:N]
    RR = np.array([Ro[j] @ Ri[i] for j in range(len(Co)) for i in range(len(X))])[:N]
    lg = ndsim.legalize(pb, CC, RR)
    lin = next((x.get('contributor') or x.get('lineage') for x in (si, so) if x.get('contributor') or x.get('lineage')), None)
    return lg, lin


def main():
    S1 = json.load(open(sys.argv[1])); apply = '--apply' in sys.argv
    S = {}
    for p in E.PID:
        S[(p, 1)] = 1.0 if E.PID[p][0] == E.PID[p][1] else (S1.get(p) or {}).get('s')
        for n in range(E.NMIN, E.nmax(p) + 1):
            c = E._read(E._path('best', p, n))
            if c and c.get('best'): S[(p, n)] = c['best']['s']
    dims = {}
    for p, (a, b) in E.PID.items(): dims.setdefault(E.DIM[p], set()).update((a, b))
    took = 0
    for p, (P, C) in E.PID.items():
        for N in range(E.NMIN, E.nmax(p) + 1):
            cur = S.get((p, N)); cands = []
            for Q in dims[E.DIM[p]]:
                pq, qc = f'{P}in{Q}', f'{Q}in{C}'
                for m in range(1, E.nmax(pq) + 1):
                    n = -(-N // m)
                    if n > E.nmax(qc) or not S.get((pq, m)) or not S.get((qc, n)): continue
                    if (m == 1 and Q == P) or (n == 1 and Q == C): continue
                    cands.append((S[(pq, m)] * S[(qc, n)], Q, m, n))
            cands.sort()
            for v, Q, m, n in cands[:3]:
                if not cur or v >= cur * (1 - 1e-9): break
                lg, lin = compose(P, Q, C, m, n, N, S1)
                line = f'{p} N={N} via {Q} (m={m}, n={n}): product {v:.10f}, built {lg["s"]:.10f}, archive {cur:.10f}'
                if lg['s'] >= cur - 1e-12: print(line, '-> not better'); continue
                print(line, '-> NEW BEST' + ('' if apply else ' (dry run)'))
                if apply:
                    with E.locked():
                        case = E.load_case(p, N); b0 = case['best']
                        if b0 and lg['s'] >= b0['s'] - 1e-12: break
                        C2, R2 = E.rnd(lg['C'], lg['R'])
                        src = {'move': 'compose', 'via': Q, 'inner': [f'{P}in{Q}', m], 'outer': [f'{Q}in{C}', n]}
                        if lin: src['lineage'] = lin
                        case['best'] = {'s': lg['s'], 'C': C2, 'R': R2, 't': time.time(), 'tightened': False, 'src': src}
                        st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time(); st['needs_tighten'] = True
                        E.save_case(case)
                        E.pool_insert(p, N, {'s': lg['s'], 'C': C2, 'R': R2, 'src': 'compose', 't': time.time()})
                        E.enforce_monotone(p, print)
                        with open(os.path.join(E.STATE, 'attempts.jsonl'), 'a') as f:
                            f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': N, 'move': 'compose', 'raw': v, 's': lg['s'],
                                                'best_before': b0['s'] if b0 else None, 'improved': True, 'secs': 0, 'raw_secs': 0,
                                                'host': 'compose'}) + '\n')
                    S[(p, N)] = lg['s']; cur = lg['s']
                took += 1
                break
    print(f'{took} composite packings beat the archive' + ('' if apply else ' (dry run)'))


if __name__ == '__main__':
    main()
