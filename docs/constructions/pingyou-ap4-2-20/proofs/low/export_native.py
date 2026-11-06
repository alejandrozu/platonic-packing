"""Export native records from the specified exact antiprism constructions.

Requires mpmath. The construction endpoint and the strictly separated native
record are recorded separately. Run from any working directory.
"""
from pathlib import Path
from fractions import Fraction
import json,sys
import mpmath as mp
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
mp.mp.dps=160
HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'records'
alpha=mp.root(2,4);H=alpha**3/2;R=alpha**2/2
DILATION=1+mp.mpf('1e-12')
def value(x):
    if isinstance(x,(list,tuple)):return sum(value(c)*alpha**i for i,c in enumerate(x))
    if isinstance(x,str) and '/' in x:
        a,b=x.split('/');return mp.mpf(a)/mp.mpf(b)
    return mp.mpf(x)
def vec(v):return [value(x)for x in v]
def mat(m):return mp.matrix([vec(r)for r in m])
def read(n,file):return json.loads((HERE/f'n{n:02d}'/file).read_text())
def rot(q):
    w,x,y,z=q;d=w*w+x*x+y*y+z*z
    return mp.matrix([[w*w+x*x-y*y-z*z,2*(x*y-w*z),2*(x*z+w*y)],
                      [2*(x*y+w*z),w*w-x*x+y*y-z*z,2*(y*z-w*x)],
                      [2*(x*z-w*y),2*(y*z+w*x),w*w-x*x-y*y+z*z]])/d
def quaternion(M):
    i=max(range(4),key=lambda i: [1+M[0,0]+M[1,1]+M[2,2],1+M[0,0]-M[1,1]-M[2,2],1-M[0,0]+M[1,1]-M[2,2],1-M[0,0]-M[1,1]+M[2,2]][i])
    if i==0:
        q=[mp.sqrt(1+M[0,0]+M[1,1]+M[2,2])/2,0,0,0];d=4*q[0];q[1:]=[(M[2,1]-M[1,2])/d,(M[0,2]-M[2,0])/d,(M[1,0]-M[0,1])/d]
    else:
        j,k=(i%3,(i+1)%3);r=i-1
        # cyclic axes r,j,k are (0,1,2), (1,2,0), or (2,0,1).
        q=[0,0,0,0];q[i]=mp.sqrt(1+M[r,r]-M[j,j]-M[k,k])/2;d=4*q[i]
        q[0]=(M[k,j]-M[j,k])/d;q[j+1]=(M[r,j]+M[j,r])/d;q[k+1]=(M[r,k]+M[k,r])/d
    assert mp.norm(rot(q)-M)<mp.mpf('1e-65'),mp.norm(rot(q)-M)
    return q
P=[mp.matrix([R,0,H/2]),mp.matrix([-R,0,H/2]),mp.matrix([0,R,H/2]),mp.matrix([0,-R,H/2])]+[mp.matrix([mp.mpf(x)/2,mp.mpf(y)/2,-H/2])for x in[-1,1]for y in[-1,1]]
FACES=[[1,3,4],[1,4,5],[0,3,6],[3,4,6],[1,2,5],[0,2,7],[0,6,7],[2,5,7],[0,1,2,3],[4,5,6,7]]
def cross(x,y):return mp.matrix([x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]])
U=[]
for f in FACES:
    u=cross(P[f[1]]-P[f[0]],P[f[2]]-P[f[0]])
    if mp.fdot(u,P[f[0]])<0:u=-u
    U.append(u)
