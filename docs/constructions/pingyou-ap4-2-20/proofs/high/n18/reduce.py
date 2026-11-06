"""Exact structural reduction of the N18 contact equations.

Coordinates use Q(alpha), alpha**4=2.  The p variables are rotation
parameters, never decimal constants.  Polynomial rows have 56 entries:
54 center coefficients, scale coefficient, constant.  Contact equations are
homogenized only by the strictly positive rotation denominators.
"""
import json
from pathlib import Path
import sympy as s
from sympy.polys.rings import ring

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'contact_input.json').read_text())
LABELS=DATA['all_equations']
K=s.QQ.algebraic_field(s.root(2,4))
R,*p=ring('p0:22',K)
def scalar(x):return R.ground_new(K.from_sympy(s.sympify(x)))
a=scalar(s.root(2,4));r=a*a/2;h=a*a*a/2
one=R.one;zero=R.zero
P=[(r,zero,h/2),(-r,zero,h/2),(zero,r,h/2),(zero,-r,h/2)]
P += [(scalar(x)/2,scalar(y)/2,-h/2)for x in [-1,1]for y in [-1,1]]
def dot(v,w):return sum((x*y for x,y in zip(v,w)),zero)
def sub(v,w):return tuple(x-y for x,y in zip(v,w))
def cross(v,w):return tuple(v[(i+1)%3]*w[(i+2)%3]-v[(i+2)%3]*w[(i+1)%3]for i in range(3))
def mv(M,v):return tuple(dot(row,v)for row in M)
I=[[one if i==j else zero for j in range(3)]for i in range(3)]
Q=[[one if i==j==0 else -one if i==j else zero for j in range(3)]for i in range(3)]
def cayley(w):
 x,y,z=w;ww=dot(w,w);C=[[zero,-z,y],[z,zero,-x],[-y,x,zero]]
 return [[((one-ww)if i==j else zero)+2*w[i]*w[j]+2*C[i][j]for j in range(3)]for i in range(3)],one+ww
def mm(A,B):return [[sum((A[i][k]*B[k][j]for k in range(3)),zero)for j in range(3)]for i in range(3)]
def quat(q):
 w,x,y,z=q;d=w*w+x*x+y*y+z*z
 return [[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)], [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]],d
k=(one-r)*a;l=(r-one/2)*a
n0=(-one,-one,k);n2=(one,-one,k);n3=(zero,one,l);n1=(one,zero,l);n6=(one,zero,-l);n5=(one,one,k)
e=(one/2-r,one/2,-h);en=cross(e,n5)
face_axes={1:n0,3:n2,6:n2,12:n3,14:n1,16:n6}
N={i:I for i in range(18)};D={i:one for i in range(18)};POSITIVE_FACTORS=[]
N[0],D[0]=cayley(p[:3]);N[0]=mm(N[0],Q)
N[4],D[4]=cayley(p[3:6])
j=6
for i,axis in face_axes.items():N[i],D[i]=cayley(tuple(p[j]*v for v in axis));j+=1
N[5],D[5]=cayley(tuple(p[j]*v for v in n6));N[5]=mm(N[5],Q);j+=1
t=p[j];j+=1
bb=4-a*a+2*a*t;dd=-a**3+(2*a**3-2*a)*t*t+(3*a*a-2)*t
N[10],D[10]=quat((-bb,dd,-t*bb,zero))
for i in [2,8]:
 ss,tt=p[j:j+2];j+=2
 N[i],D[i]=cayley(tuple(ss*n5[k]+tt*e[k]-ss*tt*en[k]for k in range(3)))
 POSITIVE_FACTORS.extend([one+tt*tt,one+dot(n5,n5)*ss*ss])
 assert D[i]==POSITIVE_FACTORS[-1]*POSITIVE_FACTORS[-2]
for i,edge in [(15,sub(P[5],P[2])),(17,sub(P[5],P[1]))]:
 ss,tt=p[j:j+2];j+=2
 bnum,bden=quat((one+edge[0],zero,edge[2],-edge[1]));base=[[v.exquo(bden)for v in row]for row in bnum]
 assert dot(edge,edge)==one
 N[i],D[i]=cayley((tt,ss*tt,ss));N[i]=mm(N[i],base)
 POSITIVE_FACTORS.extend([one+ss*ss,one+tt*tt])
 assert D[i]==POSITIVE_FACTORS[-1]*POSITIVE_FACTORS[-2]
