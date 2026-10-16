"""Download immutable remaining catalogue witnesses, with bounded concurrency.

This imports source bytes and hashes only; it makes no verification claim.
Existing files are parsed and checked against the frozen index before reuse.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request

HERE=Path(__file__).resolve().parent

def leaves(x):
    if isinstance(x,list):
        for v in x:yield from leaves(v)
    else:yield x

def kinds(d):
    out={}
    xs=[d['s_full'],*d.get('container_center',[]),*leaves(d['pieces'])]
    if 'mu' in d:xs.append(d['mu'])
    for x in xs:
        try:Fraction(x);k='rational'
        except (ValueError,TypeError):k='algebraic-string' if isinstance(x,str) and 'sqrt' in x else 'unsupported'
        out[k]=out.get(k,0)+1
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dimension',type=int,nargs='*',default=[3,4,5,6])
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--workers',type=int,default=8)
    args=ap.parse_args()
    registry=json.loads((HERE/'remaining-targets.json').read_text(encoding='utf8'))
    selected=[r for r in registry['records'] if r['dimension'] in args.dimension and r['n']<=args.max_n]
    dest=HERE/'inputs'
    for path in ['src/solids_exact.json','src/polytopes_nd.json']:
        source=HERE.parents[2]/'data/sources'/path
        target=dest/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    def fetch(r):
        path=dest/r['file']
        if path.is_file():b=path.read_bytes()
        else:
            last=None
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(r['immutable_url'],timeout=60) as response:b=response.read()
                    last=None;break
                except Exception as e:
                    last=e
                    if attempt<3:time.sleep(min(2**attempt,8))
            if last:raise last
        d=json.loads(b)
        assert d['piece']==r['piece'] and d['container']==r['container'] and d['n']==r['n']
        assert len(d['pieces'])==d['n']
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.is_file():path.write_bytes(b)
        return dict(r,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),scalar_kinds=kinds(d),
            credit_preserved=bool(d.get('credit')),source_keys=list(d))
    records=[];errors=[]
    started=time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(fetch,r):r for r in selected}
        for future in as_completed(futures):
            try:records.append(future.result())
            except Exception as e:errors.append(dict(file=futures[future]['file'],error=str(e)))
            if (len(records)+len(errors))%100==0:
                print(json.dumps(dict(imported=len(records),errors=len(errors),selected=len(selected),seconds=round(time.monotonic()-started,1))),flush=True)
    report_path=HERE/'input-manifest.json'
    old=json.loads(report_path.read_text(encoding='utf8')) if report_path.is_file() else {}
    merged={r['file']:r for r in old.get('records',[])}
    merged.update({r['file']:r for r in records})
    report=dict(freeze_git_sha=registry['freeze_git_sha'],formal_verification='Source import only; no Lean build implied',
        geometry_sources=registry['geometry_sources'],records=sorted(merged.values(),key=lambda r:(r['dimension'],r['problem'],r['n'])),errors=errors)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(dict(imported=len(records),errors=len(errors),total_local_records=len(merged),seconds=round(time.monotonic()-started,1))),flush=True)
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
