#!/usr/bin/env python3
"""Resumable, source-bound CI shards of all 45 frozen algebraic ND pilots."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,threading,time,zipfile
from pathlib import Path

import run_verified as base
import generate_fragmented_nd_pilots as generator

HERE=Path(__file__).resolve().parent
FORMAL=HERE.parents[1]
REGISTRY=HERE/'generated-nd-pilots-registry.json'
ASSETS=HERE/'ci-nd45-assets.json'

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(FORMAL).as_posix()
def save(p,value):base.save(Path(p),value)


def assets(registry):
    files={FORMAL/name for name in ['lean-toolchain','lakefile.toml','lake-manifest.json',
        'verify_core.py','verify_extensions.py']}
    files.update(base.core.stages())
    for row in registry['records']:
        files.update(FORMAL/row[k]for k in ['generated_module','proposal_path','geometry_source_path','geometry_intervals_path'])
        files.add(HERE/'inputs'/row['source_path'])
    files.update(FORMAL/item['module']for item in registry['canonical_data_modules'])
    files.add(FORMAL/'PackingCertificates/Algebraic/FragmentND.lean')
    files.add(FORMAL/'PackingCertificates/Algebraic/TemplateFragments.lean')
    files.add(FORMAL/'PackingCertificates/Algebraic/RangeAssembly.lean')
    files.add(FORMAL/'PackingCertificates/Algebraic/RationalEncoding.lean')
    # Alternative canonical proof sources are publication inputs too, rather
    # than unpinned imports discovered only after the first record is emitted.
    import generate_fragmented_nd_templates as canonical
    geometry=read(HERE/'geometry-intervals-nd.json')
    names={Path(item['module']).stem for item in registry['canonical_data_modules']}
    for name in sorted(names):
        if name in geometry['templates']and geometry['templates'][name]['vertex_count']>=128:
            plan=canonical.generate(name,32,write=False)
            files.update(FORMAL/f['path']for f in plan['files'])
    for source in list(files):
        if source.suffix=='.lean':files.update(base.closure.local_import_closure(source,FORMAL))
    files.update(HERE/name for name in ['run_ci_nd45.py','generate_fragmented_nd_pilots.py','generate_fragmented_nd_templates.py','nd_array_data.py','nd_split_data.py',
        'run_verified_fragmented_nd.py','run_verified_nd.py','run_verified.py','generate_nd_pilots.py',
        'export_nd_pilots.py','nd_geometry.py','generate_3d.py','geometry_intervals.py'])
    files.update([HERE.parent/'export_nd.py',HERE.parent/'export_cubes.py',
        HERE.parent/'inputs/src/polytopes_nd.json',REGISTRY])
    return sorted(files,key=rel)


def verify_assets(manifest):
    if manifest['record_count']!=45 or manifest['frozen_commit']!=base.FREEZE:
        raise ValueError('Unexpected ND45 publication manifest')
    names=set()
    for row in manifest['files']:
        p=base.path(row['path'])
        if row['path']in names or not p.is_file()or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:
            raise ValueError('Missing, duplicate or changed ND publication asset: '+row['path'])
        names.add(row['path'])


def plan(registry,count):
    rows=[]
    for record in registry['records']:
        c=read(FORMAL/record['proposal_path']);d=record['dimension'];n=record['n']
        b=len(c['container_bases']);k=len(c['placed_vertex_intervals'][0])
        rows.append(dict(record_id=record['record_id'],dimension=d,n=n,vertices=k,
            bases=b,cost=b*(d+1)**3*64+n*k*d*64+(FORMAL/record['generated_module']).stat().st_size))
    if len(rows)!=45 or len({r['record_id']for r in rows})!=45:
        raise ValueError('This worker requires all 45 distinct frozen ND pilots')
    shards=[dict(index=i,cost=0,records=[])for i in range(count)]
    for row in sorted(rows,key=lambda r:(-r['cost'],r['record_id'])):
        dest=min(shards,key=lambda s:(s['cost'],s['index']))
        dest['records'].append(row);dest['cost']+=row['cost']
    for shard in shards:shard['records'].sort(key=lambda r:(r['cost'],r['record_id']))
    return dict(schema='nd45-proof-shards-v1',frozen_commit=base.FREEZE,
        total_records=45,shard_count=count,shards=shards)


def receipt_files(receipt):
    result={receipt};c=read(receipt)
    for key in ['builder_path','registry_path','fragment_builder_path']:
        if c.get(key):result.add(FORMAL/c[key])
    for stage in c.get('stages',[]):
        for key in ['path','olean_path','log']:
            if stage.get(key):result.add(FORMAL/stage[key])
        for dep in stage.get('imported_dependencies',[]):
            result.update(FORMAL/dep[k]for k in ['path','olean_path'])
    return result


def package(status,outdir):
    files=set(assets(read(REGISTRY)))|{ASSETS,outdir/'status.json',outdir/'shard-plan.json',FORMAL/'core-verification.json'}
    core=read(FORMAL/'core-verification.json')
    for stage in core['results']:
        files.update(FORMAL/stage[k]for k in ['path','olean_path','log'])
    # Includes top-level regression/probe sources/objects/logs verbatim, even
    # when they are not transitively imported by a packing certificate.
    for record in status['records']:
        for key in ['registry','receipt','driver_log']:
            if record.get(key)and(FORMAL/record[key]).is_file():files.add(FORMAL/record[key])
        if record.get('registry')and(FORMAL/record['registry']).is_file():
            for row in read(FORMAL/record['registry'])['records']:
                files.update(FORMAL/f['path']for f in row['fragmentation']['files'])
        if record.get('receipt')and(FORMAL/record['receipt']).is_file():
            files.update(receipt_files(FORMAL/record['receipt']))
    files=sorted((p for p in files if p.is_file()),key=rel)
    inv=dict(schema='nd45-kernel-evidence-v1',files=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p))for p in files])
    save(outdir/'evidence-inventory.json',inv)
    temporary=outdir/'evidence.zip.tmp'
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3)as z:
        for p in files:z.write(p,'formal/'+rel(p))
        z.write(outdir/'evidence-inventory.json','formal/'+rel(outdir/'evidence-inventory.json'))
    temporary.replace(outdir/'evidence.zip')


def run_record(rec,row,registry,args,outdir,caches,deadline):
    stem=rec['record_id'];fragment=generator.generate(row,args.basis_width,args.vertex_width,lazy_data=True,split_data=True)
    reg=outdir/(stem+'-registry.json')
    save(reg,dict(schema='nd-fragmented-packing-registry-v1',original_registry_path=rel(REGISTRY),
        original_registry_sha256=sha(REGISTRY),canonical_data_modules=registry['canonical_data_modules'],records=[fragment]))
    receipt=outdir/(stem+'-receipt.json');log=outdir/(stem+'-driver.log')
    rec.update(registry=rel(reg),receipt=rel(receipt),driver_log=rel(log),fragment_count=len(fragment['fragmentation']['files']))
    command=[sys.executable,'-u',str(HERE/'run_verified_fragmented_nd.py'),'--registry',str(reg),
        '--only',stem,'--mathlib-project',str(args.mathlib_project),'--lean',str(args.lean),
        '--memory-mb',str(args.memory_mb),'--timeout',str(args.timeout),'--receipt',str(receipt)]
    command+=['--extra-modules','PackingCertificates/Algebraic/RangeAssembly.lean',
        'PackingCertificates/Algebraic/RationalEncoding.lean']
    if caches:command+=['--cache-receipts',*map(str,caches)]
    if args.resume:command+=['--resume']
    killed=[]
    with log.open('w',encoding='utf8')as output:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
            encoding='utf8',errors='replace',bufsize=1,start_new_session=os.name!='nt')
        def terminate():
            if process.poll()is not None:return
            killed.append(True)
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
            else:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
        timer=threading.Timer(max(1,deadline-time.monotonic()-180),terminate);timer.daemon=True;timer.start()
        try:
            for line in process.stdout:print(line,end='',flush=True);output.write(line);output.flush()
            code=process.wait()
        finally:timer.cancel()
    rec.update(exit_code=code,complete=True,global_budget_timeout=bool(killed))
    if receipt.is_file():
        built=read(receipt);accepted=built.get('verified_records',[])
        rec.update(receipt_sha256=sha(receipt),passed=code==0 and built.get('status')=='passed'and
            built.get('fragment_semantic_audits_passed')is True and len(accepted)==1 and accepted[0]['record_id']==stem)
        caches.append(receipt)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--shard-index',type=int,default=0);ap.add_argument('--shard-count',type=int,default=12)
    ap.add_argument('--basis-width',type=int,default=8);ap.add_argument('--vertex-width',type=int,default=32)
    ap.add_argument('--mathlib-project',type=Path,default=FORMAL);ap.add_argument('--lean',type=Path,default=base.core.default_lean())
    ap.add_argument('--memory-mb',type=int,default=8192);ap.add_argument('--timeout',type=int,default=1800)
    ap.add_argument('--job-budget-seconds',type=int,default=19800)
    ap.add_argument('--cache-receipts',nargs='*',type=Path,default=[])
    ap.add_argument('--only',nargs='*');ap.add_argument('--resume',action='store_true')
    ap.add_argument('--plan-only',action='store_true');ap.add_argument('--write-assets',action='store_true')
    args=ap.parse_args()
    if args.shard_count<1 or not 0<=args.shard_index<args.shard_count:ap.error('Invalid shard index/count')
    registry=read(REGISTRY)
    if args.write_assets:
        paths=assets(registry)
        if any(not p.is_file()for p in paths):raise ValueError('Publication asset missing')
        manifest=dict(schema='nd45-publication-assets-v1',record_count=45,frozen_commit=base.FREEZE,
            files=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths])
        save(ASSETS,manifest);print(json.dumps(dict(files=len(paths),bytes=sum(r['bytes']for r in manifest['files']))));return 0
    verify_assets(read(ASSETS));schedule=plan(registry,args.shard_count)
    rows={r['record_id']:r for r in registry['records']}
    selected=schedule['shards'][args.shard_index]['records']
    if args.only:
        if set(args.only)-set(rows):ap.error('Unknown record ID')
        selected=[r for s in schedule['shards']for r in s['records']if r['record_id']in args.only]
    outdir=HERE/'ci-nd45'/f'shard-{args.shard_index:02d}';outdir.mkdir(parents=True,exist_ok=True)
    save(outdir/'shard-plan.json',schedule)
    if args.plan_only:
        print(json.dumps(dict(selected=len(selected),record_ids=[r['record_id']for r in selected],total=45,plan=rel(outdir/'shard-plan.json'))));return 0
    base.approved_core();started=time.monotonic();deadline=started+args.job_budget_seconds
    status=dict(schema='nd45-kernel-shard-status-v1',started_at_utc=datetime.now(timezone.utc).isoformat(),
        frozen_commit=base.FREEZE,github_run_id=os.environ.get('GITHUB_RUN_ID'),github_commit=os.environ.get('GITHUB_SHA'),
        worker_path=rel(Path(__file__)),worker_sha256=sha(Path(__file__)),asset_manifest_path=rel(ASSETS),asset_manifest_sha256=sha(ASSETS),
        shard_index=args.shard_index,shard_count=args.shard_count,total_selected=len(selected),
        basis_width=args.basis_width,vertex_width=args.vertex_width,lazy_data=True,data_group_width=4,records=[],complete=False)
    caches=list(args.cache_receipts)
    try:
        for summary in selected:
            rec=dict(summary,passed=False,complete=False);status['records'].append(rec)
            if deadline-time.monotonic()<600:rec.update(failure='Job budget exhausted',complete=True)
            else:
                try:run_record(rec,rows[rec['record_id']],registry,args,outdir,caches,deadline)
                except Exception as error:rec.update(driver_error=repr(error),complete=True)
            status.update(passed_records=sum(r['passed']for r in status['records']),elapsed_seconds=round(time.monotonic()-started,3))
            save(outdir/'status.json',status);package(status,outdir)
    finally:
        status['worker_unchanged']=sha(Path(__file__))==status['worker_sha256']
        status['asset_manifest_unchanged']=sha(ASSETS)==status['asset_manifest_sha256']
        try:verify_assets(read(ASSETS));status['publication_assets_unchanged']=True
        except Exception as error:
            status['publication_assets_unchanged']=False
            status['publication_asset_error']=repr(error)
        status.update(complete=len(status['records'])==len(selected)and all(r['complete']for r in status['records']),
            passed_records=sum(r['passed']for r in status['records']),finished_at_utc=datetime.now(timezone.utc).isoformat())
        status['unverified_records']=len(selected)-status['passed_records']
        save(outdir/'status.json',status);package(status,outdir)
        print(json.dumps(dict(passed=status['passed_records'],unverified=status['unverified_records'],evidence=rel(outdir/'evidence.zip'))),flush=True)
    return int(not status['complete']or status['unverified_records']>0 or
        not status['worker_unchanged']or not status['asset_manifest_unchanged']or
        not status['publication_assets_unchanged'])


if __name__=='__main__':raise SystemExit(main())
