"""Prove all N18 packing inequalities at the isolated algebraic contact root.

Contact equalities are accepted only with complete polynomial proof coverage.
Every other inequality is proved strictly positive using outward integer
intervals. No geometric tolerance or added scale margin is used.
"""
from pathlib import Path
from fractions import Fraction as F
import json,time
from interval_root import D,Z,ONE,add,sub,neg,mul,div,square,field,root_box,asjson
from quartic import Q4,ALPHA
HERE=Path(__file__).resolve().parent

def sumiv(xs):
 z=Z
 for x in xs:z=add(z,x)
 return z
def dot(x,y):return sumiv(mul(a,b)for a,b in zip(x,y))
def vsub(x,y):return tuple(sub(a,b)for a,b in zip(x,y))
def vadd(x,y):return tuple(add(a,b)for a,b in zip(x,y))
def vmul(a,x):return tuple(mul(a,b)for b in x)
def cross(x,y):return tuple(sub(mul(x[(i+1)%3],y[(i+2)%3]),mul(x[(i+2)%3],y[(i+1)%3]))for i in range(3))
def mv(A,x):return tuple(dot(row,x)for row in A)
def mm(A,B):return [[sumiv(mul(A[i][k],B[k][j])for k in range(3))for j in range(3)]for i in range(3)]
def rot(w):
 norm=add(ONE,sumiv(square(x)for x in w));diag=sub(ONE,sumiv(square(x)for x in w))
 x,y,z=w;sk=[[Z,neg(z),y],[z,Z,neg(x)],[neg(y),x,Z]]
 return [[div(add(add(diag if i==j else Z,mul(field(2),mul(w[i],w[j]))),mul(field(2),sk[i][j])),norm)for j in range(3)]for i in range(3)]
def qrot(q):
 w,x,y,z=q;ww,xx,yy,zz=map(square,q);norm=sumiv([ww,xx,yy,zz])
 if norm[0]<=0:raise ValueError('quaternion norm is not proved positive')
 def twice(v):return mul(field(2),v)
 return [[div(sub(add(ww,xx),add(yy,zz)),norm),div(twice(sub(mul(x,y),mul(w,z))),norm),div(twice(add(mul(x,z),mul(w,y))),norm)],
         [div(twice(add(mul(x,y),mul(w,z))),norm),div(sub(add(ww,yy),add(xx,zz)),norm),div(twice(sub(mul(y,z),mul(w,x))),norm)],
         [div(twice(sub(mul(x,z),mul(w,y))),norm),div(twice(add(mul(y,z),mul(w,x))),norm),div(sub(add(ww,zz),add(xx,yy)),norm)]]
def exact_qrot(q):
 w,x,y,z=map(Q4,q);norm=w*w+x*x+y*y+z*z
 if norm.sign()<=0:raise ValueError('zero fixed quaternion')
 return [[field((w*w+x*x-y*y-z*z)/norm),field(2*(x*y-w*z)/norm),field(2*(x*z+w*y)/norm)],
         [field(2*(x*y+w*z)/norm),field((w*w-x*x+y*y-z*z)/norm),field(2*(y*z-w*x)/norm)],
         [field(2*(x*z-w*y)/norm),field(2*(y*z+w*x)/norm),field((w*w-x*x-y*y+z*z)/norm)]]
def positive_axis(n,delta):
 sg=dot(n,delta)
 if sg[0]>0:return n
 if sg[1]<0:return tuple(neg(x)for x in n)
 raise ValueError('unresolved normal direction/nondegeneracy')

