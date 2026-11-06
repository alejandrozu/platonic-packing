#!/usr/bin/env python3
"""Relations between the pattern classes (6 Nov 2026).

Per 3D record, a boolean for each class, then for every ordered pair of classes (A, B):
  P(B | A), the lift P(B | A) / P(B), and the count of records in both.
Formal implications (Lean theorems) are listed separately; the empirical ones are associations, not theorems.

Inputs: records/SUMMARY*.csv, docs/patterns/{features3d,inherit3d,contacts3d,transfer}.json, docs/optimality.json.
Output: docs/patterns/relations.json.
"""
import csv, json, os, re
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)

CLASSES = [
    ('plateau', 'P1 on a plateau'), ('deletion', 'P1 built by deletion'), ('frozen', 'P1 frozen subset of n+1'),
    ('insertion', 'P3 built by insertion'), ('composite', 'P4 composite or nested'), ('window', 'P5 lattice window'),
    ('one_orient', 'P6 one orientation class'), ('layered', 'P6 two or three layers'), ('symmetric', 'P7 symmetric'),
    ('closed', 'P8 closed form'), ('rational', 'P8 rational scale'), ('optimal', 'P9 proven optimal'),
    ('rattler', 'P10 has a rattler'), ('isostatic', 'P10 contacts >= 6n + 1'), ('transfer', 'P11 matched by transfer'),
]

FORMAL = [  # (from, to, Lean theorem, meaning)
    ('window', 'plateau', 'lattice_windows', 'a window of N pieces gives every n <= N at the same scale'),
    ('composite', 'transfer', 'Packing.transfer_piece / transfer_container', 'transfer is composition with one piece'),
    ('optimal', 'plateau', 'optimal_plateau_of_common_point / _of_one_piece', 'an extremal bound plus deletion proves a whole plateau'),
    ('deletion', 'plateau', 'Packing.restrict', 's(m) <= s(n) for m <= n'),
    ('rattler', 'plateau', 'Packing.restrict', 'removing a rattler keeps the scale: s(n-1) <= s(n) is attained without it'),
    ('window', 'one_orient', 'voronoi_packing', 'a single-lattice window uses one orientation'),
]


def main():
    rows = list(csv.DictReader(open(P('records', 'SUMMARY.csv')))) + list(csv.DictReader(open(P('records', 'SUMMARY_families.csv'))))
    s = {(r['problem'], int(r['n'])): float(r['s_tight']) for r in rows}
    feats = {f['record_id']: f for f in json.load(open(P('docs', 'patterns', 'features3d.json')))}
    inh = json.load(open(P('docs', 'patterns', 'inherit3d.json')))
    cont = {c['record_id']: c for c in json.load(open(P('docs', 'patterns', 'contacts3d.json')))} \
        if os.path.exists(P('docs', 'patterns', 'contacts3d.json')) else {}
    tr = json.load(open(P('docs', 'patterns', 'transfer.json'))) if os.path.exists(P('docs', 'patterns', 'transfer.json')) else {}
    trm = {m[0] for m in tr.get('matches', [])}
    st = json.load(open(P('docs', 'patterns', 'stats.json')))
    comp = {f'{p}_n{nn:02d}' if nn < 100 else f'{p}_n{nn}' for p, a, b, nn, _ in st['composites']} | set(st['nested_constructions'])
    opt = {e['record_id'] for e in json.load(open(P('docs', 'optimality.json')))['records'] if e['status'] == 'proven'}
    flags = {}
    for rid, f in feats.items():
        p, n = f['record_id'].rsplit('_n', 1)[0], f['n']
        v = s.get((p, n))
        if v is None: continue
        fam = inh.get(p, {})
        cf = f.get('closed_form') or ''
        c = cont.get(rid)
        flags[rid] = {
            'plateau': any(abs(s.get((p, m), -9) - v) < 1e-9 for m in (n - 1, n + 1)),
            'deletion': f.get('move') == 'monotone', 'frozen': fam.get(f'{n}-{n + 1}', 0) >= 0.999,
            'insertion': f.get('move') == 'ascend', 'composite': rid in comp,
            'window': bool(f.get('lattice')) and all((l or {}).get('lattice') for l in f['lattice']) and len(f['orient']) <= 4,
            'one_orient': len(f.get('orient', [])) == 1, 'layered': 2 <= len((f.get('layers') or {}).get('sizes', [])) <= 3,
            'symmetric': (f.get('sym') or {}).get('order', 1) > 1, 'closed': bool(cf),
            'rational': bool(cf) and not re.search(r'[√φπ]|sqrt', cf), 'optimal': rid in opt,
            'rattler': None if c is None else c['rattlers'] > 0, 'isostatic': None if c is None else c['excess'] >= 0,
            'transfer': rid in trm}
    keys = [k for k, _ in CLASSES]
    tot = {k: sum(1 for x in flags.values() if x[k]) for k in keys}
    base = {k: sum(1 for x in flags.values() if x[k] is not None) for k in keys}
    pair = {}
    for a in keys:
        for b in keys:
            if a == b: continue
            dom = [x for x in flags.values() if x[a] is not None and x[b] is not None]
            na = sum(1 for x in dom if x[a]); nb = sum(1 for x in dom if x[b]); nab = sum(1 for x in dom if x[a] and x[b])
            if na == 0 or nb == 0: continue
            pba = nab / na; pb = nb / len(dom)
            pair[f'{a}->{b}'] = {'n_a': na, 'n_ab': nab, 'p_b_given_a': round(pba, 4), 'p_b': round(pb, 4), 'lift': round(pba / pb, 3)}
    out = {'classes': CLASSES, 'formal': FORMAL, 'records': len(flags), 'totals': tot, 'domains': base, 'pairs': pair}
    json.dump(out, open(P('docs', 'patterns', 'relations.json'), 'w'), indent=1)
    strong = sorted(((v['lift'], k, v) for k, v in pair.items() if v['n_ab'] >= 20), reverse=True)
    for l, k, v in strong[:25]: print(f'{k:28s} lift {l:6.2f}  P(B|A) {v["p_b_given_a"]:.3f}  n_ab {v["n_ab"]}')
    print('totals', tot)


if __name__ == '__main__':
    main()
