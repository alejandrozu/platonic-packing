#!/usr/bin/env python3
"""Data appendices of the final report (docs/FINAL_REPORT.md): every record, every improvement step of every case,
and statistics over all attempts. Reads only: state/best, state/attempts.jsonl, state/actions_log.jsonl,
state/snapshot_2026-10-11_0322.json, records/*, docs/references.json, and records/SUMMARY.csv as of the end of the
first night (git commit ded8b86).

usage: python3 scripts/report_data.py > appendix.md"""
import json, os, sys, glob, math, time, collections, subprocess, csv, io, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PID = ['tetintet', 'octinoct', 'icoinico', 'dodindod', 'cubincub', 'cubinoct', 'octincub', 'dodinico', 'icoindod']
TITLE = {'tetintet': 'Tetrahedra in a tetrahedron', 'octinoct': 'Octahedra in an octahedron',
         'icoinico': 'Icosahedra in an icosahedron', 'dodindod': 'Dodecahedra in a dodecahedron',
         'cubincub': 'Cubes in a cube', 'cubinoct': 'Cubes in an octahedron', 'octincub': 'Octahedra in a cube',
         'dodinico': 'Dodecahedra in an icosahedron', 'icoindod': 'Icosahedra in a dodecahedron'}
OLD = {'tetrahedron': 'tetintet', 'octahedron': 'octinoct', 'icosahedron': 'icoinico', 'dodecahedron': 'dodindod'}
NS = range(2, 41)
lt = lambda t: time.strftime('%d %b %H:%M', time.localtime(t))
out = []
w = out.append

# ------------------------------------------------------------------ load
best = {}
for p in PID:
    for n in NS:
        best[(p, n)] = json.load(open(f'state/best/{p}/n{n:02d}.json'))
rec = {}
for p in PID:
    for n in NS:
        f = f'records/{p}/{p}_n{n:02d}.json'
        if os.path.exists(f): rec[(p, n)] = {k: v for k, v in json.load(open(f)).items() if k != 'pieces'}
derived = {}
for r in csv.DictReader(open('records/SUMMARY.csv')):
    derived[(r['problem'], int(r['n']))] = r.get('derived') == 'True'
cert = {}
for (p, n) in rec:
    try: cert[(p, n)] = 'CERTIFIED' in open(f'records/{p}/{p}_n{n:02d}.certify.txt').read()
    except OSError: cert[(p, n)] = None
att = []
for l in open('state/attempts.jsonl'):
    try: att.append(json.loads(l))
    except Exception: pass
att.sort(key=lambda a: a['t'])
snap = json.load(open('state/snapshot_2026-10-11_0322.json'))
REF = json.load(open('docs/references.json'))
night1 = {}
try:
    txt = subprocess.run(['git', 'show', 'ded8b86:records/SUMMARY.csv'], capture_output=True, text=True).stdout
    for r in csv.DictReader(io.StringIO(txt)):
        night1[(OLD.get(r['piece'], r['piece']), int(r['n']))] = float(r['s_tight'])
except Exception:
    pass
act = [json.loads(l) for l in open('state/actions_log.jsonl')] if os.path.exists('state/actions_log.jsonl') else []

imps = collections.defaultdict(list)
first = {}
for a in att:
    k = (a['p'], a['n'])
    if k not in first:
        if a.get('best_before'): first[k] = (a['t'], a['best_before'], 'archive')
        elif a['improved'] and a.get('s') is not None: first[k] = (a['t'], a['s'], a['move'])
    if a['improved']: imps[k].append(a)


def src_label(s):
    if not s: return ''
    m = s.get('move', '')
    m = {'import': 'night-1 batch run (imported 9 Oct 11:56)', 'monotone': 'monotone fill'}.get(m, m)
    bits = [m]
    if s.get('var'): bits.append(s['var'])
    if s.get('from') and m == 'hop': bits.append('from ' + str(s['from']))
    if s.get('host'): bits.append('on ' + s['host'])
    if s.get('literature') or s.get('source'): bits.append('published: ' + str(s.get('source') or s.get('literature'))[:40])
    return ', '.join(bits)


