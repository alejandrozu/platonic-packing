#!/usr/bin/env python3
"""Records for the higher-dimensional problems (regular polytopes of dimensions 4, 5 and 6; 15 Oct 2026).

usage: python3 scripts/publish_nd.py [--minutes M] [problem ...]

For every problem of scripts/engine_nd.py, n = nmax down to 2: a record file records/<id>/<id>_nNN.json built from the
archive state/nd (10^-7 clearance, rational rotations and explicit separating hyperplanes: src/claim_nd.py) and its
exact certificate records/<id>/<id>_nNN.certify.txt (certify_nd.py, standard library only). Record sizes are kept
monotone in n (a record larger than the n + 1 record is replaced by that record minus one piece). Only changed cases
are rebuilt; --minutes bounds the run (the next run continues). Then records/higher.md (tables)."""
import json, os, sys, time, hashlib, io, contextlib, math, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, 'scripts'))
import engine_nd as E
import claim_nd, certify_nd

CLEAR = 1e-7
NAME = {'c5': '5-cell', 'c8': 'tesseract', 'c16': '16-cell', 'c24': '24-cell', 'c120': '120-cell', 'c600': '600-cell',
        'sx5': '5-simplex', 'hc5': '5-cube', 'op5': '5-orthoplex', 'sx6': '6-simplex', 'hc6': '6-cube', 'op6': '6-orthoplex'}
LOG = os.path.join(ROOT, 'logs', 'publish_nd.log')
RECORDS = os.environ.get('PP_ND_RECORDS') or os.path.join(ROOT, 'records')      # (tests write elsewhere)


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'a') as f: f.write(time.strftime('%m-%d %H:%M:%S ') + msg + '\n')


def plural(w):
    return w[:-2] + 'ices' if w.endswith('simplex') else w + 'es' if w.endswith('plex') else w + 's'


def title(n, piece, container):
    return f'{n} {plural(NAME[piece])} in a {NAME[container]}'


