# F+_j(R) = sum_i |R_ij| * max(2 - |R_i|_1, 0): the version the near-axis step needs when rows can exceed l1 = 2
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(100+d)
iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T
    return R0@expm(A)
def Fp(R):
    w=np.abs(R).sum(1); return (np.abs(R[:,0])*np.maximum(2-w,0)).sum()
best=-1; bestR=None
for t in range(trials):
    if t%3==0: R0=np.linalg.qr(rng.normal(size=(d,d)))[0]; sc=0.3
    elif t%3==1:  # block: a random k-dim orthogonal block containing column 0, identity elsewhere (rows of the block may exceed 2)
        k=rng.integers(3,d+1); R0=np.eye(d); B=np.linalg.qr(rng.normal(size=(k,k)))[0]; R0[:k,:k]=B; sc=0.05
    else: R0=np.eye(d)[rng.permutation(d)]; sc=0.5
    res=minimize(lambda v:-Fp(R_of(v,R0)),rng.normal(size=len(iu[0]))*sc,method='L-BFGS-B',options={'maxiter':4000})
    if -res.fun>best: best=-res.fun; bestR=R_of(res.x,R0)
np.set_printoptions(precision=3,suppress=True,linewidth=160)
w=np.abs(bestR).sum(1)
print(d,'max F+',round(best,6),'rows l1',w,'col0',bestR[:,0])
np.save(f"plusR{d}.npy",bestR)
