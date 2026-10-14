"""Large-n study (14 Oct 2026): how well and how cheaply can n = 41..NMAX be produced for one problem?

    python3 scripts/largen_bench.py OUTDIR PROBLEM NMAX MINUTES [WORKERS]

1. Crystal cuts (scripts/crystal_cut.py) give a legal packing for every n at once; each is tightened.
2. Ascend chain: for n = 41, 42, ..., WORKERS-1 parallel 'ascend' attempts (insert a piece into the best (n-1)
   packing at its largest hole, soft-to-rigid hop, tighten) plus the tightened crystal cut compete; the best is
   best[n]. Every attempt is logged with its simulation and tightening times.
3. Descend sweep: best[n+1] minus its least useful piece replaces best[n] when smaller (monotone s(n)).
4. Remaining time: hops at random n (logged), to measure improvement rates at large n.
Tightening is the vectorized sequential LP (src/fastslp.py). Nothing is written to the archive: results go to
OUTDIR/attempts.jsonl and OUTDIR/best/<problem>_nNNN.json (centres, quaternions, s)."""
import json, math, os, sys, time, random
import multiprocessing as mp
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import engine, exact, fastslp

_SIM = None


def sim():
    global _SIM
    if _SIM is None: _SIM = engine.Sim()
    return _SIM


def tighten(p, n, C, Q, mode, tlimit=None):
    piece, cont = engine.PID[p]
    row = {'piece': piece, 'container': cont, 'problem': p, 'n': n, 'seed': 0, 'mode': mode, 'B': 0, 'C': C, 'Q': Q}
    return fastslp.tighten_run(row, tlimit=tlimit or (30 + 4 * n), slp_floor=1e-6)


