#!/usr/bin/env python3
"""Data and statistics for the second phase of the report (Archimedean, Catalan, prism and antiprism families,
12-13 Oct 2026): writes markdown sections to stdout (or to a file given as argv[1]).

Sources: state/attempts.jsonl (every cloud attempt and every harvested remote improvement, with time, case, move,
host), state/best (the archive, including attempt totals reported by remote machines), records/ (the final record
files with certificates), and the git history (the records as published at 12 Oct 22:31, before the night search).
Everything here is recomputed from those files; nothing is typed in by hand."""
import json, os, sys, glob, subprocess, statistics, collections, math, datetime, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from engine import FAM, PID, total_attempts
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
EXACT = json.load(open(os.path.join(ROOT, 'src', 'solids_exact.json')))
FAMS = ['archimedean', 'catalan', 'prisms']
NEW = [p for p in PID if FAM[p] in FAMS]
T_START = datetime.datetime(2026, 10, 12, 16, 53).timestamp()      # Alejandro's request
T_NIGHT = datetime.datetime(2026, 10, 13, 1, 38).timestamp()       # restart of the night search
T_EVENING_PUBLISH = 'c1bf7810'                                     # records as published at 12 Oct 22:31
POLY = {3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal'}


def disp(s):
    for pre in ('antiprism', 'prism'):
        if s.startswith(pre) and s[len(pre):].isdigit(): return f'{POLY[int(s[len(pre):])]} {pre}'
    return s.replace('_', ' ')


def plural(s):
    w = disp(s); return w[:-6] + 'hedra' if w.endswith('hedron') else w + 's'


def title(p):
    pc, cc = PID[p]; c = disp(cc)
    return f"{plural(pc)[0].upper() + plural(pc)[1:]} in {'an' if c[0] in 'aeiou' else 'a'} {c}"


def hm(t): return datetime.datetime.fromtimestamp(t).strftime('%d %b %H:%M')


def table(head, rows, align=None):
    align = align or ['---'] * len(head)
    out = ['| ' + ' | '.join(head) + ' |', '|' + '|'.join(align) + '|']
    out += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
    return '\n'.join(out)


def load_log():
    L = []
    for l in open(os.path.join(ROOT, 'state', 'attempts.jsonl')):
        try: a = json.loads(l)
        except json.JSONDecodeError: continue
        if a['p'] in FAM and FAM[a['p']] in FAMS and a['t'] >= T_START: L.append(a)
    return L


def load_records(rev=None):
    recs = {}
    if rev is None:
        for f in glob.glob(os.path.join(ROOT, 'records', '*', '*_n[0-9][0-9].json')):
            r = json.load(open(f)); p = r['record_id'].split('_')[0]
            if p in NEW: recs[(p, r['n'])] = r
        return recs
    names = subprocess.run(['git', '-C', ROOT, 'ls-tree', '-r', '--name-only', rev, 'records'], capture_output=True, text=True).stdout.split()
    want = [x for x in names if re.match(r'records/[a-z0-9]+/[a-z0-9]+_n\d\d\.json$', x) and x.split('/')[1] in NEW]
    # one git cat-file --batch call for all files
    inp = ''.join(f'{rev}:{x}\n' for x in want)
    out = subprocess.run(['git', '-C', ROOT, 'cat-file', '--batch'], input=inp.encode(), capture_output=True).stdout
    i = 0
    while i < len(out):
        j = out.index(b'\n', i); hdr = out[i:j].split(); size = int(hdr[2])
        r = json.loads(out[j + 1:j + 1 + size]); i = j + 1 + size + 1
        recs[(r['record_id'].split('_')[0], r['n'])] = r
    return recs


def main():
    L = load_log(); final = load_records(); evening = load_records(T_EVENING_PUBLISH)
    best = {}
    for p in NEW:
        for n in range(2, 41):
            f = os.path.join(ROOT, 'state', 'best', p, f'n{n:02d}.json')
            if os.path.exists(f): best[(p, n)] = json.load(open(f))
    S = []                                                     # output sections
    w = S.append

    # ---------------------------------------------------------------- totals
    cloud = [a for a in L if a['move'] != 'harvest']
    harv = [a for a in L if a['move'] == 'harvest']
    rem = collections.Counter()
    for c in best.values():
        st = c.get('stats', {})
        rem['cloud'] += st.get('attempts', 0)
        rem['actions'] += st.get('attempts_remote', 0)
        for h, v in (st.get('remote') or {}).items(): rem[h] += v
    tot_att = sum(total_attempts(c.get('stats', {})) for c in best.values())
    imp_cloud = sum(1 for a in cloud if a.get('improved'))
    imp_h = collections.Counter(a.get('host', 'remote') for a in harv if a.get('improved'))
    w('### Totals\n')
    w(table(['quantity', 'value'], [
        ['problems / cases', f'{len(NEW)} / {len(NEW) * 39:,}'],
        ['record files (final)', f'{len(final):,}'],
        ['records certified exactly', f"{sum(1 for (p, n), r in final.items() if _cert_ok(p, n)):,}"],
        ['attempts on all machines (archive totals)', f'{tot_att:,}'],
        ['  of which cloud workers (archive counter)', f"{rem['cloud']:,}"],
        ['  of which GitHub Actions jobs', f"{rem['actions']:,}"],
        ['  of which the laptop', f"{rem['laptop']:,}"],
        ['cloud attempts in the log since 12 Oct 16:53', f'{len(cloud):,}'],
        ['improvements of the archive (cloud attempts)', f'{imp_cloud:,}'],
        ['improvements harvested from GitHub Actions', f"{imp_h['actions']:,}"],
        ['improvements harvested from the laptop', f"{imp_h['laptop']:,}"],
    ], ['---', '---:']) + '\n')

    # ---------------------------------------------------------------- GitHub Actions runs (state/actions_log.jsonl)
    runs = []
    for l in open(os.path.join(ROOT, 'state', 'actions_log.jsonl')):
        try: a = json.loads(l)
        except json.JSONDecodeError: continue
        if a.get('t', 0) < T_START: continue
        if runs and a['t'] - runs[-1]['t1'] < 1800:            # late jobs of the same run
            r = runs[-1]; r['jobs'] += a['jobs']; r['att'] += a['attempts']; r['merged'] += a['merged']; r['t1'] = a['t']
        else: runs.append({'t0': a['t'], 't1': a['t'], 'jobs': a['jobs'], 'att': a['attempts'], 'merged': a['merged']})
    w('### GitHub Actions runs\n')
    w('Each run: 4 jobs × 4 workers × 50 minutes ("medium"), started from the archive in `main`; results merged by the '
      'cycle when the jobs finish (late jobs are merged a few minutes later and are counted with their run here).\n')
    w(table(['run', 'merged at', 'jobs', 'attempts', 'new bests merged', 'new bests per 100 attempts'],
            [[i + 1, hm(r['t0']), r['jobs'], f"{r['att']:,}", f"{r['merged']:,}", f"{100 * r['merged'] / max(1, r['att']):.0f}"] for i, r in enumerate(runs)],
            ['---:', '---', '---:', '---:', '---:', '---:']) + '\n')
    w(f"Total: {sum(r['att'] for r in runs):,} attempts and {sum(r['merged'] for r in runs):,} merged improvements in {len(runs)} runs.\n")

    # ---------------------------------------------------------------- coverage timeline (first packing of each case)
    first = {}
    for a in L:
        k = (a['p'], a['n'])
        if a.get('improved') and k not in first: first[k] = a
    marks = [(16, 53), (17, 30), (18, 0), (18, 30), (19, 0), (19, 30), (20, 0), (20, 30), (21, 0), (21, 30), (22, 0)]
    rows = []
    for h, m in marks:
        t = datetime.datetime(2026, 10, 12, h, m).timestamp()
        c = collections.Counter(FAM[p] for (p, n), a in first.items() if a['t'] <= t)
        rows.append([f'12 Oct {h:02d}:{m:02d}', c['archimedean'], c['catalan'], c['prisms'], sum(c.values())])
    w('### Coverage: cases with a packing over time\n')
    w(table(['time', 'Archimedean (of 507)', 'Catalan (of 507)', 'prisms (of 780)', 'all (of 1,794)'], rows, ['---', '---:', '---:', '---:', '---:']) + '\n')
    last = max(first.values(), key=lambda a: a['t']) if first else None
    if last: w(f"The last case to receive a packing was `{last['p']}_n{last['n']:02d}` at {hm(last['t'])}. "
               f"First packings by origin: " + ', '.join(f'{k} {v}' for k, v in collections.Counter(a.get('host', 'cloud') if a['move'] == 'harvest' else 'cloud' for a in first.values()).most_common()) + '.\n')

    # ---------------------------------------------------------------- activity by hour
    hours = collections.OrderedDict()
    for a in L:
        hkey = datetime.datetime.fromtimestamp(a['t']).strftime('%d %b %H:00')
        d = hours.setdefault(hkey, collections.Counter())
        if a['move'] == 'harvest':
            if a.get('improved'): d['h_' + a.get('host', 'remote')] += 1
        else:
            d['att'] += 1; d['imp'] += bool(a.get('improved'))
    w('### Activity by hour\n')
    w('Cloud attempts and their improvements, and improvements merged from the laptop and from GitHub Actions (remote '
      'attempts themselves are only reported as totals, see above). Hours without entries had no workers running.\n')
    w(table(['hour (Paris)', 'cloud attempts', 'cloud new bests', 'laptop new bests', 'Actions new bests'],
            [[k, v['att'], v['imp'], v['h_laptop'], v['h_actions']] for k, v in hours.items()], ['---', '---:', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- moves (cloud log)
    mv = collections.defaultdict(lambda: [0, 0, []])
    for a in cloud:
        m = mv[a['move']]; m[0] += 1; m[1] += bool(a.get('improved'))
        if a.get('secs') is not None: m[2].append(a['secs'])
    w('### Moves on the cloud workers\n')
    w(table(['move', 'attempts', 'new bests', 'success rate', 'median time per attempt'],
            [[k, v[0], v[1], f'{100 * v[1] / v[0]:.1f}%', f"{statistics.median(v[2]):.0f} s" if v[2] else '—'] for k, v in sorted(mv.items(), key=lambda kv: -kv[1][0])],
            ['---', '---:', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- origin of the final records
    orig = collections.Counter(); origm = collections.Counter()
    for k, r in final.items():
        sr = r.get('search') or {}
        host = sr.get('host', 'cloud'); orig[host] += 1; origm[(host, sr.get('move', '?'))] += 1
    w('### Where the final records came from\n')
    w(table(['machine', 'records'], [[k, v] for k, v in orig.most_common()], ['---', '---:']) + '\n')
    moves = sorted({m for _, m in origm})
    w(table(['move \\ machine'] + [h for h, _ in orig.most_common()], [[m] + [origm[(h, m)] for h, _ in orig.most_common()] for m in moves],
            ['---'] + ['---:'] * len(orig)) + '\n')

    # ---------------------------------------------------------------- the night: evening publish vs final
    rows = []; allrel = []
    for fam in FAMS:
        rel = []
        for (p, n), r in final.items():
            if FAM[p] != fam or (p, n) not in evening: continue
            e = evening[(p, n)]['s_full']; f = r['s_full']
            if f < e - 1e-9: rel.append((e - f) / e)
        allrel += rel
        nfam = sum(1 for k in final if FAM[k[0]] == fam)
        rows.append([fam, f'{len(rel)} of {nfam}', f'{100 * statistics.median(rel):.3f}%' if rel else '—',
                     f'{100 * statistics.mean(rel):.3f}%' if rel else '—', f'{100 * max(rel):.2f}%' if rel else '—'])
    w('### What the night search changed (records of 12 Oct 22:31 against the final records)\n')
    w(table(['family', 'cases improved', 'median improvement', 'mean improvement', 'largest'], rows, ['---', '---:', '---:', '---:', '---:']) + '\n')
    big = sorted(((evening[k]['s_full'] - r['s_full']) / evening[k]['s_full'], k, evening[k]['s_full'], r['s_full']) for k, r in final.items() if k in evening)[::-1][:25]
    w('Largest relative improvements overnight:\n')
    w(table(['case', 's on 12 Oct 22:31', 's final', 'improvement'], [[f'`{k[0]}_n{k[1]:02d}`', f'{e:.5f}', f'{f:.5f}', f'{100 * d:.2f}%'] for d, k, e, f in big],
            ['---', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- from the first packing to the final record
    rows = []
    for fam in FAMS:
        rel = [(first[k]['s'] - final[k]['s_full']) / first[k]['s'] for k in final if FAM[k[0]] == fam and k in first and first[k]['s'] > final[k]['s_full']]
        rows.append([fam, len(rel), f'{100 * statistics.median(rel):.2f}%' if rel else '—', f'{100 * max(rel):.1f}%' if rel else '—'])
    w('### From the first packing of each case to its final record\n')
    w('The first packing of a case is usually a quick fill (an ascend from n − 1 or a fresh run); the search then '
      'improves it. Relative decrease of s (first packing in the log, touching limit, against the certified final value):\n')
    w(table(['family', 'cases', 'median decrease', 'largest'], rows, ['---', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- per-problem summary
    def st(k): r = final.get(k); return (r.get('s_tight') or r['s_full']) if r else None
    w('### Every problem at a glance\n')
    w('s(n) for selected n (certified value, 5 decimals truncated, "+" omitted), the density reached at n = 40, the number of '
      'n in 3–40 where s(n) = s(n − 1) to 1e-9 in the touching limits (the extra piece fits in the same container), and the number of '
      'closed forms recognised. Unit: container edge ÷ piece edge, or the ratio of sizes for Catalan solids.\n')
    rows = []
    for p in NEW:
        vals = [final[(p, n)]['s_plus'].rstrip('+') if (p, n) in final else '—' for n in (2, 3, 5, 10, 20, 30, 40)]
        plat = sum(1 for n in range(3, 41) if st((p, n)) is not None and st((p, n - 1)) is not None and abs(st((p, n)) - st((p, n - 1))) < 1e-9 * st((p, n)))
        cf = sum(1 for n in range(2, 41) if (p, n) in final and final[(p, n)].get('closed_form_conjecture'))
        den = final[(p, 40)]['density'] if (p, 40) in final else None
        rows.append([f'`{p}`', title(p)] + vals + [f'{den:.3f}' if den else '—', plat, cf])
    w(table(['id', 'problem', 's(2)', 's(3)', 's(5)', 's(10)', 's(20)', 's(30)', 's(40)', 'density n=40', 'plateaus', 'closed forms'], rows,
            ['---', '---', '---:', '---:', '---:', '---:', '---:', '---:', '---:', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- exact values: integers and closed forms
    ints = collections.defaultdict(list)
    for (p, n), r in sorted(final.items()):
        t = r.get('s_tight') or r['s_full']
        if abs(t - round(t)) < 1e-8: ints[p].append((n, int(round(t))))
    w('### Integer containers\n')
    w('Cases whose touching limit is an integer to 1e-8: n copies fit in a container exactly k times the piece. These '
      'are usually lattice or layer arrangements, and long runs of equal values are plateaus of s(n).\n')
    rows = []
    for p in NEW:
        if not ints[p]: continue
        by = collections.defaultdict(list)
        for n, k in ints[p]: by[k].append(n)
        rows.append([f'`{p}`', '; '.join(f'{k}: n = {_ranges(ns)}' for k, ns in sorted(by.items()))])
    w(table(['problem', 'integer value: n'], rows) + '\n')
    cfs = [(p, n, r['closed_form_conjecture']) for (p, n), r in sorted(final.items()) if r.get('closed_form_conjecture')]
    w(f'### Closed forms\n\n{len(cfs)} records have a recognised closed form (the touching limit agrees with a short expression in '
      'the field of the solid to about 11 digits; these are conjectures about the arrangement, not proofs of optimality). '
      'Integers are listed above; the others:\n')
    rows = [[f'`{p}_n{n:02d}`', f'{(final[(p, n)].get("s_tight") or final[(p, n)]["s_full"]):.10f}', cf] for p, n, cf in cfs if not re.fullmatch(r'\d+', cf.strip())]
    w(table(['record', 'touching limit', 'closed form'], rows, ['---', '---:', '---']) + '\n' if rows else '(none besides integers)\n')

    # ---------------------------------------------------------------- density
    w('### Density at n = 40\n')
    w('Density = n · vol(piece) / vol(container). The volume bound s ≥ (n · vol piece / vol container)^(1/3) is the only lower bound used; '
      'the ratio s / bound shows how far each record is from it.\n')
    rows = sorted(([f'`{p}`', f"{final[(p, 40)]['density']:.4f}", f"{final[(p, 40)]['s_full'] / final[(p, 40)]['volume_lower_bound']:.4f}"] for p in NEW if (p, 40) in final),
                  key=lambda r: -float(r[1]))
    w(table(['problem', 'density', 's / volume bound'], rows, ['---', '---:', '---:']) + '\n')
    for fam in FAMS:
        d = [final[(p, 40)]['density'] for p in NEW if FAM[p] == fam and (p, 40) in final]
        w(f'* {fam}: density at n = 40 from {min(d):.3f} to {max(d):.3f}, median {statistics.median(d):.3f}.')
    w('')

    # ---------------------------------------------------------------- prisms: in themselves vs in a cube
    w('### Prisms and antiprisms: in themselves against in a cube\n')
    w('s for the same pieces in their own shape and in a cube (both measured in piece edges). A cube is a better container '
      'when its s is smaller relative to the volume of the two containers, so the table also gives the densities.\n')
    rows = []
    for k in ('prism3', 'prism5', 'prism6', 'prism8', 'prism12', 'antiprism4', 'antiprism5', 'antiprism6', 'antiprism8', 'antiprism12'):
        a = next((p for p in NEW if PID[p] == (k, k)), None); b = next((p for p in NEW if PID[p] == (k, 'cube')), None)
        if not a or not b: continue
        for n in (4, 10, 20, 40):
            ra, rb = final.get((a, n)), final.get((b, n))
            if ra and rb: rows.append([disp(k), n, f"{ra['s_full']:.4f}", f"{ra['density']:.3f}", f"{rb['s_full']:.4f}", f"{rb['density']:.3f}"])
    w(table(['piece', 'n', 's in itself', 'density', 's in a cube', 'density'], rows, ['---', '---:', '---:', '---:', '---:', '---:']) + '\n')

    # ---------------------------------------------------------------- certification
    times = []; near = []; fam_t = collections.defaultdict(list)
    for (p, n), r in final.items():
        f = os.path.join(ROOT, 'records', p, f'{p}_n{n:02d}.certify.txt')
        if not os.path.exists(f): continue
        x = open(f).read()
        m = re.search(r'\(([0-9.]+)s\)', x); m2 = re.search(r'disjointness: (\d+) near pairs', x)
        if m: times.append((float(m.group(1)), p, n)); fam_t[FAM[p]].append(float(m.group(1)))
        if m2: near.append(int(m2.group(1)))
    times.sort()
    w('### Exact certificates\n')
    w(f"All {sum(1 for k in final if _cert_ok(*k)):,} records of the three families pass `certify_general.py`. Certification time "
      f"per record: median {statistics.median(t for t, _, _ in times):.1f} s, longest {times[-1][0]:.1f} s (`{times[-1][1]}_n{times[-1][2]:02d}`), "
      f"total {sum(t for t, _, _ in times) / 60:.0f} minutes for all of them; {sum(near):,} near pairs were separated by explicit rational planes.\n")
    w(table(['family', 'records', 'median time', 'longest'], [[f, len(v), f'{statistics.median(v):.1f} s', f'{max(v):.1f} s'] for f, v in fam_t.items()],
            ['---', '---:', '---:', '---:']) + '\n')
    degs = collections.Counter(len(EXACT[s]['minpoly']) - 1 for s in EXACT)
    w('Degrees of the number fields of the 41 solids: ' + ', '.join(f'degree {d}: {c}' for d, c in sorted(degs.items())) + '.\n')
    return S, L, final, evening, best, first


def appendix(final):
    """Every record of the three families, one table per problem."""
    out = []
    names = {'archimedean': 'Archimedean solids', 'catalan': 'Catalan solids', 'prisms': 'Prisms and antiprisms'}
    for fam in FAMS:
        out.append(f'### {names[fam]}\n')
        for p in [q for q in NEW if FAM[q] == fam]:
            out.append(f'#### {title(p)} (`{p}`)\n')
            rows = []
            for n in range(2, 41):
                r = final.get((p, n))
                if not r: rows.append([n, '—', '', '', '', '']); continue
                sr = r.get('search') or {}
                rows.append([n, f"[{r['s_plus']}](../records/{p}/{p}_n{n:02d}.json)", f"{(r.get('s_tight') or r['s_full']):.10f}", f"{r['density']:.4f}",
                             r.get('closed_form_conjecture') or '', f"{sr.get('host', 'cloud')} / {sr.get('move', '?')}"])
            out.append(table(['n', 's (certified)', 'touching limit', 'density', 'closed form', 'machine / move'], rows,
                             ['---:', '---:', '---:', '---:', '---', '---']) + '\n')
    return out


def _ranges(ns):
    ns = sorted(ns); out = []; a = b = ns[0]
    for x in ns[1:]:
        if x == b + 1: b = x
        else: out.append(f'{a}' if a == b else f'{a}–{b}'); a = b = x
    out.append(f'{a}' if a == b else f'{a}–{b}')
    return ', '.join(out)


def _cert_ok(p, n):
    f = os.path.join(ROOT, 'records', p, f'{p}_n{n:02d}.certify.txt')
    if not os.path.exists(f): return False
    x = open(f).read(); return 'CERTIFIED' in x and 'NOT CERTIFIED' not in x


if __name__ == '__main__':
    res = main()
    out = '\n'.join(res[0])
    if '--appendix' in sys.argv: out += '\n' + '\n'.join(appendix(res[2]))
    print(out)
