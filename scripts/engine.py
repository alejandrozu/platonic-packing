#!/usr/bin/env python3
"""Autonomous search engine: anytime basin hopping over all problems and n, with a monotone archive.

usage:  python3 scripts/engine.py seed            # import earlier results + lattice constructions (idempotent)
        python3 scripts/engine.py work <id>       # one worker (run two, see scripts/run_forever.sh)
        python3 scripts/engine.py status          # print the current table
        python3 scripts/engine.py check           # verify the archive invariants (monotone s(n), files readable)
        python3 scripts/engine.py harvest DIR HOST  # merge another machine's state/best tree (re-legalized here)

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
import json, os, sys, time, math, random, subprocess, signal, glob, hashlib, contextlib
try:
    import fcntl
except ImportError:  # Site building and certification only read the problem metadata on Windows.
    fcntl = None
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import exact

STATE = os.environ.get('PP_STATE') or os.path.join(ROOT, 'state')     # PP_STATE: separate archive (remote workers)
AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico',
      # Archimedean
      'truncated_tetrahedron': 'tte', 'cuboctahedron': 'cbo', 'truncated_cube': 'tcu', 'truncated_octahedron': 'toc',
      'rhombicuboctahedron': 'rco', 'truncated_cuboctahedron': 'tco', 'snub_cube': 'snc', 'icosidodecahedron': 'ido',
      'truncated_dodecahedron': 'tdo', 'truncated_icosahedron': 'tic', 'rhombicosidodecahedron': 'rid',
      'truncated_icosidodecahedron': 'tid', 'snub_dodecahedron': 'snd',
      # Catalan
      'triakis_tetrahedron': 'ktt', 'rhombic_dodecahedron': 'rdo', 'triakis_octahedron': 'kto',
      'tetrakis_hexahedron': 'kth', 'deltoidal_icositetrahedron': 'dit', 'disdyakis_dodecahedron': 'ddo',
      'pentagonal_icositetrahedron': 'pit', 'rhombic_triacontahedron': 'rtc', 'triakis_icosahedron': 'kti',
      'pentakis_dodecahedron': 'pkd', 'deltoidal_hexecontahedron': 'dhc', 'disdyakis_triacontahedron': 'dtc',
      'pentagonal_hexecontahedron': 'phc'}
for _k in (3, 5, 6, 8, 12): AB[f'prism{_k}'] = f'pr{_k}'
for _k in (4, 5, 6, 8, 12): AB[f'antiprism{_k}'] = f'ap{_k}'
ELONG_TAGS = ('l15', 'l2', 'l3')                          # elongated prisms, height 1.5, 2, 3 (13 Oct 2026), in a cube
for _k in (3, 5, 6, 8, 12):
    for _t in ELONG_TAGS: AB[f'prism{_k}_{_t}'] = f'pr{_k}{_t}'
ARCHIMEDEAN = ['truncated_tetrahedron', 'cuboctahedron', 'truncated_cube', 'truncated_octahedron', 'rhombicuboctahedron',
               'truncated_cuboctahedron', 'snub_cube', 'icosidodecahedron', 'truncated_dodecahedron',
               'truncated_icosahedron', 'rhombicosidodecahedron', 'truncated_icosidodecahedron', 'snub_dodecahedron']
CATALAN = ['triakis_tetrahedron', 'rhombic_dodecahedron', 'triakis_octahedron', 'tetrakis_hexahedron',
           'deltoidal_icositetrahedron', 'disdyakis_dodecahedron', 'pentagonal_icositetrahedron',
           'rhombic_triacontahedron', 'triakis_icosahedron', 'pentakis_dodecahedron', 'deltoidal_hexecontahedron',
           'disdyakis_triacontahedron', 'pentagonal_hexecontahedron']
PRISMS = [f'prism{k}' for k in (3, 5, 6, 8, 12)] + [f'antiprism{k}' for k in (4, 5, 6, 8, 12)]
PROBLEMS = [('tetrahedron', 'tetrahedron'), ('octahedron', 'octahedron'), ('icosahedron', 'icosahedron'),
            ('dodecahedron', 'dodecahedron'), ('cube', 'cube'), ('cube', 'octahedron'), ('octahedron', 'cube'),
            ('dodecahedron', 'icosahedron'), ('icosahedron', 'dodecahedron')]
PLATONIC = ('tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron')
PROBLEMS += [(piece, container) for piece in PLATONIC for container in PLATONIC
             if (piece, container) not in PROBLEMS]
FAMILY = {p: 'platonic' for p in PROBLEMS}
for _s in ARCHIMEDEAN: PROBLEMS.append((_s, _s)); FAMILY[(_s, _s)] = 'archimedean'
for _s in CATALAN: PROBLEMS.append((_s, _s)); FAMILY[(_s, _s)] = 'catalan'
for _s in PRISMS:
    for _c in (_s, 'cube'): PROBLEMS.append((_s, _c)); FAMILY[(_s, _c)] = 'prisms'
ELONGATED = [f'prism{k}_{t}' for k in (3, 5, 6, 8, 12) for t in ELONG_TAGS]
for _s in ELONGATED: PROBLEMS.append((_s, 'cube')); FAMILY[(_s, 'cube')] = 'prisms'
NMIN, NMAX, POOL = 2, int(os.environ.get('PP_NMAX', '100')), 6     # n <= 100 since 14 Oct 16:49 (Alejandro); 40 before
CHAIN_FROM = 41                                                        # n above the old range: crystal-cut seeds, ascend chain first

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
WEIGHTS = {'hop': 0.55, 'reinsert': 0.12, 'fresh': 0.13, 'ascend': 0.10, 'descend': 0.10, 'symfresh': 0.0, 'perturb': 0.0}
# Adaptive search (13 Oct 2026, docs/SEARCH_METHODS_REVIEW.md). Per-family move weights (policy 'family_weights'
# overrides these): symmetric seeding leads on prisms and antiprisms, hops on Archimedean and Catalan solids.
FAMILY_WEIGHTS = {
    'prisms':      {'symfresh': 0.40, 'hop': 0.35, 'ascend': 0.10, 'descend': 0.05, 'reinsert': 0.05, 'fresh': 0.05},
    'archimedean': {'hop': 0.60, 'ascend': 0.15, 'reinsert': 0.07, 'descend': 0.06, 'symfresh': 0.08, 'fresh': 0.04},
    'catalan':     {'hop': 0.60, 'ascend': 0.15, 'reinsert': 0.07, 'descend': 0.06, 'symfresh': 0.08, 'fresh': 0.04},
    'platonic':    {'hop': 0.60, 'ascend': 0.10, 'reinsert': 0.05, 'descend': 0.10, 'symfresh': 0.10, 'fresh': 0.05},
}
# Move classes for the explore/polish switch: after `switch_after` failures in a row on a case, the class that has
# failed more since the last improvement is damped and the other one boosted (polish after failed explorations,
# explore after failed polishing).
DISCOVERY, POLISH = ('symfresh', 'fresh', 'reinsert'), ('hop', 'tighten', 'perturb')


def policy():
    return _read(os.path.join(STATE, 'policy.json'), {}) or {}


def pid(piece, container): return f'{AB[piece]}in{AB[container]}'


def lineage_of(x):
    """Published packing a packing descends from (archive src dict or pool entry), for attribution."""
    if not isinstance(x, dict): return None
    if x.get('move') == 'literature' or x.get('src') == 'literature': return x.get('source') or x.get('lineage')
    return x.get('lineage')


PID = {pid(p, c): (p, c) for p, c in PROBLEMS}
FAM = {pid(p, c): FAMILY[(p, c)] for p, c in PROBLEMS}
PID_INDEX = {p: i for i, p in enumerate(PID)}


def active_problems():
    """Problems the workers work on: policy 'families' (default: all)."""
    fams = policy().get('families')
    return [p for p in PID if not fams or FAM[p] in fams]


def shard():
    """PP_SHARD='k/m': this worker prefers the problems with index = k (mod m) while filling cases (so machines that
    do not share an archive do not all fill the same cases); it helps elsewhere when its own share is done."""
    v = os.environ.get('PP_SHARD')
    if not v: return None
    k, m = v.split('/'); return int(k), int(m)
_pb_cache = {}


def problem(p):
    if p not in _pb_cache: _pb_cache[p] = exact.Problem(*PID[p])
    return _pb_cache[p]


# ------------------------------------------------------------------ archive
@contextlib.contextmanager
def locked():
    if fcntl is None:
        raise RuntimeError('Archive workers require POSIX file locking; run them under Linux or WSL.')
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


_RCACHE = {}


def _read_cached(path):
    """Read-only view of a case for the scheduler: re-parsed only when the file changed (6,000 cases at n <= 100)."""
    try: st = os.stat(path)
    except FileNotFoundError: _RCACHE.pop(path, None); return None
    key = (st.st_mtime_ns, st.st_size); hit = _RCACHE.get(path)
    if hit and hit[0] == key: return hit[1]
    obj = _read(path)
    if obj is not None: _RCACHE[path] = (key, obj)
    return obj


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
def tighten(row, best_s, n, gate, explore=False):
    """Sequential-LP tightening with an optimistic early abort, SLSQP polish for small n when it wins.
    Policy 'tightener': 'exact' (exact.py SLP, the default until 14 Oct) or 'fast' (src/fastslp.py, 14 Oct large-n
    study): a vectorized SLP whose LP prefers small moves (reg 1e-4: 2-10x faster to the nearby optimum); when that
    lands within 0.3% of the best, the unregularized LP is also run from the same raw start, since its vertex jumps
    explore (expand 1% + displace + unregularized SLP beat 11 of 14 records at n = 35-40 in the study). explore=True
    (the 'perturb' move) runs only the unregularized LP."""
    hist = []

    def abort(it, L):
        s = problem(row['problem']).s_of_L(L); hist.append(s)
        if best_s is None or it < 15: return False
        rate = max(0.0, (hist[-6] - s) / 5) if len(hist) >= 6 else 0.0
        return s - 150 * rate > best_s                       # even 150 more rounds at this rate cannot win

    if policy().get('tightener', 'exact') == 'fast':
        import fastslp
        tl = 30 + 4 * n
        if explore:
            return fastslp.tighten_run(row, tlimit=tl, slp_floor=1e-6, abort=abort, reg=0.0)
        out = fastslp.tighten_run(row, tlimit=tl, slp_floor=1e-6, abort=abort, reg=1e-4)
        # explore only for a close call: within +-0.3% of the best (a clear win over a weak seed is taken as it is;
        # the 'perturb' move explores it later) -- at n = 75-90 the second LP doubled a 5-13 min attempt (14 Oct 22:20)
        if best_s is not None and best_s * 0.997 <= out['s'] < best_s * 1.003 and out['s_start'] - out['s'] > 1e-4 * out['s']:
            # near the best: the unregularized LP from the same raw start explores (its vertex jumps use the slack
            # of the loose start; from the regularized optimum, or from an already tight start, it finds little and
            # its degenerate LPs are slow: 14 Oct study)
            hist.clear()
            out2 = fastslp.tighten_run(row, tlimit=tl, slp_floor=1e-6, abort=abort, reg=0.0)
            if out2['s'] < out['s']: out = out2
        return out
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
    elif move == 'symfresh':
        import symmetry
        spec, sinfo = symmetry.sym_spec(piece, container, n, rng)
        B = 1.0 if n <= 16 else 0.7
        req = dict(op='fresh', piece=piece, container=container, n=n, seed=seed, mode='improved', anneal=True,
                   compact=int(5000 * B), morph=int(45000 * B), settle=int(3000 * B))
        if spec is not None:
            req['sym'] = spec
            info['sym'] = f"C{sinfo['k']}{'i' if sinfo['det'] < 0 else ''}+{sinfo['b']}"
        raw = sim.call(req)
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
    elif move == 'perturb':         # 14 Oct large-n study: expand 0.3-5%, displace centres, re-tighten (exploratory LP)
        # sizes from the 14 Oct sweep (n = 28-40): small kicks win most often, large ones (2-5%) gain the most per CPU-hour
        e = math.exp(rng.uniform(math.log(0.003), math.log(0.05))); sg = e * rng.uniform(0.5, 0.9)
        C0 = np.array(best['C']); nr = np.random.default_rng(seed)
        raw = {'s': best_s * (1 + e), 'C': (C0 * (1 + e) + nr.normal(0, sg, C0.shape)).tolist(), 'Q': best['Q']}
        info.update(expand=round(e, 4), sigma=round(sg, 4)); lin = lineage_of(best.get('src'))
    else:
        raise ValueError(move)
    t_raw = time.time() - t0
    s_raw = raw['s']
    gate = case['stats'].get('gate', 0.03)
    if move in ('fresh', 'symfresh'): gate = max(gate, 0.04)       # bake-off: 10-14% of start wins come from > 3%
    do_tight = best is None or move in ('descend', 'tighten', 'perturb') or s_raw <= best_s * (1 + gate)
    out = None
    if do_tight:
        row = {'piece': piece, 'container': container, 'problem': p, 'n': n, 'seed': seed, 'mode': move, 'B': 0,
               'C': raw['C'], 'Q': raw['Q']}
        out = tighten(row, best_s, n, gate, explore=(move == 'perturb'))
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
            st['fails'] = {}
        else:
            st['since'] += 1
            cls = 'disc' if move in DISCOVERY else 'pol' if move in POLISH else 'nbr'
            st.setdefault('fails', {})[cls] = st.get('fails', {}).get(cls, 0) + 1
        save_case(case)
        if out: pool_insert(p, n, {'s': out['s'], 'C': out['C'], 'Q': out['Q'], 'src': move, 't': time.time(), **({'lineage': lin} if lin else {})})
        fixed = enforce_monotone(p, log) if improved or cur is None else []
    log(f"{p} n={n:2d} {(move if vname == 'base' else move + '/' + vname):8s} raw {s_raw:.6f}" + (f" -> {s_new:.10f}" if out else " (gated)") +
        f"  best {'%.10f' % min(s_new, best_s) if best_s else '%.10f' % s_new}{'  NEW BEST' if improved else ''}"
        f"  {secs:.0f}s" + (f"  monotone-fixed {fixed}" if fixed else ''))
    with open(os.path.join(STATE, 'attempts.jsonl'), 'a') as f:
        f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': move, 'raw': s_raw, 's': s_new if out else None,
                            'best_before': best_s, 'improved': improved, 'secs': round(secs, 1), 'raw_secs': round(t_raw, 1),
                            **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in info.items() if k in ('minDiff', 'expand', 'focus', 'from', 'var', 'sym')}}) + '\n')
    return improved


# ------------------------------------------------------------------ scheduling
def choose(rng, wid):
    """Pick (problem, n, move). First fill every missing case (ascending n per problem, so 'ascend' can build each n
    from n-1); then bring every case to policy 'min_attempts' attempts (fewest first); then pick the case with the
    least effort per piece, discounted when it keeps failing; flagged cases are re-tightened first. Only the policy's
    active families are searched; a sharded worker (PP_SHARD) prefers its own problems in the first two phases."""
    act = active_problems()
    idx = {}
    for p in act:
        for n in range(NMIN, NMAX + 1):
            c = _read_cached(_path('best', p, n))
            idx[(p, n)] = c
    order = list(act); rng.shuffle(order)
    sh = shard()
    if sh: order.sort(key=lambda p: 0 if PID_INDEX[p] % sh[1] == sh[0] else 1)
    claimed = {tuple(x.split('|')) for x in _claims()}
    fast = bool(os.environ.get('PP_FAST'))
    FAST_NMAX = int(os.environ.get('PP_FAST_NMAX', '20'))   # fast mode: attempts above this n outlast a bounded run       # laptop: short bounded runs -> skip the slow fill phase, small n first
    for p in (order if not fast else ()):
        for n in range(NMIN, NMAX + 1):
            if idx[(p, n)] and idx[(p, n)].get('best'): continue
            if (p, str(n)) in claimed: break
            if n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best'): return p, n, 'ascend'
            if n < NMAX and idx[(p, n + 1)] and idx[(p, n + 1)].get('best'): return p, n, 'descend'
            if n == NMIN or rng.random() < 0.3: return p, n, 'symfresh' if FAM[p] == 'prisms' else 'fresh'
            break
    # ascend chain over the crystal-cut seeds above the old range (14 Oct large-n study: the chain n-1 -> n is the
    # reliable first draft; the cut competes as the seed): per problem, the lowest n whose seed has not had an ascend
    for p in (order if not fast else ()):
        for n in range(max(NMIN + 1, CHAIN_FROM), NMAX + 1):
            c = idx[(p, n)]
            if not c or not c.get('best'): break
            if (c['best'].get('src') or {}).get('move') not in ('latcut', 'monotone'): continue
            if ((c['stats'].get('moves') or {}).get('ascend') or [0])[0] > 0: continue
            if (p, str(n)) in claimed: break
            return p, n, 'ascend'
    for (p, n), c in sorted(idx.items(), key=(lambda kv: kv[0][1]) if fast else (lambda kv: rng.random())):
        if fast and n > 20: break                # fast mode: only quick re-tightenings, smallest n first
        if c and c['stats'].get('needs_tighten') and (p, str(n)) not in claimed: return p, n, 'tighten'
    best_key, best_score = None, None
    need = int(policy().get('min_attempts', 0))
    if need:                                     # bring every case to `need` attempts, fewest first (own shard first)
        low = [(total_attempts(c['stats']), 0 if not sh or PID_INDEX[p] % sh[1] == sh[0] else 1, rng.random(), p, n)
               for (p, n), c in idx.items() if c and c.get('best') and total_attempts(c['stats']) < need
               and (p, str(n)) not in claimed and (not fast or n <= FAST_NMAX)]
        if low:
            low.sort(key=(lambda x: (x[0], x[4], x[2])) if fast else (lambda x: (x[1], x[0], x[2])))
            best_key, best_score = (low[0][3], low[0][4]), -1.0
    fc = policy().get('focus') or {}             # optional: a share of attempts on listed cases ("pid:n")
    if best_key is None and fc.get('cases') and rng.random() < fc.get('share', 0):
        opts = [(x.split(':')[0], int(x.split(':')[1])) for x in fc['cases']]
        opts = [k for k in opts if k in idx and idx[k] and idx[k].get('best') and (k[0], str(k[1])) not in claimed]
        if opts: best_key, best_score = rng.choice(opts), -1.0
    for (p, n), c in (idx.items() if best_key is None else ()):
        if (p, str(n)) in claimed or not c: continue
        if fast and n > FAST_NMAX: continue
        st = c['stats']
        # gain per CPU-hour falls 35x from right after an improvement to 80 failures later: favour hot cases
        score = (st.get('effort', 0) + 30) / n * (1 + st.get('since', 0) / 12) * rng.uniform(0.7, 1.3)
        if c.get('best') and _plateau(idx, p, n): score *= 0.5            # equal s for n-1, n, n+1: likely weak
        if c.get('best') and c['best']['src'].get('move') == 'community': score *= 0.7   # new contributed packing
        if best_score is None or score < best_score: best_key, best_score = (p, n), score
    p, n = best_key
    c = idx[(p, n)]
    weak = c['best']['src'].get('move') in ('monotone', 'construction') if c.get('best') else True
    if weak:                       # placeholder from a lattice or from n+1: build a real n-packing first
        lo_ok = n > NMIN and idx[(p, n - 1)] and idx[(p, n - 1)].get('best')
        r = rng.random()
        if lo_ok and r < 0.5: return p, n, 'ascend'
        if r < 0.8: return p, n, 'symfresh' if FAM[p] == 'prisms' else 'fresh'
    return p, n, choose_move(rng, idx, p, n)


def _plateau(idx, p, n):
    s = [idx.get((p, m)) for m in (n - 1, n, n + 1)]
    v = [x['best']['s'] for x in s if x and x.get('best')]
    return len(v) == 3 and (abs(v[1] - v[0]) < 1e-7 * v[1] or abs(v[2] - v[1]) < 1e-7 * v[1])


_LEARN = {'t': 0, 'mult': {}}


def learned_multipliers():
    """Bandit part: per family, the recent gain per CPU-second of each move (last ~4000 logged attempts, with a prior
    of 1800 s at the family's average rate), as a multiplier in [0.4, 3] relative to the family's median move.
    Refreshed every 5 minutes from this machine's attempts.jsonl."""
    if time.time() - _LEARN['t'] < 300: return _LEARN['mult']
    _LEARN['t'] = time.time()
    path = os.path.join(STATE, 'attempts.jsonl')
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2); size = f.tell(); f.seek(max(0, size - 1_500_000)); lines = f.read().decode(errors='ignore').splitlines()[1:]
    except OSError:
        return _LEARN['mult']
    G, T = {}, {}
    since = float(policy().get('started') or 0)              # only attempts made under the current policy
    for l in lines[-4000:]:
        try: r = json.loads(l)
        except ValueError: continue
        if r.get('t', 0) < since: continue
        m = r.get('move'); fam = FAM.get(r.get('p'))
        if not fam or m in ('harvest', 'tighten', None) or not r.get('best_before') or not r.get('secs'): continue
        g = math.log(r['best_before'] / r['s']) if r.get('improved') and r.get('s') else 0.0
        G[(fam, m)] = G.get((fam, m), 0.0) + g; T[(fam, m)] = T.get((fam, m), 0.0) + r['secs']
    mult = {}
    for fam in set(f for f, _ in T):
        ms = [m for f, m in T if f == fam]
        tot_g = sum(G[(fam, m)] for m in ms); tot_t = sum(T[(fam, m)] for m in ms)
        base = tot_g / tot_t if tot_t else 0.0
        rate = {m: (G[(fam, m)] + base * 1800) / (T[(fam, m)] + 1800) for m in ms}
        med = sorted(rate.values())[len(rate) // 2]
        if med > 0: mult[fam] = {m: min(3.0, max(0.4, v / med)) for m, v in rate.items()}
    _LEARN['mult'] = mult
    return mult


def choose_move(rng, idx, p, n):
    """Move for a case: family weights x learned gain-per-second multipliers x case signals (cascade from n-1 / n+1,
    explore/polish switch after repeated failures)."""
    pol = policy(); c = idx[(p, n)]; st = c['stats']; fam = FAM[p]
    W = dict(WEIGHTS, **(pol.get('weights') or {}))
    W.update(FAMILY_WEIGHTS.get(fam, {})); W.update((pol.get('family_weights') or {}).get(fam, {}))
    if pol.get('adaptive', True):
        for m, k in (learned_multipliers().get(fam) or {}).items():
            if m in W: W[m] *= k
    lo = idx.get((p, n - 1)) if n > NMIN else None; hi = idx.get((p, n + 1)) if n < NMAX else None
    t_self = st.get('last_improve', 0) or 0
    if lo and lo.get('best') and (lo['stats'].get('last_improve') or 0) > t_self: W['ascend'] *= 2.0     # cascade
    if hi and hi.get('best') and (hi['stats'].get('last_improve') or 0) > t_self: W['descend'] *= 1.5
    if st.get('since', 0) >= int(pol.get('switch_after', 6)):
        f = st.get('fails') or {}
        damp, boost = (DISCOVERY, POLISH) if f.get('disc', 0) >= f.get('pol', 0) else (POLISH, DISCOVERY)
        for m in damp:
            if m in W: W[m] *= 0.4
        for m in boost:
            if m in W: W[m] *= 2.5
    moves = [(m, W.get(m, 0)) for m in ('hop', 'reinsert', 'fresh', 'symfresh', 'perturb') if W.get(m, 0) > 0 and (m != 'perturb' or c.get('best'))]
    if lo and lo.get('best'): moves.append(('ascend', W['ascend']))
    if hi and hi.get('best'): moves.append(('descend', W['descend']))
    r = rng.random() * sum(w for _, w in moves)
    for m, w in moves:
        r -= w
        if r <= 0: return m
    return 'hop'


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
    deadline = float(os.environ.get('PP_DEADLINE') or 0)      # bounded runs (laptop workspace): no new attempt after it
    while not os.path.exists(os.path.join(STATE, 'STOP')) and not (deadline and time.time() > deadline):
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


def harvest(src_dir, host):
    """Merge packings found elsewhere (another machine's state/best tree) into this archive. Each candidate is
    re-legalized here (scaled apart until no pair overlaps, then the tightest container computed), so a corrupt or
    overlapping file can never enter the archive; it replaces our best only if it is still smaller."""
    taken = []
    for p in PID:
        pb = problem(p)
        for n in range(NMIN, NMAX + 1):
            c = _read(os.path.join(src_dir, p, f'n{n:02d}.json'))
            b = c and c.get('best')
            if not b or len(b['C']) != n: continue
            cur = load_case(p, n)['best']
            if cur and b['s'] >= cur['s'] - 1e-12: continue
            R = [exact.quat_to_R(np.array(q) / np.linalg.norm(q)) for q in b['Q']]
            L, _, C0 = exact.certify(pb, np.array(b['C'], float), R)
            Lt, t = exact.tight_container(pb, C0, R)
            s = pb.s_of_L(Lt)
            with locked():
                case = load_case(p, n); cur = case['best']
                if cur and s >= cur['s'] - 1e-12: continue
                src = dict(b.get('src') or {}, host=host)
                case['best'] = {'s': s, 'C': (C0 + t).tolist(), 'Q': [list(map(float, q)) for q in b['Q']], 'src': src,
                                't': time.time(), 'tightened': True}
                st = case['stats']; st['improvements'] += 1; st['since'] = 0; st['last_improve'] = time.time()
                save_case(case)
                pool_insert(p, n, {'s': s, 'C': case['best']['C'], 'Q': case['best']['Q'], 'src': 'harvest', 't': time.time(),
                                   **({'lineage': src['lineage']} if src.get('lineage') else {})})
                enforce_monotone(p, print)
                with open(os.path.join(STATE, 'attempts.jsonl'), 'a') as f:
                    f.write(json.dumps({'t': round(time.time()), 'p': p, 'n': n, 'move': 'harvest', 'raw': b['s'], 's': s,
                                        'best_before': cur['s'] if cur else None, 'improved': True, 'secs': 0, 'raw_secs': 0,
                                        'host': host, 'var': src.get('var')}) + '\n')
            taken.append(f'{p}{n}:{s:.4f}')
    print(f'harvest from {host}: {len(taken)} improvements ' + ' '.join(taken))
    return taken


def add_remote_counts(counts, host):
    """Add attempts made on other machines ({'pid:n': k}) to the cases' statistics (attempts_remote), so that the
    policy's min_attempts counts every machine's work."""
    with locked():
        for key, k in counts.items():
            p, n = key.split(':'); n = int(n)
            if p not in PID: continue
            c = load_case(p, n)
            if not c.get('best'): continue
            c['stats']['attempts_remote'] = c['stats'].get('attempts_remote', 0) + int(k)
            save_case(c)
    print(f'remote attempts from {host}: {sum(counts.values())} on {len(counts)} cases')


def set_remote_totals(totals, host):
    """Attempts made by one remote archive in total ({'pid:n': k}; a laptop archive or one GitHub Actions job):
    stored per host, replacing that host's previous total."""
    with locked():
        for key, k in totals.items():
            p, n = key.split(':'); n = int(n)
            if p not in PID: continue
            c = load_case(p, n)
            if not c.get('best'): continue
            c['stats'].setdefault('remote', {})[host] = int(k)
            save_case(c)
    print(f'remote attempt totals from {host}: {sum(totals.values())} on {len(totals)} cases')


def total_attempts(st): return st.get('attempts', 0) + st.get('attempts_remote', 0) + sum((st.get('remote') or {}).values())


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
    elif cmd == 'harvest': harvest(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'remote')
