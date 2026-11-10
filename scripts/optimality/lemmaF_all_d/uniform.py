# Uniform column: Lemma F there <=> T(d) = min over ONB of 1^perp of the total l1 norm >= 2d - 2 sqrt d.
import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm, null_space
d=int(sys.argv[1]); rng=np.random.default_rng(d)
B0=null_space(np.ones((1,d)))            # d x (d-1), orthonormal basis of 1^perp
n=d-1; iu=np.triu_indices(n,1)
def T(v):
    A=np.zeros((n,n)); A[iu]=v; A=A-A.T; return np.abs(B0@expm(A)).sum()
# Helmert basis value
H=sum(2*np.sqrt((k-1)/k) for k in range(2,d+1))
best=1e9
for t in range(60):
    res=minimize(T,rng.normal(size=len(iu[0]))*rng.uniform(0.1,2),method='L-BFGS-B',options={'maxiter':3000})
    best=min(best,res.fun)
print(d,'min T found',round(best,4),' Helmert',round(H,4),' needed 2d-2sqrt d',round(2*d-2*np.sqrt(d),4),' margin',round(best-(2*d-2*np.sqrt(d)),4))
