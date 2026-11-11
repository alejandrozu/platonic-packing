"""Checks of the equivalent forms in Paper IV, section 2 (writes nothing; prints the largest errors).

1. Chords: for an n-simplex D and a unit vector c, the longest chord is L(c) = n vol(D) / sum_i a_i <u_i, c>^+, and a
   unit cube with orthonormal edge directions c_k fits in D by a translation iff sum_k 1/L(c_k) <= 1 (against an LP).
2. Cube in a corner simplex: a unit (d-1)-cube with frame C fits in {xi >= 0, <v, xi> = lam} iff lam >= Value(C)/2
   (against an LP), for random v > 0 and random frames.
3. Helmert: the Helmert frame is a frame of v^perp with value H(v), H(v) >= 2(S - 1), and H(v) = a H(v') + 2 v_d a.
"""
# Check: for an n-simplex D and unit vector c, the longest chord L(c) = n vol(D) / sum_i a_i <u_i,c>^+ ;
# and a unit cube with orthonormal edge directions c_k fits in D by translation iff sum_k 1/L(c_k) <= 1.
import numpy as np, math, itertools
from scipy.optimize import linprog
rng=np.random.default_rng(0)
def simplex_data(V):
    n=V.shape[1]; vol=abs(np.linalg.det(V[1:]-V[0]))/math.factorial(n)
    us=[];bs=[];areas=[]
    for i in range(n+1):
        W=np.delete(V,i,0); u=np.linalg.svd(W[1:]-W[0])[2][-1]
        if (V[i]-W[0])@u>0: u=-u
        us.append(u); bs.append(u@W[0])
        G=(W[1:]-W[0]); areas.append(math.sqrt(abs(np.linalg.det(G@G.T)))/math.factorial(n-1))
    return vol,np.array(us),np.array(bs),np.array(areas)
def longest_chord(V,c):
    n=V.shape[1]; m=n+1
    # max t s.t. x = sum l_i V_i, x + t c = sum mu_i V_i, l,mu simplex weights
    nv=2*m+1; cost=np.zeros(nv); cost[-1]=-1
    Aeq=[];beq=[]
    for k in range(n):
        row=np.zeros(nv); row[:m]=V[:,k]; row[m:2*m]=-V[:,k]; row[-1]=c[k]; Aeq.append(row); beq.append(0)
    r=np.zeros(nv); r[:m]=1; Aeq.append(r); beq.append(1)
    r=np.zeros(nv); r[m:2*m]=1; Aeq.append(r); beq.append(1)
    res=linprog(cost,A_eq=np.array(Aeq),b_eq=beq,bounds=[(0,None)]*nv,method='highs'); return -res.fun
worst=0; mism=0
for trial in range(300):
    n=rng.integers(2,6); V=rng.normal(size=(n+1,n))
    vol,us,bs,ar=simplex_data(V)
    c=rng.normal(size=n); c/=np.linalg.norm(c)
    L=longest_chord(V,c); L2=n*vol/(ar*np.maximum(us@c,0)).sum()
    worst=max(worst,abs(L-L2)/L)
    # fit test for a scaled cube
    C=np.linalg.qr(rng.normal(size=(n,n)))[0]; s=rng.uniform(0.05,1.0)*min(longest_chord(V,C[:,k]) for k in range(n))
    crit=sum(1/longest_chord(V,C[:,k]) for k in range(n))*s<=1
    # LP: exists t with t + C y in D for all vertices y of [0,s]^n: u_i.(t + C y) <= b_i -> u_i.t <= b_i - s*sum_k (u_i.C_k)^+
    rhs=bs-s*np.maximum(us@C,0).sum(1)
    res=linprog(np.zeros(n),A_ub=us,b_ub=rhs,bounds=[(None,None)]*n,method='highs')
    if (res.status==0)!=crit: mism+=1
print('max rel error of chord formula',worst,' fit-criterion mismatches',mism,'of 300')

# 2. corner simplex criterion
from scipy.linalg import null_space
mism2=0
for trial in range(300):
    d=rng.integers(3,7); v=np.abs(rng.normal(size=d))+0.05; v/=np.linalg.norm(v)
    C=null_space(v[None,:])@np.linalg.qr(rng.normal(size=(d-1,d-1)))[0]
    val=(v*np.abs(C).sum(1)).sum(); lam=val/2*rng.uniform(0.8,1.2)
    # LP: exists xi0 with <v,xi0> = lam and xi0_i + sum_k min(0,C_ik) >= 0
    neg=np.minimum(C,0).sum(1)
    res=linprog(np.zeros(d),A_ub=-np.eye(d),b_ub=neg,A_eq=v[None,:],b_eq=[lam],bounds=[(None,None)]*d,method='highs')
    if (res.status==0)!=(lam>=val/2-1e-12): mism2+=1
print('corner-simplex criterion mismatches',mism2,'of 300')
# 3. Helmert
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames import helmert_value, helmert_frame
e1=e2=e3=0; low=9
for trial in range(500):
    d=rng.integers(3,12); v=np.abs(rng.normal(size=d))**rng.uniform(0.5,3); v/=np.linalg.norm(v)
    C=helmert_frame(v); H=helmert_value(v)
    e1=max(e1,abs(C.T@v).max(),abs(C.T@C-np.eye(d-1)).max()); e2=max(e2,abs((v*np.abs(C).sum(1)).sum()-H))
    low=min(low,H-2*(v.sum()-1))
    w=np.sort(v)[::-1]; a=math.sqrt(1-w[-1]**2); e3=max(e3,abs(H-(a*helmert_value(w[:-1]/a)+2*w[-1]*a)))
print('Helmert frame error',e1,' value error',e2,' min H-2(S-1)',low,' recursion error',e3)
