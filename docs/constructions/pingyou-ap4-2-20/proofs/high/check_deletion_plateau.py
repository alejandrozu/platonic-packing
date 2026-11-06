"""Exact coverage of all N15/N16 deletions from the retained N17 witness.

Standard library only; no new rotations or numerical optimization.
"""
import sys,json,itertools,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
from check_field import K,P,U,B,h,mv,mm,transpose,dot,cross,sub,maxk

SOURCE=HERE/'n17/n17_exact.json'
d=json.loads(SOURCE.read_text());N=d['n'];assert N==17
S=K(d['scale_coefficients']);assert (S-3).sign()==0
C=[[K(v)for v in row]for row in d['physical_centers']]
M=[[[K(v)for v in row]for row in m]for m in d['frames']]
V=[]
for m in M:
    assert all((v-int(i==j)).sign()==0 for i,row in enumerate(mm(m,transpose(m)))for j,v in enumerate(row))
    assert (dot(m[0],cross(m[1],m[2]))-1).sign()==0
    V.append([mv(m,p)for p in P])
for i,vs in enumerate(V):
    for p in vs:
        globalp=[a+b for a,b in zip(C[i],p)]
        assert all((S*b-dot(u,globalp)).sign()>=0 for u,b in zip(U,B))
pairmap={}
for ridx,row in enumerate(d['separators']):
    i,j=row['pair'];u=list(map(K,row['normal']));assert i<j
    rhs=-maxk([dot(u,p)for p in V[i]])-maxk([-dot(u,p)for p in V[j]])
    assert (rhs-dot(u,sub(C[i],C[j]))).sign()>=0
    pairmap[(i,j)]=(ridx,u,rhs)
assert set(pairmap)==set(itertools.combinations(range(17),2))

CHAINS=[(10,0,5),(13,1,9),(12,2,7),(11,3,6),(14,16,8)]
assert len(set(itertools.chain.from_iterable(CHAINS)))==15
top=next(i for i,u in enumerate(U)if u[0].sign()==u[1].sign()==0 and u[2].sign()>0)
bottom=next(i for i,u in enumerate(U)if u[0].sign()==u[1].sign()==0 and u[2].sign()<0)
certificates=[]
for chain in CHAINS:
    for i in chain:
        assert (maxk([p[2]for p in V[i]])-h/2).sign()==0
        assert (maxk([-p[2]for p in V[i]])-h/2).sign()==0
    rows=[]
    for owner,facet in [(chain[0],bottom),(chain[2],top)]:
        u=U[facet];a=[K()for _ in range(3*N+1)];a[3*owner:3*owner+3]=u;a[-1]=-B[facet]
        rhs=-maxk([dot(u,p)for p in V[owner]])
        scale=u[2] if u[2].sign()>0 else -u[2]
        rows.append((a,rhs,K(1)/(h*scale),{'kind':'host','owner':owner,'facet':facet}))
    for lo,hi in zip(chain,chain[1:]):
        i,j=sorted((lo,hi));ridx,u,rhs=pairmap[(i,j)]
        assert u[0].sign()==u[1].sign()==0 and u[2].sign()!=0
        assert (u[2]*(C[j][2]-C[i][2])).sign()>0
        a=[K()for _ in range(3*N+1)];a[3*i:3*i+3]=u;a[3*j:3*j+3]=[-v for v in u]
        scale=u[2] if u[2].sign()>0 else -u[2]
        assert (rhs+h*scale).sign()==0
        rows.append((a,rhs,K(1)/(h*scale),{'kind':'pair','pair':[i,j],'source_separator_index':ridx}))
    total=[K()for _ in range(3*N+1)];rr=K()
    for a,rhs,w,_ in rows:
        assert w.sign()>0
        total=[v+w*x for v,x in zip(total,a)];rr+=w*rhs
    assert all(v.sign()==0 for v in total[:-1])
    assert (total[-1]+1).sign()==0 and (rr+3).sign()==0
    certificates.append({'chain_bottom_middle_top':list(chain),'dual_rows':[dict(tag,weight=w.out())for _,_,w,tag in rows],
                         'weighted_sum_scale_coefficient':total[-1].out(),'weighted_sum_rhs':rr.out()})

coverage=[]
for delete_count in [0,1,2]:
    for deleted in itertools.combinations(range(N),delete_count):
        remaining=[i for i,c in enumerate(CHAINS)if set(c).isdisjoint(deleted)]
        assert len(remaining)>=5-delete_count
        coverage.append({'remaining_count':N-delete_count,'deleted':list(deleted),'available_chain_certificates':remaining,
                         'selected_chain_certificate':remaining[0],'exact_fixed_frame_original_side_optimum':'3'})
out={'status':'PASS_EXACT_ALL_DELETIONS_SCALE_THREE','source':str(SOURCE.relative_to(HERE)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'source_geometry_checks':{'proper_rotations':17,'host_vertex_inequalities':1360,'complete_body_pairs':136},
     'deletion_counts':{'N17':1,'N16':17,'N15':136},'chains':certificates,'coverage':coverage,
     'argument':'Each surviving chain gives -S <= -3 by a positive exact combination of two host facets and two retained vertical pair rows. Feasibility at S=3 is inherited by deletion from the independently checked complete N17 witness.',
     'scope':'All translations with the retained exact body frames and original pair-separation sides; no new rotations and no unrestricted optimality assertion.'}
(HERE/'deletion_plateau_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in ['coverage','chains']},indent=2))
