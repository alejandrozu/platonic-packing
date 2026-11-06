"""Validated Krawczyk isolation of the three-hinge physical contact root.
No decimal recognition; equations decode directly from named body features.
"""
from pathlib import Path
from fractions import Fraction as Q
import json
HERE=Path(__file__).resolve().parent
from geometry import K,P,U,ED,H,R,ALPHA
from flint import arb,arb_mat,fmpq,ctx
ctx.prec=512
D=json.loads((HERE/'root.json').read_text())
RADIUS=Q(1,10**65)
def ball(v):
 if isinstance(v,arb):return v
 if isinstance(v,Q):return arb(fmpq(v.numerator,v.denominator))
 return arb(v)
def ak(v):return sum((ball(Q(x))*arb(2).root(4)**i for i,x in enumerate(v.coeffs)),arb(0))
class A:
 def __init__(self,v=0,g=None):self.v=ball(v);self.g=[arb(0)]*3 if g is None else g
 def __add__(self,b):b=aa(b);return A(self.v+b.v,[x+y for x,y in zip(self.g,b.g)])
 __radd__=__add__
 def __neg__(self):return A(-self.v,[-x for x in self.g])
 def __sub__(self,b):return self+-aa(b)
 def __rsub__(self,b):return aa(b)+-self
 def __mul__(self,b):b=aa(b);return A(self.v*b.v,[x*b.v+self.v*y for x,y in zip(self.g,b.g)])
 __rmul__=__mul__
 def __truediv__(self,b):b=aa(b);return A(self.v/b.v,[(x*b.v-self.v*y)/(b.v*b.v)for x,y in zip(self.g,b.g)])
def aa(x):return x if isinstance(x,A)else A(x)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),A())
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def mv(M,v):return [dot(row,v)for row in M]
def mm(M,N):return [[dot(row,col)for col in zip(*N)]for row in M]
def invsolve(M,b):
 Z=[row[:]+[z]for row,z in zip(M,b)];n=len(b)
 for k in range(n):
  choices=[i for i in range(k,n)if not Z[i][k].v.contains(0)];assert choices,('interval singular',k)
  j=max(choices,key=lambda i:abs(float(Z[i][k].v.mid())));Z[k],Z[j]=Z[j],Z[k]
  p=Z[k][k];Z[k]=[z/p for z in Z[k]]
  for i in range(n):
   if i==k:continue
   p=Z[i][k];Z[i]=[x-p*y for x,y in zip(Z[i],Z[k])]
 return [row[-1]for row in Z]
PP=[[A(ak(v))for v in p]for p in P];UU=[[A(ak(v))for v in p]for p in U]
k=[-H,K(),R-K(1)/2];sk=[[K(),-k[2],k[1]],[k[2],K(),-k[0]],[-k[1],k[0],K()]]
R0=[[A(ak(K(int(i==j))+sk[i][j]+2*sum((sk[i][k]*sk[k][j]for k in range(3)),K())))for j in range(3)]for i in range(3)]
I=[[A(int(i==j))for j in range(3)]for i in range(3)]
facev=[1,1,0,3,1,0,0,2,0,4]
def frames(t):
 def rot(u,v):
  w=[x*v for x in u];s=dot(w,w);sk=[[A(),-w[2],w[1]],[w[2],A(),-w[0]],[-w[1],w[0],A()]]
  return [[((1-s)*int(i==j)+2*w[i]*w[j]+2*sk[i][j])/(1+s)for j in range(3)]for i in range(3)]
 c=(1-t[2]*t[2])/(1+t[2]*t[2]);s=2*t[2]/(1+t[2]*t[2]);rr=[[c,A(),s],[A(),A(1),A()],[-s,A(),c]]
 return [rot(UU[7],t[0]),I,I,rot(UU[0],t[1]),mm(R0,rr)]
