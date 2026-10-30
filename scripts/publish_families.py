#!/usr/bin/env python3
"""Records for the Archimedean, Catalan and prism families (the Platonic records are scripts/publish.py's).

usage: python3 scripts/publish_families.py [--minutes M] [problem ...]

For every active problem, n = 40 down to 2: a record file records/<id>/<id>_nNN.json (10^-7 clearance, same format
as the Platonic records) built from the archive's best packing, checked by verify_general.py (floating point,
exact separating-axis set); monotone in n on the record sizes, like publish.py. Only changed cases are rebuilt; with
--minutes the run stops after that many minutes (the next run continues). Then records/families.md (tables) and
records/SUMMARY_families.csv. The exact certificate for these solids is pending (general certifier)."""
import json, os, sys, time, csv, hashlib, subprocess, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, ROOT)
import claim, engine
from engine import PID, NMIN, NMAX, _read, _path, FAM
from records import closed_form
import verify_general, certify_general

CLEAR = 1e-7
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
FAMILIES = ['archimedean', 'catalan', 'prisms']
FAM_TITLE = {'archimedean': 'Archimedean solids', 'catalan': 'Catalan solids', 'prisms': 'Prisms and antiprisms'}



def credit_of(bs, default='Alejandro Zarzuelo'):
    """found_by for a record from the archive's src: community packings and everything derived from them, or from a
    published packing, keep that credit (13 Oct 2026)."""
    bs = bs or {}
    lin = bs.get('lineage')
    if bs.get('move') == 'community':
        return (f"{lin} (community contribution" + (f", {bs['issue']}" if bs.get('issue') else '')
                + (f"; refinement of the packing by {bs['refines']}" if bs.get('refines') else '')
                + (f"; search started from the packing of {bs['started_from']}" if bs.get('started_from') else '')
                + (f"; cells filled with packings by {', '.join(bs['uses'])}" if bs.get('uses') else '') + ')')
    if bs.get('move') == 'literature':
        return f"{bs.get('source')} (published packing, imported as a starting point; not improved yet)"
    if bs.get('move') == 'tighten' and lin:
        return f"{lin} (re-tightened by the search)"
    if bs.get('move') == 'monotone' and lin:
        return f"{lin} (their packing for n + 1 minus one piece)"
    if lin:
        return f"{default} (search started from the packing of {lin})"
    return default


POLY = {3: 'triangular', 4: 'square', 5: 'pentagonal', 6: 'hexagonal', 8: 'octagonal', 12: 'dodecagonal'}
ELONG_H = {'l15': '1.5', 'l2': '2', 'l3': '3'}


def name(s):
    if s.startswith('prism') and '_' in s:                     # elongated prism, e.g. prism6_l2
        base, tag = s.split('_')
        return f'{POLY[int(base[5:])]} prism of height {ELONG_H.get(tag, tag)}'
    return s.replace('_', ' ')


def plural(s):
    w = name(s)
    if ' prism of height ' in w: return w.replace(' prism of ', ' prisms of ')
    if w.endswith('hedron'): return w[:-6] + 'hedra'
    if w.endswith('prism'): return w + 's'
    return w + 's'


def title(p):
    pc, cc = PID[p]
    return f"{plural(pc).capitalize()} in {'a cube' if cc == 'cube' else ('an ' if name(cc)[0] in 'aeiou' else 'a ') + name(cc)}"


def verify(fn):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: rc = verify_general.main(fn)
        except Exception as e: print('ERROR', type(e).__name__, e); rc = 1
    open(fn.replace('.json', '.verify.txt'), 'w').write(buf.getvalue())
    return rc == 0


def certify(fn):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: rc = certify_general.main(fn)
        except Exception as e: print('ERROR', type(e).__name__, e); print('NOT CERTIFIED'); rc = 1
    open(fn.replace('.json', '.certify.txt'), 'w').write(buf.getvalue())
    return rc == 0


def cert_status(fn):
    t = fn.replace('.json', '.certify.txt')
    if not os.path.exists(t): return None
    x = open(t).read(); return 'CERTIFIED' in x and 'NOT CERTIFIED' not in x


