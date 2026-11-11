# max over RC of Delta = F_j(R) - F_j(Q) for the pivot p = argmin x, q = argmax_{q != j} |R_pq|.
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(31+d); iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; return R0@expm(A)
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def polar(R,p,q):
    s=np.sign(R[p,q]) or 1.0; R=R.copy(); R[:,q]*=s
    c=R[p,q]; r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1)
    return M-np.outer(xt,r)/(1+c)
def delta(R):
    x=np.abs(R[:,0]); p=int(np.argmin(x)); q=1+int(np.argmax(np.abs(R[p,1:])))
    Q=polar(R,p,q); return F(R)-F(Q), np.abs(Q).sum(1).max()
def pen(R):
    w=np.abs(R).sum(1); x=np.abs(R[:,0]); rest=w-x
    return np.maximum(w-2,0).sum()
def obj(v,R0,mu): R=R_of(v,R0); D,wq=delta(R); return -(D-mu*(pen(R)+max(wq-2,0)))
best=-9; bR=None
for t in range(trials):
    if t%2: R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
    else:
        col=np.abs(rng.normal(size=d))+0.5; col/=np.linalg.norm(col)
        R0=np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]
    v=rng.normal(size=len(iu[0]))*0.1
    for mu in (3,30,300,3000):
        res=minimize(obj,v,args=(R0,mu),method='L-BFGS-B',options={'maxiter':2000}); v=res.x
    R=R_of(v,R0); D,wq=delta(R)
    if pen(R)<1e-7 and wq<=2+1e-7 and D>best: best=D; bR=R
np.set_printoptions(precision=3,suppress=True,linewidth=170)
print(d,'max Delta(argmin,argmax) over rows<=2 =',round(best,5))
if bR is not None:
    x=np.abs(bR[:,0]); print(' F',round(F(bR),4),'col',x,'S',round(x.sum(),3)); print(' rows',np.abs(bR).sum(1)); print(bR)
