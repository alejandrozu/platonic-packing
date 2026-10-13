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
    return S, L, final, evening, best


def _cert_ok(p, n):
    f = os.path.join(ROOT, 'records', p, f'{p}_n{n:02d}.certify.txt')
    if not os.path.exists(f): return False
    x = open(f).read(); return 'CERTIFIED' in x and 'NOT CERTIFIED' not in x


if __name__ == '__main__':
    S = main()[0]
    print('\n'.join(S))
