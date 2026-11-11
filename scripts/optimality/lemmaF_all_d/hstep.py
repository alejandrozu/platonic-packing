# C-formulation: v>=0 unit, C = d x (d-1) ONB of v^perp, rows r_i. Value = sum v_i |r_i|_1 ; Lemma F <=> Value >= 2(S-1).
# Helmert step at (p,q): rotate R^{d-1} so r_p -> a e_q, drop row p / col q -> C'' ONB of v'^perp.
# slack_pq = Value(C) - a Value(C'') - 2 nu a + 2(1-a)(1-nu) >= 0 closes the induction.
import numpy as np, sys
from scipy.optimize import minimize
from scipy.linalg import expm, null_space
def value(v,C): return (v*np.abs(C).sum(1)).sum()
def step(v,C,p,q):
    d=len(v); nu=v[p]; a=np.sqrt(1-nu*nu); u=C[p]/a
    if u[q]<0: C=C.copy(); C[:,q]*=-1; u=C[p]/a
    c=u[q]; e=np.zeros(d-1); e[q]=1
    G=lambda r: r-(r@(u+e))/(1+c)*(u+e)+2*(r@u)*e
    Ct=np.array([G(r) for r in C]); C2=np.delete(np.delete(Ct,p,0),q,1); v2=np.delete(v,p)/a
    return value(v,C)-a*value(v2,C2)-2*nu*a+2*(1-a)*(1-nu), c
def allslack(v,C):
    d=len(v); out=[]
    for p in range(d):
        if v[p]>1-1e-9: continue
        q=int(np.argmax(np.abs(C[p]))); s,c=step(v,C,p,q); out.append((s,c,p,q))
    return out
def randC(v,rng):
    B=null_space(v[None,:]); return B@np.linalg.qr(rng.normal(size=(len(v)-1,)*2))[0]
if __name__=="__main__":
    d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); iu=np.triu_indices(d-1,1)
    worst=9
    for t in range(N):
        k=t%3
        v=np.abs(rng.normal(size=d)) if k==0 else (np.ones(d)+rng.normal(size=d)*0.1 if k==1 else np.abs(rng.normal(size=d))*rng.exponential(1,d)**2)
        v=np.abs(v)/np.linalg.norm(v); C0=randC(v,rng)
        Cof=lambda x:(lambda A: C0@expm(A-A.T))((lambda A:(A.__setitem__(iu,x),A)[1])(np.zeros((d-1,d-1))))
        # adversary: minimise the best slack over rows
        f=lambda x: max(s[0] for s in allslack(v,Cof(x)))
        x=rng.normal(size=len(iu[0]))*0.3
        r=minimize(f,x,method='Nelder-Mead',options={'maxiter':4000,'fatol':1e-10})
        if r.fun<worst: worst=r.fun; C=Cof(r.x); print(' t',t,'min max_p slack %.5f'%r.fun,' Value-2(S-1) %.4f'%(value(v,C)-2*(v.sum()-1)),' v',np.round(np.sort(v),3),flush=True)
    print(d,'worst',worst)
