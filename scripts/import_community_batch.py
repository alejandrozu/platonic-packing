"""Read public contributed archives as data; certify using our current upstream.

All path/hash and geometry bindings are checked. The exact certifier is imported
without edits; its canonical solid cache is reused inside each worker process.
No contributor Python is executed.
"""
import argparse, contextlib, hashlib, io, json, math, multiprocessing, os, pathlib, re, subprocess, sys, time, zipfile
from fractions import Fraction as Q
from urllib.request import urlopen
if not __debug__:
    raise SystemExit('Exact canonical-solid checks require assertions; do not use Python -O.')

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(os.environ.get('PACKING_COMMUNITY_ARCHIVES', ROOT / '.community-import')).resolve()
sys.path.insert(0, str(ROOT))
import certify_general as U
import verify_general as V

BATCHES = [
    ('construction', HERE / 'constructions47/pingyou-3d-constructions-2026-10-13-v2', 6,
     'https://github.com/user-attachments/files/33363589/pingyou-3d-constructions-47-2026-10-13.zip',
     '38236a05eb54e73799344a52288100efb17d1a9c8a823709dfb256eb93e1871d'),
    ('same_nominal', HERE / 'refinements4/pingyou-four-shared-nominal-refinements-2026-10-13-v1', 6,
     'https://github.com/user-attachments/files/33363596/pingyou-four-shared-nominal-refinements-2026-10-13.zip',
     'cdce02d8f6e717dd2b6e5bf5af0cb2cb12566e6f7c08be76ce2c705adaf682b6'),
    ('wall_padding', HERE / 'refinements1357/pingyou-3d-certificate-refinements-2026-10-13-v1', 7,
     'https://github.com/user-attachments/files/33363620/pingyou-3d-certificate-refinements-2026-10-13-v1.zip',
     '48285558f37bc071c2f368796874cce5f4442edcce2c71f931ebf348a27cb2d1'),
]
ARCHIVE_NAMES={'construction':'constructions47.zip','same_nominal':'refinements4.zip','wall_padding':'refinements1357.zip'}

def prepare():
    """Download SHA-bound public archives and extract JSON data only."""
    HERE.mkdir(parents=True,exist_ok=True)
    for kind,base,issue,url,sha in BATCHES:
        archive=HERE/ARCHIVE_NAMES[kind]
        if not archive.exists():
            with urlopen(url,timeout=60)as response:archive.write_bytes(response.read(64*1024*1024))
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==sha, f'archive hash: {kind}'
        destination=base.parent.resolve();destination.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(archive)as z:
            members=z.infolist();assert len(members)<=20000 and sum(i.file_size for i in members)<=512*1024*1024
            for member in members:
                name=member.filename.replace('\\','/');pure=pathlib.PurePosixPath(name)
                assert not pure.is_absolute() and '..'not in pure.parts and ':'not in name
                path=(destination/pathlib.Path(*pure.parts)).resolve()
                assert path.is_relative_to(base.resolve()), 'unexpected archive top folder'
                if not name.endswith('.json'):continue
                assert member.file_size<=20*1024*1024
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(member))
        print(kind,'SHA-256 verified; JSON extracted',flush=True)

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))

def checked_file(base, rel, expected):
    base = pathlib.Path(base).resolve(); path = (base / rel).resolve()
    assert path.is_relative_to(base), 'unsafe archive path'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'hash: {rel}'
    return path

