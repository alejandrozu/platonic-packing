# Verify on random restricted matrices: F(Q)-F(R) >= a*mu*X, X as in the compact formula; and the case-A bound.
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(9)
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
worst=9; worstA=9; nA=0; nB=0; cnt=0
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.05,1.2); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@expm(A)
    if rng.random()<0.3: R=np.linalg.qr(rng.normal(size=(d,d)))[0]
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]; p=int(np.argmin(x)); q=1+int(np.argmax(np.abs(R[p,1:])))
    R[:,q]*=np.sign(R[p,q]); c=R[p,q]; mu=x[p]; a=1/(1+c)
    if mu<1e-9: continue
    cnt+=1
    r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; tt=x[oth]/mu; g=2-w[oth]; rho=w[p]-mu-c
    br=2*(1+c-rho)*(tt-a*z)-g
    X=c*w[p]-1+(np.maximum(-z,0)*g).sum()+(np.maximum(z,0)*br).sum()
    worst=min(worst,(F(Q)-F(R))-a*mu*X)
    if rho<=c+mu/2+mu*mu/(2*c):
        nA+=1; worstA=min(worstA,(np.where(z>0,br,0)).min())
    else: nB+=1
print(d,'samples',cnt,' min [F(Q)-F(R) - a mu X] =',worst,' caseA',nA,' min bracket in A',worstA,' caseB',nB)
