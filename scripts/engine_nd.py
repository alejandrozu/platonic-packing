#!/usr/bin/env python3
"""Search engine for packings of regular polytopes in 4, 5 and 6 dimensions (15 Oct 2026; Alejandro: "generalize
the method for 4d 5d and 6d ... the regular polytopes in themselves and in their duals").

usage:  python3 scripts/engine_nd.py work <id>          one worker (archive: state/nd, or PP_STATE_ND)
        python3 scripts/engine_nd.py status             the table of best sizes
        python3 scripts/engine_nd.py check              archive invariants (monotone s(n), piece counts)
        python3 scripts/engine_nd.py export STATE REF   like remote.py export (cases of STATE/best better than REF)
        python3 scripts/engine_nd.py import BLOB HOST   decode an export and harvest it (every packing re-legalized)
        python3 scripts/engine_nd.py harvest DIR HOST   merge another archive's best tree

The engine is engine.py with the d-dimensional geometry of src/ndsim.py (soft-to-rigid simulation, legalization by
explicit separating hyperplanes) and src/ndslp.py (sequential-LP tightening). Archive: state/nd/best/<problem>/nNN.json
holds the best packing of each case in internal units (piece inradius 1/2; container {N_f . x <= L/2 off_f}; s =
container edge / piece edge): centres C (n x d) and rotation matrices R (n x d x d), plus statistics. Moves: fresh,
hop, reinsert, ascend, descend, tighten, perturb, as in engine.py. Every stored packing has passed legalization (each
near pair separated by a hyperplane with gap >= -1e-12); records are proven exactly by certify_nd.py."""
import json, os, sys, time, math, random, glob, contextlib, base64, gzip, tempfile
try:
    import fcntl
except ImportError:
    fcntl = None
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.append(os.path.join(ROOT, 'scripts'))      # appended: scripts/coverage.py must not shadow the package numba imports

STATE = os.environ.get('PP_STATE_ND') or os.path.join(ROOT, 'state', 'nd')
# 15 Oct 05:07 (Alejandro: "could we do all the permutations of the 4d 5d and 6d polytopes?"): every ordered pair of
# regular polytopes of the same dimension, piece in container: 6 x 6 in 4D, 3 x 3 in 5D and in 6D (54 problems);
# listed self packings first, then the dual pairs, then the rest
_ALL = {4: ['c5', 'c8', 'c16', 'c24', 'c120', 'c600'], 5: ['sx5', 'hc5', 'op5'], 6: ['sx6', 'hc6', 'op6']}
_DUAL = {'c5': 'c5', 'c8': 'c16', 'c16': 'c8', 'c24': 'c24', 'c120': 'c600', 'c600': 'c120', 'sx5': 'sx5', 'hc5': 'op5',
         'op5': 'hc5', 'sx6': 'sx6', 'hc6': 'op6', 'op6': 'hc6'}
PROBLEMS = []
for _d, _ps in _ALL.items():
    PROBLEMS += [(p, p) for p in _ps]
    PROBLEMS += [(p, _DUAL[p]) for p in _ps if _DUAL[p] != p]
    PROBLEMS += [(p, c) for p in _ps for c in _ps if c != p and c != _DUAL[p]]
KIND = {f'{p}in{c}': 'self' if p == c else 'dual' if _DUAL[p] == c else 'mixed' for p, c in PROBLEMS}
DIMS = {'c5': 4, 'c8': 4, 'c16': 4, 'c24': 4, 'c120': 4, 'c600': 4, 'sx5': 5, 'hc5': 5, 'op5': 5, 'sx6': 6, 'hc6': 6, 'op6': 6}
PID = {f'{p}in{c}': (p, c) for p, c in PROBLEMS}
DIM = {k: DIMS[v[0]] for k, v in PID.items()}
PID_INDEX = {p: i for i, p in enumerate(PID)}
NMIN = 2
NMAX_DIM = {4: 40, 5: 32, 6: 24}          # see docs/HIGHER_DIM.md (cost study, 15 Oct)
NMAX_ENV = os.environ.get('PP_ND_NMAX')


def nmax(p):
    return min(NMAX_DIM[DIM[p]], int(NMAX_ENV)) if NMAX_ENV else NMAX_DIM[DIM[p]]


POOL = 6
# symfresh (15 Oct 08:10): soft-to-rigid run constrained to central symmetry (pairs x, -x), then released; in a first
# test it beat 3 of 5 records (2 24-cells in a 24-cell: 1.8780 against 1.8856)
WEIGHTS = {'hop': 0.45, 'reinsert': 0.08, 'fresh': 0.10, 'symfresh': 0.20, 'ascend': 0.09, 'descend': 0.07, 'perturb': 0.08}
DISCOVERY, POLISH = ('fresh', 'symfresh', 'reinsert'), ('hop', 'tighten', 'perturb')
_pb = {}


