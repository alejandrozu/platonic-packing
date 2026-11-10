# Search for a counterexample to restricted Lemma F: maximise F_0(R) over orthogonal R with all rows l1 <= 2,
# from many random starts (Haar, near-uniform column, sink-like, block-structured). Report the best F and the best
# value found away from equality cases (max |R_i0| <= 0.95).
import numpy as np, sys, time
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); iu=np.triu_indices(d,1)
def F(R): w=np.abs(R).sum(1); return (np.abs(R[:,0])*(2-w)).sum()
def start(t):
    k=t%4
    if k==0: return np.linalg.qr(rng.normal(size=(d,d)))[0]
    if k==1:
        col=np.abs(np.ones(d)+rng.normal(size=d)*0.4); col/=np.linalg.norm(col)
        return np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]
    if k==2:   # sink-like: one large entry, others small
        col=np.abs(rng.normal(size=d))*0.15; col[0]=rng.uniform(0.6,0.9); col/=np.linalg.norm(col)
        return np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]
    A=rng.normal(size=(d,d))*rng.uniform(0.1,0.8); A=A-A.T; return np.eye(d)[rng.permutation(d)]@expm(A)
best=-9; bestfar=-9; t0=time.time()
for t in range(trials):
    R0=start(t)
    def obj(v,m):
        A=np.zeros((d,d)); A[iu]=v; A=A-A.T; R=R0@expm(A); w=np.abs(R).sum(1); return -F(R)+m*np.maximum(w-2,0).sum()
    v=rng.normal(size=len(iu[0]))*0.05
    for m in (3,30,300,3000):
        v=minimize(obj,v,args=(m,),method='L-BFGS-B',options={'maxiter':1500}).x
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; R=R0@expm(A); w=np.abs(R).sum(1)
    if w.max()<=2+1e-12:
        f=F(R); best=max(best,f)
        if np.abs(R[:,0]).max()<=0.95 and f>bestfar: bestfar=f; np.save('cexsearch_%d.npy'%d,R)
        if f>1+1e-9: print('  !!! F > 1:',f,flush=True); np.save('cexsearch_hit_%d_%d.npy'%(d,t),R)
print(d,'trials',trials,'best F %.6f'%best,' best F away from axis-aligned columns %.6f'%bestfar,' time %.0fs'%(time.time()-t0),flush=True)
