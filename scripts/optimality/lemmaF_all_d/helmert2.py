# Targeted test of Helmert optimality: sink-like vectors v = (c, t, ..., t), two large entries, geometric decay;
# optimiser started from random bases and from perturbed Helmert bases.
import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm, null_space
d=int(sys.argv[1]); rng=np.random.default_rng(77+d); n=d-1; iu=np.triu_indices(n,1)
def helmert_basis(v):
    order=np.argsort(-v); w=v[order]; cols=[]
    for k in range(1,d):
        b=np.zeros(d); A=(w[:k]**2).sum(); b[k]=A; b[:k]=-w[k]*w[:k]; b/=np.linalg.norm(b); cols.append(b)
    B=np.zeros((d,n)); B[order,:]=np.array(cols).T; return B
fams=[]
for c in (0.95,0.9,0.85,0.8,0.7):
    v=np.full(d,np.sqrt((1-c*c)/(d-1))); v[0]=c; fams.append(('sink c=%.2f'%c,v))
for a in (0.6,0.5):
    v=np.full(d,0.0); v[0]=v[1]=a; v[2:]=np.sqrt((1-2*a*a)/(d-2)); fams.append(('two big %.2f'%a,v))
for q in (0.8,0.6):
    v=q**np.arange(d); v/=np.linalg.norm(v); fams.append(('geometric %.1f'%q,v))
worst=0
for name,v in fams:
    B0=helmert_basis(v); H=np.abs(B0*v[:,None]).sum()
    def G(p,Bs):
        A=np.zeros((n,n)); A[iu]=p; A=A-A.T; return np.abs((Bs@expm(A))*v[:,None]).sum()
    best=1e9
    for s in range(30):
        Bs=B0 if s<10 else null_space(v[None,:])
        sc=0.02 if s<10 else rng.uniform(0.1,2)
        res=minimize(G,rng.normal(size=len(iu[0]))*sc,args=(Bs,),method='L-BFGS-B',options={'maxiter':3000})
        best=min(best,res.fun)
    worst=min(worst,best-H)
    print(d,name,'Helmert',round(H,6),'best found',round(best,6),'2(S-1)',round(2*(v.sum()-1),6),flush=True)
print(d,'most negative gap',worst)
