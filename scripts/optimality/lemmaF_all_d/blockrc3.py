# R = blockdiag(S4 @ U, B) @ expm(eps*C):  U = expm(delta*S) reshapes the flat row (order sqrt(nu)), C mixes in column j (order nu).
import numpy as np, sys
from scipy.linalg import expm
rng=np.random.default_rng(int(sys.argv[2])); b=int(sys.argv[1]); d=4+b; s3=np.sqrt(3); N=int(sys.argv[3])
S4=np.array([[.5,.5,.5,.5],[s3/2,-1/(2*s3),-1/(2*s3),-1/(2*s3)],[0,1/np.sqrt(2),-1/np.sqrt(2),0],[0,1/np.sqrt(6),1/np.sqrt(6),-2/np.sqrt(6)]])
def F(R,j=0): w=np.abs(R).sum(1); return (np.abs(R[:,j])*(2-w)).sum()
Bs=[]
while len(Bs)<30:
    Bm=np.linalg.qr(rng.normal(size=(b,b)))[0]; Bm=Bm*np.sign(Bm[:,[0]]); wb=np.abs(Bm).sum(1)
    if wb.max()<=1.97 and (wb-np.abs(Bm[:,0])>1.03).all() and np.abs(Bm[:,0]).sum()>2.0: Bs.append(Bm)
res=[]; keep=None
for t in range(N):
    Bm=Bs[t%len(Bs)]
    Sk=rng.normal(size=(4,4)); Sk=Sk-Sk.T; delta=10**rng.uniform(-2.5,-0.7); U=expm(delta*Sk)
    R1=np.zeros((d,d)); R1[np.ix_(range(4),[1,2,3,4])]=S4@U; R1[np.ix_(range(4,d),[0]+list(range(5,d)))]=Bm
    C=np.zeros((d,d)); C[0,1:5]=rng.normal(size=4); C[0,5:]=rng.normal(size=b-1)*rng.uniform(0,1); C=C-C.T
    Cm=rng.normal(size=(d,d))*rng.uniform(0,0.3); C=C+(Cm-Cm.T)
    eps=delta**2*10**rng.uniform(-1.5,0.3)
    R=R1@expm(eps*C); w=np.abs(R).sum(1)
    if w.max()>2: continue
    x=np.abs(R[:,0])
    if int(np.argmin(x))!=0: continue
    rest=w-x
    if (rest<=1).any() or x.sum()<=2: continue
    Rn=R*np.sign(R[:,[0]]); ab=np.abs(Rn[0]).copy(); ab[0]=-1; q=int(np.argmax(ab))
    Rn[:,q]*=np.sign(Rn[0,q]); c=Rn[0,q]; nu=Rn[0,0]
    oth=list(range(1,d)); z=Rn[oth,q]; y=Rn[oth,0]; G=2-w[oth]; L=w[0]-c; a=1/(1+c); k1=1+c-(L-nu)
    if L>1+c: continue
    Xi=nu*(c*(c+L)-1)+(2*k1*np.maximum(z,0)*(y-a*nu*z)-nu*z*G).sum()
    r=np.delete(Rn[0],q); xt=np.delete(Rn[:,q],0); M=np.delete(np.delete(Rn,0,0),q,1); Q=M-np.outer(xt,r)/(1+c)
    if np.abs(Q).sum(1).max()>2: continue
    res.append((Xi/nu,(F(Q)-F(R))/nu,nu,c,q,k1,F(R)))
    if keep is None or Xi/nu<keep[0]: keep=(Xi/nu,R)
res=np.array(res); np.set_printoptions(precision=4,suppress=True)
print('b',b,'d',d,'valid',len(res))
if len(res):
    o=np.argsort(res[:,0]); print(' min Xi/nu',res[o[0],0],' frac<0',(res[:,0]<0).mean(),' min dF/nu',res[:,1].min()); print(res[o[:6]])
    np.save('blockrc3_%d.npy'%b,keep[1])