def audit():
    registry = load(ROOT / 'docs/external_records.json')['entries']
    community_path=ROOT/'docs/community_records.json'
    community=load(community_path)['entries'] if community_path.exists() else []
    tasks = []; excluded = []; batches = []
    for kind, base, issue, url, archive_sha in BATCHES:
        archive=HERE/ARCHIVE_NAMES[kind]
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==archive_sha, f'archive hash: {kind}'
        manifest = load(base / 'MANIFEST.json')
        assert manifest['count'] == len(manifest['cases'])
        batches.append({'kind': kind, 'count': manifest['count'], 'archive': url, 'sha256': archive_sha})
        for e in manifest['cases']:
            file = checked_file(base, e.get('file', e.get('witness')), e.get('sha256', e.get('witness_sha256')))
            rec = load(file); rid = e['record_id']; pid = rid.split('_')[0]; n = rec['n']
            assert n == len(rec['pieces']) and 2 <= n <= 200
            assert all(len(p) == 7 and all(type(v) in (int, float) and math.isfinite(v) for v in p) for p in rec['pieces'])
            assert type(rec['s_full']) in (float, int) and math.isfinite(rec['s_full']) and rec['s_full'] > 0
            assert all(sum(Q(v)**2 for v in p[3:]) > 0 for p in rec['pieces'])
            own_path = ROOT / 'records' / pid / f'{pid}_n{n:02d}.json'
            candidates = [(load(own_path), own_path)] if own_path.exists() else []
            for x in registry+community:
                if x['problem'] != pid or x['n'] != n or (x in registry and x['kind'] != 'coordinates'): continue
                ep = (ROOT / x['file']).resolve();assert ep.is_relative_to(ROOT/'records')
                cert = ep.with_suffix('.certify.txt')
                if not cert.exists(): continue
                text = cert.read_text(encoding='utf-8')
                if 'CERTIFIED' in text and 'NOT CERTIFIED' not in text: candidates.append((load(ep), ep))
            cur, curpath = min(candidates, key=lambda a:a[0]['s_full']) if candidates else (None, None)
            task = {'record_id': rid, 'kind': kind, 'base': str(base), 'file': str(file), 'entry': e,
                    'issue': issue, 'archive': url, 'archive_sha256': archive_sha,
                    'scale': rec['s_full'], 'baseline_scale': cur['s_full'] if cur else None,
                    'baseline_file': curpath.relative_to(ROOT).as_posix() if curpath else None,
                    'baseline_author': cur.get('found_by') if cur else None}
            if cur and not rec['s_full'] < cur['s_full'] - 1e-12:
                task['reason'] = 'does not beat latest certified coordinate baseline'; excluded.append(task); continue
            published = [x for x in registry if x['problem']==pid and x['n']==n]
            if published:
                best = min(published, key=lambda a:a['published_value'])
                task['published_reference'] = {k:best.get(k) for k in ('published_value','author','url','kind')}
                task['behind_published_reference'] = rec['s_full'] > best['published_value'] + 1e-5
            tasks.append(task)
    # When archives duplicate a case retain the best candidate, not the source order.
    chosen = {}
    for t in tasks:
        prev = chosen.get(t['record_id'])
        if prev is None or t['scale'] < prev['scale']:
            if prev: prev['reason'] = 'overtaken by another supplied witness'; excluded.append(prev)
            chosen[t['record_id']] = t
        else:
            t['reason'] = 'overtaken by another supplied witness'; excluded.append(t)
    out = {'baseline_commit': subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
           'batches': batches, 'eligible': list(chosen.values()), 'excluded': excluded}
    (HERE / 'audit.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps({'baseline': out['baseline_commit'], 'eligible':len(chosen), 'excluded':len(excluded),
                      'by_kind': {k:sum(t['kind']==k for t in chosen.values()) for k, *_ in BATCHES},
                      'excluded_records':[(t['record_id'],t['scale'],t['baseline_scale']) for t in excluded]}, indent=2))

