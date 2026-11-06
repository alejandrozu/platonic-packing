"""Exact rational interval proof for a six-parameter N3 contact construction.

The decimal root is a proposal only. All acceptance uses outward integer
intervals, a checked contraction, and complete-body inequalities.
"""
from pathlib import Path
from fractions import Fraction as F
from math import isqrt
import json,sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
D=10**100;NV=6
def floor(q):return q.numerator//q.denominator
def ceil(q):return -((-q.numerator)//q.denominator)
class I:
    def __init__(self,x=0,hi=None,raw=False):
        if raw:self.lo,self.hi=x,hi
        elif isinstance(x,I):self.lo,self.hi=x.lo,x.hi
        else:
            x=F(x);self.lo,self.hi=floor(x*D),ceil(x*D)
    @classmethod
    def box(cls,a,b):return cls(floor(F(a)*D),ceil(F(b)*D),True)
    def __add__(self,o):
        o=I(o);return I(self.lo+o.lo,self.hi+o.hi,True)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo,True)
    def __sub__(self,o):return self+-I(o)
    def __rsub__(self,o):return I(o)+-self
    def __mul__(self,o):
        if isinstance(o,AD):return o*self
        o=I(o);v=[a*b for a in [self.lo,self.hi]for b in[o.lo,o.hi]]
        return I(min(v)//D,-((-max(v))//D),True)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=I(o);assert o.lo>0 or o.hi<0
        v=[(a*D,b)for a in[self.lo,self.hi]for b in[o.lo,o.hi]]
        return I(min(a//b for a,b in v),max(-((-a)//b)for a,b in v),True)
    def __rtruediv__(self,o):return I(o)/self
    def mag(self):return F(max(abs(self.lo),abs(self.hi)),D)
    def out(self):return [str(F(self.lo,D)),str(F(self.hi,D))]
class AD:
    def __init__(self,x=0,der=None):
        if isinstance(x,AD):self.v,self.der=x.v,x.der
        else:self.v=I(x);self.der=[I(0)for _ in range(NV)]if der is None else der
    def __add__(self,o):
        o=AD(o);return AD(self.v+o.v,[a+b for a,b in zip(self.der,o.der)])
    __radd__=__add__
    def __neg__(self):return AD(-self.v,[-x for x in self.der])
    def __sub__(self,o):return self+-AD(o)
    def __rsub__(self,o):return AD(o)+-self
    def __mul__(self,o):
        o=AD(o);return AD(self.v*o.v,[a*o.v+self.v*b for a,b in zip(self.der,o.der)])
    __rmul__=__mul__
    def __truediv__(self,o):
        o=AD(o);return AD(self.v/o.v,[(a*o.v-self.v*b)/(o.v*o.v)for a,b in zip(self.der,o.der)])
    def __rtruediv__(self,o):return AD(o)/self
def const(x):return AD(x)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),AD())
def sub(a,b):return [x-y for x,y in zip(a,b)]
def add(a,b):return [x+y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def mv(M,v):return [dot(r,v)for r in M]
def mm(A,B):return [[dot(r,c)for c in zip(*B)]for r in A]
def col(M,j):return [r[j]for r in M]
def inv3(A):
    a,b,c=A
    cols=[cross(b,c),cross(c,a),cross(a,b)];det=dot(a,cols[0])
    return [[cols[j][i]/det for j in range(3)]for i in range(3)]
def rot(q):
    w,x,y,z=map(AD,q);nn=w*w+x*x+y*y+z*z
    return [[a/nn for a in r]for r in[[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]]]

alpha_lo=isqrt(isqrt(2*D**4));alpha=AD(I(alpha_lo,alpha_lo+1,True));H=alpha*alpha*alpha/2;R=alpha*alpha/2
P=[[R,AD(0),H/2],[-R,AD(0),H/2],[AD(0),R,H/2],[AD(0),-R,H/2]]+[[AD(F(x,2)),AD(F(y,2)),-H/2]for x in[-1,1]for y in[-1,1]]
FACES=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
U=[];B=[]
for f in FACES:
    u=cross(sub(P[f[1]],P[f[0]]),sub(P[f[2]],P[f[0]]))
    if dot(u,P[f[0]]).v.hi<0:u=[-v for v in u]
    assert dot(u,P[f[0]]).v.lo>0
    U.append(u);B.append(dot(u,P[f[0]]))
E=[AD(F(1,2))-R,AD(F(1,2)),H]
base0=rot([1+E[1],E[2],0,-E[0]])
base1=[[AD(-1),AD(0),AD(0)],[AD(0),AD(1),AD(0)],[AD(0),AD(0),AD(-1)]]
HOST=[[(0,4),(1,6),(8,5)],[(2,4),(6,4),(8,7)],[(5,2),(7,2),(9,3)]]
INV=[inv3([U[f]for f,v in spec])for spec in HOST]
def geometry(x):
    t,a,b,c,w,S=x
    M0=mm(base0,rot([1,0,t,0]));M1=mm(rot([1,a,b,c]),base1);M2=mm(M1,rot([1,0,0,w]));M=[M0,M1,M2]
    V=[[mv(m,p)for p in P]for m in M]
    C=[mv(INV[i],[S*B[f]-dot(U[f],V[i][v])for f,v in spec])for i,spec in enumerate(HOST)]
    return M,V,C
def equations(x):
    M,V,C=geometry(x);u0=col(M[0],2);u1=col(M[1],2)
    return [dot(U[2],col(M[1],1)),dot(U[7],sub(V[2][2],V[2][1])),dot(u0,sub(V[1][6],V[1][0])),
            dot(u0,sub(add(C[1],V[1][0]),add(C[0],V[0][0]))),
            dot(u0,sub(add(C[2],V[2][6]),add(C[0],V[0][0]))),
            dot(u1,sub(add(C[2],V[2][4]),add(C[1],V[1][0])))]
def variables(box):
    return [AD(v,[I(int(i==j))for j in range(NV)])for i,v in enumerate(box)]

def run():
    here=Path(__file__).resolve().parent
    doc=json.loads((here/'root.json').read_text());center=list(map(F,doc['values']));radius=F(1,10**60)
    box=[I.box(c-radius,c+radius)for c in center]
    F0=equations(variables([I(c)for c in center]));FX=equations(variables(box))
    # This inverse only proposes a rational preconditioner. The checks below
    # prove it works, independently of numerical inversion accuracy.
    if '--replay' in sys.argv:
        saved=json.loads((here/'certificate.json').read_text())
        assert list(map(F,saved['center']))==center and F(saved['radius'])==radius
        A=[[F(a)for a in row]for row in saved['preconditioner']]
    else:
        import mpmath as mp
        mp.mp.dps=90
        J=mp.matrix([[mp.mpf(str(F(a.lo+a.hi,2*D)))for a in f.der]for f in F0])
        Ap=J**-1;A=[[F(mp.nstr(Ap[i,j],80))for j in range(NV)]for i in range(NV)]
    qrows=[];errors=[]
    for i in range(NV):
        error=sum((I(A[i][j])*F0[j].v for j in range(NV)),I());errors.append(error.mag())
        row=[]
        for j in range(NV):
            value=I(int(i==j))-sum((I(A[i][k])*FX[k].der[j]for k in range(NV)),I())
            row.append(value.mag())
        qrows.append(sum(row))
    q=max(qrows);err=max(errors)
    assert q<1 and err+q*radius<radius,(float(q),float(err))
    # The thirteen wall equalities below follow from the nine defining center
    # equations, the two tangency equations, and R0 e_y=E.
    zeros={(0,0,4),(0,0,5),(0,1,6),(0,1,7),(0,8,5),(1,2,4),(1,2,5),(1,6,4),(1,8,7),(2,5,2),(2,7,1),(2,7,2),(2,9,3)}
    M,V,C=geometry([AD(v)for v in box]);S=AD(box[5]);wallmin=None;strictwalls=0
    for i in range(3):
        for f in range(10):
            for v in range(8):
                if(i,f,v)in zeros:continue
                gap=(S*B[f]-dot(U[f],add(C[i],V[i][v]))).v
                assert gap.lo>0,('wall',i,f,v,gap.out())
                strictwalls+=1;wallmin=gap.lo if wallmin is None else min(wallmin,gap.lo)
    pair_zero={(0,1):{(v,w)for v in range(4)for w in[0,6]},(0,2):{(v,6)for v in range(4)},(1,2):{(v,w)for v in range(4)for w in range(4,8)}}
    pairmin=None;strictpairs=0
    for i,j,u in[(0,1,col(M[0],2)),(0,2,col(M[0],2)),(1,2,col(M[1],2))]:
        for vi in range(8):
            for vj in range(8):
                if(vi,vj)in pair_zero[i,j]:continue
                gap=dot(u,sub(add(C[j],V[j][vj]),add(C[i],V[i][vi]))).v
                assert gap.lo>0,('pair',i,j,vi,vj,gap.out())
                strictpairs+=1;pairmin=gap.lo if pairmin is None else min(pairmin,gap.lo)
    result={'status':'PASS_EXACT_RATIONAL_INTERVAL_N3_CONTACT_ROOT','field':'Q(alpha), alpha>0, alpha^4=2',
            'variables':doc['variables'],'center':[str(c)for c in center],'radius':str(radius),
            'preconditioner':[[str(a)for a in row]for row in A],
            'q_upper':str(q),'error_upper':str(err),'invariance_margin':str(radius-err-q*radius),
            'scale_interval':box[5].out(),'strict_wall_checks':strictwalls,'exact_wall_equalities':len(zeros),
            'strict_pair_checks':strictpairs,'exact_pair_equalities':sum(map(len,pair_zero.values())),
            'wall_margin_lower':str(F(wallmin,D)),'pair_margin_lower':str(F(pairmin,D)),
            'proper_frames':'Quaternion rotations, product rotations; all norm denominators positive',
            'definition':'Unique root of equations() in this rational box, decoded by geometry()',
            'scope':'Feasible construction only; no unrestricted optimality assertion.'}

    print({k:v for k,v in result.items()if k not in['preconditioner','center']})
if __name__=='__main__':run()
