import numpy as np, sys
from scipy.optimize import linprog
from hstep import *
def helmert(v):
    d=len(v); o=np.argsort(-v); vs=v[o]; A=np.zeros((d,d-1))
    for k in range(1,d):
        Ak=(vs[:k]**2).sum(); b=np.zeros(d); b[k]=Ak; b[:k]=-vs[k]*vs[:k]; A[o,k-1]=b/np.linalg.norm(b)
    return A
def LP(v,C):
    d=len(v); r=linprog(np.ones(d-1),A_ub=-np.abs(C),b_ub=-2*v*(1-v*v),bounds=[(0,None)]*(d-1)); return r.fun
rng=np.random.default_rng(1)
for d in (3,4,6,10):
    w=9; wh=9
    for t in range(300):
        v=np.abs(rng.normal(size=d)); v/=np.linalg.norm(v)
        if t%3==0: v=np.ones(d)/np.sqrt(d)
        C=randC(v,rng); w=min(w,LP(v,C)-2*(v.sum()-1)); H=helmert(v); wh=min(wh,LP(v,H)-2*(v.sum()-1))
    print(d,'min LP-2(S-1): random C %.4f, Helmert C %.4f'%(w,wh))
