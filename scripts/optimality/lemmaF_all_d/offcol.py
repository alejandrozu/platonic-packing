# Off-column step: pivot at the row p with the smallest |R_pj| and its largest entry c = |R_pq| (q != j).
# Claim: if c^2 >= 3/4 (and rows of R are <= 2), then F_j(R) <= F_j(Q), Q the polar factor of R minus row p, column q.
import numpy as np, sys
from scipy.linalg import expm
rng=np.random.default_rng(5)
def polar_drop(R,p,q):
    s=np.sign(R[p,q]); R=R.copy(); R[:,q]*=s
    c=R[p,q]; r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1)
    Q=M-np.outer(xt,r)/(1+c); return Q, c, r
def F(R,j): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
bad=0; tested=0; worst=-9
for t in range(200000):
    d=rng.integers(3,9)
    A=rng.normal(size=(d,d))*rng.uniform(0.05,0.8); A=A-A.T
    P=np.eye(d)[rng.permutation(d)]*rng.choice([-1,1],d)
    R=P@expm(A)
    if np.abs(R).sum(1).max()>2: continue
    j=0; x=np.abs(R[:,j]); p=int(np.argmin(x)); q=int(np.argmax(np.abs(R[p]))); c=abs(R[p,q])
    if q==j or c*c<0.75: continue
    tested+=1
    Q,_,_=polar_drop(R,p,q); jq=j if j<q else j-1
    assert np.abs(Q@Q.T-np.eye(d-1)).max()<1e-9
    diff=F(R,j)-F(Q,jq); worst=max(worst,diff)
    if diff>1e-12: bad+=1
print('tested',tested,'violations',bad,'max F(R)-F(Q)',worst)
