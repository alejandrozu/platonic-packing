# Random check of the pivot conjecture (Lean form of Xi) in dimension d.
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
def Xi(R):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]; p=int(np.argmin(x))
    q=1+int(np.argmax(np.abs(R[p,1:]))); R=R.copy(); R[:,q]*=np.sign(R[p,q]); c=R[p,q]; nu=x[p]
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; y=x[oth]; G=2-w[oth]
    L=w[p]-c; a=(1-c)/(z**2).sum(); k1=1+c-(L-nu)
    return nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum(), nu, c
cnt=0; worst=9; wr=None
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.02,0.9); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@np.diag(rng.choice([-1,1],d))@expm(A)
    if np.abs(R).sum(1).max()>2: continue
    cnt+=1; X,nu,c=Xi(R)
    v=X/max(nu,1e-12)
    if v<worst: worst=v; wr=(nu,c)
print(d,'samples',cnt,'min Xi/nu',round(worst,5),'(nu,c) there',np.round(wr,4) if wr else None)
