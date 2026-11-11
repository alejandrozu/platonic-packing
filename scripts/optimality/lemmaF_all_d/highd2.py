# Try to break the pivot conjecture in high dimension with a designed structure:
# spread pivot row p, many light rows with tiny column-j entries and small positive entries in column q.
import numpy as np, sys
from scipy.linalg import polar
from scipy.optimize import minimize
d=int(sys.argv[1]); trials=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def parts(R):
    w=np.abs(R).sum(1); R=R*np.sign(R[:,[0]]+1e-300); x=R[:,0]; p=int(np.argmin(x))
    q=1+int(np.argmax(np.abs(R[p,1:]))); R=R.copy(); R[:,q]*=np.sign(R[p,q]); c=R[p,q]; nu=max(x[p],1e-12)
    oth=[i for i in range(d) if i!=p]; z=R[oth,q]; y=x[oth]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(R[p],q); xt=np.delete(R[:,q],p); M=np.delete(np.delete(R,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    return Xi/nu, F(Q)-F(R), c, L-nu, nu, np.abs(Q).sum(1).max()
def design():
    nu=rng.uniform(0.005,0.05); nL=int(rng.integers(d//3, d-6)); A=np.zeros((d,d))
    c3=rng.uniform(0.45,0.58); A[0,:4]=[nu,0.58,0.58,c3]
    for b in range(nL):
        e=rng.uniform(0.02,0.12); A[1+b,[0,1,2,4+b]]=[nu*rng.uniform(1.0,1.3),e,-e,1]
    free=list(range(4+nL,d)); rest=list(range(1+nL,d))
    for k,i in enumerate(rest):
        A[i,0]=rng.uniform(0.3,1.0); A[i,[1,2,3]]=rng.normal(size=3)*0.4
        if free: A[i,free[k%len(free)]]=1.0
    return A+rng.normal(size=(d,d))*0.005
best=(9,None,None)
for t in range(trials):
    A0=design()
    def obj(a,m):
        R=polar(a.reshape(d,d))[0]; w=np.abs(R).sum(1); P=parts(R)
        return P[0]+m*(np.maximum(w-2,0).sum()+max(P[5]-2,0)+max(P[2]+0.3-P[3],0))
    a=A0.ravel()
    for m in (3,30,300):
        a=minimize(obj,a,args=(m,),method='L-BFGS-B',options={'maxiter':800}).x
    R=polar(a.reshape(d,d))[0]
    if np.abs(R).sum(1).max()<=2+1e-7 and parts(R)[3]>=parts(R)[2]+0.3-1e-6:
        P=parts(R)
        if P[0]<best[0]: best=(P[0],P,R); print(' t',t,'Xi/nu',round(P[0],4),'exact dF',round(P[1],6),'c,rho,nu',np.round(P[2:5],3),flush=True)
print(d,'min Xi/nu',best[0])
if best[2] is not None: np.save('highd_best_%d.npy'%d,best[2])
