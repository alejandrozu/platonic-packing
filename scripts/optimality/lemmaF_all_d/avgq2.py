# Decompose  sum_V c_q Xi_q / nu = S1 + S2 + S3 + S4 :
#  S1 = nu(1-nu w_p) + nu sum_i y_i G_i ,  S2 = sum_small c_q (1 - c_q w_p),
#  S3 = sum_small R_pq sum_{i!=p} R_iq G_i (cross term),  S4 = K_V/nu >= 0
import numpy as np, sys
from scipy.linalg import expm
d=int(sys.argv[1]); N=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
rows=[]
for t in range(N):
    A=rng.normal(size=(d,d))*rng.uniform(0.02,0.9); A=A-A.T
    R=np.eye(d)[rng.permutation(d)]@np.diag(rng.choice([-1,1],d))@expm(A)
    if rng.random()<0.3: R=np.linalg.qr(rng.normal(size=(d,d)))[0]
    w=np.abs(R).sum(1)
    if w.max()>2: continue
    R=R*np.sign(R[:,[0]]+1e-300); p=int(np.argmin(R[:,0])); nu=R[p,0]
    if nu<1e-6: continue
    oth=[i for i in range(d) if i!=p]; G=2-w; y=R[oth,0]
    thr=(w[p]-1)/2
    V=[q for q in range(1,d) if abs(R[p,q])>=thr]; Sm=[q for q in range(1,d) if 0<abs(R[p,q])<thr]
    S1=nu*(1-nu*w[p])+nu*(y*G[oth]).sum()
    S2=sum(abs(R[p,q])*(1-abs(R[p,q])*w[p]) for q in Sm)
    S3=sum(R[p,q]*(R[oth,q]*G[oth]).sum() for q in Sm)
    S4=0
    for q in V:
        c=abs(R[p,q]); z=R[oth,q]*np.sign(R[p,q]); a=1/(1+c); k1=1+2*c+nu-w[p]
        S4+=c*2*k1*(np.maximum(z,0)*(y/nu-a*z)).sum()
    rows.append((S1,S2,S3,S4,S1+S2+S3+S4, sum(abs(R[p,q]) for q in Sm), w[p]))
rows=np.array(rows); np.set_printoptions(precision=4,suppress=True,linewidth=160)
print(d,len(rows),'min total',rows[:,4].min(),' min S3',rows[:,3-1].min(),' frac S3<0',(rows[:,2]<0).mean())
o=np.argsort(rows[:,4]); print(' worst (S1,S2,S3,S4,tot,|small|_1,w_p):'); print(rows[o[:5]])
r=rows[:,2]/(rows[:,0]+rows[:,1]+1e-12); print(' min S3/(S1+S2)',r.min())
t3=rows[:,0]+rows[:,1]+rows[:,2]; o=np.argsort(t3)
print(' min S1+S2+S3 =',t3.min(),' frac<0',(t3<0).mean()); print(rows[o[:6]])
