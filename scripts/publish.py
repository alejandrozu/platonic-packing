#!/usr/bin/env python3
"""Publish the archive: record files (with clearance, checked by both checkers), tables, progress report, results
site, and a git commit + push. Safe to run while the engine is running; only changed records are rebuilt.

usage: python3 scripts/publish.py [--no-push] [problem ...]

Records are built from n = 40 down to 2 for every problem, and record monotonicity is enforced exactly on the
certified sizes: if the record for n would need a larger container than the record for n + 1 (this can only happen
through clearance rounding, since the archive is already monotone), the n-record is the (n+1)-record minus one piece,
in the same container."""
import json, os, sys, time, csv, hashlib, subprocess, glob, math
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import claim
from engine import PID, PROBLEMS, NMIN, NMAX, STATE, _read, _path, AB
from records import closed_form

CLEAR = 1e-7
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
PL = {'tetrahedron': 'tetrahedra', 'cube': 'cubes', 'octahedron': 'octahedra', 'dodecahedron': 'dodecahedra', 'icosahedron': 'icosahedra'}
REF = json.load(open(os.path.join(ROOT, 'docs', 'references.json')))


def art(w): return ('an ' if w[0] in 'aeiou' else 'a ') + w


def title(p): pc, cc = PID[p]; return f'{PL[pc].capitalize()} in {art(cc)}'


def run_checkers(fn):
    v = subprocess.run([sys.executable, os.path.join(ROOT, 'verify.py'), fn], capture_output=True, text=True)
    x = subprocess.run([sys.executable, os.path.join(ROOT, 'certify_exact.py'), fn], capture_output=True, text=True)
    open(fn.replace('.json', '.verify.txt'), 'w').write(v.stdout + v.stderr[-2000:])
    open(fn.replace('.json', '.certify.txt'), 'w').write(x.stdout + x.stderr[-2000:])
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'figures.py'), fn], capture_output=True)
    return v.returncode == 0, x.returncode == 0


def status_of(fn):
    try:
        v = open(fn.replace('.json', '.verify.txt')).read(); x = open(fn.replace('.json', '.certify.txt')).read()
    except FileNotFoundError: return None
    return ('VALID' in v and 'INVALID' not in v), ('CERTIFIED' in x and 'NOT CERTIFIED' not in x)


def build_problem(p, log):
    piece, container = PID[p]
    d = os.path.join(ROOT, 'records', p); os.makedirs(d, exist_ok=True)
    rows, prev, rebuilt = [], None, 0
    for n in range(NMAX, NMIN - 1, -1):
        case = _read(_path('best', p, n))
        fn = os.path.join(d, f'{p}_n{n:02d}.json')
        if not case or not case.get('best'): prev = None; continue
        b = case['best']
        h = hashlib.sha1(json.dumps([round(b['s'], 13), b['C'], b['Q']]).encode()).hexdigest()[:16]
        src = {'hash': h, 'clear': CLEAR, 'cap': prev['s_full'] if prev else None}
        old = _read(fn); st = status_of(fn)
        if old and old.get('source') == src and st is not None:
            rec, (ver, cert) = old, st
        else:
            try: cf = closed_form(b['s'])
            except Exception: cf = None                   # a hint only; never let it stop a publish
            meta = {'record_id': f'{p}_n{n:02d}', 'title': f'{n} unit {PL[piece]} in {art(container)}', 'source': src,
                    's_tight': round(b['s'], 12), 'closed_form_conjecture': cf,
                    'volume_lower_bound': (n * SOL[piece]['volume'] / SOL[container]['volume']) ** (1 / 3),
                    'found_by': 'Alejandro Zarzuelo',
                    'credit': "soft-to-rigid method by Yohei Nakajima (2026); generalization to Platonic solids, basin-hopping "
                              "search and exact certification developed with Claude (Anthropic) under Alejandro Zarzuelo's direction",
                    'search': b.get('src', {})}
            rec = claim.make_claim({'piece': piece, 'container': container, 'C': b['C'], 'Q': b['Q']}, GAP=CLEAR, WALL=CLEAR, meta=meta)
            if prev is not None and rec['s_full'] > prev['s_full']:
                # monotone records: the (n+1)-record minus its last piece, same container (all clearances kept)
                rec = dict(prev); rec.update(meta)
                rec['n'] = n; rec['pieces'] = prev['pieces'][:-1]; rec['derived_from'] = f'{p}_n{n + 1:02d} minus its last piece'
                rec['s_tight'] = min(round(b['s'], 12), prev.get('s_tight', b['s']))
                rec['problem'] = prev['problem']; rec['record_id'] = f'{p}_n{n:02d}'; rec['title'] = meta['title']
            rec['density'] = n * SOL[piece]['volume'] / (SOL[container]['volume'] * rec['s_full'] ** 3)
            rec['date'] = time.strftime('%Y-%m-%d')
            json.dump(rec, open(fn, 'w'), indent=1)
            ver, cert = run_checkers(fn); rebuilt += 1
            log(f"record {p}_n{n:02d}  s_full {rec['s_full']:.13f}  {'CERTIFIED' if ver and cert else 'FAILED'}")
        ref = REF.get(p, {}).get(str(n))
        rows.append(dict(record_id=f'{p}_n{n:02d}', problem=p, piece=piece, container=container, n=n, s=rec['s_plus'],
                         s_full=rec['s_full'], s_tight=f"{rec.get('s_tight', b['s']):.12f}",
                         closed_form_conjecture=rec.get('closed_form_conjecture') or '',
                         volume_lower_bound=f"{rec['volume_lower_bound']:.5f}", density=f"{rec['density']:.4f}",
                         reference=ref[0] if ref else '', reference_source=ref[1] if ref else '',
                         verified=ver, certified=cert, derived=bool(rec.get('derived_from')),
                         file=os.path.relpath(fn, ROOT)))
        prev = rec
    # drop stale records for n that no longer have an archive entry (none expected)
    return rows[::-1], rebuilt


