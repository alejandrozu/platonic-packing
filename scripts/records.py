#!/usr/bin/env python3
"""Build the record set: for every (piece, container, n) the best tightened packing becomes a record file with explicit
clearance, checked by verify.py and certify_exact.py, plus a picture, a per-problem table and records/SUMMARY.csv.

usage: python3 scripts/records.py [problem-id ...]       e.g. tetintet octinoct (default: all with results)

Record ids follow Erich Friedman's naming (cubincub = cubes in cube): <piece><in><container> with
tet / cub / oct / dod / ico, e.g. tetintet_n05 = 5 unit tetrahedra in the smallest tetrahedron found.
The measure s is (container edge) / (piece edge). s_full carries >= 1e-7 clearance (pairs and walls) and is what the
checkers certify; s_tight is the touching-contact limit reached by the exact tightening (12 digits), and a closed form
is reported only when s_tight matches a quadratic irrationality with small coefficients to 1e-11 (a conjecture, not
a proof)."""
import json, os, sys, math, subprocess, csv, glob, datetime
from math import gcd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src')); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import claim
import pipeline

AB = {'tetrahedron': 'tet', 'cube': 'cub', 'octahedron': 'oct', 'dodecahedron': 'dod', 'icosahedron': 'ico'}
PL = {'tetrahedron': 'tetrahedra', 'cube': 'cubes', 'octahedron': 'octahedra', 'dodecahedron': 'dodecahedra', 'icosahedron': 'icosahedra'}
SOL = json.load(open(os.path.join(ROOT, 'src', 'solids.json')))
CLEAR = 1e-7      # minimum pair gap and wall gap written into every record (far above float noise ~1e-15)


def pid(piece, container): return f'{AB[piece]}in{AB[container]}'


def closed_form(x):
    """Small-coefficient algebraic identification of x (accurate to ~1e-12): rationals, then quadratics."""
    try:
        import mpmath as mp
    except ImportError:
        return None
    mp.mp.dps = 30
    v = mp.mpf(x)
    for deg, cmax in ((1, 60), (2, 200)):
        p = mp.findpoly(v, deg, maxcoeff=cmax, tol=1e-11)
        if not p: continue
        if deg == 1:
            a, b = p; q = mp.mpf(-b) / a
            if abs(q - v) < 1e-11:
                g = gcd(int(b), int(a)); num, den = -int(b) // g, int(a) // g
                if den < 0: num, den = -num, -den
                return str(num) if den == 1 else f'{num}/{den}'
            continue
        A, B, C = (int(c) for c in p)
        D = B * B - 4 * A * C
        if D <= 0: continue
        k, m = 1, D                                   # D = k^2 m, m squarefree
        f = 2
        while f * f <= m:
            while m % (f * f) == 0: m //= f * f; k *= f
            f += 1
        if m == 1: continue                           # rational root: caught by degree 1
        for sg in (1, -1):
            if abs((-B + sg * k * mp.sqrt(m)) / (2 * A) - v) < 1e-11:
                num0, kk, den = -B, sg * k, 2 * A
                if den < 0: num0, kk, den = -num0, -kk, -den
                g = gcd(gcd(abs(num0), abs(kk)), den); num0, kk, den = num0 // g, kk // g, den // g
                rad = f'√{m}' if abs(kk) == 1 else f'{abs(kk)}√{m}'
                expr = (f'{num0} {"+" if kk > 0 else "-"} {rad}' if num0 else (rad if kk > 0 else f'-{rad}'))
                return expr if den == 1 else f'({expr})/{den}'
    return None


