"""Import frozen Berthold et al. Platonic poses without transferring discovery credit.

All geometry is recovered from published mesh vertices, rather than depending on
ambiguous Euler conventions. The entire source container is aligned with the
project's canonical solid, and all source vertices are matched after conversion.
"""
import copy,base64,concurrent.futures as cf,hashlib,itertools,json,math,pathlib,re,subprocess,sys,threading,time,urllib.request
import numpy as np
from scipy.spatial.transform import Rotation
REPO=pathlib.Path(__file__).resolve().parents[1]
HERE=REPO/'logs'/'kamp-import'
HERE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO/'src'))
from claim import make_claim_fast
from exact import Problem,SOL
REV='27f71632d8655ae4b6a049410a401976748b94e3'
PACKAGE=REPO
AUTHOR='Timo Berthold, Dominik Kamp, Gioni Mexi, Sebastian Pokutta and Imre Pólik'
NAMES={1:'tetrahedron',2:'octahedron',3:'cube',4:'icosahedron',5:'dodecahedron'}
ABBR={'tetrahedron':'tet','octahedron':'oct','cube':'cub','icosahedron':'ico','dodecahedron':'dod'}
BODY={s:np.array(SOL[s]['V'])/float(SOL[s]['circumradius']) for s in NAMES.values()}
EDGES={s:1/float(SOL[s]['circumradius']) for s in NAMES.values()}

def decode(v):return np.frombuffer(base64.b64decode(v['bdata']),dtype=v['dtype']) if isinstance(v,dict) else np.asarray(v)
def vertices(t):return np.column_stack([decode(t[k]) for k in 'xyz'])
def point_error(a,b):return float(np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(-1)).min(1).max())

def rigid_fit(canonical,target):
    """Return a proper row-vector map canonical->target and fixed vertex triples.

    The 3 points are linearly independent about the common zero center. Candidate
    source triples are chosen by identical Gram matrices and tested against ALL
    vertices. This avoids factorial full-permutation searches for dodecahedra.
    """
    choices=list(itertools.combinations(range(len(canonical)),3))
    triple=max(choices,key=lambda t:abs(np.linalg.det(canonical[list(t)])))
    X=canonical[list(triple)];gram=X@X.T
    triples=np.array(list(itertools.permutations(range(len(target)),3)))
    Ys=target[triples];grams=np.einsum('nij,nkj->nik',Ys,Ys)
    matches=np.where(np.max(np.abs(grams-gram),axis=(1,2))<1e-9)[0]
    best=None
    for i in matches:
        Y=Ys[i]
        u,_,vt=np.linalg.svd(X.T@Y);mat=u@vt
        if np.linalg.det(mat)<0:continue
        error=point_error(canonical@mat,target)
        if best is None or error<best[0]:best=(error,mat,triple,tuple(triples[i]))
        if error<2e-14:break
    if best is None or best[0]>1e-12:raise ValueError(f'Cannot rigidly match canonical solid to published mesh: {best}')
    return best

def fetch(item):
    l,m,n=item
    rel=f'platonic/l{l}/m{m}/n{n}/platonic_n{n}_m{m}_l{l}'
    files={}
    for ext in ['txt','html']:
        pid=ABBR[NAMES[m]]+'in'+ABBR[NAMES[l]]
        target=PACKAGE/'docs'/'literature'/'external'/f'kamp-{pid}-n{n:02d}.{ext}'
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            url='https://raw.githubusercontent.com/DominikKamp/Packing/'+REV+'/'+rel+'.'+ext
            for attempt in range(3):
                try:target.write_bytes(urllib.request.urlopen(url,timeout=45).read());break
                except Exception:
                    if attempt==2:raise
                    time.sleep(1+attempt)
        files[ext]=target
    return l,m,n,rel,files

def read_traces(files):
    raw=files['html'].read_text()
    match=re.search(r'Plotly.newPlot\(\s*"[^"]+",\s*',raw)
    return json.JSONDecoder().raw_decode(raw[match.end():])[0]

def outer_vertices(traces):
    return np.unique(np.round(np.concatenate([vertices(t) for t in traces if t.get('type')=='scatter3d' and t.get('line',{}).get('color')=='red']),14),axis=0)