def problem(p):
    if p not in _pb:
        import ndsim
        _pb[p] = ndsim.Problem(*PID[p])
    return _pb[p]


# ------------------------------------------------------------------ archive (as engine.py)
@contextlib.contextmanager
def locked():
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, '.lock'), 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(f, fcntl.LOCK_UN)


def _path(kind, p, n): return os.path.join(STATE, kind, p, f'n{n:02d}.json')


def _read(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return default


_RC = {}


def _read_cached(path):
    try: st = os.stat(path)
    except FileNotFoundError: _RC.pop(path, None); return None
    key = (st.st_mtime_ns, st.st_size); hit = _RC.get(path)
    if hit and hit[0] == key: return hit[1]
    obj = _read(path)
    if obj is not None: _RC[path] = (key, obj)
    return obj


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + f'.tmp{os.getpid()}'
    with open(tmp, 'w') as f: json.dump(obj, f, separators=(',', ':'))
    os.replace(tmp, path)


def load_case(p, n):
    c = _read(_path('best', p, n)) or {'problem': p, 'piece': PID[p][0], 'container': PID[p][1], 'dim': DIM[p], 'n': n,
                                         'best': None, 'stats': {}}
    st = c.setdefault('stats', {})
    for k, v in (('attempts', 0), ('effort', 0.0), ('improvements', 0), ('since', 0), ('last_improve', None),
                 ('needs_tighten', False), ('gaps', []), ('moves', {})):
        st.setdefault(k, v)
    return c


def save_case(c): _write(_path('best', c['problem'], c['n']), c)
def load_pool(p, n): return _read(_path('pool', p, n), [])
def save_pool(p, n, pool): _write(_path('pool', p, n), pool)


def rnd(C, R):
    return np.round(np.asarray(C, float), 15).tolist(), np.round(np.asarray(R, float), 15).tolist()


def distinct(a, b, edge):
    if abs(a['s'] - b['s']) > 1e-7: return True
    def fp(C):
        C = np.asarray(C); d = np.sqrt(((C[:, None] - C[None]) ** 2).sum(-1)); return np.sort(d[np.triu_indices(len(C), 1)])
    return float(np.abs(fp(a['C']) - fp(b['C'])).mean()) / edge > 0.02


def pool_insert(p, n, cand):
    pool = load_pool(p, n); edge = problem(p).edge
    for i, q in enumerate(pool):
        if not distinct(q, cand, edge):
            if cand['s'] < q['s']: pool[i] = cand
            break
    else:
        pool.append(cand)
    pool.sort(key=lambda q: q['s']); save_pool(p, n, pool[:POOL])


def remove_one(pb, C, R):
    """all single-piece removals ranked by the tight container of the rest (an LP each); [(s, i, C', R')]"""
    import ndsim
    C = np.asarray(C, float); R = np.asarray(R, float); out = []
    for i in range(len(C)):
        idx = [j for j in range(len(C)) if j != i]
        L, t = ndsim.tight_container(pb, C[idx], R[idx])
        out.append((pb.s_of_L(L), i, C[idx] + t, R[idx]))
    out.sort(key=lambda x: x[0])
    return out


def enforce_monotone(p, log=None):
    pb = problem(p); fixed = []
    for n in range(nmax(p) - 1, NMIN - 1, -1):
        up = load_case(p, n + 1)
        if not up['best']: continue
        cur = load_case(p, n)
        if cur['best'] and cur['best']['s'] <= up['best']['s']: continue
        s_up = up['best']['s']
        s_new, i, C2, R2 = remove_one(pb, up['best']['C'], up['best']['R'])[0]
        if s_new > s_up:
            keep = [j for j in range(n + 1) if j != i]
            C2 = np.asarray(up['best']['C'])[keep]; R2 = np.asarray(up['best']['R'])[keep]; s_new = s_up
        C2, R2 = rnd(C2, R2)
        cur['best'] = {'s': s_new, 'C': C2, 'R': R2, 'src': {'move': 'monotone', 'from_n': n + 1, 'removed': i},
                       't': time.time(), 'tightened': False}
        cur['stats']['needs_tighten'] = True
        save_case(cur); fixed.append(n)
        if log: log(f'monotone: {p} n={n} set to s={s_new:.10f} from n={n + 1} minus piece {i}')
    return fixed


# ------------------------------------------------------------------ one attempt
def tighten(pb, C, R, best_s, n, explore=False):
    import ndslp
    hist = []

    def abort(it, L):
        s = pb.s_of_L(L); hist.append(s)
        if best_s is None or it < 15: return False
        rate = max(0.0, (hist[-6] - s) / 5) if len(hist) >= 6 else 0.0
        return s - 150 * rate > best_s
    return ndslp.tighten(pb, C, R, tlimit=30 + 4 * n, reg=0.0 if explore else 1e-4, abort=abort)


def attempt(p, n, move, rng, log):
    import ndsim
    pb = problem(p); d = pb.d
    with locked():
        case = load_case(p, n); lo = load_case(p, n - 1) if n > NMIN else None; hi = load_case(p, n + 1) if n < nmax(p) else None
    best = case['best']; best_s = best['s'] if best else None
    seed = rng.randrange(1, 2 ** 31 - 1)
    t0 = time.time(); info = {'move': move, 'seed': seed}
    hopkw = dict(morph=4000 + 150 * n, settle=1000 + 25 * n)
    if move == 'symfresh':          # a symmetry group of the container: {I,-I}, {I,G}, {I,-I,G,-G}, {I,G1,G2,G1G2}
        kinds = ['central', 'mirror', 'klein', 'mirror2'] if n >= 4 else ['central', 'mirror']
        rng.shuffle(kinds); raw = None
        for kind in kinds + ['mirror']:
            raw = ndsim.symfresh(pb, n, seed, B=1.0 if n <= 16 else 0.7, kind=kind)
            if raw is not None: info['sym'] = kind; break
        if raw is None: move = info['move'] = 'fresh'
    if move == 'fresh':
        raw = ndsim.fresh(pb, n, seed, B=1.0 if n <= 16 else 0.7)
    elif move == 'symfresh':
        pass
    elif move in ('hop', 'reinsert'):
        pool = load_pool(p, n)
        start = best if (rng.random() < 0.6 or not pool) else rng.choice(pool)
        info['from'] = 'best' if start is best else 'pool'
        L = pb.L_of_s(start['s'])
        if move == 'hop':
            prm = dict(minDiff=math.exp(rng.uniform(math.log(0.04), math.log(0.6))), expand=rng.uniform(0.01, 0.05),
                       rh=rng.uniform(0.06, 0.2), focus=0 if (n < 8 or rng.random() >= 0.6) else rng.randint(3, max(4, n // 3)))
        else:
            k = rng.randint(1, 3 if n >= 12 else 2)
            prm = dict(remove=rng.sample(range(n), k), add=k, rh=rng.uniform(0.12, 0.25), expand=rng.uniform(0.0, 0.03))
        info.update({k: v for k, v in prm.items() if k in ('minDiff', 'expand', 'rh', 'focus', 'remove')})
        raw = ndsim.hop(pb, start['C'], start['R'], L, seed, **prm, **hopkw)
    elif move == 'ascend':
        src = lo['best']
        raw = ndsim.hop(pb, src['C'], src['R'], pb.L_of_s(src['s']), seed, add=1, rh=rng.uniform(0.15, 0.3),
                        expand=rng.uniform(0.0, 0.03), **hopkw)
    elif move == 'descend':
        s0, i, C2, R2 = rng.choice(remove_one(pb, hi['best']['C'], hi['best']['R'])[:3])
        raw = {'s': s0, 'C': C2, 'R': R2}; info['removed'] = i
    elif move == 'tighten':
        raw = {'s': best_s, 'C': best['C'], 'R': best['R']}
    elif move == 'perturb':
        e = math.exp(rng.uniform(math.log(0.003), math.log(0.05))); sg = e * rng.uniform(0.5, 0.9)
        C0 = np.array(best['C']); nr = np.random.default_rng(seed)
        raw = {'s': best_s * (1 + e), 'C': C0 * (1 + e) + nr.normal(0, sg, C0.shape), 'R': best['R']}
        info.update(expand=round(e, 4), sigma=round(sg, 4))
    else:
        raise ValueError(move)
    t_raw = time.time() - t0; s_raw = raw['s']
    gate = case['stats'].get('gate', 0.03)
    if move in ('fresh', 'symfresh'): gate = max(gate, 0.04)
    out = None
    if best is None or move in ('descend', 'tighten', 'perturb') or s_raw <= best_s * (1 + gate):
        out = tighten(pb, raw['C'], raw['R'], best_s, n, explore=(move == 'perturb'))
    secs = time.time() - t0; s_new = out['s'] if out else s_raw
    improved = False
    with locked():
        case = load_case(p, n); st = case['stats']; cur = case['best']
        st['attempts'] += 1; st['effort'] += secs
        mv = st['moves'].setdefault(move, [0, 0]); mv[0] += 1
        if out:
            st['gaps'] = (st['gaps'] + [max(0.0, s_raw / out['s'] - 1)])[-30:]
            g = sorted(st['gaps'])
            st['gate'] = float(min(0.08, max(0.006, 1.5 * g[int(0.8 * (len(g) - 1))]))) if len(g) >= 5 else 0.03
        if move == 'tighten': st['needs_tighten'] = False
        if out and (cur is None or out['s'] < cur['s'] - 1e-12):
            improved = True; mv[1] += 1
            C2, R2 = rnd(out['C'], out['R'])
            case['best'] = {'s': out['s'], 'C': C2, 'R': R2, 'src': dict(info, raw=s_raw), 't': time.time(), 'tightened': True}
            st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time(); st['fails'] = {}
            # a tightening stopped by its time limit is continued later (from this best, with a full time budget)
            st['needs_tighten'] = bool(out.get('timed_out'))
        else:
            st['since'] += 1
            cls = 'disc' if move in DISCOVERY else 'pol' if move in POLISH else 'nbr'
            st.setdefault('fails', {})[cls] = st.get('fails', {}).get(cls, 0) + 1
        save_case(case)
        if out:
            C2, R2 = rnd(out['C'], out['R'])
            pool_insert(p, n, {'s': out['s'], 'C': C2, 'R': R2, 'src': move, 't': time.time()})
        fixed = enforce_monotone(p, log) if improved or cur is None else []
    log(f"{p} n={n:2d} {move:8s} raw {s_raw:.6f}" + (f" -> {s_new:.10f}" if out else " (gated)") +
        f"  best {min(s_new, best_s) if best_s else s_new:.10f}{'  NEW BEST' if improved else ''}  {secs:.0f}s" +
        (f"  monotone-fixed {fixed}" if fixed else ''))
    with open(os.path.join(STATE, 'attempts.jsonl'), 'a') as f:
        f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': move, 'raw': s_raw, 's': s_new if out else None,
                            'best_before': best_s, 'improved': improved, 'secs': round(secs, 1), 'raw_secs': round(t_raw, 1)}) + '\n')
    return improved


# ------------------------------------------------------------------ scheduling (engine.py's rules, simplified)
def shard():
    v = os.environ.get('PP_SHARD')
    if not v: return None
    k, m = v.split('/'); return int(k), int(m)


def _claims():
    d = os.path.join(STATE, 'claims'); os.makedirs(d, exist_ok=True); out = []
    for f in os.listdir(d):
        try:
            pidn = int(open(os.path.join(d, f)).read().split()[0]); os.kill(pidn, 0); out.append(f)
        except Exception:
            with contextlib.suppress(Exception): os.remove(os.path.join(d, f))
    return out


@contextlib.contextmanager
def claim(p, n):
    f = os.path.join(STATE, 'claims', f'{p}|{n}')
    with locked():
        if f'{p}|{n}' in _claims(): yield False; return
        open(f, 'w').write(f'{os.getpid()}\n')
    try: yield True
    finally:
        with contextlib.suppress(Exception): os.remove(f)


def central_ok(p, n):
    """central-symmetry seeds apply: centrally symmetric container; odd n needs a centrally symmetric piece"""
    pc, cc = PID[p]; simplex = ('c5', 'sx5', 'sx6')
    return cc not in simplex and (n % 2 == 0 or pc not in simplex)


def sym_ok(p, n):
    return True                      # a mirror symmetry exists for every container (central symmetry: central_ok)


def known_optimal(p, n):
    """cases whose stored value is a proven optimum (no search needed): n hypercubes in a hypercube need s >= 2 for every
    n >= 2 (two unit cubes do not fit in a cube of side < 2), and the 2 x ... x 2 grid holds 2^d at s = 2"""
    pc, cc = PID[p]
    return pc == cc and pc in ('c8', 'hc5', 'hc6') and 2 <= n <= 2 ** DIM[p]


def active_problems():
    only = os.environ.get('PP_ND_PROBLEMS')
    return [p for p in PID if not only or p in only.split(',')]


_LEARN = {'t': 0, 'mult': {}}


def learned_multipliers():
    """engine.py's bandit: per dimension, the recent gain per CPU-second of each move (last ~3000 logged attempts of this
    archive, prior 1800 s at the dimension's average rate), as a multiplier in [0.4, 3] relative to the median move;
    refreshed every 5 minutes"""
    if time.time() - _LEARN['t'] < 300: return _LEARN['mult']
    _LEARN['t'] = time.time()
    try:
        with open(os.path.join(STATE, 'attempts.jsonl'), 'rb') as f:
            f.seek(0, 2); size = f.tell(); f.seek(max(0, size - 1_000_000)); lines = f.read().decode(errors='ignore').splitlines()[1:]
    except OSError:
        return _LEARN['mult']
    G, T = {}, {}
    for l in lines[-3000:]:
        try: r = json.loads(l)
        except ValueError: continue
        m = r.get('move'); p = r.get('p')
        if p not in DIM or m in ('harvest', 'tighten', None) or not r.get('best_before') or not r.get('secs'): continue
        k = (DIM[p], m)
        G[k] = G.get(k, 0.0) + (math.log(r['best_before'] / r['s']) if r.get('improved') and r.get('s') else 0.0)
        T[k] = T.get(k, 0.0) + r['secs']
    mult = {}
    for d in set(x for x, _ in T):
        ms = [m for x, m in T if x == d]
        tg = sum(G[(d, m)] for m in ms); tt = sum(T[(d, m)] for m in ms)
        base = tg / tt if tt else 0.0
        rate = {m: (G[(d, m)] + base * 1800) / (T[(d, m)] + 1800) for m in ms}
        med = sorted(rate.values())[len(rate) // 2]
        if med > 0: mult[d] = {m: min(3.0, max(0.4, v / med)) for m, v in rate.items()}
    _LEARN['mult'] = mult
    return mult


def total_remote(st):
    return st.get('attempts_remote', 0)


def choose(rng):
    """fill missing cases in ascending n (ascend from n-1), re-tighten flagged ones, then the case with the least
    effort per piece (favouring recently improved cases), and a move by the weights x case signals"""
    act = active_problems(); idx = {}
    for p in act:
        for n in range(NMIN, nmax(p) + 1): idx[(p, n)] = _read_cached(_path('best', p, n))
    order = list(act); rng.shuffle(order)
    sh = shard()
    if sh: order.sort(key=lambda p: 0 if PID_INDEX[p] % sh[1] == sh[0] else 1)
    claimed = {tuple(x.split('|')) for x in _claims()}
    for p in order:
        for n in range(NMIN, nmax(p) + 1):
            if idx[(p, n)] and idx[(p, n)].get('best'): continue
            if (p, str(n)) in claimed: break
            if n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best'): return p, n, 'ascend'
            if n < nmax(p) and idx[(p, n + 1)] and idx[(p, n + 1)].get('best'): return p, n, 'descend'
            return p, n, 'fresh'
    tq = [(p, n) for (p, n), c in idx.items() if c and c['stats'].get('needs_tighten') and (p, str(n)) not in claimed and not known_optimal(p, n)]
    if tq:                                       # flagged cases: own shard first (18 Actions jobs must not all re-tighten the same)
        rng.shuffle(tq)
        tq.sort(key=lambda k: 0 if not sh or PID_INDEX[k[0]] % sh[1] == sh[0] else 1)
        if not sh or PID_INDEX[tq[0][0]] % sh[1] == sh[0] or rng.random() < 0.15: return tq[0][0], tq[0][1], 'tighten'
    best_key, best_score = None, None
    for (p, n), c in idx.items():
        if (p, str(n)) in claimed or not c: continue
        if known_optimal(p, n) and c.get('best') and c['best']['s'] <= 2 + 1e-9: continue
        st = c['stats']
        # 15 Oct 08:20 (Alejandro: "many attempts at all the higher polytope cases"): equalize the NUMBER of attempts
        # per case (all machines), not the CPU time per piece -- with time per piece, n <= 8 had < 1 attempt on average
        # while n = 33-40 had 9; cases that keep failing (since) still fall back
        score = (st.get('attempts', 0) + total_remote(st) + 1) * (1 + st.get('since', 0) / 12) * rng.uniform(0.7, 1.3)
        if sh and PID_INDEX[p] % sh[1] != sh[0]: score *= 3     # sharded workers (Actions jobs) mostly keep to their own problems
        if best_score is None or score < best_score: best_key, best_score = (p, n), score
    if best_key is None: return None
    p, n = best_key; c = idx[(p, n)]; st = c['stats']
    if c['best']['src'].get('move') == 'monotone':
        r = rng.random()
        return p, n, 'ascend' if (n > NMIN and r < 0.4) else 'symfresh' if (sym_ok(p, n) and r < 0.75) else 'fresh'
    W = dict(WEIGHTS)
    for m, k in (learned_multipliers().get(DIM[p]) or {}).items():
        if m in W: W[m] *= k
    lo = idx.get((p, n - 1)); hi = idx.get((p, n + 1))
    t_self = st.get('last_improve') or 0
    if lo and lo.get('best') and (lo['stats'].get('last_improve') or 0) > t_self: W['ascend'] *= 2.0
    if hi and hi.get('best') and (hi['stats'].get('last_improve') or 0) > t_self: W['descend'] *= 1.5
    if st.get('since', 0) >= 6:
        f = st.get('fails') or {}
        damp, boost = (DISCOVERY, POLISH) if f.get('disc', 0) >= f.get('pol', 0) else (POLISH, DISCOVERY)
        for m in damp:
            if m in W: W[m] *= 0.4
        for m in boost:
            if m in W: W[m] *= 2.5
    moves = [(m, W[m]) for m in ('hop', 'reinsert', 'fresh', 'perturb')]
    if sym_ok(p, n): moves.append(('symfresh', W['symfresh']))
    if n > NMIN and lo and lo.get('best'): moves.append(('ascend', W['ascend']))
    if hi and hi.get('best'): moves.append(('descend', W['descend']))
    r = rng.random() * sum(w for _, w in moves)
    for m, w in moves:
        r -= w
        if r <= 0: return p, n, m
    return p, n, 'hop'


def work(wid):
    rng = random.Random(os.getpid() * 1000003 + int(time.time()))
    os.makedirs(os.path.join(ROOT, 'logs'), exist_ok=True)
    logf = open(os.path.join(ROOT, 'logs', f'engine_nd{wid}.log'), 'a')

    def log(msg):
        logf.write(time.strftime('%m-%d %H:%M:%S ') + msg + '\n'); logf.flush()
    log(f'nd worker {wid} started (pid {os.getpid()})')
    deadline = float(os.environ.get('PP_DEADLINE') or 0)
    while not os.path.exists(os.path.join(STATE, 'STOP')) and not (deadline and time.time() > deadline):
        ch = choose(rng)
        if ch is None: time.sleep(5); continue
        p, n, move = ch
        with claim(p, n) as ok:
            if not ok: time.sleep(0.5); continue
            try:
                attempt(p, n, move, rng, log)
            except Exception as e:
                import traceback
                log(f'ERROR {p} n={n} {move}: {type(e).__name__}: {str(e)[:300]} | {traceback.format_exc()[-600:]}')
                time.sleep(2)
    log('stopping')


# ------------------------------------------------------------------ harvest / export (remote workers, Actions)
def harvest(src_dir, host):
    """merge another archive's best tree; every candidate is re-legalized here (scaled apart until every near pair
    has a separating hyperplane, then the tight container), so a corrupt file cannot enter the archive"""
    import ndsim
    taken = []
    for p in PID:
        pb = problem(p)
        for n in range(NMIN, nmax(p) + 1):
            c = _read(os.path.join(src_dir, p, f'n{n:02d}.json'))
            b = c and c.get('best')
            if not b or len(b.get('C', [])) != n: continue
            cur = load_case(p, n)['best']
            if cur and b['s'] >= cur['s'] - 1e-12: continue
            C = np.array(b['C'], float); R = np.array(b['R'], float)
            if C.shape != (n, pb.d) or R.shape != (n, pb.d, pb.d): continue
            R = np.array([np.linalg.qr(r)[0] * np.sign(np.diag(np.linalg.qr(r)[1])) for r in R])   # exactly orthogonal (float)
            if any(np.linalg.det(r) < 0 for r in R): continue
            lg = ndsim.legalize(pb, C, R)
            s = lg['s']
            with locked():
                case = load_case(p, n); cur = case['best']
                if cur and s >= cur['s'] - 1e-12: continue
                C2, R2 = rnd(lg['C'], lg['R'])
                case['best'] = {'s': s, 'C': C2, 'R': R2, 'src': dict(b.get('src') or {}, host=host), 't': time.time(), 'tightened': True}
                st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time()
                st['needs_tighten'] = False              # a harvested packing was tightened where it was found
                save_case(case)
                pool_insert(p, n, {'s': s, 'C': C2, 'R': R2, 'src': 'harvest', 't': time.time()})
                enforce_monotone(p, print)
                with open(os.path.join(STATE, 'attempts.jsonl'), 'a') as f:
                    f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': 'harvest', 'raw': b['s'], 's': s,
                                        'best_before': cur['s'] if cur else None, 'improved': True, 'secs': 0, 'raw_secs': 0, 'host': host}) + '\n')
            taken.append(f'{p}{n}:{s:.4f}')
    print(f'nd harvest from {host}: {len(taken)} improvements ' + ' '.join(taken))
    return taken


