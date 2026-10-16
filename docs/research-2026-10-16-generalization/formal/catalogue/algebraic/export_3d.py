"""Source-bound algebraic 3D packing certificate proposals.

All geometry/placements retain their source meaning. Python/SciPy chooses a
simplex and strict separating planes; exact rational interval computations
independently reject bad proposals. Only Lean compilation is formal verification.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from export_cubes import rotation,number,dot,determinant,encode
from geometry_intervals import add,neg,mul,outward
try:
    import numpy as np
    from scipy.spatial import Delaunay
    from scipy.optimize import linprog
except ImportError:
    sys.path.insert(0,str(HERE.parents[4]/'work/website-runtime/Lib/site-packages'))
    import numpy as np
    from scipy.spatial import Delaunay
    from scipy.optimize import linprog

BITS=170
GEOMETRY=json.loads((HERE/'geometry-intervals.json').read_text())
TEMPLATES=GEOMETRY['templates']
PERMS={n:[(p,(-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n)))
          for p in itertools.permutations(range(n))]for n in (3,4)}

def point(x):return Q(x),Q(x)
def sumI(xs):
    out=point(0)
    for x in xs:out=add(out,x)
    return out
def dotI(a,b):return sumI(mul(x,y)for x,y in zip(a,b))
def detI(a):
    out=point(0)
    for p,sign in PERMS[len(a)]:
        z=point(sign)
        for i,j in enumerate(p):z=mul(z,a[i][j])
        out=add(out,z)
    return out
def midpoint(a):return float((a[0]+a[1])/2)
def unencode(x):
    if isinstance(x,str):return Q(x)
    if isinstance(x,list):return [unencode(v)for v in x]
    return x

class Container:
    def __init__(self,name):
        self.name=name
        self.vi=unencode(TEMPLATES[name]['vertex_intervals'])
        self.v=np.array([[midpoint(c)for c in v]for v in self.vi])
        self.A=np.vstack((np.ones(len(self.vi)),self.v.T))
        self.tri=Delaunay(self.v)
        self.bases={}

    def basis(self,ids):
        ids=tuple(int(i)for i in ids)
        if ids in self.bases:return self.bases[ids]
        A=[[point(1)for _ in ids]]+[[self.vi[i][a]for i in ids]for a in range(3)]
        den=outward(detI(A),BITS)
        if den[0]<=0<=den[1]:return None
        cof=[]
        for j in range(4):
            col=[]
            for row in range(4):
                minor=[[A[a][b]for b in range(4)if b!=j]for a in range(4)if a!=row]
                z=detI(minor)
                col.append(outward(z if (row+j)%2==0 else neg(z),BITS))
            cof.append(col)
        b=dict(id=len(self.bases),indices=ids,determinant_interval=den,cofactor_columns=cof)
        self.bases[ids]=b
        return b

    def containment(self,x):
        xf=np.array([midpoint(a)for a in x])
        si=int(self.tri.find_simplex(xf,tol=1e-8));candidates=[]
        if si>=0:
            candidates.append(tuple(self.tri.simplices[si]))
            candidates.extend(tuple(self.tri.simplices[j])for j in self.tri.neighbors[si]if j>=0)
        # All nonnegative LP solutions have a sparse vertex basis. This is an
        # untrusted fallback when the triangulation's float boundary test fails.
        def lp_ids(eps):
            sol=linprog(np.zeros(len(self.vi)),A_eq=self.A,b_eq=np.r_[1-len(self.vi)*float(eps),xf],
                bounds=[(0,None)]*len(self.vi),method='highs')
            if not sol.success:return []
            active=[i for i,w in enumerate(sol.x)if w>1e-10]
            if len(active)>4:return []
            if len(active)==4:return [tuple(active)]
            return [tuple(active+list(extra))for extra in itertools.islice(
                itertools.combinations([i for i in range(len(self.vi))if i not in active],4-len(active)),50)]
        epsilons=[Q(0),Q(1,10**15),Q(1,10**14),Q(1,10**13),Q(1,10**12)]
        seen=set()
        def attempt(ids,eps):
            rhs=[point(1-len(self.vi)*eps),*x]
            ids=tuple(ids)
            if (ids,eps)in seen:return None
            seen.add((ids,eps));basis=self.basis(ids)
            if basis is None:return None
            den=basis['determinant_interval']
            nums=[outward(add(dotI(cof,rhs),mul(point(eps),den)),BITS)
                  for cof in basis['cofactor_columns']]
            if all((den[0]>0 and z[0]>=0)or(den[1]<0 and z[1]<=0)for z in nums):
                return dict(basis=basis['id'],epsilon=eps,corrected_numerator_intervals=nums)
            return None
        for eps in epsilons:
            for ids in candidates:
                answer=attempt(ids,eps)
                if answer:return answer
        for eps in epsilons:
            for ids in lp_ids(eps):
                answer=attempt(ids,eps)
                if answer:return answer
        # Near an internal simplex boundary, an adjacent tetrahedron need not
        # be an immediate triangulation neighbor. Exhaustive fallback is finite.
        for ids in self.tri.simplices:
            basis=self.basis(ids)
            if basis is None:continue
            den=basis['determinant_interval']
            for eps in epsilons:
                rhs=[point(1-len(self.vi)*eps),*x]
                nums=[outward(add(dotI(cof,rhs),mul(point(eps),den)),BITS)
                      for cof in basis['cofactor_columns']]
                if all((den[0]>0 and z[0]>=0)or(den[1]<0 and z[1]<=0)for z in nums):
                    return dict(basis=basis['id'],epsilon=eps,corrected_numerator_intervals=nums)
        raise ValueError('No interval-certified simplicial containment for vertex '+str(xf))

CONTAINERS={}
def plane(a,b,ca,cb,faces):
    def test(u):
        u=[Q(x)for x in u]
        ap=[dotI(list(map(point,u)),p)for p in a]
        bp=[dotI(list(map(point,u)),p)for p in b]
        lo=max(x[1]for x in ap);hi=min(x[0]for x in bp)
        return dict(normal=u,lower=lo,upper=hi)if lo<hi else None
    delta=[y-x for x,y in zip(ca,cb)]
    for u in [delta,*([Q(int(i==j))for i in range(3)]for j in range(3))]:
        for sg in [1,-1]:
            ans=test([sg*x for x in u])
            if ans:return ans
    af=np.array([[midpoint(x)for x in v]for v in a]);bf=np.array([[midpoint(x)for x in v]for v in b])
    # Facet/edge SAT directions are merely proposals. They also resolve gaps
    # smaller than floating LP solvers' minimum feasibility tolerance.
    def edges(v):
        seen=set();out=[]
        for face in faces:
            for i,j in zip(face,face[1:]+face[:1]):
                e=v[j]-v[i];norm=np.linalg.norm(e)
                if norm<1e-15:continue
                e=e/norm
                if next((x for x in e if abs(x)>1e-10),1)<0:e=-e
                key=tuple(np.round(e,10))
                if key not in seen:seen.add(key);out.append(e)
        return out
    for v in [af,bf]:
        for face in faces:
            u=np.cross(v[face[1]]-v[face[0]],v[face[2]]-v[face[0]])
            norm=np.linalg.norm(u)
            if norm<1e-15:continue
            u=u/norm
            for sg in [1,-1]:
                ans=test([Q(float(sg*x))for x in u])
                if ans:return ans
    # Maximize h-l with u in [-1,1]^3, u*a<=l, u*b>=h.
    A=np.vstack((np.c_[af,-np.ones(len(af)),np.zeros(len(af))],
                 np.c_[-bf,np.zeros(len(bf)),np.ones(len(bf))]))
    sol=linprog([0,0,0,1,-1],A_ub=A,b_ub=np.zeros(len(A)),bounds=[(-1,1)]*3+[(None,None)]*2,
        method='highs-ds',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
    if sol.success:
        u=[Q(float(x)).limit_denominator(10**14)for x in sol.x[:3]]
        ans=test(u)
        if ans:return ans
    for ea in edges(af):
        for eb in edges(bf):
            u=np.cross(ea,eb);norm=np.linalg.norm(u)
            if norm<1e-12:continue
            u=u/norm
            for sg in [1,-1]:
                ans=test([Q(float(sg*x))for x in u])
                if ans:return ans
    raise ValueError('No interval-certified strict pair plane')

def export(row):
    path=HERE/'inputs'/row['file'];raw=path.read_bytes();rec=json.loads(raw)
    if len(rec['pieces'])!=rec['n']:raise ValueError('piece count mismatch')
    scale=number(rec['s_full']);cc=list(map(number,rec.get('container_center',[0,0,0])))
    if scale<=0:raise ValueError('nonpositive scale')
    piece=rec['piece'];container=rec['container']
    template=unencode(TEMPLATES[piece]['vertex_intervals'])
    if container not in CONTAINERS:CONTAINERS[container]=Container(container)
    C=CONTAINERS[container]
    centres=[];quaternions=[];rotations=[];vertices=[];normalized=[];containment=[]
    for pose in rec['pieces']:
        c=list(map(number,pose[:3]));q=list(map(number,pose[3:]));R=rotation(q)
        if any(dot(R[i],R[j])!=int(i==j)for i in range(3)for j in range(3))or determinant(R)!=1:
            raise ValueError('source quaternion rotation not proper orthogonal')
        v=[[outward(add(point(c[a]),dotI(list(map(point,R[a])),p)),BITS)for a in range(3)]for p in template]
        x=[[outward(mul(point(1/scale),add(z,point(-cc[a]))),BITS)for a,z in enumerate(p)]for p in v]
        inclusion=[C.containment(p)for p in x]
        centres.append(c);quaternions.append(q);rotations.append(R);vertices.append(v);normalized.append(x);containment.append(inclusion)
    planes=[dict(i=i,j=j,**plane(vertices[i],vertices[j],centres[i],centres[j],TEMPLATES[piece]['faces']))for i,j in itertools.combinations(range(rec['n']),2)]
    used={c['basis']for p in containment for c in p}
    return encode(dict(schema='algebraic-packing-intervals-v1',status='EXPORTED_NOT_LEAN_VERIFIED',
        record_id=path.stem,source_path=row['file'],source_sha256=hashlib.sha256(raw).hexdigest(),
        proposal_exporter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_freeze='1abc63218db34cea95802aeb3b6d4a6b6fe1c61b',source_credit={k:rec[k]for k in ['found_by','credit','certificate_refined_by','source','contribution']if k in rec},
        geometry_path=GEOMETRY['geometry_path'],geometry_sha256=GEOMETRY['geometry_sha256'],piece=piece,container=container,
        dimension=3,n=rec['n'],scale=scale,container_center=cc,numeric_semantics='JSON unquoted values -> binary64 -> exact Fraction, rational strings -> exact Fraction',
        quaternions=quaternions,centres=centres,rotations=rotations,placed_vertex_intervals=vertices,normalized_vertex_intervals=normalized,
        containment=containment,container_bases=sorted([b for b in C.bases.values()if b['id']in used],key=lambda x:x['id']),
        planes=planes,pair_count=len(planes),vertex_count=sum(map(len,vertices)),interval_rounding_bits=BITS))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--all',action='store_true');ap.add_argument('--only',nargs='*');ap.add_argument('--max-n',type=int,default=100);ap.add_argument('--resume',action='store_true')
    args=ap.parse_args();rows=json.loads((HERE/'remaining-targets.json').read_text())['records'];rows=[r for r in rows if r['dimension']==3 and r['n']<=args.max_n]
    if args.only:rows=[r for r in rows if Path(r['file']).stem in args.only or r['problem']in args.only]
    if not args.all:
        first={}
        for r in rows:
            if r['problem']not in first or r['n']<first[r['problem']]['n']:first[r['problem']]=r
        rows=list(first.values())
    out=HERE/'witnesses3d';out.mkdir(exist_ok=True)
    report=dict(status='PREPARATION_NOT_FORMAL_VERIFICATION',exported=[],failures=[])
    exporter_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    reportpath=HERE/('export3d-all-report.json'if args.all else 'export3d-report.json')
    for r in rows:
        start=time.monotonic()
        try:
            dest=out/(Path(r['file']).stem+'.json');cert=None
            if args.resume and dest.exists():
                old=json.loads(dest.read_text())
                if old.get('source_sha256')==hashlib.sha256((HERE/'inputs'/r['file']).read_bytes()).hexdigest() and old.get('proposal_exporter_sha256')==exporter_hash and old.get('geometry_sha256')==GEOMETRY['geometry_sha256']:
                    cert=old
            if cert is None:
                cert=export(r);dest.write_text(json.dumps(cert,indent=2)+'\n',encoding='utf8')
            item={k:cert[k]for k in ['record_id','source_path','source_sha256','piece','container','n','pair_count','vertex_count']}
            item.update(witness_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),seconds=round(time.monotonic()-start,3));report['exported'].append(item)
            print(json.dumps(dict(exported=item['record_id'],seconds=item['seconds'])),flush=True)
        except (ValueError,KeyError,IndexError)as e:
            report['failures'].append(dict(source_path=r['file'],reason=str(e)));print(json.dumps(report['failures'][-1]),flush=True)
        reportpath.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return 0 if not report['failures']else 1

if __name__=='__main__':raise SystemExit(main())