def evaluate(values):
 t=[A(v,[arb(int(i==j))for i in range(3)])for j,v in enumerate(values)];M=frames(t);V=[[mv(R,p)for p in PP]for R in M];N=[[mv(R,u)for u in UU]for R in M];E=[[[v[b][k]-v[a][k]for k in range(3)]for a,b in ED]for v in V]
 rows=[];rhs=[];normals=[]
 for tag,feature in zip(D['active_tags'],D['support_vertices']):
  row=[A()for _ in range(16)]
  if tag[0]=='host':
   _,i,f=tag;u=UU[f]
   for k in range(3):row[3*i+k]=u[k]
   row[15]=-dot(UU[f],PP[facev[f]]);b=-dot(u,V[i][feature[0]])
  else:
   _,i,j,ix,sense=tag
   if ix<10:u=N[i][ix]
   elif ix<20:u=N[j][ix-10]
   else:a,b=divmod(ix-20,len(ED));u=cross(E[i][a],E[j][b])
   u=[sense*x for x in u]
   for k in range(3):row[3*i+k]=u[k];row[3*j+k]=-u[k]
   b=-dot(u,V[i][feature[0]])+dot(u,V[j][feature[1]])
  rows.append(row);rhs.append(b);normals.append(u)
 x=invsolve([rows[i]for i in D['basis_rows']],[rhs[i]for i in D['basis_rows']])
 residual=[dot(a,x)-b for a,b in zip(rows,rhs)]
 return [residual[i]for i in D['three_closure_rows']],x,rows,rhs,V,N,E,normals
mid=[Q(v)for v in D['root']];rad=ball(RADIUS);box=[ball(v)+arb(0,rad)for v in mid]
F0,x0,*_=evaluate([ball(v)for v in mid]);FB,X,*_=evaluate(box)
C=[[ball(Q(x))for x in row]for row in D['preconditioner']]
assert arb_mat(C).det().abs_lower()>0
G=[[arb(int(i==j))-sum((C[i][k]*FB[k].g[j]for k in range(3)),arb(0))for j in range(3)]for i in range(3)]
Kraw=[ball(mid[i])-sum((C[i][k]*F0[k].v for k in range(3)),arb(0))+sum((G[i][j]*arb(0,rad)for j in range(3)),arb(0))for i in range(3)]
assert all((Kraw[i]-ball(mid[i])).abs_upper()<rad for i in range(3))
contraction=max(sum((x.abs_upper()for x in row),arb(0))for row in G)
assert contraction<1
out={'status':'PASS_VALIDATED_THREE_HINGE_ROOT','precision_bits':ctx.prec,'root_box_centers':[str(x)for x in mid],'root_box_radius':str(RADIUS),'preconditioner':D['preconditioner'],'krawczyk_strict_inclusion':True,'jacobian_contraction_bound':str(contraction),'root_unique_in_box':True,'scale_image_ball':str(X[15].v),'equations':'three_closure_rows in root.json; all entries decoded from named AP4 supports and structural hinge rotations.','feasibility_status':'Root isolation only in this receipt; full geometric lift checked separately.'}
print(json.dumps(out,indent=2))

# Whole-body lift: the extra20th contact is an exact facet-row dependency.
from geometry import solveK
wanted=4
assert D['active_tags'][wanted]==['host',1,7]
base_ids=[2,3,5]
ns=[U[D['active_tags'][i][2]]for i in base_ids]
lamb=solveK([list(z)for z in zip(*ns)],U[7])
be=lambda f:sum((U[f][k]*P[facev[f]][k]for k in range(3)),K())
assert sum((a*be(D['active_tags'][i][2])for a,i in zip(lamb,base_ids)),K())==be(7)

_,X,rows,rhs,V,N,E,active_normals=evaluate(box)
def makeaxis(tag,N,E):
 _,i,j,ix,sense=tag
 if ix<10:u=N[i][ix]
 elif ix<20:u=N[j][ix-10]
 else:a,b=divmod(ix-20,len(ED));u=cross(E[i][a],E[j][b])
 return [sense*x for x in u]
ptags={tuple(tag[1:3]):tag for tag in D['pair_tags']}
active={(tag[0],*tag[1:3]):(idx,feat)for idx,(tag,feat)in enumerate(zip(D['active_tags'],D['support_vertices']))}
zero_support=[];strict_lower=[];checks=0
paramowner={0:0,3:1,4:2}

def exactframes(t):
 def rot(u,v):
  w=[v*x for x in u];x,y,z=w;n=sum((a*a for a in w),K());sk=[[K(),-z,y],[z,K(),-x],[-y,x,K()]]
  return [[((1-n)*int(i==j)+2*w[i]*w[j]+2*sk[i][j])/(1+n)for j in range(3)]for i in range(3)]
 kk=[-H,K(),R-K(1)/2];ss=[[K(),-kk[2],kk[1]],[kk[2],K(),-kk[0]],[-kk[1],kk[0],K()]]
 base=[[K(int(i==j))+ss[i][j]+2*sum((ss[i][k]*ss[k][j]for k in range(3)),K())for j in range(3)]for i in range(3)]
 eye=[[K(int(i==j))for j in range(3)]for i in range(3)]
 c=(1-t[2]*t[2])/(1+t[2]*t[2]);s=2*t[2]/(1+t[2]*t[2]);ry=[[c,K(),s],[K(),K(1),K()],[-s,K(),c]]
 def kmul(A,B):return [[sum((A[i][k]*B[k][j]for k in range(3)),K())for j in range(3)]for i in range(3)]
 return [rot(U[7],t[0]),eye,eye,rot(U[0],t[1]),kmul(base,ry)]
