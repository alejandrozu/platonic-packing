#!/usr/bin/env python3
"""Compare hop settings from state/attempts.jsonl (written by scripts/engine.py).

usage: python3 scripts/experiment.py [since_unix_time]      (default: state/policy.json 'started')

For every variant: hop attempts, CPU time, new bests (any decrease of the archived s), new bests that shrink s by
more than 1e-4 (relative), the total relative shrinkage, and near misses (tightened to within 0.1% of the best).
Rates are per CPU-hour of that variant's own attempts; the interval is a 90% Poisson interval for the count."""
import json, os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def poisson_ci(k, z=1.645):
    """Approximate 90% interval for a Poisson count (Wilson-Hilferty)."""
    lo = 0.0 if k == 0 else k * (1 - 1 / (9 * k) - z / (3 * math.sqrt(k))) ** 3
    k1 = k + 1
    hi = k1 * (1 - 1 / (9 * k1) + z / (3 * math.sqrt(k1))) ** 3
    return lo, hi


def report(since=None, until=None, out=print):
    pol = json.load(open(os.path.join(ROOT, 'state', 'policy.json'))) if os.path.exists(os.path.join(ROOT, 'state', 'policy.json')) else {}
    since = since or pol.get('started', 0)
    rows = []
    for l in open(os.path.join(ROOT, 'state', 'attempts.jsonl')):
        try: a = json.loads(l)
        except Exception: continue
        if a['t'] >= since and (until is None or a['t'] < until) and a.get('best_before'): rows.append(a)
    hops = [a for a in rows if a['move'] == 'hop' and 'var' in a]
    names = sorted({a['var'] for a in hops}, key=lambda v: (v != 'base', v))
    res = {}
    out(f'{len(rows)} attempts since {since}, {len(hops)} hops with a variant tag; '
        f'{(max(a["t"] for a in rows) - since) / 60 if rows else 0:.0f} min')
    out(f'{"variant":8s} {"hops":>5s} {"CPU min":>8s} {"new bests":>9s} {"per CPU-h (90% CI)":>22s} {">1e-4/CPU-h":>12s} '
        f'{"shrink/CPU-h":>13s} {"near 0.1%":>9s} {"tightened":>9s}')
    for v in names:
        rs = [a for a in hops if a['var'] == v]
        sec = sum(a['secs'] for a in rs) or 1
        imp = [math.log(a['best_before'] / a['s']) for a in rs if a['improved']]
        big = sum(1 for m in imp if m > 1e-4)
        near = sum(1 for a in rs if a['s'] is not None and a['s'] < a['best_before'] * 1.001)
        tight = sum(1 for a in rs if a['s'] is not None)
        lo, hi = poisson_ci(len(imp))
        h = sec / 3600
        res[v] = dict(hops=len(rs), cpu_h=h, bests=len(imp), rate=len(imp) / h, lo=lo / h, hi=hi / h, big_rate=big / h,
                      shrink_rate=sum(imp) / h, near=near / max(1, len(rs)), tight=tight / max(1, len(rs)))
        r = res[v]
        out(f'{v:8s} {len(rs):5d} {sec / 60:8.1f} {len(imp):9d} {r["rate"]:8.1f} ({r["lo"]:5.1f}-{r["hi"]:5.1f}) '
            f'{r["big_rate"]:12.1f} {r["shrink_rate"]:13.2e} {100 * r["near"]:8.1f}% {100 * r["tight"]:8.0f}%')
    return res


if __name__ == '__main__':
    report(int(sys.argv[1]) if len(sys.argv) > 1 else None)
