# minimise X / (structure) restricted to spread pivots c <= cmax, and also report the decomposition
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); cmax=float(sys.argv[3]); rng=np.random.default_rng(43+d); iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; return R0@expm(A)
def parts(R):
    R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]; p=int(np.argmin(x)); q=1+int(np.argmax(np.abs(R[p,1:])))
    R[:,q]*=np.sign(R[p,q]); c=R[p,q]; mu=x[p]; a=1/(1+c)
    others=[i for i in range(d) if i!=p]; kk=[k for k in range(d) if k not in (0,q)]
    rho=np.abs(R[p,kk]).sum(); z=R[others,q]; xs=x[others]; mn=np.abs(R[np.ix_(others,kk)]).sum(1)
    X=2*(1+c-rho)*(xs/max(mu,1e-9)*np.maximum(z,0)).sum()+rho-2*(1-c*c)+(z*(mn-2)).sum()+a*rho*(z*np.abs(z)).sum()
    return X,mu,c,rho
def obj(v,R0,m):
    R=R_of(v,R0)
    if not np.isfinite(R).all(): return 1e6
    w=np.abs(R).sum(1); X,mu,c,rho=parts(R); return X+m*(np.maximum(w-2,0).sum()+max(c-cmax,0))
best=9; bR=None
for t in range(trials):
    R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
    v=rng.normal(size=len(iu[0]))*rng.uniform(0.05,0.6)
    for m in (3,30,300,3000):
        res=minimize(obj,v,args=(R0,m),method='L-BFGS-B',options={'maxiter':3000}); v=res.x
    R=R_of(v,R0)
    if np.isfinite(R).all() and np.abs(R).sum(1).max()<=2+1e-7 and parts(R)[2]<=cmax+1e-7:
        X=parts(R)[0]
        if X<best: best=X; bR=R
np.set_printoptions(precision=3,suppress=True,linewidth=170)
print(d,'cmax',cmax,'min X =',round(best,5), 'mu,c,rho =',np.round(parts(bR)[1:],4))
print(' col',np.abs(bR[:,0]),' rows',np.abs(bR).sum(1)); print(bR)
