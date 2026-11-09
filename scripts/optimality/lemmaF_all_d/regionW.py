# sup F over W = RC and no good row (generalized case A) and no old-O row. Penalty method.
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; return R0@expm(A)
def F(R): w=np.abs(R).sum(1); return (np.abs(R[:,0])*(2-w)).sum()
def margins(R):
    # for each row b: a number <= 0 iff row b is good (gen. case A) or old-O applies; we need all > 0
    w=np.abs(R).sum(1); Rn=R*np.sign(R[:,[0]]+1e-300); x=Rn[:,0]; out=[]
    for b in range(d):
        q=1+int(np.argmax(np.abs(Rn[b,1:]))); c=abs(Rn[b,q]); z=Rn[:,q]*np.sign(Rn[b,q]); xb=x[b]; rho=w[b]-xb-c; a=1/(1+c)
        K=2*(1+c-rho)+xb+xb*xb/c
        viol=[2*xb-x[i]*K-2*a*xb*rho*z[i] for i in range(d) if i!=b and z[i]>0]+[a*xb*z[i]-x[i] for i in range(d) if i!=b and z[i]>0]
        mA=max([xb-c, xb+rho-1-c]+viol) if viol else max(xb-c, xb+rho-1-c)   # good iff mA<=0
        mO=max([0.75-c*c]+[x[b]-2*(1+2*c-w[b])*x[i] for i in range(d) if i!=b])  # oldO iff mO<=0
        out.append(min(mA,mO))
    return np.array(out)
def pen(R):
    w=np.abs(R).sum(1); x=np.abs(R[:,0]); rest=w-x
    return np.maximum(w-2,0).sum()+np.maximum(1-rest,0).sum()+max(2-x.sum(),0)+np.maximum(1e-4-margins(R),0).sum()
def obj(v,R0,m):
    R=R_of(v,R0)
    if not np.isfinite(R).all(): return 1e6
    return -(F(R)-m*pen(R))
best=-9; bR=None
for t in range(trials):
    R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
    v=rng.normal(size=len(iu[0]))*0.1
    for m in (3,30,300,3000):
        v=minimize(obj,v,args=(R0,m),method='L-BFGS-B',options={'maxiter':1500}).x
    R=R_of(v,R0)
    if np.isfinite(R).all() and pen(R)<1e-9 and F(R)>best: best=F(R); bR=R; print('  t',t,'best',round(best,4),flush=True)
np.set_printoptions(precision=3,suppress=True,linewidth=170)
print(d,'sup F over W =',best)
if bR is not None: print(' col',np.abs(bR[:,0]),' rows',np.abs(bR).sum(1)); print(bR)