def decode(n):
    if n==2:
        d=read(n,'endpoint.json');t=mp.sqrt(mp.sqrt(2)-1)
        def evaluate(x):return sum(value(c)*t**i for i,c in enumerate(x))
        A=mp.matrix([[evaluate(x)for x in r]for r in d['normalized_frame0']]);L=mp.diag([1,1,1/alpha]);M=L*A*L**-1
        c=L*mp.matrix([evaluate(x)for x in d['center0']]);T=mp.diag([-1,-1,1])
        return evaluate(d['S']),[c,T*c],[M,T*M]
    if n==3:
        d=read(n,'root.json');return value(d['values'][-1]),[mp.matrix(vec(c))for c in d['centers']],[mat(m)for m in d['matrices']]
    if n in[4,7]:
        d=read(n,'endpoint.json');return value(d['scale_coefficients']),[mp.matrix(vec(c))for c in d['physical_centers']],[mat(m)for m in d['frames']]
    if n==5:
        d=read(n,'root.json');t=vec(d['root'])
        def around(u,v):return rot([1]+list(u*v))
        k=mp.matrix([-H,0,R-mp.mpf('.5')]);K=mp.matrix([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
        base=mp.eye(3)+K+2*K*K
        return value(d['scale']),[mp.matrix(vec(c))for c in d['centers']],[around(U[7],t[0]),mp.eye(3),mp.eye(3),around(U[0],t[1]),base*rot([1,0,t[2],0])]
    if n==6:
        d=read(n,'certificate.json');t,u=vec(d['root_center'])
        def poly(xs):return sum(value(v['coefficients'])*t**v['powers'][0]*u**v['powers'][1]for v in xs)
        def rat(f):return poly(f['numerator'])/poly(f['denominator'])
        S,x,y=[rat(d['solution_functions'][k])for k in ['S','x','y']]
        B0=mp.matrix([[-R,R,0],[R,R,0],[0,0,-1]]);B1=mp.diag([-1,-1,1]);T=mp.matrix([[R,-R,0],[-R,-R,0],[0,0,-1]])
        n0=mp.matrix([H,0,(1-alpha**2)/2]);n1=mp.matrix([alpha/2,alpha/2,(alpha**2-1)/2])
        M0=rot([1]+list(n0*t))*B0;M1=rot([1]+list(n1*u))*B1;M=[M0,M1,mp.eye(3),T,T*M1,T*M0]
        V0=M0*P[1];V1=M1*P[1];z0=-S*H/2-V0[2];x0=((S-1)*mp.fdot(n0,P[0])-n0[2]*z0)/n0[0]
        z1=S*H/2-V1[2];y1=((S-1)*mp.fdot(n1,P[0])-n1[2]*z1)/n1[1]-x
        C0=mp.matrix([x0,y,z0]);C1=mp.matrix([x,y1,z1]);C2=mp.matrix([-(S-1)/2,(S-1)/2,-(S-1)*H/2])
        return S,[C0,C1,C2,T*C2,T*C1,T*C0],M
    raise ValueError(n)
def decimal(v):return mp.nstr(v,65,min_fixed=-100,max_fixed=100)
def ceil65(v):
    x=int(mp.ceil(v*10**65));return str(x//10**65)+'.'+str(x%10**65).zfill(65)
def main():
    OUT.mkdir(exist_ok=True)
    for n in range(2,8):
        S,C,M=decode(n)
        record={'piece':'antiprism4','container':'antiprism4','n':n,'s_full':ceil65(S*DILATION),
        'pieces':[[decimal(x*DILATION)for x in c]+[decimal(x)for x in quaternion(m)]for c,m in zip(C,M)],
        'found_by':'PingYou Ltd','credit':'PingYou Ltd (PY)',
        'method':'Exact contact construction with rational native-coordinate export',
        'construction':{'endpoint_decimal':decimal(S),'exact_source':f'../exact/n{n:02d}/'+('endpoint.json' if n in[2,4,7]else 'root.json' if n in[3,5]else 'certificate.json'),
        'native_center_dilation':'1.000000000001','native_scale_rule':'construction endpoint times native_center_dilation, rounded upward to 65 decimal places','native_scale_excess':decimal(S*(DILATION-1))}}
        if n in[2,4]:record['certificate_refined_by']='PingYou Ltd (PY)'
        if n==2:
            record['found_by']='Alejandro Zarzuelo'
            record['credit']='Alejandro Zarzuelo; soft-to-rigid method by Yohei Nakajima'
            record['method']='Exact reconstruction and native-certificate refinement of the cited construction'
            record['source_record']='records/community/ap4inap4/ap4inap4_n02_pingyou_20261013.json'
        if n==4:
            record['source_record']='records/community/ap4inap4/ap4inap4_n04_submission_81_6eda01c3edcc.json'
        (OUT/f'ap4inap4_n{n:02d}_py.json').write_text(json.dumps(record,indent=2)+'\n')
        print(n,record['s_full'])
if __name__=='__main__':main()
