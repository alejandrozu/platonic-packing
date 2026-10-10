#!/usr/bin/env python3
"""Autonomous search engine: anytime basin hopping over all problems and n, with a monotone archive.

usage:  python3 scripts/engine.py seed            # import earlier results + lattice constructions (idempotent)
        python3 scripts/engine.py work <id>       # one worker (run two, see scripts/run_forever.sh)
        python3 scripts/engine.py status          # print the current table
        python3 scripts/engine.py check           # verify the archive invariants (monotone s(n), files readable)

Archive: state/best/<problem>/nNN.json = best packing found (internal units of src/sim.js / src/exact.py: piece
inradius 1/2, container {N_f . x <= L/2} centred at the origin; s = container edge / piece edge) plus statistics;
state/pool/<problem>/nNN.json = up to POOL distinct good packings (starting points for hops). Writes are atomic
(write + rename) under a global file lock, so workers can run concurrently and be killed at any time.

Moves (per attempt, one case (problem, n)):
  fresh     full soft-to-rigid run from random balls (Nakajima's schedule)
  hop       from the best (or a pool member): expand, soften, shake until the relative arrangement of the pieces
            has changed by >= minDiff piece edges (all pieces, or a local cluster), re-sharpen under pressure
  reinsert  remove 1-3 random pieces and put them back into the largest holes, re-sharpen
  ascend    from the best (n-1)-packing: add one piece in the largest hole, re-sharpen
  descend   from the best (n+1)-packing: remove the piece whose removal shrinks the container most (LP), tighten
  tighten   re-tighten the current best (after it was set by the monotone rule)
A raw result is tightened (sequential LP, then SLSQP polish for small n) only if it is within the case's gate of
the best; hopeless tightenings are abandoned early. Every accepted packing has passed legalization (no overlap at
tolerance 1e-12 by the separating-axis test); records add clearance and are proven by certify_exact.py.

Monotonicity invariant (enforced after every change of a best): s(n) <= s(n+1) for every problem. If it fails, the
(n+1)-packing minus one piece is stored as the n-packing (same container, so its size can only drop); the case is
then flagged for re-tightening.
"""
import json, os, sys, time, math, random, fcntl, subprocess, signal, glob, hashlib, contextlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import exact

STATE = os.path.join(ROOT, 'state')
AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico'}
PROBLEMS = [('tetrahedron', 'tetrahedron'), ('octahedron', 'octahedron'), ('icosahedron', 'icosahedron'),
            ('dodecahedron', 'dodecahedron'), ('cube', 'cube'), ('cube', 'octahedron'), ('octahedron', 'cube'),
            ('dodecahedron', 'icosahedron'), ('icosahedron', 'dodecahedron')]
NMIN, NMAX, POOL = 2, 40, 6

# Hop settings. A variant overrides some of HOP_DEFAULT (ranges are sampled uniformly, minDiff log-uniformly).
# state/policy.json selects what the workers do (re-read before every attempt, so no restart is needed):
#   {"mode": "experiment", "variants": [...], "weights": {...}}  every hop draws a variant uniformly at random
#   {"mode": "production", "hop_variant": "<name>", "weights": {...}}
# weights = relative probabilities of hop / reinsert / fresh / ascend / descend for an ordinary case.
HOP_DEFAULT = dict(minDiff=(0.04, 0.6), expand=(0.01, 0.05), rh=(0.06, 0.2), noise=0.004, shake=400, morph_mult=1.0,
                   from_best=0.6, focus_p=0.6, nraw=1)
VARIANTS = {
    'base': {},                                                       # the settings used until 10 Oct 19:20
    'jiggle': dict(noise=0.012, shake=600),                           # shake 3x harder and 1.5x longer
    'expand': dict(expand=(0.06, 0.15), rh=(0.12, 0.3), morph_mult=1.3),  # let the container grow 6-15% first
    'volume': dict(nraw=3),                                           # 3 raw hops, tighten only the best one
    'gentle': dict(minDiff=(0.02, 0.10), expand=(0.005, 0.03), from_best=0.9),  # small hops from the best
}
WEIGHTS = {'hop': 0.55, 'reinsert': 0.12, 'fresh': 0.13, 'ascend': 0.10, 'descend': 0.10}


def policy():
    return _read(os.path.join(STATE, 'policy.json'), {}) or {}