def export(state, ref):
    out = {}
    for f in glob.glob(os.path.join(state, 'best', '*', 'n[0-9]*.json')):
        p, nn = f.split(os.sep)[-2], os.path.basename(f)
        try:
            b = json.load(open(f)).get('best')
            rf = os.path.join(ref, p, nn)
            r = json.load(open(rf)).get('best') if os.path.exists(rf) else None
        except (json.JSONDecodeError, OSError):
            continue
        if b and (r is None or b['s'] < r['s'] - 1e-12):
            out.setdefault(p, {})[nn] = {'best': {k: b[k] for k in ('s', 'C', 'R', 'src') if k in b}}
    counts = {}
    ap = os.path.join(state, 'attempts.jsonl')
    for l in (open(ap).read().splitlines() if os.path.exists(ap) else []):
        try: a = json.loads(l)
        except json.JSONDecodeError: continue
        if a.get('move') == 'harvest': continue
        k = f"{a['p']}:{a['n']}"; counts[k] = counts.get(k, 0) + 1
    out['_totals'] = counts
    mv = {}                                  # per dimension and move: attempts, improvements, CPU seconds (for steering)
    for l in (open(ap).read().splitlines() if os.path.exists(ap) else []):
        try: a = json.loads(l)
        except json.JSONDecodeError: continue
        if a.get('move') == 'harvest' or a.get('p') not in DIM: continue
        k = f"{DIM[a['p']]}:{a['move']}"; r = mv.setdefault(k, [0, 0, 0.0]); r[0] += 1; r[1] += bool(a.get('improved')); r[2] += a.get('secs', 0)
    out['_moves'] = mv
    blob = base64.b64encode(gzip.compress(json.dumps(out, separators=(',', ':')).encode())).decode()
    print(f'EXPORT {sum(len(v) for k, v in out.items() if not k.startswith("_"))} {blob}')


