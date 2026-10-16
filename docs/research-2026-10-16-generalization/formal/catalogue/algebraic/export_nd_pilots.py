"""Prepare actual selected witnesses for the 45 remaining ND families.

Exact quadratic-coefficient inverse certificates avoid factorial determinants.
The original s_full, Cayley parameters, centres and mu are never perturbed.
Preparation is not formal verification; Lean must check every certificate.
"""
from fractions import Fraction as Q
import argparse,hashlib,itertools,json,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from export_nd import cayley
from export_cubes import number,encode
from geometry_intervals import add,mul,inverse,outward,evaluate
from nd_geometry import inverse_matrix,BITS
from export_3d import point,sumI,dotI,midpoint,unencode,np,Delaunay,linprog

G=json.loads((HERE/'geometry-intervals-nd.json').read_text(encoding='utf8'))
T=G['templates'];ROOTS=G['roots']

class Container:
    def __init__(self,t):
        self.t=t;self.d=t['dimension'];self.k=self.d+1
        self.raw=unencode(t['coefficients']);self.r=Q(t['radicand'])
        self.rootI=unencode(ROOTS[str(t['radicand'])]['interval'])
        self.vi=unencode(t['vertex_intervals']);self.normI=unencode(t['normalizer_interval']);self.inverseNorm=inverse(self.normI)
        self.v=np.array([[midpoint(c)for c in v]for v in self.vi]);self.A=np.vstack((np.ones(len(self.vi)),self.v.T))
        self.tri=Delaunay(self.v);self.bases={}

    def basis(self,ids):
        ids=tuple(map(int,ids))
        if len(set(ids))!=self.k:return None
        if ids in self.bases:return self.bases[ids]
        A=[[(Q(1),Q(0))for _ in ids]]+[[tuple(self.raw[j][a])for j in ids]for a in range(self.d)]
        try:B=inverse_matrix(A,self.r)
        except ValueError:return None
        BI=[[outward(evaluate(q,self.rootI)if j==0 else mul(evaluate(q,self.rootI),self.inverseNorm),BITS)
             for j,q in enumerate(row)]for row in B]
        result=dict(id=len(self.bases),indices=ids,inverse_coefficients=B,inverse_intervals=BI)
        self.bases[ids]=result;return result

    def containment(self,x):
        xf=np.array([midpoint(a)for a in x]);si=int(self.tri.find_simplex(xf,tol=1e-8));candidates=[]
        if si>=0:
            candidates.append(tuple(self.tri.simplices[si]));candidates.extend(tuple(self.tri.simplices[j])for j in self.tri.neighbors[si]if j>=0)
        epsilons=[Q(0),Q(1,10**16),Q(1,10**15),Q(1,10**14),Q(1,10**13),Q(1,10**12)]
        seen=set()
        def attempt(ids,eps):
            ids=tuple(ids)
            if (ids,eps)in seen:return None
            seen.add((ids,eps));b=self.basis(ids)
            if b is None:return None
            rhs=[point(1-len(self.vi)*eps),*x]
            weights=[outward(add(point(eps),dotI(row,rhs)),BITS)for row in b['inverse_intervals']]
            if all(w[0]>=0 for w in weights):return dict(basis=b['id'],epsilon=eps,weight_intervals=weights)
            return None
        for eps in epsilons:
            for ids in candidates:
                hit=attempt(ids,eps)
                if hit:return hit
        for eps in epsilons:
            sol=linprog(np.zeros(len(self.vi)),A_eq=self.A,b_eq=np.r_[1-len(self.vi)*float(eps),xf],bounds=[(0,None)]*len(self.vi),method='highs')
            if not sol.success:continue
            active=[i for i,w in enumerate(sol.x)if w>1e-10]
            if len(active)>self.k:continue
            extras=[i for i in range(len(self.vi))if i not in active]
            for extra in itertools.islice(itertools.combinations(extras,self.k-len(active)),100):
                hit=attempt(active+list(extra),eps)
                if hit:return hit
        for ids in self.tri.simplices:
            for eps in epsilons:
                hit=attempt(ids,eps)
                if hit:return hit
        raise ValueError('No positive exact interval inverse-basis weights for '+str(xf))

