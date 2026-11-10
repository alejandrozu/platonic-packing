# The case left after the all-dimension near step: R orthogonal, every row l1 <= 2, and every row i of column 0
# has rest l1 >= 1 (no row qualifies for the near step).  Then F < S - 1, so only S = |col|_1 > 2 matters.
# Report sup F in this case (penalty method, many restarts), and the zero-sum bound max sum phi(x_i) with S >= 2.
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(7+d); iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; return R0@expm(A)
def parts(R):
    w=np.abs(R).sum(1); x=np.abs(R[:,0]); rest=w-x; return w,x,rest
def obj(v,R0,mu):
    R=R_of(v,R0); w,x,rest=parts(R)
    F=(x*(2-w)).sum()
    pen=np.maximum(w-2,0).sum()+np.maximum(1-rest,0).sum()+max(2-x.sum(),0)
    return -(F-mu*pen)
best=-9; bR=None
for t in range(trials):
    if t%2: R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
    else:
        col=np.abs(rng.normal(size=d))+0.5; col/=np.linalg.norm(col)
        M=np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]; R0=M
    v=rng.normal(size=len(iu[0]))*0.1
    for mu in (3,30,300):
        res=minimize(obj,v,args=(R0,mu),method='L-BFGS-B',options={'maxiter':3000}); v=res.x
    R=R_of(v,R0); w,x,rest=parts(R)
    ok=(w.max()<=2+1e-7) and (rest[x>1e-9].min()>=1-1e-7) and x.sum()>=2-1e-7
    if ok:
        F=(x*(2-w)).sum()
        if F>best: best=F; bR=R
phi=lambda t:(2-np.sqrt(2))*t-t*t+np.sqrt(2)*t**3
# zero-sum bound over the sphere with S >= 2
zb=-9
for t in range(4000):
    x=np.abs(rng.normal(size=d))**rng.uniform(0.2,3); x/=np.linalg.norm(x)
    res=minimize(lambda z:-(phi(np.abs(z)/np.linalg.norm(z)).sum())+100*max(2-np.abs(z).sum()/np.linalg.norm(z),0),x,method='Nelder-Mead',options={'maxiter':4000})
    z=np.abs(res.x)/np.linalg.norm(res.x)
    if z.sum()>=2-1e-6: zb=max(zb,phi(z).sum())
np.set_printoptions(precision=3,suppress=True,linewidth=160)
print(d,'remaining case: sup F =',round(best,5),' | zero-sum bound sup (S>=2) =',round(zb,5))
if bR is not None:
    w,x,rest=parts(bR); print('  col',x,'S',round(x.sum(),3),'rows',w)