# ------------------------------------------------------------------ A. records
w('## Appendix A. Every record (final state, 11 Oct 2026 17:39)\n')
w('Columns: **s_full** is the certified container edge (10⁻⁷ clearance, rounded up at the 13th decimal); **s_tight** '
  'the touching limit from the tightening; **closed form** a conjecture from 12-digit numerics; **density** the '
  'fraction of the container volume filled; **vol. bound** the volume lower bound (n·vol B / vol A)^{1/3}; '
  '**cert.** whether the exact certificate passed. "Found by" is the move that produced the current packing '
  '(hop variant, start, machine); "derived" marks packings obtained from the n + 1 packing by deleting a piece.\n')
ncert = sum(1 for v in cert.values() if v)
w(f'{len(rec)} record files, {ncert} with a passing exact certificate.\n')
for p in PID:
    w(f'### A.{PID.index(p) + 1} {TITLE[p]} (`{p}`)\n')
    w('| n | s_full | s_tight | closed form | density | vol. bound | cert. | found by | found |')
    w('|---:|---|---|---|---|---|---|---|---|')
    for n in NS:
        r = rec.get((p, n), {}); b = best[(p, n)]['best']
        cf = r.get('closed_form_conjecture') or ''
        dens = r.get('density'); vb = r.get('volume_lower_bound')
        der = ' — record derived from the n + 1 record' if derived.get((p, n)) else ''
        w(f"| {n} | {r.get('s_full', float('nan')):.13f} | {r.get('s_tight', b['s']):.12f} | {cf} | "
          f"{'' if dens is None else f'{dens:.4f}'} | {'' if vb is None else f'{vb:.5f}'} | "
          f"{'yes' if cert.get((p, n)) else 'NO'} | {src_label(b.get('src'))}{der} | {lt(b['t']) if b.get('t') else ''} |")
    w('')
    w(f'**Search history of each case ({TITLE[p]}).** "first" = the archive value when the engine first worked on '
      f'the case (9 Oct from 12:02; for n ≤ 20 same-solid cases this is the night-1 value imported at 11:56); "night 1" = the record at the end of the first night (9 Oct 08:12, same-solid problems n ≤ 20 only); '
      f'"11 Oct 03:23" = the baseline of the 14-hour run; "final" = touching limit now. Attempts and CPU time are the '
      f'cloud workers\' (laptop and Actions attempts are not logged per case); improvements include merged remote '
      f'results.\n')
    w('| n | first | night 1 | 11 Oct 03:23 | final | total shrink | attempts | CPU min | improvements | last improvement |')
    w('|---:|---|---|---|---|---|---|---|---|---|')
    for n in NS:
        b = best[(p, n)]; st = b.get('stats', {})
        f0 = first.get((p, n)); s0 = snap['s'].get(f'{p}:{n}')
        fin = b['best']['s']
        tot = (f0[1] - fin) / f0[1] * 100 if f0 else float('nan')
        cpu = sum(a.get('secs', 0) for a in att if a['p'] == p and a['n'] == n and a['move'] != 'harvest') / 60
        last = imps[(p, n)][-1]['t'] if imps[(p, n)] else None
        nn1 = night1.get((p, n))
        w(f"| {n} | {f0[1]:.6f} | {'' if nn1 is None else f'{nn1:.6f}'} | {'' if s0 is None else f'{s0:.6f}'} | "
          f"{fin:.6f} | {tot:.3f}% | {st.get('attempts', 0)} | {cpu:.0f} | {len(imps[(p, n)])} | "
          f"{lt(last) if last else '—'} |" if f0 else f"| {n} | | | | {fin:.6f} | | | | | |")
    w('')
    w(f'**Attempts and successes by move for each case ({TITLE[p]})**, from the archive statistics '
      f'(attempts / improvements).\n')
    w('| n | hop | reinsert | fresh | ascend | descend | tighten | gate | since last improvement |')
    w('|---:|---|---|---|---|---|---|---|---|')
    for n in NS:
        st = best[(p, n)].get('stats', {}); mv = st.get('moves', {})
        cell = lambda m: f"{mv[m][0]} / {mv[m][1]}" if m in mv else '—'
        w(f"| {n} | {cell('hop')} | {cell('reinsert')} | {cell('fresh')} | {cell('ascend')} | {cell('descend')} | "
          f"{cell('tighten')} | {st.get('gate', 0):.4f} | {st.get('since', '')} |")
    w('')

