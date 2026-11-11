import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm
from hstep import value
def helmB(v):   # v sorted decreasing; columns b_2..b_d
    d=len(v); B=np.zeros((d,d-1))
    for k in range(1,d):
        A=(v[:k]**2).sum(); b=np.zeros(d); b[k]=A; b[:k]=-v[k]*v[:k]; B[:,k-1]=b/np.linalg.norm(b)
    return B
def bounds(v,C,B):
    d=len(v); n=d-1; H=2*sum(v[k]*B[k,k-1] for k in range(1,d)); lam=(C.T@B)**2   # lam[j,k-1]
    tot_l=0; tot_m=0
    for j in range(n):
        c=C[:,j]; br=[]
        for k in range(1,d):
            s=np.sign(c[k]) or 1.0
            br.append(v[k]*abs(c[k])+np.maximum(s*v[k+1:]*c[k+1:],0).sum())
        br=np.array(br); tot_l+=(lam[j]*br).sum(); tot_m+=br.max()
    return 2*tot_l-H, 2*tot_m-H, value(v,C)-H
d=int(sys.argv[1]); rng=np.random.default_rng(int(sys.argv[2])); n=d-1; iu=np.triu_indices(n,1); w=[9,9,9]
for t in range(int(sys.argv[3])):
    v=np.sort(np.abs(rng.normal(size=d)))[::-1]; v/=np.linalg.norm(v)
    if t%4==0: v=np.ones(d)/np.sqrt(d)
    B=helmB(v)
    for which in (0,1):
        def f(x):
            A=np.zeros((n,n)); A[iu]=x; return bounds(v,B@expm(A-A.T),B)[which]
        r=minimize(f,rng.normal(size=len(iu[0])),method='Nelder-Mead',options={'maxiter':3000})
        w[which]=min(w[which],r.fun)
print(d,'min over C of [flag-lambda bound - H] = %.4f ;  [flag-max bound - H] = %.4f'%(w[0],w[1]))
