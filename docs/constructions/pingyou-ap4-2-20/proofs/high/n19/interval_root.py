#!/usr/bin/env python3
"""Replayable exact Banach certificate for the derived N19 contact system.

Numerics only propose a dyadic preconditioner. Polynomial/derivative evaluation,
coefficient bounds, matrix products and acceptance use outward integer dyadics.
"""
from pathlib import Path
import json,sys,time,hashlib
from fractions import Fraction as F
from quartic import Q4
BITS=256;D=1<<BITS;Z=(0,0);ONE=(D,D)
NVAR=CENTERCOUNT=PARAMCOUNT=SINDEX=None
def configure(source):
 global NVAR,CENTERCOUNT,PARAMCOUNT,SINDEX
 if source.get("representation")=="full-polynomials":
  NVAR=len(source["variable_names"]);CENTERCOUNT=source.get("center_count",0);PARAMCOUNT=NVAR-CENTERCOUNT-1
 else:
  CENTERCOUNT=len(source["columns"])-2
  PARAMCOUNT=len(next(term for row in source["rows"] for col in row for term in col["terms"])["powers"])
  NVAR=CENTERCOUNT+PARAMCOUNT+1
  assert CENTERCOUNT%3==0
 SINDEX=source.get("scale_index",NVAR-1)
 assert 0<=SINDEX<NVAR
 return NVAR
def initial_values(data):
 if "x" in data:return data["x"]
 return [x for row in data["centers_physical"] for x in row]+data["parameters"]+[data["scale"]]
