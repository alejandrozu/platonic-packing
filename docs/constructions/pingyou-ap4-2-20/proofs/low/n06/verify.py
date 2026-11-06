"""Exact rational-interval root and complete geometric check for N6.

No SymPy/SciPy/Flint dependency. The contact decoder identities are checked by verify_decoder.py.
"""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import json,itertools

HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'certificate.json').read_text())
class I:
    def __init__(self,a=0,b=None):
        if isinstance(a,I):self.a,self.b=a.a,a.b
        else:self.a,self.b=F(a),F(a if b is None else b)
        assert self.a<=self.b
    def __add__(self,o):o=I(o);return I(self.a+o.a,self.b+o.b)
    __radd__=__add__
    def __neg__(self):return I(-self.b,-self.a)
    def __sub__(self,o):return self+-I(o)
    def __rsub__(self,o):return I(o)+-self
    def __mul__(self,o):
        o=I(o);v=[self.a*o.a,self.a*o.b,self.b*o.a,self.b*o.b];return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=I(o);assert o.a>0 or o.b<0;return self*I(1/o.b,1/o.a)
    def __rtruediv__(self,o):return I(o)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        if n==0:return I(1)
        if n%2:return I(self.a**n,self.b**n)
        return I(0 if self.a<=0<=self.b else min(self.a**n,self.b**n),max(self.a**n,self.b**n))
    def contains_zero(self):return self.a<=0<=self.b
    def mid(self):return (self.a+self.b)/2
    def out(self):return [str(self.a),str(self.b)]
    def __repr__(self):return f'I({float(self.a)},{float(self.b)})'

den=10**100;root=isqrt(isqrt(2*den**4));alpha=I(F(root,den),F(root+1,den))
assert alpha.a**4<2<alpha.b**4
def field(c):
    out=I(0)
    for v in c[::-1]:out=out*alpha+I(v)
    return out
def poly(terms,z):
    return sum((field(v['coefficients'])*z[0]**v['powers'][0]*z[1]**v['powers'][1]for v in terms),I(0))
def deriv(terms,j):
    out=[]
    for v in terms:
        power=v['powers'][j]
        if power:
            q=list(v['powers']);q[j]-=1
            out.append({'powers':q,'coefficients':[str(F(c)*power)for c in v['coefficients']]})
    return out
def rational(expr,z):return poly(expr['numerator'],z)/poly(expr['denominator'],z)
mid=[F(v)for v in D['root_center']];rad=F(D['box_radius']);box=[I(v-rad,v+rad)for v in mid]
Y=[[F(v)for v in row]for row in D['preconditioner']]
FV=[poly(f,[I(v)for v in mid])for f in D['equations']]
J=[[poly(deriv(f,j),box)for j in range(2)]for f in D['equations']]
Err=[[I(int(i==j))-sum((Y[i][k]*J[k][j]for k in range(2)),I(0))for j in range(2)]for i in range(2)]
NK=[I(mid[i])-sum((Y[i][k]*FV[k]for k in range(2)),I(0))+sum((Err[i][j]*I(-rad,rad)for j in range(2)),I(0))for i in range(2)]
assert all(box[i].a<NK[i].a<NK[i].b<box[i].b for i in range(2))
contraction=max(sum(max(abs(v.a),abs(v.b))for v in row)for row in Err)
assert contraction<1
def univariate_u(x,derivative=False):
    return sum((field(q['coefficients'])*(q['power'] if derivative else 1)*
                x**(q['power']-1 if derivative else q['power'])
                for q in D['univariate_u'] if not derivative or q['power']),I(0))
pu_lo=univariate_u(I(box[1].a));pu_hi=univariate_u(I(box[1].b))
pu_derivative=univariate_u(box[1],True)
assert pu_derivative.a>0 or pu_derivative.b<0
assert (pu_lo.b<0<pu_hi.a) or (pu_hi.b<0<pu_lo.a)
S=rational(D['solution_functions']['S'],box)
xp=rational(D['solution_functions']['x'],box);yp=rational(D['solution_functions']['y'],box)


def dot(a,b):return sum((x*y for x,y in zip(a,b)),I(0))
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def mv(m,v):return [dot(row,v)for row in m]
def mm(a,b):return [[dot(row,col)for col in zip(*b)]for row in a]
def neg(v):return [-x for x in v]
Z=I(0);O=I(1);H=alpha**3/2;R=alpha**2/2
P=[[R,Z,H/2],[-R,Z,H/2],[Z,R,H/2],[Z,-R,H/2]]+[[I(x)/2,I(y)/2,-H/2]for x,y in itertools.product([-1,1],repeat=2)]
ID=[[I(int(i==j))for j in range(3)]for i in range(3)]
B0=[[-R,R,Z],[R,R,Z],[Z,Z,-O]];B1=[[-O,Z,Z],[Z,-O,Z],[Z,Z,O]];T=[[R,-R,Z],[-R,-R,Z],[Z,Z,-O]]
n0=[H,Z,(O-alpha**2)/2];n1=[alpha/2,alpha/2,(alpha**2-O)/2]
def rotation(n,k):
    sk=[[Z,-n[2],n[1]],[n[2],Z,-n[0]],[-n[1],n[0],Z]];den=O+I(F(3,4))*k*k
    assert den.a>0
    return [[((O-I(F(3,4))*k*k)*int(i==j)+2*k*k*n[i]*n[j]+2*k*sk[i][j])/den for j in range(3)]for i in range(3)]
