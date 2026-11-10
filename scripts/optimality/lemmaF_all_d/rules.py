import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm
from hstep import *
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); iu=np.triu_indices(d-1,1)
def pick(v,C,rule):
    sl=allslack(v,C)
    if rule=='conc': return max(sl,key=lambda s:s[1])
    if rule=='minv': return min(sl,key=lambda s:v[s[2]])
    if rule=='maxv': return max(sl,key=lambda s:v[s[2]])
    if rule=='best': return max(sl,key=lambda s:s[0])
worst={r:(9,None) for r in ('conc','minv','maxv','best')}
for t in range(N):
    k=t%3
    v=np.abs(rng.normal(size=d)) if k==0 else (np.ones(d)+rng.normal(size=d)*0.1 if k==1 else np.abs(rng.normal(size=d))*rng.exponential(1,d)**2)
    v=np.abs(v)/np.linalg.norm(v); C0=randC(v,rng)
    def Cof(x):
        A=np.zeros((d-1,d-1)); A[iu]=x; return C0@expm(A-A.T)
    for rule in worst:
        x=rng.normal(size=len(iu[0]))*0.3
        r=minimize(lambda x: pick(v,Cof(x),rule)[0],x,method='Powell',options={'maxiter':6000,'ftol':1e-10})
        if r.fun<worst[rule][0]: worst[rule]=(r.fun,(v,Cof(r.x)))
for rule,(f,ex) in worst.items():
    v,C=ex; s=pick(v,C,rule); print(d,rule,'worst slack %.5f'%f,' c\' %.3f v_p %.3f'%(s[1],v[s[2]]),' Value-2(S-1) %.4f'%(value(v,C)-2*(v.sum()-1)),' v',np.round(v,3))
