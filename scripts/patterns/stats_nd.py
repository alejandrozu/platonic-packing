"""Aggregate statistics of the 4D-6D structural features (docs/patterns/stats_nd.json).

Reads docs/patterns/features_nd.json and docs/patterns/inherit_nd.json (scripts/patterns/features_nd.py) and the
3D aggregates of docs/patterns/stats.json for comparison. Tabulates, per dimension and per container:
orientation classes, configuration symmetry (exact and loose), relative rotations of orientation classes
(rational, simple, isoclinic; the commonest angle tuples), lattice windows, layers, plateaus and subset
inheritance (frozen subsets: record k is k pieces of record N moved rigidly by a container symmetry).
"""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'docs', 'patterns')


def share(a, b): return round(a / b, 4) if b else None


def main():
    F = json.load(open(os.path.join(P, 'features_nd.json')))
    I = json.load(open(os.path.join(P, 'inherit_nd.json')))
    s3 = json.load(open(os.path.join(P, 'stats.json')))
    out = {'records': len(F), 'families': len({f['problem'] for f in F})}
    # plateaus: maximal runs of equal s_full in n (relative 1e-9), from the records themselves
    S = collections.defaultdict(dict)
    for f in F: S[f['problem']][f['n']] = f['s']
    def plateau_ids():
        ids = set()
        for fam, by in S.items():
            for n in by:
                if (n - 1 in by and abs(by[n - 1] - by[n]) < 1e-9 * by[n]) or (n + 1 in by and abs(by[n + 1] - by[n]) < 1e-9 * by[n]):
                    ids.add(f'{fam}_n{n:02d}')
        return ids
    plat = plateau_ids()
    groups = collections.defaultdict(list)
    for f in F:
        groups[('dim', f['dim'])].append(f)
        groups[('container', f['container'])].append(f)
    def summarize(L):
        n = len(L)
        oc = collections.Counter(min(len(f['orient']), 9) for f in L)
        sym = collections.Counter(f['sym']['order'] for f in L)
        rel = [r for f in L if f['rel'] for r in f['rel']]
        ang = collections.Counter(tuple(round(a, 2) for a in r['angles']) for r in rel if r['rational'])
        lat = [f for f in L if f['lattice'] and any(x and x.get('lattice') for x in f['lattice'])]
        lat1 = [f for f in lat if len(f['orient']) == 1]
        fewl = sum(1 for f in L if f['layers'] and len(f['layers']['sizes']) <= max(1, round(f['n'] ** (1 / f['dim']))) + 1)
        return {
            'records': n,
            'orientation_classes': {('9+' if k == 9 else str(k)): v for k, v in sorted(oc.items())},
            'single_orientation': share(oc[1], n),
            'symmetric': share(sum(v for k, v in sym.items() if k > 1), n),
            'symmetric_loose': share(sum(1 for f in L if f['sym_loose']['order'] > 1), n),
            'symmetry_orders': dict(sorted(sym.items())),
            'max_symmetry': max((f['sym']['order'], f['record_id']) for f in L),
            'relative_pairs': len(rel),
            'relative_rational': share(sum(1 for r in rel if r['rational']), len(rel)),
            'relative_simple': share(sum(1 for r in rel if r['simple']), len(rel)),
            'relative_isoclinic': share(sum(1 for r in rel if r['isoclinic']), len(rel)),
            'common_rational_angles': [[list(k), v] for k, v in ang.most_common(8)],
            'lattice_windows': len(lat), 'lattice_single_orientation': len(lat1),
            'few_layers': share(fewl, n),
            'on_plateau': share(sum(1 for f in L if f['record_id'] in plat), n),
        }
    out['by_dim'] = {str(k[1]): summarize(v) for k, v in sorted(groups.items()) if k[0] == 'dim'}
    out['by_container'] = {k[1]: summarize(v) for k, v in sorted(groups.items()) if k[0] == 'container'}
    # associations (lift) within ND
    def lift(A, B, L):
        n = len(L); a = [f for f in L if A(f)]; b = sum(1 for f in L if B(f)); ab = sum(1 for f in a if B(f))
        return round((ab / len(a)) / (b / n), 3) if a and b else None
    single = lambda f: len(f['orient']) == 1
    symm = lambda f: f['sym']['order'] > 1
    latt = lambda f: bool(f['lattice']) and any(x and x.get('lattice') for x in f['lattice'])
    onp = lambda f: f['record_id'] in plat
    cf = lambda f: bool(f['closed_form'])
    out['lifts'] = {'symmetric|single_orientation': lift(single, symm, F), 'lattice|symmetric': lift(symm, latt, F),
                    'plateau|lattice': lift(latt, onp, F), 'plateau|symmetric': lift(symm, onp, F),
                    'closed_form|symmetric': lift(symm, cf, F), 'single_orientation|plateau': lift(onp, single, F)}
    # inheritance
    inh = {'pairs': len(I)}
    for d in (4, 5, 6):
        J = [x for x in I if next((f['dim'] for f in F if f['problem'] == x['problem']), None) == d]
        cons = [x for x in J if x['N'] == x['k'] + 1]
        inh[str(d)] = {'pairs': len(J), 'consecutive': len(cons), 'consecutive_frozen': sum(1 for x in cons if x['f'] == 1),
                       'frozen_any_gap': sum(1 for x in J if x['f'] == 1),
                       'partial_ge_0.8': sum(1 for x in J if 0.8 <= x['f'] < 1),
                       'by_gap': {str(g): [sum(1 for x in J if x['N'] - x['k'] == g and x['f'] == 1),
                                           sum(1 for x in J if x['N'] - x['k'] == g)] for g in range(1, 7)}}
    fz = collections.Counter(x['problem'] for x in I if x['f'] == 1 and x['N'] == x['k'] + 1)
    inh['frozen_consecutive_by_family'] = dict(fz.most_common(15))
    out['inheritance'] = inh
    # 3D reference
    f3 = s3['features3d']; i3 = s3['inheritance']
    out['reference_3d'] = {'records': f3['records'],
                           'single_orientation': share(f3['orientation_classes'].get('1', 0), f3['records']),
                           'symmetric': share(f3['records'] - f3['symmetry_order'].get('1', 0), f3['records']),
                           'consecutive_frozen': share(i3['consecutive_frozen'], i3['consecutive_pairs'])}
    json.dump(out, open(os.path.join(P, 'stats_nd.json'), 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('records', 'families', 'lifts', 'reference_3d')}, indent=1))
    for d, v in out['by_dim'].items():
        print(d, {k: v[k] for k in ('records', 'single_orientation', 'symmetric', 'relative_rational', 'relative_isoclinic', 'lattice_windows', 'on_plateau')})
    for d in ('4', '5', '6'): print(d, out['inheritance'][d])


if __name__ == '__main__':
    main()