assert j==22
POSITIVE_FACTORS.extend(D.values())
V={i:[mv(N[i],v)for v in P]for i in range(18)}
k=(one-r)*a;l=(r-one/2)*a
W=[(-one,-one,k),(-one,zero,-l),(one,-one,k),(zero,-one,-l),(-one,one,k),(one,one,k),(one,zero,-l),(zero,one,-l),(zero,zero,a),(zero,zero,-a)]
B=[(one+r)/2,(r+one/2)/2,(one+r)/2,(r+one/2)/2,(one+r)/2,(one+r)/2,(r+one/2)/2,(r+one/2)/2,one/2,one/2]
OWNERS=list(range(18));OI={i:k for k,i in enumerate(OWNERS)}
def empty():return [zero]*56
def primitive(row):
 original=row
 nonzero=[x for x in row if x]
 if not nonzero:return row
 # Only cancel factors known strictly positive for every real parameter.
 # A general multivariate gcd is unnecessary, costly, and may hide branches.
 for denominator in POSITIVE_FACTORS:
  if denominator==one:continue
  while True:
   divided=[x.div(denominator)if x else(zero,zero)for x in row]
   if any(remainder for _,remainder in divided):break
   row=[quotient for quotient,_ in divided]
 lc=next(x for x in row if x).LC
 result=[x.quo_ground(lc)if x else x for x in row]
 first=next(i for i,x in enumerate(result)if x)
 factor=original[first].exquo(result[first])
 assert all(x==factor*y for x,y in zip(original,result))
 return result
def putcenter(row,i,v,mult=one):
 for k in range(3):row[3*OI[i]+k]+=mult*v[k]
def wall(i,k,v):
 row=empty();putcenter(row,i,W[k],D[i]);row[54]=-B[k]*D[i];row[55]=dot(W[k],V[i][v]);return row
PAIR={(q['i'],q['j']):q for q in DATA['pairs']}
normals={}
for(i,j),q in PAIR.items():
 ia,ib=q['vertices_i'],q['vertices_j']
 if len(ia)>=3:
  nf=cross(sub(P[ia[1]],P[ia[0]]),sub(P[ia[2]],P[ia[0]]));n=mv(N[i],nf);mode='i'
 elif len(ib)>=3:
  nf=cross(sub(P[ib[1]],P[ib[0]]),sub(P[ib[2]],P[ib[0]]));n=mv(N[j],nf);mode='j'
 else:
  n=cross(sub(V[i][ia[1]],V[i][ia[0]]),sub(V[j][ib[1]],V[j][ib[0]]));nf=None;mode='edge'
 normals[i,j]=(mode,n,nf)
def pairbase(i,j,v,w):
 row=empty();mode,n,nf=normals[i,j]
 if mode=='i':
  nn=tuple(x*D[j]for x in n);row[55]=dot(n,V[j][w])-dot(nf,P[v])*D[i]*D[j]
 elif mode=='j':
  nn=tuple(x*D[i]for x in n);row[55]=dot(nf,P[w])*D[i]*D[j]-dot(n,V[i][v])
 else:
  nn=tuple(x*D[i]*D[j]for x in n);row[55]=D[i]*dot(n,V[j][w])-D[j]*dot(n,V[i][v])
 putcenter(row,j,nn);putcenter(row,i,nn,-one);return row
def edge(i,j,v,w,side):
 row=empty();mode,n,nf=normals[i,j];owner=i if side=='i'else j
 row[55]=dot(n,sub(V[owner][v],V[owner][w]));return row
ROWS=[]
for label in LABELS:
 t=label[0]
 if t=='wall':row=wall(*label[1:])
 elif t=='pairbase':row=pairbase(*label[1:])
 else:row=edge(*label[1:],t[-1])
 ROWS.append(primitive(row))

def coeffs(value):
 c=list(reversed(value.to_list()));c += [s.QQ.zero]*(4-len(c))
 return [str(x)for x in c]
