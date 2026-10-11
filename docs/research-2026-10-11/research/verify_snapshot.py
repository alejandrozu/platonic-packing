import argparse, concurrent.futures, hashlib, json, pathlib, shutil, subprocess, sys, time

p=argparse.ArgumentParser()
p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path('work/repository'))
p.add_argument('--out',type=pathlib.Path,default=pathlib.Path('outputs/research/verification.json'))
p.add_argument('--workers',type=int,default=4)
a=p.parse_args(); repo=a.repo.resolve(); start=time.time()
files=sorted(repo.glob('records/*/*.json'))

def check(f):
    raw=f.read_bytes(); d=json.loads(raw)
    schema=bool(d['n']==len(d['pieces']) and len(d['pieces'])>=2 and all(len(x)==7 and sum(v*v for v in x[3:])>0 for x in d['pieces']))
    results={}
    for script in ['certify_exact.py','verify.py']:
        r=subprocess.run([sys.executable,str(repo/script),str(f)],cwd=repo,capture_output=True,text=True)
        results[script]={'exit_code':r.returncode,'output':r.stdout.strip(),'stderr':r.stderr.strip()}
    return {'path':f.relative_to(repo).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'n':d['n'],'piece':d['piece'],'container':d['container'],'s_full':d['s_full'],'schema_ok':schema,'checks':results,'ok':schema and all(r['exit_code']==0 for r in results.values())}

rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
    for row in pool.map(check,files):
        rows.append(row)
        if len(rows)%20==0: print(f'Checked {len(rows)}/{len(files)}; failures={sum(not x["ok"] for x in rows)}',flush=True)
git=shutil.which('git')
if not git: raise RuntimeError('Git must be available on PATH to identify the source commit')
sha=subprocess.check_output([git,'-C',str(repo),'rev-parse','HEAD'],text=True).strip()
payload={'source_commit':sha,'record_count':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'elapsed_seconds':time.time()-start,'command':'python work/verify_snapshot.py --repo work/repository --out outputs/research/verification.json','records':rows}
a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k!='records'},indent=2),flush=True)
sys.exit(0 if len(rows)==351 and payload['failed']==0 else 1)