def equality_coverage(contacts):
 source=json.loads((HERE/'polynomial_rows.json').read_text());reduction=json.loads((HERE/'structural_reduction.json').read_text());cert=json.loads((HERE/'interval_root_certificate.json').read_text())
 labels=contacts['all_equations']
 if labels!=source['labels'] or len(labels)!=len(source['rows'])or len(labels)!=reduction['source_row_count']:raise ValueError('contact/polynomial/reduction labels differ')
 if len({tuple(x)for x in labels})!=len(labels):raise ValueError('duplicate equality label')
 selected=set(reduction['exact_polynomial_independent_indices'])
 if list(reduction['exact_polynomial_independent_indices'])!=cert['source_row_indices']:raise ValueError('different selected root equations')
 for op in reduction['wall_difference_operations']:
  if op['index']in selected and op['subtract']not in selected:raise ValueError('selected wall difference missing its base')
 proved={tuple(x)for x in labels};equalwalls=set()
 for label in labels:
  if label[0]=='wall':
   _,i,f,v=label
   if not(0<=i<18 and 0<=f<10 and 0<=v<8):raise ValueError('invalid wall equality')
   equalwalls.add((i,f,v))
 seen=set();products=0
 for row in contacts['pairs']:
  i,j=row['i'],row['j'];ia,ib=row['vertices_i'],row['vertices_j']
  if not(0<=i<j<18)or(i,j)in seen:raise ValueError('invalid/duplicate pair')
  seen.add((i,j))
  if not ia or not ib or len(set(ia))!=len(ia)or len(set(ib))!=len(ib)or any(type(v)is not int or not 0<=v<8 for v in ia+ib):raise ValueError('invalid contact feature')
  needed={('pairbase',i,j,ia[0],ib[0])}|{('edgei',i,j,a,ia[0])for a in ia[1:]}|{('edgej',i,j,b,ib[0])for b in ib[1:]}
  if not needed<=proved:raise ValueError('contact lacks a base or feature equality: '+str((i,j)))
  products+=len(ia)*len(ib)
 return equalwalls,{'pair_equalities_with_polynomial_coverage':products,'wall_equalities_with_polynomial_coverage':len(equalwalls),'selected_raw_vs_wall_difference_equivalence':'PASS'}

def frames(p):
 a=ALPHA;R=a*a/2;H=a*a*a/2;k=(1-R)*a;l=(R-F(1,2))*a
 I=[[ONE if i==j else Z for j in range(3)]for i in range(3)];Q=[[ONE if i==j==0 else neg(ONE)if i==j else Z for j in range(3)]for i in range(3)]
 M=[I for _ in range(18)];M[0]=mm(rot(p[:3]),Q);M[4]=rot(p[3:6]);j=6
 face_axes={1:(-1,-1,k),3:(1,-1,k),6:(1,-1,k),12:(0,1,l),14:(1,0,l),16:(1,0,-l)}
 for i,axis in face_axes.items():M[i]=rot(tuple(mul(p[j],field(v))for v in axis));j+=1
 n6=tuple(map(field,(1,0,-l)));M[5]=mm(rot(vmul(p[j],n6)),Q);j+=1
 t=p[j];j+=1;A=field(a)
 bb=add(field(4-a*a),mul(field(2*a),t));dd=add(add(field(-a**3),mul(field(2*a**3-2*a),square(t))),mul(field(3*a*a-2),t))
 M[10]=qrot((neg(bb),dd,neg(mul(t,bb)),Z))
 n5=tuple(map(field,(1,1,k)));edge=tuple(map(field,(F(1,2)-R,F(1,2),-H)));en=cross(edge,n5)
 for i in[2,8]:
  s,t=p[j:j+2];j+=2
  M[i]=rot(vsub(vadd(vmul(s,n5),vmul(t,edge)),vmul(mul(s,t),en)))
 bedges={15:(F(-1,2),F(1,2)-R,-H),17:(R-F(1,2),F(1,2),-H)}
 for i,edge in bedges.items():
  s,t=p[j:j+2];j+=2
  ex,ey,ez=edge;base=exact_qrot((1+ex,0,ez,-ey))
  M[i]=mm(rot((t,mul(s,t),s)),base)
 if j!=22:raise AssertionError('parameter mismatch')
 return M

