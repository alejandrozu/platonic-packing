# d = 4: local minima of Value(C) over frames of v^perp. Classify by zero pattern; compare with Helmert value.
import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm, null_space
from hstep import value
d=int(sys.argv[1]); rng=np.random.default_rng(int(sys.argv[2])); nv=int(sys.argv[3]); nst=int(sys.argv[4])
n=d-1; iu=np.triu_indices(n,1)
def helm(v):
    vs=np.sort(v)[::-1]; A=np.cumsum(vs**2); return 2*sum(vs[k]*np.sqrt(A[k-1]/A[k]) for k in range(1,d))
def polish(v,B,Q):
    # alternate: local descent with shrinking Nelder-Mead in so(n) coordinates
    def f(x,Q0):
        A=np.zeros((n,n)); A[iu]=x; return value(v,B@Q0@expm(A-A.T))
    for it in range(6):
        r=minimize(f,np.zeros(len(iu[0])),args=(Q,),method='Nelder-Mead',options={'xatol':1e-13,'fatol':1e-15,'maxiter':4000,'initial_simplex':np.vstack([np.zeros(len(iu[0])),np.eye(len(iu[0]))*0.3**(it+1)])})
        A=np.zeros((n,n)); A[iu]=r.x; Q=Q@expm(A-A.T)
    return Q
pat_count={}
for t in range(nv):
    v=np.abs(rng.normal(size=d)); v/=np.linalg.norm(v); v=np.sort(v)[::-1]; B=null_space(v[None,:]); H=helm(v)
    found={}
    for s in range(nst):
        Q=np.linalg.qr(rng.normal(size=(n,n)))[0]; Q=polish(v,B,Q); C=B@Q; val=value(v,C)
        Z=(np.abs(C)<1e-6)
        key=(round(val,6))
        rowzeros=tuple(sorted(Z.sum(1))); aligned=Z.sum(1).max()==n-1
        found[key]=(val,int(Z.sum()),aligned,rowzeros)
    vals=sorted(found.values())
    gmin=vals[0]
    print('v',np.round(v,3),'Helmert %.6f'%H,' global %.6f aligned=%s zeros=%d'%(gmin[0],gmin[2],gmin[1]),' #locmin',len(vals),' nonaligned locmins:',[(round(x[0]-H,4),x[1]) for x in vals if not x[2]][:4],flush=True)
