from pathlib import Path
from fractions import Fraction
import json, shutil, sys, importlib.util
import mpmath as mp
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

HERE=Path(__file__).resolve().parent
SOURCE=HERE
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
OUTPUT=args.output_dir
OUTPUT.mkdir(parents=True,exist_ok=True)
mp.mp.dps=110
alpha=mp.root(2,4)
h=alpha**3/2
factor=1+mp.mpf('1e-12')

def qval(x):
    x=Fraction(x);return mp.mpf(x.numerator)/x.denominator

def field(v):return sum(qval(c)*alpha**i for i,c in enumerate(v))
def value(v):return mp.nstr(v,48)
def ceil_decimal(v,places=45):
    denominator=10**places
    z=int(mp.ceil(v*denominator))
    return f'{z//denominator}.{z%denominator:0{places}d}'
def quat(M):
    # Diagonal maximum avoids loss of precision near half-turns.
    ds=[1+M[0][0]+M[1][1]+M[2][2],1+M[0][0]-M[1][1]-M[2][2],1-M[0][0]+M[1][1]-M[2][2],1-M[0][0]-M[1][1]+M[2][2]]
    k=max(range(4),key=lambda i:ds[i]);q=[mp.mpf(0)]*4;q[k]=mp.sqrt(ds[k])/2;t=4*q[k]
    if k==0:q[1:]=[(M[2][1]-M[1][2])/t,(M[0][2]-M[2][0])/t,(M[1][0]-M[0][1])/t]
    elif k==1:q[0]=(M[2][1]-M[1][2])/t;q[2]=(M[0][1]+M[1][0])/t;q[3]=(M[0][2]+M[2][0])/t
    elif k==2:q[0]=(M[0][2]-M[2][0])/t;q[1]=(M[0][1]+M[1][0])/t;q[3]=(M[1][2]+M[2][1])/t
    else:q[0]=(M[1][0]-M[0][1])/t;q[1]=(M[0][2]+M[2][0])/t;q[2]=(M[1][2]+M[2][1])/t
    return q

def save(n,S,centers,matrices,method,lineage=None,quaternions=None):
    rec={'piece':'antiprism4','container':'antiprism4','n':n,'s_full':ceil_decimal(S*factor),'pieces':[[value(x*factor) for x in c]+(quaternions[i] if quaternions is not None else [value(x) for x in quat(M)])for i,(c,M) in enumerate(zip(centers,matrices))],'found_by':'PingYou Ltd (PY)','credit':'PingYou Ltd (PY)','method':method,'publication_permission':'Permission granted by the contributor to publish this construction, coordinates and certificate.'}
    if lineage:rec['lineage']=lineage
    p=OUTPUT/f'ap4inap4_n{n:02d}.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(rec,indent=2)+'\n')
    return {'n':n,'file':p.name,'endpoint':value(S),'native_s_full':rec['s_full'],'uniform_dilation_factor':'1.000000000001','native_scale_overhead':value(S*(factor-1))}

results=[]
d=json.loads((SOURCE/'n17/n17_exact.json').read_text());C=[[field(v)for v in row]for row in d['physical_centers']];M=[[[field(v)for v in row]for row in mat]for mat in d['frames']]
for n in [15,16,17]:
    keep=list(range(n));lineage=None if n==17 else {'operation':'delete_pieces','parent':'ap4inap4_n17.json','parent_zero_based_indices_kept':keep,'parent_zero_based_indices_deleted':list(range(n,17))}
    results.append(save(n,mp.mpf(3),[C[i]for i in keep],[M[i]for i in keep],'Exact construction in Q(2^(1/4)); positive-clearance rational export.',lineage))

for n in [18,19]:
    folder=SOURCE/f'n{n}'
    for name in ['check_root_packing','interval_root','quartic']:sys.modules.pop(name,None)
    sys.path.insert(0,str(folder))
    import check_root_packing as geometry
    import interval_root as root
    X=root.root_box();nc=3*n;np=22 if n==18 else 57
    p=X[nc:nc+np]
    if n==18:MI=geometry.frames(p)
    else:MI=geometry.frames(p,json.loads((folder/'contact_input.json').read_text())['base_ids'])
    iv=lambda v:mp.mpf(v[0]+v[1])/(2*root.D)
    C=[[iv(v)for v in X[i*3:i*3+3]]for i in range(n)]
    M=[[[iv(v)for v in row]for row in mat]for mat in MI]
    results.append(save(n,iv(X[-1]),C,M,f'Certified {nc+np+1}-equation algebraic contact root; positive-clearance rational export.'))
    sys.path.pop(0)

d=json.loads((SOURCE/'n20/endpoint.json').read_text())
C=[[field(v)for v in row]for row in d['physical_centers']]
M=[[[field(v)for v in row]for row in mat]for mat in d['frames']]
results.append(save(20,field(d['scale_coefficients']),C,M,'Exact rational-quaternion contact construction; positive-clearance rational export.',quaternions=d['quaternions_wxyz']))
(OUTPUT/'high_export_metadata.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
