# d = 5 + n. Columns 0=j, 1=q, 2..4 = other big entries of row p, 5.. = axes of light rows.
import numpy as np, sys
from scipy.linalg import polar, expm
rng=np.random.default_rng(int(sys.argv[2])); n=int(sys.argv[1]); d=5+n
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def parts(R,p):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]
    q=1+int(np.argmax(np.abs(R[p,1:]))); R=R.copy(); R[:,q]*=np.sign(R[p,q]); c=R[p,q]; nu=max(x[p],1e-12)
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; y=x[oth]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    br=np.where(z>0,2*k1*(y-a*nu*z)-nu*G,0)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    return Xi/nu, F(Q)-F(R), c, L-nu, nu, k1, (br/nu).min(), np.abs(Q).sum(1).max()
best=None; cnt=0; ok=0
for t in range(int(sys.argv[3])):
    nu=rng.uniform(0.002,0.05)
    v=np.sort(rng.uniform(0.25,0.62,4))[::-1]; v=v/np.linalg.norm(v)*np.sqrt(1-nu*nu)
    if v[0]>0.7 or nu+v.sum()>1.99: continue
    pr=np.concatenate([[nu],v])
    B=np.linalg.qr(np.column_stack([pr,rng.normal(size=(5,4))]))[0][:,1:]
    H=(B@expm((lambda S:S-S.T)(rng.normal(size=(4,4))*2))).T
    if (np.abs(H).sum(1)>1.95).any(): continue
    H=H*np.sign(H[:,[0]]+1e-300)
    if (H[:,0]<3*nu).any(): continue
    A=np.zeros((d,d)); A[0,:5]=pr; A[n+1:,:5]=H
    for b in range(n):
        e=rng.uniform(0.0,0.2); tt=rng.uniform(1.15,1.6)
        dl=(nu*nu*tt+v[0]*e)/v[1]
        A[1+b,[0,1,2]]=[nu*tt,e,-dl]; A[1+b,5+b]=np.sqrt(max(1-(nu*tt)**2-e*e-dl*dl,0.01))
    Qm,Rm=np.linalg.qr(A.T); R=(Qm*np.sign(np.diag(Rm))).T; w=np.abs(R).sum(1); cnt+=1
    if w.max()>2: continue
    x=np.abs(R[:,0])
    if int(np.argmin(x))!=0: continue
    ok+=1; P=parts(R,0)
    if best is None or P[0]<best[0][0]: best=(P,R)
print('n',n,'d',d,'tried',cnt,'valid with argmin=p',ok)
if best:
    P,R=best; print(' min Xi/nu %.4f  exact dF %.6f  c %.3f rho %.3f nu %.4f kappa1 %.3f  min bracket/nu %.3f  Qrows %.3f'%P)
    np.save('construct2_best_%d.npy'%n,R)
