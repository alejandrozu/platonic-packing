#!/usr/bin/env python3
"""Tighten the best raw runs for every (piece, container, n), keep the best certified result, write claim files,
and run both checkers on them.

usage: python3 scripts/pipeline.py tighten [K=4] [piece,piece,...]     # tighten up to K distinct best runs per case
       python3 scripts/pipeline.py descend [piece,piece,...]            # n-packings from (n+1)-packings minus one piece
       python3 scripts/pipeline.py claims                               # best tightened result -> claims/, verify + certify
Tightened results are cached in results/tight.jsonl (one line per (piece, container, n, mode, B, seed))."""
import json, glob, os, sys, time, subprocess, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
import exact, claim

TIGHT = os.path.join(ROOT, 'results', 'tight.jsonl')
TIGHT_SLP = os.path.join(ROOT, 'results', 'tight_slp.jsonl')    # fast sequential-LP screen (also valid results)
AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico'}


def wanted(only, piece, container):
    """only: None, or a set of piece names and/or problem ids like 'tetintet'."""
    return only is None or piece in only or f'{AB[piece]}in{AB[container]}' in only
os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)


def load_runs():
    rows = [json.loads(l) for f in glob.glob(os.path.join(ROOT, 'runs', '*', '*.jsonl')) for l in open(f) if l.strip()]
    by = collections.defaultdict(list)
    for r in rows: by[(r['piece'], r['container'], r['n'])].append(r)
    return by


def load_tight(path=None):
    out = {}
    for fn in ([path] if path else [TIGHT, TIGHT_SLP]):
        if not os.path.exists(fn): continue
        for l in open(fn):
            if l.strip():
                e = json.loads(l); k = (e['piece'], e['container'], e['n'], e['mode'], e['B'], e['seed'])
                if k not in out or e['s'] < out[k]['s']: out[k] = e
    return out


def tighten(K=2, only=None, tlimit=600, screen=6):
    """Per case: SLP-tighten the `screen` best distinct raw runs (cheap), then SLSQP-tighten the K most promising
    by their SLP value (from the raw configuration). Every result is a certified packing; the best one wins."""
    by = load_runs()
    done_slp, done = load_tight(TIGHT_SLP), load_tight(TIGHT)
    fs, f = open(TIGHT_SLP, 'a'), open(TIGHT, 'a')
    for key in sorted(by, key=lambda k: (k[2], k[0])):
        if not wanted(only, key[0], key[1]): continue
        rows = sorted(by[key], key=lambda r: r['s'])
        picked = []
        for r in rows:   # distinct raw values (different arrangements usually give different sides)
            if all(abs(r['s'] - p['s']) > 1e-7 for p in picked): picked.append(r)
            if len(picked) >= screen: break
        scored = []
        for r in picked:
            tk = (r['piece'], r['container'], r['n'], r['mode'], r['B'], r['seed'])
            if tk not in done_slp:
                t0 = time.time(); out = exact.tighten_run(r, tlimit=120, method='slp', slp_floor=1e-6); out['secs'] = round(time.time() - t0, 1)
                out['tmethod'] = 'slp'; fs.write(json.dumps(out) + '\n'); fs.flush(); done_slp[tk] = out
                print(f"{key[0]:13s} in {key[1]:12s} n={key[2]:2d} seed={r['seed']:3d} raw {r['s']:.9f} -> SLP {out['s']:.12f} ({out['secs']}s)", flush=True)
            scored.append((done_slp[tk]['s'], r))
        scored.sort(key=lambda t: t[0])
        for _, r in scored[:K]:
            tk = (r['piece'], r['container'], r['n'], r['mode'], r['B'], r['seed'])
            if tk in done: continue
            t0 = time.time(); out = exact.tighten_run(r, tlimit=tlimit); out['secs'] = round(time.time() - t0, 1)
            out['tmethod'] = 'slsqp'; f.write(json.dumps(out) + '\n'); f.flush(); done[tk] = out
            print(f"{key[0]:13s} in {key[1]:12s} n={key[2]:2d} seed={r['seed']:3d} raw {r['s']:.9f} -> SLSQP {out['s']:.12f} ({out['secs']}s)", flush=True)


def best_tight():
    best = {}
    for e in load_tight().values():
        k = (e['piece'], e['container'], e['n'])
        if k not in best or e['s'] < best[k]['s']: best[k] = e
    return best


