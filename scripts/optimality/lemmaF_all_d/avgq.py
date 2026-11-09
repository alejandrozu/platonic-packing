# Averaging over pivot columns q in the argmin row p, weights c_q = |R_pq|.
# Xi_q for any q with c_q>0 (pivot_bound needs no argmax).  Valid pivots: L_q <= 1 + c_q.
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
def Xi_q(R,p,q):
    # R normalised: column 0 >= 0
    w=np.abs(R).sum(1); s=np.sign(R[p,q]); c=abs(R[p,q]); nu=R[p,0]
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]*s; y=R[oth,0]; G=2-w[oth]
    L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    return nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum(), L<=1+c+1e-12
stats=dict(n=0,allvalid=0,avg_allvalid_neg=0,avgV_neg=0,anyok_fail=0,argmax_neg=0)
worst=9
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.02,0.9); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@np.diag(rng.choice([-1,1],d))@expm(A)
    if rng.random()<0.3: R=np.linalg.qr(rng.normal(size=(d,d)))[0]
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    R=R*np.sign(R[:,[0]]+1e-300); p=int(np.argmin(R[:,0]))
    stats['n']+=1
    qs=[q for q in range(1,d) if abs(R[p,q])>1e-12]
    vals=[(abs(R[p,q]),)+Xi_q(R,p,q) for q in qs]
    valid=[v for v in vals if v[2]]
    if len(valid)==len(vals): stats['allvalid']+=1
    sV=sum(v[0]*v[1] for v in valid)
    if sV<-1e-12: stats['avgV_neg']+=1
    if not any(v[1]>=-1e-12 for v in valid): stats['anyok_fail']+=1
    qa=max(vals,key=lambda v:v[0])
    if qa[1]<-1e-12: stats['argmax_neg']+=1
    nu=R[p,0]
    if nu>1e-9: worst=min(worst,sV/nu**2)
print(d,stats,'min sum_V c Xi / nu^2 =',round(worst,4))
