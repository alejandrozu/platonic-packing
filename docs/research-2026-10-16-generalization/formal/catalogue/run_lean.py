#!/usr/bin/env python3
"""Build generated modules with the actual Lean kernel and save honest receipts."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parent
ALLOWED={'propext','Classical.choice','Quot.sound'}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_one(row, lean, env, timeout, memory_mb=4096):
    if not isinstance(memory_mb,int) or memory_mb<1:
        raise ValueError('memory_mb must be a positive integer')
    path=FORMAL/row['path']
    target=path.with_suffix('.olean')
    source_before=digest(path)
    start=time.monotonic()
    args=[str(lean),'-j','1','-M',str(memory_mb),'-o',str(target),str(path)]
    try:
        p=subprocess.run(args,cwd=FORMAL,env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=timeout)
        code=p.returncode;log=p.stdout+p.stderr
    except subprocess.TimeoutExpired as err:
        code=None;log='TIMEOUT\n'+str(err.stdout or '')+str(err.stderr or '')
    used=set()
    for line in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',log):
        used.update(x.strip() for x in line.split(',') if x.strip())
    audit_seen=bool(re.search(r'depends on axioms:|does not depend on any axioms',log))
    bad=sorted(used-ALLOWED)
    source_after=digest(path)
    unchanged=source_before==source_after
    passed=code==0 and target.is_file() and audit_seen and not bad and 'sorryAx' not in log and unchanged
    logs=HERE/'build-logs';logs.mkdir(exist_ok=True)
    logpath=logs/(row['id']+'.log');logpath.write_text(log,encoding='utf8')
    return {**row,'passed':passed,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3),
            'memory_mb':memory_mb,
            'source_sha256':source_before,'source_unchanged_during_build':unchanged,
            'olean_sha256':digest(target) if passed else None,
            'axioms':sorted(used),'unexpected_axioms':bad,'audit_output_seen':audit_seen,
            'log':str(logpath.relative_to(FORMAL)).replace('\\','/'),'command':args,
            'log_sha256':digest(logpath)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--lean',type=Path,default=Path(shutil.which('lean') or str(Path.home()/'.elan/toolchains/leanprover--lean4---v4.31.0/bin/lean.exe')))
    ap.add_argument('--mathlib-project',type=Path,default=FORMAL)
    ap.add_argument('--max-n',type=int,default=100)
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--workers',type=int,default=1)
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--memory-mb',type=int,default=4096)
    ap.add_argument('--manifest',default='generated-modules.json')
    ap.add_argument('--receipt',default='lean-verification.json')
    args=ap.parse_args()
    if args.memory_mb<1:
        ap.error('--memory-mb must be positive')
    deps=[p/'.lake/build/lib/lean' for p in (args.mathlib_project/'.lake/packages').iterdir() if (p/'.lake/build/lib/lean').is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[FORMAL,FORMAL/'.lake/build/lib/lean',*deps]))
    rows=json.loads((HERE/args.manifest).read_text())
    rows=sorted((r for r in rows if r['n']<=args.max_n and (not args.only or r['id'] in args.only)),key=lambda r:r['n'])
    receipt={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
             'compiler':subprocess.check_output([str(args.lean),'--version'],text=True).strip(),
             'kernel_arithmetic':'by decide +kernel; no native_decide',
             'memory_mb':args.memory_mb,'results':[],'passed_records':0,'failed_records':0}
    receipt['core_source_hashes']={str(p.relative_to(FORMAL)).replace('\\','/'):digest(p)
                                  for p in (FORMAL/'PackingCertificates').glob('*.lean')}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run_one,r,args.lean,env,args.timeout,args.memory_mb):r for r in rows}
        for future in as_completed(futures):
            result=future.result();receipt['results'].append(result)
            receipt['passed_records']=sum(r['passed'] for r in receipt['results'])
            receipt['failed_records']=len(receipt['results'])-receipt['passed_records']
            (HERE/args.receipt).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
            print(json.dumps({k:result[k] for k in ('id','passed','exit_code','elapsed_seconds')}),flush=True)
    return int(receipt['failed_records']>0)


if __name__=='__main__':
    raise SystemExit(main())