def pid(piece, container): return f'{AB[piece]}in{AB[container]}'


def lineage_of(x):
    """Published packing a packing descends from (archive src dict or pool entry), for attribution."""
    if not isinstance(x, dict): return None
    if x.get('move') == 'literature' or x.get('src') == 'literature': return x.get('source') or x.get('lineage')
    return x.get('lineage')


PID = {pid(p, c): (p, c) for p, c in PROBLEMS}
_pb_cache = {}


def problem(p):
    if p not in _pb_cache: _pb_cache[p] = exact.Problem(*PID[p])
    return _pb_cache[p]


# ------------------------------------------------------------------ archive
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


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + f'.tmp{os.getpid()}'
    with open(tmp, 'w') as f: json.dump(obj, f, separators=(',', ':'))
    os.replace(tmp, path)


def load_case(p, n):
    c = _read(_path('best', p, n)) or {'problem': p, 'piece': PID[p][0], 'container': PID[p][1], 'n': n, 'best': None,
                                         'stats': {}}
    st = c.setdefault('stats', {})
    for k, v in (('attempts', 0), ('effort', 0.0), ('improvements', 0), ('since', 0), ('last_improve', None),
                 ('needs_tighten', False), ('gaps', []), ('moves', {})):
        st.setdefault(k, v)
    return c


def save_case(c): _write(_path('best', c['problem'], c['n']), c)
def load_pool(p, n): return _read(_path('pool', p, n), [])
def save_pool(p, n, pool): _write(_path('pool', p, n), pool)


def fingerprint(C):
    C = np.asarray(C); d = np.sqrt(((C[:, None, :] - C[None, :, :]) ** 2).sum(-1))
    return np.sort(d[np.triu_indices(len(C), 1)])


def distinct(a, b, edge):
    """Two packings of the same case are 'the same basin' if their sorted centre-distance lists agree to 0.02 edges
    on average and their sizes agree to 1e-7."""
    if abs(a['s'] - b['s']) > 1e-7: return True
    fa, fb = fingerprint(a['C']), fingerprint(b['C'])
    return float(np.abs(fa - fb).mean()) / edge > 0.02


def pool_insert(p, n, cand):
    pool = load_pool(p, n)
    edge = problem(p).edge
    for i, q in enumerate(pool):
        if not distinct(q, cand, edge):
            if cand['s'] < q['s']: pool[i] = cand
            break
    else:
        pool.append(cand)
    pool.sort(key=lambda q: q['s'])
    save_pool(p, n, pool[:POOL])


def remove_one(pb, C, Q, exclude=None):
    """All single-piece removals ranked by the size of the tightest container for the remaining pieces (an LP).
    Returns [(s, i, C', Q')]; the remaining pieces keep their places, so every s here is <= the parent's s."""
    C = np.asarray(C); R = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in Q]
    out = []
    for i in range(len(C)):
        idx = [j for j in range(len(C)) if j != i]
        L, t = exact.tight_container(pb, C[idx], [R[j] for j in idx])
        out.append((pb.s_of_L(L), i, (C[idx] + t).tolist(), [Q[j] for j in idx]))
    out.sort(key=lambda x: x[0])
    return out


def enforce_monotone(p, log=None):
    """Make s(n) <= s(n+1) hold for every n of problem p (call under the lock). Returns the list of fixed n."""
    pb = problem(p); fixed = []
    for n in range(NMAX - 1, NMIN - 1, -1):
        up = load_case(p, n + 1)
        if not up['best']: continue
        cur = load_case(p, n)
        if cur['best'] and cur['best']['s'] <= up['best']['s']: continue
        s_up = up['best']['s']
        cand = remove_one(pb, up['best']['C'], up['best']['Q'])[0]
        s_new, i, C2, Q2 = cand
        if s_new > s_up:                         # float noise in the LP: keep the parent's container exactly
            keep = [j for j in range(n + 1) if j != i]
            C2 = [up['best']['C'][j] for j in keep]; Q2 = [up['best']['Q'][j] for j in keep]; s_new = s_up
        lin = lineage_of(up['best'].get('src'))
        cur['best'] = {'s': s_new, 'C': C2, 'Q': Q2, 'src': {'move': 'monotone', 'from_n': n + 1, 'removed': i, **({'lineage': lin} if lin else {})},
                       't': time.time(), 'tightened': False}
        cur['stats']['needs_tighten'] = True
        save_case(cur); fixed.append(n)
        if log: log(f'monotone: {p} n={n} set to s={s_new:.10f} from n={n + 1} minus piece {i}')
    return fixed


