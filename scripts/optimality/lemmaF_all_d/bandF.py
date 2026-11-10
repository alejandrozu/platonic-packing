# sup of F_0(R) over orthogonal R whose column 0 has max entry^2 <= tau (penalty), many restarts
import numpy as np, sys, json
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); taus=[float(t) for t in sys.argv[2].split(',')]; trials=int(sys.argv[3])
rng=np.random.default_rng(d)
iu=np.triu_indices(d,1)
def R_of(v,R0):
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T
    return R0@expm(A)
def obj(v,R0,tau,restrict):
    R=R_of(v,R0); w=np.abs(R).sum(1); x=np.abs(R[:,0])
    f=(x*(2-w)).sum()-100*np.maximum(x.max()**2-tau,0)
    if restrict: f-=100*np.maximum(w-2,0).sum()
    return -f
out={}
for tau in taus:
    for restrict in (0,1):
        best=-9
        for t in range(trials):
            R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
            if t%2: # start from a structured column: spread over k coordinates
                k=rng.integers(2,d+1); col=np.zeros(d); col[:k]=rng.choice([-1,1],k)/np.sqrt(k)
                M=np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]; M[:,0]*=np.sign(M[:,0]@col); R0=M
            v0=rng.normal(size=len(iu[0]))*0.05
            res=minimize(obj,v0,args=(R0,tau,restrict),method='L-BFGS-B',options={'maxiter':3000})
            R=R_of(res.x,R0); x=np.abs(R[:,0]); w=np.abs(R).sum(1)
            if x.max()**2<=tau+1e-6 and (not restrict or w.max()<=2+1e-6):
                best=max(best,(x*(2-w)).sum())
        out[f'{tau}_{restrict}']=best
        print(d,'tau',tau,'restricted' if restrict else 'all',round(best,5),flush=True)
json.dump(out,open(f'band{d}.json','w'))