def main():
 start=time.monotonic();contacts=json.loads((HERE/'contact_input.json').read_text());equalwalls,coverage=equality_coverage(contacts)
 X=root_box();S=X[76];p=X[54:76];C=[tuple(X[3*i:3*i+3])for i in range(18)];M=frames(p)
 a=ALPHA;R=a*a/2;H=a*a*a/2;k=(1-R)*a;l=(R-F(1,2))*a
 base=[(R,Q4(),H/2),(-R,Q4(),H/2),(Q4(),R,H/2),(Q4(),-R,H/2)]+[(Q4(F(x,2)),Q4(F(y,2)),-H/2)for x in[-1,1]for y in[-1,1]]
 P=[tuple(map(field,v))for v in base];V=[[mv(m,v)for v in P]for m in M]
 norms=[(-1,-1,k),(-1,0,-l),(1,-1,k),(0,-1,-l),(-1,1,k),(1,1,k),(1,0,-l),(0,1,-l),(0,0,1),(0,0,-1)]
 W=[tuple(map(field,n))for n in norms];supports=[(1+R)/2,(R+F(1,2))/2,(1+R)/2,(R+F(1,2))/2,(1+R)/2,(1+R)/2,(R+F(1,2))/2,(R+F(1,2))/2,H/2,H/2];B=list(map(field,supports))
 pairs={(r['i'],r['j']):r for r in contacts['pairs']};axes=json.loads((HERE/'fallback_axes.json').read_text());fallback={tuple(r['pair']):tuple(field(F(v))for v in r['rational_axis'])for r in axes['separation_witnesses']}
 strict_wall=equal_wall=strict_pair=equal_pair=0;minwall=minpair=None;failures=[]
 for i in range(18):
  for f,n in enumerate(W):
   for v in range(8):
    if(i,f,v)in equalwalls:equal_wall+=1;continue
    slack=sub(mul(S,B[f]),dot(n,vadd(C[i],V[i][v])))
    if slack[0]<=0:failures.append(['wall',i,f,v,asjson(slack)])
    strict_wall+=1;minwall=slack[0]if minwall is None else min(minwall,slack[0])
 for i in range(18):
  for j in range(i+1,18):
   row=pairs.get((i,j))
   if row:
    ia,ib=row['vertices_i'],row['vertices_j']
    if len(ia)>=3:n=cross(vsub(V[i][ia[1]],V[i][ia[0]]),vsub(V[i][ia[2]],V[i][ia[0]]))
    elif len(ib)>=3:n=cross(vsub(V[j][ib[1]],V[j][ib[0]]),vsub(V[j][ib[2]],V[j][ib[0]]))
    else:n=cross(vsub(V[i][ia[1]],V[i][ia[0]]),vsub(V[j][ib[1]],V[j][ib[0]]))
    n=positive_axis(n,vsub(C[j],C[i]));zeros={(u,v)for u in ia for v in ib}
   else:n=fallback[i,j];zeros=set()
   if not any(v[0]>0 or v[1]<0 for v in n):raise ValueError('normal might vanish')
   center=dot(n,vsub(C[j],C[i]))
   for vi in range(8):
    for vj in range(8):
     if(vi,vj)in zeros:equal_pair+=1;continue
     slack=add(center,dot(n,vsub(V[j][vj],V[i][vi])))
     if slack[0]<=0:failures.append(['pair',i,j,vi,vj,asjson(slack)])
     strict_pair+=1;minpair=slack[0]if minpair is None else min(minpair,slack[0])
 result={'status':'PASS_DERIVED_ROOT_PACKING'if not failures else'UNRESOLVED','n':18,'root_source':'interval_root_certificate.json','equality_source':'proved contact polynomial identities','host_total':strict_wall+equal_wall,'host_strict_interval':strict_wall,'host_exact_equalities':equal_wall,'pair_total':153,'pair_vertex_total':strict_pair+equal_pair,'pair_strict_interval':strict_pair,'pair_exact_equalities':equal_pair,'strict_host_margin_lower':str(F(minwall,D)),'strict_pair_margin_lower':str(F(minpair,D)),'equality_coverage':coverage,'scale_interval':asjson(S),'failures':failures,'elapsed_seconds':time.monotonic()-start,'scope':'exact construction at a proved algebraic root; no global optimality claim'}
 (HERE/'root_packing_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['failures','scale_interval']},indent=2))
 if failures:print('First failures',failures[:8]);raise SystemExit(1)
 return result
if __name__=='__main__':main()
