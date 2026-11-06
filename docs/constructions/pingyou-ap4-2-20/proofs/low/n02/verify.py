"""Independent stdlib full-body reconstruction in Q(t), t^4=1-2t^2."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
D=Path(__file__).parent;src=D/'endpoint.json';d=json.loads(src.read_text())
lo,hi=map(F,d['root_interval']);assert lo>0 and lo**4+2*lo**2<1<hi**4+2*hi**2
def q(x):return x if isinstance(x,tuple)else(F(x),F(0),F(0),F(0))
def add(x,y):return tuple(a+b for a,b in zip(q(x),q(y)))
def neg(x):return tuple(-a for a in q(x))
def sub(x,y):return add(x,neg(y))
def mul(x,y):
 z=[F(0)]*7
 for i,a in enumerate(q(x)):
  for j,b in enumerate(q(y)):z[i+j]+=a*b
 for k in range(6,3,-1):z[k-4]+=z[k];z[k-2]-=2*z[k]
 return tuple(z[:4])
def div(x,y):return tuple(a/F(y)for a in q(x))
def sign(x):
 x=q(x)
 if not any(x):return 0
 a=b=F(0)
 for c in reversed(x):
  z=[a*lo,a*hi,b*lo,b*hi];a=min(z)+c;b=max(z)+c
 assert a>0 or b<0
 return 1 if a>0 else -1
def dot(x,y):
 z=q(0)
 for a,b in zip(x,y):z=add(z,mul(a,b))
 return z
def mv(A,x):return tuple(dot(r,x)for r in A)
def transpose(A):return list(zip(*A))
def mm(A,B):return [[dot(row,col)for col in transpose(B)]for row in A]
def scale(v,a):return mul(v,a)
t=(F(0),F(1),F(0),F(0));t2=mul(t,t);t3=mul(t2,t);one=q(1);zero=q(0);r=div(add(one,t2),2);invt=add(t3,scale(t,2))
A=[[div(t2,2),div(t,2),div(invt,2)],[q(F(1,2)),div(invt,2),div(neg(t),2)],[q(-1),t,zero]]
G=[[r if i==j==2 else one if i==j else zero for j in range(3)]for i in range(3)]
assert mm(mm(transpose(A),G),A)==G
det=add(sub(mul(A[0][0],sub(mul(A[1][1],A[2][2]),mul(A[1][2],A[2][1]))),mul(A[0][1],sub(mul(A[1][0],A[2][2]),mul(A[1][2],A[2][0])))),mul(A[0][2],sub(mul(A[1][0],A[2][1]),mul(A[1][1],A[2][0]))));assert det==one
C=[div(sub(sub(scale(t3,3),t2),scale(t,3)),4),div(sub(add(neg(t3),scale(t,3)),one),4),div(add(sub(t3,scale(t,2)),one),2)];S=sub(scale(t,3),t3);assert sign(S)>0
assert mul(S,S)==sub(scale(add(one,t2),26),34)
assert [list(map(str,c))for c in C]==d['center0']
P=[(r,zero,q(F(1,2))),(neg(r),zero,q(F(1,2))),(zero,r,q(F(1,2))),(zero,neg(r),q(F(1,2)))]+[(q(F(x,2)),q(F(y,2)),q(F(-1,2)))for x in[-1,1]for y in[-1,1]]
T=[[q(-1),zero,zero],[zero,q(-1),zero],[zero,zero,one]]
# Same proper host half-turn applied to the whole second owner.
CC=[C,mv(T,C)];frames=[A,mm(T,A)];V=[[tuple(add(c,x)for c,x in zip(CC[i],mv(frames[i],v)))for v in P]for i in range(2)]
b=div(t2,2);aa=div(add(t2,2),4);cc=mul(t2,r);dd=div(mul(add(t2,2),r),2)
W=[(zero,zero,one),(zero,zero,q(-1))]+[(q(x),zero,neg(b))for x in[-1,1]]+[(zero,q(y),neg(b))for y in[-1,1]]+[(q(x),q(y),cc)for x in[-1,1]for y in[-1,1]];B=[q(F(1,2))]*2+[aa]*4+[dd]*4
# First verify the proposed host halfspaces against the actual canonical vertices.
for n,h in zip(W,B):
 gaps=[sub(h,dot(n,v))for v in P];assert all(sign(g)>=0 for g in gaps);assert any(sign(g)==0 for g in gaps)
wc=pc=0
for vs in V:
 for v in vs:
  for n,h in zip(W,B):assert sign(sub(mul(S,h),dot(n,v)))>=0;wc+=1
n=(div(invt,2),div(neg(t),2),zero)
for v in V[0]:
 for w in V[1]:assert sign(dot(n,tuple(sub(b,a)for a,b in zip(v,w))))>=0;pc+=1
out={'status':'PASS_INDEPENDENT_STD_LIB_EXACT_N2','scale':'sqrt(26sqrt(2)-34)','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'host_vertex_inequalities':wc,'pair_vertex_inequalities':pc,'proper_physical_rotations':2,'method':'independent degree-four field arithmetic; reconstructed full vertices, normalized-metric rotation, host halfspaces, and separator'}
print(json.dumps(out,indent=2))