# ------------------------------------------------------------------ compute server (node)
class Sim:
    def __init__(self):
        self.p = None; self.start()

    def start(self):
        if self.p:
            with contextlib.suppress(Exception): self.p.kill()
        self.p = subprocess.Popen(['node', os.path.join(ROOT, 'src', 'server.js')], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1)

    def call(self, msg):
        for attempt in range(2):
            try:
                self.p.stdin.write(json.dumps(msg) + '\n'); self.p.stdin.flush()
                line = self.p.stdout.readline()
                if not line: raise RuntimeError('server closed')
                out = json.loads(line)
                if 'error' in out: raise RuntimeError(out['error'][:500])
                return out
            except (BrokenPipeError, RuntimeError, json.JSONDecodeError):
                if attempt: raise
                self.start()


# ------------------------------------------------------------------ one attempt
def tighten(row, best_s, n, gate):
    """Sequential-LP tightening with an optimistic early abort, SLSQP polish for small n when it wins."""
    hist = []

    def abort(it, L):
        s = problem(row['problem']).s_of_L(L); hist.append(s)
        if best_s is None or it < 15: return False
        rate = max(0.0, (hist[-6] - s) / 5) if len(hist) >= 6 else 0.0
        return s - 150 * rate > best_s                       # even 150 more rounds at this rate cannot win

    out = exact.tighten_run(row, tlimit=30 + 4 * n, method='slp', slp_floor=1e-6, abort=abort)
    if n <= 14 and (best_s is None or out['s'] < best_s + 1e-9):
        row2 = dict(row, C=out['C'], Q=out['Q'])
        out2 = exact.tighten_run(row2, tlimit=60 + 6 * n)
        if out2['s'] < out['s']: out = out2
    return out


