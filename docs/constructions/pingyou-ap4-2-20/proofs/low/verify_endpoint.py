"""Independent standard-library replay of exact primal/dual packing endpoints.

Does not import the endpoint search, SciPy, Flint, or its field implementation.
"""
from pathlib import Path
import sys, json, itertools, hashlib
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
from check_field import K,P,U,B,mv,mm,transpose,dot,cross,sub,maxk

def verify(path):
    path=Path(path);d=json.loads(path.read_text());n=d['n'];S=K(d['scale_coefficients'])
    C=[[K(x)for x in c]for c in d['physical_centers']]
    M=[[[K(x)for x in row]for row in m]for m in d['frames']]
    assert len(C)==len(M)==n
    V=[]
    for c,m in zip(C,M):
        assert all((x-int(i==j)).sign()==0 for i,row in enumerate(mm(m,transpose(m)))for j,x in enumerate(row))
        assert (dot(m[0],cross(m[1],m[2]))-1).sign()==0
        V.append([mv(m,p)for p in P])
    for i in range(n):
        for p in V[i]:
            x=[a+b for a,b in zip(C[i],p)]
            for u,b in zip(U,B):assert (S*b-dot(u,x)).sign()>=0,(i,'host')
    normals={}
    for s in d['separators']:
        i,j=s['pair'];u=[K(x)for x in s['normal']]
        assert i<j and (i,j)not in normals and dot(u,u).sign()>0
        gap=dot(u,sub(C[j],C[i]))-maxk([dot(u,p)for p in V[i]])-maxk([-dot(u,p)for p in V[j]])
        assert gap.sign()>=0,('pair',i,j)
        normals[(i,j)]=u
    assert set(normals)==set(itertools.combinations(range(n),2))
    # Reconstruct each active constraint rather than trusting a supplied matrix.
    nv=3*n+1;total=[K()for _ in range(nv)];rhs=K()
    assert len(d['active_basis'])==len(d['lp_dual_weights'])==nv
    for tag,raw in zip(d['active_basis'],d['lp_dual_weights']):
        w=K(raw);assert w.sign()>=0
        row=[K()for _ in range(nv)]
        if tag[0]=='host':
            _,i,f=tag;u=U[f];row[3*i:3*i+3]=u;row[-1]=-B[f]
            b=-maxk([dot(u,p)for p in V[i]])
        else:
            assert tag[0]=='pair';i,j=tag[1:3];u=normals[(i,j)]
            row[3*i:3*i+3]=u;row[3*j:3*j+3]=[-x for x in u]
            b=-maxk([dot(u,p)for p in V[i]])-maxk([-dot(u,p)for p in V[j]])
        x=[a for c in C for a in c]+[S]
        assert (dot(row,x)-b).sign()==0,('not tight',tag)
        total=[a+w*b for a,b in zip(total,row)];rhs+=w*b
    assert all((x+int(i==nv-1)).sign()==0 for i,x in enumerate(total))
    assert (-rhs-S).sign()==0
    assert (K(d['lp_lower_bound'])-S).sign()==0
    for precision in [40,50,60]:
        if f'exact_scale_lower_{precision}'in d:
            lo,hi=d[f'exact_scale_lower_{precision}'],d[f'exact_scale_upper_{precision}']
            assert (S-K(lo)).sign()>=0 and (K(hi)-S).sign()>=0
    r={'status':'PASS_INDEPENDENT_PRIMAL_DUAL_ENDPOINT','n':n,
       'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'proper_rotations':n,'host_vertex_inequalities':80*n,
       'complete_body_pairs':n*(n-1)//2,'equivalent_pair_vertex_inequalities':32*n*(n-1),
       'dual_vector_equalities':nv,'dual_objective_matches_primal':True,
       'no_padding':True,'scope':'optimal for the retained exact frames and selected separation sides'}
    print(json.dumps(r),flush=True)
    return r
if __name__=='__main__':
    for path in sys.argv[1:]:verify(path)