def task(args):
    """One attempt; returns a log dict with the packing."""
    kind, p, n, src, seed = args
    piece, cont = engine.PID[p]; pb = engine.problem(p); rng = random.Random(seed)
    t0 = time.time(); info = {}
    try:
        if kind == 'ascend':
            raw = sim().call(dict(op='hop', piece=piece, container=cont, seed=seed, C=src['C'], Q=src['Q'], L=2 * pb.rhoC * src['s'],
                                  add=1, rh=rng.uniform(0.15, 0.3), expand=rng.uniform(0.0, 0.03), morph=4000 + 150 * n, settle=1000 + 25 * n))
        elif kind == 'hop':
            V = dict(engine.HOP_DEFAULT, **engine.VARIANTS['gentle']); lo, hi = V['minDiff']
            raw = sim().call(dict(op='hop', piece=piece, container=cont, seed=seed, C=src['C'], Q=src['Q'], L=2 * pb.rhoC * src['s'],
                                  morph=4000 + 150 * n, settle=1000 + 25 * n, minDiff=math.exp(rng.uniform(math.log(lo), math.log(hi))),
                                  expand=rng.uniform(*V['expand']), rh=rng.uniform(*V['rh']), noise=V['noise'], shake=V['shake'],
                                  focus=0 if rng.random() >= V['focus_p'] else rng.randint(3, max(4, n // 3))))
        elif kind == 'cut':
            raw = {'s': src['s'], 'C': src['C'], 'Q': src['Q']}
        else:
            raise ValueError(kind)
        t_sim = time.time() - t0
        out = tighten(p, n, raw['C'], raw['Q'], kind)
        return {'kind': kind, 'p': p, 'n': n, 'seed': seed, 'raw': raw['s'], 's': out['s'], 'iters': out['iters'],
                'secs_sim': round(t_sim, 1), 'secs_tight': round(time.time() - t0 - t_sim, 1), 'C': out['C'], 'Q': out['Q']}
    except Exception as e:
        return {'kind': kind, 'p': p, 'n': n, 'seed': seed, 'error': str(e)[:300], 'secs_sim': round(time.time() - t0, 1)}


def main():
    out_dir, p, nmax, minutes = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
    W = int(sys.argv[5]) if len(sys.argv) > 5 else os.cpu_count()
    deadline = time.time() + 60 * minutes
    os.makedirs(os.path.join(out_dir, 'best'), exist_ok=True)
    logf = open(os.path.join(out_dir, 'attempts.jsonl'), 'a')

    def log(d):
        logf.write(json.dumps({k: v for k, v in d.items() if k not in ('C', 'Q')}) + '\n'); logf.flush()

    best = {}
    b40 = engine.load_case(p, engine.NMAX)['best']
    best[engine.NMAX] = {'s': b40['s'], 'C': b40['C'], 'Q': b40['Q'], 'how': 'record'}
    # 1. crystal cuts for all n
    cuts = {}
    try:
        import crystal_cut
        t = time.time()
        bc, cutters = crystal_cut.search(p, nmax, nrand=80)
        for n in range(engine.NMAX + 1, nmax + 1):
            if bc[n][1] is None: continue
            s, C0, Q, s_est = crystal_cut.certify_cut(p, cutters, bc[n][1], n)
            cuts[n] = {'s': s, 'C': np.asarray(C0).tolist(), 'Q': Q}
        log({'kind': 'cutsearch', 'p': p, 'secs': round(time.time() - t, 1), 'cuts': {n: round(c['s'], 6) for n, c in cuts.items()}})
    except Exception as e:
        log({'kind': 'cutsearch', 'p': p, 'error': str(e)[:300]})

    def save(n):
        b = best[n]
        json.dump({'problem': p, 'n': n, 's': b['s'], 'how': b['how'], 'C': b['C'], 'Q': b['Q']},
                  open(os.path.join(out_dir, 'best', f'{p}_n{n:03d}.json'), 'w'))

    pool = mp.Pool(W)
    # 2. ascend chain (+ the tightened cut) for n = 41..nmax
    rng = random.Random(hash(p) & 0xffff)
    for n in range(engine.NMAX + 1, nmax + 1):
        if time.time() > deadline: break
        tasks = [('ascend', p, n, best[n - 1], rng.randrange(1, 2 ** 31 - 1)) for _ in range(max(1, W - (1 if n in cuts else 0)))]
        if n in cuts: tasks.append(('cut', p, n, cuts[n], 0))
        t = time.time(); res = pool.map(task, tasks)
        for r in res:
            log(r)
            if 'error' not in r and (n not in best or r['s'] < best[n]['s']):
                best[n] = {'s': r['s'], 'C': r['C'], 'Q': r['Q'], 'how': r['kind']}
        if n not in best: break
        log({'kind': 'step', 'p': p, 'n': n, 's': best[n]['s'], 'how': best[n]['how'], 'wall': round(time.time() - t, 1)})
        save(n)
    # 3. descend sweep
    pb = engine.problem(p)
    for n in sorted(best, reverse=True):
        if n - 1 in best and n - 1 > engine.NMAX:
            s0, i, C2, Q2 = engine.remove_one(pb, best[n]['C'], best[n]['Q'])[0]
            if s0 < best[n - 1]['s'] - 1e-9:
                log({'kind': 'descend', 'p': p, 'n': n - 1, 'from': best[n - 1]['s'], 's': s0})
                best[n - 1] = {'s': s0, 'C': C2, 'Q': Q2, 'how': 'descend'}; save(n - 1)
    # 4. hops at random n until the deadline
    ns = [n for n in best if n > engine.NMAX]
    while ns and time.time() < deadline - 300:
        batch = [('hop', p, n, best[n], rng.randrange(1, 2 ** 31 - 1)) for n in rng.sample(ns, min(W, len(ns)))]
        for r in pool.map(task, batch):
            r['before'] = best[r['n']]['s']; log(r)
            if 'error' not in r and r['s'] < best[r['n']]['s'] - 1e-9:
                best[r['n']] = {'s': r['s'], 'C': r['C'], 'Q': r['Q'], 'how': 'hop'}; save(r['n'])
    pool.terminate()
    log({'kind': 'done', 'p': p, 'n_done': max(best), 'secs': round(time.time() - (deadline - 60 * minutes))})


if __name__ == '__main__':
    main()
