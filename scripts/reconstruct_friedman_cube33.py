import hashlib,subprocess
import itertools,json,math,pathlib,sys
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from scipy.spatial.transform import Rotation
REPO=pathlib.Path(__file__).resolve().parents[1]
HERE=REPO/'logs'/'friedman-cube33-reconstruction'
HERE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO/'src'))
from exact import Problem,pair_gaps
S=3+1/math.sqrt(2);r=(S-1)/2
centers=[];rots=[];labels=[]
for c in itertools.product([-r,-r+1,r-1,r],repeat=3):
    centers.append(c);rots.append(np.eye(3));labels.append('axis grid')
for axis in range(3):
 for sign in [-1,1]:
  for a,b in itertools.product([-.5,.5],repeat=2):
    c=np.zeros(3);c[axis]=sign*r
    other=[i for i in range(3)if i!=axis]
    c[other[0]]=a;c[other[1]]=b
    centers.append(c);rots.append(Rotation.from_rotvec(np.eye(3)[axis]*math.pi/4).as_matrix());labels.append('face45')
centers.append(np.zeros(3));rots.append(np.eye(3));labels.append('center')
pb=Problem('cube','cube')
C=np.asarray(centers)*pb.edge
pairs=np.array(list(itertools.combinations(range(len(C)),2)))
gap=pair_gaps(pb,C,rots,pairs)
conflicts=pairs[gap < -1e-8]
row=np.repeat(np.arange(len(conflicts)),2)
col=conflicts.reshape(-1)
A=coo_matrix((np.ones(len(row)),(row,col)),shape=(len(conflicts),len(C))).tocsc()
print('Finite reconstruction candidates',len(C),'conflicts',len(conflicts),flush=True)
result=milp(-np.ones(len(C)),integrality=np.ones(len(C)),bounds=Bounds(0,1),constraints=LinearConstraint(A,-np.inf,1),options={'time_limit':40,'mip_rel_gap':0.0})
if result.x is None:raise RuntimeError(result.message)
indices=np.where(result.x>.5)[0]
print('Reconstruction cardinality',len(indices),result.message,flush=True)
if len(indices)>=33:
    quats=[]
    for i in indices[:33]:
        q=Rotation.from_matrix(rots[i]).as_quat();quats.append([q[3],*q[:3]])
    out={'piece':'cube','container':'cube','C':C[indices[:33]].tolist(),'Q':quats,'source':'https://erich-friedman.github.io/packing/cubincub/','published_bound':S,'reconstruction':'Finite candidate reconstruction from axis-grid shell, 45-degree face cubes, and central cube; matching numeric bound, not a claim of the original author pose.'}
    (HERE/'cube33-candidate.json').write_text(json.dumps(out,indent=2)+'\n')

PACKAGE=REPO
sys.path.insert(0,str(REPO/'src'))
from claim import make_claim_fast
from exact import SOL
candidate_path=HERE/'cube33-candidate.json'
candidate=json.loads(candidate_path.read_text())
dest=PACKAGE/'docs'/'literature'/'external'/'friedman-cube33-reconstruction.json'
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(candidate_path.read_bytes())
source={'kind':'external','author':'Erich Friedman (1998); matching-bound coordinate reconstruction',
 'url':'https://erich-friedman.github.io/packing/cubincub/',
 'original_diagram_url':'https://erich-friedman.github.io/packing/cubincub/cube33.gif',
 'source_file':dest.relative_to(PACKAGE).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'historical_author':'Erich Friedman','historical_year':1998,
 'published_s_full':candidate['published_bound'],'published_expression':'3 + 1/sqrt(2)',
 'derivation':'Reconstruct a feasible matching-bound configuration from an axis-grid shell, 45-degree face cubes and a central cube using a finite independent-set model. The resulting 33 poses are separately certified. These are project-generated matching-bound coordinates, not a claim of the original author coordinate file or a new improvement over the 1998 bound.',
 'derivation_by':'Polyhedra in Polyhedra Packing project','reconstructed_on':'2026-10-13',
 'normalization':'Candidate coordinates are in the optimization engine internal cube units. Convert to canonical unit-edge cube poses and add standard1e-7pair/wallclearance. No further shape optimization.',
 'method':'Reconstruction of a previously published cubic packing bound; finite axis-grid and45-degree-face candidate search'}
rid='cubincub_n33_friedman_reconstruction'
meta={'record_id':rid,'title':'33 unit cubes in a cube — reconstruction of the 1998 bound','found_by':source['author'],
 'credit':'Historicalbound by Erich Friedman (1998). Matching-bound coordinates reconstructed by the project; not asserted to be the originalpublishedpose.',
 'method':source['method'],'date':'2026-10-13','source':source,'search':{'move':'historicalconstructionreconstruction'},
 'volume_lower_bound':33**(1/3),'closed_form_conjecture':None}
claim=make_claim_fast({'piece':'cube','container':'cube','C':np.asarray(candidate['C']),'Q':candidate['Q']},GAP=1e-7,WALL=1e-7,meta=meta)
claim['s_tight']=None;claim['density']=33/claim['s_full']**3
folder=PACKAGE/'records'/'external'/'cubincub';folder.mkdir(parents=True,exist_ok=True)
path=folder/(rid+'.json');path.write_text(json.dumps(claim,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
for script,suffix in [('verify.py','.verify.txt'),('certify_exact.py','.certify.txt')]:
    check=subprocess.run([sys.executable,'-X','utf8',str(REPO/script),str(path)],capture_output=True,text=True,encoding='utf-8')
    path.with_suffix(suffix).write_text(check.stdout+check.stderr,encoding='utf-8')
    if check.returncode:raise RuntimeError(check.stdout+check.stderr)
entry={'problem':'cubincub','n':33,'file':path.relative_to(PACKAGE).as_posix(),'published_value':candidate['published_bound'],
 'published_expression':'3 + 1/sqrt(2)','author':source['author'],'url':source['url'],
 'value_precision':'reconstruction matching the published exact expression within standardclearance; originalposes not asserted',
 'kind':'coordinates','derivation':source['derivation']}
(HERE/'cube33-reconstructed-registry-entry.json').write_text(json.dumps(entry,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Cubes33 reconstruction CERTIFIED:',claim['s_full'],'publishedformula',candidate['published_bound'])

registry_path=REPO/'docs'/'external_records.json'
registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {'entries':[]}
registry['entries']=[old for old in registry.get('entries',[]) if old.get('file')!=entry['file']]+[entry]
registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