def compare(s_full, ref):
    """'better' only if more than 1e-5 below the published value (published values are often 5-decimal truncations
    and our records carry 1e-7 clearance), 'equal' within 1e-5, else 'behind'."""
    s_full, ref = float(s_full), float(ref)
    return 'better' if s_full < ref - 1e-5 else ('equal' if s_full <= ref + 1e-5 else 'behind')


def src_code(src):
    return 'T' if 'trivial' in src else 'N' if 'Nakajima' in src else 'W' if 'Walsh' in src else 'L' if 'Lin' in src else 'F'


SRC_LEGEND = ('previous: F = E. Friedman (1998), W = R. Walsh (June 2026), L = H. Lin (July 2026), N = Y. Nakajima '
              '(Oct 2026), T = trivial grid packing (Friedman: best known); from Erich Friedman\'s Packing Center and '
              'docs/references.json. ✱ = ours is more than 1e-5 below the previous value.')


def fmt_cell(r, link_prefix):
    if not r: return ''
    cf = r['closed_form_conjecture']
    s = f"[{r['s']}]({link_prefix}{r['file'].split('/', 1)[1]})" + (f" ≈ {cf}" if cf and cf not in ('2', '3', '4') else '')
    if r['reference'] != '' and compare(r['s_full'], r['reference']) == 'better': s += ' ✱'
    if str(r['certified']) != 'True': s += ' **(not certified)**'
    return s


def fmt_ref(r):
    if not r or r['reference'] == '': return ''
    return f"{float(r['reference']):.5f} {src_code(r['reference_source'])}"


def tables(rows, link_prefix):
    by = {}
    for r in rows: by.setdefault(r['problem'], {})[int(r['n'])] = r
    groups = [('Same solid', ['tetintet', 'octinoct', 'icoinico', 'dodindod', 'cubincub']),
              ('Duals', ['cubinoct', 'octincub', 'dodinico', 'icoindod'])]
    out = []
    for name, ps in groups:
        ps = [p for p in ps if p in PID]
        cols = []
        for p in ps:
            cols.append((title(p), p, False))
            if REF.get(p): cols.append(('previous', p, True))          # only where a published value exists
        out += [f'### {name}', '', '| n | ' + ' | '.join(c[0] for c in cols) + ' |', '|---:|' + '---|' * len(cols)]
        for n in range(NMIN, NMAX + 1):
            out.append(f'| {n} | ' + ' | '.join(fmt_ref(by.get(p, {}).get(n)) if isref else fmt_cell(by.get(p, {}).get(n), link_prefix)
                                                 for _, p, isref in cols) + ' |')
        out.append('')
    out.append(SRC_LEGEND)
    out.append('')
    out.append(comparison(rows))
    return '\n'.join(out)