def descend(only=None, tlimit=300, keep=3, slack=0.02):
    """Removing a piece from a valid (n+1)-packing leaves a valid n-packing. For every case, take the best tightened
    (n+1)-packing, rank the n+1 removals by the size of the tightest container for the remaining pieces (an LP), and
    re-tighten the `keep` best removals whose size is within `slack` of (or below) the current best for n."""
    import numpy as np
    done = load_tight(TIGHT); f = open(TIGHT, 'a')
    cases = sorted({(k[0], k[1]) for k in best_tight()})
    for piece, container in cases:
        if not wanted(only, piece, container): continue
        pb = exact.Problem(piece, container)
        ns = sorted(n for (p, c, n) in best_tight() if (p, c) == (piece, container))
        for n in reversed(ns[:-1]):
            best = best_tight()
            parent, cur = best.get((piece, container, n + 1)), best.get((piece, container, n))
            if parent is None: continue
            C = np.array(parent['C']); R = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in parent['Q']]
            cand = []
            for i in range(n + 1):
                idx = [j for j in range(n + 1) if j != i]
                L, t = exact.tight_container(pb, C[idx], [R[j] for j in idx])
                cand.append((pb.s_of_L(L), i))
            cand.sort()
            screened = []
            for s0, i in cand[:keep]:
                if cur is not None and s0 > cur['s'] * (1 + slack): break
                seed = int(parent['seed']) * 1000 + i if parent['mode'] != 'descend' else int(parent['seed']) % 10 ** 9 * 100 + i
                tk = (piece, container, n, 'descend', parent['B'], seed)
                if tk in done: continue
                idx = [j for j in range(n + 1) if j != i]
                row = dict(piece=piece, container=container, n=n, seed=seed, mode='descend', B=parent['B'],
                           C=C[idx].tolist(), Q=[parent['Q'][j] for j in idx])
                t0 = time.time(); out = exact.tighten_run(row, tlimit=120, method='slp', slp_floor=1e-6)
                out['secs'] = round(time.time() - t0, 1); out['parent'] = [n + 1, parent['mode'], parent['seed'], i]; out['tmethod'] = 'slp'
                screened.append((out['s'], row, out, tk))
                print(f"{piece:13s} n={n:2d} from n+1 (seed {parent['seed']}) minus piece {i}: {s0:.9f} -> SLP {out['s']:.12f}"
                      f"  (best was {cur['s'] if cur else float('nan'):.12f}) {out['secs']}s", flush=True)
            screened.sort(key=lambda t: t[0])
            for k_, (sv, row, out, tk) in enumerate(screened):
                if k_ == 0 and (cur is None or sv < cur['s'] + 1e-3):      # polish the most promising removal
                    t0 = time.time(); out2 = exact.tighten_run(row, tlimit=tlimit)
                    if out2['s'] < out['s']:
                        out2.update(parent=out['parent'], tmethod='slsqp'); out2['secs'] = round(time.time() - t0, 1); out = out2
                    print(f"{'':13s} n={n:2d}   polished -> {out['s']:.12f}", flush=True)
                f.write(json.dumps(out) + '\n'); f.flush(); done[tk] = out


def claims():
    best = {}
    for e in load_tight().values():
        k = (e['piece'], e['container'], e['n'])
        if k not in best or e['s'] < best[k]['s']: best[k] = e
    summary = []
    for k in sorted(best, key=lambda k: (k[0], k[2])):
        e = best[k]
        d = os.path.join(ROOT, 'claims', f'{k[0]}_in_{k[1]}'); os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, f'n{k[2]:02d}.json')
        c = claim.make_claim(e, meta={'seed': e['seed'], 'search_mode': e['mode'], 'budget': e['B']})
        json.dump(c, open(fn, 'w'), indent=1)
        v = subprocess.run([sys.executable, os.path.join(ROOT, 'verify.py'), fn], capture_output=True, text=True)
        x = subprocess.run([sys.executable, os.path.join(ROOT, 'certify_exact.py'), fn], capture_output=True, text=True)
        open(fn.replace('.json', '.verify.txt'), 'w').write(v.stdout)
        open(fn.replace('.json', '.certify.txt'), 'w').write(x.stdout)
        ok = v.returncode == 0 and x.returncode == 0
        summary.append(dict(piece=k[0], container=k[1], n=k[2], s_tight=e['s'], s_full=c['s_full'], seed=e['seed'],
                            mode=e['mode'], B=e['B'], verified=v.returncode == 0, certified=x.returncode == 0,
                            file=os.path.relpath(fn, ROOT)))
        print(f"{k[0]:13s} n={k[2]:2d}  tight {e['s']:.12f}  claim {c['s_full']:.13f}  {'CERTIFIED' if ok else 'FAILED'}", flush=True)
    json.dump(summary, open(os.path.join(ROOT, 'results', 'summary.json'), 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == 'descend':
        descend(set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None)
    elif sys.argv[1] == 'tighten':
        K = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None
        tighten(K, only)
    else:
        claims()