def attempt(sim, p, n, move, rng, log, vname='base'):
    piece, container = PID[p]
    pb = problem(p)
    V = dict(HOP_DEFAULT, **VARIANTS.get(vname, {}))
    with locked():
        case = load_case(p, n); lo = load_case(p, n - 1) if n > NMIN else None; hi = load_case(p, n + 1) if n < NMAX else None
    best = case['best']; best_s = best['s'] if best else None
    seed = rng.randrange(1, 2 ** 31 - 1)
    t0 = time.time(); info = {'move': move, 'seed': seed, 'var': vname}; lin = None
    base = dict(op='hop', piece=piece, container=container, seed=seed)
    if move == 'fresh':
        B = 1.0 if n <= 16 else 0.7
        raw = sim.call(dict(op='fresh', piece=piece, container=container, n=n, seed=seed, mode='improved', anneal=True,
                            compact=int(5000 * B), morph=int(45000 * B), settle=int(3000 * B)))
    elif move in ('hop', 'reinsert'):
        pool = load_pool(p, n)
        raw = None
        for k_raw in range(V['nraw'] if move == 'hop' else 1):       # 'volume': several raw hops, keep the best
            start = best if (rng.random() < V['from_best'] or not pool) else rng.choice(pool)
            L = 2 * pb.rhoC * start['s']
            prm = dict(base, seed=seed + 7 * k_raw, C=start['C'], Q=start['Q'], L=L, morph=4000 + 150 * n,
                       settle=1000 + 25 * n)
            if move == 'hop':
                lo, hi = V['minDiff']
                prm.update(minDiff=math.exp(rng.uniform(math.log(lo), math.log(hi))), expand=rng.uniform(*V['expand']),
                           rh=rng.uniform(*V['rh']), noise=V['noise'], shake=V['shake'],
                           focus=0 if (n < 8 or rng.random() >= V['focus_p']) else rng.randint(3, max(4, n // 3)))
                prm['morph'] = int(prm['morph'] * V['morph_mult'])
            else:
                k = rng.randint(1, 3 if n >= 12 else 2)
                prm.update(remove=rng.sample(range(n), k), add=k, rh=rng.uniform(0.12, 0.25), expand=rng.uniform(0.0, 0.03))
            r1 = sim.call(prm)
            if raw is None or r1['s'] < raw['s']:
                raw = r1
                info.update({k: prm[k] for k in ('minDiff', 'expand', 'rh', 'focus', 'remove') if k in prm})
                info['from'] = 'best' if start is best else 'pool'
                lin = lineage_of(start['src']) if start is best else lineage_of(start)
    elif move == 'ascend':
        src = lo['best']
        lin = lineage_of(src.get('src'))
        raw = sim.call(dict(base, C=src['C'], Q=src['Q'], L=2 * pb.rhoC * src['s'], add=1, rh=rng.uniform(0.15, 0.3),
                            expand=rng.uniform(0.0, 0.03), morph=4000 + 150 * n, settle=1000 + 25 * n))
    elif move == 'descend':
        cands = remove_one(pb, hi['best']['C'], hi['best']['Q'])[:3]
        s0, i, C2, Q2 = rng.choice(cands)
        raw = {'s': s0, 'C': C2, 'Q': Q2}; info['removed'] = i; lin = lineage_of(hi['best'].get('src'))
    elif move == 'tighten':
        raw = {'s': best_s, 'C': best['C'], 'Q': best['Q']}; lin = lineage_of(best.get('src'))
    else:
        raise ValueError(move)
    t_raw = time.time() - t0
    s_raw = raw['s']
    gate = case['stats'].get('gate', 0.03)
    do_tight = best is None or move in ('descend', 'tighten') or s_raw <= best_s * (1 + gate)
    out = None
    if do_tight:
        row = {'piece': piece, 'container': container, 'problem': p, 'n': n, 'seed': seed, 'mode': move, 'B': 0,
               'C': raw['C'], 'Q': raw['Q']}
        out = tighten(row, best_s, n, gate)
    secs = time.time() - t0
    s_new = out['s'] if out else s_raw
    # ---- update the archive
    improved = False
    with locked():
        case = load_case(p, n); st = case['stats']
        cur = case['best']
        st['attempts'] += 1; st['effort'] += secs
        mv = st['moves'].setdefault(move, [0, 0]); mv[0] += 1
        if out:
            st['gaps'] = (st['gaps'] + [max(0.0, s_raw / out['s'] - 1)])[-30:]
            g = sorted(st['gaps'])
            st['gate'] = float(min(0.08, max(0.006, 1.5 * g[int(0.8 * (len(g) - 1))]))) if len(g) >= 5 else 0.03
        if move == 'tighten': st['needs_tighten'] = False
        if out and (cur is None or out['s'] < cur['s'] - 1e-12):
            improved = True; mv[1] += 1
            case['best'] = {'s': out['s'], 'C': out['C'], 'Q': out['Q'], 'src': dict(info, raw=s_raw, **({'lineage': lin} if lin else {})), 't': time.time(),
                            'tightened': True}
            st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time(); st['needs_tighten'] = False
        else:
            st['since'] += 1
        save_case(case)
        if out: pool_insert(p, n, {'s': out['s'], 'C': out['C'], 'Q': out['Q'], 'src': move, 't': time.time(), **({'lineage': lin} if lin else {})})
        fixed = enforce_monotone(p, log) if improved or cur is None else []
    log(f"{p} n={n:2d} {(move if vname == 'base' else move + '/' + vname):8s} raw {s_raw:.6f}" + (f" -> {s_new:.10f}" if out else " (gated)") +
        f"  best {'%.10f' % min(s_new, best_s) if best_s else '%.10f' % s_new}{'  NEW BEST' if improved else ''}"
        f"  {secs:.0f}s" + (f"  monotone-fixed {fixed}" if fixed else ''))
    with open(os.path.join(STATE, 'attempts.jsonl'), 'a') as f:
        f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': move, 'raw': s_raw, 's': s_new if out else None,
                            'best_before': best_s, 'improved': improved, 'secs': round(secs, 1), 'raw_secs': round(t_raw, 1),
                            **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in info.items() if k in ('minDiff', 'expand', 'focus', 'from', 'var')}}) + '\n')
    return improved


