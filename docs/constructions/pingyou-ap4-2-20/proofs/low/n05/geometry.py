from fractions import Fraction as F
import itertools
from quartic import Q4 as K,ALPHA,ZERO,ONE,dot,cross
H=ALPHA**3/2;R=ALPHA**2/2
P=[[R,ZERO,H/2],[-R,ZERO,H/2],[ZERO,R,H/2],[ZERO,-R,H/2]]+[[K(x)/2,K(y)/2,-H/2]for x,y in itertools.product([-1,1],repeat=2)]
faces=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
U=[];B=[]
for f in faces:
 p=P[f[0]];u=cross([P[f[1]][k]-p[k]for k in range(3)],[P[f[2]][k]-p[k]for k in range(3)])
 if dot(u,p).sign()<0:u=[-z for z in u]
 U.append(u);B.append(dot(u,p))
ED=sorted(set(tuple(sorted((i,j)))for f in faces for i,j in itertools.combinations(f,2)if (dot([P[i][k]-P[j][k]for k in range(3)],[P[i][k]-P[j][k]for k in range(3)])-1).sign()==0))
def matvec(m,v):return [dot(r,v)for r in m]

def solveK(A,b):
    z=[list(row)+[v] for row,v in zip(A,b)]
    for j in range(len(b)):
        i=next(i for i in range(j,len(b)) if z[i][j].sign())
        z[j],z[i]=z[i],z[j];p=z[j][j];z[j]=[v/p for v in z[j]]
        for i in range(len(b)):
            if i!=j:
                p=z[i][j];z[i]=[a-p*v for a,v in zip(z[i],z[j])]
    return [row[-1] for row in z]
