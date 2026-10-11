#!/usr/bin/env python3
"""Analysis of a search period: baseline snapshot (state/snapshot_*.json) against the current archive.

usage: python3 scripts/analysis.py SNAPSHOT [--laptop-attempts N] [--out docs/analysis-....md]

Reports attempts and improvements by source (cloud workers, laptop workers merged through 'harvest', GitHub Actions
runs merged through 'harvest'), which cases improved and by how much, the comparison with published values before
and after, the hourly rate of improvements, and the cases that stopped moving."""
import json, os, sys, glob, math, time, collections, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from engine import PID, NMIN, NMAX
import publish

TITLE = {p: publish.title(p) for p in PID}
REF = json.load(open(os.path.join(ROOT, 'docs', 'references.json')))


def load_archive():
    out = {}
    for f in glob.glob(os.path.join(ROOT, 'state', 'best', '*', 'n*.json')):
        c = json.load(open(f)); p = f.split(os.sep)[-2]; n = int(os.path.basename(f)[1:3])
        out[(p, n)] = c['best']
    return out


def compare(s, ref):
    return 'better' if s < ref - 1e-5 else ('equal' if s <= ref + 1e-5 else 'behind')


def main():
    snap = json.load(open(sys.argv[1])); t0 = snap['t']
    lap = int(sys.argv[sys.argv.index('--laptop-attempts') + 1]) if '--laptop-attempts' in sys.argv else None
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    now = load_archive()
    att = []
    for l in open(os.path.join(ROOT, 'state', 'attempts.jsonl')):
        try: a = json.loads(l)
        except Exception: continue
        if a['t'] >= t0: att.append(a)
    cloud = [a for a in att if a['move'] != 'harvest']
    harv = [a for a in att if a['move'] == 'harvest']
    act_runs = [json.loads(l) for l in open(os.path.join(ROOT, 'state', 'actions_log.jsonl'))] if os.path.exists(os.path.join(ROOT, 'state', 'actions_log.jsonl')) else []
    act_att = sum(r.get('attempts', 0) for r in act_runs)
    hours = (time.time() - t0) / 3600
    L = []
    w = L.append
    w(f"# Search analysis, {snap['local']} to {time.strftime('%Y-%m-%d %H:%M')} ({hours:.1f} h)\n")
    # ---------------- sources
    imp_by = collections.Counter()
    for a in cloud:
        if a['improved']: imp_by['cloud'] += 1
    for a in harv: imp_by[a.get('host', 'remote')] += 1
    w('## Compute and improvements by source\n')
    w('| source | cores | attempts | improvements merged |')
    w('|---|---|---|---|')
    w(f"| cloud machine (2 workers) | 2 | {len(cloud):,} | {imp_by['cloud']:,} |")
    w(f"| laptop (2 workers, bounded runs) | 2 | {f'{lap:,}' if lap is not None else 'n/a'} | {imp_by['laptop']:,} |")
    w(f"| GitHub Actions ({len(act_runs)} runs x 4 jobs x 4 workers, 25 min) | 16 per run | {act_att:,} | {imp_by['actions']:,} |")
    tot_att = len(cloud) + (lap or 0) + act_att
    w(f"| **total** | | **{tot_att:,}** | **{sum(imp_by.values()):,}** |\n")
    w('Laptop and Actions improvements are counted when merged (one merge can contain several steps made remotely); '
      'every merged packing was re-legalized here first.\n')
    # ---------------- per case change
    rows = []
    for k, b in now.items():
        s0 = snap['s'].get(f'{k[0]}:{k[1]}')
        if s0 is None: continue
        rows.append((k[0], k[1], s0, b['s'], (s0 - b['s']) / s0))
    improved = [r for r in rows if r[4] > 1e-12]
    w('## What changed\n')
    w(f"{len(improved)} of {len(rows)} cases have a smaller container than at {snap['local']}; "
      f"median shrink {100 * sorted(r[4] for r in improved)[len(improved) // 2]:.3f}%, "
      f"largest {100 * max(r[4] for r in improved):.2f}%.\n")
    w('| problem | cases improved | median shrink | largest shrink (n: before → after) |')
    w('|---|---|---|---|')
    for p in PID:
        rp = [r for r in improved if r[0] == p]
        if not rp: w(f'| {TITLE[p]} | 0 | | |'); continue
        big = max(rp, key=lambda r: r[4])
        w(f"| {TITLE[p]} | {len(rp)} / {NMAX - NMIN + 1} | {100 * sorted(r[4] for r in rp)[len(rp) // 2]:.3f}% | "
          f"{100 * big[4]:.2f}% (n = {big[1]}: {big[2]:.5f} → {big[3]:.5f}) |")
    w('')
    w('### The 15 largest improvements\n')
    w('| problem | n | before | after | shrink |')
    w('|---|---|---|---|---|')
    for r in sorted(improved, key=lambda r: -r[4])[:15]:
        w(f'| {TITLE[r[0]]} | {r[1]} | {r[2]:.5f} | {r[3]:.5f} | {100 * r[4]:.2f}% |')
    w('')
    # ---------------- literature
    w('## Against published values\n')
    for p in REF:
        if p.startswith('_'): continue
        before = collections.Counter(); after = collections.Counter(); changed = []
        for n_s, (ref, src) in REF[p].items():
            n = int(n_s); s0 = snap['s'].get(f'{p}:{n}'); s1 = now.get((p, n), {}).get('s')
            if s0 is None or s1 is None: continue
            c0, c1 = compare(s0, ref), compare(s1, ref)
            before[c0] += 1; after[c1] += 1
            if c0 != c1: changed.append(f'n = {n}: {c0} → {c1} ({s1:.5f} vs {ref:.5f})')
        w(f"**{TITLE[p]}**: better {before['better']} → **{after['better']}**, equal {before['equal']} → {after['equal']}, "
          f"behind {before['behind']} → {after['behind']}.")
        for c in changed: w(f'- {c}')
        w('')
    w('(Comparison on the touching limits; certified records add 1e-7 clearance.)\n')
    # ---------------- rate over time
    w('## Improvements per hour\n')
    per = collections.Counter()
    for a in att:
        if a['improved']: per[int((a['t'] - t0) // 3600)] += 1
    w('| hour | improvements |')
    w('|---|---|')
    for h in range(int(hours) + 1):
        w(f"| {time.strftime('%H:%M', time.localtime(t0 + 3600 * h))} | {per.get(h, 0)} |")
    w('')
    w('(The last row is a partial hour.)\n')
    # ---------------- where the cloud compute went
    band = lambda n: '2–10' if n <= 10 else ('11–20' if n <= 20 else ('21–30' if n <= 30 else '31–40'))
    sec = collections.defaultdict(float); cnt = collections.Counter(); imp = collections.Counter()
    for a in cloud:
        k = ('hop' if a['move'] == 'hop' else 'other moves', band(a['n']))
        sec[k] += a.get('secs', 0); cnt[k] += 1; imp[k] += a['improved']
    tot = sum(sec.values()) or 1
    w('## Where the compute went (cloud workers, which log every attempt)\n')
    w('"other moves" = ascend, descend, reinsert, fresh start, tighten.\n')
    w('| move | n | attempts | CPU-hours | share of CPU | improvements | improvements per CPU-hour |')
    w('|---|---|---|---|---|---|---|')
    for k in sorted(sec, key=lambda k: (k[0], int(k[1].split('–')[0]))):
        w(f"| {k[0]} | {k[1]} | {cnt[k]:,} | {sec[k] / 3600:.1f} | {100 * sec[k] / tot:.0f}% | {imp[k]} | "
          f"{imp[k] / max(sec[k] / 3600, 1e-9):.1f} |")
    w('')
    msec = collections.defaultdict(float); mimp = collections.Counter(); mcnt = collections.Counter()
    for a in cloud: msec[a['move']] += a.get('secs', 0); mimp[a['move']] += a['improved']; mcnt[a['move']] += 1
    w('| move | attempts | CPU-hours | improvements | improvements per CPU-hour |')
    w('|---|---|---|---|---|')
    for m in sorted(msec, key=lambda m: -msec[m]):
        w(f"| {m} | {mcnt[m]:,} | {msec[m] / 3600:.1f} | {mimp[m]} | {mimp[m] / max(msec[m] / 3600, 1e-9):.1f} |")
    w('')
    # ---------------- size of the improvements
    w('## Size of the improvements\n')
    w('Relative shrink of each improvement step (cloud steps and remote merges).\n')
    w('| period | steps | > 0.1% | 0.001–0.1% | ≤ 0.001% | median |')
    w('|---|---|---|---|---|---|')
    steps = [a for a in att if a['improved'] and a.get('best_before') and a.get('s')]
    edges = list(range(0, int(hours) + 1, 4)) + [hours]
    for lo, hi in zip(edges[:-1], edges[1:]):
        g = sorted((a['best_before'] - a['s']) / a['best_before'] for a in steps if t0 + lo * 3600 <= a['t'] < t0 + hi * 3600)
        if not g: continue
        w(f"| {time.strftime('%H:%M', time.localtime(t0 + lo * 3600))}–{time.strftime('%H:%M', time.localtime(t0 + hi * 3600))} | "
          f"{len(g)} | {sum(x > 1e-3 for x in g)} | {sum(1e-5 < x <= 1e-3 for x in g)} | {sum(x <= 1e-5 for x in g)} | "
          f"{100 * g[len(g) // 2]:.4f}% |")
    big = collections.Counter((a.get('host', 'remote') if a['move'] == 'harvest' else 'cloud') for a in steps
                              if (a['best_before'] - a['s']) / a['best_before'] > 1e-3)
    w('')
    w('Steps larger than 0.1% by source: ' + ', '.join(f'{k} {v}' for k, v in big.most_common()) +
      ' (a remote merge can bundle several steps, which favours the remote sources here).\n')
    # ---------------- stalled
    last = {}
    for a in att:
        if a['improved']: last[(a['p'], a['n'])] = max(last.get((a['p'], a['n']), 0), a['t'])
    stalled = [k for k in now if k not in last]
    w('## Cases that did not move\n')
    w(f"{len(stalled)} cases had no improvement during the period. By problem:\n")
    for p in PID:
        ns = sorted(n for q, n in stalled if q == p)
        w(f"- {TITLE[p]}: {len(ns)} ({', '.join(map(str, ns)) if ns else 'none'})")
    w('')
    text = '\n'.join(L)
    if out: open(out, 'w').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