def fl(q):return q.numerator//q.denominator
def ce(q):return -((-q.numerator)//q.denominator)
def ivfrac(q):return(fl(q*D),ce(q*D))
def add(a,b):return(a[0]+b[0],a[1]+b[1])
def neg(a):return(-a[1],-a[0])
def sub(a,b):return add(a,neg(b))
def mul(a,b):
 if a==Z or b==Z:return Z
 v=(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]);return(min(v)//D,-((-max(v))//D))
def times(a,k):return(a[0]*k,a[1]*k)if k>=0 else(a[1]*k,a[0]*k)
def div(a,b):
 if b[0]<=0<=b[1]:raise ZeroDivisionError('Interval denominator contains zero')
 quotients=[(x*D,y)for x in a for y in b]
 return(min(n//d for n,d in quotients),max(-((-n)//d)for n,d in quotients))
def square(a):
 if a[0]<=0<=a[1]:return(0,-((-max(a[0]*a[0],a[1]*a[1]))//D))
 return mul(a,a)
def field(value):
 value=value if isinstance(value,Q4)else Q4(value)
 lo,hi=value.interval(bits=BITS)
 return(fl(lo*D),ce(hi*D))
def root_box(certificate=None,refined=True):
 if certificate is None:certificate=json.loads(Path(__file__).with_name('interval_root_certificate.json').read_text())
 if int(certificate['center_denominator'])!=D:raise ValueError('Wrong dyadic denominator')
 center=[int(x)for x in certificate['center_numerators']]
 radius=F(certificate['refined_uniform_radius']if refined else certificate['box_radius'])
 r=ce(radius*D)
 return[(x-r,x+r)for x in center]
def maxabs(a):return max(abs(a[0]),abs(a[1]))
def asjson(a):return[str(F(a[0],D)),str(F(a[1],D))]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dec(q,places=12):
 import mpmath as mp
 mp.mp.dps=max(40,places+20);return mp.nstr(mp.mpf(q.numerator)/q.denominator,places)
def compile_rows(source,indices):
 if source.get("representation")=="full-polynomials":
  return [[(Q4(t["coefficients"]),tuple((k,p)for k,p in enumerate(t["powers"])if p))for t in source["rows"][i]]for i in indices]
 rows=[]
 for ri in indices:
  row={}
  for column in source['rows'][ri]:
   col=column['column'];cv=col if col<CENTERCOUNT else (NVAR-1) if col==CENTERCOUNT else None
   for term in column['terms']:
    exps=[0]*NVAR
    for k,p in enumerate(term['powers']):exps[CENTERCOUNT+k]=p
    if cv is not None:exps[cv]+=1
    key=tuple((k,p)for k,p in enumerate(exps)if p)
    row[key]=row.get(key,Q4())+Q4(term['coefficients'])
  rows.append([(coef,exps)for exps,coef in row.items()if coef])
 return rows

def evaluate(rows,X,jacobian=True):
 maxdegree={}
 for row in rows:
  for coeff,exps in row:
   for k,p in exps:maxdegree[k]=max(maxdegree.get(k,0),p)
 powers={}
 for k,d in maxdegree.items():
  ar=[ONE]
  for p in range(d):ar.append(mul(ar[-1],X[k]))
  powers[k]=ar
 values=[];J=[]
 for row in rows:
  val=Z;jac=[Z]*NVAR
  for coeff,exps in row:
   lo,hi=coeff.interval(bits=BITS);ci=(fl(lo*D),ce(hi*D));term=ci
   for k,p in exps:term=mul(term,powers[k][p])
   val=add(val,term)
   if jacobian:
    for k,p in exps:
     part=times(ci,p)
     for l,d in exps:part=mul(part,powers[l][d-int(l==k)])
     jac[k]=add(jac[k],part)
  values.append(val);J.append(jac)
 return values,J

def selftest():
 for a in [F(-7,3),F(-1,7),F(0),F(1,13),F(19,7)]:
  for b in [F(-9,7),F(-1,11),F(0),F(11,5)]:
   aa,bb=ivfrac(a),ivfrac(b)
   for value,it in [(a+b,add(aa,bb)),(a-b,sub(aa,bb)),(a*b,mul(aa,bb)),(a*a,square(aa))]:assert F(it[0],D)<=value<=F(it[1],D)
   if b:
    it=div(aa,bb);assert F(it[0],D)<=a/b<=F(it[1],D)
 return 'PASS: signed outward dyadic add/subtract/multiply/divide/square controls'

def replay(path=None,base=None):
 """Verify saved rational preconditioner and bounds without any numerical solve."""
 start=time.monotonic();base=Path(base)if base else Path(__file__).resolve().parent
 path=Path(path)if path else base/'interval_root_certificate.json'
 cert=json.loads(path.read_text())
 for name,digest in cert['source_sha256'].items():
  if sha(base/name)!=digest:raise ValueError('Input digest changed: '+name)
 source=json.loads((base/'polynomial_rows.json').read_text());configure(source)
 red=json.loads((base/'structural_reduction.json').read_text())
 indices=red['exact_polynomial_independent_indices']
 assert indices==cert['source_row_indices'];rows=compile_rows(source,indices)
 assert int(cert['center_denominator'])==D and int(cert['preconditioner_denominator'])==D
 center=[int(x)for x in cert['center_numerators']];A=[[int(x)for x in row]for row in cert['preconditioner_numerators']]
 assert len(center)==NVAR and len(A)==NVAR and all(len(row)==NVAR for row in A)
 radius=F(cert['box_radius']);assert (radius*D).denominator==1;r=int(radius*D)
 C=[(x,x)for x in center];X=[(x-r,x+r)for x in center]
 fc,_=evaluate(rows,C,jacobian=False);_,jx=evaluate(rows,X)
 qs=[];es=[]
 for i in range(NVAR):
  rr=Z
  for k in range(NVAR):rr=add(rr,mul((A[i][k],A[i][k]),fc[k]))
  es.append(maxabs(rr));qrow=0
  for j in range(NVAR):
   a=Z
   for k in range(NVAR):a=add(a,mul((A[i][k],A[i][k]),jx[k][j]))
   qrow+=maxabs(sub(ONE if i==j else Z,a))
  qs.append(qrow)
 e=max(es);q=max(qs)
 assert F(q,D)==F(cert['q_upper']);assert F(e,D)==F(cert['e_upper'])
 assert q<D and e*D+q*r<r*D
 assert F(e,D-q)==F(cert['refined_uniform_radius'])
 assert [F(center[SINDEX],D)-F(e,D-q),F(center[SINDEX],D)+F(e,D-q)]==list(map(F,cert['scale_interval']))
 result={'status':'PASS_EXACT_ROOT_CERTIFICATE_REPLAY','numerical_inverse_used':False,'q_upper':cert['q_upper'],'e_upper':cert['e_upper'],'all_decisions':'integer and rational only','elapsed_seconds':time.monotonic()-start}
 (base/'interval_root_replay.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 return result

def main(base=None):
 import mpmath as mp
 start=time.monotonic();base=Path(base)if base else Path(__file__).resolve().parent
 sourcepath=base/'polynomial_rows.json';reductionpath=base/'structural_reduction.json';rootpath=base/'root_75digits.json'
 source=json.loads(sourcepath.read_text());configure(source);red=json.loads(reductionpath.read_text());indices=red['exact_polynomial_independent_indices'];assert len(indices)==NVAR
 rows=compile_rows(source,indices);rootdata=json.loads(rootpath.read_text());raw=initial_values(rootdata);assert len(raw)==NVAR
 center=[fl(F(x)*D+F(1,2))for x in raw];r=ce(F('1e-20')*D);C=[(x,x)for x in center];X=[(x-r,x+r)for x in center]
 print('COMPILED',len(rows),'terms',sum(len(row)for row in rows),'seconds',time.monotonic()-start,flush=True)
 fc,jc=evaluate(rows,C);_,jx=evaluate(rows,X)
 print('EVALUATED',time.monotonic()-start,flush=True)
 mp.mp.dps=100
 JJ=mp.matrix([[mp.mpf(a+b)/(2*D)for a,b in row]for row in jc]);AA=JJ**-1
 A=[[int(mp.nint(AA[i,j]*D))for j in range(NVAR)]for i in range(NVAR)]
 print('PRECONDITIONER',time.monotonic()-start,flush=True)
 # Multiplying a point dyadic A_ik by an interval J_kj stays outward.
 residual=[];qs=[];es=[]
 for i in range(NVAR):
  rr=Z
  for k in range(NVAR):rr=add(rr,mul((A[i][k],A[i][k]),fc[k]))
  residual.append(rr);es.append(maxabs(rr))
  qrow=0
  for j in range(NVAR):
   a=Z
   for k in range(NVAR):a=add(a,mul((A[i][k],A[i][k]),jx[k][j]))
   g=sub(ONE if i==j else Z,a);qrow+=maxabs(g)
  qs.append(qrow)
 e=max(es);q=max(qs);assert q<D,'not contractive';assert e*D+q*r<r*D,'box not invariant'
 refined=F(e,D-q)
 scale_center=F(center[SINDEX],D);slo=scale_center-refined;shi=scale_center+refined
 result={'status':'PASS_EXACT_BANACH_ROOT_CERTIFICATE','system':f'{NVAR} independent polynomial numerators from the contact derivation','field':'Q(alpha), alpha>0, alpha^4=2','arithmetic':'256-bit fixed dyadics; all operations outward rounded using integer division; final acceptance is exact integer inequalities','source_sha256':{p.name:sha(p)for p in[sourcepath,reductionpath,rootpath]},'source_row_indices':indices,'variable_order':source.get('variable_names',f'{CENTERCOUNT} physical center coordinates, {PARAMCOUNT} orientation parameters, S'),'scale_index':SINDEX,'center_denominator':str(D),'center_numerators':[str(x)for x in center],'box_radius':str(F(r,D)),'preconditioner_denominator':str(D),'preconditioner_numerators':[[str(x)for x in row]for row in A],'q_upper':str(F(q,D)),'e_upper':str(F(e,D)),'q_row_bounds':[str(F(x,D))for x in qs],'e_coordinate_bounds':[str(F(x,D))for x in es],'invariance_integer_margin':str(r*D-e*D-q*r),'refined_uniform_radius':str(refined),'scale_interval':[str(slo),str(shi)],'scale_decimal_approximation':[dec(slo,80),dec(shi,80)],'interval_arithmetic_selftest':selftest(),'elapsed_seconds':time.monotonic()-start,'theorem':'T(x)=x-AF(x) maps the closed box into itself and is a strict sup-norm contraction. Since ||I-AJ||<1, A is invertible, so its unique fixed point is the unique zero of F in the box. It lies within e/(1-q) of the center.','scope':'Existence and uniqueness of the derived polynomial root only. Full packing inequalities and polynomial-system equivalence are separate obligations.'}
 out=base/'interval_root_certificate.json';out.write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k]for k in ['status','q_upper','e_upper','refined_uniform_radius','scale_decimal_approximation','elapsed_seconds']},indent=2));print(out)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');parser.add_argument('--directory',default=None);args=parser.parse_args()
 if args.replay:replay(base=args.directory)
 else:main(base=args.directory)
