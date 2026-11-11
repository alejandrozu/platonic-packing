# Adversarial search for Xi < 0 inside the remaining case RC: rows <= 2, every row with x_i > 0 has rest_i > 1, S > 2.
# Pivot: p = argmin |col 0|, q = argmax |row p| (off col 0).  Minimise Xi/nu (and record exact dF).
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); iu=np.triu_indices(d,1)
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def info(R):
    w=np.abs(R).sum(1); x=np.abs(R[:,0]); p=int(np.argmin(x)); Rn=R*np.sign(R[:,[0]]+1e-300)
    ab=np.abs(Rn[p]).copy(); ab[0]=-1; q=int(np.argmax(ab)); Rn=Rn.copy(); Rn[:,q]*=np.sign(Rn[p,q]); c=Rn[p,q]; nu=max(Rn[p,0],1e-12)
    oth=[i for i in range(d) if i!=p]; z=Rn[oth,q]; y=Rn[oth,0]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(Rn[p],q); xt=np.delete(Rn[:,q],p); M=np.delete(np.delete(Rn,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    rest=w-x
    rcv=np.maximum(1-rest,0).sum()+max(2-x.sum(),0)        # RC violation
    return Xi/nu, F(Q)-F(R), rcv, np.maximum(w-2,0).sum(), nu, c, L-nu, F(R)
best=None
for t in range(trials):
    if t%3==0: R0=np.linalg.qr(rng.normal(size=(d,d)))[0]
    elif t%3==1:
        col=np.abs(rng.normal(size=d))+0.3; col/=np.linalg.norm(col); R0=np.linalg.qr(np.column_stack([col,rng.normal(size=(d,d-1))]))[0]
    else:
        # flat-ish pivot row seed
        R0=np.linalg.qr(rng.normal(size=(d,d)))[0]; v=np.zeros(d); v[1:5]=0.5; v[0]=0.02; v/=np.linalg.norm(v)
        B=np.linalg.qr(np.column_stack([v,rng.normal(size=(d,d-1))]))[0]; R0=B.T
    def obj(vv,m):
        A=np.zeros((d,d)); A[iu]=vv; A=A-A.T; R=R0@expm(A); I=info(R); return I[0]+m*(I[2]+I[3])
    vv=rng.normal(size=len(iu[0]))*0.05
    for m in (3,30,300,3000):
        vv=minimize(obj,vv,args=(m,),method='L-BFGS-B',options={'maxiter':2000}).x
    A=np.zeros((d,d)); A[iu]=vv; A=A-A.T; R=R0@expm(A); I=info(R)
    if I[2]<1e-9 and I[3]<1e-9 and (best is None or I[0]<best[0][0]): best=(I,R); print('  t',t,'Xi/nu %.4f dF %.5f nu %.4f c %.3f rho %.3f F %.4f'%(I[0],I[1],I[4],I[5],I[6],I[7]),flush=True)
print(d,'RC: min Xi/nu',best[0][0] if best else None)
if best: np.save('rcattack_%d.npy'%d,best[1])
