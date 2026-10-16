#!/usr/bin/env python3
"""Independent bounded source/provenance audit; this is not a Lean proof.

Run with Python's standard library from any directory. No inputs are mutated.
The output records source binding only, never formal certification status.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'inputs'
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'


def number(x):
    assert not isinstance(x, bool)
    return Q(x)


def vector(v):
    return [number(x) for x in v]


def matrix(v):
    return [vector(row) for row in v]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def audit_record(row, kind, geometry, geometry_hash):
    path = INPUTS / row['file']
    original = path.read_bytes()
    assert digest(original) == row['sha256']
    rec = json.loads(original)
    folder = 'witnesses' if kind == 'cube' else 'witnesses_nd'
    w = json.loads((HERE / folder / (path.stem + '.json')).read_text())
    assert w['source_sha256'] == row['sha256']
    assert w['source_path'] == row['file'].replace('\\', '/')
    n, d = rec['n'], 3 if kind == 'cube' else rec['dim']
    assert n == row['n'] == w['n'] == len(rec['pieces'])
    assert w['record_id'] == path.stem and w['dimension'] == d
    assert len(w['centres']) == len(w['rotations']) == n
    assert vector(w['container_center']) == vector(rec.get('container_center', [0]*d))
    assert len(w['container_center']) == d
    for raw, centre in zip(rec['pieces'], w['centres']):
        assert vector(centre) == vector(raw[:d])
    keys = [(p['i'], p['j']) for p in w['planes']]
    assert keys == list(itertools.combinations(range(n), 2))
    assert len(keys) == w['unordered_pairs']
    for p in w['planes']:
        assert len(p['normal']) == d and number(p['lower']) < number(p['upper'])
    if kind == 'cube':
        assert rec['piece'] == rec['container'] == 'cube'
        assert number(w['scale']) == number(rec['s_full']) > 0
        assert len(w['quaternions']) == n
        for raw, q in zip(rec['pieces'], w['quaternions']):
            assert len(raw) == 7 and vector(q) == vector(raw[3:])
        corners = [list(p) for p in itertools.product((Q(-1, 2), Q(1, 2)), repeat=3)]
        assert matrix(w['template_vertices']) == corners
        return path.stem, d, None
    assert rec['piece'] == w['piece'] and rec['container'] == w['container']
    assert w['geometry_sha256'] == geometry_hash
    pg, cg = geometry[rec['piece']], geometry[rec['container']]
    assert pg['dim'] == cg['dim'] == d
    assert matrix(w['template_vertices']) == matrix(pg['V'])
    assert matrix(w['container_vertices']) == matrix(cg['V'])
    mu, sf = number(rec['mu']), number(rec['s_full'])
    assert mu == number(w['edge_ratio']) > 0
    assert number(w['s_full']) == sf
    assert number(w['scale']) == sf*mu > 0
    assert mu*mu*number(cg['edge2']) == number(pg['edge2'])
    assert len(w['raw_skews']) == len(w['diagonal_signs']) == len(w['cayley_inverses']) == n
    m = d*(d-1)//2
    for raw, S, D in zip(rec['pieces'], w['raw_skews'], w['diagonal_signs']):
        assert len(raw) == 2*d+m and vector(D) == vector(raw[d+m:])
        upper, s, offset = vector(raw[d:d+m]), matrix(S), 0
        assert len(s) == d and all(len(v) == d for v in s)
        for a in range(d):
            assert s[a][a] == 0
            for b in range(a+1, d):
                assert s[a][b] == upper[offset] and s[b][a] == -upper[offset]
                offset += 1
    k, l, t = len(pg['V']), len(cg['V']), w['barycentric_width']
    assert t == d+2 and len(w['indices']) == len(w['weights']) == n
    for ir, wr in zip(w['indices'], w['weights']):
        assert len(ir) == len(wr) == k
        for ix, wx in zip(ir, wr):
            assert len(ix) == len(wx) == t
            assert all(isinstance(z, int) and 0 <= z < l for z in ix)
            weights = vector(wx)
            assert all(z >= 0 for z in weights) and sum(weights, Q(0)) == 1
    return path.stem, d, str(mu)


def main():
    cubes = json.loads((HERE / 'inventory/catalogue-inventory.json').read_text())
    nd = json.loads((HERE / 'inventory/rational-nd-inventory.json').read_text())
    assert cubes['freeze_git_sha'] == nd['freeze_git_sha'] == FREEZE
    raw_geometry = (INPUTS / 'src/polytopes_nd.json').read_bytes()
    geometry = json.loads(raw_geometry)
    counts, mus, ids, errors = Counter(), Counter(), [], []
    for kind, rows in [('cube', cubes['cube_native_records']), ('nd', nd['records'])]:
        for row in rows:
            try:
                rid, d, mu = audit_record(row, kind, geometry, digest(raw_geometry))
                ids.append(rid)
                counts[kind] += 1
                counts[f'dimension_{d}'] += 1
                if mu is not None:
                    mus[mu] += 1
            except Exception as error:
                errors.append({'kind': kind, 'record': row['file'],
                    'error': str(error), 'type': type(error).__name__})
    assert len(set(ids)) == len(ids)
    selected = {r['piece'] for r in nd['records']} | {r['container'] for r in nd['records']}
    for pid in sorted(selected):
        g = geometry[pid]
        vs, e2 = matrix(g['V']), number(g['edge2'])
        assert all(sum(((a-b)**2 for a, b in zip(vs[i], vs[j])), Q(0)) == e2
            for i, j in g['edges'])
    passed = not errors and counts['cube'] == 99 and counts['nd'] == 303
    summary = {'freeze': FREEZE, 'checked_source_bindings': len(ids),
        'counts': dict(counts), 'edge_ratios': dict(mus), 'errors': errors,
        'result': 'PASS' if passed else 'INCOMPLETE_OR_FAIL'}
    (HERE / 'end-to-end-source-audit.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