# ------------------------------------------------------------------ scheduling
def choose(rng, wid):
    """Pick (problem, n, move). First fill every missing case (ascending n per problem, so 'ascend' can build each n
    from n-1); then pick the case with the least effort per piece, discounted when it keeps failing; flagged cases are
    re-tightened first."""
    idx = {}
    for p in PID:
        for n in range(NMIN, NMAX + 1):
            c = _read(_path('best', p, n))
            idx[(p, n)] = c
    order = list(PID); rng.shuffle(order)
    claimed = {tuple(x.split('|')) for x in _claims()}
    for p in order:
        for n in range(NMIN, NMAX + 1):
            if idx[(p, n)] and idx[(p, n)].get('best'): continue
            if (p, str(n)) in claimed: break
            if n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best'): return p, n, 'ascend'
            if n < NMAX and idx[(p, n + 1)] and idx[(p, n + 1)].get('best'): return p, n, 'descend'
            if n == NMIN or rng.random() < 0.3: return p, n, 'fresh'
            break
    for (p, n), c in sorted(idx.items(), key=lambda kv: rng.random()):
        if c and c['stats'].get('needs_tighten') and (p, str(n)) not in claimed: return p, n, 'tighten'
    best_key, best_score = None, None
    fc = policy().get('focus') or {}             # optional: a share of attempts on listed cases ("pid:n")
    if fc.get('cases') and rng.random() < fc.get('share', 0):
        opts = [(x.split(':')[0], int(x.split(':')[1])) for x in fc['cases']]
        opts = [k for k in opts if k in idx and idx[k] and idx[k].get('best') and (k[0], str(k[1])) not in claimed]
        if opts: best_key, best_score = rng.choice(opts), -1.0
    for (p, n), c in (idx.items() if best_key is None else ()):
        if (p, str(n)) in claimed or not c: continue
        st = c['stats']
        score = (st.get('effort', 0) + 30) / n * (1 + st.get('since', 0) / 40) * rng.uniform(0.7, 1.3)
        if best_score is None or score < best_score: best_key, best_score = (p, n), score
    p, n = best_key
    c = idx[(p, n)]
    weak = c['best']['src'].get('move') in ('monotone', 'construction') if c.get('best') else True
    if weak:                       # placeholder from a lattice or from n+1: build a real n-packing first
        lo_ok = n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best')
        r = rng.random()
        if lo_ok and r < 0.5: return p, n, 'ascend'
        if r < 0.8: return p, n, 'fresh'
    W = dict(WEIGHTS, **(policy().get('weights') or {}))
    moves = [('hop', W['hop']), ('reinsert', W['reinsert']), ('fresh', W['fresh'])]
    if n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best'): moves.append(('ascend', W['ascend']))
    if n < NMAX and idx[(p, n + 1)] and idx[(p, n + 1)].get('best'): moves.append(('descend', W['descend']))
    r = rng.random() * sum(w for _, w in moves)
    for m, w in moves:
        r -= w
        if r <= 0: return p, n, m
    return p, n, 'hop'


def _claims():
    d = os.path.join(STATE, 'claims'); os.makedirs(d, exist_ok=True)
    out = []
    for f in os.listdir(d):
        try:
            pidn = int(open(os.path.join(d, f)).read().split()[0])
            os.kill(pidn, 0); out.append(f)
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


def work(wid):
    rng = random.Random(os.getpid() * 1000003 + int(time.time()))
    sim = Sim()
    logf = open(os.path.join(ROOT, 'logs', f'engine{wid}.log'), 'a')

    def log(msg):
        logf.write(time.strftime('%m-%d %H:%M:%S ') + msg + '\n'); logf.flush()
    log(f'worker {wid} started (pid {os.getpid()})')
    while not os.path.exists(os.path.join(STATE, 'STOP')):
        p, n, move = choose(rng, wid)
        with claim(p, n) as ok:
            if not ok: time.sleep(0.5); continue
            pol = policy(); vname = 'base'
            if move == 'hop':
                if pol.get('mode') == 'experiment': vname = rng.choice(pol.get('variants') or ['base'])
                elif pol.get('hop_variant') in VARIANTS: vname = pol['hop_variant']
            try:
                attempt(sim, p, n, move, rng, log, vname)
            except Exception as e:
                log(f'ERROR {p} n={n} {move}: {type(e).__name__}: {str(e)[:300]}')
                time.sleep(2)
    log('STOP file found, exiting')