def certify(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: code = certify_nd.main(fn)
        except Exception as e: print(f'NOT CERTIFIED: {type(e).__name__}: {e}'); code = 1
    open(fn.replace('.json', '.certify.txt'), 'w').write(buf.getvalue())
    return code == 0


def cert_ok(fn):
    t = fn.replace('.json', '.certify.txt')
    if not os.path.exists(t): return None
    s = open(t).read(); return 'CERTIFIED' in s and 'NOT CERTIFIED' not in s


def build(p, deadline):
    piece, container = E.PID[p]; d = E.DIM[p]
    D = claim_nd.ndsim.data(); vP, vC = D[piece]['volume'], D[container]['volume']
    from multiquad import parse
    mu = float(parse(claim_nd.mu_of(piece, container)))
    out_dir = os.path.join(RECORDS, p); os.makedirs(out_dir, exist_ok=True)
    rows, prev, rebuilt = [], None, 0
    for n in range(E.nmax(p), E.NMIN - 1, -1):
        case = E._read(E._path('best', p, n)); fn = os.path.join(out_dir, f'{p}_n{n:02d}.json')
        if not case or not case.get('best'): prev = None; continue
        b = case['best']
        h = hashlib.sha1(json.dumps([round(b['s'], 13), b['C'], b['R']]).encode()).hexdigest()[:16]
        src = {'hash': h, 'clear': CLEAR, 'cap': prev['s_full'] if prev else None}
        old = E._read(fn)
        if old and old.get('source') == src and cert_ok(fn):          # (a failed certificate is rebuilt)
            rec = old; ok = cert_ok(fn)
        elif time.time() > deadline:
            if old: rec = old; ok = cert_ok(fn)
            else: prev = None; continue
        else:
            meta = {'record_id': f'{p}_n{n:02d}', 'title': title(n, piece, container), 'family': f'{d}d',
                    'kind': E.KIND[p], 'source': src, 's_tight': round(b['s'], 12),
                    'volume_lower_bound': (n * vP / vC) ** (1 / d) / mu,
                    'found_by': 'Alejandro Zarzuelo',
                    'credit': "soft-to-rigid method by Yohei Nakajima (2026); generalization to regular polytopes of dimensions "
                              "4-6, basin-hopping search and exact certification developed with Claude (Anthropic) under "
                              "Alejandro Zarzuelo's direction",
                    'certificate': 'pending', 'search': b.get('src', {})}
            try:
                rec = claim_nd.make_claim(p, piece, container, b['C'], b['R'], GAP=CLEAR, WALL=CLEAR, meta=meta)
            except Exception as e:
                log(f'record {p}_n{n:02d} FAILED to build: {type(e).__name__}: {e}'); prev = None; continue
            if prev is not None and rec['s_full'] > prev['s_full']:
                rec = dict(prev); rec.update(meta)
                rec['n'] = n; rec['pieces'] = prev['pieces'][:-1]
                rec['planes'] = [pl for pl in prev['planes'] if pl[0] < n and pl[1] < n]
                rec['derived_from'] = f'{p}_n{n + 1:02d} minus its last piece'
                rec['s_tight'] = min(round(b['s'], 12), prev.get('s_tight', b['s'])); rec['record_id'] = f'{p}_n{n:02d}'
            rec['s'] = math.floor(rec['s_full'] * 1e5) / 1e5; rec['s_plus'] = f"{rec['s']:.5f}+"
            rec['density'] = n * vP / (vC * (rec['s_full'] * mu) ** d)
            rec['date'] = time.strftime('%Y-%m-%d')
            json.dump(rec, open(fn, 'w'), indent=1)
            ok = certify(fn); rebuilt += 1
            rec['certificate'] = 'exact certificate: certify_nd.py (src/polytopes_nd.json)' if ok else 'exact certification FAILED'
            json.dump(rec, open(fn, 'w'), indent=1)
            log(f"record {p}_n{n:02d}  s_full {rec['s_full']:.13f}  {'CERTIFIED' if ok else 'NOT CERTIFIED'}")
        rows.append(dict(record_id=f'{p}_n{n:02d}', problem=p, n=n, s=rec['s_plus'], s_full=rec['s_full'], certified=bool(ok),
                         density=rec['density'], vlb=rec['volume_lower_bound'], file='records/' + os.path.relpath(fn, RECORDS)))
        prev = rec
    return rows[::-1], rebuilt


def write_tables(allrows):
    by = {}
    for r in allrows: by.setdefault(r['problem'], {})[r['n']] = r
    L = ['# Records: regular polytopes in 4, 5 and 6 dimensions', '',
         f'_Generated {time.strftime("%Y-%m-%d %H:%M %Z")} from the running search._ s = container edge ÷ piece edge. Each entry: '
         'the record\'s container with 10⁻⁷ clearance, truncated to 5 decimals, linking to the record file; ✓ = proven by '
         '`certify_nd.py` (exact coordinates in Q(√2, √3, √5, √7), rational rotations, explicit separating hyperplanes, '
         'rigorous interval arithmetic).', '']
    for d in (4, 5, 6):
        L += [f'## {d} dimensions', '']
        for p in [q for q in E.PID if E.DIM[q] == d]:
            pc, cc = E.PID[p]
            rows = by.get(p, {})
            L.append(f'### {plural(NAME[pc])[0].upper() + plural(NAME[pc])[1:]} in a {NAME[cc]} (`{p}`, {len(rows)} of {E.nmax(p) - 1} values)')
            L.append('')
            if rows:
                L.append(' · '.join(f"n={n}: [{r['s']}]({os.path.basename(r['file'])}){' ✓' if r['certified'] else ''}"
                                    .replace(f"]({os.path.basename(r['file'])})", f"]({r['file'].replace('records/', '')})")
                                    for n, r in sorted(rows.items())))
                L.append('')
    open(os.path.join(RECORDS, 'higher.md'), 'w').write('\n'.join(L) + '\n')


def _build(arg):
    p, deadline = arg
    try: return build(p, deadline)
    except Exception as e:
        log(f'problem {p} FAILED: {type(e).__name__}: {e}'); return [], 0


def main():
    """problems in parallel (PP_PUBLISH_PROCS, default 2), the ones with the oldest records first"""
    args = sys.argv[1:]
    minutes = 30.0
    if args and args[0] == '--minutes': minutes = float(args[1]); args = args[2:]
    deadline = time.time() + 60 * minutes
    probs = args or list(E.PID)
    def age(p):                      # oldest record file first, so every problem gets its turn when time runs out
        fs = glob.glob(os.path.join(RECORDS, p, f'{p}_n[0-9][0-9].json'))
        return min((os.path.getmtime(f) for f in fs), default=0)
    probs.sort(key=age)
    procs = int(os.environ.get('PP_PUBLISH_PROCS', '2'))
    allrows, tot = [], 0
    if procs > 1:
        import multiprocessing as mp
        with mp.Pool(procs) as pool:
            for rows, k in pool.imap_unordered(_build, [(p, deadline) for p in probs]): allrows += rows; tot += k
    else:
        for p in probs:
            rows, k = build(p, deadline); allrows += rows; tot += k
    if not args: write_tables(allrows)
    cert = sum(r['certified'] for r in allrows)
    log(f'publish_nd: {len(allrows)} records ({cert} certified), {tot} rebuilt')
    print(f'publish_nd: {len(allrows)} records ({cert} certified), {tot} rebuilt')


if __name__ == '__main__':
    main()