def do_import(blobfile, host):
    txt = open(blobfile).read().strip()
    if txt.startswith('EXPORT'): txt = txt.split(None, 2)[2] if len(txt.split(None, 2)) > 2 else ''
    data = json.loads(gzip.decompress(base64.b64decode(txt))) if txt else {}
    totals = data.pop('_totals', {})
    moves = data.pop('_moves', None)
    if moves:
        with open(os.path.join(STATE, 'actions_moves.jsonl'), 'a') as f:
            f.write(json.dumps({'t': round(time.time()), 'host': host, 'moves': moves}) + '\n')
    if totals:
        with locked():
            for key, k in totals.items():
                p, n = key.split(':'); n = int(n)
                if p not in PID: continue
                c = load_case(p, n)
                if not c.get('best'): continue
                c['stats']['attempts_remote'] = c['stats'].get('attempts_remote', 0) + int(k); save_case(c)
    with tempfile.TemporaryDirectory() as d:
        for p, cases in data.items():
            os.makedirs(os.path.join(d, p), exist_ok=True)
            for nn, c in cases.items(): json.dump(c, open(os.path.join(d, p, nn), 'w'))
        return harvest(d, host)


def seed():
    """Exact constructions as starting records (15 Oct): k x ... x k grids of hypercubes in a hypercube (k = 2 in 4, 5
    and 6 dimensions, k = 3 in 4 dimensions), trimmed to nmax by the best LP removals; monotonicity then gives s = 2
    for every n <= 2^d (the 14 Oct benchmark: random starts did not find the grid at n = 16-32 in 5D and 6D)."""
    import itertools, ndsim
    n_new = 0
    for d, hc, ks in ((4, 'c8', (2, 3)), (5, 'hc5', (2,)), (6, 'hc6', (2,))):
        p = f'{hc}in{hc}'; pb = problem(p)
        for k in ks:
            C = np.array(list(itertools.product(range(k), repeat=d)), float) - (k - 1) / 2
            R = np.array([np.eye(d)] * len(C))
            while len(C) > nmax(p):
                _, i, C, R = remove_one(pb, C, R)[0]
            lg = ndsim.legalize(pb, C, R); n = len(C)
            with locked():
                case = load_case(p, n)
                if not case['best'] or lg['s'] < case['best']['s'] - 1e-12:
                    C2, R2 = rnd(lg['C'], lg['R'])
                    case['best'] = {'s': lg['s'], 'C': C2, 'R': R2, 'src': {'move': 'construction', 'name': f'{k}^{d} grid'},
                                    't': time.time(), 'tightened': True}
                    save_case(case); n_new += 1
                    pool_insert(p, n, {'s': lg['s'], 'C': C2, 'R': R2, 'src': 'construction', 't': time.time()})
                enforce_monotone(p, print)
            print(f'{p}: {k}^{d} grid -> n = {n}, s = {lg["s"]:.10f}')
    # lattice cuts: hypercubes and 24-cells in every container of their dimension
    for p in PID:
        if PID[p][0] not in LATTICE: continue
        pb = problem(p); cuts = lattice_cuts(p); took = []
        for n, (L, X, Q) in sorted(cuts.items()):
            cur = load_case(p, n)['best']
            if cur and pb.s_of_L(L) >= cur['s'] - 1e-9: continue
            lg = ndsim.legalize(pb, X, np.array([Q] * n))
            with locked():
                case = load_case(p, n)
                if case['best'] and lg['s'] >= case['best']['s'] - 1e-12: continue
                C2, R2 = rnd(lg['C'], lg['R'])
                case['best'] = {'s': lg['s'], 'C': C2, 'R': R2, 'src': {'move': 'latcut'}, 't': time.time(), 'tightened': False}
                case['stats']['needs_tighten'] = True
                save_case(case); n_new += 1; took.append(f'{n}:{lg["s"]:.4f}')
                pool_insert(p, n, {'s': lg['s'], 'C': C2, 'R': R2, 'src': 'latcut', 't': time.time()})
        with locked(): enforce_monotone(p)
        print(f'{p}: lattice cuts {len(took)} cases ' + ' '.join(took[:12]))
    print(f'seeded {n_new} cases')


