# Limit nu -> 0, kappa1 = lambda*nu: X -> (2c-1) - <col_q,G> + 2 lambda sum_{i!=p} z_i^+ y_i.
# Flat pivot row p = (0, 1/2,1/2,1/2,1/2, 0...), c = 1/2, w_p = 2, lambda = 1 (kappa1 = 2c-1+nu = nu).
# Test  T := 2*sum z+ y - <z,G>  >= 0  over random completions (rows <= 2), j = column 0 (y_p = 0), q = column 1.
import numpy as np, sys
from scipy.linalg import expm, null_space
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
p=np.zeros(d); p[1:5]=0.5
Bp=null_space(p[None,:])            # d x (d-1)
worst=np.inf; cnt=0; ex=None
for t in range(N):
    U=np.linalg.qr(rng.normal(size=(d-1,d-1)))[0]
    if rng.random()<0.5: U=expm((lambda S:S-S.T)(rng.normal(size=(d-1,d-1))*rng.uniform(0.05,1)))@np.eye(d-1)[rng.permutation(d-1)]
    O=(Bp@U).T                       # d-1 rows orthonormal, orthogonal to p
    R=np.vstack([p,O]); w=np.abs(R).sum(1)
    if w.max()>2+1e-12: continue
    R=R*np.sign(R[:,[0]]+1e-300); cnt+=1
    y=R[1:,0]; z=R[1:,1]; G=2-w[1:]
    T=2*(np.maximum(z,0)*y).sum()-(z*G).sum()
    if T<worst: worst=T; ex=R
np.set_printoptions(precision=3,suppress=True,linewidth=160)
print(d,'samples',cnt,'min T',worst)
if ex is not None: print(ex); print(' rows',np.abs(ex).sum(1))
