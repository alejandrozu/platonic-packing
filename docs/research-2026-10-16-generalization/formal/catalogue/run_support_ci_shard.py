#!/usr/bin/env python3
"""Support-first phase two for 225 ND records or the complete 402-record set.

This is a separate cohort and never changes the first 402-record partition.
The 177 complementary cube/24-cell-container records remain explicit in its
plan. Every selected record requires a fresh strict source/extension/object
closure receipt; old Windows successes are not silently reused on Linux.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import time

import run_ci_shard as base
import run_chunked
import generate_geometric_support_nd as generator

HERE, FORMAL = base.HERE, base.FORMAL


def support_catalogue(block_size=4):
    all_records = base.load_catalogue()
    selected, complement = [], []
    for row in all_records:
        c = json.loads((HERE / row['witness_path']).read_text(encoding='utf8'))
        if c['dimension'] == 3 or c['container'] == 'c24':
            strategy=base.strategies(c)[0]
            n,k=c['n'],len(c['template_vertices'])
            modules=1 if strategy=='ordinary' else 2+(n+4)//5 if strategy=='cube_chunks' else n+2 if strategy=='nd_chunks' else 2+n*(2+(k+7)//8)
            complement.append(dict(row,cost=row['cost']+modules*30000,
                estimated_modules=modules,optimized_support=False))
            continue
        n, d, k = c['n'], c['dimension'], len(c['template_vertices'])
        modules = (n + block_size - 1) // block_size + 2
        groups = len(set(generator.source_representatives(c)))
        # Include process/import overhead as well as rational arithmetic.
        weight = modules * 30000 + n*n*d*d*10 + groups*d*d*d*100
        selected.append(dict(row, cost=weight, estimated_modules=modules, source_groups=groups,optimized_support=True))
    if len(selected) != 225 or len(complement) != 177:
        raise ValueError('Unexpected support/complement partition of all 402 frozen witnesses')
    return selected, complement


def plan_shards(records, complement, count, scope='225'):
    plan = base.shard_plan(records, count)
    plan.update(schema_version=2, total_records=len(records), total_frozen_records=402,
                complementary_records=len(complement) if scope=='225' else 0,
                complement=complement if scope=='225' else [],
                original_strategy_records=len(complement),optimized_support_records=225,
                cohort='support-first-'+scope,
                scheduling='deterministic greedy module-overhead plus rational-work cost',
                proof_method='exact Cayley source; proved Gram; support pair planes; actual canonical hull containment')
    return plan


def strategies(c, block_size=4):
    if c['dimension']==3 or c['container']=='c24':
        return base.strategies(c)
    return ['support_b'+str(b) for b in dict.fromkeys([block_size]+([4] if block_size>4 else [])+[1])]


def emit(c, witness, strategy):
    if not strategy.startswith('support_b'):
        return base.emit(c,witness,strategy)
    block_size = int(strategy.removeprefix('support_b'))
    box = c['container'] in {'c8', 'hc5', 'hc6'}
    name, files = generator.generate(c, use_box_support=box, derive_gram=True,
                                     reuse_sources=True, block_size=block_size)
    ns = 'PackingCertificates.Catalogue.' + name
    directory = FORMAL / 'PackingCertificates' / 'Catalogue' / name
    directory.mkdir(parents=True, exist_ok=True)
    steps = []
    for entry in files:
        short = entry['short']
        path = directory / (short + '.lean') if short else directory.with_suffix('.lean')
        path.write_text(entry['text'], encoding='utf8', newline='\n')
        audits = re.findall(r'^#print axioms ([A-Za-z0-9_.]+)', entry['text'], re.M)
        steps.append(dict(id='phase2_' + name + ('_' + short.lower() if short else ''),
            record_id=c['record_id'], n=c['n'], dimension=c['dimension'],
            module=ns + ('.' + short if short else ''), path=str(path.relative_to(FORMAL)).replace('\\','/'),
            kind=entry['kind'], piece_indices=entry['piece_indices'], generated_source_sha256=base.sha(path),
            expected_audits=[a if '.' in a else ns + '.' + a for a in audits]))
    names = ['NDGeometry', 'NDSupport', 'NDModels', 'CayleyGeometry'] + (['BoxSupport'] if box else [])
    extensions = [FORMAL / 'PackingCertificates/Extensions' / (n + '.lean') for n in names]
    for source in extensions:
        if not source.with_suffix('.olean').is_file():
            raise ValueError('Compile pinned extension before phase two: ' + str(source))
    row = dict(base.metadata(c,witness), id='phase2_' + name,
        module=ns, path=steps[-1]['path'], block_size=block_size,
        source_representatives=generator.source_representatives(c),
        extension_dependencies=[dict(path=str(p.relative_to(FORMAL)).replace('\\','/'),
            source_sha256=base.sha(p),olean_sha256=base.sha(p.with_suffix('.olean'))) for p in extensions],
        steps=steps,dependencies=[{k:s[k] for k in ('module','path','generated_source_sha256')} for s in steps[:-1]])
    run_chunked.validate_plan(row)
    run_chunked.extension_dependencies(row)
    return row


def generic_receipt_provenance(path):
    path=path if path.is_absolute() else FORMAL/path
    path=path.resolve();path.relative_to(FORMAL)
    receipt=json.loads(path.read_text(encoding='utf8'))
    if receipt.get('schema')!='packing-extension-verification-v2' or receipt.get('passed') is not True:
        raise ValueError('A successful v2 generic extension build receipt is required')
    if receipt.get('verifier',{}).get('sha256')!=base.sha(FORMAL/'verify_extensions.py') or receipt.get('core_verifier_sha256')!=base.sha(FORMAL/'verify_core.py'):
        raise ValueError('Generic receipt verifier source differs from current pinned verifier')
    built={r['path']:r for r in receipt.get('results',[])}
    for name in ('NDGeometry','NDSupport','NDModels','BoxSupport','CayleyGeometry'):
        relative='PackingCertificates/Extensions/'+name+'.lean'
        row=built.get(relative);source=FORMAL/relative;target=source.with_suffix('.olean')
        if (not row or row.get('passed') is not True or row.get('exit_code')!=0 or
            row.get('source_sha256')!=base.sha(source) or row.get('olean_sha256')!=base.sha(target)):
            raise ValueError('Generic source/object build provenance mismatch: '+relative)
        log=FORMAL/row['log']
        if not log.is_file() or base.sha(log)!=row.get('log_sha256'):
            raise ValueError('Generic build log provenance mismatch: '+relative)
        if run_chunked.extension_audit.changed_dependencies(row.get('imported_dependencies',[])):
            raise ValueError('Generic transitive build dependency changed: '+relative)
    return dict(path=str(path.relative_to(FORMAL)).replace('\\','/'),sha256=base.sha(path),schema=receipt['schema'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--shard-index',type=int,default=0)
    ap.add_argument('--shard-count',type=int,default=12)
    ap.add_argument('--mathlib-project',type=Path,default=FORMAL)
    ap.add_argument('--lean',type=Path,default=Path(shutil.which('lean') or str(Path.home()/'.elan/toolchains/leanprover--lean4---v4.31.0/bin/lean.exe')))
    ap.add_argument('--timeout',type=int,default=900)
    ap.add_argument('--memory-mb',type=int,default=8192)
    ap.add_argument('--job-budget-seconds',type=int,default=19800)
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--plan-only',action='store_true')
    ap.add_argument('--block-size',type=int,choices=[1,4,8],default=4)
    ap.add_argument('--scope',choices=['225','all402'],default='225')
    ap.add_argument('--generic-extension-receipt',type=Path,default=Path('support225-generic-verification.json'))
    args=ap.parse_args()
    if args.shard_count<1 or not 0<=args.shard_index<args.shard_count:
        ap.error('Require 0 <= shard-index < shard-count')
    records,complement=support_catalogue(args.block_size)
    if args.scope=='all402':
        records=sorted(records+complement,key=lambda r:r['record_id'])
    plan=plan_shards(records,complement,args.shard_count,args.scope)
    outdir=HERE/'ci-support'/f'shard-{args.shard_index:02d}'
    outdir.mkdir(parents=True,exist_ok=True)
    base.write_json(outdir/'shard-plan.json',plan)
    selected=plan['shards'][args.shard_index]['records']
    if args.only:
        unknown=set(args.only)-{r['record_id'] for r in records}
        if unknown:ap.error('Not in selected support-first scope: '+', '.join(sorted(unknown)))
        selected=[r for r in records if r['record_id'] in args.only]
    if args.plan_only:
        print(json.dumps(dict(selected=len(selected),target_records=len(records),total_frozen_records=402,
            optimized_support_records=225,complement_records=177 if args.scope=='225' else 0,
            shards=args.shard_count,plan=str(outdir/'shard-plan.json'))),flush=True)
        return 0
    generic=generic_receipt_provenance(args.generic_extension_receipt)
    worker=Path(__file__).resolve()
    status_path=outdir/'status.json'
    status=dict(schema_version=2,started_at_utc=datetime.now(timezone.utc).isoformat(),
        cohort='support-first-'+args.scope,shard_index=args.shard_index,shard_count=args.shard_count,
        frozen_commit=base.FREEZE,total_selected=len(selected),total_cohort_records=len(records),
        block_size=args.block_size,
        total_frozen_records=402,memory_mb=args.memory_mb,timeout_per_module=args.timeout,
        github_run_id=os.environ.get('GITHUB_RUN_ID'),github_commit=os.environ.get('GITHUB_SHA'),
        worker_path=str(worker.relative_to(FORMAL)).replace('\\','/'),worker_sha256=base.sha(worker),
        generic_extension_receipt=generic,generic_extension_receipt_path=generic['path'],
        generic_extension_receipt_sha256=generic['sha256'],
        records=[],complete=False,proof_rule='Only complete strict source/object/import-closure audited kernel receipts accept records.')
    started=time.monotonic();deadline=started+args.job_budget_seconds;error=None
    try:
        for original in selected:
            rec=dict(original,attempts=[],passed=False,complete=False)
            status['records'].append(rec);base.write_json(status_path,status)
            if deadline-time.monotonic()<600:
                rec['failure']='Insufficient remaining job budget; no formal success claimed'
                continue
            try:
                base.build_record(rec,args,outdir,status,status_path,deadline,
                    strategy_picker=lambda c:strategies(c,args.block_size),emitter=emit)
            except base.IntegrityError:
                raise
            except Exception as exc:
                rec.update(driver_error=repr(exc),complete=True)
                print(json.dumps(dict(record_id=rec['record_id'],driver_error=repr(exc))),flush=True)
            status['passed_records']=sum(r['passed'] for r in status['records'])
            status['unverified_records']=len(selected)-status['passed_records']
            status['elapsed_seconds']=round(time.monotonic()-started,3)
            base.write_json(status_path,status);base.package(status,outdir)
    except Exception as exc:
        error=repr(exc);status['driver_error']=error
        raise
    finally:
        worker_stable=base.sha(worker)==status['worker_sha256']
        generic_stable=base.sha(FORMAL/generic['path'])==generic['sha256']
        status.update(complete=error is None and len(status['records'])==len(selected) and all(r['complete'] for r in status['records']),
            passed_records=sum(r['passed'] for r in status['records']),
            elapsed_seconds=round(time.monotonic()-started,3),finished_at_utc=datetime.now(timezone.utc).isoformat())
        status['worker_source_unchanged']=worker_stable
        status['generic_extension_receipt_unchanged']=generic_stable
        status['complete']=status['complete'] and worker_stable and generic_stable
        status['unverified_records']=len(selected)-status['passed_records']
        base.write_json(status_path,status);base.package(status,outdir)
        print(json.dumps(dict(passed_records=status['passed_records'],unverified_records=status['unverified_records'],
            evidence=str(outdir/'evidence.zip'))),flush=True)
    return int(status['unverified_records']>0 or not status['complete'])


if __name__=='__main__':
    raise SystemExit(main())