def build_problem(p, log, deadline):
    piece, container = PID[p]
    d = os.path.join(ROOT, 'records', p); os.makedirs(d, exist_ok=True)
    rows, prev, rebuilt = [], None, 0
    for n in range(NMAX, NMIN - 1, -1):
        case = _read(_path('best', p, n)); fn = os.path.join(d, f'{p}_n{n:02d}.json')
        if not case or not case.get('best'): prev = None; continue
        b = case['best']
        h = hashlib.sha1(json.dumps([round(b['s'], 13), b['C'], b['Q']]).encode()).hexdigest()[:16]
        src = {'hash': h, 'clear': CLEAR, 'cap': prev['s_full'] if prev else None}
        old = _read(fn)
        vtxt = fn.replace('.json', '.verify.txt')
        if old and old.get('source') == src and os.path.exists(vtxt):
            rec = old; ver = 'VALID' in open(vtxt).read() and 'INVALID' not in open(vtxt).read()
            cert = cert_status(fn)
            if cert is None and time.time() < deadline:          # records built before the exact certifier existed
                cert = certify(fn)
                rec['certificate'] = 'exact certificate: certify_general.py (src/solids_exact.json)' if cert else 'exact certification FAILED'
                json.dump(rec, open(fn, 'w'), indent=1)
                log(f"certify {p}_n{n:02d}  {'CERTIFIED' if cert else 'NOT CERTIFIED'}")
        elif time.time() > deadline:
            if old: rec = old; ver = os.path.exists(vtxt) and 'INVALID' not in open(vtxt).read(); cert = cert_status(fn)
            else: prev = None; continue
        else:
            try: cf = closed_form(b['s'])
            except Exception: cf = None
            meta = {'record_id': f'{p}_n{n:02d}', 'title': f'{n} {plural(piece)} in ' + ('a cube' if container == 'cube' else 'a ' + name(container)),
                    'family': FAM[p], 'source': src, 's_tight': round(b['s'], 12), 'closed_form_conjecture': cf,
                    'volume_lower_bound': (n * SOL[piece]['volume'] / SOL[container]['volume']) ** (1 / 3),
                    'found_by': credit_of(b.get('src')),
                    'credit': "soft-to-rigid method by Yohei Nakajima (2026); generalization to Archimedean, Catalan, prism and "
                              "antiprism solids, basin-hopping search and certification developed with Claude (Anthropic) under "
                              "Alejandro Zarzuelo's direction",
                    'certificate': 'pending',
                    'search': b.get('src', {})}
            try:
                rec = claim.make_claim_fast({'piece': piece, 'container': container, 'C': b['C'], 'Q': b['Q']}, GAP=CLEAR, WALL=CLEAR, meta=meta)
            except Exception as e:
                log(f'record {p}_n{n:02d} FAILED to build: {e}'); prev = None; continue
            if prev is not None and rec['s_full'] > prev['s_full']:
                rec = dict(prev); rec.update(meta)
                rec['n'] = n; rec['pieces'] = prev['pieces'][:-1]; rec['derived_from'] = f'{p}_n{n + 1:02d} minus its last piece'
                rec['s_tight'] = min(round(b['s'], 12), prev.get('s_tight', b['s'])); rec['record_id'] = f'{p}_n{n:02d}'
            rec['density'] = n * SOL[piece]['volume'] / (SOL[container]['volume'] * rec['s_full'] ** 3)
            rec['date'] = time.strftime('%Y-%m-%d')
            json.dump(rec, open(fn, 'w'), indent=1)
            ver = verify(fn); cert = certify(fn); rebuilt += 1
            rec['certificate'] = 'exact certificate: certify_general.py (src/solids_exact.json)' if cert else 'exact certification FAILED'
            json.dump(rec, open(fn, 'w'), indent=1)
            log(f"record {p}_n{n:02d}  s_full {rec['s_full']:.13f}  {'CERTIFIED' if ver and cert else 'VERIFIED, NOT CERTIFIED' if ver else 'FAILED'}")
        rows.append(dict(record_id=f'{p}_n{n:02d}', problem=p, family=FAM[p], piece=piece, container=container, n=n,
                         s=rec['s_plus'], s_full=rec['s_full'], s_tight=f"{rec.get('s_tight', b['s']):.12f}",
                         closed_form_conjecture=rec.get('closed_form_conjecture') or '',
                         volume_lower_bound=f"{rec['volume_lower_bound']:.5f}", density=f"{rec['density']:.4f}",
                         verified=ver, certified=bool(cert), derived=bool(rec.get('derived_from')), file=os.path.relpath(fn, ROOT)))
        prev = rec
    return rows[::-1], rebuilt


