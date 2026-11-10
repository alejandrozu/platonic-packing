# For restricted matrices: does a "good row" b exist (generalized case A)?  Report failures, and F at failures.
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(17)
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def good(R,j,b):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[j]]+1e-300); x=R[:,j]
    oth=[k for k in range(d) if k!=j]; q=oth[int(np.argmax(np.abs(R[b,oth])))]
    c=abs(R[b,q]);
    if c<x[b]: return False
    z=R[:,q]*np.sign(R[b,q]); xb=x[b]; rho=w[b]-xb-c; a=1/(1+c)
    if xb+rho>1+c: return False
    K=2*(1+c-rho)+xb+xb*xb/c
    for i in range(d):
        if i==b or z[i]<=0: continue
        if x[i]*K+2*a*xb*rho*z[i]<2*xb-1e-12 or x[i]<a*xb*z[i]-1e-12: return False
    return True
cnt=0; fails=0; maxF=-9; argminfail=0
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.05,1.2); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@expm(A)
    if rng.random()<0.4: R=np.linalg.qr(rng.normal(size=(d,d)))[0]
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    for j in range(d):
        cnt+=1; x=np.abs(R[:,j])
        if not good(R,j,int(np.argmin(x))): argminfail+=1
        else: continue
        if not any(good(R,j,b) for b in range(d)):
            fails+=1; maxF=max(maxF,F(R,j))
print(d,'cases',cnt,'argmin not good',argminfail,'no good row',fails,'maxF at no-good',round(maxF,4))
# second pass: RC only, and also allow old off-column step (c^2>=3/4, x_b <= 2(1+2c-w_b) x_i)
def oldO(R,j,b):
    w=np.abs(R).sum(1); x=np.abs(R[:,j]); oth=[k for k in range(d) if k!=j]; c=np.abs(R[b,oth]).max()
    if c*c<0.75: return False
    return all(x[b]<=2*(1+2*c-w[b])*x[i]+1e-12 for i in range(d) if i!=b)
cnt=0; fails=0; maxF=-9; ex=None
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.05,1.2); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@expm(A)
    if rng.random()<0.4: R=np.linalg.qr(rng.normal(size=(d,d)))[0]
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    for j in range(d):
        x=np.abs(R[:,j]); rest=w-x
        if x.sum()<=2 or (rest[x>1e-12]<=1).any(): continue
        cnt+=1
        if any(good(R,j,b) or oldO(R,j,b) for b in range(d)): continue
        fails+=1
        if F(R,j)>maxF: maxF=F(R,j); ex=(R,j)
print(d,'RC cases',cnt,'no good row/oldO',fails,'maxF',round(maxF,4))
if ex is not None:
    np.set_printoptions(precision=3,suppress=True,linewidth=170); R,j=ex; print(' j',j,'col',np.abs(R[:,j]),'rows',np.abs(R).sum(1)); print(R)
