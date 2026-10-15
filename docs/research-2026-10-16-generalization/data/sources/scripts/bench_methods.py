"""Experimental bake-off of search moves at equal treatment (13 Oct 2026; see docs/SEARCH_METHODS_REVIEW.md).

    python3 scripts/bench_methods.py OUT.jsonl SECONDS [WORKERS] [METHODS] [CASES]

Each worker repeatedly picks a benchmark case and a method (round robin), runs one attempt and fully tightens the
result with the production tightener (no early abort, so every attempt yields a final s). Nothing is written to the
archive; every attempt is one JSON line: case, method, raw, s, record s, seconds, and method details.

Methods
  fresh      production fresh start (random balls -> soft-to-rigid -> legalize)
  symfresh   the same with the configuration constrained to a random cyclic subgroup <g> of the container's symmetry
             group during the soft phase (orbits of |g| pieces plus pieces on the fixed set of g); free tightening after
  symfresh25 symfresh starting the morph at softness r0 = 0.25 instead of 0.5 (Nakajima's "quarter" start)
  hop        production 'gentle' hop from the current record (or a pool packing)
  squeeze    fixed-size separation below the record (sparrow / HAMSP style), see sim.js squeeze()
"""
import json, os, sys, time, random, math, multiprocessing as mp
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import engine

from symmetry import SOL, sym_group, sym_spec


def cases_default():
    """Benchmark set: mature cases of the three new families at n = 9..30 (fixed list, chosen at random once)."""
    rng = random.Random(20261013)
    out = []
    for fam in ('archimedean', 'catalan', 'prisms'):
        probs = [p for p in engine.PID if engine.FAM[p] == fam]
        for n in (9, 12, 15, 18, 21, 24, 27, 30):
            out.append((rng.choice(probs), n))
    return out


def attempt(sim, p, n, method, rng):
    piece, container = engine.PID[p]
    pb = engine.problem(p)
    case = engine.load_case(p, n); best = case['best']; rec = best['s']
    seed = rng.randrange(1, 2 ** 31 - 1); info = {}
    t0 = time.time()
    B = 1.0 if n <= 16 else 0.7
    fresh = dict(op='fresh', piece=piece, container=container, n=n, seed=seed, mode='improved', anneal=True,
                 compact=int(5000 * B), morph=int(45000 * B), settle=int(3000 * B))
    if method == 'fresh':
        raw = sim.call(fresh)
    elif method == 'symchain':                     # a symmetric fresh start, then 3 gentle hops from the chain's best
        spec, info = sym_spec(piece, container, n, rng)
        if spec is None: return None
        raw0 = sim.call(dict(fresh, sym=spec))
        row = {'piece': piece, 'container': container, 'problem': p, 'n': n, 'seed': seed, 'mode': method, 'B': 0, 'C': raw0['C'], 'Q': raw0['Q']}
        cur = engine.tighten(row, None, n, 0.03); info['s0'] = cur['s']
        V = dict(engine.HOP_DEFAULT, **engine.VARIANTS['gentle'])
        for h in range(3):
            lo, hi = V['minDiff']
            prm = dict(op='hop', piece=piece, container=container, seed=seed + 101 * (h + 1), C=cur['C'], Q=cur['Q'], L=2 * pb.rhoC * cur['s'],
                       morph=4000 + 150 * n, settle=1000 + 25 * n, minDiff=math.exp(rng.uniform(math.log(lo), math.log(hi))),
                       expand=rng.uniform(*V['expand']), rh=rng.uniform(0.06, 0.2), noise=V['noise'], shake=V['shake'],
                       focus=0 if (n < 8 or rng.random() >= V['focus_p']) else rng.randint(3, max(4, n // 3)))
            r1 = sim.call(prm)
            row = dict(row, C=r1['C'], Q=r1['Q'])
            o1 = engine.tighten(row, cur['s'], n, 0.03)
            if o1['s'] < cur['s']: cur = o1
        raw = {'s': info['s0'], 'C': cur['C'], 'Q': cur['Q']}
    elif method.startswith('symfresh'):
        spec, info = sym_spec(piece, container, n, rng)
        if spec is None: return None
        if method == 'symfresh25': fresh['r0'] = 0.25
        raw = sim.call(dict(fresh, sym=spec))
    elif method == 'hop':
        pool = engine.load_pool(p, n)
        V = dict(engine.HOP_DEFAULT, **engine.VARIANTS['gentle'])
        start = best if (rng.random() < V['from_best'] or not pool) else rng.choice(pool)
        lo, hi = V['minDiff']
        prm = dict(op='hop', piece=piece, container=container, seed=seed, C=start['C'], Q=start['Q'], L=2 * pb.rhoC * start['s'],
                   morph=4000 + 150 * n, settle=1000 + 25 * n, minDiff=math.exp(rng.uniform(math.log(lo), math.log(hi))),
                   expand=rng.uniform(*V['expand']), rh=rng.uniform(0.06, 0.2), noise=V['noise'], shake=V['shake'],
                   focus=0 if (n < 8 or rng.random() >= V['focus_p']) else rng.randint(3, max(4, n // 3)))
        raw = sim.call(prm); info = {'from': 'best' if start is best else 'pool', 'minDiff': round(prm['minDiff'], 4)}
    elif method == 'squeeze':
        delta = math.exp(rng.uniform(math.log(0.001), math.log(0.01)))
        raw = sim.call(dict(op='squeeze', piece=piece, container=container, seed=seed, C=best['C'], Q=best['Q'],
                            L=2 * pb.rhoC * rec, delta=delta, n=n))
        info = {'delta': round(delta, 5), 'ok': raw.get('ok'), 'rounds': raw.get('rounds')}
    else:
        raise ValueError(method)
    t_raw = time.time() - t0
    row = {'piece': piece, 'container': container, 'problem': p, 'n': n, 'seed': seed, 'mode': method, 'B': 0,
           'C': raw['C'], 'Q': raw['Q']}
    out = engine.tighten(row, None, n, 0.03)
    res = {'p': p, 'n': n, 'method': method, 'raw': raw['s'], 's': out['s'], 'rec': rec, 'beat': out['s'] < rec - 1e-9,
           'secs': round(time.time() - t0, 1), 'raw_secs': round(t_raw, 1), 'since': case['stats'].get('since'),
           'attempts': engine.total_attempts(case['stats']), **info}
    if res['beat']: res.update(C=out['C'], Q=out['Q'])
    return res


def worker(wid, out_path, deadline, methods, cases):
    rng = random.Random(os.getpid() * 1000 + wid)
    sim = engine.Sim(); k = rng.randrange(len(methods))
    while time.time() < deadline:
        p, n = rng.choice(cases); m = methods[k % len(methods)]; k += 1
        try:
            r = attempt(sim, p, n, m, rng)
        except Exception as e:
            r = {'p': p, 'n': n, 'method': m, 'error': str(e)[:300]}
            sim.start()
        if r is None: continue
        r['t'] = round(time.time()); r['w'] = wid
        with open(out_path, 'a') as f: f.write(json.dumps(r) + '\n')


if __name__ == '__main__':
    out, secs = sys.argv[1], float(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else os.cpu_count()
    methods = (sys.argv[4] if len(sys.argv) > 4 else 'fresh,symfresh,symfresh25,hop').split(',')
    cases = cases_default() if len(sys.argv) <= 5 else [(x.split(':')[0], int(x.split(':')[1])) for x in sys.argv[5].split(',')]
    deadline = time.time() + secs
    ps = [mp.Process(target=worker, args=(w, out, deadline, methods, cases)) for w in range(W)]
    for q in ps: q.start()
    for q in ps: q.join()
