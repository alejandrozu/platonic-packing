"""Independent exact rational-function audit of the N6 native decoder.

Reconstructs from the vertex geometry and certificate coefficient lists;
imports none of the exploratory derivation or numerical root code.
"""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as F
from math import isqrt
import sympy as s,json,hashlib,itertools
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'certificate.json').read_text())
a=s.real_root(2,4);t,u=s.symbols('t u');K=s.QQ.algebraic_field(a).frac_field(t,u);T0,U0=K.gens
def constant_sign(v):
    """Exact rational enclosure sign for a constant element of Q(a)."""
    base=s.QQ.algebraic_field(a);cs=list(reversed(base.from_sympy(K.to_sympy(v)).to_list()))
    d=10**100;j=isqrt(isqrt(2*d**4));al,ah=F(j,d),F(j+1,d)
    lo=hi=F(0)
    for c in cs[::-1]:
        vals=[lo*al,lo*ah,hi*al,hi*ah];c=F(int(c.numerator),int(c.denominator));lo,hi=min(vals)+c,max(vals)+c
    assert lo>0 or hi<0
    return 1 if lo>0 else -1
@lru_cache(None)
def coeff(c):return K.from_sympy(sum(s.Rational(z)*a**i for i,z in enumerate(c)))
def poly(p):return sum((coeff(tuple(q['coefficients']))*T0**q['powers'][0]*U0**q['powers'][1]for q in p),K.zero)
def rational(q):return poly(q['numerator'])/poly(q['denominator'])
def dot(x,y):return sum((v*w for v,w in zip(x,y)),K.zero)
def add(x,y):return [v+w for v,w in zip(x,y)]
def sub(x,y):return [v-w for v,w in zip(x,y)]
def cross(x,y):return [x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
def mv(M,v):return [dot(row,v)for row in M]
def mm(M,N):return [[dot(row,col)for col in zip(*N)]for row in M]
def transpose(M):return list(map(list,zip(*M)))
Z=K.zero;O=K.one;A=coeff(('0','1','0','0'));H=A**3/2;R=A**2/2
P=[[R,Z,H/2],[-R,Z,H/2],[Z,R,H/2],[Z,-R,H/2]]+[[K.convert(x)/2,K.convert(y)/2,-H/2]for x,y in itertools.product([-1,1],repeat=2)]
I=[[K.convert(int(i==j))for j in range(3)]for i in range(3)]
B0=[[-R,R,Z],[R,R,Z],[Z,Z,-O]];B1=[[-O,Z,Z],[Z,-O,Z],[Z,Z,O]];T=[[R,-R,Z],[-R,-R,Z],[Z,Z,-O]]
n0=[H,Z,(1-A**2)/2];n1=[A/2,A/2,(A**2-1)/2]
def rot(n,k):
 sk=[[Z,-n[2],n[1]],[n[2],Z,-n[0]],[-n[1],n[0],Z]]
 return [[((1-K.convert(s.Rational(3,4))*k*k)*int(i==j)+2*k*k*n[i]*n[j]+2*k*sk[i][j])/(1+K.convert(s.Rational(3,4))*k*k)for j in range(3)]for i in range(3)]
M0=mm(rot(n0,T0),B0);M1=mm(rot(n1,U0),B1);M=[M0,M1,I,T,mm(T,M1),mm(T,M0)]
for ii,m in enumerate([B0,B1,T,M0,M1]):
 assert all(mm(m,transpose(m))[i][j]-I[i][j]==0 for i in range(3)for j in range(3))
 assert dot(m[0],cross(m[1],m[2]))-1==0
for b in [B0,B1,T]:assert all(any(all(v[k]-q[k]==0 for k in range(3))for q in P)for v in [mv(b,p)for p in P])
V=[[mv(m,p)for p in P]for m in M]
S=rational(D['solution_functions']['S']);x=rational(D['solution_functions']['x']);y=rational(D['solution_functions']['y'])
z0=-S*H/2-V[0][1][2];x0=((S-1)*dot(n0,P[0])-n0[2]*z0)/n0[0]
z1=S*H/2-V[1][1][2];y1=((S-1)*dot(n1,P[0])-n1[2]*z1)/n1[1]-x
C0=[x0,y,z0];C1=[x,y1,z1];C2=[-(S-1)/2,(S-1)/2,-(S-1)*H/2];C=[C0,C1,C2,mv(T,C2),mv(T,C1),mv(T,C0)]
faces=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
Normals=[];Bs=[]
for f in faces:
 n=cross(sub(P[f[1]],P[f[0]]),sub(P[f[2]],P[f[0]]))
 # Constants only; choosing outward sign does not use approximate arithmetic.
 if constant_sign(dot(n,P[f[0]]))<0:n=[-z for z in n]
 Normals.append(n);Bs.append(dot(n,P[f[0]]))
wallzero={0:{6:[1,2,5],9:[1]},1:{5:[1,3,4],8:[1]},2:{1:[1,4,5],4:[1,2,5],7:[2,5,7],9:[4,5,6,7]},3:{0:[2,5,7],1:[1,2,5],4:[1,4,5],8:[4,5,6,7]},4:{3:[1,3,4],9:[1]},5:{2:[1,2,5],8:[1]}}
wc=0
for i,fs in wallzero.items():
 for f,vs in fs.items():
  for v in vs:assert S*Bs[f]-dot(Normals[f],add(C[i],V[i][v]))==0;wc+=1
bases=[(0,1,mv(M1,[Z,Z,O]),[7],[4,5,6,7]),(0,2,cross(sub(V[0][6],V[0][0]),sub(P[6],P[0])),[0,6],[0,6]),(0,4,cross(sub(V[0][6],V[0][3]),sub(V[4][5],V[4][2])),[3,6],[2,5]),(1,2,cross(sub(V[1][7],V[1][6]),sub(P[2],P[0])),[6,7],[0,2]),(1,3,cross(sub(V[1][7],V[1][0]),sub(V[3][6],V[3][3])),[0,7],[3,6])]
contact_res=[];ties=0;divisibility=[]
for idx,(i,j,n,aa,bb)in enumerate(bases):
 g=dot(n,sub(add(C[j],V[j][bb[0]]),add(C[i],V[i][aa[0]])))
 for av,bv in itertools.product(aa,bb):
  assert dot(n,sub(add(C[j],V[j][bv]),add(C[i],V[i][av])))-g==0;ties+=1
 if idx in [1,3,4]:assert g==0;divisibility.append('identically zero')
 else:
  f=poly(D['equations'][0 if idx==0 else 1]);q,r=divmod(g.numer,f.numer);assert not r
  assert q;divisibility.append('numerator exactly divisible by defining polynomial')
print('AUDIT_COMPLETE',flush=True)
receipt={'status':'PASS_INDEPENDENT_EXACT_RATIONAL_FUNCTION_DECODER','structural_wall_equalities':wc,'base_pair_feature_ties':ties,'base_contact_implications':divisibility,'proper_rotations_symbolically_verified':5,'body_symmetry_vertex_sets_verified':3,'certificate_sha256':hashlib.sha256((HERE/'certificate.json').read_bytes()).hexdigest(),'method':'Native geometry reconstructed over Q(2^(1/4))(t,u); all structural zeros exact; three base contact gaps identically zero and two exactly divisible by defining polynomials.'}
print(json.dumps(receipt,indent=2))