LATTICE = {'c8': 'Z', 'hc5': 'Z', 'hc6': 'Z', 'c24': 'F4'}     # pieces whose translates by a lattice tile space


def lattice_cuts(p, rots=8, offsets=60, seed=1):
    """Best cut of a lattice tiling by the container, for every n (the 3D crystal cuts of 14 Oct, for the pieces that
    tile d-space by translations: hypercubes on Z^d, the 24-cell on the F4 lattice). For random rotations Q (and Q = I)
    and offsets t, every lattice cell Q(z + P) + t needs the container size L_z = max_f 2 (N_f.x + h_QP(N_f)) / off_f;
    the n-th smallest L_z is the cut's size for n pieces. Returns {n: (L, centres, Q)}."""
    import itertools
    pb = problem(p); d = pb.d; piece = PID[p][0]
    if piece not in LATTICE: return {}
    if LATTICE[piece] == 'Z': B = np.eye(d)
    else: B = np.vstack([np.eye(4)[:3], np.full(4, 0.5)])          # F4 = D4*: e_1, e_2, e_3, (1,1,1,1)/2 (internal units)
    rng = np.random.default_rng(seed)
    N = pb.CN; off = pb.off
    best = {}
    k = int(np.ceil(1.3 * nmax(p) ** (1 / d))) + 2
    Z = np.array(list(itertools.product(range(-k, k + 1), repeat=d)), float) @ B
    Z = Z[np.linalg.norm(Z, axis=1) <= k + 0.5]
    import ndsim
    Qs = [np.eye(d)] + [ndsim.random_rotation(rng, d) for _ in range(rots)]
    # only lattice points that can lie in the container of the n = nmax cut at Q = I, t = 0 (plus a margin) matter
    h0 = (N @ pb.V.T).max(1)
    L0 = np.sort((2 * (Z @ N.T + h0[None, :]) / off[None, :]).max(1))[min(nmax(p), len(Z)) - 1]
    Z = Z[np.linalg.norm(Z, axis=1) <= (L0 / 2) * pb.Ccirc / pb.rhoC + 2 * pb.circ + 1.0]
    for qi, Q in enumerate(Qs):
        h = (N @ Q @ pb.V.T).max(1)                                   # support of Q P in the facet normals
        X0 = Z @ Q.T
        for ti in range(offsets):
            t = (rng.random(d) - 0.5) @ B @ Q.T if ti else np.zeros(d)
            X = X0 + t
            Lz = (2 * (X @ N.T + h[None, :]) / off[None, :]).max(1)
            order = np.argsort(Lz)
            for n in range(NMIN, min(nmax(p), len(order)) + 1):
                L = Lz[order[n - 1]]
                if n not in best or L < best[n][0] - 1e-12: best[n] = (L, X[order[:n]].copy(), Q)
    return best


