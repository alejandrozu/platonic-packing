#!/usr/bin/env python3
"""Build disjoint, deterministic shards of the 85 frozen algebraic 3D pilots.

Run verify_core.py first. Shared generic/canonical modules are reused only from
hash-matched complete stage receipts. Every record is checked independently;
failed exports/builds are retained and never counted as verified packings.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import threading
import time
import zipfile

import run_verified as verifier

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
REGISTRY=HERE/'generated3d-registry.json'
ASSETS=HERE/'ci-pilot-assets.json'
REGRESSION='PackingCertificates/Algebraic/Regression.lean'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rel(p):return p.resolve().relative_to(FORMAL).as_posix()
def write(p,value):verifier.save(p,value)


def assets(registry):
    """Publication allowlist: 85 pilots only, never the full export directory."""
    paths={FORMAL/'lean-toolchain',FORMAL/'lakefile.toml',FORMAL/'lake-manifest.json',
        FORMAL/'verify_core.py',FORMAL/'verify_extensions.py',REGISTRY,
        HERE/'run_verified.py',HERE/'run_ci_pilots.py',HERE/'export_3d.py',
        HERE/'generate_3d.py',HERE/'geometry_intervals.py',HERE/'README.md',HERE/'CI-PILOTS.md'}
    paths.update(FORMAL.glob('*.lean'))
    paths.update((FORMAL/'PackingCertificates').glob('*.lean'))
    paths.update(FORMAL/'PackingCertificates/Algebraic'/name for name in
        ['Interval.lean','Root.lean','Template.lean','Simplex.lean','Placement.lean','Packing.lean','Regression.lean'])
    paths.update(FORMAL/item['module']for item in registry['canonical_data_modules'])
    for row in registry['records']:
        paths.update([HERE/'inputs'/row['source_path'],FORMAL/row['proposal_path'],
            FORMAL/row['generated_module'],FORMAL/row['geometry_source_path'],FORMAL/row['geometry_intervals_path']])
    return sorted(paths,key=rel)


def asset_manifest(registry):
    paths=assets(registry)
    if any(not p.is_file()for p in paths):raise ValueError('Publication asset missing: '+str([rel(p)for p in paths if not p.is_file()]))
    return dict(schema='algebraic-pilot-assets-v1',frozen_commit=verifier.FREEZE,
        record_count=len(registry['records']),files=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths])


def verify_assets(manifest):
    names=set()
    for row in manifest['files']:
        p=verifier.path(row['path'])
        if row['path']in names or not p.is_file()or sha(p)!=row['sha256']or p.stat().st_size!=row['bytes']:
            raise ValueError('Missing, duplicate or changed publication asset: '+row['path'])
        names.add(row['path'])


def catalogue(registry):
    rows=[]
    for row in registry['records']:
        p=read(FORMAL/row['proposal_path']);n=row['n'];v=p['vertex_count'];b=len(p['container_bases'])
        # Integer workload estimate only; this is not a proved execution time.
        cost=b*24*64+v*16+n*n*16+(FORMAL/row['generated_module']).stat().st_size
        rows.append(dict(record_id=row['record_id'],piece=row['piece'],container=row['container'],n=n,
            vertices=v,cached_bases=b,cost=cost))
    if len(rows)!=85 or len({r['record_id']for r in rows})!=85:
        raise ValueError('This worker requires exactly the frozen 85 distinct 3D pilots')
    return sorted(rows,key=lambda r:r['record_id'])


def shard_plan(rows,count):
    shards=[dict(index=i,estimated_cost=0,records=[])for i in range(count)]
    for row in sorted(rows,key=lambda r:(-r['cost'],r['record_id'])):
        s=min(shards,key=lambda s:(s['estimated_cost'],s['index']))
        s['records'].append(row);s['estimated_cost']+=row['cost']
    for s in shards:s['records'].sort(key=lambda r:(r['cost'],r['record_id']))
    assert sorted(r['record_id']for s in shards for r in s['records'])==sorted(r['record_id']for r in rows)
    return dict(schema='algebraic-pilot-shards-v1',frozen_commit=verifier.FREEZE,total_records=85,
        shard_count=count,scheduling='Greedy descending integer estimate; lowest shard index breaks ties',shards=shards)


def receipt_files(receipt_path):
    result={receipt_path}
    receipt=read(receipt_path)
    for key in ['builder_path','registry_path']:
        if key in receipt:result.add(FORMAL/receipt[key])
    for stage in receipt.get('stages',[]):
        for key in ['path','olean_path','log']:
            if stage.get(key):result.add(FORMAL/stage[key])
        for dep in stage.get('imported_dependencies',[]):
            result.update([FORMAL/dep['path'],FORMAL/dep['olean_path']])
    return result


def package(status,outdir):
    paths=set(assets(read(REGISTRY)))|{ASSETS,outdir/'shard-plan.json',outdir/'status.json',FORMAL/'core-verification.json'}
    core=read(FORMAL/'core-verification.json')
    for row in core['results']:
        paths.update(FORMAL/row[k]for k in ['path','olean_path','log'])
    for rec in status['records']:
        for key in ['receipt','driver_log']:
            if rec.get(key)and (FORMAL/rec[key]).is_file():paths.add(FORMAL/rec[key])
        if rec.get('receipt')and(FORMAL/rec['receipt']).is_file():paths.update(receipt_files(FORMAL/rec['receipt']))
    paths=sorted((p for p in paths if p.is_file()),key=rel)
    inventory=dict(schema='algebraic-pilot-evidence-v1',files=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths])
    write(outdir/'evidence-inventory.json',inventory)
    temporary=outdir/'evidence.zip.tmp'
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3)as z:
        for p in paths:z.write(p,'formal/'+rel(p))
        z.write(outdir/'evidence-inventory.json','formal/'+rel(outdir/'evidence-inventory.json'))
    temporary.replace(outdir/'evidence.zip')


def run_record(rec,args,outdir,caches,deadline):
    stem=rec['record_id'];receipt=outdir/(stem+'-receipt.json');log=outdir/(stem+'-driver.log')
    command=[sys.executable,'-u',str(HERE/'run_verified.py'),'--registry',str(REGISTRY),
        '--only',stem,'--mathlib-project',str(args.mathlib_project),'--lean',str(args.lean),
        '--memory-mb',str(args.memory_mb),'--timeout',str(args.timeout),'--receipt',str(receipt),
        '--extra-modules',REGRESSION]
    if caches:command+=['--cache-receipts',*map(str,caches)]
    if args.resume:command+=['--resume']
    rec.update(receipt=rel(receipt),driver_log=rel(log),passed=False,complete=False)
    timed_out=[]
    with log.open('w',encoding='utf8')as output:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
            encoding='utf8',errors='replace',bufsize=1,start_new_session=os.name!='nt')
        def terminate():
            if process.poll()is not None:return
            timed_out.append(True)
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
            else:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
        timer=threading.Timer(max(1,deadline-time.monotonic()-180),terminate);timer.daemon=True;timer.start()
        try:
            for line in process.stdout:print(line,end='',flush=True);output.write(line);output.flush()
            code=process.wait()
        finally:timer.cancel()
    rec.update(exit_code=code,complete=True,global_budget_timeout=bool(timed_out))
    if receipt.is_file():
        built=read(receipt);accepted=built.get('verified_records',[])
        rec.update(receipt_sha256=sha(receipt),passed=code==0 and built.get('status')=='passed'and
            len(accepted)==1 and accepted[0]['record_id']==stem)
        # Failed record stages may still be reused only after individual exact
        # source/object/log/import validation by run_verified.reusable.
        caches.append(receipt)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mathlib-project',type=Path,default=FORMAL)
    p.add_argument('--lean',type=Path,default=verifier.core.default_lean())
    p.add_argument('--shard-index',type=int,default=0);p.add_argument('--shard-count',type=int,default=8)
    p.add_argument('--memory-mb',type=int,default=8192);p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--job-budget-seconds',type=int,default=19800)
    p.add_argument('--only',nargs='*');p.add_argument('--resume',action='store_true');p.add_argument('--plan-only',action='store_true')
    p.add_argument('--cache-receipts',nargs='*',type=Path,default=[],help='Existing complete stage receipts, still checked against current source/object/log/import hashes')
    p.add_argument('--write-assets',action='store_true',help='Write the explicit publication asset manifest and stop')
    args=p.parse_args()
    if args.shard_count<1 or not 0<=args.shard_index<args.shard_count:p.error('Require 0 <= shard-index < shard-count')
    registry=read(REGISTRY)
    if args.write_assets:
        manifest=asset_manifest(registry);write(ASSETS,manifest)
        print(json.dumps(dict(manifest=rel(ASSETS),files=len(manifest['files']),bytes=sum(r['bytes']for r in manifest['files']))));return 0
    manifest=read(ASSETS);verify_assets(manifest)
    rows=catalogue(registry);plan=shard_plan(rows,args.shard_count)
    selected=plan['shards'][args.shard_index]['records']
    if args.only:
        unknown=set(args.only)-{r['record_id']for r in rows}
        if unknown:p.error('Unknown record IDs: '+','.join(sorted(unknown)))
        selected=[r for r in rows if r['record_id']in args.only]
    outdir=HERE/'ci'/f'shard-{args.shard_index:02d}';outdir.mkdir(parents=True,exist_ok=True)
    write(outdir/'shard-plan.json',plan)
    if args.plan_only:
        print(json.dumps(dict(selected=len(selected),record_ids=[r['record_id']for r in selected],total=85,shards=args.shard_count,
            plan=rel(outdir/'shard-plan.json'),asset_files=len(manifest['files']))));return 0
    verifier.approved_core()
    started=time.monotonic();deadline=started+args.job_budget_seconds
    status=dict(schema='algebraic-pilot-shard-status-v1',started_at_utc=datetime.now(timezone.utc).isoformat(),
        frozen_commit=verifier.FREEZE,github_run_id=os.environ.get('GITHUB_RUN_ID'),github_commit=os.environ.get('GITHUB_SHA'),
        worker_path=rel(Path(__file__)),worker_sha256=sha(Path(__file__)),asset_manifest_path=rel(ASSETS),asset_manifest_sha256=sha(ASSETS),
        shard_index=args.shard_index,shard_count=args.shard_count,total_selected=len(selected),memory_mb=args.memory_mb,
        records=[],complete=False,proof_rule='Only successful source/geometry/render-bound kernel build receipts count.')
    caches=list(args.cache_receipts)
    try:
        for row in selected:
            rec=dict(row,passed=False,complete=False);status['records'].append(rec)
            if deadline-time.monotonic()<600:rec.update(failure='Job budget exhausted; no verification claimed',complete=True)
            else:
                try:run_record(rec,args,outdir,caches,deadline)
                except Exception as exc:rec.update(driver_error=repr(exc),complete=True)
            status.update(passed_records=sum(r['passed']for r in status['records']),elapsed_seconds=round(time.monotonic()-started,3))
            write(outdir/'status.json',status)
    finally:
        status.update(complete=len(status['records'])==len(selected)and all(r['complete']for r in status['records']),
            passed_records=sum(r['passed']for r in status['records']),finished_at_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=round(time.monotonic()-started,3))
        status['unverified_records']=len(selected)-status['passed_records']
        write(outdir/'status.json',status);package(status,outdir)
        print(json.dumps(dict(status=rel(outdir/'status.json'),passed=status['passed_records'],unverified=status['unverified_records'],
            evidence=rel(outdir/'evidence.zip'))),flush=True)
    return int(not status['complete']or status['unverified_records']>0)


if __name__=='__main__':raise SystemExit(main())
