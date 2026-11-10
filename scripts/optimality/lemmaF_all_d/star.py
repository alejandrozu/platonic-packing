# (*)  Value(C) >= a * Value(C'') + 2 v_p |C_pq|   (Helmert step at row p, column q = argmax |C_p.|), needs |r_p|_1 <= a + 2|C_pq|
import numpy as np, sys
from hstep import *
rng=np.random.default_rng(int(sys.argv[1])); worst=9; n=0; nout=0; worst_out=9
for t in range(int(sys.argv[2])):
    d=int(rng.integers(3,11)); v=np.abs(rng.normal(size=d))*rng.exponential(1,d)**rng.integers(0,3); v/=np.linalg.norm(v)
    C=randC(v,rng)
    if rng.random()<0.5:   # near-Helmert-ish: make rows concentrated by sorting trick
        from scipy.linalg import expm
        o=np.argsort(-v); A=np.zeros((d,d-1)); vs=v[o]
        for k in range(1,d):
            Ak=(vs[:k]**2).sum(); b=np.zeros(d); b[k]=Ak; b[:k]=-vs[k]*vs[:k]; A[o,k-1]=b/np.linalg.norm(b)
        S=rng.normal(size=(d-1,d-1))*rng.uniform(0,0.5); C=A@expm(S-S.T)
    for p in range(d):
        nu=v[p]; a=np.sqrt(1-nu*nu)
        if a<1e-6: continue
        q=int(np.argmax(np.abs(C[p]))); s,c=step(v,C,p,q)
        lhs=s-2*(1-a)*(1-nu)+2*nu*a-2*nu*abs(C[p,q])    # = Value - a Value'' - 2 v_p |C_pq|
        if np.abs(C[p]).sum()<=a+2*abs(C[p,q]): n+=1; worst=min(worst,lhs)
        else: nout+=1; worst_out=min(worst_out,lhs)
print('in domain',n,'min',worst,'| outside domain',nout,'min',worst_out)
