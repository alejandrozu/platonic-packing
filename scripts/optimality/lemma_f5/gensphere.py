"""Exact line-bound certificates for  sum_i (s_i^3 + lam s_i) <= U  on  s >= 0, sum s_i^2 = 1, s_i^2 <= cap.

Per coordinate the range of s is cut at rational points 0 = b_0 < b_1 < ... < b_k = smax; on [b_j, b_{j+1}] the bound
s^3 + lam s <= al_j + be_j s^2 comes from an exact factorization of  al + be s^2 - s^3 - lam s:
  tangent at t0:      (s - t0)^2 (u - s),        valid for s <= u,        u = (lam - t0^2)/(2 t0)
  chord on [a, b]:    (s - a)(b - s)(s - u),     valid for a <= s <= b,  u = (lam - a b)/(a + b) <= a
The case LP (every coordinate in some interval, sum of squares 1) is maximized exactly over its vertices.
"""
from fractions import Fraction as Fr
import itertools, math


def tangent(lam, t0):
    u = (lam - t0 * t0) / (2 * t0)
    return {'kind': 'tan', 't0': t0, 'u': u, 'al': t0 * t0 * u, 'be': u + 2 * t0}


def chord(lam, a, b):
    u = (lam - a * b) / (a + b)
    return {'kind': 'chord', 'a': a, 'b': b, 'u': u, 'al': a * b * u, 'be': a + b + u}


def valid(line, lo, hi):
    if line['kind'] == 'tan': return line['u'] >= hi and line['t0'] >= 0
    return line['u'] <= line['a'] and line['a'] <= lo and hi <= line['b']


def f(lam, s): return s ** 3 + lam * s


def best_for_interval(lam, lo, hi, grid=40, den=10 ** 4):
    """Candidate lines valid on [lo, hi]; returns list of (line) sorted by max overestimate on the interval."""
    cands = []
    if lo > 0 or True:
        a = lo if lo > 0 else None
        if a is not None:
            L = chord(lam, lo, hi)
            if valid(L, lo, hi): cands.append(L)
    for k in range(grid + 1):
        t = lo + (hi - lo) * Fr(k, grid)
        t = Fr(round(float(t) * den), den)
        if t <= 0: continue
        L = tangent(lam, t)
        if valid(L, lo, hi): cands.append(L)
    return cands


def lp_max(lines, ivals, combo, cap2=1):
    """max sum_i al + be s_i^2 over s_i^2 in [lo^2, hi^2], sum s_i^2 = 1 (exact, vertex enumeration)."""
    n = len(combo)
    B = [(ivals[j][0] ** 2, ivals[j][1] ** 2) for j in combo]
    al = sum(lines[j]['al'] for j in combo); be = [lines[j]['be'] for j in combo]
    best = None
    for free in range(n):
        for bits in itertools.product([0, 1], repeat=n - 1):
            q = [None] * n; it = iter(bits)
            for i in range(n):
                if i != free: q[i] = B[i][1] if next(it) else B[i][0]
            rest = 1 - sum(q[i] for i in range(n) if i != free)
            if rest < B[free][0] or rest > B[free][1]: continue
            q[free] = rest
            v = al + sum(be[i] * q[i] for i in range(n))
            if best is None or v > best: best = v
    return best


def certify(lam, n, breaks, picks, U):
    ivals = list(zip(breaks[:-1], breaks[1:]))
    worst = None; arg = None
    for combo in itertools.combinations_with_replacement(range(len(ivals)), n):
        v = lp_max(picks, ivals, combo)
        if v is None: continue
        if worst is None or v > worst: worst, arg = v, combo
    return worst, arg


def design(lam, n, breaks, targets=None):
    """For each interval pick the valid line minimizing the value at the target point (default: interval centre)."""
    ivals = list(zip(breaks[:-1], breaks[1:]))
    picks = []
    for j, (lo, hi) in enumerate(ivals):
        t = targets[j] if targets else (lo + hi) / 2
        cands = best_for_interval(lam, lo, hi)
        if not cands: raise ValueError(f'no line for [{lo},{hi}]')
        picks.append(min(cands, key=lambda L: L['al'] + L['be'] * t * t))
    return picks