def write_tables(rows):
    by = {}
    for r in rows: by.setdefault(r['problem'], {})[r['n']] = r
    L = ['# Records: Archimedean, Catalan, prism and antiprism families', '',
         f'_Generated {time.strftime("%Y-%m-%d %H:%M %Z")} from the running search._ s = container size ÷ piece size '
         '(edge ratio; for Catalan solids the ratio of the same canonical solid). Each entry: the record\'s container, '
         'with 10⁻⁷ clearance, truncated to 5 decimals, linking to the record file. Every record is proven by '
         '`certify_general.py` (exact number fields for the solids, rigorous interval arithmetic for the packing) and '
         'checked by `verify_general.py` (floating point). '
         '"≈ x" = conjectured closed form. The square prism is the cube and the triangular antiprism the octahedron: '
         'see the Platonic tables (cubes in a cube, octahedra in an octahedron, octahedra in a cube).', '']
    for fam in FAMILIES:
        ps = [p for p in PID if FAM[p] == fam]
        L += [f'## {FAM_TITLE[fam]}', '']
        for chunk in [ps[i:i + 5] for i in range(0, len(ps), 5)]:
            L.append('| n | ' + ' | '.join(title(p) for p in chunk) + ' |')
            L.append('|---:|' + '---|' * len(chunk))
            for n in range(NMIN, NMAX + 1):
                cells = []
                for p in chunk:
                    r = by.get(p, {}).get(n)
                    if not r: cells.append(''); continue
                    c = f"[{r['s']}]({os.path.relpath(os.path.join(ROOT, r['file']), os.path.join(ROOT, 'records'))})"
                    if r['closed_form_conjecture'] and not r['closed_form_conjecture'].isdigit(): c += f" ≈ {r['closed_form_conjecture']}"
                    if not r['certified']: c += ' (not certified)'
                    cells.append(c)
                L.append(f'| {n} | ' + ' | '.join(cells) + ' |')
            L.append('')
    open(os.path.join(ROOT, 'records', 'families.md'), 'w').write('\n'.join(L) + '\n')
    if rows:
        with open(os.path.join(ROOT, 'records', 'SUMMARY_families.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def _build(args):
    p, deadline = args
    logf = open(os.path.join(ROOT, 'logs', 'publish_families.log'), 'a')

    def log(m): logf.write(time.strftime('%m-%d %H:%M:%S ') + m + '\n'); logf.flush()
    return build_problem(p, log, deadline)


def main():
    args = sys.argv[1:]
    minutes = float(args[args.index('--minutes') + 1]) if '--minutes' in args else 1e9
    only = [a for a in args if a in PID]
    deadline = time.time() + 60 * minutes
    logf = open(os.path.join(ROOT, 'logs', 'publish_families.log'), 'a')

    def log(m): logf.write(time.strftime('%m-%d %H:%M:%S ') + m + '\n'); logf.flush(); print(m, flush=True)
    rows, total = [], 0
    todo = [p for p in PID if FAM[p] in FAMILIES and (not only or p in only)]
    procs = int(os.environ.get('PP_PUBLISH_PROCS', '1'))
    if procs > 1:                     # 14 Oct (n <= 100): problems certified in parallel processes
        import multiprocessing as mp
        with mp.Pool(procs) as pool:
            for r, k in pool.imap_unordered(_build, [(p, deadline) for p in todo]): rows += r; total += k
    else:
        for p in todo:
            r, k = build_problem(p, log, deadline); rows += r; total += k
    rows.sort(key=lambda r: (list(PID).index(r['problem']), r['n']))
    write_tables(rows)
    log(f'publish_families: {len(rows)} records, {total} rebuilt')


if __name__ == '__main__':
    main()