def direct_exact_planes(task):
    """Independent full replay: exact walls and every pair, using banked normals
    solely as proposals. Does not trust the author's PASS receipts/logs.
    """
    e=task['entry']; base=pathlib.Path(task['base']); d=load(task['file'])
    old=load(checked_file(base,e['predecessor'],e['predecessor_sha256']))
    plane=load(checked_file(base,e['planes'],e['planes_sha256']))
    pcs=d['pieces']; n=d['n']; size=Q(d['s_full'])
    if e['predecessor_encoding']=='native':
        oldpcs=old['pieces']; oldsize=Q(old['s_full'])
        assert d.get('container_center',[0,0,0])==old.get('container_center',[0,0,0])
        for k in ('found_by','credit','method','source'): assert d.get(k)==old.get(k), f'changed original {k}'
    else:
        assert e['predecessor_encoding']=='konoha_cube'
        oldsize=Q(old['S']); oldpcs=[[*(Q(x)-oldsize/2 for x in o['c']),*o['q']] for o in old['cubes']]
    assert len(oldpcs)==n and all(all(Q(x)==Q(y) for x,y in zip(a,b)) for a,b in zip(pcs,oldpcs)), 'changed inherited geometry'
    assert size==Q(e['new_scale_exact']) and oldsize==Q(e['old_scale_exact'])
    assert oldsize-size==Q(e['strict_decrease_exact'])>0
    assert plane['record_sha256']==e['witness_sha256']
    P,C=U.get_solid(d['piece']),U.get_solid(d['container']); X=[]; centers=[]
    for owner in pcs:
        R=[[U.fx(q) for q in row] for row in U.rot(owner[3:])]; c=list(map(U.fx,owner[:3])); centers.append(list(map(Q,owner[:3])))
        X.append([[U.fadd(c[k],U.fdot(R[k],v)) for k in range(3)] for v in P.V])
    cc=list(map(U.fx,d.get('container_center',[0,0,0]))); walls=0; minwall=None
    for vertices in X:
        for x in vertices:
            y=[U.fsub(x[k],cc[k]) for k in range(3)]
            for normal,beta in zip(C.N,C.B):
                slack=U.fsub(U.fmul(U.fx(size),beta),U.fdot(normal,y))[0]
                assert slack>0, 'wall touch or overlap'; walls+=1; minwall=slack if minwall is None else min(minwall,slack)
    planes={}
    for p in plane['planes']:
        i,j=p['i'],p['j']; assert type(i)is int and type(j)is int and 0<=i<j<n and (i,j)not in planes
        assert len(p['normal'])==3
        planes[i,j]=list(map(U.fx,map(Q,p['normal'])))
    pairs=far=0; mingap=None
    for i in range(n):
        for j in range(i+1,n):
            if(i,j)in planes:
                u=planes[i,j]; gap=min(U.fdot(u,x)[0]for x in X[j])-max(U.fdot(u,x)[1]for x in X[i])
                assert gap>0, 'pair touch or overlap'; mingap=gap if mingap is None else min(mingap,gap)
            else:
                distance=sum((centers[i][k]-centers[j][k])**2 for k in range(3))
                assert distance*U.ONE>4*P.R2up, 'unproved far pair'; far+=1
            pairs+=1
    text=(f'solid check: {P.check}\n'+(f'solid check: {C.check}\n' if C is not P else '')+
          f'containment: {walls} exact outward-interval vertex/face inequalities, smallest slack >= {minwall/U.ONE:.3e} (times |normal|)\n'+
          f'disjointness: {pairs-far} pairs checked against explicit rational plane proposals, smallest gap >= {(mingap or 0)/U.ONE:.3e}; {far} exact circumradius distance checks\n'+
          f'CERTIFIED: {n} {d["piece"]} in s = {d["s_full"]} x {d["container"]}\n'+
          'Independent full geometry replay using current certify_general.py canonical solids and 170-bit outward arithmetic; contributor code was not executed.\n')
    return text, {'walls':walls,'pairs':pairs,'far_pairs':far,'wall_slack':minwall/U.ONE,'plane_margin':(mingap or 0)/U.ONE}