def table():
    lines = []
    for p in PID:
        row = []
        for n in range(NMIN, nmax(p) + 1):
            c = _read(_path('best', p, n))
            row.append(f"{n}:{c['best']['s']:.5f}" if c and c.get('best') else f'{n}:-')
        lines.append(f'{p}  ' + ' '.join(row))
    return '\n'.join(lines)


def check():
    bad = 0
    for p in PID:
        prev = None
        for n in range(NMIN, nmax(p) + 1):
            c = _read(_path('best', p, n))
            if not c or not c.get('best'): prev = None; continue
            if len(c['best']['C']) != n: print('wrong piece count', p, n); bad += 1
            if prev is not None and prev > c['best']['s']: print('NOT MONOTONE', p, n - 1, prev, '>', n, c['best']['s']); bad += 1
            prev = c['best']['s']
    print('nd archive check:', 'ok' if not bad else f'{bad} problems')
    return bad


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'work': work(sys.argv[2] if len(sys.argv) > 2 else '0')
    elif cmd == 'status': print(table())
    elif cmd == 'seed': seed()
    elif cmd == 'check': sys.exit(1 if check() else 0)
    elif cmd == 'harvest': harvest(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'remote')
    elif cmd == 'export': export(sys.argv[2], sys.argv[3])
    elif cmd == 'import': do_import(sys.argv[2], sys.argv[3])
