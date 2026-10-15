#!/usr/bin/env python3
"""Cost of one search attempt in 4, 5 and 6 dimensions against 3D on the same machine (15 Oct 2026; docs/HIGHER_DIM.md).

    python3 scripts/nd_bench.py OUT.jsonl CASE [CASE ...]
CASE = piece:container:n (src/polytopes_nd.json ids, e.g. c24:c24:40) or 3d:<problem>:n (an engine.py problem, e.g.
3d:dodindod:40). Per case: a fresh soft-to-rigid run from random balls + its tightening, then two hops from that
packing + their tightenings (the engine's settings), each timed; one JSON line per case."""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.append(os.path.join(ROOT, 'scripts'))      # appended: scripts/coverage.py must not shadow the package numba imports
import numpy as np


def nd_case(piece, cont, n):
    import ndsim, ndslp
    pb = ndsim.Problem(piece, cont)
    B = 1.0 if n <= 16 else 0.7
    t = time.time(); out = ndsim.fresh(pb, n, 1, B=B); t1 = time.time() - t
    t = time.time(); tt = ndslp.tighten(pb, out['C'], out['R'], tlimit=30 + 4 * n, reg=1e-4); t2 = time.time() - t
    rec = dict(p=f'{piece}in{cont}', d=pb.d, n=n, raw=out['s'], s=tt['s'], t_fresh=round(t1, 1), t_tight=round(t2, 1), it=tt['iters'], hops=[])
    best = tt
    for k in range(2):
        t = time.time(); h = ndsim.hop(pb, best['C'], best['R'], pb.L_of_s(best['s']), 7 + k, minDiff=0.15, expand=0.03, rh=0.12,
                                       morph=4000 + 150 * n, settle=1000 + 25 * n); t3 = time.time() - t
        t = time.time(); th = ndslp.tighten(pb, h['C'], h['R'], tlimit=30 + 4 * n, reg=1e-4); t4 = time.time() - t
        rec['hops'].append(dict(raw=h['s'], s=th['s'], t_sim=round(t3, 1), t_tight=round(t4, 1), it=th['iters']))
        if th['s'] < best['s']: best = th
    rec['best'] = best['s']; rec['dens'] = n * pb.volume / (pb.Cvolume * best['s'] ** pb.d)
    return rec


def d3_case(p, n):
    import engine, fastslp
    piece, cont = engine.PID[p]; pb = engine.problem(p); sim = engine.Sim()
    B = 1.0 if n <= 16 else 0.7
    t = time.time()
    raw = sim.call(dict(op='fresh', piece=piece, container=cont, n=n, seed=1, mode='improved', anneal=True,
                        compact=int(5000 * B), morph=int(45000 * B), settle=int(3000 * B)))
    t1 = time.time() - t
    row = {'piece': piece, 'container': cont, 'problem': p, 'n': n, 'seed': 1, 'mode': 'fresh', 'B': 0, 'C': raw['C'], 'Q': raw['Q']}
    t = time.time(); tt = fastslp.tighten_run(row, tlimit=30 + 4 * n, slp_floor=1e-6, reg=1e-4); t2 = time.time() - t
    rec = dict(p=p, d=3, n=n, raw=raw['s'], s=tt['s'], t_fresh=round(t1, 1), t_tight=round(t2, 1), it=tt['iters'], hops=[])
    best = tt
    for k in range(2):
        t = time.time()
        h = sim.call(dict(op='hop', piece=piece, container=cont, seed=7 + k, C=best['C'], Q=best['Q'], L=2 * pb.rhoC * best['s'],
                          minDiff=0.15, expand=0.03, rh=0.12, morph=4000 + 150 * n, settle=1000 + 25 * n))
        t3 = time.time() - t
        row = dict(row, C=h['C'], Q=h['Q'], mode='hop')
        t = time.time(); th = fastslp.tighten_run(row, tlimit=30 + 4 * n, slp_floor=1e-6, reg=1e-4); t4 = time.time() - t
        rec['hops'].append(dict(raw=h['s'], s=th['s'], t_sim=round(t3, 1), t_tight=round(t4, 1), it=th['iters']))
        if th['s'] < best['s']: best = th
    rec['best'] = best['s']
    sim.p.kill()
    return rec


def main():
    out = open(sys.argv[1], 'a')
    for case in sys.argv[2:]:
        a, b, n = case.split(':'); n = int(n)
        t = time.time()
        try:
            rec = d3_case(b, n) if a == '3d' else nd_case(a, b, n)
        except Exception as e:
            rec = dict(case=case, error=f'{type(e).__name__}: {str(e)[:300]}')
        rec['wall'] = round(time.time() - t, 1)
        out.write(json.dumps(rec) + '\n'); out.flush(); print(json.dumps(rec), flush=True)


if __name__ == '__main__':
    main()