# ------------------------------------------------------------------ A'. literature
w('## Appendix B. Against every published value\n')
w('Published values from Erich Friedman\'s Packing Center (cubes in a cube: Friedman 1998 and later entries; octahedra '
  'in a cube: R. Walsh, June 2026, and H. Lin, July 2026) and Y. Nakajima (12 cubes, Oct 2026); `docs/references.json`. '
  'Comparison on the touching limit with a 10⁻⁵ tolerance (Friedman\'s values are 5-decimal truncations). '
  '"first passed" is the first time the archive reached or beat the published value.\n')
for p in [q for q in REF if not q.startswith('_')]:
    w(f'### {TITLE[p]}\n')
    w('| n | published | source | ours (touching) | difference | status | first reached / passed |')
    w('|---:|---|---|---|---|---|---|')
    for n_s, (ref, src) in sorted(REF[p].items(), key=lambda x: int(x[0])):
        n = int(n_s)
        if (p, n) not in best: continue
        s = best[(p, n)]['best']['s']
        stt = 'better' if s < ref - 1e-5 else ('equal' if s <= ref + 1e-5 else 'behind')
        reached = next((a['t'] for a in imps[(p, n)] if a['s'] <= ref + 1e-5), None)
        if reached is None and first.get((p, n)) and first[(p, n)][1] <= ref + 1e-5: reached = first[(p, n)][0]
        w(f"| {n} | {ref:.6f} | {src} | {s:.6f} | {100 * (s - ref) / ref:+.3f}% | {stt} | {lt(reached) if reached else '—'} |")
    w('')

# ------------------------------------------------------------------ C. statistics
cloud = [a for a in att if a['move'] != 'harvest']
harv = [a for a in att if a['move'] == 'harvest']
w('## Appendix C. Statistics over every attempt\n')
w(f"The cloud workers logged {len(cloud):,} attempts ({sum(a.get('secs', 0) for a in cloud) / 3600:.1f} CPU-hours) "
  f"from {lt(cloud[0]['t'])} to {lt(cloud[-1]['t'])}; {len(harv):,} merges of remote results (laptop "
  f"{sum(1 for a in harv if a.get('host') == 'laptop')}, GitHub Actions {sum(1 for a in harv if a.get('host') == 'actions')}, "
  f"other {sum(1 for a in harv if a.get('host') not in ('laptop', 'actions'))}) are logged with move 'harvest'. "
  f"An attempt is one move on one case: perturb or build, re-sharpen, legalize, and tighten if the raw result is within "
  f"the case's gate. 'Improved' means the archive's best for that case got smaller.\n")
MOVES = ['hop', 'reinsert', 'fresh', 'ascend', 'descend', 'tighten']
w('### C.1 By problem and move (cloud workers)\n')
w('| problem | move | attempts | improvements | success rate | CPU-hours | improvements per CPU-hour |')
w('|---|---|---|---|---|---|---|')
for p in PID:
    for m in MOVES:
        xs = [a for a in cloud if a['p'] == p and a['move'] == m]
        if not xs: continue
        i = sum(a['improved'] for a in xs); h = sum(a.get('secs', 0) for a in xs) / 3600
        w(f"| {p} | {m} | {len(xs):,} | {i} | {100 * i / len(xs):.1f}% | {h:.2f} | {i / max(h, 1e-9):.1f} |")
    xs = [a for a in cloud if a['p'] == p]; i = sum(a['improved'] for a in xs); h = sum(a.get('secs', 0) for a in xs) / 3600
    w(f"| **{p}** | **all** | **{len(xs):,}** | **{i}** | {100 * i / len(xs):.1f}% | **{h:.2f}** | {i / max(h, 1e-9):.1f} |")
w('')
w('### C.2 By size of n and move (cloud workers)\n')
band = lambda n: '2–10' if n <= 10 else ('11–20' if n <= 20 else ('21–30' if n <= 30 else '31–40'))
w('| n | move | attempts | improvements | CPU-hours | improvements per CPU-hour | mean seconds per attempt |')
w('|---|---|---|---|---|---|---|')
for bd in ['2–10', '11–20', '21–30', '31–40']:
    for m in MOVES:
        xs = [a for a in cloud if band(a['n']) == bd and a['move'] == m]
        if not xs: continue
        i = sum(a['improved'] for a in xs); h = sum(a.get('secs', 0) for a in xs) / 3600
        w(f"| {bd} | {m} | {len(xs):,} | {i} | {h:.2f} | {i / max(h, 1e-9):.1f} | {3600 * h / len(xs):.1f} |")
