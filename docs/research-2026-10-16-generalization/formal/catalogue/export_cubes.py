#!/usr/bin/env python3
"""Export exact, source-bound witnesses for the frozen cube catalogue.

Python proposes separating planes; Lean must independently check all numbers.
Unquoted JSON numbers retain the production checker's Fraction(float) meaning.
No scale, centre, orientation or vertex is perturbed by this exporter.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
VERTICES = list(itertools.product((Q(-1, 2), Q(1, 2)), repeat=3))
AXES = [(Q(1), Q(0), Q(0)), (Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(1))]


def number(x):
    if isinstance(x, bool):
        raise ValueError('Boolean is not a coordinate')
    return Q(x)


def rotation(q):
    w, x, y, z = q
    norm = sum(a*a for a in q)
    if norm <= 0:
        raise ValueError('Zero quaternion')
    return [[a/norm for a in row] for row in (
        (w*w+x*x-y*y-z*z, 2*(x*y-w*z), 2*(x*z+w*y)),
        (2*(x*y+w*z), w*w-x*x+y*y-z*z, 2*(y*z-w*x)),
        (2*(x*z-w*y), 2*(y*z+w*x), w*w-x*x-y*y+z*z))]


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def determinant(r):
    return dot(r[0], cross(r[1], r[2]))


def proposal(a, b, ra, rb, ca, cb):
    """All pairs, including distant pairs, receive explicit separating planes."""
    for k,u in enumerate(AXES):
        lo,hi=max(p[k] for p in a),min(p[k] for p in b)
        if lo < hi:
            return {'normal':u,'lower':lo,'upper':hi}
        lo,hi=max(-p[k] for p in a),min(-p[k] for p in b)
        if lo < hi:
            return {'normal':tuple(-x for x in u),'lower':lo,'upper':hi}
    candidates = list(AXES)
    candidates.append(tuple(float(y-x) for x, y in zip(ca, cb)))
    ea = list(zip(*ra))
    eb = list(zip(*rb))
    candidates.extend(ea)
    candidates.extend(eb)
    candidates.extend(cross(x, y) for x in ea for y in eb)
    scored = []
    af = [list(map(float, x)) for x in a]
    bf = [list(map(float, x)) for x in b]
    for c in candidates:
        cf = list(map(float, c))
        norm = math.sqrt(sum(x*x for x in cf))
        if norm < 1e-15:
            continue
        cf = [x/norm for x in cf]
        ap = [sum(x*y for x, y in zip(cf, p)) for p in af]
        bp = [sum(x*y for x, y in zip(cf, p)) for p in bf]
        for sign in (1, -1):
            gap = min(sign*x for x in bp)-max(sign*x for x in ap)
            scored.append((gap, [Q(sign*x).limit_denominator(10**12) for x in cf]))
    scored.sort(key=lambda x: x[0], reverse=True)
    for _, u in scored:
        lo = max(dot(u, p) for p in a)
        hi = min(dot(u, p) for p in b)
        if lo < hi:
            # Rational endpoints have a positive verified gap. No rounding.
            return {'normal':u, 'lower':lo, 'upper':hi}
    raise ValueError('No strictly separating plane found')


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {k:encode(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)):
        return [encode(v) for v in x]
    return x


def export(path):
    raw = path.read_bytes()
    rec = json.loads(raw)
    if rec['piece'] != 'cube' or rec['container'] != 'cube':
        raise ValueError('Not a cube-in-cube witness')
    n = rec['n']
    if not isinstance(n,int) or n < 2 or len(rec['pieces']) != n:
        raise ValueError('Invalid piece count')
    scale = number(rec['s_full'])
    cc = [number(x) for x in rec.get('container_center',[0,0,0])]
    if scale <= 0 or len(cc) != 3:
        raise ValueError('Invalid container')
    centres, quaternions, rotations, vertices = [], [], [], []
    for p in rec['pieces']:
        if len(p) != 7:
            raise ValueError('Invalid placement shape')
        c, q = list(map(number,p[:3])), list(map(number,p[3:]))
        r = rotation(q)
        if any(dot(r[i],r[j]) != int(i == j) for i in range(3) for j in range(3)) or determinant(r) != 1:
            raise ValueError('Rotation algebra failure')
        v = [tuple(c[k]+dot(r[k],p) for k in range(3)) for p in VERTICES]
        if any(abs(p[k]-cc[k]) > scale/2 for p in v for k in range(3)):
            raise ValueError('Containment failure')
        centres.append(c); quaternions.append(q); rotations.append(r); vertices.append(v)
    planes = []
    for i,j in itertools.combinations(range(n),2):
        planes.append({'i':i,'j':j,**proposal(vertices[i],vertices[j],rotations[i],rotations[j],centres[i],centres[j])})
    return encode({
        'record_id':path.stem,'n':n,'dimension':3,'source_path':str(path.relative_to(HERE/'inputs')).replace('\\','/'),
        'source_sha256':hashlib.sha256(raw).hexdigest(),
        'numeric_semantics':'JSON numbers via binary64 then exact Fraction; rational strings via Fraction',
        'scale':scale,'container_center':cc,'template_vertices':VERTICES,
        'centres':centres,'quaternions':quaternions,'rotations':rotations,
        'planes':planes,'vertex_wall_tests':n*8*6,'unordered_pairs':n*(n-1)//2,
    })


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--only',nargs='*')
    args=ap.parse_args()
    out=HERE/'witnesses'; out.mkdir(parents=True,exist_ok=True)
    report={'exporter_is_trusted_for_provenance_only':True,'formal_verification':'Pending Lean compilation; Python success is not a Lean proof','exported':[],'excluded':[]}
    for path in sorted((HERE/'inputs'/'records').rglob('*.json')):
        if args.only and path.stem not in args.only:
            continue
        rec=json.loads(path.read_bytes())
        if rec.get('piece')!='cube' or rec.get('container')!='cube':
            continue
        if rec.get('n',0)>args.max_n:
            continue
        t=time.monotonic()
        try:
            cert=export(path)
            dest=out/(path.stem+'.json')
            dest.write_text(json.dumps(cert,indent=2)+'\n',encoding='utf8')
            item={k:cert[k] for k in ('record_id','n','source_path','source_sha256','vertex_wall_tests','unordered_pairs')}
            item.update(witness_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),export_seconds=round(time.monotonic()-t,3))
            report['exported'].append(item)
            print(json.dumps({'exported':path.stem,'seconds':item['export_seconds']}),flush=True)
        except (ValueError,KeyError,ZeroDivisionError) as err:
            report['excluded'].append({'source_path':str(path),'reason':str(err)})
            print(json.dumps({'excluded':path.stem,'reason':str(err)}),flush=True)
        (HERE/'export-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
