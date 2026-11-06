from fractions import Fraction as F
from math import isqrt
from functools import lru_cache
@lru_cache(None)
def enclosure(d):
 den=10**d; lo=F(isqrt(isqrt(2*den**4)),den);return lo,lo+F(1,den)
class K:
 def __init__(self,x=0):self.c=x.c if isinstance(x,K) else tuple(F(a)for a in x) if isinstance(x,(list,tuple)) else (F(x),F(0),F(0),F(0))
 def __add__(self,o):o=K(o);return K(tuple(a+b for a,b in zip(self.c,o.c)))
 __radd__=__add__
 def __neg__(self):return K(tuple(-a for a in self.c))
 def __sub__(self,o):return self+-K(o)
 def __rsub__(self,o):return K(o)+-self
 def __mul__(self,o):
  o=K(o);v=[F(0)]*7
  for i,a in enumerate(self.c):
   for j,b in enumerate(o.c):v[i+j]+=a*b
  for i in range(6,3,-1):v[i-4]+=2*v[i]
  return K(v[:4])
 __rmul__=__mul__
 def inverse(self):
  if not any(self.c):raise ZeroDivisionError
  mat=[]
  cols=[self*K([int(i==j)for i in range(4)])for j in range(4)]
  for i in range(4):mat.append([c.c[i]for c in cols]+[F(int(i==0))])
  for j in range(4):
   p=next(i for i in range(j,4)if mat[i][j]);mat[j],mat[p]=mat[p],mat[j];v=mat[j][j];mat[j]=[x/v for x in mat[j]]
   for i in range(4):
    if i!=j:
     v=mat[i][j];mat[i]=[x-v*y for x,y in zip(mat[i],mat[j])]
  return K([r[-1]for r in mat])
 def __truediv__(self,o):
  o=K(o)
  if not any(o.c[1:]):return K(tuple(a/o.c[0]for a in self.c))
  return self*o.inverse()
 def __float__(self):return sum(float(a)*2**(i/4)for i,a in enumerate(self.c))
 def sign(self):
  if not any(self.c):return 0
  for d in [20,40,80,160,320,640]:
   lo,hi=enclosure(d);vl=vh=self.c[3]
   for a in self.c[2::-1]:
    corners=[vl*lo,vl*hi,vh*lo,vh*hi];vl=min(corners)+a;vh=max(corners)+a
   if vl>0:return 1
   if vh<0:return -1
  raise ValueError('Unresolved algebraic sign')
 def out(self):return [str(c)for c in self.c]
z=K();one=K(1);alpha=K([0,1,0,0]);r=alpha*alpha/2;h=alpha*alpha*alpha/2

def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def scale(a,t):return [x*t for x in a]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),z)
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def mv(m,x):return [dot(a,x)for a in m]
def transpose(m):return list(map(list,zip(*m)))
def mm(m,n):return [[dot(a,b)for b in transpose(n)]for a in m]
def maxk(v):
 q=v[0]
 for x in v[1:]:
  if (x-q).sign()>0:q=x
 return q
P=[[r,z,h/2],[-r,z,h/2],[z,r,h/2],[z,-r,h/2]]+[[K(x)/2,K(y)/2,-h/2]for x in [-1,1]for y in [-1,1]]
faces=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
U=[];B=[]
for f in faces:
 p=P[f[0]];n=cross(sub(P[f[1]],p),sub(P[f[2]],p))
 if dot(n,p).sign()<0:n=scale(n,-1)
 U.append(n);B.append(dot(n,p))
edges=sorted(set(tuple(sorted((i,j)))for ids in faces for i in ids for j in ids if i<j and (dot(sub(P[i],P[j]),sub(P[i],P[j]))-1).sign()==0))