def replay_one(task):
    t=time.time(); rid=task['record_id']; folder=HERE/'replay'/task['kind']; folder.mkdir(parents=True,exist_ok=True)
    try:
        if task['kind']=='wall_padding': exact,stats=direct_exact_planes(task)
        else:
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture): code=U.main(task['file'])
            exact=capture.getvalue(); assert code==0 and 'NOT CERTIFIED' not in exact; stats={}
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf): fcode=V.main(task['file'])
        floatlog=buf.getvalue()
        assert fcode==0, f'floating check failed: {floatlog}'
        (folder/f'{rid}.certify.txt').write_text(exact,encoding='utf-8')
        (folder/f'{rid}.verify.txt').write_text(floatlog,encoding='utf-8')
        receipt={'record_id':rid,'kind':task['kind'],'status':'PASS','scale':task['scale'],'seconds':round(time.time()-t,3),
                 'witness_sha256':hashlib.sha256(pathlib.Path(task['file']).read_bytes()).hexdigest(),**stats}
    except Exception as err:
        receipt={'record_id':rid,'kind':task['kind'],'status':'FAIL','error':str(err),'seconds':round(time.time()-t,3)}
    (folder/f'{rid}.receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return receipt

def replay(workers,kind):
    tasks=load(HERE/'audit.json')['eligible']
    if kind: tasks=[t for t in tasks if t['kind']in kind]
    tasks=[t for t in tasks if not (HERE/'replay'/t['kind']/f'{t["record_id"]}.receipt.json').exists()]
    with multiprocessing.Pool(workers) as pool:
        for i,r in enumerate(pool.imap_unordered(replay_one,tasks,chunksize=4),1):
            if i%20==0 or r['status']!='PASS': print(json.dumps({'processed':i,'total':len(tasks),**r}),flush=True)
    receipts=[load(p)for p in (HERE/'replay').glob('*/*.receipt.json')]
    print(json.dumps({'total_receipts':len(receipts),'passed':sum(r['status']=='PASS'for r in receipts),
                      'failed':[r for r in receipts if r['status']!='PASS']},indent=2),flush=True)

def stage():
    """Stage only checked improvements locally; this never pushes or comments."""
    sys.path.insert(0,str(ROOT/'scripts'))
    from engine import FAM
    solids=load(ROOT/'src/solids.json'); auditdata=load(HERE/'audit.json'); imported=[]; skipped=[]
    for task in auditdata['eligible']:
        rid=task['record_id']; folder=HERE/'replay'/task['kind']; receipt=load(folder/f'{rid}.receipt.json')
        assert receipt['status']=='PASS', f'not certified {rid}'
        raw=pathlib.Path(task['file']).read_bytes(); assert hashlib.sha256(raw).hexdigest()==receipt['witness_sha256']
        rec=load(task['file']); pid=rid.split('_')[0];unique_id=f'{rid}_pingyou_20261013'
        dest=ROOT/'records/community'/pid/f'{unique_id}.json'
        canonical=ROOT/'records'/pid/f'{rid}.json';old=load(canonical) if canonical.exists() else None
        if old and not rec['s_full']<old['s_full']-1e-12:
            skipped.append({'record_id':rid,'reason':'overtaken before staging'});continue
        previous={k:old.get(k) for k in ('s_full','s_tight','found_by','credit','method','source','date')} if old else None
        exact=(folder/f'{rid}.certify.txt').read_text(encoding='utf-8'); floatlog=(folder/f'{rid}.verify.txt').read_text(encoding='utf-8')
        vp,vc=solids[rec['piece']]['volume'],solids[rec['container']]['volume'];sf=rec['s_full'];floor=math.floor(sf*1e5)/1e5
        rec.update(record_id=unique_id,case_id=rid,family=FAM[pid],s=floor,s_plus=f'{floor:.5f}+',density=rec['n']*vp/(vc*sf**3),
                   volume_lower_bound=(rec['n']*vp/vc)**(1/3),problem=f'min/{rec["piece"]}_in_{rec["container"]}',
                   certificate='exact geometry certificate: current certify_general.py canonical solids; 170-bit outward-interval full replay',
                   date=rec.get('date','2026-10-13') if task['kind']=='wall_padding' else '2026-10-13')
        rec.setdefault('title',f'{rec["n"]} {rec["piece"]} in {rec["container"]}')
        rec.setdefault('measure','linear size of the container divided by the linear size of the pieces (canonical solid scaling)' if solids[rec['piece']].get('unit','edge')!='edge' else 'edge length of the container divided by the edge length of the pieces')
        rec.setdefault('format','[x, y, z, qw, qx, qy, qz] per piece; exact binary64 stored numbers interpreted rationally; scalar-first quaternion gives exact orthogonal rotation; canonical solids from src/solids_exact.json')
        rec['contribution']={'issue':f'https://github.com/alejandrozu/platonic-packing/issues/{task["issue"]}',
                             'submitted_by':'BuddenPing','credit':'PingYou Ltd','kind':task['kind'],
                             'archive':task['archive'],'archive_sha256':task['archive_sha256'],
                             'witness_sha256':receipt['witness_sha256'],'replayed_on':'2026-10-13'}
        if task['kind']=='wall_padding':
            rec['certificate_refined_by']='PingYou Ltd'
            if task['entry']['predecessor_encoding']=='konoha_cube':
                rec['found_by']='konoha-ily2';rec['credit']='Construction and original exact certificate by konoha-ily2; original geometry retained.'
                rec['method']='Sphere-to-cube continuation with L-BFGS; explicit separating-plane tightening; basin hopping for n=28.'
                rec['source']={'author':'konoha-ily2','url':task['entry']['predecessor_public_source'],
                               'original_certificate_sha256':task['entry']['predecessor_sha256']}
                rec['s_tight']=None
            rec['certificate_refined_on']='2026-10-13'
            rec['certificate_refinement']={'kind':'wall-padding reduction only; inherited piece poses unchanged',
                                           'previous_scale_exact':task['entry']['old_scale_exact'],
                                           'scale_exact':task['entry']['new_scale_exact'],
                                           'decrease_exact':task['entry']['strict_decrease_exact'],
                                           'new_nominal_construction':False}
        else:
            rec['found_by']='PingYou Ltd';rec['credit']='PingYou Ltd (finite construction and certificate submission); classical tessellation/subdivision acknowledged.'
            rec['source']={'issue':rec['contribution']['issue'],'author':'PingYou Ltd','submitted_by':'BuddenPing'}
            rec['nominal_bound_improvement']=task['kind']=='construction'
        # The old record is retained in Git history and its attribution remains accessible in the new record.
        rec['previous_record']=previous
        rec['clearance']={}
        for field,expr in [('min_wall_gap',r'min wall gap ([0-9.eE+\-]+)'),('min_pair_gap',r'min pair separation ([0-9.eE+\-]+)')]:
            m=re.search(expr,floatlog);rec['clearance'][field]=float(m.group(1)) if m else None
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(rec,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
        floatlog=floatlog.replace(task['file'],dest.relative_to(ROOT).as_posix())
        dest.with_suffix('.certify.txt').write_text(exact,encoding='utf-8');dest.with_suffix('.verify.txt').write_text(floatlog,encoding='utf-8')
        imported.append({k:task.get(k) for k in ('record_id','kind','scale','baseline_scale','baseline_file','baseline_author','behind_published_reference')})
        imported[-1]['file']=dest.relative_to(ROOT).as_posix()
    report={'checked_on':'2026-10-13','baseline_commit':auditdata['baseline_commit'],'imported_count':len(imported),
            'categories':len({r['record_id'].split('_')[0]for r in imported}),
            'by_kind':{k:sum(t['kind']==k for t in imported)for k,*_ in BATCHES},'batches':auditdata['batches'],
            'method':'Contributor scripts were not run. Every accepted JSON passed current upstream canonical-solid validation, full exact containment and pair separation replay, plus the current float verifier.',
            'imported':imported,'excluded':[{k:t.get(k)for k in ('record_id','kind','scale','baseline_scale','baseline_file','reason')}for t in auditdata['excluded']],
            'skipped_at_staging':skipped}
    dest=ROOT/'docs/community/2026-10-13';dest.mkdir(parents=True,exist_ok=True)
    (dest/'batch-receipt.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    registry=ROOT/'docs/community_records.json'
    previous=load(registry).get('entries',[]) if registry.exists() else []
    by_path={e['file']:e for e in previous}
    for task in imported:
        r=load(ROOT/task['file'])
        by_path[task['file']]={'problem':task['record_id'].split('_')[0],'n':r['n'],'file':task['file'],
                              'issue':r['contribution']['issue'],'kind':'coordinates','refinement_kind':task['kind']}
    registry.write_text(json.dumps({'checked_on':'2026-10-13','scope':'Certified coordinate candidates only; these entries are not published-reference bounds.',
                                    'entries':list(by_path.values())},indent=2)+'\n',encoding='utf-8')
    summary=['# Community construction and certificate batch, 13 October 2026','',
             f'{len(imported)} certified coordinate improvements were selected against commit `{auditdata["baseline_commit"]}` and available external certified coordinates.',
             '',f'- 47 different nominal-bound constructions: finite classical honeycomb and subdivision patches.',
             '- Four different triangular-subdivision configurations at an unchanged nominal side 2, with smaller positive-clearance certificates.',
             f'- {report["by_kind"]["wall_padding"]} wall-padding refinements: inherited pieces and orientations are unchanged. Discovery attribution is preserved; PingYou Ltd is credited separately for certificate refinement.',
             '',f'{len(auditdata["excluded"])} submitted cases were omitted because newer certified coordinates were already better.',
             '', 'A smaller certified container is an upper bound. Exact feasibility certification is not a proof of global optimality. Published source-only bounds remain separately attributed when no poses are available.',
             '', '[Construction submission and publication permission](https://github.com/alejandrozu/platonic-packing/issues/6) · [Wall-padding submission and publication permission](https://github.com/alejandrozu/platonic-packing/issues/7)',
             '', 'Source archives, SHA-256 values, exact witness bindings and current comparisons appear in `batch-receipt.json` and in each record’s `contribution` field. Geometry numbers are not rounded during import.']
    (dest/'README.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
    print(json.dumps({'staged':len(imported),'by_kind':report['by_kind'],'skipped':skipped},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','audit','replay','stage']);p.add_argument('--workers',type=int,default=4)
    p.add_argument('--kind',nargs='*');p.add_argument('--archive-dir');a=p.parse_args()
    if a.archive_dir:
        selected=pathlib.Path(a.archive_dir).resolve()
        BATCHES=[(k,selected/b.relative_to(HERE),i,u,s)for k,b,i,u,s in BATCHES]
        HERE=selected;os.environ['PACKING_COMMUNITY_ARCHIVES']=str(HERE)
    if a.mode=='prepare':prepare()
    elif a.mode=='audit':audit()
    elif a.mode=='replay':replay(a.workers,a.kind)
    else:stage()