def kmv(A,v):return [sum((x*y for x,y in zip(row,v)),K())for row in A]
def kdot(a,b):return sum((x*y for x,y in zip(a,b)),K())
def kcross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
from functools import lru_cache
from itertools import product
@lru_cache(None)
def exact_geometry(tup):
 ts=[K(t)for t in tup];M=exactframes(ts);v=[[kmv(m,p)for p in P]for m in M];ns=[[kmv(m,u)for u in U]for m in M];es=[[[a[b][k]-a[c][k]for k in range(3)]for c,b in ED]for a in v]
 return v,ns,es

def identity(desc):
 if desc[0]=='host':
  _,i,f,chosen,j=desc;params=[paramowner[i]]if i in paramowner else[]
 else:
  _,tag,side,chosen,j=desc;params=sorted({paramowner[b]for b in tag[1:3]if b in paramowner})
 # Each rotation numerator and denominator has degree<=2 in its one
 # parameter. Face/cross-edge axes and one projection have degree<=4
 # in each parameter after multiplying by the positive denominators.
 # A 5-point grid in each parameter is therefore an exact identity test.
 for vals in product(range(5),repeat=len(params)):
  t=[0,0,0]
  for k,v in zip(params,vals):t[k]=v
  v,ns,es=exact_geometry(tuple(t))
  if desc[0]=='host':value=kdot(U[f],[v[i][chosen][k]-v[i][j][k]for k in range(3)])
  else:
   _,i,b,ix,sense=tag
   if ix<10:u=ns[i][ix]
   elif ix<20:u=ns[b][ix-10]
   else:a,c=divmod(ix-20,len(ED));u=kcross(es[i][a],es[b][c])
   u=[sense*x for x in u];owner=i if side==0 else b
   diff=[v[owner][chosen][k]-v[owner][j][k]for k in range(3)]
   value=kdot(u,diff)
  assert value.sign()==0,('nonidentity support switch',desc,vals,float(value))
 zero_support.append({'descriptor':desc,'parameter_degree_bound':4,'grid_size':5**len(params)})

def good(value,desc=None):
 global checks
 checks+=1
 if value.v.lower()>=0:return
 if value.v.upper()<0:raise AssertionError(('strictly negative',desc,str(value.v)))
 assert desc is not None,('unresolved whole gap',str(value.v))
 identity(desc)

for i in range(5):
 for f,u in enumerate(UU):
  entry=active.get(('host',i,f))
  if entry:
   idx,feature=entry;chosen=feature[0]
   for j in range(8):good(dot(u,[V[i][chosen][k]-V[i][j][k]for k in range(3)]),['host',i,f,chosen,j])
  else:
   for j in range(8):
    gap=X[15]*dot(u,PP[facev[f]])-dot(u,[X[3*i+k]+V[i][j][k]for k in range(3)])
    good(gap)
for (i,j),tag in ptags.items():
 u=makeaxis(tag,N,E);assert dot(u,u).v.lower()>0
 entry=active.get(('pair',i,j))
 if entry:
  idx,feat=entry;ci,cj=feat
  assert tag == D['active_tags'][idx], ('active separator mismatch',tag,D['active_tags'][idx])
  for a in range(8):good(dot(u,[V[i][ci][k]-V[i][a][k]for k in range(3)]),['pair',tag,0,ci,a])
  for b in range(8):good(dot(u,[V[j][b][k]-V[j][cj][k]for k in range(3)]),['pair',tag,1,cj,b])
 else:
  for a in range(8):
   for b in range(8):good(dot(u,[X[3*j+k]+V[j][b][k]-X[3*i+k]-V[i][a][k]for k in range(3)]))
unit=10**60
lowint=(X[15].v.lower()*unit).floor().fmpz();upint=(X[15].v.upper()*unit).ceil().fmpz()
def fixed_decimal(z):
 z=str(z);return z[:-60]+'.'+z[-60:]
print('FULL_BODY_LIFT_PASS',checks,'exact support identities',len(zero_support),'scale',X[15].v)
