# Is the Helmert basis (v sorted decreasing) the minimiser of sum_k ||v o b_k||_1 over orthonormal bases b of v^perp?
# If yes for every unit v >= 0, Lemma F holds in every dimension (the Helmert value telescopes to >= 2(|v|_1 - 1)).
import numpy as np, sys, itertools
from scipy.optimize import minimize
from scipy.linalg import expm, null_space
d=int(sys.argv[1]); nv=int(sys.argv[2]); rng=np.random.default_rng(1000+d)
n=d-1; iu=np.triu_indices(n,1)
def helmert(v):
    v=np.sort(v)[::-1]; A=np.cumsum(v**2)      # A[k-1] = sum_{i<=k} v_i^2
    return 2*sum(v[k]*np.sqrt(A[k-1]/A[k]) for k in range(1,d))
worst=0; worst_v=None
for t in range(nv):
    v=np.abs(rng.normal(size=d))**rng.uniform(0.3,4); v[rng.random(d)<0.2]*=rng.uniform(0,0.3); v/=np.linalg.norm(v)
    B0=null_space(v[None,:])
    def G(p):
        A=np.zeros((n,n)); A[iu]=p; A=A-A.T; return np.abs((B0@expm(A))*v[:,None]).sum()
    best=1e9
    for s in range(25):
        res=minimize(G,rng.normal(size=len(iu[0]))*rng.uniform(0.05,2),method='L-BFGS-B',options={'maxiter':2000})
        best=min(best,res.fun)
    H=helmert(v); gap=best-H
    if gap<worst: worst=gap; worst_v=(v.copy(),best,H)
print(d,'most negative (found - Helmert):',worst)
if worst_v is not None:
    v,b,H=worst_v; np.set_printoptions(precision=4,suppress=True); print('  v',np.sort(v)[::-1],'found',b,'Helmert',H,'2(S-1)',2*(v.sum()-1))