def comparison(rows):
    """One line per problem with published values: where ours is better, equal, behind."""
    out = []
    for p in PID:
        rs = sorted((r for r in rows if r['problem'] == p and r['reference'] != ''), key=lambda r: int(r['n']))
        if not rs: continue
        g = {'better': [], 'equal': [], 'behind': []}
        for r in rs: g[compare(r['s_full'], r['reference'])].append(r)
        def ns(lst): return ', '.join(str(r['n']) for r in lst) or 'none'
        beh = ', '.join(f"{r['n']} (+{100 * (float(r['s_full']) / float(r['reference']) - 1):.2f}%)" for r in g['behind']) or 'none'
        out.append(f"**{title(p)} vs published values** (n = {rs[0]['n']}–{rs[-1]['n']}): better at {ns(g['better'])}; "
                   f"equal at {ns(g['equal'])}; behind at {beh}.")
    return '\n\n'.join(out) + '\n'


def write_tables(rows):
    path = os.path.join(ROOT, 'records', 'SUMMARY.csv')
    keys = list(rows[0].keys())
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    head = ['# Records', '',
            'Smallest container found for n unit-edge pieces; entry = s = container edge / piece edge, certified with 1e-7 '
            'clearance and truncated to 5 decimals. Each entry links to its record file, which `certify_exact.py` proves '
            'valid in exact arithmetic over Q(√2, √5). s(n) is non-decreasing in n by construction. "≈ x" is a '
            'conjectured closed form (touching limit agrees with x to ~11 digits). Published values exist only for cubes in a '
            'cube and octahedra in a cube; they are shown in the "previous" columns. Full data: [SUMMARY.csv](SUMMARY.csv).', '']
    open(os.path.join(ROOT, 'records', 'README.md'), 'w').write('\n'.join(head) + '\n' + tables(rows, '') + '\n')
    for p in PID:
        rs = [r for r in rows if r['problem'] == p]
        if not rs: continue
        hasref = bool(REF.get(p))
        lines = [f'# {title(p)}', '', 's = container edge / piece edge; every row certified in exact arithmetic.', '',
                 '| n | s | touching limit | closed form (conj.) |' + (' previous best | vs previous |' if hasref else '') +
                 ' volume bound | density | picture |', '|---|---|---|---|' + ('---|---|' if hasref else '') + '---|---|---|']
        for r in rs:
            refc = ''
            if hasref:
                if r['reference'] != '':
                    c = compare(r['s_full'], r['reference'])
                    d = f"{100 * (float(r['s_full']) / float(r['reference']) - 1):+.3f}%"
                    refc = f" {float(r['reference']):.5f} ({r['reference_source']}) | {'**better** ' + d if c == 'better' else 'equal' if c == 'equal' else 'behind ' + d} |"
                else: refc = ' | |'
            lines.append(f"| {r['n']} | [{r['s']}]({os.path.basename(r['file'])}) | {r['s_tight']} | {r['closed_form_conjecture']} |{refc} "
                         f"{r['volume_lower_bound']} | {r['density']} | ![]({os.path.basename(r['file']).replace('.json', '.png')}) |")
        if hasref: lines += ['', comparison(rs)]
        open(os.path.join(ROOT, 'records', p, 'README.md'), 'w').write('\n'.join(lines) + '\n')
    # README results block
    rp = os.path.join(ROOT, 'README.md'); s = open(rp).read()
    a, b = '<!-- RESULTS:START -->', '<!-- RESULTS:END -->'
    if a in s and b in s:
        block = (f"{a}\n_Auto-generated {time.strftime('%Y-%m-%d %H:%M %Z')} from the running search; see "
                 f"[PROGRESS.md](PROGRESS.md) for search statistics._\n\n" + tables(rows, 'records/') + b)
        s = s[:s.index(a)] + block + s[s.index(b) + len(b):]
        open(rp, 'w').write(s)


def retable():
    """Rewrite the tables (records/README.md, per-problem READMEs, README block, SUMMARY.csv) from SUMMARY.csv with the
    current docs/references.json, without rebuilding or re-certifying any record."""
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'records', 'SUMMARY.csv'))))
    for r in rows:
        ref = REF.get(r['problem'], {}).get(str(int(r['n'])))
        r['reference'] = ref[0] if ref else ''; r['reference_source'] = ref[1] if ref else ''
    rows.sort(key=lambda r: (list(PID).index(r['problem']), int(r['n'])))
    write_tables(rows)
    return rows


