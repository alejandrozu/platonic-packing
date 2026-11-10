# Structured family: row p = (nu, c, c, c3, c4) spread; n "light" rows with entries (nu t, e, -e) in (j,q,k) and an axis;
# 4 rows H spanning p^perp in the first 5 coordinates, with H_q = H_k so that columns q,k can be orthogonal.
# Exact orthogonality by Gram-Schmidt in the order [p, H, L].
import numpy as np, sys
from scipy.linalg import expm
rng=np.random.default_rng(int(sys.argv[2])); n=int(sys.argv[1]); d=5+n
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def parts(R,p):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]
    q=1+int(np.argmax(np.abs(R[p,1:]))); R=R.copy(); R[:,q]*=np.sign(R[p,q]); c=R[p,q]; nu=max(x[p],1e-12)
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; y=x[oth]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    return Xi/nu, F(Q)-F(R), c, L-nu, nu, k1, np.abs(Q).sum(1).max(), F(R)
def gs(A):
    Q,Rr=np.linalg.qr(A.T); return (Q*np.sign(np.diag(Rr))).T
best=None; tried=0; valid=0
for t in range(int(sys.argv[3])):
    nu=rng.uniform(0.0005,0.03); c=rng.uniform(0.5,0.65); c3=rng.uniform(0.25,0.45)
    c4sq=1-nu*nu-2*c*c-c3*c3
    if c4sq<=0 or np.sqrt(c4sq)>c: continue
    pr=np.array([nu,c,c,c3,np.sqrt(c4sq)])
    if pr.sum()>1.995: continue
    # H: basis of p^perp in R^5 with equal q,k entries: work in the subspace {v: v_q = v_k}
    E=np.eye(5); B0=np.column_stack([E[0],(E[1]+E[2])/np.sqrt(2),E[3],E[4]])   # 5x4, spans v_q=v_k
    pp=B0.T@pr                                                                 # p projected
    C=np.linalg.qr(np.column_stack([pp,rng.normal(size=(4,3))]))[0][:,1:]      # 3 vectors in R^4 orth to pp
    C=C@expm((lambda S:S-S.T)(rng.normal(size=(3,3))*2)); H3=(B0@C).T            # 3 rows in R^5
    # 4th H row: orthogonal to p and H3, lies outside v_q=v_k
    h4=np.linalg.svd(np.vstack([pr,H3]))[2][-1]; H=np.vstack([H3,h4])
    H=H*np.sign(H[:,[0]]+1e-300)
    if (np.abs(H).sum(1)>1.9).any(): continue
    A=np.zeros((d,d)); A[0,:5]=pr; A[1:5,:5]=H
    e=rng.uniform(0.3,1.0)/np.sqrt(2*n); tt=rng.uniform(1.05,1.6)
    for b in range(n):
        A[5+b,[0,1,2]]=[nu*tt,e,-e*(c/c)]; A[5+b,5+b]=1.0
    R=gs(A); tried+=1; w=np.abs(R).sum(1)
    if w.max()>2: continue
    if int(np.argmin(np.abs(R[:,0])))!=0: continue
    valid+=1; P=parts(R,0)
    if best is None or P[0]<best[0][0]: best=(P,R)
print('n',n,'d',d,'tried',tried,'valid',valid)
if best:
    P,R=best; print(' min Xi/nu %.4f  exact dF %.6f  c %.3f rho %.3f nu %.5f kappa1 %.3f  Qrows %.3f  F %.4f'%P); np.save('c4_%d.npy'%n,R)
