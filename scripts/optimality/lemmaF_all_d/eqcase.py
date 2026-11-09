import numpy as np, sys
from scipy.linalg import expm
rng=np.random.default_rng(int(sys.argv[1])); s3=np.sqrt(3)
R0=np.array([[0,.5,.5,.5,.5],[0,s3/2,-1/(2*s3),-1/(2*s3),-1/(2*s3)],[1,0,0,0,0],
             [0,0,1/np.sqrt(2),-1/np.sqrt(2),0],[0,0,1/np.sqrt(6),1/np.sqrt(6),-2/np.sqrt(6)]])
d=5; print('orth err',np.abs(R0@R0.T-np.eye(5)).max(),' rows',np.abs(R0).sum(1))
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def piv(R,p,q):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]
    R=R.copy(); R[:,q]*=np.sign(R[p,q]); c=R[p,q]; nu=x[p]
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; y=x[oth]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    return Xi, F(Q)-F(R), nu, c, k1, np.abs(Q).sum(1).max(), L<=1+c
res=[]
for t in range(200000):
    eps=10**rng.uniform(-4,-1.3); A=rng.normal(size=(d,d)); A=A-A.T
    R=R0@expm(eps*A)
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    x=np.abs(R[:,0]); p=int(np.argmin(x))
    others=[k for k in range(1,d)]
    mx=np.abs(R[p,1:]).max(); qs=[k for k in others if abs(abs(R[p,k])-mx)<1e-15]
    q=qs[0]
    Xi,dF,nu,c,k1,qr,valid=piv(R,p,q)
    res.append((Xi/nu,dF/nu,nu,c,k1,p,F(R),valid,qr))
res=np.array(res); np.set_printoptions(precision=4,suppress=True,linewidth=160)
print('samples',len(res),' min Xi/nu',res[:,0].min(),' min dF/nu',res[:,1].min(),' frac Xi<0',(res[:,0]<0).mean(),' frac dF<0',(res[:,1]<0).mean())
o=np.argsort(res[:,0]); print(' worst Xi (Xi/nu,dF/nu,nu,c,k1,p,F,valid,Qrows):'); print(res[o[:6]])
o=np.argsort(res[:,1]); print(' worst dF:'); print(res[o[:6]])