def progress():
    import collections
    att = []
    fp = os.path.join(STATE, 'attempts.jsonl')
    if os.path.exists(fp):
        for l in open(fp):
            try: att.append(json.loads(l))
            except json.JSONDecodeError: pass
    now = time.time()
    day = [a for a in att if now - a['t'] < 86400]; hour = [a for a in att if now - a['t'] < 3600]
    mv = collections.defaultdict(lambda: [0, 0])
    for a in att: mv[a['move']][0] += 1; mv[a['move']][1] += a['improved']
    lines = ['# Search progress', '', f"Updated {time.strftime('%Y-%m-%d %H:%M %Z')}. The engine runs unattended "
             '(scripts/run_forever.sh); this file is regenerated with every publish.', '',
             f'* attempts: {len(att)} total, {len(day)} in the last 24 h, {len(hour)} in the last hour',
             f"* improvements: {sum(a['improved'] for a in att)} total, {sum(a['improved'] for a in day)} in the last 24 h",
             '* by move (attempts / improvements): ' + ', '.join(f'{m} {v[0]}/{v[1]}' for m, v in sorted(mv.items())), '',
             '| problem | n with a packing | attempts | CPU hours | improvements (24 h) | last improvement |', '|---|---|---|---|---|---|']
    for p in PID:
        cs = [_read(_path('best', p, n)) for n in range(NMIN, NMAX + 1)]
        cs = [c for c in cs if c and c.get('best')]
        a = sum(c['stats'].get('attempts', 0) for c in cs); e = sum(c['stats'].get('effort', 0) for c in cs) / 3600
        imp = sum(1 for x in day if x['p'] == p and x['improved'])
        last = max([c['stats'].get('last_improve') or 0 for c in cs] + [0])
        lines.append(f"| {title(p)} ({p}) | {len(cs)}/{NMAX - NMIN + 1} | {a} | {e:.1f} | {imp} | "
                     f"{time.strftime('%m-%d %H:%M', time.localtime(last)) if last else '-'} |")
    # live values straight from the archive (not yet certified records; records follow at the next publish)
    lines += ['', '## Current best values (live archive, uncertified until the next records publish)', '',
              's = container edge / piece edge, touching limit from the tightening; s(n) is non-decreasing by construction.', '']
    ps = list(PID)
    lines += ['| n | ' + ' | '.join(ps) + ' |', '|---:|' + '---|' * len(ps)]
    for n in range(NMIN, NMAX + 1):
        cells = []
        for p in ps:
            c = _read(_path('best', p, n))
            if c and c.get('best'):
                fresh = c['stats'].get('last_improve') and now - c['stats']['last_improve'] < 86400
                cells.append(f"{c['best']['s']:.5f}" + (' •' if fresh else ''))
            else: cells.append('')
        lines.append(f'| {n} | ' + ' | '.join(cells) + ' |')
    lines += ['', '• improved in the last 24 hours.']
    open(os.path.join(ROOT, 'PROGRESS.md'), 'w').write('\n'.join(lines) + '\n')


def git_push(log):
    import fcntl
    lockf = open(os.path.join(STATE, '.gitlock'), 'w'); fcntl.flock(lockf, fcntl.LOCK_EX)   # shared with checkpoint.sh
    def g(*a, check=False): return subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True, check=check)
    g('add', '-A')
    if not g('diff', '--cached', '--quiet').returncode: log('git: nothing to commit'); return
    msg = (f"Auto-update records ({time.strftime('%Y-%m-%d %H:%M')})\n\n"
           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_015sjhNzKTinVQnSnofRcCoP")
    g('commit', '-q', '-m', msg)
    for attempt in range(3):
        r = g('push', '-q', 'origin', 'HEAD:main')
        if r.returncode == 0: log('git: pushed'); return
        log(f'git push failed: {r.stderr.strip()[:300]}'); time.sleep(30)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only = set(args) or set(PID)
    logf = open(os.path.join(ROOT, 'logs', 'publish.log'), 'a')
    def log(m): logf.write(time.strftime('%m-%d %H:%M:%S ') + m + '\n'); logf.flush(); print(m, flush=True)
    t0 = time.time()
    rows, total = [], 0
    for p in PID:
        if p in only:
            r, k = build_problem(p, log); rows += r; total += k
        else:
            rows += [x for x in (_csv_rows() or []) if x['problem'] == p]
    write_tables(rows)
    progress()
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'site.py')], capture_output=True)
    log(f'publish: {len(rows)} records, {total} rebuilt, {time.time() - t0:.0f}s')
    if '--no-push' not in sys.argv: git_push(log)


def _csv_rows():
    path = os.path.join(ROOT, 'records', 'SUMMARY.csv')
    return list(csv.DictReader(open(path))) if os.path.exists(path) else None


if __name__ == '__main__':
    main()
