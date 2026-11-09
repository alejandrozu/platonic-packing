# Inductive inequality for the band bound BC:  F_j(R) <= 1 - phi(m_j),  phi(m) = (m + sqrt(1-m^2) - 1)^2 for m >= 1/sqrt2.
# Near step at the largest entry c = m_j (row i0):  1 - F_j(R) >= sum_k |r_k| (1 - F_k(Q)) + E + 2(1-c)(1-rho0).
# With the IH  1 - F_k(Q) >= phi_k := phi(max_i |Q_ik|) (phi := phi(1/sqrt2) below 1/sqrt2, conservatively),
# test  LHS := sum_k |r_k| phi_k + E + 2(1-c)(1-rho0)  >=  phi(c).
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
s2=1/np.sqrt(2)
def phi(m): m=np.maximum(m,s2); return (m+np.sqrt(1-m*m)-1)**2
def F(R,j): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
cnt=0; bad=0; worst=9; ex=None; bcv=0
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.02,1.0); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@np.diag(rng.choice([-1,1],d))@expm(A)
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    for j in range(d):
        x=np.abs(R[:,j]); i0=int(np.argmax(x)); c=x[i0]
        if c<s2: continue
        cnt+=1
        if 1-F(R,j) < phi(c)-1e-12: bcv+=1
        Rn=R.copy(); Rn[i0]*=np.sign(Rn[i0,j]); cc=Rn[i0,j]
        r=np.delete(Rn[i0],j); xx=np.delete(Rn[:,j],i0); M=np.delete(np.delete(Rn,i0,0),j,1)
        Q=M-np.outer(xx,r)/(1+cc); wQ=np.abs(Q).sum(1)
        if wQ.max()>2+1e-12: continue
        rho0=np.abs(r).sum(); yv=Q.T@xx            # = -r
        E=((2-wQ)*(np.abs(Q)@np.abs(yv)-np.abs(xx))).sum()
        mk=np.abs(Q).max(0); LHS=(np.abs(r)*phi(mk)).sum()+E+2*(1-cc)*(1-rho0)
        v=LHS-phi(cc)
        if v<worst: worst=v; ex=(c,rho0,E,LHS,phi(cc),1-F(R,j))
        if v<-1e-12: bad+=1
print(d,'cases',cnt,'BC violations',bcv,'inductive-ineq failures',bad,'min LHS-phi(c)',round(worst,5),' (c,rho0,E,LHS,phi(c),1-F) at worst',np.round(ex,4))
