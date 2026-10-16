#!/usr/bin/env python3
"""Exact Python audit of frozen ND reference edges and native scale factors.

Run from any directory with the standard Python library:
  python catalogue/nd-edge-scale-audit.py

This complements the Lean packing certificates. It is not a Lean proof of
polytope regularity, adjacency classification, minimum distance, or optimality.
No floating-point arithmetic or external package is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from math import gcd, isqrt
from pathlib import Path
import platform
import re


FORMAL = Path(__file__).resolve().parents[1]
REGISTRY = 'catalogue/algebraic/generated-nd-pilots-registry.json'
REGISTRY_SHA256 = 'e568993b3400835c98d52b18c048c1bd5044bc61573fae559eca265e0b5aae36'
GEOMETRY = 'catalogue/algebraic/inputs/src/polytopes_nd.json'
GEOMETRY_SHA256 = '668f2e176e56e11738722784a6286784151479f24820db13910bd627627b596e'
FREEZE = '1abc63218db34cea95802aeb3b6d4a6b6fe1c61b'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_json(formal, relative, expected):
    path = formal / relative
    actual = digest(path)
    if actual != expected:
        raise ValueError('Frozen input hash mismatch: ' + relative)
    return json.loads(path.read_text(encoding='utf8'))


def clean(value):
    return {r: c for r, c in value.items() if c}


def parse(text):
    """Parse native rational linear combinations of square-free radicals."""
    compact = str(text).replace(' ', '')
    terms = re.findall(r'[+-]?[^+-]+', compact)
    if ''.join(terms) != compact or not terms:
        raise ValueError('Unsupported exact native expression: ' + str(text))
    out = {}
    for term in terms:
        if 'sqrt' in term:
            coefficient, radical = term.split('sqrt')
            coefficient = coefficient.rstrip('*')
            value = (Fraction(1) if coefficient in ('', '+') else
                Fraction(-1) if coefficient == '-' else Fraction(coefficient))
            radicand = int(radical)
            if radicand < 1 or any(radicand % (p*p) == 0
                for p in range(2, isqrt(radicand)+1)):
                raise ValueError('Expected positive square-free native radicand')
        else:
            value, radicand = Fraction(term), 1
        out[radicand] = out.get(radicand, Fraction(0)) + value
    return clean(out)


def add(x, y):
    out = dict(x)
    for r, c in y.items():
        out[r] = out.get(r, Fraction(0)) + c
    return clean(out)


def sub(x, y):
    return add(x, {r: -c for r, c in y.items()})


def mul(x, y):
    out = {}
    for r, c in x.items():
        for s, d in y.items():
            common = gcd(r, s)
            radical = r*s // (common*common)
            out[radical] = out.get(radical, Fraction(0)) + c*d*common
    return clean(out)


def native_mu_positive(mu):
    """Exact sign for (a+b sqrt(5)), optionally times positive sqrt(2)."""
    if set(mu) <= {1, 5}:
        a, b = mu.get(1, Fraction(0)), mu.get(5, Fraction(0))
    elif set(mu) <= {2, 10}:
        a, b = mu.get(2, Fraction(0)), mu.get(10, Fraction(0))
    else:
        raise ValueError('Unexpected frozen native mu primitive roots')
    if a >= 0 and b >= 0:
        return a > 0 or b > 0
    if a <= 0 and b <= 0:
        return False
    return a*a > 5*b*b if a >= 0 else 5*b*b > a*a


def encoded(value):
    return {str(r): str(c) for r, c in sorted(value.items())}


def run(formal):
    registry = checked_json(formal, REGISTRY, REGISTRY_SHA256)
    geometry = checked_json(formal, GEOMETRY, GEOMETRY_SHA256)
    records = registry['records']
    if len(records) != 45 or len({r['record_id'] for r in records}) != 45:
        raise ValueError('Expected precisely the frozen 45 distinct ND pilots')
    shapes = set()
    record_rows = []
    for row in records:
        if row['source_freeze'] != FREEZE or row['geometry_source_path'] != GEOMETRY or row['geometry_source_sha256'] != GEOMETRY_SHA256:
            raise ValueError('Unexpected ND source freeze/geometry reference')
        source = 'catalogue/algebraic/inputs/' + row['source_path']
        raw = checked_json(formal, source, row['source_sha256'])
        if any(raw[key] != row[key] for key in ['piece', 'container', 'n']):
            raise ValueError('Native identity differs from frozen registry')
        if raw['dim'] != row['dimension']:
            raise ValueError('Native dimension differs from frozen registry')
        mu = parse(raw['mu'])
        mu_squared = mul(mu, mu)
        piece_edge = parse(geometry[row['piece']]['edge2'])
        container_edge = parse(geometry[row['container']]['edge2'])
        if not native_mu_positive(mu) or mul(mu_squared, container_edge) != piece_edge:
            raise ValueError('Exact native edge-ratio identity failed: ' + row['record_id'])
        record_rows.append(dict(record_id=row['record_id'], source_path=source,
            source_sha256=row['source_sha256'], piece=row['piece'], container=row['container'],
            dimension=row['dimension'], native_mu=raw['mu'], native_mu_positive=True,
            mu_squared=encoded(mu_squared), piece_edge_squared=encoded(piece_edge),
            container_edge_squared=encoded(container_edge), edge_ratio_identity=True))
        shapes.update([row['piece'], row['container']])
    shape_rows = []
    total_edges = 0
    for name in sorted(shapes):
        shape = geometry[name]
        vertices = [[parse(x) for x in row] for row in shape['V']]
        if not vertices or any(len(v) != shape['dim'] for v in vertices):
            raise ValueError('Unexpected reference-coordinate dimension')
        expected = parse(shape['edge2'])
        edges = shape['edges']
        if not edges or len({tuple(sorted(e)) for e in edges}) != len(edges):
            raise ValueError('Empty or duplicated listed reference edges')
        for edge in edges:
            if len(edge) != 2 or any(not isinstance(i, int) or not 0 <= i < len(vertices) for i in edge) or edge[0] == edge[1]:
                raise ValueError('Malformed listed reference edge')
            i, j = edge
            distance = {}
            for a, b in zip(vertices[i], vertices[j]):
                delta = sub(a, b)
                distance = add(distance, mul(delta, delta))
            if distance != expected:
                raise ValueError('Exact reference edge length failed: ' + name)
        total_edges += len(edges)
        semantic_bytes = json.dumps(shape, sort_keys=True, ensure_ascii=False,
            separators=(',', ':')).encode('utf8')
        shape_rows.append(dict(shape=name, dimension=shape['dim'], vertex_count=len(vertices),
            listed_edges_checked=len(edges), edge_squared=encoded(expected),
            geometry_entry_sha256=hashlib.sha256(semantic_bytes).hexdigest(),
            reference_edge=edges[0], all_listed_edge_identities=True))
    if len(shapes) != 12 or total_edges != 2490:
        raise ValueError('Unexpected frozen reference audit coverage')
    return dict(schema='nd-reference-edge-python-audit-v1',
        created_utc=datetime.now(timezone.utc).isoformat(), status='passed_python_exact_audit',
        lean_verification=False, arithmetic='fractions.Fraction and exact square-free radical coefficients',
        scope='All listed reference edges and all 45 positive native edge-ratio factors',
        source_freeze=FREEZE, registry_path=REGISTRY, registry_sha256=REGISTRY_SHA256,
        geometry_path=GEOMETRY, geometry_sha256=GEOMETRY_SHA256,
        auditor_path='catalogue/nd-edge-scale-audit.py', auditor_sha256=digest(Path(__file__)),
        python_version=platform.python_version(), shape_count=12, listed_edges_checked=2490,
        records_checked=45, shapes=shape_rows, records=record_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--formal-root', type=Path, default=FORMAL)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    receipt = run(args.formal_root.resolve())
    output = args.output or args.formal_root / 'catalogue/nd-edge-scale-audit.json'
    output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    print(json.dumps({k: receipt[k] for k in ['status', 'lean_verification', 'shape_count',
        'listed_edges_checked', 'records_checked', 'auditor_sha256']}))


if __name__ == '__main__':
    main()