M0=mm(rotation(n0,box[0]),B0);M1=mm(rotation(n1,box[1]),B1)
M=[M0,M1,ID,T,mm(T,M1),mm(T,M0)]
V=[[mv(m,p)for p in P]for m in M]
b0=dot(n0,P[0]);b1=dot(n1,P[0])
z0=-S*H/2-V[0][1][2];x0=((S-1)*b0-n0[2]*z0)/n0[0]
z1=S*H/2-V[1][1][2];y1=((S-1)*b1-n1[2]*z1)/n1[1]-xp
C0=[x0,yp,z0];C1=[xp,y1,z1];C2=[-(S-1)/2,(S-1)/2,-(S-1)*H/2]
C=[C0,C1,C2,mv(T,C2),mv(T,C1),mv(T,C0)]
G=[[add(c,v)for v in vs]for c,vs in zip(C,V)]
faces=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
U=[];BB=[]
for f in faces:
    n=cross(sub(P[f[1]],P[f[0]]),sub(P[f[2]],P[f[0]]))
    if dot(n,P[f[0]]).mid()<0:n=neg(n)
    U.append(n);BB.append(dot(n,P[f[0]]))
wallzero={
0:{6:[1,2,5],9:[1]},1:{5:[1,3,4],8:[1]},
2:{1:[1,4,5],4:[1,2,5],7:[2,5,7],9:[4,5,6,7]},
3:{0:[2,5,7],1:[1,2,5],4:[1,4,5],8:[4,5,6,7]},
4:{3:[1,3,4],9:[1]},5:{2:[1,2,5],8:[1]}}
positive=[];wall_eq=0
for i,vs in enumerate(G):
    for f,n in enumerate(U):
        for v,p in enumerate(vs):
            gap=S*BB[f]-dot(n,p)
            if v in wallzero[i].get(f,[]):assert gap.contains_zero();wall_eq+=1
            else:
                assert gap.a>0,('wall',i,f,v,gap)
                positive.append(gap.a)

active={}
def insert(i,j,n,aa,bb):
    if i>j:i,j,n,aa,bb=j,i,neg(n),bb,aa
    # Select the outward separation sense using the centroid separation.
    sense=dot(n,sub(C[j],C[i]));assert not sense.contains_zero()
    if sense.b<0:n=neg(n)
    assert dot(n,n).a>0
    active[(i,j)]=(n,aa,bb)
bases=[(0,1,mv(M1,[Z,Z,O]),[7],[4,5,6,7]),
       (0,2,cross(sub(V[0][6],V[0][0]),sub(P[6],P[0])),[0,6],[0,6]),
       (0,4,cross(sub(V[0][6],V[0][3]),sub(V[4][5],V[4][2])),[3,6],[2,5]),
       (1,2,cross(sub(V[1][7],V[1][6]),sub(P[2],P[0])),[6,7],[0,2]),
       (1,3,cross(sub(V[1][7],V[1][0]),sub(V[3][6],V[3][3])),[0,7],[3,6])]
mate={0:5,5:0,1:4,4:1,2:3,3:2}
for i,j,n,aa,bb in bases:
    insert(i,j,n,aa,bb);insert(mate[i],mate[j],mv(T,n),aa,bb)
fixed={tuple(r['pair']):[field(c)for c in r['normal']]for r in D['inactive_pair_normals']}
pair_eq=0
for i,j in itertools.combinations(range(6),2):
    n,aa,bb=active.get((i,j),(fixed.get((i,j)),[],[]));assert n is not None
    for a,b in itertools.product(range(8),repeat=2):
        gap=dot(n,sub(G[j][b],G[i][a]))
        if a in aa and b in bb:assert gap.contains_zero();pair_eq+=1
        else:
            assert gap.a>0,('pair',i,j,a,b,gap)
            positive.append(gap.a)

def dec(q,n,ceil=False):
    p=10**n;z=(q.numerator*p)//q.denominator
    if ceil and F(z,p)<q:z+=1
    return ('-'if z<0 else'')+str(abs(z)//p)+'.'+str(abs(z)%p).zfill(n)
out={'status':'PASS_EXACT_ALGEBRAIC_N6_CONSTRUCTION','root_center':D['root_center'],'root_radius':D['box_radius'],
     'krawczyk_strict_interior':True,'contraction_upper':str(contraction),
     'univariate_u_root_isolated_by_strict_signs_and_derivative':True,
     'S_lower_60':dec(S.a,60),'S_upper_60':dec(S.b,60,True),
     'host_vertex_checks':480,'host_equalities':wall_eq,'pair_vertex_checks':960,'pair_equalities':pair_eq,
     'minimum_strict_noncontact_gap_lower':dec(min(positive),30),
     'proper_rotations':'Exact Cayley rotations of proper P symmetries; denominator1+3k²/4>0',
     'decoder_identity_check':D['exact_decoder_identities_checked'],
     'scope':'One exactly reconstructed six-body contact family; no unrestricted optimality claim.'}

print(json.dumps(out,indent=2))