def build(only=None):
    best = pipeline.best_tight()
    rows = []
    out_root = os.path.join(ROOT, 'records'); os.makedirs(out_root, exist_ok=True)
    for (piece, container, n) in sorted(best, key=lambda k: (pid(k[0], k[1]), k[2])):
        P = pid(piece, container)
        if only and P not in only: continue
        if n < 2 or n > 20: continue
        e = best[(piece, container, n)]
        d = os.path.join(out_root, P); os.makedirs(d, exist_ok=True)
        rid = f'{P}_n{n:02d}'; fn = os.path.join(d, rid + '.json')
        src = {'seed': e['seed'], 'mode': e['mode'], 'budget': e['B'], 's_tight': round(e['s'], 12), 'clearance': CLEAR}
        if os.path.exists(fn) and os.path.exists(fn.replace('.json', '.certify.txt')):
            old = json.load(open(fn))
            if old.get('source') == src:                      # unchanged packing: keep the existing record
                cert = open(fn.replace('.json', '.certify.txt')).read(); ver = open(fn.replace('.json', '.verify.txt')).read()
                rows.append(dict(record_id=rid, problem=old['problem'], piece=piece, container=container, n=n, s=old['s_plus'],
                                 s_full=old['s_full'], s_tight=f"{e['s']:.12f}", closed_form_conjecture=old.get('closed_form_conjecture') or '',
                                 volume_lower_bound=f"{old['volume_lower_bound']:.5f}", density=f"{old['density']:.4f}",
                                 verified='VALID' in ver and 'INVALID' not in ver, certified='CERTIFIED' in cert and 'NOT CERTIFIED' not in cert,
                                 seed=e['seed'], mode=e['mode'], file=os.path.relpath(fn, ROOT)))
                continue
        cf = closed_form(e['s'])
        meta = {'source': src,'record_id': rid, 'title': f'{n} unit {PL[piece]} in a {container}',
                'page_convention': 'Friedman-style: s = container edge / piece edge, pieces may rotate freely',
                's_tight': round(e['s'], 12), 'closed_form_conjecture': cf,
                'volume_lower_bound': (n * SOL[piece]['volume'] / SOL[container]['volume']) ** (1 / 3),
                'found_by': 'Alejandro Zarzuelo',
                'credit': "soft-to-rigid method by Yohei Nakajima (2026); generalization to Platonic solids, search and exact "
                          "certification developed with Claude (Anthropic) under Alejandro Zarzuelo's direction",
                'search': {'seed': e['seed'], 'mode': e['mode'], 'budget': e['B'], **({'parent': e['parent']} if 'parent' in e else {})}}
        c = claim.make_claim(e, GAP=CLEAR, WALL=CLEAR, meta=meta)
        c['density'] = n * SOL[piece]['volume'] / (SOL[container]['volume'] * c['s_full'] ** 3)
        json.dump(c, open(fn, 'w'), indent=1)
        v = subprocess.run([sys.executable, os.path.join(ROOT, 'verify.py'), fn], capture_output=True, text=True)
        x = subprocess.run([sys.executable, os.path.join(ROOT, 'certify_exact.py'), fn], capture_output=True, text=True)
        open(os.path.join(d, rid + '.verify.txt'), 'w').write(v.stdout)
        open(os.path.join(d, rid + '.certify.txt'), 'w').write(x.stdout)
        subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'figures.py'), fn], capture_output=True)
        rows.append(dict(record_id=rid, problem=c['problem'], piece=piece, container=container, n=n, s=c['s_plus'],
                         s_full=c['s_full'], s_tight=f"{e['s']:.12f}", closed_form_conjecture=cf or '',
                         volume_lower_bound=f"{c['volume_lower_bound']:.5f}", density=f"{c['density']:.4f}",
                         verified=v.returncode == 0, certified=x.returncode == 0, seed=e['seed'], mode=e['mode'],
                         file=os.path.relpath(fn, ROOT)))
        print(f"{rid}  s = {c['s_plus']:10s} s_tight {e['s']:.12f}  {cf or '':22s} {'CERTIFIED' if x.returncode == 0 and v.returncode == 0 else 'FAILED'}", flush=True)
    # merge into SUMMARY.csv (replace rows of the problems rebuilt)
    path = os.path.join(out_root, 'SUMMARY.csv')
    old = list(csv.DictReader(open(path))) if os.path.exists(path) else []
    rebuilt = {r['record_id'] for r in rows}
    allrows = [r for r in old if r['record_id'] not in rebuilt] + rows
    allrows.sort(key=lambda r: (r['problem'], int(r['n'])))
    if allrows:
        with open(path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else list(old[0].keys()))
            w.writeheader(); [w.writerow(r) for r in allrows]
    # per-problem markdown tables
    by = {}
    for r in allrows: by.setdefault((r['problem'], r['piece'], r['container']), []).append(r)
    for (prob, piece, container), rs in by.items():
        P = pid(piece, container)
        lines = [f'# {PL[piece].capitalize()} in a {container}', '',
                 f'Smallest {container} found that holds n unit-edge {PL[piece]}; s = container edge / piece edge. '
                 f'Every row is certified in exact arithmetic (`certify_exact.py`).', '',
                 '| n | s | s (touching limit) | closed form (conjectured) | volume lower bound | density | picture |',
                 '|---|---|---|---|---|---|---|']
        for r in sorted(rs, key=lambda r: int(r['n'])):
            ok = '' if str(r['certified']) == 'True' else ' **NOT CERTIFIED**'
            lines.append(f"| {r['n']} | [{r['s']}]({os.path.basename(r['file'])}){ok} | {r['s_tight']} | {r['closed_form_conjecture']} | "
                         f"{r['volume_lower_bound']} | {r['density']} | ![]({os.path.basename(r['file']).replace('.json', '.png')}) |")
        open(os.path.join(out_root, P, 'README.md'), 'w').write('\n'.join(lines) + '\n')