w('')
w('### C.3 Over time (cloud workers, 4-hour blocks; remote merges shown separately)\n')
w('| block starting | attempts | CPU-hours | improvements | of which > 0.1% | median step | remote merges (improving) |')
w('|---|---|---|---|---|---|---|')
t0 = att[0]['t']; t1 = att[-1]['t']
b0 = t0 - (t0 % 3600)
for s in range(int(b0), int(t1) + 1, 4 * 3600):
    xs = [a for a in cloud if s <= a['t'] < s + 4 * 3600]
    hs = [a for a in harv if s <= a['t'] < s + 4 * 3600 and a['improved']]
    if not xs and not hs: continue
    st = [(a['best_before'] - a['s']) / a['best_before'] for a in xs if a['improved'] and a.get('best_before')]
    med = f'{100 * statistics.median(st):.4f}%' if st else ''
    w(f"| {lt(s)} | {len(xs):,} | {sum(a.get('secs', 0) for a in xs) / 3600:.2f} | {sum(a['improved'] for a in xs)} | "
      f"{sum(x > 1e-3 for x in st)} | {med} | {len(hs)} |")
w('')
w('### C.4 Hop size (minDiff: the relative rearrangement a hop must reach before re-sharpening)\n')
w('Policy periods: until 10 Oct 19:14 the default hop (minDiff 0.04–0.6); 19:14–20:14 the settings experiment (five '
  'variants); from 20:14 the "gentle" hop (minDiff 0.02–0.10).\n')
w('| minDiff | hops | improvements | rate | CPU-hours | improvements per CPU-hour |')
w('|---|---|---|---|---|---|')
bins = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3, 0.45, 0.61]
hops = [a for a in cloud if a['move'] == 'hop' and a.get('minDiff') is not None]
for lo, hi in zip(bins[:-1], bins[1:]):
    xs = [a for a in hops if lo <= a['minDiff'] < hi]
    if not xs: continue
    i = sum(a['improved'] for a in xs); h = sum(a.get('secs', 0) for a in xs) / 3600
    w(f"| {lo:.2f}–{hi:.2f} | {len(xs):,} | {i} | {100 * i / len(xs):.1f}% | {h:.2f} | {i / max(h, 1e-9):.1f} |")
w('')
w('### C.5 Hop start, variant and focus\n')
w('| group | hops | improvements | CPU-hours | improvements per CPU-hour |')
w('|---|---|---|---|---|')
groups = collections.OrderedDict()
for a in [a for a in cloud if a['move'] == 'hop']:
    groups.setdefault(f"start: {a.get('from', 'unknown')}", []).append(a)
for a in [a for a in cloud if a['move'] == 'hop']:
    groups.setdefault(f"variant: {a.get('var', 'none (before 10 Oct 19:14)')}", []).append(a)
for a in [a for a in cloud if a['move'] == 'hop']:
    groups.setdefault('cluster (focused) hop' if a.get('focus') else 'global hop', []).append(a)
for g, xs in groups.items():
    i = sum(a['improved'] for a in xs); h = sum(a.get('secs', 0) for a in xs) / 3600
    w(f"| {g} | {len(xs):,} | {i} | {h:.2f} | {i / max(h, 1e-9):.1f} |")
w('')
w('### C.6 The attempts that did not improve: how close they came\n')
w('For every attempt that did not improve its case: the relative excess (result − best) / best of its container over the '
  'best known at that moment. "Tightened" attempts are measured after tightening; attempts whose raw result was outside '
  'the case\'s gate were not tightened and are measured on the raw (legalized) result.\n')
w('| move | stage | attempts | < 10⁻⁶ (same basin) | 10⁻⁶–10⁻⁴ | 10⁻⁴–10⁻³ | 10⁻³–10⁻² | 10⁻²–10⁻¹ | > 10⁻¹ |')
w('|---|---|---|---|---|---|---|---|---|')
for m in MOVES:
    xs = [a for a in cloud if a['move'] == m and not a['improved'] and a.get('best_before')]
    for stage in ('tightened', 'raw only (outside gate)'):
        ys = [a for a in xs if (a.get('s') is not None) == (stage == 'tightened')]
        vals = [((a['s'] if a.get('s') is not None else a.get('raw')) - a['best_before']) / a['best_before'] for a in ys
                if (a.get('s') is not None or a.get('raw') is not None)]
        if not vals: continue
        c = collections.Counter('a' if d < 1e-6 else 'b' if d < 1e-4 else 'c' if d < 1e-3 else 'd' if d < 1e-2 else
                                'e' if d < 1e-1 else 'f' for d in vals)
        tot = len(vals)
        pc = lambda k: f"{c[k]:,} ({100 * c[k] / tot:.0f}%)"
        w(f"| {m} | {stage} | {tot:,} | {pc('a')} | {pc('b')} | {pc('c')} | {pc('d')} | {pc('e')} | {pc('f')} |")