# ------------------------------------------------------------------ seeding and status
def seed():
    """Import earlier tightened results (results/*.jsonl) and exact lattice constructions, then enforce monotonicity."""
    import constructions
    rows = []
    for fn in ('results/tight.jsonl', 'results/tight_slp.jsonl'):
        fp = os.path.join(ROOT, fn)
        if os.path.exists(fp): rows += [json.loads(l) for l in open(fp) if l.strip()]
    by = {}
    for r in rows:
        k = (pid(r['piece'], r['container']), r['n'])
        if k[0] in PID and NMIN <= r['n'] <= NMAX: by.setdefault(k, []).append(r)
    # constructions (internal units)
    extra = []
    for k in (2, 3, 4):
        C, Q = constructions.tetra(k); extra.append(('tetintet', C, Q, f'tetrahedron subdivision k={k}'))
        C, Q = constructions.octa(k); extra.append(('octinoct', C, Q, f'octahedron lattice k={k}'))
    for k in (2, 3, 4):   # cube grids: k^3 unit cubes in a cube of side k
        g = np.array([(x, y, z) for x in range(k) for y in range(k) for z in range(k)], float) - (k - 1) / 2
        extra.append(('cubincub', g, [[1.0, 0, 0, 0]] * len(g), f'cube grid k={k}'))
    n_imp = 0
    with locked():
        for (p, n), rs in by.items():
            pb = problem(p)
            rs.sort(key=lambda r: r['s'])
            case = load_case(p, n)
            for r in rs[:12]: pool_insert(p, n, {'s': r['s'], 'C': r['C'], 'Q': r['Q'], 'src': 'import', 't': time.time()})
            b = rs[0]
            if not case['best'] or b['s'] < case['best']['s'] - 1e-12:
                case['best'] = {'s': b['s'], 'C': b['C'], 'Q': b['Q'], 't': time.time(), 'tightened': True,
                                'src': {'move': 'import', 'mode': b.get('mode'), 'seed': b.get('seed')}}
                save_case(case); n_imp += 1
        for p, C, Q, name in extra:
            pb = problem(p); C = np.asarray(C, float)
            C = C * pb.edge                          # constructions are in unit-edge coordinates
            R = [exact.quat_to_R(np.array(q)) for q in Q]
            L, _, C0 = exact.certify(pb, C, R)
            Cc, Qc = C0.tolist(), [list(map(float, q)) for q in Q]
            while len(Cc) > NMAX:                    # trim to NMAX by the best LP removals
                s_, i, Cc, Qc = remove_one(pb, Cc, Qc)[0]
            n = len(Cc); s = pb.s_of_L(exact.tight_container(pb, np.array(Cc), [exact.quat_to_R(np.array(q)) for q in Qc])[0])
            case = load_case(p, n)
            if not case['best'] or s < case['best']['s'] - 1e-12:
                case['best'] = {'s': s, 'C': Cc, 'Q': Qc, 't': time.time(), 'tightened': True, 'src': {'move': 'construction', 'name': name}}
                save_case(case); n_imp += 1
            pool_insert(p, n, {'s': s, 'C': Cc, 'Q': Qc, 'src': 'construction', 't': time.time()})
        for p in PID: enforce_monotone(p, print)
    print(f'seeded {n_imp} cases')


def table():
    lines = []
    for p in PID:
        row = []
        for n in range(NMIN, NMAX + 1):
            c = _read(_path('best', p, n))
            row.append(f"{n}:{c['best']['s']:.5f}" if c and c.get('best') else f'{n}:-')
        lines.append(f'{p}  ' + ' '.join(row))
    return '\n'.join(lines)


def check():
    bad = 0
    for p in PID:
        prev = None
        for n in range(NMIN, NMAX + 1):
            c = _read(_path('best', p, n))
            if not c or not c.get('best'): prev = None; continue
            if len(c['best']['C']) != n: print('wrong piece count', p, n); bad += 1
            if prev is not None and prev > c['best']['s']: print('NOT MONOTONE', p, n - 1, prev, '>', n, c['best']['s']); bad += 1
            prev = c['best']['s']
    print('archive check:', 'ok' if not bad else f'{bad} problems')
    return bad


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'logs'), exist_ok=True)
    cmd = sys.argv[1]
    if cmd == 'seed': seed()
    elif cmd == 'work': work(sys.argv[2] if len(sys.argv) > 2 else '0')
    elif cmd == 'status': print(table())
    elif cmd == 'check': sys.exit(1 if check() else 0)