def encode(poly):return [{'powers':list(m),'coefficients':coeffs(c)}for m,c in poly.terms()]
def textpoly(poly):return str(poly.as_expr())
def main():
 # The conic's homogeneous quaternion is never zero for a real parameter.
 # If bb(t)=0 then t=(a²-4)/(2a), at which dd=6a(1-a²) !=0.
 conic_zero=(a*a-4).exquo(2*a)
 expected=6*a*(one-a*a)
 conic_at_zero=-a**3+(2*a**3-2*a)*conic_zero**2+(3*a*a-2)*conic_zero
 assert conic_at_zero==expected and expected
 # Prove every rational matrix represents a proper rotation, including the
 # conic and both bridge base frames, directly in the polynomial ring.
 for i in range(18):
  for u in range(3):
   for v in range(3):
    assert sum((N[i][k][u]*N[i][k][v]for k in range(3)),zero)==(D[i]**2 if u==v else zero)
  assert dot(N[i][0],cross(N[i][1],N[i][2]))==D[i]**3
 # Replace later support vertices on each wall by differences from the first.
 # The center and S coefficients cancel exactly, exposing only orientation.
 transformed=[];firstwall={};duplicates=[];zeros=[];orientation=[];affine=[]
 for index,(label,row)in enumerate(zip(LABELS,ROWS)):
  if label[0]=='wall':
   key=tuple(label[1:3])
   if key in firstwall:
    row=primitive([x-y for x,y in zip(row,ROWS[firstwall[key]])])
    duplicates.append({'index':index,'subtract':firstwall[key]})
   else:firstwall[key]=index
  transformed.append(row)
  if not any(row):zeros.append(index)
  elif not any(row[:55]):orientation.append(index)
  else:affine.append(index)
 print('ROWS',len(ROWS),'ZERO/IDENTICAL',len(zeros),'ORIENTATION',len(orientation),'AFFINE',len(affine),flush=True)
 unique=[];same=[]
 for i in orientation:
  for j in unique:
   if transformed[i]==transformed[j]:same.append([i,j]);break
  else:unique.append(i)
 report={'field':'Q(alpha), alpha^4=2, alpha>0','parameters':['p'+str(i)for i in range(22)],'source_row_count':len(ROWS),'unconditionally_redundant_indices':zeros,'wall_difference_operations':duplicates,'nonzero_orientation_rows':orientation,'unique_orientation_rows':unique,'duplicate_orientation_rows':same,'affine_rows':affine,'orientation_polynomials':[{'index':i,'label':LABELS[i],'polynomial':textpoly(transformed[i][55]),'terms':encode(transformed[i][55])}for i in unique]}
 # Stronger than a numerical rank computation: expand in independent center
 # variables and parameter monomials, then eliminate over the number field K.
 # A zero sparse row is therefore an exact polynomial identity for every p.
 pivots={};relations=[];independent=[]
 for index in affine+unique:
  sparse={(col,monomial):coefficient for col,poly in enumerate(transformed[index])for monomial,coefficient in poly.terms()}
  combination={index:K.one}
  while sparse:
   key=min(sparse);value=sparse[key]
   if key not in pivots:
    sparse={k:v/value for k,v in sparse.items()}
    combination={k:v/value for k,v in combination.items()}
    pivots[key]=(sparse,combination);independent.append(index);break
   old,oldcomb=pivots[key]
   for k,v in old.items():
    z=sparse.get(k,K.zero)-value*v
    if z:sparse[k]=z
    else:sparse.pop(k,None)
   for k,v in oldcomb.items():
    z=combination.get(k,K.zero)-value*v
    if z:combination[k]=z
    else:combination.pop(k,None)
  else:
   for column in range(56):
    assert sum((transformed[j][column].mul_ground(c)for j,c in combination.items()),zero)==zero
   relations.append({'dependent_index':index,'combination':[{'index':k,'coefficient':coeffs(v)}for k,v in sorted(combination.items())]})
 report['constant_coefficient_polynomial_rank']=len(independent)
 report['exact_polynomial_independent_indices']=independent
 report['exact_constant_coefficient_relations']=relations
 assert len(zeros)==143 and len(unique)==6 and len(affine)==73
 assert len(independent)==77 and len(relations)==2
 print('EXACT POLYNOMIAL RANK',len(independent),'relations',len(relations),flush=True)
 for relation in relations:print('RELATION',relation,flush=True)
 (HERE/'structural_reduction.json').write_text(json.dumps(report,indent=2))
 print('PASS: exact N18 polynomial row reduction.',flush=True)
 # This exports all rows as actual coefficient polynomials, not a numerical
 # interpolation or formal placeholder det(M).
 (HERE/'polynomial_rows.json').write_text(json.dumps({'columns':['c'+str(i)+'_'+str(k)for i in OWNERS for k in range(3)]+['S','constant'],'labels':LABELS,'rows':[[{'column':j,'terms':encode(x)}for j,x in enumerate(row)if x]for row in ROWS]},indent=2))

if __name__=='__main__':main()