w('')
w('### C.7 What tightening adds\n')
w('Relative gain of the tightening over the raw (legalized) result of the dynamics, (raw − tightened) / raw, for '
  'attempts that were tightened (raw above the result). Tightening runs only when the raw result is within the gate.\n')
w('| move | tightened | median gain | 90th percentile | max |')
w('|---|---|---|---|---|')
for m in MOVES:
    g = sorted((a['raw'] - a['s']) / a['raw'] for a in cloud if a['move'] == m and a.get('raw') and a.get('s')
               and a['raw'] > a['s'] + 1e-15)
    if not g: continue
    w(f"| {m} | {len(g):,} | {100 * g[len(g) // 2]:.4f}% | {100 * g[int(0.9 * len(g))]:.3f}% | {100 * g[-1]:.2f}% |")
w('')
w('### C.8 Time per attempt\n')
w('| problem | n | attempts | mean seconds | of which dynamics (raw) | median seconds |')
w('|---|---|---|---|---|---|')
for p in PID:
    for bd in ['2–10', '11–20', '21–30', '31–40']:
        xs = [a for a in cloud if a['p'] == p and band(a['n']) == bd]
        if not xs: continue
        se = [a.get('secs', 0) for a in xs]; rs = [a.get('raw_secs', 0) or 0 for a in xs]
        w(f"| {p} | {bd} | {len(xs):,} | {sum(se) / len(se):.1f} | {sum(rs) / len(rs):.1f} | {sorted(se)[len(se) // 2]:.1f} |")
w('')
w('### C.9 GitHub Actions runs\n')
w('Each run: 4 jobs × 4 workers for 25 minutes on GitHub-hosted runners; the results were merged (re-legalized) by the '
  '10-minute cycle. Attempt counts of the early runs were reconstructed from the 10-minute reports.\n')
w('| # | time (local; start for the reconstructed runs, merge time for the others) | attempts | improvements merged | note |')
w('|---|---|---|---|---|')
for i, r in enumerate(act, 1):
    w(f"| {i} | {r.get('started') or r.get('local', '')} | {r.get('attempts', 0):,} | {r.get('merged', 0)} | {r.get('note', '')} |")
w(f"| | **total** | **{sum(r.get('attempts', 0) for r in act):,}** | **{sum(r.get('merged', 0) for r in act)}** | |")
w('')

# ------------------------------------------------------------------ D. every improvement
w('## Appendix D. Every improvement step of every case\n')
w('One line per improvement of the archive, oldest first: local time, move (hop variant, start, or the machine for '
  'merged remote results), the new touching limit, and the shrink relative to the previous best. The first line of '
  'each case is the first packing the engine accepted (no previous best). Cases are listed in table order.\n')
for p in PID:
    w(f'### D.{PID.index(p) + 1} {TITLE[p]}\n')
    for n in NS:
        xs = imps[(p, n)]
        w(f'**n = {n}** — {len(xs)} improvement steps, final {best[(p, n)]["best"]["s"]:.12f}\n')
        if not xs: w(''); continue
        lines = []
        for a in xs:
            mv = a['move']
            if mv == 'harvest': mv = f"merged from {a.get('host', 'remote')}"
            elif mv == 'hop' and a.get('var'): mv = f"hop ({a['var']}{', pool' if a.get('from') == 'pool' else ''})"
            g = f" (−{100 * (a['best_before'] - a['s']) / a['best_before']:.4f}%)" if a.get('best_before') else ' (first)'
            lines.append(f"{lt(a['t'])} {mv} → {a['s']:.10f}{g}")
        w('<details><summary>show the steps</summary>\n')
        w('\n'.join('- ' + x for x in lines))
        w('\n</details>\n')
print('\n'.join(out))