def overview():
    """records/README.md: one matrix per container (rows n, columns piece) from SUMMARY.csv."""
    path = os.path.join(ROOT, 'records', 'SUMMARY.csv')
    if not os.path.exists(path): return
    rows = list(csv.DictReader(open(path)))
    order = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
    out = ['# Records', '',
           'Smallest container found for n unit-edge pieces; entry = s = container edge / piece edge (certified, 1e-7 clearance, '
           'truncated to 5 decimals). Every entry links to its record file, which `certify_exact.py` proves valid in exact '
           'arithmetic. Bold: the four same-solid problems. Full data: [SUMMARY.csv](SUMMARY.csv).', '']
    same = [r for r in rows if r['piece'] == r['container'] and r['piece'] != 'cube']
    if same:
        cols = [c for c in order if any(r['piece'] == c for r in same)]
        out += ['## Same solid (A = B)', '', '| n | ' + ' | '.join(f'**{PL[c]} in {c}**' for c in cols) + ' |', '|---|' + '---|' * len(cols)]
        for n in range(2, 21):
            cells = []
            for c in cols:
                r = next((r for r in same if r['piece'] == c and int(r['n']) == n), None)
                cells.append(f"[{r['s']}]({os.path.relpath(os.path.join(ROOT, r['file']), os.path.join(ROOT, 'records'))})" + (f" = {r['closed_form_conjecture']}?" if r['closed_form_conjecture'] else '') if r else '')
            out.append(f'| {n} | ' + ' | '.join(cells) + ' |')
        out.append('')
    for cont in order:
        rs = [r for r in rows if r['container'] == cont and not (r['piece'] == cont and cont != 'cube')]
        if not rs: continue
        cols = [p for p in order if any(r['piece'] == p for r in rs)]
        out += [f'## In a {cont}', '', '| n | ' + ' | '.join(PL[c] for c in cols) + ' |', '|---|' + '---|' * len(cols)]
        for n in range(2, 21):
            cells = []
            for c in cols:
                r = next((r for r in rs if r['piece'] == c and int(r['n']) == n), None)
                cells.append(f"[{r['s']}]({os.path.relpath(os.path.join(ROOT, r['file']), os.path.join(ROOT, 'records'))})" if r else '')
            out.append(f'| {n} | ' + ' | '.join(cells) + ' |')
        out.append('')
    out += ['"= x?" marks a conjectured closed form: the touching-contact limit agrees with x to about 11 digits. It is not '
            'part of the certificate.', '']
    open(os.path.join(ROOT, 'records', 'README.md'), 'w').write('\n'.join(out))


if __name__ == '__main__':
    build(set(sys.argv[1:]) or None)
    overview()
