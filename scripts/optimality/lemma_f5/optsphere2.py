"""Partitions with a designated largest coordinate s0 (others s_i <= s0).

big partition on [b_lo, b_hi] for s0, small partition on [0, s_hi] for the others; LP per case:
  q0 in I0, q_i in J_i, sum q = 1, q_i <= q0; maximize sum al + be q.
Usage: python3 optsphere2.py lam n b_lo b_hi s_hi kbig ksmall seed iters
"""
import sys, random, itertools, pickle
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
from gensphere import tangent, chord, valid, best_for_interval

random.seed(int(sys.argv[8]))
lam = Fr(sys.argv[1]); n = int(sys.argv[2])
b_lo, b_hi, s_hi = Fr(sys.argv[3]), Fr(sys.argv[4]), Fr(sys.argv[5])
kb, ks = int(sys.argv[6]), int(sys.argv[7]); iters = int(sys.argv[9])


def rnd(x, den=1000): return Fr(round(x * den), den)


def pick(lo, hi, t):
    c = best_for_interval(lam, lo, hi)
    if not c: return None
    return min(c, key=lambda L: L['al'] + L['be'] * t * t)


def lp(big, small, jb, js):
    lo0, hi0, L0 = big[jb]
    c = [-float(L0['be'])] + [-float(small[j][2]['be']) for j in js]
    const = float(L0['al']) + sum(float(small[j][2]['al']) for j in js)
    bounds = [(float(lo0 ** 2), float(hi0 ** 2))] + [(float(small[j][0] ** 2), float(small[j][1] ** 2)) for j in js]
    A = []; b = []
    for i in range(1, n):
        row = [0.0] * n; row[i] = 1; row[0] = -1; A.append(row); b.append(0.0)
    r = linprog(c, A_ub=A, b_ub=b, A_eq=[[1.0] * n], b_eq=[1.0], bounds=bounds, method='highs')
    if r.status != 0: return -np.inf
    return const - r.fun


def evaluate(bb, sb, bt, st):
    big = []; small = []
    for (lo, hi), t in zip(zip(bb[:-1], bb[1:]), bt):
        L = pick(lo, hi, t)
        if L is None: return None
        big.append((lo, hi, L))
    for (lo, hi), t in zip(zip(sb[:-1], sb[1:]), st):
        L = pick(lo, hi, t)
        if L is None: return None
        small.append((lo, hi, L))
    worst = -np.inf; arg = None
    for jb in range(len(big)):
        for js in itertools.combinations_with_replacement(range(len(small)), n - 1):
            v = lp(big, small, jb, js)
            if v > worst: worst, arg = v, (jb, js)
    return worst, arg, big, small


best = None
for it in range(iters):
    def mk(lo, hi, k, prev):
        if prev is None or random.random() < 0.25:
            inner = sorted(random.uniform(float(lo) + 0.01, float(hi) - 0.01) for _ in range(k - 1))
        else:
            inner = sorted(min(float(hi) - 0.003, max(float(lo) + 0.003, float(x) + random.gauss(0, 0.01) * random.choice([0.3, 1, 3]))) for x in prev[1:-1])
        br = [lo] + [rnd(x) for x in inner] + [hi]
        return br if all(b2 > b1 for b1, b2 in zip(br[:-1], br[1:])) else None
    bb = mk(b_lo, b_hi, kb, best[1][0] if best else None)
    sb = mk(Fr(0), s_hi, ks, best[1][1] if best else None)
    if bb is None or sb is None: continue
    def tg(br, prev):
        if prev is None or random.random() < 0.3 or len(prev) != len(br) - 1:
            return [lo + (hi - lo) * Fr(random.randint(0, 20), 20) for lo, hi in zip(br[:-1], br[1:])]
        return [min(hi, max(lo, rnd(float(t) + random.gauss(0, 0.01)))) for t, (lo, hi) in zip(prev, zip(br[:-1], br[1:]))]
    bt = tg(bb, best[1][2] if best else None); st = tg(sb, best[1][3] if best else None)
    res = evaluate(bb, sb, bt, st)
    if res is None: continue
    w, arg, big, small = res
    if best is None or w < best[0]: best = (w, (bb, sb, bt, st, arg, big, small))
w, (bb, sb, bt, st, arg, big, small) = best
print('lam', lam, 'n', n, 'kb', kb, 'ks', ks, 'bound', w, 'worst', arg)
print('big', [str(x) for x in bb]); print('small', [str(x) for x in sb])
pickle.dump(best, open(f'sph2_{float(lam)}_{n}_{kb}_{ks}.pkl', 'wb'))
