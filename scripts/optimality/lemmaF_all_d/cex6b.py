# Find a clean counterexample to PivotConj (Xi < 0) near the 5D equality case, and a 6D one; verify carefully.
import numpy as np, sys
from scipy.linalg import expm
from scipy.optimize import minimize
rng=np.random.default_rng(int(sys.argv[2])); d=int(sys.argv[1]); s3=np.sqrt(3)
R5=np.array([[0,.5,.5,.5,.5],[0,s3/2,-1/(2*s3),-1/(2*s3),-1/(2*s3)],[1,0,0,0,0],
             [0,0,1/np.sqrt(2),-1/np.sqrt(2),0],[0,0,1/np.sqrt(6),1/np.sqrt(6),-2/np.sqrt(6)]])
R0=np.eye(d); R0[:5,:5]=R5
if d>5:
    th=0.0; G=np.eye(d); G[2,2]=np.cos(th); G[2,5]=-np.sin(th); G[5,2]=np.sin(th); G[5,5]=np.cos(th); R0=G@R0
iu=np.triu_indices(d,1)
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
def info(R):
    w=np.abs(R).sum(1); x=np.abs(R[:,0]); p=0; gap=np.delete(x,0).min()-x[0]
    Rn=R*np.sign(R[:,[0]]+1e-300); ab=np.abs(Rn[p]); ab0=ab.copy(); ab0[0]=-1; q=int(np.argmax(ab0))
    s2=np.sort(ab0)[::-1]; qgap=s2[0]-s2[1]
    Rn=Rn.copy(); Rn[:,q]*=np.sign(Rn[p,q]); c=Rn[p,q]; nu=Rn[p,0]
    oth=[i for i in range(d) if i!=p]; z=Rn[oth,q]; y=Rn[oth,0]; G=2-w[oth]; L=w[p]-c; a=1/(1+c); k1=1+c-(L-nu)
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(Rn[p],q); xt=np.delete(Rn[:,q],p); M=np.delete(np.delete(Rn,p,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    return dict(Xi=Xi,Xinu=Xi/nu,dF=F(Q)-F(R),nu=nu,c=c,p=p,q=q,gap=gap,qgap=qgap,valid=L<=1+c,Qrows=np.abs(Q).sum(1).max(),rows=w.max(),F=F(R),orth=np.abs(R@R.T-np.eye(d)).max())
best=None
for t in range(int(sys.argv[3])):
    A0=rng.normal(size=len(iu[0]))*rng.uniform(0.002,0.03)
    def obj(v,m):
        A=np.zeros((d,d)); A[iu]=v; A=A-A.T; R=R0@expm(A); I=info(R)
        return I['Xinu']+m*(max(I['rows']-2,0)+max(I['Qrows']-2,0)+max(0.003-I['nu'],0)+max(0.002-I['gap'],0)+max(0.002-I['qgap'],0))
    v=A0
    for m in (10,100,1000):
        v=minimize(obj,v,args=(m,),method='Nelder-Mead',options={'maxiter':20000,'xatol':1e-10,'fatol':1e-12}).x
    A=np.zeros((d,d)); A[iu]=v; A=A-A.T; R=R0@expm(A); I=info(R)
    ok=I['rows']<=2 and I['Qrows']<=2 and I['nu']>=0.003 and I['gap']>=0.002 and I['qgap']>=0.002 and I['valid']
    if ok and (best is None or I['Xinu']<best[0]['Xinu']): best=(I,R)
if best:
    I,R=best; np.set_printoptions(precision=6,suppress=True,linewidth=170)
    print(d,{k:(round(v,6) if isinstance(v,float) else v) for k,v in I.items()}); print(R); np.save('cex_%d.npy'%d,R)
else: print(d,'none')
