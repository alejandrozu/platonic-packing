#!/usr/bin/env python3
"""Export exact source-bound ND witnesses; successful export is not a Lean proof.

Every original placement and scale is preserved with Fraction(float) semantics.
Only separating directions and barycentric decompositions are proposed here;
Lean must independently check them.  Containment targets the convex hull of the
actual canonical container vertices, not an assumed halfspace reconstruction.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time

from export_cubes import encode, dot, number

HERE = Path(__file__).resolve().parent
INPUTS = HERE/'inputs'
GEOMETRY = json.loads((INPUTS/'src/polytopes_nd.json').read_text(encoding='utf8'))
_TEMPLATES = {}
_SIMPLEX = {}


def determinant(matrix):
    a = [list(row) for row in matrix]
    n = len(a)
    value = Q(1)
    for k in range(n):
        pivot = next((i for i in range(k,n) if a[i][k]), None)
        if pivot is None:
            return Q(0)
        if pivot != k:
            a[pivot], a[k] = a[k], a[pivot]
            value = -value
        pv = a[k][k]
        value *= pv
        for i in range(k+1,n):
            factor = a[i][k] / pv
            for j in range(k+1,n):
                a[i][j] -= factor*a[k][j]
    return value


def inverse(matrix):
    n = len(matrix)
    a = [list(row)+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(matrix)]
    for k in range(n):
        pivot = next((i for i in range(k,n) if a[i][k]), None)
        if pivot is None:
            raise ValueError('Singular exact matrix')
        a[pivot], a[k] = a[k], a[pivot]
        pv = a[k][k]
        a[k] = [x/pv for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                factor = a[i][k]
                a[i] = [x-factor*y for x,y in zip(a[i],a[k])]
    return [row[n:] for row in a]


def cayley_source(raw, dimension):
    d = dimension
    m = d*(d-1)//2
    if len(raw) != 2*d+m:
        raise ValueError('Invalid ND placement shape')
    centre = list(map(number,raw[:d]))
    upper = list(map(number,raw[d:d+m]))
    signs = list(map(number,raw[d+m:]))
    if any(x not in (Q(-1),Q(1)) for x in signs) or math.prod(signs) != 1:
        raise ValueError('Invalid diagonal signs')
    skew = [[Q(0) for _ in range(d)] for _ in range(d)]
    t = 0
    for i in range(d):
        for j in range(i+1,d):
            skew[i][j],skew[j][i] = upper[t],-upper[t]
            t += 1
    return centre,skew,signs


def cayley(raw, dimension):
    d = dimension
    centre,skew,signs = cayley_source(raw,d)
    a = [[Q(int(i==j))-skew[i][j] for j in range(d)] for i in range(d)]
    ainv = inverse(a)
    # (I-S)^-1(I+S) = 2(I-S)^-1-I; exact, with no float conversion.
    r = [[signs[i]*(2*ainv[i][j]-int(i==j)) for j in range(d)] for i in range(d)]
    if any(dot(r[i],r[j]) != int(i==j) for i in range(d) for j in range(d)):
        raise ValueError('Cayley orthogonality failed')
    if determinant(r) != 1:
        raise ValueError('Cayley proper orientation failed')
    return centre,skew,signs,ainv,r


def source_binding_check(cert,rec):
    """Bind reused arithmetic witnesses to native scalars, not just a hash label.

    Lean checks the inverse/Cayley/Gram conditions; here the unverified import
    boundary also explicitly checks that its raw inputs are the source values.
    """
    d=rec['dim']
    sources=[cayley_source(p,d) for p in rec['pieces']]
    expected={
        'dimension':d,'n':rec['n'],'piece':rec['piece'],'container':rec['container'],
        'centres':[x[0] for x in sources],'raw_skews':[x[1] for x in sources],
        'diagonal_signs':[x[2] for x in sources],
        'template_vertices':template(rec['piece'])[1],
        'container_vertices':template(rec['container'])[1],
        's_full':number(rec['s_full']),'edge_ratio':number(rec['mu']),
        'scale':number(rec['s_full'])*number(rec['mu']),
        'container_center':list(map(number,rec.get('container_center',[0]*d))),
    }
    if any(cert[k]!=encode(v) for k,v in expected.items()):
        raise ValueError('Cached witness differs from native source parameters')


def template(pid):
    if pid not in _TEMPLATES:
        raw = GEOMETRY[pid]
        vertices = [tuple(map(number,p)) for p in raw['V']]
        _TEMPLATES[pid] = (raw,vertices,{v:i for i,v in enumerate(vertices)})
    return _TEMPLATES[pid]


def scipy_tools():
    """Use an existing optional runtime only for untrusted proposal generation."""
    try:
        import numpy as np
        from scipy.spatial import Delaunay
        from scipy.optimize import linprog
    except ImportError:
        local = HERE.parents[3]/'work/website-runtime/Lib/site-packages'
        if str(local) not in sys.path:
            sys.path.insert(0,str(local))
        import numpy as np
        from scipy.spatial import Delaunay
        from scipy.optimize import linprog
    return np,Delaunay,linprog


def pad_membership(pairs, dimension):
    pairs = [(int(i),Q(w)) for i,w in pairs if w]
    if len(pairs) > dimension+2:
        raise ValueError('Barycentric support exceeds fixed width')
    return pairs+[(0,Q(0))]*(dimension+2-len(pairs))


def hypercube_membership(point, lookup):
    d = len(point)
    shifted = [x+Q(1,2) for x in point]
    if any(x<0 or x>1 for x in shifted):
        raise ValueError('Point outside exact hypercube')
    order = sorted(range(d),key=lambda i:shifted[i],reverse=True)
    v = [Q(-1,2)]*d
    pairs = [(lookup[tuple(v)],1-shifted[order[0]])]
    for rank,i in enumerate(order):
        v[i] = Q(1,2)
        w = shifted[i]-(shifted[order[rank+1]] if rank+1<d else 0)
        pairs.append((lookup[tuple(v)],w))
    return pad_membership(pairs,d)


def cross_membership(point, lookup):
    d = len(point)
    slack = 1-sum(map(abs,point),Q(0))
    if slack < 0:
        raise ValueError('Point outside exact cross polytope')
    pairs=[]
    for i,x in enumerate(point):
        v=[Q(0)]*d
        v[i] = 1 if x>=0 else -1
        pairs.append((lookup[tuple(v)],abs(x)))
    for sign in (-1,1):
        v=[Q(0)]*d
        v[0]=sign
        pairs.append((lookup[tuple(v)],slack/2))
    return pad_membership(pairs,d)


def simplex_data(pid):
    if pid not in _SIMPLEX:
        np,Delaunay,_ = scipy_tools()
        _,vertices,_ = template(pid)
        tri = Delaunay(np.array(vertices,dtype=float))
        matrices=[]
        for simplex in tri.simplices:
            ids=list(map(int,simplex))
            a = [[vertices[j][i] for j in ids] for i in range(len(vertices[0]))]+[[Q(1)]*len(ids)]
            try:
                inv = inverse(a)
            except ValueError:
                inv = None
            matrices.append((ids,inv))
        _SIMPLEX[pid]=(tri,matrices)
    return _SIMPLEX[pid]


def simplex_membership(pid,point):
    tri,matrices=simplex_data(pid)
    candidate=int(tri.find_simplex([list(map(float,point))],tol=1e-10)[0])
    rhs=list(point)+[Q(1)]
    order=([candidate] if candidate>=0 else [])+[i for i in range(len(matrices)) if i!=candidate]
    for j in order:
        ids,inv=matrices[j]
        if inv is None:
            continue
        weights=[dot(row,rhs) for row in inv]
        if all(w>=0 for w in weights):
            return pad_membership(zip(ids,weights),len(point))
    # Optional float LP proposes a basis only; exact reconstruction is required.
    np,_,linprog=scipy_tools()
    _,vertices,_=template(pid)
    eq=np.array([[float(v[i]) for v in vertices] for i in range(len(point))]+[[1.0]*len(vertices)])
    lp=linprog(np.zeros(len(vertices)),A_eq=eq,b_eq=np.array(list(map(float,point))+[1.0]),bounds=(0,None),method='highs')
    if lp.success:
        ids=[i for i,w in enumerate(lp.x) if w>1e-12]
        if len(ids)==len(point)+1:
            inv=inverse([[vertices[j][i] for j in ids] for i in range(len(point))]+[[Q(1)]*len(ids)])
            weights=[dot(row,rhs) for row in inv]
            if all(w>=0 for w in weights):
                return pad_membership(zip(ids,weights),len(point))
    raise ValueError('No exact convex decomposition proposed')


def membership(pid,point):
    _,vertices,lookup=template(pid)
    if pid in ('c8','hc5','hc6'):
        pairs=hypercube_membership(point,lookup)
    elif pid in ('c16','op5','op6'):
        pairs=cross_membership(point,lookup)
    else:
        pairs=simplex_membership(pid,point)
    if any(w<0 for _,w in pairs) or sum((w for _,w in pairs),Q(0)) != 1:
        raise ValueError('Invalid exact convex weights')
    if any(sum((w*vertices[j][a] for j,w in pairs),Q(0))!=point[a] for a in range(len(point))):
        raise ValueError('Invalid exact convex coordinates')
    return pairs


def simple_endpoints(lo,hi):
    for bits in (64,96,160):
        den=1<<bits
        lower=Q(-(-lo.numerator*den//lo.denominator),den)
        upper=Q(hi.numerator*den//hi.denominator,den)
        if lower<upper:
            return lower,upper
    return lo,hi


def check_direction(a,b,u):
    if not any(u):
        return None
    lo=max(dot(u,p) for p in a)
    hi=min(dot(u,p) for p in b)
    if lo>=hi:
        return None
    lower,upper=simple_endpoints(lo,hi)
    return dict(normal=u,lower=lower,upper=upper)


def separating_plane(a,b,ca,cb,stored=None):
    if stored is not None:
        result=check_direction(a,b,stored)
        if result is not None:
            return result
    # Missing distant pairs are already known to be ball-separated in the
    # production checker, so the centre direction normally suffices.
    direction=tuple(y-x for x,y in zip(ca,cb))
    result=check_direction(a,b,direction)
    if result is not None:
        return result
    d=len(ca)
    for k in range(d):
        for sign in (-1,1):
            u=tuple(Q(sign if i==k else 0) for i in range(d))
            result=check_direction(a,b,u)
            if result is not None:
                return result
    np,_,linprog=scipy_tools()
    constraints=[[float(x) for x in p]+[-1.0,1.0] for p in a]
    constraints += [[-float(x) for x in p]+[1.0,1.0] for p in b]
    objective=[0.0]*(d+1)+[-1.0]
    lp=linprog(objective,A_ub=np.array(constraints),b_ub=np.zeros(len(constraints)),bounds=[(-1.0,1.0)]*d+[(None,None),(0,None)],method='highs')
    if lp.success:
        for bound in (10**12,10**16):
            u=tuple(Q(float(x)).limit_denominator(bound) for x in lp.x[:d])
            result=check_direction(a,b,u)
            if result is not None:
                return result
    raise ValueError('No strictly separating rational plane proposed')


def export(path):
    raw=path.read_bytes()
    rec=json.loads(raw)
    if rec.get('dim') not in (4,5,6):
        raise ValueError('Not a 4D-6D packing')
    d,n=rec['dim'],rec['n']
    if not isinstance(n,int) or n<2 or len(rec['pieces'])!=n:
        raise ValueError('Invalid piece count')
    pg,pv,_=template(rec['piece'])
    cg,cv,_=template(rec['container'])
    if pg['dim']!=d or cg['dim']!=d or any(len(v)!=d for v in pv+cv):
        raise ValueError('Canonical template dimension mismatch')
    mu=number(rec['mu'])
    if mu<=0 or mu*mu*number(cg['edge2'])!=number(pg['edge2']):
        raise ValueError('Incorrect exact canonical edge ratio')
    scale=number(rec['s_full'])*mu
    cc=list(map(number,rec.get('container_center',[0]*d)))
    if scale<=0 or len(cc)!=d:
        raise ValueError('Invalid container')
    centres=[];skews=[];signs=[];inverses=[];rotations=[];placed=[];indices=[];weights=[]
    for p in rec['pieces']:
        c,s,ds,ainv,r=cayley(p,d)
        world=[tuple(c[k]+dot(r[k],v) for k in range(d)) for v in pv]
        decompositions=[membership(rec['container'],tuple((v[k]-cc[k])/scale for k in range(d))) for v in world]
        centres.append(c);skews.append(s);signs.append(ds);inverses.append(ainv);rotations.append(r);placed.append(world)
        indices.append([[j for j,w in pairs] for pairs in decompositions])
        weights.append([[w for j,w in pairs] for pairs in decompositions])
    original_planes={}
    for row in rec.get('planes',[]):
        i,j=int(row[0]),int(row[1])
        u=tuple(map(number,row[2:2+d]))
        original_planes[min(i,j),max(i,j)]=u if i<j else tuple(-x for x in u)
    planes=[]
    for i,j in itertools.combinations(range(n),2):
        pl=separating_plane(placed[i],placed[j],centres[i],centres[j],original_planes.get((i,j)))
        planes.append(dict(i=i,j=j,**pl))
    return encode(dict(record_id=path.stem,n=n,dimension=d,piece=rec['piece'],container=rec['container'],
        source_path=str(path.relative_to(INPUTS)).replace('\\','/'),source_sha256=hashlib.sha256(raw).hexdigest(),
        geometry_path='src/polytopes_nd.json',geometry_sha256=hashlib.sha256((INPUTS/'src/polytopes_nd.json').read_bytes()).hexdigest(),
        numeric_semantics='JSON numbers via binary64 then exact Fraction; rational strings via Fraction',
        scale=scale,s_full=number(rec['s_full']),edge_ratio=mu,container_center=cc,
        template_vertices=pv,container_vertices=cv,centres=centres,raw_skews=skews,diagonal_signs=signs,
        cayley_inverses=inverses,rotations=rotations,indices=indices,weights=weights,
        barycentric_width=d+2,planes=planes,unordered_pairs=n*(n-1)//2,
        vertex_membership_tests=n*len(pv),original_plane_count=len(original_planes)))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    out=HERE/'witnesses_nd';out.mkdir(parents=True,exist_ok=True)
    report_path=HERE/'export-nd-report.json'
    report={'exporter_is_trusted_for_provenance_only':True,'formal_verification':'Pending Lean compilation; Python success is not a Lean proof','exported':[],'excluded':[]}
    inventory=json.loads((HERE/'inventory/rational-nd-inventory.json').read_text(encoding='utf8'))
    for row in inventory['records']:
        path=INPUTS/row['file']
        if row['n']>args.max_n or (args.only and path.stem not in args.only and row['problem'] not in args.only):
            continue
        t=time.monotonic()
        try:
            dest=out/(path.stem+'.json')
            if dest.is_file() and not args.overwrite:
                cert=json.loads(dest.read_text(encoding='utf8'))
                if cert['source_sha256']!=hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError('Existing witness source hash mismatch')
                if cert['source_path']!=str(path.relative_to(INPUTS)).replace('\\','/') or cert['record_id']!=path.stem:
                    raise ValueError('Existing witness source identity mismatch')
                if cert['geometry_sha256']!=hashlib.sha256((INPUTS/'src/polytopes_nd.json').read_bytes()).hexdigest():
                    raise ValueError('Existing witness geometry hash mismatch')
                source_binding_check(cert,json.loads(path.read_bytes()))
            else:
                cert=export(path)
                dest.write_text(json.dumps(cert,indent=2)+'\n',encoding='utf8')
            item={k:cert[k] for k in ('record_id','n','dimension','piece','container','source_path','source_sha256','vertex_membership_tests','unordered_pairs')}
            item.update(witness_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),export_seconds=round(time.monotonic()-t,3))
            report['exported'].append(item)
            print(json.dumps({'exported':path.stem,'seconds':item['export_seconds']}),flush=True)
        except (ValueError,KeyError,ZeroDivisionError) as err:
            report['excluded'].append({'source_path':str(path),'reason':str(err)})
            print(json.dumps({'excluded':path.stem,'reason':str(err)}),flush=True)
        report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    report['totals']={
        'records':len(report['exported']),
        'excluded':len(report['excluded']),
        'unordered_pairs':sum(r['unordered_pairs'] for r in report['exported']),
        'vertex_membership_tests':sum(r['vertex_membership_tests'] for r in report['exported']),
        'witness_bytes':sum((out/(r['record_id']+'.json')).stat().st_size for r in report['exported']),
    }
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