# Initialize source vertex order and container maps from real source data before
# using threads; these maps remain read-only and are checked on every instance.
INNER_TRIPLES={};OUTER_MATS={}
for i,solid in NAMES.items():
    item=fetch((i,i,2));traces=read_traces(item[4]);R=float(item[4]['txt'].read_text().splitlines()[1])
    mesh=next(t for t in traces if t.get('type')=='mesh3d')
    V=vertices(mesh);V=V-V.mean(0)
    fit=rigid_fit(BODY[solid],V);INNER_TRIPLES[solid]=(fit[2],fit[3]);inner_error=fit[0]
    outer=outer_vertices(traces)/R
    fit=rigid_fit(BODY[solid],outer);OUTER_MATS[solid]=fit[1].T
    print(f'Canonical {solid} aligned: inner error {inner_error:.2g}; outer error {fit[0]:.2g}',flush=True)

def normalize(item):
    l,m,n,rel,files=item
    piece,container=NAMES[m],NAMES[l]
    pid=ABBR[piece]+'in'+ABBR[container];rid=f'{pid}_n{n:02d}_kamp'
    path=PACKAGE/'records'/'external'/pid/(rid+'.json')
    # Reuse already certified imports from the same frozen publication.
    if path.exists() and path.with_suffix('.verify.txt').exists() and path.with_suffix('.certify.txt').exists() and path.with_suffix('.verify.txt').read_text().strip().splitlines()[-1:] == ['VALID'] and path.with_suffix('.certify.txt').read_text().strip().splitlines()[-1:] == ['CERTIFIED']:
        claim=json.loads(path.read_text(encoding='utf-8'))
        if claim['source']['revision']==REV:
            return {'problem':pid,'n':n,'file':path.relative_to(PACKAGE).as_posix(),'published_value':claim['source']['published_s_full'],'author':AUTHOR,'url':claim['source']['url'],'value_precision':'full coordinates','kind':'coordinates','reused':True}
    Rsource=float(files['txt'].read_text().splitlines()[1]);published=Rsource/(float(SOL[container]['circumradius'])*EDGES[piece])
    traces=read_traces(files);meshes=[t for t in traces if t.get('type')=='mesh3d']
    if len(meshes)!=n:raise ValueError((pid,n,len(meshes)))
    global_mat=OUTER_MATS[container]
    outer=outer_vertices(traces)/Rsource@global_mat
    outer_error=point_error(outer,BODY[container])
    if len(outer)!=len(BODY[container]) or outer_error>1e-12:raise ValueError((pid,n,'outer match',outer_error))
    ct,st=INNER_TRIPLES[piece]
    canonical=BODY[piece];X=canonical[list(ct)]
    centers,quats=[],[];max_error=0.
    for t in meshes:
        V=vertices(t)@global_mat;center=V.mean(0);local=V-center
        Y=local[list(st)];u,_,vt=np.linalg.svd(X.T@Y);rot_row=u@vt
        if np.linalg.det(rot_row)<0:raise ValueError((pid,n,'reflection'))
        error=point_error(canonical@rot_row,local);max_error=max(max_error,error)
        if error>1e-12:raise ValueError((pid,n,'piece match',error))
        quat=Rotation.from_matrix(rot_row.T).as_quat()
        centers.append(center/EDGES[piece]);quats.append([quat[3],*quat[:3]])
    sources={}
    for ext,source_path in files.items():
        dest=PACKAGE/'docs'/'literature'/'external'/f'kamp-{pid}-n{n:02d}.{ext}'
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source_path.read_bytes())
        sources[ext]={'file':dest.relative_to(PACKAGE).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    source={'kind':'external','author':AUTHOR,'repository':'https://github.com/DominikKamp/Packing','revision':REV,
      'url':'https://github.com/DominikKamp/Packing/blob/'+REV+'/'+rel+'.html',
      'source_file':sources['html']['file'],'sha256':sources['html']['sha256'],
      'numeric_source_file':sources['txt']['file'],'numeric_source_sha256':sources['txt']['sha256'],
      'paper':'Out-of-the-Box Global Optimization for Packing Problems: New Models and Improved Solutions (2026)',
      'paper_url':'https://arxiv.org/abs/2605.04850','paper_publication_date':'2026-05-06',
      'source_commit_date':'2026-04-16T22:48:50Z','published_s_full':published,'published_circumradius':Rsource,
      'source_to_canonical_row_matrix':global_mat.tolist(),'outer_conversion_max_error':outer_error,'vertex_conversion_max_error':max_error,
      'normalization':f'Original pieces have unit circumradius, so {piece} edge length is {EDGES[piece]:.17g}; centers divided by this edge. Apply a proper rigid rotation to align ALL published {container} outer vertices with the project canonical solid (normalized discrepancy {outer_error:.3g}). Fit piece rotations to ALL source mesh vertices (maximum discrepancy {max_error:.3g}). Convert container circumradius into edge ratio R/({SOL[container]["circumradius"]:.17g} * {EDGES[piece]:.17g}). Add standard 1e-7 clearance without transferring discovery credit.',
      'method':'Published global-optimization construction from the Berthold, Kamp, Mexi, Pokutta and Pólik study','imported_on':'2026-10-13'}
    meta={'record_id':rid,'title':f'{n} unit {piece}s in a {container}','found_by':AUTHOR,
      'credit':f'Published construction by {AUTHOR}; imported and checked without transferring discovery credit.',
      'method':source['method'],'date':'2026-05-06','source':source,'search':{'move':'published construction'},
      'volume_lower_bound':(n*SOL[piece]['volume']/SOL[container]['volume'])**(1/3),'closed_form_conjecture':None}
    pb=Problem(piece,container)
    claim=make_claim_fast({'piece':piece,'container':container,'C':np.asarray(centers)*pb.edge,'Q':quats},GAP=1e-7,WALL=1e-7,meta=meta)
    claim['s_tight']=None;claim['density']=n*SOL[piece]['volume']/(SOL[container]['volume']*claim['s_full']**3)
    candidate=HERE/(rid+'.json')
    candidate.write_text(json.dumps(claim,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    for script,suffix in [('verify.py','.verify.txt'),('certify_exact.py','.certify.txt')]:
        check=subprocess.run([sys.executable,'-X','utf8',str(REPO/script),str(candidate)],capture_output=True,text=True,encoding='utf-8')
        candidate.with_suffix(suffix).write_text(check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise RuntimeError(f'{rid} {script} failed {check.stdout} {check.stderr}')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(candidate.read_bytes())
    for suffix in ['.verify.txt','.certify.txt']:path.with_suffix(suffix).write_bytes(candidate.with_suffix(suffix).read_bytes())
    return {'problem':pid,'n':n,'file':path.relative_to(PACKAGE).as_posix(),'published_value':published,'author':AUTHOR,'url':source['url'],'value_precision':'full coordinates','kind':'coordinates'}

# Download all25×29 cases (one absent source is represented by an explicit subset). Process newly exposed families first.
EXISTING={(1,1),(3,3),(2,2),(4,4),(5,5),(5,4),(4,5),(3,2),(2,3)}
families=sorted([(l,m) for l in NAMES for m in NAMES],key=lambda pair:(pair in EXISTING,pair))
items=[(l,m,n) for l,m in families for n in range(2,31)]
# Frozen GitHub source tree contains749of750 n1–30cases. This one file
# is absent; it must never be described as a published n28 result.
missing=[(3,4,28)]
items=[item for item in items if item not in missing]
(HERE/'kamp-missing-platonic-cases.json').write_text(json.dumps(missing),encoding='utf-8')
print(f'Downloading {len(items)} published configurations; absent source cases {missing}...',flush=True)
with cf.ThreadPoolExecutor(max_workers=12) as pool:
    downloaded=list(pool.map(fetch,items))
print('Downloaded; normalizing and certifying with four workers...',flush=True)
entries=[];errors=[]
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    pending={pool.submit(normalize,item):item[:3] for item in downloaded}
    for future in cf.as_completed(pending):
        ident=pending[future]
        try:entries.append(future.result())
        except Exception as exc:errors.append({'case':ident,'error':str(exc)});print('FAILED',ident,repr(exc),flush=True)
        if (len(entries)+len(errors))%10==0:
            (HERE/'all-platonic-kamp-progress.json').write_text(json.dumps({'certified':len(entries),'failed':errors,'entries':entries},indent=2,ensure_ascii=False),encoding='utf-8')
            print(f'CERTIFIED {len(entries)}/{len(items)}; failed{len(errors)}; justprocessed{ident}',flush=True)
if errors:
    (HERE/'all-platonic-kamp-errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    raise RuntimeError(f'{len(errors)} source imports failed verification; registry was not changed.')

folder=PACKAGE/'records'/'external'/'icoincub'
basepath=folder/'icoincub_n29_kamp.json'
base=json.loads(basepath.read_text(encoding='utf-8'))
assert base['n']==29 and len(base['pieces'])==29
assert basepath.with_suffix('.verify.txt').read_text().strip().splitlines()[-1:] == ['VALID']
assert basepath.with_suffix('.certify.txt').read_text().strip().splitlines()[-1:] == ['CERTIFIED']
claim=copy.deepcopy(base)
claim['n']=28;claim['pieces']=claim['pieces'][:28]
claim['record_id']='icoincub_n28_kamp_from_n29'
claim['title']='28 unit icosahedra in a cube (subset of a published 29-piece construction)'
claim['date']='2026-10-13'
claim['density']=base['density']*28/29
claim['volume_lower_bound']=base['volume_lower_bound']*(28/29)**(1/3)
claim['source']['base_published_s_full']=base['source']['published_s_full']
claim['source']['published_s_full']=base['s_full']
claim['source']['published_n']=29
claim['source']['derivation']='Delete piece index28 (zero-based) from the certified normalized copy of the published n29 configuration. Keep the identical container size, all remaining centers, all remaining orientations and all established clearances. The upstream publication has no n28 configuration file; this is an explicitly derived subset.'
claim['source']['derivation_by']='Polyhedra in Polyhedra Packing project'
claim['source']['derived_from']={'record_id':base['record_id'],'file':basepath.relative_to(PACKAGE).as_posix(),'n':29,'url':base['source']['url']}
claim['source']['normalization']=base['source']['normalization']+' Subsequently remove the final piece to obtain a valid28-piece subset at the SAME certified container size; no additional optimization.'
claim['credit']='Base 29-piece arrangement by '+claim['source']['author']+'; 28-piece subset generated by deleting one piece. This is not a claim that the source published an n28 result.'
path=folder/'icoincub_n28_kamp_from_n29.json'
candidate=HERE/path.name
candidate.write_text(json.dumps(claim,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
for script,suffix in [('verify.py','.verify.txt'),('certify_exact.py','.certify.txt')]:
    check=subprocess.run([sys.executable,'-X','utf8',str(REPO/script),str(candidate)],capture_output=True,text=True,encoding='utf-8')
    candidate.with_suffix(suffix).write_text(check.stdout+check.stderr,encoding='utf-8')
    if check.returncode:raise RuntimeError(check.stdout+check.stderr)
path.write_bytes(candidate.read_bytes())
for suffix in ['.verify.txt','.certify.txt']:path.with_suffix(suffix).write_bytes(candidate.with_suffix(suffix).read_bytes())
entry={'problem':'icoincub','n':28,'file':path.relative_to(PACKAGE).as_posix(),'published_value':base['s_full'],'author':base['source']['author'],'url':base['source']['url'],'value_precision':'derived subset of published n29; certified at the unchanged n29 container size','kind':'coordinates','derivation':claim['source']['derivation'],'derived_from':claim['source']['derived_from']}
entries.append(entry)
print('icoincub28 derived from29, exact/floatCERTIFIED at unchanged s=',claim['s_full'])

entries.sort(key=lambda r:(r['problem'],r['n']))
(HERE/'all-platonic-kamp-normalized-registry-entries.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(HERE/'all-platonic-kamp-errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('DONE',len(entries),'certified',len(errors),'failed',flush=True)


# Merge by exact imported file, preserving every other original author, catalogue
# source, community record and external reconstruction already registered.
registry_path=REPO/'docs'/'external_records.json'
registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {'entries':[]}
updated_files={entry['file'] for entry in entries}
registry['entries']=[entry for entry in registry.get('entries',[]) if entry.get('file') not in updated_files]+entries
registry['checked_on']='2026-10-13'
registry['scope']='Published and certified coordinate sources for all 25 Platonic pairs, n=2–30; original cube/octahedron catalogue comparisons retained. 724 direct Kamp source cases and one explicitly derived 28-piece subset. This is not a global completeness or optimality claim.'
registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Registered 724 direct source configurations and one explicitly derived subset; original source attributions preserved.')