def plane(a,b,ca,cb,stored):
    d=len(ca)
    def test(u):
        u=list(map(Q,u))
        lo=max(dotI(list(map(point,u)),p)[1]for p in a);hi=min(dotI(list(map(point,u)),p)[0]for p in b)
        return dict(normal=u,lower=lo,upper=hi)if lo<hi else None
    if stored is not None:
        hit=test(stored)
        if hit:return hit
    for u in [[y-x for x,y in zip(ca,cb)],*([Q(int(i==j))for i in range(d)]for j in range(d))]:
        for sign in [1,-1]:
            hit=test([sign*x for x in u])
            if hit:return hit
    af=np.array([[midpoint(x)for x in v]for v in a]);bf=np.array([[midpoint(x)for x in v]for v in b])
    A=np.vstack((np.c_[af,-np.ones(len(af)),np.zeros(len(af))],np.c_[-bf,np.zeros(len(bf)),np.ones(len(bf))]))
    sol=linprog([0]*d+[1,-1],A_ub=A,b_ub=np.zeros(len(A)),bounds=[(-1,1)]*d+[(None,None)]*2,
        method='highs-ds',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
    if sol.success:
        hit=test([Q(float(x))for x in sol.x[:d]])
        if hit:return hit
    raise ValueError('No strict rational plane for actual ND pair')

def export(row):
    path=HERE/'inputs'/row['file'];raw=path.read_bytes();rec=json.loads(raw)
    d,n=rec['dim'],rec['n'];pt=T['piece_'+rec['piece']];ct=T['container_'+row['problem']]
    V=unencode(pt['vertex_intervals']);C=Container(ct);scale=number(rec['s_full']);cc=list(map(number,rec.get('container_center',[0]*d)))
    if scale<=0:raise ValueError('nonpositive native s_full')
    centres=[];skews=[];signs=[];inverses=[];rotations=[];placed=[];normalized=[];containment=[]
    for pose in rec['pieces']:
        c,s,ds,ai,R=cayley(pose,d)
        world=[[outward(add(point(c[a]),dotI(list(map(point,R[a])),p)),BITS)for a in range(d)]for p in V]
        normalizedPiece=[[outward(mul(point(1/scale),add(z,point(-cc[a]))),BITS)for a,z in enumerate(p)]for p in world]
        inclusion=[C.containment(p)for p in normalizedPiece]
        centres.append(c);skews.append(s);signs.append(ds);inverses.append(ai);rotations.append(R);placed.append(world);normalized.append(normalizedPiece);containment.append(inclusion)
    stored={}
    for p in rec.get('planes',[]):
        i,j=int(p[0]),int(p[1]);u=list(map(number,p[2:2+d]));stored[min(i,j),max(i,j)]=u if i<j else[-x for x in u]
    planes=[dict(i=i,j=j,**plane(placed[i],placed[j],centres[i],centres[j],stored.get((i,j))))for i,j in itertools.combinations(range(n),2)]
    used={z['basis']for p in containment for z in p}
    return encode(dict(schema='nd-quadratic-inverse-packing-v1',status='PREPARATION_NOT_FORMAL_VERIFICATION',record_id=path.stem,problem=row['problem'],
        source_path=row['file'],source_sha256=hashlib.sha256(raw).hexdigest(),source_freeze='1abc63218db34cea95802aeb3b6d4a6b6fe1c61b',
        proposal_exporter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),geometry_path=G['geometry_path'],geometry_sha256=G['geometry_sha256'],
        piece=rec['piece'],container=rec['container'],dimension=d,n=n,s_full=scale,scale=scale,native_mu=rec['mu'],mu_spec=G['scales'][row['problem']],
        source_credit={k:rec[k]for k in ['found_by','credit','certificate_refined_by','source','contribution']if k in rec},
        container_center=cc,centres=centres,raw_skews=skews,diagonal_signs=signs,cayley_inverses=inverses,rotations=rotations,
        placed_vertex_intervals=placed,normalized_vertex_intervals=normalized,containment=containment,planes=planes,
        container_bases=[z for z in C.bases.values()if z['id']in used],vertex_count=sum(map(len,placed)),pair_count=len(planes),interval_rounding_bits=BITS))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='*');args=ap.parse_args();rows=G['pilot_records']
    if args.only:rows=[r for r in rows if r['problem']in args.only or Path(r['file']).stem in args.only]
    out=HERE/'witnesses_nd_pilots';out.mkdir(exist_ok=True);report=dict(status='PREPARATION_NOT_FORMAL_VERIFICATION',exported=[],failures=[])
    for row in rows:
        start=time.monotonic()
        try:
            cert=export(row);dest=out/(cert['record_id']+'.json');dest.write_bytes((json.dumps(cert,indent=2)+'\n').replace('\n','\r\n').encode('utf8'))
            item={k:cert[k]for k in ['record_id','problem','source_path','source_sha256','piece','container','dimension','n','vertex_count','pair_count']};item.update(seconds=round(time.monotonic()-start,3),witness_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bases=len(cert['container_bases']));report['exported'].append(item);print(json.dumps(item),flush=True)
        except (ValueError,KeyError)as e:
            failure=dict(source_path=row['file'],problem=row['problem'],reason=str(e));report['failures'].append(failure);print(json.dumps(failure),flush=True)
        (HERE/'export-nd-pilots-report.json').write_bytes((json.dumps(report,indent=2)+'\n').replace('\n','\r\n').encode('utf8'))
    return 0 if not report['failures']else 1

if __name__=='__main__':raise SystemExit(main())
